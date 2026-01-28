// Package ui provides the Bubbletea TUI implementation
package ui

import (
	"fmt"

	"github.com/charmbracelet/bubbles/key"
	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"
)

// ConfirmResult is sent when the user confirms or cancels
type ConfirmResult struct {
	Confirmed bool
	Context   interface{} // Optional context to pass back
}

// ConfirmAction identifies the type of action being confirmed
type ConfirmAction string

const (
	ConfirmActionInstall   ConfirmAction = "Install"
	ConfirmActionUpdate    ConfirmAction = "Update"
	ConfirmActionReinstall ConfirmAction = "Reinstall"
	ConfirmActionUninstall ConfirmAction = "Uninstall"
)

// ConfirmModel implements a confirmation dialog
type ConfirmModel struct {
	question    string
	focused     int         // 0=No, 1=Yes
	context     interface{} // Context to pass back with result
	width       int
	height      int
	action      ConfirmAction  // Type of action for styling
	borderColor lipgloss.Color // Border color (varies by action)
}

// Confirm key bindings
type confirmKeyMap struct {
	Left   key.Binding
	Right  key.Binding
	Tab    key.Binding
	Enter  key.Binding
	Escape key.Binding
	Yes    key.Binding
	No     key.Binding
}

var confirmKeys = confirmKeyMap{
	Left: key.NewBinding(
		key.WithKeys("left", "h"),
		key.WithHelp("←/h", "no"),
	),
	Right: key.NewBinding(
		key.WithKeys("right", "l"),
		key.WithHelp("→/l", "yes"),
	),
	Tab: key.NewBinding(
		key.WithKeys("tab"),
		key.WithHelp("tab", "switch"),
	),
	Enter: key.NewBinding(
		key.WithKeys("enter"),
		key.WithHelp("enter", "confirm"),
	),
	Escape: key.NewBinding(
		key.WithKeys("esc"),
		key.WithHelp("esc", "cancel"),
	),
	Yes: key.NewBinding(
		key.WithKeys("y", "Y"),
		key.WithHelp("y", "yes"),
	),
	No: key.NewBinding(
		key.WithKeys("n", "N"),
		key.WithHelp("n", "no"),
	),
}

// NewConfirmModel creates a new confirmation dialog
func NewConfirmModel(question string, context interface{}) ConfirmModel {
	return ConfirmModel{
		question:    question,
		focused:     0, // Default to "No" for safety
		context:     context,
		width:       50,
		height:      7,
		action:      ConfirmActionUninstall, // Default to uninstall styling for backwards compat
		borderColor: ColorWarning,
	}
}

// NewConfirmModelWithAction creates a new confirmation dialog with action-specific styling
func NewConfirmModelWithAction(question string, context interface{}, action ConfirmAction) ConfirmModel {
	// Determine border color based on action
	var borderColor lipgloss.Color
	var defaultFocus int

	switch action {
	case ConfirmActionInstall:
		borderColor = ColorPrimary // Magenta for install (positive action)
		defaultFocus = 1           // Default to Yes for install
	case ConfirmActionUpdate:
		borderColor = ColorWarning // Orange for update (caution)
		defaultFocus = 1           // Default to Yes for update
	case ConfirmActionReinstall:
		borderColor = ColorWarning // Orange for reinstall (caution)
		defaultFocus = 0           // Default to No for reinstall (destructive)
	case ConfirmActionUninstall:
		borderColor = ColorWarning // Orange for uninstall (danger)
		defaultFocus = 0           // Default to No for uninstall (destructive)
	default:
		borderColor = ColorWarning
		defaultFocus = 0
	}

	return ConfirmModel{
		question:    question,
		focused:     defaultFocus,
		context:     context,
		width:       50,
		height:      7,
		action:      action,
		borderColor: borderColor,
	}
}

// Init implements tea.Model
func (m ConfirmModel) Init() tea.Cmd {
	return nil
}

// Update implements tea.Model
func (m ConfirmModel) Update(msg tea.Msg) (ConfirmModel, tea.Cmd) {
	switch msg := msg.(type) {
	case tea.KeyMsg:
		switch {
		case key.Matches(msg, confirmKeys.Left):
			m.focused = 0 // No
		case key.Matches(msg, confirmKeys.Right):
			m.focused = 1 // Yes
		case key.Matches(msg, confirmKeys.Tab):
			m.focused = 1 - m.focused // Toggle
		case key.Matches(msg, confirmKeys.Enter):
			return m, func() tea.Msg {
				return ConfirmResult{
					Confirmed: m.focused == 1,
					Context:   m.context,
				}
			}
		case key.Matches(msg, confirmKeys.Escape), key.Matches(msg, confirmKeys.No):
			return m, func() tea.Msg {
				return ConfirmResult{
					Confirmed: false,
					Context:   m.context,
				}
			}
		case key.Matches(msg, confirmKeys.Yes):
			return m, func() tea.Msg {
				return ConfirmResult{
					Confirmed: true,
					Context:   m.context,
				}
			}
		}

	case tea.WindowSizeMsg:
		m.width = msg.Width
		m.height = msg.Height
	}

	return m, nil
}

// View implements tea.Model
func (m ConfirmModel) View() string {
	// Button styles
	buttonStyle := lipgloss.NewStyle().
		Padding(0, 3).
		Border(lipgloss.RoundedBorder()).
		BorderForeground(ColorMuted)

	selectedButtonStyle := lipgloss.NewStyle().
		Padding(0, 3).
		Border(lipgloss.RoundedBorder()).
		BorderForeground(ColorPrimary).
		Foreground(ColorPrimary).
		Bold(true)

	// Determine Yes button style based on action type
	var yesSelectedStyle lipgloss.Style
	switch m.action {
	case ConfirmActionInstall:
		// Primary/positive for install
		yesSelectedStyle = lipgloss.NewStyle().
			Padding(0, 3).
			Border(lipgloss.RoundedBorder()).
			BorderForeground(ColorPrimary).
			Foreground(ColorPrimary).
			Bold(true)
	case ConfirmActionUpdate:
		// Primary for update (generally safe)
		yesSelectedStyle = lipgloss.NewStyle().
			Padding(0, 3).
			Border(lipgloss.RoundedBorder()).
			BorderForeground(ColorPrimary).
			Foreground(ColorPrimary).
			Bold(true)
	default:
		// Danger/warning for reinstall and uninstall
		yesSelectedStyle = lipgloss.NewStyle().
			Padding(0, 3).
			Border(lipgloss.RoundedBorder()).
			BorderForeground(ColorError).
			Foreground(ColorError).
			Bold(true)
	}

	// Render buttons
	var noButton, yesButton string
	if m.focused == 0 {
		noButton = selectedButtonStyle.Render("  No  ")
		yesButton = buttonStyle.Render(" Yes ")
	} else {
		noButton = buttonStyle.Render("  No  ")
		yesButton = yesSelectedStyle.Render(" Yes ")
	}

	buttons := lipgloss.JoinHorizontal(lipgloss.Center, noButton, "    ", yesButton)

	// Question with icon (varies by action)
	var icon string
	switch m.action {
	case ConfirmActionInstall:
		icon = IconPackage
	case ConfirmActionUpdate:
		icon = IconArrowUp
	default:
		icon = IconWarning
	}

	questionStyle := lipgloss.NewStyle().
		Foreground(m.borderColor).
		Bold(true)
	questionText := questionStyle.Render(icon + "  " + m.question)

	// Help text
	helpText := HelpStyle.Render("[←/→] Select  [Enter] Confirm  [Esc] Cancel  [Y/N] Quick select")

	// Compose the dialog
	content := lipgloss.JoinVertical(
		lipgloss.Center,
		"",
		questionText,
		"",
		buttons,
		"",
		helpText,
	)

	// Dialog box style - use action-specific border color
	dialogStyle := lipgloss.NewStyle().
		Border(lipgloss.DoubleBorder()).
		BorderForeground(m.borderColor).
		Padding(1, 4).
		Width(60)

	dialog := dialogStyle.Render(content)

	// Center the dialog on screen
	return lipgloss.Place(
		m.width,
		m.height,
		lipgloss.Center,
		lipgloss.Center,
		dialog,
	)
}

// SetSize sets the dialog dimensions for centering
func (m *ConfirmModel) SetSize(width, height int) {
	m.width = width
	m.height = height
}

// ConfirmUninstall creates a confirmation dialog for uninstalling a tool
func ConfirmUninstall(toolName string, context interface{}) ConfirmModel {
	question := fmt.Sprintf("Uninstall %s? This action cannot be undone.", toolName)
	return NewConfirmModelWithAction(question, context, ConfirmActionUninstall)
}

// ConfirmInstall creates a confirmation dialog for installing a tool
func ConfirmInstall(toolName string, context interface{}) ConfirmModel {
	question := fmt.Sprintf("Install %s?", toolName)
	return NewConfirmModelWithAction(question, context, ConfirmActionInstall)
}

// ConfirmUpdate creates a confirmation dialog for updating a tool
func ConfirmUpdate(toolName string, context interface{}) ConfirmModel {
	question := fmt.Sprintf("Update %s to the latest version?", toolName)
	return NewConfirmModelWithAction(question, context, ConfirmActionUpdate)
}

// ConfirmReinstall creates a confirmation dialog for reinstalling a tool
func ConfirmReinstall(toolName string, context interface{}) ConfirmModel {
	question := fmt.Sprintf("Reinstall %s? This will uninstall and reinstall the tool.", toolName)
	return NewConfirmModelWithAction(question, context, ConfirmActionReinstall)
}

// GetAction returns the confirmation action type
func (m ConfirmModel) GetAction() ConfirmAction {
	return m.action
}
