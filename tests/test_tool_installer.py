from __future__ import annotations

from pathlib import Path
import subprocess  # nosec B404
from unittest import mock

from dotfiles_tools.baseline import DEV_BASE_PACKAGES
from dotfiles_tools.tool_installer import (
    DEV_BASE_ENTRY_ID,
    build_tool_install_plan,
    execute_tool_install_operation,
    run_post_install_actions,
    verify_installed_tools,
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
            return self._run_dpkg_query(args)
        if command == "dpkg" and "--print-architecture" in args:
            return subprocess.CompletedProcess(args, 0, stdout=f"{self.dpkg_arch}\n", stderr="")
        if "--version" in args:
            return subprocess.CompletedProcess(args, 0, stdout="dummy 1.2.3\n", stderr="")
        return subprocess.CompletedProcess(args, 0, stdout="", stderr="")

    def _run_dpkg_query(self, args: list[str]) -> subprocess.CompletedProcess[str]:
        package = args[-1]
        if package in self.installed_dpkg:
            return subprocess.CompletedProcess(args, 0, stdout="install ok installed", stderr="")
        return subprocess.CompletedProcess(args, 1, stdout="", stderr="not installed")

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
        # Phase 1: curl ops carry an explicit interpreter so dash-only systems
        # don't run bash scripts under /bin/sh.
        self.assertEqual(claude_ops[0]["interpreter"], "bash")

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
        runner = FakeRunner(which={"bash": "/bin/bash"})
        cache_dir = home / ".cache" / "tool-installers"
        op = {
            "entry_id": "tools.claude",
            "recipe": "tool_installs",
            "type": "tool_install_curl",
            "url": "https://claude.ai/install.sh",
            "script_name": "claude-install.sh",
            "interpreter": "bash",
            "requires_sudo": False,
            "cache_dir": str(cache_dir),
        }
        execute_tool_install_operation(op, runner=runner, cache_dir=cache_dir)
        self.assertEqual(len(runner.downloads), 1)
        self.assertEqual(runner.downloads[0][0], "https://claude.ai/install.sh")
        self.assertTrue(runner.commands)
        self.assertEqual(runner.commands[-1][0], "/bin/bash")
        # No sudo for the curl installer.
        self.assertNotIn("sudo", runner.commands[-1])

    def test_curl_installer_uses_bash_by_default_when_no_interpreter_set(self) -> None:
        home = self.make_home()
        runner = FakeRunner(which={"bash": "/usr/bin/bash"})
        cache_dir = home / ".cache" / "tool-installers"
        op = {
            "entry_id": "tools.claude",
            "recipe": "tool_installs",
            "type": "tool_install_curl",
            "url": "https://example.test/install.sh",
            "script_name": "x.sh",
            "requires_sudo": False,
            "cache_dir": str(cache_dir),
        }
        execute_tool_install_operation(op, runner=runner, cache_dir=cache_dir)
        self.assertEqual(runner.commands[-1][0], "/usr/bin/bash")

    def test_curl_installer_honors_interpreter_override(self) -> None:
        home = self.make_home()
        runner = FakeRunner(which={"python3": "/usr/bin/python3"})
        cache_dir = home / ".cache" / "tool-installers"
        op = {
            "entry_id": "tools.thing",
            "recipe": "tool_installs",
            "type": "tool_install_curl",
            "url": "https://example.test/install.py",
            "script_name": "x.py",
            "interpreter": "python3",
            "requires_sudo": False,
            "cache_dir": str(cache_dir),
        }
        execute_tool_install_operation(op, runner=runner, cache_dir=cache_dir)
        self.assertEqual(runner.commands[-1][0], "/usr/bin/python3")

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


class VerifyAndPostInstallTests(DotfilesTestCase):
    def test_verify_marks_each_bootstrap_tool_with_path_and_version(self) -> None:
        home = self.make_home()
        runner = FakeRunner(which={"git": "/usr/bin/git", "fish": "/usr/bin/fish"})
        results = verify_installed_tools(home, runner=runner, env={"PATH": ""})
        by_command = {item["command"]: item for item in results}
        self.assertTrue(by_command["git"]["verified"])
        self.assertEqual(by_command["git"]["path"], "/usr/bin/git")
        self.assertTrue(by_command["fish"]["verified"])
        self.assertFalse(by_command["claude"]["verified"])
        self.assertEqual(by_command["claude"]["path"], None)

    def test_post_install_auto_executes_when_yes_true_and_template_resolves(self) -> None:
        home = self.make_home()
        runner = FakeRunner(which={"fish": "/usr/bin/fish"})
        env = {"PATH": "/usr/bin", "USER": "alice"}
        results = run_post_install_actions(home, yes=True, runner=runner, env=env)
        ran = [r for r in results if r["status"] == "ran"]
        labels = [r["label"] for r in ran]
        self.assertIn("Set fish as default shell", labels)
        # The chsh template uses {which:fish} and {user} — both substituted.
        chsh = next(r for r in ran if r["label"] == "Set fish as default shell")
        self.assertEqual(chsh["command"], ["sudo", "chsh", "-s", "/usr/bin/fish", "alice"])

    def test_post_install_auto_downgrades_to_guidance_when_yes_false(self) -> None:
        home = self.make_home()
        runner = FakeRunner(which={"fish": "/usr/bin/fish"})
        env = {"PATH": "/usr/bin", "USER": "alice"}
        results = run_post_install_actions(home, yes=False, runner=runner, env=env)
        statuses = {r["status"] for r in results}
        self.assertEqual(statuses, {"guidance"})
        self.assertFalse(runner.commands)  # no exec attempted

    def test_post_install_login_actions_never_auto_run_even_with_yes(self) -> None:
        home = self.make_home()
        runner = FakeRunner(which={"gh": "/usr/bin/gh", "claude": "/usr/local/bin/claude"})
        results = run_post_install_actions(home, yes=True, runner=runner, env={"PATH": ""})
        gh_actions = [r for r in results if r["tool"] == "gh"]
        self.assertTrue(gh_actions)
        for r in gh_actions:
            self.assertEqual(r["status"], "guidance")
            self.assertEqual(r["kind"], "guidance")

    def test_post_install_unresolved_placeholder_downgrades_to_skipped(self) -> None:
        home = self.make_home()
        # fish on PATH so post_install runs, but no `which:fish` resolution
        # because the runner doesn't return a path. Wait — fish IS in `which`
        # below but the chsh template asks for which:fish; let's test by
        # making USER absent so {user} can't resolve.
        runner = FakeRunner(which={"fish": "/usr/bin/fish"})
        env = {"PATH": ""}  # no USER
        results = run_post_install_actions(home, yes=True, runner=runner, env=env)
        chsh = next(r for r in results if r["label"] == "Set fish as default shell")
        self.assertEqual(chsh["status"], "skipped")
        self.assertIn("user", chsh["reason"])

    def test_post_install_protected_apply_copies_fish_plugins(self) -> None:
        home = self.make_home()
        repo = self.make_home() / "repo"
        (repo / "fish").mkdir(parents=True)
        (repo / "fish" / "fish_plugins").write_text("jorgebucaran/fisher\n")
        runner = FakeRunner(which={"fish": "/usr/bin/fish"})
        env = {"PATH": "/usr/bin", "USER": "alice"}
        results = run_post_install_actions(
            home, yes=True, runner=runner, env=env, repo_path=repo,
        )
        plugin_action = next(r for r in results if "fisher update" in " ".join(r["command"]))
        self.assertEqual(plugin_action["status"], "ran")
        target = home / ".config" / "fish" / "fish_plugins"
        self.assertTrue(target.exists())
        self.assertEqual(target.read_text(), "jorgebucaran/fisher\n")
        self.assertTrue(plugin_action["protected_overrides"])

    def test_every_bootstrap_tool_declares_post_install(self) -> None:
        from dotfiles_tools.baseline import TOOL_BASELINE
        for item in TOOL_BASELINE:
            if not item.get("bootstrap"):
                continue
            self.assertIn("post_install", item, f"{item['id']} missing post_install")
