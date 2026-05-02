from __future__ import annotations

import os
from pathlib import Path
import sys
from typing import Any, Mapping

from .backups import BackupError, create_backup
from .baseline import DEV_BASE_GROUPS, DEV_BASE_PACKAGES, TOOL_BASELINE
from .font_runner import CommandRunner
from .manifest import ManifestError, load_manifest


TOOL_CACHE_REL = ".cache/000-dotfiles/tool-installers"
DEV_BASE_ENTRY_ID = "tools.dev_base"

_APT_OP_TYPE = {"install": "tool_install_apt", "upgrade": "tool_install_apt_upgrade"}
_APT_REASON_SUFFIX = {"install": "apt", "upgrade": "apt --only-upgrade"}


__all__ = (
    "build_tool_install_plan",
    "execute_tool_install_operation",
    "verify_installed_tools",
    "run_post_install_actions",
    "TOOL_CACHE_REL",
    "DEV_BASE_ENTRY_ID",
)


def build_tool_install_plan(
    home: Path | str,
    *,
    env: Mapping[str, str] | None = None,
    path: str | None = None,
    runner: CommandRunner | None = None,
) -> dict[str, Any]:
    home_path = Path(home).expanduser().resolve()
    effective_env = dict(os.environ if env is None else env)
    effective_path = path if path is not None else effective_env.get("PATH", "")
    effective_runner = runner or CommandRunner(env=effective_env, path=effective_path)
    cache_dir = home_path / TOOL_CACHE_REL

    if not _is_linux(effective_env):
        return _unsupported_plan(effective_runner)

    entries: list[dict[str, Any]] = []
    operations: list[dict[str, Any]] = []
    tools: list[dict[str, Any]] = []

    _extend_dev_base_plan(effective_runner, cache_dir, entries, operations, tools)
    _extend_tool_baseline_plan(effective_runner, cache_dir, entries, operations, tools)

    return {"entries": entries, "operations": operations, "tools": tools}


def execute_tool_install_operation(
    op: dict[str, Any],
    *,
    runner: CommandRunner | None = None,
    cache_dir: Path | str | None = None,
) -> int:
    effective_runner = runner or CommandRunner()
    op_cache = Path(cache_dir or op.get("cache_dir") or Path.home() / TOOL_CACHE_REL)
    op_type = op["type"]
    handlers = _operation_handlers(effective_runner, op_cache)
    handler = handlers.get(op_type)
    if handler is None:
        raise RuntimeError(f"unknown tool install operation: {op_type}")
    return handler(op)


def _operation_handlers(runner: CommandRunner, cache_dir: Path) -> dict[str, Any]:
    return {
        "tool_install_apt": lambda op: _execute_apt(op, runner, mode="install"),
        "tool_install_apt_upgrade": lambda op: _execute_apt(op, runner, mode="upgrade"),
        "tool_install_apt_keyring": lambda op: _execute_apt_keyring(op, runner, cache_dir),
        "tool_install_curl": lambda op: _execute_curl(op, runner, cache_dir),
        "tool_install_npm": lambda op: _execute_npm(op, runner, mode="install"),
        "tool_install_npm_upgrade": lambda op: _execute_npm(op, runner, mode="upgrade"),
        "tool_install_uv_tool": lambda op: _execute_uv_tool(op, runner),
        "tool_install_skip": lambda op: 0,
    }


# ---------------------------------------------------------------------------
# Platform gating
# ---------------------------------------------------------------------------


def _is_linux(env: Mapping[str, str]) -> bool:
    forced = env.get("DOTFILES_TOOL_PLATFORM")
    if forced:
        return forced.lower() == "linux"
    return sys.platform.startswith("linux")


def _unsupported_plan(runner: CommandRunner) -> dict[str, Any]:
    entries = [
        {
            "entry_id": DEV_BASE_ENTRY_ID,
            "recipe": "tool_installs",
            "label": "Developer base packages",
            "command": None,
            "state": "unsupported",
            "install_method": "apt",
            "action": "manual",
            "reason": "tool installs are Linux/Ubuntu-only in v1",
        }
    ]
    for item in TOOL_BASELINE:
        if not item.get("bootstrap") or item["install_method"] == "manual":
            continue
        entries.append(
            {
                "entry_id": f"tools.{item['id']}",
                "recipe": "tool_installs",
                "label": item["label"],
                "command": item["command"],
                "state": "unsupported",
                "install_method": item["install_method"],
                "action": "manual",
                "reason": "tool installs are Linux/Ubuntu-only in v1",
            }
        )
    return {"entries": entries, "operations": [], "tools": []}


# ---------------------------------------------------------------------------
# Dev-base apt bundle
# ---------------------------------------------------------------------------


def _extend_dev_base_plan(
    runner: CommandRunner,
    cache_dir: Path,
    entries: list[dict[str, Any]],
    operations: list[dict[str, Any]],
    tools: list[dict[str, Any]],
) -> None:
    package_states = {pkg: _dpkg_installed(runner, pkg) for pkg in DEV_BASE_PACKAGES}
    missing = tuple(pkg for pkg in DEV_BASE_PACKAGES if not package_states[pkg])
    installed = tuple(pkg for pkg in DEV_BASE_PACKAGES if package_states[pkg])
    entry = _dev_base_entry(missing, installed, package_states)
    entries.append(entry)
    tools.append(entry)
    operations.extend(_dev_base_operations(missing, installed, cache_dir))


def _dev_base_entry(
    missing: tuple[str, ...],
    installed: tuple[str, ...],
    package_states: dict[str, bool],
) -> dict[str, Any]:
    state, action = _dev_base_state_action(missing, installed)
    return {
        "entry_id": DEV_BASE_ENTRY_ID,
        "recipe": "tool_installs",
        "label": "Developer base packages",
        "command": None,
        "state": state,
        "install_method": "apt",
        "action": action,
        "missing_packages": list(missing),
        "installed_packages": list(installed),
        "groups": _dev_base_groups_summary(package_states),
        "total_packages": len(DEV_BASE_PACKAGES),
    }


def _dev_base_state_action(missing: tuple[str, ...], installed: tuple[str, ...]) -> tuple[str, str]:
    if missing and installed:
        return "needs_update", "install_and_upgrade"
    if missing:
        return "missing", "install"
    return "installed", "upgrade"


def _dev_base_groups_summary(package_states: dict[str, bool]) -> list[dict[str, Any]]:
    return [
        {
            "name": name,
            "packages": list(group_pkgs),
            "installed": [pkg for pkg in group_pkgs if package_states[pkg]],
            "missing": [pkg for pkg in group_pkgs if not package_states[pkg]],
        }
        for name, group_pkgs in DEV_BASE_GROUPS
    ]


def _dev_base_operations(
    missing: tuple[str, ...],
    installed: tuple[str, ...],
    cache_dir: Path,
) -> list[dict[str, Any]]:
    ops: list[dict[str, Any]] = []
    if missing:
        ops.append(
            _apt_op(
                entry_id=DEV_BASE_ENTRY_ID,
                op_type="tool_install_apt",
                packages=list(missing),
                requires_sudo=True,
                cache_dir=cache_dir,
                reason=f"install {len(missing)} missing dev-base packages",
            )
        )
    if installed:
        ops.append(
            _apt_op(
                entry_id=DEV_BASE_ENTRY_ID,
                op_type="tool_install_apt_upgrade",
                packages=list(installed),
                requires_sudo=True,
                cache_dir=cache_dir,
                reason=f"upgrade {len(installed)} installed dev-base packages",
            )
        )
    return ops


# ---------------------------------------------------------------------------
# Tool baseline (per-tool)
# ---------------------------------------------------------------------------


def _extend_tool_baseline_plan(
    runner: CommandRunner,
    cache_dir: Path,
    entries: list[dict[str, Any]],
    operations: list[dict[str, Any]],
    tools: list[dict[str, Any]],
) -> None:
    for item in TOOL_BASELINE:
        if not item.get("bootstrap") or item["install_method"] == "manual":
            continue
        entry, ops = _plan_tool_entry(item, runner, cache_dir)
        entries.append(entry)
        tools.append(entry)
        operations.extend(ops)


def _plan_tool_entry(
    item: Mapping[str, Any],
    runner: CommandRunner,
    cache_dir: Path,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    method = item["install_method"]
    found_path = runner.which(item["command"])
    base_entry: dict[str, Any] = {
        "entry_id": f"tools.{item['id']}",
        "recipe": "tool_installs",
        "label": item["label"],
        "command": item["command"],
        "install_method": method,
        "requires_sudo": item.get("requires_sudo", False),
    }
    if found_path:
        base_entry.update(
            {
                "state": "installed",
                "current_path": found_path,
                "current_version": _detect_version(item["command"], found_path, runner),
                "action": "upgrade",
            }
        )
    else:
        base_entry.update({"state": "missing", "action": "install"})
    ops = _tool_operations(item, cache_dir, mode="upgrade" if found_path else "install")
    return base_entry, ops


def _tool_operations(item: Mapping[str, Any], cache_dir: Path, *, mode: str) -> list[dict[str, Any]]:
    method = item["install_method"]
    iargs = dict(item.get("install_args", {}))
    entry_id = f"tools.{item['id']}"
    if method == "apt":
        return [
            _apt_op(
                entry_id=entry_id,
                op_type=_APT_OP_TYPE[mode],
                packages=list(iargs.get("packages", [])),
                requires_sudo=item.get("requires_sudo", True),
                cache_dir=cache_dir,
                reason=f"{mode} {item['label']} via {_APT_REASON_SUFFIX[mode]}",
            )
        ]
    if method == "apt_keyring":
        return [_apt_keyring_op(entry_id, item, iargs, cache_dir, mode=mode)]
    if method == "curl_installer":
        return [_curl_op(entry_id, item, iargs, cache_dir, mode=mode)]
    if method == "npm":
        return [_npm_op(entry_id, item, iargs, cache_dir, mode=mode)]
    if method == "uv_tool":
        return [_uv_tool_op(entry_id, item, iargs, cache_dir, mode=mode)]
    return []


# ---------------------------------------------------------------------------
# Operation factories
# ---------------------------------------------------------------------------


def _apt_op(
    *,
    entry_id: str,
    op_type: str,
    packages: list[str],
    requires_sudo: bool,
    cache_dir: Path,
    reason: str,
) -> dict[str, Any]:
    return {
        "entry_id": entry_id,
        "recipe": "tool_installs",
        "type": op_type,
        "packages": packages,
        "requires_sudo": requires_sudo,
        "requires_network": True,
        "requires_approval": True,
        "cache_dir": str(cache_dir),
        "reason": reason,
    }


def _apt_keyring_op(
    entry_id: str,
    item: Mapping[str, Any],
    args: Mapping[str, Any],
    cache_dir: Path,
    *,
    mode: str,
) -> dict[str, Any]:
    return {
        "entry_id": entry_id,
        "recipe": "tool_installs",
        "type": "tool_install_apt_keyring",
        "mode": mode,
        "packages": list(args.get("packages") or ()),
        "keyring_url": args["keyring_url"],
        "keyring_path": args["keyring_path"],
        "source_line": args["source_line"],
        "source_path": args["source_path"],
        "requires_sudo": True,
        "requires_network": True,
        "requires_approval": True,
        "cache_dir": str(cache_dir),
        "reason": f"{mode} {item['label']} via GitHub keyring repo",
    }


def _curl_op(
    entry_id: str,
    item: Mapping[str, Any],
    args: Mapping[str, Any],
    cache_dir: Path,
    *,
    mode: str,
) -> dict[str, Any]:
    return {
        "entry_id": entry_id,
        "recipe": "tool_installs",
        "type": "tool_install_curl",
        "mode": mode,
        "url": args["url"],
        "script_name": args.get("script_name", "installer.sh"),
        "interpreter": args.get("interpreter", "bash"),
        "requires_sudo": item.get("requires_sudo", False),
        "requires_network": True,
        "requires_approval": True,
        "cache_dir": str(cache_dir),
        "reason": f"{mode} {item['label']} via {args['url']}",
    }


def _npm_op(
    entry_id: str,
    item: Mapping[str, Any],
    args: Mapping[str, Any],
    cache_dir: Path,
    *,
    mode: str,
) -> dict[str, Any]:
    op_type = "tool_install_npm" if mode == "install" else "tool_install_npm_upgrade"
    return {
        "entry_id": entry_id,
        "recipe": "tool_installs",
        "type": op_type,
        "mode": mode,
        "package": args["package"],
        "requires_sudo": item.get("requires_sudo", True),
        "requires_network": True,
        "requires_approval": True,
        "cache_dir": str(cache_dir),
        "reason": f"{mode} {item['label']} via npm",
    }


def _uv_tool_op(
    entry_id: str,
    item: Mapping[str, Any],
    args: Mapping[str, Any],
    cache_dir: Path,
    *,
    mode: str,
) -> dict[str, Any]:
    op_type = "tool_install_uv_tool"
    op: dict[str, Any] = {
        "entry_id": entry_id,
        "recipe": "tool_installs",
        "type": op_type,
        "mode": mode,
        "package": args["package"],
        "requires_sudo": item.get("requires_sudo", False),
        "requires_network": True,
        "requires_approval": True,
        "cache_dir": str(cache_dir),
        "reason": f"{mode} {item['label']} via uv tool",
    }
    if "from_url" in args:
        op["from_url"] = args["from_url"]
    return op


# ---------------------------------------------------------------------------
# Probes
# ---------------------------------------------------------------------------


def _dpkg_installed(runner: CommandRunner, package: str) -> bool:
    dpkg = runner.which("dpkg-query")
    if not dpkg:
        return False
    try:
        result = runner.run(
            [dpkg, "-W", "-f=${Status}", package],
            capture_output=True,
            check=False,
        )
    except (OSError, RuntimeError):
        return False
    return result.returncode == 0 and "install ok installed" in (result.stdout or "")


def _detect_version(command: str, found_path: str, runner: CommandRunner) -> str:
    try:
        result = runner.run([found_path, "--version"], capture_output=True, check=False)
    except (OSError, RuntimeError):
        return ""
    output = (result.stdout or "").strip().splitlines()
    return output[0] if output else ""


# ---------------------------------------------------------------------------
# Executors
# ---------------------------------------------------------------------------


def _sudo_prefix() -> list[str]:
    if hasattr(os, "geteuid") and os.geteuid() == 0:
        return []
    return ["sudo"]


def _execute_apt(op: dict[str, Any], runner: CommandRunner, *, mode: str) -> int:
    packages = [str(pkg) for pkg in op.get("packages", []) if pkg]
    if not packages:
        return 0
    apt_get = runner.which("apt-get")
    if not apt_get:
        op["result"] = "apt-get not found; install packages manually"
        return 0
    _apt_update_then_install(runner, _sudo_prefix(), apt_get, packages, mode=mode)
    return 1


def _execute_apt_keyring(op: dict[str, Any], runner: CommandRunner, cache_dir: Path) -> int:
    packages = [str(pkg) for pkg in op.get("packages", []) if pkg]
    if not packages:
        return 0
    apt_get = runner.which("apt-get")
    if not apt_get:
        op["result"] = "apt-get not found; install manually"
        return 0
    cache_dir.mkdir(parents=True, exist_ok=True)
    prefix = _sudo_prefix()
    keyring_path = Path(op["keyring_path"])
    source_path = Path(op["source_path"])

    if not keyring_path.exists():
        cached_keyring = cache_dir / keyring_path.name
        runner.download(op["keyring_url"], cached_keyring)
        runner.run([*prefix, "install", "-D", "-m", "0644", str(cached_keyring), str(keyring_path)])

    rendered_source = op["source_line"].replace("{ARCH}", _detect_dpkg_arch(runner))
    cached_source = cache_dir / source_path.name
    cached_source.write_text(rendered_source + "\n")
    runner.run([*prefix, "install", "-D", "-m", "0644", str(cached_source), str(source_path)])

    _apt_update_then_install(runner, prefix, apt_get, packages, mode=op.get("mode", "install"))
    return 1


def _execute_curl(op: dict[str, Any], runner: CommandRunner, cache_dir: Path) -> int:
    interpreter_name = op.get("interpreter", "bash")
    interpreter = runner.which(interpreter_name) or f"/bin/{interpreter_name}"
    cache_dir.mkdir(parents=True, exist_ok=True)
    script = cache_dir / op["script_name"]
    runner.download(op["url"], script)
    if not script.exists():
        op["result"] = f"failed to download installer from {op['url']}"
        return 0
    script.chmod(0o755)
    prefix = _sudo_prefix() if op.get("requires_sudo") else []
    runner.run([*prefix, interpreter, str(script)])
    return 1


def _apt_update_then_install(
    runner: CommandRunner,
    prefix: list[str],
    apt_get: str,
    packages: list[str],
    *,
    mode: str,
) -> None:
    runner.run([*prefix, apt_get, "update"])
    if mode == "upgrade":
        runner.run([*prefix, apt_get, "install", "--only-upgrade", "-y", *packages])
    else:
        runner.run([*prefix, apt_get, "install", "-y", *packages])


def _execute_npm(op: dict[str, Any], runner: CommandRunner, *, mode: str) -> int:
    package = op.get("package")
    if not package:
        return 0
    npm = runner.which("npm")
    if not npm:
        op["result"] = "npm not found; install Node first or re-run option 1 after dev-base completes"
        return 0
    prefix = _sudo_prefix() if op.get("requires_sudo", True) else []
    if mode == "upgrade":
        runner.run([*prefix, npm, "update", "-g", package])
    else:
        runner.run([*prefix, npm, "install", "-g", package])
    return 1


def _execute_uv_tool(op: dict[str, Any], runner: CommandRunner) -> int:
    package = op.get("package")
    if not package:
        return 0
    uv = runner.which("uv")
    if not uv:
        op["result"] = "uv not found; install uv first"
        return 0
    prefix = _sudo_prefix() if op.get("requires_sudo", False) else []
    mode = op.get("mode", "install")
    if mode == "upgrade":
        cmd = [*prefix, uv, "tool", "upgrade", package]
    else:
        cmd = [*prefix, uv, "tool", "install", package]
        from_url = op.get("from_url")
        if from_url:
            cmd += ["--from", from_url]
    runner.run(cmd)
    return 1


def _detect_dpkg_arch(runner: CommandRunner) -> str:
    dpkg = runner.which("dpkg")
    if not dpkg:
        return "amd64"
    try:
        result = runner.run([dpkg, "--print-architecture"], capture_output=True, check=False)
    except (OSError, RuntimeError):
        return "amd64"
    return (result.stdout or "amd64").strip() or "amd64"


# ---------------------------------------------------------------------------
# Verification + post-install actions
# ---------------------------------------------------------------------------


def verify_installed_tools(
    home: Path | str,
    *,
    runner: CommandRunner | None = None,
    env: Mapping[str, str] | None = None,
) -> list[dict[str, Any]]:
    """Re-probe each bootstrap tool. Returns one result per tool with
    keys: entry_id, label, command, path, verified (bool), version."""
    effective_env = dict(os.environ if env is None else env)
    effective_runner = runner or CommandRunner(env=effective_env, path=effective_env.get("PATH", ""))
    results: list[dict[str, Any]] = []
    for item in TOOL_BASELINE:
        if not item.get("bootstrap"):
            continue
        path = effective_runner.which(item["command"])
        version = _detect_version(item["command"], path, effective_runner) if path else ""
        results.append({
            "entry_id": f"tools.{item['id']}",
            "label": item["label"],
            "command": item["command"],
            "path": path,
            "verified": bool(path),
            "version": version,
        })
    return results


def run_post_install_actions(
    home: Path | str,
    *,
    yes: bool = False,
    runner: CommandRunner | None = None,
    env: Mapping[str, str] | None = None,
    repo_path: Path | str | None = None,
    backup_dir: Path | str | None = None,
) -> list[dict[str, Any]]:
    """For each verified tool, walk its `post_install` list:
      - kind='auto' AND yes=True → execute via runner.run; record outcome.
      - kind='auto' AND yes=False → downgrade to guidance, record command.
      - kind='guidance' → record command for printing.
    Templates with `{which:<name>}` or `{user}` placeholders are substituted
    before execution; an unresolved placeholder downgrades the action to
    guidance. `requires_protected_apply` copies the listed protected files
    from the repo before exec (only when yes=True and repo_path is set);
    existing targets are backed up to `backup_dir` first."""
    effective_env = dict(os.environ if env is None else env)
    effective_runner = runner or CommandRunner(env=effective_env, path=effective_env.get("PATH", ""))
    repo = Path(repo_path).resolve() if repo_path else None
    home_path = Path(home).expanduser().resolve()
    backup = Path(backup_dir).expanduser().resolve() if backup_dir else None
    return _walk_post_install(
        effective_runner, effective_env, yes=yes,
        repo=repo, home=home_path, backup_dir=backup,
    )


def _walk_post_install(
    runner: CommandRunner,
    env: Mapping[str, str],
    *,
    yes: bool,
    repo: Path | None,
    home: Path,
    backup_dir: Path | None,
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for item in TOOL_BASELINE:
        if not item.get("bootstrap") or not runner.which(item["command"]):
            continue
        for action in item.get("post_install", ()):
            results.append(_run_one_post_install(
                item, action, runner, env, yes=yes,
                repo=repo, home=home, backup_dir=backup_dir,
            ))
    return results


def _run_one_post_install(
    item: Mapping[str, Any],
    action: Mapping[str, Any],
    runner: CommandRunner,
    env: Mapping[str, str],
    *,
    yes: bool,
    repo: Path | None,
    home: Path,
    backup_dir: Path | None,
) -> dict[str, Any]:
    label = action.get("label", "")
    kind = action.get("kind", "guidance")
    template = list(action.get("command_template", ()))
    rendered, unresolved = _render_post_install_template(template, runner, env)
    base = {
        "tool": item["id"], "label": label, "kind": kind,
        "command": rendered, "raw_template": template,
    }
    if unresolved:
        return {**base, "kind": "guidance", "status": "skipped",
                "reason": f"unresolved placeholder: {unresolved}"}
    if kind != "auto" or not yes:
        return {**base, "status": "guidance"}
    if not rendered:
        return {**base, "status": "skipped", "reason": "empty command after substitution"}
    return _execute_post_install_action(action, rendered, runner, base, repo=repo, home=home, backup_dir=backup_dir)


def _execute_post_install_action(
    action: Mapping[str, Any],
    rendered: list[str],
    runner: CommandRunner,
    base: dict[str, Any],
    *,
    repo: Path | None,
    home: Path,
    backup_dir: Path | None,
) -> dict[str, Any]:
    protected = list(action.get("requires_protected_apply", ()))
    overrides: list[dict[str, str]] = []
    backups: list[dict[str, str]] = []
    try:
        if protected:
            overrides, backups = _apply_protected_files(protected, repo, home, backup_dir)
        runner.run(rendered)
    except (OSError, RuntimeError, BackupError) as exc:
        return {**base, "status": "failed", "result": str(exc),
                "protected_overrides": overrides, "backups": backups}
    return {**base, "status": "ran", "protected_overrides": overrides, "backups": backups}


def _render_post_install_template(
    template: list[str],
    runner: CommandRunner,
    env: Mapping[str, str],
) -> tuple[list[str], str | None]:
    rendered: list[str] = []
    for token in template:
        substituted, missing = _substitute_token(token, runner, env)
        if missing:
            return rendered, missing
        rendered.append(substituted)
    return rendered, None


def _substitute_token(
    token: str,
    runner: CommandRunner,
    env: Mapping[str, str],
) -> tuple[str, str | None]:
    if not (token.startswith("{") and token.endswith("}")):
        return token, None
    expr = token[1:-1]
    if expr == "user":
        user = env.get("USER") or env.get("LOGNAME")
        return (user, None) if user else (token, "user")
    if expr.startswith("which:"):
        name = expr[len("which:"):]
        path = runner.which(name)
        return (path, None) if path else (token, expr)
    return token, expr


def _apply_protected_files(
    protected: list[str],
    repo: Path | None,
    home: Path,
    backup_dir: Path | None,
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    """Look up each `protected` source path in the manifest, back up the
    existing target (when a `backup_dir` is set), and copy the repo file
    into place. Returns (overrides_applied, backups_created)."""
    if not repo:
        return [], []
    try:
        manifest = load_manifest(repo)
    except ManifestError:
        return [], []
    by_source = {entry.source: entry for entry in manifest.entries}
    overrides: list[dict[str, str]] = []
    backups: list[dict[str, str]] = []
    for rel in protected:
        entry = by_source.get(rel)
        if entry is None:
            continue
        result = _copy_protected_file(entry, repo, home, backup_dir)
        if result is None:
            continue
        override, backup = result
        overrides.append(override)
        if backup is not None:
            backups.append(backup)
    return overrides, backups


def _copy_protected_file(
    entry: Any,  # ManifestEntry
    repo: Path,
    home: Path,
    backup_dir: Path | None,
) -> tuple[dict[str, str], dict[str, str] | None] | None:
    source = repo / entry.source
    target = home / entry.target
    if not source.exists():
        return None
    backup: dict[str, str] | None = None
    if (target.exists() or target.is_symlink()) and backup_dir is not None:
        backup = create_backup(target, backup_dir, entry_id=f"post_install:{entry.id}")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(source.read_text())
    override = {"source": str(source), "target": str(target), "entry_id": entry.id}
    return override, backup
