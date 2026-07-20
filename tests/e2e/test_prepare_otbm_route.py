from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


MODULE_PATH = Path(__file__).resolve().parents[2] / "tools" / "e2e" / "prepare_otbm_route.py"
SPEC = importlib.util.spec_from_file_location("prepare_otbm_route", MODULE_PATH)
assert SPEC and SPEC.loader
prepare_otbm_route = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = prepare_otbm_route
SPEC.loader.exec_module(prepare_otbm_route)


class PrepareOtbmRouteTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.manifest = self.root / "scenario-manifest.json"
        self.runtime_map = self.root / "otservbr.otbm"
        self.assets = self.root / "assets"
        self.artifacts = self.root / "artifacts"
        self.registry = self.root / "landmarks.json"
        self.requests = self.root / "routes"
        self.scanner_source = self.root / "otbm_item_audit_scan.cpp"

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def write_manifest(self, steps: list[dict] | None) -> None:
        scenario: dict[str, object] = {"id": "fixture"}
        if steps is not None:
            scenario["steps"] = steps
        self.manifest.write_text(
            json.dumps({"schema_version": 1, "scenario": scenario}), encoding="utf-8"
        )

    def write_route_inputs(self) -> None:
        self.runtime_map.write_bytes(b"map")
        self.assets.mkdir()
        (self.assets / "appearances-abc.dat").write_bytes(b"appearances")
        self.requests.mkdir()
        (self.requests / "thais-temple-depot.json").write_text(
            json.dumps(
                {
                    "from": {"landmarkId": "thais.temple"},
                    "to": {"landmarkId": "thais.depot"},
                    "routingOptions": {
                        "allowDiagonal": False,
                        "maxExecutablePositions": 10000,
                    },
                }
            ),
            encoding="utf-8",
        )
        self.scanner_source.write_text("// scanner\n", encoding="utf-8")

    def test_non_route_scenario_is_a_noop_before_runtime_inputs_are_required(self) -> None:
        self.write_manifest([{"id": "wait", "action": "wait", "ms": 1}])
        result = prepare_otbm_route.prepare_routes(
            manifest_path=self.manifest,
            runtime_map_path=self.runtime_map,
            assets_dir=self.assets,
            artifact_dir=self.artifacts,
            landmark_registry_path=self.registry,
            route_request_root=self.requests,
            scanner_source=self.scanner_source,
        )
        self.assertEqual(result, {"status": "not-required", "routeIds": []})
        self.assertFalse(self.artifacts.exists())

    def test_route_ids_are_deduplicated_in_first_use_order(self) -> None:
        document = {
            "scenario": {
                "steps": [
                    {"id": "a", "action": "follow_route", "route": "first"},
                    {"id": "b", "action": "wait", "ms": 1},
                    {"id": "c", "action": "follow_route", "route": "first"},
                    {"id": "d", "action": "follow_route", "route": "second"},
                ]
            }
        }
        self.assertEqual(prepare_otbm_route.route_ids_from_manifest(document), ["first", "second"])

    def test_unsafe_route_id_is_rejected_before_request_path_resolution(self) -> None:
        document = {
            "scenario": {
                "steps": [
                    {"id": "route", "action": "follow_route", "route": "../escape"},
                ]
            }
        }
        with self.assertRaisesRegex(prepare_otbm_route.RoutePreparationError, "must match"):
            prepare_otbm_route.route_ids_from_manifest(document)

    def test_canonical_route_is_written_only_after_exact_preflight_passes(self) -> None:
        self.write_manifest(
            [
                {
                    "id": "route",
                    "action": "follow_route",
                    "route": "thais-temple-depot",
                    "timeout_ms": 120000,
                }
            ]
        )
        self.write_route_inputs()
        plan = {
            "format": "canary-otbm-e2e-route-plan-v1",
            "schemaVersion": 1,
            "executionStatus": "executable",
            "pathComplete": True,
            "routingMode": "strict",
            "origin": [32369, 32241, 7],
            "destination": [32352, 32226, 7],
            "distance": 66,
            "blockers": [],
            "planHashSha256": "a" * 64,
        }
        world_manifest = {
            "source": {"sha256": "b" * 64},
            "index": {"sha256": "c" * 64, "size": 842280592},
        }
        origin = {
            "regionId": "thais.temple-depot",
            "routingBounds": {"from": [32347, 32216, 7], "to": [32369, 32241, 7]},
            "anchor": {"position": [32369, 32241, 7]},
        }
        destination = {
            "regionId": "thais.temple-depot",
            "routingBounds": {"from": [32347, 32216, 7], "to": [32369, 32241, 7]},
            "anchor": {"position": [32352, 32226, 7]},
        }

        with (
            mock.patch.object(prepare_otbm_route, "compile_scanner"),
            mock.patch.object(
                prepare_otbm_route, "build_world_index", return_value=world_manifest
            ),
            mock.patch.object(prepare_otbm_route, "load_registry", return_value={}),
            mock.patch.object(
                prepare_otbm_route,
                "resolve_landmark_anchor",
                side_effect=[origin, destination],
            ),
            mock.patch.object(
                prepare_otbm_route, "export_route_plan_index_path", return_value=plan
            ) as export_plan,
            mock.patch.object(
                prepare_otbm_route,
                "preflight_index_paths",
                return_value={"ok": True, "status": "passed", "firstBlocker": None},
            ) as preflight,
        ):
            result = prepare_otbm_route.prepare_routes(
                manifest_path=self.manifest,
                runtime_map_path=self.runtime_map,
                assets_dir=self.assets,
                artifact_dir=self.artifacts,
                landmark_registry_path=self.registry,
                route_request_root=self.requests,
                scanner_source=self.scanner_source,
            )

        self.assertEqual(result["status"], "passed")
        self.assertEqual(result["routeIds"], ["thais-temple-depot"])
        final_plan = self.artifacts / "route-thais-temple-depot.json"
        self.assertTrue(final_plan.is_file())
        self.assertEqual(json.loads(final_plan.read_text(encoding="utf-8")), plan)
        self.assertEqual(export_plan.call_args.kwargs["origin"], (32369, 32241, 7))
        self.assertEqual(export_plan.call_args.kwargs["destination"], (32352, 32226, 7))
        self.assertIsNone(export_plan.call_args.kwargs.get("transitions_path"))
        self.assertTrue(preflight.called)
        self.assertTrue((self.artifacts / "route-thais-temple-depot-preflight.json").is_file())
        self.assertTrue((self.artifacts / "route-thais-temple-depot-request.json").is_file())
        self.assertTrue((self.artifacts / "route-thais-temple-depot-world-index-manifest.json").is_file())
        self.assertFalse(any(path.suffix == ".widx" for path in self.artifacts.iterdir()))

    def test_blocked_preflight_never_publishes_canonical_route(self) -> None:
        self.write_manifest(
            [{"id": "route", "action": "follow_route", "route": "thais-temple-depot"}]
        )
        self.write_route_inputs()
        plan = {
            "executionStatus": "executable",
            "pathComplete": True,
            "planHashSha256": "a" * 64,
        }
        world_manifest = {
            "source": {"sha256": "b" * 64},
            "index": {"sha256": "c" * 64, "size": 1},
        }
        resolution = {
            "regionId": "thais.temple-depot",
            "routingBounds": {"from": [1, 1, 7], "to": [2, 2, 7]},
            "anchor": {"position": [1, 1, 7]},
        }
        with (
            mock.patch.object(prepare_otbm_route, "compile_scanner"),
            mock.patch.object(
                prepare_otbm_route, "build_world_index", return_value=world_manifest
            ),
            mock.patch.object(prepare_otbm_route, "load_registry", return_value={}),
            mock.patch.object(
                prepare_otbm_route,
                "resolve_landmark_anchor",
                side_effect=[resolution, resolution],
            ),
            mock.patch.object(
                prepare_otbm_route, "export_route_plan_index_path", return_value=plan
            ),
            mock.patch.object(
                prepare_otbm_route,
                "preflight_index_paths",
                return_value={
                    "ok": False,
                    "status": "blocked",
                    "firstBlocker": {"code": "ROUTE_CURRENT_EVIDENCE_MISMATCH"},
                },
            ),
        ):
            with self.assertRaisesRegex(
                prepare_otbm_route.RoutePreparationError, "static preflight blocked"
            ):
                prepare_otbm_route.prepare_routes(
                    manifest_path=self.manifest,
                    runtime_map_path=self.runtime_map,
                    assets_dir=self.assets,
                    artifact_dir=self.artifacts,
                    landmark_registry_path=self.registry,
                    route_request_root=self.requests,
                    scanner_source=self.scanner_source,
                )

        self.assertFalse((self.artifacts / "route-thais-temple-depot.json").exists())
        self.assertTrue((self.artifacts / "route-thais-temple-depot-preflight.json").is_file())


if __name__ == "__main__":
    unittest.main()
