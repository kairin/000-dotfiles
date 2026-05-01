from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from .font_catalog import (
    APT_FONT_CATALOG,
    FONT_CACHE_REL,
    FONT_ENTRY_ID,
    FONT_INSTALL_BASE_REL,
    FONT_MARKER_NAME,
    NERD_FONTS_REPO,
    NERD_FONT_CATALOG,
    FontError,
    NerdFontItem,
)
from .font_context import host_action, terminal_impact
from .font_runner import CommandRunner


def select_nerd_font_asset(release: Mapping[str, Any], asset_name: str) -> dict[str, Any]:
    for asset in release.get("assets") or []:
        if asset.get("name") == asset_name and asset.get("browser_download_url"):
            return {
                "name": asset["name"],
                "browser_download_url": asset["browser_download_url"],
                "size": asset.get("size"),
                "tag_name": release.get("tag_name") or release.get("name") or "latest",
            }
    raise FontError(f"{asset_name} not found in latest {NERD_FONTS_REPO} release")


def nerd_paths(home: Path, item: NerdFontItem) -> dict[str, Path]:
    cache_dir = home / FONT_CACHE_REL
    return {
        "cache_dir": cache_dir,
        "archive": cache_dir / item.asset_name,
        "version": cache_dir / f"{item.cache_stem}.version.json",
        "extract_dir": cache_dir / item.cache_stem,
        "install_dir": home / FONT_INSTALL_BASE_REL / item.install_dir_name,
    }


def nerd_font_summary(home: Path, context: dict[str, Any], item: NerdFontItem, release: Mapping[str, Any]) -> dict[str, Any]:
    paths = nerd_paths(home, item)
    installed_files = installed_font_files(paths["install_dir"])
    installed_version = read_version(paths["install_dir"] / FONT_MARKER_NAME)
    cached_version = read_version(paths["version"])
    latest_version = release_tag_for_asset(release, item.asset_name) or cached_version.get("tag_name")
    installed_tag = installed_version.get("tag_name") if installed_version else None
    cached_tag = cached_version.get("tag_name") if cached_version else None
    state, reason = nerd_font_state(item, installed_files, installed_tag, latest_version, cached_tag)
    return nerd_font_summary_record(context, item, paths, state, reason, installed_tag, latest_version, cached_tag)


def nerd_font_state(
    item: NerdFontItem,
    installed_files: list[Path],
    installed_tag: str | None,
    latest_version: str | None,
    cached_tag: str | None,
) -> tuple[str, str]:
    if not installed_files:
        return "missing", f"{item.label} is not installed in the user font directory"
    update_reason = nerd_font_update_reason(installed_tag, latest_version, cached_tag)
    if update_reason:
        return "needs_update", update_reason
    return "installed", f"user-local {item.label} files are present"


def nerd_font_update_reason(
    installed_tag: str | None,
    latest_version: str | None,
    cached_tag: str | None,
) -> str | None:
    if latest_version and installed_tag and installed_tag != latest_version:
        return f"installed {installed_tag} but latest is {latest_version}"
    if not latest_version and cached_tag and installed_tag and installed_tag != cached_tag:
        return f"installed {installed_tag} but cached archive is {cached_tag}"
    return None


def nerd_font_summary_record(
    context: dict[str, Any],
    item: NerdFontItem,
    paths: dict[str, Path],
    state: str,
    reason: str,
    installed_tag: str | None,
    latest_version: str | None,
    cached_tag: str | None,
) -> dict[str, Any]:
    return {
        "entry_id": item.entry_id,
        "label": item.label,
        "family": item.family,
        "source_type": "nerd_font_release",
        "source": f"GitHub latest release asset {NERD_FONTS_REPO}/{item.asset_name}",
        "asset_name": item.asset_name,
        "state": state,
        "installed_version": installed_tag,
        "latest_version": latest_version,
        "cached_version": cached_tag,
        "candidate_version": None,
        "target": str(paths["install_dir"]),
        "cache_path": str(paths["archive"]),
        "terminal_face": item.terminal_face,
        "platform": context["platform"],
        "requires_sudo": False,
        "terminal_impact": terminal_impact(context["platform"]),
        "host_action": host_action(context),
        "reason": reason,
    }


def release_tag_for_asset(release: Mapping[str, Any], asset_name: str) -> str | None:
    if not release:
        return None
    try:
        select_nerd_font_asset(release, asset_name)
    except FontError:
        return None
    tag = release.get("tag_name") or release.get("name")
    return str(tag) if tag else None


def apt_font_summary(context: dict[str, Any], item: dict[str, str], runner: CommandRunner) -> dict[str, Any]:
    installed_version, installed_reason = apt_installed_version(item["package"], runner)
    candidate_version, candidate_reason = apt_candidate_version(item["package"], runner)
    if installed_reason or candidate_reason:
        state = "manual"
        reason = installed_reason or candidate_reason or "apt metadata unavailable"
    elif not installed_version:
        state = "missing"
        reason = f"{item['package']} is not installed"
    elif candidate_version and installed_version != candidate_version:
        state = "needs_update"
        reason = f"installed {installed_version} but apt candidate is {candidate_version}"
    else:
        state = "installed"
        reason = f"{item['package']} is installed"

    return {
        "entry_id": item["entry_id"],
        "label": item["family"],
        "family": item["family"],
        "source_type": "apt_package",
        "source": "apt",
        "package": item["package"],
        "state": state,
        "installed_version": installed_version,
        "latest_version": None,
        "candidate_version": candidate_version,
        "target": item["package"],
        "cache_path": None,
        "terminal_face": item["terminal_face"],
        "platform": context["platform"],
        "requires_sudo": state in {"missing", "needs_update"},
        "terminal_impact": terminal_impact(context["platform"]),
        "host_action": host_action(context),
        "reason": reason,
    }


def apt_installed_version(package: str, runner: CommandRunner) -> tuple[str | None, str | None]:
    dpkg_query = runner.which("dpkg-query")
    if not dpkg_query:
        return None, "dpkg-query not found; apt package state must be checked manually"
    result = runner.run([dpkg_query, "-W", "-f=${Version}", package], capture_output=True, check=False)
    if result.returncode != 0:
        return None, None
    version = (result.stdout or "").strip()
    return version or None, None


def apt_candidate_version(package: str, runner: CommandRunner) -> tuple[str | None, str | None]:
    apt_cache = runner.which("apt-cache")
    if not apt_cache:
        return None, "apt-cache not found; apt candidate state must be checked manually"
    result = runner.run([apt_cache, "policy", package], capture_output=True, check=False)
    if result.returncode != 0:
        return None, f"apt-cache policy failed for {package}"
    for line in (result.stdout or "").splitlines():
        text = line.strip()
        if text.startswith("Candidate:"):
            candidate = text.split(":", 1)[1].strip()
            return None if candidate == "(none)" else candidate, None
    return None, None


def font_entry(summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "entry_id": summary["entry_id"],
        "source": summary["source"],
        "source_type": summary["source_type"],
        "family": summary["family"],
        "target": summary["target"],
        "state": summary["state"],
        "protected": False,
        "reason": summary["reason"],
        "recipe": "fonts",
        "cache_path": summary.get("cache_path"),
        "terminal_face": summary.get("terminal_face"),
        "requires_sudo": summary["requires_sudo"],
        "terminal_impact": summary["terminal_impact"],
        "host_action": summary["host_action"],
    }


def build_unsupported_plan(home: Path, context: dict[str, Any]) -> dict[str, Any]:
    reason = "automatic font setup is unsupported on this platform"
    fonts = [unsupported_nerd_summary(home, context, item, reason) for item in NERD_FONT_CATALOG]
    fonts.extend(unsupported_apt_summary(context, item, reason) for item in APT_FONT_CATALOG)
    return {
        "entries": [font_entry(summary) for summary in fonts],
        "operations": [manual_op(FONT_ENTRY_ID, "Install terminal fonts manually on this platform.")],
        "fonts": fonts,
        "context": context,
    }


def unsupported_nerd_summary(home: Path, context: dict[str, Any], item: NerdFontItem, reason: str) -> dict[str, Any]:
    paths = nerd_paths(home, item)
    return {
        "entry_id": item.entry_id,
        "label": item.label,
        "family": item.family,
        "source_type": "nerd_font_release",
        "source": f"GitHub latest release asset {NERD_FONTS_REPO}/{item.asset_name}",
        "asset_name": item.asset_name,
        "state": "unsupported",
        "installed_version": None,
        "latest_version": None,
        "cached_version": None,
        "candidate_version": None,
        "target": str(paths["install_dir"]),
        "cache_path": str(paths["archive"]),
        "terminal_face": item.terminal_face,
        "platform": context["platform"],
        "requires_sudo": False,
        "terminal_impact": terminal_impact(context["platform"]),
        "host_action": host_action(context),
        "reason": reason,
    }


def unsupported_apt_summary(context: dict[str, Any], item: dict[str, str], reason: str) -> dict[str, Any]:
    return {
        "entry_id": item["entry_id"],
        "label": item["family"],
        "family": item["family"],
        "source_type": "apt_package",
        "source": "apt",
        "package": item["package"],
        "state": "unsupported",
        "installed_version": None,
        "latest_version": None,
        "candidate_version": None,
        "target": item["package"],
        "cache_path": None,
        "terminal_face": item["terminal_face"],
        "platform": context["platform"],
        "requires_sudo": False,
        "terminal_impact": terminal_impact(context["platform"]),
        "host_action": host_action(context),
        "reason": reason,
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


def installed_ttf_files(install_dir: Path) -> list[Path]:
    return installed_font_files(install_dir)


def installed_font_files(install_dir: Path) -> list[Path]:
    if not install_dir.exists():
        return []
    return sorted(path for path in install_dir.glob("*") if path.suffix.lower() in {".ttf", ".otf"})


def read_version(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return {}
