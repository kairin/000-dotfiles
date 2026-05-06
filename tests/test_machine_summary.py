from __future__ import annotations

from pathlib import Path

from unittest import mock

from dotfiles_tools.machine_summary import (
    _action_summary,
    _group_entries,
    _recommendation,
    render_menu_mode,
    render_missing_tool_count,
    render_reports,
)
from dotfiles_tools.reports import Report
from tests.helpers import DotfilesTestCase, REPO_ROOT


def doctor(
    home: Path,
    *,
    errors: list[dict[str, str] | str] | None = None,
    tool_checks: list[dict[str, str]] | None = None,
    auth_guidance: list[dict[str, str]] | None = None,
) -> Report:
    return Report(
        "doctor",
        "warning",
        str(REPO_ROOT),
        home=str(home),
        profile="machine",
        errors=errors or [],
        extra={
            "tool_checks": tool_checks or [],
            "auth_guidance": auth_guidance or [],
        },
    )


def plan(
    home: Path,
    *,
    entries: list[dict] | None = None,
    operations: list[dict] | None = None,
    fonts: list[dict] | None = None,
    errors: list[dict[str, str] | str] | None = None,
) -> Report:
    return Report(
        "bootstrap-plan",
        "warning",
        str(REPO_ROOT),
        home=str(home),
        profile="machine",
        entries=entries or [],
        operations=operations or [],
        errors=errors or [],
        extra={"fonts": fonts or []},
    )


def manifest_entry(entry_id: str, state: str, *, protected: bool = False, reason: str = "target differs") -> dict:
    entry = {
        "entry_id": entry_id,
        "state": state,
        "protected": protected,
        "reason": reason,
    }
    if protected:
        entry["manual_reason"] = reason
    return entry


def nerd_font(state: str = "missing") -> dict:
    return {
        "entry_id": "fonts.jetbrains-mono-nerd",
        "label": "JetBrainsMono Nerd Font",
        "source_type": "nerd_font_release",
        "state": state,
        "requires_sudo": False,
        "reason": "font files are not installed",
        "cache_path": "cache/JetBrainsMono.zip",
        "target": "home/.local/share/fonts/JetBrainsMonoNerdFont",
        "terminal_face": "JetBrainsMono Nerd Font Mono",
        "terminal_impact": "Local terminals can select a Mono face.",
    }


def apt_font(state: str = "missing", *, package: str = "fonts-noto-color-emoji") -> dict:
    return {
        "entry_id": f"fonts.apt.{package.removeprefix('fonts-')}",
        "label": "Noto Color Emoji",
        "source_type": "apt_package",
        "package": package,
        "state": state,
        "requires_sudo": state in {"missing", "needs_update"},
        "reason": "apt package is not installed",
        "candidate_version": "1.0",
        "target": package,
        "terminal_face": "Noto Color Emoji",
        "terminal_impact": "Emoji fallback for terminals.",
    }


def font_entry(item: dict) -> dict:
    return {
        "entry_id": item["entry_id"],
        "source_type": item["source_type"],
        "family": item.get("label"),
        "state": item["state"],
        "recipe": "fonts",
        "requires_sudo": item.get("requires_sudo", False),
        "reason": item.get("reason", ""),
    }


class MachineSummaryTests(DotfilesTestCase):
    def render(self, plan_report: Report, *, doctor_report: Report | None = None) -> str:
        home = Path(plan_report.home or self.make_home())
        return render_reports(doctor_report or doctor(home), plan_report, REPO_ROOT, home)

    def test_summary_groups_changes_without_raw_diagnostic_dump(self) -> None:
        home = self.make_home()
        fonts = [nerd_font("missing"), apt_font("missing")]
        plan_report = plan(
            home,
            entries=[
                manifest_entry("claude.settings", "drifted"),
                manifest_entry("codex.config", "missing"),
                manifest_entry("git.config", "protected", protected=True, reason="Git config contains committer identity."),
                *(font_entry(item) for item in fonts),
            ],
            operations=[
                {"entry_id": "fonts.jetbrains-mono-nerd", "type": "font_download", "recipe": "fonts", "requires_approval": True, "requires_network": True},
                {"entry_id": "fonts.apt.noto-color-emoji", "type": "font_install_packages", "recipe": "fonts", "requires_approval": True, "requires_sudo": True, "source_type": "apt_package"},
            ],
            fonts=fonts,
        )

        text = self.render(plan_report)

        self.assertIn("Machine setup summary", text)
        self.assertIn("Recommended next step: 2. Apply safe non-protected dotfiles - Safe non-protected setup changes are pending.", text)
        self.assertIn("Update existing files with backups:", text)
        self.assertIn("~/.claude/settings.json", text)
        self.assertIn("Create missing files:", text)
        self.assertIn("~/.codex/config.toml", text)
        self.assertIn("Protected/manual files:", text)
        self.assertIn("~/.config/git/config: Git config contains committer identity.", text)
        self.assertIn("Fonts:", text)
        self.assertIn("Nerd Fonts:", text)
        self.assertIn("JetBrainsMono Nerd Font: missing", text)
        self.assertIn("Apt fallback fonts:", text)
        self.assertIn("Noto Color Emoji [fonts-noto-color-emoji]: missing", text)
        self.assertIn("Terminal configuration uses `Nerd Font Mono` faces, never Propo.", text)
        self.assertIn("Full details: choose option 3", text)
        self.assertNotIn("<- repo/", text)
        self.assertNotIn("entries:", text)
        self.assertNotIn("operations:", text)
        self.assertNotIn("cache:", text)
        self.assertNotIn("version:", text)
        self.assertNotIn("terminal face:", text)
        self.assertNotIn("terminal impact:", text)

    def test_incomplete_audit_recommends_details(self) -> None:
        home = self.make_home()
        plan_report = plan(home, errors=[{"message": "manifest parse failed"}])

        text = self.render(plan_report, doctor_report=doctor(home))

        self.assertIn("Recommended next step: 3. Show full technical details - The audit is incomplete.", text)
        self.assertIn("The audit is incomplete; inspect the full technical details.", text)
        self.assertIn("Plan errors:", text)
        self.assertIn("manifest parse failed", text)

    def test_missing_tools_recommend_install_first(self) -> None:
        home = self.make_home()
        plan_report = plan(home)
        doctor_report = doctor(
            home,
            tool_checks=[
                {"command": "gh", "state": "missing", "install_hint": "install gh"},
                {"command": "uv", "state": "available", "install_hint": ""},
            ],
        )

        text = self.render(plan_report, doctor_report=doctor_report)

        self.assertIn("Recommended next step: 1. Install / update developer tools - Developer tools should be installed or updated first.", text)
        self.assertIn("1 developer tools are missing or unverified.", text)
        self.assertIn("gh: install gh", text)

    def test_auth_guidance_recommends_sign_in_help(self) -> None:
        home = self.make_home()
        plan_report = plan(home)
        doctor_report = doctor(
            home,
            auth_guidance=[
                {"command": "gh auth status", "state": "available", "guidance": "gh auth status"},
            ],
        )

        text = self.render(plan_report, doctor_report=doctor_report)

        self.assertIn("Recommended next step: 4. Show tool and sign-in guidance - Sign-in guidance is the useful next step.", text)
        self.assertIn("Pending sign-ins: gh auth status.", text)

    def test_current_setup_recommends_exit(self) -> None:
        home = self.make_home()
        plan_report = plan(home)

        text = self.render(plan_report)

        self.assertIn("Recommended next step: 5. Exit without writing - Setup is current and no write action is needed.", text)
        self.assertIn("Setup is current and no write action is needed.", text)

    def test_all_fonts_ok_collapses_to_already_ok(self) -> None:
        home = self.make_home()
        fonts = [nerd_font("installed"), apt_font("installed")]
        plan_report = plan(home, entries=[font_entry(item) for item in fonts], fonts=fonts)

        text = self.render(plan_report)

        self.assertIn("Recommended next step: 5. Exit without writing - Setup is current and no write action is needed.", text)
        self.assertIn("Nerd Fonts:", text)
        self.assertIn("Apt fallback fonts:", text)
        self.assertIn("none to install/update", text)
        self.assertIn("Already OK:", text)
        self.assertIn("JetBrainsMono Nerd Font", text)
        self.assertIn("Noto Color Emoji [fonts-noto-color-emoji]", text)

    def test_nerd_font_missing_shows_network_need_without_cache_metadata(self) -> None:
        home = self.make_home()
        fonts = [nerd_font("missing")]
        plan_report = plan(
            home,
            entries=[font_entry(fonts[0])],
            operations=[
                {"entry_id": "fonts.jetbrains-mono-nerd", "type": "font_download", "recipe": "fonts", "requires_approval": True, "requires_network": True},
            ],
            fonts=fonts,
        )

        text = self.render(plan_report)

        self.assertIn("Install/update 1 Nerd Font.", text)
        self.assertIn("Network may be used for Nerd Font downloads unless cached.", text)
        self.assertIn("JetBrainsMono Nerd Font: missing (network if cache is missing)", text)
        self.assertNotIn("cache/JetBrainsMono.zip", text)

    def test_apt_font_missing_shows_sudo_need(self) -> None:
        home = self.make_home()
        fonts = [apt_font("missing")]
        plan_report = plan(
            home,
            entries=[font_entry(fonts[0])],
            operations=[
                {"entry_id": "fonts.apt.noto-color-emoji", "type": "font_install_packages", "recipe": "fonts", "requires_approval": True, "requires_sudo": True, "source_type": "apt_package"},
            ],
            fonts=fonts,
        )

        text = self.render(plan_report)

        self.assertIn("Install/update 1 apt fallback font package.", text)
        self.assertIn("sudo is needed for apt fallback font packages.", text)
        self.assertIn("Noto Color Emoji [fonts-noto-color-emoji]: missing (sudo)", text)
        self.assertNotIn("candidate_version", text)
        self.assertNotIn("1.0", text)

    def test_blockers_and_manual_fonts_stay_visible(self) -> None:
        home = self.make_home()
        manual_font = nerd_font("manual")
        blocked_entry = manifest_entry("claude.settings", "blocked", reason="target is a directory")
        plan_report = plan(
            home,
            entries=[blocked_entry, font_entry(manual_font)],
            fonts=[manual_font],
            errors=[{"message": "manifest parse failed"}],
        )

        text = self.render(plan_report, doctor_report=doctor(home, errors=[{"message": "doctor failed"}]))

        self.assertIn("Recommended next step: 3. Show full technical details - The audit is incomplete.", text)
        self.assertIn("The audit is incomplete; inspect the full technical details.", text)
        self.assertIn("Manual/skipped:", text)
        self.assertIn("JetBrainsMono Nerd Font: manual check needed", text)
        self.assertIn("Needs attention before apply:", text)
        self.assertIn("~/.claude/settings.json: target is a directory", text)
        self.assertIn("Doctor errors:", text)
        self.assertIn("doctor failed", text)
        self.assertIn("Plan errors:", text)
        self.assertIn("manifest parse failed", text)
        self.assertIn("Manual/skipped:", text)
        self.assertIn("JetBrainsMono Nerd Font: manual check needed", text)

    def test_menu_mode_returns_tools_missing_when_any_bootstrap_tool_absent(self) -> None:
        home = self.make_home()
        # Empty PATH means no bootstrap tool is detected on the user's machine
        # (linux platform forced so the plan emits real entries, not "unsupported").
        with mock.patch.dict("os.environ", {"PATH": "", "DOTFILES_TOOL_PLATFORM": "linux"}, clear=False):
            mode = render_menu_mode(REPO_ROOT, home)
            count = render_missing_tool_count(REPO_ROOT, home)
        self.assertEqual(mode, "tools_missing")
        self.assertGreater(count, 0)

    def test_fonts_entries_excluded_from_file_change_groups(self) -> None:
        nerd = nerd_font("missing")
        apt = apt_font("missing")
        entries = [
            manifest_entry("claude.settings", "drifted"),
            manifest_entry("codex.config", "missing"),
            font_entry(nerd),
            font_entry(apt),
        ]

        groups = _group_entries(entries)

        font_ids = {nerd["entry_id"], apt["entry_id"]}
        for bucket in ("updates", "creates", "protected", "blocked"):
            bucket_ids = {entry.get("entry_id") for entry in groups[bucket]}
            self.assertFalse(
                bucket_ids & font_ids,
                f"font entries leaked into groups[{bucket!r}]: {bucket_ids & font_ids}",
            )
        self.assertNotIn("fonts", groups)
        self.assertEqual({entry["entry_id"] for entry in groups["updates"]}, {"claude.settings"})
        self.assertEqual({entry["entry_id"] for entry in groups["creates"]}, {"codex.config"})

    def test_recommendation_falls_through_to_current_when_nothing_pending(self) -> None:
        home = self.make_home()
        plan_report = plan(home)
        doctor_report = doctor(home)
        groups = _group_entries(plan_report.entries)
        action_summary = _action_summary(doctor_report, plan_report, groups)

        rec = _recommendation(doctor_report, plan_report, action_summary, groups)

        self.assertEqual(rec.option_number, 5)
        self.assertEqual(rec.state_category, "current")
        self.assertEqual(rec.label, "Exit without writing")

    def test_menu_mode_returns_tools_present_when_platform_unsupported(self) -> None:
        home = self.make_home()
        # Forcing darwin makes every tool entry "unsupported", so nothing is
        # "missing" — this is also the behaviour every test exercises through
        # env_for in test_setup_script.py.
        with mock.patch.dict("os.environ", {"DOTFILES_TOOL_PLATFORM": "darwin"}, clear=False):
            mode = render_menu_mode(REPO_ROOT, home)
            count = render_missing_tool_count(REPO_ROOT, home)
        self.assertEqual(mode, "tools_present")
        self.assertEqual(count, 0)
