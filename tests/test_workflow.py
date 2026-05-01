from pathlib import Path

from tests.helpers import DotfilesTestCase, REPO_ROOT


class WorkflowTests(DotfilesTestCase):
    def test_workflow_generates_coverage_and_gates_codacy_upload(self):
        workflow = (REPO_ROOT / ".github/workflows/dotfiles-validation.yml").read_text()
        self.assertIn("coverage run -m unittest discover -s tests", workflow)
        self.assertIn("coverage xml", workflow)
        self.assertIn("coverage.xml", workflow)
        self.assertIn("CODACY_API_TOKEN", workflow)
        self.assertIn("codacy/codacy-coverage-reporter-action@v1.3.0", workflow)
