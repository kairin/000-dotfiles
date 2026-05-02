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
        "post_install": (),
    },
    {
        "id": "git",
        "label": "Git",
        "command": "git",
        "bootstrap": True,
        "install_method": "apt",
        "install_args": {"packages": ("git",)},
        "requires_sudo": True,
        "install_hint": "Installed by the setup tool-install menu option (apt).",
        "post_install": (
            {
                "kind": "guidance",
                "label": "Configure git identity (skip if git/config already sets it)",
                "command_template": ("git", "config", "--global", "user.email", "<your-email>"),
            },
        ),
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
        "install_hint": "Installed by the setup tool-install menu option (GitHub keyring repo).",
        "post_install": (
            {
                "kind": "guidance",
                "label": "Sign in to GitHub CLI",
                "command_template": ("gh", "auth", "login"),
            },
        ),
    },
    {
        "id": "fish",
        "label": "fish",
        "command": "fish",
        "bootstrap": True,
        "install_method": "apt",
        "install_args": {"packages": ("fish",)},
        "requires_sudo": True,
        "install_hint": "Installed by the setup tool-install menu option (apt).",
        "post_install": (
            {
                "kind": "auto",
                "label": "Set fish as default shell",
                "command_template": ("sudo", "chsh", "-s", "{which:fish}", "{user}"),
            },
            {
                "kind": "auto",
                "label": "Bootstrap fisher (one-time)",
                "command_template": (
                    "fish",
                    "-c",
                    "curl -sL https://raw.githubusercontent.com/jorgebucaran/fisher/main/functions/fisher.fish | source && fisher install jorgebucaran/fisher",
                ),
            },
            {
                "kind": "auto",
                "label": "Apply fish_plugins via fisher update",
                "command_template": ("fish", "-c", "fisher update"),
                "requires_protected_apply": ("fish/fish_plugins",),
            },
        ),
    },
    {
        "id": "direnv",
        "label": "direnv",
        "command": "direnv",
        "bootstrap": True,
        "install_method": "apt",
        "install_args": {"packages": ("direnv",)},
        "requires_sudo": True,
        "install_hint": "Installed by the setup tool-install menu option (apt).",
        "post_install": (),  # hook is in fish/direnv.fish.template; no manual step needed
    },
    {
        "id": "codex",
        "label": "Codex CLI",
        "command": "codex",
        "bootstrap": True,
        "install_method": "npm",
        "install_args": {"package": "@openai/codex"},
        "requires_sudo": True,
        "install_hint": "Installed by the setup tool-install menu option (npm install -g @openai/codex).",
        "post_install": (
            {
                "kind": "guidance",
                "label": "Sign in to Codex CLI",
                "command_template": ("codex", "auth", "login"),
            },
        ),
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
            "interpreter": "bash",
        },
        "requires_sudo": False,
        "install_hint": "Installed by the setup tool-install menu option (claude.ai/install.sh).",
        "post_install": (
            {
                "kind": "guidance",
                "label": "Sign in to Claude Code",
                "command_template": ("claude", "/login"),
            },
        ),
    },
    {
        "id": "gemini",
        "label": "Gemini CLI",
        "command": "gemini",
        "bootstrap": True,
        "install_method": "npm",
        "install_args": {"package": "@google/gemini-cli"},
        "requires_sudo": True,
        "install_hint": "Installed by the setup tool-install menu option (npm install -g @google/gemini-cli).",
        "post_install": (
            {
                "kind": "guidance",
                "label": "Sign in to Gemini CLI",
                "command_template": ("gemini",),
            },
        ),
    },
    {
        "id": "copilot",
        "label": "GitHub Copilot CLI",
        "command": "copilot",
        "bootstrap": True,
        "install_method": "npm",
        "install_args": {"package": "@github/copilot"},
        "requires_sudo": True,
        "install_hint": "Installed by the setup tool-install menu option (npm install -g @github/copilot).",
        "post_install": (
            {
                "kind": "guidance",
                "label": "Sign in to GitHub Copilot CLI",
                "command_template": ("copilot", "/login"),
            },
        ),
    },
    {
        "id": "specify",
        "label": "SpecKit CLI",
        "command": "specify",
        "bootstrap": True,
        "install_method": "uv_tool",
        "install_args": {
            "package": "specify-cli",
            "from_url": "git+https://github.com/github/spec-kit.git",
        },
        "requires_sudo": False,
        "install_hint": "Installed by the setup tool-install menu option (uv tool install specify-cli).",
        "post_install": (
            {
                "kind": "guidance",
                "label": "Initialise SpecKit in a project",
                "command_template": ("specify", "init", "--here"),
            },
        ),
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
    ("network",   ("openssh-client", "bind9-dnsutils", "iputils-ping", "net-tools")),
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
    {
        "id": "copilot",
        "tool": "copilot",
        "command": "copilot auth",
        "guidance": "Run when GitHub Copilot CLI is installed and needs user authentication.",
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
            hint = "Install via the setup tool-install menu option."
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
