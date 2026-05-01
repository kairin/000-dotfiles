from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from .doctor import run_doctor
from .installer import apply_plan, build_plan
from .project_init import init_project
from .reports import render


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="dotfiles_tools")
    subparsers = parser.add_subparsers(dest="command", required=True)

    doctor = subparsers.add_parser("doctor", help="Audit repository and target home without writing")
    _common(doctor)
    doctor.add_argument("--home", required=True)
    doctor.add_argument("--profile", default="machine")

    plan = subparsers.add_parser("plan", help="Print setup operations without writing")
    _common(plan)
    plan.add_argument("--home", required=True)
    plan.add_argument("--profile", default="machine")
    plan.add_argument("--include-protected", action="append", default=[])

    apply = subparsers.add_parser("apply", help="Apply setup operations with approval and backups")
    _common(apply)
    apply.add_argument("--home", required=True)
    apply.add_argument("--profile", default="machine")
    apply.add_argument("--backup-dir", required=True)
    apply.add_argument("--yes", action="store_true")
    apply.add_argument("--include-protected", action="append", default=[])

    project = subparsers.add_parser("init-project", help="Initialize project-level agent docs")
    _common(project)
    project.add_argument("--project", required=True)
    project.add_argument("--vars", required=True)
    project.add_argument("--backup-dir")
    project.add_argument("--yes", action="store_true")
    project.add_argument("--copilot", action="store_true")
    return parser


def _common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--repo", required=True)
    parser.add_argument("--json", action="store_true", dest="as_json")


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    repo = Path(args.repo)
    if args.command == "doctor":
        report = run_doctor(repo, args.home, profile=args.profile)
    elif args.command == "plan":
        report = build_plan(repo, args.home, profile=args.profile, include_protected=args.include_protected)
    elif args.command == "apply":
        report = apply_plan(repo, args.home, profile=args.profile, backup_dir=args.backup_dir, yes=args.yes, include_protected=args.include_protected)
    elif args.command == "init-project":
        report = init_project(repo, args.project, args.vars, backup_dir=args.backup_dir, yes=args.yes, copilot=args.copilot)
    else:
        parser.error(f"unknown command: {args.command}")
    print(render(report, args.as_json), end="")
    return 1 if report.status in {"failed", "partial"} else 0
