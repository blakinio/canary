from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WYRDIN_SCRIPT = ROOT / "data-otservbr-global/npc/wyrdin.lua"
ONGULF_SCRIPT = ROOT / "data-otservbr-global/npc/ongulf.lua"


def keyword_branch(source: str, keyword: str) -> str:
    match = re.search(
        rf'\telseif MsgContains\(message, "{re.escape(keyword)}"\)(.*?)(?=\n\telseif|\n\telse)',
        source,
        re.DOTALL,
    )
    if not match:
        raise AssertionError(f"keyword branch {keyword!r} not found")
    return match.group(1)


class TheNewFrontierWyrdinFlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.wyrdin = WYRDIN_SCRIPT.read_text(encoding="utf-8")
        cls.ongulf = ONGULF_SCRIPT.read_text(encoding="utf-8")

    def test_ongulf_assigns_four_wyrdin_keyword_variants(self) -> None:
        self.assertRegex(
            self.ongulf,
            r"Mission05\.WyrdinKeyword,\s*math\.random\(1, 4\)",
        )

    def test_all_four_assigned_keywords_have_bounded_success_paths(self) -> None:
        expected = {
            "plea": 1,
            "bluff": 2,
            "flatter": 3,
            "reason": 4,
        }
        for keyword, variant in expected.items():
            with self.subTest(keyword=keyword):
                branch = keyword_branch(self.wyrdin, keyword)
                self.assertIn(f"Mission05.WyrdinKeyword) == {variant}", branch)
                self.assertIn("Mission05.Wyrdin) == 1", branch)
                self.assertIn("npcHandler:getTopic(playerId) == 2", branch)
                self.assertIn(
                    "player:setStorageValue(TheNewFrontier.Mission05.Wyrdin, 3)",
                    branch,
                )
                self.assertIn("npcHandler:setTopic(playerId, 0)", branch)

    def test_reason_uses_the_fourth_variant_dialogue(self) -> None:
        branch = keyword_branch(self.wyrdin, "reason")
        self.assertIn("new discoveries are made", branch)
        self.assertIn("I think we'll send a representative", branch)

    def test_known_failed_arguments_are_bounded_and_reset_the_topic(self) -> None:
        for keyword in ("impress", "threaten"):
            with self.subTest(keyword=keyword):
                branch = keyword_branch(self.wyrdin, keyword)
                self.assertIn("Mission05.Wyrdin) == 1", branch)
                self.assertIn("npcHandler:getTopic(playerId) == 2", branch)
                self.assertIn(
                    "player:setStorageValue(TheNewFrontier.Mission05.Wyrdin, 2)",
                    branch,
                )
                self.assertIn("npcHandler:setTopic(playerId, 0)", branch)

    def test_unrelated_messages_cannot_fail_the_negotiation_outside_topic_two(self) -> None:
        fallback = re.search(
            r"\n\telse\n(.*?)\n\tend\n\n\treturn true",
            self.wyrdin,
            re.DOTALL,
        )
        self.assertIsNotNone(fallback)
        body = fallback.group(1)
        self.assertIn("TheNewFrontier.Questline) == 14", body)
        self.assertIn("Mission05.Wyrdin) == 1", body)
        self.assertIn("npcHandler:getTopic(playerId) == 2", body)
        self.assertIn(
            "player:setStorageValue(TheNewFrontier.Mission05.Wyrdin, 2)",
            body,
        )
        self.assertIn("npcHandler:setTopic(playerId, 0)", body)

    def test_plea_keeps_only_its_two_authentic_success_responses(self) -> None:
        branch = keyword_branch(self.wyrdin, "plea")
        self.assertIn("math.random(1, 2)", branch)
        self.assertNotIn("math.random(1, 3)", branch)


if __name__ == "__main__":
    unittest.main()
