# Version Verification Matrix

> **Source**: [version-verification-feb2026.xlsx](version-verification-feb2026.xlsx), Sheet 1 — "Version Verification"
> **Date**: 24 Feb 2026

## Tool Versions

| Category | Tool | Guide Version | Latest Version | Status | Install Method | Notes |
|----------|------|---------------|----------------|--------|----------------|-------|
| Core Tools | Fish shell | 4.5.0 | 4.5.0 | ✅ Current | PPA (fish-shell/release-4) | Released Feb 17, 2026 |
| Core Tools | Go | 1.26.0 | 1.26.0 | ✅ Current | Static binary (go.dev) | Released Feb 10, 2026 |
| Core Tools | Node.js | 25.x (via fnm) | 25.6.1 | ✅ Current | fnm version manager | Current branch; LTS is 24.x |
| Core Tools | npm | (bundled) | 11.9.0 | ✅ Current | Bundled with Node.js | Comes with Node 25.6.1 |
| Version Mgrs | fnm | Not specified | 1.38.1 | ⚠️ No version | curl installer | Always installs latest via script |
| Version Mgrs | uv | 0.10.4 | 0.10.4 | ✅ Current | curl installer | Released Feb 17, 2026 |
| Version Mgrs | Fisher | 4.4.8 | 4.4.8 | ✅ Current | curl installer | Fish plugin manager |
| Git & GitHub | Git | apt default | 2.47.3 (apt) | ✅ Correct | apt | Version varies by distro release |
| Git & GitHub | GitHub CLI (gh) | 2.87.2 | 2.87.2 | ✅ Current | apt (GitHub repo) | 2.87.0/2.87.1 had issues |
| AI CLIs | Claude Code | 2.1.50 | 2.1.50 | ✅ Current | npm -g | Anthropic CLI |
| AI CLIs | Codex CLI | 0.104.0 | 0.104.0 | ✅ Current | npm -g | OpenAI CLI; published ~5 days ago |
| AI CLIs | Gemini CLI | 0.29.5 | 0.29.5 | ✅ Current | npm -g | Google CLI; published ~4 days ago |
| AI CLIs | Backlog.md | 1.38.0 | 1.38.0 | ✅ Current | npm -g | Markdown task manager & Kanban |
| Fonts | Nerd Fonts | v3.4.0 | v3.4.0 | ✅ Current | curl + unzip | April 2025 release; still latest |
| Fish Plugins | Tide | v6 (6.2.0) | v6 (6.2.0) | ✅ Current | Fisher | Pinned to @v6 tag |
| Fish Plugins | fzf.fish | Not specified | Latest (Fisher) | ⚠️ No version | Fisher | Fisher installs HEAD by default |
| Fish Plugins | z | Not specified | Latest (Fisher) | ⚠️ No version | Fisher | Fisher installs HEAD by default |
| Fish Plugins | done | Not specified | Latest (Fisher) | ⚠️ No version | Fisher | Fisher installs HEAD by default |
| Fish Plugins | autopair.fish | Not specified | Latest (Fisher) | ⚠️ No version | Fisher | Fisher installs HEAD by default |
| Apt Utilities | fastfetch | Not specified | apt varies | ⚠️ No version | apt (PPA on 24.04) | PPA needed for Ubuntu 24.04 |
| Apt Utilities | ShellCheck | 0.10.0 | 0.10.0 (apt) | ✅ Current | apt | Static analysis for shell scripts |
| Apt Utilities | direnv | 2.32.1 | 2.32.1+ (apt) | ✅ Current | apt | Per-project env vars |
| Apt Utilities | fzf | 0.60 | 0.60+ (apt) | ✅ Current | apt | Fuzzy finder; system dependency |

## Summary

- **✅ Current**: 17 tools verified at latest versions
- **⚠️ No version in guide**: 6 tools (fnm, fzf.fish, z, done, autopair.fish, fastfetch) — installed via scripts/Fisher that always fetch latest
- All explicitly versioned tools in the guide match current releases as of 24 Feb 2026
- Apt-managed tools show versions from actual test installations (correct, as these vary by distro)
