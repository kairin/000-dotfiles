# gstack Browser Docker Rollout

**Status:** Complete and verified
**Date:** 2026-05-16

## What Was Completed

- Docker Engine is installed through the `./setup` developer-tools flow.
- The Docker post-install action adds `kkk` to the `docker` group.
- `util-linux-extra` is part of the dev-base package set so `newgrp docker` is available on Ubuntu 26.04.
- Host Docker access works without `sudo` after refreshing group membership.
- `gstack-browser:latest` builds successfully from the Ubuntu 24.04 Playwright base image.
- `gstack-dev` starts as a long-running Docker Compose container.
- `./setup gstack-setup` runs gstack setup inside the container instead of on the Ubuntu 26.04 host.
- `./setup gstack-codex` and `./setup gstack-shell` work from the host.
- `./setup gstack-codex` is context-aware inside the container and runs `codex` directly instead of requiring Docker.

## Fixes Made During Rollout

- Docker apt keyrings are dearmored when an ASCII-armored key is downloaded to a `.gpg` path.
- Apt keyring sources are prepared before any `apt-get update`, so a stale/broken third-party source cannot break earlier apt operations.
- The Docker image installs `unzip` before running the Bun installer.
- The Docker image handles the Playwright base image's `ubuntu` user at UID 1000 and maps it to the host user.
- The setup wrapper uses the account UID/GID, not temporary `sg` or `newgrp` group state, when building the container.
- Docker permission errors now explain inactive group membership and point to `newgrp docker`.
- The compose environment sets `GSTACK_CONTAINER=1` so wrapper commands can detect when they are already inside the container.

## Verified State

Host:

```bash
docker info --format '{{.ServerVersion}}'
# 29.5.0
```

Container:

```bash
./setup gstack-shell
sudo -n true && echo sudo-ok
codex --version
/home/kkk/Apps/gstack/browse/dist/browse --help | head
```

Verified results:

- `sudo-ok`
- `codex-cli 0.130.0`
- `browse` prints the gstack browser help text
- container user is `uid=1000(kkk) gid=1000(kkk)`

## Daily Use

From the host:

```bash
cd /home/kkk/Apps/000-dotfiles
./setup gstack-shell
```

Inside the container, run Codex directly:

```bash
codex
```

The host wrapper is also safe from inside the container:

```bash
./setup gstack-codex
```

## Persistence

Exiting the shell does not remove the container. `gstack-dev` remains available for re-entry.

Mounted host paths persist on the host:

- `/home/kkk/Apps`
- `/home/kkk/.codex`
- `/home/kkk/.claude`
- `/home/kkk/.gstack`
- `/home/kkk/.config/gh`

Files written outside mounted paths persist only while the container exists.

## Docker Hub Safety

Pushing `gstack-browser:latest` as an image is acceptable if the repository is private or the personal assumptions are intentional. Do not publish an image created with `docker commit gstack-dev`, because the running container receives token environment variables from `docker/gstack-browser/.env`.

The built image does not bake in `.envrc.local`, GitHub tokens, Codacy tokens, `~/.codex`, `~/.claude`, or `~/.config/gh`.

