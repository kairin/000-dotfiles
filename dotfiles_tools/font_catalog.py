from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


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


class FontError(RuntimeError):
    """Raised when a font recipe cannot complete."""


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
