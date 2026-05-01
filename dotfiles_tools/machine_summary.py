from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Sequence

from .bootstrap import build_bootstrap_plan
from .doctor import run_doctor
from .manifest import ManifestEntry, ManifestError, load_manifest
from .reports import Report


def render_machine_summary(repo: Path | str, home: Path | str, *, profile: str = "machine") -> str:
    repo_path = Path(repo).resolve()
    home_path = Path(home).resolve()
    doctor = run_doctor(repo_path, home_path, profile=profile)
    plan = build_bootstrap_plan(repo_path, home_path, profile=profile)
    return render_reports(doctor, plan, repo_path, home_path, profile=profile)


def render_menu_label(repo: Path | str, home: Path | str, *, profile: str = "machine") -> str:
    repo_path = Path(repo).resolve()
    home_path = Path(home).resolve()
    plan = build_bootstrap_plan(repo_path, home_path, profile=profile)
    groups = _group_entries(plan.entries)
    return _option_one_label(plan, groups)


def render_reports(doctor: Report, plan: Report, repo: Path, home: Path, *, profile: str = "machine") -> str:
    groups = _group_entries(plan.entries)
    action_summary = _action_summary(doctor, plan, groups)
    manifest_entries = _manifest_entry_map(repo)
    lines = _summary_header(repo, home, profile)
    _extend_option_decision(lines, action_summary, groups)
    _extend_report_sections(lines, doctor, plan, groups, manifest_entries)
    lines.extend([
        "",
        "Full details: choose option 2 for cache paths, versions, package candidates, terminal faces, host actions, and raw operations.",
    ])
    return "\n".join(lines) + "\n"


def _manifest_entry_map(repo: Path) -> dict[str, ManifestEntry]:
    try:
        return load_manifest(repo).entry_map()
    except ManifestError:
        return {}


def _summary_header(repo: Path, home: Path, profile: str) -> list[str]:
    return [
        "Machine setup summary",
        f"Repo: {repo}",
        f"Home: {home}",
        f"Profile: {profile}",
        "",
        "Option 1 will:",
    ]


def _extend_option_decision(
    lines: list[str],
    action_summary: dict[str, int | bool],
    groups: dict[str, list[dict[str, Any]]],
) -> None:
    _extend_file_decision(lines, action_summary, groups)
    _extend_font_decision(lines, action_summary)
    _extend_requirement_decisions(lines, action_summary)
    _extend_skip_decisions(lines, action_summary, groups)
    lines.append("  - Nothing changes until you choose option 1.")


def _extend_file_decision(
    lines: list[str],
    action_summary: dict[str, int | bool],
    groups: dict[str, list[dict[str, Any]]],
) -> None:
    if not action_summary["file_changes"]:
        lines.append("  - Apply no file changes; all non-protected targets are current.")
        return
    sentence = _file_change_sentence(len(groups["updates"]), len(groups["creates"]), action_summary["backups"])
    lines.append("  - " + sentence)


def _extend_font_decision(lines: list[str], action_summary: dict[str, int | bool]) -> None:
    if action_summary["font_actions"]:
        lines.append("  - Install/update " + _font_action_sentence(action_summary) + ".")
    else:
        lines.append("  - Run no font install/update actions.")


def _extend_requirement_decisions(lines: list[str], action_summary: dict[str, int | bool]) -> None:
    if action_summary["requires_network"]:
        lines.append("  - Network may be used for Nerd Font downloads unless cached.")
    if action_summary["requires_apt_sudo"]:
        lines.append("  - sudo is needed for apt fallback font packages.")
    elif action_summary["requires_sudo"]:
        lines.append("  - sudo is needed for host/system font actions.")


def _extend_skip_decisions(
    lines: list[str],
    action_summary: dict[str, int | bool],
    groups: dict[str, list[dict[str, Any]]],
) -> None:
    if groups["protected"]:
        lines.append(f"  - Leave {_plural(len(groups['protected']), 'protected/manual file')} untouched.")
    if action_summary["manual_fonts"]:
        lines.append(f"  - Skip {_plural(action_summary['manual_fonts'], 'manual/unsupported font item')}; see Fonts below.")
    if action_summary["blockers"]:
        lines.append(f"  - Stop on {_plural(action_summary['blockers'], 'blocking issue')}; fix before applying.")


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


def _extend_auth_summary_line(lines: list[str], auth_guidance: list[dict[str, Any]]) -> None:
    commands = ", ".join(str(item.get("command")) for item in auth_guidance if item.get("state") == "available")
    if commands:
        lines.append(f"  - Auth checks are manual: {commands}.")


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


def _option_one_label(plan: Report, groups: dict[str, list[dict[str, Any]]]) -> str:
    action_summary = _action_summary(
        Report("doctor", "ok", plan.repo, home=plan.home, profile=plan.profile),
        plan,
        groups,
    )
    file_changes = int(action_summary["file_changes"])
    font_actions = int(action_summary["font_actions"])
    label = _option_base_label(file_changes, font_actions)
    details = _option_label_details(action_summary)
    if details:
        label += f" ({'; '.join(details)})"
    return label


def _option_base_label(file_changes: int, font_actions: int) -> str:
    if file_changes and font_actions:
        return f"Apply {_plural(file_changes, 'file change')} + {_plural(font_actions, 'font action')}"
    if file_changes:
        return f"Apply {_plural(file_changes, 'file change')}"
    if font_actions:
        return f"Apply {_plural(font_actions, 'font action')}"
    return "Apply safe changes"


def _option_label_details(action_summary: dict[str, int | bool]) -> list[str]:
    details: list[str] = []
    backups = int(action_summary["backups"])
    if backups:
        details.append(f"backs up {_plural(backups, 'file')}")
    _extend_sudo_label_details(details, action_summary)
    if action_summary["requires_network"]:
        details.append("network may be used for Nerd Fonts")
    return details


def _extend_sudo_label_details(details: list[str], action_summary: dict[str, int | bool]) -> None:
    if action_summary["requires_apt_sudo"]:
        details.append("sudo needed for apt fonts")
    elif action_summary["requires_sudo"]:
        details.append("sudo needed")


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
    parser.add_argument("--menu-label", action="store_true")
    args = parser.parse_args(argv)
    if args.menu_label:
        print(render_menu_label(args.repo, args.home, profile=args.profile))
    else:
        print(render_machine_summary(args.repo, args.home, profile=args.profile), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
