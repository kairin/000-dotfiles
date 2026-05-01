from __future__ import annotations

from pathlib import Path
from typing import Any

from .manifest import ManifestEntry, ManifestError, load_manifest, resolve_source, resolve_target, validate_included_protected
from .reports import Report, status_from_entries
from .secrets import scan_file
from .templates import expected_text, validate_template


ROOT_SYMLINKS = {
    "CLAUDE.md": "AGENTS.md",
    "GEMINI.md": "AGENTS.md",
    "agents/CLAUDE.md.template": "AGENTS.md.template",
    "agents/GEMINI.md.template": "AGENTS.md.template",
}


def check_symlinks(repo: Path) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for rel_path, expected in ROOT_SYMLINKS.items():
        path = repo / rel_path
        state = "current"
        reason = "symlink is intact"
        if not path.is_symlink():
            state = "invalid"
            reason = "expected symlink"
        else:
            actual = str(path.readlink())
            if actual != expected:
                state = "invalid"
                reason = f"expected {expected}, found {actual}"
            elif not (path.parent / path.readlink()).exists():
                state = "invalid"
                reason = "symlink target is missing"
        entries.append({
            "entry_id": f"symlink.{rel_path}",
            "source": rel_path,
            "target": rel_path,
            "state": state,
            "protected": True,
            "reason": reason,
        })
    return entries


def evaluate_entry(repo: Path, home: Path, entry: ManifestEntry, include_protected: set[str] | None = None) -> dict[str, Any]:
    include_protected = include_protected or set()
    source_path = resolve_source(repo, entry)
    target_path = resolve_target(repo, home, entry)
    result = _base_result(entry, source_path, target_path)

    source_error = _source_error(source_path, entry)
    if source_error:
        return _state(result, "invalid", source_error)

    if entry.protected and entry.id not in include_protected:
        return _state(result, "protected", entry.manual_reason or "protected/manual entry")

    if target_path.exists() and target_path.is_dir() and entry.kind != "symlink":
        return _state(result, "blocked", "target is a directory")

    if entry.kind == "symlink":
        return _symlink_target_state(result, target_path, entry.link_target or "")

    if not target_path.exists():
        return _state(result, "missing", "target is missing")

    try:
        source_text = expected_text(source_path, entry)
        target_text = target_path.read_text()
    except OSError as exc:
        return _state(result, "blocked", str(exc))
    if target_text == source_text:
        return _state(result, "current", "target matches source")
    return _state(result, "drifted", "target differs from source")


def _base_result(entry: ManifestEntry, source_path: Path, target_path: Path) -> dict[str, Any]:
    result = {
        "entry_id": entry.id,
        "source": str(source_path),
        "target": str(target_path),
        "state": "missing",
        "protected": entry.protected,
        "reason": "",
    }
    if entry.manual_reason:
        result["manual_reason"] = entry.manual_reason
    return result


def _source_error(source_path: Path, entry: ManifestEntry) -> str | None:
    if not source_path.exists() and not source_path.is_symlink():
        return "source path is missing"
    if entry.kind == "symlink":
        if not source_path.is_symlink():
            return "source is not a symlink"
        if entry.link_target and str(source_path.readlink()) != entry.link_target:
            return f"source symlink must point to {entry.link_target}"
        return None
    template_errors = validate_template(source_path, entry)
    secret_errors = [f"secret-like {finding.kind} on line {finding.line}" for finding in scan_file(source_path)]
    errors = template_errors + secret_errors
    return "; ".join(errors) if errors else None


def _symlink_target_state(result: dict[str, Any], target_path: Path, expected: str) -> dict[str, Any]:
    if not target_path.exists() and not target_path.is_symlink():
        return _state(result, "missing", "target symlink is missing")
    if not target_path.is_symlink():
        return _state(result, "drifted", "target is not a symlink")
    if str(target_path.readlink()) == expected:
        return _state(result, "current", "target symlink matches")
    return _state(result, "drifted", "target symlink differs")


def _state(result: dict[str, Any], state: str, reason: str) -> dict[str, Any]:
    result["state"] = state
    result["reason"] = reason
    return result


def run_doctor(repo: Path | str, home: Path | str, *, profile: str = "machine", include_protected: list[str] | None = None) -> Report:
    repo_path = Path(repo).resolve()
    home_path = Path(home).resolve()
    entries: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    try:
        manifest = load_manifest(repo_path)
        include_set = validate_included_protected(manifest, include_protected)
        entries.extend(check_symlinks(repo_path))
        entries.extend(evaluate_entry(repo_path, home_path, entry, include_set) for entry in manifest.entries_for_profile(profile))
    except ManifestError as exc:
        errors.append({"message": str(exc)})
    status = status_from_entries(entries, errors)
    return Report(
        command="doctor",
        status=status,
        repo=str(repo_path),
        home=str(home_path),
        profile=profile,
        entries=entries,
        errors=errors,
    )
