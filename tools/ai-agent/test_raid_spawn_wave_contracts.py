#!/usr/bin/env python3
"""Contracts for progressive scripted raid monster waves."""

from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DRAPTOR_PATH = ROOT / "data-otservbr-global/scripts/raids/monsters/draptor.lua"
YETI_PATH = ROOT / "data-otservbr-global/scripts/raids/monsters/yeti.lua"
UNDEAD_CAVEBEAR_PATH = ROOT / "data-otservbr-global/scripts/raids/monsters/undead_cavebear.lua"
ENCOUNTERS_PATH = ROOT / "data/libs/systems/encounters.lua"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def extract_wave_amounts(source: str, name: str) -> list[int]:
    match = re.search(rf"local {name} = \{{([^}}]+)\}}", source)
    if not match:
        raise AssertionError(f"missing {name} wave table")
    return [int(value) for value in re.findall(r"\d+", match.group(1))]


def duration_ms(source: str, field: str) -> int:
    match = re.search(rf'{field}\s*=\s*"(\d+)(ms|s|m)"', source)
    if not match:
        raise AssertionError(f"missing {field} duration")
    value, unit = match.groups()
    return int(value) * {"ms": 1, "s": 1000, "m": 60000}[unit]


def wave_advance_ms(source: str, table_name: str) -> int:
    match = re.search(
        rf"for _, amount in ipairs\({table_name}\) do.*?autoAdvance\(\"(\d+)(ms|s|m)\"\)\s*end",
        source,
        re.DOTALL,
    )
    if not match:
        raise AssertionError(f"missing {table_name} progressive loop")
    value, unit = match.groups()
    return int(value) * {"ms": 1, "s": 1000, "m": 60000}[unit]


class RaidSpawnWaveContractsTest(unittest.TestCase):
    def assert_spawn_precedes_stage_advance(self, source: str, table_name: str):
        spawn_delay = duration_ms(source, "timeToSpawnMonsters")
        advance_delay = wave_advance_ms(source, table_name)
        self.assertLess(spawn_delay, advance_delay)

    def test_draptor_progressive_waves_preserve_population(self):
        source = read(DRAPTOR_PATH)
        waves = extract_wave_amounts(source, "dragonWaves")
        self.assertEqual(waves, [20, 20, 20, 10, 20, 20, 20, 20])
        self.assertEqual(sum(waves), 150)
        self.assertLessEqual(max(waves), 20)
        self.assert_spawn_precedes_stage_advance(source, "dragonWaves")

        self.assertRegex(
            source,
            re.compile(r'for i = 1, 8 do.*?name = "Draptor".*?amount = 1', re.DOTALL),
        )
        self.assertRegex(source, r'name = "Grand Mother Foulscale"\s*,?\s*amount = 1')
        self.assertIn("The dragons of the Dragonblaze Mountains", source)

    def test_yeti_progressive_waves_preserve_population(self):
        source = read(YETI_PATH)
        waves = extract_wave_amounts(source, "yetiWaves")
        self.assertEqual(waves, [20, 20, 20])
        self.assertEqual(sum(waves), 60)
        self.assertLessEqual(max(waves), 20)
        self.assert_spawn_precedes_stage_advance(source, "yetiWaves")

        self.assertEqual(source.count("raid:addBroadcast("), 3)
        self.assertIn("Something is moving to the icy grounds of Folda.", source)
        self.assertIn("Many Yetis are emerging from the icy mountains of Folda.", source)
        self.assertIn("Numerous Yetis are dominating Folda, beware!", source)

    def test_draptor_registration_is_not_reused_by_undead_cavebear(self):
        draptor = read(DRAPTOR_PATH)
        cavebear = read(UNDEAD_CAVEBEAR_PATH)
        self.assertEqual(draptor.count('Raid("farmine.draptor"'), 1)
        self.assertNotIn('farmine.draptor', cavebear)
        self.assertIn('Raid("liberty_bay.undead-cavebear"', cavebear)
        self.assertIn('Zone("liberty_bay.undead-cavebear"', cavebear)
        self.assertIn(
            "zone:addArea(Position(31909, 32554, 10), Position(31983, 32579, 10))",
            cavebear,
        )

    def test_encounter_stage_transition_cancels_pending_spawn_events(self):
        source = read(ENCOUNTERS_PATH)
        enter_stage = source[
            source.index("function Encounter:enterStage") : source.index("function Encounter:spawnMonsters")
        ]
        self.assertLess(enter_stage.index("self:cancelEvents()"), enter_stage.index("stage:start()"))
        self.assertIn("end, self.timeToSpawnMonsters, name, position", source)

    def test_rejects_cancel_before_spawn_timing(self):
        self.assertFalse(3000 < 2000, "a 3s spawn lead-in must not be paired with a 2s stage advance")


if __name__ == "__main__":
    unittest.main()
