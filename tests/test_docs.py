from tests.helpers import DotfilesTestCase, REPO_ROOT


class DocsTests(DotfilesTestCase):
    def test_readme_includes_canonical_commands_and_coverage(self):
        readme = (REPO_ROOT / "README.md").read_text()
        for command in ["doctor", "plan", "apply", "init-project"]:
            self.assertIn(f"dotfiles_tools {command}", readme)
        self.assertIn("uv run python -m unittest discover -s tests", readme)
        self.assertIn("coverage xml", readme)
        self.assertIn("docs/codacy-coverage-rollout.md", readme)
        self.assertIn("docs/operations/github-actions-usage-baseline.md", readme)

    def test_docs_cover_optional_codacy_environment_flow(self):
        getting_started = (REPO_ROOT / "docs" / "getting-started.md").read_text()
        rollout = (REPO_ROOT / "docs" / "codacy-coverage-rollout.md").read_text()
        fish_env = (REPO_ROOT / "fish" / "env.fish.template").read_text()

        combined_docs = getting_started + "\n" + rollout
        for text in (
            "Optional integrations and APIs",
            "Manage Codacy API access",
            "repository token",
            "account token",
            "~/.codacy/",
            "preview",
            "final confirmation",
            "backup",
            "direnv allow",
        ):
            self.assertIn(text, combined_docs)

        for variable in (
            "CODACY_PROJECT_TOKEN",
            "CODACY_API_TOKEN",
            "CODACY_ORGANIZATION_PROVIDER",
            "CODACY_USERNAME",
            "CODACY_PROJECT_NAME",
        ):
            self.assertIn(variable, combined_docs)

        self.assertIn("project optional integrations menu", fish_env)
        self.assertIn("Do not export Codacy tokens globally here", fish_env)
