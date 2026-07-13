from __future__ import annotations

import hashlib
import json
import os
import tempfile
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Iterator

from otbm_world_index import MAX_LIMIT, WorldIndex, WorldIndexError

REACHABILITY_FORMAT = "canary-otbm-reachability-v1"
MOVEMENT_CATALOG_FORMAT = "canary-otbm-movement-catalog-v1"
APPEARANCES_INDEX_FORMAT = "canary-appearances-index-v1"
DEFAULT_SAMPLE_LIMIT = 100
MAX_SAMPLE_LIMIT = 10_000
DEFAULT_MAX_NODES = 250_000
MAX_REGION_POSITIONS = 1_000_000
MAX_PATH_SAMPLE = 10_000
CARDINAL_DELTAS = ((-1, 0, 0), (1, 0, 0), (0, -1, 0), (0, 1, 0))


class ReachabilityError(RuntimeError):
    pass


@dataclass(frozen=True)
class Bounds:
    lower: tuple[int, int, int]
    upper: tuple[int, int, int]

    def __post_init__(self) -> None:
        if any(value < 0 for value in (*self.lower, *self.upper)):
            raise ReachabilityError("bounds must be non-negative")
        if self.lower[0] > self.upper[0] or self.lower[1] > self.upper[1] or self.lower[2] > self.upper[2]:
            raise ReachabilityError("lower bounds must not exceed upper bounds")
        if self.upper[0] > 0xFFFF or self.upper[1] > 0xFFFF or self.upper[2] > 15:
            raise ReachabilityError("bounds exceed the OTBM coordinate range")
        if self.position_count > MAX_REGION_POSITIONS:
            raise ReachabilityError(f"bounded region exceeds {MAX_REGION_POSITIONS} coordinate positions")

    @property
    def position_count(self) -> int:
        return (
            (self.upper[0] - self.lower[0] + 1)
            * (self.upper[1] - self.lower[1] + 1)
            * (self.upper[2] - self.lower[2] + 1)
        )

    def contains(self, position: tuple[int, int, int]) -> bool:
        return all(self.lower[index] <= position[index] <= self.upper[index] for index in range(3))

    def to_json(self) -> dict[str, list[int]]:
        return {"from": list(self.lower), "to": list(self.upper)}


@dataclass(frozen=True)
class MovementRule:
    item_id: int
    role: str
    offset: tuple[int, int, int]
    bidirectional: bool = False

    def destination(self, source: tuple[int, int, int]) -> tuple[int, int, int]:
        return tuple(source[index] + self.offset[index] for index in range(3))  # type: ignore[return-value]


@dataclass(frozen=True)
class Transition:
    source: tuple[int, int, int]
    destination: tuple[int, int, int]
    kind: str
    item_id: int
    placement_ordinal: int
    role: str | None = None

    def to_json(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "source": list(self.source),
            "destination": list(self.destination),
            "kind": self.kind,
            "itemId": self.item_id,
            "placementOrdinal": self.placement_ordinal,
        }
        if self.role is not None:
            result["role"] = self.role
        return result


def sha256_path(path: Path, chunk_size: int = 8 * 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def parse_position(value: str) -> tuple[int, int, int]:
    try:
        parts = tuple(int(part.strip()) for part in value.split(","))
    except ValueError as exc:
        raise ReachabilityError(f"invalid position {value!r}") from exc
    if len(parts) != 3:
        raise ReachabilityError(f"position must be x,y,z: {value!r}")
    x, y, z = parts
    if not (0 <= x <= 0xFFFF and 0 <= y <= 0xFFFF and 0 <= z <= 15):
        raise ReachabilityError(f"position is outside the OTBM coordinate range: {value!r}")
    return x, y, z


def _load_json(path: Path) -> dict[str, Any]:
    resolved = path.expanduser().resolve()
    if not resolved.is_file():
        raise FileNotFoundError(resolved)
    try:
        payload = json.loads(resolved.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ReachabilityError(f"cannot read JSON {resolved}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ReachabilityError(f"JSON root must be an object: {resolved}")
    return payload


def load_appearances(path: Path) -> tuple[dict[int, dict[str, Any]], dict[str, Any]]:
    payload = _load_json(path)
    if payload.get("format") != APPEARANCES_INDEX_FORMAT:
        raise ReachabilityError(f"unsupported appearances index format: {payload.get('format')!r}")
    entries = payload.get("appearances")
    if not isinstance(entries, list):
        raise ReachabilityError("appearances index has no appearances list")
    result: dict[int, dict[str, Any]] = {}
    for entry in entries:
        if not isinstance(entry, dict) or entry.get("category") != "object":
            continue
        item_id = entry.get("id")
        if not isinstance(item_id, int) or not 0 <= item_id <= 0xFFFF:
            raise ReachabilityError("appearance object has an invalid ID")
        if item_id in result:
            raise ReachabilityError(f"duplicate object appearance ID {item_id}")
        result[item_id] = entry
    source = payload.get("source") if isinstance(payload.get("source"), dict) else {}
    provenance = {
        "path": str(path.expanduser().resolve()),
        "sha256": sha256_path(path.expanduser().resolve()),
        "source": source,
        "objectCount": len(result),
    }
    return result, provenance


def load_movement_catalog(path: Path | None) -> tuple[dict[int, MovementRule], dict[str, Any] | None]:
    if path is None:
        return {}, None
    payload = _load_json(path)
    if payload.get("format") != MOVEMENT_CATALOG_FORMAT:
        raise ReachabilityError(f"unsupported movement catalogue format: {payload.get('format')!r}")
    entries = payload.get("rules")
    if not isinstance(entries, list):
        raise ReachabilityError("movement catalogue has no rules list")
    rules: dict[int, MovementRule] = {}
    allowed_roles = {"stairs", "ladder", "hole", "rope", "floor-change", "custom"}
    for entry in entries:
        if not isinstance(entry, dict):
            raise ReachabilityError("movement rule must be an object")
        item_id = entry.get("itemId")
        role = entry.get("role")
        offset = entry.get("offset")
        bidirectional = entry.get("bidirectional", False)
        if not isinstance(item_id, int) or not 0 <= item_id <= 0xFFFF:
            raise ReachabilityError("movement rule itemId must be in 0..65535")
        if not isinstance(role, str) or role not in allowed_roles:
            raise ReachabilityError(f"unsupported movement role for item {item_id}: {role!r}")
        if (
            not isinstance(offset, list)
            or len(offset) != 3
            or any(not isinstance(value, int) or isinstance(value, bool) for value in offset)
            or all(value == 0 for value in offset)
        ):
            raise ReachabilityError(f"movement rule {item_id} needs a non-zero integer offset [dx,dy,dz]")
        if abs(offset[0]) > 16 or abs(offset[1]) > 16 or abs(offset[2]) > 15:
            raise ReachabilityError(f"movement rule {item_id} offset exceeds the conservative bound")
        if not isinstance(bidirectional, bool):
            raise ReachabilityError(f"movement rule {item_id} bidirectional must be boolean")
        if item_id in rules:
            raise ReachabilityError(f"duplicate movement rule for item {item_id}")
        rules[item_id] = MovementRule(item_id, role, tuple(offset), bidirectional)  # type: ignore[arg-type]
    return rules, {
        "path": str(path.expanduser().resolve()),
        "sha256": sha256_path(path.expanduser().resolve()),
        "ruleCount": len(rules),
    }


def _bounded_limit(limit: int) -> int:
    if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= MAX_SAMPLE_LIMIT:
        raise ReachabilityError(f"sample limit must be between 1 and {MAX_SAMPLE_LIMIT}")
    return limit


def _flags(appearance: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(appearance, dict):
        return {}
    flags = appearance.get("flags")
    return flags if isinstance(flags, dict) else {}


def tile_evidence(index: Any, appearances: dict[int, dict[str, Any]], position: tuple[int, int, int]) -> dict[str, Any]:
    found = index.find_tile(position)
    if found is None:
        return {
            "position": list(position),
            "exists": False,
            "floor": "absent",
            "walkability": "blocked",
            "reasons": ["missing-tile"],
            "placements": [],
        }
    tile_index, tile = found
    placements = [index.placement(ordinal) for ordinal in range(tile.placement_start, tile.placement_start + tile.placement_count)]
    floor_ids: list[int] = []
    blockers: list[int] = []
    conditional_blockers: list[int] = []
    avoid_ids: list[int] = []
    missing_appearance_ids: list[int] = []
    for placement in placements:
        item_id = placement["itemId"]
        appearance = appearances.get(item_id)
        flags = _flags(appearance)
        if appearance is None:
            missing_appearance_ids.append(item_id)
            continue
        if isinstance(flags.get("bank"), dict):
            floor_ids.append(item_id)
        if flags.get("avoid"):
            avoid_ids.append(item_id)
        if flags.get("unpassable"):
            if any(key in placement for key in ("actionId", "uniqueId", "houseDoorId")):
                conditional_blockers.append(item_id)
            else:
                blockers.append(item_id)
    reasons: list[str] = []
    floor = "confirmed" if floor_ids else ("unresolved" if missing_appearance_ids else "absent")
    if blockers:
        walkability = "blocked"
        reasons.append("static-unpassable-item")
    elif floor == "absent":
        walkability = "blocked"
        reasons.append("missing-floor")
    elif conditional_blockers or avoid_ids:
        walkability = "conditional"
        if conditional_blockers:
            reasons.append("mechanic-controlled-blocker")
        if avoid_ids:
            reasons.append("avoid-item")
    elif missing_appearance_ids or floor == "unresolved":
        walkability = "unresolved"
        reasons.append("missing-appearance-evidence")
    else:
        walkability = "walkable"
    return {
        "position": list(position),
        "exists": True,
        "tileIndex": tile_index,
        "tileKind": tile.kind,
        "houseId": tile.house_id,
        "tileFlags": tile.flags,
        "floor": floor,
        "floorItemIds": sorted(set(floor_ids)),
        "walkability": walkability,
        "reasons": reasons,
        "blockingItemIds": sorted(set(blockers)),
        "conditionalBlockingItemIds": sorted(set(conditional_blockers)),
        "avoidItemIds": sorted(set(avoid_ids)),
        "missingAppearanceItemIds": sorted(set(missing_appearance_ids)),
        "placements": placements,
    }


def iter_transitions(index: Any, movement_rules: dict[int, MovementRule]) -> Iterator[Transition]:
    for mechanic_index in range(index.header.mechanic_count):
        placement_ordinal, mechanic = index.mechanic_record(mechanic_index)
        destination = mechanic.get("teleportDestination")
        if not isinstance(destination, list) or len(destination) != 3:
            continue
        placement = index.placement(placement_ordinal)
        yield Transition(
            source=tuple(placement["position"]),
            destination=tuple(destination),
            kind="teleport",
            item_id=placement["itemId"],
            placement_ordinal=placement_ordinal,
        )
    for item_id, rule in sorted(movement_rules.items()):
        start, count = index.item_directory(item_id)
        for posting in range(start, start + count):
            placement_ordinal = index.posting(posting)
            placement = index.placement(placement_ordinal)
            source = tuple(placement["position"])
            destination = rule.destination(source)
            if not (0 <= destination[0] <= 0xFFFF and 0 <= destination[1] <= 0xFFFF and 0 <= destination[2] <= 15):
                continue
            yield Transition(source, destination, "relative", item_id, placement_ordinal, rule.role)
            if rule.bidirectional:
                yield Transition(destination, source, "relative-reverse", item_id, placement_ordinal, rule.role)


def _adjacent(position: tuple[int, int, int]) -> Iterator[tuple[int, int, int]]:
    for dx, dy, dz in CARDINAL_DELTAS:
        target = position[0] + dx, position[1] + dy, position[2] + dz
        if 0 <= target[0] <= 0xFFFF and 0 <= target[1] <= 0xFFFF:
            yield target


def audit_transitions(
    index: Any,
    appearances: dict[int, dict[str, Any]],
    movement_rules: dict[int, MovementRule],
    *,
    bounds: Bounds | None = None,
    sample_limit: int = DEFAULT_SAMPLE_LIMIT,
) -> dict[str, Any]:
    sample_limit = _bounded_limit(sample_limit)
    transitions = [entry for entry in iter_transitions(index, movement_rules) if bounds is None or bounds.contains(entry.source)]
    transition_pairs = {(entry.source, entry.destination) for entry in transitions}
    outgoing: dict[tuple[int, int, int], list[Transition]] = {}
    for entry in transitions:
        outgoing.setdefault(entry.source, []).append(entry)
    counts = {
        "confirmed": 0,
        "conditional": 0,
        "unresolved": 0,
        "invalid": 0,
        "selfLoop": 0,
        "reversePaired": 0,
        "oneWay": 0,
        "deadEnd": 0,
    }
    findings: list[dict[str, Any]] = []
    for transition in transitions:
        destination = tile_evidence(index, appearances, transition.destination)
        source = tile_evidence(index, appearances, transition.source)
        codes: list[str] = []
        if transition.destination == (0, 0, 0):
            status = "invalid"
            codes.append("zero-destination")
        elif transition.source == transition.destination:
            status = "invalid"
            codes.append("self-loop")
            counts["selfLoop"] += 1
        elif not destination["exists"]:
            status = "invalid"
            codes.append("missing-destination-tile")
        elif destination["floor"] == "absent":
            status = "invalid"
            codes.append("missing-destination-floor")
        elif destination["walkability"] == "blocked":
            status = "invalid"
            codes.append("blocked-destination")
        elif destination["walkability"] == "conditional" or source["walkability"] == "conditional":
            status = "conditional"
            codes.append("dynamic-or-mechanic-state")
        elif destination["walkability"] == "unresolved" or source["walkability"] == "unresolved":
            status = "unresolved"
            codes.append("insufficient-walkability-evidence")
        else:
            status = "confirmed"
        reverse_paired = (transition.destination, transition.source) in transition_pairs
        if reverse_paired:
            counts["reversePaired"] += 1
        else:
            counts["oneWay"] += 1
        dead_end = False
        if destination["exists"] and destination["walkability"] != "blocked":
            cardinal_exit = any(
                tile_evidence(index, appearances, neighbor)["walkability"] in {"walkable", "conditional", "unresolved"}
                for neighbor in _adjacent(transition.destination)
            )
            dead_end = not cardinal_exit and not outgoing.get(transition.destination)
            if dead_end:
                counts["deadEnd"] += 1
                codes.append("destination-dead-end")
                if status == "confirmed":
                    status = "conditional"
        counts[status] += 1
        findings.append(
            {
                "status": status,
                "codes": codes,
                "transition": transition.to_json(),
                "reversePaired": reverse_paired,
                "oneWay": not reverse_paired,
                "deadEnd": dead_end,
                "sourceEvidence": source,
                "destinationEvidence": destination,
            }
        )
    findings.sort(
        key=lambda entry: (
            entry["transition"]["source"][2],
            entry["transition"]["source"][1],
            entry["transition"]["source"][0],
            entry["transition"]["placementOrdinal"],
            entry["transition"]["destination"],
        )
    )
    return {
        "totalCount": len(findings),
        "sampleLimit": sample_limit,
        "truncated": len(findings) > sample_limit,
        "counts": counts,
        "findings": findings[:sample_limit],
    }


def _bfs(
    nodes: dict[tuple[int, int, int], str],
    transitions: dict[tuple[int, int, int], list[tuple[int, int, int]]],
    start: tuple[int, int, int],
    goal: tuple[int, int, int],
    allowed: set[str],
) -> list[tuple[int, int, int]] | None:
    if nodes.get(start) not in allowed or nodes.get(goal) not in allowed:
        return None
    queue: deque[tuple[int, int, int]] = deque([start])
    previous: dict[tuple[int, int, int], tuple[int, int, int] | None] = {start: None}
    while queue:
        current = queue.popleft()
        if current == goal:
            path: list[tuple[int, int, int]] = []
            cursor: tuple[int, int, int] | None = current
            while cursor is not None:
                path.append(cursor)
                cursor = previous[cursor]
            path.reverse()
            return path
        candidates = list(_adjacent(current))
        candidates.extend(transitions.get(current, []))
        for candidate in candidates:
            if candidate in previous or nodes.get(candidate) not in allowed:
                continue
            previous[candidate] = current
            queue.append(candidate)
    return None


def validate_route(
    index: Any,
    appearances: dict[int, dict[str, Any]],
    movement_rules: dict[int, MovementRule],
    *,
    bounds: Bounds,
    start: tuple[int, int, int],
    goal: tuple[int, int, int],
    max_nodes: int = DEFAULT_MAX_NODES,
) -> dict[str, Any]:
    if not bounds.contains(start) or not bounds.contains(goal):
        raise ReachabilityError("start and goal must be inside the explicit bounds")
    if not isinstance(max_nodes, int) or isinstance(max_nodes, bool) or not 1 <= max_nodes <= MAX_REGION_POSITIONS:
        raise ReachabilityError(f"max_nodes must be between 1 and {MAX_REGION_POSITIONS}")
    nodes: dict[tuple[int, int, int], str] = {}
    evidence: dict[tuple[int, int, int], dict[str, Any]] = {}
    for _, tile in index.iter_region_tiles(bounds.lower, bounds.upper):
        position = (tile.x, tile.y, tile.z)
        entry = tile_evidence(index, appearances, position)
        evidence[position] = entry
        nodes[position] = entry["walkability"]
        if len(nodes) > max_nodes:
            raise ReachabilityError(f"region contains more than max_nodes={max_nodes} indexed tiles")
    start_evidence = evidence.get(start) or tile_evidence(index, appearances, start)
    goal_evidence = evidence.get(goal) or tile_evidence(index, appearances, goal)
    transition_map: dict[tuple[int, int, int], list[tuple[int, int, int]]] = {}
    transition_count = 0
    for transition in iter_transitions(index, movement_rules):
        if bounds.contains(transition.source) and bounds.contains(transition.destination):
            transition_map.setdefault(transition.source, []).append(transition.destination)
            transition_count += 1
    for destinations in transition_map.values():
        destinations.sort(key=lambda position: (position[2], position[1], position[0]))
    definite_path = _bfs(nodes, transition_map, start, goal, {"walkable"})
    permissive_path = definite_path or _bfs(nodes, transition_map, start, goal, {"walkable", "conditional", "unresolved"})
    if definite_path is not None:
        status = "confirmed"
        selected = definite_path
        reason = "definite-walkable-path"
    elif permissive_path is not None:
        status = "unresolved"
        selected = permissive_path
        reason = "path-requires-conditional-or-unresolved-tiles"
    else:
        status = "unreachable"
        selected = None
        reason = "no-path-in-definite-or-permissive-graph"
    sampled = selected[:MAX_PATH_SAMPLE] if selected else []
    conditional_positions = []
    if selected:
        conditional_positions = [list(position) for position in selected if nodes.get(position) in {"conditional", "unresolved"}]
    return {
        "status": status,
        "reason": reason,
        "bounds": bounds.to_json(),
        "start": list(start),
        "goal": list(goal),
        "startEvidence": start_evidence,
        "goalEvidence": goal_evidence,
        "indexedNodeCount": len(nodes),
        "transitionEdgeCount": transition_count,
        "pathLength": None if selected is None else max(0, len(selected) - 1),
        "pathTruncated": bool(selected and len(selected) > MAX_PATH_SAMPLE),
        "path": [list(position) for position in sampled],
        "conditionalPathPositions": conditional_positions[:MAX_PATH_SAMPLE],
    }


def build_report(
    index_path: Path,
    appearances_path: Path,
    *,
    movement_catalog_path: Path | None = None,
    bounds: Bounds | None = None,
    start: tuple[int, int, int] | None = None,
    goal: tuple[int, int, int] | None = None,
    sample_limit: int = DEFAULT_SAMPLE_LIMIT,
    max_nodes: int = DEFAULT_MAX_NODES,
) -> dict[str, Any]:
    appearances, appearances_provenance = load_appearances(appearances_path)
    movement_rules, movement_provenance = load_movement_catalog(movement_catalog_path)
    index_resolved = index_path.expanduser().resolve()
    with WorldIndex(index_resolved) as index:
        transition_audit = audit_transitions(
            index,
            appearances,
            movement_rules,
            bounds=bounds,
            sample_limit=sample_limit,
        )
        route = None
        if (start is None) != (goal is None):
            raise ReachabilityError("start and goal must be provided together")
        if start is not None and goal is not None:
            if bounds is None:
                raise ReachabilityError("route validation requires explicit bounds")
            route = validate_route(
                index,
                appearances,
                movement_rules,
                bounds=bounds,
                start=start,
                goal=goal,
                max_nodes=max_nodes,
            )
        summary = {
            "transitionCount": transition_audit["totalCount"],
            **transition_audit["counts"],
            "routeStatus": route["status"] if route else None,
        }
        index_header = index.header_json()
    return {
        "format": REACHABILITY_FORMAT,
        "schemaVersion": 1,
        "provenance": {
            "worldIndex": {
                "path": str(index_resolved),
                "sha256": sha256_path(index_resolved),
                "header": index_header,
            },
            "appearances": appearances_provenance,
            "movementCatalog": movement_provenance,
        },
        "bounds": bounds.to_json() if bounds else None,
        "summary": summary,
        "transitionAudit": transition_audit,
        "route": route,
        "evidenceBoundary": {
            "dynamicLuaExecuted": False,
            "mapModified": False,
            "appearanceUnpassableIsRuntimeProof": False,
            "unreviewedFloorTransitionsGuessed": False,
        },
    }


def write_json_atomic(path: Path, payload: dict[str, Any], *, overwrite: bool = False) -> None:
    target = path.expanduser().resolve(strict=False)
    if path.is_symlink() or target.is_symlink():
        raise ReachabilityError(f"refusing to write through a symlink: {path}")
    if target.exists() and not overwrite:
        raise FileExistsError(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{target.name}.", suffix=".tmp", dir=target.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, target)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise
