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
        "head",
        "find",
        "mkdir",
        "cp",
        "cmp",
        "rm",
        "cat",
        "chmod",
        "date",
        "git",
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
        # Provide a fake gh that always reports authenticated so optional_integrations_menu
        # omits the gh option and Codacy remains option 1 (matching test input sequences).
        if not (bin_dir / "gh").exists():
            self.write_executable(
                bin_dir / "gh",
                "#!/usr/bin/env bash\n[[ \"${1:-}\" == auth && \"${2:-}\" == status ]] && exit 0\nexit 1\n",
            )
        return bin_dir

    def env_for(self, bin_dir: Path, home: Path, *, machine_summary_output: str | None = None) -> dict[str, str]:
        env = os.environ.copy()
        env["PATH"] = str(bin_dir)
        env["HOME"] = str(home)
        env["PYTHONPATH"] = str(REPO_ROOT)
        # Default tests to the configured-machine ("tools_present") menu mode
        # so option numbers stay stable. Tests that need the fresh-box flow
        # explicitly override this.
        env["DOTFILES_TOOL_PLATFORM"] = "darwin"
        if machine_summary_output is not None:
            env["FAKE_MACHINE_SUMMARY_OUTPUT"] = machine_summary_output
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
  if [[ -n "${{FAKE_MACHINE_SUMMARY_OUTPUT:-}}" && "${{1:-}}" == "python" && "${{2:-}}" == "-m" && "${{3:-}}" == "dotfiles_tools.machine_summary" ]]; then
    printf '%s' "$FAKE_MACHINE_SUMMARY_OUTPUT"
    exit 0
  fi
  exec "$@"
fi
echo "fake uv unsupported: $*" >&2
exit 64
""",
        )

    def machine_summary_output(self, option_number: int, label: str, reason: str, *lines: str) -> str:
        output_lines = [
            "Machine setup summary",
            "Repo: /tmp/fake-repo",
            "Home: /tmp/fake-home",
            "Profile: machine",
            "",
            f"Recommended next step: {option_number}. {label} - {reason}",
            *lines,
        ]
        return "\n".join(output_lines) + "\n"

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

    def assert_no_codacy_files(self, project: Path, home: Path) -> None:
        self.assertFalse((project / ".envrc").exists())
        self.assertFalse((project / ".envrc.local").exists())
        self.assertFalse((home / ".codacy").exists())
        self.assertFalse(list(project.glob(".envrc.bak.*")))
        self.assertFalse(list(project.glob(".envrc.local.bak.*")))

    def run_project_setup(
        self,
        project: Path,
        input_text: str,
        *,
        home: Path | None = None,
    ) -> tuple[subprocess.CompletedProcess, Path]:
        actual_home = home or self.make_home()
        bin_dir = self.make_command_path()
        self.write_fake_uv(bin_dir, actual_home / "uv.log")
        result = run_setup(str(project), env=self.env_for(bin_dir, actual_home), input_text=input_text)
        return result, actual_home

    def test_no_args_runs_machine_doctor_plan_after_uv_bootstrap(self) -> None:
        home = self.make_home()
        bin_dir = self.make_command_path()
        log_path = home / "uv.log"
        self.write_fake_uv(bin_dir, log_path)

        result = run_setup(env=self.env_for(bin_dir, home), input_text="6\n")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("uv found at", result.stdout)
        self.assertIn("uv self update completed.", result.stdout)
        self.assertIn("Machine setup summary", result.stdout)
        self.assertIn("Recommended next step: 1. Install / update developer tools - Developer tools should be installed or updated first.", result.stdout)
        self.assertIn("Fonts:", result.stdout)
        self.assertIn("Create missing files:", result.stdout)
        self.assertIn("1. Install / update developer tools", result.stdout)
        self.assertIn("3. Show full technical details.", result.stdout)
        self.assertIn("1. Install / update developer tools (preview, then apply). [recommended]", result.stdout)
        self.assertNotRegex(result.stdout, r"2\..*\[recommended\]")
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

        result = run_setup(env=self.env_for(bin_dir, home), input_text="5\n")

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

        result = run_setup(env=self.env_for(bin_dir, home), input_text="5\n")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("official standalone installer (wget)", result.stdout)
        self.assertIn("Using uv 0.wget", result.stdout)
        self.assertIn("-qO-", log_path.read_text())

    def test_uv_self_update_failure_warns_and_continues(self) -> None:
        home = self.make_home()
        bin_dir = self.make_command_path()
        log_path = home / "uv.log"
        self.write_fake_uv(bin_dir, log_path, self_update_status=7)

        result = run_setup(env=self.env_for(bin_dir, home), input_text="5\n")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Machine setup summary", result.stdout)
        self.assertIn("WARN: uv self update failed", result.stderr)

    def test_no_arg_apply_writes_only_non_protected_config(self) -> None:
        home = self.make_home()
        bin_dir = self.make_command_path()
        self.write_fake_uv(bin_dir, home / "uv.log")

        env = self.env_for(bin_dir, home)
        env["DOTFILES_PLATFORM"] = "pixel-avf"
        result = run_setup(env=env, input_text="2\n")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue((home / ".config" / "fish" / "functions" / "direnv.fish").exists())
        self.assertFalse((home / ".config" / "git" / "config").exists())
        self.assertTrue((home / ".config" / "fish" / "conf.d" / "000-dotfiles-pixel-avf-prompt.fish").exists())

    def test_no_arg_tool_guidance_choice_prints_status(self) -> None:
        home = self.make_home()
        bin_dir = self.make_command_path()
        self.write_fake_uv(bin_dir, home / "uv.log")
        summary = self.machine_summary_output(
            4,
            "Show tool and sign-in guidance",
            "Sign-in guidance is the useful next step.",
            "  - Tool and sign-in guidance: gh auth status.",
        )

        result = run_setup(env=self.env_for(bin_dir, home, machine_summary_output=summary), input_text="4\n5\n")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Recommended next step: 4. Show tool and sign-in guidance - Sign-in guidance is the useful next step.", result.stdout)
        self.assertIn("4. Show tool and sign-in guidance. [recommended]", result.stdout)
        self.assertIn("Tool status:", result.stdout)
        self.assertIn("Missing tools:", result.stdout)
        self.assertIn("Sign-in checks unavailable until the tool is installed:", result.stdout)
        self.assertNotIn("Missing tool install/auth commands:", result.stdout)

    def test_no_arg_details_choice_prints_full_diagnostics(self) -> None:
        home = self.make_home()
        bin_dir = self.make_command_path()
        self.write_fake_uv(bin_dir, home / "uv.log")
        summary = self.machine_summary_output(
            3,
            "Show full technical details",
            "The audit is incomplete.",
            "  - The audit is incomplete; inspect the full technical details.",
        )

        result = run_setup(env=self.env_for(bin_dir, home, machine_summary_output=summary), input_text="3\n5\n")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Recommended next step: 3. Show full technical details - The audit is incomplete.", result.stdout)
        self.assertIn("3. Show full technical details. [recommended]", result.stdout)
        self.assertIn("Full machine doctor:", result.stdout)
        self.assertIn("doctor:", result.stdout)
        self.assertIn("Full machine plan:", result.stdout)
        self.assertIn("font actions:", result.stdout)
        self.assertIn("operations:", result.stdout)
        self.assertIn("Show full technical details.", result.stdout)

    def test_no_arg_install_choice_refreshes_summary_after_cancel(self) -> None:
        home = self.make_home()
        bin_dir = self.make_command_path()
        self.write_fake_uv(bin_dir, home / "uv.log")
        summary = self.machine_summary_output(
            1,
            "Install / update developer tools",
            "Developer tools should be installed or updated first.",
            "  - 2 developer tools are missing or unverified.",
            "    - gh: install gh",
        )

        result = run_setup(env=self.env_for(bin_dir, home, machine_summary_output=summary), input_text="1\nn\n5\n")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertGreaterEqual(result.stdout.count("Machine setup summary"), 2)
        self.assertGreaterEqual(result.stdout.count("Recommended next step: 1. Install / update developer tools - Developer tools should be installed or updated first."), 2)
        self.assertGreaterEqual(result.stdout.count("1. Install / update developer tools (preview, then apply). [recommended]"), 2)
        self.assertIn("No tool changes applied.", result.stdout)

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

    def test_empty_project_menu_uses_optional_integrations_entry(self) -> None:
        project = self.make_project()
        result, _home = self.run_project_setup(project, "5\n")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("3. Open optional integrations and APIs.", result.stdout)
        self.assertIn("1. Bootstrap AGENTS.md plus CLAUDE.md/GEMINI.md symlinks.", result.stdout)
        self.assertIn("2. Bootstrap agent docs plus Copilot instructions.", result.stdout)
        self.assertNotIn("Manage Codacy API access", result.stdout)
        self.assertNotRegex(result.stdout, r"Open optional integrations.*\[recommended\]")

    def test_existing_project_menu_uses_optional_integrations_entry(self) -> None:
        project = self.make_project()
        write_clean_project(project)
        result, _home = self.run_project_setup(project, "6\n")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("4. Open optional integrations and APIs.", result.stdout)
        self.assertIn("1. Verify agent docs.", result.stdout)
        self.assertIn("2. Repair/bootstrap AGENTS.md plus CLAUDE.md/GEMINI.md symlinks.", result.stdout)
        self.assertIn("3. Add or refresh Copilot instructions.", result.stdout)
        self.assertNotIn("Manage Codacy API access", result.stdout)
        self.assertNotRegex(result.stdout, r"Open optional integrations.*\[recommended\]")

    def test_optional_integrations_back_and_eof_do_not_write_codacy_files(self) -> None:
        project = self.make_project()
        result, home = self.run_project_setup(project, "3\n2\n5\n")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Manage Codacy API access", result.stdout)
        self.assertIn("Back to project setup", result.stdout)
        self.assert_no_codacy_files(project, home)

        eof_project = self.make_project()
        eof_result, eof_home = self.run_project_setup(eof_project, "3\n")

        self.assertEqual(eof_result.returncode, 0, eof_result.stdout + eof_result.stderr)
        self.assertIn("No optional integration selection received", eof_result.stdout)
        self.assert_no_codacy_files(eof_project, eof_home)

    def test_codacy_repository_token_mode_writes_secret_safe_bridge(self) -> None:
        project = self.make_project()
        secret = "repo-token-value"
        result, home = self.run_project_setup(
            project,
            f"3\n1\n1\nkairin\n000-dotfiles\n{secret}\ny\n2\n5\n",
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        token_file = home / ".codacy" / "kairin-000-dotfiles.project-token"
        envrc = project / ".envrc"
        envrc_local = project / ".envrc.local"
        self.assertTrue(token_file.exists())
        self.assertEqual(token_file.read_text(), secret + "\n")
        self.assertEqual(oct(token_file.stat().st_mode & 0o777), "0o600")
        self.assertEqual(oct(envrc.stat().st_mode & 0o777), "0o444")
        self.assertEqual(oct(envrc_local.stat().st_mode & 0o777), "0o600")
        self.assertIn("source_env_if_exists .envrc.local", envrc.read_text())
        local_text = envrc_local.read_text()
        self.assertIn("CODACY_PROJECT_TOKEN", local_text)
        self.assertIn('CODACY_ORGANIZATION_PROVIDER="gh"', local_text)
        self.assertIn('CODACY_USERNAME="kairin"', local_text)
        self.assertIn('CODACY_PROJECT_NAME="000-dotfiles"', local_text)
        self.assertNotIn(secret, local_text)
        self.assertNotIn(secret, result.stdout)
        self.assertNotIn(secret, result.stderr)

    def test_codacy_account_token_mode_writes_secret_safe_bridge(self) -> None:
        project = self.make_project()
        secret = "account-token-value"
        result, home = self.run_project_setup(
            project,
            f"3\n1\n2\nkairin\n000-dotfiles\n{secret}\ny\n2\n5\n",
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        token_file = home / ".codacy" / "account-token"
        self.assertTrue(token_file.exists())
        self.assertEqual(token_file.read_text(), secret + "\n")
        local_text = (project / ".envrc.local").read_text()
        self.assertIn("CODACY_API_TOKEN", local_text)
        self.assertIn('CODACY_ORGANIZATION_PROVIDER="gh"', local_text)
        self.assertIn('CODACY_USERNAME="kairin"', local_text)
        self.assertIn('CODACY_PROJECT_NAME="000-dotfiles"', local_text)
        self.assertNotIn(secret, local_text)
        self.assertNotIn(secret, result.stdout)
        self.assertNotIn(secret, result.stderr)

    def test_codacy_mode_cancel_returns_to_optional_menu_without_writes(self) -> None:
        project = self.make_project()
        result, home = self.run_project_setup(project, "3\n1\n3\n2\n5\n")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Codacy setup cancelled; returning to optional integrations.", result.stdout)
        self.assertIn("2. Back to project setup.", result.stdout)
        self.assert_no_codacy_files(project, home)

    def test_codacy_identity_fallback_prompts_for_owner_and_repository(self) -> None:
        project = self.make_project()
        result, _home = self.run_project_setup(
            project,
            "3\n1\n1\nfallback-owner\nfallback-repo\nrepo-token\ny\n2\n5\n",
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("GitHub owner", result.stdout)
        self.assertIn("GitHub repository", result.stdout)
        local_text = (project / ".envrc.local").read_text()
        self.assertIn('CODACY_USERNAME="fallback-owner"', local_text)
        self.assertIn('CODACY_PROJECT_NAME="fallback-repo"', local_text)

    def test_codacy_declined_confirmation_creates_no_files_or_backups(self) -> None:
        project = self.make_project()
        secret = "declined-token"
        result, home = self.run_project_setup(
            project,
            f"3\n1\n1\nkairin\n000-dotfiles\n{secret}\nn\n2\n5\n",
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("No Codacy environment changes applied.", result.stdout)
        self.assert_no_codacy_files(project, home)
        self.assertNotIn(secret, result.stdout)
        self.assertNotIn(secret, result.stderr)

    def test_codacy_blank_token_without_existing_file_writes_no_active_token_export(self) -> None:
        project = self.make_project()
        result, home = self.run_project_setup(
            project,
            "3\n1\n1\nkairin\n000-dotfiles\n\ny\n2\n5\n",
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse((home / ".codacy" / "kairin-000-dotfiles.project-token").exists())
        local_text = (project / ".envrc.local").read_text()
        self.assertIn("CODACY_PROJECT_TOKEN not exported", local_text)
        self.assertNotIn("export CODACY_PROJECT_TOKEN=", local_text)
        self.assertIn("A Codacy token is required before activation.", result.stdout)

    def test_codacy_existing_env_files_are_backed_up_before_changes(self) -> None:
        project = self.make_project()
        (project / ".envrc").write_text("# user envrc\n")
        (project / ".envrc.local").write_text("# user local env\n")
        result, _home = self.run_project_setup(
            project,
            "4\n1\n1\nkairin\n000-dotfiles\nrepo-token\ny\n2\n6\n",
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        envrc_backups = list(project.glob(".envrc.bak.*"))
        local_backups = list(project.glob(".envrc.local.bak.*"))
        self.assertEqual(len(envrc_backups), 1)
        self.assertEqual(len(local_backups), 1)
        self.assertEqual(envrc_backups[0].read_text(), "# user envrc\n")
        self.assertEqual(local_backups[0].read_text(), "# user local env\n")
        self.assertIn("# user envrc", (project / ".envrc").read_text())
        self.assertIn("# user local env", (project / ".envrc.local").read_text())

    def test_codacy_repeat_setup_keeps_one_managed_section_and_preserves_content(self) -> None:
        project = self.make_project()
        result, home = self.run_project_setup(
            project,
            "3\n1\n1\nkairin\n000-dotfiles\nrepo-token\ny\n2\n5\n",
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        local_file = project / ".envrc.local"
        local_file.write_text(local_file.read_text() + "\n# user managed line\n")
        second_result, _home = self.run_project_setup(
            project,
            "4\n1\n1\nkairin\n000-dotfiles\n\ny\n2\n6\n",
            home=home,
        )

        self.assertEqual(second_result.returncode, 0, second_result.stdout + second_result.stderr)
        local_text = local_file.read_text()
        self.assertEqual(local_text.count("# BEGIN DOTFILES CODACY"), 1)
        self.assertEqual(local_text.count("# END DOTFILES CODACY"), 1)
        self.assertIn("# user managed line", local_text)
        self.assertEqual((home / ".codacy" / "kairin-000-dotfiles.project-token").read_text(), "repo-token\n")


if __name__ == "__main__":
    import unittest

    unittest.main()
