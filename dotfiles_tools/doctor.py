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

    if not source_path.exists() and not source_path.is_symlink():
        result["state"] = "invalid"
        result["reason"] = "source path is missing"
        return result

    if entry.kind == "symlink":
        if not source_path.is_symlink():
            result["state"] = "invalid"
            result["reason"] = "source is not a symlink"
            return result
        if entry.link_target and str(source_path.readlink()) != entry.link_target:
            result["state"] = "invalid"
            result["reason"] = f"source symlink must point to {entry.link_target}"
            return result
    else:
        template_errors = validate_template(source_path, entry)
        secret_findings = scan_file(source_path)
        errors = template_errors + [f"secret-like {finding.kind} on line {finding.line}" for finding in secret_findings]
        if errors:
            result["state"] = "invalid"
            result["reason"] = "; ".join(errors)
            return result

    if entry.protected and entry.id not in include_protected:
        result["state"] = "protected"
        result["reason"] = entry.manual_reason or "protected/manual entry"
        return result

    if target_path.exists() and target_path.is_dir() and entry.kind != "symlink":
        result["state"] = "blocked"
        result["reason"] = "target is a directory"
        return result

    if entry.kind == "symlink":
        if not target_path.exists() and not target_path.is_symlink():
            result["state"] = "missing"
            result["reason"] = "target symlink is missing"
        elif not target_path.is_symlink():
            result["state"] = "drifted"
            result["reason"] = "target is not a symlink"
        elif str(target_path.readlink()) == (entry.link_target or ""):
            result["state"] = "current"
            result["reason"] = "target symlink matches"
        else:
            result["state"] = "drifted"
            result["reason"] = "target symlink differs"
        return result

    if not target_path.exists():
        result["state"] = "missing"
        result["reason"] = "target is missing"
        return result

    try:
        source_text = expected_text(source_path, entry)
        target_text = target_path.read_text()
    except OSError as exc:
        result["state"] = "blocked"
        result["reason"] = str(exc)
        return result
    if target_text == source_text:
        result["state"] = "current"
        result["reason"] = "target matches source"
    else:
        result["state"] = "drifted"
        result["reason"] = "target differs from source"
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
