// Dotfiles Installer TUI - Go + Bubbletea implementation
package main

import (
	"flag"
	"fmt"
	"os"
	"os/exec"
	"os/signal"
	"path/filepath"
	"syscall"

	tea "github.com/charmbracelet/bubbletea"
	"github.com/kairin/dotfiles-installer/internal/ui"
)

// Command line flags
var (
	demoMode   = flag.Bool("demo-child", false, "Run in demo mode (for VHS/asciinema recording)")
	sudoCached = flag.Bool("sudo-cached", false, "Use cached sudo credentials in demo mode")
	showHelp   = flag.Bool("help", false, "Show help message")
)

func main() {
	flag.Parse()

	if *showHelp {
		fmt.Println("Dotfiles Installer TUI")
		fmt.Println()
		fmt.Println("Usage: installer [options]")
		fmt.Println()
		fmt.Println("Options:")
		flag.PrintDefaults()
		os.Exit(0)
	}

	// Bug #197 fix: Ensure terminal state is restored on exit
	// This deferred function runs after the TUI exits (normal or signal)
	// to reset terminal to cooked mode and restore copy/paste functionality
	defer restoreTerminalState()

	// Set up signal handling for clean shutdown
	// This ensures terminal state is restored even on Ctrl+C
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)

	// Handle signals in a goroutine
	go func() {
		<-sigChan
		// Signal received - restore terminal and exit
		restoreTerminalState()
		os.Exit(0)
	}()

	// Determine repo root (parent of tui/)
	execPath, err := os.Executable()
	if err != nil {
		execPath, _ = os.Getwd()
	}

	// If running from tui/cmd/installer, go up 3 levels
	// If running from repo root, use current dir
	repoRoot := findRepoRoot(execPath)
	if repoRoot == "" {
		// Fallback to current directory
		repoRoot, _ = os.Getwd()
	}

	// Create the TUI model
	m := ui.NewModel(repoRoot, *demoMode)

	// Set sudo cached if in demo mode
	if *demoMode && *sudoCached {
		m.SetSudoCached(true)
	}

	// Create and run the TUI
	p := tea.NewProgram(m, tea.WithAltScreen())

	if _, err := p.Run(); err != nil {
		fmt.Printf("Error running program: %v\n", err)
		os.Exit(1)
	}
}

// restoreTerminalState resets the terminal to cooked mode
// This fixes Bug #197: Copy/paste stops working after TUI exit
// The function uses 'stty sane' to restore standard terminal settings
// including line editing, echo, and proper signal handling
func restoreTerminalState() {
	// Use stty sane to reset terminal to a known good state
	// This restores: echo, icanon (line mode), signal handling, etc.
	cmd := exec.Command("stty", "sane")
	cmd.Stdin = os.Stdin
	_ = cmd.Run() // Ignore errors - best effort cleanup
}

// findRepoRoot locates the repository root by looking for CLAUDE.md
func findRepoRoot(startPath string) string {
	// Start from the directory containing the executable
	dir := filepath.Dir(startPath)

	// Walk up the directory tree
	for i := 0; i < 10; i++ { // Max 10 levels up
		// Check for CLAUDE.md (repo root marker)
		claudeMd := filepath.Join(dir, "CLAUDE.md")
		if _, err := os.Stat(claudeMd); err == nil {
			return dir
		}

		// Check for start.sh (repo root marker)
		startSh := filepath.Join(dir, "start.sh")
		if _, err := os.Stat(startSh); err == nil {
			return dir
		}

		// Go up one level
		parent := filepath.Dir(dir)
		if parent == dir {
			break // Reached filesystem root
		}
		dir = parent
	}

	return ""
}
