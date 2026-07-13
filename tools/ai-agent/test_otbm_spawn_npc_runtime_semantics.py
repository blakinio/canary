from __future__ import annotations

import tempfile
import unittest
from dataclasses import dataclass
from pathlib import Path

from otbm_spawn_npc import scan_active_datapack, validate_evidence


@dataclass(frozen=True)
class FakeTile:
    kind: str = "tile"


class FakeIndex:
    def find_tile(self, position):
        return 0, FakeTile()


class RuntimeSemanticsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "data-otservbr-global"
        (self.root / "world").mkdir(parents=True)
        (self.root / "monster").mkdir(parents=True)
        (self.root / "npc").mkdir(parents=True)
        (self.root / "scripts").mkdir(parents=True)
        (self.root / "world" / "otservbr-npc.xml").write_text("<npcs/>", encoding="utf-8")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _scan(self):
        return scan_active_datapack(
            datapack_root=self.root,
            monster_spawn_files=("world/otservbr-monster.xml",),
            npc_spawn_files=("world/otservbr-npc.xml",),
            sample_limit=100,
        )

    def _write_two_monsters(self, boss_body: str) -> None:
        (self.root / "world" / "otservbr-monster.xml").write_text(
            """<monsters>
  <monster centerx="100" centery="100" centerz="7" radius="2">
    <monster name="Boss" x="1" y="0" spawntime="90" />
    <monster name="Rat" x="1" y="0" spawntime="60" />
  </monster>
</monsters>
""",
            encoding="utf-8",
        )
        (self.root / "monster" / "boss.lua").write_text(
            'local mType = Game.createMonsterType("Boss")\n' + boss_body + "\n",
            encoding="utf-8",
        )
        (self.root / "monster" / "rat.lua").write_text(
            'local mType = Game.createMonsterType("Rat")\n', encoding="utf-8"
        )

    def test_reward_boss_does_not_define_runtime_spawn_boss(self) -> None:
        self._write_two_monsters("monster.flags = { rewardBoss = true }")
        report = self._scan()
        self.assertNotIn("boss_mixed_in_spawn_block", report["summary"]["findings"]["byCode"])
        boss = next(entry for entry in report["placements"] if entry["name"] == "Boss")
        self.assertTrue(boss["rewardBossLiteral"])
        self.assertFalse(boss["spawnBossLiteral"])

    def test_nonempty_bosstiary_class_defines_runtime_spawn_boss(self) -> None:
        self._write_two_monsters(
            'monster.flags = { rewardBoss = true }\n'
            'monster.Bosstiary = { class = "Archfoe", bossRace = 1 }'
        )
        report = self._scan()
        self.assertEqual(report["summary"]["findings"]["byCode"]["boss_mixed_in_spawn_block"], 1)
        boss = next(entry for entry in report["placements"] if entry["name"] == "Boss")
        self.assertTrue(boss["spawnBossLiteral"])

    def test_large_monster_spawntime_is_rate_dependent(self) -> None:
        (self.root / "world" / "otservbr-monster.xml").write_text(
            """<monsters>
  <monster centerx="100" centery="100" centerz="7" radius="1">
    <monster name="Rat" x="0" y="0" spawntime="100000" />
  </monster>
</monsters>
""",
            encoding="utf-8",
        )
        (self.root / "monster" / "rat.lua").write_text(
            'local mType = Game.createMonsterType("Rat")\n', encoding="utf-8"
        )
        report = self._scan()
        placement = report["placements"][0]
        self.assertEqual(placement["spawntimeStatus"], "rate-dependent")
        self.assertEqual(
            report["summary"]["findings"]["byCode"]["monster_spawntime_rate_dependent"], 1
        )
        self.assertNotIn("monster_spawntime_runtime_clamp", report["summary"]["findings"]["byCode"])

    def test_unpositioned_dynamic_evidence_is_explicitly_global(self) -> None:
        evidence = {
            "format": "canary-otbm-spawn-npc-evidence-v1",
            "definitions": [],
            "placements": [],
            "spawnGroups": [],
            "dynamicCreations": [
                {
                    "kind": "monster",
                    "name": None,
                    "canonicalName": None,
                    "source": "scripts/example.lua",
                    "line": 1,
                    "position": None,
                    "status": "unresolved",
                }
            ],
        }
        phase3 = {
            "format": "canary-otbm-reachability-v1",
            "region": {"from": [100, 100, 7], "to": [100, 100, 7]},
            "tileDiagnostics": [],
            "tileDiagnosticsTruncated": False,
        }
        report = validate_evidence(
            evidence=evidence,
            world_index=FakeIndex(),
            reachability_report=phase3,
            lower=(100, 100, 7),
            upper=(100, 100, 7),
        )
        self.assertEqual(report["summary"]["unpositionedDynamicCreations"], 1)
        self.assertEqual(
            report["policy"]["unpositionedDynamicEvidenceScope"],
            "selected-active-datapack-global",
        )
        self.assertTrue(report["policy"]["boundedDynamicPositionsOnly"])


if __name__ == "__main__":
    unittest.main()
