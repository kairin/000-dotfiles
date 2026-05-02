from tests.helpers import DotfilesTestCase, REPO_ROOT


class DocsTests(DotfilesTestCase):
    def test_readme_is_short_and_points_into_docs(self):
        readme = (REPO_ROOT / "README.md").read_text()
        self.assertIn("docs/README.md", readme)
        self.assertIn("docs/getting-started.md", readme)
        self.assertIn("docs/setup-reference.md", readme)
        self.assertIn("docs/validation.md", readme)
        self.assertIn("docs/architecture/setup-flow.md", readme)
        self.assertIn("docs/architecture/scaffold-flow.md", readme)
        self.assertIn("CHANGELOG.md", readme)
        self.assertIn("flowchart", readme)
        self.assertNotIn("dotfiles_tools doctor", readme)
        self.assertNotIn("coverage==7.5.4", readme)

    def test_docs_hub_points_to_the_split_pages(self):
        docs_readme = (REPO_ROOT / "docs/README.md").read_text()
        self.assertIn("Getting Started", docs_readme)
        self.assertIn("Setup Reference", docs_readme)
        self.assertIn("Repo Layout", docs_readme)
        self.assertIn("Protected Files", docs_readme)
        self.assertIn("Validation", docs_readme)
        self.assertIn("Troubleshooting", docs_readme)
        self.assertIn("architecture/setup-flow.md", docs_readme)
        self.assertIn("architecture/scaffold-flow.md", docs_readme)

    def test_coverage_config_targets_production_python_only(self):
        coveragerc = (REPO_ROOT / ".coveragerc").read_text()
        self.assertIn("source =", coveragerc)
        self.assertIn("dotfiles_tools", coveragerc)
        self.assertIn("tests/*", coveragerc)
        self.assertIn("docs/*", coveragerc)

    def test_setup_reference_contains_wrapper_and_direct_cli_commands(self):
        setup_ref = (REPO_ROOT / "docs/setup-reference.md").read_text()
        self.assertIn("./setup", setup_ref)
        self.assertIn("dotfiles_tools doctor", setup_ref)
        self.assertIn("bootstrap-apply", setup_ref)
        self.assertIn("dotfiles-setup verify", setup_ref)

    def test_validation_doc_mentions_pinned_coverage(self):
        validation = (REPO_ROOT / "docs/validation.md").read_text()
        self.assertIn("coverage==7.5.4", validation)
        self.assertIn(".coveragerc", validation)
        self.assertIn("Codacy Static Code Analysis", validation)

    def test_architecture_docs_cover_setup_and_scaffold_flows(self):
        setup_flow = (REPO_ROOT / "docs/architecture/setup-flow.md").read_text()
        scaffold_flow = (REPO_ROOT / "docs/architecture/scaffold-flow.md").read_text()
        self.assertIn("recommended option", setup_flow)
        self.assertIn("5-option menu", setup_flow)
        self.assertIn("project agent docs", scaffold_flow)
        self.assertIn("project-vars.json", scaffold_flow)
