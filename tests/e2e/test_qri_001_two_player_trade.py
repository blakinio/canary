from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCENARIO_PATH = REPO_ROOT / "tests" / "e2e" / "scenarios" / "multiclient" / "player-trade-persistence.json"
PRIMARY_PATH = SCENARIO_PATH.parent / "player-trade-persistence" / "primary.lua"
SECONDARY_PATH = SCENARIO_PATH.parent / "player-trade-persistence" / "secondary.lua"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


MULTI_CLIENT = load_module(
    "canary_qri001_multi_client_orchestration",
    REPO_ROOT / "tools" / "e2e" / "multi_client_orchestration.py",
)
PERSISTENCE = load_module(
    "canary_qri001_persistence_assertions",
    REPO_ROOT / "tools" / "e2e" / "persistence_assertions.py",
)


class Qri001TwoPlayerTradeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.scenario = json.loads(SCENARIO_PATH.read_text(encoding="utf-8"))
        cls.primary = PRIMARY_PATH.read_text(encoding="utf-8")
        cls.secondary = SECONDARY_PATH.read_text(encoding="utf-8")

    def test_scenario_reuses_bounded_two_client_contract_with_distinct_actors(self) -> None:
        manifest = {
            "key": "multiclient/player-trade-persistence",
            "scenario": self.scenario,
        }
        with tempfile.TemporaryDirectory() as temporary:
            values = MULTI_CLIENT.compile_secondary(manifest, artifact_dir=Path(temporary))

        self.assertEqual(self.scenario["fixture"]["account"], "@test15")
        self.assertEqual(self.scenario["fixture"]["character"], "Paladin 15")
        self.assertEqual(values["AGENT_E2E_ACTOR_ID"], "trade-b")
        self.assertEqual(values["AGENT_E2E_ACCOUNT"], "@test14")
        self.assertEqual(values["AGENT_E2E_CHARACTER"], "Paladin 14")
        self.assertEqual(values["AGENT_E2E_PRIMARY_CHARACTER"], "Paladin 15")
        self.assertNotIn("AGENT_E2E_PASSWORD", values)

    def test_trade_is_driven_through_real_bilateral_maintained_client_protocol_surface(self) -> None:
        self.assertIn('g_game.talk("/i 3043, 1")', self.primary)
        self.assertIn("g_game.open(backpack, nil)", self.primary)
        self.assertIn("g_game.open(backpack, nil)", self.secondary)
        self.assertIn("g_game.findItemInContainers(RESOURCE_ITEM_ID, -1, 0)", self.primary)
        self.assertIn("g_game.requestTrade(item, peer)", self.primary)
        self.assertIn("g_game.requestTrade(counterItem, primary)", self.secondary)
        self.assertIn('hasEvent(PRIMARY_EVENTS_PATH, "trade_request", "sent")', self.secondary)
        self.assertIn("item:getCount() == 1", self.secondary)
        self.assertIn("g_game.acceptTrade()", self.primary)
        self.assertIn("g_game.acceptTrade()", self.secondary)
        self.assertIn("onOwnTrade", self.primary)
        self.assertIn("onCounterTrade", self.primary)
        self.assertIn("onCloseTrade", self.primary)
        self.assertIn("onOwnTrade", self.secondary)
        self.assertIn("onCounterTrade", self.secondary)
        self.assertIn("onCloseTrade", self.secondary)
        self.assertIn("not ownTradeObserved or not counterTradeObserved", self.secondary)
        self.assertNotIn("Game.createItem", self.primary + self.secondary)
        self.assertNotIn("player:addItem", self.primary + self.secondary)
        self.assertNotIn("mariadb", self.primary + self.secondary)
        self.assertNotIn("io.popen", self.primary + self.secondary)

    def test_fixture_uses_one_tracked_resource_and_existing_count_one_counteroffer(self) -> None:
        self.assertIn("local RESOURCE_ITEM_ID = 3043", self.primary)
        self.assertIn("local RESOURCE_ITEM_ID = 3043", self.secondary)
        self.assertIn('appendEvent("trade_fixture_created", "item-3043")', self.primary)
        self.assertIn('appendEvent("trade_fixture_precondition", "empty")', self.primary)
        self.assertIn('appendEvent("trade_fixture_precondition_secondary", "empty")', self.secondary)
        self.assertIn('appendEvent("trade_counteroffer_secondary", "selected")', self.secondary)
        self.assertIn('appendEvent("trade_counteroffer_item_id", tostring(counterItem:getId()))', self.secondary)
        self.assertIn('appendEvent("trade_request_secondary", "sent")', self.secondary)
        self.assertIn('appendEvent("trade_offer_secondary_own", "observed")', self.secondary)
        self.assertIn('appendEvent("trade_offer_secondary_counter", "observed")', self.secondary)
        self.assertIn('appendEvent("trade_backpack_open_" .. phase, "confirmed")', self.primary)
        self.assertIn('appendEvent("trade_backpack_open_" .. phase, "confirmed")', self.secondary)

    def test_secondary_relog_backpack_open_retries_within_existing_bound(self) -> None:
        self.assertIn("local openAttempts = 0", self.secondary)
        self.assertIn("if phase == 2 and checks % 10 == 0 then", self.secondary)
        self.assertIn('appendEvent("trade_backpack_open_retry_2", tostring(openAttempts))', self.secondary)
        self.assertIn("for _, container in pairs(g_game.getContainers()) do", self.secondary)
        self.assertIn("local checks = 100", self.secondary)

    def test_immediate_and_relog_conservation_markers_are_required(self) -> None:
        required = set(self.scenario["assertions"]["required_markers"])
        expected = {
            "trade_backpack_open_1=confirmed",
            "trade_fixture_created=item-3043",
            "trade_request=sent",
            "trade_offer_primary=observed",
            "trade_offer_secondary=observed",
            "trade_accept_primary=sent",
            "trade_accept_secondary=sent",
            "trade_immediate_primary=0",
            "trade_immediate_secondary=1",
            "trade_immediate_conservation=1",
            "trade_backpack_open_2=confirmed",
            "trade_relog_primary=0",
            "trade_relog_secondary=1",
            "trade_relog_conservation=1",
            "multi_client_secondary_exit=clean",
            "e2e=success",
        }
        self.assertTrue(expected.issubset(required))
        secondary_only = {
            "trade_counteroffer_secondary=selected",
            "trade_request_secondary=sent",
            "trade_offer_secondary_own=observed",
            "trade_offer_secondary_counter=observed",
        }
        self.assertTrue(required.isdisjoint(secondary_only))
        self.assertIn('string.format("%s/session-%d.record", ARTIFACT_DIR, phase)', self.primary)
        self.assertIn('string.format("%s/session-%d.record", ARTIFACT_DIR, phase)', self.secondary)

    def test_persistence_contract_proves_primary_absence_and_cross_actor_conservation(self) -> None:
        persistence = self.scenario["assertions"]["persistence"]
        compiled = PERSISTENCE.compile_persistence_assertions(persistence, character="Paladin 15")
        sql = self.scenario["assertions"]["sql"]

        self.assertEqual(
            persistence,
            {
                "required": True,
                "checks": [
                    {
                        "id": "primary-traded-item-3043-absent",
                        "type": "player_item_presence",
                        "location": "inventory",
                        "item_id": 3043,
                        "present": False,
                    }
                ],
            },
        )
        self.assertEqual(len(compiled), 1)
        self.assertIn("NOT EXISTS", compiled[0])
        self.assertIn("`pi`.`itemtype` = 3043", compiled[0])
        self.assertIn(
            "SELECT COUNT(*) = 0 FROM player_items AS pi INNER JOIN players AS p ON p.id = pi.player_id WHERE p.name = 'Paladin 15' AND pi.itemtype = 3043",
            sql,
        )
        self.assertIn(
            "SELECT COUNT(*) = 1 FROM player_items AS pi INNER JOIN players AS p ON p.id = pi.player_id WHERE p.name = 'Paladin 14' AND pi.itemtype = 3043",
            sql,
        )
        self.assertIn(
            "SELECT COUNT(*) = 1 FROM player_items AS pi INNER JOIN players AS p ON p.id = pi.player_id WHERE p.name IN ('Paladin 15', 'Paladin 14') AND pi.itemtype = 3043",
            sql,
        )
        self.assertIn("SELECT COUNT(*) = 0 FROM players_online", sql)

    def test_failure_evidence_is_actor_and_step_specific(self) -> None:
        for script in (self.primary, self.secondary):
            self.assertIn('appendEvent("failure_actor"', script)
            self.assertIn('appendEvent("failure_client"', script)
            self.assertIn('appendEvent("failure_last_successful_step"', script)
            self.assertIn('appendEvent("failure_first_failed_step"', script)
            self.assertIn('appendEvent("failure_expected"', script)
            self.assertIn('appendEvent("failure_observed"', script)
            self.assertIn('appendEvent("failure_primary_position"', script)
            self.assertIn('appendEvent("failure_secondary_position"', script)

    def test_qri001_does_not_claim_future_result_or_cleanup_contracts(self) -> None:
        serialized = json.dumps(self.scenario, sort_keys=True)
        self.assertNotIn("cleanup_certified", serialized)
        self.assertNotIn("artifact_manifest", serialized)
        self.assertNotIn("first_failure", serialized)


if __name__ == "__main__":
    unittest.main()
