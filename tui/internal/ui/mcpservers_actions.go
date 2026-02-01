// Package ui - mcpservers_actions.go provides menu/action handlers for MCP servers view
package ui

import (
	"fmt"
	"strings"

	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"
	"github.com/kairin/dotfiles-installer/internal/config"
	"github.com/kairin/dotfiles-installer/internal/registry"
)

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

func (m *MCPServersModel) openPreferenceMenu() {
	m.preferenceMode = true
	m.preferenceCursor = 0
	m.preferenceItems = m.buildPreferenceItems()
}

func (m *MCPServersModel) buildPreferenceItems() []string {
	items := []string{}
	if m.cliAvailability.ClaudeInstalled && m.cliAvailability.CodexInstalled {
		items = append(items, "Default: Both", "Default: Claude", "Default: Codex")
	} else if m.cliAvailability.ClaudeInstalled {
		items = append(items, "Default: Claude")
	} else if m.cliAvailability.CodexInstalled {
		items = append(items, "Default: Codex")
	}
	items = append(items, "Back")
	return items
}

func (m *MCPServersModel) showActionMenu(server *registry.MCPServer) {
	m.selectedServer = server
	m.menuMode = true
	m.actionCursor = 0
	m.selectedAction = ""

	status := m.statuses[server.ID]
	claudeAdded := status.Claude.Connected
	codexAdded := status.Codex.Connected

	m.actionItems = buildActionItems(
		m.cliAvailability.ClaudeInstalled,
		m.cliAvailability.CodexInstalled,
		claudeAdded,
		codexAdded,
	)
}

func (m *MCPServersModel) handleActionMenuKey(msg tea.KeyMsg) (tea.Cmd, bool) {
	switch msg.String() {
	case "up", "k":
		m.moveActionCursor(-1)
		return nil, false
	case "down", "j":
		m.moveActionCursor(1)
		return nil, false
	case "esc":
		m.resetActionMenu()
		return nil, false
	case "enter":
		return m.handleActionMenuSelection()
	}

	return nil, false
}

func (m *MCPServersModel) moveActionCursor(delta int) {
	if len(m.actionItems) == 0 {
		m.actionCursor = 0
		return
	}
	m.actionCursor = shiftCursor(m.actionCursor, len(m.actionItems), delta)
}

func (m *MCPServersModel) handleActionMenuSelection() (tea.Cmd, bool) {
	if m.actionCursor >= len(m.actionItems) {
		return nil, false
	}
	if len(m.actionItems) == 0 {
		return nil, false
	}

	action := m.actionItems[m.actionCursor]
	m.selectedAction = action
	if action == "Back" {
		m.resetActionMenu()
		return nil, false
	}

	server := m.selectedServer
	target := m.parseActionTarget(action)
	m.resetActionMenu()

	if strings.HasPrefix(action, "Install") {
		if server != nil && (!server.AllPrerequisitesPassed() || !server.AllSecretsPresent()) {
			return func() tea.Msg {
				return MCPShowPrereqMsg{Server: server, Target: target}
			}, false
		}
		return func() tea.Msg {
			return MCPInstallServerMsg{Server: server, Target: target}
		}, false
	}

	if strings.HasPrefix(action, "Remove") {
		return m.removeMCPServerFromTarget(server, target), false
	}

	return nil, false
}

func (m *MCPServersModel) moveMainCursor(delta int) {
	serverCount := len(m.servers)
	menuItemCount := 3 // Setup Secrets + Set Default Target + Back
	total := serverCount + menuItemCount
	if total == 0 {
		m.cursor = 0
		return
	}
	m.cursor = shiftCursor(m.cursor, total, delta)
}

func (m *MCPServersModel) handleMainMenuSelection() (tea.Cmd, bool) {
	serverCount := len(m.servers)
	if m.cursor < serverCount {
		m.showActionMenu(m.servers[m.cursor])
		return nil, false
	}

	menuIndex := m.cursor - serverCount
	switch menuIndex {
	case 0:
		return func() tea.Msg { return MCPShowSecretsWizardMsg{} }, true
	case 1:
		m.openPreferenceMenu()
		return nil, false
	default:
		return nil, true
	}
}

func (m *MCPServersModel) resetActionMenu() {
	m.menuMode = false
	m.selectedServer = nil
	m.actionItems = nil
	m.actionCursor = 0
	m.selectedAction = ""
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
		if m.defaultTarget != "" {
			return m.defaultTarget
		}
		return config.MCPTargetBoth
	}
	if m.cliAvailability.ClaudeInstalled {
		return config.MCPTargetClaude
	}
	return config.MCPTargetCodex
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
