from __future__ import annotations

import json
import re
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "data-otservbr-global/catalog"


def load_json(relative_path: str) -> object:
    return json.loads((CATALOG / relative_path).read_text(encoding="utf-8"))


class DefaultMetadataTest(unittest.TestCase):
    def test_profile_preserves_unknown_content_boundaries(self) -> None:
        profile = load_json("profile.json")
        self.assertEqual("oteryn.game-catalog", profile["contract"])
        self.assertEqual("1.2.0", profile["schema_version"])
        self.assertEqual("15.25", profile["runtime_release"])
        self.assertEqual("15.25", profile["content_target_release"])
        self.assertIsNone(profile["verified_content_through_release"])
        self.assertIsNone(profile["contains_content_through_release"])
        self.assertEqual(100000, profile["loot_roll_maximum"])
        self.assertNotIn("loot_chance_denominator", profile)

        releases = load_json("releases.json")
        self.assertEqual(["15.25"], [release["key"] for release in releases])
        self.assertEqual(152500, releases[0]["release_order"])

        core = (ROOT / "src/core.hpp").read_text(encoding="utf-8")
        self.assertRegex(core, r"\bCLIENT_VERSION\s*=\s*1525\s*;")

    def test_dragon_shield_item_claim_matches_items_xml(self) -> None:
        versioning = load_json("versioning/items.json")["3416"]
        availability = load_json("availability/items.json")["3416"]

        item = next(
            candidate
            for candidate in ET.parse(ROOT / "data/items/items.xml").getroot().iter("item")
            if candidate.get("id") == "3416"
        )
        self.assertEqual("dragon shield", item.get("name"))
        self.assertEqual("item:dragon-shield", versioning["canonical_key"])
        self.assertIsNone(versioning["introduced_in"])
        self.assertIsNone(versioning["removed_in"])
        self.assertEqual("unverified", versioning["completeness"])
        self.assertEqual("obtainable", availability["availability"])
        self.assertIs(True, availability["enabled"])

    def test_dragon_and_loot_claims_match_runtime_sources(self) -> None:
        creature = load_json("versioning/creatures.json")["dragon"]
        creature_availability = load_json("availability/creatures.json")["dragon"]
        loot = load_json("versioning/loot.json")["dragon|3416|20"]

        dragon_source = (
            ROOT / "data-otservbr-global/monster/dragons/dragon.lua"
        ).read_text(encoding="utf-8")
        self.assertIn('Game.createMonsterType("Dragon")', dragon_source)

        loot_source = dragon_source.split("monster.loot = {", maxsplit=1)[1].split(
            "\n}", maxsplit=1
        )[0]
        loot_blocks = re.findall(r"^\s*\{.*\},(?:\s*--.*)?$", loot_source, re.MULTILINE)
        self.assertEqual(21, len(loot_blocks))
        self.assertIn('name = "dragon shield"', loot_blocks[20])
        self.assertIn("chance = 110", loot_blocks[20])

        spawn_root = ET.parse(
            ROOT / "data-otservbr-global/world/otservbr-monster.xml"
        ).getroot()
        self.assertTrue(
            any(
                monster.get("name") == "Dragon"
                for monster in spawn_root.iter("monster")
            )
        )

        self.assertEqual("creature:dragon", creature["canonical_key"])
        self.assertEqual("encounterable", creature_availability["availability"])
        self.assertEqual("loot:dragon:dragon-shield", loot["canonical_key"])
        for record in (creature, loot):
            self.assertIsNone(record["introduced_in"])
            self.assertIsNone(record["removed_in"])
            self.assertEqual("unverified", record["completeness"])


if __name__ == "__main__":
    unittest.main()
