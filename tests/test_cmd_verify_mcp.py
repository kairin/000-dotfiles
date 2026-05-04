"""Regression coverage for `setup verify` MCP server check non-blocking behavior.

PR #165 appended ``|| true`` to the ``check_mcp_servers`` invocation in
``cmd_verify`` so that an MCP misconfiguration (e.g. unset ``GITHUB_TOKEN``)
no longer aborts ``setup verify`` under ``set -euo pipefail``. These tests
exercise that contract directly so any future regression — for example,
re-removing the ``|| true`` suffix — fails loudly.
"""

from __future__ import annotations

import json
import os
# Tests execute only the repo-local setup script.
import subprocess  # nosec B404
from pathlib import Path

from tests.helpers import REPO_ROOT, DotfilesTestCase


SETUP = REPO_ROOT / "setup"


def write_clean_project(project: Path) -> None:
    (project / "AGENTS.md").write_text("# Example Project\n\nrendered content.\n")
    (project / "CLAUDE.md").symlink_to("AGENTS.md")
    (project / "GEMINI.md").symlink_to("AGENTS.md")


class CmdVerifyMcpTests(DotfilesTestCase):
    """Validate that `setup verify` is not gated by `check_mcp_servers`."""

    def _sandbox_env(self, home: Path) -> dict[str, str]:
        """Return a minimal env that points HOME at a sandbox without leaking
        real MCP credentials. Inherits PATH so bash / python3 / coreutils are
        available, but scrubs every variable that the user's MCP servers might
        consume so a stale token cannot mask a regression."""
        env = {
            "PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"),
            "HOME": str(home),
            "LANG": os.environ.get("LANG", "C.UTF-8"),
        }
        # Strip any MCP-related credentials that the parent process may have
        # exported. The script reads these via ${!env_var:-} from inside
        # check_mcp_server_config; leaving them set would mask the failure
        # path we are trying to exercise.
        for var in ("GITHUB_TOKEN", "CODACY_ACCOUNT_TOKEN", "HF_TOKEN"):
            env.pop(var, None)
        return env

    def _run_verify(self, project: Path, home: Path) -> subprocess.CompletedProcess:
        # Fixed executable path, test-controlled args, shell=False.
        return subprocess.run(  # nosec B603
            [str(SETUP), "verify", "--project", str(project)],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
            env=self._sandbox_env(home),
            shell=False,
        )

    def _write_mcp_with_unset_env(self, home: Path) -> None:
        """Create ~/.claude.json declaring an MCP server whose required env
        var is guaranteed to be unset, forcing check_mcp_server_config to
        return 1 and therefore check_mcp_servers to return non-zero."""
        claude_json = home / ".claude.json"
        claude_json.write_text(
            json.dumps(
                {
                    "mcpServers": {
                        "github": {
                            "command": "bash",
                            "args": ["-c", "true"],
                            "env": {"GITHUB_TOKEN": "$GITHUB_TOKEN"},
                        }
                    }
                }
            )
        )

    def test_verify_exit_zero_when_github_token_unset(self) -> None:
        """When GITHUB_TOKEN is unset and an MCP server depends on it,
        check_mcp_servers returns non-zero. cmd_verify must still exit 0."""
        home = self.make_home()
        project = self.make_project()
        write_clean_project(project)
        self._write_mcp_with_unset_env(home)

        result = self._run_verify(project, home)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Verification passed.", result.stdout)
        self.assertIn("MCP server configuration:", result.stdout)
        # Confirm the warning surfaced (proving the check actually ran and
        # returned non-zero, which is what `|| true` is suppressing).
        self.assertIn("Environment variables not set", result.stdout)

    def test_verify_exit_zero_when_mcp_command_missing(self) -> None:
        """When the MCP server's `command` is not on PATH,
        check_mcp_server_config returns 1. cmd_verify must still exit 0."""
        home = self.make_home()
        project = self.make_project()
        write_clean_project(project)
        claude_json = home / ".claude.json"
        claude_json.write_text(
            json.dumps(
                {
                    "mcpServers": {
                        "definitely-not-installed": {
                            "command": "this-binary-does-not-exist-xyz123",
                            "args": [],
                            "env": {},
                        }
                    }
                }
            )
        )

        result = self._run_verify(project, home)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Verification passed.", result.stdout)
        self.assertIn("not available", result.stdout)

    def test_verify_exit_zero_when_no_claude_json(self) -> None:
        """Sanity: with no ~/.claude.json the MCP block is informational
        only; verify should still exit 0."""
        home = self.make_home()
        project = self.make_project()
        write_clean_project(project)
        # No ~/.claude.json written — check_mcp_servers should print and
        # return early without affecting cmd_verify's return code.

        result = self._run_verify(project, home)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Verification passed.", result.stdout)
        self.assertIn("~/.claude.json not found", result.stdout)

    def test_verify_still_fails_on_genuine_verification_error(self) -> None:
        """The non-blocking change must not have suppressed real failures.
        Missing AGENTS.md should still cause exit 1 even if the MCP check
        is configured to fail too."""
        home = self.make_home()
        project = self.make_project()
        # Deliberately do NOT write AGENTS.md / CLAUDE.md / GEMINI.md.
        # Also wire up a failing MCP config to prove the two failure
        # paths are independent.
        self._write_mcp_with_unset_env(home)

        result = self._run_verify(project, home)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("AGENTS.md missing", result.stdout)
        self.assertIn("Verification failed.", result.stdout)


if __name__ == "__main__":
    import unittest

    unittest.main()
