from dotfiles_tools.installer import build_plan
from tests.helpers import DotfilesTestCase, REPO_ROOT


class ProtectedPlanTests(DotfilesTestCase):
    def test_protected_entries_do_not_write_without_exact_inclusion(self):
        home = self.make_home()
        report = build_plan(REPO_ROOT, home)
        protected_ops = [op for op in report.operations if op["entry_id"] == "git.config"]
        self.assertEqual(protected_ops[0]["type"], "refuse")
        self.assertNotIn("copy", [op["type"] for op in protected_ops])
