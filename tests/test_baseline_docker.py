"""Validate the Docker TOOL_BASELINE entry that powers the gstack-browser
container workflow. These are pure-data assertions on the TOOL_BASELINE
tuple — they do not require a Docker daemon.
"""
from __future__ import annotations

from dotfiles_tools.baseline import TOOL_BASELINE
from tests.helpers import DotfilesTestCase, REPO_ROOT


def _docker_entry() -> dict:
    for item in TOOL_BASELINE:
        if item["id"] == "docker":
            return item
    raise AssertionError("docker entry missing from TOOL_BASELINE")


class DockerBaselineEntryTests(DotfilesTestCase):
    def test_entry_present_with_required_top_level_fields(self) -> None:
        entry = _docker_entry()
        for field in ("id", "label", "command", "bootstrap", "install_method",
                      "install_args", "requires_sudo", "install_hint", "post_install"):
            self.assertIn(field, entry, f"missing required field: {field}")

    def test_uses_apt_keyring_method(self) -> None:
        entry = _docker_entry()
        self.assertEqual(entry["install_method"], "apt_keyring")

    def test_install_args_include_keyring_and_source(self) -> None:
        args = _docker_entry()["install_args"]
        self.assertIn("docker-ce", args["packages"])
        self.assertIn("docker-compose-plugin", args["packages"])
        self.assertTrue(args["keyring_url"].startswith("https://download.docker.com/"))
        self.assertEqual(args["keyring_path"], "/etc/apt/keyrings/docker.gpg")
        self.assertTrue(args["source_path"].endswith(".sources"),
                        "should use deb822 format for parity with the gh entry")

    def test_source_line_contains_arch_placeholder(self) -> None:
        # _execute_apt_keyring substitutes {ARCH} via dpkg --print-architecture.
        # An entry missing the placeholder would fail on non-amd64 hosts.
        self.assertIn("{ARCH}", _docker_entry()["install_args"]["source_line"])

    def test_source_line_uses_noble_suite(self) -> None:
        # Ubuntu 26.04 has no Docker repo; the noble (24.04) repo is the
        # canonical fallback and works across recent Ubuntu releases.
        self.assertIn("Suites: noble", _docker_entry()["install_args"]["source_line"])

    def test_post_install_contains_usermod_and_build_steps(self) -> None:
        actions = _docker_entry()["post_install"]
        labels = [action["label"] for action in actions]
        self.assertTrue(any("docker group" in label for label in labels),
                        f"expected docker-group action; got labels: {labels}")
        self.assertTrue(any("gstack-browser" in label for label in labels),
                        f"expected gstack-browser build action; got labels: {labels}")

    def test_post_install_kinds_are_valid(self) -> None:
        # Only 'auto' and 'guidance' are accepted by _filter_post_install_actions.
        for action in _docker_entry()["post_install"]:
            self.assertIn(action["kind"], {"auto", "guidance"},
                          f"invalid kind for {action.get('label')}: {action['kind']}")

    def test_post_install_templates_use_only_supported_placeholders(self) -> None:
        # _render_post_install_template only supports {user} and {which:NAME}.
        # Other {token} expressions silently downgrade the action to guidance,
        # which would be a surprise if marked kind=auto.
        for action in _docker_entry()["post_install"]:
            if action["kind"] != "auto":
                continue
            for token in action["command_template"]:
                if not (token.startswith("{") and token.endswith("}")):
                    continue
                expr = token[1:-1]
                self.assertTrue(
                    expr == "user" or expr.startswith("which:"),
                    f"auto action {action['label']!r} uses unsupported "
                    f"placeholder {token}; this will downgrade to guidance",
                )


class DockerImageContextTests(DotfilesTestCase):
    """Sanity checks on the repo-side files referenced by post_install."""

    def test_dockerfile_present(self) -> None:
        self.assertTrue((REPO_ROOT / "docker" / "gstack-browser" / "Dockerfile").exists())

    def test_compose_file_present(self) -> None:
        self.assertTrue((REPO_ROOT / "docker" / "gstack-browser" / "docker-compose.yml").exists())

    def test_dockerfile_pins_playwright_base(self) -> None:
        text = (REPO_ROOT / "docker" / "gstack-browser" / "Dockerfile").read_text()
        self.assertIn("mcr.microsoft.com/playwright:", text,
                      "Dockerfile should base on the official Playwright image")
        self.assertIn("-noble", text,
                      "Dockerfile should use the Ubuntu 24.04 (Noble) variant")

    def test_dockerfile_accepts_host_user_uid_gid_args(self) -> None:
        text = (REPO_ROOT / "docker" / "gstack-browser" / "Dockerfile").read_text()
        for arg in ("HOST_UID", "HOST_GID", "HOST_USER"):
            self.assertIn(f"ARG {arg}", text,
                          f"Dockerfile missing ARG {arg}; container will not match host ownership")
