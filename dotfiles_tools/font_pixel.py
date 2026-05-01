from __future__ import annotations

from pathlib import Path
from typing import Any

from .font_catalog import FONT_CACHE_REL, FONT_INSTALL_BASE_REL, NERD_FONT_CATALOG, PIXEL_TTYD_ENTRY_ID
from .font_context import host_action, terminal_impact


def pixel_ttyd_plan(
    home: Path,
    context: dict[str, Any],
    font_summary: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any]]:
    paths = jetbrains_paths(home)
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
        "terminal_impact": terminal_impact("pixel-terminal"),
        "host_action": host_action(context),
    }
    operations = pixel_ttyd_operations(paths)
    return entry, operations, {"host_action": host_action(context), "terminal_impact": terminal_impact("pixel-terminal")}


def pixel_ttyd_operations(paths: dict[str, Path]) -> list[dict[str, Any]]:
    base = {"entry_id": PIXEL_TTYD_ENTRY_ID, "requires_approval": True, "requires_sudo": True, "recipe": "fonts"}
    return [
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


def jetbrains_paths(home: Path) -> dict[str, Path]:
    item = NERD_FONT_CATALOG[0]
    cache_dir = home / FONT_CACHE_REL
    return {
        "cache_dir": cache_dir,
        "install_dir": home / FONT_INSTALL_BASE_REL / item.install_dir_name,
    }
