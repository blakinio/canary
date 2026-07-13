from __future__ import annotations

import hashlib
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

REPORT_FORMAT = "canary-otbm-reachability-v1"
TRANSITION_FORMAT = "canary-otbm-transition-manifest-v1"
APPEARANCES_FORMAT = "canary-appearances-index-v1"
SCHEMA_VERSION = 1
MAX_REGION_COORDINATES = 1_000_000
MAX_ROUTES = 32
MAX_ROUTE_STARTS = 16
MAX_TRANSITIONS = 10_000
MAX_SAMPLE_LIMIT = 10_000
MAX_PATH_LIMIT = 10_000
DEFAULT_SAMPLE_LIMIT = 200
DEFAULT_PATH_LIMIT = 2_000

Position = tuple[int, int, int]
CARDINAL_STEPS: tuple[Position, ...] = ((-1, 0, 0), (0, -1, 0), (0, 1, 0), (1, 0, 0))
DIAGONAL_STEPS: tuple[Position, ...] = ((-1, -1, 0), (-1, 1, 0), (1, -1, 0), (1, 1, 0))
BLOCKING_UNCERTAINTIES = {
    "door-state",
    "quest-state",
    "dynamic-script",
    "runtime-condition",
    "script-resolution-missing",
    "script-resolution-unresolved",
    "script-resolution-partially-resolved",
    "script-resolution-referenced-only",
    "script-resolution-conflicting",
    "unknown",
}
ALLOWED_TRANSITION_KINDS = {
    "teleport",
    "stairs",
    "ladder",
    "hole",
    "rope",
    "floor-change",
    "custom",
}
SEVERITY_ORDER = {"error": 0, "warning": 1, "info": 2}


class ReachabilityError(RuntimeError):
    pass


@dataclass(frozen=True)
class AppearanceSemantics:
    item_id: int
    ground: bool
    unpassable: bool
    avoid: bool
    usable: bool
    multi_use: bool
    force_use: bool


@dataclass(frozen=True)
class TileState:
    position: Position
    tile_index: int
    kind: str
    house_id: int | None
    flags: int
    placement_ordinals: tuple[int, ...]
    item_ids: tuple[int, ...]
    has_ground: bool
    strict_walkable: bool
    optimistic_walkable: bool
    static_blockers: tuple[int, ...]
    conditional_blockers: tuple[int, ...]
    unknown_appearances: tuple[int, ...]
    avoid_items: tuple[int, ...]
    uncertainties: tuple[str, ...]

    def diagnostic_json(self) -> dict[str, Any]:
        return {
            "position": list(self.position),
            "kind": self.kind,
            "houseId": self.house_id,
            "tileFlags": self.flags,
            "itemIds": list(self.item_ids),
            "hasGround": self.has_ground,
            "strictWalkable": self.strict_walkable,
            "optimisticWalkable": self.optimistic_walkable,
            "staticBlockers": list(self.static_blockers),
            "conditionalBlockers": list(self.conditional_blockers),
            "unknownAppearances": list(self.unknown_appearances),
            "avoidItems": list(self.avoid_items),
            "uncertainties": list(self.uncertainties),
        }


@dataclass(frozen=True)
class TransitionSpec:
    transition_id: str
    kind: str
    source: Position
    destination: Position
    origin: str
    item_id: int | None
    expected_item_ids: tuple[int, ...]
    bidirectional: bool
    uncertainties: tuple[str, ...]
    evidence: Mapping[str, Any] | None
    script_status: str | None = None


@dataclass(frozen=True)
class TransitionState:
    spec: TransitionSpec
    valid: bool
    strict_eligible: bool
    optimistic_eligible: bool
    status: str
    issues: tuple[str, ...]

    def to_json(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "id": self.spec.transition_id,
            "kind": self.spec.kind,
            "origin": self.spec.origin,
            "source": list(self.spec.source),
            "destination": list(self.spec.destination),
            "itemId": self.spec.item_id,
            "expectedItemIds": list(self.spec.expected_item_ids),
            "bidirectional": self.spec.bidirectional,
            "uncertainties": list(self.spec.uncertainties),
            "scriptStatus": self.spec.script_status,
            "status": self.status,
            "valid": self.valid,
            "strictEligible": self.strict_eligible,
            "optimisticEligible": self.optimistic_eligible,
            "issues": list(self.issues),
        }
        if self.spec.evidence is not None:
            payload["evidence"] = dict(self.spec.evidence)
        return payload


@dataclass(frozen=True)
class GraphEdge:
    destination: Position
    transition_id: str | None


@dataclass
class FindingCollector:
    limit: int

    def __post_init__(self) -> None:
        self.counts: Counter[str] = Counter()
        self.severity_counts: Counter[str] = Counter()
        self.samples: list[dict[str, Any]] = []
        self.total = 0

    def add(self, severity: str, code: str, message: str, **details: Any) -> None:
        if severity not in SEVERITY_ORDER:
            raise ReachabilityError(f"Unsupported finding severity: {severity}")
        self.total += 1
        self.counts[code] += 1
        self.severity_counts[severity] += 1
        if len(self.samples) < self.limit:
            self.samples.append({"severity": severity, "code": code, "message": message, **details})

    def finish(self) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        self.samples.sort(
            key=lambda entry: (
                SEVERITY_ORDER[entry["severity"]],
                entry["code"],
                tuple(entry.get("position", entry.get("source", []))),
                entry.get("transitionId", ""),
            )
        )
        return self.samples, {
            "total": self.total,
            "bySeverity": {key: self.severity_counts.get(key, 0) for key in ("error", "warning", "info")},
            "byCode": dict(sorted(self.counts.items())),
            "truncated": self.total > len(self.samples),
        }


def _sha256(path: Path, chunk_size: int = 8 * 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def _position(value: Any, label: str) -> Position:
    if not isinstance(value, (list, tuple)) or len(value) != 3:
        raise ReachabilityError(f"{label} must contain exactly x,y,z")
    if any(not isinstance(part, int) or isinstance(part, bool) for part in value):
        raise ReachabilityError(f"{label} must contain integers")
    x, y, z = (int(part) for part in value)
    if not (0 <= x <= 0xFFFF and 0 <= y <= 0xFFFF and 0 <= z <= 15):
        raise ReachabilityError(f"{label} is outside the OTBM coordinate range")
    return x, y, z


def normalize_bounds(first: Position, second: Position) -> tuple[Position, Position]:
    first = _position(first, "region start")
    second = _position(second, "region end")
    lower: Position = tuple(min(first[i], second[i]) for i in range(3))  # type: ignore[assignment]
    upper: Position = tuple(max(first[i], second[i]) for i in range(3))  # type: ignore[assignment]
    coordinate_count = (upper[0] - lower[0] + 1) * (upper[1] - lower[1] + 1) * (upper[2] - lower[2] + 1)
    if coordinate_count > MAX_REGION_COORDINATES:
        raise ReachabilityError(
            f"Region contains {coordinate_count} coordinates; maximum is {MAX_REGION_COORDINATES}"
        )
    return lower, upper


def _in_bounds(position: Position, lower: Position, upper: Position) -> bool:
    return all(lower[i] <= position[i] <= upper[i] for i in range(3))


def _validate_limits(sample_limit: int, path_limit: int) -> None:
    if not isinstance(sample_limit, int) or isinstance(sample_limit, bool) or not 1 <= sample_limit <= MAX_SAMPLE_LIMIT:
        raise ReachabilityError(f"sample_limit must be in 1..{MAX_SAMPLE_LIMIT}")
    if not isinstance(path_limit, int) or isinstance(path_limit, bool) or not 1 <= path_limit <= MAX_PATH_LIMIT:
        raise ReachabilityError(f"path_limit must be in 1..{MAX_PATH_LIMIT}")


def load_appearance_semantics(path: Path) -> tuple[dict[int, AppearanceSemantics], dict[str, Any]]:
    source = path.expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError(source)
    if source.suffix.lower() == ".json":
        try:
            document = json.loads(source.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ReachabilityError(f"Cannot read appearances index {source}: {exc}") from exc
    else:
        try:
            from otbm_appearances import build_appearances_index
        except ImportError as exc:
            raise ReachabilityError("otbm_appearances.py is required to decode a binary appearances catalogue") from exc
        document = build_appearances_index(source)
    if not isinstance(document, dict) or document.get("format") != APPEARANCES_FORMAT:
        raise ReachabilityError(f"Unsupported appearances document: {source}")
    entries = document.get("appearances")
    if not isinstance(entries, list):
        raise ReachabilityError("Appearances document does not contain an appearances list")
    result: dict[int, AppearanceSemantics] = {}
    for entry in entries:
        if not isinstance(entry, dict) or entry.get("category") != "object":
            continue
        item_id = entry.get("id")
        if not isinstance(item_id, int) or isinstance(item_id, bool) or not 0 <= item_id <= 0xFFFF:
            continue
        if item_id in result:
            raise ReachabilityError(f"Duplicate object appearance ID {item_id}")
        flags = entry.get("flags") if isinstance(entry.get("flags"), dict) else {}
        result[item_id] = AppearanceSemantics(
            item_id=item_id,
            ground="bank" in flags,
            unpassable=bool(flags.get("unpassable")),
            avoid=bool(flags.get("avoid")),
            usable=bool(flags.get("usable")),
            multi_use=bool(flags.get("multiUse")),
            force_use=bool(flags.get("forceUse")),
        )
    if not result:
        raise ReachabilityError("Appearances document contains no object appearances")
    return result, {
        "path": source.name,
        "size": source.stat().st_size,
        "sha256": _sha256(source),
        "format": APPEARANCES_FORMAT,
        "objectCount": len(result),
    }


def load_transition_manifest(path: Path | None) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
    if path is None:
        return [], None
    source = path.expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError(source)
    try:
        document = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ReachabilityError(f"Cannot read transition manifest {source}: {exc}") from exc
    if not isinstance(document, dict) or document.get("format") != TRANSITION_FORMAT:
        raise ReachabilityError(f"Unsupported transition manifest: {source}")
    transitions = document.get("transitions")
    if not isinstance(transitions, list):
        raise ReachabilityError("Transition manifest does not contain a transitions list")
    if len(transitions) > MAX_TRANSITIONS:
        raise ReachabilityError(f"Transition manifest contains more than {MAX_TRANSITIONS} transitions")
    return transitions, {
        "path": source.name,
        "size": source.stat().st_size,
        "sha256": _sha256(source),
        "format": TRANSITION_FORMAT,
    }


def load_script_resolution(path: Path | None) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    if path is None:
        return None, None
    source = path.expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError(source)
    try:
        document = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ReachabilityError(f"Cannot read script-resolution report {source}: {exc}") from exc
    if not isinstance(document, dict) or document.get("format") != "canary-otbm-script-resolution-v1":
        raise ReachabilityError(f"Unsupported script-resolution report: {source}")
    if not isinstance(document.get("placements"), list):
        raise ReachabilityError("Script-resolution report does not contain placements")
    return document, {
        "path": source.name,
        "size": source.stat().st_size,
        "sha256": _sha256(source),
        "format": "canary-otbm-script-resolution-v1",
    }


def _script_lookup(report: dict[str, Any] | None) -> dict[tuple[Any, ...], str]:
    if report is None:
        return {}
    result: dict[tuple[Any, ...], str] = {}
    for entry in report.get("placements", []):
        if not isinstance(entry, dict):
            continue
        raw_position = entry.get("position")
        if raw_position is None:
            continue
        try:
            position = _position(raw_position, "script-resolution placement position")
        except ReachabilityError:
            continue
        key = (
            position,
            entry.get("itemId"),
            entry.get("actionId"),
            entry.get("uniqueId"),
            entry.get("houseDoorId"),
            tuple(entry["teleportDestination"]) if isinstance(entry.get("teleportDestination"), list) else None,
        )
        status = entry.get("status")
        if isinstance(status, str):
            result[key] = status
    return result


def _placement_script_status(placement: Mapping[str, Any], lookup: Mapping[tuple[Any, ...], str]) -> str | None:
    position = tuple(placement.get("position", ()))
    destination = placement.get("teleportDestination")
    key = (
        position,
        placement.get("itemId"),
        placement.get("actionId"),
        placement.get("uniqueId"),
        placement.get("houseDoorId"),
        tuple(destination) if isinstance(destination, list) else None,
    )
    return lookup.get(key)
