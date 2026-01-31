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
	headerStyle := lipgloss.NewStyle().
		Foreground(lipgloss.Color("135")). // Magenta for MCP
		Bold(true)
	header := headerStyle.Render(fmt.Sprintf("MCP Servers • %d Servers", registry.MCPServerCount()))
	b.WriteString(header)
	b.WriteString("\n\n")

	if m.loadError != "" {
		b.WriteString(OutputErrorStyle.Render("Error: " + m.loadError))
		b.WriteString("\n\n")
	} else if m.lastActionMessage != "" {
		style := OutputLineStyle
		if m.lastActionError {
			style = OutputErrorStyle
		}
		b.WriteString(style.Render(m.lastActionMessage))
		b.WriteString("\n\n")
	}

	// Status table
	b.WriteString(m.renderServersTable())
	b.WriteString("\n")

	// Show action menu if in menu mode, otherwise show main menu
	if m.preferenceMode {
		b.WriteString(m.renderPreferenceMenu())
	} else if m.menuMode && m.selectedServer != nil {
		b.WriteString(m.renderActionMenu())
	} else {
		b.WriteString(m.renderMCPMenu())
	}
	b.WriteString("\n")

	// Help
	var helpText string
	if m.preferenceMode || m.menuMode {
		helpText = "↑↓ navigate • enter select • esc cancel"
	} else {
		helpText = "↑↓ navigate • enter select • r refresh • esc back"
	}
	help := HelpStyle.Render(helpText)
	b.WriteString(help)

	return b.String()
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
