from __future__ import annotations

import json
from pathlib import Path
import subprocess  # nosec B404
import urllib.error
import zipfile

from dotfiles_tools.bootstrap import build_bootstrap_plan
from dotfiles_tools.font_assets import pixel_avf_prompt_text
from dotfiles_tools.font_catalog import FONT_MARKER_NAME
from dotfiles_tools.fonts import (
    APT_FONT_CATALOG,
    EXPECTED_TTF,
    FONT_FACE,
    FONT_INSTALL_REL,
    FontError,
    NERD_FONT_CATALOG,
    build_font_plan,
    execute_font_operation,
    select_nerd_font_asset,
)
from tests.helpers import DotfilesTestCase, REPO_ROOT


def release_inventory(tag: str = "v3.4.0") -> dict:
    return {
        "tag_name": tag,
        "assets": [
            {
                "name": item.asset_name,
                "browser_download_url": f"https://example/{item.asset_name}",
                "size": 12,
            }
            for item in NERD_FONT_CATALOG
        ],
    }


class FakeRunner:
    def __init__(
        self,
        *,
        which: dict[str, str] | None = None,
        release: dict | None = None,
        fail_fetch: bool = False,
        apt_installed: dict[str, str | None] | None = None,
        apt_candidate: dict[str, str | None] | None = None,
    ) -> None:
        self.which_map = which or {}
        self.release = release or release_inventory("v0.test")
        self.fail_fetch = fail_fetch
        self.apt_installed = apt_installed or {}
        self.apt_candidate = apt_candidate or {}
        self.commands: list[list[str]] = []
        self.fetches: list[str] = []
        self.downloads: list[tuple[str, Path]] = []

    def which(self, command: str) -> str | None:
        return self.which_map.get(command)

    def fetch_json(self, url: str) -> dict:
        self.fetches.append(url)
        if self.fail_fetch:
            raise OSError("offline")
        return self.release

    def download(self, url: str, target: Path) -> None:
        self.downloads.append((url, target))
        asset_name = Path(target).name
        item = next(item for item in NERD_FONT_CATALOG if item.asset_name == asset_name)
        write_font_zip(target, item.expected_regular)

    def run(self, args: list[str], *, capture_output: bool = False, check: bool = True) -> subprocess.CompletedProcess[str]:
        self.commands.append(args)
        command = Path(args[0]).name
        if command == "fc-match":
            face = args[1]
            return subprocess.CompletedProcess(args, 0, stdout=f"{face.replace(' ', '')}-Regular.ttf: \"{face}\"\n", stderr="")
        if command == "wslpath":
            return subprocess.CompletedProcess(args, 0, stdout="C:\\Users\\kkk\\Fonts\n", stderr="")
        if command == "dpkg-query":
            package = args[-1]
            version = self.apt_installed.get(package)
            return subprocess.CompletedProcess(args, 0 if version else 1, stdout=version or "", stderr="")
        if command == "apt-cache":
            package = args[-1]
            candidate = self.apt_candidate.get(package)
            stdout = f"{package}:\n  Installed: (none)\n  Candidate: {candidate or '(none)'}\n"
            return subprocess.CompletedProcess(args, 0, stdout=stdout, stderr="")
        return subprocess.CompletedProcess(args, 0, stdout="", stderr="")


def write_font_zip(path: Path, expected_regular: str = EXPECTED_TTF) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w") as bundle:
        bundle.writestr(expected_regular, b"fake-font")
        bundle.writestr(expected_regular.replace("Regular", "Bold"), b"fake-bold")
        bundle.writestr(expected_regular.replace("Mono", "Propo"), b"fake-propo")


def font_values(fonts: list[dict], source_type: str, key: str) -> set:
    return {item[key] for item in fonts if item["source_type"] == source_type}


def operation_values(operations: list[dict], op_type: str, key: str) -> set:
    return {op[key] for op in operations if op["type"] == op_type}


def operation_packages(operations: list[dict]) -> set:
    return {op["packages"][0] for op in operations if op["type"] == "font_install_packages"}


def operation_terminal_faces(operations: list[dict], op_type: str) -> list:
    return [op.get("terminal_face") for op in operations if op["type"] == op_type]


def font_by_entry(fonts: list[dict], entry_id: str) -> dict:
    return next(item for item in fonts if item["entry_id"] == entry_id)


class FontCatalogTests(DotfilesTestCase):
    def apt_runner(self, installed: dict[str, str | None] | None = None, candidate: dict[str, str | None] | None = None) -> FakeRunner:
        return FakeRunner(
            which={
                "dpkg-query": "/usr/bin/dpkg-query",
                "apt-cache": "/usr/bin/apt-cache",
                "apt-get": "/usr/bin/apt-get",
                "fc-cache": "/usr/bin/fc-cache",
                "fc-match": "/usr/bin/fc-match",
            },
            release=release_inventory(),
            apt_installed=installed or {},
            apt_candidate=candidate or {},
        )

    def test_selects_each_nerd_font_asset_from_release_json(self) -> None:
        release = release_inventory()

        assets = {item.asset_name: select_nerd_font_asset(release, item.asset_name) for item in NERD_FONT_CATALOG}

        self.assertEqual(assets["JetBrainsMono.zip"]["tag_name"], "v3.4.0")
        self.assertEqual(assets["Meslo.zip"]["browser_download_url"], "https://example/Meslo.zip")

    def test_asset_selection_fails_when_release_has_no_font_zip(self) -> None:
        with self.assertRaises(FontError):
            select_nerd_font_asset({"assets": [{"name": "Other.zip", "browser_download_url": "https://example/Other.zip"}]})

    def test_standard_linux_plan_represents_all_catalog_items_when_missing(self) -> None:
        home = self.make_home()
        packages = {item["package"] for item in APT_FONT_CATALOG}
        runner = self.apt_runner(candidate={package: "1.0" for package in packages})

        plan = build_font_plan(home, env={"DOTFILES_PLATFORM": "linux"}, path="", runner=runner)
        fonts = plan["fonts"]

        self.assertEqual(font_values(fonts, "nerd_font_release", "asset_name"), {item.asset_name for item in NERD_FONT_CATALOG})
        self.assertEqual(font_values(fonts, "apt_package", "package"), packages)
        self.assertEqual(font_values(fonts, "nerd_font_release", "latest_version"), {"v3.4.0"})
        self.assertEqual(font_values(fonts, "apt_package", "candidate_version"), {"1.0"})
        self.assertEqual(operation_values(plan["operations"], "font_download", "asset_name"), {item.asset_name for item in NERD_FONT_CATALOG})
        self.assertEqual(operation_packages(plan["operations"]), packages)

    def test_linux_font_install_reuses_cached_archives_extracts_installs_and_verifies_mono_faces(self) -> None:
        home = self.make_home()
        cache_root = home / ".cache/000-dotfiles/fonts"
        for item in NERD_FONT_CATALOG:
            archive = cache_root / item.asset_name
            write_font_zip(archive, item.expected_regular)
        cache_root.mkdir(parents=True, exist_ok=True)
        (cache_root / "nerd-fonts.latest.json").write_text(json.dumps(release_inventory()))
        runner = FakeRunner(which={"fc-cache": "/usr/bin/fc-cache", "fc-match": "/usr/bin/fc-match"}, fail_fetch=True)
        plan = build_font_plan(home, env={"DOTFILES_PLATFORM": "linux"}, path="", runner=runner)

        for op in plan["operations"]:
            execute_font_operation(op, runner=runner, backup_dir=home / "backups", backups=[])

        self.assertTrue((home / FONT_INSTALL_REL / EXPECTED_TTF).exists())
        for item in NERD_FONT_CATALOG:
            self.assertTrue((home / ".local/share/fonts" / item.install_dir_name / item.expected_regular).exists())
        verify_faces = [args[1] for args in runner.commands if Path(args[0]).name == "fc-match"]
        self.assertIn(FONT_FACE, verify_faces)
        self.assertIn("MesloLGS Nerd Font Mono", verify_faces)
        self.assertTrue(all("Propo" not in face for face in verify_faces))
        self.assertEqual(runner.downloads, [])

    def test_apt_package_states_cover_missing_current_and_needs_update(self) -> None:
        home = self.make_home()
        runner = self.apt_runner(
            installed={
                "fonts-noto-color-emoji": "1.0",
                "fonts-symbola": None,
                "fonts-freefont-ttf": "1.0",
                "fonts-dejavu-core": "2.0",
            },
            candidate={
                "fonts-noto-color-emoji": "1.0",
                "fonts-symbola": "2.0",
                "fonts-freefont-ttf": "1.1",
                "fonts-dejavu-core": "2.0",
            },
        )

        plan = build_font_plan(home, env={"DOTFILES_PLATFORM": "linux"}, path="", runner=runner)
        states = {item["package"]: item["state"] for item in plan["fonts"] if item["source_type"] == "apt_package"}

        self.assertEqual(states["fonts-noto-color-emoji"], "installed")
        self.assertEqual(states["fonts-symbola"], "missing")
        self.assertEqual(states["fonts-freefont-ttf"], "needs_update")
        self.assertEqual(states["fonts-dejavu-core"], "installed")
        self.assertEqual(
            operation_packages(plan["operations"]),
            {"fonts-symbola", "fonts-freefont-ttf"},
        )

    def test_wsl_plans_all_linux_fonts_and_windows_terminal_mono_update_when_detected(self) -> None:
        home = self.make_home()
        install_dir = home / FONT_INSTALL_REL
        install_dir.mkdir(parents=True)
        (install_dir / EXPECTED_TTF).write_text("font")
        settings = home / "windows-terminal-settings.json"
        settings.write_text('{"profiles": {"defaults": {}}}')
        env = {"DOTFILES_PLATFORM": "wsl", "DOTFILES_WINDOWS_TERMINAL_SETTINGS": str(settings)}
        runner = FakeRunner(
            which={
                "powershell.exe": "/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe",
                "wslpath": "/usr/bin/wslpath",
            },
            release=release_inventory(),
        )

        plan = build_font_plan(home, env=env, path="", runner=runner)
        op_types = [op["type"] for op in plan["operations"]]

        self.assertEqual(font_values(plan["fonts"], "nerd_font_release", "asset_name"), {item.asset_name for item in NERD_FONT_CATALOG})
        self.assertIn("font_install_windows", op_types)
        terminal_update = next(op for op in plan["operations"] if op["type"] == "font_update_windows_terminal")
        self.assertEqual(terminal_update["source"], FONT_FACE)
        self.assertNotIn("Propo", terminal_update["source"])

        manual_plan = build_font_plan(home, env={"DOTFILES_PLATFORM": "wsl"}, path="", runner=FakeRunner(release=release_inventory()))
        manual_types = [op["type"] for op in manual_plan["operations"]]
        self.assertIn("font_manual", manual_types)
        self.assertNotIn("font_update_windows_terminal", manual_types)

    def test_pi_plans_full_nerd_inventory_symbol_fallbacks_and_meslo_mono_verify(self) -> None:
        home = self.make_home()
        runner = self.apt_runner(candidate={item["package"]: "1.0" for item in APT_FONT_CATALOG})

        plan = build_font_plan(home, env={"DOTFILES_PLATFORM": "pi"}, path="", runner=runner)

        self.assertEqual(font_values(plan["fonts"], "nerd_font_release", "asset_name"), {item.asset_name for item in NERD_FONT_CATALOG})
        self.assertEqual(
            font_values(plan["fonts"], "apt_package", "package"),
            {"fonts-noto-color-emoji", "fonts-symbola", "fonts-freefont-ttf"},
        )
        self.assertIn(
            "MesloLGS Nerd Font Mono",
            operation_terminal_faces(plan["operations"], "font_verify_linux"),
        )

    def test_pixel_terminal_embeds_jetbrains_mono_subset_and_only_noto_emoji_package(self) -> None:
        home = self.make_home()
        runner = self.apt_runner(candidate={item["package"]: "1.0" for item in APT_FONT_CATALOG})

        plan = build_font_plan(home, env={"DOTFILES_PLATFORM": "pixel-terminal"}, path="", runner=runner)
        op_types = [op["type"] for op in plan["operations"]]

        self.assertEqual(font_values(plan["fonts"], "nerd_font_release", "asset_name"), {"JetBrainsMono.zip"})
        self.assertEqual(font_values(plan["fonts"], "apt_package", "package"), {"fonts-noto-color-emoji"})
        self.assertLess(op_types.index("font_ttyd_write_html"), op_types.index("font_ttyd_write_service"))
        self.assertLess(op_types.index("font_ttyd_write_service"), op_types.index("font_systemd_daemon_reload"))
        self.assertLess(op_types.index("font_systemd_daemon_reload"), op_types.index("font_systemd_restart"))
        self.assertEqual(font_by_entry(plan["fonts"], "fonts.jetbrains-mono-nerd")["embedded_alias"], "JBMono NF")

    def test_pixel_avf_skips_nerd_font_install_and_plans_prompt_fallback(self) -> None:
        home = self.make_home()

        plan = build_font_plan(home, env={"DOTFILES_PLATFORM": "pixel-avf"}, path="", runner=FakeRunner())
        states = {entry["entry_id"]: entry["state"] for entry in plan["entries"]}
        op_types = [op["type"] for op in plan["operations"]]

        self.assertEqual(states["fonts.jetbrains-mono-nerd"], "unsupported")
        self.assertNotIn("font_download", op_types)
        self.assertIn("font_pixel_avf_prompt", op_types)

    def test_verify_operation_rejects_propo_terminal_faces(self) -> None:
        with self.assertRaises(FontError):
            execute_font_operation(
                {"type": "font_verify_linux", "target": "", "terminal_face": "Hack Nerd Font Propo", "family": "Hack"},
                runner=FakeRunner(which={"fc-match": "/usr/bin/fc-match"}),
            )

    def test_bootstrap_plan_json_surface_includes_font_catalog_records(self) -> None:
        home = self.make_home()
        packages = {item["package"] for item in APT_FONT_CATALOG}
        runner = self.apt_runner(candidate={package: "1.0" for package in packages})
        report = build_bootstrap_plan(REPO_ROOT, home, env={"DOTFILES_PLATFORM": "linux"}, path="", runner=runner)
        data = report.to_dict()

        self.assertEqual(data["command"], "bootstrap-plan")
        self.assertIn("fonts", data)
        self.assertEqual(len(data["fonts"]), len(NERD_FONT_CATALOG) + len(APT_FONT_CATALOG))
        first = data["fonts"][0]
        for key in ("family", "source_type", "state", "installed_version", "target", "terminal_face"):
            self.assertIn(key, first)
        self.assertIn("font_download", {op["type"] for op in data["operations"]})


class FontReturnSemanticsTests(DotfilesTestCase):
    def test_install_linux_returns_zero_when_marker_and_files_already_match(self) -> None:
        home = self.make_home()
        source = home / "src"
        target = home / "target"
        source.mkdir()
        target.mkdir()
        (source / EXPECTED_TTF).write_bytes(b"font-bytes")
        version = {"tag_name": "v9.9.9"}
        version_source = home / "version.json"
        version_source.write_text(json.dumps(version))
        op = {"type": "font_install_linux", "source": str(source), "target": str(target), "version_source": str(version_source)}

        first = execute_font_operation(op, runner=FakeRunner())
        second = execute_font_operation(op, runner=FakeRunner())

        self.assertEqual(first, 1)
        self.assertEqual(second, 0)
        self.assertEqual((target / FONT_MARKER_NAME).read_text().strip(), json.dumps(version, indent=2, sort_keys=True))

    def test_install_linux_returns_one_when_marker_differs(self) -> None:
        home = self.make_home()
        source = home / "src"
        target = home / "target"
        source.mkdir()
        target.mkdir()
        (source / EXPECTED_TTF).write_bytes(b"font-bytes")
        (target / EXPECTED_TTF).write_bytes(b"font-bytes")
        (target / FONT_MARKER_NAME).write_text(json.dumps({"tag_name": "v0.0.1"}, indent=2, sort_keys=True) + "\n")
        version_source = home / "version.json"
        version_source.write_text(json.dumps({"tag_name": "v9.9.9"}))
        op = {"type": "font_install_linux", "source": str(source), "target": str(target), "version_source": str(version_source)}

        result = execute_font_operation(op, runner=FakeRunner())

        self.assertEqual(result, 1)

    def test_pixel_avf_prompt_returns_zero_when_already_current(self) -> None:
        home = self.make_home()
        target = home / "fish-prompt.fish"
        target.write_text(pixel_avf_prompt_text())
        op = {"type": "font_pixel_avf_prompt", "target": str(target)}

        result = execute_font_operation(op, runner=FakeRunner())

        self.assertEqual(result, 0)

    def test_pixel_avf_prompt_returns_one_on_first_write(self) -> None:
        home = self.make_home()
        target = home / "fish-prompt.fish"
        op = {"type": "font_pixel_avf_prompt", "target": str(target)}

        result = execute_font_operation(op, runner=FakeRunner())

        self.assertEqual(result, 1)
        self.assertEqual(target.read_text(), pixel_avf_prompt_text())

    def test_systemd_returns_one_to_record_state_change(self) -> None:
        runner = FakeRunner(which={"systemctl": "/usr/bin/systemctl"})
        op = {"type": "font_systemd_daemon_reload", "target": "systemd"}

        result = execute_font_operation(op, runner=runner)

        self.assertEqual(result, 1)
        self.assertTrue(any("systemctl" in arg for arg in runner.commands[0]))

    def test_ttyd_html_and_service_return_one(self) -> None:
        home = self.make_home()
        source = home / "src"
        source.mkdir()
        (source / EXPECTED_TTF).write_bytes(b"font-bytes")
        cache = home / "cache"
        target_html = home / "fake-ttyd-index.html"
        target_service = home / "fake-ttyd.service"

        html_result = execute_font_operation(
            {
                "type": "font_ttyd_write_html",
                "source": str(source),
                "target": str(target_html),
                "cache_dir": str(cache),
                "entry_id": "test",
            },
            runner=FakeRunner(),
            backups=[],
        )
        service_result = execute_font_operation(
            {
                "type": "font_ttyd_write_service",
                "target": str(target_service),
                "cache_dir": str(cache),
                "entry_id": "test",
            },
            runner=FakeRunner(),
            backups=[],
        )

        self.assertEqual(html_result, 1)
        self.assertEqual(service_result, 1)


class FontReleaseMetadataTests(DotfilesTestCase):
    def test_release_lookup_failure_with_cache_attaches_error_kind(self) -> None:
        home = self.make_home()
        cache_root = home / ".cache/000-dotfiles/fonts"
        cache_root.mkdir(parents=True)
        (cache_root / "nerd-fonts.latest.json").write_text(json.dumps(release_inventory("v1.2.3")))
        runner = FakeRunner(fail_fetch=True)

        plan = build_font_plan(home, env={"DOTFILES_PLATFORM": "linux"}, path="", runner=runner)
        nerd_summary = next(item for item in plan["fonts"] if item["source_type"] == "nerd_font_release")

        self.assertEqual(nerd_summary["latest_version"], "v1.2.3")

    def test_release_lookup_failure_without_cache_raises_font_error(self) -> None:
        home = self.make_home()
        runner = FakeRunner(fail_fetch=True)

        with self.assertRaises(FontError):
            build_font_plan(home, env={"DOTFILES_PLATFORM": "linux"}, path="", runner=runner)

    def test_release_lookup_classifies_url_error_as_network(self) -> None:
        from dotfiles_tools.fonts import _classify_release_lookup_error

        self.assertEqual(_classify_release_lookup_error(urllib.error.URLError("boom")), "network")
        self.assertEqual(_classify_release_lookup_error(urllib.error.HTTPError("u", 500, "msg", {}, None)), "http")
        self.assertEqual(_classify_release_lookup_error(TimeoutError("slow")), "timeout")
        self.assertEqual(_classify_release_lookup_error(json.JSONDecodeError("oops", "doc", 0)), "decode")
        self.assertEqual(_classify_release_lookup_error(FileNotFoundError("missing")), "offline")

    def test_release_metadata_cached_lookup_records_error_kind(self) -> None:
        from dotfiles_tools.fonts import _release_metadata
        from dotfiles_tools.font_runner import CommandRunner as RealRunner

        home = self.make_home()
        cache_root = home / ".cache/000-dotfiles/fonts"
        cache_root.mkdir(parents=True)
        (cache_root / "nerd-fonts.latest.json").write_text(json.dumps({"tag_name": "v1.2.3", "assets": []}))

        class TimeoutRunner(RealRunner):
            def fetch_json(self, url: str) -> dict:
                raise TimeoutError("slow")

        runner = TimeoutRunner(env={}, path="")
        result = _release_metadata(home, {}, runner, fetch=True)

        self.assertEqual(result["tag_name"], "v1.2.3")
        self.assertEqual(result["lookup_error_kind"], "timeout")
        self.assertIn("slow", result["lookup_error"])
