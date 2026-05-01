from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class SecretFinding:
    line: int
    kind: str
    value: str


SECRET_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("openai_key", re.compile(r"\bsk-[A-Za-z0-9]{20,}\b")),
    ("github_token", re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b")),
    ("github_pat", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{30,}\b")),
    ("huggingface_token", re.compile(r"\bhf_[A-Za-z0-9]{20,}\b")),
    ("slack_token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b")),
    ("aws_access_key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("private_key", re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----")),
)


def scan_text(text: str) -> list[SecretFinding]:
    findings: list[SecretFinding] = []
    for line_no, line in enumerate(text.splitlines(), 1):
        if "{{" in line and "}}" in line:
            continue
        for kind, pattern in SECRET_PATTERNS:
            for match in pattern.finditer(line):
                findings.append(SecretFinding(line=line_no, kind=kind, value=match.group(0)))
    return findings


def scan_file(path) -> list[SecretFinding]:
    return scan_text(path.read_text(errors="replace"))
