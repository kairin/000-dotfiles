// Package config provides Codex CLI configuration management
package config

import (
	"bytes"
	"fmt"
	"os"
	"path/filepath"
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

// CodexConfig represents the Codex CLI configuration file structure
// We use a map to preserve arbitrary sections while focusing on mcp_servers
type CodexConfig struct {
	MCPServers map[string]CodexMCPServer `toml:"mcp_servers"`

	// Preserve other sections as raw data
	rawData    map[string]interface{}
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
		rawData:    make(map[string]interface{}),
		configPath: configPath,
	}

	// Check if file exists
	if _, err := os.Stat(configPath); os.IsNotExist(err) {
		// File doesn't exist, return empty config
		return config, nil
	}

	// Read the file
	data, err := os.ReadFile(configPath)
	if err != nil {
		return nil, fmt.Errorf("failed to read Codex config: %w", err)
	}

	// First decode into raw data to preserve everything
	if err := toml.Unmarshal(data, &config.rawData); err != nil {
		return nil, fmt.Errorf("failed to parse Codex config: %w", err)
	}

	// Now decode specifically for mcp_servers
	// We use a temporary struct to get the typed data
	var typedConfig struct {
		MCPServers map[string]CodexMCPServer `toml:"mcp_servers"`
	}

	if err := toml.Unmarshal(data, &typedConfig); err != nil {
		return nil, fmt.Errorf("failed to parse MCP servers: %w", err)
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

	// Build the output by merging rawData with MCPServers
	outputData := make(map[string]interface{})

	// Copy all existing data
	for k, v := range config.rawData {
		outputData[k] = v
	}

	// Update mcp_servers section
	if len(config.MCPServers) > 0 {
		mcpSection := make(map[string]interface{})
		for name, server := range config.MCPServers {
			serverMap := make(map[string]interface{})
			if server.Command != "" {
				serverMap["command"] = server.Command
			}
			if len(server.Args) > 0 {
				serverMap["args"] = server.Args
			}
			if server.URL != "" {
				serverMap["url"] = server.URL
			}
			if server.BearerTokenEnvVar != "" {
				serverMap["bearer_token_env_var"] = server.BearerTokenEnvVar
			}
			mcpSection[name] = serverMap
		}
		outputData["mcp_servers"] = mcpSection
	} else {
		// Remove mcp_servers if empty
		delete(outputData, "mcp_servers")
	}

	// Encode to TOML
	var buf bytes.Buffer
	encoder := toml.NewEncoder(&buf)
	encoder.Indent = ""
	if err := encoder.Encode(outputData); err != nil {
		return fmt.Errorf("failed to encode Codex config: %w", err)
	}

	// Write to file
	if err := os.WriteFile(configPath, buf.Bytes(), 0644); err != nil {
		return fmt.Errorf("failed to write Codex config: %w", err)
	}

	return nil
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
