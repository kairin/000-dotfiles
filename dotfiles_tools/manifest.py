from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any


class ManifestError(ValueError):
    """Raised when the manifest cannot be used safely."""


@dataclass(frozen=True)
class Profile:
    id: str
    description: str
    entries: tuple[str, ...]


@dataclass(frozen=True)
class ManifestEntry:
    id: str
    source: str
    target: str
    kind: str
    profiles: tuple[str, ...]
    protected: bool
    manual_reason: str | None = None
    parse: str | None = None
    placeholders: str = "none"
    link_target: str | None = None
    mode: str | None = None
    scope: str = "home"

    @property
    def source_path(self) -> Path:
        return Path(self.source)

    @property
    def target_path(self) -> Path:
        return Path(self.target)


@dataclass(frozen=True)
class ProjectInitConfig:
    agent_template: str
    symlinks: tuple[str, ...]
    copilot_template: str | None = None


@dataclass(frozen=True)
class Manifest:
    version: str
    profiles: dict[str, Profile]
    entries: tuple[ManifestEntry, ...]
    project_init: ProjectInitConfig

    def entry_map(self) -> dict[str, ManifestEntry]:
        return {entry.id: entry for entry in self.entries}

    def entries_for_profile(self, profile_id: str) -> list[ManifestEntry]:
        if profile_id not in self.profiles:
            raise ManifestError(f"unknown profile: {profile_id}")
        entries = self.entry_map()
        return [entries[entry_id] for entry_id in self.profiles[profile_id].entries]


def load_manifest(repo: Path | str) -> Manifest:
    repo_path = Path(repo).resolve()
    manifest_path = repo_path / "dotfiles-manifest.json"
    if not manifest_path.exists():
        raise ManifestError(f"manifest not found: {manifest_path}")
    try:
        data = json.loads(manifest_path.read_text())
    except json.JSONDecodeError as exc:
        raise ManifestError(f"manifest is invalid JSON: {exc}") from exc
    return parse_manifest(data, repo_path)


def parse_manifest(data: dict[str, Any], repo: Path) -> Manifest:
    if not isinstance(data, dict):
        raise ManifestError("manifest root must be an object")
    version = _required_str(data, "version")
    raw_profiles = data.get("profiles")
    raw_entries = data.get("entries")
    if not isinstance(raw_profiles, dict) or not raw_profiles:
        raise ManifestError("manifest profiles must be a non-empty object")
    if not isinstance(raw_entries, list) or not raw_entries:
        raise ManifestError("manifest entries must be a non-empty array")

    entries: list[ManifestEntry] = []
    seen: set[str] = set()
    for raw_entry in raw_entries:
        entry = _parse_entry(raw_entry)
        if entry.id in seen:
            raise ManifestError(f"duplicate entry id: {entry.id}")
        seen.add(entry.id)
        _validate_relative_path(entry.source, "source", allow_dotfile=True)
        _validate_relative_path(entry.target, "target", allow_dotfile=True)
        source_path = repo / entry.source
        if not source_path.exists() and not source_path.is_symlink():
            raise ManifestError(f"source path does not exist for {entry.id}: {entry.source}")
        if entry.protected and not entry.manual_reason:
            raise ManifestError(f"protected entry lacks manual_reason: {entry.id}")
        if entry.kind == "symlink" and not entry.link_target:
            raise ManifestError(f"symlink entry lacks link_target: {entry.id}")
        if entry.kind not in {"file", "template", "symlink"}:
            raise ManifestError(f"unsupported kind for {entry.id}: {entry.kind}")
        if entry.parse not in {None, "json", "toml"}:
            raise ManifestError(f"unsupported parse value for {entry.id}: {entry.parse}")
        if entry.placeholders not in {"required", "allowed_examples", "none"}:
            raise ManifestError(f"unsupported placeholders value for {entry.id}: {entry.placeholders}")
        if entry.scope not in {"home", "repo", "project"}:
            raise ManifestError(f"unsupported scope for {entry.id}: {entry.scope}")
        entries.append(entry)

    entry_ids = {entry.id for entry in entries}
    profiles: dict[str, Profile] = {}
    for profile_id, raw_profile in raw_profiles.items():
        if not isinstance(raw_profile, dict):
            raise ManifestError(f"profile must be an object: {profile_id}")
        raw_profile_entries = raw_profile.get("entries")
        if not isinstance(raw_profile_entries, list):
            raise ManifestError(f"profile entries must be an array: {profile_id}")
        refs = tuple(str(item) for item in raw_profile_entries)
        missing_refs = [entry_id for entry_id in refs if entry_id not in entry_ids]
        if missing_refs:
            raise ManifestError(f"profile {profile_id} references unknown entries: {', '.join(missing_refs)}")
        profiles[profile_id] = Profile(
            id=profile_id,
            description=str(raw_profile.get("description", "")),
            entries=refs,
        )

    profile_ids = set(profiles)
    for entry in entries:
        unknown_profiles = [profile_id for profile_id in entry.profiles if profile_id not in profile_ids]
        if unknown_profiles:
            raise ManifestError(f"entry {entry.id} references unknown profiles: {', '.join(unknown_profiles)}")

    project_init = _parse_project_init(data.get("project_init", {}))
    return Manifest(version=version, profiles=profiles, entries=tuple(entries), project_init=project_init)


def validate_included_protected(manifest: Manifest, include_ids: list[str] | tuple[str, ...] | None) -> set[str]:
    include_set = set(include_ids or [])
    entries = manifest.entry_map()
    invalid = [entry_id for entry_id in include_set if entry_id not in entries]
    if invalid:
        raise ManifestError(f"unknown protected entry id: {', '.join(sorted(invalid))}")
    not_protected = [entry_id for entry_id in include_set if not entries[entry_id].protected]
    if not_protected:
        raise ManifestError(f"include-protected requires protected entry ids: {', '.join(sorted(not_protected))}")
    return include_set


def resolve_source(repo: Path, entry: ManifestEntry) -> Path:
    return (repo.resolve() / entry.source).resolve()


def resolve_target(repo: Path, home: Path, entry: ManifestEntry, project: Path | None = None) -> Path:
    if entry.scope == "repo":
        root = repo.resolve()
    elif entry.scope == "project":
        if project is None:
            raise ManifestError(f"project root required for entry: {entry.id}")
        root = project.resolve()
    else:
        root = home.resolve()
    return (root / entry.target).resolve()


def _parse_entry(raw: Any) -> ManifestEntry:
    if not isinstance(raw, dict):
        raise ManifestError("manifest entry must be an object")
    profiles = raw.get("profiles")
    if not isinstance(profiles, list) or not profiles:
        raise ManifestError("manifest entry profiles must be a non-empty array")
    return ManifestEntry(
        id=_required_str(raw, "id"),
        source=_required_str(raw, "source"),
        target=_required_str(raw, "target"),
        kind=_required_str(raw, "kind"),
        profiles=tuple(str(item) for item in profiles),
        protected=bool(raw.get("protected", False)),
        manual_reason=raw.get("manual_reason"),
        parse=raw.get("parse"),
        placeholders=str(raw.get("placeholders", "none")),
        link_target=raw.get("link_target"),
        mode=raw.get("mode"),
        scope=str(raw.get("scope", "home")),
    )


def _parse_project_init(raw: Any) -> ProjectInitConfig:
    if not isinstance(raw, dict):
        raw = {}
    symlinks = raw.get("symlinks", ["CLAUDE.md", "GEMINI.md"])
    if not isinstance(symlinks, list):
        raise ManifestError("project_init.symlinks must be an array")
    return ProjectInitConfig(
        agent_template=str(raw.get("agent_template", "agents/AGENTS.md.template")),
        symlinks=tuple(str(item) for item in symlinks),
        copilot_template=raw.get("copilot_template"),
    )


def _required_str(data: dict[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value:
        raise ManifestError(f"missing required string: {key}")
    return value


def _validate_relative_path(value: str, label: str, allow_dotfile: bool = False) -> None:
    path = Path(value)
    if path.is_absolute():
        raise ManifestError(f"{label} path must be relative: {value}")
    if not value or value in {".", "./"} and not allow_dotfile:
        raise ManifestError(f"{label} path must not be empty: {value}")
    if any(part == ".." for part in path.parts):
        raise ManifestError(f"{label} path must not escape root: {value}")
