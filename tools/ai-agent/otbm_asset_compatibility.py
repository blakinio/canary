from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from otbm_assets import ASSET_INDEX_FORMAT
from otbm_appearances import APPEARANCES_INDEX_FORMAT
from otbm_world_index import WORLD_INDEX_FORMAT, WorldIndex, sha256_path

MANIFEST_FORMAT = "canary-otbm-asset-compatibility-manifest-v1"
REPORT_FORMAT = "canary-otbm-asset-compatibility-v1"
SCHEMA_VERSION = 1
WALKABILITY_FLAGS = ("ground", "unpassable", "avoid", "usable", "multiUse", "forceUse")


class AssetCompatibilityError(RuntimeError):
    pass


@dataclass(frozen=True)
class AssetCompatibilityContext:
    manifest: dict[str, Any]
    world_manifest: dict[str, Any]
    used_item_ids: tuple[int, ...]
    appearances: dict[str, Any]
    assets: dict[str, Any]
    baseline_appearances: dict[str, Any] | None
    provenance: dict[str, Any]


def _sha256_json(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _read_json(path: Path, expected_format: str) -> dict[str, Any]:
    source = path.expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError(source)
    try:
        value = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise AssetCompatibilityError(f"Cannot read JSON {source}: {exc}") from exc
    if not isinstance(value, dict) or value.get("format") != expected_format:
        raise AssetCompatibilityError(f"Unsupported {expected_format} document: {source}")
    return value


def _sha(value: Any, label: str) -> str:
    if not isinstance(value, str) or len(value) != 64 or any(ch not in "0123456789abcdef" for ch in value.lower()):
        raise AssetCompatibilityError(f"{label} must be a lowercase/uppercase SHA-256 hex string")
    return value.lower()


def normalize_manifest(document: dict[str, Any]) -> dict[str, Any]:
    if document.get("format") != MANIFEST_FORMAT:
        raise AssetCompatibilityError(f"manifest.format must be {MANIFEST_FORMAT}")
    result = {
        "format": MANIFEST_FORMAT,
        "sourceMapSha256": _sha(document.get("sourceMapSha256"), "sourceMapSha256"),
        "worldIndexSha256": _sha(document.get("worldIndexSha256"), "worldIndexSha256"),
        "appearancesSha256": _sha(document.get("appearancesSha256"), "appearancesSha256"),
        "assetIndexSha256": _sha(document.get("assetIndexSha256"), "assetIndexSha256"),
    }
    baseline = document.get("baselineAppearancesSha256")
    if baseline is not None:
        result["baselineAppearancesSha256"] = _sha(baseline, "baselineAppearancesSha256")
    return result


def _appearance_map(document: dict[str, Any]) -> dict[int, dict[str, Any]]:
    entries = document.get("appearances")
    if not isinstance(entries, list):
        raise AssetCompatibilityError("appearance index does not contain appearances")
    result: dict[int, dict[str, Any]] = {}
    for entry in entries:
        if not isinstance(entry, dict) or entry.get("category") != "object":
            continue
        item_id = entry.get("id")
        if not isinstance(item_id, int) or isinstance(item_id, bool) or not 0 <= item_id <= 0xFFFF:
            continue
        if item_id in result:
            raise AssetCompatibilityError(f"duplicate object appearance ID {item_id}")
        result[item_id] = entry
    return result


def _semantic_signature(entry: dict[str, Any]) -> dict[str, bool]:
    flags = entry.get("flags") if isinstance(entry.get("flags"), dict) else {}
    return {
        "ground": "bank" in flags,
        "unpassable": bool(flags.get("unpassable")),
        "avoid": bool(flags.get("avoid")),
        "usable": bool(flags.get("usable")),
        "multiUse": bool(flags.get("multiUse")),
        "forceUse": bool(flags.get("forceUse")),
    }


def _sprite_ids(entry: dict[str, Any]) -> tuple[int, ...]:
    values: set[int] = set()
    for group in entry.get("frameGroups", []):
        if not isinstance(group, dict):
            continue
        info = group.get("spriteInfo")
        if not isinstance(info, dict):
            continue
        for value in info.get("spriteIds", []):
            if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
                values.add(value)
    return tuple(sorted(values))


def _asset_ranges(document: dict[str, Any]) -> list[tuple[int, int, bool, str | None]]:
    sprites = document.get("sprites")
    if not isinstance(sprites, list):
        raise AssetCompatibilityError("asset index does not contain sprites")
    result: list[tuple[int, int, bool, str | None]] = []
    for entry in sprites:
        if not isinstance(entry, dict):
            continue
        first = entry.get("firstSpriteId")
        last = entry.get("lastSpriteId")
        if isinstance(first, int) and isinstance(last, int) and not isinstance(first, bool) and not isinstance(last, bool) and first <= last:
            result.append((first, last, bool(entry.get("exists")), entry.get("relativePath") if isinstance(entry.get("relativePath"), str) else None))
    return sorted(result)


def _coverage(sprite_id: int, ranges: list[tuple[int, int, bool, str | None]]) -> tuple[bool, bool, tuple[str, ...]]:
    matched = [(exists, path) for first, last, exists, path in ranges if first <= sprite_id <= last]
    if not matched:
        return False, False, ()
    paths = tuple(sorted(path for _, path in matched if path))
    return True, any(exists for exists, _ in matched), paths


def _finding(severity: str, code: str, message: str, **details: Any) -> dict[str, Any]:
    return {"severity": severity, "code": code, "message": message, **details}


def build_asset_compatibility_report(context: AssetCompatibilityContext) -> dict[str, Any]:
    current = _appearance_map(context.appearances)
    baseline = _appearance_map(context.baseline_appearances) if context.baseline_appearances is not None else None
    ranges = _asset_ranges(context.assets)
    findings: list[dict[str, Any]] = []
    missing_appearance = 0
    uncovered_sprite_ids: set[int] = set()
    missing_sprite_files: set[int] = set()
    semantic_deltas = 0

    for item_id in context.used_item_ids:
        appearance = current.get(item_id)
        if appearance is None:
            missing_appearance += 1
            findings.append(_finding("error", "missing-object-appearance", "Used OTBM item ID has no canonical object appearance", itemId=item_id))
            continue
        for sprite_id in _sprite_ids(appearance):
            if sprite_id == 0:
                findings.append(_finding("warning", "zero-sprite-reference", "Used object appearance references sprite ID 0", itemId=item_id, spriteId=0))
                continue
            covered, existing, paths = _coverage(sprite_id, ranges)
            if not covered:
                uncovered_sprite_ids.add(sprite_id)
                findings.append(_finding("error", "uncovered-sprite-id", "Used object appearance references a sprite outside indexed asset ranges", itemId=item_id, spriteId=sprite_id))
            elif not existing:
                missing_sprite_files.add(sprite_id)
                findings.append(_finding("error", "missing-sprite-asset-file", "Used object appearance references a sprite range whose indexed asset file is missing", itemId=item_id, spriteId=sprite_id, assetPaths=list(paths)))

        if baseline is not None and item_id in baseline:
            before = _semantic_signature(baseline[item_id])
            after = _semantic_signature(appearance)
            if before != after:
                semantic_deltas += 1
                changed = [flag for flag in WALKABILITY_FLAGS if before[flag] != after[flag]]
                findings.append(_finding("warning", "appearance-semantics-changed", "Canonical appearance flags used by walkability/interaction classification changed for a used item ID", itemId=item_id, changedFlags=changed, before=before, after=after))

    findings.sort(key=lambda value: (value["severity"], value["code"], value.get("itemId", -1), value.get("spriteId", -1)))
    counts = {severity: sum(1 for finding in findings if finding["severity"] == severity) for severity in ("error", "warning", "info")}
    report: dict[str, Any] = {
        "format": REPORT_FORMAT,
        "schemaVersion": SCHEMA_VERSION,
        "ok": counts["error"] == 0,
        "provenance": context.provenance,
        "scope": {"usedItemIdCount": len(context.used_item_ids), "baselineCompared": baseline is not None},
        "summary": {
            "missingObjectAppearances": missing_appearance,
            "uncoveredSpriteIds": len(uncovered_sprite_ids),
            "missingSpriteAssetFiles": len(missing_sprite_files),
            "appearanceSemanticDeltas": semantic_deltas,
            "findings": len(findings),
            "bySeverity": counts,
        },
        "findings": findings,
        "policy": {
            "reusesCanonicalWorldIndex": True,
            "reusesCanonicalAppearanceIndex": True,
            "reusesCanonicalAssetIndex": True,
            "reparsesOtbm": False,
            "reparsesAppearancesOrAssets": False,
            "mutatesMapOrAssets": False,
            "runtimeRenderingProven": False,
        },
    }
    report["reportSha256"] = _sha256_json(report)
    return report


def prepare_asset_compatibility_context(
    *,
    manifest_path: Path,
    world_index_path: Path,
    world_manifest_path: Path,
    appearances_path: Path,
    asset_index_path: Path,
    baseline_appearances_path: Path | None = None,
) -> AssetCompatibilityContext:
    manifest = normalize_manifest(_read_json(manifest_path, MANIFEST_FORMAT))
    world_manifest = _read_json(world_manifest_path, WORLD_INDEX_FORMAT)
    appearances = _read_json(appearances_path, APPEARANCES_INDEX_FORMAT)
    assets = _read_json(asset_index_path, ASSET_INDEX_FORMAT)
    baseline = _read_json(baseline_appearances_path, APPEARANCES_INDEX_FORMAT) if baseline_appearances_path is not None else None

    actual_index_sha = sha256_path(world_index_path.expanduser().resolve()).lower()
    actual_appearances_sha = sha256_path(appearances_path.expanduser().resolve()).lower()
    actual_assets_sha = sha256_path(asset_index_path.expanduser().resolve()).lower()
    world_source_sha = str(world_manifest.get("source", {}).get("sha256", "")).lower()
    world_manifest_index_sha = str(world_manifest.get("index", {}).get("sha256", "")).lower()
    expected = {
        "sourceMapSha256": (manifest["sourceMapSha256"], world_source_sha),
        "worldIndexSha256": (manifest["worldIndexSha256"], actual_index_sha),
        "worldManifest.index.sha256": (manifest["worldIndexSha256"], world_manifest_index_sha),
        "appearancesSha256": (manifest["appearancesSha256"], actual_appearances_sha),
        "assetIndexSha256": (manifest["assetIndexSha256"], actual_assets_sha),
    }
    for label, (wanted, actual) in expected.items():
        if wanted != actual:
            raise AssetCompatibilityError(f"{label} provenance mismatch: expected {wanted}, got {actual or '<missing>'}")
    baseline_sha: str | None = None
    if baseline_appearances_path is not None:
        baseline_sha = sha256_path(baseline_appearances_path.expanduser().resolve()).lower()
        wanted = manifest.get("baselineAppearancesSha256")
        if wanted is None:
            raise AssetCompatibilityError("baselineAppearancesSha256 is required when baseline appearances are supplied")
        if wanted != baseline_sha:
            raise AssetCompatibilityError(f"baselineAppearancesSha256 provenance mismatch: expected {wanted}, got {baseline_sha}")
    elif "baselineAppearancesSha256" in manifest:
        raise AssetCompatibilityError("baselineAppearancesSha256 was declared but no baseline appearances input was supplied")

    used: list[int] = []
    with WorldIndex(world_index_path.expanduser().resolve()) as index:
        for item_id in range(0x10000):
            _, count = index.item_directory(item_id)
            if count:
                used.append(item_id)

    provenance = {
        "sourceMapSha256": world_source_sha,
        "worldIndexSha256": actual_index_sha,
        "appearancesSha256": actual_appearances_sha,
        "assetIndexSha256": actual_assets_sha,
        "baselineAppearancesSha256": baseline_sha,
    }
    return AssetCompatibilityContext(manifest, world_manifest, tuple(used), appearances, assets, baseline, provenance)
