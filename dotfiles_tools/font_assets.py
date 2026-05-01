from __future__ import annotations

import base64
from pathlib import Path

from .font_catalog import PIXEL_TTYD_FONT_ALIAS


def windows_font_install_script(source_dir: str) -> str:
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


def ttyd_html(font_path: Path) -> str:
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


def ttyd_service() -> str:
    return """[Unit]
Description=ttyd terminal with dotfiles-managed font embedding
After=network.target

[Service]
ExecStart=/usr/bin/ttyd --index /etc/ttyd/index.html -W /bin/bash
Restart=on-failure

[Install]
WantedBy=multi-user.target
"""


def pixel_avf_prompt_text() -> str:
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
