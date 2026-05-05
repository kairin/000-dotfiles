from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from dotfiles_tools.doctor import check_codacy_envrc_local_drift


MANAGED_BLOCK_WITHOUT_TOKENS = """\
# BEGIN DOTFILES CODACY
export CODACY_ORGANIZATION_PROVIDER="gh"
export CODACY_USERNAME="kairin"
export CODACY_PROJECT_NAME="000-dotfiles"
# END DOTFILES CODACY
"""

MANAGED_BLOCK_WITH_BOTH = """\
# BEGIN DOTFILES CODACY
export CODACY_ORGANIZATION_PROVIDER="gh"
export CODACY_API_TOKEN="$(cat "$HOME/.codacy/account-token")"
export CODACY_PROJECT_TOKEN="$(cat "$HOME/.codacy/foo.project-token")"
# END DOTFILES CODACY
"""


class DoctorCodacyDriftTests(unittest.TestCase):
    def setUp(self):
        self._tmps: list[Path] = []

    def tearDown(self):
        for path in self._tmps:
            shutil.rmtree(path, ignore_errors=True)

    def _mkdir(self, prefix: str) -> Path:
        path = Path(tempfile.mkdtemp(prefix=prefix))
        self._tmps.append(path)
        return path

    def _setup(self, *, envrc: str | None, account_token: bool, project_tokens: list[str]) -> tuple[Path, Path]:
        repo = self._mkdir("dotfiles-repo-")
        home = self._mkdir("dotfiles-home-")
        if envrc is not None:
            (repo / ".envrc.local").write_text(envrc)
        codacy_dir = home / ".codacy"
        codacy_dir.mkdir()
        if account_token:
            (codacy_dir / "account-token").write_text("dummy-account-token\n")
        for name in project_tokens:
            (codacy_dir / name).write_text("dummy-project-token\n")
        return repo, home

    def test_doctor_warns_when_account_token_file_exists_but_not_exported(self):
        repo, home = self._setup(
            envrc=MANAGED_BLOCK_WITHOUT_TOKENS,
            account_token=True,
            project_tokens=[],
        )
        entries = check_codacy_envrc_local_drift(repo, home)
        self.assertEqual(len(entries), 1)
        entry = entries[0]
        self.assertEqual(entry["entry_id"], "codacy.envrc-local.CODACY_API_TOKEN")
        self.assertEqual(entry["state"], "drifted")
        self.assertIn("CODACY_API_TOKEN", entry["reason"])
        self.assertIn("account-token", entry["reason"])
        self.assertIn("./setup repair-codacy-env", entry["reason"])

    def test_doctor_warns_when_project_token_file_exists_but_not_exported(self):
        repo, home = self._setup(
            envrc=MANAGED_BLOCK_WITHOUT_TOKENS,
            account_token=False,
            project_tokens=["kairin-000-dotfiles.project-token"],
        )
        entries = check_codacy_envrc_local_drift(repo, home)
        self.assertEqual(len(entries), 1)
        entry = entries[0]
        self.assertEqual(entry["entry_id"], "codacy.envrc-local.CODACY_PROJECT_TOKEN")
        self.assertEqual(entry["state"], "drifted")
        self.assertIn("CODACY_PROJECT_TOKEN", entry["reason"])
        self.assertIn("kairin-000-dotfiles.project-token", entry["reason"])
        self.assertIn("./setup repair-codacy-env", entry["reason"])

    def test_doctor_silent_when_token_file_and_export_both_present(self):
        repo, home = self._setup(
            envrc=MANAGED_BLOCK_WITH_BOTH,
            account_token=True,
            project_tokens=["foo.project-token"],
        )
        self.assertEqual(check_codacy_envrc_local_drift(repo, home), [])

    def test_doctor_silent_when_no_token_files_at_all(self):
        repo, home = self._setup(
            envrc=MANAGED_BLOCK_WITHOUT_TOKENS,
            account_token=False,
            project_tokens=[],
        )
        self.assertEqual(check_codacy_envrc_local_drift(repo, home), [])

    def test_doctor_silent_when_envrc_local_does_not_exist(self):
        repo, home = self._setup(
            envrc=None,
            account_token=True,
            project_tokens=["kairin-000-dotfiles.project-token"],
        )
        self.assertEqual(check_codacy_envrc_local_drift(repo, home), [])

    def test_doctor_silent_when_codacy_dir_does_not_exist(self):
        repo = self._mkdir("dotfiles-repo-")
        home = self._mkdir("dotfiles-home-")
        (repo / ".envrc.local").write_text(MANAGED_BLOCK_WITHOUT_TOKENS)
        self.assertEqual(check_codacy_envrc_local_drift(repo, home), [])

    def test_doctor_export_outside_managed_block_does_not_satisfy_check(self):
        envrc = (
            "export CODACY_API_TOKEN=$(cat ~/.codacy/account-token)\n"
            + MANAGED_BLOCK_WITHOUT_TOKENS
        )
        repo, home = self._setup(
            envrc=envrc,
            account_token=True,
            project_tokens=[],
        )
        entries = check_codacy_envrc_local_drift(repo, home)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["entry_id"], "codacy.envrc-local.CODACY_API_TOKEN")


if __name__ == "__main__":
    unittest.main()
