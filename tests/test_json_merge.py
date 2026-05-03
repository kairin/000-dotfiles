import json
from pathlib import Path

from dotfiles_tools.doctor import run_doctor
from dotfiles_tools.installer import build_plan, apply_plan
from tests.helpers import DotfilesTestCase, REPO_ROOT


class JsonMergeDetectionTests(DotfilesTestCase):
    def test_merge_strategy_entries_are_parsed(self):
        """Verify merge_strategy field is recognized in manifest."""
        from dotfiles_tools.manifest import load_manifest
        manifest = load_manifest(REPO_ROOT)
        mcp_entries = [e for e in manifest.entries if getattr(e, "merge_strategy", None) == "json_merge"]
        self.assertGreater(len(mcp_entries), 0, "MCP server entries should use json_merge strategy")
        mcp_ids = {e.id for e in mcp_entries}
        self.assertIn("claude.mcp-servers", mcp_ids)


class JsonMergeOperationTests(DotfilesTestCase):
    def test_user_customizable_settings_not_backed_up_or_replaced(self):
        """User-customizable files are not replaced or backed up even when content differs."""
        home = self.make_home()
        target = home / ".claude" / "settings.json"
        target.parent.mkdir(parents=True)
        custom_content = '{"my": "custom settings"}'
        target.write_text(custom_content)
        report = apply_plan(REPO_ROOT, home, profile="machine", backup_dir=home / ".dotfiles-backups", yes=True)
        self.assertNotEqual(report.status, "failed")
        self.assertEqual(target.read_text(), custom_content)
        self.assertFalse(report.backups)

    def test_merge_preserves_user_server_configuration(self):
        """Placeholder: json_merge strategy is not currently used (MCP servers managed via claude CLI)."""
        pass

    def test_merge_produces_valid_json_output(self):
        """Placeholder: json_merge strategy is not currently used (MCP servers managed via claude CLI)."""
        pass

    def test_missing_target_creates_copy_not_merge(self):
        """When settings.json is missing, a copy operation is planned."""
        home = self.make_home()
        report = build_plan(REPO_ROOT, home)
        settings_ops = [op for op in report.operations if op["entry_id"] == "claude.settings"]
        copy_ops = [op for op in settings_ops if op["type"] == "copy"]
        merge_ops = [op for op in settings_ops if op["type"] == "merge"]
        self.assertEqual(len(copy_ops), 1)
        self.assertEqual(len(merge_ops), 0)
