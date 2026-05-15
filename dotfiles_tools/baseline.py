from __future__ import annotations

import json
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
                "Types: deb\n"
                "URIs: https://cli.github.com/packages/\n"
                "Suites: stable\n"
                "Components: main\n"
                "Architectures: {ARCH}\n"
                "Signed-By: /etc/apt/keyrings/githubcli-archive-keyring.gpg"
            ),
            "source_path": "/etc/apt/sources.list.d/github-cli.sources",
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
        "id": "docker",
        "label": "Docker Engine",
        "command": "docker",
        "bootstrap": True,
        "install_method": "apt_keyring",
        "install_args": {
            "packages": (
                "docker-ce",
                "docker-ce-cli",
                "containerd.io",
                "docker-buildx-plugin",
                "docker-compose-plugin",
            ),
            "keyring_url": "https://download.docker.com/linux/ubuntu/gpg",
            "keyring_path": "/etc/apt/keyrings/docker.gpg",
            "source_line": (
                "Types: deb\n"
                "URIs: https://download.docker.com/linux/ubuntu\n"
                "Suites: noble\n"
                "Components: stable\n"
                "Architectures: {ARCH}\n"
                "Signed-By: /etc/apt/keyrings/docker.gpg"
            ),
            "source_path": "/etc/apt/sources.list.d/docker.sources",
        },
        "requires_sudo": True,
        "install_hint": (
            "Provides the Ubuntu 24.04 container used by gstack browser skills "
            "on hosts where Playwright lacks native support."
        ),
        "post_install": (
            {
                "kind": "auto",
                "label": "Add user to docker group (re-login required to take effect)",
                "command_template": ("sudo", "usermod", "-aG", "docker", "{user}"),
            },
            {
                "kind": "guidance",
                "label": "Reload group membership in current shell",
                "command_template": ("newgrp", "docker"),
            },
            {
                "kind": "guidance",
                "label": "Build the gstack-browser image",
                "command_template": ("./setup", "docker-build"),
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
        "requires_sudo": False,
        "install_hint": "Installed by the setup tool-install menu option (npm install -g --prefix ~/.local @openai/codex).",
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
        "requires_sudo": False,
        "install_hint": "Installed by the setup tool-install menu option (npm install -g --prefix ~/.local @google/gemini-cli).",
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
        "requires_sudo": False,
        "install_hint": "Installed by the setup tool-install menu option (npm install -g --prefix ~/.local @github/copilot).",
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
    ("system",    ("htop", "tree", "file", "util-linux-extra")),
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
        "verify_file": "~/.codex/auth.json",
        "verify_json_paths": (("tokens", "access_token"), ("tokens", "refresh_token")),
        "signed_in_detail": "cached credentials present",
    },
    {
        "id": "claude",
        "tool": "claude",
        "command": "claude login",
        "guidance": "Run when Claude Code CLI is installed and needs user authentication.",
        "verify": ("claude", "auth", "status"),
    },
    {
        "id": "gemini",
        "tool": "gemini",
        "command": "gemini",
        "guidance": "Start Gemini CLI and complete its login/setup prompt if needed.",
        "verify_file": "~/.gemini/oauth_creds.json",
        "verify_json_paths": (("access_token",), ("refresh_token",)),
        "signed_in_detail": "cached OAuth credentials present",
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


def _extend_auth_status(lines: list[str], auth_items: list[dict[str, Any]]) -> None:
    visible = [item for item in auth_items if item["state"] != "tool_missing"]
    if not visible:
        return
    lines.append("")
    signed_in = [item for item in visible if item["state"] == "signed_in"]
    pending = [item for item in visible if item["state"] == "available"]
    _append_signed_in_block(lines, signed_in, has_pending=bool(pending))
    _append_pending_block(lines, pending, has_signed_in=bool(signed_in))
    if not signed_in and not pending:
        lines.append("")
        lines.append("  No auth guidance items applicable.")


def _append_signed_in_block(lines: list[str], signed_in: list[dict[str, Any]], *, has_pending: bool) -> None:
    if not signed_in:
        return
    lines.append("Verified sign-ins:")
    for item in signed_in:
        detail = item.get("signed_in_detail") or "signed in"
        lines.append(f"  [+] {item['command']}: {detail}")
    if not has_pending:
        lines.append("")
        lines.append("  All verifiable sign-ins confirmed.")


def _append_pending_block(lines: list[str], pending: list[dict[str, Any]], *, has_signed_in: bool) -> None:
    if not pending:
        return
    if has_signed_in:
        lines.append("")
    lines.append("Pending sign-ins:")
    for item in pending:
        lines.append(f"  [ ] {item['command']}: {item['guidance']}")


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


def _auth_check(item: dict[str, str], search_path: str, home: Path) -> dict[str, str]:
    tool = item.get("tool")
    base: dict[str, Any] = {
        "id": item["id"],
        "tool": tool,
        "command": item["command"],
        "guidance": item["guidance"],
    }

    if not _auth_tool_present(tool, search_path):
        return {**base, "state": "tool_missing"}

    verify_file = item.get("verify_file")
    if verify_file:
        return _auth_check_verify_file(base, verify_file, home, item.get("verify_json_paths"), item.get("signed_in_detail"))

    verify = item.get("verify")
    if verify:
        return _auth_check_verify_command(base, verify, search_path, home)

    return {**base, "state": "available"}


def _auth_tool_present(tool: str | None, search_path: str) -> bool:
    return bool(shutil.which(tool, path=search_path)) if tool else True


def _auth_check_verify_file(
    base: dict[str, Any],
    verify_file: str,
    home: Path,
    verify_json_paths: tuple[tuple[str, ...], ...] | None,
    signed_in_detail: str | None,
) -> dict[str, Any]:
    path = _resolve_auth_verify_file(home, verify_file)
    if verify_json_paths:
        return _auth_check_verify_json_file(base, path, verify_json_paths, signed_in_detail)
    return _auth_check_verify_text_file(base, path, signed_in_detail)


def _resolve_auth_verify_file(home: Path, verify_file: str) -> Path:
    # Resolve ~ against the audited home, not the process home.
    return home / verify_file.lstrip("~/") if verify_file.startswith("~/") else Path(verify_file)


def _auth_check_verify_json_file(
    base: dict[str, Any],
    path: Path,
    verify_json_paths: tuple[tuple[str, ...], ...],
    signed_in_detail: str | None,
) -> dict[str, Any]:
    if not path.exists():
        return {**base, "state": "available"}
    try:
        data = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return {**base, "state": "available"}
    if _json_paths_present(data, verify_json_paths):
        return {**base, "state": "signed_in", "signed_in_detail": signed_in_detail or "cached credentials present"}
    return {**base, "state": "available"}


def _auth_check_verify_text_file(base: dict[str, Any], path: Path, signed_in_detail: str | None) -> dict[str, Any]:
    if path.exists() and path.read_text().strip():
        return {**base, "state": "signed_in", "signed_in_detail": signed_in_detail or "cached credentials present"}
    return {**base, "state": "available"}


def _auth_check_verify_command(
    base: dict[str, Any],
    verify: tuple[str, ...],
    search_path: str,
    home: Path,
) -> dict[str, Any]:
    try:
        # Use the same PATH the tool was found on so the right binary is called.
        env = {**os.environ, "PATH": search_path, "HOME": str(home)}
        result = subprocess.run(  # nosec B603
            list(verify),
            capture_output=True,
            text=True,
            timeout=8,
            env=env,
        )
        if result.returncode == 0:
            detail = _extract_signed_in_detail(result.stdout + result.stderr)
            return {**base, "state": "signed_in", "signed_in_detail": detail}
    except Exception:  # noqa: BLE001
        pass
    return {**base, "state": "available"}


def _json_paths_present(data: Any, paths: tuple[tuple[str, ...], ...]) -> bool:
    for path in paths:
        node = data
        for key in path:
            if not isinstance(node, dict) or key not in node:
                return False
            node = node[key]
        if node in (None, "", [], {}):
            return False
    return True


def _extract_signed_in_detail(output: str) -> str:
    try:
        data = json.loads(output)
    except json.JSONDecodeError:
        data = None
    if isinstance(data, dict) and data.get("loggedIn") is True:
        email = data.get("email")
        org_name = data.get("orgName")
        auth_method = data.get("authMethod")
        if email and org_name:
            return f"{email} ({org_name})"
        if email:
            return str(email)
        if org_name:
            return str(org_name)
        if auth_method:
            return str(auth_method)
    for line in output.splitlines():
        line = line.strip()
        if "logged in" in line.lower() or "account" in line.lower():
            return line.lstrip("!✓- ") or "signed in"
    return "signed in"


if __name__ == "__main__":
    print(render_setup_guidance(), end="")
