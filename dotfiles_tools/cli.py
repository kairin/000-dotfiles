from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from .bootstrap import (
    apply_bootstrap,
    apply_tool_installs,
    build_bootstrap_plan,
    build_tool_install_subplan,
    run_tool_install_post_install,
)
from .codacy_rollout import (
    CodacyApiClient,
    GitHubCliClient,
    audit_inventory,
    audit_repository,
    find_repository,
    load_inventory,
    plan_repository,
    render_audit_table,
)
from .doctor import run_doctor
from .installer import apply_plan, build_plan
from .project_init import init_project
from .reports import render


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="dotfiles_tools")
    subparsers = parser.add_subparsers(dest="command", required=True)
    _add_doctor_parser(subparsers)
    _add_plan_parser(subparsers)
    _add_apply_parser(subparsers)
    _add_bootstrap_plan_parser(subparsers)
    _add_bootstrap_apply_parser(subparsers)
    _add_install_tools_plan_parser(subparsers)
    _add_install_tools_apply_parser(subparsers)
    _add_install_tools_post_parser(subparsers)
    _add_init_project_parser(subparsers)
    _add_codacy_audit_parser(subparsers)
    _add_codacy_plan_parser(subparsers)
    return parser


def _add_doctor_parser(subparsers) -> None:
    doctor = subparsers.add_parser("doctor", help="Audit repository and target home without writing")
    _common(doctor)
    doctor.add_argument("--home", required=True)
    doctor.add_argument("--profile", default="machine")


def _add_plan_parser(subparsers) -> None:
    plan = subparsers.add_parser("plan", help="Print setup operations without writing")
    _common(plan)
    plan.add_argument("--home", required=True)
    plan.add_argument("--profile", default="machine")
    plan.add_argument("--include-protected", action="append", default=[])


def _add_apply_parser(subparsers) -> None:
    apply = subparsers.add_parser("apply", help="Apply setup operations with approval and backups")
    _common(apply)
    apply.add_argument("--home", required=True)
    apply.add_argument("--profile", default="machine")
    apply.add_argument("--backup-dir", required=True)
    apply.add_argument("--yes", action="store_true")
    apply.add_argument("--include-protected", action="append", default=[])


def _add_bootstrap_plan_parser(subparsers) -> None:
    bootstrap_plan = subparsers.add_parser(
        "bootstrap-plan",
        help="Print machine setup operations including install recipes",
    )
    _common(bootstrap_plan)
    bootstrap_plan.add_argument("--home", required=True)
    bootstrap_plan.add_argument("--profile", default="machine")
    bootstrap_plan.add_argument("--include-protected", action="append", default=[])


def _add_bootstrap_apply_parser(subparsers) -> None:
    bootstrap_apply = subparsers.add_parser(
        "bootstrap-apply",
        help="Apply machine setup operations and install recipes",
    )
    _common(bootstrap_apply)
    bootstrap_apply.add_argument("--home", required=True)
    bootstrap_apply.add_argument("--profile", default="machine")
    bootstrap_apply.add_argument("--backup-dir")
    bootstrap_apply.add_argument("--yes", action="store_true")
    bootstrap_apply.add_argument("--include-protected", action="append", default=[])


def _add_install_tools_plan_parser(subparsers) -> None:
    install_tools_plan = subparsers.add_parser(
        "bootstrap-install-tools-plan",
        help="Preview tool install/update actions for option 1",
    )
    _common(install_tools_plan)
    install_tools_plan.add_argument("--home", required=True)
    install_tools_plan.add_argument("--phase", choices=("all", "dev-base", "tools"), default="all")


def _add_install_tools_apply_parser(subparsers) -> None:
    install_tools_apply = subparsers.add_parser(
        "bootstrap-install-tools",
        help="Apply tool install/update actions (option 1)",
    )
    _common(install_tools_apply)
    install_tools_apply.add_argument("--home", required=True)
    install_tools_apply.add_argument("--backup-dir")
    install_tools_apply.add_argument("--yes", action="store_true")
    install_tools_apply.add_argument("--phase", choices=("all", "dev-base", "tools"), default="all")


def _add_install_tools_post_parser(subparsers) -> None:
    install_tools_post = subparsers.add_parser(
        "bootstrap-install-tools-post",
        help="Run tool verification and post-install actions",
    )
    _common(install_tools_post)
    install_tools_post.add_argument("--home", required=True)
    install_tools_post.add_argument("--backup-dir")
    install_tools_post.add_argument("--yes", action="store_true")
    install_tools_post.add_argument("--mode", choices=("all", "verify", "auto", "guidance"), default="all")


def _add_init_project_parser(subparsers) -> None:
    project = subparsers.add_parser("init-project", help="Initialize project-level agent docs")
    _common(project)
    project.add_argument("--project", required=True)
    project.add_argument("--vars", required=True)
    project.add_argument("--backup-dir")
    project.add_argument("--yes", action="store_true")
    project.add_argument("--copilot", action="store_true")


def _add_codacy_audit_parser(subparsers) -> None:
    codacy_audit = subparsers.add_parser("codacy-audit", help="Audit Codacy rollout readiness")
    _common(codacy_audit)
    codacy_audit.add_argument("--inventory", required=True)
    codacy_audit.add_argument("--target-repo")
    codacy_audit.add_argument("--project")
    codacy_audit.add_argument("--all", action="store_true")


def _add_codacy_plan_parser(subparsers) -> None:
    codacy_plan = subparsers.add_parser("codacy-plan", help="Print read-only Codacy rollout plan")
    _common(codacy_plan)
    codacy_plan.add_argument("--inventory", required=True)
    codacy_plan.add_argument("--target-repo", required=True)


def _common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--repo", required=True)
    parser.add_argument("--json", action="store_true", dest="as_json")


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command in {"codacy-audit", "codacy-plan"}:
        return _dispatch_codacy_command(args)
    report = _dispatch_command(args, Path(args.repo))
    print(render(report, args.as_json), end="")
    return 1 if report.status in {"failed", "partial"} else 0


def _dispatch_command(args: argparse.Namespace, repo: Path):
    cmd = args.command
    if cmd == "doctor":
        report = run_doctor(repo, args.home, profile=args.profile)
    elif cmd == "plan":
        report = build_plan(
            repo, args.home, profile=args.profile, include_protected=args.include_protected
        )
    elif cmd == "apply":
        report = apply_plan(
            repo, args.home,
            profile=args.profile, backup_dir=args.backup_dir,
            yes=args.yes, include_protected=args.include_protected,
        )
    elif cmd == "init-project":
        report = init_project(
            repo, args.project, args.vars,
            backup_dir=args.backup_dir, yes=args.yes, copilot=args.copilot,
        )
    elif cmd.startswith("bootstrap"):
        report = _dispatch_bootstrap(args, repo)
    else:
        raise SystemExit(f"unknown command: {cmd}")
    return report


def _dispatch_codacy_command(args: argparse.Namespace) -> int:
    dispatchers = {
        "codacy-plan": _cmd_codacy_plan,
        "codacy-audit": _cmd_codacy_audit,
    }
    handler = dispatchers.get(args.command)
    if handler is None:
        raise SystemExit(f"unknown codacy command: {args.command}")
    return handler(args)


def _cmd_codacy_plan(args: argparse.Namespace) -> int:
    inventory = load_inventory(Path(args.inventory))
    item = find_repository(inventory, repo=args.target_repo)
    output = plan_repository(item)
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


def _cmd_codacy_audit(args: argparse.Namespace) -> int:
    inventory = load_inventory(Path(args.inventory))
    github = GitHubCliClient()
    codacy = CodacyApiClient()
    if args.all:
        return _run_codacy_audit_all(args, inventory, github, codacy)
    return _run_codacy_audit_single(args, inventory, github, codacy)


def _run_codacy_audit_all(
    args: argparse.Namespace, inventory, github, codacy
) -> int:
    results = audit_inventory(inventory, github, codacy)
    if args.as_json:
        print(json.dumps([result.to_dict() for result in results], indent=2, sort_keys=True))
    else:
        print(render_audit_table(results), end="")
    return 1 if any(result.status == "FAIL" for result in results) else 0


def _run_codacy_audit_single(
    args: argparse.Namespace, inventory, github, codacy
) -> int:
    item = find_repository(
        inventory,
        repo=args.target_repo,
        project=Path(args.project) if args.project else None,
    )
    result = audit_repository(item, github, codacy)
    if args.as_json:
        print(json.dumps(result.to_dict(), indent=2, sort_keys=True))
    else:
        print(result.to_text(), end="")
    return 1 if result.status == "FAIL" else 0


def _dispatch_bootstrap(args: argparse.Namespace, repo: Path):
    cmd = args.command
    if cmd == "bootstrap-plan":
        report = build_bootstrap_plan(
            repo, args.home, profile=args.profile, include_protected=args.include_protected
        )
    elif cmd == "bootstrap-apply":
        report = apply_bootstrap(
            repo, args.home,
            profile=args.profile, backup_dir=args.backup_dir,
            yes=args.yes, include_protected=args.include_protected,
        )
    elif cmd == "bootstrap-install-tools-plan":
        report = build_tool_install_subplan(repo, args.home, phase=args.phase)
    elif cmd == "bootstrap-install-tools":
        report = apply_tool_installs(
            repo, args.home, phase=args.phase, backup_dir=args.backup_dir, yes=args.yes
        )
    elif cmd == "bootstrap-install-tools-post":
        report = run_tool_install_post_install(
            repo, args.home, mode=args.mode, backup_dir=args.backup_dir, yes=args.yes
        )
    else:
        raise SystemExit(f"unknown command: {cmd}")
    return report
