#!/usr/bin/env python3
from __future__ import annotations

import unittest
from pathlib import Path

from real_tibia_registry_lib import Registry, load_json
from upstream_intelligence_candidates import map_candidate


class UpstreamIntelligenceProtocolClientTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(__file__).resolve().parents[2]
        cls.registry = Registry.load(cls.root)
        config = load_json(cls.root / "docs/agents/upstream/registry/sources.yaml")
        cls.server_source = next(source for source in config["sources"] if source["id"] == "opentibiabr-canary")
        cls.client_source = next(source for source in config["sources"] if source["id"] == "opentibiabr-otclient")

    @staticmethod
    def candidate(paths: list[str]) -> dict:
        return {
            "paths": paths,
            "module_ids": [],
            "mapped_paths": [],
            "unmapped_paths": [],
            "triage_status": "needs-triage",
            "decision_state": "none",
        }

    def test_server_source_maps_transport_login_compatibility_and_handoff(self) -> None:
        row = self.candidate([
            "src/server/network/connection/connection.cpp",
            "src/server/network/protocol/protocol.cpp",
            "src/server/network/protocol/transport_codec.cpp",
            "src/server/network/protocol/protocollogin.cpp",
            "src/server/network/protocol/protocol_profile.cpp",
            "src/server/network/protocol/protocol_session_hint.cpp",
        ])
        map_candidate(row, self.registry, self.server_source)
        self.assertEqual(row["mapping_state"], "mapped")
        self.assertEqual(row["module_ids"], sorted(row["module_ids"]))
        for expected in (
            "login-protocol",
            "network-transport",
            "protocol",
            "protocol-compatibility",
            "protocol-session-handoff",
        ):
            self.assertIn(expected, row["module_ids"])
        self.assertFalse(any(match["bucket"] == "client" for match in row["mapped_paths"]))
        self.assertEqual(row["unmapped_paths"], [])
        self.assertEqual(row["triage_status"], "needs-triage")
        self.assertEqual(row["decision_state"], "none")
        self.assertEqual(
            row["mapped_paths"],
            sorted(
                row["mapped_paths"],
                key=lambda match: (
                    match["path"],
                    match["module_id"],
                    match["bucket"],
                    match["pattern"],
                ),
            ),
        )

    def test_client_source_maps_only_client_protocol_boundaries(self) -> None:
        row = self.candidate([
            "src/framework/net/protocol.cpp",
            "src/framework/net/connection.cpp",
            "modules/gamelib/protocollogin.lua",
            "modules/game_features/features.lua",
        ])
        map_candidate(row, self.registry, self.client_source)
        self.assertEqual(row["mapping_state"], "mapped")
        self.assertEqual(row["module_ids"], sorted(row["module_ids"]))
        for expected in (
            "login-protocol",
            "network-transport",
            "protocol",
            "protocol-compatibility",
        ):
            self.assertIn(expected, row["module_ids"])
        self.assertNotIn("protocol-session-handoff", row["module_ids"])
        self.assertTrue(all(match["bucket"] == "client" for match in row["mapped_paths"]))
        self.assertEqual(row["unmapped_paths"], [])
        self.assertEqual(row["triage_status"], "needs-triage")
        self.assertEqual(row["decision_state"], "none")


if __name__ == "__main__":
    unittest.main()
