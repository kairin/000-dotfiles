from tests.helpers import DotfilesTestCase, REPO_ROOT


class WorkflowTests(DotfilesTestCase):
    def test_workflow_is_thin_codacy_safety_net(self):
        workflow = (REPO_ROOT / ".github/workflows/dotfiles-validation.yml").read_text()
        self.assertIn("name: Codacy Safety Net", workflow)
        self.assertIn("CODACY_PROJECT_TOKEN", workflow)
        self.assertIn("concurrency:", workflow)
        self.assertIn("codacy-safety-net-${{ github.ref }}", workflow)
        self.assertIn("quality-status", workflow)
        self.assertIn("steps.codacy_status.outputs.status == 'analyzed'", workflow)
        self.assertIn("steps.codacy_status.outputs.status != 'analyzed'", workflow)
        self.assertIn("scripts/quality-pipeline.sh", workflow)
        self.assertIn("coverage.xml", workflow)
        self.assertIn("codacy/codacy-coverage-reporter-action@89d6c85cfafaec52c72b6c5e8b2878d33104c699", workflow)
        self.assertIn("codacy-cli-v2/main/codacy-cli.sh) download", workflow)
        self.assertIn('ln -sf "$CLI_PATH" "$INSTALL_DIR/codacy-cli-v2"', workflow)
        self.assertIn('ln -sf "$CLI_PATH" "$INSTALL_DIR/codacy-cli"', workflow)
        self.assertIn("cache-dependency-glob:", workflow)
        self.assertIn("scripts/quality-pipeline.sh", workflow)
        # Pinned action SHAs must be preserved.
        self.assertIn("actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd", workflow)
        self.assertIn("astral-sh/setup-uv@08807647e7069bb48b6ef5acd8ec9567f424441b", workflow)

    def test_quality_pipeline_is_non_blocking_and_uses_local_prereqs(self):
        pipeline = (REPO_ROOT / "scripts/quality-pipeline.sh").read_text()
        self.assertIn("exit 0", pipeline)
        # Stage 7 is the server-side Codacy gate; it stays informational so a
        # missing CODACY_PROJECT_TOKEN does not break local pre-push runs.
        self.assertIn("[STAGE 7/7] Codacy server-side gate", pipeline)
        # --codacy-only is the entry point used by the pre-push hook.
        self.assertIn("--codacy-only", pipeline)
        # SARIF must be uploaded for both HEAD and merge-base so Codacy can
        # diff the PR; without the base upload, the GH App posts nothing.
        self.assertIn("upload_with_retry", pipeline)
        self.assertIn('git fetch --no-tags origin "+refs/heads/$target_branch:$BASE_REF"', pipeline)
        self.assertIn('git merge-base HEAD "$BASE_REF"', pipeline)
        self.assertIn('BASE_SHA="$(resolve_base_sha "$TARGET_BRANCH")"', pipeline)
        self.assertIn("Invalid SHA for Codacy upload", pipeline)
        self.assertNotIn("Skipping upload for invalid SHA", pipeline)
        self.assertNotIn("CODACY_ACCOUNT_TOKEN", pipeline)
        self.assertNotIn("GITHUB_TOKEN", pipeline)
