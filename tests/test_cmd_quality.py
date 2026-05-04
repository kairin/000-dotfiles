from __future__ import annotations

import os
import shlex
# Tests execute only the repo-local setup script.
import subprocess  # nosec B404
import unittest
from pathlib import Path

from tests.helpers import REPO_ROOT, DotfilesTestCase


SETUP = REPO_ROOT / "setup"


def run_setup_quality(
    *args: str,
    cwd: Path,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess:
    # Fixed executable path, test-controlled args, shell=False.
    return subprocess.run(  # nosec B603
        [str(SETUP), "quality", *args],
        capture_output=True,
        text=True,
        cwd=str(cwd),
        env=env,
        shell=False,
    )


class CmdQualityTests(DotfilesTestCase):
    """Tests for the `setup quality` subcommand added in PR #169.

    The subcommand wraps `scripts/quality-pipeline.sh` from the git repo root.
    These tests stand up a temp git repo with a stub pipeline script so they
    are fully independent of the production `scripts/quality-pipeline.sh`.
    """

    def make_fake_repo(self) -> Path:
        repo = self.make_project()
        # Bootstrap a minimal git repository so `git rev-parse --show-toplevel`
        # resolves to this directory when the setup script runs.
        subprocess.run(  # nosec B603 B607
            ["git", "init", "-q"],
            cwd=str(repo),
            check=True,
        )
        return repo

    def make_nested_dir(self, repo: Path) -> Path:
        nested = repo / "subdir" / "deeper"
        nested.mkdir(parents=True, exist_ok=True)
        return nested

    def write_pipeline_stub(
        self,
        repo: Path,
        body: str,
        *,
        executable: bool = True,
    ) -> Path:
        scripts_dir = repo / "scripts"
        scripts_dir.mkdir(exist_ok=True)
        pipeline = scripts_dir / "quality-pipeline.sh"
        pipeline.write_text(body)
        if executable:
            pipeline.chmod(0o755)
        else:
            pipeline.chmod(0o644)
        return pipeline

    def env_with_path(self) -> dict[str, str]:
        # Inherit the parent PATH so bash, git, and friends resolve.
        env = os.environ.copy()
        return env

    def test_quality_succeeds_when_pipeline_is_executable(self) -> None:
        repo = self.make_fake_repo()
        cwd = self.make_nested_dir(repo)
        marker = repo / "ran.txt"
        self.write_pipeline_stub(
            repo,
            f"#!/usr/bin/env bash\necho \"ran pipeline\"\ntouch {shlex.quote(str(marker))}\nexit 0\n",
        )

        result = run_setup_quality(cwd=cwd, env=self.env_with_path())

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("ran pipeline", result.stdout)
        self.assertTrue(marker.exists(), "stub pipeline did not run")

    def test_quality_fails_outside_git_repository(self) -> None:
        cwd = self.make_project()

        result = run_setup_quality(cwd=cwd, env=self.env_with_path())

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("must run inside a git repository", result.stderr)

    def test_quality_fails_when_pipeline_script_missing(self) -> None:
        repo = self.make_fake_repo()
        # No scripts/quality-pipeline.sh created.

        result = run_setup_quality(cwd=repo, env=self.env_with_path())

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("quality pipeline script missing or not executable", result.stderr)
        self.assertIn(str(repo / "scripts" / "quality-pipeline.sh"), result.stderr)

    def test_quality_fails_when_pipeline_not_executable(self) -> None:
        repo = self.make_fake_repo()
        self.write_pipeline_stub(
            repo,
            "#!/usr/bin/env bash\nexit 0\n",
            executable=False,
        )

        result = run_setup_quality(cwd=repo, env=self.env_with_path())

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("quality pipeline script missing or not executable", result.stderr)

    def test_quality_propagates_pipeline_exit_code(self) -> None:
        repo = self.make_fake_repo()
        self.write_pipeline_stub(
            repo,
            "#!/usr/bin/env bash\necho \"failing on purpose\"\nexit 7\n",
        )

        result = run_setup_quality(cwd=repo, env=self.env_with_path())

        self.assertEqual(result.returncode, 7, result.stdout + result.stderr)
        self.assertIn("failing on purpose", result.stdout)

    @unittest.expectedFailure
    def test_quality_passes_extra_args_to_pipeline(self) -> None:
        """Extra args after `setup quality` should reach the pipeline script.

        The current implementation in setup uses `exec bash "$pipeline"`
        without forwarding `"$@"`, so extra arguments are dropped. Unit 2's
        quality-pipeline overhaul is expected to add `"$@"` forwarding so a
        user can run `./setup quality 123` to scope the pipeline to PR 123.
        Marked as expected failure until that change lands; once it does, this
        test will start passing and the decorator should be removed.
        """
        repo = self.make_fake_repo()
        log = repo / "args.log"
        self.write_pipeline_stub(
            repo,
            f"#!/usr/bin/env bash\nprintf '%s\\n' \"$@\" > {shlex.quote(str(log))}\nexit 0\n",
        )

        result = run_setup_quality("123", "extra", cwd=repo, env=self.env_with_path())

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(log.exists(), "pipeline did not record received args")
        recorded = log.read_text().splitlines()
        self.assertEqual(recorded, ["123", "extra"])


if __name__ == "__main__":
    unittest.main()
