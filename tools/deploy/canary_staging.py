"""Build and validate a complete Canary datapack before and after deployment."""

from __future__ import annotations

import argparse
import importlib.util
import shutil
import uuid
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Callable

from health_check import HealthChecker, HealthCheckResult
from path_policy import PathEscapesRootError, resolve_within_root

SmokeExecutor = Callable[[argparse.Namespace], None]


@dataclass(frozen=True)
class CanarySmokeSettings:
    repo_root: Path
    binary_path: Path
    map_name: str = "canary"
    map_download_url: str = ""
    map_cache_path: Path | None = None
    db_host: str = "127.0.0.1"
    db_port: int = 3306
    db_user: str = "root"
    db_password: str = "root"
    db_name: str = "canary_deployment_smoke"
    login_port: int = 7471
    game_port: int = 7472
    status_port: int = 7471
    startup_timeout_seconds: int = 420
    fail_on_warnings: bool = True
    skip_database_init: bool = False


def _collect_overlay_files(overlay_root: Path) -> list[Path]:
    files: list[Path] = []
    for entry in sorted(overlay_root.rglob("*")):
        if entry.is_symlink():
            raise PathEscapesRootError(f"deployment overlay must not contain symlinks: {entry}")
        if entry.is_file():
            resolve_within_root(entry, overlay_root)
            files.append(entry)
    return files


def assemble_staging_datapack(base_datapack: str | Path, overlay_dir: str | Path, destination: str | Path) -> Path:
    """Copy a trusted base datapack and apply a reviewed, symlink-free overlay.

    The destination is all-or-nothing from the caller's perspective: any
    copy/overlay failure removes the partially assembled tree before the
    exception is propagated.
    """
    base = Path(base_datapack).resolve(strict=True)
    overlay = Path(overlay_dir).resolve(strict=True)
    target = Path(destination)

    if not base.is_dir():
        raise ValueError(f"base datapack is not a directory: {base}")
    if not overlay.is_dir():
        raise ValueError(f"deployment overlay is not a directory: {overlay}")
    if target.exists() or target.is_symlink():
        raise FileExistsError(f"staging destination already exists: {target}")

    overlay_files = _collect_overlay_files(overlay)
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        shutil.copytree(base, target, symlinks=False)
        for source in overlay_files:
            relative = source.relative_to(overlay)
            destination_file = target / relative
            if destination_file.exists() and destination_file.is_dir():
                raise IsADirectoryError(f"overlay file would replace a directory: {relative}")
            destination_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination_file)
    except BaseException:
        shutil.rmtree(target, ignore_errors=True)
        raise

    return target.resolve(strict=True)


def _load_smoke_module(repo_root: Path) -> ModuleType:
    script = repo_root / ".github/scripts/smoke_test_canary.py"
    if not script.is_file():
        raise FileNotFoundError(f"Canary smoke script was not found: {script}")

    spec = importlib.util.spec_from_file_location("canary_runtime_smoke", script)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load Canary smoke script: {script}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.REPO_ROOT = repo_root
    return module


def _staging_smoke_executor(repo_root: Path) -> SmokeExecutor:
    """Load the standard smoke runner while allowing its temporary datapack alias.

    The generated config alone enables arbitrary datapack folders. Normal
    runtime configuration and the repository smoke workflow stay strict.
    """
    module = _load_smoke_module(repo_root)
    standard_write_smoke_config = module.write_smoke_config

    def write_staging_smoke_config(args: argparse.Namespace) -> None:
        standard_write_smoke_config(args)
        config_path = repo_root / "config.lua"
        config = config_path.read_text(encoding="utf-8")
        config = module.set_lua_value(config, "useAnyDatapackFolder", "true")
        config_path.write_text(config, encoding="utf-8", newline="\n")

    module.write_smoke_config = write_staging_smoke_config
    return module.run_smoke


def _safe_phase(phase: str) -> str:
    cleaned = "".join(character if character.isalnum() or character in "-_" else "-" for character in phase)
    return cleaned.strip("-") or "smoke"


def run_canary_smoke(
    datapack_dir: str | Path,
    settings: CanarySmokeSettings,
    *,
    phase: str,
    executor: SmokeExecutor | None = None,
) -> HealthCheckResult:
    """Run the repository smoke logic against an arbitrary datapack.

    Canary's Lua package path expects datapack directories to keep the
    ``data-`` prefix. A unique repository-root symlink supplies a compatible
    short name while the assembled release stays outside the source tree.
    The alias is always removed.
    """
    repo_root = Path(settings.repo_root).resolve(strict=True)
    datapack = Path(datapack_dir).resolve(strict=True)
    binary = Path(settings.binary_path)
    if not binary.is_absolute():
        binary = repo_root / binary
    binary = binary.resolve(strict=True)

    alias = repo_root / f"data-canary-deploy-{_safe_phase(phase)}-{uuid.uuid4().hex[:10]}"
    if alias.exists() or alias.is_symlink():
        raise FileExistsError(f"temporary datapack alias already exists: {alias}")

    alias.symlink_to(datapack, target_is_directory=True)
    try:
        smoke_executor = executor or _staging_smoke_executor(repo_root)

        args = argparse.Namespace(
            binary_path=str(binary),
            data_pack=alias.name,
            map_name=settings.map_name,
            map_download_url=settings.map_download_url,
            map_cache_path=str(settings.map_cache_path) if settings.map_cache_path else "",
            db_host=settings.db_host,
            db_port=settings.db_port,
            db_user=settings.db_user,
            db_password=settings.db_password,
            db_name=settings.db_name,
            login_port=settings.login_port,
            game_port=settings.game_port,
            status_port=settings.status_port,
            startup_timeout_seconds=settings.startup_timeout_seconds,
            fail_on_warnings=settings.fail_on_warnings,
            skip_database_init=settings.skip_database_init,
        )

        smoke_executor(args)
        return HealthCheckResult(healthy=True, detail=f"{phase} Canary runtime smoke passed")
    except Exception as exc:
        return HealthCheckResult(healthy=False, detail=f"{phase} Canary runtime smoke failed: {type(exc).__name__}: {exc}")
    finally:
        try:
            alias.unlink()
        except FileNotFoundError:
            pass


def make_canary_smoke_health_check(settings: CanarySmokeSettings, *, phase: str = "post-switch") -> HealthChecker:
    def check(release_dir: Path) -> HealthCheckResult:
        return run_canary_smoke(release_dir, settings, phase=phase)

    return check
