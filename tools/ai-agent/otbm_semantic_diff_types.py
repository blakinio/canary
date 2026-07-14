from __future__ import annotations

import hashlib
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

REPORT_FORMAT = "canary-otbm-semantic-diff-v1"
SCHEMA_VERSION = 1
DEFAULT_SAMPLE_LIMIT = 500
MAX_SAMPLE_LIMIT = 10_000
MAX_INDEX_BYTES = 8 * 1024 * 1024 * 1024
MAX_REPORT_INPUT_BYTES = 128 * 1024 * 1024
MAX_OUTPUT_BYTES = 64 * 1024 * 1024
MAX_CORRELATION_NODES = 1_000_000
MAX_CORRELATION_DEPTH = 32

Position = tuple[int, int, int]
MECHANIC_FIELDS = ("actionId", "uniqueId", "houseDoorId", "teleportDestination")
EVIDENCE_LEVELS = (
    "structural",
    "static",
    "semantic",
    "correlated",
    "regression",
    "runtime",
    "gameplay",
    "factual-visual-evidence",
)
CLASSIFICATIONS = {
    "added",
    "removed",
    "changed",
    "unchanged",
    "walkability-regression",
    "walkability-improvement",
    "handler-affected",
    "quest-evidence-affected",
    "spawn-npc-evidence-affected",
    "storage-evidence-affected",
    "unresolved",
    "conflicting",
    "truncated",
    "invalid-input",
}


class SemanticDiffError(RuntimeError):
    pass


def sha256_path(path: Path, chunk_size: int = 8 * 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def stable_id(kind: str, payload: Mapping[str, Any]) -> str:
    digest = hashlib.sha256((kind + "\n" + canonical_json(payload)).encode("utf-8")).hexdigest()
    return f"otbm-diff:{digest[:24]}"


def normalize_position(value: Any, label: str = "position") -> Position:
    if not isinstance(value, (list, tuple)) or len(value) != 3:
        raise SemanticDiffError(f"{label} must contain exactly x,y,z")
    if any(not isinstance(part, int) or isinstance(part, bool) for part in value):
        raise SemanticDiffError(f"{label} must contain integers")
    x, y, z = (int(part) for part in value)
    if not (0 <= x <= 0xFFFF and 0 <= y <= 0xFFFF and 0 <= z <= 15):
        raise SemanticDiffError(f"{label} is outside the OTBM coordinate range")
    return x, y, z


def normalize_bounds(first: Position, second: Position) -> tuple[Position, Position]:
    first = normalize_position(first, "region start")
    second = normalize_position(second, "region end")
    lower: Position = tuple(min(first[index], second[index]) for index in range(3))  # type: ignore[assignment]
    upper: Position = tuple(max(first[index], second[index]) for index in range(3))  # type: ignore[assignment]
    return lower, upper


def in_bounds(position: Position, bounds: tuple[Position, Position] | None) -> bool:
    if bounds is None:
        return True
    lower, upper = bounds
    return all(lower[index] <= position[index] <= upper[index] for index in range(3))


@dataclass(frozen=True)
class IndexProvenance:
    role: str
    index_path: str
    index_size: int
    index_sha256: str
    format: str
    schema_version: int
    source_path: str
    source_size: int
    source_sha256: str
    scanner_path: str
    scanner_sha256: str
    scanner_build_format: str
    otbm: Mapping[str, Any]
    summary: Mapping[str, Any]

    def to_json(self) -> dict[str, Any]:
        return {
            "role": self.role,
            "worldIndex": {
                "path": self.index_path,
                "size": self.index_size,
                "sha256": self.index_sha256,
                "format": self.format,
                "schemaVersion": self.schema_version,
            },
            "sourceMap": {
                "path": self.source_path,
                "size": self.source_size,
                "sha256": self.source_sha256,
            },
            "scanner": {
                "path": self.scanner_path,
                "sha256": self.scanner_sha256,
                "buildFormat": self.scanner_build_format,
            },
            "otbm": dict(self.otbm),
            "summary": dict(self.summary),
        }


@dataclass(frozen=True)
class TileSnapshot:
    position: Position
    kind: str
    house_id: int | None
    flags: int
    placements: tuple[Mapping[str, Any], ...]
    walkability: Mapping[str, Any] | None

    def tile_json(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "position": list(self.position),
            "kind": self.kind,
            "houseId": self.house_id,
            "flags": self.flags,
            "placementCount": len(self.placements),
        }
        if self.walkability is not None:
            result["walkability"] = dict(self.walkability)
        return result


@dataclass
class FindingCollector:
    sample_limit: int

    def __post_init__(self) -> None:
        if (
            not isinstance(self.sample_limit, int)
            or isinstance(self.sample_limit, bool)
            or not 1 <= self.sample_limit <= MAX_SAMPLE_LIMIT
        ):
            raise SemanticDiffError(f"sample_limit must be in 1..{MAX_SAMPLE_LIMIT}")
        self.total = 0
        self.samples: list[dict[str, Any]] = []
        self.by_kind: Counter[str] = Counter()
        self.by_classification: Counter[str] = Counter()
        self.by_evidence: Counter[str] = Counter()

    def add(
        self,
        *,
        kind: str,
        classifications: list[str] | tuple[str, ...],
        evidence_level: str,
        position: Position | None = None,
        before: Any = None,
        after: Any = None,
        message: str,
        details: Mapping[str, Any] | None = None,
        correlations: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        if evidence_level not in EVIDENCE_LEVELS:
            raise SemanticDiffError(f"Unsupported evidence level: {evidence_level}")
        normalized = sorted(set(classifications))
        unknown = set(normalized) - CLASSIFICATIONS
        if unknown:
            raise SemanticDiffError(f"Unsupported classifications: {sorted(unknown)}")
        output_details = dict(details or {})
        id_details = {
            key: value
            for key, value in output_details.items()
            if key not in {"correlationTotalCount", "correlationsTruncated"}
        }
        id_payload: dict[str, Any] = {
            "position": list(position) if position is not None else None,
            "before": before,
            "after": after,
            "details": id_details,
        }
        finding = {
            "id": stable_id(kind, id_payload),
            "kind": kind,
            "classifications": normalized,
            "evidenceLevel": evidence_level,
            "position": list(position) if position is not None else None,
            "before": before,
            "after": after,
            "details": output_details,
            "message": message,
            "correlations": correlations or [],
        }
        self.total += 1
        self.by_kind[kind] += 1
        self.by_evidence[evidence_level] += 1
        for classification in normalized:
            self.by_classification[classification] += 1
        if len(self.samples) < self.sample_limit:
            self.samples.append(finding)
        return finding

    def finish(self) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        self.samples.sort(
            key=lambda finding: (
                tuple(finding.get("position") or (-1, -1, -1)),
                finding["kind"],
                finding["id"],
            )
        )
        return self.samples, {
            "total": self.total,
            "byKind": dict(sorted(self.by_kind.items())),
            "byClassification": dict(sorted(self.by_classification.items())),
            "byEvidenceLevel": dict(sorted(self.by_evidence.items())),
            "sampleCount": len(self.samples),
            "truncated": self.total > len(self.samples),
        }
