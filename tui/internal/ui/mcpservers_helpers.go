// Package ui - mcpservers_helpers.go provides helpers for MCP servers view
package ui

import (
	"fmt"
	"os/exec"
	"strings"

	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"
	"github.com/kairin/dotfiles-installer/internal/config"
	"github.com/kairin/dotfiles-installer/internal/registry"
)

func runClaudeMCPList() (string, string, error) {
	cmd := exec.Command("claude", "mcp", "list")
	output, err := cmd.CombinedOutput()
	outputText := string(output)
	return outputText, strings.ToLower(outputText), err
}

func applyClaudeAuthError(statuses map[string]MCPServerStatus) {
	for _, server := range registry.GetAllMCPServers() {
		statuses[server.ID] = MCPServerStatus{
			Connected: false,
			Error:     "auth",
		}
	}
}

func parseClaudeMCPStatuses(output string) map[string]MCPServerStatus {
	statuses := make(map[string]MCPServerStatus)
	lines := strings.Split(output, "\n")
	for _, line := range lines {
		line = strings.TrimSpace(line)
		if line == "" {
			continue
		}
		for _, server := range registry.GetAllMCPServers() {
			if strings.Contains(line, server.ID) {
				connected := strings.Contains(strings.ToLower(line), "connected") ||
					strings.Contains(line, "✓") ||
					!strings.Contains(strings.ToLower(line), "error")

				statuses[server.ID] = MCPServerStatus{
					Connected: connected,
				}
			}
		}
	}
	return statuses
}

func (m MCPServersModel) renderServerRow(i int, server *registry.MCPServer, colServer, colClaude, colCodex, colDescription int) string {
	claudeStr, claudeStyle, codexStr, codexStyle := m.statusDisplayFor(server)

	rowStyle := TableRowStyle
	if i == m.cursor && m.cursor < len(m.servers) {
		rowStyle = TableSelectedStyle
	}

	desc := truncateDescription(server.Description, colDescription)
	row := fmt.Sprintf("%-*s %-*s %-*s %-*s",
		colServer, server.DisplayName,
		colClaude, claudeStyle.Render(claudeStr),
		colCodex, codexStyle.Render(codexStr),
		colDescription, desc,
	)
	return rowStyle.Render(row)
}

func (m MCPServersModel) statusDisplayFor(server *registry.MCPServer) (string, lipgloss.Style, string, lipgloss.Style) {
	if m.loading {
		spinner := m.spinner.View()
		return spinner, StatusUnknownStyle, spinner, StatusUnknownStyle
	}

	status, hasStatus := m.statuses[server.ID]
	claudeStr, claudeStyle := statusCell(m.cliAvailability.ClaudeInstalled, hasStatus, status.Claude)
	codexStr, codexStyle := statusCell(m.cliAvailability.CodexInstalled, hasStatus, status.Codex)

	return claudeStr, claudeStyle, codexStr, codexStyle
}

func statusCell(available bool, hasStatus bool, status MCPServerStatus) (string, lipgloss.Style) {
	if !available {
		return "N/A", StatusUnknownStyle
	}
	label, style := statusLabel(hasStatus, status)
	return label, style
}

func statusLabel(hasStatus bool, status MCPServerStatus) (string, lipgloss.Style) {
	if hasStatus {
		if status.Error == "auth" {
			return "Login", StatusUpdateStyle
		}
		if status.Error == "config" {
			return "Config", StatusMissingStyle
		}
		if status.Error != "" {
			return "Error", StatusMissingStyle
		}
		if status.Connected {
			return IconCheckmark + " Added", StatusInstalledStyle
		}
	}
	return IconCross + " Missing", StatusMissingStyle
}

func truncateDescription(desc string, max int) string {
	if len(desc) <= max {
		return desc
	}
	return desc[:max-3] + "..."
}


// HandleKey processes key presses in MCP Servers view
func (m *MCPServersModel) HandleKey(msg tea.KeyMsg) (tea.Cmd, bool) {
	if m.preferenceMode {
		return m.handlePreferenceMenuKey(msg)
	}
	if m.menuMode {
		return m.handleActionMenuKey(msg)
	}

	switch msg.String() {
	case "up", "k":
		m.moveMainCursor(-1)
		return nil, false

	case "down", "j":
		m.moveMainCursor(1)
		return nil, false

	case "r":
		m.loading = true
		return tea.Batch(
			m.spinner.Tick,
			m.refreshMCPStatuses(),
		), false

	case "enter":
		return m.handleMainMenuSelection()
	}

	return nil, false
}

// IsBackSelected returns true if "Back" is selected in the main menu.
func (m MCPServersModel) IsBackSelected() bool {
	if m.menuMode || m.preferenceMode {
		return false
	}
	return m.cursor == len(m.servers)+2
}


func looksLikeAuthError(msg string) bool {
	if msg == "" {
		return false
	}
	return strings.Contains(msg, "auth") ||
		strings.Contains(msg, "login") ||
		strings.Contains(msg, "unauthorized") ||
		strings.Contains(msg, "forbidden")
}

func formatMCPActionResult(action string, msg interface{}) (string, bool) {
	var serverID string
	var claudeOK bool
	var codexOK bool
	var claudeErr error
	var codexErr error

	switch v := msg.(type) {
	case mcpInstallResultMsg:
		serverID = v.serverID
		claudeOK = v.claudeOK
		codexOK = v.codexOK
		claudeErr = v.claudeErr
		codexErr = v.codexErr
	case mcpRemoveResultMsg:
		serverID = v.serverID
		claudeOK = v.claudeOK
		codexOK = v.codexOK
		claudeErr = v.claudeErr
		codexErr = v.codexErr
	default:
		return "", false
	}

	serverName := serverID
	if server, ok := registry.GetMCPServer(serverID); ok {
		serverName = server.DisplayName
	}

	okCount := 0
	failCount := 0
	if claudeOK || claudeErr != nil {
		if claudeOK {
			okCount++
		} else {
			failCount++
		}
	}
	if codexOK || codexErr != nil {
		if codexOK {
			okCount++
		} else {
			failCount++
		}
	}

	if failCount == 0 {
		return fmt.Sprintf("%s successful for %s", action, serverName), false
	}

	parts := []string{fmt.Sprintf("%s partial for %s", action, serverName)}
	if claudeErr != nil {
		parts = append(parts, "Claude: "+claudeErr.Error())
	}
	if codexErr != nil {
		parts = append(parts, "Codex: "+codexErr.Error())
	}
	return strings.Join(parts, " | "), true
}

func shiftCursor(cursor int, total int, delta int) int {
	if total == 0 {
		return 0
	}
	next := cursor + delta
	if next < 0 {
		return total - 1
	}
	if next >= total {
		return 0
	}
	return next
}

func (m *MCPServersModel) saveDefaultTarget(target config.MCPCLITarget) {
	prefs := config.NewPreferenceStore()
	if err := prefs.SetMCPDefaultTarget(target); err != nil {
		m.lastActionMessage = "Failed to save default target: " + err.Error()
		m.lastActionError = true
		return
	}
	m.defaultTarget = target
	m.lastActionMessage = "Default target set to " + string(target)
	m.lastActionError = false
}

func (m *MCPServersModel) resetPreferenceMenu() {
	m.preferenceMode = false
	m.preferenceItems = nil
	m.preferenceCursor = 0
}

func (m *MCPServersModel) installMCPServerToTarget(server *registry.MCPServer, target config.MCPCLITarget) tea.Cmd {
	return func() tea.Msg {
		var claudeOK bool
		var codexOK bool
		var claudeErr error
		var codexErr error

		if server == nil {
			return mcpInstallResultMsg{
				serverID:  "",
				target:    target,
				claudeErr: fmt.Errorf("invalid MCP server"),
			}
		}

		if target == config.MCPTargetBoth || target == config.MCPTargetClaude {
			if !m.cliAvailability.ClaudeInstalled {
				claudeErr = fmt.Errorf("Claude CLI not installed")
			} else {
				claudeOK, claudeErr = installMCPServerClaude(server)
			}
		}

		if target == config.MCPTargetBoth || target == config.MCPTargetCodex {
			if !m.cliAvailability.CodexInstalled {
				codexErr = fmt.Errorf("Codex CLI not installed")
			} else {
				codexOK, codexErr = installMCPServerCodex(server)
			}
		}

		return mcpInstallResultMsg{
			serverID:  server.ID,
			target:    target,
			claudeOK:  claudeOK,
			codexOK:   codexOK,
			claudeErr: claudeErr,
			codexErr:  codexErr,
		}
	}
}

func (m *MCPServersModel) removeMCPServerFromTarget(server *registry.MCPServer, target config.MCPCLITarget) tea.Cmd {
	return func() tea.Msg {
		var claudeOK bool
		var codexOK bool
		var claudeErr error
		var codexErr error

		if server == nil {
			return mcpRemoveResultMsg{
				serverID:  "",
				target:    target,
				claudeErr: fmt.Errorf("invalid MCP server"),
			}
		}

		if target == config.MCPTargetBoth || target == config.MCPTargetClaude {
			if !m.cliAvailability.ClaudeInstalled {
				claudeErr = fmt.Errorf("Claude CLI not installed")
			} else {
				claudeOK, claudeErr = removeMCPServerClaude(server)
			}
		}

		if target == config.MCPTargetBoth || target == config.MCPTargetCodex {
			if !m.cliAvailability.CodexInstalled {
				codexErr = fmt.Errorf("Codex CLI not installed")
			} else {
				codexOK, codexErr = removeMCPServerCodex(server)
			}
		}

		return mcpRemoveResultMsg{
			serverID:  server.ID,
			target:    target,
			claudeOK:  claudeOK,
			codexOK:   codexOK,
			claudeErr: claudeErr,
			codexErr:  codexErr,
		}
	}
}

func installMCPServerClaude(server *registry.MCPServer) (bool, error) {
	args := server.GetAddCommand()
	cmd := exec.Command("claude", args...)
	output, err := cmd.CombinedOutput()
	if err != nil {
		msg := strings.TrimSpace(string(output))
		if msg == "" {
			msg = err.Error()
		}
		return false, fmt.Errorf("Claude install failed: %s", msg)
	}
	return true, nil
}

func removeMCPServerClaude(server *registry.MCPServer) (bool, error) {
	args := server.GetRemoveCommand()
	cmd := exec.Command("claude", args...)
	output, err := cmd.CombinedOutput()
	if err != nil {
		msg := strings.TrimSpace(string(output))
		if msg == "" {
			msg = err.Error()
		}
		return false, fmt.Errorf("Claude remove failed: %s", msg)
	}
	return true, nil
}

func installMCPServerCodex(server *registry.MCPServer) (bool, error) {
	cfg, err := buildCodexMCPServer(server)
	if err != nil {
		return false, err
	}
	if err := config.AddCodexMCPServer(server.ID, cfg); err != nil {
		return false, err
	}
	return true, nil
}

func removeMCPServerCodex(server *registry.MCPServer) (bool, error) {
	if err := config.RemoveCodexMCPServer(server.ID); err != nil {
		return false, err
	}
	return true, nil
}

func buildCodexMCPServer(server *registry.MCPServer) (config.CodexMCPServer, error) {
	if server == nil {
		return config.CodexMCPServer{}, fmt.Errorf("invalid MCP server")
	}
	if server.CodexConfig.URL != "" {
		return config.CodexMCPServer{
			URL:               server.CodexConfig.URL,
			BearerTokenEnvVar: server.CodexConfig.BearerTokenEnvVar,
		}, nil
	}
	if server.CodexConfig.Command != "" {
		return config.CodexMCPServer{
			Command: server.CodexConfig.Command,
			Args:    server.CodexConfig.Args,
		}, nil
	}
	return config.CodexMCPServer{}, fmt.Errorf("missing Codex config for %s", server.DisplayName)
}
