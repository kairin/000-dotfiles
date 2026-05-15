# gstack-browser: Ubuntu 24.04 container for running gstack browser skills
# on hosts where Playwright lacks native support (e.g. Ubuntu 26.04 dev release).
#
# Base: Microsoft's official Playwright image. Ubuntu 24.04 (Noble), Playwright
# and all supported browsers preinstalled and patched together. We layer:
#   - host-matching user/uid/gid so mounted files keep correct ownership
#   - bun (gstack runtime)
#   - Codex CLI (so `codex` works inside the container)
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

# Ensure an account matching the host uid/gid exists so volume-mounted files
# retain correct ownership. Playwright images may already have uid 1000 assigned
# to `ubuntu` while `pwuser` uses a different uid, so key off the target uid.
RUN set -eux; \
    target_user="$(getent passwd "${HOST_UID}" | cut -d: -f1 || true)"; \
    existing_host_uid="$(id -u "${HOST_USER}" 2>/dev/null || true)"; \
    if [ -n "${existing_host_uid}" ] && [ "${existing_host_uid}" != "${HOST_UID}" ]; then \
        userdel -r "${HOST_USER}" 2>/dev/null || userdel "${HOST_USER}"; \
    fi; \
    if [ -n "${target_user}" ]; then \
        target_group="$(id -gn "${target_user}")"; \
        if [ "${target_group}" = "${target_user}" ] && [ "${target_group}" != "${HOST_USER}" ] && ! getent group "${HOST_USER}" >/dev/null; then \
            groupmod -n "${HOST_USER}" "${target_group}"; \
        fi; \
        if [ "${target_user}" != "${HOST_USER}" ]; then usermod -l "${HOST_USER}" "${target_user}"; fi; \
        usermod -d "/home/${HOST_USER}" -m "${HOST_USER}"; \
        current_gid="$(id -g "${HOST_USER}")"; \
        if [ "${current_gid}" != "${HOST_GID}" ]; then \
            if getent group "${HOST_GID}" >/dev/null; then \
                usermod -g "${HOST_GID}" "${HOST_USER}"; \
            else \
                groupmod -g "${HOST_GID}" "$(id -gn "${HOST_USER}")"; \
            fi; \
        fi; \
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
      git gh jq ripgrep fish curl ca-certificates direnv unzip \
    && rm -rf /var/lib/apt/lists/*

# Bun installed to /usr/local so it's on PATH for all users.
ARG BUN_VERSION=1.3.10
RUN curl -fsSL https://bun.sh/install -o /tmp/bun-install.sh && \
    BUN_INSTALL=/usr/local BUN_VERSION="${BUN_VERSION}" bash /tmp/bun-install.sh && \
    rm /tmp/bun-install.sh && \
    ln -sf /usr/local/bin/bun /usr/local/bin/bunx

# Codex CLI, pinned to the host-tested version for reproducible container use.
ARG CODEX_VERSION=0.130.0
RUN npm install -g --prefix /usr/local "@openai/codex@${CODEX_VERSION}" && \
    codex --version

USER ${HOST_USER}
WORKDIR /home/${HOST_USER}
ENV PATH="/home/${HOST_USER}/.local/bin:/usr/local/bin:${PATH}"

# Claude Code CLI. Install best-effort: if the install URL changes upstream,
# the build continues and the user can install it manually inside the container.
RUN curl -fsSL https://claude.ai/install.sh -o /tmp/claude-install.sh && \
    bash /tmp/claude-install.sh || echo "WARNING: Claude install failed; run inside container later"; \
    rm -f /tmp/claude-install.sh

# Keep the container alive so `docker exec` works for interactive sessions.
CMD ["sleep", "infinity"]
