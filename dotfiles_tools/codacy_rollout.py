from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import subprocess  # nosec B404 -- subprocess use is intentional; args are internal, never user input
from typing import Any, Iterable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


EXPECTED_CODACY_CHECKS = [
    "Codacy Static Code Analysis",
    "Codacy Coverage Variation",
    "Codacy Diff Coverage",
]


@dataclass(frozen=True)
class RepositoryItem:
    repo: str
    local_path: str
    language_profile: str
    test_workflow: str
    test_command: str
    coverage_command: str
    coverage_reports: list[str]
    expected_checks: list[str]

    @property
    def expected_codacy_checks(self) -> list[str]:
        return [check for check in self.expected_checks if check.startswith("Codacy ")]


@dataclass(frozen=True)
class Inventory:
    repositories: list[RepositoryItem]


@dataclass(frozen=True)
class AuditCheck:
    check_id: str
    status: str
    detail: str
    remediation: str = ""


@dataclass(frozen=True)
class AuditResult:
    repo: str
    status: str
    checks: list[AuditCheck]

    def to_text(self) -> str:
        lines = [f"{self.status} {self.repo}"]
        for check in self.checks:
            line = f"{check.status} {check.check_id}: {check.detail}"
            if check.remediation:
                line += f" Remediation: {check.remediation}"
            lines.append(line)
        return "\n".join(lines) + "\n"

    def to_dict(self) -> dict[str, Any]:
        return {
            "repo": self.repo,
            "status": self.status,
            "checks": [
                {
                    "id": check.check_id,
                    "status": check.status,
                    "detail": check.detail,
                    "remediation": check.remediation,
                }
                for check in self.checks
            ],
        }


def load_inventory(path: Path) -> Inventory:
    raw = json.loads(path.read_text())
    root = path.parent
    repositories = []
    for item in raw.get("repositories", []):
        item = dict(item)
        local_path = Path(item["local_path"])
        if not local_path.is_absolute():
            local_path = (root / local_path).resolve()
        repositories.append(
            RepositoryItem(
                repo=item["repo"],
                local_path=str(local_path),
                language_profile=item["language_profile"],
                test_workflow=item["test_workflow"],
                test_command=item["test_command"],
                coverage_command=item["coverage_command"],
                coverage_reports=list(item.get("coverage_reports", [])),
                expected_checks=list(item["expected_checks"]),
            )
        )
    return Inventory(repositories=repositories)


def audit_repository(item: RepositoryItem | dict[str, Any], github: Any, codacy: Any) -> AuditResult:
    repo_item = _coerce_item(item)
    checks: list[AuditCheck] = []
    default_branch = github.default_branch(repo_item.repo)
    ruleset = github.ruleset_summary(repo_item.repo, default_branch)
    classic = github.branch_protection_summary(repo_item.repo, default_branch)
    codacy_state = codacy.repository_state(repo_item.repo)
    workflow_text = _read_workflow_text(Path(repo_item.local_path))

    checks.extend(_audit_codacy(repo_item, codacy_state))
    checks.extend(_audit_github_protection(repo_item, ruleset, classic))
    checks.extend(_audit_workflow(repo_item, workflow_text))
    checks.extend(_audit_github_runtime(repo_item, github, default_branch))

    status = "FAIL" if any(check.status == "FAIL" for check in checks) else "WARN" if any(check.status == "WARN" for check in checks) else "PASS"
    return AuditResult(repo=repo_item.repo, status=status, checks=checks)


def plan_repository(item: RepositoryItem | dict[str, Any]) -> dict[str, Any]:
    repo_item = _coerce_item(item)
    return {
        "repo": repo_item.repo,
        "workflow": {
            "language_profile": repo_item.language_profile,
            "job": repo_item.test_workflow,
            "test_command": repo_item.test_command,
            "coverage_command": repo_item.coverage_command,
            "coverage_reports": repo_item.coverage_reports,
            "coverage_upload_env": {
                "CODACY_ACCOUNT_TOKEN": "${{ secrets.CODACY_ACCOUNT_TOKEN }}",
                "CODACY_API_TOKEN": "${{ secrets.CODACY_ACCOUNT_TOKEN }}",
                "CODACY_ORGANIZATION_PROVIDER": "gh",
                "CODACY_USERNAME": repo_item.repo.split("/", 1)[0],
                "CODACY_PROJECT_NAME": repo_item.repo.split("/", 1)[1],
            },
        },
        "ruleset": {
            "target": "default_branch",
            "requires_pull_request": True,
            "blocks_force_pushes": True,
            "blocks_deletions": True,
            "required_checks": repo_item.expected_checks,
        },
    }


def audit_inventory(inventory: Inventory, github: Any, codacy: Any) -> list[AuditResult]:
    return [audit_repository(item, github, codacy) for item in inventory.repositories]


def find_repository(inventory: Inventory, repo: str | None = None, project: Path | None = None) -> RepositoryItem:
    if repo:
        for item in inventory.repositories:
            if item.repo == repo:
                return item
        raise ValueError(f"repo not found in codacy-rollout.json: {repo}")
    if project:
        project_path = project.resolve()
        for item in inventory.repositories:
            if Path(item.local_path).resolve() == project_path:
                return item
        raise ValueError(f"project not found in codacy-rollout.json: {project}")
    raise ValueError("repo or project is required")


class GitHubCliClient:
    def default_branch(self, repo: str) -> str:
        return self._run(["gh", "api", f"repos/{repo}", "--jq", ".default_branch"]) or "main"

    def ruleset_summary(self, repo: str, default_branch: str) -> dict[str, Any]:
        data = self._run_json(["gh", "api", f"repos/{repo}/rulesets", "--paginate"])
        return _summarize_rulesets(data, default_branch)

    def branch_protection_summary(self, repo: str, default_branch: str) -> dict[str, Any]:
        data = self._run_json(["gh", "api", f"repos/{repo}/branches/{default_branch}/protection"])
        return _summarize_branch_protection(data)

    def repository_secret_names(self, repo: str) -> list[str]:
        output = self._run(["gh", "secret", "list", "-R", repo, "--json", "name", "--jq", ".[].name"])
        return [line.strip() for line in output.splitlines() if line.strip()]

    def latest_check_runs(self, repo: str, default_branch: str) -> dict[str, str]:
        output = self._run(
            [
                "gh",
                "api",
                f"repos/{repo}/commits/{default_branch}/check-runs",
                "--paginate",
                "--jq",
                '.check_runs[] | "\\(.name)\\t\\(.conclusion // .status)"',
            ]
        )
        checks: dict[str, str] = {}
        for line in output.splitlines():
            name, _, status = line.partition("\t")
            if name:
                checks[name] = status
        return checks

    def _run(self, args: list[str]) -> str:
        # nosec B603 # nosemgrep: python.lang.security.audit.dangerous-subprocess-use-audit.dangerous-subprocess-use-audit
        # args come from internal `gh api ...` invocations in this module; never user input.
        result = subprocess.run(args, capture_output=True, text=True, check=False)  # nosec B603
        if result.returncode != 0:
            return ""
        return result.stdout.strip()

    def _run_json(self, args: list[str]) -> Any:
        output = self._run(args)
        if not output:
            return {}
        try:
            return json.loads(output)
        except json.JSONDecodeError:
            values = []
            for line in output.splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    values.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
            return values


class CodacyApiClient:
    def __init__(self, token: str | None = None) -> None:
        self.token = token or os.environ.get("CODACY_ACCOUNT_TOKEN", "") or os.environ.get("CODACY_API_TOKEN", "")

    def repository_state(self, repo: str) -> dict[str, Any]:
        fixture_state = _load_codacy_fixture_state(repo)
        if fixture_state is not None:
            return fixture_state
        if not self.token:
            return _codacy_state_missing_token()
        fetched = _fetch_codacy_repository(repo, self.token)
        if "error" in fetched:
            return fetched
        return _build_codacy_state(fetched["data"])


def _load_codacy_fixture_state(repo: str) -> dict[str, Any] | None:
    fixture = os.environ.get("CODACY_AUDIT_CODACY_STATE_JSON")
    if not fixture:
        return None
    data = json.loads(Path(fixture).read_text())
    return data.get(repo, data)


def _codacy_state_missing_token() -> dict[str, Any]:
    return {
        "exists": False,
        "coding_standard_applied": False,
        "gate_policy_applied": False,
        "latest_pr_quality": {},
        "error": "CODACY_ACCOUNT_TOKEN is not set",
    }


def _fetch_codacy_repository(repo: str, token: str) -> dict[str, Any]:
    owner, name = repo.split("/", 1)
    url = f"https://app.codacy.com/api/v3/analysis/organizations/gh/{owner}/repositories/{name}"
    request = Request(url, headers={"api-token": token})
    try:
        # nosec B310 -- URL is hardcoded https to app.codacy.com; no user-controlled scheme.
        with urlopen(request, timeout=15) as response:  # nosec B310
            data = json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        return {"exists": False, "error": f"Codacy API HTTP {error.code}"}
    except (OSError, URLError, json.JSONDecodeError) as error:
        return {"exists": False, "error": str(error)}
    return {"data": data.get("data", data)}


def _build_codacy_state(body: dict[str, Any]) -> dict[str, Any]:
    coding_standard_keys = ("codingStandard", "coding_standard", "codingStandardName", "codingStandardId")
    gate_keys = ("qualityGate", "quality_gate", "qualityGateName", "qualityGateId")
    return {
        "exists": True,
        "coding_standard_applied": any(body.get(key) for key in coding_standard_keys),
        "gate_policy_applied": any(body.get(key) for key in gate_keys),
        "latest_pr_quality": body.get("latest_pr_quality") or body.get("latestPullRequest") or {},
    }


def render_audit_table(results: Iterable[AuditResult]) -> str:
    rows = []
    for result in results:
        failures = [check for check in result.checks if check.status == "FAIL"]
        warnings = [check for check in result.checks if check.status == "WARN"]
        rows.append(f"{result.status}\t{result.repo}\tFAIL={len(failures)}\tWARN={len(warnings)}")
    return "\n".join(rows) + ("\n" if rows else "")


def _coerce_item(item: RepositoryItem | dict[str, Any]) -> RepositoryItem:
    if isinstance(item, RepositoryItem):
        return item
    return RepositoryItem(
        repo=item["repo"],
        local_path=item["local_path"],
        language_profile=item["language_profile"],
        test_workflow=item["test_workflow"],
        test_command=item["test_command"],
        coverage_command=item["coverage_command"],
        coverage_reports=list(item.get("coverage_reports", [])),
        expected_checks=list(item["expected_checks"]),
    )


def _audit_codacy(item: RepositoryItem, state: dict[str, Any]) -> list[AuditCheck]:
    checks = [
        _check(
            "repository_onboarded",
            bool(state.get("exists")),
            "Codacy repository exists",
            f"Add {item.repo} to Codacy and rerun codacy-audit.",
            state.get("error", "Codacy repository is missing"),
        ),
        _check(
            "coding_standard",
            bool(state.get("coding_standard_applied")),
            "Codacy coding standard is applied",
            "Apply the organization coding standard in Codacy.",
            "Codacy coding standard is missing",
        ),
        _check(
            "gate_policy",
            bool(state.get("gate_policy_applied")),
            "Codacy gate policy is applied",
            "Apply the strict quality gate in Codacy.",
            "Codacy gate policy is missing",
        ),
    ]
    cause = (
        state.get("latest_pr_quality", {})
        .get("coverage", {})
        .get("diffCoverage", {})
        .get("cause")
    )
    checks.append(
        _check(
            "coverage_pr_ready",
            cause in (None, "", "None"),
            "Latest Codacy PR coverage has requirements",
            "Upload coverage for the PR head and target/common ancestor.",
            f"Codacy diff coverage cause is {cause}",
        )
    )
    return checks


def _audit_github_protection(item: RepositoryItem, ruleset: dict[str, Any], classic: dict[str, Any]) -> list[AuditCheck]:
    required_checks = sorted(set(ruleset.get("required_checks", [])) | set(classic.get("required_checks", [])))
    missing = [check for check in item.expected_checks if check not in required_checks]
    protected = bool(ruleset.get("protects_default_branch") or classic.get("protects_default_branch"))
    requires_pr = bool(ruleset.get("requires_pull_request") or classic.get("requires_pull_request"))
    blocks_force = bool(ruleset.get("blocks_force_pushes") or classic.get("blocks_force_pushes"))
    blocks_delete = bool(ruleset.get("blocks_deletions") or classic.get("blocks_deletions"))
    return [
        _check("default_branch_protected", protected, "Default branch is protected", "Enable a GitHub ruleset for the default branch.", "Default branch is not protected"),
        _check("pull_request_required", requires_pr, "Pull requests are required", "Enable a pull request requirement in the GitHub ruleset.", "Pull requests are not required"),
        _check("force_push_blocked", blocks_force, "Force pushes are blocked", "Add the non_fast_forward GitHub ruleset rule.", "Force pushes are not blocked"),
        _check("deletion_blocked", blocks_delete, "Deletions are blocked", "Add the deletion GitHub ruleset rule.", "Branch deletion is not blocked"),
        _check("required_status_checks", not missing, "Strict required checks are configured", "Require: " + ", ".join(missing), "Missing required checks: " + ", ".join(missing)),
    ]


def _audit_workflow(item: RepositoryItem, workflow_text: str) -> list[AuditCheck]:
    expected_reports = item.coverage_reports or ["coverage.xml"]
    has_report = any(report in workflow_text for report in expected_reports)
    has_identity = all(token in workflow_text for token in ("CODACY_ORGANIZATION_PROVIDER", "CODACY_USERNAME", "CODACY_PROJECT_NAME"))
    return [
        _check("coverage_generation", "coverage" in workflow_text and has_report, "Workflow generates coverage", "Add coverage generation before Codacy upload.", "Workflow does not generate coverage"),
        _check("coverage_upload", "coverage.codacy.com/get.sh" in workflow_text and "CODACY_ACCOUNT_TOKEN" in workflow_text and has_report, "Workflow uploads coverage to Codacy", "Add an Upload coverage to Codacy step.", "Workflow does not upload coverage to Codacy"),
        _check("coverage_upload_identity", has_identity, "Coverage upload includes Codacy repo identity", f"Set CODACY_ORGANIZATION_PROVIDER=gh, CODACY_USERNAME={item.repo.split('/', 1)[0]}, and CODACY_PROJECT_NAME={item.repo.split('/', 1)[1]}.", "Coverage upload identity is missing"),
        _check("coverage_upload_strict", "continue-on-error: true" not in workflow_text, "Coverage upload is blocking", "Remove continue-on-error from the Codacy coverage upload.", "Coverage upload uses continue-on-error"),
    ]


def _audit_github_runtime(item: RepositoryItem, github: Any, default_branch: str) -> list[AuditCheck]:
    secrets = github.repository_secret_names(item.repo)
    latest = github.latest_check_runs(item.repo, default_branch)
    missing = [check for check in item.expected_checks if check not in latest]
    failing = [f"{check}={latest[check]}" for check in item.expected_checks if latest.get(check) not in (None, "success")]
    return [
        _check("codacy_secret", "CODACY_ACCOUNT_TOKEN" in secrets, "CODACY account token secret is present", "Add CODACY_ACCOUNT_TOKEN as a GitHub Actions repository or organization secret.", "CODACY_ACCOUNT_TOKEN secret is missing"),
        _check("latest_checks", not missing and not failing, "Latest GitHub checks include strict profile", "Rerun CI or repair checks: " + ", ".join(missing + failing), "Latest checks are not strict-ready: " + ", ".join(missing + failing)),
    ]


def _check(check_id: str, ok: bool, pass_detail: str, remediation: str, fail_detail: str) -> AuditCheck:
    if ok:
        return AuditCheck(check_id=check_id, status="PASS", detail=pass_detail)
    return AuditCheck(check_id=check_id, status="FAIL", detail=fail_detail, remediation=remediation)


def _read_workflow_text(project: Path) -> str:
    workflow_dir = project / ".github" / "workflows"
    if not workflow_dir.is_dir():
        return ""
    parts = []
    for path in sorted(list(workflow_dir.glob("*.yml")) + list(workflow_dir.glob("*.yaml"))):
        parts.append(path.read_text(errors="ignore"))
    return "\n".join(parts)


def _summarize_rulesets(data: Any, default_branch: str) -> dict[str, Any]:
    summary = _empty_protection_summary()
    rulesets = data if isinstance(data, list) else []
    for ruleset in rulesets:
        if not _ruleset_applies(ruleset, default_branch):
            continue
        summary["protects_default_branch"] = True
        for rule in ruleset.get("rules", []) or []:
            _apply_rule_to_summary(rule, summary)
    summary["required_checks"] = sorted(set(summary["required_checks"]))
    return summary


def _ruleset_applies(ruleset: Any, default_branch: str) -> bool:
    if not isinstance(ruleset, dict) or ruleset.get("target", "branch") != "branch":
        return False
    if ruleset.get("enforcement") == "disabled":
        return False
    return _ruleset_matches_default_branch(ruleset, default_branch)


def _apply_rule_to_summary(rule: dict[str, Any], summary: dict[str, Any]) -> None:
    rule_type = rule.get("type")
    handlers = {
        "pull_request": lambda r, s: s.__setitem__("requires_pull_request", True),
        "non_fast_forward": lambda r, s: s.__setitem__("blocks_force_pushes", True),
        "deletion": lambda r, s: s.__setitem__("blocks_deletions", True),
        "required_status_checks": _append_required_checks_from_rule,
    }
    handler = handlers.get(rule_type)
    if handler:
        handler(rule, summary)


def _append_required_checks_from_rule(rule: dict[str, Any], summary: dict[str, Any]) -> None:
    for status_check in (rule.get("parameters") or {}).get("required_status_checks", []) or []:
        context = status_check.get("context") or status_check.get("name")
        if context:
            summary["required_checks"].append(context)


def _summarize_branch_protection(data: Any) -> dict[str, Any]:
    summary = _empty_protection_summary()
    if not isinstance(data, dict) or not data:
        return summary
    summary["protects_default_branch"] = True
    summary["requires_pull_request"] = bool(data.get("required_pull_request_reviews"))
    summary["blocks_force_pushes"] = not bool((data.get("allow_force_pushes") or {}).get("enabled"))
    summary["blocks_deletions"] = not bool((data.get("allow_deletions") or {}).get("enabled"))
    summary["required_checks"] = _branch_protection_required_checks(data.get("required_status_checks") or {})
    return summary


def _branch_protection_required_checks(required: dict[str, Any]) -> list[str]:
    checks: list[str] = []
    checks.extend(required.get("contexts") or [])
    checks.extend(item.get("context") for item in required.get("checks") or [] if item.get("context"))
    return sorted(set(checks))


def _empty_protection_summary() -> dict[str, Any]:
    return {
        "protects_default_branch": False,
        "requires_pull_request": False,
        "blocks_force_pushes": False,
        "blocks_deletions": False,
        "required_checks": [],
    }


def _ruleset_matches_default_branch(ruleset: dict[str, Any], default_branch: str) -> bool:
    conditions = ruleset.get("conditions") or {}
    ref_name = conditions.get("ref_name") or {}
    includes = ref_name.get("include") or []
    if not includes:
        return True
    expected = {default_branch, f"refs/heads/{default_branch}", "~DEFAULT_BRANCH"}
    return any(value in expected for value in includes)
