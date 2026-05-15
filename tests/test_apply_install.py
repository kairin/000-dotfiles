import json

from dotfiles_tools.installer import _deep_merge, apply_plan
from tests.helpers import DotfilesTestCase, REPO_ROOT


class ApplyInstallTests(DotfilesTestCase):
    def test_apply_installs_missing_non_protected_targets(self):
        home = self.make_home()
        report = apply_plan(REPO_ROOT, home, backup_dir=home / ".dotfiles-backups", yes=True)
        self.assertEqual(report.status, "warning")
        self.assertTrue((home / ".claude" / "settings.json").exists())
        self.assertTrue((home / ".claude" / "hooks" / "load-project-env.sh").exists())
        self.assertTrue((home / ".config" / "fish" / "functions" / "direnv.fish").exists())
        self.assertTrue((home / ".config" / "fish" / "conf.d" / "env.fish").exists())
        self.assertFalse((home / ".config" / "git" / "config").exists())

    def test_apply_merge_restores_missing_env_blocks_in_stale_mcp_json(self):
        home = self.make_home()
        target = home / ".claude" / ".mcp.json"
        target.parent.mkdir(parents=True)
        stale = {
            "mcpServers": {
                "github": {"command": "npx", "args": ["-y", "@modelcontextprotocol/server-github"]},
                "codacy": {"command": "npx", "args": ["-y", "@codacy/codacy-mcp@latest"]},
            }
        }
        target.write_text(json.dumps(stale))

        report = apply_plan(REPO_ROOT, home, backup_dir=home / ".dotfiles-backups", yes=True)
        self.assertNotEqual(report.status, "failed")

        merged = json.loads(target.read_text())
        self.assertEqual(
            merged["mcpServers"]["codacy"]["env"]["CODACY_ACCOUNT_TOKEN"],
            "$CODACY_ACCOUNT_TOKEN",
        )
        self.assertEqual(
            merged["mcpServers"]["github"]["env"]["GITHUB_TOKEN"],
            "$GITHUB_TOKEN",
        )
        self.assertEqual(merged["mcpServers"]["codacy"]["command"], "npx")

    def test_deep_merge_adds_missing_nested_subtree(self):
        source = json.loads((REPO_ROOT / ".claude" / ".mcp.json.template").read_text())
        target = {
            "mcpServers": {
                "github": {"command": "npx"},
                "codacy": {"command": "npx"},
            }
        }
        merged = _deep_merge(source, target)
        self.assertIn("env", merged["mcpServers"]["github"])
        self.assertIn("env", merged["mcpServers"]["codacy"])
        self.assertEqual(merged["mcpServers"]["github"]["env"]["GITHUB_TOKEN"], "$GITHUB_TOKEN")
