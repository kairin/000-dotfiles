from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Any


SUMMARY_KEYS = (
    "missing",
    "current",
    "drifted",
    "protected",
    "invalid",
    "blocked",
    "installed",
    "needs_update",
    "manual",
    "unsupported",
    "operations",
    "backups",
    "errors",
)


@dataclass
class Report:
    command: str
    status: str
    repo: str
    home: str | None = None
    project: str | None = None
    profile: str | None = None
    entries: list[dict[str, Any]] = field(default_factory=list)
    operations: list[dict[str, Any]] = field(default_factory=list)
    backups: list[dict[str, Any]] = field(default_factory=list)
    errors: list[dict[str, Any] | str] = field(default_factory=list)
    extra: dict[str, Any] = field(default_factory=dict)

    def summary(self) -> dict[str, int]:
        summary = {key: 0 for key in SUMMARY_KEYS}
        for entry in self.entries:
            state = entry.get("state")
            if state in summary:
                summary[state] += 1
        summary["operations"] = len(self.operations)
        summary["backups"] = len(self.backups)
        summary["errors"] = len(self.errors)
        return summary

    def to_dict(self) -> dict[str, Any]:
        data = {
            "command": self.command,
            "status": self.status,
            "repo": self.repo,
            "home": self.home,
            "project": self.project,
            "profile": self.profile,
            "summary": self.summary(),
            "entries": self.entries,
            "operations": self.operations,
            "backups": self.backups,
            "errors": self.errors,
        }
        data.update(self.extra)
        return data

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True) + "\n"

    def to_human(self) -> str:
        lines = [
            f"{self.command}: {self.status}",
            f"repo: {self.repo}",
        ]
        if self.home:
            lines.append(f"home: {self.home}")
        if self.project:
            lines.append(f"project: {self.project}")
        if self.profile:
            lines.append(f"profile: {self.profile}")
        lines.append("summary:")
        for key, value in self.summary().items():
            lines.append(f"  {key}: {value}")
        _extend_entries(lines, self.entries)
        _extend_operations(lines, self.operations)
        _extend_backups(lines, self.backups)
        _extend_errors(lines, self.errors)
        _extend_extra(lines, self.extra)
        return "\n".join(lines) + "\n"


def status_from_entries(entries: list[dict[str, Any]], errors: list[Any] | None = None) -> str:
    if errors:
        return "failed"
    states = {entry.get("state") for entry in entries}
    if states & {"invalid", "blocked"}:
        return "failed"
    if states & {"missing", "drifted", "protected"}:
        return "warning"
    return "ok"


def render(report: Report, as_json: bool = False) -> str:
    return report.to_json() if as_json else report.to_human()


def path_text(path: Path | None) -> str | None:
    return str(path) if path is not None else None


def _extend_entries(lines: list[str], entries: list[dict[str, Any]]) -> None:
    if not entries:
        return
    lines.append("entries:")
    for entry in entries:
        reason = entry.get("reason") or ""
        manual = entry.get("manual_reason")
        suffix = f" ({reason})" if reason else ""
        if manual:
            suffix += f" manual: {manual}"
        lines.append(f"  - {entry.get('entry_id')}: {entry.get('state')}{suffix}")


def _extend_operations(lines: list[str], operations: list[dict[str, Any]]) -> None:
    if not operations:
        return
    lines.append("operations:")
    for op in operations:
        bits = [op.get("operation_id", ""), op.get("type", ""), op.get("entry_id", "")]
        lines.append("  - " + " ".join(bit for bit in bits if bit))


def _extend_backups(lines: list[str], backups: list[dict[str, Any]]) -> None:
    if not backups:
        return
    lines.append("backups:")
    for backup in backups:
        lines.append(f"  - {backup.get('entry_id')}: {backup.get('backup_target')}")


def _extend_errors(lines: list[str], errors: list[dict[str, Any] | str]) -> None:
    if not errors:
        return
    lines.append("errors:")
    for error in errors:
        lines.append(f"  - {error}")


def _extend_extra(lines: list[str], extra: dict[str, Any]) -> None:
    _extend_extra_fonts(lines, extra.get("fonts") or [])
    _extend_extra_tool_checks(lines, extra.get("tool_checks") or [])
    _extend_extra_auth_guidance(lines, extra.get("auth_guidance") or [])


def _extend_extra_fonts(lines: list[str], fonts: list[dict[str, Any]]) -> None:
    if fonts:
        lines.append("font actions:")
        for item in fonts:
            _extend_extra_font_item(lines, item)


def _extend_extra_font_item(lines: list[str], item: dict[str, Any]) -> None:
    sudo = "yes" if item.get("requires_sudo") else "no"
    source_type = item.get("source_type")
    version = item.get("latest_version") or item.get("candidate_version") or "unknown"
    lines.append(f"  - {item.get('label')}: {item.get('state')} ({source_type}) -> {item.get('target')}")
    lines.append(f"    version: installed={item.get('installed_version') or 'unknown'} latest/candidate={version}")
    if item.get("cache_path"):
        lines.append(f"    cache: {item.get('cache_path')}")
    lines.append(f"    terminal face: {item.get('terminal_face') or 'n/a'}")
    lines.append(f"    sudo: {sudo}; host: {item.get('host_action')}")
    lines.append(f"    terminal: {item.get('terminal_impact')}")


def _extend_extra_tool_checks(lines: list[str], tool_checks: list[dict[str, Any]]) -> None:
    if tool_checks:
        lines.append("tool checks:")
        for item in tool_checks:
            lines.append(_extra_tool_check_line(item))


def _extra_tool_check_line(item: dict[str, Any]) -> str:
    path = item.get("path")
    location = f" ({path})" if path else ""
    bootstrap = " bootstrap" if item.get("bootstrap") else ""
    hint = f" - {item.get('install_hint')}" if item.get("state") == "missing" else ""
    return f"  - {item.get('command')}: {item.get('state')}{location}{bootstrap}{hint}"


def _extend_extra_auth_guidance(lines: list[str], auth_guidance: list[dict[str, Any]]) -> None:
    if auth_guidance:
        lines.append("auth/setup guidance:")
        for item in auth_guidance:
            lines.append(_extra_auth_line(item))


def _extra_auth_line(item: dict[str, Any]) -> str:
    if item.get("state") == "available":
        return f"  - {item.get('command')}: {item.get('guidance')}"
    return f"  - {item.get('tool')}: install tool before auth setup"
