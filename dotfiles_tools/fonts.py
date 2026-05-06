from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import zipfile
from typing import Any, Mapping

from .font_context import (
    apt_items_for_platform as _apt_items_for_platform,
    detect_context as _detect_context,
    host_action as _host_action,
    nerd_items_for_platform as _nerd_items_for_platform,
    terminal_impact as _terminal_impact,
)
from .font_assets import pixel_avf_prompt_text, ttyd_html, ttyd_service
from .font_catalog import (
    APT_FONT_CATALOG,
    EXPECTED_TTF,
    FONT_ARCHIVE_NAME,
    FONT_ASSET_NAME,
    FONT_CACHE_REL,
    FONT_ENTRY_ID,
    FONT_EXTRACTED_DIR,
    FONT_FACE,
    FONT_INSTALL_REL,
    FONT_MARKER_NAME,
    FONT_LABEL,
    FONT_VERSION_NAME,
    NERD_FONTS_RELEASE_URL,
    NERD_FONT_CATALOG,
    NerdFontItem,
    PIXEL_AVF_ENTRY_ID,
    PIXEL_AVF_PROMPT_REL,
    PIXEL_TTYD_FONT_ALIAS,
    FontError,
)
from .font_pixel import pixel_ttyd_plan as _pixel_ttyd_plan
from .font_records import (
    apt_font_summary as _apt_font_summary,
    build_unsupported_plan as _build_unsupported_plan,
    font_entry as _font_entry,
    installed_font_files as _installed_font_files,
    nerd_font_summary as _nerd_font_summary,
    nerd_paths as _nerd_paths,
    read_version as _read_version,
    select_nerd_font_asset as _select_nerd_font_asset,
    unsupported_nerd_summary as _unsupported_nerd_summary,
)
from .font_runner import CommandRunner
from .font_windows import (
    execute_install_windows as _execute_install_windows,
    execute_update_windows_terminal as _execute_update_windows_terminal,
    windows_host_plan as _windows_host_plan,
)

__all__ = (
    "APT_FONT_CATALOG",
    "CommandRunner",
    "EXPECTED_TTF",
    "FONT_ARCHIVE_NAME",
    "FONT_ASSET_NAME",
    "FONT_EXTRACTED_DIR",
    "FONT_FACE",
    "FONT_INSTALL_REL",
    "FONT_LABEL",
    "FONT_VERSION_NAME",
    "FontError",
    "NERD_FONT_CATALOG",
    "NerdFontItem",
    "build_font_plan",
    "execute_font_operation",
    "select_nerd_font_asset",
)


def select_nerd_font_asset(release: Mapping[str, Any], asset_name: str = FONT_ASSET_NAME) -> dict[str, Any]:
    return _select_nerd_font_asset(release, asset_name)


def build_font_plan(
    home: Path | str,
    *,
    env: Mapping[str, str] | None = None,
    path: str | None = None,
    runner: CommandRunner | None = None,
) -> dict[str, Any]:
    home_path, effective_env, effective_runner, context, fetch_release = _font_plan_inputs(home, env, path, runner)
    if context["platform"] == "unsupported":
        return _build_unsupported_plan(home_path, context)
    if context["platform"] == "pixel-avf":
        return _build_pixel_avf_plan(home_path, context)
    return _build_supported_font_plan(home_path, effective_env, effective_runner, context, fetch_release)


def _font_plan_inputs(
    home: Path | str,
    env: Mapping[str, str] | None,
    path: str | None,
    runner: CommandRunner | None,
) -> tuple[Path, dict[str, str], CommandRunner, dict[str, Any], bool]:
    home_path = Path(home).expanduser().resolve()
    effective_env = dict(os.environ if env is None else env)
    effective_path = path if path is not None else effective_env.get("PATH", "")
    runner_was_provided = runner is not None
    effective_runner = runner or CommandRunner(env=effective_env, path=effective_path)
    context = _detect_context(home_path, effective_env, effective_path, effective_runner)
    return home_path, effective_env, effective_runner, context, runner_was_provided


def _build_supported_font_plan(
    home: Path,
    env: Mapping[str, str],
    runner: CommandRunner,
    context: dict[str, Any],
    fetch_release: bool,
) -> dict[str, Any]:
    release = _release_metadata(home, env, runner, fetch=fetch_release)
    entries: list[dict[str, Any]] = []
    operations: list[dict[str, Any]] = []
    fonts: list[dict[str, Any]] = []
    _extend_nerd_font_plan(home, context, release, entries, operations, fonts)
    _extend_apt_font_plan(context, runner, entries, operations, fonts)
    _extend_platform_font_plan(home, context, entries, operations, fonts)
    return {"entries": entries, "operations": operations, "fonts": fonts, "context": context}


def _extend_nerd_font_plan(
    home: Path,
    context: dict[str, Any],
    release: Mapping[str, Any],
    entries: list[dict[str, Any]],
    operations: list[dict[str, Any]],
    fonts: list[dict[str, Any]],
) -> None:
    for item in _nerd_items_for_platform(context["platform"]):
        summary = _nerd_font_summary(home, context, item, release)
        entries.append(_font_entry(summary))
        fonts.append(summary)
        if summary["state"] in {"missing", "needs_update"}:
            operations.extend(_nerd_font_operations(home, item, reason=summary["reason"]))


def _extend_apt_font_plan(
    context: dict[str, Any],
    runner: CommandRunner,
    entries: list[dict[str, Any]],
    operations: list[dict[str, Any]],
    fonts: list[dict[str, Any]],
) -> None:
    for item in _apt_items_for_platform(context["platform"]):
        summary = _apt_font_summary(context, item, runner)
        entries.append(_font_entry(summary))
        fonts.append(summary)
        if summary["state"] in {"missing", "needs_update"}:
            operations.append(_apt_package_operation(summary))


def _extend_platform_font_plan(
    home: Path,
    context: dict[str, Any],
    entries: list[dict[str, Any]],
    operations: list[dict[str, Any]],
    fonts: list[dict[str, Any]],
) -> None:
    if context["platform"] == "wsl":
        _extend_wsl_host_plan(home, context, entries, operations, fonts)
    if context["platform"] == "pixel-terminal":
        _extend_pixel_terminal_plan(home, context, entries, operations, fonts)


def _jetbrains_font_summary(fonts: list[dict[str, Any]]) -> dict[str, Any]:
    return next(item for item in fonts if item["entry_id"] == FONT_ENTRY_ID)


def _extend_wsl_host_plan(
    home: Path,
    context: dict[str, Any],
    entries: list[dict[str, Any]],
    operations: list[dict[str, Any]],
    fonts: list[dict[str, Any]],
) -> None:
    jetbrains = next(item for item in NERD_FONT_CATALOG if item.entry_id == FONT_ENTRY_ID)
    jetbrains_summary = _jetbrains_font_summary(fonts)
    windows_entry, windows_ops, windows_summary = _windows_host_plan(home, context, jetbrains, jetbrains_summary)
    entries.append(windows_entry)
    operations.extend(windows_ops)
    jetbrains_summary["host_action"] = windows_summary["host_action"]


def _extend_pixel_terminal_plan(
    home: Path,
    context: dict[str, Any],
    entries: list[dict[str, Any]],
    operations: list[dict[str, Any]],
    fonts: list[dict[str, Any]],
) -> None:
    jetbrains_summary = _jetbrains_font_summary(fonts)
    pixel_entry, pixel_ops, pixel_summary = _pixel_ttyd_plan(home, context, jetbrains_summary)
    entries.append(pixel_entry)
    operations.extend(pixel_ops)
    jetbrains_summary["host_action"] = pixel_summary["host_action"]
    jetbrains_summary["requires_sudo"] = True
    jetbrains_summary["terminal_impact"] = pixel_summary["terminal_impact"]
    jetbrains_summary["embedded_alias"] = PIXEL_TTYD_FONT_ALIAS


def execute_font_operation(
    op: dict[str, Any],
    *,
    runner: CommandRunner | None = None,
    backup_dir: Path | None = None,
    backups: list[dict[str, Any]] | None = None,
) -> int:
    effective_runner = runner or CommandRunner()
    backup_path = backup_dir or Path.home() / ".dotfiles-backups"
    backup_records = backups if backups is not None else []
    op_type = op["type"]
    executor = _font_operation_handlers(effective_runner, backup_path, backup_records).get(op_type)
    if executor:
        return executor(op)
    raise FontError(f"unknown font operation: {op_type}")


def _font_operation_handlers(
    runner: CommandRunner,
    backup_path: Path,
    backups: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "font_skip": lambda op: 0,
        "font_manual": lambda op: 0,
        "font_download": lambda op: _execute_download(op, runner),
        "font_extract": _execute_extract,
        "font_install_linux": _execute_install_linux,
        "font_rebuild_cache": lambda op: _execute_rebuild_cache(op, runner),
        "font_verify_linux": lambda op: _execute_verify_linux(op, runner),
        "font_install_packages": lambda op: _execute_install_packages(op, runner),
        "font_install_windows": lambda op: _execute_install_windows(op, runner),
        "font_update_windows_terminal": lambda op: _execute_update_windows_terminal(op, backup_path, backups),
        "font_ttyd_write_html": lambda op: _execute_ttyd_html(op, runner, backups),
        "font_ttyd_write_service": lambda op: _execute_ttyd_service(op, runner, backups),
        "font_systemd_daemon_reload": lambda op: _execute_systemd(op, runner, "daemon-reload"),
        "font_systemd_restart": lambda op: _execute_systemd(op, runner, "restart", "ttyd.service"),
        "font_pixel_avf_prompt": _execute_pixel_avf_prompt,
    }


def _execute_systemd(op: dict[str, Any], runner: CommandRunner, *args: str) -> int:
    # State-change command (no file write). Returns 1 because callers track this
    # for partial-apply accounting; if a later op fails, we want to know systemd
    # state has already been mutated.
    runner.run(["sudo", "systemctl", *args])
    return 1


_RELEASE_FETCH_ERRORS: tuple[type[BaseException], ...] = (OSError, json.JSONDecodeError, UnicodeDecodeError)


def _classify_release_lookup_error(exc: BaseException) -> str:
    import socket
    import urllib.error

    if isinstance(exc, urllib.error.HTTPError):
        return "http"
    if isinstance(exc, urllib.error.URLError):
        return "network"
    if isinstance(exc, (TimeoutError, socket.timeout)):
        return "timeout"
    if isinstance(exc, (json.JSONDecodeError, UnicodeDecodeError)):
        return "decode"
    if isinstance(exc, FileNotFoundError):
        return "offline"
    return "network"


def _release_metadata(home: Path, env: Mapping[str, str], runner: CommandRunner, *, fetch: bool) -> dict[str, Any]:
    cache_path = home / FONT_CACHE_REL / "nerd-fonts.latest.json"
    if _truthy(env.get("DOTFILES_FONT_OFFLINE")):
        return _read_version(cache_path)
    if fetch or _truthy(env.get("DOTFILES_FONT_CHECK_LATEST")):
        try:
            release = runner.fetch_json(NERD_FONTS_RELEASE_URL)
        except _RELEASE_FETCH_ERRORS as exc:
            cached = _read_version(cache_path)
            if not cached:
                raise FontError(
                    f"nerd-fonts release lookup failed and no cache exists at {cache_path}: {exc}"
                ) from exc
            cached["lookup_error"] = str(exc)
            cached["lookup_error_kind"] = _classify_release_lookup_error(exc)
            return cached
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(json.dumps(release, indent=2, sort_keys=True) + "\n")
        return release
    return _read_version(cache_path)


def _truthy(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def _nerd_font_operations(home: Path, item: NerdFontItem, *, reason: str) -> list[dict[str, Any]]:
    paths = _nerd_paths(home, item)
    base = {
        "entry_id": item.entry_id,
        "family": item.family,
        "requires_approval": True,
        "recipe": "fonts",
    }
    return [
        {
            **base,
            "type": "font_download",
            "source": NERD_FONTS_RELEASE_URL,
            "target": str(paths["archive"]),
            "asset_name": item.asset_name,
            "reason": f"download latest {item.asset_name} or reuse cached archive",
            "requires_network": True,
        },
        {
            **base,
            "type": "font_extract",
            "source": str(paths["archive"]),
            "target": str(paths["extract_dir"]),
            "asset_name": item.asset_name,
            "terminal_face": item.terminal_face,
            "reason": f"extract {item.label} font files",
        },
        {
            **base,
            "type": "font_install_linux",
            "source": str(paths["extract_dir"]),
            "target": str(paths["install_dir"]),
            "version_source": str(paths["version"]),
            "reason": reason,
        },
        {
            **base,
            "type": "font_rebuild_cache",
            "target": str(paths["install_dir"]),
            "reason": "run fc-cache for the user-local font directory when available",
        },
        {
            **base,
            "type": "font_verify_linux",
            "target": str(paths["install_dir"]),
            "terminal_face": item.terminal_face,
            "reason": f"verify {item.terminal_face} through fontconfig when available",
        },
    ]


def _apt_package_operation(summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "entry_id": summary["entry_id"],
        "type": "font_install_packages",
        "source": "apt",
        "source_type": "apt_package",
        "target": summary["target"],
        "packages": [summary["package"]],
        "candidate_version": summary.get("candidate_version"),
        "reason": summary["reason"],
        "requires_approval": True,
        "requires_sudo": True,
        "recipe": "fonts",
    }


def _build_pixel_avf_plan(home: Path, context: dict[str, Any]) -> dict[str, Any]:
    prompt_path = home / PIXEL_AVF_PROMPT_REL
    desired = pixel_avf_prompt_text()
    prompt_state = "installed" if prompt_path.exists() and prompt_path.read_text(errors="ignore") == desired else "missing"
    fonts = [_unsupported_nerd_summary(home, context, item, "Pixel AVF weston-terminal ignores Nerd Font configuration") for item in NERD_FONT_CATALOG]
    entries = [_font_entry(summary) for summary in fonts]
    entries.append({
        "entry_id": PIXEL_AVF_ENTRY_ID,
        "source": "generated fish prompt fallback",
        "source_type": "pixel_avf_prompt",
        "family": "fish prompt",
        "target": str(prompt_path),
        "state": prompt_state,
        "protected": False,
        "reason": "plain ASCII prompt fallback for Pixel AVF weston-terminal",
        "recipe": "fonts",
        "requires_sudo": False,
        "terminal_face": None,
        "terminal_impact": _terminal_impact("pixel-avf"),
        "host_action": _host_action(context),
    })
    operations: list[dict[str, Any]] = []
    if prompt_state != "installed":
        operations.append({
            "entry_id": PIXEL_AVF_ENTRY_ID,
            "type": "font_pixel_avf_prompt",
            "source": "generated fish prompt fallback",
            "target": str(prompt_path),
            "reason": "write plain prompt fallback without Nerd Font glyph dependencies",
            "requires_approval": True,
            "recipe": "fonts",
        })
    return {"entries": entries, "operations": operations, "fonts": fonts, "context": context}


def _execute_download(op: dict[str, Any], runner: CommandRunner) -> int:
    archive = Path(op["target"])
    version_path = archive.parent / f"{Path(op.get('asset_name') or archive.name).stem}.version.json"
    archive.parent.mkdir(parents=True, exist_ok=True)
    try:
        release = runner.fetch_json(NERD_FONTS_RELEASE_URL)
        asset = select_nerd_font_asset(release, str(op.get("asset_name") or FONT_ASSET_NAME))
    except Exception as exc:
        if archive.exists():
            op["result"] = f"reused cached archive after release lookup failed: {exc}"
            return 0
        raise FontError(f"font download blocked and no cached archive exists: {exc}") from exc

    current = _read_version(version_path)
    if archive.exists() and current.get("tag_name") == asset.get("tag_name"):
        op["result"] = f"cached {asset.get('tag_name')} reused"
        return 0
    runner.download(asset["browser_download_url"], archive)
    version_path.write_text(json.dumps(asset, indent=2, sort_keys=True) + "\n")
    op["result"] = f"downloaded {asset.get('tag_name')}"
    return 1


def _execute_extract(op: dict[str, Any]) -> int:
    archive = Path(op["source"])
    extract_dir = Path(op["target"])
    if not archive.exists():
        raise FontError(f"font archive is missing: {archive}")
    if extract_dir.exists():
        shutil.rmtree(extract_dir)
    extract_dir.mkdir(parents=True, exist_ok=True)
    extracted: list[Path] = []
    with zipfile.ZipFile(archive) as bundle:
        for info in bundle.infolist():
            name = Path(info.filename).name
            if not name or Path(name).suffix.lower() not in {".ttf", ".otf"}:
                continue
            target = extract_dir / name
            target.write_bytes(bundle.read(info))
            extracted.append(target)
    if not extracted:
        raise FontError(f"no font files found in {archive}")
    return 1


def _execute_install_linux(op: dict[str, Any]) -> int:
    source = Path(op["source"])
    target = Path(op["target"])
    fonts = _installed_font_files(source)
    if not fonts:
        raise FontError(f"no extracted font files found in {source}")
    version = _read_version(Path(op.get("version_source", "")))
    marker_path = target / FONT_MARKER_NAME
    if version and _read_version(marker_path) == version and all((target / font.name).exists() for font in fonts):
        op["result"] = f"already installed at {version.get('tag_name', 'cached version')}"
        return 0
    target.mkdir(parents=True, exist_ok=True)
    for font in fonts:
        shutil.copy2(font, target / font.name)
    if version:
        marker_path.write_text(json.dumps(version, indent=2, sort_keys=True) + "\n")
    return 1


def _execute_rebuild_cache(op: dict[str, Any], runner: CommandRunner) -> int:
    fc_cache = runner.which("fc-cache")
    if not fc_cache:
        op["result"] = "fc-cache not found; font files installed but cache refresh is manual"
        return 0
    runner.run([fc_cache, "-f", op["target"]])
    return 1


def _execute_verify_linux(op: dict[str, Any], runner: CommandRunner) -> int:
    terminal_face = str(op.get("terminal_face") or "")
    _validate_mono_face(terminal_face)
    fc_match = runner.which("fc-match")
    if not fc_match:
        op["result"] = "fc-match not found; verify manually"
        return 0
    result = runner.run([fc_match, terminal_face], capture_output=True)
    _validate_fc_match_output(op, terminal_face, result.stdout or "")
    return 0


def _validate_mono_face(terminal_face: str) -> None:
    if "Propo" in terminal_face or "Mono" not in terminal_face:
        raise FontError(f"refusing terminal font face that is not Mono-safe: {terminal_face}")


def _validate_fc_match_output(op: dict[str, Any], terminal_face: str, stdout: str) -> None:
    if "Propo" in stdout:
        raise FontError(f"fontconfig resolved {terminal_face} to a Propo face: {stdout.strip()}")
    if "Mono" not in stdout:
        raise FontError(f"fontconfig did not resolve {terminal_face} to a Mono face: {stdout.strip()}")
    family = str(op.get("family") or terminal_face.split()[0])
    if _normalize(family) not in _normalize(stdout):
        raise FontError(f"fontconfig did not resolve {terminal_face}: {stdout.strip()}")


def _normalize(text: str) -> str:
    return "".join(char.lower() for char in text if char.isalnum())


def _execute_install_packages(op: dict[str, Any], runner: CommandRunner) -> int:
    packages = [str(package) for package in op.get("packages", []) if package]
    if not packages:
        return 0
    apt_get = runner.which("apt-get")
    if not apt_get:
        op["result"] = "apt-get not found; install fallback packages manually"
        return 0
    prefix = [] if hasattr(os, "geteuid") and os.geteuid() == 0 else ["sudo"]
    runner.run([*prefix, apt_get, "update"])
    runner.run([*prefix, apt_get, "install", "-y", *packages])
    return 1


# ttyd_html, ttyd_service: targets are root-owned (/etc/...) so we cannot read
# them to compare against generated content without invoking sudo (which itself
# has side effects). Returning 1 honestly: every call to these handlers performs
# a sudo install and a backup. Callers that want idempotence should gate at the
# plan level, not here.
def _execute_ttyd_html(op: dict[str, Any], runner: CommandRunner, backups: list[dict[str, Any]]) -> int:
    source_dir = Path(op["source"])
    font = _regular_mono_font(source_dir)
    html = ttyd_html(font)
    generated = Path(op["cache_dir"]) / "ttyd-index.html"
    generated.parent.mkdir(parents=True, exist_ok=True)
    generated.write_text(html)
    _sudo_backup_and_install(op["target"], generated, runner, backups, op["entry_id"])
    return 1


def _execute_ttyd_service(op: dict[str, Any], runner: CommandRunner, backups: list[dict[str, Any]]) -> int:
    generated = Path(op["cache_dir"]) / "ttyd.service"
    generated.parent.mkdir(parents=True, exist_ok=True)
    generated.write_text(ttyd_service())
    _sudo_backup_and_install(op["target"], generated, runner, backups, op["entry_id"])
    return 1


def _sudo_backup_and_install(target: str, generated: Path, runner: CommandRunner, backups: list[dict[str, Any]], entry_id: str) -> None:
    backup_target = f"{target}.000-dotfiles-backup"
    runner.run(["sudo", "sh", "-c", "if [ -e \"$1\" ]; then cp -a \"$1\" \"$2\"; fi", "sh", target, backup_target])
    backups.append({"entry_id": entry_id, "target": target, "backup_target": backup_target})
    runner.run(["sudo", "install", "-Dm0644", str(generated), target])


def _regular_mono_font(source_dir: Path) -> Path:
    exact = source_dir / EXPECTED_TTF
    if exact.exists():
        return exact
    fonts = _installed_font_files(source_dir)
    regular = _first_mono_font(fonts, require_regular=True)
    mono = _first_mono_font(fonts, require_regular=False)
    if regular or mono:
        return regular or mono
    raise FontError(f"no JetBrainsMono Nerd Font Mono file found in {source_dir}")


def _first_mono_font(fonts: list[Path], *, require_regular: bool) -> Path | None:
    for path in fonts:
        if "Mono" in path.name and (not require_regular or "Regular" in path.name):
            return path
    return None


def _execute_pixel_avf_prompt(op: dict[str, Any]) -> int:
    target = Path(op["target"])
    desired = pixel_avf_prompt_text()
    try:
        if target.read_text() == desired:
            op["result"] = "prompt fallback already current"
            return 0
    except OSError:
        pass
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(desired)
    return 1
