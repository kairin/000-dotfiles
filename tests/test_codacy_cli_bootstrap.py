from __future__ import annotations

from pathlib import Path
from unittest import mock

from dotfiles_tools.baseline import TOOL_BASELINE
from dotfiles_tools.tool_installer import (
    build_tool_install_plan,
    execute_tool_install_operation,
    verify_installed_tools,
    run_post_install_actions,
    TOOL_CACHE_REL,
)
from tests.helpers import DotfilesTestCase
from tests.test_tool_installer import FakeRunner


CODACY_ENTRY_ID = "tools.codacy-cli"
CODACY_INSTALL_URL = "https://raw.githubusercontent.com/codacy/codacy-cli-v2/main/codacy-cli.sh"
CODACY_SCRIPT_NAME = "codacy-cli.sh"
CODACY_WRAPPER = Path(__file__).resolve().parents[1] / ".codacy" / "cli.sh"


class CodacyCliBaselineEntryTests(DotfilesTestCase):
    def _get_baseline_entry(self) -> dict:
        return next(e for e in TOOL_BASELINE if e["id"] == "codacy-cli")

    def test_codacy_cli_present_in_tool_baseline(self) -> None:
        ids = [e["id"] for e in TOOL_BASELINE]
        self.assertIn("codacy-cli", ids)

    def test_codacy_cli_baseline_fields(self) -> None:
        entry = self._get_baseline_entry()
        self.assertEqual(entry["command"], "codacy-cli")
        self.assertEqual(entry["install_method"], "curl_installer")
        self.assertTrue(entry["bootstrap"])
        self.assertFalse(entry["requires_sudo"])
        self.assertEqual(entry["post_install"], ())

    def test_codacy_cli_install_args_url_and_script(self) -> None:
        entry = self._get_baseline_entry()
        args = entry["install_args"]
        self.assertEqual(args["url"], CODACY_INSTALL_URL)
        self.assertEqual(args["script_name"], CODACY_SCRIPT_NAME)

    def test_codacy_cli_interpreter_is_bash(self) -> None:
        entry = self._get_baseline_entry()
        self.assertEqual(entry["install_args"]["interpreter"], "bash")


class CodacyCliPlanTests(DotfilesTestCase):
    def setUp(self) -> None:
        super().setUp()
        self._platform = mock.patch("dotfiles_tools.tool_installer.sys.platform", "linux")
        self._platform.start()
        self.addCleanup(self._platform.stop)
        self._euid = mock.patch("dotfiles_tools.tool_installer.os.geteuid", return_value=1000, create=True)
        self._euid.start()
        self.addCleanup(self._euid.stop)

    def test_plan_emits_curl_install_op_when_missing(self) -> None:
        home = self.make_home()
        runner = FakeRunner(which={"dpkg-query": "/usr/bin/dpkg-query"})
        plan = build_tool_install_plan(home, runner=runner)
        ops = [op for op in plan["operations"] if op.get("entry_id") == CODACY_ENTRY_ID]
        self.assertEqual(len(ops), 1)
        op = ops[0]
        self.assertEqual(op["type"], "tool_install_curl")
        self.assertEqual(op["mode"], "install")
        self.assertEqual(op["url"], CODACY_INSTALL_URL)
        self.assertEqual(op["script_name"], CODACY_SCRIPT_NAME)
        self.assertEqual(op["interpreter"], "bash")

    def test_plan_emits_curl_upgrade_op_when_present(self) -> None:
        home = self.make_home()
        runner = FakeRunner(
            which={"dpkg-query": "/usr/bin/dpkg-query", "codacy-cli": "/usr/local/bin/codacy-cli"},
        )
        plan = build_tool_install_plan(home, runner=runner)
        ops = [op for op in plan["operations"] if op.get("entry_id") == CODACY_ENTRY_ID]
        self.assertEqual(len(ops), 1)
        self.assertEqual(ops[0]["type"], "tool_install_curl")
        self.assertEqual(ops[0]["mode"], "upgrade")

    def test_plan_entry_state_missing_when_not_found(self) -> None:
        home = self.make_home()
        runner = FakeRunner(which={"dpkg-query": "/usr/bin/dpkg-query"})
        plan = build_tool_install_plan(home, runner=runner)
        entry = next(e for e in plan["entries"] if e.get("entry_id") == CODACY_ENTRY_ID)
        self.assertEqual(entry["state"], "missing")
        self.assertEqual(entry["action"], "install")

    def test_plan_entry_state_installed_when_found(self) -> None:
        home = self.make_home()
        runner = FakeRunner(
            which={"dpkg-query": "/usr/bin/dpkg-query", "codacy-cli": "/usr/local/bin/codacy-cli"},
        )
        plan = build_tool_install_plan(home, runner=runner)
        entry = next(e for e in plan["entries"] if e.get("entry_id") == CODACY_ENTRY_ID)
        self.assertEqual(entry["state"], "installed")
        self.assertEqual(entry["action"], "upgrade")
        self.assertEqual(entry["current_path"], "/usr/local/bin/codacy-cli")

    def test_plan_op_requires_no_sudo(self) -> None:
        home = self.make_home()
        runner = FakeRunner(which={"dpkg-query": "/usr/bin/dpkg-query"})
        plan = build_tool_install_plan(home, runner=runner)
        ops = [op for op in plan["operations"] if op.get("entry_id") == CODACY_ENTRY_ID]
        self.assertFalse(ops[0]["requires_sudo"])


class CodacyCliExecuteTests(DotfilesTestCase):
    def setUp(self) -> None:
        super().setUp()
        self._euid = mock.patch("dotfiles_tools.tool_installer.os.geteuid", return_value=1000, create=True)
        self._euid.start()
        self.addCleanup(self._euid.stop)

    def _make_curl_op(self, cache_dir: Path) -> dict:
        return {
            "type": "tool_install_curl",
            "mode": "install",
            "url": CODACY_INSTALL_URL,
            "script_name": CODACY_SCRIPT_NAME,
            "interpreter": "bash",
            "requires_sudo": False,
            "cache_dir": str(cache_dir),
        }

    def test_execute_downloads_and_runs_script(self) -> None:
        home = self.make_home()
        cache_dir = home / TOOL_CACHE_REL
        runner = FakeRunner(which={"bash": "/bin/bash"})
        op = self._make_curl_op(cache_dir)
        result = execute_tool_install_operation(op, runner=runner, cache_dir=cache_dir)
        self.assertEqual(result, 1)
        self.assertEqual(len(runner.downloads), 1)
        downloaded_url, downloaded_path = runner.downloads[0]
        self.assertEqual(downloaded_url, CODACY_INSTALL_URL)
        self.assertEqual(downloaded_path.name, CODACY_SCRIPT_NAME)
        ran = [cmd for cmd in runner.commands if CODACY_SCRIPT_NAME in " ".join(str(c) for c in cmd)]
        self.assertTrue(ran, "installer script was not executed")

    def test_execute_uses_bash_not_sh(self) -> None:
        home = self.make_home()
        cache_dir = home / TOOL_CACHE_REL
        runner = FakeRunner(which={"bash": "/bin/bash"})
        execute_tool_install_operation(self._make_curl_op(cache_dir), runner=runner, cache_dir=cache_dir)
        script_cmds = [cmd for cmd in runner.commands if CODACY_SCRIPT_NAME in " ".join(str(c) for c in cmd)]
        self.assertTrue(script_cmds)
        self.assertEqual(Path(script_cmds[0][0]).name, "bash")

    def test_execute_no_sudo_prefix_when_requires_sudo_false(self) -> None:
        home = self.make_home()
        cache_dir = home / TOOL_CACHE_REL
        runner = FakeRunner(which={"bash": "/bin/bash"})
        execute_tool_install_operation(self._make_curl_op(cache_dir), runner=runner, cache_dir=cache_dir)
        script_cmds = [cmd for cmd in runner.commands if CODACY_SCRIPT_NAME in " ".join(str(c) for c in cmd)]
        self.assertTrue(script_cmds)
        self.assertNotIn("sudo", script_cmds[0])


class CodacyCliVerifyTests(DotfilesTestCase):
    def test_verify_returns_result_for_codacy_cli(self) -> None:
        home = self.make_home()
        runner = FakeRunner(which={"codacy-cli": "/usr/local/bin/codacy-cli"})
        results = verify_installed_tools(home, runner=runner, env={})
        codacy_result = next((r for r in results if r["entry_id"] == CODACY_ENTRY_ID), None)
        self.assertIsNotNone(codacy_result)
        self.assertTrue(codacy_result["verified"])
        self.assertEqual(codacy_result["path"], "/usr/local/bin/codacy-cli")
        self.assertEqual(codacy_result["command"], "codacy-cli")

    def test_verify_unverified_when_not_found(self) -> None:
        home = self.make_home()
        runner = FakeRunner(which={})
        results = verify_installed_tools(home, runner=runner, env={})
        codacy_result = next((r for r in results if r["entry_id"] == CODACY_ENTRY_ID), None)
        self.assertIsNotNone(codacy_result)
        self.assertFalse(codacy_result["verified"])
        self.assertIsNone(codacy_result["path"])

    def test_post_install_skipped_when_not_present(self) -> None:
        home = self.make_home()
        runner = FakeRunner(which={})
        results = run_post_install_actions(home, runner=runner, env={})
        codacy_results = [r for r in results if r.get("tool") == "codacy-cli"]
        self.assertEqual(codacy_results, [], "no post_install actions expected for codacy-cli")


class CodacyCliWrapperTests(DotfilesTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.wrapper_text = CODACY_WRAPPER.read_text()

    def test_wrapper_keeps_pipefail_enabled(self) -> None:
        self.assertIn("set -euo pipefail", self.wrapper_text)
        self.assertNotIn("set -e +o pipefail", self.wrapper_text)

    def test_wrapper_defines_fatal(self) -> None:
        self.assertIn("fatal()", self.wrapper_text)

    def test_wrapper_executes_command_without_eval(self) -> None:
        self.assertIn('exec "$run_command" "$@"', self.wrapper_text)
        self.assertNotIn('eval "$run_command $*"', self.wrapper_text)

    def test_wrapper_rejects_empty_latest_version(self) -> None:
        self.assertIn('could not determine the latest Codacy CLI version', self.wrapper_text)
