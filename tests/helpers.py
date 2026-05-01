from __future__ import annotations

import json
from pathlib import Path
import shutil
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]


class DotfilesTestCase(unittest.TestCase):
    def make_home(self) -> Path:
        path = Path(tempfile.mkdtemp(prefix="dotfiles-home-"))
        self.addCleanup(lambda: shutil.rmtree(path, ignore_errors=True))
        return path

    def make_project(self) -> Path:
        path = Path(tempfile.mkdtemp(prefix="dotfiles-project-"))
        self.addCleanup(lambda: shutil.rmtree(path, ignore_errors=True))
        return path

    def vars_file(self, project: Path, **overrides: str) -> Path:
        values = {
            "PROJECT_NAME": "Example Project",
            "PROJECT_DESCRIPTION": "example validation project",
            "LANGUAGE": "Python",
            "PACKAGE_MANAGER": "uv",
            "RUNTIME_DESCRIPTION": "local CLI",
            "INSTALL_CMD": "uv run python -m unittest discover -s tests",
            "RUN_CMD": "uv run python -m dotfiles_tools doctor --repo . --home \"$HOME\"",
            "TEST_CMD": "uv run python -m unittest discover -s tests",
        }
        values.update(overrides)
        path = project / "project-vars.json"
        path.write_text(json.dumps(values))
        return path


def read_json_report(text: str) -> dict:
    return json.loads(text)
