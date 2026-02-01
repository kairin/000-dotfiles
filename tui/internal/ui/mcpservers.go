// Package ui - mcpservers.go provides the MCP Servers management view
package ui

import (
	"fmt"

	"github.com/charmbracelet/bubbles/spinner"
	tea "github.com/charmbracelet/bubbletea"
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
	loading   bool
	loadError string

	// Action feedback
	lastActionMessage string
	lastActionError   bool

	// Action menu state (for individual server selection)
	menuMode       bool
	actionItems    []string
	actionCursor   int
	selectedServer *registry.MCPServer
	selectedAction string // Track which action is selected for context

	// Default CLI target preference
	defaultTarget config.MCPCLITarget

	// Preference menu state
	preferenceMode   bool
	preferenceItems  []string
	preferenceCursor int

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
		claudeStatuses, claudeErr := getClaudeStatuses()
		for serverID, status := range claudeStatuses {
			if dual, ok := statuses[serverID]; ok {
				dual.Claude = status
				statuses[serverID] = dual
			}
		}

		// Check Codex status
		codexStatuses, codexErr := getCodexStatuses()
		for serverID, status := range codexStatuses {
			if dual, ok := statuses[serverID]; ok {
				dual.Codex = status
				statuses[serverID] = dual
			}
		}

		return mcpAllLoadedMsg{statuses: statuses, claudeErr: claudeErr, codexErr: codexErr}
	}
}

// getClaudeStatuses gets MCP server statuses from Claude Code CLI
func getClaudeStatuses() (map[string]MCPServerStatus, error) {
	statuses := make(map[string]MCPServerStatus)
	if !config.IsClaudeInstalled() {
		return statuses, nil
	}

	output, errOutput, err := runClaudeMCPList()
	if err != nil {
		if looksLikeAuthError(errOutput) {
			applyClaudeAuthError(statuses)
			return statuses, fmt.Errorf("Claude not authenticated. Run: claude auth login")
		}
		return statuses, fmt.Errorf("Claude MCP status failed: %v", err)
	}

	return parseClaudeMCPStatuses(output), nil
}

// getCodexStatuses gets MCP server statuses from Codex CLI config
func getCodexStatuses() (map[string]MCPServerStatus, error) {
	statuses := make(map[string]MCPServerStatus)

	if !config.IsCodexInstalled() {
		return statuses, nil
	}

	// Read Codex config directly
	codexServers, err := config.GetCodexMCPServers()
	if err != nil {
		for _, server := range registry.GetAllMCPServers() {
			statuses[server.ID] = MCPServerStatus{
				Connected: false,
				Error:     "config",
			}
		}
		return statuses, fmt.Errorf("Codex config error: %v", err)
	}

	for serverID := range codexServers {
		statuses[serverID] = MCPServerStatus{
			Connected: true,
		}
	}

	return statuses, nil
}

// MCP-specific messages
type (
	mcpAllLoadedMsg struct {
		statuses  map[string]DualMCPStatus
		claudeErr error
		codexErr  error
	}

	mcpInstallResultMsg struct {
		serverID  string
		target    config.MCPCLITarget
		claudeOK  bool
		codexOK   bool
		claudeErr error
		codexErr  error
	}

	mcpRemoveResultMsg struct {
		serverID  string
		target    config.MCPCLITarget
		claudeOK  bool
		codexOK   bool
		claudeErr error
		codexErr  error
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
		return m.handleWindowSize(msg)

	case spinner.TickMsg:
		return m.handleSpinnerTick(msg)

	case mcpAllLoadedMsg:
		return m.handleAllLoaded(msg)

	case mcpInstallResultMsg:
		return m.handleInstallResult(msg)

	case mcpRemoveResultMsg:
		return m.handleRemoveResult(msg)
	}

	return m, nil
}

func (m MCPServersModel) handleWindowSize(msg tea.WindowSizeMsg) (MCPServersModel, tea.Cmd) {
	m.width = msg.Width
	m.height = msg.Height
	return m, nil
}

func (m MCPServersModel) handleSpinnerTick(msg spinner.TickMsg) (MCPServersModel, tea.Cmd) {
	var cmd tea.Cmd
	m.spinner, cmd = m.spinner.Update(msg)
	return m, cmd
}

func (m MCPServersModel) handleAllLoaded(msg mcpAllLoadedMsg) (MCPServersModel, tea.Cmd) {
	m.loadError = ""
	if msg.claudeErr != nil {
		m.loadError = msg.claudeErr.Error()
	}
	if msg.codexErr != nil {
		if m.loadError != "" {
			m.loadError += " | "
		}
		m.loadError += msg.codexErr.Error()
	}
	if msg.statuses != nil {
		m.statuses = msg.statuses
	}
	m.loading = false
	return m, nil
}

func (m MCPServersModel) handleInstallResult(msg mcpInstallResultMsg) (MCPServersModel, tea.Cmd) {
	m.lastActionMessage, m.lastActionError = formatMCPActionResult("Install", msg)
	m.loading = true
	return m, m.refreshMCPStatuses()
}

func (m MCPServersModel) handleRemoveResult(msg mcpRemoveResultMsg) (MCPServersModel, tea.Cmd) {
	m.lastActionMessage, m.lastActionError = formatMCPActionResult("Remove", msg)
	m.loading = true
	return m, m.refreshMCPStatuses()
}
