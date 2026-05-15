# gstack-browser: Docker workflow for browser automation on Ubuntu 26.04

Run gstack browser skills (`/qa`, `/browse`, `/qa-only`) inside an Ubuntu 24.04 container where Playwright + Chromium work natively. Use this on hosts where Playwright lacks support (e.g. Ubuntu 26.04, tracked at [microsoft/playwright#40117](https://github.com/microsoft/playwright/issues/40117)).

## Current status

This workflow is complete and verified on the Ubuntu 26.04 host as of 2026-05-16:

- Docker Engine 29.5.0 works without host `sudo` after `newgrp docker`
- `gstack-browser:latest` builds successfully
- `gstack-dev` starts and remains running after shell exit
- `./setup gstack-setup` completed inside the container
- Playwright Chromium downloaded successfully inside Ubuntu 24.04
- Codex CLI 0.130.0, Claude Code, Bun, and gstack `browse` are available
- passwordless `sudo -n true` works inside the container

Detailed rollout notes live at `../../docs/operations/gstack-browser-docker-rollout.md`.

## Quick start

From the dotfiles repo root:

```bash
# One-time: ensure Docker is installed (the dotfiles bootstrap can install it)
./setup            # uses TOOL_BASELINE which now includes docker

# Build the gstack-browser image (~5 minutes first time, cached after)
./setup docker-build

# Run gstack setup inside Ubuntu 24.04, not on the Ubuntu 26.04 host
./setup gstack-setup /home/kkk/Apps/gstack

# Start Codex in the gstack repo inside the container
./setup gstack-codex /home/kkk/Apps/gstack

# Enter a shell inside the container for manual debugging
./setup gstack-shell
```

Inside the container you can run `codex`, `claude`, `/qa`, `/review`, etc. and all gstack skills work the same as they would natively. The container mounts your host `~/Apps`, `~/.codex`, `~/.claude`, and `~/.gstack` directories, so your projects and skill state are shared.

If you are already inside `gstack-dev`, run `codex` directly. `./setup gstack-codex` is also safe inside the container; it detects the container and runs Codex without trying to call Docker.

Host git operations against `/home/kkk/Apps/gstack` are still fine. The Docker boundary is for `gstack ./setup` and browser-backed skill execution, because those are the paths that need Playwright Chromium.

## What's in the image

- Base: `mcr.microsoft.com/playwright:v1.60.0-noble` (Ubuntu 24.04 + Playwright + browsers)
- Bun 1.3.10 (gstack runtime)
- Codex CLI 0.130.0
- Claude Code CLI
- `git`, `gh`, `jq`, `ripgrep`, `fish`, `direnv`, `unzip`
- Host user mirrored inside the container with passwordless sudo

## Path preservation invariant

Container paths match host paths exactly:

| Host | Container |
|------|-----------|
| `/home/$USER/Apps` | `/home/$USER/Apps` |
| `/home/$USER/.codex` | `/home/$USER/.codex` |
| `/home/$USER/.claude` | `/home/$USER/.claude` |
| `/home/$USER/.gstack` | `/home/$USER/.gstack` |

This keeps absolute paths in gstack skill files working without translation. Do not change container HOME or mount paths.

## Token forwarding

Tokens from the dotfiles project's direnv-loaded local environment are passed to the container at startup via a generated `.env` file in this directory. The gstack container subcommands regenerate this file each time they start the container and only forward allowlisted variables (`GITHUB_TOKEN`, `CODACY_*`, `HF_*`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GOOGLE_*`, etc.).

## Files

- `Dockerfile` — image definition (Ubuntu 24.04 + Playwright + tools)
- `docker-compose.yml` — long-running container with volume mounts
- `.env` — generated at runtime by gstack container commands (gitignored)
- `README.md` — this file

## Persistence

`exit` leaves the shell but does not remove `gstack-dev`. Re-enter later with:

```bash
./setup gstack-shell
```

Files written under mounted paths persist on the host. Files written elsewhere inside the container persist only while the container exists.

## Publishing safety

It is acceptable to push the built `gstack-browser:latest` image to a private Docker Hub repository if you want reuse. Do not publish an image created with `docker commit gstack-dev`; the running container receives token environment variables from `.env`.

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
