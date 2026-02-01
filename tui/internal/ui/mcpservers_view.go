// Package ui - mcpservers_view.go provides MCP Servers view rendering
package ui

import (
	"fmt"
	"strings"

	"github.com/charmbracelet/lipgloss"
	"github.com/kairin/dotfiles-installer/internal/registry"
)

// View renders the MCP Servers management dashboard
func (m MCPServersModel) View() string {
	var b strings.Builder

	// Header (magenta styling for MCP)
	b.WriteString(m.renderHeader())
	b.WriteString("\n\n")

	b.WriteString(m.renderStatusBanner())

	// Status table
	b.WriteString(m.renderServersTable())
	b.WriteString("\n")

	b.WriteString(m.renderMenu())
	b.WriteString("\n")

	// Help
	b.WriteString(m.renderHelp())

	return b.String()
}

func (m MCPServersModel) renderHeader() string {
	headerStyle := lipgloss.NewStyle().
		Foreground(lipgloss.Color("135")). // Magenta for MCP
		Bold(true)
	return headerStyle.Render(fmt.Sprintf("MCP Servers • %d Servers", registry.MCPServerCount()))
}

func (m MCPServersModel) renderStatusBanner() string {
	if m.loadError != "" {
		return OutputErrorStyle.Render("Error: "+m.loadError) + "\n\n"
	}
	if m.lastActionMessage != "" {
		style := OutputLineStyle
		if m.lastActionError {
			style = OutputErrorStyle
		}
		return style.Render(m.lastActionMessage) + "\n\n"
	}
	return ""
}

func (m MCPServersModel) renderMenu() string {
	if m.preferenceMode {
		return m.renderPreferenceMenu()
	}
	if m.menuMode && m.selectedServer != nil {
		return m.renderActionMenu()
	}
	return m.renderMCPMenu()
}

func (m MCPServersModel) renderHelp() string {
	if m.preferenceMode || m.menuMode {
		return HelpStyle.Render("↑↓ navigate • enter select • esc cancel")
	}
	return HelpStyle.Render("↑↓ navigate • enter select • r refresh • esc back")
}

// renderServersTable renders the MCP servers status table with dual-CLI columns
func (m MCPServersModel) renderServersTable() string {
	var b strings.Builder

	// Column widths - adjusted for dual-CLI display
	colServer := 12
	colClaude := 10
	colCodex := 10
	colDescription := 30

	// Show CLI availability in header
	claudeHeader := "CLAUDE"
	codexHeader := "CODEX"
	if !m.cliAvailability.ClaudeInstalled {
		claudeHeader = "CLAUDE" // Will show N/A in cells
	}
	if !m.cliAvailability.CodexInstalled {
		codexHeader = "CODEX" // Will show N/A in cells
	}

	// Header
	headerLine := fmt.Sprintf("%-*s %-*s %-*s %-*s",
		colServer, "SERVER",
		colClaude, claudeHeader,
		colCodex, codexHeader,
		colDescription, "DESCRIPTION",
	)
	b.WriteString(TableHeaderStyle.Render(headerLine))
	b.WriteString("\n")

	// Separator
	sep := strings.Repeat("─", colServer+colClaude+colCodex+colDescription+3)
	b.WriteString(lipgloss.NewStyle().Foreground(ColorMuted).Render(sep))
	b.WriteString("\n")

	for i, server := range m.servers {
		row := m.renderServerRow(i, server, colServer, colClaude, colCodex, colDescription)
		b.WriteString(row)
		b.WriteString("\n")
	}

	// Box with magenta border for MCP
	boxStyle := lipgloss.NewStyle().
		BorderStyle(lipgloss.RoundedBorder()).
		BorderForeground(lipgloss.Color("135")). // Magenta
		Padding(1, 2)

	return boxStyle.Render(b.String())
}

// renderMCPMenu renders the MCP menu options
func (m MCPServersModel) renderMCPMenu() string {
	var b strings.Builder

	serverCount := len(m.servers)

	// Menu items: Individual servers (0-6) + "Setup Secrets" (7) + "Back" (8)
	menuItems := []string{"Setup Secrets", "Set Default Target", "Back"}

	b.WriteString("\nChoose:\n")

	// Render menu items
	menuStartIndex := serverCount
	for i, item := range menuItems {
		cursor := " "
		style := MenuItemStyle
		if m.cursor == menuStartIndex+i {
			cursor = ">"
			style = MenuSelectedStyle
		}
		b.WriteString(fmt.Sprintf("%s %s\n", MenuCursorStyle.Render(cursor), style.Render(item)))
	}

	return b.String()
}

// renderActionMenu renders the action menu for a selected server
func (m MCPServersModel) renderActionMenu() string {
	var b strings.Builder

	// Show which server is selected
	serverStyle := lipgloss.NewStyle().
		Foreground(lipgloss.Color("135")). // Magenta
		Bold(true)
	b.WriteString(fmt.Sprintf("\nActions for %s:\n", serverStyle.Render(m.selectedServer.DisplayName)))

	// Render action items
	for i, item := range m.actionItems {
		cursor := " "
		style := MenuItemStyle
		if i == m.actionCursor {
			cursor = ">"
			style = MenuSelectedStyle
		}
		b.WriteString(fmt.Sprintf("%s %s\n", MenuCursorStyle.Render(cursor), style.Render(item)))
	}

	return b.String()
}
