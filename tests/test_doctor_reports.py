import json

from dotfiles_tools.doctor import _missing_json_keys, run_doctor
from tests.helpers import DotfilesTestCase, REPO_ROOT


class DoctorReportTests(DotfilesTestCase):
    def test_json_report_contains_target_states(self):
        home = self.make_home()
        target = home / ".claude" / ".mcp.json"
        target.parent.mkdir(parents=True)
        target.write_text('{"mcpServers": {}}')
        hook_target = home / ".claude" / "hooks" / "load-project-env.sh"
        hook_target.parent.mkdir(parents=True)
        hook_target.write_text((REPO_ROOT / "claude" / "hooks" / "load-project-env.sh.template").read_text())
        report = run_doctor(REPO_ROOT, home)
        data = json.loads(report.to_json())
        states = {entry["entry_id"]: entry["state"] for entry in data["entries"]}
        self.assertEqual(states["claude.mcp-servers"], "needs_merge")
        self.assertEqual(states["claude.load-project-env"], "current")
        self.assertEqual(states["git.config"], "protected")
        self.assertIn("summary", data)

    def test_machine_doctor_includes_tool_and_auth_guidance(self):
        home = self.make_home()
        report = run_doctor(REPO_ROOT, home)
        data = json.loads(report.to_json())
        tool_ids = {item["id"] for item in data["tool_checks"]}
        self.assertGreaterEqual(tool_ids, {"uv", "git", "gh", "fish", "direnv", "codex", "claude", "gemini", "copilot", "specify"})
        auth_commands = {item["command"] for item in data["auth_guidance"]}
        self.assertIn("gh auth status", auth_commands)

    def test_stale_mcp_target_without_env_blocks_is_flagged(self):
        home = self.make_home()
        target = home / ".claude" / ".mcp.json"
        target.parent.mkdir(parents=True)
        target.write_text(json.dumps({
            "mcpServers": {
                "github": {"command": "npx", "args": ["-y", "@modelcontextprotocol/server-github"]},
                "codacy": {"command": "npx", "args": ["-y", "@codacy/codacy-mcp@latest"]},
            }
        }))
        report = run_doctor(REPO_ROOT, home)
        entry = next(e for e in report.entries if e["entry_id"] == "claude.mcp-servers")
        self.assertEqual(entry["state"], "needs_merge")
        self.assertIn("mcpServers.codacy.env", entry["reason"])
        self.assertIn("mcpServers.github.env", entry["reason"])


class MissingJsonKeysTests(DotfilesTestCase):
    def test_missing_top_level_key(self):
        source = {"a": 1, "b": 2}
        target = {"a": 1}
        self.assertEqual(_missing_json_keys(source, target), ["b"])

    def test_missing_second_level_key(self):
        source = {"servers": {"github": {}, "codacy": {}}}
        target = {"servers": {"github": {}}}
        self.assertEqual(_missing_json_keys(source, target), ["servers.codacy"])

    def test_missing_third_level_key_regression(self):
        source = {
            "mcpServers": {
                "codacy": {"command": "npx", "env": {"CODACY_ACCOUNT_TOKEN": "$CODACY_ACCOUNT_TOKEN"}},
                "github": {"command": "npx", "env": {"GITHUB_TOKEN": "$GITHUB_TOKEN"}},
            }
        }
        target = {
            "mcpServers": {
                "codacy": {"command": "npx"},
                "github": {"command": "npx"},
            }
        }
        self.assertEqual(
            _missing_json_keys(source, target),
            ["mcpServers.codacy.env", "mcpServers.github.env"],
        )

    def test_no_missing_keys_returns_empty(self):
        source = {"mcpServers": {"codacy": {"env": {"K": "v"}}}}
        target = {"mcpServers": {"codacy": {"env": {"K": "v"}, "extra": "ok"}}}
        self.assertEqual(_missing_json_keys(source, target), [])

    def test_target_intermediate_not_dict_reports_path(self):
        source = {"a": {"b": {"c": 1}}}
        target = {"a": "not-a-dict"}
        self.assertEqual(_missing_json_keys(source, target), ["a"])
