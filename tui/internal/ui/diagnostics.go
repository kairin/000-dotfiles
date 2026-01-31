// Package ui - diagnostics.go provides the boot diagnostics view
package ui

import (
	"context"
	"fmt"
	"strings"
	"time"

	"github.com/charmbracelet/bubbles/spinner"
	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"
	"github.com/kairin/dotfiles-installer/internal/diagnostics"
)

// DiagnosticsState represents the current state of diagnostics view
type DiagnosticsState int

const (
	DiagnosticsIdle DiagnosticsState = iota
	DiagnosticsScanning
	DiagnosticsShowingResults
	DiagnosticsFixing
	DiagnosticsFixComplete
)

// DiagnosticsModel manages the boot diagnostics view
type DiagnosticsModel struct {
	// State
	state   DiagnosticsState
	issues  []*diagnostics.Issue
	grouped map[diagnostics.IssueSeverity][]*diagnostics.Issue

	// Selection
	cursor   int
	selected map[int]bool // Multi-select for fixes

	// Cache
	cacheStore *diagnostics.CacheStore

	// Fixer
	fixer     *diagnostics.Fixer
	fixResult *diagnostics.BatchFixResult

	// Components
	spinner spinner.Model

	// Detector progress tracking (for verbose scanning view)
	detectorInfos    []diagnostics.DetectorInfo // Metadata for all 5 detectors
	detectorSpinners []spinner.Model            // Individual spinners for each detector
	progressChan     chan diagnostics.DetectorProgress
	issuesFoundSoFar int // Running count of issues found during scan

	// Config
	repoRoot   string
	demoMode   bool
	sudoCached bool

	// Dimensions
	width  int
	height int

	// Scan metadata
	lastScan  time.Time
	scanError error
}

// NewDiagnosticsModel creates a new diagnostics model
func NewDiagnosticsModel(repoRoot string, demoMode, sudoCached bool) DiagnosticsModel {
	s := spinner.New()
	s.Spinner = spinner.Dot
	s.Style = SpinnerStyle

	// Create individual spinners for each detector
	detectorInfos := diagnostics.GetDetectorInfos()
	detectorSpinners := make([]spinner.Model, len(detectorInfos))
	for i := range detectorSpinners {
		ds := spinner.New()
		ds.Spinner = spinner.Dot
		ds.Style = SpinnerStyle
		detectorSpinners[i] = ds
	}

	return DiagnosticsModel{
		state:            DiagnosticsIdle,
		selected:         make(map[int]bool),
		cacheStore:       diagnostics.NewCacheStore(),
		fixer:            diagnostics.NewFixer(repoRoot, demoMode, sudoCached),
		spinner:          s,
		detectorInfos:    detectorInfos,
		detectorSpinners: detectorSpinners,
		repoRoot:         repoRoot,
		demoMode:         demoMode,
		sudoCached:       sudoCached,
	}
}

// Diagnostics message types
type (
	// diagnosticsScanStartMsg initiates a scan
	diagnosticsScanStartMsg struct{}

	// diagnosticsScanCompleteMsg signals scan completion
	diagnosticsScanCompleteMsg struct {
		issues []*diagnostics.Issue
		err    error
	}

	// diagnosticsDetectorProgressMsg reports progress from a single detector
	diagnosticsDetectorProgressMsg struct {
		progress diagnostics.DetectorProgress
	}

	// diagnosticsFixStartMsg initiates fix execution
	diagnosticsFixStartMsg struct{}

	// diagnosticsFixCompleteMsg signals fix completion
	diagnosticsFixCompleteMsg struct {
		result *diagnostics.BatchFixResult
	}
)

// Init initializes the diagnostics model
func (m DiagnosticsModel) Init() tea.Cmd {
	// Check if we have valid cache
	if cached := m.cacheStore.Get(); cached != nil {
		m.issues = cached.Issues
		m.grouped = diagnostics.GroupBySeverity(m.issues)
		m.lastScan = cached.Timestamp
		m.state = DiagnosticsShowingResults
		return m.spinner.Tick
	}

	// Start a new scan
	return tea.Batch(
		m.spinner.Tick,
		func() tea.Msg { return diagnosticsScanStartMsg{} },
	)
}

// Update handles messages for the diagnostics model
func (m DiagnosticsModel) Update(msg tea.Msg) (DiagnosticsModel, tea.Cmd) {
	var cmds []tea.Cmd

	switch msg := msg.(type) {
	case tea.WindowSizeMsg:
		m.width = msg.Width
		m.height = msg.Height
		return m, nil

	case spinner.TickMsg:
		if m.state == DiagnosticsScanning || m.state == DiagnosticsFixing {
			// Update main spinner
			var cmd tea.Cmd
			m.spinner, cmd = m.spinner.Update(msg)
			cmds = append(cmds, cmd)

			// Update individual detector spinners for running detectors
			if m.state == DiagnosticsScanning {
				for i := range m.detectorSpinners {
					if m.detectorInfos[i].Status == diagnostics.DetectorRunning {
						var spinnerCmd tea.Cmd
						m.detectorSpinners[i], spinnerCmd = m.detectorSpinners[i].Update(msg)
						if spinnerCmd != nil {
							cmds = append(cmds, spinnerCmd)
						}
					}
				}
			}
		}
		return m, tea.Batch(cmds...)

	case diagnosticsScanStartMsg:
		m.state = DiagnosticsScanning
		m.scanError = nil
		m.issuesFoundSoFar = 0
		// Reset detector infos to pending
		m.detectorInfos = diagnostics.GetDetectorInfos()
		// Create progress channel
		m.progressChan = make(chan diagnostics.DetectorProgress, 10)
		return m, tea.Batch(
			m.spinner.Tick,
			m.runScanWithProgress(),
			m.readDetectorProgress(),
		)

	case diagnosticsDetectorProgressMsg:
		// Update the detector info with progress
		idx := msg.progress.DetectorID
		if idx >= 0 && idx < len(m.detectorInfos) {
			m.detectorInfos[idx].Status = msg.progress.Status
			m.detectorInfos[idx].IssueCount = msg.progress.IssueCount
			m.detectorInfos[idx].Error = msg.progress.Error
			m.detectorInfos[idx].Duration = msg.progress.Duration

			// Update running issue count when a detector completes
			if msg.progress.Status == diagnostics.DetectorComplete {
				m.issuesFoundSoFar += msg.progress.IssueCount
			}
		}
		// Continue reading progress if still scanning
		if m.state == DiagnosticsScanning {
			cmds = append(cmds, m.readDetectorProgress())
		}
		return m, tea.Batch(cmds...)

	case diagnosticsScanCompleteMsg:
		m.state = DiagnosticsShowingResults
		if msg.err != nil {
			m.scanError = msg.err
		} else {
			m.issues = msg.issues
			m.grouped = diagnostics.GroupBySeverity(m.issues)
			m.lastScan = time.Now()
		}
		// Close progress channel
		if m.progressChan != nil {
			close(m.progressChan)
			m.progressChan = nil
		}
		return m, nil

	case diagnosticsFixStartMsg:
		if len(m.selected) == 0 {
			return m, nil
		}
		m.state = DiagnosticsFixing
		return m, tea.Batch(
			m.spinner.Tick,
			m.runFix(),
		)

	case diagnosticsFixCompleteMsg:
		m.state = DiagnosticsFixComplete
		m.fixResult = msg.result
		// Clear selections after fix
		m.selected = make(map[int]bool)
		// Invalidate cache to force rescan
		m.cacheStore.Clear()
		return m, nil
	}

	return m, tea.Batch(cmds...)
}

// runScan executes the diagnostic scan (legacy - kept for compatibility)
func (m DiagnosticsModel) runScan() tea.Cmd {
	repoRoot := m.repoRoot
	cacheStore := m.cacheStore

	return func() tea.Msg {
		ctx := context.Background()
		result := diagnostics.RunFullScan(ctx, repoRoot)

		// Save to cache
		cacheStore.Save(result)

		return diagnosticsScanCompleteMsg{
			issues: result.Issues,
			err:    nil,
		}
	}
}

// runScanWithProgress executes the diagnostic scan with progress updates
func (m DiagnosticsModel) runScanWithProgress() tea.Cmd {
	repoRoot := m.repoRoot
	cacheStore := m.cacheStore
	progressChan := m.progressChan

	return func() tea.Msg {
		ctx := context.Background()
		result := diagnostics.RunDetectorsWithProgress(ctx, repoRoot, progressChan)

		// Create a ScanResult for caching
		scanResult := &diagnostics.ScanResult{
			Issues:        result.Issues,
			Errors:        result.Errors,
			ScanTime:      time.Now(),
			ScriptsRan:    5,
			ScriptsFailed: len(result.Errors),
		}

		// Save to cache
		cacheStore.Save(scanResult)

		return diagnosticsScanCompleteMsg{
			issues: result.Issues,
			err:    nil,
		}
	}
}

// readDetectorProgress reads progress updates from the progress channel
func (m DiagnosticsModel) readDetectorProgress() tea.Cmd {
	progressChan := m.progressChan
	if progressChan == nil {
		return nil
	}

	return func() tea.Msg {
		progress, ok := <-progressChan
		if !ok {
			return nil
		}
		return diagnosticsDetectorProgressMsg{progress: progress}
	}
}

// runFix executes selected fixes
func (m DiagnosticsModel) runFix() tea.Cmd {
	// Collect selected issues
	selectedIssues := make([]*diagnostics.Issue, 0)
	allIssues := m.getFlatIssueList()
	for idx := range m.selected {
		if idx >= 0 && idx < len(allIssues) {
			selectedIssues = append(selectedIssues, allIssues[idx])
		}
	}

	fixer := m.fixer

	return func() tea.Msg {
		ctx := context.Background()
		result := fixer.ExecuteBatch(ctx, selectedIssues)
		return diagnosticsFixCompleteMsg{result: result}
	}
}

// getFlatIssueList returns all issues in a flat list (for cursor indexing)
func (m DiagnosticsModel) getFlatIssueList() []*diagnostics.Issue {
	flat := make([]*diagnostics.Issue, 0)
	// Order: Critical, then Moderate, then Low
	for _, sev := range []diagnostics.IssueSeverity{
		diagnostics.SeverityCritical,
		diagnostics.SeverityModerate,
		diagnostics.SeverityLow,
	} {
		flat = append(flat, m.grouped[sev]...)
	}
	return flat
}

// View renders the diagnostics view
func (m DiagnosticsModel) View() string {
	var b strings.Builder

	// Header
	header := HeaderStyle.Render("Boot Diagnostics")
	b.WriteString(header)
	b.WriteString("\n\n")

	// State-specific content
	switch m.state {
	case DiagnosticsScanning:
		b.WriteString(m.renderScanningProgress())

	case DiagnosticsFixing:
		b.WriteString(m.spinner.View())
		b.WriteString(" Applying fixes...")
		b.WriteString("\n\n")
		b.WriteString(DetailStyle.Render(fmt.Sprintf("Fixing %d selected issues", len(m.selected))))

	case DiagnosticsShowingResults:
		b.WriteString(m.renderResults())

	case DiagnosticsFixComplete:
		b.WriteString(m.renderFixResults())

	default:
		b.WriteString("Initializing...")
	}

	b.WriteString("\n\n")
	b.WriteString(m.renderHelp())

	return b.String()
}

// renderScanningProgress renders the verbose per-detector progress view
func (m DiagnosticsModel) renderScanningProgress() string {
	var b strings.Builder

	// Header line with main spinner
	b.WriteString(m.spinner.View())
	b.WriteString(" Scanning for boot issues...\n\n")

	// Count completed detectors
	completedCount := 0
	for _, info := range m.detectorInfos {
		if info.Status == diagnostics.DetectorComplete ||
			info.Status == diagnostics.DetectorFailed ||
			info.Status == diagnostics.DetectorTimedOut {
			completedCount++
		}
	}

	// Render each detector with its status
	for i, info := range m.detectorInfos {
		b.WriteString("  ")

		// Status icon/spinner
		switch info.Status {
		case diagnostics.DetectorPending:
			// Gray pending indicator
			b.WriteString(StatusUnknownStyle.Render("○ "))
		case diagnostics.DetectorRunning:
			// Animated spinner
			b.WriteString(m.detectorSpinners[i].View())
			b.WriteString(" ")
		case diagnostics.DetectorComplete:
			// Green checkmark
			b.WriteString(StatusInstalledStyle.Render(IconCheckmark + " "))
		case diagnostics.DetectorFailed, diagnostics.DetectorTimedOut:
			// Red X
			b.WriteString(StatusMissingStyle.Render(IconCross + " "))
		}

		// Detector name (fixed width for alignment)
		nameStyle := lipgloss.NewStyle().Width(20)
		if info.Status == diagnostics.DetectorRunning {
			b.WriteString(SpinnerStyle.Render(nameStyle.Render(info.DisplayName)))
		} else {
			b.WriteString(nameStyle.Render(info.DisplayName))
		}

		// Description
		b.WriteString(DetailStyle.Render(info.Description))

		b.WriteString("\n")
	}

	b.WriteString("\n")

	// Progress summary line
	progressLine := fmt.Sprintf("Progress: %d/5 complete", completedCount)
	if m.issuesFoundSoFar > 0 {
		progressLine += fmt.Sprintf(" | Found %d issue", m.issuesFoundSoFar)
		if m.issuesFoundSoFar != 1 {
			progressLine += "s"
		}
		progressLine += " so far"
	}
	b.WriteString(DetailStyle.Render(progressLine))

	return b.String()
}

// renderResults renders the issue list grouped by severity
func (m DiagnosticsModel) renderResults() string {
	var b strings.Builder

	// Cache age indicator
	cacheAge := m.cacheStore.AgeString()
	if m.cacheStore.WasRebootDetected() {
		cacheAge = "reboot detected, needs rescan"
	}
	b.WriteString(DetailStyle.Render(fmt.Sprintf("Last scan: %s (%d issues found)", cacheAge, len(m.issues))))
	b.WriteString("\n\n")

	if len(m.issues) == 0 {
		b.WriteString(StatusInstalledStyle.Render(fmt.Sprintf("%s No boot issues detected!", IconCheckmark)))
		return b.String()
	}

	// Render by severity
	flatIndex := 0
	for _, sev := range []diagnostics.IssueSeverity{
		diagnostics.SeverityCritical,
		diagnostics.SeverityModerate,
		diagnostics.SeverityLow,
	} {
		issues := m.grouped[sev]
		if len(issues) == 0 {
			continue
		}

		// Severity header
		var sevStyle lipgloss.Style
		var sevIcon string
		switch sev {
		case diagnostics.SeverityCritical:
			sevStyle = SeverityCriticalStyle
			sevIcon = IconCross
		case diagnostics.SeverityModerate:
			sevStyle = SeverityModerateStyle
			sevIcon = IconWarning
		case diagnostics.SeverityLow:
			sevStyle = SeverityLowStyle
			sevIcon = IconCircle
		}

		b.WriteString(sevStyle.Render(fmt.Sprintf("%s %s (%d):", sevIcon, sev.String(), len(issues))))
		b.WriteString("\n")

		// Render issues
		for _, issue := range issues {
			// Selection indicator
			selectMarker := "  "
			if m.selected[flatIndex] {
				selectMarker = "✓ "
			}

			// Cursor indicator
			cursor := "  "
			if m.cursor == flatIndex {
				cursor = "> "
			}

			// Issue line
			issueStyle := TableRowStyle
			if m.cursor == flatIndex {
				issueStyle = TableSelectedStyle
			}

			issueLine := fmt.Sprintf("%s%s%s - %s",
				cursor, selectMarker, issue.Name, issue.Description)
			b.WriteString(issueStyle.Render(issueLine))
			b.WriteString("\n")

			// Fix command line
			if issue.FixCommand != "" {
				fixStyle := IssueNotFixableStyle
				if issue.IsFixable() {
					fixStyle = IssueFixableStyle
				}
				fixLine := fmt.Sprintf("      [%s] %s", issue.Fixable, issue.FixCommand)
				b.WriteString(fixStyle.Render(fixLine))
				b.WriteString("\n")
			}

			flatIndex++
		}
		b.WriteString("\n")
	}

	// Selection summary
	if len(m.selected) > 0 {
		b.WriteString(StatusUpdateStyle.Render(fmt.Sprintf("%d issues selected for fixing", len(m.selected))))
	}

	return b.String()
}

// renderFixResults renders the fix operation results
func (m DiagnosticsModel) renderFixResults() string {
	var b strings.Builder

	if m.fixResult == nil {
		return "No fix results available"
	}

	// Summary
	if m.fixResult.AllSuccessful() {
		b.WriteString(StatusInstalledStyle.Render(fmt.Sprintf("%s All fixes applied successfully!", IconCheckmark)))
	} else {
		b.WriteString(StatusUpdateStyle.Render(fmt.Sprintf(
			"%s Fixed: %d, Failed: %d",
			IconWarning,
			m.fixResult.TotalFixed,
			m.fixResult.TotalFailed,
		)))
	}
	b.WriteString("\n\n")

	// User-level results
	if len(m.fixResult.UserLevel) > 0 {
		b.WriteString("User-level fixes:\n")
		for _, res := range m.fixResult.UserLevel {
			icon := IconCheckmark
			style := StatusInstalledStyle
			if !res.Success {
				icon = IconCross
				style = StatusMissingStyle
			}
			b.WriteString(style.Render(fmt.Sprintf("  %s %s", icon, res.Issue.Name)))
			b.WriteString("\n")
		}
		b.WriteString("\n")
	}

	// Sudo-level results
	if len(m.fixResult.SudoLevel) > 0 {
		b.WriteString("System-level fixes:\n")
		for _, res := range m.fixResult.SudoLevel {
			icon := IconCheckmark
			style := StatusInstalledStyle
			if !res.Success {
				icon = IconCross
				style = StatusMissingStyle
			}
			b.WriteString(style.Render(fmt.Sprintf("  %s %s", icon, res.Issue.Name)))
			b.WriteString("\n")
		}
		b.WriteString("\n")
	}

	// Reboot recommendation
	if m.fixResult.NeedsReboot {
		b.WriteString(WarningBoxStyle.Render(fmt.Sprintf("%s Reboot recommended to apply changes", IconWarning)))
	}

	return b.String()
}

// renderHelp renders context-sensitive help
func (m DiagnosticsModel) renderHelp() string {
	switch m.state {
	case DiagnosticsScanning, DiagnosticsFixing:
		return HelpStyle.Render("[ESC] Cancel")

	case DiagnosticsShowingResults:
		help := "↑↓ navigate • space select • [F] fix selected • [R] rescan • [ESC] back"
		return HelpStyle.Render(help)

	case DiagnosticsFixComplete:
		return HelpStyle.Render("[R] Rescan • [ESC] Back")

	default:
		return HelpStyle.Render("[ESC] Back")
	}
}

// HandleKey processes key presses in diagnostics view
func (m *DiagnosticsModel) HandleKey(msg tea.KeyMsg) tea.Cmd {
	switch m.state {
	case DiagnosticsShowingResults:
		return m.handleResultsKey(msg)
	case DiagnosticsFixComplete:
		return m.handleFixCompleteKey(msg)
	}
	return nil
}

// handleResultsKey handles keys when showing results
func (m *DiagnosticsModel) handleResultsKey(msg tea.KeyMsg) tea.Cmd {
	flatList := m.getFlatIssueList()
	maxCursor := len(flatList) - 1

	switch msg.String() {
	case "up", "k":
		if m.cursor > 0 {
			m.cursor--
		}
		return nil

	case "down", "j":
		if m.cursor < maxCursor {
			m.cursor++
		}
		return nil

	case " ", "space":
		// Toggle selection (only for fixable issues)
		if m.cursor >= 0 && m.cursor < len(flatList) {
			issue := flatList[m.cursor]
			if issue.IsFixable() {
				if m.selected[m.cursor] {
					delete(m.selected, m.cursor)
				} else {
					m.selected[m.cursor] = true
				}
			}
		}
		return nil

	case "f", "F":
		// Start fix if items selected
		if len(m.selected) > 0 {
			return func() tea.Msg { return diagnosticsFixStartMsg{} }
		}
		return nil

	case "r", "R":
		// Rescan
		m.cacheStore.Clear()
		return func() tea.Msg { return diagnosticsScanStartMsg{} }

	case "a", "A":
		// Select all fixable
		for i, issue := range flatList {
			if issue.IsFixable() {
				m.selected[i] = true
			}
		}
		return nil

	case "n", "N":
		// Deselect all
		m.selected = make(map[int]bool)
		return nil
	}

	return nil
}

// handleFixCompleteKey handles keys when showing fix results
func (m *DiagnosticsModel) handleFixCompleteKey(msg tea.KeyMsg) tea.Cmd {
	switch msg.String() {
	case "r", "R":
		// Rescan
		return func() tea.Msg { return diagnosticsScanStartMsg{} }
	}
	return nil
}

// GetState returns the current state
func (m DiagnosticsModel) GetState() DiagnosticsState {
	return m.state
}

// IssueCount returns the number of issues found
func (m DiagnosticsModel) IssueCount() int {
	return len(m.issues)
}

// HasFixableIssues returns true if there are fixable issues
func (m DiagnosticsModel) HasFixableIssues() bool {
	return diagnostics.CountFixable(m.issues) > 0
}
