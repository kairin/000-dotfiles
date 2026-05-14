# gstack-browser: Ubuntu 24.04 container for running gstack browser skills
# on hosts where Playwright lacks native support (e.g. Ubuntu 26.04 dev release).
#
# Base: Microsoft's official Playwright image. Ubuntu 24.04 (Noble), Playwright
# and all supported browsers preinstalled and patched together. We layer:
#   - host-matching user/uid/gid so mounted files keep correct ownership
#   - bun (gstack runtime)
#   - Claude Code CLI (so `claude` works inside the container)
#   - small CLI tools: git, gh, jq, ripgrep, fish, sudo
#
# Build:
#   docker build \
#     --build-arg HOST_UID=$(id -u) \
#     --build-arg HOST_GID=$(id -g) \
#     --build-arg HOST_USER=$USER \
#     -t gstack-browser:latest \
#     docker/gstack-browser/
#
# The container itself is started by `docker compose up -d` from this directory
# or by `./setup gstack-shell` from the dotfiles repo root.

FROM mcr.microsoft.com/playwright:v1.60.0-noble

ARG HOST_UID=1000
ARG HOST_GID=1000
ARG HOST_USER=kkk

# Replace the base image's default `pwuser` (uid 1000) with one matching the
# host user so volume-mounted files retain correct ownership. If uid/gid
# already exists for a different user, create the requested user fresh.
RUN set -eux; \
    if getent passwd "${HOST_UID}" >/dev/null && [ "${HOST_UID}" -eq 1000 ] && id pwuser >/dev/null 2>&1; then \
        usermod -l "${HOST_USER}" pwuser && \
        groupmod -n "${HOST_USER}" pwuser && \
        usermod -d "/home/${HOST_USER}" -m "${HOST_USER}" && \
        usermod -u "${HOST_UID}" "${HOST_USER}" && \
        groupmod -g "${HOST_GID}" "${HOST_USER}"; \
    else \
        groupadd -g "${HOST_GID}" "${HOST_USER}" 2>/dev/null || true; \
        useradd -m -u "${HOST_UID}" -g "${HOST_GID}" -s /bin/bash "${HOST_USER}" 2>/dev/null || true; \
    fi; \
    # Passwordless sudo for the host user inside the container (dev convenience).
    apt-get update && apt-get install -y --no-install-recommends sudo && \
    echo "${HOST_USER} ALL=(ALL) NOPASSWD: ALL" > "/etc/sudoers.d/${HOST_USER}" && \
    chmod 0440 "/etc/sudoers.d/${HOST_USER}" && \
    rm -rf /var/lib/apt/lists/*

# Core CLI tooling. The Playwright base image already has node and many libs;
# we add the ones gstack skills reach for.
RUN apt-get update && apt-get install -y --no-install-recommends \
      git gh jq ripgrep fish curl ca-certificates direnv \
    && rm -rf /var/lib/apt/lists/*

# Bun installed to /usr/local so it's on PATH for all users.
ARG BUN_VERSION=1.3.10
RUN curl -fsSL https://bun.sh/install -o /tmp/bun-install.sh && \
    BUN_INSTALL=/usr/local BUN_VERSION="${BUN_VERSION}" bash /tmp/bun-install.sh && \
    rm /tmp/bun-install.sh && \
    ln -sf /usr/local/bin/bun /usr/local/bin/bunx

# Claude Code CLI. Install best-effort: if the install URL changes upstream,
# the build continues and the user can install it manually inside the container.
RUN curl -fsSL https://claude.ai/install.sh -o /tmp/claude-install.sh && \
    bash /tmp/claude-install.sh || echo "WARNING: Claude install failed; run inside container later"; \
    rm -f /tmp/claude-install.sh

USER ${HOST_USER}
WORKDIR /home/${HOST_USER}
ENV PATH="/home/${HOST_USER}/.local/bin:/usr/local/bin:${PATH}"

# Keep the container alive so `docker exec` works for interactive sessions.
CMD ["sleep", "infinity"]
