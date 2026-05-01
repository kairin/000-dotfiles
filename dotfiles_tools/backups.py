from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import shutil


class BackupError(OSError):
    pass


def backup_path_for(target: Path, backup_dir: Path, *, entry_id: str) -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    safe_name = str(target).lstrip("/").replace("/", "__")
    return backup_dir / timestamp / entry_id / safe_name


def create_backup(target: Path, backup_dir: Path, *, entry_id: str) -> dict[str, str]:
    if not target.exists() and not target.is_symlink():
        raise BackupError(f"target does not exist: {target}")
    backup_dir = backup_dir.resolve()
    backup_target = backup_path_for(target.resolve() if not target.is_symlink() else target.absolute(), backup_dir, entry_id=entry_id)
    backup_target.parent.mkdir(parents=True, exist_ok=True)
    try:
        backup_target.relative_to(backup_dir)
    except ValueError as exc:
        raise BackupError(f"backup target escapes backup dir: {backup_target}") from exc
    if target.is_symlink():
        backup_target.symlink_to(target.readlink())
    elif target.is_dir():
        shutil.copytree(target, backup_target)
    else:
        shutil.copy2(target, backup_target)
    return {
        "entry_id": entry_id,
        "original_target": str(target),
        "backup_target": str(backup_target),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "created",
        "reason": "existing target differed before replacement",
    }
