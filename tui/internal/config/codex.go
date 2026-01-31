// Package config provides Codex CLI configuration management
package config

import (
	"fmt"
	"os"
	"path/filepath"
	"regexp"
	"sort"
	"strconv"
	"strings"

	"github.com/BurntSushi/toml"
)

// CodexMCPServer represents an MCP server configuration in Codex config.toml
type CodexMCPServer struct {
	// For stdio transport
	Command string   `toml:"command,omitempty"`
	Args    []string `toml:"args,omitempty"`

	// For HTTP transport
	URL               string `toml:"url,omitempty"`
	BearerTokenEnvVar string `toml:"bearer_token_env_var,omitempty"`
}

// CodexConfig represents the Codex CLI configuration file structure.
type CodexConfig struct {
	MCPServers map[string]CodexMCPServer `toml:"mcp_servers"`

	// Preserve original file content for comment/format retention.
	rawText    string
	fileMode   os.FileMode
	configPath string
}

// GetCodexConfigPath returns the path to the Codex config file
func GetCodexConfigPath() string {
	home, err := os.UserHomeDir()
	if err != nil {
		home = os.Getenv("HOME")
	}
	return filepath.Join(home, ".codex", "config.toml")
}

// IsCodexInstalled checks if Codex CLI is available
func IsCodexInstalled() bool {
	// Check if codex command exists in PATH
	pathDirs := strings.Split(os.Getenv("PATH"), ":")
	for _, dir := range pathDirs {
		codexPath := filepath.Join(dir, "codex")
		if info, err := os.Stat(codexPath); err == nil && !info.IsDir() {
			return true
		}
	}

	// Also check common locations
	home, _ := os.UserHomeDir()
	commonPaths := []string{
		filepath.Join(home, ".local", "bin", "codex"),
		"/usr/local/bin/codex",
		"/usr/bin/codex",
	}

	for _, path := range commonPaths {
		if info, err := os.Stat(path); err == nil && !info.IsDir() {
			return true
		}
	}

	return false
}

// IsClaudeInstalled checks if Claude Code CLI is available
func IsClaudeInstalled() bool {
	// Check if claude command exists in PATH
	pathDirs := strings.Split(os.Getenv("PATH"), ":")
	for _, dir := range pathDirs {
		claudePath := filepath.Join(dir, "claude")
		if info, err := os.Stat(claudePath); err == nil && !info.IsDir() {
			return true
		}
	}

	// Also check common locations
	home, _ := os.UserHomeDir()
	commonPaths := []string{
		filepath.Join(home, ".local", "bin", "claude"),
		"/usr/local/bin/claude",
		"/usr/bin/claude",
	}

	for _, path := range commonPaths {
		if info, err := os.Stat(path); err == nil && !info.IsDir() {
			return true
		}
	}

	return false
}

// ReadCodexConfig reads the Codex config.toml file
func ReadCodexConfig() (*CodexConfig, error) {
	configPath := GetCodexConfigPath()

	config := &CodexConfig{
		MCPServers: make(map[string]CodexMCPServer),
		configPath: configPath,
	}

	// Check if file exists
	info, err := os.Stat(configPath)
	if os.IsNotExist(err) {
		// File doesn't exist, return empty config
		return config, nil
	}
	if err != nil {
		return nil, fmt.Errorf("failed to stat Codex config: %w", err)
	}

	// Read the file
	data, err := os.ReadFile(configPath)
	if err != nil {
		return nil, fmt.Errorf("failed to read Codex config: %w", err)
	}
	config.rawText = string(data)
	config.fileMode = info.Mode().Perm()

	// Decode specifically for mcp_servers
	// We use a temporary struct to get the typed data
	var typedConfig struct {
		MCPServers map[string]CodexMCPServer `toml:"mcp_servers"`
	}

	if err := toml.Unmarshal(data, &typedConfig); err != nil {
		return nil, fmt.Errorf("failed to parse Codex config: %w", err)
	}

	if typedConfig.MCPServers != nil {
		config.MCPServers = typedConfig.MCPServers
	}

	return config, nil
}

// WriteCodexConfig writes the Codex config.toml file
func WriteCodexConfig(config *CodexConfig) error {
	configPath := config.configPath
	if configPath == "" {
		configPath = GetCodexConfigPath()
	}

	// Ensure directory exists
	dir := filepath.Dir(configPath)
	if err := os.MkdirAll(dir, 0755); err != nil {
		return fmt.Errorf("failed to create Codex config directory: %w", err)
	}

	// Build mcp_servers block
	block := renderCodexMCPServersBlock(config.MCPServers)

	var output string
	if config.rawText != "" {
		output = replaceMCPServersBlock(config.rawText, block)
	} else if block != "" {
		output = block
	}

	if output != "" && !strings.HasSuffix(output, "\n") {
		output += "\n"
	}

	mode := config.fileMode
	if mode == 0 {
		mode = 0600
	}

	return writeFileAtomic(configPath, []byte(output), mode)
}

// AddCodexMCPServer adds an MCP server to the Codex config
func AddCodexMCPServer(serverID string, server CodexMCPServer) error {
	config, err := ReadCodexConfig()
	if err != nil {
		return err
	}

	// Add the server
	config.MCPServers[serverID] = server

	return WriteCodexConfig(config)
}

// RemoveCodexMCPServer removes an MCP server from the Codex config
func RemoveCodexMCPServer(serverID string) error {
	config, err := ReadCodexConfig()
	if err != nil {
		return err
	}

	// Remove the server
	delete(config.MCPServers, serverID)

	return WriteCodexConfig(config)
}

// HasCodexMCPServer checks if a server is configured in Codex
func HasCodexMCPServer(serverID string) (bool, error) {
	config, err := ReadCodexConfig()
	if err != nil {
		return false, err
	}

	_, exists := config.MCPServers[serverID]
	return exists, nil
}

// GetCodexMCPServers returns all configured MCP servers in Codex
func GetCodexMCPServers() (map[string]CodexMCPServer, error) {
	config, err := ReadCodexConfig()
	if err != nil {
		return nil, err
	}

	return config.MCPServers, nil
}

// CodexConfigExists checks if the Codex config file exists
func CodexConfigExists() bool {
	configPath := GetCodexConfigPath()
	_, err := os.Stat(configPath)
	return err == nil
}

func renderCodexMCPServersBlock(servers map[string]CodexMCPServer) string {
	if len(servers) == 0 {
		return ""
	}

	names := make([]string, 0, len(servers))
	for name := range servers {
		names = append(names, name)
	}
	sort.Strings(names)

	var b strings.Builder
	for i, name := range names {
		server := servers[name]
		b.WriteString("[mcp_servers.")
		b.WriteString(name)
		b.WriteString("]\n")
		if server.Command != "" {
			b.WriteString("command = ")
			b.WriteString(strconv.Quote(server.Command))
			b.WriteString("\n")
		}
		if len(server.Args) > 0 {
			b.WriteString("args = [")
			for idx, arg := range server.Args {
				if idx > 0 {
					b.WriteString(", ")
				}
				b.WriteString(strconv.Quote(arg))
			}
			b.WriteString("]\n")
		}
		if server.URL != "" {
			b.WriteString("url = ")
			b.WriteString(strconv.Quote(server.URL))
			b.WriteString("\n")
		}
		if server.BearerTokenEnvVar != "" {
			b.WriteString("bearer_token_env_var = ")
			b.WriteString(strconv.Quote(server.BearerTokenEnvVar))
			b.WriteString("\n")
		}
		if i < len(names)-1 {
			b.WriteString("\n")
		}
	}

	return b.String()
}

func replaceMCPServersBlock(src string, block string) string {
	lines := strings.Split(src, "\n")
	sectionRe := regexp.MustCompile(`^\s*\[(.+)\]\s*$`)

	var out []string
	inserted := false
	skip := false

	for _, line := range lines {
		match := sectionRe.FindStringSubmatch(line)
		if match != nil {
			section := strings.TrimSpace(match[1])
			isMCP := strings.HasPrefix(section, "mcp_servers")
			if isMCP && !skip {
				if block != "" && !inserted {
					out = append(out, strings.Split(block, "\n")...)
					inserted = true
				}
				skip = true
				continue
			}
			if skip && !isMCP {
				skip = false
			}
			if skip {
				continue
			}
		}
		if !skip {
			out = append(out, line)
		}
	}

	if !inserted && block != "" {
		if len(out) > 0 && strings.TrimSpace(out[len(out)-1]) != "" {
			out = append(out, "")
		}
		out = append(out, strings.Split(block, "\n")...)
	}

	return strings.Join(out, "\n")
}

func writeFileAtomic(path string, data []byte, mode os.FileMode) error {
	dir := filepath.Dir(path)
	tmp, err := os.CreateTemp(dir, ".codex-config-*.toml")
	if err != nil {
		return fmt.Errorf("failed to create temp file: %w", err)
	}
	defer func() {
		_ = os.Remove(tmp.Name())
	}()

	if _, err := tmp.Write(data); err != nil {
		_ = tmp.Close()
		return fmt.Errorf("failed to write temp config: %w", err)
	}
	if err := tmp.Close(); err != nil {
		return fmt.Errorf("failed to close temp config: %w", err)
	}

	if err := os.Chmod(tmp.Name(), mode); err != nil {
		return fmt.Errorf("failed to set config permissions: %w", err)
	}
	if err := os.Rename(tmp.Name(), path); err != nil {
		return fmt.Errorf("failed to replace config: %w", err)
	}

	return nil
}
