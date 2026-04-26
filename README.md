# dotfiles

Config templates for AI coding tools and shell environment.

## What's here

| Directory | Target path | Contents |
|---|---|---|
| `agents/` | project root | `AGENTS.md` / `CLAUDE.md` / `GEMINI.md` / `copilot-instructions.md` templates |
| `claude/` | `~/.claude/` | `settings.json`, `keybindings.json`, global `CLAUDE.md` |
| `codex/` | `~/.codex/` | `config.toml`, `rules/default.rules` |
| `gemini/` | `~/.gemini/` | `settings.json`, global `GEMINI.md` |
| `gh/` | `~/.config/gh/` | `config.yml` |
| `fish/` | `~/.config/fish/` | `fish_plugins`, `functions/direnv.fish`, `env.fish` |
| `git/` | `~/.config/git/` | `config` |

## Conventions

**`.template` suffix** — copy to the target path and fill in any `{{PLACEHOLDERS}}`.

**Symlinks** — `CLAUDE.md` and `GEMINI.md` always symlink to `AGENTS.md` so there is one source of truth per project:

```bash
ln -sf AGENTS.md CLAUDE.md
ln -sf AGENTS.md GEMINI.md
```

**Secrets** — no tokens, passwords, or API keys are ever stored here. Auth files (`hosts.yml`, `auth.json`, `oauth_creds.json`, `token`) are excluded. Use `huggingface-cli login`, `gh auth login`, `codex auth`, and env vars loaded from files outside this repo.

## Bootstrap a new machine

```bash
# Claude Code
cp claude/settings.json.template ~/.claude/settings.json
cp claude/keybindings.json.template ~/.claude/keybindings.json
cp claude/CLAUDE.md.template ~/.claude/CLAUDE.md

# Codex
cp codex/config.toml.template ~/.codex/config.toml
cp codex/rules/default.rules.template ~/.codex/rules/default.rules

# Gemini CLI
cp gemini/settings.json.template ~/.gemini/settings.json
cp gemini/GEMINI.md.template ~/.gemini/GEMINI.md

# gh CLI
cp gh/config.yml.template ~/.config/gh/config.yml

# Fish
cp fish/fish_plugins ~/.config/fish/fish_plugins
cp fish/functions/direnv.fish ~/.config/fish/functions/direnv.fish
cp fish/env.fish.template ~/.config/fish/env.fish

# Git
cp git/config ~/.config/git/config
```

## Bootstrap a new project repo

```bash
cp path/to/dotfiles/agents/AGENTS.md.template ./AGENTS.md
# fill in {{PLACEHOLDERS}} in AGENTS.md
ln -sf AGENTS.md CLAUDE.md
ln -sf AGENTS.md GEMINI.md

# optional: GitHub Copilot
mkdir -p .github
cp path/to/dotfiles/agents/copilot-instructions.md.template .github/copilot-instructions.md
```
