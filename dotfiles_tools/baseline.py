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
        "install_hint": "Installed automatically by ./setup when missing.",
    },
    {
        "id": "git",
        "label": "Git",
        "command": "git",
        "bootstrap": False,
        "install_hint": "Install git with the operating-system package manager.",
    },
    {
        "id": "gh",
        "label": "GitHub CLI",
        "command": "gh",
        "bootstrap": False,
        "install_hint": "Install the GitHub CLI, then run gh auth status.",
    },
    {
        "id": "fish",
        "label": "fish",
        "command": "fish",
        "bootstrap": False,
        "install_hint": "Install fish with the operating-system package manager.",
    },
    {
        "id": "direnv",
        "label": "direnv",
        "command": "direnv",
        "bootstrap": False,
        "install_hint": "Install direnv and enable the shell hook.",
    },
    {
        "id": "codex",
        "label": "Codex CLI",
        "command": "codex",
        "bootstrap": False,
        "install_hint": "Install Codex CLI, then run codex auth.",
    },
    {
        "id": "claude",
        "label": "Claude Code",
        "command": "claude",
        "bootstrap": False,
        "install_hint": "Install Claude Code CLI, then run claude login.",
    },
    {
        "id": "gemini",
        "label": "Gemini CLI",
        "command": "gemini",
        "bootstrap": False,
        "install_hint": "Install Gemini CLI, then complete its login/setup flow.",
    },
)


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

    lines = ["Tool status:"]
    if missing_tools:
        lines.append("  Missing tools:")
        for item in missing_tools:
            lines.append(f"    - {item['command']}: {item['install_hint']}")
    else:
        lines.append("  - No missing baseline tools. All expected commands are visible on PATH.")

    available_auth = [item for item in baseline["auth_guidance"] if item["state"] == "available"]
    missing_auth_tools = [item for item in baseline["auth_guidance"] if item["state"] != "available"]
    if available_auth:
        lines.append("")
        lines.append("Optional sign-in checks:")
        for item in available_auth:
            lines.append(f"  - {item['command']}: {item['guidance']}")
    if missing_auth_tools:
        lines.append("")
        lines.append("Sign-in checks unavailable until the tool is installed:")
        for item in missing_auth_tools:
            lines.append(f"  - {item['tool']}")
    return "\n".join(lines) + "\n"


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
