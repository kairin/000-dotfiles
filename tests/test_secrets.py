from dotfiles_tools.secrets import scan_text
from tests.helpers import DotfilesTestCase


class SecretScanTests(DotfilesTestCase):
    def test_rejects_real_looking_tokens(self):
        findings = scan_text("OPENAI_API_KEY=sk-" + "a" * 30)
        self.assertEqual(findings[0].kind, "openai_key")

    def test_allows_documented_placeholders(self):
        self.assertEqual(scan_text("OPENAI_API_KEY={{OPENAI_API_KEY}}"), [])
        self.assertEqual(scan_text("# set -gx OPENAI_API_KEY (cat ~/.openai_token)"), [])
