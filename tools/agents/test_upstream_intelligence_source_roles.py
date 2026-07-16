#!/usr/bin/env python3
from __future__ import annotations

import unittest
from pathlib import Path
from typing import Any

from real_tibia_registry_lib import load_json
from upstream_intelligence_candidates import map_candidate


class FakeRegistry:
    def __init__(self, matches: dict[str, list[tuple[str, str, str]]]) -> None:
        self.matches = matches

    def matched_modules(self, path: str) -> list[tuple[str, str, str]]:
        return list(self.matches.get(path, []))


def source(role: str, buckets: list[str], source_id: str = "test-source") -> dict[str, Any]:
    return {
        "id": source_id,
        "role": role,
        "module_mapping": {"path_buckets": buckets},
    }


def candidate(*paths: str) -> dict[str, Any]:
    return {
        "paths": list(paths),
        "module_ids": [],
        "mapped_paths": [],
        "unmapped_paths": [],
        "triage_status": "needs-triage",
        "decision_state": "none",
    }


class UpstreamIntelligenceSourceRoleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        root = Path(__file__).resolve().parents[2]
        config = load_json(root / "docs/agents/upstream/registry/sources.yaml")
        cls.sources = {row["id"]: row for row in config["sources"]}

    def test_server_roles_exclude_generic_client_bucket(self) -> None:
        registry = FakeRegistry(
            {
                "src/canary_server.cpp": [
                    ("protocol", "client", "src/**"),
                    ("engine-runtime-lifecycle", "server", "src/canary_server.*"),
                ]
            }
        )
        for role in ("upstream-server", "donor-server"):
            with self.subTest(role=role):
                row = candidate("src/canary_server.cpp")
                map_candidate(
                    row,
                    registry,
                    source(role, ["server", "data", "tests", "docs"]),
                )
                self.assertEqual(row["module_ids"], ["engine-runtime-lifecycle"])
                self.assertNotIn("protocol", row["module_ids"])
                self.assertTrue(
                    all(match["bucket"] != "client" for match in row["mapped_paths"])
                )

    def test_upstream_client_excludes_server_bucket(self) -> None:
        registry = FakeRegistry(
            {
                "src/client.cpp": [
                    ("server-runtime", "server", "src/**"),
                    ("protocol", "client", "src/**"),
                ]
            }
        )
        row = candidate("src/client.cpp")
        map_candidate(
            row,
            registry,
            source("upstream-client", ["client", "data", "tests", "docs"]),
        )
        self.assertEqual(row["module_ids"], ["protocol"])
        self.assertFalse(
            any(match["bucket"] == "server" for match in row["mapped_paths"])
        )

    def test_rme_uses_its_explicit_data_tooling_policy(self) -> None:
        registry = FakeRegistry(
            {
                "data/materials.xml": [
                    ("world-data", "data", "data/**"),
                    ("client-assets", "client", "data/**"),
                ],
                "source/map.cpp": [
                    ("server-runtime", "server", "source/**"),
                    ("client-runtime", "client", "source/**"),
                ],
            }
        )
        row = candidate("source/map.cpp", "data/materials.xml")
        map_candidate(row, registry, self.sources["opentibiabr-rme"])
        self.assertEqual(row["module_ids"], ["world-data"])
        self.assertEqual(row["unmapped_paths"], ["source/map.cpp"])
        self.assertEqual(row["mapping_state"], "partial")
        self.assertTrue(
            all(match["bucket"] in {"data", "tests", "docs"} for match in row["mapped_paths"])
        )

    def test_client_editor_uses_separate_client_capable_policy(self) -> None:
        registry = FakeRegistry(
            {
                "src/client_check.cpp": [
                    ("server-runtime", "server", "src/**"),
                    ("protocol", "client", "src/**"),
                ],
                "data/appearances.dat": [
                    ("item-data", "data", "data/**"),
                ],
            }
        )
        row = candidate("data/appearances.dat", "src/client_check.cpp")
        map_candidate(row, registry, self.sources["opentibiabr-client-editor"])
        self.assertEqual(row["module_ids"], ["item-data", "protocol"])
        self.assertFalse(
            any(match["bucket"] == "server" for match in row["mapped_paths"])
        )

    def test_unknown_role_is_explicitly_unmapped_without_state_changes(self) -> None:
        registry = FakeRegistry(
            {"src/unknown.cpp": [("anything", "server", "src/**")]}
        )
        row = candidate("src/unknown.cpp")
        map_candidate(
            row,
            registry,
            source("unsupported", ["server", "client", "data", "tests", "docs"]),
        )
        self.assertEqual(row["mapping_state"], "unmapped")
        self.assertEqual(row["module_ids"], [])
        self.assertEqual(row["mapped_paths"], [])
        self.assertEqual(row["unmapped_paths"], ["src/unknown.cpp"])
        self.assertEqual(row["triage_status"], "needs-triage")
        self.assertEqual(row["decision_state"], "none")

    def test_missing_source_record_does_not_fall_back_to_all_buckets(self) -> None:
        registry = FakeRegistry(
            {"src/missing.cpp": [("anything", "client", "src/**")]}
        )
        row = candidate("src/missing.cpp")
        map_candidate(row, registry, None)
        self.assertEqual(row["mapping_state"], "unmapped")
        self.assertEqual(row["unmapped_paths"], ["src/missing.cpp"])
        self.assertEqual(row["module_ids"], [])

    def test_multiple_allowed_matches_and_outputs_are_deterministically_sorted(self) -> None:
        registry = FakeRegistry(
            {
                "src/z.cpp": [
                    ("zeta", "server", "src/**"),
                    ("alpha", "server", "src/**"),
                    ("protocol", "client", "src/**"),
                ],
                "src/a.cpp": [
                    ("beta", "server", "src/**"),
                    ("alpha", "server", "src/**"),
                ],
                "unknown/file": [],
            }
        )
        row = candidate("src/z.cpp", "unknown/file", "src/a.cpp")
        map_candidate(
            row,
            registry,
            source("upstream-server", ["server", "data", "tests", "docs"]),
        )
        self.assertEqual(row["module_ids"], ["alpha", "beta", "zeta"])
        self.assertEqual(row["unmapped_paths"], ["unknown/file"])
        self.assertEqual(row["mapping_state"], "partial")
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
        self.assertEqual(row["triage_status"], "needs-triage")
        self.assertEqual(row["decision_state"], "none")


if __name__ == "__main__":
    unittest.main()
