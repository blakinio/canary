#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

DEFAULT_DATAPACK = "data-otservbr-global"
DEFAULT_MAP = "otservbr"
SAFE_SEGMENT_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


class ServerSelectionError(ValueError):
    pass


@dataclass(frozen=True)
class ServerSelection:
    datapack: str
    map_name: str
    datapack_path: Path
    map_path: Path
    allow_map_download: bool


def _safe_segment(value: object, field: str) -> str:
    if not isinstance(value, str) or not SAFE_SEGMENT_RE.fullmatch(value):
        raise ServerSelectionError(
            f"scenario.server.{field} must be a safe repository-local path segment matching {SAFE_SEGMENT_RE.pattern}"
        )
    return value


def _inside(path: Path, parent: Path, field: str) -> None:
    if not path.is_relative_to(parent):
        raise ServerSelectionError(f"scenario.server.{field} resolves outside the repository-selected runtime root")


def resolve_server_selection(manifest_path: Path, root: Path) -> ServerSelection:
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ServerSelectionError(f"cannot read scenario manifest: {exc}") from exc

    scenario = manifest.get("scenario")
    if not isinstance(scenario, dict):
        raise ServerSelectionError("scenario manifest is missing scenario object")
    server = scenario.get("server")
    if not isinstance(server, dict):
        raise ServerSelectionError("scenario manifest is missing scenario.server object")

    datapack = _safe_segment(server.get("datapack"), "datapack")
    map_name = _safe_segment(server.get("map"), "map")

    repository_root = root.resolve()
    datapack_path = (repository_root / datapack).resolve(strict=False)
    _inside(datapack_path, repository_root, "datapack")
    if not datapack_path.is_dir():
        raise ServerSelectionError(f"selected datapack directory does not exist: {datapack_path}")

    world_path = (datapack_path / "world").resolve(strict=False)
    _inside(world_path, datapack_path, "datapack")
    map_path = (world_path / f"{map_name}.otbm").resolve(strict=False)
    _inside(map_path, world_path, "map")

    allow_map_download = datapack == DEFAULT_DATAPACK and map_name == DEFAULT_MAP
    if not allow_map_download and (not map_path.is_file() or map_path.stat().st_size <= 0):
        raise ServerSelectionError(f"selected non-default map is missing or empty: {map_path}")

    return ServerSelection(
        datapack=datapack,
        map_name=map_name,
        datapack_path=datapack_path,
        map_path=map_path,
        allow_map_download=allow_map_download,
    )


def github_environment(selection: ServerSelection) -> dict[str, str]:
    return {
        "AGENT_E2E_SERVER_DATAPACK": selection.datapack,
        "AGENT_E2E_SERVER_MAP": selection.map_name,
        "AGENT_E2E_SERVER_DATAPACK_PATH": str(selection.datapack_path),
        "AGENT_E2E_SERVER_MAP_PATH": str(selection.map_path),
        "AGENT_E2E_SERVER_ALLOW_MAP_DOWNLOAD": "true" if selection.allow_map_download else "false",
    }


def write_github_env(path: Path, values: dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        for key, value in values.items():
            if "\n" in value or "\r" in value:
                raise ServerSelectionError(f"environment value for {key} contains a newline")
            handle.write(f"{key}={value}\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Resolve a repository-confined physical E2E server datapack and map.")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--github-env", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        selection = resolve_server_selection(args.manifest.resolve(), args.root.resolve())
        write_github_env(args.github_env, github_environment(selection))
    except ServerSelectionError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
