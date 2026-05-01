import json

from dotfiles_tools.project_init import init_project
from tests.helpers import DotfilesTestCase, REPO_ROOT


class ProjectInitReportTests(DotfilesTestCase):
    def test_json_report_includes_writes_symlinks_backups_and_errors(self):
        project = self.make_project()
        (project / "CLAUDE.md").write_text("old")
        vars_path = self.vars_file(project)
        report = init_project(REPO_ROOT, project, vars_path, yes=True)
        data = json.loads(report.to_json())
        self.assertIn("operations", data)
        self.assertIn("backups", data)
        self.assertTrue(any(op["type"] == "symlink" for op in data["operations"]))
        self.assertEqual(data["errors"], [])
