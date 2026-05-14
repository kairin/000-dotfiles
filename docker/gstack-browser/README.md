# gstack-browser: Docker workflow for browser automation on Ubuntu 26.04

Run gstack browser skills (`/qa`, `/browse`, `/qa-only`) inside an Ubuntu 24.04 container where Playwright + Chromium work natively. Use this on hosts where Playwright lacks support (e.g. Ubuntu 26.04 "Resolute Raccoon", tracked at [microsoft/playwright#40117](https://github.com/microsoft/playwright/issues/40117)).

## Quick start

From the dotfiles repo root:

```bash
# One-time: ensure Docker is installed (the dotfiles bootstrap can install it)
./setup            # uses TOOL_BASELINE which now includes docker

# Build the gstack-browser image (~5 minutes first time, cached after)
./setup docker-build

# Enter a shell inside the container (auto-starts if not running)
./setup gstack-shell
```

Inside the container you can run `claude`, `/qa`, `/review`, etc. and all gstack skills work the same as they would natively. The container mounts your host `~/Apps`, `~/.claude`, and `~/.gstack` directories, so your projects and skill state are shared.

## What's in the image

- Base: `mcr.microsoft.com/playwright:v1.60.0-noble` (Ubuntu 24.04 + Playwright + browsers)
- Bun 1.3.10 (gstack runtime)
- Claude Code CLI
- `git`, `gh`, `jq`, `ripgrep`, `fish`, `direnv`
- Host user mirrored inside the container with passwordless sudo

## Path preservation invariant

Container paths match host paths exactly:

| Host | Container |
|------|-----------|
| `/home/$USER/Apps` | `/home/$USER/Apps` |
| `/home/$USER/.claude` | `/home/$USER/.claude` |
| `/home/$USER/.gstack` | `/home/$USER/.gstack` |

This keeps absolute paths in gstack skill files working without translation. Do not change container HOME or mount paths.

## Token forwarding

Tokens from `.envrc.local` (the dotfiles project's local env file) are passed to the container at startup via a generated `.env` file in this directory. The `gstack-shell` subcommand regenerates this file each time it starts the container. See `setup` (`cmd_gstack_shell`) for the list of forwarded variables.

## Files

- `Dockerfile` — image definition (Ubuntu 24.04 + Playwright + tools)
- `docker-compose.yml` — long-running container with volume mounts
- `.env` — generated at runtime by `./setup gstack-shell` (gitignored)
- `README.md` — this file

## Rebuild / update

```bash
./setup docker-build
docker compose -f docker/gstack-browser/docker-compose.yml down
./setup gstack-shell    # starts fresh with new image
```

## Remove

```bash
docker compose -f docker/gstack-browser/docker-compose.yml down
docker rmi gstack-browser:latest
```

## When this becomes obsolete

Once Playwright adds Ubuntu 26.04 support (issue #40117), this Docker workflow becomes optional — gstack browser skills will work natively on the host again. The Docker path can stay as a fallback for users on niche platforms.
