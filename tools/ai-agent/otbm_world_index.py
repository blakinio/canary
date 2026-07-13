from __future__ import annotations

import hashlib
import json
import mmap
import os
import struct
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator

WORLD_INDEX_MAGIC = b"OTSWIDX1"
WORLD_INDEX_FORMAT = "canary-otbm-world-index-v1"
WORLD_QUERY_FORMAT = "canary-otbm-world-query-v1"
WORLD_BUILD_FORMAT = "canary-otbm-world-index-build-v1"
SCHEMA_VERSION = 1
HEADER_SIZE = 256
ITEM_DIRECTORY_COUNT = 65536
DEFAULT_LIMIT = 100
MAX_LIMIT = 10_000
NO_MECHANIC = 0xFFFFFFFF

ITEM_DIRECTORY_STRUCT = struct.Struct("<QQ")
AREA_STRUCT = struct.Struct("<HHBBHII")
TILE_STRUCT = struct.Struct("<HHBBIIII")
PLACEMENT_STRUCT = struct.Struct("<HHII")
MECHANIC_STRUCT = struct.Struct("<HHHHHHHI")
POSTING_STRUCT = struct.Struct("<I")

MECHANIC_ACTION = 1 << 0
MECHANIC_UNIQUE = 1 << 1
MECHANIC_HOUSE_DOOR = 1 << 2
MECHANIC_TELEPORT = 1 << 3


class WorldIndexError(RuntimeError):
    pass


@dataclass(frozen=True)
class Header:
    file_size: int
    source_map_size: int
    tile_count: int
    placement_count: int
    mechanic_count: int
    area_count: int
    raw_area_count: int
    item_directory_offset: int
    area_directory_offset: int
    area_postings_offset: int
    tile_offset: int
    placement_offset: int
    mechanic_offset: int
    item_postings_offset: int
    item_directory_count: int
    area_directory_count: int
    tile_record_size: int
    placement_record_size: int
    mechanic_record_size: int
    area_record_size: int
    posting_record_size: int
    otbm_version: int
    map_width: int
    map_height: int
    items_major: int
    items_minor: int
    unknown_attribute_tails: int
    max_item_depth: int


@dataclass(frozen=True)
class Area:
    base_x: int
    base_y: int
    z: int
    postings_start: int
    tile_count: int


@dataclass(frozen=True)
class Tile:
    x: int
    y: int
    z: int
    kind: str
    house_id: int | None
    flags: int
    placement_start: int
    placement_count: int

    def to_json(self) -> dict[str, Any]:
        return {
            "position": [self.x, self.y, self.z],
            "kind": self.kind,
            "houseId": self.house_id,
            "flags": self.flags,
            "placementCount": self.placement_count,
        }


def sha256_path(path: Path, chunk_size: int = 8 * 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def _u32(data: mmap.mmap | bytes, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


def _u64(data: mmap.mmap | bytes, offset: int) -> int:
    return struct.unpack_from("<Q", data, offset)[0]


def _parse_header(data: mmap.mmap) -> Header:
    if len(data) < HEADER_SIZE:
        raise WorldIndexError("World index is smaller than its fixed header")
    if data[:8] != WORLD_INDEX_MAGIC:
        raise WorldIndexError(f"Unsupported world-index magic: {bytes(data[:8])!r}")
    version = _u32(data, 8)
    header_size = _u32(data, 12)
    if version != SCHEMA_VERSION or header_size != HEADER_SIZE:
        raise WorldIndexError(f"Unsupported world-index version/header: {version}/{header_size}")
    header = Header(
        file_size=_u64(data, 16),
        source_map_size=_u64(data, 24),
        tile_count=_u64(data, 32),
        placement_count=_u64(data, 40),
        mechanic_count=_u64(data, 48),
        area_count=_u64(data, 56),
        raw_area_count=_u64(data, 64),
        item_directory_offset=_u64(data, 72),
        area_directory_offset=_u64(data, 80),
        area_postings_offset=_u64(data, 88),
        tile_offset=_u64(data, 96),
        placement_offset=_u64(data, 104),
        mechanic_offset=_u64(data, 112),
        item_postings_offset=_u64(data, 120),
        item_directory_count=_u64(data, 128),
        area_directory_count=_u64(data, 136),
        tile_record_size=_u32(data, 144),
        placement_record_size=_u32(data, 148),
        mechanic_record_size=_u32(data, 152),
        area_record_size=_u32(data, 156),
        posting_record_size=_u32(data, 160),
        otbm_version=_u32(data, 164),
        map_width=_u32(data, 168),
        map_height=_u32(data, 172),
        items_major=_u32(data, 176),
        items_minor=_u32(data, 180),
        unknown_attribute_tails=_u64(data, 184),
        max_item_depth=_u32(data, 192),
    )
    expected = {
        "file size": (header.file_size, len(data)),
        "item directory offset": (header.item_directory_offset, HEADER_SIZE),
        "area directory offset": (
            header.area_directory_offset,
            HEADER_SIZE + ITEM_DIRECTORY_COUNT * ITEM_DIRECTORY_STRUCT.size,
        ),
        "area postings offset": (
            header.area_postings_offset,
            header.area_directory_offset + header.area_count * AREA_STRUCT.size,
        ),
        "tile offset": (
            header.tile_offset,
            header.area_postings_offset + header.tile_count * POSTING_STRUCT.size,
        ),
        "placement offset": (
            header.placement_offset,
            header.tile_offset + header.tile_count * TILE_STRUCT.size,
        ),
        "mechanic offset": (
            header.mechanic_offset,
            header.placement_offset + header.placement_count * PLACEMENT_STRUCT.size,
        ),
        "item postings offset": (
            header.item_postings_offset,
            header.mechanic_offset + header.mechanic_count * MECHANIC_STRUCT.size,
        ),
        "calculated file size": (
            header.file_size,
            header.item_postings_offset + header.placement_count * POSTING_STRUCT.size,
        ),
        "item directory count": (header.item_directory_count, ITEM_DIRECTORY_COUNT),
        "area directory count": (header.area_directory_count, header.area_count),
        "tile record size": (header.tile_record_size, TILE_STRUCT.size),
        "placement record size": (header.placement_record_size, PLACEMENT_STRUCT.size),
        "mechanic record size": (header.mechanic_record_size, MECHANIC_STRUCT.size),
        "area record size": (header.area_record_size, AREA_STRUCT.size),
        "posting record size": (header.posting_record_size, POSTING_STRUCT.size),
    }
    for label, (actual, wanted) in expected.items():
        if actual != wanted:
            raise WorldIndexError(f"Invalid world-index {label}: {actual}; expected {wanted}")
    return header


class WorldIndex:
    def __init__(self, path: Path):
        self.path = path.expanduser().resolve()
        if not self.path.is_file():
            raise FileNotFoundError(self.path)
        self._file = self.path.open("rb")
        try:
            self._mmap = mmap.mmap(self._file.fileno(), 0, access=mmap.ACCESS_READ)
            self.header = _parse_header(self._mmap)
            self.areas = self._read_areas()
            self.area_lookup: dict[tuple[int, int, int], Area] = {
                (area.base_x, area.base_y, area.z): area for area in self.areas
            }
            if len(self.area_lookup) != len(self.areas):
                raise WorldIndexError("World-index area directory contains duplicate area keys")
        except Exception:
            self._file.close()
            raise

    def close(self) -> None:
        if hasattr(self, "_mmap"):
            self._mmap.close()
        self._file.close()

    def __enter__(self) -> "WorldIndex":
        return self

    def __exit__(self, exc_type: Any, exc: Any, traceback: Any) -> None:
        self.close()

    def _read_areas(self) -> list[Area]:
        result: list[Area] = []
        previous: tuple[int, int, int] | None = None
        for index in range(self.header.area_count):
            offset = self.header.area_directory_offset + index * AREA_STRUCT.size
            base_x, base_y, z, reserved, reserved2, postings_start, tile_count = AREA_STRUCT.unpack_from(
                self._mmap, offset
            )
            if reserved or reserved2:
                raise WorldIndexError("World-index area record has non-zero reserved fields")
            if postings_start + tile_count > self.header.tile_count:
                raise WorldIndexError("World-index area-posting range escapes the area-postings section")
            key = (z, base_y, base_x)
            if previous is not None and key <= previous:
                raise WorldIndexError("World-index area directory is not strictly sorted")
            previous = key
            result.append(Area(base_x, base_y, z, postings_start, tile_count))
        return result

    def item_directory(self, item_id: int) -> tuple[int, int]:
        if not 0 <= item_id < ITEM_DIRECTORY_COUNT:
            raise WorldIndexError("item_id must be in 0..65535")
        offset = self.header.item_directory_offset + item_id * ITEM_DIRECTORY_STRUCT.size
        start, count = ITEM_DIRECTORY_STRUCT.unpack_from(self._mmap, offset)
        if start + count > self.header.placement_count:
            raise WorldIndexError(f"Item directory entry {item_id} escapes the postings section")
        return start, count

    def tile(self, tile_index: int) -> Tile:
        if not 0 <= tile_index < self.header.tile_count:
            raise WorldIndexError(f"Tile index {tile_index} is outside the world index")
        offset = self.header.tile_offset + tile_index * TILE_STRUCT.size
        x, y, z, kind, house_id, flags, placement_start, placement_count = TILE_STRUCT.unpack_from(self._mmap, offset)
        if kind not in (0, 1):
            raise WorldIndexError(f"Tile {tile_index} has invalid kind {kind}")
        if placement_start + placement_count > self.header.placement_count:
            raise WorldIndexError(f"Tile {tile_index} placement range escapes the placement section")
        return Tile(
            x=x,
            y=y,
            z=z,
            kind="house" if kind else "tile",
            house_id=house_id if kind else None,
            flags=flags,
            placement_start=placement_start,
            placement_count=placement_count,
        )

    def _mechanic(self, mechanic_index: int, expected_placement: int) -> dict[str, Any]:
        if not 0 <= mechanic_index < self.header.mechanic_count:
            raise WorldIndexError(f"Mechanic index {mechanic_index} is outside the world index")
        offset = self.header.mechanic_offset + mechanic_index * MECHANIC_STRUCT.size
        flags, action_id, unique_id, house_door_id, tele_x, tele_y, tele_z, placement_ordinal = MECHANIC_STRUCT.unpack_from(
            self._mmap, offset
        )
        if flags & ~(MECHANIC_ACTION | MECHANIC_UNIQUE | MECHANIC_HOUSE_DOOR | MECHANIC_TELEPORT):
            raise WorldIndexError(f"Mechanic {mechanic_index} has unsupported flags {flags:#x}")
        if placement_ordinal != expected_placement:
            raise WorldIndexError(
                f"Mechanic {mechanic_index} points to placement {placement_ordinal}; expected {expected_placement}"
            )
        result: dict[str, Any] = {"flags": flags, "placementOrdinal": placement_ordinal}
        if flags & MECHANIC_ACTION:
            result["actionId"] = action_id
        if flags & MECHANIC_UNIQUE:
            result["uniqueId"] = unique_id
        if flags & MECHANIC_HOUSE_DOOR:
            if house_door_id > 0xFF:
                raise WorldIndexError(f"Mechanic {mechanic_index} has invalid house-door ID {house_door_id}")
            result["houseDoorId"] = house_door_id
        if flags & MECHANIC_TELEPORT:
            if tele_z > 15:
                raise WorldIndexError(f"Mechanic {mechanic_index} has invalid teleport floor {tele_z}")
            result["teleportDestination"] = [tele_x, tele_y, tele_z]
        return result

    def placement(self, placement_ordinal: int) -> dict[str, Any]:
        if not 0 <= placement_ordinal < self.header.placement_count:
            raise WorldIndexError(f"Placement {placement_ordinal} is outside the world index")
        offset = self.header.placement_offset + placement_ordinal * PLACEMENT_STRUCT.size
        item_id, meta, mechanic_index, tile_index = PLACEMENT_STRUCT.unpack_from(self._mmap, offset)
        tile = self.tile(tile_index)
        node = bool(meta & 0x8000)
        depth = meta & 0x7FFF
        if not node and depth:
            raise WorldIndexError(f"Inline placement {placement_ordinal} has invalid depth metadata")
        if not (tile.placement_start <= placement_ordinal < tile.placement_start + tile.placement_count):
            raise WorldIndexError(f"Placement {placement_ordinal} does not belong to referenced tile {tile_index}")
        result: dict[str, Any] = {
            "placementOrdinal": placement_ordinal,
            "itemId": item_id,
            "position": [tile.x, tile.y, tile.z],
            "itemDepth": depth if node else -1,
            "source": "node" if node else "inline",
            "tileIndex": tile_index,
        }
        if mechanic_index != NO_MECHANIC:
            mechanic = self._mechanic(mechanic_index, placement_ordinal)
            mechanic.pop("flags", None)
            mechanic.pop("placementOrdinal", None)
            result.update(mechanic)
        return result

    def posting(self, posting_index: int) -> int:
        if not 0 <= posting_index < self.header.placement_count:
            raise WorldIndexError(f"Item posting {posting_index} is outside the world index")
        offset = self.header.item_postings_offset + posting_index * POSTING_STRUCT.size
        ordinal = POSTING_STRUCT.unpack_from(self._mmap, offset)[0]
        if ordinal >= self.header.placement_count:
            raise WorldIndexError(f"Item posting {posting_index} points outside placements: {ordinal}")
        return ordinal

    def area_posting(self, posting_index: int) -> int:
        if not 0 <= posting_index < self.header.tile_count:
            raise WorldIndexError(f"Area posting {posting_index} is outside the world index")
        offset = self.header.area_postings_offset + posting_index * POSTING_STRUCT.size
        tile_index = POSTING_STRUCT.unpack_from(self._mmap, offset)[0]
        if tile_index >= self.header.tile_count:
            raise WorldIndexError(f"Area posting {posting_index} points outside tiles: {tile_index}")
        return tile_index

    def mechanic_record(self, mechanic_index: int) -> tuple[int, dict[str, Any]]:
        if not 0 <= mechanic_index < self.header.mechanic_count:
            raise WorldIndexError(f"Mechanic index {mechanic_index} is outside the world index")
        offset = self.header.mechanic_offset + mechanic_index * MECHANIC_STRUCT.size
        _, _, _, _, _, _, _, placement_ordinal = MECHANIC_STRUCT.unpack_from(self._mmap, offset)
        mechanic = self._mechanic(mechanic_index, placement_ordinal)
        return placement_ordinal, mechanic

    def find_tile(self, position: tuple[int, int, int]) -> tuple[int, Tile] | None:
        x, y, z = position
        if not (0 <= x <= 0xFFFF and 0 <= y <= 0xFFFF and 0 <= z <= 15):
            raise WorldIndexError("position is outside the OTBM coordinate range")
        area = self.area_lookup.get((x & 0xFF00, y & 0xFF00, z))
        if area is None:
            return None
        target = (y, x)
        low = area.postings_start
        high = area.postings_start + area.tile_count
        while low < high:
            middle = (low + high) // 2
            tile_index = self.area_posting(middle)
            tile = self.tile(tile_index)
            key = (tile.y, tile.x)
            if key < target:
                low = middle + 1
            else:
                high = middle
        if low >= area.postings_start + area.tile_count:
            return None
        tile_index = self.area_posting(low)
        tile = self.tile(tile_index)
        return (tile_index, tile) if (tile.x, tile.y, tile.z) == position else None

    def iter_region_tiles(
        self,
        lower: tuple[int, int, int],
        upper: tuple[int, int, int],
    ) -> Iterator[tuple[int, Tile]]:
        for area in self.areas:
            if not lower[2] <= area.z <= upper[2]:
                continue
            if area.base_x > upper[0] or area.base_x + 255 < lower[0]:
                continue
            if area.base_y > upper[1] or area.base_y + 255 < lower[1]:
                continue
            for posting_index in range(area.postings_start, area.postings_start + area.tile_count):
                tile_index = self.area_posting(posting_index)
                tile = self.tile(tile_index)
                if lower[0] <= tile.x <= upper[0] and lower[1] <= tile.y <= upper[1]:
                    yield tile_index, tile

    def logical_summary(self) -> dict[str, Any]:
        used_item_ids = 0
        for item_id in range(ITEM_DIRECTORY_COUNT):
            _, count = self.item_directory(item_id)
            if count:
                used_item_ids += 1
        return {
            "tileCount": self.header.tile_count,
            "totalPlacements": self.header.placement_count,
            "mechanicPlacements": self.header.mechanic_count,
            "tileAreaCount": self.header.area_count,
            "rawTileAreaNodes": self.header.raw_area_count,
            "usedItemIds": used_item_ids,
            "unknownAttributeTails": self.header.unknown_attribute_tails,
            "maxItemDepth": self.header.max_item_depth,
        }

    def header_json(self) -> dict[str, Any]:
        return {
            "schemaVersion": SCHEMA_VERSION,
            "sourceMapSize": self.header.source_map_size,
            "otbm": {
                "version": self.header.otbm_version,
                "width": self.header.map_width,
                "height": self.header.map_height,
                "itemsMajor": self.header.items_major,
                "itemsMinor": self.header.items_minor,
            },
            "summary": self.logical_summary(),
            "binary": {
                "fileSize": self.header.file_size,
                "tileRecordSize": self.header.tile_record_size,
                "placementRecordSize": self.header.placement_record_size,
                "mechanicRecordSize": self.header.mechanic_record_size,
                "areaRecordSize": self.header.area_record_size,
                "postingRecordSize": self.header.posting_record_size,
            },
        }


def _bounded_page(limit: int, offset: int) -> tuple[int, int]:
    if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= MAX_LIMIT:
        raise WorldIndexError(f"limit must be between 1 and {MAX_LIMIT}")
    if not isinstance(offset, int) or isinstance(offset, bool) or offset < 0:
        raise WorldIndexError("offset must be non-negative")
    return limit, offset


def _paged_result(query: dict[str, Any], total: int, placements: list[dict[str, Any]], limit: int, offset: int) -> dict[str, Any]:
    return {
        "format": WORLD_QUERY_FORMAT,
        "query": query,
        "totalCount": total,
        "offset": offset,
        "limit": limit,
        "truncated": offset + len(placements) < total,
        "placements": placements,
    }


def index_summary(index_path: Path, manifest_path: Path | None = None) -> dict[str, Any]:
    with WorldIndex(index_path) as index:
        payload = {
            "format": WORLD_INDEX_FORMAT,
            **index.header_json(),
        }
    candidate = manifest_path or index_path.with_suffix(index_path.suffix + ".json")
    if candidate.is_file():
        try:
            manifest = json.loads(candidate.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise WorldIndexError(f"Cannot read world-index manifest {candidate}: {exc}") from exc
        if not isinstance(manifest, dict) or manifest.get("format") != WORLD_INDEX_FORMAT:
            raise WorldIndexError(f"Unsupported world-index manifest: {candidate}")
        payload["manifest"] = manifest
    return payload


def query_item(index_path: Path, item_id: int, *, limit: int = DEFAULT_LIMIT, offset: int = 0) -> dict[str, Any]:
    limit, offset = _bounded_page(limit, offset)
    with WorldIndex(index_path) as index:
        start, total = index.item_directory(item_id)
        available = max(0, min(limit, total - offset))
        placements = [index.placement(index.posting(start + offset + page)) for page in range(available)]
    return _paged_result({"type": "itemId", "value": item_id}, total, placements, limit, offset)


def _query_mechanics(
    index_path: Path,
    *,
    query: dict[str, Any],
    predicate: Any,
    limit: int,
    offset: int,
) -> dict[str, Any]:
    limit, offset = _bounded_page(limit, offset)
    matches: list[int] = []
    with WorldIndex(index_path) as index:
        for mechanic_index in range(index.header.mechanic_count):
            placement_ordinal, mechanic = index.mechanic_record(mechanic_index)
            if predicate(mechanic):
                matches.append(placement_ordinal)
        page = matches[offset : offset + limit]
        placements = [index.placement(ordinal) for ordinal in page]
    return _paged_result(query, len(matches), placements, limit, offset)


def query_action(index_path: Path, action_id: int, *, limit: int = DEFAULT_LIMIT, offset: int = 0) -> dict[str, Any]:
    if not 0 <= action_id <= 0xFFFF:
        raise WorldIndexError("action_id must be in 0..65535")
    return _query_mechanics(
        index_path,
        query={"type": "actionId", "value": action_id},
        predicate=lambda mechanic: mechanic.get("actionId") == action_id,
        limit=limit,
        offset=offset,
    )


def query_unique(index_path: Path, unique_id: int, *, limit: int = DEFAULT_LIMIT, offset: int = 0) -> dict[str, Any]:
    if not 0 <= unique_id <= 0xFFFF:
        raise WorldIndexError("unique_id must be in 0..65535")
    return _query_mechanics(
        index_path,
        query={"type": "uniqueId", "value": unique_id},
        predicate=lambda mechanic: mechanic.get("uniqueId") == unique_id,
        limit=limit,
        offset=offset,
    )


def query_house_door(index_path: Path, house_door_id: int, *, limit: int = DEFAULT_LIMIT, offset: int = 0) -> dict[str, Any]:
    if not 0 <= house_door_id <= 0xFF:
        raise WorldIndexError("house_door_id must be in 0..255")
    return _query_mechanics(
        index_path,
        query={"type": "houseDoorId", "value": house_door_id},
        predicate=lambda mechanic: mechanic.get("houseDoorId") == house_door_id,
        limit=limit,
        offset=offset,
    )


def query_teleport_destination(
    index_path: Path,
    destination: tuple[int, int, int],
    *,
    limit: int = DEFAULT_LIMIT,
    offset: int = 0,
) -> dict[str, Any]:
    x, y, z = destination
    if not (0 <= x <= 0xFFFF and 0 <= y <= 0xFFFF and 0 <= z <= 15):
        raise WorldIndexError("destination is outside the OTBM coordinate range")
    expected = [x, y, z]
    return _query_mechanics(
        index_path,
        query={"type": "teleportDestination", "value": expected},
        predicate=lambda mechanic: mechanic.get("teleportDestination") == expected,
        limit=limit,
        offset=offset,
    )


def query_position(index_path: Path, position: tuple[int, int, int]) -> dict[str, Any]:
    with WorldIndex(index_path) as index:
        found = index.find_tile(position)
        if found is None:
            tile_json = None
            placements: list[dict[str, Any]] = []
        else:
            _, tile = found
            tile_json = tile.to_json()
            placements = [
                index.placement(ordinal)
                for ordinal in range(tile.placement_start, tile.placement_start + tile.placement_count)
            ]
    return {
        "format": WORLD_QUERY_FORMAT,
        "query": {"type": "position", "value": list(position)},
        "tile": tile_json,
        "placements": placements,
    }


def _normalized_bounds(
    first: tuple[int, int, int], second: tuple[int, int, int]
) -> tuple[tuple[int, int, int], tuple[int, int, int]]:
    lower = tuple(min(first[index], second[index]) for index in range(3))
    upper = tuple(max(first[index], second[index]) for index in range(3))
    if not (
        0 <= lower[0] <= upper[0] <= 0xFFFF
        and 0 <= lower[1] <= upper[1] <= 0xFFFF
        and 0 <= lower[2] <= upper[2] <= 15
    ):
        raise WorldIndexError("region is outside the OTBM coordinate range")
    return lower, upper  # type: ignore[return-value]


def query_region(
    index_path: Path,
    first: tuple[int, int, int],
    second: tuple[int, int, int],
    *,
    limit: int = DEFAULT_LIMIT,
    offset: int = 0,
    tile_limit: int | None = None,
    tile_offset: int = 0,
) -> dict[str, Any]:
    limit, offset = _bounded_page(limit, offset)
    tile_limit, tile_offset = _bounded_page(tile_limit or limit, tile_offset)
    lower, upper = _normalized_bounds(first, second)
    placement_total = 0
    tile_total = 0
    placements: list[dict[str, Any]] = []
    tiles: list[dict[str, Any]] = []
    with WorldIndex(index_path) as index:
        for _, tile in index.iter_region_tiles(lower, upper):
            if tile_offset <= tile_total < tile_offset + tile_limit:
                tiles.append(tile.to_json())
            tile_total += 1
            start = tile.placement_start
            end = start + tile.placement_count
            for ordinal in range(start, end):
                if offset <= placement_total < offset + limit:
                    placements.append(index.placement(ordinal))
                placement_total += 1
    return {
        "format": WORLD_QUERY_FORMAT,
        "query": {"type": "region", "from": list(lower), "to": list(upper)},
        "totalCount": placement_total,
        "offset": offset,
        "limit": limit,
        "truncated": offset + len(placements) < placement_total,
        "placements": placements,
        "tileTotalCount": tile_total,
        "tileOffset": tile_offset,
        "tileLimit": tile_limit,
        "tileTruncated": tile_offset + len(tiles) < tile_total,
        "tiles": tiles,
    }


def _validate_output(path: Path, *, overwrite: bool) -> None:
    if path.is_symlink():
        raise WorldIndexError(f"Output must not be a symlink: {path}")
    if path.exists() and not path.is_file():
        raise WorldIndexError(f"Output path exists but is not a regular file: {path}")
    if path.exists() and not overwrite:
        raise WorldIndexError(f"Output already exists: {path}; pass overwrite=True")
    path.parent.mkdir(parents=True, exist_ok=True)


def build_world_index(
    *,
    map_path: Path,
    scanner: Path,
    output: Path,
    manifest_output: Path | None = None,
    overwrite: bool = False,
    timeout_seconds: int = 3600,
) -> dict[str, Any]:
    map_path = map_path.expanduser().resolve()
    scanner = scanner.expanduser().resolve()
    output = output.expanduser().resolve()
    manifest_output = (
        manifest_output.expanduser().resolve()
        if manifest_output is not None
        else output.with_suffix(output.suffix + ".json")
    )
    if not map_path.is_file():
        raise FileNotFoundError(map_path)
    if not scanner.is_file():
        raise FileNotFoundError(scanner)
    if timeout_seconds <= 0:
        raise WorldIndexError("timeout_seconds must be positive")
    _validate_output(output, overwrite=overwrite)
    _validate_output(manifest_output, overwrite=overwrite)

    stat_before = map_path.stat()
    map_sha256 = sha256_path(map_path)
    scanner_sha256 = sha256_path(scanner)
    temporary = output.with_name(f".{output.name}.{os.getpid()}.tmp")
    if temporary.is_symlink():
        raise WorldIndexError(f"Temporary output must not be a symlink: {temporary}")
    temporary.unlink(missing_ok=True)
    try:
        completed = subprocess.run(
            [str(scanner), "--world-index", str(map_path), str(temporary)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_seconds,
            check=False,
            shell=False,
        )
        if completed.returncode != 0:
            detail = completed.stderr.strip() or completed.stdout.strip() or f"exit code {completed.returncode}"
            raise WorldIndexError(f"World-index scanner failed: {detail}")
        try:
            build_report = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            raise WorldIndexError(f"World-index scanner returned invalid JSON: {exc}") from exc
        if not isinstance(build_report, dict) or build_report.get("format") != WORLD_BUILD_FORMAT:
            raise WorldIndexError(f"Unsupported scanner build report: {build_report!r}")
        if not temporary.is_file():
            raise WorldIndexError("World-index scanner did not create its output")

        with WorldIndex(temporary) as index:
            header = index.header_json()
            summary = header["summary"]
        checks = {
            "tileCount": summary["tileCount"],
            "totalPlacements": summary["totalPlacements"],
            "mechanicPlacements": summary["mechanicPlacements"],
            "areaCount": summary["tileAreaCount"],
            "rawAreaCount": summary["rawTileAreaNodes"],
            "uniqueItemIds": summary["usedItemIds"],
            "unknownAttributeTails": summary["unknownAttributeTails"],
            "maxItemDepth": summary["maxItemDepth"],
            "fileSize": header["binary"]["fileSize"],
        }
        for key, value in checks.items():
            if build_report.get(key) != value:
                raise WorldIndexError(
                    f"Scanner report {key}={build_report.get(key)!r}; binary index contains {value!r}"
                )

        stat_after = map_path.stat()
        if stat_before.st_size != stat_after.st_size or stat_before.st_mtime_ns != stat_after.st_mtime_ns:
            raise WorldIndexError("Map changed while the world index was being built")
        if sha256_path(map_path) != map_sha256:
            raise WorldIndexError("Map hash changed while the world index was being built")

        index_sha256 = sha256_path(temporary)
        manifest = {
            "format": WORLD_INDEX_FORMAT,
            "ok": summary["unknownAttributeTails"] == 0,
            "schemaVersion": SCHEMA_VERSION,
            "source": {
                "path": map_path.name,
                "size": stat_before.st_size,
                "sha256": map_sha256,
            },
            "scanner": {
                "path": scanner.name,
                "sha256": scanner_sha256,
                "buildFormat": WORLD_BUILD_FORMAT,
            },
            "index": {
                "path": output.name,
                "size": temporary.stat().st_size,
                "sha256": index_sha256,
                **header["binary"],
            },
            "otbm": header["otbm"],
            "summary": summary,
            "warnings": (
                []
                if summary["unknownAttributeTails"] == 0
                else [
                    {
                        "code": "unknown-attribute-tails",
                        "count": summary["unknownAttributeTails"],
                        "message": "At least one item contains an attribute tail the scanner could not fully decode.",
                    }
                ]
            ),
        }
        os.replace(temporary, output)
        manifest_temp = manifest_output.with_name(f".{manifest_output.name}.{os.getpid()}.tmp")
        manifest_temp.write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        os.replace(manifest_temp, manifest_output)
        return manifest
    except subprocess.TimeoutExpired as exc:
        temporary.unlink(missing_ok=True)
        raise WorldIndexError(f"World-index scanner timed out after {timeout_seconds} seconds") from exc
    except Exception:
        temporary.unlink(missing_ok=True)
        raise
