import shutil

from dotfiles_tools.doctor import check_symlinks
from tests.helpers import DotfilesTestCase, REPO_ROOT


class DoctorSymlinkTests(DotfilesTestCase):
    def test_root_symlinks_are_intact_in_repo(self):
        entries = check_symlinks(REPO_ROOT)
        self.assertTrue(all(entry["state"] == "current" for entry in entries))

    def test_broken_symlink_is_reported(self):
        repo = self.make_project()
        shutil.copytree(REPO_ROOT / "agents", repo / "agents", symlinks=True)
        (repo / "AGENTS.md").write_text("ok")
        (repo / "CLAUDE.md").symlink_to("missing.md")
        (repo / "GEMINI.md").symlink_to("AGENTS.md")
        entries = check_symlinks(repo)
        bad = [entry for entry in entries if entry["entry_id"] == "symlink.CLAUDE.md"][0]
        self.assertEqual(bad["state"], "invalid")
