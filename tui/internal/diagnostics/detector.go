// Package diagnostics - detector.go handles running detector scripts and parsing output
package diagnostics

import (
	"context"
	"os/exec"
	"path/filepath"
	"strings"
	"sync"
	"time"
)

// DetectorStatus represents the current status of a detector
type DetectorStatus int

const (
	DetectorPending DetectorStatus = iota
	DetectorRunning
	DetectorComplete
	DetectorFailed
	DetectorTimedOut
)

// String returns the string representation of DetectorStatus
func (s DetectorStatus) String() string {
	switch s {
	case DetectorPending:
		return "pending"
	case DetectorRunning:
		return "running"
	case DetectorComplete:
		return "complete"
	case DetectorFailed:
		return "failed"
	case DetectorTimedOut:
		return "timeout"
	default:
		return "unknown"
	}
}

// DetectorInfo holds metadata about a single detector
type DetectorInfo struct {
	ID          int    // Index in the detector list (0-4)
	Script      string // Script path relative to repo root
	DisplayName string // Human-readable name
	Description string // One-line description of what it checks
	Status      DetectorStatus
	IssueCount  int           // Number of issues found by this detector
	Error       error         // Error if failed/timeout
	Duration    time.Duration // How long the detector took to run
}

// detectorMetadata contains display information for each detector
var detectorMetadata = []struct {
	DisplayName string
	Description string
}{
	{"Failed Services", "Identifies systemd services that failed to start"},
	{"Orphaned Services", "Finds services referencing executables that no longer exist"},
	{"Network Wait Issues", "Detects NetworkManager-wait-online timeout problems"},
	{"Unsupported Snaps", "Identifies snaps incompatible with your Ubuntu version"},
	{"Cosmetic Warnings", "Known harmless warnings (ALSA, GNOME keyring, etc.)"},
}

// GetDetectorInfos returns metadata for all detectors with initial pending status
func GetDetectorInfos() []DetectorInfo {
	infos := make([]DetectorInfo, len(detectorScripts))
	for i, script := range detectorScripts {
		meta := detectorMetadata[i]
		infos[i] = DetectorInfo{
			ID:          i,
			Script:      script,
			DisplayName: meta.DisplayName,
			Description: meta.Description,
			Status:      DetectorPending,
		}
	}
	return infos
}

// DetectorProgress reports the progress of a single detector
type DetectorProgress struct {
	DetectorID int            // Which detector (0-4)
	Status     DetectorStatus // Current status
	IssueCount int            // Number of issues found (when complete)
	Error      error          // Error if failed/timeout
	Duration   time.Duration  // How long it took
}

// StreamingDetectorResult holds the result from the streaming detector run
type StreamingDetectorResult struct {
	Issues []*Issue
	Errors []error
}

// RunDetectorsWithProgress executes all detector scripts concurrently and sends progress updates
// The progressChan receives updates as each detector starts and completes
// Returns the final result when all detectors are done
func RunDetectorsWithProgress(ctx context.Context, repoRoot string, progressChan chan<- DetectorProgress) *StreamingDetectorResult {
	var wg sync.WaitGroup
	results := make(chan struct {
		index  int
		result DetectorResult
	}, len(detectorScripts))

	// Run each detector concurrently
	for i, script := range detectorScripts {
		wg.Add(1)
		go func(index int, scriptPath string) {
			defer wg.Done()

			// Send "running" status
			progressChan <- DetectorProgress{
				DetectorID: index,
				Status:     DetectorRunning,
			}

			// Run the detector
			start := time.Now()
			result := runSingleDetector(ctx, repoRoot, scriptPath)
			duration := time.Since(start)

			// Determine final status
			status := DetectorComplete
			if result.Error != nil {
				if ctx.Err() == context.DeadlineExceeded {
					status = DetectorTimedOut
				} else {
					status = DetectorFailed
				}
			}

			// Send completion status
			progressChan <- DetectorProgress{
				DetectorID: index,
				Status:     status,
				IssueCount: len(result.Issues),
				Error:      result.Error,
				Duration:   duration,
			}

			results <- struct {
				index  int
				result DetectorResult
			}{index, result}
		}(i, script)
	}

	// Close results channel when all detectors complete
	go func() {
		wg.Wait()
		close(results)
	}()

	// Collect results
	allIssues := make([]*Issue, 0)
	errors := make([]error, 0)

	for r := range results {
		if r.result.Error != nil {
			errors = append(errors, r.result.Error)
			continue
		}
		allIssues = append(allIssues, r.result.Issues...)
	}

	return &StreamingDetectorResult{
		Issues: allIssues,
		Errors: errors,
	}
}

// DetectorScript paths relative to repo root
var detectorScripts = []string{
	"scripts/007-diagnostics/detect_failed_services.sh",
	"scripts/007-diagnostics/detect_orphaned_services.sh",
	"scripts/007-diagnostics/detect_network_wait_issues.sh",
	"scripts/007-diagnostics/detect_unsupported_snaps.sh",
	"scripts/007-diagnostics/detect_cosmetic_warnings.sh",
}

// DetectorTimeout is the timeout for each detector script
const DetectorTimeout = 30 * time.Second

// DetectorResult holds the result from a single detector
type DetectorResult struct {
	Script string
	Issues []*Issue
	Error  error
}

// RunDetectors executes all detector scripts concurrently and aggregates results
func RunDetectors(ctx context.Context, repoRoot string) ([]*Issue, []error) {
	var wg sync.WaitGroup
	results := make(chan DetectorResult, len(detectorScripts))

	// Run each detector concurrently
	for _, script := range detectorScripts {
		wg.Add(1)
		go func(scriptPath string) {
			defer wg.Done()
			result := runSingleDetector(ctx, repoRoot, scriptPath)
			results <- result
		}(script)
	}

	// Close results channel when all detectors complete
	go func() {
		wg.Wait()
		close(results)
	}()

	// Collect results
	allIssues := make([]*Issue, 0)
	errors := make([]error, 0)

	for result := range results {
		if result.Error != nil {
			errors = append(errors, result.Error)
			continue
		}
		allIssues = append(allIssues, result.Issues...)
	}

	return allIssues, errors
}

// runSingleDetector executes a single detector script
func runSingleDetector(ctx context.Context, repoRoot, scriptPath string) DetectorResult {
	result := DetectorResult{Script: scriptPath}

	// Build absolute path
	fullPath := filepath.Join(repoRoot, scriptPath)

	// Create context with timeout
	ctx, cancel := context.WithTimeout(ctx, DetectorTimeout)
	defer cancel()

	// Execute script
	cmd := exec.CommandContext(ctx, "bash", fullPath)
	cmd.Dir = repoRoot

	output, err := cmd.Output()
	if err != nil {
		// Check if it's a context error (timeout/cancellation)
		if ctx.Err() != nil {
			result.Error = ctx.Err()
			return result
		}
		// Non-zero exit is okay - might just mean no issues found
		// Only record error if we got no output
		if len(output) == 0 {
			result.Error = err
			return result
		}
	}

	// Parse output into issues
	result.Issues = ParseIssues(string(output))
	return result
}

// RunSingleDetector runs one detector script (for testing or targeted scanning)
func RunSingleDetector(ctx context.Context, repoRoot, scriptPath string) ([]*Issue, error) {
	result := runSingleDetector(ctx, repoRoot, scriptPath)
	return result.Issues, result.Error
}

// GetDetectorScripts returns the list of detector script paths
func GetDetectorScripts() []string {
	return detectorScripts
}

// DetectorExists checks if a detector script exists
func DetectorExists(repoRoot, scriptPath string) bool {
	fullPath := filepath.Join(repoRoot, scriptPath)
	_, err := exec.LookPath("bash")
	if err != nil {
		return false
	}

	cmd := exec.Command("test", "-f", fullPath)
	return cmd.Run() == nil
}

// GetMissingDetectors returns a list of missing detector scripts
func GetMissingDetectors(repoRoot string) []string {
	missing := make([]string, 0)
	for _, script := range detectorScripts {
		if !DetectorExists(repoRoot, script) {
			missing = append(missing, script)
		}
	}
	return missing
}

// ScanResult holds the complete scan result
type ScanResult struct {
	Issues        []*Issue
	Errors        []error
	ScanTime      time.Time
	Duration      time.Duration
	ScriptsRan    int
	ScriptsFailed int
}

// RunFullScan executes all detectors and returns a complete scan result
func RunFullScan(ctx context.Context, repoRoot string) *ScanResult {
	start := time.Now()

	issues, errors := RunDetectors(ctx, repoRoot)

	return &ScanResult{
		Issues:        issues,
		Errors:        errors,
		ScanTime:      start,
		Duration:      time.Since(start),
		ScriptsRan:    len(detectorScripts),
		ScriptsFailed: len(errors),
	}
}

// Summary returns a human-readable summary of the scan
func (r *ScanResult) Summary() string {
	var b strings.Builder

	b.WriteString("Scan completed in ")
	b.WriteString(r.Duration.Round(time.Millisecond).String())
	b.WriteString("\n")

	total := len(r.Issues)
	groups := GroupBySeverity(r.Issues)

	b.WriteString("Found ")
	b.WriteString(string(rune('0' + total)))
	b.WriteString(" issues: ")

	parts := make([]string, 0, 3)
	if len(groups[SeverityCritical]) > 0 {
		parts = append(parts, string(rune('0'+len(groups[SeverityCritical])))+" critical")
	}
	if len(groups[SeverityModerate]) > 0 {
		parts = append(parts, string(rune('0'+len(groups[SeverityModerate])))+" moderate")
	}
	if len(groups[SeverityLow]) > 0 {
		parts = append(parts, string(rune('0'+len(groups[SeverityLow])))+" low")
	}

	if len(parts) > 0 {
		b.WriteString(strings.Join(parts, ", "))
	} else {
		b.WriteString("no issues found")
	}

	if r.ScriptsFailed > 0 {
		b.WriteString(" (")
		b.WriteString(string(rune('0' + r.ScriptsFailed)))
		b.WriteString(" scripts failed)")
	}

	return b.String()
}
