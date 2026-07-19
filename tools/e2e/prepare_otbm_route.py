#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Mapping

REPO_ROOT = Path(__file__).resolve().parents[2]
AI_AGENT_ROOT = REPO_ROOT / "tools" / "ai-agent"
if str(AI_AGENT_ROOT) not in sys.path:
    sys.path.insert(0, str(AI_AGENT_ROOT))

from otbm_reachability import export_route_plan_index_path, write_report  # noqa: E402
from otbm_route_preflight import preflight_index_paths  # noqa: E402
from otbm_semantic_landmarks import load_registry, resolve_landmark_anchor  # noqa: E402
from otbm_world_index import build_world_index, sha256_path  # noqa: E402

ROUTE_ID_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")
MAX_EXECUTABLE_POSITIONS = 10_000


class RoutePreparationError(RuntimeError):
    pass


def _load_json(path: Path, label: str) -> dict[str, Any]:
    candidate = path.expanduser().resolve()
    if not candidate.is_file():
        raise RoutePreparationError(f"{label} does not exist: {candidate}")
    try:
        document = json.loads(candidate.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RoutePreparationError(f"cannot read {label} {candidate}: {exc}") from exc
    if not isinstance(document, dict):
        raise RoutePreparationError(f"{label} must contain a JSON object: {candidate}")
    return document


def _write_json(path: Path, document: Mapping[str, Any]) -> None:
    write_report(path, document, overwrite=True)


def route_ids_from_manifest(document: Mapping[str, Any]) -> list[str]:
    scenario = document.get("scenario")
    if not isinstance(scenario, Mapping):
        raise RoutePreparationError("scenario manifest is missing scenario object")
    steps = scenario.get("steps")
    if steps is None:
        return []
    if not isinstance(steps, list):
        raise RoutePreparationError("scenario.steps must be an array when supplied")

    route_ids: list[str] = []
    seen: set[str] = set()
    for index, step in enumerate(steps):
        if not isinstance(step, Mapping):
            raise RoutePreparationError(f"scenario.steps[{index}] must be an object")
        if step.get("action") != "follow_route":
            continue
        route_id = step.get("route")
        if not isinstance(route_id, str) or ROUTE_ID_RE.fullmatch(route_id) is None:
            raise RoutePreparationError(
                f"scenario.steps[{index}].route must match {ROUTE_ID_RE.pattern}"
            )
        if route_id not in seen:
            seen.add(route_id)
            route_ids.append(route_id)
    return route_ids


def _validate_endpoint(value: Any, label: str) -> dict[str, str]:
    if not isinstance(value, Mapping):
        raise RoutePreparationError(f"{label} must be an object")
    unknown = set(value) - {"landmarkId", "anchorId"}
    if unknown:
        raise RoutePreparationError(f"{label} has unknown fields: {', '.join(sorted(unknown))}")
    landmark_id = value.get("landmarkId")
    if not isinstance(landmark_id, str) or not landmark_id:
        raise RoutePreparationError(f"{label}.landmarkId must be a non-empty string")
    result = {"landmarkId": landmark_id}
    anchor_id = value.get("anchorId")
    if anchor_id is not None:
        if not isinstance(anchor_id, str) or not anchor_id:
            raise RoutePreparationError(f"{label}.anchorId must be a non-empty string when supplied")
        result["anchorId"] = anchor_id
    return result


def load_route_request(path: Path) -> dict[str, Any]:
    request = _load_json(path, "route request")
    unknown = set(request) - {"from", "to", "routingOptions"}
    if unknown:
        raise RoutePreparationError(f"route request has unknown fields: {', '.join(sorted(unknown))}")

    origin = _validate_endpoint(request.get("from"), "route request.from")
    destination = _validate_endpoint(request.get("to"), "route request.to")
    options_value = request.get("routingOptions", {})
    if not isinstance(options_value, Mapping):
        raise RoutePreparationError("route request.routingOptions must be an object")
    unknown_options = set(options_value) - {"allowDiagonal", "maxExecutablePositions"}
    if unknown_options:
        raise RoutePreparationError(
            "route request.routingOptions has unknown fields: " + ", ".join(sorted(unknown_options))
        )
    allow_diagonal = options_value.get("allowDiagonal", False)
    if not isinstance(allow_diagonal, bool):
        raise RoutePreparationError("route request.routingOptions.allowDiagonal must be boolean")
    max_positions = options_value.get("maxExecutablePositions", MAX_EXECUTABLE_POSITIONS)
    if (
        not isinstance(max_positions, int)
        or isinstance(max_positions, bool)
        or not 1 <= max_positions <= MAX_EXECUTABLE_POSITIONS
    ):
        raise RoutePreparationError(
            f"route request.routingOptions.maxExecutablePositions must be in 1..{MAX_EXECUTABLE_POSITIONS}"
        )
    return {
        "from": origin,
        "to": destination,
        "routingOptions": {
            "allowDiagonal": allow_diagonal,
            "maxExecutablePositions": max_positions,
        },
    }


def find_appearances(assets_dir: Path) -> Path:
    directory = assets_dir.expanduser().resolve()
    if not directory.is_dir():
        raise RoutePreparationError(f"client assets directory does not exist: {directory}")
    candidates = sorted(path for path in directory.glob("appearances-*.dat") if path.is_file())
    if len(candidates) != 1:
        raise RoutePreparationError(
            f"expected exactly one appearances-*.dat in {directory}, found {len(candidates)}"
        )
    return candidates[0]


def compile_scanner(source: Path, output: Path, *, cxx: str | None = None) -> None:
    source = source.expanduser().resolve()
    if not source.is_file():
        raise RoutePreparationError(f"native OTBM scanner source does not exist: {source}")
    compiler = shlex.split(cxx or os.environ.get("CXX", "g++"))
    if not compiler:
        raise RoutePreparationError("CXX resolves to an empty compiler command")
    command = [
        *compiler,
        "-O2",
        "-std=c++20",
        "-Wall",
        "-Wextra",
        "-Wpedantic",
        "-Werror",
        str(source),
        "-o",
        str(output),
    ]
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip() or f"exit code {completed.returncode}"
        raise RoutePreparationError(f"native OTBM scanner compilation failed: {detail}")


def _resolve_endpoint(
    registry: Mapping[str, Any],
    endpoint: Mapping[str, str],
    *,
    role: str,
    map_sha256: str,
    world_index_sha256: str,
) -> dict[str, Any]:
    anchor_id = endpoint.get("anchorId")
    return resolve_landmark_anchor(
        registry,
        landmark_id=endpoint["landmarkId"],
        anchor_id=anchor_id,
        role=None if anchor_id is not None else role,
        expected_source_map_sha256=map_sha256,
        expected_world_index_sha256=world_index_sha256,
    )


def prepare_routes(
    *,
    manifest_path: Path,
    runtime_map_path: Path,
    assets_dir: Path,
    artifact_dir: Path,
    landmark_registry_path: Path,
    route_request_root: Path,
    scanner_source: Path,
    cxx: str | None = None,
) -> dict[str, Any]:
    manifest = _load_json(manifest_path, "scenario manifest")
    route_ids = route_ids_from_manifest(manifest)
    if not route_ids:
        return {"status": "not-required", "routeIds": []}

    runtime_map = runtime_map_path.expanduser().resolve()
    if not runtime_map.is_file() or runtime_map.stat().st_size <= 0:
        raise RoutePreparationError(f"runtime OTBM map is missing or empty: {runtime_map}")
    appearances = find_appearances(assets_dir)
    registry_path = landmark_registry_path.expanduser().resolve()
    request_root = route_request_root.expanduser().resolve()
    output_root = artifact_dir.expanduser().resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="canary-otbm-e2e-route-") as temporary_name:
        temporary = Path(temporary_name)
        scanner = temporary / "otbm_item_audit_scan"
        index_path = temporary / "runtime.widx"
        index_manifest_path = temporary / "runtime.widx.json"
        compile_scanner(scanner_source, scanner, cxx=cxx)
        world_manifest = build_world_index(
            map_path=runtime_map,
            scanner=scanner,
            output=index_path,
            manifest_output=index_manifest_path,
            overwrite=False,
        )
        map_sha256 = str(world_manifest["source"]["sha256"])
        world_index_sha256 = str(world_manifest["index"]["sha256"])
        registry = load_registry(
            registry_path,
            expected_source_map_sha256=map_sha256,
            expected_world_index_sha256=world_index_sha256,
            require_reviewed=True,
        )

        prepared: list[dict[str, Any]] = []
        for route_id in route_ids:
            request_path = (request_root / f"{route_id}.json").resolve()
            if not request_path.is_relative_to(request_root):
                raise RoutePreparationError(f"route request escapes canonical root: {route_id}")
            request = load_route_request(request_path)
            origin = _resolve_endpoint(
                registry,
                request["from"],
                role="route-origin",
                map_sha256=map_sha256,
                world_index_sha256=world_index_sha256,
            )
            destination = _resolve_endpoint(
                registry,
                request["to"],
                role="route-destination",
                map_sha256=map_sha256,
                world_index_sha256=world_index_sha256,
            )
            if origin["regionId"] != destination["regionId"]:
                raise RoutePreparationError(
                    f"route {route_id} endpoints resolve to different regions: "
                    f"{origin['regionId']} != {destination['regionId']}"
                )
            if origin["routingBounds"] != destination["routingBounds"]:
                raise RoutePreparationError(f"route {route_id} endpoints disagree on routing bounds")

            bounds = origin["routingBounds"]
            lower = tuple(bounds["from"])
            upper = tuple(bounds["to"])
            origin_position = tuple(origin["anchor"]["position"])
            destination_position = tuple(destination["anchor"]["position"])
            options = request["routingOptions"]
            plan = export_route_plan_index_path(
                index_path=index_path,
                appearances_path=appearances,
                lower=lower,
                upper=upper,
                origin=origin_position,
                destination=destination_position,
                world_manifest_path=index_manifest_path,
                allow_diagonal=bool(options["allowDiagonal"]),
                max_positions=int(options["maxExecutablePositions"]),
            )
            if plan.get("executionStatus") != "executable" or plan.get("pathComplete") is not True:
                raise RoutePreparationError(
                    f"route {route_id} is not executable under current exact-map evidence: "
                    f"status={plan.get('executionStatus')!r} blockers={plan.get('blockers')!r}"
                )

            candidate_plan = temporary / f"route-{route_id}.json"
            request_evidence = output_root / f"route-{route_id}-request.json"
            preflight_evidence = output_root / f"route-{route_id}-preflight.json"
            manifest_evidence = output_root / f"route-{route_id}-world-index-manifest.json"
            final_plan = output_root / f"route-{route_id}.json"
            _write_json(candidate_plan, plan)
            _write_json(request_evidence, request)
            _write_json(manifest_evidence, world_manifest)
            preflight = preflight_index_paths(
                route_plan_path=candidate_plan,
                runtime_map_path=runtime_map,
                index_path=index_path,
                appearances_path=appearances,
                world_manifest_path=index_manifest_path,
                landmark_registry_path=registry_path,
                landmark_request_path=request_evidence,
            )
            _write_json(preflight_evidence, preflight)
            if preflight.get("ok") is not True:
                raise RoutePreparationError(
                    f"route {route_id} exact-map static preflight blocked: {preflight.get('firstBlocker')!r}"
                )
            _write_json(final_plan, plan)
            prepared.append(
                {
                    "routeId": route_id,
                    "planHashSha256": plan.get("planHashSha256"),
                    "origin": plan.get("origin"),
                    "destination": plan.get("destination"),
                    "distance": plan.get("distance"),
                    "routingMode": plan.get("routingMode"),
                    "preflightStatus": preflight.get("status"),
                }
            )

        summary = {
            "status": "passed",
            "routeIds": route_ids,
            "runtimeMap": {
                "path": runtime_map.name,
                "size": runtime_map.stat().st_size,
                "sha256": map_sha256,
            },
            "worldIndex": {
                "retained": False,
                "size": world_manifest["index"]["size"],
                "sha256": world_index_sha256,
            },
            "appearances": {
                "path": appearances.name,
                "size": appearances.stat().st_size,
                "sha256": sha256_path(appearances),
            },
            "scannerSource": {
                "path": scanner_source.name,
                "sha256": sha256_path(scanner_source.expanduser().resolve()),
            },
            "routes": prepared,
        }
        _write_json(output_root / "route-preparation.json", summary)
        return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Prepare canonical exact-map OTBM route-plan artifacts for Universal Physical E2E"
    )
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--runtime-map", type=Path, required=True)
    parser.add_argument("--assets-dir", type=Path, required=True)
    parser.add_argument("--artifact-dir", type=Path, required=True)
    parser.add_argument(
        "--landmark-registry",
        type=Path,
        default=REPO_ROOT / "docs" / "ai-agent" / "OTBM_SEMANTIC_LANDMARKS.json",
    )
    parser.add_argument(
        "--route-request-root",
        type=Path,
        default=REPO_ROOT / "tests" / "e2e" / "routes",
    )
    parser.add_argument(
        "--scanner-source",
        type=Path,
        default=REPO_ROOT / "tools" / "ai-agent" / "otbm_item_audit_scan.cpp",
    )
    parser.add_argument("--cxx")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = prepare_routes(
            manifest_path=args.manifest,
            runtime_map_path=args.runtime_map,
            assets_dir=args.assets_dir,
            artifact_dir=args.artifact_dir,
            landmark_registry_path=args.landmark_registry,
            route_request_root=args.route_request_root,
            scanner_source=args.scanner_source,
            cxx=args.cxx,
        )
    except (OSError, RoutePreparationError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
