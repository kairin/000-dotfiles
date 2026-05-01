from dotfiles_tools.installer import apply_plan
from tests.helpers import DotfilesTestCase, REPO_ROOT


class ProtectedApplyTests(DotfilesTestCase):
    def test_exact_manifest_entry_id_required_for_protected_write(self):
        home = self.make_home()
        bad = apply_plan(REPO_ROOT, home, backup_dir=home / ".dotfiles-backups", yes=True, include_protected=["git/config"])
        self.assertEqual(bad.status, "failed")
        good = apply_plan(REPO_ROOT, home, backup_dir=home / ".dotfiles-backups", yes=True, include_protected=["git.config"])
        self.assertTrue((home / ".config" / "git" / "config").exists())
        self.assertNotEqual(good.status, "failed")
