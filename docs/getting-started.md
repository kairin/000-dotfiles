# Getting Started

Use this repo to set up a machine once, then keep it in sync with repeatable audits and menu-driven updates.
If you want command details, jump to [Setup Reference](setup-reference.md). For the flow diagrams, use [Architecture: Setup Flow](architecture/setup-flow.md).

## First-Time Setup

1. Clone the repo.
2. Run `./setup`.
3. Choose option 1 on a fresh machine.
4. Confirm the install preview.
5. When the menu returns, choose option 2 to apply safe config and font changes.
6. Run the sign-in commands the menu prints for your installed tools.

```bash
git clone https://github.com/kairin/000-dotfiles.git ~/000-dotfiles
cd ~/000-dotfiles
./setup
```

Option 1 installs or updates developer tools. Option 2 applies non-protected dotfiles and approved font recipes.
The menu refreshes after tool install so the recommended option can change as the machine state changes.

## Ongoing Maintenance

Run `./setup` again whenever you want to check drift or pick up new templates.

- Option 1 upgrades tools.
- Option 2 applies safe config drift.
- Option 3 prints full technical details.
- Option 4 shows tool and sign-in guidance.
- Option 5 exits without writing.

## Project Scaffolding

Use `./setup init --yes --project /path/to/project` to render `AGENTS.md` and the `CLAUDE.md` / `GEMINI.md` symlinks for a project.
If `project-vars.json` is missing, the wrapper infers sensible defaults from common project files before running `dotfiles_tools init-project`.

For the full project-doc flow, see [Architecture: Scaffold Flow](architecture/scaffold-flow.md).
