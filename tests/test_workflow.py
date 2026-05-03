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
        # Pinned action SHAs must be preserved.
        self.assertIn("actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5", workflow)
        self.assertIn("astral-sh/setup-uv@d4b2f3b6ecc6e67c4457f6d3e41ec42d3d0fcb86", workflow)
