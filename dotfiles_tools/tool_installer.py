from __future__ import annotations

import os
from pathlib import Path
import sys
from typing import Any, Mapping

from .baseline import DEV_BASE_GROUPS, DEV_BASE_PACKAGES, TOOL_BASELINE
from .font_runner import CommandRunner


TOOL_CACHE_REL = ".cache/000-dotfiles/tool-installers"
DEV_BASE_ENTRY_ID = "tools.dev_base"


__all__ = (
    "build_tool_install_plan",
    "execute_tool_install_operation",
    "TOOL_CACHE_REL",
    "DEV_BASE_ENTRY_ID",
)


def build_tool_install_plan(
    home: Path | str,
    *,
    env: Mapping[str, str] | None = None,
    path: str | None = None,
    runner: CommandRunner | None = None,
) -> dict[str, Any]:
    home_path = Path(home).expanduser().resolve()
    effective_env = dict(os.environ if env is None else env)
    effective_path = path if path is not None else effective_env.get("PATH", "")
    effective_runner = runner or CommandRunner(env=effective_env, path=effective_path)
    cache_dir = home_path / TOOL_CACHE_REL

    if not _is_linux(effective_env):
        return _unsupported_plan(effective_runner)

    entries: list[dict[str, Any]] = []
    operations: list[dict[str, Any]] = []
    tools: list[dict[str, Any]] = []

    _extend_dev_base_plan(effective_runner, cache_dir, entries, operations, tools)
    _extend_tool_baseline_plan(effective_runner, cache_dir, entries, operations, tools)

    return {"entries": entries, "operations": operations, "tools": tools}


def execute_tool_install_operation(
    op: dict[str, Any],
    *,
    runner: CommandRunner | None = None,
    cache_dir: Path | str | None = None,
) -> int:
    effective_runner = runner or CommandRunner()
    op_cache = Path(cache_dir or op.get("cache_dir") or Path.home() / TOOL_CACHE_REL)
    op_type = op["type"]
    handlers = _operation_handlers(effective_runner, op_cache)
    handler = handlers.get(op_type)
    if handler is None:
        raise RuntimeError(f"unknown tool install operation: {op_type}")
    return handler(op)


def _operation_handlers(runner: CommandRunner, cache_dir: Path) -> dict[str, Any]:
    return {
        "tool_install_apt": lambda op: _execute_apt(op, runner, mode="install"),
        "tool_install_apt_upgrade": lambda op: _execute_apt(op, runner, mode="upgrade"),
        "tool_install_apt_keyring": lambda op: _execute_apt_keyring(op, runner, cache_dir),
        "tool_install_curl": lambda op: _execute_curl(op, runner, cache_dir),
        "tool_install_npm": lambda op: _execute_npm(op, runner, mode="install"),
        "tool_install_npm_upgrade": lambda op: _execute_npm(op, runner, mode="upgrade"),
        "tool_install_skip": lambda op: 0,
    }


# ---------------------------------------------------------------------------
# Platform gating
# ---------------------------------------------------------------------------


def _is_linux(env: Mapping[str, str]) -> bool:
    forced = env.get("DOTFILES_TOOL_PLATFORM")
    if forced:
        return forced.lower() == "linux"
    return sys.platform.startswith("linux")


def _unsupported_plan(runner: CommandRunner) -> dict[str, Any]:
    entries = [
        {
            "entry_id": DEV_BASE_ENTRY_ID,
            "recipe": "tool_installs",
            "label": "Developer base packages",
            "command": None,
            "state": "unsupported",
            "install_method": "apt",
            "action": "manual",
            "reason": "tool installs are Linux/Ubuntu-only in v1",
        }
    ]
    for item in TOOL_BASELINE:
        if not item.get("bootstrap") or item["install_method"] == "manual":
            continue
        entries.append(
            {
                "entry_id": f"tools.{item['id']}",
                "recipe": "tool_installs",
                "label": item["label"],
                "command": item["command"],
                "state": "unsupported",
                "install_method": item["install_method"],
                "action": "manual",
                "reason": "tool installs are Linux/Ubuntu-only in v1",
            }
        )
    return {"entries": entries, "operations": [], "tools": []}


# ---------------------------------------------------------------------------
# Dev-base apt bundle
# ---------------------------------------------------------------------------


def _extend_dev_base_plan(
    runner: CommandRunner,
    cache_dir: Path,
    entries: list[dict[str, Any]],
    operations: list[dict[str, Any]],
    tools: list[dict[str, Any]],
) -> None:
    package_states = {pkg: _dpkg_installed(runner, pkg) for pkg in DEV_BASE_PACKAGES}
    missing = tuple(pkg for pkg in DEV_BASE_PACKAGES if not package_states[pkg])
    installed = tuple(pkg for pkg in DEV_BASE_PACKAGES if package_states[pkg])
    groups_summary = []
    for name, group_pkgs in DEV_BASE_GROUPS:
        groups_summary.append(
            {
                "name": name,
                "packages": list(group_pkgs),
                "installed": [pkg for pkg in group_pkgs if package_states[pkg]],
                "missing": [pkg for pkg in group_pkgs if not package_states[pkg]],
            }
        )

    if missing and installed:
        state = "needs_update"
        action = "install_and_upgrade"
    elif missing:
        state = "missing"
        action = "install"
    else:
        state = "installed"
        action = "upgrade"

    entry = {
        "entry_id": DEV_BASE_ENTRY_ID,
        "recipe": "tool_installs",
        "label": "Developer base packages",
        "command": None,
        "state": state,
        "install_method": "apt",
        "action": action,
        "missing_packages": list(missing),
        "installed_packages": list(installed),
        "groups": groups_summary,
        "total_packages": len(DEV_BASE_PACKAGES),
    }
    entries.append(entry)
    tools.append(entry)

    if missing:
        operations.append(
            _apt_op(
                entry_id=DEV_BASE_ENTRY_ID,
                op_type="tool_install_apt",
                packages=list(missing),
                requires_sudo=True,
                cache_dir=cache_dir,
                reason=f"install {len(missing)} missing dev-base packages",
            )
        )
    if installed:
        operations.append(
            _apt_op(
                entry_id=DEV_BASE_ENTRY_ID,
                op_type="tool_install_apt_upgrade",
                packages=list(installed),
                requires_sudo=True,
                cache_dir=cache_dir,
                reason=f"upgrade {len(installed)} installed dev-base packages",
            )
        )


# ---------------------------------------------------------------------------
# Tool baseline (per-tool)
# ---------------------------------------------------------------------------


def _extend_tool_baseline_plan(
    runner: CommandRunner,
    cache_dir: Path,
    entries: list[dict[str, Any]],
    operations: list[dict[str, Any]],
    tools: list[dict[str, Any]],
) -> None:
    for item in TOOL_BASELINE:
        if not item.get("bootstrap") or item["install_method"] == "manual":
            continue
        entry, ops = _plan_tool_entry(item, runner, cache_dir)
        entries.append(entry)
        tools.append(entry)
        operations.extend(ops)


def _plan_tool_entry(
    item: Mapping[str, Any],
    runner: CommandRunner,
    cache_dir: Path,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    method = item["install_method"]
    found_path = runner.which(item["command"])
    base_entry: dict[str, Any] = {
        "entry_id": f"tools.{item['id']}",
        "recipe": "tool_installs",
        "label": item["label"],
        "command": item["command"],
        "install_method": method,
        "requires_sudo": item.get("requires_sudo", False),
    }
    if found_path:
        base_entry.update(
            {
                "state": "installed",
                "current_path": found_path,
                "current_version": _detect_version(item["command"], found_path, runner),
                "action": "upgrade",
            }
        )
        ops = _upgrade_operations(item, cache_dir)
    else:
        base_entry.update({"state": "missing", "action": "install"})
        ops = _install_operations(item, cache_dir)
    return base_entry, ops


def _install_operations(item: Mapping[str, Any], cache_dir: Path) -> list[dict[str, Any]]:
    method = item["install_method"]
    args = dict(item.get("install_args") or {})
    entry_id = f"tools.{item['id']}"
    if method == "apt":
        return [
            _apt_op(
                entry_id=entry_id,
                op_type="tool_install_apt",
                packages=list(args.get("packages") or ()),
                requires_sudo=item.get("requires_sudo", True),
                cache_dir=cache_dir,
                reason=f"install {item['label']} via apt",
            )
        ]
    if method == "apt_keyring":
        return [_apt_keyring_op(entry_id, item, args, cache_dir, mode="install")]
    if method == "curl_installer":
        return [_curl_op(entry_id, item, args, cache_dir, mode="install")]
    if method == "npm":
        return [_npm_op(entry_id, item, args, cache_dir, mode="install")]
    return []


def _upgrade_operations(item: Mapping[str, Any], cache_dir: Path) -> list[dict[str, Any]]:
    method = item["install_method"]
    args = dict(item.get("install_args") or {})
    entry_id = f"tools.{item['id']}"
    if method == "apt":
        return [
            _apt_op(
                entry_id=entry_id,
                op_type="tool_install_apt_upgrade",
                packages=list(args.get("packages") or ()),
                requires_sudo=item.get("requires_sudo", True),
                cache_dir=cache_dir,
                reason=f"upgrade {item['label']} via apt --only-upgrade",
            )
        ]
    if method == "apt_keyring":
        return [_apt_keyring_op(entry_id, item, args, cache_dir, mode="upgrade")]
    if method == "curl_installer":
        # Re-running self-updating installers (claude.ai/install.sh) refreshes the install.
        return [_curl_op(entry_id, item, args, cache_dir, mode="upgrade")]
    if method == "npm":
        return [_npm_op(entry_id, item, args, cache_dir, mode="upgrade")]
    return []


# ---------------------------------------------------------------------------
# Operation factories
# ---------------------------------------------------------------------------


def _apt_op(
    *,
    entry_id: str,
    op_type: str,
    packages: list[str],
    requires_sudo: bool,
    cache_dir: Path,
    reason: str,
) -> dict[str, Any]:
    return {
        "entry_id": entry_id,
        "recipe": "tool_installs",
        "type": op_type,
        "packages": packages,
        "requires_sudo": requires_sudo,
        "requires_network": True,
        "requires_approval": True,
        "cache_dir": str(cache_dir),
        "reason": reason,
    }


def _apt_keyring_op(
    entry_id: str,
    item: Mapping[str, Any],
    args: Mapping[str, Any],
    cache_dir: Path,
    *,
    mode: str,
) -> dict[str, Any]:
    return {
        "entry_id": entry_id,
        "recipe": "tool_installs",
        "type": "tool_install_apt_keyring",
        "mode": mode,
        "packages": list(args.get("packages") or ()),
        "keyring_url": args["keyring_url"],
        "keyring_path": args["keyring_path"],
        "source_line": args["source_line"],
        "source_path": args["source_path"],
        "requires_sudo": True,
        "requires_network": True,
        "requires_approval": True,
        "cache_dir": str(cache_dir),
        "reason": f"{mode} {item['label']} via GitHub keyring repo",
    }


def _curl_op(
    entry_id: str,
    item: Mapping[str, Any],
    args: Mapping[str, Any],
    cache_dir: Path,
    *,
    mode: str,
) -> dict[str, Any]:
    return {
        "entry_id": entry_id,
        "recipe": "tool_installs",
        "type": "tool_install_curl",
        "mode": mode,
        "url": args["url"],
        "script_name": args.get("script_name", "installer.sh"),
        "requires_sudo": item.get("requires_sudo", False),
        "requires_network": True,
        "requires_approval": True,
        "cache_dir": str(cache_dir),
        "reason": f"{mode} {item['label']} via {args['url']}",
    }


def _npm_op(
    entry_id: str,
    item: Mapping[str, Any],
    args: Mapping[str, Any],
    cache_dir: Path,
    *,
    mode: str,
) -> dict[str, Any]:
    op_type = "tool_install_npm" if mode == "install" else "tool_install_npm_upgrade"
    return {
        "entry_id": entry_id,
        "recipe": "tool_installs",
        "type": op_type,
        "mode": mode,
        "package": args["package"],
        "requires_sudo": item.get("requires_sudo", True),
        "requires_network": True,
        "requires_approval": True,
        "cache_dir": str(cache_dir),
        "reason": f"{mode} {item['label']} via npm",
    }


# ---------------------------------------------------------------------------
# Probes
# ---------------------------------------------------------------------------


def _dpkg_installed(runner: CommandRunner, package: str) -> bool:
    dpkg = runner.which("dpkg-query")
    if not dpkg:
        return False
    try:
        result = runner.run(
            [dpkg, "-W", "-f=${Status}", package],
            capture_output=True,
            check=False,
        )
    except (OSError, RuntimeError):
        return False
    return result.returncode == 0 and "install ok installed" in (result.stdout or "")


def _detect_version(command: str, found_path: str, runner: CommandRunner) -> str:
    try:
        result = runner.run([found_path, "--version"], capture_output=True, check=False)
    except (OSError, RuntimeError):
        return ""
    output = (result.stdout or "").strip().splitlines()
    return output[0] if output else ""


# ---------------------------------------------------------------------------
# Executors
# ---------------------------------------------------------------------------


def _sudo_prefix() -> list[str]:
    if hasattr(os, "geteuid") and os.geteuid() == 0:
        return []
    return ["sudo"]


def _execute_apt(op: dict[str, Any], runner: CommandRunner, *, mode: str) -> int:
    packages = [str(pkg) for pkg in op.get("packages", []) if pkg]
    if not packages:
        return 0
    apt_get = runner.which("apt-get")
    if not apt_get:
        op["result"] = "apt-get not found; install packages manually"
        return 0
    prefix = _sudo_prefix()
    runner.run([*prefix, apt_get, "update"])
    if mode == "upgrade":
        runner.run([*prefix, apt_get, "install", "--only-upgrade", "-y", *packages])
    else:
        runner.run([*prefix, apt_get, "install", "-y", *packages])
    return 1


def _execute_apt_keyring(op: dict[str, Any], runner: CommandRunner, cache_dir: Path) -> int:
    packages = [str(pkg) for pkg in op.get("packages", []) if pkg]
    if not packages:
        return 0
    apt_get = runner.which("apt-get")
    if not apt_get:
        op["result"] = "apt-get not found; install manually"
        return 0
    prefix = _sudo_prefix()
    keyring_path = Path(op["keyring_path"])
    source_path = Path(op["source_path"])

    if not keyring_path.exists():
        cached_keyring = Path(cache_dir) / keyring_path.name
        runner.download(op["keyring_url"], cached_keyring)
        runner.run([*prefix, "install", "-D", "-m", "0644", str(cached_keyring), str(keyring_path)])

    arch = _detect_dpkg_arch(runner)
    rendered_source = op["source_line"].replace("{ARCH}", arch)
    cached_source = Path(cache_dir) / source_path.name
    cached_source.parent.mkdir(parents=True, exist_ok=True)
    cached_source.write_text(rendered_source + "\n")
    runner.run([*prefix, "install", "-D", "-m", "0644", str(cached_source), str(source_path)])

    runner.run([*prefix, apt_get, "update"])
    if op.get("mode") == "upgrade":
        runner.run([*prefix, apt_get, "install", "--only-upgrade", "-y", *packages])
    else:
        runner.run([*prefix, apt_get, "install", "-y", *packages])
    return 1


def _execute_curl(op: dict[str, Any], runner: CommandRunner, cache_dir: Path) -> int:
    sh = runner.which("sh") or "/bin/sh"
    script = Path(cache_dir) / op["script_name"]
    runner.download(op["url"], script)
    if script.exists():
        script.chmod(0o755)
    prefix = _sudo_prefix() if op.get("requires_sudo") else []
    runner.run([*prefix, sh, str(script)])
    return 1


def _execute_npm(op: dict[str, Any], runner: CommandRunner, *, mode: str) -> int:
    package = op.get("package")
    if not package:
        return 0
    npm = runner.which("npm")
    if not npm:
        op["result"] = "npm not found; install Node first or re-run option 5 after dev-base completes"
        return 0
    prefix = _sudo_prefix() if op.get("requires_sudo", True) else []
    if mode == "upgrade":
        runner.run([*prefix, npm, "update", "-g", package])
    else:
        runner.run([*prefix, npm, "install", "-g", package])
    return 1


def _detect_dpkg_arch(runner: CommandRunner) -> str:
    dpkg = runner.which("dpkg")
    if not dpkg:
        return "amd64"
    try:
        result = runner.run([dpkg, "--print-architecture"], capture_output=True, check=False)
    except (OSError, RuntimeError):
        return "amd64"
    return (result.stdout or "amd64").strip() or "amd64"
