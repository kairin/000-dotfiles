from dotfiles_tools.reports import Report
from tests.helpers import DotfilesTestCase


class ReportTests(DotfilesTestCase):
    def test_json_report_has_stable_fields(self):
        report = Report("doctor", "warning", "/repo", home="/home", profile="machine", entries=[{"state": "missing"}])
        data = report.to_dict()
        self.assertEqual(data["command"], "doctor")
        self.assertEqual(data["summary"]["missing"], 1)
        self.assertIn("operations", data)

    def test_human_report_includes_status_and_entries(self):
        report = Report("plan", "warning", "/repo", operations=[{"operation_id": "op-001", "type": "copy", "entry_id": "x"}])
        text = report.to_human()
        self.assertIn("plan: warning", text)
        self.assertIn("op-001 copy x", text)
