import json

from dotfiles_tools.doctor import run_doctor
from tests.helpers import DotfilesTestCase, REPO_ROOT


class DoctorReportTests(DotfilesTestCase):
    def test_json_report_contains_target_states(self):
        home = self.make_home()
        target = home / ".claude" / "settings.json"
        target.parent.mkdir(parents=True)
        target.write_text('{"drift": true}')
        report = run_doctor(REPO_ROOT, home)
        data = json.loads(report.to_json())
        states = {entry["entry_id"]: entry["state"] for entry in data["entries"]}
        self.assertEqual(states["claude.settings"], "current")
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
