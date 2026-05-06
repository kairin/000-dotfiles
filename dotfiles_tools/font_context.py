from __future__ import annotations

from pathlib import Path
import platform
from typing import Any, Mapping

from .font_catalog import APT_FONT_CATALOG, NERD_FONT_CATALOG, WINDOWS_TERMINAL_PACKAGES
from .font_runner import CommandRunner


def detect_context(home: Path, env: Mapping[str, str], path: str, runner: CommandRunner) -> dict[str, Any]:
    return {
        "platform": platform_id(env),
        "architecture": platform.machine().lower(),
        "path": path,
        "powershell": runner.which("powershell.exe"),
        "wslpath": runner.which("wslpath"),
        "windows_terminal_settings": discover_windows_terminal_settings(home, env),
    }


def platform_id(env: Mapping[str, str]) -> str:
    override = (env.get("DOTFILES_PLATFORM") or "").strip().lower()
    override_id = platform_override(override)
    if override_id:
        return override_id
    return detected_platform(env)


def platform_override(override: str) -> str | None:
    overrides = {
        "linux": "linux",
        "native-linux": "linux",
        "ubuntu": "linux",
        "pi": "pi",
        "raspberry-pi": "pi",
        "raspberrypi": "pi",
        "wsl": "wsl",
        "wsl-linux": "wsl",
        "wsl2": "wsl",
        "pixel-terminal": "pixel-terminal",
        "pixel_ttyd": "pixel-terminal",
        "ttyd": "pixel-terminal",
        "pixel-avf": "pixel-avf",
        "avf": "pixel-avf",
    }
    return overrides.get(override)


def detected_platform(env: Mapping[str, str]) -> str:
    if is_wsl(env):
        return "wsl"
    if is_raspberry_pi():
        return "pi"
    if Path("/etc/ttyd").exists() or Path("/etc/systemd/system/ttyd.service").exists():
        return "pixel-terminal"
    return "linux" if platform.system().lower() == "linux" else "unsupported"


def is_wsl(env: Mapping[str, str]) -> bool:
    if env.get("WSL_DISTRO_NAME") or env.get("WSL_INTEROP"):
        return True
    try:
        return "microsoft" in Path("/proc/version").read_text(errors="ignore").lower()
    except OSError:
        return False


def is_raspberry_pi() -> bool:
    try:
        return "raspberry pi" in Path("/proc/device-tree/model").read_text(errors="ignore").lower()
    except OSError:
        return False


def discover_windows_terminal_settings(home: Path, env: Mapping[str, str]) -> str | None:
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


def check_windows_fonts_installed(source_dir: Path, _users_root: Path | None = None) -> bool:
    """Return True if at least one font file from source_dir is present in the Windows per-user font store."""
    users_root = _users_root if _users_root is not None else Path("/mnt/c/Users")
    if not users_root.exists() or not source_dir.exists():
        return False
    font_files = list(source_dir.glob("*.ttf")) + list(source_dir.glob("*.otf"))
    if not font_files:
        return False
    for user_dir in users_root.glob("*"):
        win_fonts = user_dir / "AppData/Local/Microsoft/Windows/Fonts"
        if any((win_fonts / f.name).exists() for f in font_files):
            return True
    return False


def nerd_items_for_platform(platform_name: str) -> tuple:
    if platform_name == "pixel-terminal":
        return (NERD_FONT_CATALOG[0],)
    if platform_name in {"linux", "wsl", "pi"}:
        return NERD_FONT_CATALOG
    return ()


def apt_items_for_platform(platform_name: str) -> tuple[dict[str, str], ...]:
    if platform_name in {"linux", "wsl"}:
        return APT_FONT_CATALOG
    if platform_name == "pi":
        return tuple(item for item in APT_FONT_CATALOG if item["package"] != "fonts-dejavu-core")
    if platform_name == "pixel-terminal":
        return tuple(item for item in APT_FONT_CATALOG if item["package"] == "fonts-noto-color-emoji")
    return ()


def terminal_impact(platform_name: str) -> str:
    if platform_name == "wsl":
        return "Linux terminals get Nerd Font Mono faces; Windows Terminal is updated when its settings file is discoverable."
    if platform_name == "pixel-terminal":
        return "Pixel Terminal ttyd pages use an embedded JetBrainsMono Nerd Font Mono subset."
    if platform_name == "pi":
        return "Local Linux terminal apps can select Nerd Font Mono faces; emoji/symbol fallbacks are installed with apt."
    if platform_name == "pixel-avf":
        return "Pixel AVF weston-terminal ignores Nerd Font configuration; a plain prompt fallback is used."
    return "Local Linux terminal apps can select Nerd Font Mono faces after install."


def host_action(context: dict[str, Any]) -> str:
    platform_name = context["platform"]
    if platform_name == "wsl":
        return wsl_host_action(context)
    if platform_name == "pixel-terminal":
        return "sudo writes /etc/ttyd/index.html and ttyd.service, then restarts ttyd.service."
    if platform_name == "pixel-avf":
        return "No host font action; weston-terminal ignores Nerd Font UI configuration."
    return "No host-side action."


def wsl_host_action(context: dict[str, Any]) -> str:
    if context.get("powershell") and context.get("windows_terminal_settings"):
        return "PowerShell installs JetBrainsMono Nerd Font Mono on Windows and Windows Terminal defaults are updated."
    if context.get("powershell"):
        return "PowerShell installs JetBrainsMono Nerd Font Mono on Windows; set Windows Terminal manually if no settings file is found."
    return "Manual Windows host font install required because powershell.exe was not found."
