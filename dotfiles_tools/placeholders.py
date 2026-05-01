from __future__ import annotations

import re


PLACEHOLDER_RE = re.compile(r"\{\{([A-Z][A-Z0-9_]*)\}\}")


class PlaceholderError(ValueError):
    pass


def find_placeholders(text: str) -> list[str]:
    return sorted(set(PLACEHOLDER_RE.findall(text)))


def render_placeholders(text: str, values: dict[str, str], *, allow_unresolved: bool = False) -> str:
    def replace(match: re.Match[str]) -> str:
        name = match.group(1)
        if name in values:
            return str(values[name])
        return match.group(0)

    rendered = PLACEHOLDER_RE.sub(replace, text)
    unresolved = find_placeholders(rendered)
    if unresolved and not allow_unresolved:
        raise PlaceholderError(f"unresolved placeholders: {', '.join(unresolved)}")
    return rendered


def assert_no_unresolved(text: str, *, allow_examples: bool = False) -> list[str]:
    unresolved = find_placeholders(text)
    if unresolved and not allow_examples:
        raise PlaceholderError(f"unresolved placeholders: {', '.join(unresolved)}")
    return unresolved
