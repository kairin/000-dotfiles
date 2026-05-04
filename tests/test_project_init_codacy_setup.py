import json

from dotfiles_tools.project_init import init_project
from tests.helpers import DotfilesTestCase, REPO_ROOT


class ProjectInitCodacySetupGuidanceTests(DotfilesTestCase):
    def test_guidance_present_on_success(self):
        project = self.make_project()
        vars_path = self.vars_file(project)
        report = init_project(REPO_ROOT, project, vars_path, yes=True)
        self.assertEqual(report.status, "ok")
        guidance = report.extra.get("codacy_setup_guidance")
        self.assertIsNotNone(guidance)
        self.assertEqual(guidance["tool"], "mcp__codacy__codacy_setup_repository")
        self.assertIn("codacy_setup_repository", guidance["guidance"])
        self.assertEqual(guidance["project"], str(project))

    def test_guidance_absent_on_failure(self):
        project = self.make_project()
        vars_path = self.vars_file(project)
        report = init_project(REPO_ROOT, project, vars_path, yes=False)
        self.assertEqual(report.status, "failed")
        self.assertNotIn("codacy_setup_guidance", report.extra)

    def test_guidance_in_json_output(self):
        project = self.make_project()
        vars_path = self.vars_file(project)
        report = init_project(REPO_ROOT, project, vars_path, yes=True)
        data = json.loads(report.to_json())
        self.assertIn("codacy_setup_guidance", data)
        guidance = data["codacy_setup_guidance"]
        self.assertEqual(guidance["tool"], "mcp__codacy__codacy_setup_repository")

    def test_guidance_in_human_output(self):
        project = self.make_project()
        vars_path = self.vars_file(project)
        report = init_project(REPO_ROOT, project, vars_path, yes=True)
        human = report.to_human()
        self.assertIn("codacy setup guidance:", human)
        self.assertIn("mcp__codacy__codacy_setup_repository", human)
        self.assertIn("codacy_setup_repository", human)
