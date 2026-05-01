from __future__ import annotations

import os
# Tests execute only the repo-local setup script.
import subprocess  # nosec B404
from pathlib import Path

from tests.helpers import REPO_ROOT, DotfilesTestCase


SETUP = REPO_ROOT / "setup"


def run_setup(
    *args: str,
    executable: str | Path = SETUP,
    cwd: Path = REPO_ROOT,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess:
    # Fixed executable path, test-controlled args, shell=False.
    return subprocess.run(  # nosec B603
        [str(executable), *args],
        capture_output=True,
        text=True,
        cwd=str(cwd),
        env=env,
        shell=False,
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

    def test_source_does_not_require_gnu_readlink_f(self) -> None:
        self.assertNotIn("readlink -f", SETUP.read_text())

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

    def test_verify_works_from_symlink_on_path(self) -> None:
        project = self.make_project()
        write_clean_project(project)
        bin_dir = self.make_home() / "bin"
        bin_dir.mkdir()
        relative_target = os.path.relpath(SETUP, start=bin_dir)
        (bin_dir / "dotfiles-setup").symlink_to(relative_target)
        env = os.environ.copy()
        env["PATH"] = f"{bin_dir}{os.pathsep}{env.get('PATH', '')}"

        result = run_setup("verify", executable="dotfiles-setup", cwd=project, env=env)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Verification passed.", result.stdout)

    def test_init_missing_vars_prints_example(self) -> None:
        project = self.make_project()
        result = run_setup("init", "--project", str(project), "--yes")
        self.assertEqual(result.returncode, 2)
        self.assertIn("project-vars.json", result.stderr)
        self.assertIn("PROJECT_NAME", result.stderr)

    def test_init_success_with_vars(self) -> None:
        project = self.make_project()
        self.vars_file(project)
        result = run_setup("init", "--project", str(project), "--yes")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Verification passed.", result.stdout)
        self.assertTrue((project / "AGENTS.md").is_file())
        self.assertTrue((project / "CLAUDE.md").is_symlink())
        self.assertTrue((project / "GEMINI.md").is_symlink())

    def test_init_defaults_to_current_project_and_auto_verifies(self) -> None:
        project = self.make_project()
        self.vars_file(project)
        result = run_setup("init", "--yes", cwd=project)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Bootstrapping project:", result.stdout)
        self.assertIn("Verification passed.", result.stdout)
        self.assertTrue((project / "AGENTS.md").is_file())
        self.assertTrue((project / "CLAUDE.md").is_symlink())
        self.assertTrue((project / "GEMINI.md").is_symlink())

    def test_doctor_runs_against_home(self) -> None:
        home = self.make_home()
        result = run_setup("doctor", "--home", str(home))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("doctor:", result.stdout.lower())


if __name__ == "__main__":
    import unittest

    unittest.main()
