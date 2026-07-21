from __future__ import annotations

import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MONSTER_SPAWNS_PATH = ROOT / "data-otservbr-global" / "world" / "otservbr-monster.xml"
FIXTURE_START = (32369, 32241, 7)


class DeterministicCombatSpawnEvidenceTests(unittest.TestCase):
    def test_report_nearest_current_monster_spawns_to_fixture(self) -> None:
        root = ET.parse(MONSTER_SPAWNS_PATH).getroot()
        candidates: list[tuple[int, str, tuple[int, int, int]]] = []

        for spawn in root.findall("monster"):
            center_x = int(spawn.attrib["centerx"])
            center_y = int(spawn.attrib["centery"])
            center_z = int(spawn.attrib["centerz"])
            for monster in spawn.findall("monster"):
                x = center_x + int(monster.attrib.get("x", "0"))
                y = center_y + int(monster.attrib.get("y", "0"))
                z = int(monster.attrib.get("z", str(center_z)))
                if z != FIXTURE_START[2]:
                    continue
                distance = max(abs(x - FIXTURE_START[0]), abs(y - FIXTURE_START[1]))
                candidates.append((distance, monster.attrib["name"], (x, y, z)))

        nearest = sorted(candidates, key=lambda item: (item[0], item[1], item[2]))[:12]
        self.assertTrue(nearest, "expected current monster spawn evidence on fixture floor")
        self.fail(f"combat spawn evidence probe nearest={nearest!r}")


if __name__ == "__main__":
    unittest.main()
