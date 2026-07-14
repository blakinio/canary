from __future__ import annotations

import hashlib
import json
import os
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping

REPORT_FORMAT = "canary-otbm-geometry-audit-v1"
RULES_FORMAT = "canary-otbm-geometry-rules-v1"
RENDER_FORMAT = "canary-otbm-geometry-audit-render-v1"
SCHEMA_VERSION = 1
PZ_FLAG_MASK = 0x0001
MAX_REGION_COORDINATES = 1_000_000
MAX_SAMPLE_LIMIT = 10_000
MAX_RULES = 10_000
MAX_JSON_BYTES = 64 * 1024 * 1024
DEFAULT_SAMPLE_LIMIT = 500
DEFAULT_ORPHAN_MAX_TILES = 8
SEVERITY_ORDER = {"error": 0, "warning": 1, "info": 2}
CONFIDENCE_ORDER = {"high": 0, "medium": 1, "low": 2}
DIRECTIONS: dict[str, tuple[int, int, int]] = {
    "north": (0, -1, 0),
    "east": (1, 0, 0),
    "south": (0, 1, 0),
    "west": (-1, 0, 0),
}

Position = tuple[int, int, int]


class GeometryAuditError(RuntimeError):
    pass


@dataclass(frozen=True)
class AdjacencyRule:
    rule_id: str
    category: str
    source_item_ids: tuple[int, ...]
    direction: str
    required_neighbor_item_ids: tuple[int, ...]
    severity: str
    confidence: str
    message: str

    def to_json(self) -> dict[str, Any]:
        return {
            "id": self.rule_id,
            "category": self.category,
            "sourceItemIds": list(self.source_item_ids),
            "direction": self.direction,
            "requiredNeighborItemIds": list(self.required_neighbor_item_ids),
            "severity": self.severity,
            "confidence": self.confidence,
            "message": self.message,
        }


@dataclass(frozen=True)
class AppearanceEvidence:
    item_id: int
    ground: bool
    unpassable: bool
    sprite_ids: tuple[int, ...]

    @property
    def has_nonzero_sprite(self) -> bool:
        return any(sprite_id > 0 for sprite_id in self.sprite_ids)


@dataclass
class FindingCollector:
    limit: int

    def __post_init__(self) -> None:
        if not isinstance(self.limit, int) or isinstance(self.limit, bool) or not 1 <= self.limit <= MAX_SAMPLE_LIMIT:
            raise GeometryAuditError(f"sample_limit must be in 1..{MAX_SAMPLE_LIMIT}")
        self.samples: list[dict[str, Any]] = []
        self.total = 0
        self.kind_counts: Counter[str] = Counter()
        self.severity_counts: Counter[str] = Counter()
        self.confidence_counts: Counter[str] = Counter()

    def add(
        self,
        kind: str,
        severity: str,
        confidence: str,
        message: str,
        *,
        position: Position | None = None,
        **details: Any,
    ) -> str:
        if severity not in SEVERITY_ORDER:
            raise GeometryAuditError(f"Unsupported severity: {severity}")
        if confidence not in CONFIDENCE_ORDER:
            raise GeometryAuditError(f"Unsupported confidence: {confidence}")
        if not kind or len(kind) > 120:
            raise GeometryAuditError("Finding kind must be a bounded non-empty string")
        identity: dict[str, Any] = {"kind": kind, "position": list(position) if position else None, "details": details}
        finding_id = hashlib.sha256(
            json.dumps(identity, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        ).hexdigest()[:24]
        self.total += 1
        self.kind_counts[kind] += 1
        self.severity_counts[severity] += 1
        self.confidence_counts[confidence] += 1
        if len(self.samples) < self.limit:
            entry: dict[str, Any] = {
                "id": finding_id,
                "kind": kind,
                "severity": severity,
                "confidence": confidence,
                "message": message,
            }
            if position is not None:
                entry["position"] = list(position)
            entry.update(details)
            self.samples.append(entry)
        return finding_id

    def finish(self) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        self.samples.sort(
            key=lambda entry: (
                SEVERITY_ORDER[entry["severity"]],
                CONFIDENCE_ORDER[entry["confidence"]],
                entry["kind"],
                tuple(entry.get("position", [])),
                entry["id"],
            )
        )
        return self.samples, {
            "total": self.total,
            "byKind": dict(sorted(self.kind_counts.items())),
            "bySeverity": {key: self.severity_counts.get(key, 0) for key in ("error", "warning", "info")},
            "byConfidence": {key: self.confidence_counts.get(key, 0) for key in ("high", "medium", "low")},
            "sampled": len(self.samples),
            "truncated": self.total > len(self.samples),
        }


def sha256_path(path: Path, chunk_size: int = 8 * 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def normalize_bounds(first: Position, second: Position) -> tuple[Position, Position]:
    for label, value in (("region start", first), ("region end", second)):
        if not isinstance(value, tuple) or len(value) != 3:
            raise GeometryAuditError(f"{label} must contain exactly x,y,z")
        if any(not isinstance(part, int) or isinstance(part, bool) for part in value):
            raise GeometryAuditError(f"{label} must contain integers")
    lower: Position = tuple(min(first[i], second[i]) for i in range(3))  # type: ignore[assignment]
    upper: Position = tuple(max(first[i], second[i]) for i in range(3))  # type: ignore[assignment]
    if not (
        0 <= lower[0] <= upper[0] <= 0xFFFF
        and 0 <= lower[1] <= upper[1] <= 0xFFFF
        and 0 <= lower[2] <= upper[2] <= 15
    ):
        raise GeometryAuditError("region is outside the OTBM coordinate range")
    coordinate_count = (upper[0] - lower[0] + 1) * (upper[1] - lower[1] + 1) * (upper[2] - lower[2] + 1)
    if coordinate_count > MAX_REGION_COORDINATES:
        raise GeometryAuditError(
            f"region contains {coordinate_count} coordinates; maximum is {MAX_REGION_COORDINATES}"
        )
    return lower, upper


def in_bounds(position: Position, lower: Position, upper: Position) -> bool:
    return all(lower[index] <= position[index] <= upper[index] for index in range(3))


def touches_boundary(position: Position, lower: Position, upper: Position) -> bool:
    return any(position[index] in (lower[index], upper[index]) for index in range(3))


def resolve_artifact_path(
    artifact_root: Path,
    candidate: Path,
    *,
    label: str,
    require_file: bool = True,
    max_bytes: int | None = None,
) -> Path:
    root = artifact_root.expanduser().resolve()
    raw_path = candidate if candidate.is_absolute() else root / candidate
    raw_path = raw_path.expanduser()
    if raw_path.is_symlink():
        raise GeometryAuditError(f"{label} must not be a symlink: {candidate}")
    path = raw_path.resolve()
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise GeometryAuditError(f"{label} escapes artifact_root: {candidate}") from exc
    if require_file and not path.is_file():
        raise FileNotFoundError(path)
    if require_file and max_bytes is not None and path.stat().st_size > max_bytes:
        raise GeometryAuditError(f"{label} exceeds {max_bytes} bytes: {candidate}")
    return path


def load_json(path: Path, *, label: str, max_bytes: int = MAX_JSON_BYTES) -> Any:
    if path.stat().st_size > max_bytes:
        raise GeometryAuditError(f"{label} exceeds {max_bytes} bytes")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise GeometryAuditError(f"Cannot read {label} {path}: {exc}") from exc


def load_rules(path: Path | None) -> tuple[list[AdjacencyRule], dict[str, Any] | None]:
    if path is None:
        return [], None
    document = load_json(path, label="geometry rules", max_bytes=4 * 1024 * 1024)
    if not isinstance(document, dict) or document.get("format") != RULES_FORMAT or document.get("schemaVersion") != 1:
        raise GeometryAuditError(f"Unsupported geometry-rules document: {path}")
    raw_rules = document.get("adjacencyRules")
    if not isinstance(raw_rules, list):
        raise GeometryAuditError("geometry rules must contain adjacencyRules")
    if len(raw_rules) > MAX_RULES:
        raise GeometryAuditError(f"geometry rules contain more than {MAX_RULES} entries")
    result: list[AdjacencyRule] = []
    seen: set[str] = set()
    for raw in raw_rules:
        if not isinstance(raw, dict):
            raise GeometryAuditError("every adjacency rule must be an object")
        rule_id = raw.get("id")
        category = raw.get("category")
        direction = raw.get("direction")
        severity = raw.get("severity", "warning")
        confidence = raw.get("confidence", "high")
        message = raw.get("message", "Reviewed adjacency rule is not satisfied")
        source_ids = raw.get("sourceItemIds")
        neighbor_ids = raw.get("requiredNeighborItemIds")
        if not isinstance(rule_id, str) or not rule_id or len(rule_id) > 160 or rule_id in seen:
            raise GeometryAuditError(f"invalid or duplicate adjacency rule id: {rule_id!r}")
        seen.add(rule_id)
        if category not in ("wall", "border"):
            raise GeometryAuditError(f"rule {rule_id} category must be wall or border")
        if direction not in DIRECTIONS:
            raise GeometryAuditError(f"rule {rule_id} has unsupported direction {direction!r}")
        if severity not in SEVERITY_ORDER or confidence not in CONFIDENCE_ORDER:
            raise GeometryAuditError(f"rule {rule_id} has unsupported severity/confidence")
        if not isinstance(message, str) or not message or len(message) > 500:
            raise GeometryAuditError(f"rule {rule_id} message must be a bounded string")
        source = _item_id_tuple(source_ids, f"rule {rule_id} sourceItemIds")
        neighbors = _item_id_tuple(neighbor_ids, f"rule {rule_id} requiredNeighborItemIds")
        result.append(AdjacencyRule(rule_id, category, source, direction, neighbors, severity, confidence, message))
    result.sort(key=lambda rule: rule.rule_id)
    return result, {
        "path": path.name,
        "size": path.stat().st_size,
        "sha256": sha256_path(path),
        "format": RULES_FORMAT,
        "ruleCount": len(result),
    }


def _item_id_tuple(value: Any, label: str) -> tuple[int, ...]:
    if not isinstance(value, list) or not value:
        raise GeometryAuditError(f"{label} must be a non-empty list")
    if any(not isinstance(item_id, int) or isinstance(item_id, bool) or not 0 <= item_id <= 0xFFFF for item_id in value):
        raise GeometryAuditError(f"{label} must contain item IDs in 0..65535")
    return tuple(sorted(set(int(item_id) for item_id in value)))


def appearance_sprite_evidence(document: Mapping[str, Any]) -> dict[int, AppearanceEvidence]:
    entries = document.get("appearances")
    if not isinstance(entries, list):
        raise GeometryAuditError("appearances document does not contain an appearances list")
    result: dict[int, AppearanceEvidence] = {}
    for entry in entries:
        if not isinstance(entry, dict) or entry.get("category") != "object":
            continue
        item_id = entry.get("id")
        if not isinstance(item_id, int) or isinstance(item_id, bool) or not 0 <= item_id <= 0xFFFF:
            continue
        if item_id in result:
            raise GeometryAuditError(f"duplicate object appearance ID {item_id}")
        flags = entry.get("flags") if isinstance(entry.get("flags"), dict) else {}
        sprite_ids: list[int] = []
        frame_groups = entry.get("frameGroups")
        if isinstance(frame_groups, list):
            for group in frame_groups:
                if not isinstance(group, dict):
                    continue
                info = group.get("spriteInfo")
                if not isinstance(info, dict):
                    continue
                raw_sprites = info.get("spriteIds")
                if isinstance(raw_sprites, list):
                    sprite_ids.extend(
                        int(sprite_id)
                        for sprite_id in raw_sprites
                        if isinstance(sprite_id, int) and not isinstance(sprite_id, bool) and sprite_id >= 0
                    )
        result[item_id] = AppearanceEvidence(
            item_id=item_id,
            ground="bank" in flags,
            unpassable=bool(flags.get("unpassable")),
            sprite_ids=tuple(sprite_ids),
        )
    if not result:
        raise GeometryAuditError("appearances document contains no object appearances")
    return result


def validate_output(path: Path, *, overwrite: bool) -> None:
    if path.is_symlink():
        raise GeometryAuditError(f"output must not be a symlink: {path}")
    if path.exists() and not path.is_file():
        raise GeometryAuditError(f"output path exists but is not a regular file: {path}")
    if path.exists() and not overwrite:
        raise GeometryAuditError(f"output already exists: {path}; pass overwrite=True")
    path.parent.mkdir(parents=True, exist_ok=True)


def write_json_atomic(document: Mapping[str, Any], path: Path, *, overwrite: bool = False) -> None:
    output = path.expanduser().resolve()
    validate_output(output, overwrite=overwrite)
    temporary = output.with_name(f".{output.name}.{os.getpid()}.tmp")
    if temporary.is_symlink():
        raise GeometryAuditError(f"temporary output must not be a symlink: {temporary}")
    temporary.unlink(missing_ok=True)
    try:
        temporary.write_text(
            json.dumps(document, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        os.replace(temporary, output)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def component_bounds(positions: Iterable[Position]) -> tuple[Position, Position]:
    values = tuple(positions)
    if not values:
        raise GeometryAuditError("component must contain at least one position")
    lower: Position = tuple(min(position[index] for position in values) for index in range(3))  # type: ignore[assignment]
    upper: Position = tuple(max(position[index] for position in values) for index in range(3))  # type: ignore[assignment]
    return lower, upper
