from tests.helpers import DotfilesTestCase, REPO_ROOT


class DocsTests(DotfilesTestCase):
    def test_readme_includes_canonical_commands_and_coverage(self):
        readme = (REPO_ROOT / "README.md").read_text()
        for command in ["doctor", "plan", "apply", "init-project"]:
            self.assertIn(f"dotfiles_tools {command}", readme)
        self.assertIn("uv run python -m unittest discover -s tests", readme)
        self.assertIn("coverage xml", readme)
        self.assertIn("docs/codacy-coverage-rollout.md", readme)
        self.assertIn("docs/codacy-workflow-templates.md", readme)
        self.assertIn("docs/operations/github-actions-usage-baseline.md", readme)

    def test_codacy_workflow_templates_cover_rollout_profiles(self):
        templates = (REPO_ROOT / "docs" / "codacy-workflow-templates.md").read_text()
        for text in (
            "Python uv + coverage.py",
            "Node npm/Vitest coverage",
            "Mixed Node + Python",
            "CODACY_API_TOKEN",
            "CODACY_ORGANIZATION_PROVIDER",
            "CODACY_USERNAME",
            "CODACY_PROJECT_NAME",
            "coverage.xml",
            "coverage/lcov.info",
        ):
            self.assertIn(text, templates)

    def test_docs_cover_optional_codacy_environment_flow(self):
        getting_started = (REPO_ROOT / "docs" / "getting-started.md").read_text()
        rollout = (REPO_ROOT / "docs" / "codacy-coverage-rollout.md").read_text()
        fish_env = (REPO_ROOT / "fish" / "conf.d" / "env.fish.template").read_text()

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

    def test_manifest_fish_env_target_is_conf_d(self):
        """T021: fish.env target path matches conf.d/ — catches regression if manifest reverts."""
        import json
        manifest = json.loads((REPO_ROOT / "dotfiles-manifest.json").read_text())
        fish_env = next(e for e in manifest["entries"] if e.get("id") == "fish.env")
        self.assertIn("conf.d", fish_env["target"])
        self.assertIn("conf.d", fish_env["source"])

    def test_codacy_rollout_has_required_checks_field(self):
        """T022: codacy-rollout.json has required_checks separate from expected_checks."""
        import json
        rollout = json.loads((REPO_ROOT / "codacy-rollout.json").read_text())
        dotfiles_entry = next(r for r in rollout["repositories"] if "000-dotfiles" in r["repo"])
        self.assertIn("required_checks", dotfiles_entry,
            "codacy-rollout.json must have required_checks distinct from expected_checks")
        self.assertIn("codacy-safety-net", dotfiles_entry["required_checks"])

    def test_quality_pipeline_claims_four_required_checks(self):
        """T025: quality-pipeline.sh must state all four Codacy checks are required.

        This test was inverted on 2026-05-16 (PR #254 follow-up). Original guard
        protected the Phase 2 policy where only ``codacy-safety-net`` was required;
        Phase 3 reversal made all four Codacy checks unconditionally required, so
        the script's banner must now actively claim that.
        """
        pipeline = (REPO_ROOT / "scripts" / "quality-pipeline.sh").read_text()
        self.assertIn("All four Codacy checks are required", pipeline)

    def test_architecture_hub_and_tests_present(self):
        """Sentinel for the hub-and-spoke docs convention.

        ARCHITECTURE.md and tests/test_architecture.py together enforce the
        single-source-of-truth pattern documented at
        ARCHITECTURE.md#drift-prevention. Removing either short-circuits the
        whole convention; this assertion lives in test_docs.py (already
        load-bearing) so it survives deletion of the architecture test file.
        """
        self.assertTrue(
            (REPO_ROOT / "ARCHITECTURE.md").is_file(),
            "ARCHITECTURE.md must exist — it is the canonical hub document.",
        )
        self.assertTrue(
            (REPO_ROOT / "tests" / "test_architecture.py").is_file(),
            "tests/test_architecture.py must exist — it enforces hub-and-spoke "
            "drift contracts. See ARCHITECTURE.md#drift-prevention.",
        )
