from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "data-otservbr-global/scripts/quests/the_beginning/the_beginning_tutorial_moveevents.lua"
EXPECTED_HINT_AIDS = {
    50058,
    50059,
    50060,
    50061,
    50062,
    50063,
    50064,
    50065,
    50066,
    50067,
    50068,
    50069,
    50075,
    50076,
    50077,
    50078,
    50079,
    50081,
}
EXPECTED_STOP_AIDS = {50070, 50071, 50072, 50074, 50080, 50088}
EXPECTED_AIDS = EXPECTED_HINT_AIDS | EXPECTED_STOP_AIDS


def parse_aid_registrations(source: str) -> list[set[int]]:
    registrations: list[set[int]] = []
    for match in re.finditer(r"[:.]aid\(([^)]*)\)", source, re.DOTALL):
        registrations.append({int(value) for value in re.findall(r"\b\d+\b", match.group(1))})
    return registrations


class TheBeginningTutorialMoveEventsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = SCRIPT.read_text(encoding="utf-8")

    def test_registers_exact_verified_map_aids(self) -> None:
        registrations = parse_aid_registrations(self.source)
        self.assertEqual(len(registrations), 2)
        self.assertIn(EXPECTED_HINT_AIDS, registrations)
        self.assertIn(EXPECTED_STOP_AIDS, registrations)
        self.assertEqual(set().union(*registrations), EXPECTED_AIDS)
        self.assertNotIn(50073, set().union(*registrations))
        self.assertNotIn(50089, set().union(*registrations))

    def test_uses_current_storage_namespace(self) -> None:
        self.assertIn("Storage.Quest.U8_2.TheBeginningQuest", self.source)
        self.assertNotIn("PlayerStorageKeys", self.source)
        for key in (
            "TutorialHintsStorage",
            "SantiagoNpcGreetStorage",
            "ZirellaNpcGreetStorage",
        ):
            self.assertIn(key, self.source)

    def test_restores_both_stepin_families(self) -> None:
        self.assertEqual(self.source.count("MoveEvent()"), 2)
        self.assertEqual(self.source.count(':type("stepin")'), 2)
        self.assertEqual(self.source.count(":register()"), 2)
        self.assertIn("advanceHint(player, config)", self.source)
        self.assertIn("denyPassage(player, fromPosition", self.source)

    def test_preserves_one_shot_monotonic_hint_progression(self) -> None:
        self.assertRegex(
            self.source,
            r"getStorageValue\(tutorialStorage\.TutorialHintsStorage\) >= config\.storageValue",
        )
        self.assertIn(
            "player:setStorageValue(tutorialStorage.TutorialHintsStorage, config.storageValue)",
            self.source,
        )
        expected_stages = {
            50058: 1,
            50059: 2,
            50060: 3,
            50061: 4,
            50062: 5,
            50063: 6,
            50064: 7,
            50065: 8,
            50067: 10,
            50068: 11,
            50069: 12,
            50066: 13,
            50075: 14,
            50078: 18,
            50079: 20,
        }
        for aid, stage in expected_stages.items():
            pattern = rf"\[{aid}\]\s*=\s*\{{.*?storageValue\s*=\s*{stage}\b"
            self.assertRegex(self.source, re.compile(pattern, re.DOTALL))

    def test_critical_gates_have_current_state_safety(self) -> None:
        self.assertIn("actionId == 50069", self.source)
        self.assertIn("SantiagoNpcGreetStorage) < 6", self.source)
        self.assertIn("actionId == 50078 and currentHint < 19", self.source)
        self.assertIn("player:getItemCount(3457) < 1", self.source)
        self.assertRegex(
            self.source,
            re.compile(r"\[50088\].*?TutorialHintsStorage.*?minimum\s*=\s*20", re.DOTALL),
        )
        self.assertIn("actionId == 50074 and pairedPass[playerId]", self.source)

    def test_does_not_modify_map_or_create_world_items(self) -> None:
        forbidden = (
            "Game.createItem",
            ":transform(",
            ":remove(",
            "setActionId",
            "setUniqueId",
        )
        for token in forbidden:
            self.assertNotIn(token, self.source)


if __name__ == "__main__":
    unittest.main()
