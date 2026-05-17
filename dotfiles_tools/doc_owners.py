"""Documentation hub-and-spoke owner map.

ARCHITECTURE.md is the canonical owner for every concept listed in CANONICAL.
Satellites that mirror a concept must carry a same-file
``<!-- mirrors: ARCHITECTURE.md#<anchor> -->`` comment near the mirrored content.

Used by tests/test_architecture.py and tests/test_docs.py to enforce the
hub-and-spoke convention. Update this file when a new canonical section is
added to ARCHITECTURE.md or when a satellite acquires a mirror.
"""

from __future__ import annotations

CANONICAL: dict[str, tuple[str, ...]] = {
    "overview": ("README.md", "AGENTS.md"),
    "system-design": ("README.md", "docs/getting-started.md"),
    "tool-catalog": ("README.md",),
    "auth-guidance": ("AGENTS.md", "docs/getting-started.md"),
    "protected-files-canonical-list": ("README.md", "AGENTS.md"),
    "mcp-tool-availability": ("AGENTS.md", "docs/getting-started.md"),
    "template-convention": ("AGENTS.md",),
    "symlink-convention": ("AGENTS.md",),
    "development-workflow": ("README.md", "AGENTS.md"),
    "python-module-architecture": (),
    "docker-based-browser-automation": ("README.md", "AGENTS.md"),
    "codacy-cli-configuration": ("AGENTS.md",),
    "hook-trigger-map": ("AGENTS.md",),
    "drift-prevention": (),
    "design-history": (),
}

REQUIRED_H2_ANCHORS: frozenset[str] = frozenset(CANONICAL.keys()) | {"toc"}
