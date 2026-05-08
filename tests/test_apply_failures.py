from pathlib import Path

from dotfiles_tools.bootstrap import _execute_bootstrap_operations
from dotfiles_tools.installer import apply_plan
from dotfiles_tools.reports import Report
from tests.helpers import DotfilesTestCase, REPO_ROOT


class _NoDownloadRunner:
    """Runner whose download() is a no-op so the installer script never lands on disk."""

    def __init__(self) -> None:
        self.commands: list[list[str]] = []
        self.downloads: list[tuple[str, Path]] = []

    def which(self, command: str) -> str | None:
        return "/bin/bash" if command == "bash" else None

    def run(self, args, *, capture_output: bool = False, check: bool = True, timeout: float | None = None):  # pragma: no cover
        self.commands.append(list(args))
        raise AssertionError("runner.run should not be invoked when download fails")

    def download(self, url: str, target: Path) -> None:
        self.downloads.append((url, target))


class ApplyFailureTests(DotfilesTestCase):
    def test_apply_requires_yes(self):
        home = self.make_home()
        report = apply_plan(REPO_ROOT, home, backup_dir=home / ".dotfiles-backups", yes=False)
        self.assertEqual(report.status, "failed")
        self.assertIn("--yes", report.errors[0]["message"])

    def test_apply_reports_partial_on_late_failure(self):
        home = self.make_home()
        blocked = home / ".codex" / "config.toml"
        blocked.parent.mkdir(parents=True)
        blocked.mkdir()
        report = apply_plan(REPO_ROOT, home, backup_dir=home / ".dotfiles-backups", yes=True)
        self.assertIn(report.status, {"failed", "partial"})
        self.assertTrue(report.errors)

    def test_curl_install_download_failure_propagates_to_failed_report(self):
        home = self.make_home()
        cache_dir = home / ".cache" / "tool-installers"
        op = {
            "operation_id": "op-001",
            "entry_id": "tools.claude",
            "recipe": "tool_installs",
            "type": "tool_install_curl",
            "url": "https://claude.ai/install.sh",
            "script_name": "claude-install.sh",
            "interpreter": "bash",
            "requires_sudo": False,
            "cache_dir": str(cache_dir),
        }
        report = Report(
            "bootstrap-install-tools",
            "warning",
            str(REPO_ROOT),
            home=str(home),
            profile="machine",
            operations=[op],
        )
        runner = _NoDownloadRunner()
        result = _execute_bootstrap_operations(
            report, REPO_ROOT, home / ".dotfiles-backups", runner
        )
        self.assertEqual(result.status, "failed")
        self.assertTrue(result.errors)
        first_error = result.errors[0]
        self.assertEqual(first_error["entry_id"], "tools.claude")
        self.assertIn("failed to download installer", first_error["message"])
        self.assertIn("https://claude.ai/install.sh", first_error["message"])
