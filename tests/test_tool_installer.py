from __future__ import annotations

from pathlib import Path
import subprocess  # nosec B404
from unittest import mock

from dotfiles_tools.baseline import DEV_BASE_PACKAGES
from dotfiles_tools.tool_installer import (
    DEV_BASE_ENTRY_ID,
    build_tool_install_plan,
    execute_tool_install_operation,
)
from tests.helpers import DotfilesTestCase


class FakeRunner:
    def __init__(
        self,
        *,
        which: dict[str, str] | None = None,
        installed_dpkg: tuple[str, ...] = (),
        dpkg_arch: str = "amd64",
        run_failures: dict[str, OSError] | None = None,
    ) -> None:
        self.which_map = which or {}
        self.installed_dpkg = set(installed_dpkg)
        self.dpkg_arch = dpkg_arch
        self.run_failures = run_failures or {}
        self.commands: list[list[str]] = []
        self.downloads: list[tuple[str, Path]] = []

    def which(self, command: str) -> str | None:
        return self.which_map.get(command)

    def run(
        self,
        args: list[str],
        *,
        capture_output: bool = False,
        check: bool = True,
    ) -> subprocess.CompletedProcess[str]:
        self.commands.append(list(args))
        if args and Path(args[0]).name in self.run_failures:
            raise self.run_failures[Path(args[0]).name]
        command = Path(args[0]).name if args else ""
        if command == "dpkg-query":
            package = args[-1]
            if package in self.installed_dpkg:
                return subprocess.CompletedProcess(args, 0, stdout="install ok installed", stderr="")
            return subprocess.CompletedProcess(args, 1, stdout="", stderr="not installed")
        if command == "dpkg" and "--print-architecture" in args:
            return subprocess.CompletedProcess(args, 0, stdout=f"{self.dpkg_arch}\n", stderr="")
        if "--version" in args:
            return subprocess.CompletedProcess(args, 0, stdout="dummy 1.2.3\n", stderr="")
        return subprocess.CompletedProcess(args, 0, stdout="", stderr="")

    def download(self, url: str, target: Path) -> None:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("#!/bin/sh\necho fake\n")
        self.downloads.append((url, target))


class ToolInstallPlanTests(DotfilesTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.geteuid_patch = mock.patch("dotfiles_tools.tool_installer.os.geteuid", return_value=1000, create=True)
        self.geteuid_patch.start()
        self.addCleanup(self.geteuid_patch.stop)
        self.platform_patch = mock.patch("dotfiles_tools.tool_installer.sys.platform", "linux")
        self.platform_patch.start()
        self.addCleanup(self.platform_patch.stop)

    def _make_runner(self, **kwargs) -> FakeRunner:
        defaults = dict(which={"dpkg-query": "/usr/bin/dpkg-query", "apt-get": "/usr/bin/apt-get"})
        defaults.update(kwargs.pop("which", {}) and {"which": {**defaults["which"], **kwargs.pop("which")}} or {})
        defaults.update(kwargs)
        # remerge which if user passed it
        return FakeRunner(**defaults)

    def test_dev_base_apt_batched_install_fresh(self) -> None:
        home = self.make_home()
        runner = FakeRunner(which={"dpkg-query": "/usr/bin/dpkg-query"})
        plan = build_tool_install_plan(home, runner=runner)
        dev_base_ops = [op for op in plan["operations"] if op.get("entry_id") == DEV_BASE_ENTRY_ID]
        self.assertEqual(len(dev_base_ops), 1)
        op = dev_base_ops[0]
        self.assertEqual(op["type"], "tool_install_apt")
        self.assertEqual(set(op["packages"]), set(DEV_BASE_PACKAGES))

    def test_dev_base_partial_install(self) -> None:
        home = self.make_home()
        installed = DEV_BASE_PACKAGES[:5]
        missing = DEV_BASE_PACKAGES[5:]
        runner = FakeRunner(
            which={"dpkg-query": "/usr/bin/dpkg-query"},
            installed_dpkg=installed,
        )
        plan = build_tool_install_plan(home, runner=runner)
        dev_base_ops = [op for op in plan["operations"] if op.get("entry_id") == DEV_BASE_ENTRY_ID]
        types = {op["type"]: set(op["packages"]) for op in dev_base_ops}
        self.assertEqual(types["tool_install_apt"], set(missing))
        self.assertEqual(types["tool_install_apt_upgrade"], set(installed))

    def test_dev_base_all_installed_emits_upgrade_only(self) -> None:
        home = self.make_home()
        runner = FakeRunner(
            which={"dpkg-query": "/usr/bin/dpkg-query"},
            installed_dpkg=DEV_BASE_PACKAGES,
        )
        plan = build_tool_install_plan(home, runner=runner)
        dev_base_ops = [op for op in plan["operations"] if op.get("entry_id") == DEV_BASE_ENTRY_ID]
        self.assertEqual(len(dev_base_ops), 1)
        self.assertEqual(dev_base_ops[0]["type"], "tool_install_apt_upgrade")

    def test_apt_keyring_for_gh_missing(self) -> None:
        home = self.make_home()
        runner = FakeRunner(which={"dpkg-query": "/usr/bin/dpkg-query"})
        plan = build_tool_install_plan(home, runner=runner)
        gh_ops = [op for op in plan["operations"] if op.get("entry_id") == "tools.gh"]
        self.assertEqual(len(gh_ops), 1)
        self.assertEqual(gh_ops[0]["type"], "tool_install_apt_keyring")
        self.assertEqual(gh_ops[0]["mode"], "install")
        self.assertEqual(gh_ops[0]["packages"], ["gh"])

    def test_apt_keyring_for_gh_installed_upgrade_path(self) -> None:
        home = self.make_home()
        runner = FakeRunner(which={"dpkg-query": "/usr/bin/dpkg-query", "gh": "/usr/bin/gh"})
        plan = build_tool_install_plan(home, runner=runner)
        gh_ops = [op for op in plan["operations"] if op.get("entry_id") == "tools.gh"]
        self.assertEqual(len(gh_ops), 1)
        self.assertEqual(gh_ops[0]["mode"], "upgrade")

    def test_curl_installer_for_claude_install(self) -> None:
        home = self.make_home()
        runner = FakeRunner(which={"dpkg-query": "/usr/bin/dpkg-query"})
        plan = build_tool_install_plan(home, runner=runner)
        claude_ops = [op for op in plan["operations"] if op.get("entry_id") == "tools.claude"]
        self.assertEqual(len(claude_ops), 1)
        self.assertEqual(claude_ops[0]["type"], "tool_install_curl")
        self.assertEqual(claude_ops[0]["mode"], "install")
        self.assertIn("install.sh", claude_ops[0]["url"])

    def test_curl_installer_for_claude_upgrade_reruns_installer(self) -> None:
        home = self.make_home()
        runner = FakeRunner(
            which={"dpkg-query": "/usr/bin/dpkg-query", "claude": "/home/x/.local/bin/claude"},
        )
        plan = build_tool_install_plan(home, runner=runner)
        claude_ops = [op for op in plan["operations"] if op.get("entry_id") == "tools.claude"]
        self.assertEqual(claude_ops[0]["type"], "tool_install_curl")
        self.assertEqual(claude_ops[0]["mode"], "upgrade")

    def test_npm_install_for_codex_and_gemini(self) -> None:
        home = self.make_home()
        runner = FakeRunner(which={"dpkg-query": "/usr/bin/dpkg-query"})
        plan = build_tool_install_plan(home, runner=runner)
        codex_ops = [op for op in plan["operations"] if op.get("entry_id") == "tools.codex"]
        gemini_ops = [op for op in plan["operations"] if op.get("entry_id") == "tools.gemini"]
        self.assertEqual(codex_ops[0]["type"], "tool_install_npm")
        self.assertEqual(codex_ops[0]["package"], "@openai/codex")
        self.assertEqual(gemini_ops[0]["package"], "@google/gemini-cli")

    def test_npm_upgrade_when_present(self) -> None:
        home = self.make_home()
        runner = FakeRunner(
            which={
                "dpkg-query": "/usr/bin/dpkg-query",
                "codex": "/usr/local/bin/codex",
                "gemini": "/usr/local/bin/gemini",
            },
        )
        plan = build_tool_install_plan(home, runner=runner)
        codex_ops = [op for op in plan["operations"] if op.get("entry_id") == "tools.codex"]
        self.assertEqual(codex_ops[0]["type"], "tool_install_npm_upgrade")

    def test_entries_include_installed_for_preview(self) -> None:
        home = self.make_home()
        runner = FakeRunner(
            which={"dpkg-query": "/usr/bin/dpkg-query", "git": "/usr/bin/git"},
        )
        plan = build_tool_install_plan(home, runner=runner)
        git_entry = next(e for e in plan["entries"] if e.get("entry_id") == "tools.git")
        self.assertEqual(git_entry["state"], "installed")
        self.assertEqual(git_entry["current_path"], "/usr/bin/git")
        self.assertEqual(git_entry["action"], "upgrade")

    def test_unsupported_on_non_linux(self) -> None:
        home = self.make_home()
        runner = FakeRunner()
        with mock.patch("dotfiles_tools.tool_installer.sys.platform", "darwin"):
            plan = build_tool_install_plan(home, runner=runner, env={})
        self.assertEqual(plan["operations"], [])
        self.assertTrue(all(entry["state"] == "unsupported" for entry in plan["entries"]))


class ToolInstallExecuteTests(DotfilesTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.geteuid_patch = mock.patch(
            "dotfiles_tools.tool_installer.os.geteuid", return_value=1000, create=True
        )
        self.geteuid_patch.start()
        self.addCleanup(self.geteuid_patch.stop)

    def test_apt_executes_with_sudo_prefix(self) -> None:
        home = self.make_home()
        runner = FakeRunner(which={"apt-get": "/usr/bin/apt-get"})
        op = {
            "entry_id": DEV_BASE_ENTRY_ID,
            "recipe": "tool_installs",
            "type": "tool_install_apt",
            "packages": ["curl", "wget"],
            "cache_dir": str(home / ".cache"),
        }
        execute_tool_install_operation(op, runner=runner, cache_dir=Path(op["cache_dir"]))
        self.assertEqual(runner.commands[0], ["sudo", "/usr/bin/apt-get", "update"])
        self.assertEqual(
            runner.commands[1],
            ["sudo", "/usr/bin/apt-get", "install", "-y", "curl", "wget"],
        )

    def test_apt_upgrade_uses_only_upgrade_flag(self) -> None:
        home = self.make_home()
        runner = FakeRunner(which={"apt-get": "/usr/bin/apt-get"})
        op = {
            "entry_id": DEV_BASE_ENTRY_ID,
            "recipe": "tool_installs",
            "type": "tool_install_apt_upgrade",
            "packages": ["git"],
            "cache_dir": str(home / ".cache"),
        }
        execute_tool_install_operation(op, runner=runner, cache_dir=Path(op["cache_dir"]))
        self.assertIn("--only-upgrade", runner.commands[1])

    def test_apt_missing_apt_get_soft_skips(self) -> None:
        home = self.make_home()
        runner = FakeRunner(which={})
        op = {
            "entry_id": DEV_BASE_ENTRY_ID,
            "recipe": "tool_installs",
            "type": "tool_install_apt",
            "packages": ["git"],
            "cache_dir": str(home / ".cache"),
        }
        result = execute_tool_install_operation(op, runner=runner, cache_dir=Path(op["cache_dir"]))
        self.assertEqual(result, 0)
        self.assertIn("apt-get not found", op["result"])
        self.assertEqual(runner.commands, [])

    def test_curl_installer_downloads_and_runs(self) -> None:
        home = self.make_home()
        runner = FakeRunner(which={"sh": "/bin/sh"})
        cache_dir = home / ".cache" / "tool-installers"
        op = {
            "entry_id": "tools.claude",
            "recipe": "tool_installs",
            "type": "tool_install_curl",
            "url": "https://claude.ai/install.sh",
            "script_name": "claude-install.sh",
            "requires_sudo": False,
            "cache_dir": str(cache_dir),
        }
        execute_tool_install_operation(op, runner=runner, cache_dir=cache_dir)
        self.assertEqual(len(runner.downloads), 1)
        self.assertEqual(runner.downloads[0][0], "https://claude.ai/install.sh")
        self.assertTrue(runner.commands)
        self.assertEqual(runner.commands[-1][0], "/bin/sh")
        # No sudo for the curl installer.
        self.assertNotIn("sudo", runner.commands[-1])

    def test_npm_missing_skips(self) -> None:
        home = self.make_home()
        runner = FakeRunner(which={})
        op = {
            "entry_id": "tools.codex",
            "recipe": "tool_installs",
            "type": "tool_install_npm",
            "package": "@openai/codex",
            "cache_dir": str(home / ".cache"),
            "requires_sudo": True,
        }
        result = execute_tool_install_operation(op, runner=runner, cache_dir=Path(op["cache_dir"]))
        self.assertEqual(result, 0)
        self.assertIn("npm not found", op["result"])

    def test_npm_present_runs_global_install(self) -> None:
        home = self.make_home()
        runner = FakeRunner(which={"npm": "/usr/bin/npm"})
        op = {
            "entry_id": "tools.codex",
            "recipe": "tool_installs",
            "type": "tool_install_npm",
            "package": "@openai/codex",
            "cache_dir": str(home / ".cache"),
            "requires_sudo": True,
        }
        execute_tool_install_operation(op, runner=runner, cache_dir=Path(op["cache_dir"]))
        self.assertEqual(
            runner.commands[0],
            ["sudo", "/usr/bin/npm", "install", "-g", "@openai/codex"],
        )

    def test_apt_keyring_downloads_keyring_and_writes_source(self) -> None:
        home = self.make_home()
        cache_dir = home / ".cache" / "tool-installers"
        runner = FakeRunner(
            which={
                "apt-get": "/usr/bin/apt-get",
                "dpkg": "/usr/bin/dpkg",
            },
            dpkg_arch="amd64",
        )
        op = {
            "entry_id": "tools.gh",
            "recipe": "tool_installs",
            "type": "tool_install_apt_keyring",
            "mode": "install",
            "packages": ["gh"],
            "keyring_url": "https://example.test/keyring.gpg",
            "keyring_path": str(home / "keyrings" / "gh.gpg"),
            "source_line": "deb [arch={ARCH} signed-by=...] https://example.test stable main",
            "source_path": str(home / "sources.list.d" / "gh.list"),
            "cache_dir": str(cache_dir),
        }
        execute_tool_install_operation(op, runner=runner, cache_dir=cache_dir)
        self.assertEqual(len(runner.downloads), 1)
        # First install command should be the keyring file.
        install_cmds = [cmd for cmd in runner.commands if cmd[:1] == ["sudo"] and "install" in cmd]
        self.assertGreaterEqual(len(install_cmds), 2)
        # Source line was rendered with the architecture.
        rendered_source_path = cache_dir / "gh.list"
        self.assertIn("arch=amd64", rendered_source_path.read_text())

    def test_sudo_gating_as_root(self) -> None:
        home = self.make_home()
        runner = FakeRunner(which={"apt-get": "/usr/bin/apt-get"})
        op = {
            "entry_id": DEV_BASE_ENTRY_ID,
            "recipe": "tool_installs",
            "type": "tool_install_apt",
            "packages": ["git"],
            "cache_dir": str(home / ".cache"),
        }
        with mock.patch("dotfiles_tools.tool_installer.os.geteuid", return_value=0, create=True):
            execute_tool_install_operation(op, runner=runner, cache_dir=Path(op["cache_dir"]))
        self.assertNotIn("sudo", runner.commands[0])
