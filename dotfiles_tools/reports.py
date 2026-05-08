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
    _extend_extra_tools(lines, extra.get("tools") or [])
    _extend_extra_verification(lines, extra.get("verification") or [])
    _extend_extra_post_install(lines, extra.get("post_install_actions") or [])
    _extend_extra_codacy_setup(lines, extra.get("codacy_setup_guidance"))


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


def _extend_extra_tools(lines: list[str], tools: list[dict[str, Any]]) -> None:
    if not tools:
        return
    dev_base = next((item for item in tools if item.get("entry_id") == "tools.dev_base"), None)
    individual = [item for item in tools if item.get("entry_id") != "tools.dev_base"]
    lines.append("tool install/update preview:")
    _extend_tool_section(lines, individual, "installed",
                         "  Already installed (will be updated where possible):", _tool_installed_line)
    _extend_tool_section(lines, individual, "missing",
                         "  Missing (will be installed):", _tool_missing_line)
    _extend_tool_section(lines, individual, "unsupported",
                         "  Unsupported on this platform:", _tool_unsupported_line)
    if dev_base is not None:
        _extend_dev_base_summary(lines, dev_base)


def _extend_tool_section(
    lines: list[str],
    items: list[dict[str, Any]],
    state: str,
    header: str,
    formatter,
) -> None:
    matching = [item for item in items if item.get("state") == state]
    if not matching:
        return
    lines.append(header)
    for item in matching:
        lines.append(formatter(item))


def _tool_unsupported_line(item: dict[str, Any]) -> str:
    return f"    - {item.get('label')} ({item.get('install_method')})"


def _tool_installed_line(item: dict[str, Any]) -> str:
    method = item.get("install_method")
    action_label = {
        "apt": "apt --only-upgrade",
        "apt_keyring": "apt --only-upgrade (keyring repo)",
        "curl_installer": "re-run installer (self-update)",
        "npm": "npm update -g --prefix ~/.local",
    }.get(method, "skip")
    label = item.get("label") or item.get("command") or item.get("entry_id")
    path = item.get("current_path") or ""
    version = item.get("current_version") or ""
    suffix = f" {version}" if version else ""
    return f"    - {label}: {path}{suffix} -> {action_label}"


def _tool_missing_line(item: dict[str, Any]) -> str:
    method = item.get("install_method")
    method_label = {
        "apt": "apt (sudo)",
        "apt_keyring": "apt + keyring repo (sudo)",
        "curl_installer": "curl installer (no sudo)",
        "npm": "npm install -g --prefix ~/.local",
    }.get(method, method or "manual")
    label = item.get("label") or item.get("command") or item.get("entry_id")
    return f"    - {label}: {method_label}"


def _extend_dev_base_summary(lines: list[str], dev_base: dict[str, Any]) -> None:
    total = dev_base.get("total_packages") or 0
    missing = dev_base.get("missing_packages") or []
    installed = dev_base.get("installed_packages") or []
    lines.append(f"  Dev base packages ({total} total, grouped):")
    for group in dev_base.get("groups") or []:
        lines.append(_dev_base_group_line(group))
    summary = _dev_base_summary_line(missing, installed)
    if summary:
        lines.append(summary)


def _dev_base_group_line(group: dict[str, Any]) -> str:
    name = group.get("name", "")
    present = len(group.get("installed") or [])
    size = len(group.get("packages") or [])
    missing_pkgs = group.get("missing") or []
    if missing_pkgs:
        return f"    {name:<10s} {present}/{size} installed (missing: {', '.join(missing_pkgs)})"
    return f"    {name:<10s} {present}/{size} installed -> apt --only-upgrade"


def _dev_base_summary_line(missing: list[str], installed: list[str]) -> str:
    if missing and installed:
        return (
            f"  -> One batched apt install for {len(missing)} missing packages,"
            f" one batched apt upgrade for {len(installed)} present packages."
        )
    if missing:
        return f"  -> One batched apt install for {len(missing)} missing packages."
    if installed:
        return f"  -> One batched apt upgrade for {len(installed)} present packages."
    return ""


def _extend_extra_verification(lines: list[str], verification: list[dict[str, Any]]) -> None:
    if not verification:
        return
    lines.append("verification:")
    for item in verification:
        glyph = "OK" if item.get("verified") else "MISSING"
        path = item.get("path") or "not found on PATH"
        version = f"  ({item['version']})" if item.get("version") else ""
        lines.append(f"  {glyph}  {item.get('command', ''):<10s} {path}{version}")


def _extend_extra_post_install(lines: list[str], actions: list[dict[str, Any]]) -> None:
    if not actions:
        return
    by_status = _post_install_group_by_status(actions)
    _extend_post_install_auto(lines, by_status["ran"], by_status["failed"])
    _extend_post_install_skipped(lines, by_status["skipped"])
    _extend_post_install_guidance(lines, by_status["guidance"])


def _post_install_group_by_status(actions: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    groups: dict[str, list[dict[str, Any]]] = {
        "ran": [], "failed": [], "skipped": [], "guidance": [],
    }
    for action in actions:
        bucket = groups.get(action.get("status"))
        if bucket is not None:
            bucket.append(action)
    return groups


def _extend_post_install_auto(
    lines: list[str],
    auto_run: list[dict[str, Any]],
    auto_failed: list[dict[str, Any]],
) -> None:
    if not (auto_run or auto_failed):
        return
    lines.append("post-install actions (auto-run, --yes):")
    for item in auto_run:
        lines.append(_post_install_line(item, glyph="OK"))
    for item in auto_failed:
        lines.append(_post_install_line(item, glyph="FAIL"))
        if item.get("result"):
            lines.append(f"      reason: {item['result']}")


def _extend_post_install_skipped(lines: list[str], skipped: list[dict[str, Any]]) -> None:
    if not skipped:
        return
    lines.append("post-install actions (skipped, unresolved placeholder):")
    for item in skipped:
        lines.append(f"  - {item.get('tool')}  {item.get('label')}: {item.get('reason')}")


def _extend_post_install_guidance(lines: list[str], guidance: list[dict[str, Any]]) -> None:
    if not guidance:
        return
    lines.append("post-install actions (manual, run when ready):")
    for item in guidance:
        cmd = " ".join(item.get("command") or item.get("raw_template") or [])
        lines.append(f"  - {item.get('tool'):<8s} {item.get('label')}:  {cmd}")


def _post_install_line(item: dict[str, Any], *, glyph: str) -> str:
    cmd = " ".join(item.get("command") or [])
    return f"  {glyph}  {item.get('tool'):<8s} {item.get('label')}:  {cmd}"


def _extend_extra_codacy_setup(lines: list[str], guidance: dict[str, Any] | None) -> None:
    if not guidance:
        return
    lines.append("codacy setup guidance:")
    lines.append(f"  tool: {guidance.get('tool')}")
    lines.append(f"  {guidance.get('guidance')}")
