from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from otbm_world_index import WORLD_INDEX_FORMAT, WorldIndex, sha256_path

POLICY_FORMAT = "canary-otbm-static-hotspot-policy-v1"
REPORT_FORMAT = "canary-otbm-static-hotspots-v1"
SCHEMA_VERSION = 1


class StaticHotspotError(RuntimeError):
    pass


@dataclass(frozen=True)
class TileMetric:
    position: tuple[int, int, int]
    placement_count: int
    max_item_depth: int
    mechanic_count: int


@dataclass(frozen=True)
class HotspotContext:
    policy: dict[str, Any]
    tile_metrics: tuple[TileMetric, ...]
    provenance: dict[str, Any]


def _json_hash(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _read_json(path: Path, expected_format: str) -> dict[str, Any]:
    source = path.expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError(source)
    try:
        value = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise StaticHotspotError(f"Cannot read JSON {source}: {exc}") from exc
    if not isinstance(value, dict) or value.get("format") != expected_format:
        raise StaticHotspotError(f"Unsupported {expected_format} document: {source}")
    return value


def _sha(value: Any, label: str) -> str:
    if not isinstance(value, str) or len(value) != 64 or any(ch not in "0123456789abcdef" for ch in value.lower()):
        raise StaticHotspotError(f"{label} must be a SHA-256 hex string")
    return value.lower()


def _threshold(value: Any, label: str, *, minimum: int = 1) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < minimum:
        raise StaticHotspotError(f"{label} must be an integer >= {minimum}")
    return value


def normalize_policy(document: dict[str, Any]) -> dict[str, Any]:
    if document.get("format") != POLICY_FORMAT:
        raise StaticHotspotError(f"policy.format must be {POLICY_FORMAT}")
    thresholds = document.get("thresholds")
    if not isinstance(thresholds, dict):
        raise StaticHotspotError("policy.thresholds must be an object")
    return {
        "format": POLICY_FORMAT,
        "sourceMapSha256": _sha(document.get("sourceMapSha256"), "sourceMapSha256"),
        "worldIndexSha256": _sha(document.get("worldIndexSha256"), "worldIndexSha256"),
        "thresholds": {
            "placementsPerTile": _threshold(thresholds.get("placementsPerTile"), "placementsPerTile"),
            "maxItemDepth": _threshold(thresholds.get("maxItemDepth"), "maxItemDepth", minimum=0),
            "mechanicsPerTile": _threshold(thresholds.get("mechanicsPerTile"), "mechanicsPerTile"),
            "tilesPerArea": _threshold(thresholds.get("tilesPerArea"), "tilesPerArea"),
            "placementsPerArea": _threshold(thresholds.get("placementsPerArea"), "placementsPerArea"),
        },
    }


def collect_tile_metrics(index_path: Path) -> tuple[TileMetric, ...]:
    metrics: list[TileMetric] = []
    with WorldIndex(index_path.expanduser().resolve()) as index:
        for tile_index in range(index.header.tile_count):
            tile = index.tile(tile_index)
            max_depth = -1
            mechanics = 0
            for ordinal in range(tile.placement_start, tile.placement_start + tile.placement_count):
                placement = index.placement(ordinal)
                depth = placement.get("itemDepth")
                if isinstance(depth, int):
                    max_depth = max(max_depth, depth)
                if any(key in placement for key in ("actionId", "uniqueId", "houseDoorId", "teleportDestination")):
                    mechanics += 1
            metrics.append(TileMetric((tile.x, tile.y, tile.z), tile.placement_count, max_depth, mechanics))
    return tuple(metrics)


def build_static_hotspot_report(context: HotspotContext) -> dict[str, Any]:
    thresholds = context.policy["thresholds"]
    findings: list[dict[str, Any]] = []
    areas: dict[tuple[int, int, int], dict[str, int]] = {}
    for metric in context.tile_metrics:
        x, y, z = metric.position
        area_key = (x & 0xFF00, y & 0xFF00, z)
        aggregate = areas.setdefault(area_key, {"tiles": 0, "placements": 0, "mechanics": 0})
        aggregate["tiles"] += 1
        aggregate["placements"] += metric.placement_count
        aggregate["mechanics"] += metric.mechanic_count
        if metric.placement_count >= thresholds["placementsPerTile"]:
            findings.append({"severity": "warning", "code": "tile-placement-density", "message": "Tile placement count meets the reviewed hotspot threshold", "position": list(metric.position), "value": metric.placement_count, "threshold": thresholds["placementsPerTile"]})
        if metric.max_item_depth >= thresholds["maxItemDepth"]:
            findings.append({"severity": "warning", "code": "tile-item-depth", "message": "Tile maximum item depth meets the reviewed hotspot threshold", "position": list(metric.position), "value": metric.max_item_depth, "threshold": thresholds["maxItemDepth"]})
        if metric.mechanic_count >= thresholds["mechanicsPerTile"]:
            findings.append({"severity": "warning", "code": "tile-mechanic-density", "message": "Tile mechanic count meets the reviewed hotspot threshold", "position": list(metric.position), "value": metric.mechanic_count, "threshold": thresholds["mechanicsPerTile"]})

    for (base_x, base_y, z), aggregate in sorted(areas.items()):
        if aggregate["tiles"] >= thresholds["tilesPerArea"]:
            findings.append({"severity": "info", "code": "area-tile-density", "message": "Indexed 256x256 area tile count meets the reviewed hotspot threshold", "area": [base_x, base_y, z], "value": aggregate["tiles"], "threshold": thresholds["tilesPerArea"]})
        if aggregate["placements"] >= thresholds["placementsPerArea"]:
            findings.append({"severity": "warning", "code": "area-placement-density", "message": "Indexed 256x256 area placement count meets the reviewed hotspot threshold", "area": [base_x, base_y, z], "value": aggregate["placements"], "threshold": thresholds["placementsPerArea"], "mechanics": aggregate["mechanics"]})

    findings.sort(key=lambda item: (item["code"], tuple(item.get("position", item.get("area", [])))))
    report: dict[str, Any] = {
        "format": REPORT_FORMAT,
        "schemaVersion": SCHEMA_VERSION,
        "provenance": context.provenance,
        "thresholds": thresholds,
        "summary": {
            "tileCount": len(context.tile_metrics),
            "areaCount": len(areas),
            "candidateCount": len(findings),
            "byCode": {code: sum(1 for finding in findings if finding["code"] == code) for code in sorted({finding["code"] for finding in findings})},
        },
        "candidates": findings,
        "policy": {
            "reusesCanonicalWorldIndex": True,
            "reparsesOtbm": False,
            "runsRuntimeProfiler": False,
            "runtimePerformanceImpactProven": False,
            "mutatesMap": False,
        },
    }
    report["reportSha256"] = _json_hash(report)
    return report


def prepare_hotspot_context(*, policy_path: Path, world_index_path: Path, world_manifest_path: Path) -> HotspotContext:
    policy = normalize_policy(_read_json(policy_path, POLICY_FORMAT))
    world_manifest = _read_json(world_manifest_path, WORLD_INDEX_FORMAT)
    index_sha = sha256_path(world_index_path.expanduser().resolve()).lower()
    source_sha = str(world_manifest.get("source", {}).get("sha256", "")).lower()
    manifest_index_sha = str(world_manifest.get("index", {}).get("sha256", "")).lower()
    if policy["sourceMapSha256"] != source_sha:
        raise StaticHotspotError(f"sourceMapSha256 provenance mismatch: expected {policy['sourceMapSha256']}, got {source_sha or '<missing>'}")
    if policy["worldIndexSha256"] != index_sha or policy["worldIndexSha256"] != manifest_index_sha:
        raise StaticHotspotError("worldIndexSha256 provenance mismatch between policy, index file and World Index manifest")
    return HotspotContext(policy, collect_tile_metrics(world_index_path), {"sourceMapSha256": source_sha, "worldIndexSha256": index_sha})
