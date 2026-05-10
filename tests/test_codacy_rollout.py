from __future__ import annotations

import json
from pathlib import Path
from textwrap import dedent

from tests.helpers import DotfilesTestCase, REPO_ROOT

from dotfiles_tools.codacy_rollout import (
    EXPECTED_CODACY_CHECKS,
    audit_repository,
    load_inventory,
    plan_repository,
)


class FakeGitHub:
    def __init__(
        self,
        *,
        required_checks: list[str] | None = None,
        latest_checks: dict[str, str] | None = None,
        secret_names: list[str] | None = None,
    ) -> None:
        self.required_checks = required_checks or [
            "codacy-safety-net",
            *EXPECTED_CODACY_CHECKS,
        ]
        self.latest_checks = latest_checks or {
            "codacy-safety-net": "success",
            **{check: "success" for check in EXPECTED_CODACY_CHECKS},
        }
        self.secret_names = secret_names or ["CODACY_ACCOUNT_TOKEN"]

    def default_branch(self, repo: str) -> str:
        return "main"

    def ruleset_summary(self, repo: str, default_branch: str) -> dict:
        return {
            "protects_default_branch": True,
            "requires_pull_request": True,
            "blocks_force_pushes": True,
            "blocks_deletions": True,
            "required_checks": self.required_checks,
        }

    def branch_protection_summary(self, repo: str, default_branch: str) -> dict:
        return {
            "protects_default_branch": False,
            "requires_pull_request": False,
            "blocks_force_pushes": False,
            "blocks_deletions": False,
            "required_checks": [],
        }

    def repository_secret_names(self, repo: str) -> list[str]:
        return self.secret_names

    def latest_check_runs(self, repo: str, default_branch: str) -> dict[str, str]:
        return self.latest_checks


class FakeCodacy:
    def __init__(
        self,
        *,
        exists: bool = True,
        coding_standard: bool = True,
        gate_policy: bool = True,
        pr_quality: dict | None = None,
    ) -> None:
        self.exists = exists
        self.coding_standard = coding_standard
        self.gate_policy = gate_policy
        self.pr_quality = pr_quality or {"coverage": {"diffCoverage": {"cause": None}}}

    def repository_state(self, repo: str) -> dict:
        return {
            "exists": self.exists,
            "coding_standard_applied": self.coding_standard,
            "gate_policy_applied": self.gate_policy,
            "latest_pr_quality": self.pr_quality,
        }


class CodacyRolloutTests(DotfilesTestCase):
    def write_workflow(self, project: Path, body: str) -> None:
        workflow_dir = project / ".github" / "workflows"
        workflow_dir.mkdir(parents=True)
        (workflow_dir / "validation.yml").write_text(dedent(body))

    def inventory_item(self, project: Path) -> dict:
        return {
            "repo": "kairin/example",
            "local_path": str(project),
            "language_profile": "python",
            "test_workflow": "codacy-safety-net",
            "test_command": "uv run python -m unittest discover -s tests",
            "coverage_command": "uv run --with coverage coverage run -m unittest discover -s tests && uv run --with coverage coverage xml",
            "coverage_reports": ["coverage.xml"],
            "expected_checks": ["codacy-safety-net", *EXPECTED_CODACY_CHECKS],
        }

    def strict_workflow(self) -> str:
        return """
        jobs:
          codacy-safety-net:
            steps:
              - name: Run unit tests with coverage
                run: uv run --with coverage coverage run -m unittest discover -s tests
              - name: Generate coverage XML
                run: uv run --with coverage coverage xml
              - name: Upload coverage to Codacy
                env:
                  CODACY_ACCOUNT_TOKEN: ${{ secrets.CODACY_ACCOUNT_TOKEN }}
                  CODACY_ORGANIZATION_PROVIDER: gh
                  CODACY_USERNAME: kairin
                  CODACY_PROJECT_NAME: example
                run: |
                  bash <(curl -Ls https://coverage.codacy.com/get.sh) report \
                    --api-token "$CODACY_ACCOUNT_TOKEN" \
                    -r coverage.xml
        """

    def test_tracked_inventory_lists_initial_active_repos(self) -> None:
        inventory = load_inventory(REPO_ROOT / "codacy-rollout.json")
        repos = [item.repo for item in inventory.repositories]

        self.assertEqual(["kairin/000-dotfiles", "kairin/BCM", "kairin/graph-obsidian"], repos)
        for item in inventory.repositories:
            self.assertEqual(["Codacy Static Code Analysis", "Codacy Coverage Variation", "Codacy Diff Coverage"], item.expected_codacy_checks)

    def test_fully_protected_repo_passes(self) -> None:
        project = self.make_project()
        self.write_workflow(project, self.strict_workflow())

        result = audit_repository(self.inventory_item(project), FakeGitHub(), FakeCodacy())

        self.assertEqual("PASS", result.status, result.to_text())
        self.assertEqual([], [check for check in result.checks if check.status != "PASS"])

    def test_missing_codacy_repository_fails_with_remediation(self) -> None:
        project = self.make_project()
        self.write_workflow(project, self.strict_workflow())

        result = audit_repository(self.inventory_item(project), FakeGitHub(), FakeCodacy(exists=False))

        self.assertEqual("FAIL", result.status)
        self.assertIn("repository_onboarded", result.to_text())
        self.assertIn("Add kairin/example to Codacy", result.to_text())

    def test_missing_coverage_upload_fails(self) -> None:
        project = self.make_project()
        self.write_workflow(project, "jobs:\n  codacy-safety-net:\n    steps: []\n")

        result = audit_repository(self.inventory_item(project), FakeGitHub(), FakeCodacy())

        self.assertEqual("FAIL", result.status)
        self.assertIn("coverage_upload", result.to_text())
        self.assertIn("Upload coverage to Codacy", result.to_text())

    def test_coverage_upload_with_continue_on_error_fails_strict_audit(self) -> None:
        project = self.make_project()
        self.write_workflow(
            project,
            self.strict_workflow()
            + "\n              - name: Legacy upload\n                continue-on-error: true\n",
        )

        result = audit_repository(self.inventory_item(project), FakeGitHub(), FakeCodacy())

        self.assertEqual("FAIL", result.status)
        self.assertIn("coverage_upload_strict", result.to_text())
        self.assertIn("Remove continue-on-error", result.to_text())

    def test_ruleset_missing_one_codacy_check_fails(self) -> None:
        project = self.make_project()
        self.write_workflow(project, self.strict_workflow())
        required = ["codacy-safety-net", "Codacy Static Code Analysis", "Codacy Coverage Variation"]

        result = audit_repository(self.inventory_item(project), FakeGitHub(required_checks=required), FakeCodacy())

        self.assertEqual("FAIL", result.status)
        self.assertIn("required_status_checks", result.to_text())
        self.assertIn("Codacy Diff Coverage", result.to_text())

    def test_codacy_missing_requirements_fails(self) -> None:
        project = self.make_project()
        self.write_workflow(project, self.strict_workflow())
        codacy = FakeCodacy(
            pr_quality={"coverage": {"diffCoverage": {"cause": "MissingRequirements"}}}
        )

        result = audit_repository(self.inventory_item(project), FakeGitHub(), codacy)

        self.assertEqual("FAIL", result.status)
        self.assertIn("coverage_pr_ready", result.to_text())
        self.assertIn("MissingRequirements", result.to_text())

    def test_plan_repository_is_read_only_and_names_required_changes(self) -> None:
        item = self.inventory_item(self.make_project())

        plan = plan_repository(item)

        self.assertEqual("kairin/example", plan["repo"])
        self.assertIn("workflow", plan)
        self.assertIn("ruleset", plan)
        self.assertEqual("${{ secrets.CODACY_ACCOUNT_TOKEN }}", plan["workflow"]["coverage_upload_env"]["CODACY_API_TOKEN"])
        self.assertEqual(item["expected_checks"], plan["ruleset"]["required_checks"])
        json.dumps(plan)
