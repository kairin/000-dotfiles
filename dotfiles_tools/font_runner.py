from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess  # nosec B404
from typing import Any, Mapping
import urllib.request


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
