from dotfiles_tools.project_init import init_project
from tests.helpers import DotfilesTestCase, REPO_ROOT


class ProjectInitPlaceholderTests(DotfilesTestCase):
    def test_init_project_fails_when_placeholders_remain(self):
        project = self.make_project()
        vars_path = self.vars_file(project)
        vars_path.write_text('{"PROJECT_NAME":"Only Name"}')
        report = init_project(REPO_ROOT, project, vars_path, yes=True)
        self.assertEqual(report.status, "failed")
        self.assertIn("unresolved placeholders", report.errors[0]["message"])
        self.assertFalse((project / "AGENTS.md").exists())
