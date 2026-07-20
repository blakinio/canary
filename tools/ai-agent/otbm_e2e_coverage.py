#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

TARGET_FORMAT = "canary-otbm-e2e-coverage-targets-v1"
OUTPUT_FORMAT = "canary-otbm-e2e-coverage-matrix-v1"
ITEM_AUDIT_FORMAT = "canary-otbm-item-audit-v1"
SCRIPT_FORMAT = "canary-otbm-script-resolution-v1"
REACHABILITY_FORMAT = "canary-otbm-reachability-v1"
WORLD_FORMAT = "canary-otbm-world-index-v1"
ROUTE_FORMAT = "canary-otbm-e2e-route-plan-v1"
SCHEMA_VERSION = 1
MAX_TARGETS = 10_000
MAX_ARTIFACT_FILES = 4_096
MAX_ARTIFACT_JSON_BYTES = 32 * 1024 * 1024
SELECTOR_KEYS = ("itemId", "actionId", "uniqueId", "houseDoorId", "teleportDestination")


class CoverageError(ValueError):
    pass


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CoverageError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise CoverageError(f"{path} must contain a JSON object")
    return value


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _require_format(document: dict[str, Any], expected: str, label: str) -> None:
    if document.get("format") != expected:
        raise CoverageError(f"{label} format must be {expected!r}")


def _position(value: Any, label: str) -> list[int]:
    if not isinstance(value, list) or len(value) != 3:
        raise CoverageError(f"{label} must be [x,y,z]")
    if any(not isinstance(item, int) or isinstance(item, bool) for item in value):
        raise CoverageError(f"{label} must contain integers")
    x, y, z = value
    if not (0 <= x <= 65535 and 0 <= y <= 65535 and 0 <= z <= 15):
        raise CoverageError(f"{label} is outside OTBM coordinate bounds")
    return [x, y, z]


def _selector(raw: Any, label: str) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise CoverageError(f"{label} must be an object")
    unknown = sorted(set(raw) - {"position", *SELECTOR_KEYS})
    if unknown:
        raise CoverageError(f"{label} has unsupported keys: {', '.join(unknown)}")
    if "position" not in raw:
        raise CoverageError(f"{label}.position is required")
    result: dict[str, Any] = {"position": _position(raw["position"], f"{label}.position")}
    identity_count = 0
    for key in SELECTOR_KEYS:
        value = raw.get(key)
        if value is None:
            result[key] = None
            continue
        if key == "teleportDestination":
            result[key] = _position(value, f"{label}.{key}")
        else:
            maximum = 255 if key == "houseDoorId" else 65535
            if not isinstance(value, int) or isinstance(value, bool) or not 0 <= value <= maximum:
                raise CoverageError(f"{label}.{key} must be in 0..{maximum} or null")
            result[key] = value
        identity_count += 1
    if identity_count == 0:
        raise CoverageError(f"{label} requires at least one mechanic identity field")
    return result


def _load_targets(path: Path) -> tuple[list[dict[str, Any]], str]:
    document = _read_json(path)
    _require_format(document, TARGET_FORMAT, "targets")
    if document.get("schemaVersion") != SCHEMA_VERSION:
        raise CoverageError("targets schemaVersion must be 1")
    raw_targets = document.get("targets")
    if not isinstance(raw_targets, list) or not raw_targets:
        raise CoverageError("targets.targets must be a non-empty array")
    if len(raw_targets) > MAX_TARGETS:
        raise CoverageError(f"targets.targets exceeds maximum {MAX_TARGETS}")
    seen: set[str] = set()
    targets: list[dict[str, Any]] = []
    for index, raw in enumerate(raw_targets):
        if not isinstance(raw, dict):
            raise CoverageError(f"targets.targets[{index}] must be an object")
        target_id = raw.get("id")
        reason = raw.get("reason")
        if not isinstance(target_id, str) or not target_id.strip():
            raise CoverageError(f"targets.targets[{index}].id must be non-empty")
        target_id = target_id.strip()
        if target_id in seen:
            raise CoverageError(f"duplicate target id {target_id!r}")
        seen.add(target_id)
        if not isinstance(reason, str) or not reason.strip():
            raise CoverageError(f"targets.targets[{index}].reason must be non-empty")
        targets.append(
            {
                "id": target_id,
                "reason": reason.strip(),
                "selector": _selector(raw.get("selector"), f"targets.targets[{index}].selector"),
            }
        )
    targets.sort(key=lambda item: item["id"])
    return targets, _sha256_file(path)


def _world_identity(path: Path) -> tuple[dict[str, str], str]:
    document = _read_json(path)
    _require_format(document, WORLD_FORMAT, "world manifest")
    source = document.get("source")
    index = document.get("index")
    map_sha = source.get("sha256") if isinstance(source, dict) else None
    index_sha = index.get("sha256") if isinstance(index, dict) else None
    if not _is_sha256(map_sha) or not _is_sha256(index_sha):
        raise CoverageError("world manifest source.sha256 and index.sha256 are required")
    return {"mapSha256": map_sha, "worldIndexSha256": index_sha}, _sha256_file(path)


def _candidate_position(candidate: dict[str, Any]) -> Any:
    for key in ("position", "source", "targetPosition"):
        if key in candidate:
            return candidate.get(key)
    return None


def _selector_matches(selector: dict[str, Any], candidate: dict[str, Any]) -> bool:
    if _candidate_position(candidate) != selector["position"]:
        return False
    for key in SELECTOR_KEYS:
        expected = selector.get(key)
        if expected is None:
            continue
        actual = candidate.get(key)
        if key == "teleportDestination" and actual is None:
            actual = candidate.get("destination")
        if actual != expected:
            return False
    return True


def _extract_hashes(provenance: Any) -> tuple[str | None, str | None]:
    if not isinstance(provenance, dict):
        return None, None

    def extract(*keys: str) -> str | None:
        for key in keys:
            value = provenance.get(key)
            if isinstance(value, dict) and _is_sha256(value.get("sha256")):
                return value["sha256"]
            if _is_sha256(value):
                return value
        return None

    map_sha = extract("map", "sourceMap")
    index_sha = extract("worldIndex", "index")
    manifest = provenance.get("worldIndexManifest")
    if isinstance(manifest, dict):
        source = manifest.get("source")
        index = manifest.get("index")
        if map_sha is None and isinstance(source, dict) and _is_sha256(source.get("sha256")):
            map_sha = source["sha256"]
        if index_sha is None and isinstance(index, dict) and _is_sha256(index.get("sha256")):
            index_sha = index["sha256"]
    return map_sha, index_sha


def _load_item_audit(path: Path, current: dict[str, str]) -> tuple[dict[str, Any], str]:
    document = _read_json(path)
    _require_format(document, ITEM_AUDIT_FORMAT, "item audit")
    sources = document.get("sources")
    map_source = sources.get("map") if isinstance(sources, dict) else None
    map_sha = map_source.get("sha256") if isinstance(map_source, dict) else None
    if map_sha != current["mapSha256"]:
        raise CoverageError("item audit map SHA-256 does not match current World Index manifest")
    if not isinstance(document.get("mechanicPlacements"), list):
        raise CoverageError("item audit mechanicPlacements must be an array")
    return document, _sha256_file(path)


def _load_script_resolution(path: Path, current: dict[str, str]) -> tuple[dict[str, Any], str]:
    document = _read_json(path)
    _require_format(document, SCRIPT_FORMAT, "script resolution")
    if not isinstance(document.get("placements"), list):
        raise CoverageError("script resolution placements must be an array")
    sources = document.get("sources")
    item_sources = sources.get("itemAudit") if isinstance(sources, dict) else None
    map_source = item_sources.get("map") if isinstance(item_sources, dict) else None
    map_sha = map_source.get("sha256") if isinstance(map_source, dict) else None
    if map_sha != current["mapSha256"]:
        raise CoverageError("script resolution item-audit map SHA-256 does not match current map")
    return document, _sha256_file(path)


def _load_reachability(
    paths: Iterable[Path], current: dict[str, str]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    reports: list[dict[str, Any]] = []
    provenance: list[dict[str, Any]] = []
    for path in paths:
        document = _read_json(path)
        _require_format(document, REACHABILITY_FORMAT, f"reachability {path}")
        mechanics = document.get("mechanics")
        if not isinstance(mechanics, list):
            raise CoverageError(f"reachability {path} mechanics must be an array")
        map_sha, index_sha = _extract_hashes(document.get("provenance"))
        report = {
            "path": str(path),
            "sha256": _sha256_file(path),
            "mapSha256": map_sha,
            "worldIndexSha256": index_sha,
            "currentProvenance": (
                map_sha == current["mapSha256"] and index_sha == current["worldIndexSha256"]
            ),
            "mechanics": mechanics,
        }
        reports.append(report)
        provenance.append({key: value for key, value in report.items() if key != "mechanics"})
    return reports, provenance


@dataclass(frozen=True)
class ArtifactFiles:
    label: str
    names: tuple[str, ...]
    read: Any
    digest: str


def _artifact_files(path: Path) -> ArtifactFiles:
    if path.is_dir():
        paths = sorted(item for item in path.rglob("*") if item.is_file())
        names = tuple(item.relative_to(path).as_posix() for item in paths)
        if len(names) > MAX_ARTIFACT_FILES:
            raise CoverageError(f"physical artifact exceeds {MAX_ARTIFACT_FILES} files")
        by_name = {item.relative_to(path).as_posix(): item for item in paths}
        digest = hashlib.sha256()
        for name in names:
            digest.update(name.encode())
            digest.update(b"\0")
            digest.update(bytes.fromhex(_sha256_file(by_name[name])))
        return ArtifactFiles(str(path), names, lambda name: by_name[name].read_bytes(), digest.hexdigest())
    if path.is_file() and zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as archive:
            names = tuple(sorted(name for name in archive.namelist() if not name.endswith("/")))
        if len(names) > MAX_ARTIFACT_FILES:
            raise CoverageError(f"physical artifact exceeds {MAX_ARTIFACT_FILES} files")

        def read_zip(name: str) -> bytes:
            with zipfile.ZipFile(path) as archive:
                return archive.read(name)

        return ArtifactFiles(str(path), names, read_zip, _sha256_file(path))
    raise CoverageError(f"physical artifact must be a directory or ZIP: {path}")


def _artifact_json(files: ArtifactFiles, name: str) -> dict[str, Any]:
    if name not in files.names:
        raise CoverageError(f"{files.label} is missing {name}")
    payload = files.read(name)
    if len(payload) > MAX_ARTIFACT_JSON_BYTES:
        raise CoverageError(f"{files.label}:{name} exceeds JSON size limit")
    try:
        value = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CoverageError(f"{files.label}:{name} is not valid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise CoverageError(f"{files.label}:{name} must contain an object")
    return value


def _artifact_text(files: ArtifactFiles, name: str) -> str | None:
    if name not in files.names:
        return None
    try:
        return files.read(name).decode("utf-8").strip()
    except UnicodeDecodeError as exc:
        raise CoverageError(f"{files.label}:{name} is not UTF-8: {exc}") from exc


def _scenario_route_ids(manifest: dict[str, Any]) -> set[str]:
    scenario = manifest.get("scenario")
    if not isinstance(scenario, dict):
        scenario = manifest
    steps = scenario.get("steps")
    if not isinstance(steps, list):
        return set()
    return {
        step["route"].strip()
        for step in steps
        if isinstance(step, dict)
        and step.get("action") == "follow_route"
        and isinstance(step.get("route"), str)
        and step["route"].strip()
    }


def _plan_candidates(plan: dict[str, Any]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    edges = plan.get("edges")
    if not isinstance(edges, list):
        return candidates
    for edge in edges:
        if not isinstance(edge, dict):
            continue
        evidence = edge.get("evidence")
        if edge.get("kind") == "transition" and isinstance(evidence, dict):
            transition = evidence.get("transition")
            if isinstance(transition, dict):
                candidates.append(transition)
        interactions = edge.get("interactions")
        if isinstance(interactions, list):
            for interaction in interactions:
                query = interaction.get("selectorQuery") if isinstance(interaction, dict) else None
                if isinstance(query, dict):
                    candidates.append(query)
    return candidates


def _load_physical_artifacts(
    paths: Iterable[Path], current: dict[str, str]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    runs: list[dict[str, Any]] = []
    provenance: list[dict[str, Any]] = []
    for path in paths:
        files = _artifact_files(path)
        result = _artifact_json(files, "result.json")
        manifest = _artifact_json(files, "scenario-manifest.json")
        scenario = result.get("scenario") or manifest.get("key")
        if not isinstance(scenario, str) or not scenario:
            raise CoverageError(f"{files.label} lacks scenario identity")
        success = result.get("status") == "success"
        checks = result.get("checks")
        if isinstance(checks, dict) and any(value is not True for value in checks.values()):
            success = False
        runtime_raw = _artifact_text(files, "map.sha256")
        runtime_sha = runtime_raw.split()[0] if runtime_raw else None
        if runtime_sha is not None and not _is_sha256(runtime_sha):
            raise CoverageError(f"{files.label}:map.sha256 does not begin with lowercase SHA-256")
        route_ids = _scenario_route_ids(manifest)
        expected_names = {f"route-{route_id}.json" for route_id in route_ids}
        plans: list[dict[str, Any]] = []
        for name in files.names:
            if Path(name).name not in expected_names:
                continue
            plan = _artifact_json(files, name)
            if plan.get("format") != ROUTE_FORMAT:
                continue
            map_sha, index_sha = _extract_hashes(plan.get("provenance"))
            plans.append(
                {
                    "name": name,
                    "executionStatus": plan.get("executionStatus"),
                    "mapSha256": map_sha,
                    "worldIndexSha256": index_sha,
                    "currentProvenance": (
                        map_sha == current["mapSha256"]
                        and index_sha == current["worldIndexSha256"]
                        and runtime_sha == current["mapSha256"]
                    ),
                    "candidates": _plan_candidates(plan),
                }
            )
        run = {
            "artifact": files.label,
            "artifactSha256": files.digest,
            "scenario": scenario,
            "success": success,
            "runtimeMapSha256": runtime_sha,
            "routeIds": sorted(route_ids),
            "plans": plans,
        }
        runs.append(run)
        provenance.append(
            {
                **{key: value for key, value in run.items() if key != "plans"},
                "routePlans": [
                    {key: value for key, value in plan.items() if key != "candidates"} for plan in plans
                ],
            }
        )
    runs.sort(key=lambda item: (item["scenario"], item["artifact"]))
    provenance.sort(key=lambda item: (item["scenario"], item["artifact"]))
    return runs, provenance


def _script_resolved(status: Any) -> bool:
    return isinstance(status, str) and status.startswith("handled-")


def _best_reachability_status(statuses: Iterable[str]) -> str | None:
    order = {"confirmed": 3, "conditional": 2, "unreachable": 1}
    valid = [status for status in statuses if status in order]
    return max(valid, key=lambda status: order[status]) if valid else None


def build_matrix(
    *,
    targets: list[dict[str, Any]],
    item_audit: dict[str, Any],
    script_resolution: dict[str, Any],
    reachability_reports: list[dict[str, Any]],
    physical_runs: list[dict[str, Any]],
    current: dict[str, str],
    provenance: dict[str, Any],
) -> dict[str, Any]:
    static_placements = [item for item in item_audit["mechanicPlacements"] if isinstance(item, dict)]
    script_placements = [item for item in script_resolution["placements"] if isinstance(item, dict)]
    rows: list[dict[str, Any]] = []
    findings: list[dict[str, str]] = []

    for target in targets:
        selector = target["selector"]
        target_id = target["id"]
        static_matches = [item for item in static_placements if _selector_matches(selector, item)]
        script_matches = [item for item in script_placements if _selector_matches(selector, item)]
        unique_static = len(static_matches) == 1
        unique_script = len(script_matches) == 1
        script_status = script_matches[0].get("status") if unique_script else None
        script_is_resolved = unique_static and unique_script and _script_resolved(script_status)

        reach_current: list[dict[str, Any]] = []
        reach_stale: list[dict[str, Any]] = []
        for report in reachability_reports:
            matches = [
                item
                for item in report["mechanics"]
                if isinstance(item, dict) and _selector_matches(selector, item)
            ]
            if not matches:
                continue
            payload = {
                "reportSha256": report["sha256"],
                "mapSha256": report["mapSha256"],
                "worldIndexSha256": report["worldIndexSha256"],
                "statuses": sorted({str(item.get("status")) for item in matches}),
            }
            (reach_current if report["currentProvenance"] else reach_stale).append(payload)

        scenarios: set[str] = set()
        proven_any: set[str] = set()
        proven_current: set[str] = set()
        proven_stale: set[str] = set()
        for run in physical_runs:
            for plan in run["plans"]:
                if not any(_selector_matches(selector, candidate) for candidate in plan["candidates"]):
                    continue
                scenarios.add(run["scenario"])
                if run["success"] and plan["executionStatus"] == "executable":
                    proven_any.add(run["scenario"])
                    if plan["currentProvenance"]:
                        proven_current.add(run["scenario"])
                    else:
                        proven_stale.add(run["scenario"])

        current_statuses = [status for evidence in reach_current for status in evidence["statuses"]]
        stale_statuses = [status for evidence in reach_stale for status in evidence["statuses"]]
        stale_gap = (bool(reach_stale) and not bool(reach_current)) or (
            bool(proven_stale) and not bool(proven_current)
        )
        has_any_provenance_evidence = bool(reach_current or reach_stale or proven_current or proven_stale)
        stale_state: bool | None = True if stale_gap else (False if has_any_provenance_evidence else None)
        missing_physical = bool(static_matches) and not scenarios

        row = {
            "id": target_id,
            "reason": target["reason"],
            "selector": selector,
            "static": {
                "indexed": bool(static_matches),
                "uniqueMatch": unique_static,
                "matchCount": len(static_matches),
            },
            "script": {
                "covered": bool(script_matches),
                "uniqueMatch": unique_script,
                "matchCount": len(script_matches),
                "status": script_status,
                "resolved": script_is_resolved,
            },
            "reachability": {
                "covered": bool(reach_current),
                "status": _best_reachability_status(current_statuses),
                "currentEvidence": reach_current,
                "staleEvidence": reach_stale,
                "staleStatus": _best_reachability_status(stale_statuses),
            },
            "physical": {
                "scenarioPresent": bool(scenarios),
                "scenarios": sorted(scenarios),
                "runtimeProven": bool(proven_any),
                "runtimeProvenScenarios": sorted(proven_any),
                "runtimeProvenOnCurrentMap": bool(proven_current),
                "currentMapScenarios": sorted(proven_current),
                "staleMapScenarios": sorted(proven_stale),
            },
            "staleAgainstCurrentMapProvenance": stale_state,
            "missingPhysicalScenario": missing_physical,
        }
        rows.append(row)

        def finding(code: str, severity: str) -> None:
            findings.append({"targetId": target_id, "code": code, "severity": severity})

        if not static_matches:
            finding("STATIC_MECHANIC_NOT_INDEXED", "error")
        elif not unique_static:
            finding("STATIC_MECHANIC_AMBIGUOUS", "error")
        elif not script_matches:
            finding("SCRIPT_RESOLUTION_NOT_COVERED", "unresolved")
        elif not unique_script:
            finding("SCRIPT_RESOLUTION_AMBIGUOUS", "unresolved")
        elif not script_is_resolved:
            finding("SCRIPT_NOT_RESOLVED", "unresolved")
        if not reach_current:
            finding("REACHABILITY_NOT_COVERED", "warning")
        if missing_physical:
            finding("PHYSICAL_SCENARIO_MISSING", "warning")
        elif scenarios and not proven_current:
            finding("PHYSICAL_RUNTIME_NOT_PROVEN_ON_CURRENT_MAP", "warning")
        if stale_state is True:
            finding("STALE_MAP_PROVENANCE", "warning")

    findings.sort(key=lambda item: (item["targetId"], item["code"]))
    summary = {
        "targets": len(rows),
        "staticallyIndexed": sum(row["static"]["indexed"] for row in rows),
        "scriptResolved": sum(row["script"]["resolved"] for row in rows),
        "reachabilityCovered": sum(row["reachability"]["covered"] for row in rows),
        "physicalScenarioPresent": sum(row["physical"]["scenarioPresent"] for row in rows),
        "physicallyRuntimeProven": sum(row["physical"]["runtimeProven"] for row in rows),
        "physicallyRuntimeProvenOnCurrentMap": sum(
            row["physical"]["runtimeProvenOnCurrentMap"] for row in rows
        ),
        "staleAgainstCurrentMapProvenance": sum(
            row["staleAgainstCurrentMapProvenance"] is True for row in rows
        ),
        "missingPhysicalScenario": sum(row["missingPhysicalScenario"] for row in rows),
        "findings": len(findings),
    }
    return {
        "format": OUTPUT_FORMAT,
        "schemaVersion": SCHEMA_VERSION,
        "currentMap": current,
        "provenance": provenance,
        "summary": summary,
        "mechanics": rows,
        "findings": findings,
        "notes": [
            "This tool aggregates existing Item Audit, Script Resolution, Reachability and Physical E2E evidence; it does not parse OTBM.",
            "Reachability is static evidence only and is current only when map and World Index hashes match.",
            "Physical mechanic proof requires a successful executed route plan with an exact mechanic reference and retained current runtime map provenance.",
            "Unresolved, ambiguous, stale or missing-provenance evidence is never promoted to handled or current runtime proof.",
        ],
    }


def _write_json(path: Path, value: dict[str, Any], overwrite: bool) -> None:
    if path.exists() and not overwrite:
        raise CoverageError(f"output exists; pass --overwrite: {path}")
    if path.is_symlink():
        raise CoverageError(f"refusing symlink output: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(payload)
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def build_from_args(args: argparse.Namespace) -> dict[str, Any]:
    targets, targets_sha = _load_targets(args.targets)
    current, world_sha = _world_identity(args.world_manifest)
    item_audit, item_sha = _load_item_audit(args.item_audit, current)
    script_resolution, script_sha = _load_script_resolution(args.script_resolution, current)
    reachability, reach_provenance = _load_reachability(args.reachability, current)
    physical, physical_provenance = _load_physical_artifacts(args.physical_artifact, current)
    return build_matrix(
        targets=targets,
        item_audit=item_audit,
        script_resolution=script_resolution,
        reachability_reports=reachability,
        physical_runs=physical,
        current=current,
        provenance={
            "targetsSha256": targets_sha,
            "worldManifestSha256": world_sha,
            "itemAuditSha256": item_sha,
            "scriptResolutionSha256": script_sha,
            "reachability": reach_provenance,
            "physicalArtifacts": physical_provenance,
        },
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build deterministic OTBM mechanic to Physical E2E coverage from existing evidence."
    )
    parser.add_argument("--targets", type=Path, required=True)
    parser.add_argument("--world-manifest", type=Path, required=True)
    parser.add_argument("--item-audit", type=Path, required=True)
    parser.add_argument("--script-resolution", type=Path, required=True)
    parser.add_argument("--reachability", type=Path, action="append", default=[])
    parser.add_argument("--physical-artifact", type=Path, action="append", default=[])
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args(argv)
    try:
        _write_json(args.output, build_from_args(args), args.overwrite)
    except CoverageError as exc:
        parser.exit(2, f"error: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
