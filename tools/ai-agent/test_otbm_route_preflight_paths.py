from __future__ import annotations

import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from otbm_route_preflight import preflight_index_paths


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _rehash(plan: dict) -> dict:
    plan = copy.deepcopy(plan)
    plan.pop("planHashSha256", None)
    payload = json.dumps(plan, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    plan["planHashSha256"] = hashlib.sha256(payload).hexdigest()
    return plan


def _plan(map_sha: str, index_sha: str, appearances_sha: str) -> dict:
    return _rehash(
        {
            "format": "canary-otbm-e2e-route-plan-v1",
            "schemaVersion": 1,
            "provenance": {
                "map": {"sha256": map_sha},
                "worldIndex": {"sha256": index_sha},
                "appearances": {"sha256": appearances_sha},
                "transitionManifest": None,
                "scriptResolution": None,
                "interactionRegistry": None,
            },
            "inputHashSha256": "1" * 64,
            "origin": [10, 10, 7],
            "destination": [11, 10, 7],
            "routingBounds": {"from": [10, 10, 7], "to": [11, 10, 7]},
            "routingOptions": {
                "allowDiagonal": False,
                "diagonalCornerCutting": False,
                "maxExecutablePositions": 10,
                "interactionAware": False,
            },
            "routeStatus": "confirmed",
            "executionStatus": "executable",
            "routingMode": "strict",
            "distance": 1,
            "strictDistance": 1,
            "optimisticDistance": 1,
            "executableDistance": None,
            "pathComplete": True,
            "path": [[10, 10, 7], [11, 10, 7]],
            "edges": [
                {
                    "from": [10, 10, 7],
                    "to": [11, 10, 7],
                    "kind": "movement",
                    "isTransition": False,
                    "transitionId": None,
                    "evidence": {
                        "source": "reachability-bfs-predecessor",
                        "edgeSource": "_movement_neighbors",
                        "routingMode": "strict",
                    },
                }
            ],
            "blockers": [],
        }
    )


class RoutePreflightPathIntegrationTests(unittest.TestCase):
    def test_path_preflight_reuses_canonical_route_exporter(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            map_path = root / "map.otbm"
            index_path = root / "map.widx"
            appearances_path = root / "appearances.json"
            manifest_path = root / "map.widx.json"
            route_path = root / "route.json"

            map_bytes = b"runtime-map-fixture"
            index_bytes = b"world-index-fixture"
            appearances_bytes = b"appearances-fixture"
            map_path.write_bytes(map_bytes)
            index_path.write_bytes(index_bytes)
            appearances_path.write_bytes(appearances_bytes)
            manifest_path.write_text("{}\n", encoding="utf-8")

            plan = _plan(_sha(map_bytes), _sha(index_bytes), _sha(appearances_bytes))
            route_path.write_text(json.dumps(plan), encoding="utf-8")
            manifest = {
                "source": {"sha256": _sha(map_bytes)},
                "index": {"sha256": _sha(index_bytes)},
            }

            with (
                mock.patch("otbm_route_preflight._load_world_manifest", return_value=manifest),
                mock.patch("otbm_route_preflight.export_route_plan_index_path", return_value=copy.deepcopy(plan)) as exporter,
            ):
                result = preflight_index_paths(
                    route_plan_path=route_path,
                    runtime_map_path=map_path,
                    index_path=index_path,
                    appearances_path=appearances_path,
                    world_manifest_path=manifest_path,
                )

            self.assertTrue(result["ok"])
            exporter.assert_called_once_with(
                index_path=index_path.resolve(),
                appearances_path=appearances_path.resolve(),
                lower=(10, 10, 7),
                upper=(11, 10, 7),
                origin=(10, 10, 7),
                destination=(11, 10, 7),
                transitions_path=None,
                script_resolution_path=None,
                interaction_registry_path=None,
                world_manifest_path=manifest_path,
                allow_diagonal=False,
                max_positions=10,
            )

    def test_world_manifest_runtime_map_mismatch_blocks_before_export(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            map_path = root / "map.otbm"
            index_path = root / "map.widx"
            appearances_path = root / "appearances.json"
            manifest_path = root / "map.widx.json"
            route_path = root / "route.json"

            map_bytes = b"runtime-map-fixture"
            index_bytes = b"world-index-fixture"
            appearances_bytes = b"appearances-fixture"
            map_path.write_bytes(map_bytes)
            index_path.write_bytes(index_bytes)
            appearances_path.write_bytes(appearances_bytes)
            manifest_path.write_text("{}\n", encoding="utf-8")
            plan = _plan(_sha(map_bytes), _sha(index_bytes), _sha(appearances_bytes))
            route_path.write_text(json.dumps(plan), encoding="utf-8")

            with (
                mock.patch(
                    "otbm_route_preflight._load_world_manifest",
                    return_value={"source": {"sha256": "0" * 64}, "index": {"sha256": _sha(index_bytes)}},
                ),
                mock.patch("otbm_route_preflight.export_route_plan_index_path") as exporter,
            ):
                result = preflight_index_paths(
                    route_plan_path=route_path,
                    runtime_map_path=map_path,
                    index_path=index_path,
                    appearances_path=appearances_path,
                    world_manifest_path=manifest_path,
                )

            self.assertFalse(result["ok"])
            self.assertEqual(result["firstBlocker"]["code"], "ROUTE_PROVENANCE_MISMATCH")
            exporter.assert_not_called()


if __name__ == "__main__":
    unittest.main()
