from pathlib import Path

from dotfiles_tools.manifest import ManifestEntry
from dotfiles_tools.placeholders import PlaceholderError, assert_no_unresolved, find_placeholders
from dotfiles_tools.templates import validate_template
from tests.helpers import DotfilesTestCase


class TemplateTests(DotfilesTestCase):
    def test_json_and_toml_templates_parse(self):
        repo = self.make_project()
        json_path = repo / "settings.json.template"
        toml_path = repo / "config.toml.template"
        json_path.write_text('{"ok": true}')
        toml_path.write_text('model = "test"')
        self.assertEqual(validate_template(json_path, ManifestEntry("j", "settings.json.template", "x", "template", ("machine",), False, parse="json")), [])
        self.assertEqual(validate_template(toml_path, ManifestEntry("t", "config.toml.template", "x", "template", ("machine",), False, parse="toml")), [])

    def test_unresolved_placeholders_fail_unless_allowed_as_examples(self):
        self.assertEqual(find_placeholders("hello {{PROJECT_NAME}}"), ["PROJECT_NAME"])
        with self.assertRaises(PlaceholderError):
            assert_no_unresolved("hello {{PROJECT_NAME}}")
        self.assertEqual(assert_no_unresolved("hello {{PROJECT_NAME}}", allow_examples=True), ["PROJECT_NAME"])
