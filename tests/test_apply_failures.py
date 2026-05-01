from dotfiles_tools.installer import apply_plan
from tests.helpers import DotfilesTestCase, REPO_ROOT


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
