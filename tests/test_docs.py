from tests.helpers import DotfilesTestCase, REPO_ROOT


class DocsTests(DotfilesTestCase):
    def test_readme_includes_canonical_commands_and_coverage(self):
        readme = (REPO_ROOT / "README.md").read_text()
        for command in ["doctor", "plan", "apply", "init-project"]:
            self.assertIn(f"dotfiles_tools {command}", readme)
        self.assertIn("uv run python -m unittest discover -s tests", readme)
        self.assertIn("coverage xml", readme)
