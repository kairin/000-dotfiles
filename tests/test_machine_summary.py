from __future__ import annotations

from pathlib import Path

from dotfiles_tools.machine_summary import render_menu_label, render_reports
from dotfiles_tools.reports import Report
from tests.helpers import DotfilesTestCase, REPO_ROOT


def doctor(home: Path, *, errors: list[dict[str, str] | str] | None = None) -> Report:
    return Report("doctor", "warning", str(REPO_ROOT), home=str(home), profile="machine", errors=errors or [])


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
        self.assertIn("Option 1 will:", text)
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
        self.assertIn("Full details: choose option 2", text)
        self.assertNotIn("<- repo/", text)
        self.assertNotIn("entries:", text)
        self.assertNotIn("operations:", text)
        self.assertNotIn("cache:", text)
        self.assertNotIn("version:", text)
        self.assertNotIn("terminal face:", text)
        self.assertNotIn("terminal impact:", text)

    def test_all_fonts_ok_collapses_to_already_ok(self) -> None:
        home = self.make_home()
        fonts = [nerd_font("installed"), apt_font("installed")]
        plan_report = plan(home, entries=[font_entry(item) for item in fonts], fonts=fonts)

        text = self.render(plan_report)

        self.assertIn("Run no font install/update actions.", text)
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

        self.assertIn("Stop on 3 blocking issues; fix before applying.", text)
        self.assertIn("Skip 1 manual/unsupported font item; see Fonts below.", text)
        self.assertIn("Needs attention before apply:", text)
        self.assertIn("~/.claude/settings.json: target is a directory", text)
        self.assertIn("Doctor errors:", text)
        self.assertIn("doctor failed", text)
        self.assertIn("Plan errors:", text)
        self.assertIn("manifest parse failed", text)
        self.assertIn("Manual/skipped:", text)
        self.assertIn("JetBrainsMono Nerd Font: manual check needed", text)

    def test_menu_label_is_dynamic_and_specific(self) -> None:
        home = self.make_home()
        drifted = home / ".claude" / "settings.json"
        drifted.parent.mkdir(parents=True)
        drifted.write_text('{"drift": true}')

        label = render_menu_label(REPO_ROOT, home)

        self.assertRegex(label, r"^Apply [0-9]+ file changes?( \+ [0-9]+ font actions?)?")
        self.assertIn("backs up 1 file", label)
