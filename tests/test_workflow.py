import re

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
        self.assertIn("coverage.codacy.com/get.sh", workflow)
        self.assertIn("continue-on-error: true", workflow)
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
        self.assertIn("git merge-base HEAD origin/main", pipeline)
        self.assertNotIn("CODACY_ACCOUNT_TOKEN", pipeline)
        self.assertNotIn("GITHUB_TOKEN", pipeline)
