#!/usr/bin/env bash

#######################################
# Script: performance-monitor.sh
# Purpose: Monitor system performance and environment metrics
# Usage: ./performance-monitor.sh [--test|--baseline|--compare|--weekly-report|--help]
# Dependencies: jq (optional), coreutils
#######################################

set -euo pipefail
IFS=$'\n\t'

# Script configuration
SCRIPT_NAME=$(basename "$0")
readonly SCRIPT_NAME
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly SCRIPT_DIR
LOG_DIR="$SCRIPT_DIR/../logs"
readonly LOG_DIR
REPO_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
readonly REPO_DIR

# Ensure log directory exists
mkdir -p "$LOG_DIR"

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m'

# Logging function
log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    case "$level" in
        "ERROR") echo -e "${RED}[$timestamp] [ERROR] $message${NC}" >&2 ;;
        "SUCCESS") echo -e "${GREEN}[$timestamp] [SUCCESS] $message${NC}" ;;
        "WARNING") echo -e "${YELLOW}[$timestamp] [WARNING] $message${NC}" ;;
        "INFO") echo -e "${BLUE}[$timestamp] [INFO] $message${NC}" ;;
    esac
}

# Error handler
error_exit() {
    log "ERROR" "$1"
    exit 1
}

# Cleanup function
cleanup() {
    # Cleanup temporary files if any were created
    local exit_code=$?
    if [ -n "${TEMP_FILES:-}" ]; then
        rm -f "$TEMP_FILES" 2>/dev/null || true
    fi
    exit $exit_code
}

# Register cleanup on exit
trap cleanup EXIT INT TERM

# Dependency checking
check_dependencies() {
    # jq is optional but recommended
    if ! command -v jq >/dev/null 2>&1; then
        log "WARNING" "jq not found - JSON output will be basic"
    fi
}

# Monitor system performance
monitor_system_performance() {
    local test_mode="${1:-default}"

    log "INFO" "📊 Monitoring system performance (mode: $test_mode)..."

    local loadavg
    loadavg=$(awk '{print $1" "$2" "$3}' /proc/loadavg 2>/dev/null || echo "unknown")
    local mem_available_kb
    mem_available_kb=$(awk '/MemAvailable/ {print $2}' /proc/meminfo 2>/dev/null || echo "unknown")
    local root_available
    root_available=$(df -h / 2>/dev/null | awk 'NR==2 {print $4}' || echo "unknown")

    # Generate performance report
    local output_file
    output_file="$LOG_DIR/performance-$(date +%s).json"
    cat > "$output_file" << EOF
{
    "timestamp": "$(date -Iseconds)",
    "test_mode": "$test_mode",
    "system": {
        "hostname": "$(hostname)",
        "kernel": "$(uname -r)",
        "uptime": "$(uptime -p 2>/dev/null || echo 'unknown')",
        "loadavg": "$loadavg",
        "mem_available_kb": "$mem_available_kb",
        "root_available": "$root_available"
    }
}
EOF

    log "SUCCESS" "✅ Performance data collected: $output_file"

    # Display summary if jq is available
    if command -v jq >/dev/null 2>&1; then
        echo ""
        jq '.' "$output_file"
    fi
}

# Generate weekly performance report
generate_weekly_report() {
    log "INFO" "📈 Generating weekly performance report..."

    # Find all performance logs from the last 7 days
    local report_file
    report_file="$LOG_DIR/weekly-report-$(date +%Y%m%d).txt"
    local logs_found=0

    {
        echo "======================================"
        echo "Weekly Performance Report"
        echo "Generated: $(date)"
        echo "======================================"
        echo ""

        # Find performance logs from last 7 days
        if command -v find >/dev/null 2>&1; then
            while IFS= read -r -d '' file; do
                logs_found=$((logs_found + 1))
                echo "--- $(basename "$file") ---"
                if command -v jq >/dev/null 2>&1; then
                    jq -r '. | "Time: \(.timestamp)\nLoadavg: \(.system.loadavg)\nMem Available (KB): \(.system.mem_available_kb)\nRoot Available: \(.system.root_available)\n"' "$file" 2>/dev/null || cat "$file"
                else
                    cat "$file"
                fi
                echo ""
            done < <(find "$LOG_DIR" -name "performance-*.json" -type f -mtime -7 -print0 2>/dev/null)
        fi

        if [ $logs_found -eq 0 ]; then
            echo "No performance logs found in the last 7 days."
            echo "Run './performance-monitor.sh --test' to generate initial data."
        else
            echo "Total measurements: $logs_found"
        fi

        echo ""
        echo "======================================"
    } > "$report_file"

    cat "$report_file"
    log "SUCCESS" "✅ Weekly report saved to: $report_file"
}

# Display help information
show_help() {
    cat << EOF
Usage: $SCRIPT_NAME [OPTION]

Monitor system performance and generate performance reports.

Options:
    --test          Run performance test and collect metrics
    --baseline      Establish performance baseline
    --compare       Compare current performance to baseline
    --weekly-report Generate weekly performance summary report
    --help          Display this help message and exit

Examples:
    $SCRIPT_NAME --test
        Run a performance test and save metrics to JSON

    $SCRIPT_NAME --weekly-report
        Generate a summary of all performance data from the last 7 days

    $SCRIPT_NAME --baseline
        Establish a baseline for performance comparison

Dependencies:
    Optional: jq (for enhanced JSON output)

Output:
    Performance data is saved to: $LOG_DIR/performance-*.json
    Weekly reports are saved to: $LOG_DIR/weekly-report-*.txt

Exit Codes:
    0    Success
    1    Error (missing dependencies, invalid arguments, etc.)

EOF
}

# Main function
main() {
    local mode="${1:-default}"

    # Handle help first
    if [[ "$mode" == "--help" || "$mode" == "-h" ]]; then
        show_help
        exit 0
    fi

    # Check dependencies
    check_dependencies

    # Process command
    case "$mode" in
        --test)
            monitor_system_performance "test"
            ;;
        --baseline)
            monitor_system_performance "baseline"
            ;;
        --compare)
            monitor_system_performance "compare"
            log "INFO" "Comparison feature will be implemented in future version"
            ;;
        --weekly-report)
            generate_weekly_report
            ;;
        *)
            monitor_system_performance "default"
            ;;
    esac
}

# Execute main function
main "$@"
