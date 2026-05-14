"""Verify the docker-build and gstack-shell setup subcommands are wired up.

These tests do not require Docker — they exercise the subcommand dispatch
and `--help` documentation only. Real container builds are manual.
"""
from __future__ import annotations

import os
import shutil
import subprocess  # nosec B404
from pathlib import Path

from tests.helpers import REPO_ROOT, DotfilesTestCase


SETUP = REPO_ROOT / "setup"


def _run_setup(
    *args: str,
    cwd: Path = REPO_ROOT,
    env: dict[str, str] | None = None,
    timeout: float = 10.0,
) -> subprocess.CompletedProcess:
    return subprocess.run(  # nosec B603
        [str(SETUP), *args],
        capture_output=True,
        text=True,
        cwd=str(cwd),
        env=env,
        timeout=timeout,
        shell=False,
    )


class SetupDockerSubcommandsTests(DotfilesTestCase):
    def test_help_documents_docker_build(self) -> None:
        result = _run_setup("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("docker-build", result.stdout)
        self.assertIn("gstack-browser", result.stdout)

    def test_help_documents_gstack_shell(self) -> None:
        result = _run_setup("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("gstack-shell", result.stdout)

    def test_docker_build_fails_clearly_without_docker(self) -> None:
        # Run with a minimal PATH that excludes `docker`. The subcommand
        # should fail via `require_cmd docker` (exit 2) rather than crash.
        minimal_bin = self.make_home() / "bin"
        minimal_bin.mkdir()
        for needed in ("bash", "id", "uname", "cat", "echo", "readlink", "dirname"):
            src = shutil.which(needed)
            if src and not (minimal_bin / needed).exists():
                (minimal_bin / needed).symlink_to(src)
        env = {"PATH": str(minimal_bin), "HOME": str(self.make_home())}
        result = _run_setup("docker-build", env=env, timeout=10.0)
        self.assertNotEqual(result.returncode, 0,
                            "expected setup docker-build to fail without docker on PATH")
        # require_cmd dies with exit 2 and ERROR message.
        self.assertIn("ERROR", result.stderr + result.stdout)
        self.assertIn("docker", result.stderr + result.stdout)

    def test_unknown_subcommand_still_rejected(self) -> None:
        # Sanity: adding new subcommands should not relax dispatching.
        result = _run_setup("not-a-real-subcommand", timeout=10.0)
        self.assertNotEqual(result.returncode, 0)


class DockerComposeFileShapeTests(DotfilesTestCase):
    """Spot-check the docker-compose.yml — full YAML parsing avoided to
    keep tests stdlib-only (no PyYAML dependency in this project)."""

    def test_compose_file_present_and_references_image(self) -> None:
        compose = REPO_ROOT / "docker" / "gstack-browser" / "docker-compose.yml"
        text = compose.read_text()
        self.assertIn("gstack-browser:latest", text)
        self.assertIn("container_name: gstack-dev", text)
        self.assertIn("restart: unless-stopped", text)

    def test_compose_mounts_critical_host_paths(self) -> None:
        text = (REPO_ROOT / "docker" / "gstack-browser" / "docker-compose.yml").read_text()
        # The path-preservation invariant: host paths mounted at identical
        # container paths. Skill files use absolute paths; mismatches are silent.
        for required_mount in ("/Apps:", "/.claude:", "/.gstack:"):
            self.assertIn(required_mount, text,
                          f"compose missing required mount fragment: {required_mount}")

    def test_compose_env_file_is_gitignored(self) -> None:
        gi = (REPO_ROOT / "docker" / "gstack-browser" / ".gitignore").read_text()
        self.assertIn(".env", gi,
                      ".env contains tokens at runtime and must be gitignored")
