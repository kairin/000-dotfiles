// Package ui - mcpservers.go provides the MCP Servers management view
package ui

import (
	"fmt"
	"os/exec"
	"strings"

	"github.com/charmbracelet/bubbles/spinner"
	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"
	"github.com/kairin/dotfiles-installer/internal/config"
	"github.com/kairin/dotfiles-installer/internal/registry"
)

// MCPServerStatus represents the connection status of an MCP server for a single CLI
type MCPServerStatus struct {
	Connected bool
	Error     string
}

// DualMCPStatus represents the status of an MCP server in both CLIs
type DualMCPStatus struct {
	Claude MCPServerStatus
	Codex  MCPServerStatus
}

// CLIAvailability tracks which CLIs are installed and usable
type CLIAvailability struct {
	ClaudeInstalled bool
	CodexInstalled  bool
}

// MCPServersModel manages the MCP Servers management view
type MCPServersModel struct {
	// Server selection
	cursor  int
	servers []*registry.MCPServer

	// Status tracking (dual-CLI)
	statuses map[string]DualMCPStatus

	// CLI availability
	cliAvailability CLIAvailability

	// State
	loading bool

	// Action menu state (for individual server selection)
	menuMode       bool
	actionItems    []string
	actionCursor   int
	selectedServer *registry.MCPServer
	selectedAction string // Track which action is selected for context

	// Default CLI target preference
	defaultTarget config.MCPCLITarget

	// Components
	spinner spinner.Model

	// Dimensions
	width  int
	height int
}

// NewMCPServersModel creates a new MCP Servers model
func NewMCPServersModel() MCPServersModel {
	s := spinner.New()
	s.Spinner = spinner.Dot
	s.Style = SpinnerStyle

	// Detect CLI availability
	cliAvail := CLIAvailability{
		ClaudeInstalled: config.IsClaudeInstalled(),
		CodexInstalled:  config.IsCodexInstalled(),
	}

	// Load default target preference
	prefStore := config.NewPreferenceStore()
	defaultTarget, _ := prefStore.GetMCPDefaultTarget()

	return MCPServersModel{
		cursor:          0,
		servers:         registry.GetAllMCPServers(),
		statuses:        make(map[string]DualMCPStatus),
		cliAvailability: cliAvail,
		defaultTarget:   defaultTarget,
		spinner:         s,
		loading:         true,
	}
}

// Init initializes the MCP Servers model
func (m MCPServersModel) Init() tea.Cmd {
	return tea.Batch(
		m.spinner.Tick,
		m.refreshMCPStatuses(),
	)
}

// refreshMCPStatuses returns a command that checks MCP server statuses for both CLIs
func (m MCPServersModel) refreshMCPStatuses() tea.Cmd {
	return func() tea.Msg {
		statuses := make(map[string]DualMCPStatus)

		// Initialize statuses for all servers
		for _, server := range registry.GetAllMCPServers() {
			statuses[server.ID] = DualMCPStatus{}
		}

		// Check Claude status
		claudeStatuses := getClaudeStatuses()
		for serverID, status := range claudeStatuses {
			if dual, ok := statuses[serverID]; ok {
				dual.Claude = status
				statuses[serverID] = dual
			}
		}

		// Check Codex status
		codexStatuses := getCodexStatuses()
		for serverID, status := range codexStatuses {
			if dual, ok := statuses[serverID]; ok {
				dual.Codex = status
				statuses[serverID] = dual
			}
		}

		return mcpAllLoadedMsg{statuses: statuses}
	}
}

// getClaudeStatuses gets MCP server statuses from Claude Code CLI
func getClaudeStatuses() map[string]MCPServerStatus {
	statuses := make(map[string]MCPServerStatus)

	if !config.IsClaudeInstalled() {
		return statuses
	}

	// Run claude mcp list to get current server status
	cmd := exec.Command("claude", "mcp", "list")
	output, err := cmd.Output()
	if err != nil {
		return statuses
	}

	lines := strings.Split(string(output), "\n")
	for _, line := range lines {
		line = strings.TrimSpace(line)
		if line == "" {
			continue
		}

		// Parse format: "server_name: connected" or "server_name: disconnected"
		// Or format with status indicators
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

// getCodexStatuses gets MCP server statuses from Codex CLI config
func getCodexStatuses() map[string]MCPServerStatus {
	statuses := make(map[string]MCPServerStatus)

	if !config.IsCodexInstalled() {
		return statuses
	}

	// Read Codex config directly
	codexServers, err := config.GetCodexMCPServers()
	if err != nil {
		return statuses
	}

	for serverID := range codexServers {
		statuses[serverID] = MCPServerStatus{
			Connected: true,
		}
	}

	return statuses
}

// MCP-specific messages
type (
	mcpAllLoadedMsg struct {
		statuses map[string]DualMCPStatus
		err      error
	}

	mcpInstallResultMsg struct {
		serverID     string
		target       config.MCPCLITarget
		claudeOK     bool
		codexOK      bool
		claudeErr    error
		codexErr     error
	}

	mcpRemoveResultMsg struct {
		serverID     string
		target       config.MCPCLITarget
		claudeOK     bool
		codexOK      bool
		claudeErr    error
		codexErr     error
	}

	// MCPShowPrereqMsg signals that prerequisites view should be shown
	MCPShowPrereqMsg struct {
		Server *registry.MCPServer
		Target config.MCPCLITarget
	}

	// MCPInstallServerMsg signals that a server should be installed (prerequisites passed)
	MCPInstallServerMsg struct {
		Server *registry.MCPServer
		Target config.MCPCLITarget
	}

	// MCPShowSecretsWizardMsg signals that secrets wizard should be shown
	MCPShowSecretsWizardMsg struct{}
)

// Update handles messages for the MCP Servers model
func (m MCPServersModel) Update(msg tea.Msg) (MCPServersModel, tea.Cmd) {
	switch msg := msg.(type) {
	case tea.WindowSizeMsg:
		m.width = msg.Width
		m.height = msg.Height
		return m, nil

	case spinner.TickMsg:
		var cmd tea.Cmd
		m.spinner, cmd = m.spinner.Update(msg)
		return m, cmd

	case mcpAllLoadedMsg:
		if msg.err == nil && msg.statuses != nil {
			m.statuses = msg.statuses
		}
		m.loading = false
		return m, nil

	case mcpInstallResultMsg:
		// Refresh status after install
		m.loading = true
		return m, m.refreshMCPStatuses()

	case mcpRemoveResultMsg:
		// Refresh status after remove
		m.loading = true
		return m, m.refreshMCPStatuses()
	}

	return m, nil
}

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

	// Status table
	b.WriteString(m.renderServersTable())
	b.WriteString("\n")

	// Show action menu if in menu mode, otherwise show main menu
	if m.menuMode && m.selectedServer != nil {
		b.WriteString(m.renderActionMenu())
	} else {
		b.WriteString(m.renderMCPMenu())
	}
	b.WriteString("\n")

	// Help
	var helpText string
	if m.menuMode {
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

	// Servers
	for i, server := range m.servers {
		// Determine Claude status display
		var claudeStr, codexStr string
		var claudeStyle, codexStyle lipgloss.Style

		if m.loading {
			claudeStr = m.spinner.View()
			claudeStyle = StatusUnknownStyle
			codexStr = m.spinner.View()
			codexStyle = StatusUnknownStyle
		} else {
			// Claude status
			if !m.cliAvailability.ClaudeInstalled {
				claudeStr = "N/A"
				claudeStyle = StatusUnknownStyle
			} else {
				status, hasStatus := m.statuses[server.ID]
				if hasStatus && status.Claude.Connected {
					claudeStr = IconCheckmark + " Added"
					claudeStyle = StatusInstalledStyle
				} else {
					claudeStr = IconCross + " Missing"
					claudeStyle = StatusMissingStyle
				}
			}

			// Codex status
			if !m.cliAvailability.CodexInstalled {
				codexStr = "N/A"
				codexStyle = StatusUnknownStyle
			} else {
				status, hasStatus := m.statuses[server.ID]
				if hasStatus && status.Codex.Connected {
					codexStr = IconCheckmark + " Added"
					codexStyle = StatusInstalledStyle
				} else {
					codexStr = IconCross + " Missing"
					codexStyle = StatusMissingStyle
				}
			}
		}

		// Format row
		rowStyle := TableRowStyle
		if i == m.cursor && m.cursor < len(m.servers) {
			rowStyle = TableSelectedStyle
		}

		// Truncate description if needed
		desc := server.Description
		if len(desc) > colDescription {
			desc = desc[:colDescription-3] + "..."
		}

		row := fmt.Sprintf("%-*s %-*s %-*s %-*s",
			colServer, server.DisplayName,
			colClaude, claudeStyle.Render(claudeStr),
			colCodex, codexStyle.Render(codexStr),
			colDescription, desc,
		)
		b.WriteString(rowStyle.Render(row))
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
	menuItems := []string{"Setup Secrets", "Back"}

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

// HandleKey processes key presses in MCP Servers view
func (m *MCPServersModel) HandleKey(msg tea.KeyMsg) (tea.Cmd, bool) {
	// Handle action menu mode separately
	if m.menuMode {
		return m.handleActionMenuKey(msg)
	}

	// Calculate menu boundaries
	serverCount := len(m.servers)
	menuItemCount := 2 // Setup Secrets + Back
	maxCursor := serverCount + menuItemCount - 1

	switch msg.String() {
	case "up", "k":
		if m.cursor > 0 {
			m.cursor--
		} else {
			m.cursor = maxCursor // Wrap to bottom
		}
		return nil, false

	case "down", "j":
		if m.cursor < maxCursor {
			m.cursor++
		} else {
			m.cursor = 0 // Wrap to top
		}
		return nil, false

	case "r":
		// Refresh status
		m.loading = true
		return m.refreshMCPStatuses(), false

	case "enter":
		// Handle selection
		if m.cursor < serverCount {
			// Selected a server - show action menu
			m.showActionMenu(m.servers[m.cursor])
			return nil, false
		} else if m.cursor == serverCount {
			// "Setup Secrets" selected
			return func() tea.Msg {
				return MCPShowSecretsWizardMsg{}
			}, false
		} else {
			// "Back" selected
			return nil, true
		}
	}

	return nil, false
}

// showActionMenu prepares and displays the action menu for a server
func (m *MCPServersModel) showActionMenu(server *registry.MCPServer) {
	m.selectedServer = server
	m.menuMode = true
	m.actionCursor = 0

	// Build action items based on server status and CLI availability
	status, hasStatus := m.statuses[server.ID]
	claudeInstalled := m.cliAvailability.ClaudeInstalled
	codexInstalled := m.cliAvailability.CodexInstalled

	m.actionItems = []string{}

	// Determine if server is installed in each CLI
	claudeAdded := hasStatus && status.Claude.Connected
	codexAdded := hasStatus && status.Codex.Connected

	// Add install options
	if claudeInstalled && codexInstalled {
		// Both CLIs available
		if !claudeAdded && !codexAdded {
			// Not in either - offer all install options
			m.actionItems = append(m.actionItems, "Install (Both)")
			m.actionItems = append(m.actionItems, "Install (Claude only)")
			m.actionItems = append(m.actionItems, "Install (Codex only)")
		} else if !claudeAdded {
			// Only missing from Claude
			m.actionItems = append(m.actionItems, "Install (Claude only)")
		} else if !codexAdded {
			// Only missing from Codex
			m.actionItems = append(m.actionItems, "Install (Codex only)")
		}
	} else if claudeInstalled && !codexInstalled {
		// Only Claude available
		if !claudeAdded {
			m.actionItems = append(m.actionItems, "Install (Claude)")
		}
	} else if !claudeInstalled && codexInstalled {
		// Only Codex available
		if !codexAdded {
			m.actionItems = append(m.actionItems, "Install (Codex)")
		}
	}

	// Add remove options
	if claudeInstalled && claudeAdded {
		m.actionItems = append(m.actionItems, "Remove (Claude)")
	}
	if codexInstalled && codexAdded {
		m.actionItems = append(m.actionItems, "Remove (Codex)")
	}
	if claudeInstalled && codexInstalled && claudeAdded && codexAdded {
		// Offer bulk remove if in both
		m.actionItems = append(m.actionItems, "Remove (Both)")
	}

	m.actionItems = append(m.actionItems, "Back")

	// Set default cursor based on user preference
	m.setDefaultActionCursor()
}

// setDefaultActionCursor sets the cursor to the user's preferred default option
func (m *MCPServersModel) setDefaultActionCursor() {
	// Map preference to action item prefix
	var targetPrefix string
	switch m.defaultTarget {
	case config.MCPTargetBoth:
		targetPrefix = "(Both)"
	case config.MCPTargetClaude:
		targetPrefix = "(Claude"
	case config.MCPTargetCodex:
		targetPrefix = "(Codex"
	default:
		targetPrefix = "(Both)"
	}

	// Find matching install action
	for i, item := range m.actionItems {
		if strings.HasPrefix(item, "Install") && strings.Contains(item, targetPrefix) {
			m.actionCursor = i
			return
		}
	}
	// Default to first item
	m.actionCursor = 0
}

// handleActionMenuKey processes key presses when in action menu mode
func (m *MCPServersModel) handleActionMenuKey(msg tea.KeyMsg) (tea.Cmd, bool) {
	switch msg.String() {
	case "up", "k":
		if m.actionCursor > 0 {
			m.actionCursor--
		} else {
			m.actionCursor = len(m.actionItems) - 1 // Wrap to bottom
		}
		return nil, false

	case "down", "j":
		if m.actionCursor < len(m.actionItems)-1 {
			m.actionCursor++
		} else {
			m.actionCursor = 0 // Wrap to top
		}
		return nil, false

	case "esc":
		// Cancel action menu
		m.menuMode = false
		m.selectedServer = nil
		m.actionItems = nil
		m.actionCursor = 0
		return nil, false

	case "enter":
		// Execute selected action
		if m.actionCursor < len(m.actionItems) {
			action := m.actionItems[m.actionCursor]

			// Determine target from action string
			target := m.parseActionTarget(action)

			if strings.HasPrefix(action, "Install") {
				server := m.selectedServer
				m.menuMode = false
				m.selectedServer = nil
				m.actionItems = nil
				m.actionCursor = 0

				// Check prerequisites first
				if !server.AllPrerequisitesPassed() || !server.AllSecretsPresent() {
					// Show prerequisites view
					return func() tea.Msg {
						return MCPShowPrereqMsg{Server: server, Target: target}
					}, false
				}

				// Prerequisites passed - install directly
				m.loading = true
				return m.installMCPServerToTarget(server, target), false

			} else if strings.HasPrefix(action, "Remove") {
				cmd := m.removeMCPServerFromTarget(m.selectedServer, target)
				m.menuMode = false
				m.selectedServer = nil
				m.actionItems = nil
				m.actionCursor = 0
				m.loading = true
				return cmd, false

			} else if action == "Back" {
				m.menuMode = false
				m.selectedServer = nil
				m.actionItems = nil
				m.actionCursor = 0
				return nil, false
			}
		}
	}

	return nil, false
}

// parseActionTarget extracts the CLI target from an action string
func (m *MCPServersModel) parseActionTarget(action string) config.MCPCLITarget {
	if strings.Contains(action, "(Both)") {
		return config.MCPTargetBoth
	} else if strings.Contains(action, "(Claude") {
		return config.MCPTargetClaude
	} else if strings.Contains(action, "(Codex") {
		return config.MCPTargetCodex
	}
	// Default based on what's available
	if m.cliAvailability.ClaudeInstalled && m.cliAvailability.CodexInstalled {
		return config.MCPTargetBoth
	} else if m.cliAvailability.ClaudeInstalled {
		return config.MCPTargetClaude
	}
	return config.MCPTargetCodex
}

// installMCPServerToTarget returns a command to install an MCP server to the specified target(s)
func (m *MCPServersModel) installMCPServerToTarget(server *registry.MCPServer, target config.MCPCLITarget) tea.Cmd {
	return func() tea.Msg {
		result := mcpInstallResultMsg{
			serverID: server.ID,
			target:   target,
		}

		// Install to Claude if needed
		if target == config.MCPTargetBoth || target == config.MCPTargetClaude {
			args := server.GetAddCommand()
			cmd := exec.Command("claude", args...)
			err := cmd.Run()
			result.claudeOK = (err == nil)
			result.claudeErr = err
		}

		// Install to Codex if needed
		if target == config.MCPTargetBoth || target == config.MCPTargetCodex {
			codexServer := config.CodexMCPServer{
				Command:           server.CodexConfig.Command,
				Args:              server.CodexConfig.Args,
				URL:               server.CodexConfig.URL,
				BearerTokenEnvVar: server.CodexConfig.BearerTokenEnvVar,
			}
			err := config.AddCodexMCPServer(server.ID, codexServer)
			result.codexOK = (err == nil)
			result.codexErr = err
		}

		return result
	}
}

// removeMCPServerFromTarget returns a command to remove an MCP server from the specified target(s)
func (m *MCPServersModel) removeMCPServerFromTarget(server *registry.MCPServer, target config.MCPCLITarget) tea.Cmd {
	return func() tea.Msg {
		result := mcpRemoveResultMsg{
			serverID: server.ID,
			target:   target,
		}

		// Remove from Claude if needed
		if target == config.MCPTargetBoth || target == config.MCPTargetClaude {
			args := server.GetRemoveCommand()
			cmd := exec.Command("claude", args...)
			err := cmd.Run()
			result.claudeOK = (err == nil)
			result.claudeErr = err
		}

		// Remove from Codex if needed
		if target == config.MCPTargetBoth || target == config.MCPTargetCodex {
			err := config.RemoveCodexMCPServer(server.ID)
			result.codexOK = (err == nil)
			result.codexErr = err
		}

		return result
	}
}

// GetSelectedServer returns the currently selected server, or nil for menu items
func (m MCPServersModel) GetSelectedServer() *registry.MCPServer {
	if m.cursor < len(m.servers) {
		return m.servers[m.cursor]
	}
	return nil
}

// IsSetupSecretsSelected returns true if "Setup Secrets" is selected
func (m MCPServersModel) IsSetupSecretsSelected() bool {
	return m.cursor == len(m.servers)
}

// IsBackSelected returns true if "Back" is selected
func (m MCPServersModel) IsBackSelected() bool {
	return m.cursor == len(m.servers)+1
}
