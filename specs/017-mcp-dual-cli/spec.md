# Feature Specification: MCP Server Installation for Dual CLI Support

**Feature Branch**: `017-mcp-dual-cli`
**Created**: 2026-01-31
**Status**: Draft
**Input**: User description: "Add MCP server installation support for both Anthropic Claude Code and OpenAI Codex CLI through the TUI with target selection and dual-status display"

**Related**: Extends `specs/008-mcp-server-dashboard` by adding Codex CLI support alongside existing Claude Code integration

## Clarifications

### Session 2026-01-31

- Q: What configuration files are used by each CLI?
  - Claude Code: `~/.claude.json` (JSON format, `mcpServers` key at root)
  - Codex CLI: `~/.codex/config.toml` (TOML format, `[mcp_servers.<name>]` sections)

- Q: How are MCP servers added to each CLI?
  - Claude Code: Via `claude mcp add` CLI command
  - Codex CLI: Direct TOML file editing (no CLI command)

- Q: Should users be able to choose which CLI to install for?
  - Yes: Users can select "Claude only", "Codex only", or "Both"

- Q: Should the TUI detect which CLIs are installed?
  - Yes: Grey out options for CLIs that are not installed

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View Dual-CLI MCP Status Overview (Priority: P1)

As a user using both Claude Code and Codex CLI, I want to see a dashboard displaying all MCP servers with their installation status for EACH CLI, so I can understand which servers are configured in which tool.

**Why this priority**: Users need visibility into both CLI configurations before taking any actions. This is the foundation for all other functionality.

**Independent Test**: Can be fully tested by launching the TUI, navigating to MCP Servers, and verifying the status table shows separate columns for Claude and Codex status.

**Acceptance Scenarios**:

1. **Given** the user has both CLIs installed with some servers configured differently, **When** the dashboard loads, **Then** the status table displays server name, Claude status, Codex status, and description in aligned columns.
2. **Given** a server is installed in Claude but not Codex, **When** viewing the dashboard, **Then** that server shows "Added" under Claude and "Missing" under Codex.
3. **Given** neither CLI is installed, **When** the dashboard loads, **Then** a helpful message indicates prerequisites are not met with guidance to install Claude Code and/or Codex CLI.

---

### User Story 2 - Install MCP Server to Both CLIs (Priority: P1)

As a user, I want to install an MCP server to both Claude Code and Codex CLI with a single action, so I can maintain consistent tooling across both environments without repetitive configuration.

**Why this priority**: The primary value proposition of this feature - unified MCP management across CLIs.

**Independent Test**: Can be fully tested by selecting an uninstalled server, choosing "Install (Both)", and verifying the server appears as "Added" in both Claude's `~/.claude.json` and Codex's `~/.codex/config.toml`.

**Acceptance Scenarios**:

1. **Given** a server shows "Missing" in both CLIs, **When** the user selects "Install (Both)", **Then** the installation process configures the server in both `~/.claude.json` and `~/.codex/config.toml`.
2. **Given** installation succeeds for both CLIs, **When** returning to the dashboard, **Then** the server shows "Added" for both Claude and Codex.
3. **Given** one CLI installation fails, **When** the process completes, **Then** clear feedback indicates which CLI succeeded and which failed with the specific error.

---

### User Story 3 - Install MCP Server to Single CLI (Priority: P2)

As a user who only uses one CLI or wants different configurations, I want to install an MCP server to a specific CLI only, so I can maintain separate configurations per tool.

**Why this priority**: Provides flexibility for users with different workflow needs.

**Independent Test**: Can be fully tested by selecting a server and choosing "Install (Claude only)" or "Install (Codex only)", then verifying only the target configuration file is modified.

**Acceptance Scenarios**:

1. **Given** a server shows "Missing" in both CLIs, **When** the user selects "Install (Claude only)", **Then** only `~/.claude.json` is modified and Codex status remains "Missing".
2. **Given** a server shows "Missing" in both CLIs, **When** the user selects "Install (Codex only)", **Then** only `~/.codex/config.toml` is modified and Claude status remains "Missing".
3. **Given** only Codex CLI is installed (Claude not present), **When** viewing installation options, **Then** "Install (Claude only)" and "Install (Both)" options are disabled with explanation.

---

### User Story 4 - Remove MCP Server from CLI(s) (Priority: P2)

As a user, I want to remove MCP servers from one or both CLIs, so I can clean up configurations I no longer need.

**Why this priority**: Essential for lifecycle management, but secondary to installation.

**Independent Test**: Can be fully tested by selecting an installed server, choosing Remove for the desired CLI(s), and verifying the configuration files are updated accordingly.

**Acceptance Scenarios**:

1. **Given** a server is installed in both CLIs, **When** the user selects "Remove (Both)", **Then** the server is removed from both configuration files.
2. **Given** a server is installed only in Claude, **When** viewing removal options, **Then** only "Remove (Claude)" is available; Codex removal option is disabled.
3. **Given** the user confirms removal, **When** the process completes, **Then** the dashboard updates to show "Missing" for the affected CLI(s).

---

### User Story 5 - Configure mcp-hfspace Server (Priority: P3)

As a user of HuggingFace Spaces, I want to install the mcp-hfspace server (currently missing from the TUI), so I can use HF Spaces tools in my AI coding assistants.

**Why this priority**: Adds a missing server that users have already configured manually.

**Independent Test**: Can be fully tested by verifying mcp-hfspace appears in the server list and can be installed to either or both CLIs.

**Acceptance Scenarios**:

1. **Given** the MCP Servers dashboard is displayed, **When** viewing the server list, **Then** "mcp-hfspace" (HF Space) appears as an available server.
2. **Given** the user installs mcp-hfspace, **When** prerequisites are met, **Then** the server is configured with the correct HF_TOKEN environment variable reference.
3. **Given** the HuggingFace token file is missing, **When** attempting to install, **Then** a clear message indicates the prerequisite with instructions to run `huggingface-cli login`.

---

### User Story 6 - Set Default CLI Target Preference (Priority: P3)

As a frequent user, I want to set a default CLI target for MCP operations, so I don't have to choose every time when I typically use one CLI.

**Why this priority**: Quality of life improvement for power users.

**Independent Test**: Can be fully tested by setting a default preference and verifying subsequent installations default to the chosen target.

**Acceptance Scenarios**:

1. **Given** no preference is set, **When** the user accesses installation options, **Then** "Install (Both)" is highlighted as the default option.
2. **Given** the user sets "Claude only" as the default, **When** installing subsequent servers, **Then** "Install (Claude only)" is pre-selected.
3. **Given** a default preference is set, **When** the user views the action menu, **Then** they can still override by selecting a different option.

---

### Edge Cases

**CLI Detection Edge Cases:**
- What happens when Claude Code is installed but not authenticated? Show "Not authenticated" status with guidance to run `claude auth login`.
- What happens when Codex CLI is installed but config.toml doesn't exist? Create the config file with just the MCP server section.
- What happens when both CLIs are not installed? Display message indicating both CLIs are missing with installation instructions.

**Configuration Format Edge Cases:**
- What happens when Codex config.toml has comments or custom formatting? Preserve comments and formatting when modifying the file.
- What happens when `~/.codex/config.toml` has extra sections beyond MCP servers? Preserve all existing sections, only modify `mcp_servers`.
- What happens when a server name contains special TOML characters? Properly escape or quote the server name.

**Transport Type Edge Cases:**
- What happens when a server uses different transports per CLI (e.g., context7 can be HTTP or stdio)? Use CLI-specific configuration; don't assume same transport.
- What happens when secrets/API keys are required? Prompt via existing Secrets Wizard, then apply to both CLIs as needed.

**Concurrent Access Edge Cases:**
- What happens if another process is editing the config file? Use file locking or atomic write operations.
- What happens if config file becomes corrupted? Validate TOML/JSON before writing; keep backup of last known good config.

## Requirements *(mandatory)*

### Functional Requirements

**CLI Detection and Status:**
- **FR-001**: System MUST detect whether Claude Code CLI is installed by checking for `claude` command availability.
- **FR-002**: System MUST detect whether Codex CLI is installed by checking for `codex` command availability.
- **FR-003**: System MUST read Claude MCP server status from `~/.claude.json` or via `claude mcp list` output.
- **FR-004**: System MUST read Codex MCP server status by parsing `~/.codex/config.toml` file.
- **FR-005**: System MUST display separate status columns for Claude and Codex in the server table.

**Server Registry:**
- **FR-006**: System MUST include mcp-hfspace server in the MCP server registry.
- **FR-007**: System MUST store Codex-specific configuration (command, args, url, bearer_token_env_var) for each server.
- **FR-008**: System MUST support 8 MCP servers: context7, github, markitdown, playwright, hf-mcp-server, shadcn, shadcn-ui, mcp-hfspace.

**Installation Operations:**
- **FR-009**: System MUST support installing servers to Claude Code via `claude mcp add` command.
- **FR-010**: System MUST support installing servers to Codex CLI by writing to `~/.codex/config.toml`.
- **FR-011**: System MUST offer three installation targets: "Claude only", "Codex only", "Both".
- **FR-012**: System MUST disable target options for CLIs that are not installed.
- **FR-013**: System MUST preserve existing config.toml content when adding MCP servers.
- **FR-014**: System MUST create `~/.codex/config.toml` if it doesn't exist during Codex installation.

**Removal Operations:**
- **FR-015**: System MUST support removing servers from Claude Code via `claude mcp remove` command.
- **FR-016**: System MUST support removing servers from Codex CLI by editing `~/.codex/config.toml`.
- **FR-017**: System MUST only show removal options for CLIs where the server is currently installed.

**User Preferences:**
- **FR-018**: System MUST allow users to set a default CLI target preference.
- **FR-019**: System MUST persist the default preference across TUI sessions.
- **FR-020**: System MUST allow users to override the default for individual operations.

**Error Handling:**
- **FR-021**: System MUST display clear error messages when installation fails for either CLI.
- **FR-022**: System MUST report partial success when one CLI succeeds and the other fails.
- **FR-023**: System MUST validate TOML syntax before writing to config.toml.

### Key Entities

- **MCP Server**: A Model Context Protocol server with configuration for both Claude and Codex CLIs. Properties: ID, display name, description, transport type, prerequisites, secrets, Claude config, Codex config.
- **Codex MCP Config**: CLI-specific configuration for Codex. Properties: command (for stdio), args (for stdio), url (for HTTP), bearer_token_env_var (for HTTP auth).
- **CLI Target**: The destination CLI(s) for an operation. Values: Claude only, Codex only, Both.
- **Dual Status**: The installation state of a server across both CLIs. Properties: Claude status (Added/Missing/Error), Codex status (Added/Missing/Error).
- **CLI Availability**: Whether a CLI is installed and usable on the system. Properties: installed (boolean), authenticated (boolean), config path.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can view dual-CLI status for all 8 MCP servers within 3 seconds of opening the dashboard.
- **SC-002**: Users can install a server to both CLIs in under 30 seconds from selection to completion.
- **SC-003**: 90% of users can successfully install a server to their desired CLI(s) on their first attempt without documentation.
- **SC-004**: Server status displayed matches actual configuration state in both `~/.claude.json` and `~/.codex/config.toml` with 100% accuracy.
- **SC-005**: All operations (navigation, installation, removal) complete within 5 seconds for single-CLI targets.
- **SC-006**: Users with only one CLI installed can use the dashboard without errors or confusion.
- **SC-007**: Existing Codex config.toml content (projects, settings, comments) is preserved after MCP modifications.

## Assumptions

- Users have at least one of Claude Code or Codex CLI installed.
- The Codex CLI config file location is `~/.codex/config.toml` (not configurable).
- The Claude Code config file location is `~/.claude.json` for user-scope MCP servers.
- Claude Code's `claude mcp add/remove` commands remain the official method for Claude configuration.
- TOML format for Codex CLI follows standard TOML 1.0 specification.
- Server prerequisites (Node.js, gh auth, etc.) apply to both CLIs equally.
- API keys/secrets are shared between CLIs (stored in environment variables or `~/.mcp-secrets`).
- The existing MCP Servers UI patterns from `008-mcp-server-dashboard` will be reused and extended.
