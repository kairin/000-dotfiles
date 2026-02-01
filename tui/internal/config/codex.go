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
	configPath, err := codexConfigPath()
	if err != nil {
		return nil, err
	}

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

	// Read the file (path is resolved within ~/.codex).
	// nosemgrep: gosec.G304 -- path is fixed to ~/.codex/config.toml via codexConfigPath
	// #nosec G304 -- path is fixed to ~/.codex/config.toml via codexConfigPath
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
	configPath, err := resolveCodexConfigPath(config)
	if err != nil {
		return err
	}

	if err := ensureCodexConfigDir(configPath); err != nil {
		return err
	}

	output := buildCodexConfigOutput(config.rawText, config.MCPServers)
	mode := codexFileMode(config.fileMode)

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

func resolveCodexConfigPath(config *CodexConfig) (string, error) {
	configPath := config.configPath
	if configPath == "" {
		return codexConfigPath()
	}
	if err := validateCodexConfigPath(configPath); err != nil {
		return "", err
	}
	return configPath, nil
}

func ensureCodexConfigDir(configPath string) error {
	dir := filepath.Dir(configPath)
	if err := os.MkdirAll(dir, 0755); err != nil {
		return fmt.Errorf("failed to create Codex config directory: %w", err)
	}
	return nil
}

func buildCodexConfigOutput(rawText string, servers map[string]CodexMCPServer) string {
	block := renderCodexMCPServersBlock(servers)

	var output string
	if rawText != "" {
		output = replaceMCPServersBlock(rawText, block)
	} else if block != "" {
		output = block
	}

	if output != "" && !strings.HasSuffix(output, "\n") {
		output += "\n"
	}

	return output
}

func codexFileMode(mode os.FileMode) os.FileMode {
	if mode == 0 {
		return 0600
	}
	return mode
}

func renderCodexMCPServersBlock(servers map[string]CodexMCPServer) string {
	if len(servers) == 0 {
		return ""
	}

	names := sortedCodexServerNames(servers)
	var b strings.Builder
	for i, name := range names {
		writeCodexServerBlock(&b, name, servers[name])
		if i < len(names)-1 {
			b.WriteString("\n")
		}
	}

	return b.String()
}

func replaceMCPServersBlock(src string, block string) string {
	lines := strings.Split(src, "\n")
	sectionRe := regexp.MustCompile(`^\s*\[(.+)\]\s*$`)

	out, inserted := filterMCPServerSections(lines, sectionRe, block)
	if !inserted && block != "" {
		out = appendBlock(out, block)
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

func validateCodexConfigPath(configPath string) error {
	clean := filepath.Clean(configPath)
	if !filepath.IsAbs(clean) {
		return fmt.Errorf("invalid Codex config path: %s", configPath)
	}
	home, err := os.UserHomeDir()
	if err != nil || home == "" {
		return fmt.Errorf("failed to resolve home directory for Codex config")
	}
	allowed := filepath.Join(home, ".codex", "config.toml")
	if clean == allowed {
		return nil
	}
	codexDir := filepath.Join(home, ".codex") + string(os.PathSeparator)
	if strings.HasPrefix(clean, codexDir) {
		return nil
	}
	return fmt.Errorf("unexpected Codex config path: %s", configPath)
}

func codexConfigPath() (string, error) {
	home, err := os.UserHomeDir()
	if err != nil || home == "" {
		return "", fmt.Errorf("failed to resolve home directory for Codex config")
	}
	baseDir := filepath.Join(home, ".codex")
	filename := filepath.Base("config.toml")
	resolved := filepath.Join(baseDir, filename)
	allowedPrefix := baseDir + string(os.PathSeparator)
	if !strings.HasPrefix(resolved, allowedPrefix) {
		return "", fmt.Errorf("unexpected Codex config path: %s", resolved)
	}
	return resolved, nil
}

func sortedCodexServerNames(servers map[string]CodexMCPServer) []string {
	names := make([]string, 0, len(servers))
	for name := range servers {
		names = append(names, name)
	}
	sort.Strings(names)
	return names
}

func writeCodexServerBlock(b *strings.Builder, name string, server CodexMCPServer) {
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
}

func filterMCPServerSections(lines []string, sectionRe *regexp.Regexp, block string) ([]string, bool) {
	out := []string{}
	inserted := false
	skip := false

	for _, line := range lines {
		nextSkip, wroteBlock, wroteLine := handleSectionLine(line, sectionRe, block, skip, inserted, &out)
		if wroteBlock {
			inserted = true
		}
		if wroteLine {
			continue
		}
		skip = nextSkip
		if !skip {
			out = append(out, line)
		}
	}

	return out, inserted
}

func appendBlock(out []string, block string) []string {
	if len(out) > 0 && strings.TrimSpace(out[len(out)-1]) != "" {
		out = append(out, "")
	}
	return append(out, strings.Split(block, "\n")...)
}

func parseSection(line string, sectionRe *regexp.Regexp) (string, bool) {
	match := sectionRe.FindStringSubmatch(line)
	if match == nil {
		return "", false
	}
	return strings.TrimSpace(match[1]), true
}

func handleMCPSection(block string, skip bool, inserted bool, out *[]string) (bool, bool, bool) {
	if !skip && block != "" && !inserted {
		*out = append(*out, strings.Split(block, "\n")...)
		return true, true, true
	}
	if skip {
		return true, false, true
	}
	return true, false, true
}
func handleSectionLine(line string, sectionRe *regexp.Regexp, block string, skip bool, inserted bool, out *[]string) (bool, bool, bool) {
	section, ok := parseSection(line, sectionRe)
	if !ok {
		return skip, false, false
	}

	isMCP := strings.HasPrefix(section, "mcp_servers")
	if isMCP {
		return handleMCPSection(block, skip, inserted, out)
	}
	if skip {
		return false, false, false
	}
	return skip, false, false
}
