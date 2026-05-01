from pathlib import Path
import copy

from dotfiles_tools.manifest import ManifestError, load_manifest, parse_manifest, validate_included_protected
from tests.helpers import DotfilesTestCase, REPO_ROOT


class ManifestTests(DotfilesTestCase):
    def test_manifest_loads_current_repo(self):
        manifest = load_manifest(REPO_ROOT)
        self.assertIn("machine", manifest.profiles)
        self.assertIn("git.config", manifest.entry_map())
        for entry in manifest.entries:
            self.assertFalse(Path(entry.source).is_absolute())
            self.assertFalse(Path(entry.target).is_absolute())

    def test_manifest_rejects_duplicates_unknown_profiles_and_missing_manual_reason(self):
        data = {
            "version": "1",
            "profiles": {"machine": {"entries": ["x"]}},
            "entries": [
                {"id": "x", "source": "README.md", "target": "x", "kind": "file", "profiles": ["machine"], "protected": True}
            ],
        }
        with self.assertRaises(ManifestError):
            parse_manifest(data, REPO_ROOT)
        bad = copy.deepcopy(data)
        bad["entries"][0]["protected"] = False
        bad["profiles"]["machine"]["entries"] = ["missing"]
        with self.assertRaises(ManifestError):
            parse_manifest(bad, REPO_ROOT)

    def test_include_protected_requires_exact_protected_id(self):
        manifest = load_manifest(REPO_ROOT)
        self.assertEqual(validate_included_protected(manifest, ["git.config"]), {"git.config"})
        with self.assertRaises(ManifestError):
            validate_included_protected(manifest, ["git/config"])
        with self.assertRaises(ManifestError):
            validate_included_protected(manifest, ["claude.settings"])
