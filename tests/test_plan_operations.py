from dotfiles_tools.installer import build_plan
from tests.helpers import DotfilesTestCase, REPO_ROOT


class PlanOperationTests(DotfilesTestCase):
    def test_plan_orders_mkdir_copy_and_refuse(self):
        home = self.make_home()
        report = build_plan(REPO_ROOT, home)
        op_types = [op["type"] for op in report.operations]
        self.assertIn("mkdir", op_types)
        self.assertIn("copy", op_types)
        self.assertIn("refuse", op_types)
        self.assertLess(op_types.index("mkdir"), op_types.index("copy"))
