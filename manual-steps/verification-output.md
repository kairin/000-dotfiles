# Verification Output

> **Date**: 25 Feb 2026
> **Machine**: ThinkPad L14 Gen 4 (21H50022SG)
> **OS**: Ubuntu 24.04.4 LTS (Noble Numbat) x86_64
> **Source**: [verification-output-feb2026.txt](verification-output-feb2026.txt)

## System Info (fastfetch)

| Property | Value |
|----------|-------|
| OS | Ubuntu 24.04.4 LTS (Noble Numbat) x86_64 |
| Host | 21H50022SG (ThinkPad L14 Gen 4) |
| Kernel | Linux 6.17.0-14-generic |
| Uptime | 6 hours, 40 mins |
| Packages | 1588 (dpkg), 10 (snap) |
| Shell | fish 4.5.0 |
| Display | 1920x1080 in 14", 60 Hz |
| DE | GNOME 46.0 |
| WM | Mutter (Wayland) |
| Terminal | GNOME Terminal 3.52.0 |
| Terminal Font | FiraCode Nerd Font (12pt) |
| CPU | AMD Ryzen 7 PRO 7730U (16) @ 4.55 GHz |
| GPU | AMD Barcelo [Integrated] |
| Memory | 4.01 GiB / 14.42 GiB (28%) |

## Core System

| Tool | Output |
|------|--------|
| Fish | fish, version 4.5.0 |
| Git | git version 2.43.0 |

## Shell Plugins

| Tool | Output |
|------|--------|
| Fisher | fisher, version 4.4.8 |
| Tide | tide, version 6.2.0 |

## Node.js Ecosystem

| Tool | Output |
|------|--------|
| fnm | fnm 1.38.1 |
| Node.js | v25.6.1 |
| npm | 11.9.0 |

## Go

| Tool | Output |
|------|--------|
| Go | go version go1.26.0 linux/amd64 |

## System Utilities

| Tool | Output |
|------|--------|
| ShellCheck | version: 0.9.0 |
| direnv | 2.32.1 |
| fzf | 0.44.1 (debian) |

## GitHub

| Tool | Output |
|------|--------|
| gh | gh version 2.45.0 (2026-02-03 Ubuntu 2.45.0-1ubuntu0.3+esm2) |
| Auth | Logged in to github.com account kairin (keyring) |
| Protocol | https |
| Token scopes | gist, read:org, repo, workflow |

## Python / uv

| Tool | Output |
|------|--------|
| uv | uv 0.10.5 |

## AI Coding CLIs

| Tool | Output |
|------|--------|
| Claude Code | 2.1.52 (Claude Code) |
| Codex CLI | codex-cli 0.104.0 |
| Gemini CLI | 0.29.7 |

## Task & Spec Tools

| Tool | Output |
|------|--------|
| Backlog.md | 1.39.2 |
| Specify | ✅ Installed (verified via `--help`) |

## MCP Servers

### Claude Code MCP

| Server | URL | Status |
|--------|-----|--------|
| claude.ai Mermaid Chart | https://mcp.mermaidchart.com/mcp | ✅ Connected |
| claude.ai Hugging Face | https://huggingface.co/mcp?login&gradio=none | ✅ Connected |
| claude.ai Google Calendar | https://gcal.mcp.claude.com/mcp | ⚠️ Needs authentication |
| claude.ai Gmail | https://gmail.mcp.claude.com/mcp | ⚠️ Needs authentication |
| context7 | https://mcp.context7.com/mcp (HTTP) | ✅ Connected |

### Codex CLI MCP

| Name | Command | Status |
|------|---------|--------|
| context7 | npx -y @upstash/context7-mcp | enabled |

## Nerd Fonts

4 font families detected, with multiple variants:

| Family | Variants Installed |
|--------|--------------------|
| JetBrainsMono Nerd Font | Regular, Mono, Propo, NL (all weights) |
| FiraCode Nerd Font | Regular, Mono, Propo (all weights) |
| Hack Nerd Font | Regular, Mono, Propo |
| Meslo Nerd Font | LGS, LGM, LGL, LGSDZ, LGMDZ, LGLDZ (all sub-families, Regular/Mono/Propo) |

## Version Differences: xlsx (24 Feb) vs Output (25 Feb)

Some tools updated between the xlsx snapshot (24 Feb) and this verification run (25 Feb):

| Tool | xlsx (24 Feb) | Output (25 Feb) | Notes |
|------|---------------|-----------------|-------|
| Claude Code | 2.1.50 | 2.1.52 | Patch update |
| uv | 0.10.4 | 0.10.5 | Patch update |
| Gemini CLI | 0.29.5 | 0.29.7 | Patch update |
| Backlog.md | 1.38.0 | 1.39.2 | Minor update |
| Git | 2.47.3 (Pi test) | 2.43.0 (Ubuntu 24.04 apt) | Different distro versions |
| gh | 2.87.2 (Pi test) | 2.45.0 (Ubuntu 24.04 apt) | Ubuntu apt lags; Pi used GitHub's repo |
| ShellCheck | 0.10.0 (Pi test) | 0.9.0 (Ubuntu 24.04 apt) | Ubuntu apt ships older version |
| fzf | 0.60 (Pi test) | 0.44.1 (Ubuntu 24.04 apt) | Ubuntu apt ships older version |

> **Note**: The xlsx was verified on Raspberry Pi 4 (Debian Trixie) which uses newer apt packages for git, gh, ShellCheck, and fzf. Ubuntu 24.04 LTS ships older versions of these apt-managed tools. The AI CLIs (Claude, Gemini, Backlog) updated because they use npm/curl installers that always fetch latest.
