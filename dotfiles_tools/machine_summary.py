from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

from .bootstrap import build_bootstrap_plan, build_tool_install_subplan
from .doctor import run_doctor
from .manifest import ManifestEntry, ManifestError, load_manifest
from .reports import Report
from .tool_installer import DEV_BASE_ENTRY_ID


@dataclass(frozen=True)
class Recommendation:
    option_number: int
    label: str
    reason: str
    state_category: str


def render_machine_summary(repo: Path | str, home: Path | str, *, profile: str = "machine") -> str:
    repo_path = Path(repo).resolve()
    home_path = Path(home).resolve()
    doctor = run_doctor(repo_path, home_path, profile=profile)
    plan = build_bootstrap_plan(repo_path, home_path, profile=profile)
    return render_reports(doctor, plan, repo_path, home_path, profile=profile)


def render_menu_mode(repo: Path | str, home: Path | str) -> str:
    """Return 'tools_missing' if any non-dev-base bootstrap tool is absent;
    otherwise 'tools_present'. The bash menu reads this token to decide
    which option is tagged [recommended]."""
    plan = build_tool_install_subplan(Path(repo).resolve(), Path(home).resolve())
    has_missing = any(
        entry.get("state") == "missing"
        for entry in plan.entries
        if entry.get("entry_id") != DEV_BASE_ENTRY_ID
    )
    return "tools_missing" if has_missing else "tools_present"


def render_missing_tool_count(repo: Path | str, home: Path | str) -> int:
    plan = build_tool_install_subplan(Path(repo).resolve(), Path(home).resolve())
    return sum(
        1
        for entry in plan.entries
        if entry.get("state") == "missing" and entry.get("entry_id") != DEV_BASE_ENTRY_ID
    )


def render_reports(doctor: Report, plan: Report, repo: Path, home: Path, *, profile: str = "machine") -> str:
    groups = _group_entries(plan.entries)
    action_summary = _action_summary(doctor, plan, groups)
    manifest_entries = _manifest_entry_map(repo)
    recommendation = _recommendation(doctor, plan, action_summary, groups)
    lines = _summary_header(repo, home, profile, recommendation)
    _extend_recommendation_context(lines, recommendation, action_summary, groups, doctor, plan)
    _extend_report_sections(lines, doctor, plan, groups, manifest_entries)
    lines.extend([
        "",
        "Full details: choose option 3 for cache paths, versions, package candidates, terminal faces, host actions, and raw operations.",
    ])
    return "\n".join(lines) + "\n"


def _manifest_entry_map(repo: Path) -> dict[str, ManifestEntry]:
    try:
        return load_manifest(repo).entry_map()
    except ManifestError:
        return {}


def _recommendation(
    doctor: Report,
    plan: Report,
    action_summary: dict[str, int | bool],
    groups: dict[str, list[dict[str, Any]]],
) -> Recommendation:
    # Return the first matching recommendation; fall back to "current".
    return (
        _recommendation_for_audit_failure(doctor, plan)
        or _recommendation_for_blockers(action_summary)
        or _recommendation_for_missing_tools(doctor)
        or _recommendation_for_safe_changes(action_summary)
        or _recommendation_for_auth_guidance(doctor)
        or _recommendation_for_manual_only(action_summary, groups)
        or _recommendation_for_current()
    )


def _recommendation_for_audit_failure(doctor: Report, plan: Report) -> Recommendation | None:
    if doctor.errors or plan.errors:
        return Recommendation(3, "Show full technical details", "The audit is incomplete.", "incomplete_audit")
    return None


def _recommendation_for_blockers(action_summary: dict[str, int | bool]) -> Recommendation | None:
    if action_summary["blockers"]:
        return Recommendation(
            3,
            "Show full technical details",
            "Inspect the full details before applying changes.",
            "blocked",
        )
    return None


def _recommendation_for_missing_tools(doctor: Report) -> Recommendation | None:
    if _missing_tool_checks(doctor.extra.get("tool_checks") or []):
        return Recommendation(
            1,
            "Install / update developer tools",
            "Developer tools should be installed or updated first.",
            "tools_missing",
        )
    return None


def _recommendation_for_safe_changes(action_summary: dict[str, int | bool]) -> Recommendation | None:
    if action_summary["file_changes"] or action_summary["font_actions"]:
        return Recommendation(
            2,
            "Apply safe non-protected dotfiles",
            "Safe non-protected setup changes are pending.",
            "safe_changes",
        )
    return None


def _recommendation_for_auth_guidance(doctor: Report) -> Recommendation | None:
    auth_guidance = doctor.extra.get("auth_guidance") or []
    # Only recommend option 4 when at least one tool is present but not yet signed in.
    if any(item.get("state") == "available" for item in auth_guidance):
        return Recommendation(
            4,
            "Show tool and sign-in guidance",
            "Sign-in guidance is the useful next step.",
            "auth_guidance",
        )
    return None


def _recommendation_for_manual_only(
    action_summary: dict[str, int | bool],
    groups: dict[str, list[dict[str, Any]]],
) -> Recommendation | None:
    if groups["protected"] or action_summary["manual_fonts"]:
        return Recommendation(
            3,
            "Show full technical details",
            "Manual items need inspection and are not applied automatically.",
            "manual_only",
        )
    return None


def _recommendation_for_current() -> Recommendation:
    return Recommendation(7, "Exit without writing", "Setup is current and no write action is needed.", "current")


def _missing_tool_checks(tool_checks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [item for item in tool_checks if item.get("state") == "missing"]


def _summary_header(repo: Path, home: Path, profile: str, recommendation: Recommendation) -> list[str]:
    return [
        "Machine setup summary",
        f"Repo: {repo}",
        f"Home: {home}",
        f"Profile: {profile}",
        "",
        f"Recommended next step: {recommendation.option_number}. {recommendation.label} - {recommendation.reason}",
    ]


def _extend_recommendation_context(
    lines: list[str],
    recommendation: Recommendation,
    action_summary: dict[str, int | bool],
    groups: dict[str, list[dict[str, Any]]],
    doctor: Report,
    plan: Report,
) -> None:
    handlers = {
        "tools_missing": lambda: _extend_tools_missing_context(lines, doctor),
        "safe_changes": lambda: _extend_safe_changes_context(lines, action_summary, groups),
        "incomplete_audit": lambda: _extend_incomplete_audit_context(lines, doctor, plan),
        "blocked": lambda: _extend_blocked_context(lines, action_summary),
        "auth_guidance": lambda: _extend_auth_guidance_context(lines, doctor),
        "manual_only": lambda: _extend_manual_only_context(lines, action_summary, groups),
        "current": lambda: lines.append("  - Setup is current and no write action is needed."),
    }
    handler = handlers.get(recommendation.state_category)
    if handler is not None:
        handler()


def _extend_tools_missing_context(lines: list[str], doctor: Report) -> None:
    missing = _missing_tool_checks(doctor.extra.get("tool_checks") or [])
    lines.append(f"  - {len(missing)} developer tools are missing or unverified.")
    for item in missing:
        lines.append(f"    - {item.get('command')}: {item.get('install_hint')}")


def _extend_safe_changes_context(
    lines: list[str],
    action_summary: dict[str, int | bool],
    groups: dict[str, list[dict[str, Any]]],
) -> None:
    lines.append("  - Safe non-protected setup changes are pending.")
    if action_summary["file_changes"]:
        sentence = _file_change_sentence(len(groups["updates"]), len(groups["creates"]), action_summary["backups"])
        lines.append("  - " + sentence)
    if action_summary["font_actions"]:
        lines.append("  - Install/update " + _font_action_sentence(action_summary) + ".")
    if action_summary["requires_network"]:
        lines.append("  - Network may be used for Nerd Font downloads unless cached.")
    if action_summary["requires_apt_sudo"]:
        lines.append("  - sudo is needed for apt fallback font packages.")
    elif action_summary["requires_sudo"]:
        lines.append("  - sudo is needed for host/system font actions.")


def _extend_incomplete_audit_context(lines: list[str], doctor: Report, plan: Report) -> None:
    lines.append("  - The audit is incomplete; inspect the full technical details.")
    if doctor.errors:
        lines.append(f"  - Doctor errors: {_plural(len(doctor.errors), 'issue')}.")
    if plan.errors:
        lines.append(f"  - Plan errors: {_plural(len(plan.errors), 'issue')}.")


def _extend_blocked_context(lines: list[str], action_summary: dict[str, int | bool]) -> None:
    lines.append(f"  - Stop on {_plural(action_summary['blockers'], 'blocking issue')}; fix before applying.")


def _partition_auth_guidance(
    auth_guidance: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    pending = [item for item in auth_guidance if item.get("state") == "available"]
    signed_in = [item for item in auth_guidance if item.get("state") == "signed_in"]
    return pending, signed_in


def _append_signed_in_line(lines: list[str], signed_in: list[dict[str, Any]]) -> None:
    if not signed_in:
        return
    identities = ", ".join(_auth_identity_label(item) for item in signed_in)
    lines.append(f"  - Verified sign-ins: {identities}.")


def _extend_auth_guidance_context(lines: list[str], doctor: Report) -> None:
    auth_guidance = doctor.extra.get("auth_guidance") or []
    pending, signed_in = _partition_auth_guidance(auth_guidance)
    _append_signed_in_line(lines, signed_in)
    if pending:
        commands = ", ".join(str(item.get("command")) for item in pending)
        lines.append(f"  - Pending sign-ins: {commands}.")


def _extend_manual_only_context(
    lines: list[str],
    action_summary: dict[str, int | bool],
    groups: dict[str, list[dict[str, Any]]],
) -> None:
    if groups["protected"]:
        lines.append(f"  - Leave {_plural(len(groups['protected']), 'protected/manual file')} untouched.")
    if action_summary["manual_fonts"]:
        lines.append(f"  - Skip {_plural(action_summary['manual_fonts'], 'manual/unsupported font item')}; see Fonts below.")


def _extend_report_sections(
    lines: list[str],
    doctor: Report,
    plan: Report,
    groups: dict[str, list[dict[str, Any]]],
    manifest_entries: dict[str, ManifestEntry],
) -> None:
    _extend_change_group(lines, "Update existing files with backups", groups["updates"], manifest_entries)
    _extend_change_group(lines, "Create missing files", groups["creates"], manifest_entries)
    _extend_manual_group(lines, groups["protected"], manifest_entries)
    _extend_blocking_group(lines, groups["blocked"], manifest_entries)
    _extend_report_errors(lines, "Doctor errors", doctor.errors)
    _extend_report_errors(lines, "Plan errors", plan.errors)
    _extend_font_summary(lines, plan)
    _extend_tool_summary(lines, doctor.extra)


def _group_entries(entries: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    groups: dict[str, list[dict[str, Any]]] = {
        "updates": [],
        "creates": [],
        "protected": [],
        "blocked": [],
    }
    for entry in entries:
        group = _entry_group(entry)
        if group:
            groups[group].append(entry)
    return groups


def _entry_group(entry: dict[str, Any]) -> str | None:
    # Fonts use install/needs-update/manual semantics, not file-drift, and are
    # rendered separately by _extend_font_summary; excluding them avoids
    # double-counting in _action_summary["file_changes"].
    if entry.get("recipe") == "fonts":
        return None
    state = entry.get("state")
    protected = bool(entry.get("protected"))
    if state == "drifted" and not protected:
        return "updates"
    if state == "missing" and not protected:
        return "creates"
    if state == "protected":
        return "protected"
    if state in {"invalid", "blocked"}:
        return "blocked"
    return None


def _extend_change_group(lines: list[str], title: str, entries: list[dict[str, Any]], manifest_entries: dict[str, ManifestEntry]) -> None:
    if not entries:
        return
    lines.extend(["", f"{title}:"])
    for entry in entries:
        target = _target_label(entry, manifest_entries)
        lines.append(f"  - {target}")


def _extend_manual_group(lines: list[str], entries: list[dict[str, Any]], manifest_entries: dict[str, ManifestEntry]) -> None:
    if not entries:
        return
    lines.extend(["", "Protected/manual files:"])
    for entry in entries:
        target = _target_label(entry, manifest_entries)
        reason = entry.get("manual_reason") or entry.get("reason") or "protected/manual item"
        lines.append(f"  - {target}: {reason}")


def _extend_blocking_group(lines: list[str], entries: list[dict[str, Any]], manifest_entries: dict[str, ManifestEntry]) -> None:
    if not entries:
        return
    lines.extend(["", "Needs attention before apply:"])
    for entry in entries:
        target = _target_label(entry, manifest_entries)
        lines.append(f"  - {target}: {entry.get('reason')}")


def _extend_report_errors(lines: list[str], title: str, errors: list[dict[str, Any] | str]) -> None:
    if not errors:
        return
    lines.extend(["", f"{title}:"])
    for error in errors:
        if isinstance(error, dict):
            message = error.get("message") or error
            entry = error.get("entry_id")
            prefix = f"{entry}: " if entry else ""
            lines.append(f"  - {prefix}{message}")
        else:
            lines.append(f"  - {error}")


def _extend_font_summary(lines: list[str], plan: Report) -> None:
    fonts, other_entries = _font_summary_items(plan)
    if not fonts and not other_entries:
        return

    actionable_ids = _actionable_font_ids(plan)
    groups = _font_summary_groups(fonts, other_entries, actionable_ids)
    lines.extend([
        "",
        "Fonts:",
        "  - Terminal configuration uses `Nerd Font Mono` faces, never Propo.",
    ])
    _extend_font_action_group(lines, "Nerd Fonts", groups["nerd"], actionable_ids)
    _extend_font_action_group(lines, "Apt fallback fonts", groups["apt"], actionable_ids)
    _extend_other_font_actions(lines, groups["other_actionable"])
    _extend_font_names(lines, "Already OK", groups["already_ok"])
    _extend_manual_font_items(lines, groups["manual_or_blocked"])


def _font_summary_items(plan: Report) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    fonts = list(plan.extra.get("fonts") or [])
    font_entries = [entry for entry in plan.entries if entry.get("recipe") == "fonts"]
    other_entries = [entry for entry in font_entries if entry.get("source_type") not in {"nerd_font_release", "apt_package"}]
    return fonts, other_entries


def _font_summary_groups(
    fonts: list[dict[str, Any]],
    other_entries: list[dict[str, Any]],
    actionable_ids: set[str],
) -> dict[str, list[dict[str, Any]]]:
    all_items = fonts + other_entries
    return {
        "nerd": _font_items_by_source(fonts, "nerd_font_release"),
        "apt": _font_items_by_source(fonts, "apt_package"),
        "already_ok": _font_items_by_state(all_items, {"installed", "current"}),
        "manual_or_blocked": _font_items_by_state(all_items, {"manual", "unsupported", "blocked", "invalid"}),
        "other_actionable": _other_actionable_fonts(other_entries, actionable_ids),
    }


def _font_items_by_source(items: list[dict[str, Any]], source_type: str) -> list[dict[str, Any]]:
    return [item for item in items if item.get("source_type") == source_type]


def _font_items_by_state(items: list[dict[str, Any]], states: set[str]) -> list[dict[str, Any]]:
    return [item for item in items if item.get("state") in states]


def _other_actionable_fonts(items: list[dict[str, Any]], actionable_ids: set[str]) -> list[dict[str, Any]]:
    return [item for item in items if _font_item_is_actionable(item, actionable_ids)]


def _font_item_is_actionable(item: dict[str, Any], actionable_ids: set[str]) -> bool:
    return item.get("entry_id") in actionable_ids or item.get("state") in {"missing", "needs_update"}


def _extend_other_font_actions(lines: list[str], other_actionable: list[dict[str, Any]]) -> None:
    if other_actionable:
        lines.append("  Other font actions:")
        for item in other_actionable:
            lines.append(f"    - {_font_item_line(item)}")


def _extend_font_names(lines: list[str], title: str, items: list[dict[str, Any]]) -> None:
    if not items:
        return
    lines.append(f"  {title}:")
    for item in items:
        lines.append(f"    - {_font_item_name(item)}")


def _extend_manual_font_items(lines: list[str], manual_or_blocked: list[dict[str, Any]]) -> None:
    if manual_or_blocked:
        lines.append("  Manual/skipped:")
        for item in manual_or_blocked:
            lines.append(f"    - {_font_item_line(item, show_reason=True)}")


def _extend_font_action_group(
    lines: list[str],
    title: str,
    items: list[dict[str, Any]],
    actionable_ids: set[str],
) -> None:
    if not items:
        return
    actionable = [
        item
        for item in items
        if item.get("entry_id") in actionable_ids or item.get("state") in {"missing", "needs_update"}
    ]
    lines.append(f"  {title}:")
    if not actionable:
        lines.append("    - none to install/update")
        return
    for item in actionable:
        lines.append(f"    - {_font_item_line(item)}")


def _extend_tool_summary(lines: list[str], extra: dict[str, Any]) -> None:
    tool_checks = extra.get("tool_checks") or []
    auth_guidance = extra.get("auth_guidance") or []
    if not tool_checks and not auth_guidance:
        return

    lines.extend(["", "Tools and auth:"])
    _extend_tool_check_lines(lines, tool_checks)
    _extend_auth_summary_line(lines, auth_guidance)


def _extend_tool_check_lines(lines: list[str], tool_checks: list[dict[str, Any]]) -> None:
    missing = [item for item in tool_checks if item.get("state") == "missing"]
    if not missing:
        lines.append(f"  - All {len(tool_checks)} baseline tools are visible on PATH.")
        return
    lines.append("  - Missing tools:")
    for item in missing:
        lines.append(f"    {item.get('command')}: {item.get('install_hint')}")


def _append_pending_auth_line(lines: list[str], pending: list[dict[str, Any]], signed_in: list[dict[str, Any]]) -> None:
    if pending:
        commands = ", ".join(str(item.get("command")) for item in pending)
        lines.append(f"  - Auth checks are manual: {commands}.")
    elif not signed_in:
        lines.append("  - No auth guidance items applicable.")


def _extend_auth_summary_line(lines: list[str], auth_guidance: list[dict[str, Any]]) -> None:
    pending, signed_in = _partition_auth_guidance(auth_guidance)
    _append_signed_in_line(lines, signed_in)
    _append_pending_auth_line(lines, pending, signed_in)


def _auth_identity_label(item: dict[str, Any]) -> str:
    detail = item.get("signed_in_detail")
    if detail:
        return f"{item.get('id')}={detail}"
    return str(item.get("id"))


def _target_label(entry: dict[str, Any], manifest_entries: dict[str, ManifestEntry]) -> str:
    manifest_entry = manifest_entries.get(str(entry.get("entry_id")))
    if manifest_entry:
        return _home_label(manifest_entry.target)
    return str(entry.get("target", ""))


def _home_label(target: str) -> str:
    return "~" if target in {"", "."} else f"~/{target}"


def _action_summary(doctor: Report, plan: Report, groups: dict[str, list[dict[str, Any]]]) -> dict[str, int | bool]:
    actionable_font_ids = _actionable_font_ids(plan)
    font_entries = [entry for entry in plan.entries if entry.get("recipe") == "fonts"]
    nerd_actions, apt_actions, other_font_actions = _font_action_counts(plan, font_entries, actionable_font_ids)

    return {
        "file_changes": len(groups["updates"]) + len(groups["creates"]),
        "backups": len(groups["updates"]),
        "font_actions": len(actionable_font_ids),
        "nerd_actions": nerd_actions,
        "apt_actions": apt_actions,
        "other_font_actions": other_font_actions,
        "manual_fonts": _manual_font_count(font_entries),
        "blockers": len(groups["blocked"]) + len(doctor.errors) + len(plan.errors),
        "requires_network": _has_actionable_operation(plan.operations, "requires_network"),
        "requires_sudo": _has_actionable_operation(plan.operations, "requires_sudo"),
        "requires_apt_sudo": _has_apt_sudo_operation(plan.operations),
    }


def _font_action_counts(
    plan: Report,
    font_entries: list[dict[str, Any]],
    actionable_font_ids: set[str],
) -> tuple[int, int, int]:
    source_types = {str(entry.get("entry_id")): entry.get("source_type") for entry in font_entries}
    counts = {"nerd_font_release": 0, "apt_package": 0, "other": 0}
    for entry_id in actionable_font_ids:
        source_type = _font_source_type(entry_id, source_types, plan.operations)
        bucket = source_type if source_type in {"nerd_font_release", "apt_package"} else "other"
        counts[bucket] += 1
    return counts["nerd_font_release"], counts["apt_package"], counts["other"]


def _manual_font_count(font_entries: list[dict[str, Any]]) -> int:
    return sum(1 for entry in font_entries if entry.get("state") in {"manual", "unsupported"})


def _has_actionable_operation(operations: list[dict[str, Any]], flag: str) -> bool:
    return any(_is_actionable_operation(op) and op.get(flag) for op in operations)


def _has_apt_sudo_operation(operations: list[dict[str, Any]]) -> bool:
    return any(_is_actionable_operation(op) and op.get("type") == "font_install_packages" and op.get("requires_sudo") for op in operations)


def _file_change_sentence(updates: int, creates: int, backups: int) -> str:
    parts: list[str] = []
    if updates:
        backup_text = f" with {_plural(backups, 'backup')}" if backups else ""
        parts.append(f"update {_plural(updates, 'existing file')}{backup_text}")
    if creates:
        parts.append(f"create {_plural(creates, 'missing file')}")
    return " and ".join(parts).capitalize() + "."


def _font_action_sentence(action_summary: dict[str, int | bool]) -> str:
    parts: list[str] = []
    nerd = int(action_summary["nerd_actions"])
    apt = int(action_summary["apt_actions"])
    other = int(action_summary["other_font_actions"])
    if nerd:
        parts.append(_plural(nerd, "Nerd Font"))
    if apt:
        parts.append(_plural(apt, "apt fallback font package"))
    if other:
        parts.append(_plural(other, "host/system font action"))
    return ", ".join(parts) if parts else _plural(int(action_summary["font_actions"]), "font action")


def _actionable_font_ids(plan: Report) -> set[str]:
    return {
        str(op.get("entry_id"))
        for op in plan.operations
        if op.get("recipe") == "fonts" and _is_actionable_operation(op) and op.get("entry_id")
    }


def _is_actionable_operation(op: dict[str, Any]) -> bool:
    op_type = str(op.get("type", ""))
    return bool(op.get("requires_approval")) and op_type not in {"skip", "refuse", "font_skip", "font_manual"}


def _font_source_type(entry_id: str, source_types: dict[str, Any], operations: list[dict[str, Any]]) -> Any:
    if source_types.get(entry_id):
        return source_types[entry_id]
    for op in operations:
        if op.get("entry_id") == entry_id and op.get("source_type"):
            return op.get("source_type")
    if entry_id.startswith("fonts.apt."):
        return "apt_package"
    if entry_id.endswith("-nerd") or ".nerd" in entry_id:
        return "nerd_font_release"
    return None


def _font_item_line(item: dict[str, Any], *, show_reason: bool = False) -> str:
    bits = [_font_item_name(item) + f": {_font_state(item)}"]
    if item.get("requires_sudo"):
        bits.append("sudo")
    if item.get("source_type") == "nerd_font_release" and item.get("state") in {"missing", "needs_update"}:
        bits.append("network if cache is missing")
    if show_reason and item.get("reason"):
        bits.append(str(item["reason"]))
    if len(bits) == 1:
        return bits[0]
    return f"{bits[0]} ({'; '.join(bits[1:])})"


def _font_item_name(item: dict[str, Any]) -> str:
    label = str(item.get("label") or item.get("family") or item.get("entry_id") or "font item")
    package = item.get("package")
    if item.get("source_type") == "apt_package" and package:
        return f"{label} [{package}]"
    return label


def _font_state(item: dict[str, Any]) -> str:
    state = str(item.get("state") or "unknown")
    return {
        "needs_update": "needs update",
        "installed": "already OK",
        "current": "already OK",
        "manual": "manual check needed",
        "unsupported": "skipped here",
        "invalid": "blocked",
    }.get(state, state)


def _plural(count: int, singular: str) -> str:
    suffix = "" if count == 1 else "s"
    return f"{count} {singular}{suffix}"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="dotfiles_tools.machine_summary")
    parser.add_argument("--repo", required=True)
    parser.add_argument("--home", required=True)
    parser.add_argument("--profile", default="machine")
    parser.add_argument("--menu-mode", action="store_true")
    parser.add_argument("--missing-tool-count", action="store_true")
    parser.add_argument("--recommendation", action="store_true")
    args = parser.parse_args(argv)
    if args.menu_mode:
        print(render_menu_mode(args.repo, args.home))
    elif args.missing_tool_count:
        print(render_missing_tool_count(args.repo, args.home))
    elif args.recommendation:
        repo_path = Path(args.repo).resolve()
        home_path = Path(args.home).resolve()
        doctor = run_doctor(repo_path, home_path, profile=args.profile)
        plan = build_bootstrap_plan(repo_path, home_path, profile=args.profile)
        groups = _group_entries(plan.entries)
        action_summary = _action_summary(doctor, plan, groups)
        recommendation = _recommendation(doctor, plan, action_summary, groups)
        print(
            f"{recommendation.option_number}\t{recommendation.label}\t{recommendation.reason}\t{recommendation.state_category}"
        )
    else:
        print(render_machine_summary(args.repo, args.home, profile=args.profile), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
