from __future__ import annotations

import subprocess
from pathlib import Path

from tests.helpers import REPO_ROOT, DotfilesTestCase


SETUP = REPO_ROOT / "setup"


def run_setup(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(SETUP), *args],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )


def write_clean_project(project: Path) -> None:
    (project / "AGENTS.md").write_text("# Example Project\n\nrendered content.\n")
    (project / "CLAUDE.md").symlink_to("AGENTS.md")
    (project / "GEMINI.md").symlink_to("AGENTS.md")


class SetupScriptTests(DotfilesTestCase):
    def test_help_no_args(self) -> None:
        result = run_setup()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Usage:", result.stdout)

    def test_help_subcommand(self) -> None:
        result = run_setup("help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Usage:", result.stdout)

    def test_unknown_command(self) -> None:
        result = run_setup("nope")
        self.assertEqual(result.returncode, 2)
        self.assertIn("unknown command", result.stderr)

    def test_verify_clean_project(self) -> None:
        project = self.make_project()
        write_clean_project(project)
        result = run_setup("verify", "--project", str(project))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Verification passed.", result.stdout)

    def test_verify_missing_agents(self) -> None:
        project = self.make_project()
        result = run_setup("verify", "--project", str(project))
        self.assertEqual(result.returncode, 1)
        self.assertIn("AGENTS.md missing", result.stdout)

    def test_verify_unresolved_placeholder(self) -> None:
        project = self.make_project()
        (project / "AGENTS.md").write_text("# {{PROJECT_NAME}}\n")
        (project / "CLAUDE.md").symlink_to("AGENTS.md")
        (project / "GEMINI.md").symlink_to("AGENTS.md")
        result = run_setup("verify", "--project", str(project))
        self.assertEqual(result.returncode, 1)
        self.assertIn("unresolved placeholders", result.stdout)

    def test_verify_unresolved_placeholder_with_digit(self) -> None:
        project = self.make_project()
        (project / "AGENTS.md").write_text("# rev {{VERSION_2}}\n")
        (project / "CLAUDE.md").symlink_to("AGENTS.md")
        (project / "GEMINI.md").symlink_to("AGENTS.md")
        result = run_setup("verify", "--project", str(project))
        self.assertEqual(result.returncode, 1)
        self.assertIn("unresolved placeholders", result.stdout)

    def test_verify_wrong_symlink_target(self) -> None:
        project = self.make_project()
        (project / "AGENTS.md").write_text("# ok\n")
        (project / "OTHER.md").write_text("noise\n")
        (project / "CLAUDE.md").symlink_to("OTHER.md")
        (project / "GEMINI.md").symlink_to("AGENTS.md")
        result = run_setup("verify", "--project", str(project))
        self.assertEqual(result.returncode, 1)
        self.assertIn("CLAUDE.md -> OTHER.md", result.stdout)

    def test_verify_copilot_flag_missing_file(self) -> None:
        project = self.make_project()
        write_clean_project(project)
        result = run_setup("verify", "--project", str(project), "--copilot")
        self.assertEqual(result.returncode, 1)
        self.assertIn("--copilot specified", result.stdout)

    def test_verify_copilot_flag_clean(self) -> None:
        project = self.make_project()
        write_clean_project(project)
        github_dir = project / ".github"
        github_dir.mkdir()
        (github_dir / "copilot-instructions.md").write_text("# clean copilot\n")
        result = run_setup("verify", "--project", str(project), "--copilot")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(".github/copilot-instructions.md clean", result.stdout)

    def test_init_missing_vars_prints_example(self) -> None:
        project = self.make_project()
        result = run_setup("init", "--project", str(project), "--yes")
        self.assertEqual(result.returncode, 2)
        self.assertIn("project-vars.json", result.stderr)
        self.assertIn("PROJECT_NAME", result.stderr)


if __name__ == "__main__":
    import unittest

    unittest.main()
