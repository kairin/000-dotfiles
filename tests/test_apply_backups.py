from dotfiles_tools.installer import apply_plan
from tests.helpers import DotfilesTestCase, REPO_ROOT


class ApplyBackupTests(DotfilesTestCase):
    def test_apply_preserves_user_customizable_file_with_custom_content(self):
        home = self.make_home()
        target = home / ".claude" / "settings.json"
        target.parent.mkdir(parents=True)
        custom_content = '{"drift": true}'
        target.write_text(custom_content)
        report = apply_plan(REPO_ROOT, home, backup_dir=home / ".dotfiles-backups", yes=True)
        self.assertFalse(report.backups)
        self.assertEqual(target.read_text(), custom_content)
        self.assertTrue(any(op["type"] == "skip" and op["entry_id"] == "claude.settings" for op in report.operations))

    def test_apply_skips_current_target(self):
        home = self.make_home()
        target = home / ".claude" / "settings.json"
        target.parent.mkdir(parents=True)
        target.write_text((REPO_ROOT / "claude/settings.json.template").read_text())
        report = apply_plan(REPO_ROOT, home, backup_dir=home / ".dotfiles-backups", yes=True)
        self.assertTrue(any(op["type"] == "skip" and op["entry_id"] == "claude.settings" for op in report.operations))
