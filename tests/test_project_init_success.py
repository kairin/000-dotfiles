from dotfiles_tools.project_init import init_project
from tests.helpers import DotfilesTestCase, REPO_ROOT


class ProjectInitSuccessTests(DotfilesTestCase):
    def test_init_project_creates_agents_and_symlinks(self):
        project = self.make_project()
        vars_path = self.vars_file(project)
        report = init_project(REPO_ROOT, project, vars_path, yes=True)
        self.assertEqual(report.status, "ok")
        self.assertTrue((project / "AGENTS.md").exists())
        self.assertTrue((project / "CLAUDE.md").is_symlink())
        self.assertEqual(str((project / "CLAUDE.md").readlink()), "AGENTS.md")
        self.assertTrue((project / "GEMINI.md").is_symlink())
        agents_text = (project / "AGENTS.md").read_text()
        self.assertNotIn("{{PROJECT_NAME}}", agents_text)
        self.assertIn("Optional Codacy API Environment", agents_text)
        for variable in (
            "CODACY_PROJECT_TOKEN",
            "CODACY_API_TOKEN",
            "CODACY_ORGANIZATION_PROVIDER",
            "CODACY_USERNAME",
            "CODACY_PROJECT_NAME",
        ):
            self.assertIn(variable, agents_text)
        self.assertIn("Do not read, print, cat, copy, or commit", agents_text)
        self.assertIn("~/.codacy/", agents_text)

    def test_init_project_rejects_self_as_target(self):
        with self.assertRaises(ValueError) as ctx:
            init_project(REPO_ROOT, REPO_ROOT, "fake.json", yes=True)
        self.assertIn("Cannot run init_project against the dotfiles source repo", str(ctx.exception))
