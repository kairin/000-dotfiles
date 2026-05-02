from __future__ import annotations

import os
# Tests execute only the repo-local setup script.
import subprocess  # nosec B404
from pathlib import Path
import shutil

from tests.helpers import REPO_ROOT, DotfilesTestCase


SETUP = REPO_ROOT / "setup"


def run_setup(
    *args: str,
    executable: str | Path = SETUP,
    cwd: Path = REPO_ROOT,
    env: dict[str, str] | None = None,
    input_text: str | None = None,
) -> subprocess.CompletedProcess:
    # Fixed executable path, test-controlled args, shell=False.
    return subprocess.run(  # nosec B603
        [str(executable), *args],
        capture_output=True,
        text=True,
        cwd=str(cwd),
        env=env,
        input=input_text,
        shell=False,
    )


def write_clean_project(project: Path) -> None:
    (project / "AGENTS.md").write_text("# Example Project\n\nrendered content.\n")
    (project / "CLAUDE.md").symlink_to("AGENTS.md")
    (project / "GEMINI.md").symlink_to("AGENTS.md")


class SetupScriptTests(DotfilesTestCase):
    COMMON_COMMANDS = (
        "bash",
        "sh",
        "dirname",
        "basename",
        "readlink",
        "mktemp",
        "grep",
        "sed",
        "find",
        "mkdir",
        "cp",
        "rm",
        "cat",
        "chmod",
        "python",
    )

    def make_command_path(self, *extra_commands: str) -> Path:
        bin_dir = self.make_home() / "bin"
        bin_dir.mkdir()
        for name in (*self.COMMON_COMMANDS, *extra_commands):
            if (bin_dir / name).exists():
                continue
            target = shutil.which(name)
            if target is None and name == "python":
                target = shutil.which("python3")
            self.assertIsNotNone(target, f"required command not found for test PATH: {name}")
            (bin_dir / name).symlink_to(target)
        return bin_dir

    def env_for(self, bin_dir: Path, home: Path) -> dict[str, str]:
        env = os.environ.copy()
        env["PATH"] = str(bin_dir)
        env["HOME"] = str(home)
        env["PYTHONPATH"] = str(REPO_ROOT)
        # Default tests to the configured-machine ("tools_present") menu mode
        # so option numbers stay stable. Tests that need the fresh-box flow
        # explicitly override this.
        env["DOTFILES_TOOL_PLATFORM"] = "darwin"
        return env

    def write_executable(self, path: Path, text: str) -> None:
        path.write_text(text)
        path.chmod(0o755)

    def write_fake_uv(
        self,
        bin_dir: Path,
        log_path: Path,
        *,
        self_update_status: int = 0,
        version: str = "uv 0.test",
    ) -> None:
        self.write_executable(
            bin_dir / "uv",
            f"""#!/usr/bin/env bash
set -euo pipefail
printf '%s\\n' "$*" >> "{log_path}"
if [[ "${{1:-}}" == "--version" ]]; then
  echo "{version}"
  exit 0
fi
if [[ "${{1:-}}" == "self" && "${{2:-}}" == "update" ]]; then
  echo "fake self update"
  exit {self_update_status}
fi
if [[ "${{1:-}}" == "run" ]]; then
  shift
  exec "$@"
fi
echo "fake uv unsupported: $*" >&2
exit 64
""",
        )

    def write_uv_installer(self, installer_path: Path, *, version: str) -> None:
        installer_path.write_text(
            f"""#!/usr/bin/env sh
mkdir -p "$HOME/.local/bin"
cat > "$HOME/.local/bin/uv" <<'UV'
#!/usr/bin/env bash
set -euo pipefail
if [[ "${{1:-}}" == "--version" ]]; then
  echo "{version}"
  exit 0
fi
if [[ "${{1:-}}" == "run" ]]; then
  shift
  exec "$@"
fi
echo "installed fake uv unsupported: $*" >&2
exit 64
UV
chmod +x "$HOME/.local/bin/uv"
"""
        )

    def write_fake_downloader(self, bin_dir: Path, name: str, installer_path: Path, log_path: Path) -> None:
        self.write_executable(
            bin_dir / name,
            f"""#!/usr/bin/env bash
set -euo pipefail
printf '%s\\n' "$*" >> "{log_path}"
cat "{installer_path}"
""",
        )

    def test_no_args_runs_machine_doctor_plan_after_uv_bootstrap(self) -> None:
        home = self.make_home()
        bin_dir = self.make_command_path()
        log_path = home / "uv.log"
        self.write_fake_uv(bin_dir, log_path)

        result = run_setup(env=self.env_for(bin_dir, home), input_text="4\n")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("uv found at", result.stdout)
        self.assertIn("uv self update completed.", result.stdout)
        self.assertIn("Machine setup summary", result.stdout)
        self.assertIn("Option 1 will:", result.stdout)
        self.assertIn("Fonts:", result.stdout)
        self.assertIn("Create missing files:", result.stdout)
        self.assertRegex(result.stdout, r"1\. Apply [0-9]+ file changes?( \+ [0-9]+ font actions?)?")
        self.assertIn("2. Show full technical details.", result.stdout)
        self.assertNotIn("entries:", result.stdout)
        self.assertNotIn("operations:", result.stdout)
        self.assertIn("No changes applied.", result.stdout)
        log_lines = log_path.read_text().splitlines()
        self.assertEqual(log_lines[0], "self update")
        self.assertEqual(log_lines[1], "--version")
        self.assertIn("dotfiles_tools.machine_summary", log_lines[2])

    def test_uv_missing_uses_curl_installer_and_refreshes_path(self) -> None:
        home = self.make_home()
        bin_dir = self.make_command_path()
        installer_path = home / "install-uv.sh"
        log_path = home / "curl.log"
        self.write_uv_installer(installer_path, version="uv 0.curl")
        self.write_fake_downloader(bin_dir, "curl", installer_path, log_path)

        result = run_setup(env=self.env_for(bin_dir, home), input_text="4\n")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("uv is required", result.stdout)
        self.assertIn("official standalone installer (curl)", result.stdout)
        self.assertIn("Using uv 0.curl", result.stdout)
        self.assertTrue((home / ".local" / "bin" / "uv").exists())
        self.assertIn("https://astral.sh/uv/install.sh", log_path.read_text())

    def test_uv_missing_uses_wget_installer_when_curl_missing(self) -> None:
        home = self.make_home()
        bin_dir = self.make_command_path()
        installer_path = home / "install-uv.sh"
        log_path = home / "wget.log"
        self.write_uv_installer(installer_path, version="uv 0.wget")
        self.write_fake_downloader(bin_dir, "wget", installer_path, log_path)

        result = run_setup(env=self.env_for(bin_dir, home), input_text="4\n")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("official standalone installer (wget)", result.stdout)
        self.assertIn("Using uv 0.wget", result.stdout)
        self.assertIn("-qO-", log_path.read_text())

    def test_uv_self_update_failure_warns_and_continues(self) -> None:
        home = self.make_home()
        bin_dir = self.make_command_path()
        log_path = home / "uv.log"
        self.write_fake_uv(bin_dir, log_path, self_update_status=7)

        result = run_setup(env=self.env_for(bin_dir, home), input_text="4\n")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Machine setup summary", result.stdout)
        self.assertIn("WARN: uv self update failed", result.stderr)

    def test_no_arg_apply_writes_only_non_protected_config_with_backups(self) -> None:
        home = self.make_home()
        drifted = home / ".claude" / "settings.json"
        drifted.parent.mkdir(parents=True)
        drifted.write_text('{"drift": true}')
        bin_dir = self.make_command_path()
        self.write_fake_uv(bin_dir, home / "uv.log")

        env = self.env_for(bin_dir, home)
        env["DOTFILES_PLATFORM"] = "pixel-avf"
        result = run_setup(env=env, input_text="1\n")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue((home / ".config" / "fish" / "functions" / "direnv.fish").exists())
        self.assertFalse((home / ".config" / "git" / "config").exists())
        self.assertTrue((home / ".config" / "fish" / "conf.d" / "000-dotfiles-pixel-avf-prompt.fish").exists())
        self.assertTrue(any(path.is_file() for path in (home / ".dotfiles-backups").rglob("*")))

    def test_no_arg_tool_guidance_choice_prints_status(self) -> None:
        home = self.make_home()
        bin_dir = self.make_command_path()
        self.write_fake_uv(bin_dir, home / "uv.log")

        result = run_setup(env=self.env_for(bin_dir, home), input_text="3\n4\n")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Show tool and sign-in guidance.", result.stdout)
        self.assertIn("Tool status:", result.stdout)
        self.assertIn("Missing tools:", result.stdout)
        self.assertIn("Sign-in checks unavailable until the tool is installed:", result.stdout)
        self.assertNotIn("Missing tool install/auth commands:", result.stdout)

    def test_no_arg_details_choice_prints_full_diagnostics(self) -> None:
        home = self.make_home()
        bin_dir = self.make_command_path()
        self.write_fake_uv(bin_dir, home / "uv.log")

        result = run_setup(env=self.env_for(bin_dir, home), input_text="2\n4\n")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Full machine doctor:", result.stdout)
        self.assertIn("doctor:", result.stdout)
        self.assertIn("Full machine plan:", result.stdout)
        self.assertIn("font actions:", result.stdout)
        self.assertIn("operations:", result.stdout)
        self.assertIn("Show full technical details.", result.stdout)

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

    def test_init_without_vars_persists_inferred_defaults(self) -> None:
        project = self.make_project()
        home = self.make_home()
        bin_dir = self.make_command_path()
        self.write_fake_uv(bin_dir, home / "uv.log")
        result = run_setup("init", "--project", str(project), "--yes", env=self.env_for(bin_dir, home))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue((project / ".dotfiles" / "project-vars.json").exists())
        self.assertIn("Using inferred project defaults saved to:", result.stdout)

    def test_init_success_with_vars(self) -> None:
        project = self.make_project()
        home = self.make_home()
        bin_dir = self.make_command_path()
        self.write_fake_uv(bin_dir, home / "uv.log")
        self.vars_file(project)
        result = run_setup("init", "--project", str(project), "--yes", env=self.env_for(bin_dir, home))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Verification passed.", result.stdout)
        self.assertTrue((project / "AGENTS.md").is_file())
        self.assertTrue((project / "CLAUDE.md").is_symlink())
        self.assertTrue((project / "GEMINI.md").is_symlink())

    def test_init_defaults_to_current_project_and_auto_verifies(self) -> None:
        project = self.make_project()
        home = self.make_home()
        bin_dir = self.make_command_path()
        self.write_fake_uv(bin_dir, home / "uv.log")
        self.vars_file(project)
        result = run_setup("init", "--yes", cwd=project, env=self.env_for(bin_dir, home))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Bootstrapping project:", result.stdout)
        self.assertIn("Verification passed.", result.stdout)
        self.assertTrue((project / "AGENTS.md").is_file())
        self.assertTrue((project / "CLAUDE.md").is_symlink())
        self.assertTrue((project / "GEMINI.md").is_symlink())

    def test_doctor_runs_against_home(self) -> None:
        home = self.make_home()
        fake_home = self.make_home()
        bin_dir = self.make_command_path()
        self.write_fake_uv(bin_dir, fake_home / "uv.log")
        result = run_setup("doctor", "--home", str(home), env=self.env_for(bin_dir, fake_home))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("doctor:", result.stdout.lower())

    def test_project_path_persists_metadata_without_bootstrapping_on_exit(self) -> None:
        project = self.make_project()
        home = self.make_home()
        bin_dir = self.make_command_path()
        self.write_fake_uv(bin_dir, home / "uv.log")

        result = run_setup(str(project), env=self.env_for(bin_dir, home), input_text="4\n")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue((project / ".dotfiles" / "project-vars.json").exists())
        self.assertFalse((project / "AGENTS.md").exists())
        self.assertIn("Project folder is empty", result.stdout)


if __name__ == "__main__":
    import unittest

    unittest.main()
