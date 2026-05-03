from tests.helpers import DotfilesTestCase, REPO_ROOT


class WorkflowTests(DotfilesTestCase):
    def test_workflow_generates_coverage_and_gates_codacy_upload(self):
        workflow = (REPO_ROOT / ".github/workflows/dotfiles-validation.yml").read_text()
        self.assertIn("coverage:", workflow)
        self.assertIn("codacy-static-analysis:", workflow)
        self.assertIn("codacy-cli-v2/main/codacy-cli.sh) download", workflow)
        self.assertIn('ln -sf "$cli_path" "$HOME/.local/bin/codacy-cli"', workflow)
        self.assertIn("codacy-cli analyze --tool pylint --format sarif -o pylint.sarif", workflow)
        self.assertIn("codacy-cli upload -s pylint.sarif", workflow)
        self.assertIn("CODACY_COMMIT_SHA", workflow)
        self.assertIn("coverage run -m unittest discover -s tests", workflow)
        self.assertIn("coverage xml", workflow)
        self.assertIn("coverage.xml", workflow)
        self.assertIn("CODACY_PROJECT_TOKEN", workflow)
        self.assertIn("github.event_name == 'push'", workflow)
        self.assertIn("project-token:", workflow)
        self.assertIn("codacy/codacy-coverage-reporter-action@89d6c85cfafaec52c72b6c5e8b2878d33104c699", workflow)
