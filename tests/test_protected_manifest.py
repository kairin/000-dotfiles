from dotfiles_tools.manifest import load_manifest
from tests.helpers import DotfilesTestCase, REPO_ROOT


class ProtectedManifestTests(DotfilesTestCase):
    def test_protected_entries_have_expected_ids_and_reasons(self):
        manifest = load_manifest(REPO_ROOT)
        entries = manifest.entry_map()
        for entry_id in ["git.config", "fish.plugins", "repo.gitignore", "agents.claude-template", "agents.gemini-template"]:
            self.assertTrue(entries[entry_id].protected)
            self.assertTrue(entries[entry_id].manual_reason)
