from __future__ import annotations

import base64
from dataclasses import dataclass
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess  # nosec B404
import urllib.request
import zipfile
from typing import Any, Mapping

from .backups import create_backup


NERD_FONTS_RELEASE_URL = "https://api.github.com/repos/ryanoasis/nerd-fonts/releases/latest"
NERD_FONTS_REPO = "ryanoasis/nerd-fonts"
FONT_CACHE_REL = Path(".cache/000-dotfiles/fonts")
FONT_INSTALL_BASE_REL = Path(".local/share/fonts")
FONT_MARKER_NAME = ".000-dotfiles-font-source.json"
WINDOWS_TERMINAL_PACKAGES = (
    "Microsoft.WindowsTerminal_8wekyb3d8bbwe",
    "Microsoft.WindowsTerminalPreview_8wekyb3d8bbwe",
)

FONT_ASSET_NAME = "JetBrainsMono.zip"
FONT_FACE = "JetBrainsMono Nerd Font Mono"
FONT_LABEL = "JetBrainsMono Nerd Font"
FONT_ENTRY_ID = "fonts.jetbrains-mono-nerd"
FONT_INSTALL_REL = FONT_INSTALL_BASE_REL / "JetBrainsMonoNerdFont"
FONT_EXTRACTED_DIR = "JetBrainsMono"
FONT_ARCHIVE_NAME = FONT_ASSET_NAME
FONT_VERSION_NAME = "JetBrainsMono.version.json"
EXPECTED_TTF = "JetBrainsMonoNerdFontMono-Regular.ttf"
WINDOWS_ENTRY_ID = "fonts.windows-host"
PIXEL_TTYD_ENTRY_ID = "fonts.pixel-ttyd"
PIXEL_AVF_ENTRY_ID = "fonts.pixel-avf-prompt"
PIXEL_TTYD_FONT_ALIAS = "JBMono NF"
PIXEL_AVF_PROMPT_REL = Path(".config/fish/conf.d/000-dotfiles-pixel-avf-prompt.fish")


@dataclass(frozen=True)
class NerdFontItem:
    entry_id: str
    label: str
    family: str
    asset_name: str
    install_dir_name: str
    terminal_face: str
    expected_regular: str

    @property
    def cache_stem(self) -> str:
        return Path(self.asset_name).stem


NERD_FONT_CATALOG: tuple[NerdFontItem, ...] = (
    NerdFontItem(
        FONT_ENTRY_ID,
        FONT_LABEL,
        "JetBrainsMono",
        FONT_ASSET_NAME,
        "JetBrainsMonoNerdFont",
        FONT_FACE,
        EXPECTED_TTF,
    ),
    NerdFontItem(
        "fonts.fira-code-nerd",
        "FiraCode Nerd Font",
        "FiraCode",
        "FiraCode.zip",
        "FiraCodeNerdFont",
        "FiraCode Nerd Font Mono",
        "FiraCodeNerdFontMono-Regular.ttf",
    ),
    NerdFontItem(
        "fonts.hack-nerd",
        "Hack Nerd Font",
        "Hack",
        "Hack.zip",
        "HackNerdFont",
        "Hack Nerd Font Mono",
        "HackNerdFontMono-Regular.ttf",
    ),
    NerdFontItem(
        "fonts.meslo-nerd",
        "MesloLGS Nerd Font",
        "MesloLGS",
        "Meslo.zip",
        "MesloNerdFont",
        "MesloLGS Nerd Font Mono",
        "MesloLGSNerdFontMono-Regular.ttf",
    ),
)

APT_FONT_CATALOG: tuple[dict[str, str], ...] = (
    {
        "entry_id": "fonts.apt.noto-color-emoji",
        "family": "Noto Color Emoji",
        "package": "fonts-noto-color-emoji",
        "terminal_face": "Noto Color Emoji",
    },
    {
        "entry_id": "fonts.apt.symbola",
        "family": "Symbola",
        "package": "fonts-symbola",
        "terminal_face": "Symbola",
    },
    {
        "entry_id": "fonts.apt.freefont",
        "family": "GNU FreeFont",
        "package": "fonts-freefont-ttf",
        "terminal_face": "FreeMono",
    },
    {
        "entry_id": "fonts.apt.dejavu-core",
        "family": "DejaVu Core",
        "package": "fonts-dejavu-core",
        "terminal_face": "DejaVu Sans Mono",
    },
)


class FontError(RuntimeError):
    """Raised when a font recipe cannot complete."""


class CommandRunner:
    def __init__(self, *, env: Mapping[str, str] | None = None, path: str | None = None) -> None:
        self.env = dict(os.environ if env is None else env)
        self.path = path if path is not None else self.env.get("PATH", "")

    def which(self, command: str) -> str | None:
        return shutil.which(command, path=self.path)

    def run(self, args: list[str], *, capture_output: bool = False, check: bool = True) -> subprocess.CompletedProcess[str]:
        env = dict(self.env)
        env["PATH"] = self.path
        # codacy-disable-next-line
        return subprocess.run(  # nosec B603  # nosemgrep
            args,
            check=check,
            capture_output=capture_output,
            text=True,
            env=env,
            shell=False,
        )

    def fetch_json(self, url: str) -> dict[str, Any]:
        request = urllib.request.Request(
            url,
            headers={"Accept": "application/vnd.github+json", "User-Agent": "000-dotfiles-bootstrap"},
        )
        with urllib.request.urlopen(request, timeout=20) as response:  # nosec B310
            return json.loads(response.read().decode("utf-8"))

    def download(self, url: str, target: Path) -> None:
        target.parent.mkdir(parents=True, exist_ok=True)
        tmp = target.with_suffix(target.suffix + ".tmp")
        request = urllib.request.Request(url, headers={"User-Agent": "000-dotfiles-bootstrap"})
        with urllib.request.urlopen(request, timeout=60) as response:  # nosec B310
            tmp.write_bytes(response.read())
        tmp.replace(target)


def select_nerd_font_asset(release: Mapping[str, Any], asset_name: str = FONT_ASSET_NAME) -> dict[str, Any]:
    for asset in release.get("assets") or []:
        if asset.get("name") == asset_name and asset.get("browser_download_url"):
            return {
                "name": asset["name"],
                "browser_download_url": asset["browser_download_url"],
                "size": asset.get("size"),
                "tag_name": release.get("tag_name") or release.get("name") or "latest",
            }
    raise FontError(f"{asset_name} not found in latest {NERD_FONTS_REPO} release")


def build_font_plan(
    home: Path | str,
    *,
    env: Mapping[str, str] | None = None,
    path: str | None = None,
    runner: CommandRunner | None = None,
) -> dict[str, Any]:
    home_path = Path(home).expanduser().resolve()
    effective_env = dict(os.environ if env is None else env)
    effective_path = path if path is not None else effective_env.get("PATH", "")
    runner_was_provided = runner is not None
    effective_runner = runner or CommandRunner(env=effective_env, path=effective_path)
    context = _detect_context(home_path, effective_env, effective_path, effective_runner)

    if context["platform"] == "unsupported":
        return _build_unsupported_plan(home_path, context)
    if context["platform"] == "pixel-avf":
        return _build_pixel_avf_plan(home_path, context)

    release = _release_metadata(home_path, effective_env, effective_runner, fetch=runner_was_provided)
    entries: list[dict[str, Any]] = []
    operations: list[dict[str, Any]] = []
    fonts: list[dict[str, Any]] = []

    for item in _nerd_items_for_platform(context["platform"]):
        summary = _nerd_font_summary(home_path, context, item, release)
        entries.append(_font_entry(summary))
        fonts.append(summary)
        if summary["state"] in {"missing", "needs_update"}:
            operations.extend(_nerd_font_operations(home_path, item, reason=summary["reason"]))

    for item in _apt_items_for_platform(context["platform"]):
        summary = _apt_font_summary(context, item, effective_runner)
        entries.append(_font_entry(summary))
        fonts.append(summary)
        if summary["state"] in {"missing", "needs_update"}:
            operations.append(_apt_package_operation(summary))

    if context["platform"] == "wsl":
        jetbrains = next(item for item in NERD_FONT_CATALOG if item.entry_id == FONT_ENTRY_ID)
        jetbrains_summary = next(item for item in fonts if item["entry_id"] == FONT_ENTRY_ID)
        windows_entry, windows_ops, windows_summary = _windows_host_plan(home_path, context, jetbrains, jetbrains_summary)
        entries.append(windows_entry)
        operations.extend(windows_ops)
        jetbrains_summary["host_action"] = windows_summary["host_action"]

    if context["platform"] == "pixel-terminal":
        jetbrains_summary = next(item for item in fonts if item["entry_id"] == FONT_ENTRY_ID)
        pixel_entry, pixel_ops, pixel_summary = _pixel_ttyd_plan(home_path, context, jetbrains_summary)
        entries.append(pixel_entry)
        operations.extend(pixel_ops)
        jetbrains_summary["host_action"] = pixel_summary["host_action"]
        jetbrains_summary["requires_sudo"] = True
        jetbrains_summary["terminal_impact"] = pixel_summary["terminal_impact"]
        jetbrains_summary["embedded_alias"] = PIXEL_TTYD_FONT_ALIAS

    return {"entries": entries, "operations": operations, "fonts": fonts, "context": context}


def execute_font_operation(
    op: dict[str, Any],
    *,
    runner: CommandRunner | None = None,
    backup_dir: Path | None = None,
    backups: list[dict[str, Any]] | None = None,
) -> int:
    effective_runner = runner or CommandRunner()
    backup_path = backup_dir or Path.home() / ".dotfiles-backups"
    backup_records = backups if backups is not None else []
    op_type = op["type"]
    if op_type in {"font_skip", "font_manual"}:
        return 0
    if op_type == "font_download":
        return _execute_download(op, effective_runner)
    if op_type == "font_extract":
        return _execute_extract(op)
    if op_type == "font_install_linux":
        return _execute_install_linux(op)
    if op_type == "font_rebuild_cache":
        return _execute_rebuild_cache(op, effective_runner)
    if op_type == "font_verify_linux":
        return _execute_verify_linux(op, effective_runner)
    if op_type == "font_install_packages":
        return _execute_install_packages(op, effective_runner)
    if op_type == "font_install_windows":
        return _execute_install_windows(op, effective_runner)
    if op_type == "font_update_windows_terminal":
        return _execute_update_windows_terminal(op, backup_path, backup_records)
    if op_type == "font_ttyd_write_html":
        return _execute_ttyd_html(op, effective_runner, backup_records)
    if op_type == "font_ttyd_write_service":
        return _execute_ttyd_service(op, effective_runner, backup_records)
    if op_type == "font_systemd_daemon_reload":
        effective_runner.run(["sudo", "systemctl", "daemon-reload"])
        return 1
    if op_type == "font_systemd_restart":
        effective_runner.run(["sudo", "systemctl", "restart", "ttyd.service"])
        return 1
    if op_type == "font_pixel_avf_prompt":
        return _execute_pixel_avf_prompt(op)
    raise FontError(f"unknown font operation: {op_type}")


def _detect_context(home: Path, env: Mapping[str, str], path: str, runner: CommandRunner) -> dict[str, Any]:
    override = (env.get("DOTFILES_PLATFORM") or "").strip().lower()
    if override in {"linux", "native-linux", "ubuntu"}:
        platform_id = "linux"
    elif override in {"pi", "raspberry-pi", "raspberrypi"}:
        platform_id = "pi"
    elif override in {"wsl", "wsl-linux", "wsl2"}:
        platform_id = "wsl"
    elif override in {"pixel-terminal", "pixel_ttyd", "ttyd"}:
        platform_id = "pixel-terminal"
    elif override in {"pixel-avf", "avf"}:
        platform_id = "pixel-avf"
    elif _is_wsl(env):
        platform_id = "wsl"
    elif _is_raspberry_pi():
        platform_id = "pi"
    elif Path("/etc/ttyd").exists() or Path("/etc/systemd/system/ttyd.service").exists():
        platform_id = "pixel-terminal"
    else:
        platform_id = "linux" if platform.system().lower() == "linux" else "unsupported"

    return {
        "platform": platform_id,
        "architecture": platform.machine().lower(),
        "path": path,
        "powershell": runner.which("powershell.exe"),
        "wslpath": runner.which("wslpath"),
        "windows_terminal_settings": _discover_windows_terminal_settings(home, env),
    }


def _is_wsl(env: Mapping[str, str]) -> bool:
    if env.get("WSL_DISTRO_NAME") or env.get("WSL_INTEROP"):
        return True
    try:
        return "microsoft" in Path("/proc/version").read_text(errors="ignore").lower()
    except OSError:
        return False


def _is_raspberry_pi() -> bool:
    try:
        return "raspberry pi" in Path("/proc/device-tree/model").read_text(errors="ignore").lower()
    except OSError:
        return False


def _discover_windows_terminal_settings(home: Path, env: Mapping[str, str]) -> str | None:
    explicit = env.get("DOTFILES_WINDOWS_TERMINAL_SETTINGS")
    if explicit:
        path = Path(explicit)
        return str(path) if path.exists() else None
    users_root = Path("/mnt/c/Users")
    if not users_root.exists():
        return None
    candidates: list[Path] = []
    for user_dir in users_root.glob("*"):
        for package in WINDOWS_TERMINAL_PACKAGES:
            candidates.append(user_dir / "AppData/Local/Packages" / package / "LocalState/settings.json")
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    return None


def _release_metadata(home: Path, env: Mapping[str, str], runner: CommandRunner, *, fetch: bool) -> dict[str, Any]:
    cache_path = home / FONT_CACHE_REL / "nerd-fonts.latest.json"
    if _truthy(env.get("DOTFILES_FONT_OFFLINE")):
        return _read_version(cache_path)
    if fetch or _truthy(env.get("DOTFILES_FONT_CHECK_LATEST")):
        try:
            release = runner.fetch_json(NERD_FONTS_RELEASE_URL)
        except Exception as exc:
            cached = _read_version(cache_path)
            if cached:
                cached["lookup_error"] = str(exc)
            return cached
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(json.dumps(release, indent=2, sort_keys=True) + "\n")
        return release
    return _read_version(cache_path)


def _truthy(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def _nerd_items_for_platform(platform_id: str) -> tuple[NerdFontItem, ...]:
    if platform_id == "pixel-terminal":
        return (NERD_FONT_CATALOG[0],)
    if platform_id in {"linux", "wsl", "pi"}:
        return NERD_FONT_CATALOG
    return ()


def _apt_items_for_platform(platform_id: str) -> tuple[dict[str, str], ...]:
    if platform_id in {"linux", "wsl"}:
        return APT_FONT_CATALOG
    if platform_id == "pi":
        return tuple(item for item in APT_FONT_CATALOG if item["package"] != "fonts-dejavu-core")
    if platform_id == "pixel-terminal":
        return tuple(item for item in APT_FONT_CATALOG if item["package"] == "fonts-noto-color-emoji")
    return ()


def _paths(home: Path) -> dict[str, Path]:
    return _nerd_paths(home, NERD_FONT_CATALOG[0])


def _nerd_paths(home: Path, item: NerdFontItem) -> dict[str, Path]:
    cache_dir = home / FONT_CACHE_REL
    return {
        "cache_dir": cache_dir,
        "archive": cache_dir / item.asset_name,
        "version": cache_dir / f"{item.cache_stem}.version.json",
        "extract_dir": cache_dir / item.cache_stem,
        "install_dir": home / FONT_INSTALL_BASE_REL / item.install_dir_name,
    }


def _nerd_font_summary(home: Path, context: dict[str, Any], item: NerdFontItem, release: Mapping[str, Any]) -> dict[str, Any]:
    paths = _nerd_paths(home, item)
    installed_files = _installed_font_files(paths["install_dir"])
    installed_version = _read_version(paths["install_dir"] / FONT_MARKER_NAME)
    cached_version = _read_version(paths["version"])
    latest_version = _release_tag_for_asset(release, item.asset_name) or cached_version.get("tag_name")
    installed_tag = installed_version.get("tag_name") if installed_version else None
    cached_tag = cached_version.get("tag_name") if cached_version else None
    if not installed_files:
        state = "missing"
        reason = f"{item.label} is not installed in the user font directory"
    elif latest_version and installed_tag and installed_tag != latest_version:
        state = "needs_update"
        reason = f"installed {installed_tag} but latest is {latest_version}"
    elif not latest_version and cached_tag and installed_tag and installed_tag != cached_tag:
        state = "needs_update"
        reason = f"installed {installed_tag} but cached archive is {cached_tag}"
    else:
        state = "installed"
        reason = f"user-local {item.label} files are present"

    return {
        "entry_id": item.entry_id,
        "label": item.label,
        "family": item.family,
        "source_type": "nerd_font_release",
        "source": f"GitHub latest release asset {NERD_FONTS_REPO}/{item.asset_name}",
        "asset_name": item.asset_name,
        "state": state,
        "installed_version": installed_tag,
        "latest_version": latest_version,
        "cached_version": cached_tag,
        "candidate_version": None,
        "target": str(paths["install_dir"]),
        "cache_path": str(paths["archive"]),
        "terminal_face": item.terminal_face,
        "platform": context["platform"],
        "requires_sudo": False,
        "terminal_impact": _terminal_impact(context["platform"]),
        "host_action": _host_action(context),
        "reason": reason,
    }


def _release_tag_for_asset(release: Mapping[str, Any], asset_name: str) -> str | None:
    if not release:
        return None
    try:
        select_nerd_font_asset(release, asset_name)
    except FontError:
        return None
    tag = release.get("tag_name") or release.get("name")
    return str(tag) if tag else None


def _apt_font_summary(context: dict[str, Any], item: dict[str, str], runner: CommandRunner) -> dict[str, Any]:
    installed_version, installed_reason = _apt_installed_version(item["package"], runner)
    candidate_version, candidate_reason = _apt_candidate_version(item["package"], runner)
    if installed_reason or candidate_reason:
        state = "manual"
        reason = installed_reason or candidate_reason or "apt metadata unavailable"
    elif not installed_version:
        state = "missing"
        reason = f"{item['package']} is not installed"
    elif candidate_version and installed_version != candidate_version:
        state = "needs_update"
        reason = f"installed {installed_version} but apt candidate is {candidate_version}"
    else:
        state = "installed"
        reason = f"{item['package']} is installed"

    return {
        "entry_id": item["entry_id"],
        "label": item["family"],
        "family": item["family"],
        "source_type": "apt_package",
        "source": "apt",
        "package": item["package"],
        "state": state,
        "installed_version": installed_version,
        "latest_version": None,
        "candidate_version": candidate_version,
        "target": item["package"],
        "cache_path": None,
        "terminal_face": item["terminal_face"],
        "platform": context["platform"],
        "requires_sudo": state in {"missing", "needs_update"},
        "terminal_impact": _terminal_impact(context["platform"]),
        "host_action": _host_action(context),
        "reason": reason,
    }


def _apt_installed_version(package: str, runner: CommandRunner) -> tuple[str | None, str | None]:
    dpkg_query = runner.which("dpkg-query")
    if not dpkg_query:
        return None, "dpkg-query not found; apt package state must be checked manually"
    result = runner.run([dpkg_query, "-W", "-f=${Version}", package], capture_output=True, check=False)
    if result.returncode != 0:
        return None, None
    version = (result.stdout or "").strip()
    return version or None, None


def _apt_candidate_version(package: str, runner: CommandRunner) -> tuple[str | None, str | None]:
    apt_cache = runner.which("apt-cache")
    if not apt_cache:
        return None, "apt-cache not found; apt candidate state must be checked manually"
    result = runner.run([apt_cache, "policy", package], capture_output=True, check=False)
    if result.returncode != 0:
        return None, f"apt-cache policy failed for {package}"
    for line in (result.stdout or "").splitlines():
        text = line.strip()
        if text.startswith("Candidate:"):
            candidate = text.split(":", 1)[1].strip()
            return None if candidate == "(none)" else candidate, None
    return None, None


def _font_entry(summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "entry_id": summary["entry_id"],
        "source": summary["source"],
        "source_type": summary["source_type"],
        "family": summary["family"],
        "target": summary["target"],
        "state": summary["state"],
        "protected": False,
        "reason": summary["reason"],
        "recipe": "fonts",
        "cache_path": summary.get("cache_path"),
        "terminal_face": summary.get("terminal_face"),
        "requires_sudo": summary["requires_sudo"],
        "terminal_impact": summary["terminal_impact"],
        "host_action": summary["host_action"],
    }


def _terminal_impact(platform_id: str) -> str:
    if platform_id == "wsl":
        return "Linux terminals get Nerd Font Mono faces; Windows Terminal is updated when its settings file is discoverable."
    if platform_id == "pixel-terminal":
        return "Pixel Terminal ttyd pages use an embedded JetBrainsMono Nerd Font Mono subset."
    if platform_id == "pi":
        return "Local Linux terminal apps can select Nerd Font Mono faces; emoji/symbol fallbacks are installed with apt."
    if platform_id == "pixel-avf":
        return "Pixel AVF weston-terminal ignores Nerd Font configuration; a plain prompt fallback is used."
    return "Local Linux terminal apps can select Nerd Font Mono faces after install."


def _host_action(context: dict[str, Any]) -> str:
    platform_id = context["platform"]
    if platform_id == "wsl":
        if context.get("powershell") and context.get("windows_terminal_settings"):
            return "PowerShell installs JetBrainsMono Nerd Font Mono on Windows and Windows Terminal defaults are updated."
        if context.get("powershell"):
            return "PowerShell installs JetBrainsMono Nerd Font Mono on Windows; set Windows Terminal manually if no settings file is found."
        return "Manual Windows host font install required because powershell.exe was not found."
    if platform_id == "pixel-terminal":
        return "sudo writes /etc/ttyd/index.html and ttyd.service, then restarts ttyd.service."
    if platform_id == "pixel-avf":
        return "No host font action; weston-terminal ignores Nerd Font UI configuration."
    return "No host-side action."


def _nerd_font_operations(home: Path, item: NerdFontItem, *, reason: str) -> list[dict[str, Any]]:
    paths = _nerd_paths(home, item)
    base = {
        "entry_id": item.entry_id,
        "family": item.family,
        "requires_approval": True,
        "recipe": "fonts",
    }
    return [
        {
            **base,
            "type": "font_download",
            "source": NERD_FONTS_RELEASE_URL,
            "target": str(paths["archive"]),
            "asset_name": item.asset_name,
            "reason": f"download latest {item.asset_name} or reuse cached archive",
            "requires_network": True,
        },
        {
            **base,
            "type": "font_extract",
            "source": str(paths["archive"]),
            "target": str(paths["extract_dir"]),
            "asset_name": item.asset_name,
            "terminal_face": item.terminal_face,
            "reason": f"extract {item.label} font files",
        },
        {
            **base,
            "type": "font_install_linux",
            "source": str(paths["extract_dir"]),
            "target": str(paths["install_dir"]),
            "version_source": str(paths["version"]),
            "reason": reason,
        },
        {
            **base,
            "type": "font_rebuild_cache",
            "target": str(paths["install_dir"]),
            "reason": "run fc-cache for the user-local font directory when available",
        },
        {
            **base,
            "type": "font_verify_linux",
            "target": str(paths["install_dir"]),
            "terminal_face": item.terminal_face,
            "reason": f"verify {item.terminal_face} through fontconfig when available",
        },
    ]


def _apt_package_operation(summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "entry_id": summary["entry_id"],
        "type": "font_install_packages",
        "source": "apt",
        "source_type": "apt_package",
        "target": summary["target"],
        "packages": [summary["package"]],
        "candidate_version": summary.get("candidate_version"),
        "reason": summary["reason"],
        "requires_approval": True,
        "requires_sudo": True,
        "recipe": "fonts",
    }


def _windows_host_plan(
    home: Path,
    context: dict[str, Any],
    item: NerdFontItem,
    font_summary: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any]]:
    operations: list[dict[str, Any]] = []
    powershell = context.get("powershell")
    settings = context.get("windows_terminal_settings")
    state = "missing" if powershell else "manual"
    reason = "powershell.exe is available for Windows per-user font install" if powershell else "powershell.exe is not visible from WSL"
    entry = {
        "entry_id": WINDOWS_ENTRY_ID,
        "source": str(_nerd_paths(home, item)["install_dir"]),
        "source_type": "windows_host",
        "family": item.family,
        "target": "Windows per-user font store",
        "state": state,
        "protected": False,
        "reason": reason,
        "recipe": "fonts",
        "requires_sudo": False,
        "terminal_face": item.terminal_face,
        "terminal_impact": _terminal_impact("wsl"),
        "host_action": _host_action(context),
    }
    if powershell:
        source_dir = _nerd_paths(home, item)["install_dir"] if font_summary["state"] == "installed" else _nerd_paths(home, item)["extract_dir"]
        operations.append({
            "entry_id": WINDOWS_ENTRY_ID,
            "type": "font_install_windows",
            "source": str(source_dir),
            "target": "Windows per-user font store",
            "terminal_face": item.terminal_face,
            "reason": "install JetBrainsMono Nerd Font Mono into the Windows user font store through PowerShell",
            "requires_approval": True,
            "recipe": "fonts",
        })
        if settings:
            operations.append({
                "entry_id": WINDOWS_ENTRY_ID,
                "type": "font_update_windows_terminal",
                "source": item.terminal_face,
                "target": settings,
                "reason": "set Windows Terminal profile defaults font.face",
                "requires_approval": True,
                "recipe": "fonts",
            })
        else:
            operations.append(_manual_op(WINDOWS_ENTRY_ID, f"Set Windows Terminal font face to {item.terminal_face} manually."))
    else:
        operations.append(_manual_op(WINDOWS_ENTRY_ID, f"Install {item.terminal_face} on the Windows host manually."))
    return entry, operations, {"host_action": _host_action(context), "requires_sudo": False}


def _pixel_ttyd_plan(home: Path, context: dict[str, Any], font_summary: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any]]:
    paths = _paths(home)
    entry = {
        "entry_id": PIXEL_TTYD_ENTRY_ID,
        "source": str(paths["install_dir"]),
        "source_type": "pixel_ttyd",
        "family": "JetBrainsMono",
        "target": "/etc/ttyd/index.html",
        "state": "missing",
        "protected": False,
        "reason": "Pixel Terminal ttyd font embedding is managed as a system recipe",
        "recipe": "fonts",
        "requires_sudo": True,
        "terminal_face": font_summary["terminal_face"],
        "terminal_impact": _terminal_impact("pixel-terminal"),
        "host_action": _host_action(context),
    }
    base = {"entry_id": PIXEL_TTYD_ENTRY_ID, "requires_approval": True, "requires_sudo": True, "recipe": "fonts"}
    operations = [
        {
            **base,
            "type": "font_ttyd_write_html",
            "source": str(paths["install_dir"]),
            "target": "/etc/ttyd/index.html",
            "cache_dir": str(paths["cache_dir"]),
            "reason": "backup and write ttyd HTML with embedded JetBrainsMono Nerd Font Mono subset",
        },
        {
            **base,
            "type": "font_ttyd_write_service",
            "source": "generated ttyd.service",
            "target": "/etc/systemd/system/ttyd.service",
            "cache_dir": str(paths["cache_dir"]),
            "reason": "backup and write ttyd systemd service using the custom index",
        },
        {
            **base,
            "type": "font_systemd_daemon_reload",
            "target": "systemd",
            "reason": "reload systemd after ttyd.service update",
        },
        {
            **base,
            "type": "font_systemd_restart",
            "target": "ttyd.service",
            "reason": "restart Pixel Terminal ttyd service",
        },
    ]
    return entry, operations, {"host_action": _host_action(context), "terminal_impact": _terminal_impact("pixel-terminal")}


def _build_pixel_avf_plan(home: Path, context: dict[str, Any]) -> dict[str, Any]:
    prompt_path = home / PIXEL_AVF_PROMPT_REL
    desired = _pixel_avf_prompt_text()
    prompt_state = "installed" if prompt_path.exists() and prompt_path.read_text(errors="ignore") == desired else "missing"
    fonts = [_unsupported_nerd_summary(home, context, item, "Pixel AVF weston-terminal ignores Nerd Font configuration") for item in NERD_FONT_CATALOG]
    entries = [_font_entry(summary) for summary in fonts]
    entries.append({
        "entry_id": PIXEL_AVF_ENTRY_ID,
        "source": "generated fish prompt fallback",
        "source_type": "pixel_avf_prompt",
        "family": "fish prompt",
        "target": str(prompt_path),
        "state": prompt_state,
        "protected": False,
        "reason": "plain ASCII prompt fallback for Pixel AVF weston-terminal",
        "recipe": "fonts",
        "requires_sudo": False,
        "terminal_face": None,
        "terminal_impact": _terminal_impact("pixel-avf"),
        "host_action": _host_action(context),
    })
    operations: list[dict[str, Any]] = []
    if prompt_state != "installed":
        operations.append({
            "entry_id": PIXEL_AVF_ENTRY_ID,
            "type": "font_pixel_avf_prompt",
            "source": "generated fish prompt fallback",
            "target": str(prompt_path),
            "reason": "write plain prompt fallback without Nerd Font glyph dependencies",
            "requires_approval": True,
            "recipe": "fonts",
        })
    return {"entries": entries, "operations": operations, "fonts": fonts, "context": context}


def _build_unsupported_plan(home: Path, context: dict[str, Any]) -> dict[str, Any]:
    reason = "automatic font setup is unsupported on this platform"
    fonts = [_unsupported_nerd_summary(home, context, item, reason) for item in NERD_FONT_CATALOG]
    fonts.extend(_unsupported_apt_summary(context, item, reason) for item in APT_FONT_CATALOG)
    return {
        "entries": [_font_entry(summary) for summary in fonts],
        "operations": [_manual_op(FONT_ENTRY_ID, "Install terminal fonts manually on this platform.")],
        "fonts": fonts,
        "context": context,
    }


def _unsupported_nerd_summary(home: Path, context: dict[str, Any], item: NerdFontItem, reason: str) -> dict[str, Any]:
    paths = _nerd_paths(home, item)
    return {
        "entry_id": item.entry_id,
        "label": item.label,
        "family": item.family,
        "source_type": "nerd_font_release",
        "source": f"GitHub latest release asset {NERD_FONTS_REPO}/{item.asset_name}",
        "asset_name": item.asset_name,
        "state": "unsupported",
        "installed_version": None,
        "latest_version": None,
        "cached_version": None,
        "candidate_version": None,
        "target": str(paths["install_dir"]),
        "cache_path": str(paths["archive"]),
        "terminal_face": item.terminal_face,
        "platform": context["platform"],
        "requires_sudo": False,
        "terminal_impact": _terminal_impact(context["platform"]),
        "host_action": _host_action(context),
        "reason": reason,
    }


def _unsupported_apt_summary(context: dict[str, Any], item: dict[str, str], reason: str) -> dict[str, Any]:
    return {
        "entry_id": item["entry_id"],
        "label": item["family"],
        "family": item["family"],
        "source_type": "apt_package",
        "source": "apt",
        "package": item["package"],
        "state": "unsupported",
        "installed_version": None,
        "latest_version": None,
        "candidate_version": None,
        "target": item["package"],
        "cache_path": None,
        "terminal_face": item["terminal_face"],
        "platform": context["platform"],
        "requires_sudo": False,
        "terminal_impact": _terminal_impact(context["platform"]),
        "host_action": _host_action(context),
        "reason": reason,
    }


def _font_skip_op(entry_id: str, reason: str) -> dict[str, Any]:
    return {
        "entry_id": entry_id,
        "type": "font_skip",
        "target": "",
        "reason": reason,
        "requires_approval": False,
        "recipe": "fonts",
    }


def _manual_op(entry_id: str, reason: str) -> dict[str, Any]:
    return {
        "entry_id": entry_id,
        "type": "font_manual",
        "target": "",
        "reason": reason,
        "requires_approval": False,
        "recipe": "fonts",
    }


def _installed_ttf_files(install_dir: Path) -> list[Path]:
    return _installed_font_files(install_dir)


def _installed_font_files(install_dir: Path) -> list[Path]:
    if not install_dir.exists():
        return []
    return sorted(path for path in install_dir.glob("*") if path.suffix.lower() in {".ttf", ".otf"})


def _read_version(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return {}


def _execute_download(op: dict[str, Any], runner: CommandRunner) -> int:
    archive = Path(op["target"])
    version_path = archive.parent / f"{Path(op.get('asset_name') or archive.name).stem}.version.json"
    archive.parent.mkdir(parents=True, exist_ok=True)
    try:
        release = runner.fetch_json(NERD_FONTS_RELEASE_URL)
        asset = select_nerd_font_asset(release, str(op.get("asset_name") or FONT_ASSET_NAME))
    except Exception as exc:
        if archive.exists():
            op["result"] = f"reused cached archive after release lookup failed: {exc}"
            return 0
        raise FontError(f"font download blocked and no cached archive exists: {exc}") from exc

    current = _read_version(version_path)
    if archive.exists() and current.get("tag_name") == asset.get("tag_name"):
        op["result"] = f"cached {asset.get('tag_name')} reused"
        return 0
    runner.download(asset["browser_download_url"], archive)
    version_path.write_text(json.dumps(asset, indent=2, sort_keys=True) + "\n")
    op["result"] = f"downloaded {asset.get('tag_name')}"
    return 1


def _execute_extract(op: dict[str, Any]) -> int:
    archive = Path(op["source"])
    extract_dir = Path(op["target"])
    if not archive.exists():
        raise FontError(f"font archive is missing: {archive}")
    if extract_dir.exists():
        shutil.rmtree(extract_dir)
    extract_dir.mkdir(parents=True, exist_ok=True)
    extracted: list[Path] = []
    with zipfile.ZipFile(archive) as bundle:
        for info in bundle.infolist():
            name = Path(info.filename).name
            if not name or Path(name).suffix.lower() not in {".ttf", ".otf"}:
                continue
            target = extract_dir / name
            target.write_bytes(bundle.read(info))
            extracted.append(target)
    if not extracted:
        raise FontError(f"no font files found in {archive}")
    return 1


def _execute_install_linux(op: dict[str, Any]) -> int:
    source = Path(op["source"])
    target = Path(op["target"])
    fonts = _installed_font_files(source)
    if not fonts:
        raise FontError(f"no extracted font files found in {source}")
    target.mkdir(parents=True, exist_ok=True)
    for font in fonts:
        shutil.copy2(font, target / font.name)
    version = _read_version(Path(op.get("version_source", "")))
    if version:
        (target / FONT_MARKER_NAME).write_text(json.dumps(version, indent=2, sort_keys=True) + "\n")
    return 1


def _execute_rebuild_cache(op: dict[str, Any], runner: CommandRunner) -> int:
    fc_cache = runner.which("fc-cache")
    if not fc_cache:
        op["result"] = "fc-cache not found; font files installed but cache refresh is manual"
        return 0
    runner.run([fc_cache, "-f", op["target"]])
    return 1


def _execute_verify_linux(op: dict[str, Any], runner: CommandRunner) -> int:
    terminal_face = str(op.get("terminal_face") or "")
    if "Propo" in terminal_face or "Mono" not in terminal_face:
        raise FontError(f"refusing terminal font face that is not Mono-safe: {terminal_face}")
    fc_match = runner.which("fc-match")
    if not fc_match:
        op["result"] = "fc-match not found; verify manually"
        return 0
    result = runner.run([fc_match, terminal_face], capture_output=True)
    stdout = result.stdout or ""
    if "Propo" in stdout:
        raise FontError(f"fontconfig resolved {terminal_face} to a Propo face: {stdout.strip()}")
    if "Mono" not in stdout:
        raise FontError(f"fontconfig did not resolve {terminal_face} to a Mono face: {stdout.strip()}")
    family = str(op.get("family") or terminal_face.split()[0])
    if _normalize(family) not in _normalize(stdout):
        raise FontError(f"fontconfig did not resolve {terminal_face}: {stdout.strip()}")
    return 0


def _normalize(text: str) -> str:
    return "".join(char.lower() for char in text if char.isalnum())


def _execute_install_packages(op: dict[str, Any], runner: CommandRunner) -> int:
    packages = [str(package) for package in op.get("packages", []) if package]
    if not packages:
        return 0
    apt_get = runner.which("apt-get")
    if not apt_get:
        op["result"] = "apt-get not found; install fallback packages manually"
        return 0
    prefix = [] if hasattr(os, "geteuid") and os.geteuid() == 0 else ["sudo"]
    runner.run([*prefix, apt_get, "update"])
    runner.run([*prefix, apt_get, "install", "-y", *packages])
    return 1


def _execute_install_windows(op: dict[str, Any], runner: CommandRunner) -> int:
    powershell = runner.which("powershell.exe")
    if not powershell:
        op["result"] = "powershell.exe not found; install Windows host font manually"
        return 0
    source = Path(op["source"])
    if not source.exists():
        raise FontError(f"Windows font source directory is missing: {source}")
    windows_source = str(source)
    wslpath = runner.which("wslpath")
    if wslpath:
        converted = runner.run([wslpath, "-w", str(source)], capture_output=True)
        windows_source = converted.stdout.strip()
    script = _windows_font_install_script(windows_source)
    runner.run([powershell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script])
    return 1


def _windows_font_install_script(source_dir: str) -> str:
    escaped = source_dir.replace("'", "''")
    return (
        "$FontDir = Join-Path $env:LOCALAPPDATA 'Microsoft\\Windows\\Fonts'; "
        "New-Item -ItemType Directory -Force -Path $FontDir | Out-Null; "
        f"Get-ChildItem -Path '{escaped}' -File | Where-Object {{ $_.Extension -in '.ttf','.otf' }} | ForEach-Object {{ "
        "$Dest = Join-Path $FontDir $_.Name; "
        "Copy-Item $_.FullName $Dest -Force; "
        "New-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows NT\\CurrentVersion\\Fonts' "
        "-Name \"$($_.BaseName) (TrueType)\" -Value $_.Name -PropertyType String -Force | Out-Null "
        "}"
    )


def _execute_update_windows_terminal(op: dict[str, Any], backup_dir: Path, backups: list[dict[str, Any]]) -> int:
    target = Path(op["target"])
    if not target.exists():
        op["result"] = "Windows Terminal settings file was not found; set font face manually"
        return 0
    record = create_backup(target, backup_dir, entry_id=op["entry_id"])
    backups.append(record)
    try:
        data = json.loads(target.read_text())
    except json.JSONDecodeError as exc:
        raise FontError(f"invalid Windows Terminal settings JSON: {target}") from exc
    profiles = data.setdefault("profiles", {})
    if not isinstance(profiles, dict):
        profiles = {}
        data["profiles"] = profiles
    defaults = profiles.setdefault("defaults", {})
    if not isinstance(defaults, dict):
        defaults = {}
        profiles["defaults"] = defaults
    font = defaults.setdefault("font", {})
    if not isinstance(font, dict):
        font = {}
        defaults["font"] = font
    font["face"] = FONT_FACE
    target.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    op["backup_target"] = record["backup_target"]
    return 1


def _execute_ttyd_html(op: dict[str, Any], runner: CommandRunner, backups: list[dict[str, Any]]) -> int:
    source_dir = Path(op["source"])
    font = _regular_mono_font(source_dir)
    html = _ttyd_html(font)
    generated = Path(op["cache_dir"]) / "ttyd-index.html"
    generated.parent.mkdir(parents=True, exist_ok=True)
    generated.write_text(html)
    _sudo_backup_and_install(op["target"], generated, runner, backups, op["entry_id"])
    return 1


def _execute_ttyd_service(op: dict[str, Any], runner: CommandRunner, backups: list[dict[str, Any]]) -> int:
    generated = Path(op["cache_dir"]) / "ttyd.service"
    generated.parent.mkdir(parents=True, exist_ok=True)
    generated.write_text(_ttyd_service())
    _sudo_backup_and_install(op["target"], generated, runner, backups, op["entry_id"])
    return 1


def _sudo_backup_and_install(target: str, generated: Path, runner: CommandRunner, backups: list[dict[str, Any]], entry_id: str) -> None:
    backup_target = f"{target}.000-dotfiles-backup"
    runner.run(["sudo", "sh", "-c", "if [ -e \"$1\" ]; then cp -a \"$1\" \"$2\"; fi", "sh", target, backup_target])
    backups.append({"entry_id": entry_id, "target": target, "backup_target": backup_target})
    runner.run(["sudo", "install", "-Dm0644", str(generated), target])


def _regular_mono_font(source_dir: Path) -> Path:
    exact = source_dir / EXPECTED_TTF
    if exact.exists():
        return exact
    fonts = _installed_font_files(source_dir)
    regular = [path for path in fonts if "Mono" in path.name and "Regular" in path.name]
    if regular:
        return regular[0]
    mono = [path for path in fonts if "Mono" in path.name]
    if mono:
        return mono[0]
    raise FontError(f"no JetBrainsMono Nerd Font Mono file found in {source_dir}")


def _ttyd_html(font_path: Path) -> str:
    encoded = base64.b64encode(font_path.read_bytes()).decode("ascii")
    return f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<style>
@font-face {{
  font-family: '{PIXEL_TTYD_FONT_ALIAS}';
  src: url(data:font/truetype;charset=utf-8;base64,{encoded}) format('truetype');
  font-weight: normal;
  font-style: normal;
}}
body, #terminal, .terminal, .xterm, .xterm-rows {{
  font-family: '{PIXEL_TTYD_FONT_ALIAS}', 'Noto Color Emoji', monospace !important;
}}
</style>
</head>
<body>
<div id="terminal"></div>
</body>
</html>
"""


def _ttyd_service() -> str:
    return """[Unit]
Description=ttyd terminal with dotfiles-managed font embedding
After=network.target

[Service]
ExecStart=/usr/bin/ttyd --index /etc/ttyd/index.html -W /bin/bash
Restart=on-failure

[Install]
WantedBy=multi-user.target
"""


def _execute_pixel_avf_prompt(op: dict[str, Any]) -> int:
    target = Path(op["target"])
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(_pixel_avf_prompt_text())
    return 1


def _pixel_avf_prompt_text() -> str:
    return """# Managed by 000-dotfiles for Pixel AVF weston-terminal.
# Uses a plain prompt without Nerd Font private-use glyphs.
function fish_prompt
    set -l code $status
    set -l marker '>'
    if test $code -ne 0
        set marker '!'
    end
    printf '%s %s ' (prompt_pwd) $marker
end
"""
