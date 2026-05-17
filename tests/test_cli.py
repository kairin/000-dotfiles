from __future__ import annotations

import io
import json
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import MagicMock, patch

from tests.helpers import DotfilesTestCase, REPO_ROOT
from tests.test_codacy_rollout import FakeCodacy, FakeGitHub

from dotfiles_tools.cli import main, build_parser


class CliParserTests(DotfilesTestCase):
    def test_build_parser_registers_all_subcommands(self) -> None:
        parser = build_parser()
        subparsers_action = None
        for action in parser._subparsers._actions:
            if hasattr(action, "choices") and action.choices:
                subparsers_action = action
                break
        self.assertIsNotNone(subparsers_action)
        subcommands = set(subparsers_action.choices.keys())
        expected = {
            "doctor",
            "plan",
            "apply",
            "bootstrap-plan",
            "bootstrap-apply",
            "bootstrap-install-tools-plan",
            "bootstrap-install-tools",
            "bootstrap-install-tools-post",
            "init-project",
            "codacy-audit",
            "codacy-plan",
        }
        self.assertEqual(subcommands, expected)

    def test_doctor_routes_to_run_doctor(self) -> None:
        mock_report = MagicMock(status="ok")
        with patch("dotfiles_tools.cli.run_doctor", return_value=mock_report) as mock_fn:
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["doctor", "--repo", str(REPO_ROOT), "--home", "/tmp/h"])
            self.assertEqual(rc, 0)
            mock_fn.assert_called_once()

    def test_plan_routes_to_build_plan(self) -> None:
        mock_report = MagicMock(status="ok")
        with patch("dotfiles_tools.cli.build_plan", return_value=mock_report) as mock_fn:
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["plan", "--repo", str(REPO_ROOT), "--home", "/tmp/h"])
            self.assertEqual(rc, 0)
            mock_fn.assert_called_once()

    def test_apply_routes_to_apply_plan(self) -> None:
        mock_report = MagicMock(status="ok")
        with patch("dotfiles_tools.cli.apply_plan", return_value=mock_report) as mock_fn:
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "apply",
                        "--repo",
                        str(REPO_ROOT),
                        "--home",
                        "/tmp/h",
                        "--backup-dir",
                        "/tmp/b",
                    ]
                )
            self.assertEqual(rc, 0)
            mock_fn.assert_called_once()

    def test_bootstrap_plan_routes(self) -> None:
        mock_report = MagicMock(status="ok")
        with patch(
            "dotfiles_tools.cli.build_bootstrap_plan", return_value=mock_report
        ) as mock_fn:
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["bootstrap-plan", "--repo", str(REPO_ROOT), "--home", "/tmp/h"])
            self.assertEqual(rc, 0)
            mock_fn.assert_called_once()

    def test_bootstrap_apply_routes(self) -> None:
        mock_report = MagicMock(status="ok")
        with patch("dotfiles_tools.cli.apply_bootstrap", return_value=mock_report) as mock_fn:
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["bootstrap-apply", "--repo", str(REPO_ROOT), "--home", "/tmp/h"])
            self.assertEqual(rc, 0)
            mock_fn.assert_called_once()

    def test_install_tools_plan_routes(self) -> None:
        mock_report = MagicMock(status="ok")
        with patch(
            "dotfiles_tools.cli.build_tool_install_subplan", return_value=mock_report
        ) as mock_fn:
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    ["bootstrap-install-tools-plan", "--repo", str(REPO_ROOT), "--home", "/tmp/h"]
                )
            self.assertEqual(rc, 0)
            mock_fn.assert_called_once()

    def test_install_tools_apply_routes(self) -> None:
        mock_report = MagicMock(status="ok")
        with patch("dotfiles_tools.cli.apply_tool_installs", return_value=mock_report) as mock_fn:
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "bootstrap-install-tools",
                        "--repo",
                        str(REPO_ROOT),
                        "--home",
                        "/tmp/h",
                    ]
                )
            self.assertEqual(rc, 0)
            mock_fn.assert_called_once()

    def test_install_tools_post_routes(self) -> None:
        mock_report = MagicMock(status="ok")
        with patch(
            "dotfiles_tools.cli.run_tool_install_post_install", return_value=mock_report
        ) as mock_fn:
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    ["bootstrap-install-tools-post", "--repo", str(REPO_ROOT), "--home", "/tmp/h"]
                )
            self.assertEqual(rc, 0)
            mock_fn.assert_called_once()

    def test_init_project_routes(self) -> None:
        project = self.make_project()
        vars_file = self.vars_file(project)
        mock_report = MagicMock(status="ok")
        with patch("dotfiles_tools.cli.init_project", return_value=mock_report) as mock_fn:
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "init-project",
                        "--repo",
                        str(REPO_ROOT),
                        "--project",
                        str(project),
                        "--vars",
                        str(vars_file),
                    ]
                )
            self.assertEqual(rc, 0)
            mock_fn.assert_called_once()

    def test_exit_code_1_when_report_failed(self) -> None:
        mock_report = MagicMock(status="failed")
        with patch("dotfiles_tools.cli.run_doctor", return_value=mock_report):
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["doctor", "--repo", str(REPO_ROOT), "--home", "/tmp/h"])
            self.assertEqual(rc, 1)

    def test_exit_code_0_when_report_ok(self) -> None:
        mock_report = MagicMock(status="ok")
        with patch("dotfiles_tools.cli.run_doctor", return_value=mock_report):
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["doctor", "--repo", str(REPO_ROOT), "--home", "/tmp/h"])
            self.assertEqual(rc, 0)

    def test_exit_code_1_when_report_partial(self) -> None:
        mock_report = MagicMock(status="partial")
        with patch("dotfiles_tools.cli.run_doctor", return_value=mock_report):
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["doctor", "--repo", str(REPO_ROOT), "--home", "/tmp/h"])
            self.assertEqual(rc, 1)

    def test_json_flag_calls_render_with_json(self) -> None:
        mock_report = MagicMock(status="ok")
        with patch("dotfiles_tools.cli.run_doctor", return_value=mock_report):
            with patch("dotfiles_tools.cli.render", return_value="{}") as mock_render:
                buf = io.StringIO()
                with redirect_stdout(buf):
                    main(["doctor", "--repo", str(REPO_ROOT), "--home", "/tmp/h", "--json"])
                mock_render.assert_called_once()
                call_args = mock_render.call_args
                self.assertTrue(call_args[0][1])

    def test_codacy_plan_subcommand(self) -> None:
        inventory_file = REPO_ROOT / "codacy-rollout.json"
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(
                [
                    "codacy-plan",
                    "--repo",
                    str(REPO_ROOT),
                    "--inventory",
                    str(inventory_file),
                    "--target-repo",
                    "kairin/000-dotfiles",
                ]
            )
        self.assertEqual(rc, 0)
        output = buf.getvalue()
        parsed = json.loads(output)
        self.assertIn("repo", parsed)
        self.assertEqual(parsed["repo"], "kairin/000-dotfiles")

    def test_codacy_audit_single_repo(self) -> None:
        inventory_file = REPO_ROOT / "codacy-rollout.json"
        with patch("dotfiles_tools.cli.GitHubCliClient", return_value=FakeGitHub()):
            with patch("dotfiles_tools.cli.CodacyApiClient", return_value=FakeCodacy()):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "codacy-audit",
                            "--repo",
                            str(REPO_ROOT),
                            "--inventory",
                            str(inventory_file),
                            "--target-repo",
                            "kairin/000-dotfiles",
                        ]
                    )
                output = buf.getvalue()
        self.assertIn("kairin/000-dotfiles", output)

    def test_codacy_audit_single_repo_fail(self) -> None:
        inventory_file = REPO_ROOT / "codacy-rollout.json"
        with patch("dotfiles_tools.cli.GitHubCliClient", return_value=FakeGitHub()):
            with patch(
                "dotfiles_tools.cli.CodacyApiClient", return_value=FakeCodacy(exists=False)
            ):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "codacy-audit",
                            "--repo",
                            str(REPO_ROOT),
                            "--inventory",
                            str(inventory_file),
                            "--target-repo",
                            "kairin/000-dotfiles",
                        ]
                    )
        self.assertEqual(rc, 1)

    def test_codacy_audit_all_text(self) -> None:
        inventory_file = REPO_ROOT / "codacy-rollout.json"
        with patch("dotfiles_tools.cli.GitHubCliClient", return_value=FakeGitHub()):
            with patch("dotfiles_tools.cli.CodacyApiClient", return_value=FakeCodacy()):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "codacy-audit",
                            "--repo",
                            str(REPO_ROOT),
                            "--inventory",
                            str(inventory_file),
                            "--all",
                        ]
                    )
                output = buf.getvalue()
        self.assertIn("kairin/000-dotfiles", output)
        self.assertIsInstance(rc, int)

    def test_codacy_audit_all_json(self) -> None:
        inventory_file = REPO_ROOT / "codacy-rollout.json"
        with patch("dotfiles_tools.cli.GitHubCliClient", return_value=FakeGitHub()):
            with patch("dotfiles_tools.cli.CodacyApiClient", return_value=FakeCodacy()):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "codacy-audit",
                            "--repo",
                            str(REPO_ROOT),
                            "--inventory",
                            str(inventory_file),
                            "--all",
                            "--json",
                        ]
                    )
                output = buf.getvalue()
        parsed = json.loads(output)
        self.assertIsInstance(parsed, list)
        self.assertGreater(len(parsed), 0)
        self.assertIsInstance(rc, int)

    def test_codacy_audit_single_json(self) -> None:
        inventory_file = REPO_ROOT / "codacy-rollout.json"
        with patch("dotfiles_tools.cli.GitHubCliClient", return_value=FakeGitHub()):
            with patch("dotfiles_tools.cli.CodacyApiClient", return_value=FakeCodacy()):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "codacy-audit",
                            "--repo",
                            str(REPO_ROOT),
                            "--inventory",
                            str(inventory_file),
                            "--target-repo",
                            "kairin/000-dotfiles",
                            "--json",
                        ]
                    )
                output = buf.getvalue()
        parsed = json.loads(output)
        self.assertIsInstance(parsed, dict)
        self.assertIn("repo", parsed)
        self.assertIn("status", parsed)
