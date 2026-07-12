#!/usr/bin/env python3
"""Shared parsing and validation for Gameplay Analytics named hunt areas.

Used by both validate_gameplay_analytics_hunt_areas.py (checks the shipped Lua config and any
candidate file) and generate_gameplay_analytics_hunt_areas.py (assembles a candidate file into
a Lua snippet). Nothing here invents coordinates: every entry either comes
from the existing `huntAreas` table in
data-otservbr-global/scripts/config/gameplay_analytics.lua, or from a
candidate file an operator fills in after confirming real in-game
coordinates themselves (see docs/systems/gameplay-analytics-hunt-areas.md).
"""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Any

# From src/map/map_const.hpp: MAP_MAX_LAYERS = 16, floors 0-15. x/y are
# transmitted as 16-bit map coordinates, so 0-65535 is the outer bound the
# engine itself can represent - not a guessed play-area size.
MIN_Z, MAX_Z = 0, 15
MIN_XY, MAX_XY = 0, 65535
PLACEHOLDER_NAME = "REPLACE_WITH_REAL_HUNT_NAME"
EXAMPLE_COMMENT_MARKER = "EXAMPLE ONLY"


@dataclass(frozen=True)
class HuntArea:
    name: str
    from_x: int
    from_y: int
    from_z: int
    to_x: int
    to_y: int
    to_z: int
    source: str = ""

    def overlaps(self, other: "HuntArea") -> bool:
        z_overlap = self.from_z <= other.to_z and other.from_z <= self.to_z
        x_overlap = self.from_x <= other.to_x and other.from_x <= self.to_x
        y_overlap = self.from_y <= other.to_y and other.from_y <= self.to_y
        return z_overlap and x_overlap and y_overlap


class HuntAreaError(ValueError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise HuntAreaError(message)


def _coerce_area(raw: dict[str, Any], source: str) -> HuntArea:
    raw_name = raw.get("name")
    _require(isinstance(raw_name, str) and raw_name.strip() != "", f"{source}: hunt area name must be a non-empty string")
    name = raw_name.strip()
    _require(name.casefold() != PLACEHOLDER_NAME.casefold(), f"{source}: replace the placeholder hunt area name before validation")

    for key in ("from", "to"):
        _require(isinstance(raw.get(key), dict), f"{source} ({name}): missing '{key}' coordinates")
        for axis in ("x", "y", "z"):
            _require(isinstance(raw[key].get(axis), int), f"{source} ({name}): '{key}.{axis}' must be an integer")

    area = HuntArea(
        name=name,
        from_x=raw["from"]["x"],
        from_y=raw["from"]["y"],
        from_z=raw["from"]["z"],
        to_x=raw["to"]["x"],
        to_y=raw["to"]["y"],
        to_z=raw["to"]["z"],
        source=source,
    )

    for axis, lo, hi in (("x", area.from_x, area.to_x), ("y", area.from_y, area.to_y), ("z", area.from_z, area.to_z)):
        _require(lo <= hi, f"{source} ({area.name}): from.{axis} ({lo}) must not be greater than to.{axis} ({hi})")

    for axis, values in (("x", (area.from_x, area.to_x)), ("y", (area.from_y, area.to_y))):
        for value in values:
            _require(MIN_XY <= value <= MAX_XY, f"{source} ({area.name}): {axis}={value} is outside the representable map range [{MIN_XY}, {MAX_XY}]")
    for value in (area.from_z, area.to_z):
        _require(MIN_Z <= value <= MAX_Z, f"{source} ({area.name}): z={value} is outside the valid floor range [{MIN_Z}, {MAX_Z}]")

    return area


_BLOCK_START = re.compile(r"huntAreas\s*=\s*\{")
_ENTRY_PATTERN = re.compile(
    r"""
    name\s*=\s*"(?P<name>[^"]*)"\s*,\s*
    from\s*=\s*\{\s*x\s*=\s*(?P<from_x>-?\d+)\s*,\s*y\s*=\s*(?P<from_y>-?\d+)\s*,\s*z\s*=\s*(?P<from_z>-?\d+)\s*,?\s*\}\s*,\s*
    to\s*=\s*\{\s*x\s*=\s*(?P<to_x>-?\d+)\s*,\s*y\s*=\s*(?P<to_y>-?\d+)\s*,\s*z\s*=\s*(?P<to_z>-?\d+)\s*,?\s*\}
    """,
    re.DOTALL | re.VERBOSE,
)


def _extract_block(text: str) -> str:
    match = _BLOCK_START.search(text)
    _require(match is not None, "could not find a 'huntAreas = { ... }' table in the config")
    depth = 1
    index = match.end()
    start = index
    while depth > 0:
        _require(index < len(text), "unterminated 'huntAreas' table (unbalanced braces)")
        char = text[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
        index += 1
    return text[start : index - 1]


def parse_lua_config(text: str, source: str) -> list[HuntArea]:
    block = _extract_block(text)
    areas = []
    for match in _ENTRY_PATTERN.finditer(block):
        raw = {
            "name": match.group("name"),
            "from": {"x": int(match.group("from_x")), "y": int(match.group("from_y")), "z": int(match.group("from_z"))},
            "to": {"x": int(match.group("to_x")), "y": int(match.group("to_y")), "z": int(match.group("to_z"))},
        }
        areas.append(_coerce_area(raw, source))
    return areas


def parse_candidate_file(path: Path) -> list[HuntArea]:
    data = json.loads(path.read_text(encoding="utf-8"))
    _require(isinstance(data, list), f"{path}: candidate file must contain a JSON list of hunt areas")

    areas = []
    for index, entry in enumerate(data):
        source = f"{path}[{index}]"
        _require(isinstance(entry, dict), f"{source}: each candidate must be a JSON object")
        comment = entry.get("_comment")
        _require(
            not (isinstance(comment, str) and EXAMPLE_COMMENT_MARKER.casefold() in comment.casefold()),
            f"{source}: remove the example-only _comment marker before generating",
        )
        areas.append(_coerce_area(entry, source))
    return areas


def validate_areas(areas: list[HuntArea]) -> list[str]:
    """Returns a list of human-readable problems; empty means valid."""
    problems: list[str] = []

    seen_names: dict[str, HuntArea] = {}
    for area in areas:
        key = area.name.strip().lower()
        if key in seen_names:
            problems.append(f"duplicate hunt area name (case-insensitive): '{area.name}' collides with '{seen_names[key].name}'")
        else:
            seen_names[key] = area

    for i, area in enumerate(areas):
        for other in areas[i + 1 :]:
            if area.overlaps(other):
                problems.append(
                    f"overlapping hunt areas: '{area.name}' and '{other.name}' both cover a shared "
                    f"x/y/z region; first-match order (see docs) would make one of them unreachable"
                )

    return problems


def format_lua_table(areas: list[HuntArea]) -> str:
    lines = ["huntAreas = {"]
    for area in areas:
        lines.append("\t{")
        lines.append(f'\t\tname = "{area.name}",')
        lines.append(f"\t\tfrom = {{ x = {area.from_x}, y = {area.from_y}, z = {area.from_z} }},")
        lines.append(f"\t\tto = {{ x = {area.to_x}, y = {area.to_y}, z = {area.to_z} }},")
        lines.append("\t},")
    lines.append("}")
    return "\n".join(lines)
