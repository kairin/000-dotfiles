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
        mcp_entry = manifest.entry_map()["claude.mcp-servers"]
        self.assertEqual(mcp_entry.merge_strategy, "json_merge")

    def test_missing_target_reports_missing_state(self):
        """When target .mcp.json doesn't exist, state is 'missing'."""
        home = self.make_home()
        report = run_doctor(REPO_ROOT, home)
        mcp_state = {e["entry_id"]: e for e in report.entries}["claude.mcp-servers"]
        self.assertEqual(mcp_state["state"], "missing")

    def test_target_with_all_required_servers_reports_current(self):
        """When target has all required servers, state is 'current'."""
        home = self.make_home()
        target = home / ".claude" / ".mcp.json"
        target.parent.mkdir(parents=True)
        target.write_text(json.dumps({
            "mcpServers": {
                "codacy": {
                    "command": "npx",
                    "args": ["-y", "@codacy/codacy-mcp@latest"],
                    "env": {"CODACY_ACCOUNT_TOKEN": "$CODACY_ACCOUNT_TOKEN"}
                }
            }
        }, indent=2))
        report = run_doctor(REPO_ROOT, home)
        mcp_state = {e["entry_id"]: e for e in report.entries}["claude.mcp-servers"]
        self.assertEqual(mcp_state["state"], "current")
        self.assertIn("required entries are present", mcp_state["reason"])

    def test_target_with_required_and_extra_servers_reports_current(self):
        """When target has required servers plus extras, state is 'current'."""
        home = self.make_home()
        target = home / ".claude" / ".mcp.json"
        target.parent.mkdir(parents=True)
        target.write_text(json.dumps({
            "mcpServers": {
                "codacy": {
                    "command": "npx",
                    "args": ["-y", "@codacy/codacy-mcp@latest"],
                    "env": {"CODACY_ACCOUNT_TOKEN": "$CODACY_ACCOUNT_TOKEN"}
                },
                "custom-server": {
                    "command": "node",
                    "args": ["custom.js"]
                }
            }
        }, indent=2))
        report = run_doctor(REPO_ROOT, home)
        mcp_state = {e["entry_id"]: e for e in report.entries}["claude.mcp-servers"]
        self.assertEqual(mcp_state["state"], "current")

    def test_target_missing_required_server_reports_needs_merge(self):
        """When target lacks a required server, state is 'needs_merge'."""
        home = self.make_home()
        target = home / ".claude" / ".mcp.json"
        target.parent.mkdir(parents=True)
        target.write_text(json.dumps({
            "mcpServers": {
                "some-other-server": {
                    "command": "node",
                    "args": ["other.js"]
                }
            }
        }, indent=2))
        report = run_doctor(REPO_ROOT, home)
        mcp_state = {e["entry_id"]: e for e in report.entries}["claude.mcp-servers"]
        self.assertEqual(mcp_state["state"], "needs_merge")
        self.assertIn("missing entries", mcp_state["reason"])
        self.assertIn("codacy", mcp_state["reason"])

    def test_invalid_json_reports_blocked(self):
        """When target is invalid JSON, state is 'blocked'."""
        home = self.make_home()
        target = home / ".claude" / ".mcp.json"
        target.parent.mkdir(parents=True)
        target.write_text("{ invalid json }")
        report = run_doctor(REPO_ROOT, home)
        mcp_state = {e["entry_id"]: e for e in report.entries}["claude.mcp-servers"]
        self.assertEqual(mcp_state["state"], "blocked")


class JsonMergeOperationTests(DotfilesTestCase):
    def test_needs_merge_creates_merge_operation(self):
        """When state is 'needs_merge', a merge operation is planned."""
        home = self.make_home()
        target = home / ".claude" / ".mcp.json"
        target.parent.mkdir(parents=True)
        target.write_text(json.dumps({
            "mcpServers": {
                "other": {"command": "node"}
            }
        }))
        report = build_plan(REPO_ROOT, home)
        merge_ops = [op for op in report.operations if op["type"] == "merge"]
        self.assertEqual(len(merge_ops), 1)
        self.assertEqual(merge_ops[0]["entry_id"], "claude.mcp-servers")

    def test_merge_adds_missing_servers_preserves_existing(self):
        """Merge operation adds required servers, preserves user additions."""
        home = self.make_home()
        backup_dir = self.make_home()
        target = home / ".claude" / ".mcp.json"
        target.parent.mkdir(parents=True)
        user_servers = {
            "mcpServers": {
                "user-server": {
                    "command": "node",
                    "args": ["user.js"]
                }
            }
        }
        target.write_text(json.dumps(user_servers))
        report = apply_plan(REPO_ROOT, home, profile="machine", backup_dir=backup_dir, yes=True)
        self.assertNotEqual(report.status, "failed")
        merged = json.loads(target.read_text())
        self.assertIn("codacy", merged["mcpServers"])
        self.assertIn("user-server", merged["mcpServers"])

    def test_merge_preserves_user_server_configuration(self):
        """Merge preserves existing user server config unchanged."""
        home = self.make_home()
        backup_dir = self.make_home()
        target = home / ".claude" / ".mcp.json"
        target.parent.mkdir(parents=True)
        user_config = {
            "mcpServers": {
                "user-server": {
                    "command": "node",
                    "args": ["user.js"],
                    "custom_key": "custom_value"
                }
            }
        }
        target.write_text(json.dumps(user_config))
        apply_plan(REPO_ROOT, home, profile="machine", backup_dir=backup_dir, yes=True)
        merged = json.loads(target.read_text())
        self.assertEqual(
            merged["mcpServers"]["user-server"]["custom_key"],
            "custom_value"
        )
        self.assertEqual(
            merged["mcpServers"]["user-server"]["args"],
            ["user.js"]
        )

    def test_merge_produces_valid_json_output(self):
        """Merged file is valid JSON with proper formatting."""
        home = self.make_home()
        backup_dir = self.make_home()
        target = home / ".claude" / ".mcp.json"
        target.parent.mkdir(parents=True)
        target.write_text(json.dumps({
            "mcpServers": {
                "other": {"command": "node"}
            }
        }))
        apply_plan(REPO_ROOT, home, profile="machine", backup_dir=backup_dir, yes=True)
        content = target.read_text()
        merged = json.loads(content)
        self.assertIsInstance(merged, dict)
        self.assertIn("mcpServers", merged)
        self.assertTrue(content.endswith("\n"), "JSON should end with newline")

    def test_missing_target_creates_copy_not_merge(self):
        """When target is missing, operation is copy (not merge)."""
        home = self.make_home()
        report = build_plan(REPO_ROOT, home)
        mcp_ops = [op for op in report.operations if op["entry_id"] == "claude.mcp-servers"]
        copy_ops = [op for op in mcp_ops if op["type"] == "copy"]
        merge_ops = [op for op in mcp_ops if op["type"] == "merge"]
        self.assertEqual(len(copy_ops), 1)
        self.assertEqual(len(merge_ops), 0)
