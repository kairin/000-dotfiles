from __future__ import annotations

import io
import subprocess
import zipfile
from pathlib import Path

from dotfiles_tools.font_catalog import NERD_FONT_CATALOG, EXPECTED_TTF
from dotfiles_tools.bootstrap import (
    WARNING_STATES,
    FAILED_STATES,
    _renumber_operations,
    _status,
    _has_manual_or_refused_work,
    _collect_post_install_backups,
    _execute_bootstrap_operations,
    build_bootstrap_plan,
    apply_bootstrap,
    build_tool_install_subplan,
    apply_tool_installs,
    run_tool_install_post_install,
)
from dotfiles_tools.reports import Report
from tests.helpers import DotfilesTestCase, REPO_ROOT


class FakeRunner:
    def __init__(self, *, which: dict[str, str] | None = None) -> None:
        self.which_map = which or {}
        self.installed_dpkg: set[str] = set()
        self.commands: list[list[str]] = []
        self.downloads: list[tuple[str, Path]] = []

    def which(self, command: str) -> str | None:
        return self.which_map.get(command)

    def fetch_json(self, url: str) -> dict:
        return {
            "tag_name": "v3.4.0",
            "assets": [
                {"name": item.asset_name, "browser_download_url": f"https://example/{item.asset_name}", "size": 12}
                for item in NERD_FONT_CATALOG
            ],
        }

    def download(self, url: str, target: Path) -> None:
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.suffix.lower() == ".zip":
            buf = io.BytesIO()
            with zipfile.ZipFile(buf, "w") as zf:
                zf.writestr(EXPECTED_TTF, b"fake-font-bytes")
            target.write_bytes(buf.getvalue())
        else:
            target.write_text("-----BEGIN PGP PUBLIC KEY BLOCK-----\nfake\n")
        self.downloads.append((url, target))

    def run(
        self,
        args: list[str],
        *,
        capture_output: bool = False,
        check: bool = True,
        timeout: float | None = None,
    ) -> subprocess.CompletedProcess[str]:
        self.commands.append(list(args))
        command = Path(args[0]).name if args else ""
        if command == "gpg" and "--output" in args:
            output = Path(args[args.index("--output") + 1])
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(b"dearmored-keyring")
            return subprocess.CompletedProcess(args, 0, stdout="", stderr="")
        if command == "dpkg-query":
            package = args[-1]
            if package in self.installed_dpkg:
                return subprocess.CompletedProcess(args, 0, stdout="install ok installed", stderr="")
            return subprocess.CompletedProcess(args, 1, stdout="", stderr="not installed")
        if command == "dpkg" and "--print-architecture" in args:
            return subprocess.CompletedProcess(args, 0, stdout="amd64\n", stderr="")
        if "--version" in args:
            return subprocess.CompletedProcess(args, 0, stdout="dummy 1.2.3\n", stderr="")
        return subprocess.CompletedProcess(args, 0, stdout="", stderr="")


class RenumberOperationsTests(DotfilesTestCase):
    def test_renumbers_from_one(self):
        ops = [{"operation_id": "op-099"}, {"operation_id": "op-007"}]
        _renumber_operations(ops)
        self.assertEqual(ops[0]["operation_id"], "op-001")
        self.assertEqual(ops[1]["operation_id"], "op-002")

    def test_empty_list_is_noop(self):
        ops: list = []
        _renumber_operations(ops)
        self.assertEqual(ops, [])


class StatusTests(DotfilesTestCase):
    def test_ok_when_no_entries_or_ops(self):
        self.assertEqual(_status([], [], []), "ok")

    def test_failed_when_errors_present(self):
        self.assertEqual(_status([], [], [{"message": "boom"}]), "failed")

    def test_failed_when_entry_has_failed_state(self):
        for state in FAILED_STATES:
            with self.subTest(state=state):
                self.assertEqual(_status([{"state": state}], [], []), "failed")

    def test_warning_when_operations_present(self):
        self.assertEqual(_status([], [{"type": "copy"}], []), "warning")

    def test_warning_when_entry_has_warning_state(self):
        for state in WARNING_STATES:
            with self.subTest(state=state):
                self.assertEqual(_status([{"state": state}], [], []), "warning")

    def test_failed_takes_precedence_over_warning(self):
        entries = [{"state": "invalid"}, {"state": "missing"}]
        self.assertEqual(_status(entries, [], []), "failed")


class HasManualOrRefusedWorkTests(DotfilesTestCase):
    def _report(self, ops=None, entries=None):
        return Report("cmd", "ok", "/repo", operations=ops or [], entries=entries or [])

    def test_false_when_nothing_special(self):
        self.assertFalse(_has_manual_or_refused_work(self._report()))

    def test_true_when_refuse_op(self):
        r = self._report(ops=[{"type": "refuse"}])
        self.assertTrue(_has_manual_or_refused_work(r))

    def test_true_when_font_manual_op(self):
        r = self._report(ops=[{"type": "font_manual"}])
        self.assertTrue(_has_manual_or_refused_work(r))

    def test_true_when_protected_entry(self):
        r = self._report(entries=[{"state": "protected"}])
        self.assertTrue(_has_manual_or_refused_work(r))

    def test_true_when_manual_entry(self):
        r = self._report(entries=[{"state": "manual"}])
        self.assertTrue(_has_manual_or_refused_work(r))

    def test_true_when_unsupported_entry(self):
        r = self._report(entries=[{"state": "unsupported"}])
        self.assertTrue(_has_manual_or_refused_work(r))


class CollectPostInstallBackupsTests(DotfilesTestCase):
    def test_returns_empty_when_no_actions(self):
        self.assertEqual(_collect_post_install_backups([]), [])

    def test_returns_empty_when_no_backups_key(self):
        actions = [{"status": "ran", "tool": "gh"}]
        self.assertEqual(_collect_post_install_backups(actions), [])

    def test_collects_backups_from_all_actions(self):
        b1 = {"entry_id": "a", "backup_target": "/tmp/a"}
        b2 = {"entry_id": "b", "backup_target": "/tmp/b"}
        actions = [
            {"status": "ran", "backups": [b1]},
            {"status": "ran", "backups": [b2]},
        ]
        result = _collect_post_install_backups(actions)
        self.assertEqual(result, [b1, b2])

    def test_skips_none_backups(self):
        actions = [{"status": "ran", "backups": None}]
        self.assertEqual(_collect_post_install_backups(actions), [])


class ExecuteBootstrapOperationsTests(DotfilesTestCase):
    def test_prepares_apt_keyrings_before_first_apt_update(self) -> None:
        home = self.make_home()
        keyring_path = home / "keyrings" / "docker.gpg"
        keyring_path.parent.mkdir(parents=True, exist_ok=True)
        keyring_path.write_text("-----BEGIN PGP PUBLIC KEY BLOCK-----\nstale\n")
        cache_dir = home / ".cache" / "tools"
        operations = [
            {
                "operation_id": "op-001",
                "entry_id": "tools.git",
                "recipe": "tool_installs",
                "type": "tool_install_apt_upgrade",
                "mode": "upgrade",
                "packages": ["git"],
                "cache_dir": str(cache_dir),
            },
            {
                "operation_id": "op-002",
                "entry_id": "tools.docker",
                "recipe": "tool_installs",
                "type": "tool_install_apt_keyring",
                "mode": "install",
                "packages": ["docker-ce"],
                "keyring_url": "https://download.docker.com/linux/ubuntu/gpg",
                "keyring_path": str(keyring_path),
                "source_line": (
                    "Types: deb\n"
                    "URIs: https://download.docker.com/linux/ubuntu\n"
                    "Suites: noble\n"
                    "Components: stable\n"
                    "Architectures: {ARCH}\n"
                    f"Signed-By: {keyring_path}"
                ),
                "source_path": str(home / "sources.list.d" / "docker.sources"),
                "cache_dir": str(cache_dir),
            },
        ]
        runner = FakeRunner(which={
            "apt-get": "/usr/bin/apt-get",
            "dpkg": "/usr/bin/dpkg",
            "gpg": "/usr/bin/gpg",
        })
        report = Report(
            "bootstrap-install-tools",
            "warning",
            str(REPO_ROOT),
            home=str(home),
            operations=operations,
        )

        result = _execute_bootstrap_operations(report, REPO_ROOT, home / ".backups", runner)

        self.assertNotEqual(result.status, "failed")
        apt_update_index = next(
            i for i, cmd in enumerate(runner.commands) if cmd == ["sudo", "/usr/bin/apt-get", "update"]
        )
        keyring_install_index = next(
            i for i, cmd in enumerate(runner.commands)
            if cmd[:3] == ["sudo", "install", "-D"] and cmd[-1] == str(keyring_path)
        )
        self.assertLess(keyring_install_index, apt_update_index)


class BuildBootstrapPlanTests(DotfilesTestCase):
    def test_returns_report_with_correct_command(self):
        home = self.make_home()
        report = build_bootstrap_plan(REPO_ROOT, home, profile="machine")
        self.assertEqual(report.command, "bootstrap-plan")

    def test_profile_stored_in_report(self):
        home = self.make_home()
        report = build_bootstrap_plan(REPO_ROOT, home, profile="machine")
        self.assertEqual(report.profile, "machine")

    def test_machine_profile_includes_font_context(self):
        home = self.make_home()
        report = build_bootstrap_plan(REPO_ROOT, home, profile="machine")
        self.assertIn("fonts", report.extra)
        self.assertIn("font_context", report.extra)

    def test_operations_are_renumbered_sequentially(self):
        home = self.make_home()
        report = build_bootstrap_plan(REPO_ROOT, home, profile="machine")
        ids = [op["operation_id"] for op in report.operations]
        expected = [f"op-{i:03d}" for i in range(1, len(ids) + 1)]
        self.assertEqual(ids, expected)

    def test_repo_and_home_are_absolute(self):
        home = self.make_home()
        report = build_bootstrap_plan(REPO_ROOT, home, profile="machine")
        self.assertTrue(report.repo.startswith("/"))
        self.assertTrue(report.home.startswith("/"))


class ApplyBootstrapTests(DotfilesTestCase):
    def test_requires_yes_flag(self):
        home = self.make_home()
        report = apply_bootstrap(REPO_ROOT, home, yes=False)
        self.assertEqual(report.status, "failed")
        self.assertTrue(any("--yes" in str(e) for e in report.errors))

    def test_applies_with_yes(self):
        home = self.make_home()
        runner = FakeRunner()
        report = apply_bootstrap(
            REPO_ROOT, home,
            profile="machine",
            backup_dir=home / ".dotfiles-backups",
            yes=True,
            runner=runner,
        )
        self.assertIn(report.status, {"ok", "warning", "partial"})
        self.assertEqual(report.command, "bootstrap-apply")

    def test_default_backup_dir_inside_home(self):
        home = self.make_home()
        runner = FakeRunner()
        report = apply_bootstrap(
            REPO_ROOT, home,
            profile="machine",
            yes=True,
            runner=runner,
        )
        self.assertNotEqual(report.status, "failed")


class BuildToolInstallSubplanTests(DotfilesTestCase):
    def test_returns_report_with_correct_command(self):
        home = self.make_home()
        report = build_tool_install_subplan(REPO_ROOT, home)
        self.assertEqual(report.command, "bootstrap-install-tools-plan")

    def test_profile_is_machine(self):
        home = self.make_home()
        report = build_tool_install_subplan(REPO_ROOT, home)
        self.assertEqual(report.profile, "machine")

    def test_tools_key_present_in_extra(self):
        home = self.make_home()
        report = build_tool_install_subplan(REPO_ROOT, home)
        self.assertIn("tools", report.extra)

    def test_operations_renumbered(self):
        home = self.make_home()
        report = build_tool_install_subplan(REPO_ROOT, home)
        ids = [op["operation_id"] for op in report.operations]
        expected = [f"op-{i:03d}" for i in range(1, len(ids) + 1)]
        self.assertEqual(ids, expected)

    def test_dev_base_phase_only_includes_dev_base(self):
        home = self.make_home()
        report = build_tool_install_subplan(REPO_ROOT, home, phase="dev-base")
        self.assertTrue(report.operations)
        self.assertEqual({entry["entry_id"] for entry in report.entries}, {"tools.dev_base"})

    def test_tools_phase_skips_dev_base(self):
        home = self.make_home()
        report = build_tool_install_subplan(REPO_ROOT, home, phase="tools")
        self.assertTrue(report.operations)
        self.assertNotIn("tools.dev_base", {entry["entry_id"] for entry in report.entries})


class ApplyToolInstallsTests(DotfilesTestCase):
    def test_requires_yes_flag(self):
        home = self.make_home()
        report = apply_tool_installs(REPO_ROOT, home, yes=False)
        self.assertEqual(report.status, "failed")
        self.assertTrue(any("--yes" in str(e) for e in report.errors))

    def test_command_set_to_bootstrap_install_tools(self):
        home = self.make_home()
        runner = FakeRunner()
        report = apply_tool_installs(
            REPO_ROOT, home,
            backup_dir=home / ".dotfiles-backups",
            yes=True,
            runner=runner,
        )
        self.assertEqual(report.command, "bootstrap-install-tools")

    def test_post_install_report_command(self):
        home = self.make_home()
        runner = FakeRunner()
        report = run_tool_install_post_install(
            REPO_ROOT, home,
            backup_dir=home / ".dotfiles-backups",
            yes=True,
            runner=runner,
        )
        self.assertEqual(report.command, "bootstrap-install-tools-post")

    def test_post_install_verify_mode_skips_actions(self):
        home = self.make_home()
        runner = FakeRunner()
        report = run_tool_install_post_install(
            REPO_ROOT, home,
            mode="verify",
            backup_dir=home / ".dotfiles-backups",
            runner=runner,
        )
        self.assertEqual(report.command, "bootstrap-install-tools-verify")
        self.assertIn("verification", report.extra)
        self.assertNotIn("post_install_actions", report.extra)

    def test_post_install_guidance_mode_omits_verification(self):
        home = self.make_home()
        runner = FakeRunner(which={"gh": "/usr/bin/gh"})
        report = run_tool_install_post_install(
            REPO_ROOT, home,
            mode="guidance",
            backup_dir=home / ".dotfiles-backups",
            runner=runner,
        )
        self.assertEqual(report.command, "bootstrap-install-tools-post")
        self.assertNotIn("verification", report.extra)
        self.assertTrue(report.extra["post_install_actions"])
