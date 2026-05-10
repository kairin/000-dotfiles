import re
import os
import subprocess  # nosec B404

from tests.helpers import DotfilesTestCase, REPO_ROOT


class WorkflowTests(DotfilesTestCase):
    def test_third_party_actions_are_pinned_to_full_commit_shas(self):
        mutable_refs = []
        action_ref = re.compile(r"^\s*uses:\s*['\"]?([^'\"\s#]+)")

        for workflow in sorted((REPO_ROOT / ".github/workflows").glob("*.yml")):
            for line_number, line in enumerate(workflow.read_text().splitlines(), 1):
                match = action_ref.match(line)
                if not match:
                    continue

                uses = match.group(1)
                if uses.startswith("./") or uses.startswith("actions/"):
                    continue

                _, _, ref = uses.partition("@")
                if not re.fullmatch(r"[0-9a-f]{40}", ref):
                    relative = workflow.relative_to(REPO_ROOT)
                    mutable_refs.append(f"{relative}:{line_number}: {uses}")

        self.assertEqual([], mutable_refs)

    def test_workflow_runs_tests_and_uploads_coverage(self):
        workflow = (REPO_ROOT / ".github/workflows/dotfiles-validation.yml").read_text()
        self.assertIn("name: Dotfiles Validation", workflow)
        # job name must stay codacy-safety-net — required by branch protection ruleset
        self.assertIn("codacy-safety-net:", workflow)
        self.assertIn("CODACY_ACCOUNT_TOKEN", workflow)
        self.assertIn("concurrency:", workflow)
        self.assertIn("coverage run -m unittest discover -s tests", workflow)
        self.assertIn("coverage xml", workflow)
        self.assertIn("coverage.xml", workflow)
        self.assertIn("coverage.codacy.com/get.sh", workflow)
        self.assertIn("continue-on-error: true", workflow)
        # Pinned action SHAs must be preserved.
        self.assertIn("actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd", workflow)
        self.assertIn("astral-sh/setup-uv@08807647e7069bb48b6ef5acd8ec9567f424441b", workflow)
        # Codacy CLI and quality pipeline must not run in CI — cloud analysis covers it.
        self.assertNotIn("codacy-cli", workflow)
        self.assertNotIn("quality-pipeline.sh", workflow)

    def test_quality_pipeline_is_non_blocking_and_uses_local_prereqs(self):
        pipeline = (REPO_ROOT / "scripts/quality-pipeline.sh").read_text()
        self.assertIn("exit 0", pipeline)
        # Stage 7 is the server-side Codacy gate; it stays informational so a
        # missing CODACY_PROJECT_TOKEN does not break local pre-push runs.
        self.assertIn("[STAGE 7/7] Codacy server-side gate", pipeline)
        # --codacy-only is a mode of quality-pipeline.sh used by ./setup ship
        # to refresh the SARIF upload after a merge. The pre-push hook does
        # NOT use this mode; Codacy enforcement runs in CI and at ship time.
        self.assertIn("--codacy-only", pipeline)
        # SARIF must be uploaded for both HEAD and merge-base so Codacy can
        # diff the PR; without the base upload, the GH App posts nothing.
        self.assertIn("upload_with_retry", pipeline)
        self.assertIn("git merge-base HEAD origin/main", pipeline)
        self.assertNotIn("CODACY_ACCOUNT_TOKEN", pipeline)
        self.assertNotIn("GITHUB_TOKEN", pipeline)

    def test_pre_push_blocks_direct_main_push_before_quality_checks(self):
        home = self.make_home()
        bin_dir = home / "bin"
        bin_dir.mkdir()
        fake_uv = bin_dir / "uv"
        fake_uv.write_text("#!/usr/bin/env bash\nexit 0\n")
        fake_uv.chmod(0o755)

        env = os.environ.copy()
        env["PATH"] = f"{bin_dir}:{env['PATH']}"
        env.pop("CODACY_PROJECT_TOKEN", None)

        hook = REPO_ROOT / "scripts/hooks/pre-push"
        result = subprocess.run(  # nosec B603
            [str(hook)],
            input="refs/heads/main 0000000000000000000000000000000000000000 refs/heads/main 1111111111111111111111111111111111111111\n",
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
            env=env,
            shell=False,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Direct pushes to main are blocked", result.stderr)
        self.assertNotIn("Running unit tests", result.stdout)

    def test_pre_push_allows_feature_branch_to_reach_quality_checks(self):
        home = self.make_home()
        bin_dir = home / "bin"
        bin_dir.mkdir()
        fake_uv = bin_dir / "uv"
        # Fake uv that handles radon cc by emitting complexity output, and unit tests by exiting 0
        fake_uv.write_text(
            "#!/usr/bin/env bash\n"
            "if [[ \"$*\" == *\"radon cc\"* ]]; then\n"
            '  echo "Average complexity: A (1.0)"\n'
            "  exit 0\n"
            "fi\n"
            "exit 0\n"
        )
        fake_uv.chmod(0o755)

        env = os.environ.copy()
        env["PATH"] = f"{bin_dir}:{env['PATH']}"
        env.pop("CODACY_PROJECT_TOKEN", None)

        hook = REPO_ROOT / "scripts/hooks/pre-push"
        result = subprocess.run(  # nosec B603
            [str(hook)],
            input="refs/heads/feature/example 0000000000000000000000000000000000000000 refs/heads/feature/example 1111111111111111111111111111111111111111\n",
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
            env=env,
            shell=False,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Running unit tests", result.stdout)
        self.assertIn("Ready to push to remote", result.stdout)
        # Pre-push must not invoke any Codacy stage; that lives in CI / ship.
        self.assertNotIn("[5/", result.stdout)
        self.assertNotIn("Codacy", result.stdout)

    def test_push_with_pr_refuses_main_branch(self):
        script = REPO_ROOT / "scripts/push-with-pr.sh"
        text = script.read_text()
        self.assertIn('BRANCH=$(git rev-parse --abbrev-ref HEAD)', text)
        self.assertIn('if [ "$BRANCH" = "main" ]', text)
