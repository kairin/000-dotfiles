from dotfiles_tools.installer import apply_plan
from tests.helpers import DotfilesTestCase, REPO_ROOT


class ApplyInstallTests(DotfilesTestCase):
    def test_apply_installs_missing_non_protected_targets(self):
        home = self.make_home()
        report = apply_plan(REPO_ROOT, home, backup_dir=home / ".dotfiles-backups", yes=True)
        self.assertEqual(report.status, "warning")
        self.assertTrue((home / ".claude" / "settings.json").exists())
        self.assertTrue((home / ".config" / "fish" / "functions" / "direnv.fish").exists())
        self.assertFalse((home / ".config" / "git" / "config").exists())
