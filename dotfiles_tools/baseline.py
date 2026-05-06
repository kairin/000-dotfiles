from __future__ import annotations

import os
import shutil
import subprocess  # nosec B404
from pathlib import Path
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
    {
        "id": "huggingface",
        "label": "HuggingFace Hub",
        "command": "hf",
        "bootstrap": True,
        "install_method": "uv_tool",
        "install_args": {
            "package": "huggingface-hub",
        },
        "requires_sudo": False,
        "install_hint": "Installed by the setup tool-install menu option (uv tool install huggingface-hub).",
        "post_install": (
            {
                "kind": "guidance",
                "label": "Sign in to HuggingFace",
                "command_template": ("hf", "auth", "login"),
            },
        ),
    },
    {
        "id": "codacy-cli",
        "label": "Codacy CLI",
        "command": "codacy-cli",
        "bootstrap": True,
        "install_method": "curl_installer",
        "install_args": {
            "url": "https://raw.githubusercontent.com/codacy/codacy-cli-v2/main/codacy-cli.sh",
            "script_name": "codacy-cli.sh",
            "interpreter": "bash",
            "install_to": "~/.local/bin/codacy-cli",
        },
        "requires_sudo": False,
        "install_hint": "Installed by the setup tool-install menu option (codacy-cli-v2 install script).",
        "post_install": (),
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
        "verify": ("gh", "auth", "status"),
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
        "command": "copilot /login",
        "guidance": "Run when GitHub Copilot CLI is installed and needs user authentication.",
    },
    {
        "id": "huggingface",
        "tool": "hf",
        "command": "hf auth status",
        "guidance": "Run 'hf auth login' to authenticate with the HuggingFace Hub.",
        "verify": ("hf", "auth", "status"),
    },
)


def collect_tool_baseline(path: str | None = None, home: Path | None = None) -> dict[str, list[dict[str, Any]]]:
    search_path = path if path is not None else os.environ.get("PATH", "")
    resolved_home = home if home is not None else Path.home()
    tool_checks = [_tool_check(item, search_path) for item in TOOL_BASELINE]
    auth_guidance = [_auth_check(item, search_path, resolved_home) for item in AUTH_GUIDANCE]
    return {"tool_checks": tool_checks, "auth_guidance": auth_guidance}


def render_setup_guidance(path: str | None = None) -> str:
    baseline = collect_tool_baseline(path)
    missing_tools = [item for item in baseline["tool_checks"] if item["state"] == "missing"]
    auth_items = baseline["auth_guidance"]

    lines = ["Tool status:"]
    _extend_missing_tools(lines, missing_tools)
    _extend_auth_status(lines, auth_items)
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


def _auth_item_line(item: dict[str, Any]) -> str:
    if item["state"] == "signed_in":
        marker, detail = "[+]", item.get("signed_in_detail") or "signed in"
    else:
        marker, detail = "[ ]", item["guidance"]
    return f"  {marker} {item['command']}: {detail}"


def _extend_auth_status(lines: list[str], auth_items: list[dict[str, Any]]) -> None:
    visible = [item for item in auth_items if item["state"] != "tool_missing"]
    if not visible:
        return
    lines.append("")
    lines.append("Sign-in status:")
    lines.extend(_auth_item_line(item) for item in visible)
    if all(item["state"] == "signed_in" for item in visible):
        lines.append("")
        lines.append("  All verifiable sign-ins confirmed.")


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


def _check_verify_file(base: dict[str, Any], home: Path, verify_file: str) -> dict[str, Any]:
    # Resolve ~ against the audited home, not the process home.
    p = home / verify_file.lstrip("~/") if verify_file.startswith("~/") else Path(verify_file)
    if p.exists() and p.read_text().strip():
        return {**base, "state": "signed_in", "signed_in_detail": f"token present at {verify_file}"}
    return {**base, "state": "available"}


def _run_verify_cmd(
    base: dict[str, Any], verify: Any, search_path: str, home: Path
) -> dict[str, Any]:
    if not isinstance(verify, (list, tuple)) or not all(isinstance(arg, str) for arg in verify):
        return {**base, "state": "available"}
    env = {**os.environ, "PATH": search_path, "HOME": str(home)}
    try:
        result = subprocess.run(verify, capture_output=True, text=True, timeout=8, env=env)  # nosec B603 # nosemgrep: dangerous-subprocess-use-audit
        if result.returncode == 0:
            detail = _extract_signed_in_detail(result.stdout + result.stderr)
            return {**base, "state": "signed_in", "signed_in_detail": detail}
        return {**base, "state": "available"}
    except Exception:  # noqa: BLE001
        return {**base, "state": "available"}


def _auth_check(item: dict[str, str], search_path: str, home: Path) -> dict[str, str]:
    tool = item.get("tool")
    found = shutil.which(tool, path=search_path) if tool else None
    tool_present = bool(found) or tool is None

    base: dict[str, Any] = {
        "id": item["id"],
        "tool": tool,
        "command": item["command"],
        "guidance": item["guidance"],
    }

    if not tool_present:
        return {**base, "state": "tool_missing"}
    verify_file = item.get("verify_file")
    if verify_file:
        return _check_verify_file(base, home, verify_file)
    verify = item.get("verify")
    if verify:
        return _run_verify_cmd(base, verify, search_path, home)
    return {**base, "state": "available"}


def _extract_signed_in_detail(output: str) -> str:
    for line in output.splitlines():
        line = line.strip()
        if "logged in" in line.lower() or "account" in line.lower():
            return line.lstrip("!✓- ") or "signed in"
    return "signed in"


if __name__ == "__main__":
    print(render_setup_guidance(), end="")
