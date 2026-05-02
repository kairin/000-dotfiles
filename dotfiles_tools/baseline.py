from __future__ import annotations

import os
import shutil
from typing import Any


TOOL_BASELINE = (
    {
        "id": "uv",
        "label": "uv",
        "command": "uv",
        "bootstrap": True,
        "install_method": "manual",
        "install_args": {},
        "requires_sudo": False,
        "install_hint": "Installed automatically by ./setup when missing.",
    },
    {
        "id": "git",
        "label": "Git",
        "command": "git",
        "bootstrap": True,
        "install_method": "apt",
        "install_args": {"packages": ("git",)},
        "requires_sudo": True,
        "install_hint": "Installed by setup option 5 (apt).",
    },
    {
        "id": "gh",
        "label": "GitHub CLI",
        "command": "gh",
        "bootstrap": True,
        "install_method": "apt_keyring",
        "install_args": {
            "packages": ("gh",),
            "keyring_url": "https://cli.github.com/packages/githubcli-archive-keyring.gpg",
            "keyring_path": "/etc/apt/keyrings/githubcli-archive-keyring.gpg",
            "source_line": (
                "deb [arch={ARCH} signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg]"
                " https://cli.github.com/packages stable main"
            ),
            "source_path": "/etc/apt/sources.list.d/github-cli.list",
        },
        "requires_sudo": True,
        "install_hint": "Installed by setup option 5 (GitHub keyring repo).",
    },
    {
        "id": "fish",
        "label": "fish",
        "command": "fish",
        "bootstrap": True,
        "install_method": "apt",
        "install_args": {"packages": ("fish",)},
        "requires_sudo": True,
        "install_hint": "Installed by setup option 5 (apt).",
    },
    {
        "id": "direnv",
        "label": "direnv",
        "command": "direnv",
        "bootstrap": True,
        "install_method": "apt",
        "install_args": {"packages": ("direnv",)},
        "requires_sudo": True,
        "install_hint": "Installed by setup option 5 (apt).",
    },
    {
        "id": "codex",
        "label": "Codex CLI",
        "command": "codex",
        "bootstrap": True,
        "install_method": "npm",
        "install_args": {"package": "@openai/codex"},
        "requires_sudo": True,
        "install_hint": "Installed by setup option 5 (npm install -g @openai/codex).",
    },
    {
        "id": "claude",
        "label": "Claude Code",
        "command": "claude",
        "bootstrap": True,
        "install_method": "curl_installer",
        "install_args": {
            "url": "https://claude.ai/install.sh",
            "script_name": "claude-install.sh",
        },
        "requires_sudo": False,
        "install_hint": "Installed by setup option 5 (claude.ai/install.sh).",
    },
    {
        "id": "gemini",
        "label": "Gemini CLI",
        "command": "gemini",
        "bootstrap": True,
        "install_method": "npm",
        "install_args": {"package": "@google/gemini-cli"},
        "requires_sudo": True,
        "install_hint": "Installed by setup option 5 (npm install -g @google/gemini-cli).",
    },
)


# Grouped for readability when rendering the option-5 preview.
# Flattened into DEV_BASE_PACKAGES at module load. All packages live in
# Ubuntu main/universe; no third-party repos required.
DEV_BASE_GROUPS = (
    ("tls_keys",  ("ca-certificates", "gnupg", "apt-transport-https")),
    ("transfer",  ("curl", "wget")),
    ("archives",  ("unzip", "zip", "tar", "xz-utils")),
    ("build",     ("build-essential", "pkg-config", "make")),
    ("python",    ("python3", "python3-pip", "python3-venv")),
    ("node",      ("nodejs", "npm")),
    ("json_text", ("jq", "ripgrep", "fd-find")),
    ("editors",   ("vim", "nano")),
    ("shell",     ("tmux", "less", "man-db")),
    ("system",    ("htop", "tree", "file")),
    ("network",   ("openssh-client", "dnsutils", "iputils-ping", "net-tools")),
)
DEV_BASE_PACKAGES = tuple(pkg for _, group in DEV_BASE_GROUPS for pkg in group)


AUTH_GUIDANCE = (
    {
        "id": "gh",
        "tool": "gh",
        "command": "gh auth status",
        "guidance": "If it reports no authenticated host, run gh auth login.",
    },
    {
        "id": "codex",
        "tool": "codex",
        "command": "codex auth",
        "guidance": "Run when Codex CLI is installed and needs user authentication.",
    },
    {
        "id": "claude",
        "tool": "claude",
        "command": "claude login",
        "guidance": "Run when Claude Code CLI is installed and needs user authentication.",
    },
    {
        "id": "gemini",
        "tool": "gemini",
        "command": "gemini",
        "guidance": "Start Gemini CLI and complete its login/setup prompt if needed.",
    },
)


def collect_tool_baseline(path: str | None = None) -> dict[str, list[dict[str, Any]]]:
    search_path = path if path is not None else os.environ.get("PATH", "")
    tool_checks = [_tool_check(item, search_path) for item in TOOL_BASELINE]
    auth_guidance = [_auth_check(item, search_path) for item in AUTH_GUIDANCE]
    return {"tool_checks": tool_checks, "auth_guidance": auth_guidance}


def render_setup_guidance(path: str | None = None) -> str:
    baseline = collect_tool_baseline(path)
    missing_tools = [item for item in baseline["tool_checks"] if item["state"] == "missing"]
    available_auth = [item for item in baseline["auth_guidance"] if item["state"] == "available"]
    missing_auth_tools = [item for item in baseline["auth_guidance"] if item["state"] != "available"]

    lines = ["Tool status:"]
    _extend_missing_tools(lines, missing_tools)
    _extend_available_auth(lines, available_auth)
    _extend_missing_auth_tools(lines, missing_auth_tools)
    return "\n".join(lines) + "\n"


def _extend_missing_tools(lines: list[str], missing_tools: list[dict[str, Any]]) -> None:
    if not missing_tools:
        lines.append("  - No missing baseline tools. All expected commands are visible on PATH.")
        return
    lines.append("  Missing tools:")
    for item in missing_tools:
        if item.get("bootstrap"):
            hint = "Install via setup option 5 (Install / update developer tools)."
        else:
            hint = item["install_hint"]
        lines.append(f"    - {item['command']}: {hint}")


def _extend_available_auth(lines: list[str], available_auth: list[dict[str, Any]]) -> None:
    if not available_auth:
        return
    lines.append("")
    lines.append("Optional sign-in checks:")
    for item in available_auth:
        lines.append(f"  - {item['command']}: {item['guidance']}")


def _extend_missing_auth_tools(lines: list[str], missing_auth_tools: list[dict[str, Any]]) -> None:
    if not missing_auth_tools:
        return
    lines.append("")
    lines.append("Sign-in checks unavailable until the tool is installed:")
    for item in missing_auth_tools:
        lines.append(f"  - {item['tool']}")


def _tool_check(item: dict[str, Any], search_path: str) -> dict[str, Any]:
    found = shutil.which(item["command"], path=search_path)
    return {
        "id": item["id"],
        "label": item["label"],
        "command": item["command"],
        "state": "installed" if found else "missing",
        "path": found,
        "bootstrap": item["bootstrap"],
        "install_hint": item["install_hint"],
    }


def _auth_check(item: dict[str, str], search_path: str) -> dict[str, str]:
    found = shutil.which(item["tool"], path=search_path)
    return {
        "id": item["id"],
        "tool": item["tool"],
        "command": item["command"],
        "state": "available" if found else "tool_missing",
        "guidance": item["guidance"],
    }


if __name__ == "__main__":
    print(render_setup_guidance(), end="")
