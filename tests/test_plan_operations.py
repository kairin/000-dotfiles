from dotfiles_tools.installer import build_plan
from tests.helpers import DotfilesTestCase, REPO_ROOT


class PlanOperationTests(DotfilesTestCase):
    def test_plan_orders_mkdir_copy_backup_and_refuse(self):
        home = self.make_home()
        target = home / ".claude" / "settings.json"
        target.parent.mkdir(parents=True)
        target.write_text('{"drift": true}')
        report = build_plan(REPO_ROOT, home)
        op_types = [op["type"] for op in report.operations]
        self.assertLess(op_types.index("backup"), op_types.index("copy"))
        self.assertIn("mkdir", op_types)
        self.assertIn("refuse", op_types)
