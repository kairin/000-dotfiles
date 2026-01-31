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

func buildActionItems(claudeInstalled, codexInstalled, claudeAdded, codexAdded bool) []string {
	items := []string{}
	items = append(items, buildInstallActions(claudeInstalled, codexInstalled, claudeAdded, codexAdded)...)
	items = append(items, buildRemoveActions(claudeInstalled, codexInstalled, claudeAdded, codexAdded)...)
	items = append(items, "Back")
	return items
}

func buildInstallActions(claudeInstalled, codexInstalled, claudeAdded, codexAdded bool) []string {
	items := []string{}
	if claudeInstalled && codexInstalled {
		return buildInstallActionsBoth(items, claudeAdded, codexAdded)
	}
	if claudeInstalled {
		return buildInstallActionsClaudeOnly(items, claudeAdded)
	}
	if codexInstalled {
		return buildInstallActionsCodexOnly(items, codexAdded)
	}
	return items
}

func buildInstallActionsBoth(items []string, claudeAdded, codexAdded bool) []string {
	if !claudeAdded && !codexAdded {
		items = append(items, "Install (Both)")
		items = append(items, "Install (Claude only)")
		items = append(items, "Install (Codex only)")
		return items
	}
	if !claudeAdded {
		items = append(items, "Install (Claude only)")
	} else if !codexAdded {
		items = append(items, "Install (Codex only)")
	}
	return items
}

func buildInstallActionsClaudeOnly(items []string, claudeAdded bool) []string {
	if !claudeAdded {
		items = append(items, "Install (Claude)")
	}
	return items
}

func buildInstallActionsCodexOnly(items []string, codexAdded bool) []string {
	if !codexAdded {
		items = append(items, "Install (Codex)")
	}
	return items
}

func buildRemoveActions(claudeInstalled, codexInstalled, claudeAdded, codexAdded bool) []string {
	items := []string{}
	items = append(items, buildRemoveActionsSingle(claudeInstalled, claudeAdded, codexInstalled, codexAdded)...)
	items = append(items, buildRemoveActionsBoth(claudeInstalled, codexInstalled, claudeAdded, codexAdded)...)
	return items
}

func buildRemoveActionsSingle(claudeInstalled, claudeAdded, codexInstalled, codexAdded bool) []string {
	items := []string{}
	if claudeInstalled && claudeAdded {
		items = append(items, "Remove (Claude)")
	}
	if codexInstalled && codexAdded {
		items = append(items, "Remove (Codex)")
	}
	return items
}

func buildRemoveActionsBoth(claudeInstalled, codexInstalled, claudeAdded, codexAdded bool) []string {
	if claudeInstalled && codexInstalled && claudeAdded && codexAdded {
		return []string{"Remove (Both)"}
	}
	return nil
}

func (m *MCPServersModel) handlePreferenceMenuKey(msg tea.KeyMsg) (tea.Cmd, bool) {
	switch msg.String() {
	case "up", "k":
		m.preferenceCursor = shiftCursor(m.preferenceCursor, len(m.preferenceItems), -1)
		return nil, false
	case "down", "j":
		m.preferenceCursor = shiftCursor(m.preferenceCursor, len(m.preferenceItems), 1)
		return nil, false
	case "esc":
		m.resetPreferenceMenu()
		return nil, false
	case "enter":
		return m.handlePreferenceSelection()
	}
	return nil, false
}

func (m MCPServersModel) renderPreferenceMenu() string {
	var b strings.Builder
	titleStyle := lipgloss.NewStyle().Foreground(lipgloss.Color("135")).Bold(true)
	b.WriteString("\n")
	b.WriteString(titleStyle.Render("Default MCP Target:"))
	b.WriteString("\n")
	for i, item := range m.preferenceItems {
		cursor := " "
		style := MenuItemStyle
		if i == m.preferenceCursor {
			cursor = ">"
			style = MenuSelectedStyle
		}
		b.WriteString(fmt.Sprintf("%s %s\n", MenuCursorStyle.Render(cursor), style.Render(item)))
	}
	return b.String()
}

// parseActionTarget extracts the CLI target from an action string
func (m *MCPServersModel) parseActionTarget(action string) config.MCPCLITarget {
	if strings.Contains(action, "(Both)") {
		return config.MCPTargetBoth
	}
	if strings.Contains(action, "(Claude") {
		return config.MCPTargetClaude
	}
	if strings.Contains(action, "(Codex") {
		return config.MCPTargetCodex
	}
	if m.cliAvailability.ClaudeInstalled && m.cliAvailability.CodexInstalled {
		return config.MCPTargetBoth
	}
	if m.cliAvailability.ClaudeInstalled {
		return config.MCPTargetClaude
	}
	return config.MCPTargetCodex
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

func (m *MCPServersModel) handlePreferenceSelection() (tea.Cmd, bool) {
	if m.preferenceCursor >= len(m.preferenceItems) {
		return nil, false
	}
	choice := m.preferenceItems[m.preferenceCursor]
	if choice == "Back" {
		m.resetPreferenceMenu()
		return nil, false
	}
	target := preferenceTargetFromChoice(choice)
	if target != "" {
		m.saveDefaultTarget(target)
	}
	m.resetPreferenceMenu()
	return nil, false
}

func preferenceTargetFromChoice(choice string) config.MCPCLITarget {
	switch choice {
	case "Default: Both":
		return config.MCPTargetBoth
	case "Default: Claude":
		return config.MCPTargetClaude
	case "Default: Codex":
		return config.MCPTargetCodex
	default:
		return ""
	}
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
