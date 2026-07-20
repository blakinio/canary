#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import shutil
import subprocess
import sys
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

REPO_ROOT = Path(__file__).resolve().parents[2]
for _root in (REPO_ROOT / "tools" / "e2e", REPO_ROOT / "tools" / "ai-agent"):
    if str(_root) not in sys.path:
        sys.path.insert(0, str(_root))

FORMAT = "canary-otbm-candidate-physical-validation-v1"
PIPELINE_FORMAT = "canary-otbm-repair-materialization-pipeline-v1"
DIFF_FORMAT = "canary-otbm-semantic-diff-v1"
SELECTION_FORMAT = "canary-otbm-e2e-impacted-selection-v1"
LANDMARK_FORMAT = "canary-otbm-semantic-landmarks-v1"


class CandidatePhysicalValidationError(RuntimeError):
    pass


@dataclass(frozen=True)
class EvidenceChain:
    source_sha256: str
    candidate_sha256: str
    semantic_diff_sha256: str
    before_world_index_sha256: str
    after_world_index_sha256: str
    pipeline: dict[str, Any]
    semantic_diff: dict[str, Any]
    selection: dict[str, Any]


@dataclass(frozen=True)
class ScenarioBinding:
    suite: str
    scenario_id: str
    scenario: Any
    selection_entry: dict[str, Any]

    @property
    def key(self) -> str:
        return f"{self.suite}/{self.scenario_id}"


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _file(path: Path, label: str) -> Path:
    path = path.expanduser().resolve()
    if not path.is_file() or path.is_symlink() or path.stat().st_size <= 0:
        raise CandidatePhysicalValidationError(f"{label} must be a non-empty regular non-symlink file: {path}")
    return path


def _json(path: Path, label: str) -> dict[str, Any]:
    path = _file(path, label)
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CandidatePhysicalValidationError(f"cannot read {label} {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise CandidatePhysicalValidationError(f"{label} must contain a JSON object")
    return value


def _write(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _map(value: object, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise CandidatePhysicalValidationError(f"{label} must be an object")
    return value


def _sha(value: object, label: str) -> str:
    if not isinstance(value, str) or len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
        raise CandidatePhysicalValidationError(f"{label} must be a lowercase SHA-256")
    return value


def _format(document: Mapping[str, Any], expected: str, label: str) -> None:
    if document.get("format") != expected or document.get("schemaVersion") != 1:
        raise CandidatePhysicalValidationError(f"{label} must be {expected} schemaVersion 1")


def _true(value: object, label: str) -> None:
    if value is not True:
        raise CandidatePhysicalValidationError(f"{label} must be true")


def _false(value: object, label: str) -> None:
    if value is not False:
        raise CandidatePhysicalValidationError(f"{label} must be false")


def validate_evidence_chain(
    *,
    source_map_path: Path,
    candidate_map_path: Path,
    pipeline_result_path: Path,
    semantic_diff_path: Path,
    impacted_selection_path: Path,
) -> EvidenceChain:
    source = _file(source_map_path, "source map")
    candidate = _file(candidate_map_path, "candidate map")
    if source == candidate:
        raise CandidatePhysicalValidationError("source and candidate map paths must be distinct")
    source_sha = sha256_path(source)
    candidate_sha = sha256_path(candidate)
    pipeline = _json(pipeline_result_path, "pipeline result")
    diff = _json(semantic_diff_path, "Semantic OTBM Diff")
    selection = _json(impacted_selection_path, "impacted E2E selection")
    diff_sha = sha256_path(_file(semantic_diff_path, "Semantic OTBM Diff"))

    _format(pipeline, PIPELINE_FORMAT, "pipeline result")
    _true(pipeline.get("ok"), "pipeline result ok")
    pipeline_source = _map(pipeline.get("source"), "pipeline source")
    pipeline_output = _map(pipeline.get("output"), "pipeline output")
    quality = _map(pipeline.get("quality"), "pipeline quality")
    safety = _map(pipeline.get("safety"), "pipeline safety")
    if _sha(pipeline_source.get("sha256"), "pipeline source sha256") != source_sha:
        raise CandidatePhysicalValidationError("pipeline source SHA does not match exact source map")
    _true(pipeline_source.get("unchanged"), "pipeline source unchanged")
    if _sha(pipeline_output.get("sha256"), "pipeline output sha256") != candidate_sha:
        raise CandidatePhysicalValidationError("pipeline output SHA does not match exact candidate map")
    _true(pipeline_output.get("createNew"), "pipeline output createNew")
    _true(pipeline_output.get("byteIdenticalToVerifiedCandidate"), "pipeline output byteIdenticalToVerifiedCandidate")
    _true(quality.get("ok"), "pipeline quality ok")
    if _sha(quality.get("sourceSha256"), "pipeline quality sourceSha256") != candidate_sha:
        raise CandidatePhysicalValidationError("pipeline quality source SHA does not match candidate map")
    for key in ("sourceModifiedInPlace", "silentOverwrite", "newOtbmParserCreated", "newOtbmWriterCreated", "productionMapExecutionAuthorized"):
        _false(safety.get(key), f"pipeline safety {key}")
    for key in ("existingMutationBoundaryReused", "existingMapQualityGateReused", "allDirectFileInputsPinned"):
        _true(safety.get(key), f"pipeline safety {key}")

    _format(diff, DIFF_FORMAT, "Semantic OTBM Diff")
    _true(diff.get("ok"), "Semantic OTBM Diff ok")
    _true(_map(diff.get("compatibility"), "Semantic OTBM Diff compatibility").get("compatible"), "Semantic OTBM Diff compatible")
    provenance = _map(diff.get("provenance"), "Semantic OTBM Diff provenance")
    before = _map(provenance.get("before"), "Semantic OTBM Diff before")
    after = _map(provenance.get("after"), "Semantic OTBM Diff after")
    before_map = _map(before.get("sourceMap"), "Semantic OTBM Diff before sourceMap")
    after_map = _map(after.get("sourceMap"), "Semantic OTBM Diff after sourceMap")
    before_index = _map(before.get("worldIndex"), "Semantic OTBM Diff before worldIndex")
    after_index = _map(after.get("worldIndex"), "Semantic OTBM Diff after worldIndex")
    if _sha(before_map.get("sha256"), "Semantic OTBM Diff before map sha256") != source_sha:
        raise CandidatePhysicalValidationError("Semantic OTBM Diff before map SHA does not match source map")
    if _sha(after_map.get("sha256"), "Semantic OTBM Diff after map sha256") != candidate_sha:
        raise CandidatePhysicalValidationError("Semantic OTBM Diff after map SHA does not match candidate map")
    before_index_sha = _sha(before_index.get("sha256"), "Semantic OTBM Diff before world index sha256")
    after_index_sha = _sha(after_index.get("sha256"), "Semantic OTBM Diff after world index sha256")

    _format(selection, SELECTION_FORMAT, "impacted E2E selection")
    _true(selection.get("ok"), "impacted E2E selection ok")
    selection_diff = _map(selection.get("semanticDiff"), "impacted E2E selection semanticDiff")
    pins = {
        "sha256": diff_sha,
        "beforeMapSha256": source_sha,
        "afterMapSha256": candidate_sha,
        "beforeWorldIndexSha256": before_index_sha,
        "afterWorldIndexSha256": after_index_sha,
    }
    for key, expected in pins.items():
        if _sha(selection_diff.get(key), f"impacted E2E selection semanticDiff.{key}") != expected:
            raise CandidatePhysicalValidationError(f"impacted E2E selection semanticDiff.{key} does not match exact evidence chain")

    scenarios = selection.get("scenarios")
    if not isinstance(scenarios, list) or not scenarios:
        raise CandidatePhysicalValidationError("impacted E2E selection scenarios must be a non-empty array")
    selected_count = skipped_count = fail_closed_count = 0
    seen: set[str] = set()
    for index, raw in enumerate(scenarios):
        entry = _map(raw, f"impacted E2E selection scenarios[{index}]")
        suite, scenario_id = entry.get("suite"), entry.get("id")
        if not isinstance(suite, str) or not suite or not isinstance(scenario_id, str) or not scenario_id:
            raise CandidatePhysicalValidationError(f"scenario selection entry {index} has invalid suite/id")
        key = f"{suite}/{scenario_id}"
        if key in seen:
            raise CandidatePhysicalValidationError(f"duplicate impacted E2E scenario {key}")
        seen.add(key)
        selected, fail_closed = entry.get("selected"), entry.get("failClosed")
        if not isinstance(selected, bool) or not isinstance(fail_closed, bool):
            raise CandidatePhysicalValidationError(f"scenario {key} selected/failClosed must be boolean")
        if entry.get("decision") != ("selected" if selected else "skipped"):
            raise CandidatePhysicalValidationError(f"scenario {key} decision disagrees with selected flag")
        _sha(_map(entry.get("manifest"), f"scenario {key} manifest").get("sha256"), f"scenario {key} manifest sha256")
        selected_count += int(selected)
        skipped_count += int(not selected)
        fail_closed_count += int(fail_closed)
    summary = _map(selection.get("summary"), "impacted E2E selection summary")
    for key, expected in {
        "scenarioCount": len(scenarios),
        "selectedCount": selected_count,
        "skippedCount": skipped_count,
        "failClosedCount": fail_closed_count,
    }.items():
        if summary.get(key) != expected:
            raise CandidatePhysicalValidationError(f"impacted E2E selection summary.{key} does not match computed {expected}")

    return EvidenceChain(source_sha, candidate_sha, diff_sha, before_index_sha, after_index_sha, pipeline, diff, selection)


def bind_selected_scenarios(repo_root: Path, chain: EvidenceChain) -> list[ScenarioBinding]:
    entries = [entry for entry in chain.selection["scenarios"] if entry["selected"] is True]
    if not entries:
        return []
    from run_agent_e2e import discover, select

    scenarios = discover(repo_root)
    bindings: list[ScenarioBinding] = []
    logical_server: tuple[str, str] | None = None
    for entry in entries:
        scenario = select(scenarios, str(entry["suite"]), str(entry["id"]))
        expected = str(entry["manifest"]["sha256"])
        if sha256_path(scenario.path) != expected:
            raise CandidatePhysicalValidationError(f"scenario {scenario.key} manifest SHA changed after impacted selection")
        server = _map(scenario.data.get("server"), f"scenario {scenario.key} server")
        pair = (str(server.get("datapack")), str(server.get("map")))
        if logical_server is not None and pair != logical_server:
            raise CandidatePhysicalValidationError("selected candidate-map scenarios must share one logical server datapack/map")
        logical_server = pair
        bindings.append(ScenarioBinding(scenario.suite, scenario.scenario_id, scenario, dict(entry)))
    return bindings


def _route_ids(scenario: Any) -> list[str]:
    from prepare_otbm_route import route_ids_from_manifest
    from run_agent_e2e import normalized_manifest

    return route_ids_from_manifest(normalized_manifest(scenario))


def _exact_diff_positions(diff: Mapping[str, Any]) -> set[tuple[int, int, int]]:
    scope = _map(diff.get("scope"), "Semantic OTBM Diff scope")
    finding_summary = _map(_map(diff.get("summary"), "Semantic OTBM Diff summary").get("findings"), "Semantic OTBM Diff finding summary")
    findings = diff.get("findings")
    if scope.get("type") != "full-index":
        raise CandidatePhysicalValidationError("candidate landmark provenance derivation requires full-index Semantic OTBM Diff")
    if finding_summary.get("truncated") is not False:
        raise CandidatePhysicalValidationError("candidate landmark provenance derivation requires non-truncated Semantic OTBM Diff")
    if not isinstance(findings, list) or finding_summary.get("total") != len(findings) or finding_summary.get("sampleCount") != len(findings):
        raise CandidatePhysicalValidationError("candidate landmark provenance derivation requires the complete exact Semantic OTBM Diff finding set")
    positions: set[tuple[int, int, int]] = set()
    for raw in findings:
        position = _map(raw, "Semantic OTBM Diff finding").get("position")
        if not isinstance(position, list) or len(position) != 3 or any(not isinstance(v, int) or isinstance(v, bool) for v in position):
            raise CandidatePhysicalValidationError("candidate landmark provenance derivation requires an exact position for every Semantic OTBM Diff finding")
        positions.add((position[0], position[1], position[2]))
    return positions


def derive_candidate_landmark_registry(
    *, repo_root: Path, bindings: Sequence[ScenarioBinding], chain: EvidenceChain, baseline_registry_path: Path, output_path: Path
) -> Path | None:
    route_ids = list(dict.fromkeys(route for binding in bindings for route in _route_ids(binding.scenario)))
    if not route_ids:
        return None
    changed = _exact_diff_positions(chain.semantic_diff)
    registry = _json(baseline_registry_path, "baseline semantic landmark registry")
    _format(registry, LANDMARK_FORMAT, "baseline semantic landmark registry")
    if registry.get("registryStatus") != "reviewed":
        raise CandidatePhysicalValidationError("baseline semantic landmark registry must be reviewed")
    provenance = _map(registry.get("provenance"), "baseline landmark provenance")
    if _sha(_map(provenance.get("sourceMap"), "baseline landmark sourceMap").get("sha256"), "baseline landmark source map sha256") != chain.source_sha256:
        raise CandidatePhysicalValidationError("baseline landmark registry is not pinned to Semantic Diff before map")
    if _sha(_map(provenance.get("worldIndex"), "baseline landmark worldIndex").get("sha256"), "baseline landmark world index sha256") != chain.before_world_index_sha256:
        raise CandidatePhysicalValidationError("baseline landmark registry is not pinned to Semantic Diff before World Index")

    from otbm_semantic_landmarks import resolve_landmark_anchor
    from prepare_otbm_route import load_route_request

    checked: list[dict[str, Any]] = []
    for route_id in route_ids:
        request = load_route_request(repo_root / "tests" / "e2e" / "routes" / f"{route_id}.json")
        for role, endpoint in (("route-origin", request["from"]), ("route-destination", request["to"])):
            anchor_id = endpoint.get("anchorId")
            resolved = resolve_landmark_anchor(
                registry,
                landmark_id=endpoint["landmarkId"],
                anchor_id=anchor_id,
                role=None if anchor_id is not None else role,
                expected_source_map_sha256=chain.source_sha256,
                expected_world_index_sha256=chain.before_world_index_sha256,
            )
            position = tuple(int(v) for v in resolved["anchor"]["position"])
            if position in changed:
                raise CandidatePhysicalValidationError(
                    f"reviewed landmark anchor {endpoint['landmarkId']} at {position} changed; supply an explicitly reviewed candidate landmark registry"
                )
            checked.append({"routeId": route_id, "landmarkId": endpoint["landmarkId"], "anchorId": resolved["anchor"]["id"], "position": list(position)})
    candidate_registry = copy.deepcopy(registry)
    candidate_registry["provenance"]["sourceMap"]["sha256"] = chain.candidate_sha256
    candidate_registry["provenance"]["worldIndex"]["sha256"] = chain.after_world_index_sha256
    _write(output_path, candidate_registry)
    _write(output_path.with_name("candidate-landmark-provenance.json"), {
        "format": "canary-otbm-candidate-landmark-provenance-v1", "schemaVersion": 1,
        "beforeMapSha256": chain.source_sha256, "afterMapSha256": chain.candidate_sha256,
        "beforeWorldIndexSha256": chain.before_world_index_sha256, "afterWorldIndexSha256": chain.after_world_index_sha256,
        "semanticDiffSha256": chain.semantic_diff_sha256, "checkedAnchors": checked,
        "policy": {"fullIndexRequired": True, "nonTruncatedRequired": True, "completeFindingSetRequired": True, "changedAnchorBlocksDerivation": True, "committedRegistryModified": False},
    })
    return output_path


def _copy_runtime_repository(
    *, repo_root: Path, source_datapack: str, map_name: str, candidate_map_path: Path, candidate_sha256: str, runtime_parent: Path
) -> tuple[Path, Path]:
    root = repo_root.resolve()
    source_datapack_path = (root / source_datapack).resolve()
    if not source_datapack_path.is_dir() or source_datapack_path.is_symlink() or not source_datapack_path.is_relative_to(root):
        raise CandidatePhysicalValidationError(f"selected source datapack is missing or unsafe: {source_datapack_path}")
    artifacts = (root / "artifacts").resolve()
    artifacts.mkdir(parents=True, exist_ok=True)
    runtime_parent = runtime_parent.resolve()
    if not runtime_parent.is_relative_to(artifacts):
        raise CandidatePhysicalValidationError("candidate runtime parent must remain under repository artifacts/")
    runtime_repo = runtime_parent / "repo"

    def ignore(directory: str, names: list[str]) -> set[str]:
        current = Path(directory).resolve()
        try:
            relative = current.relative_to(root)
        except ValueError:
            return set()
        ignored: set[str] = set()
        if relative == Path("."):
            for name in names:
                if name in {".git", "artifacts", "otclient", "vcpkg_installed"} or name == "build" or name.startswith("build-") or name.startswith("cmake-build-"):
                    ignored.add(name)
        if relative == Path("tibia-client-assets") and "assets" in names:
            ignored.add("assets")
        return ignored

    shutil.copytree(root, runtime_repo, copy_function=shutil.copy2, ignore=ignore)
    runtime_datapack = (runtime_repo / source_datapack).resolve()
    if not runtime_datapack.is_dir() or not runtime_datapack.is_relative_to(runtime_repo.resolve()):
        raise CandidatePhysicalValidationError("disposable runtime repository is missing the selected datapack")
    runtime_map = runtime_datapack / "world" / f"{map_name}.otbm"
    runtime_map.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(candidate_map_path, runtime_map)
    if sha256_path(runtime_map) != candidate_sha256:
        raise CandidatePhysicalValidationError("disposable runtime repository candidate map SHA does not match verified candidate")
    return runtime_repo, runtime_map


def run_candidate_validation(
    *, source_map_path: Path, candidate_map_path: Path, pipeline_result_path: Path, semantic_diff_path: Path,
    impacted_selection_path: Path, repo_root: Path, output_dir: Path, assets_dir: Path | None = None,
    candidate_landmark_registry_path: Path | None = None, execute: bool = False,
    environment: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    repo_root = repo_root.expanduser().resolve()
    output_dir = output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    source_map = _file(source_map_path, "source map")
    candidate_map = _file(candidate_map_path, "candidate map")
    source_before = sha256_path(source_map)
    chain = validate_evidence_chain(
        source_map_path=source_map, candidate_map_path=candidate_map, pipeline_result_path=pipeline_result_path,
        semantic_diff_path=semantic_diff_path, impacted_selection_path=impacted_selection_path,
    )
    bindings = bind_selected_scenarios(repo_root, chain)
    server_pairs = {(str(b.scenario.data["server"]["datapack"]), str(b.scenario.data["server"]["map"])) for b in bindings}
    if len(server_pairs) > 1:
        raise CandidatePhysicalValidationError("selected scenarios disagree on logical candidate server datapack/map")
    logical_server = next(iter(server_pairs), None)

    landmark_registry: Path | None = None
    if bindings and any(_route_ids(binding.scenario) for binding in bindings):
        if candidate_landmark_registry_path is not None:
            candidate_registry = _json(candidate_landmark_registry_path, "candidate semantic landmark registry")
            _format(candidate_registry, LANDMARK_FORMAT, "candidate semantic landmark registry")
            if candidate_registry.get("registryStatus") != "reviewed":
                raise CandidatePhysicalValidationError("explicit candidate semantic landmark registry must be reviewed")
            provenance = _map(candidate_registry.get("provenance"), "candidate landmark provenance")
            if _sha(_map(provenance.get("sourceMap"), "candidate landmark sourceMap").get("sha256"), "candidate landmark source map sha256") != chain.candidate_sha256:
                raise CandidatePhysicalValidationError("explicit candidate landmark registry source map SHA does not match candidate")
            if _sha(_map(provenance.get("worldIndex"), "candidate landmark worldIndex").get("sha256"), "candidate landmark world index sha256") != chain.after_world_index_sha256:
                raise CandidatePhysicalValidationError("explicit candidate landmark registry World Index SHA does not match Semantic Diff after index")
            landmark_registry = _file(candidate_landmark_registry_path, "candidate semantic landmark registry")
        else:
            landmark_registry = derive_candidate_landmark_registry(
                repo_root=repo_root, bindings=bindings, chain=chain,
                baseline_registry_path=repo_root / "docs" / "ai-agent" / "OTBM_SEMANTIC_LANDMARKS.json",
                output_path=output_dir / "candidate-semantic-landmarks.json",
            )

    scenario_results: list[dict[str, Any]] = []
    runtime_removed = True
    if execute and bindings:
        if assets_dir is None:
            raise CandidatePhysicalValidationError("--assets-dir is required when --execute is used")
        assets = assets_dir.expanduser().resolve()
        if not (assets / "catalog-content.json").is_file():
            raise CandidatePhysicalValidationError(f"client assets directory is incomplete: {assets}")
        assert logical_server is not None
        runtime_root = repo_root / "artifacts" / f"otbm-candidate-runtime-{uuid.uuid4().hex[:12]}"
        runtime_root.mkdir(parents=True, exist_ok=False)
        try:
            runtime_repo, runtime_map = _copy_runtime_repository(
                repo_root=repo_root, source_datapack=logical_server[0], map_name=logical_server[1],
                candidate_map_path=candidate_map, candidate_sha256=chain.candidate_sha256, runtime_parent=runtime_root,
            )
            from prepare_otbm_route import prepare_routes
            from run_agent_e2e import normalized_manifest

            for binding in bindings:
                scenario_dir = output_dir / "scenarios" / binding.suite / binding.scenario_id
                scenario_dir.mkdir(parents=True, exist_ok=True)
                manifest_path = scenario_dir / "scenario-manifest.json"
                _write(manifest_path, normalized_manifest(binding.scenario))
                route_summary: dict[str, Any] = {"status": "not-required", "routeIds": []}
                if _route_ids(binding.scenario):
                    if landmark_registry is None:
                        raise CandidatePhysicalValidationError(f"candidate landmark registry is required for route scenario {binding.key}")
                    route_summary = prepare_routes(
                        manifest_path=manifest_path, runtime_map_path=runtime_map, assets_dir=assets,
                        artifact_dir=scenario_dir, landmark_registry_path=landmark_registry,
                        route_request_root=repo_root / "tests" / "e2e" / "routes",
                        scanner_source=repo_root / "tools" / "ai-agent" / "otbm_item_audit_scan.cpp",
                    )
                env = os.environ.copy()
                if environment is not None:
                    env.update({str(k): str(v) for k, v in environment.items()})
                env.update({
                    "AGENT_E2E_SUITE": binding.suite,
                    "AGENT_E2E_SCENARIO_ID": binding.scenario_id,
                    "AGENT_E2E_ARTIFACT_DIR": str(scenario_dir),
                    "AGENT_E2E_ASSET_SOURCE": str(assets),
                    "AGENT_E2E_OTCLIENT_ROOT": str(repo_root / "otclient"),
                })
                completed = subprocess.run(
                    ["bash", str(runtime_repo / "tools" / "e2e" / "run_physical_e2e.sh")], cwd=runtime_repo,
                    env=env, text=True, capture_output=True, check=False,
                )
                result_path = scenario_dir / "result.json"
                try:
                    physical_result = json.loads(result_path.read_text(encoding="utf-8")) if result_path.is_file() else None
                except json.JSONDecodeError:
                    physical_result = None
                map_sha_path = scenario_dir / "map.sha256"
                tokens = map_sha_path.read_text(encoding="utf-8", errors="replace").strip().split() if map_sha_path.is_file() else []
                runtime_map_sha = tokens[0] if tokens else None
                if runtime_map_sha != chain.candidate_sha256:
                    raise CandidatePhysicalValidationError(f"existing Universal Physical E2E runner did not retain exact candidate runtime map evidence for {binding.key}")
                scenario_results.append({
                    "suite": binding.suite, "id": binding.scenario_id, "key": binding.key, "executed": True,
                    "returnCode": completed.returncode, "runtimeMapSha256": runtime_map_sha,
                    "routePreparation": route_summary, "physicalResult": physical_result,
                })
                if completed.returncode != 0 or not isinstance(physical_result, dict) or physical_result.get("status") != "success":
                    raise CandidatePhysicalValidationError(f"existing Universal Physical E2E runner failed for selected scenario {binding.key}; returnCode={completed.returncode}")
        finally:
            shutil.rmtree(runtime_root, ignore_errors=True)
            runtime_removed = not runtime_root.exists()
    else:
        scenario_results = [{
            "suite": b.suite, "id": b.scenario_id, "key": b.key, "executed": False,
            "returnCode": None, "runtimeMapSha256": None, "routePreparation": None, "physicalResult": None,
        } for b in bindings]

    if sha256_path(source_map) != source_before:
        raise CandidatePhysicalValidationError("source map changed during candidate physical validation")
    selected_summary = [{
        "suite": b.suite, "id": b.scenario_id, "key": b.key, "manifestSha256": sha256_path(b.scenario.path),
        "failClosed": bool(b.selection_entry["failClosed"]), "impactedFindingIds": list(b.selection_entry.get("impactedFindingIds", [])),
    } for b in bindings]
    result = {
        "format": FORMAT, "schemaVersion": 1, "ok": True, "mode": "execute" if execute else "validate-only",
        "source": {"path": str(source_map), "sha256": chain.source_sha256, "unchanged": True},
        "candidate": {"path": str(candidate_map), "sha256": chain.candidate_sha256, "createNew": True},
        "evidence": {
            "pipelineResult": {"path": str(_file(pipeline_result_path, "pipeline result")), "sha256": sha256_path(_file(pipeline_result_path, "pipeline result"))},
            "semanticDiff": {"path": str(_file(semantic_diff_path, "Semantic OTBM Diff")), "sha256": chain.semantic_diff_sha256, "beforeWorldIndexSha256": chain.before_world_index_sha256, "afterWorldIndexSha256": chain.after_world_index_sha256},
            "impactedSelection": {"path": str(_file(impacted_selection_path, "impacted E2E selection")), "sha256": sha256_path(_file(impacted_selection_path, "impacted E2E selection"))},
            "candidateLandmarkRegistry": None if landmark_registry is None else {"path": str(landmark_registry), "sha256": sha256_path(landmark_registry)},
        },
        "selection": {
            "scenarioCount": int(chain.selection["summary"]["scenarioCount"]), "selectedCount": int(chain.selection["summary"]["selectedCount"]),
            "skippedCount": int(chain.selection["summary"]["skippedCount"]), "failClosedCount": int(chain.selection["summary"]["failClosedCount"]),
            "selectedScenarios": selected_summary,
        },
        "execution": {"requested": execute, "required": bool(bindings), "performed": execute and bool(bindings), "runtimeWorkspaceRemoved": runtime_removed, "scenarios": scenario_results},
        "safety": {
            "sourceModifiedInPlace": False, "candidateCopiedToActiveDatapack": False, "productionMapDeployed": False,
            "newOtbmParserCreated": False, "newOtbmWriterCreated": False, "newWorldIndexImplementationCreated": False,
            "newPathfinderCreated": False, "newPhysicalE2ERunnerCreated": False, "newWorkflowCreated": False,
            "existingMutationBoundaryReused": True, "existingMapQualityGateReused": True, "existingSemanticDiffReused": True,
            "existingImpactedSelectionReused": True, "existingRoutePreparationReused": True, "existingPhysicalE2ERunnerReused": True,
        },
    }
    _write(output_dir / "candidate-physical-validation.json", result)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate and optionally execute selected Universal Physical E2E scenarios on an exact create-new OTBM candidate map")
    parser.add_argument("--source-map", type=Path, required=True)
    parser.add_argument("--candidate-map", type=Path, required=True)
    parser.add_argument("--pipeline-result", type=Path, required=True)
    parser.add_argument("--semantic-diff", type=Path, required=True)
    parser.add_argument("--impacted-selection", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--assets-dir", type=Path)
    parser.add_argument("--candidate-landmark-registry", type=Path)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args(argv)
    try:
        result = run_candidate_validation(
            source_map_path=args.source_map, candidate_map_path=args.candidate_map,
            pipeline_result_path=args.pipeline_result, semantic_diff_path=args.semantic_diff,
            impacted_selection_path=args.impacted_selection, repo_root=args.repo_root,
            output_dir=args.output_dir, assets_dir=args.assets_dir,
            candidate_landmark_registry_path=args.candidate_landmark_registry, execute=args.execute,
        )
    except (OSError, ValueError, CandidatePhysicalValidationError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
