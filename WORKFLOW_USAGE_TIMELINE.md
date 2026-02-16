# Dotfiles Usage Timeline (Oldest -> Latest)

## Why this document exists

This is a chronological breakdown of the setup/validation conversation flow used for this dotfiles project, from the earliest guide instructions to the latest implemented improvements.

Use this as a practical operating record for how you (and future assistants) should run and validate the environment.

## Source of truth used for reconstruction

The shared URL was not directly retrievable from this environment due Cloudflare/login challenge, so this timeline was reconstructed from local session artifacts:

- `~/.claude/projects/-home-kkk-Apps/a2495866-6917-4300-93d4-958be0b5a86f.jsonl`
- `~/.claude/projects/-home-kkk-Apps/3bad2475-7564-43a7-8577-85d64c013d25.jsonl`
- `~/.claude/paste-cache/b8ac4a8748403068.txt`
- Local project commits/changes in this repository

---

## 1. Oldest Instructions (Base Setup Guide)

The initial source instructions came from:

- `/home/kkk/Downloads/ubuntu-fresh-install-setup-guide.md`

Core guide sequence:

1. Install base packages (`curl`, `wget`, `git`, `fastfetch`, `fish`, `nodejs`, `npm`)
2. Set Fish as login shell
3. Install Fisher
4. Configure npm global prefix (`~/.npm-global`)
5. Install `gh`
6. Install `uv`
7. Install Claude Code
8. Install Codex CLI
9. Install Specify CLI
10. Configure Context7 MCP for Claude
11. Verify all tools
12. Authenticate `gh`
13. Configure git identity via Claude/gh
14. Initialize Spec Kit in project workflows

---

## 2. First Validation Conversation (2026-02-15)

User request:

- "help me identify if we have installed all tools described in this document"

What was done:

1. Read the setup guide from disk.
2. Ran parallel checks for all required tools/configs.
3. Validated versions/paths for:
   - `curl`, `wget`, `git`, `fastfetch`, `fish`, `node`, `npm`
   - `fisher`, `gh`, `uv`, `claude`, `codex`, `specify`
   - Fish default shell, npm prefix, `gh auth`, git identity
4. Corrected false negative for `specify`:
   - `specify --version` failed
   - `specify --help` proved it was installed

Initial issues detected:

1. `gh auth` token invalid in keyring
2. Context7 shown as "not configured" in command check context

---

## 3. Remediation Steps Performed (2026-02-15)

### 3.1 GitHub CLI auth fix

Executed in Fish:

```bash
gh auth status
gh auth login -h github.com
gh auth status
```

Result:

- `gh` authenticated successfully as `kairin`
- Git protocol set to `https`
- Required scopes present: `gist`, `read:org`, `repo`, `workflow`

### 3.2 MCP reconnection check

In Claude MCP UI:

- Context7 connected
- Hugging Face connected
- Hugging Face (2) reconnected and healthy
- Mermaid Chart connected

Result:

- All 4 MCP servers reported connected

---

## 4. State After First Conversation

Final outcome from Claude-side workflow:

- Guide requirements effectively satisfied
- `gh auth` issue fixed
- MCP servers connected in active session
- Toolchain installed and usable

---

## 5. Next Request: Codex Context7 Location (2026-02-16)

Question asked:

- "where is the location of the context7 mcp server for codex?"

Resolved with concrete path:

- `~/.codex/config.toml`
- `mcp_servers.context7.url = "https://mcp.context7.com/mcp"`
- Header forwarding via environment mapping:
  - `env_http_headers = { CONTEXT7_API_KEY = "CONTEXT7_API_KEY" }`

Security note:

- API key value is not stored in plaintext in repository files.
- Runtime env var is forwarded as header name mapping.

---

## 6. Project-Level Improvements Implemented (Latest)

After "let's build something", the workflow was upgraded from manual checks to built-in project capabilities.

### 6.1 Secret-safe workstation audit mode

Enhanced existing script (no new wrapper script) in:

- `.runners-local/workflows/health-check.sh`

New command:

```bash
./.runners-local/workflows/health-check.sh --workstation-audit
```

What it checks:

- Tool presence/versions
- Fish/Fisher/npm prefix
- `gh auth` status
- Git identity
- Context7 status for Claude + Codex
- `CONTEXT7_API_KEY` presence only

Secret handling:

- No token/API key values are printed
- Only status/presence is shown

### 6.2 TUI menu integration (no memorized flag needed)

Added a dashboard menu item:

- `Workstation Audit`

Selecting it runs the same audit via TUI output flow.

Updated areas:

- `tui/internal/ui/model.go` (menu item + action routing)
- `tui/internal/executor/configure.go` (configure stage argument pass-through)
- `README.md` (usage notes)

---

## 7. Current Recommended Personal Usage Flow

### Primary entrypoint

```bash
./start.sh
```

### Health/audit routine

1. Launch TUI with `./start.sh`
2. Run `Workstation Audit` from dashboard menu
3. If any FAIL/WARN appears:
   - resolve auth/mcp/tool issue
   - rerun `Workstation Audit`

### Optional CLI-only audit

```bash
./.runners-local/workflows/health-check.sh --workstation-audit
```

---

## 8. Practical Takeaways

1. Installation status checks should be verified with behavior, not only `--version` flags (example: `specify`).
2. MCP status is scope-sensitive and can appear inconsistent across CLI/session contexts.
3. `gh auth` drift is a common post-install break point; re-authentication fixes most issues quickly.
4. Embedding audit into TUI significantly improves repeatability for daily use.
5. Secret-safe reporting is mandatory for reusable health tooling.

