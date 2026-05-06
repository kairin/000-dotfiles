from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .backups import create_backup
from .manifest import ManifestError, load_manifest
from .placeholders import PlaceholderError, find_placeholders, render_placeholders
from .reports import Report


def load_vars(path: Path | str) -> dict[str, str]:
    data = json.loads(Path(path).read_text())
    if not isinstance(data, dict):
        raise ValueError("vars JSON must be an object")
    return {str(key): str(value) for key, value in data.items()}


def init_project(
    repo: Path | str,
    project: Path | str,
    vars_path: Path | str,
    *,
    backup_dir: Path | str | None = None,
    yes: bool = False,
    copilot: bool = False,
) -> Report:
    repo_path = Path(repo).resolve()
    project_path = Path(project).resolve()
    if not yes:
        return Report("init-project", "failed", str(repo_path), project=str(project_path), errors=[{"message": "init-project requires --yes before writing"}])

    prepared, error = _prepare_project_init(repo_path, vars_path, copilot)
    if error:
        return Report("init-project", "failed", str(repo_path), project=str(project_path), errors=[{"message": error}])

    config, agent_text, copilot_text = prepared
    backup_path = Path(backup_dir).resolve() if backup_dir else project_path / ".dotfiles-backups"
    operations: list[dict[str, Any]] = []
    backups: list[dict[str, Any]] = []
    errors = _write_project_docs(project_path, config.symlinks, agent_text, copilot_text, backup_path, backups, operations)
    _renumber_operations(operations)
    entries = [_project_entry(repo_path, project_path, config.agent_template, agent_text)]
    status = "failed" if errors else "ok"
    report = Report("init-project", status, str(repo_path), project=str(project_path), entries=entries, operations=operations, backups=backups, errors=errors)
    if not errors:
        report.extra["codacy_setup_guidance"] = _codacy_setup_guidance(project_path)
    return report


def _prepare_project_init(repo_path: Path, vars_path: Path | str, copilot: bool):
    try:
        manifest = load_manifest(repo_path)
        values = load_vars(vars_path)
        config = manifest.project_init
        agent_source = repo_path / config.agent_template
        agent_text = render_placeholders(agent_source.read_text(), values)
        copilot_text = None
        if copilot:
            if not config.copilot_template:
                raise ManifestError("project_init.copilot_template is not configured")
            copilot_text = render_placeholders((repo_path / config.copilot_template).read_text(), values)
    except (ManifestError, PlaceholderError, OSError, json.JSONDecodeError, ValueError) as exc:
        return None, str(exc)
    return (config, agent_text, copilot_text), None


def _write_project_docs(
    project_path: Path,
    symlinks: tuple[str, ...],
    agent_text: str,
    copilot_text: str | None,
    backup_path: Path,
    backups: list[dict[str, Any]],
    operations: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    try:
        _write_file(project_path / "AGENTS.md", agent_text, backup_path, "project.agents", backups, operations)
        for link_name in symlinks:
            _write_symlink(project_path / link_name, "AGENTS.md", backup_path, f"project.{link_name}", backups, operations)
        if copilot_text is not None:
            _write_file(project_path / ".github" / "copilot-instructions.md", copilot_text, backup_path, "project.copilot", backups, operations)
    except OSError as exc:
        errors.append({"message": str(exc)})
    return errors


def _project_entry(repo_path: Path, project_path: Path, template: str, agent_text: str) -> dict[str, Any]:
    return {
        "entry_id": "project.placeholders",
        "source": str(repo_path / template),
        "target": str(project_path / "AGENTS.md"),
        "state": "current" if not find_placeholders(agent_text) else "invalid",
        "protected": False,
        "reason": "project agent docs rendered",
    }


def _write_file(path: Path, content: str, backup_dir: Path, entry_id: str, backups: list[dict[str, Any]], operations: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() or path.is_symlink():
        if path.is_symlink() or path.read_text() != content:
            backups.append(create_backup(path, backup_dir, entry_id=entry_id))
            if path.is_dir():
                raise OSError(f"cannot replace directory: {path}")
            path.unlink()
        else:
            operations.append(_operation("skip", entry_id, path, "target already current"))
            return
    path.write_text(content)
    operations.append(_operation("copy", entry_id, path, "wrote rendered file"))


def _write_symlink(path: Path, target: str, backup_dir: Path, entry_id: str, backups: list[dict[str, Any]], operations: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() or path.is_symlink():
        if path.is_symlink() and str(path.readlink()) == target:
            operations.append(_operation("skip", entry_id, path, "symlink already current"))
            return
        backups.append(create_backup(path, backup_dir, entry_id=entry_id))
        if path.is_dir() and not path.is_symlink():
            raise OSError(f"cannot replace directory: {path}")
        path.unlink()
    path.symlink_to(target)
    operations.append(_operation("symlink", entry_id, path, "created symlink", link_target=target))


def _operation(op_type: str, entry_id: str, target: Path, reason: str, **extra: Any) -> dict[str, Any]:
    operation = {
        "operation_id": "",
        "entry_id": entry_id,
        "type": op_type,
        "target": str(target),
        "reason": reason,
        "requires_approval": op_type not in {"skip"},
    }
    operation.update(extra)
    return operation


def _renumber_operations(operations: list[dict[str, Any]]) -> None:
    for index, operation in enumerate(operations, 1):
        operation["operation_id"] = f"op-{index:03d}"


def _codacy_setup_guidance(project_path: Path) -> dict[str, Any]:
    return {
        "tool": "mcp__codacy__codacy_setup_repository",
        "project": str(project_path),
        "guidance": (
            "Run codacy_setup_repository via the Codacy MCP server to register this "
            "repository and enable issue tracking and coverage reporting."
        ),
    }
