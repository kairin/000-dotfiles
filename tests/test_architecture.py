import re

from tests.helpers import DotfilesTestCase, REPO_ROOT

from dotfiles_tools.doc_owners import CANONICAL, REQUIRED_H2_ANCHORS


ANCHOR_PATTERN = re.compile(r"<!-- anchor: ([a-z0-9-]+) -->")
MIRROR_PATTERN = re.compile(r"<!-- mirrors: ARCHITECTURE\.md#([a-z0-9-]+) -->")
H2_LINE_PATTERN = re.compile(r"^## (.+?)\s*(<!--.*-->)?\s*$")


def _read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


class ArchitectureHubTests(DotfilesTestCase):
    def test_every_h2_has_same_line_anchor_comment(self):
        arch = _read("ARCHITECTURE.md")
        missing: list[str] = []
        for line in arch.splitlines():
            if not line.startswith("## "):
                continue
            if "<!-- anchor: " not in line:
                missing.append(line)
        self.assertEqual(
            missing,
            [],
            "Every ARCHITECTURE.md H2 must carry a same-line "
            "<!-- anchor: slug --> comment. Missing on:\n  "
            + "\n  ".join(missing),
        )

    def test_required_anchors_present(self):
        arch = _read("ARCHITECTURE.md")
        found = set(ANCHOR_PATTERN.findall(arch))
        missing = REQUIRED_H2_ANCHORS - found
        self.assertEqual(
            missing,
            set(),
            "ARCHITECTURE.md missing required anchors: "
            + ", ".join(sorted(missing)),
        )

    def test_anchors_are_unique(self):
        arch = _read("ARCHITECTURE.md")
        anchors = ANCHOR_PATTERN.findall(arch)
        duplicates = {a for a in anchors if anchors.count(a) > 1}
        self.assertEqual(
            duplicates,
            set(),
            "Duplicate anchors in ARCHITECTURE.md: "
            + ", ".join(sorted(duplicates)),
        )

    def test_mirror_comments_resolve(self):
        """Every <!-- mirrors: ARCHITECTURE.md#x --> in a satellite must
        point at an existing anchor in the hub."""
        arch = _read("ARCHITECTURE.md")
        hub_anchors = set(ANCHOR_PATTERN.findall(arch))
        offenders: list[tuple[str, str]] = []
        for satellite in ("README.md", "AGENTS.md", "docs/getting-started.md"):
            try:
                text = _read(satellite)
            except FileNotFoundError:
                continue
            for slug in MIRROR_PATTERN.findall(text):
                if slug not in hub_anchors:
                    offenders.append((satellite, slug))
        self.assertEqual(
            offenders,
            [],
            "Satellite mirror comments reference missing hub anchors:\n  "
            + "\n  ".join(f"{f}: #{s}" for f, s in offenders),
        )

    def test_canonical_phrase_appears_only_in_hub(self):
        """The exact phrase 'Protected Files Canonical List' may only appear
        in ARCHITECTURE.md. Satellites must use 'Protected Files' or link out."""
        phrase = "Protected Files Canonical List"
        for satellite in ("README.md", "AGENTS.md", "docs/getting-started.md"):
            try:
                text = _read(satellite)
            except FileNotFoundError:
                continue
            self.assertNotIn(
                phrase,
                text,
                f"{satellite} contains the canonical hub heading "
                f"'{phrase}'; link to ARCHITECTURE.md instead.",
            )

    def test_doc_owner_map_keys_match_hub_anchors(self):
        arch = _read("ARCHITECTURE.md")
        hub_anchors = set(ANCHOR_PATTERN.findall(arch))
        unknown_owners = set(CANONICAL.keys()) - hub_anchors
        self.assertEqual(
            unknown_owners,
            set(),
            "dotfiles_tools/doc_owners.py CANONICAL lists anchors not in "
            "ARCHITECTURE.md: " + ", ".join(sorted(unknown_owners)),
        )
