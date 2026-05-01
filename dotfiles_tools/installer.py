from __future__ import annotations

from pathlib import Path
from typing import Any

from .backups import BackupError, create_backup
from .doctor import evaluate_entry
from .manifest import ManifestError, load_manifest, resolve_source, resolve_target, validate_included_protected
from .reports import Report
from .templates import expected_text


def build_plan(repo: Path | str, home: Path | str, *, profile: str = "machine", include_protected: list[str] | None = None) -> Report:
    repo_path = Path(repo).resolve()
    home_path = Path(home).resolve()
    entries: list[dict[str, Any]] = []
    operations: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    try:
        manifest = load_manifest(repo_path)
        include_set = validate_included_protected(manifest, include_protected)
        for entry in manifest.entries_for_profile(profile):
            state = evaluate_entry(repo_path, home_path, entry, include_set)
            entries.append(state)
            operations.extend(_operations_for_state(repo_path, home_path, entry, state))
    except ManifestError as exc:
        errors.append({"message": str(exc)})
    _renumber_operations(operations)
    status = "failed" if errors or any(entry["state"] in {"invalid", "blocked"} for entry in entries) else "warning" if operations else "ok"
    return Report("plan", status, str(repo_path), home=str(home_path), profile=profile, entries=entries, operations=operations, errors=errors)


def apply_plan(
    repo: Path | str,
    home: Path | str,
    *,
    profile: str = "machine",
    backup_dir: Path | str,
    yes: bool = False,
    include_protected: list[str] | None = None,
) -> Report:
    repo_path = Path(repo).resolve()
    home_path = Path(home).resolve()
    backup_path = Path(backup_dir).expanduser().resolve()
    if not yes:
        return _approval_error(repo_path, home_path, profile)
    report = build_plan(repo_path, home_path, profile=profile, include_protected=include_protected)
    report.command = "apply"
    if _attach_blocking_errors(report):
        return report

    return _execute_apply_operations(report, repo_path, backup_path)


def _approval_error(repo: Path, home: Path, profile: str) -> Report:
    return Report(
        "apply",
        "failed",
        str(repo),
        home=str(home),
        profile=profile,
        errors=[{"message": "apply requires --yes before writing"}],
    )


def _attach_blocking_errors(report: Report) -> bool:
    if report.errors:
        report.status = "failed"
        return True
    blocking_entries = [entry for entry in report.entries if entry.get("state") in {"invalid", "blocked"}]
    for entry in blocking_entries:
        report.errors.append({"entry_id": entry["entry_id"], "message": entry.get("reason", "entry blocks apply")})
    if blocking_entries:
        report.status = "failed"
        return True
    return False


def _execute_apply_operations(report: Report, repo_path: Path, backup_path: Path) -> Report:
    backups: list[dict[str, Any]] = []
    completed_writes = 0
    executed: list[dict[str, Any]] = []
    for op in report.operations:
        try:
            completed_writes += _execute_operation(op, repo_path, backup_path, backups)
            executed.append(op)
        except (OSError, BackupError) as exc:
            return _failed_apply_report(report, executed, op, backups, completed_writes, exc)
    report.backups = backups
    report.status = "warning" if any(op["type"] == "refuse" for op in report.operations) else "ok"
    return report


def _execute_operation(op: dict[str, Any], repo_path: Path, backup_path: Path, backups: list[dict[str, Any]]) -> int:
    if op["type"] == "mkdir":
        Path(op["target"]).mkdir(parents=True, exist_ok=True)
        return 1
    if op["type"] == "backup":
        record = create_backup(Path(op["target"]), backup_path, entry_id=op["entry_id"])
        op["backup_target"] = record["backup_target"]
        backups.append(record)
        return 1
    if op["type"] == "copy":
        _copy_operation(op, repo_path)
        return 1
    if op["type"] == "symlink":
        _symlink_operation(op)
        return 1
    return 0


def _copy_operation(op: dict[str, Any], repo_path: Path) -> None:
    target = Path(op["target"])
    target.parent.mkdir(parents=True, exist_ok=True)
    source = Path(op["source"])
    target.write_text(expected_text(source, _entry_for(op["entry_id"], repo_path)))


def _symlink_operation(op: dict[str, Any]) -> None:
    target = Path(op["target"])
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() or target.is_symlink():
        if target.is_dir() and not target.is_symlink():
            raise OSError(f"cannot replace directory with symlink: {target}")
        target.unlink()
    target.symlink_to(op["link_target"])


def _failed_apply_report(
    report: Report,
    executed: list[dict[str, Any]],
    op: dict[str, Any],
    backups: list[dict[str, Any]],
    completed_writes: int,
    exc: Exception,
) -> Report:
    report.errors.append({"operation_id": op.get("operation_id", ""), "entry_id": op.get("entry_id", ""), "message": str(exc)})
    report.operations = executed + [op]
    report.backups = backups
    report.status = "partial" if completed_writes else "failed"
    if completed_writes:
        report.operations.append({
            "operation_id": f"op-{len(report.operations) + 1:03d}",
            "entry_id": op.get("entry_id", ""),
            "type": "partial_apply",
            "target": op.get("target"),
            "reason": "stopped on first failed write",
            "requires_approval": False,
        })
    return report


def _operations_for_state(repo: Path, home: Path, entry, state: dict[str, Any]) -> list[dict[str, Any]]:
    source = resolve_source(repo, entry)
    target = resolve_target(repo, home, entry)
    base = {
        "entry_id": entry.id,
        "source": str(source),
        "target": str(target),
        "requires_approval": True,
    }
    if state["state"] == "protected":
        return [{**base, "type": "refuse", "reason": state.get("reason", "protected/manual entry"), "requires_approval": False}]
    if state["state"] in {"invalid", "blocked"}:
        return [{**base, "type": "refuse", "reason": state.get("reason", "cannot plan write"), "requires_approval": False}]
    if state["state"] == "current":
        return [{**base, "type": "skip", "reason": "target already current", "requires_approval": False}]
    ops: list[dict[str, Any]] = []
    if not target.parent.exists():
        ops.append({**base, "type": "mkdir", "target": str(target.parent), "reason": "target parent directory is missing"})
    if state["state"] == "drifted":
        ops.append({**base, "type": "backup", "reason": "target differs and must be backed up before replacement"})
    if entry.kind == "symlink":
        ops.append({**base, "type": "symlink", "link_target": entry.link_target, "reason": "create target symlink"})
    else:
        ops.append({**base, "type": "copy", "reason": "copy source to target"})
    return ops


def _renumber_operations(operations: list[dict[str, Any]]) -> None:
    for index, operation in enumerate(operations, 1):
        operation["operation_id"] = f"op-{index:03d}"


def _entry_for(entry_id: str, repo: Path):
    manifest = load_manifest(repo)
    return manifest.entry_map()[entry_id]
