from __future__ import annotations

import json
from pathlib import Path
import tomllib

from .manifest import ManifestEntry
from .placeholders import PlaceholderError, assert_no_unresolved


class TemplateError(ValueError):
    pass


def read_source(path: Path) -> str:
    return path.read_text()


def expected_text(source_path: Path, entry: ManifestEntry) -> str:
    if entry.kind == "symlink":
        return entry.link_target or ""
    return source_path.read_text()


def validate_template(source_path: Path, entry: ManifestEntry) -> list[str]:
    text = source_path.read_text()
    errors: list[str] = []
    try:
        if entry.parse == "json":
            json.loads(text)
        elif entry.parse == "toml":
            tomllib.loads(text)
    except Exception as exc:
        errors.append(f"{entry.parse} parse failed: {exc}")
    try:
        assert_no_unresolved(text, allow_examples=entry.placeholders == "allowed_examples")
    except PlaceholderError as exc:
        errors.append(str(exc))
    return errors
