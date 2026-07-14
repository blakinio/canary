from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

PLAN_FORMAT = "canary-otbm-bounded-patch-plan-v1"
RESULT_FORMAT = "canary-otbm-bounded-patch-result-v1"
ANCHOR_FORMAT = "canary-otbm-patch-anchors-v1"
NATIVE_ANCHOR_FORMAT = "canary-otbm-patch-anchors-native-v1"
MAX_REGION_COORDINATES = 1_000_000
SUPPORTED_OPERATIONS = {
    "set-action-id": ("actionId", 0xFFFF, 2),
    "set-unique-id": ("uniqueId", 0xFFFF, 2),
    "set-house-door-id": ("houseDoorId", 0xFF, 1),
    "set-teleport-destination": ("teleportDestination", None, 5),
}
Position = tuple[int, int, int]


class BoundedPatchError(ValueError):
    """Raised when a bounded patch cannot be proven safe."""


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def sha256_file(path: Path, *, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def _mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise BoundedPatchError(f"{label} must be an object")
    return value


def _strict_keys(value: Mapping[str, Any], *, required: set[str], optional: set[str], label: str) -> None:
    missing = sorted(required - value.keys())
    unknown = sorted(value.keys() - required - optional)
    if missing:
        raise BoundedPatchError(f"{label} is missing: {', '.join(missing)}")
    if unknown:
        raise BoundedPatchError(f"{label} has unknown fields: {', '.join(unknown)}")


def _integer(value: Any, label: str, lower: int, upper: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise BoundedPatchError(f"{label} must be an integer")
    if not lower <= value <= upper:
        raise BoundedPatchError(f"{label} must be between {lower} and {upper}")
    return value


def _text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise BoundedPatchError(f"{label} must be a non-empty string")
    return value


def parse_position(value: Any, label: str) -> Position:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)) or len(value) != 3:
        raise BoundedPatchError(f"{label} must contain x,y,z")
    return (
        _integer(value[0], f"{label}[0]", 0, 0xFFFF),
        _integer(value[1], f"{label}[1]", 0, 0xFFFF),
        _integer(value[2], f"{label}[2]", 0, 15),
    )


def encoded_width(value: int) -> int:
    return 2 if value in (0xFD, 0xFE, 0xFF) else 1


def encode_logical_bytes(values: Sequence[int]) -> bytes:
    output = bytearray()
    for value in values:
        _integer(value, "logical byte", 0, 0xFF)
        if encoded_width(value) == 2:
            output.append(0xFD)
        output.append(value)
    return bytes(output)


def value_bytes(kind: str, value: int | Position) -> tuple[int, ...]:
    if kind not in SUPPORTED_OPERATIONS:
        raise BoundedPatchError(f"unsupported operation kind: {kind}")
    _attribute, maximum, logical_size = SUPPORTED_OPERATIONS[kind]
    if kind == "set-teleport-destination":
        x, y, z = parse_position(value, "teleport destination")
        result = (x & 0xFF, x >> 8, y & 0xFF, y >> 8, z)
    else:
        scalar = _integer(value, f"{kind} value", 0, int(maximum))
        result = (scalar & 0xFF,) if logical_size == 1 else (scalar & 0xFF, scalar >> 8)
    if len(result) != logical_size:
        raise AssertionError("logical size mismatch")
    return result


@dataclass(frozen=True)
class SourcePin:
    file_name: str
    sha256: str
    size: int
    otbm_version: int
    items_major: int
    items_minor: int

    @classmethod
    def from_raw(cls, raw: Any) -> "SourcePin":
        value = _mapping(raw, "source")
        _strict_keys(
            value,
            required={"fileName", "sha256", "size", "otbmVersion", "itemsMajor", "itemsMinor"},
            optional=set(),
            label="source",
        )
        sha256 = _text(value["sha256"], "source.sha256")
        if len(sha256) != 64 or any(character not in "0123456789abcdef" for character in sha256):
            raise BoundedPatchError("source.sha256 must be a lowercase SHA-256 hex digest")
        file_name = _text(value["fileName"], "source.fileName")
        if Path(file_name).name != file_name:
            raise BoundedPatchError("source.fileName must be a base name")
        return cls(
            file_name=file_name,
            sha256=sha256,
            size=_integer(value["size"], "source.size", 1, 2**63 - 1),
            otbm_version=_integer(value["otbmVersion"], "source.otbmVersion", 0, 0xFFFFFFFF),
            items_major=_integer(value["itemsMajor"], "source.itemsMajor", 0, 0xFFFFFFFF),
            items_minor=_integer(value["itemsMinor"], "source.itemsMinor", 0, 0xFFFFFFFF),
        )


@dataclass(frozen=True)
class Region:
    lower: Position
    upper: Position

    @classmethod
    def from_raw(cls, raw: Any) -> "Region":
        value = _mapping(raw, "region")
        _strict_keys(value, required={"from", "to"}, optional=set(), label="region")
        first = parse_position(value["from"], "region.from")
        second = parse_position(value["to"], "region.to")
        lower = tuple(min(first[index], second[index]) for index in range(3))
        upper = tuple(max(first[index], second[index]) for index in range(3))
        coordinate_count = (upper[0] - lower[0] + 1) * (upper[1] - lower[1] + 1) * (upper[2] - lower[2] + 1)
        if coordinate_count > MAX_REGION_COORDINATES:
            raise BoundedPatchError(
                f"region covers {coordinate_count} coordinates; limit is {MAX_REGION_COORDINATES}"
            )
        return cls(lower=lower, upper=upper)  # type: ignore[arg-type]

    def contains(self, position: Position) -> bool:
        return all(self.lower[index] <= position[index] <= self.upper[index] for index in range(3))


PatchValue = int | Position


@dataclass(frozen=True)
class PatchOperation:
    operation_id: str
    kind: str
    position: Position
    tile_placement_index: int
    item_id: int
    item_depth: int
    expected: PatchValue
    replacement: PatchValue

    @property
    def attribute(self) -> str:
        return SUPPORTED_OPERATIONS[self.kind][0]

    @classmethod
    def from_raw(cls, raw: Any, index: int) -> "PatchOperation":
        value = _mapping(raw, f"operations[{index}]")
        _strict_keys(
            value,
            required={
                "id",
                "kind",
                "position",
                "tilePlacementIndex",
                "itemId",
                "itemDepth",
                "expected",
                "replacement",
            },
            optional=set(),
            label=f"operations[{index}]",
        )
        kind = _text(value["kind"], f"operations[{index}].kind")
        if kind not in SUPPORTED_OPERATIONS:
            raise BoundedPatchError(f"operations[{index}].kind is unsupported: {kind}")
        if kind == "set-teleport-destination":
            expected: PatchValue = parse_position(value["expected"], f"operations[{index}].expected")
            replacement: PatchValue = parse_position(value["replacement"], f"operations[{index}].replacement")
        else:
            maximum = int(SUPPORTED_OPERATIONS[kind][1])
            expected = _integer(value["expected"], f"operations[{index}].expected", 0, maximum)
            replacement = _integer(value["replacement"], f"operations[{index}].replacement", 0, maximum)
        if expected == replacement:
            raise BoundedPatchError(f"operations[{index}] does not change the value")
        return cls(
            operation_id=_text(value["id"], f"operations[{index}].id"),
            kind=kind,
            position=parse_position(value["position"], f"operations[{index}].position"),
            tile_placement_index=_integer(
                value["tilePlacementIndex"], f"operations[{index}].tilePlacementIndex", 0, 0xFFFFFFFF
            ),
            item_id=_integer(value["itemId"], f"operations[{index}].itemId", 0, 0xFFFF),
            item_depth=_integer(value["itemDepth"], f"operations[{index}].itemDepth", 0, 0x7FFF),
            expected=expected,
            replacement=replacement,
        )

    def identity(self) -> tuple[Any, ...]:
        return (
            self.position,
            self.tile_placement_index,
            self.item_id,
            self.item_depth,
            self.attribute,
        )


@dataclass(frozen=True)
class PatchPlan:
    source: SourcePin
    region: Region
    operations: tuple[PatchOperation, ...]

    @classmethod
    def from_raw(cls, raw: Any) -> "PatchPlan":
        value = _mapping(raw, "plan")
        _strict_keys(value, required={"format", "source", "region", "operations"}, optional=set(), label="plan")
        if value["format"] != PLAN_FORMAT:
            raise BoundedPatchError(f"plan.format must be {PLAN_FORMAT}")
        raw_operations = value["operations"]
        if not isinstance(raw_operations, list) or not raw_operations:
            raise BoundedPatchError("operations must be a non-empty array")
        operations = tuple(PatchOperation.from_raw(entry, index) for index, entry in enumerate(raw_operations))
        ids = [operation.operation_id for operation in operations]
        if len(ids) != len(set(ids)):
            raise BoundedPatchError("operation ids must be unique")
        identities = [operation.identity() for operation in operations]
        if len(identities) != len(set(identities)):
            raise BoundedPatchError("operations must target distinct attributes")
        region = Region.from_raw(value["region"])
        for operation in operations:
            if not region.contains(operation.position):
                raise BoundedPatchError(f"operation {operation.operation_id} is outside the bounded region")
        return cls(source=SourcePin.from_raw(value["source"]), region=region, operations=operations)


def load_plan(path: Path) -> PatchPlan:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise BoundedPatchError(f"invalid plan JSON: {exc}") from exc
    return PatchPlan.from_raw(raw)
