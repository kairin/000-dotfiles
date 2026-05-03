import json
from dotfiles_tools.installer import apply_plan
from tests.helpers import DotfilesTestCase, REPO_ROOT


class ApplyBackupTests(DotfilesTestCase):
    def test_apply_merges_json_files_without_backup(self):
        home = self.make_home()
        target = home / ".claude" / ".mcp.json"
        target.parent.mkdir(parents=True)
        target.write_text('{"mcpServers": {}}')
        report = apply_plan(REPO_ROOT, home, backup_dir=home / ".dotfiles-backups", yes=True)
        self.assertFalse(report.backups, "merge operations do not create backups")
        merged = json.loads(target.read_text())
        self.assertIn("codacy", merged["mcpServers"])
        self.assertIn("github", merged["mcpServers"])

    def test_apply_skips_current_target(self):
        home = self.make_home()
        target = home / ".claude" / "settings.json"
        target.parent.mkdir(parents=True)
        target.write_text((REPO_ROOT / "claude/settings.json.template").read_text())
        report = apply_plan(REPO_ROOT, home, backup_dir=home / ".dotfiles-backups", yes=True)
        self.assertTrue(any(op["type"] == "skip" and op["entry_id"] == "claude.settings" for op in report.operations))
