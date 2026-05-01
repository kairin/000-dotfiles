from dotfiles_tools.project_init import init_project
from tests.helpers import DotfilesTestCase, REPO_ROOT


class ProjectInitBackupTests(DotfilesTestCase):
    def test_init_project_backs_up_drift_and_creates_copilot(self):
        project = self.make_project()
        (project / "AGENTS.md").write_text("old")
        vars_path = self.vars_file(project)
        report = init_project(REPO_ROOT, project, vars_path, yes=True, copilot=True)
        self.assertEqual(report.status, "ok")
        self.assertTrue(report.backups)
        self.assertTrue((project / ".github" / "copilot-instructions.md").exists())
