from __future__ import annotations

import json
import os
import tempfile
import unittest
from dataclasses import dataclass
from pathlib import Path

from otbm_spawn_npc_validation import (
    EVIDENCE_FORMAT,
    REPORT_FORMAT,
    SpawnNpcValidationError,
    scan_active_datapack,
    validate_evidence,
    write_json,
)


@dataclass(frozen=True)
class FakeTile:
    x: int
    y: int
    z: int
    kind: str = "tile"


class FakeIndex:
    def __init__(self, positions: list[tuple[int, int, int]]) -> None:
        self.tiles = {position: (index, FakeTile(*position)) for index, position in enumerate(positions)}

    def find_tile(self, position):
        return self.tiles.get(tuple(position))


def reachability(
    lower=(100, 100, 7),
    upper=(110, 110, 7),
    diagnostics=None,
    *,
    truncated=False,
):
    return {
        "format": "canary-otbm-reachability-v1",
        "region": {"from": list(lower), "to": list(upper)},
        "tileDiagnostics": diagnostics or [],
        "tileDiagnosticsTruncated": truncated,
    }


class Phase4Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "data-otservbr-global"
        (self.root / "world").mkdir(parents=True)
        (self.root / "monster" / "demons").mkdir(parents=True)
        (self.root / "npc").mkdir(parents=True)
        (self.root / "scripts" / "quests" / "sample").mkdir(parents=True)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _write_standard_files(self) -> None:
        (self.root / "world" / "otservbr-monster.xml").write_text(
            """<?xml version=\"1.0\"?>
<monsters>
  <monster centerx=\"100\" centery=\"100\" centerz=\"7\" radius=\"2\">
    <monster name=\"Demon\" x=\"1\" y=\"0\" z=\"8\" spawntime=\"90\" />
  </monster>
</monsters>
""",
            encoding="utf-8",
        )
        (self.root / "world" / "otservbr-npc.xml").write_text(
            """<?xml version=\"1.0\"?>
<npcs>
  <npc centerx=\"102\" centery=\"100\" centerz=\"7\" radius=\"1\">
    <npc name=\"Guide\" x=\"0\" y=\"0\" z=\"7\" spawntime=\"60\" />
  </npc>
</npcs>
""",
            encoding="utf-8",
        )
        (self.root / "monster" / "demons" / "demon.lua").write_text(
            'local mType = Game.createMonsterType("Demon")\nmonster.flags = { rewardBoss = true }\n',
            encoding="utf-8",
        )
        (self.root / "npc" / "guide.lua").write_text(
            'local internalNpcName = "Guide"\nlocal npcType = Game.createNpcType(internalNpcName)\n',
            encoding="utf-8",
        )
        (self.root / "scripts" / "quests" / "sample" / "spawn.lua").write_text(
            'Game.createMonster("Demon", Position(101, 100, 7), true, true)\n'
            'Game.createNpc(dynamicName, dynamicPosition)\n',
            encoding="utf-8",
        )

    def _scan(self):
        return scan_active_datapack(
            datapack_root=self.root,
            monster_spawn_files=("world/otservbr-monster.xml",),
            npc_spawn_files=("world/otservbr-npc.xml",),
            sample_limit=200,
        )

    def test_scan_uses_center_z_and_detects_dynamic_overlap(self) -> None:
        self._write_standard_files()
        report = self._scan()
        self.assertEqual(report["format"], EVIDENCE_FORMAT)
        demon = next(entry for entry in report["placements"] if entry["name"] == "Demon")
        self.assertEqual(demon["position"], [101, 100, 7])
        self.assertEqual(demon["childZ"], 8)
        self.assertEqual(report["summary"]["literalDynamicCreations"], 1)
        self.assertEqual(report["summary"]["unresolvedDynamicCreations"], 1)
        codes = report["summary"]["findings"]["byCode"]
        self.assertEqual(codes["child_z_ignored"], 1)
        self.assertEqual(codes["static_dynamic_overlap"], 1)

    def test_npc_definition_variable_is_resolved(self) -> None:
        self._write_standard_files()
        report = self._scan()
        guide = next(entry for entry in report["placements"] if entry["name"] == "Guide")
        self.assertEqual(guide["definitionMatchCount"], 1)
        self.assertEqual(guide["definitionSources"], ["npc/guide.lua"])

    def test_missing_definition_is_error(self) -> None:
        self._write_standard_files()
        (self.root / "monster" / "demons" / "demon.lua").unlink()
        report = self._scan()
        self.assertFalse(report["ok"])
        self.assertEqual(report["summary"]["findings"]["byCode"]["spawn_definition_missing"], 1)

    def test_conflicting_definition_is_error(self) -> None:
        self._write_standard_files()
        (self.root / "monster" / "demons" / "second.lua").write_text(
            'local mType = Game.createMonsterType("demon")\n', encoding="utf-8"
        )
        report = self._scan()
        self.assertFalse(report["ok"])
        self.assertEqual(report["summary"]["findings"]["byCode"]["conflicting_creature_definition"], 1)

    def test_outside_radius_is_error(self) -> None:
        self._write_standard_files()
        monster_xml = self.root / "world" / "otservbr-monster.xml"
        monster_xml.write_text(monster_xml.read_text().replace('x="1"', 'x="3"'), encoding="utf-8")
        report = self._scan()
        self.assertEqual(report["summary"]["findings"]["byCode"]["placement_outside_spawn_radius"], 1)

    def test_npc_invalid_spawntime_is_runtime_rejected(self) -> None:
        self._write_standard_files()
        npc_xml = self.root / "world" / "otservbr-npc.xml"
        npc_xml.write_text(npc_xml.read_text().replace('spawntime="60"', 'spawntime="0"'), encoding="utf-8")
        report = self._scan()
        guide = next(entry for entry in report["placements"] if entry["name"] == "Guide")
        self.assertEqual(guide["spawntimeStatus"], "runtime-rejected")
        self.assertEqual(report["summary"]["findings"]["byCode"]["npc_spawntime_runtime_rejected"], 1)

    def test_dtd_is_rejected(self) -> None:
        self._write_standard_files()
        monster_xml = self.root / "world" / "otservbr-monster.xml"
        monster_xml.write_text('<!DOCTYPE monsters [<!ENTITY x "Demon">]><monsters/>', encoding="utf-8")
        with self.assertRaises(SpawnNpcValidationError):
            self._scan()

    def test_source_escape_is_rejected(self) -> None:
        self._write_standard_files()
        outside = Path(self.temp.name) / "outside.xml"
        outside.write_text("<monsters/>", encoding="utf-8")
        with self.assertRaises(SpawnNpcValidationError):
            scan_active_datapack(
                datapack_root=self.root,
                monster_spawn_files=(outside,),
                npc_spawn_files=(),
            )

    def test_validate_confirmed_and_conditional_positions(self) -> None:
        self._write_standard_files()
        evidence = self._scan()
        index = FakeIndex([(100, 100, 7), (101, 100, 7), (102, 100, 7)])
        phase3 = reachability(
            diagnostics=[
                {
                    "position": [102, 100, 7],
                    "hasGround": True,
                    "strictWalkable": False,
                    "optimisticWalkable": True,
                    "staticBlockers": [],
                    "conditionalBlockers": [999],
                    "unknownAppearances": [],
                    "uncertainties": ["door-state"],
                }
            ]
        )
        report = validate_evidence(
            evidence=evidence,
            world_index=index,
            reachability_report=phase3,
            lower=(100, 100, 7),
            upper=(102, 100, 7),
        )
        self.assertEqual(report["format"], REPORT_FORMAT)
        statuses = {entry["name"]: entry["status"] for entry in report["placements"]}
        self.assertEqual(statuses["Demon"], "confirmed")
        self.assertEqual(statuses["Guide"], "conditional")

    def test_validate_missing_tile_is_error(self) -> None:
        self._write_standard_files()
        evidence = self._scan()
        index = FakeIndex([(100, 100, 7), (102, 100, 7)])
        report = validate_evidence(
            evidence=evidence,
            world_index=index,
            reachability_report=reachability(),
            lower=(100, 100, 7),
            upper=(102, 100, 7),
        )
        demon = next(entry for entry in report["placements"] if entry["name"] == "Demon")
        self.assertEqual(demon["status"], "missing-tile")
        self.assertFalse(report["ok"])

    def test_truncated_phase3_diagnostics_fail_closed(self) -> None:
        self._write_standard_files()
        evidence = self._scan()
        index = FakeIndex([(100, 100, 7), (101, 100, 7), (102, 100, 7)])
        report = validate_evidence(
            evidence=evidence,
            world_index=index,
            reachability_report=reachability(truncated=True),
            lower=(100, 100, 7),
            upper=(102, 100, 7),
        )
        self.assertFalse(report["ok"])
        self.assertEqual(report["summary"]["findings"]["byCode"]["reachability_diagnostics_truncated"], 1)
        self.assertTrue(all(entry["status"] == "unresolved" for entry in report["placements"]))

    def test_region_must_be_covered_by_phase3(self) -> None:
        self._write_standard_files()
        evidence = self._scan()
        with self.assertRaises(SpawnNpcValidationError):
            validate_evidence(
                evidence=evidence,
                world_index=FakeIndex([]),
                reachability_report=reachability(lower=(101, 100, 7), upper=(102, 100, 7)),
                lower=(100, 100, 7),
                upper=(102, 100, 7),
            )

    def test_output_is_atomic_and_refuses_overwrite(self) -> None:
        path = Path(self.temp.name) / "report.json"
        write_json(path, {"format": "x"})
        self.assertEqual(json.loads(path.read_text()), {"format": "x"})
        with self.assertRaises(SpawnNpcValidationError):
            write_json(path, {"format": "y"})
        write_json(path, {"format": "y"}, overwrite=True)
        self.assertEqual(json.loads(path.read_text()), {"format": "y"})

    @unittest.skipUnless(hasattr(os, "symlink"), "symlink unavailable")
    def test_output_symlink_is_rejected(self) -> None:
        target = Path(self.temp.name) / "target.json"
        target.write_text("{}", encoding="utf-8")
        link = Path(self.temp.name) / "link.json"
        link.symlink_to(target)
        with self.assertRaises(SpawnNpcValidationError):
            write_json(link, {"format": "x"}, overwrite=True)


if __name__ == "__main__":
    unittest.main()
