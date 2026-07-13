from __future__ import annotations

from collections import deque
from typing import Iterator, Mapping, Sequence

from otbm_reachability_types import (
    CARDINAL_STEPS,
    DIAGONAL_STEPS,
    GraphEdge,
    Position,
    TileState,
    TransitionState,
    _in_bounds,
)


def _movement_neighbors(
    position: Position,
    tiles: Mapping[Position, TileState],
    *,
    strict: bool,
    allow_diagonal: bool,
) -> Iterator[Position]:
    walkable = (lambda state: state.strict_walkable) if strict else (lambda state: state.optimistic_walkable)
    for dx, dy, dz in CARDINAL_STEPS:
        candidate = (position[0] + dx, position[1] + dy, position[2] + dz)
        state = tiles.get(candidate)
        if state is not None and walkable(state):
            yield candidate
    if not allow_diagonal:
        return
    for dx, dy, dz in DIAGONAL_STEPS:
        candidate = (position[0] + dx, position[1] + dy, position[2] + dz)
        state = tiles.get(candidate)
        if state is None or not walkable(state):
            continue
        first = tiles.get((position[0] + dx, position[1], position[2]))
        second = tiles.get((position[0], position[1] + dy, position[2]))
        if first is not None and second is not None and walkable(first) and walkable(second):
            yield candidate


def _transition_edges(
    transitions: Sequence[TransitionState], lower: Position, upper: Position, *, strict: bool
) -> dict[Position, list[GraphEdge]]:
    result: dict[Position, list[GraphEdge]] = {}
    for transition in transitions:
        eligible = transition.strict_eligible if strict else transition.optimistic_eligible
        if not eligible:
            continue
        spec = transition.spec
        if _in_bounds(spec.source, lower, upper) and _in_bounds(spec.destination, lower, upper):
            result.setdefault(spec.source, []).append(GraphEdge(spec.destination, spec.transition_id))
            if spec.bidirectional:
                result.setdefault(spec.destination, []).append(GraphEdge(spec.source, spec.transition_id))
    for edges in result.values():
        edges.sort(key=lambda edge: (edge.destination, edge.transition_id or ""))
    return result


def _bfs(
    start: Position,
    tiles: Mapping[Position, TileState],
    transitions: Mapping[Position, Sequence[GraphEdge]],
    *,
    strict: bool,
    allow_diagonal: bool,
) -> tuple[dict[Position, int], dict[Position, tuple[Position, str | None]]]:
    start_state = tiles.get(start)
    if start_state is None or not (start_state.strict_walkable if strict else start_state.optimistic_walkable):
        return {}, {}
    distances = {start: 0}
    previous: dict[Position, tuple[Position, str | None]] = {}
    queue: deque[Position] = deque((start,))
    while queue:
        current = queue.popleft()
        neighbors = [GraphEdge(value, None) for value in _movement_neighbors(
            current, tiles, strict=strict, allow_diagonal=allow_diagonal
        )]
        neighbors.extend(transitions.get(current, ()))
        neighbors.sort(key=lambda edge: (edge.destination, edge.transition_id or ""))
        for edge in neighbors:
            if edge.destination in distances:
                continue
            distances[edge.destination] = distances[current] + 1
            previous[edge.destination] = (current, edge.transition_id)
            queue.append(edge.destination)
    return distances, previous


def _reconstruct_path(
    start: Position,
    goal: Position,
    previous: Mapping[Position, tuple[Position, str | None]],
    *,
    limit: int,
) -> tuple[list[list[int]], list[str], bool]:
    points: list[Position] = [goal]
    transition_ids: list[str] = []
    current = goal
    while current != start:
        parent = previous.get(current)
        if parent is None:
            return [], [], False
        current, transition_id = parent
        points.append(current)
        if transition_id is not None:
            transition_ids.append(transition_id)
    points.reverse()
    transition_ids.reverse()
    truncated = len(points) > limit
    if truncated:
        head = max(1, limit // 2)
        tail = max(0, limit - head)
        points = points[:head] + (points[-tail:] if tail else [])
    return [list(point) for point in points], transition_ids, truncated


def _tarjan_cycles(adjacency: Mapping[Position, Sequence[Position]]) -> list[list[Position]]:
    index_counter = 0
    stack: list[Position] = []
    on_stack: set[Position] = set()
    indices: dict[Position, int] = {}
    lowlinks: dict[Position, int] = {}
    components: list[list[Position]] = []

    def visit(node: Position) -> None:
        nonlocal index_counter
        indices[node] = index_counter
        lowlinks[node] = index_counter
        index_counter += 1
        stack.append(node)
        on_stack.add(node)
        for target in sorted(adjacency.get(node, ())):
            if target not in indices:
                visit(target)
                lowlinks[node] = min(lowlinks[node], lowlinks[target])
            elif target in on_stack:
                lowlinks[node] = min(lowlinks[node], indices[target])
        if lowlinks[node] == indices[node]:
            component: list[Position] = []
            while stack:
                member = stack.pop()
                on_stack.remove(member)
                component.append(member)
                if member == node:
                    break
            has_self_loop = len(component) == 1 and component[0] in adjacency.get(component[0], ())
            if len(component) > 1 or has_self_loop:
                components.append(sorted(component))

    for node in sorted(adjacency):
        if node not in indices:
            visit(node)
    components.sort()
    return components
