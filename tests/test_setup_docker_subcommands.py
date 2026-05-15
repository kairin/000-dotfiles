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

    def test_help_documents_gstack_exec_setup_and_codex(self) -> None:
        result = _run_setup("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("gstack-exec", result.stdout)
        self.assertIn("gstack-setup", result.stdout)
        self.assertIn("gstack-codex", result.stdout)

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

    def test_docker_build_explains_inactive_docker_group(self) -> None:
        home = self.make_home()
        bin_dir = home / "bin"
        bin_dir.mkdir()
        for needed in ("bash", "basename", "cat", "dirname", "echo", "readlink", "uname"):
            src = shutil.which(needed)
            if src:
                (bin_dir / needed).symlink_to(src)
        fake_docker = bin_dir / "docker"
        fake_docker.write_text(
            "#!/usr/bin/env bash\n"
            "if [[ \"$1\" == \"info\" ]]; then\n"
            "  echo 'permission denied while trying to connect to the docker API' >&2\n"
            "  exit 1\n"
            "fi\n"
            "exit 0\n"
        )
        fake_docker.chmod(0o755)
        fake_id = bin_dir / "id"
        fake_id.write_text(
            "#!/usr/bin/env bash\n"
            "if [[ \"$1\" == \"-nG\" ]]; then echo 'kkk adm sudo'; exit 0; fi\n"
            "if [[ \"$1\" == \"-u\" ]]; then echo '1000'; exit 0; fi\n"
            "if [[ \"$1\" == \"-g\" ]]; then echo '1000'; exit 0; fi\n"
            "exit 0\n"
        )
        fake_id.chmod(0o755)
        fake_groups = bin_dir / "groups"
        fake_groups.write_text("#!/usr/bin/env bash\necho 'kkk : kkk adm sudo docker'\n")
        fake_groups.chmod(0o755)
        env = {"PATH": str(bin_dir), "HOME": str(home), "USER": "kkk"}
        result = _run_setup("docker-build", env=env, timeout=10.0)

        self.assertNotEqual(result.returncode, 0)
        output = result.stderr + result.stdout
        self.assertIn("Docker group membership is configured but not active", output)
        self.assertIn("util-linux-extra", output)

    def test_unknown_subcommand_still_rejected(self) -> None:
        # Sanity: adding new subcommands should not relax dispatching.
        result = _run_setup("not-a-real-subcommand", timeout=10.0)
        self.assertNotEqual(result.returncode, 0)

    def test_docker_build_uses_account_gid_not_active_newgrp_gid(self) -> None:
        home = self.make_home()
        bin_dir = home / "bin"
        bin_dir.mkdir()
        log_path = home / "docker.log"
        for needed in ("bash", "basename", "cat", "dirname", "echo", "readlink", "uname"):
            src = shutil.which(needed)
            if src:
                (bin_dir / needed).symlink_to(src)
        fake_docker = bin_dir / "docker"
        fake_docker.write_text(
            "#!/usr/bin/env bash\n"
            "printf '%s\\n' \"$*\" >> \"$DOCKER_LOG\"\n"
            "if [[ \"$1\" == \"info\" ]]; then exit 0; fi\n"
            "if [[ \"$1\" == \"build\" ]]; then exit 0; fi\n"
            "exit 0\n"
        )
        fake_docker.chmod(0o755)
        fake_id = bin_dir / "id"
        fake_id.write_text(
            "#!/usr/bin/env bash\n"
            "if [[ \"$1 $2\" == \"-u kkk\" ]]; then echo '1000'; exit 0; fi\n"
            "if [[ \"$1 $2\" == \"-g kkk\" ]]; then echo '1000'; exit 0; fi\n"
            "if [[ \"$1\" == \"-u\" ]]; then echo '1000'; exit 0; fi\n"
            "if [[ \"$1\" == \"-g\" ]]; then echo '973'; exit 0; fi\n"
            "if [[ \"$1\" == \"-un\" ]]; then echo 'kkk'; exit 0; fi\n"
            "exit 0\n"
        )
        fake_id.chmod(0o755)
        env = {
            "DOCKER_LOG": str(log_path),
            "HOME": str(home),
            "PATH": str(bin_dir),
            "USER": "kkk",
        }

        result = _run_setup("docker-build", env=env, timeout=10.0)

        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        log = log_path.read_text()
        self.assertIn("--build-arg HOST_UID=1000", log)
        self.assertIn("--build-arg HOST_GID=1000", log)
        self.assertNotIn("--build-arg HOST_GID=973", log)

    def test_gstack_setup_runs_repo_setup_inside_container(self) -> None:
        home = self.make_home()
        bin_dir = home / "bin"
        bin_dir.mkdir()
        workdir = home / "Apps" / "gstack"
        workdir.mkdir(parents=True)
        log_path = home / "docker.log"
        fake_docker = bin_dir / "docker"
        fake_docker.write_text(
            "#!/usr/bin/env bash\n"
            "printf '%s\\n' \"$*\" >> \"$DOCKER_LOG\"\n"
            "if [[ \"$1\" == \"info\" ]]; then exit 0; fi\n"
            "if [[ \"$1 $2\" == \"image inspect\" ]]; then exit 0; fi\n"
            "if [[ \"$1\" == \"ps\" ]]; then echo gstack-dev; exit 0; fi\n"
            "if [[ \"$1\" == \"exec\" ]]; then exit 0; fi\n"
            "exit 0\n"
        )
        fake_docker.chmod(0o755)
        fake_direnv = bin_dir / "direnv"
        fake_direnv.write_text("#!/usr/bin/env bash\nexit 1\n")
        fake_direnv.chmod(0o755)
        env = os.environ.copy()
        env.update({
            "DOCKER_LOG": str(log_path),
            "HOME": str(home),
            "PATH": f"{bin_dir}:{env.get('PATH', '')}",
            "USER": "kkk",
        })
        envfile = REPO_ROOT / "docker" / "gstack-browser" / ".env"
        previous_envfile = envfile.read_bytes() if envfile.exists() else None

        try:
            result = _run_setup(
                "gstack-setup",
                str(workdir),
                env=env,
                timeout=10.0,
            )
        finally:
            if previous_envfile is None:
                if envfile.exists():
                    envfile.unlink()
            else:
                envfile.write_bytes(previous_envfile)
                envfile.chmod(0o600)

        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertIn(
            f"exec -w {workdir} gstack-dev ./setup --host auto",
            log_path.read_text(),
        )

    def test_gstack_codex_runs_directly_inside_container_without_docker(self) -> None:
        home = self.make_home()
        workdir = home / "Apps" / "gstack"
        workdir.mkdir(parents=True)
        bin_dir = home / "bin"
        bin_dir.mkdir()
        log_path = home / "codex.log"
        for needed in ("bash", "basename", "cat", "dirname", "echo", "readlink", "uname"):
            src = shutil.which(needed)
            if src:
                (bin_dir / needed).symlink_to(src)
        fake_codex = bin_dir / "codex"
        fake_codex.write_text(
            "#!/usr/bin/env bash\n"
            "printf 'pwd=%s args=%s\\n' \"$PWD\" \"$*\" >> \"$CODEX_LOG\"\n"
        )
        fake_codex.chmod(0o755)
        env = {
            "CODEX_LOG": str(log_path),
            "GSTACK_CONTAINER": "1",
            "HOME": str(home),
            "PATH": str(bin_dir),
            "USER": "kkk",
        }

        result = _run_setup(
            "gstack-codex",
            str(workdir),
            "--",
            "--version",
            env=env,
            timeout=10.0,
        )

        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertIn("Already inside gstack-dev", result.stdout)
        self.assertEqual(log_path.read_text(), f"pwd={workdir} args=--version\n")


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
        for required_mount in ("/Apps:", "/.claude:", "/.codex:", "/.gstack:"):
            self.assertIn(required_mount, text,
                          f"compose missing required mount fragment: {required_mount}")

    def test_compose_configures_playwright_runtime_stability(self) -> None:
        text = (REPO_ROOT / "docker" / "gstack-browser" / "docker-compose.yml").read_text()
        self.assertIn("init: true", text)
        self.assertIn("GSTACK_CONTAINER:", text)
        self.assertTrue(
            "ipc: host" in text or "shm_size:" in text,
            "compose should avoid Chromium /dev/shm starvation",
        )

    def test_compose_env_file_is_gitignored(self) -> None:
        gi = (REPO_ROOT / "docker" / "gstack-browser" / ".gitignore").read_text()
        self.assertIn(".env", gi,
                      ".env contains tokens at runtime and must be gitignored")
