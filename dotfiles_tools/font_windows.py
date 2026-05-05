from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .backups import create_backup
from .font_assets import windows_font_install_script
from .font_catalog import FONT_CACHE_REL, FONT_FACE, FONT_INSTALL_BASE_REL, WINDOWS_ENTRY_ID, FontError, NerdFontItem
from .font_context import check_windows_fonts_installed, host_action, terminal_impact
from .font_runner import CommandRunner


def windows_host_plan(
    home: Path,
    context: dict[str, Any],
    item: NerdFontItem,
    font_summary: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any]]:
    powershell = context.get("powershell")
    if not powershell:
        state = "manual"
        reason = "powershell.exe is not visible from WSL"
    else:
        source_dir = nerd_paths(home, item)["install_dir"]
        if check_windows_fonts_installed(source_dir):
            state = "installed"
            reason = f"{item.terminal_face} files are present in Windows per-user font store"
        else:
            state = "missing"
            reason = "powershell.exe is available for Windows per-user font install"
    operations = windows_host_operations(home, context, item, font_summary, state)
    return windows_host_entry(home, context, item, state, reason), operations, {"host_action": host_action(context), "requires_sudo": False}


def windows_host_entry(
    home: Path,
    context: dict[str, Any],
    item: NerdFontItem,
    state: str,
    reason: str,
) -> dict[str, Any]:
    return {
        "entry_id": WINDOWS_ENTRY_ID,
        "source": str(nerd_paths(home, item)["install_dir"]),
        "source_type": "windows_host",
        "family": item.family,
        "target": "Windows per-user font store",
        "state": state,
        "protected": False,
        "reason": reason,
        "recipe": "fonts",
        "requires_sudo": False,
        "terminal_face": item.terminal_face,
        "terminal_impact": terminal_impact("wsl"),
        "host_action": host_action(context),
    }


def windows_host_operations(
    home: Path,
    context: dict[str, Any],
    item: NerdFontItem,
    font_summary: dict[str, Any],
    state: str = "missing",
) -> list[dict[str, Any]]:
    if not context.get("powershell"):
        return [manual_op(WINDOWS_ENTRY_ID, f"Install {item.terminal_face} on the Windows host manually.")]
    if state == "installed":
        return [_windows_skip_op(WINDOWS_ENTRY_ID, f"{item.terminal_face} already installed in Windows per-user font store")]
    operations = [windows_font_install_operation(home, item, font_summary)]
    settings = context.get("windows_terminal_settings")
    if settings:
        operations.append(windows_terminal_update_operation(item, settings))
    else:
        operations.append(manual_op(WINDOWS_ENTRY_ID, f"Set Windows Terminal font face to {item.terminal_face} manually."))
    return operations


def windows_font_install_operation(home: Path, item: NerdFontItem, font_summary: dict[str, Any]) -> dict[str, Any]:
    source_dir = nerd_paths(home, item)["install_dir"] if font_summary["state"] == "installed" else nerd_paths(home, item)["extract_dir"]
    return {
        "entry_id": WINDOWS_ENTRY_ID,
        "type": "font_install_windows",
        "source": str(source_dir),
        "target": "Windows per-user font store",
        "terminal_face": item.terminal_face,
        "reason": "install JetBrainsMono Nerd Font Mono into the Windows user font store through PowerShell",
        "requires_approval": True,
        "recipe": "fonts",
    }


def windows_terminal_update_operation(item: NerdFontItem, settings: str) -> dict[str, Any]:
    return {
        "entry_id": WINDOWS_ENTRY_ID,
        "type": "font_update_windows_terminal",
        "source": item.terminal_face,
        "target": settings,
        "reason": "set Windows Terminal profile defaults font.face",
        "requires_approval": True,
        "recipe": "fonts",
    }


def nerd_paths(home: Path, item: NerdFontItem) -> dict[str, Path]:
    cache_dir = home / FONT_CACHE_REL
    return {
        "cache_dir": cache_dir,
        "archive": cache_dir / item.asset_name,
        "version": cache_dir / f"{item.cache_stem}.version.json",
        "extract_dir": cache_dir / item.cache_stem,
        "install_dir": home / FONT_INSTALL_BASE_REL / item.install_dir_name,
    }


def _windows_skip_op(entry_id: str, reason: str) -> dict[str, Any]:
    return {
        "entry_id": entry_id,
        "type": "font_skip",
        "target": "Windows per-user font store",
        "reason": reason,
        "requires_approval": False,
        "recipe": "fonts",
    }


def manual_op(entry_id: str, reason: str) -> dict[str, Any]:
    return {
        "entry_id": entry_id,
        "type": "font_manual",
        "target": "",
        "reason": reason,
        "requires_approval": False,
        "recipe": "fonts",
    }


def execute_install_windows(op: dict[str, Any], runner: CommandRunner) -> int:
    powershell = runner.which("powershell.exe")
    if not powershell:
        op["result"] = "powershell.exe not found; install Windows host font manually"
        return 0
    source = Path(op["source"])
    if not source.exists():
        raise FontError(f"Windows font source directory is missing: {source}")
    windows_source = str(source)
    wslpath = runner.which("wslpath")
    if wslpath:
        converted = runner.run([wslpath, "-w", str(source)], capture_output=True)
        windows_source = converted.stdout.strip()
    script = windows_font_install_script(windows_source)
    runner.run([powershell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script])
    return 1


def execute_update_windows_terminal(op: dict[str, Any], backup_dir: Path, backups: list[dict[str, Any]]) -> int:
    target = Path(op["target"])
    if not target.exists():
        op["result"] = "Windows Terminal settings file was not found; set font face manually"
        return 0
    record = create_backup(target, backup_dir, entry_id=op["entry_id"])
    backups.append(record)
    try:
        data = json.loads(target.read_text())
    except json.JSONDecodeError as exc:
        raise FontError(f"invalid Windows Terminal settings JSON: {target}") from exc
    font = terminal_settings_font(data)
    font["face"] = FONT_FACE
    target.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    op["backup_target"] = record["backup_target"]
    return 1


def terminal_settings_font(data: dict[str, Any]) -> dict[str, Any]:
    profiles = data.setdefault("profiles", {})
    if not isinstance(profiles, dict):
        profiles = {}
        data["profiles"] = profiles
    defaults = profiles.setdefault("defaults", {})
    if not isinstance(defaults, dict):
        defaults = {}
        profiles["defaults"] = defaults
    font = defaults.setdefault("font", {})
    if not isinstance(font, dict):
        font = {}
        defaults["font"] = font
    return font
