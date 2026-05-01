from dotfiles_tools.doctor import run_doctor
from tests.helpers import DotfilesTestCase, REPO_ROOT


class DoctorTests(DotfilesTestCase):
    def test_empty_temp_home_reports_missing_without_writes(self):
        home = self.make_home()
        before = sorted(home.rglob("*"))
        report = run_doctor(REPO_ROOT, home)
        after = sorted(home.rglob("*"))
        self.assertEqual(before, after)
        states = {entry["entry_id"]: entry["state"] for entry in report.entries}
        self.assertEqual(states["claude.settings"], "missing")
        self.assertEqual(states["git.config"], "protected")
        self.assertEqual(report.status, "warning")
