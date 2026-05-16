from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from .backups import BackupError
from .fonts import CommandRunner, execute_font_operation, build_font_plan
from .installer import build_plan, execute_manifest_operation, failed_report
from .reports import Report
from .tool_installer import (
    TOOL_CACHE_REL,
    collect_post_install_summary,
    build_tool_install_plan,
    execute_tool_install_operation,
    prepare_apt_keyring_operations,
)


WARNING_STATES = {"missing", "drifted", "protected", "manual", "unsupported", "needs_update"}
FAILED_STATES = {"invalid", "blocked"}
TOOL_INSTALL_PHASES = {"all", "dev-base", "tools"}
TOOL_POST_INSTALL_MODES = {"all", "verify", "auto", "guidance"}


def _resolve_apply_paths(
    repo: Path | str,
    home: Path | str,
    backup_dir: Path | str | None,
) -> tuple[Path, Path, Path]:
    repo_path = Path(repo).resolve()
    home_path = Path(home).resolve()
    backup_path = (
        Path(backup_dir).expanduser().resolve()
        if backup_dir
        else home_path / ".dotfiles-backups"
    )
    return repo_path, home_path, backup_path


def _required_yes_report(
    command_name: str,
    repo_path: Path,
    home_path: Path,
    profile: str,
) -> Report:
    return Report(
        command_name,
        "failed",
        str(repo_path),
        home=str(home_path),
        profile=profile,
        errors=[{"message": f"{command_name} requires --yes before writing"}],
    )


def build_bootstrap_plan(
    repo: Path | str,
    home: Path | str,
    *,
    profile: str = "machine",
    include_protected: list[str] | None = None,
    env: Mapping[str, str] | None = None,
    path: str | None = None,
    runner: CommandRunner | None = None,
) -> Report:
    repo_path = Path(repo).resolve()
    home_path = Path(home).resolve()
    manifest_report = build_plan(repo_path, home_path, profile=profile, include_protected=include_protected)
    entries = list(manifest_report.entries)
    operations = list(manifest_report.operations)
    errors = list(manifest_report.errors)
    extra: dict[str, Any] = dict(manifest_report.extra)

    if profile == "machine":
        font_plan = build_font_plan(home_path, env=env, path=path, runner=runner)
        entries.extend(font_plan["entries"])
        operations.extend(font_plan["operations"])
        extra["fonts"] = font_plan["fonts"]
        extra["font_context"] = font_plan["context"]

    _renumber_operations(operations)
    status = _status(entries, operations, errors)
    return Report(
        "bootstrap-plan",
        status,
        str(repo_path),
        home=str(home_path),
        profile=profile,
        entries=entries,
        operations=operations,
        errors=errors,
        extra=extra,
    )


def apply_bootstrap(
    repo: Path | str,
    home: Path | str,
    *,
    profile: str = "machine",
    backup_dir: Path | str | None = None,
    yes: bool = False,
    include_protected: list[str] | None = None,
    env: Mapping[str, str] | None = None,
    runner: CommandRunner | None = None,
) -> Report:
    repo_path, home_path, backup_path = _resolve_apply_paths(repo, home, backup_dir)
    if not yes:
        return _required_yes_report("bootstrap-apply", repo_path, home_path, profile)

    report = build_bootstrap_plan(
        repo_path,
        home_path,
        profile=profile,
        include_protected=include_protected,
        env=env,
        runner=runner,
    )
    report.command = "bootstrap-apply"
    if report.errors or any(entry.get("state") in FAILED_STATES for entry in report.entries):
        report.status = "failed"
        return report

    return _execute_bootstrap_operations(report, repo_path, backup_path, runner)


def build_tool_install_subplan(
    repo: Path | str,
    home: Path | str,
    *,
    phase: str = "all",
    env: Mapping[str, str] | None = None,
    runner: CommandRunner | None = None,
) -> Report:
    repo_path = Path(repo).resolve()
    home_path = Path(home).resolve()
    tool_plan = build_tool_install_plan(home_path, phase=phase, env=env, runner=runner)
    operations = list(tool_plan["operations"])
    _renumber_operations(operations)
    entries = list(tool_plan["entries"])
    status = _status(entries, operations, [])
    return Report(
        "bootstrap-install-tools-plan",
        status,
        str(repo_path),
        home=str(home_path),
        profile="machine",
        entries=entries,
        operations=operations,
        extra={"tools": tool_plan["tools"]},
    )


def apply_tool_installs(
    repo: Path | str,
    home: Path | str,
    *,
    phase: str = "all",
    backup_dir: Path | str | None = None,
    yes: bool = False,
    env: Mapping[str, str] | None = None,
    runner: CommandRunner | None = None,
) -> Report:
    repo_path, home_path, backup_path = _resolve_apply_paths(repo, home, backup_dir)
    if not yes:
        return _required_yes_report("bootstrap-install-tools", repo_path, home_path, "machine")

    plan = build_tool_install_subplan(repo_path, home_path, phase=phase, env=env, runner=runner)
    plan.command = "bootstrap-install-tools"
    if plan.errors or any(entry.get("state") in FAILED_STATES for entry in plan.entries):
        plan.status = "failed"
        return plan
    report = _execute_bootstrap_operations(plan, repo_path, backup_path, runner)
    if phase == "all":
        summary = collect_post_install_summary(
            home_path,
            mode="all",
            yes=yes,
            runner=runner,
            env=env,
            repo_path=repo_path,
            backup_dir=backup_path,
        )
        _attach_post_install_summary(report, summary)
    return report


def run_tool_install_post_install(
    repo: Path | str,
    home: Path | str,
    *,
    mode: str = "all",
    yes: bool = False,
    env: Mapping[str, str] | None = None,
    runner: CommandRunner | None = None,
    backup_dir: Path | str | None = None,
) -> Report:
    repo_path, home_path, backup_path = _resolve_apply_paths(repo, home, backup_dir)
    if mode not in TOOL_POST_INSTALL_MODES:
        raise ValueError(f"unknown tool post-install mode: {mode}")
    report = Report(
        "bootstrap-install-tools-verify" if mode == "verify" else "bootstrap-install-tools-post",
        "ok",
        str(repo_path),
        home=str(home_path),
        profile="machine",
    )
    summary = collect_post_install_summary(
        home_path,
        mode=mode,
        yes=yes,
        runner=runner,
        env=env,
        repo_path=repo_path,
        backup_dir=backup_path,
    )
    _attach_post_install_summary(report, summary)
    return report


def _attach_post_install_summary(report: Report, summary: dict[str, Any]) -> None:
    if summary["verification"]:
        report.extra["verification"] = summary["verification"]
    if summary["post_install_actions"]:
        report.extra["post_install_actions"] = summary["post_install_actions"]
    report.backups.extend(summary["backups"])
    if summary["status"] == "warning":
        report.status = "warning"


def _execute_bootstrap_operations(
    report: Report,
    repo_path: Path,
    backup_path: Path,
    runner: CommandRunner | None,
) -> Report:
    backups: list[dict[str, Any]] = []
    completed_writes = 0
    executed: list[dict[str, Any]] = []
    effective_runner = runner or CommandRunner()
    if any(op.get("type") == "tool_install_apt_keyring" for op in report.operations):
        try:
            prepare_apt_keyring_operations(report.operations, runner=effective_runner)
        except (OSError, BackupError, RuntimeError) as exc:
            apt_keyring_op = next(
                op for op in report.operations if op.get("type") == "tool_install_apt_keyring"
            )
            return failed_report(report, executed, apt_keyring_op, backups, completed_writes, exc)
    for op in report.operations:
        try:
            completed_writes += _execute_operation(op, repo_path, backup_path, backups, effective_runner)
            executed.append(op)
        except (OSError, BackupError, RuntimeError) as exc:
            return failed_report(report, executed, op, backups, completed_writes, exc)
    report.backups = backups
    report.status = "warning" if _has_manual_or_refused_work(report) else "ok"
    return report


def _execute_operation(
    op: dict[str, Any],
    repo_path: Path,
    backup_path: Path,
    backups: list[dict[str, Any]],
    runner: CommandRunner | None,
) -> int:
    if op.get("recipe") == "tool_installs" or str(op.get("type", "")).startswith("tool_install_"):
        cache_dir = Path(op.get("cache_dir") or Path.home() / TOOL_CACHE_REL)
        return execute_tool_install_operation(op, runner=runner, cache_dir=cache_dir)
    if op.get("recipe") == "fonts" or str(op.get("type", "")).startswith("font_"):
        return execute_font_operation(op, runner=runner, backup_dir=backup_path, backups=backups)
    return execute_manifest_operation(op, repo_path, backup_path, backups)


def _has_manual_or_refused_work(report: Report) -> bool:
    if any(op.get("type") in {"refuse", "font_manual"} for op in report.operations):
        return True
    return any(entry.get("state") in {"protected", "manual", "unsupported"} for entry in report.entries)


def _status(entries: list[dict[str, Any]], operations: list[dict[str, Any]], errors: list[Any]) -> str:
    if errors or any(entry.get("state") in FAILED_STATES for entry in entries):
        return "failed"
    if operations or any(entry.get("state") in WARNING_STATES for entry in entries):
        return "warning"
    return "ok"


def _renumber_operations(operations: list[dict[str, Any]]) -> None:
    for index, operation in enumerate(operations, 1):
        operation["operation_id"] = f"op-{index:03d}"
