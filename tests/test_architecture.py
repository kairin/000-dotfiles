import re

from tests.helpers import DotfilesTestCase, REPO_ROOT

from dotfiles_tools.doc_owners import CANONICAL, REQUIRED_H2_ANCHORS


ANCHOR_PATTERN = re.compile(r"<!-- anchor: ([a-z0-9-]+) -->")
MIRROR_PATTERN = re.compile(r"<!-- mirrors: ARCHITECTURE\.md#([a-z0-9-]+) -->")
H2_LINE_PATTERN = re.compile(r"^## (.+?)\s*(<!--.*-->)?\s*$")


def _read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


class ArchitectureHubTests(DotfilesTestCase):
    def test_every_h2_has_anchor_comment_on_next_line(self):
        """Each ARCHITECTURE.md H2 must be followed by an
        ``<!-- anchor: slug -->`` line. The anchor lives on the line
        immediately after the heading so it does not pollute GitHub's
        auto-derived slug (markdownlint MD051 trips on inline HTML)."""
        arch_lines = _read("ARCHITECTURE.md").splitlines()
        missing: list[str] = []
        for idx, line in enumerate(arch_lines):
            if not line.startswith("## "):
                continue
            next_line = arch_lines[idx + 1] if idx + 1 < len(arch_lines) else ""
            if not ANCHOR_PATTERN.search(next_line):
                missing.append(f"line {idx + 1}: {line!r}")
        self.assertEqual(
            missing,
            [],
            "Every ARCHITECTURE.md H2 must have an <!-- anchor: slug --> "
            "comment on the line immediately following it. Missing on:\n  "
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
