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
        self.assertNotIn("{{PROJECT_NAME}}", (project / "AGENTS.md").read_text())
