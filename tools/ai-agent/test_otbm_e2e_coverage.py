from __future__ import annotations

import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

MODULE_DIR = Path(__file__).parent
sys.path.insert(0, str(MODULE_DIR))

import otbm_e2e_coverage as mod

MAP = "a" * 64
WIDX = "b" * 64
OLD_MAP = "c" * 64
OLD_WIDX = "d" * 64


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value), encoding="utf-8")


def target_doc(selector: dict[str, object] | None = None) -> dict[str, object]:
    return {
        "format": mod.TARGET_FORMAT,
        "schemaVersion": 1,
        "targets": [
            {
                "id": "critical.teleport",
                "reason": "reviewed critical route transition",
                "selector": selector
                or {
                    "position": [100, 100, 7],
                    "itemId": 1387,
                    "teleportDestination": [200, 200, 7],
                },
            }
        ],
    }


def world_doc() -> dict[str, object]:
    return {
        "format": mod.WORLD_FORMAT,
        "source": {"sha256": MAP},
        "index": {"sha256": WIDX},
    }


def item_doc(*, duplicate: bool = False, map_sha: str = MAP) -> dict[str, object]:
    placement = {
        "itemId": 1387,
        "position": [100, 100, 7],
        "itemDepth": 0,
        "teleportDestination": [200, 200, 7],
    }
    placements = [placement, dict(placement, itemDepth=1)] if duplicate else [placement]
    return {
        "format": mod.ITEM_AUDIT_FORMAT,
        "sources": {"map": {"sha256": map_sha}},
        "mechanicPlacements": placements,
    }


def script_doc(
    status: str = "handled-by-engine", *, duplicate: bool = False, map_sha: str = MAP
) -> dict[str, object]:
    placement = {
        "index": 5,
        "itemId": 1387,
        "position": [100, 100, 7],
        "actionId": None,
        "uniqueId": None,
        "houseDoorId": None,
        "teleportDestination": [200, 200, 7],
        "status": status,
    }
    placements = [placement, dict(placement, index=6)] if duplicate else [placement]
    return {
        "format": mod.SCRIPT_FORMAT,
        "sources": {"itemAudit": {"map": {"sha256": map_sha}}},
        "placements": placements,
    }


def reach_doc(
    map_sha: str = MAP, widx_sha: str = WIDX, status: str = "confirmed"
) -> dict[str, object]:
    return {
        "format": mod.REACHABILITY_FORMAT,
        "provenance": {
            "map": {"sha256": map_sha},
            "worldIndex": {"sha256": widx_sha},
        },
        "mechanics": [
            {
                "placementOrdinal": 5,
                "itemId": 1387,
                "position": [100, 100, 7],
                "actionId": None,
                "uniqueId": None,
                "houseDoorId": None,
                "teleportDestination": [200, 200, 7],
                "status": status,
            }
        ],
    }


def route_plan(
    map_sha: str = MAP, widx_sha: str = WIDX, *, transition: bool = True
) -> dict[str, object]:
    if transition:
        edges = [
            {
                "kind": "transition",
                "from": [100, 100, 7],
                "to": [200, 200, 7],
                "transitionId": "teleport:5",
                "evidence": {
                    "transition": {
                        "source": [100, 100, 7],
                        "destination": [200, 200, 7],
                        "itemId": 1387,
                        "actionId": None,
                        "uniqueId": None,
                        "houseDoorId": None,
                    }
                },
            }
        ]
    else:
        edges = [
            {
                "kind": "movement",
                "from": [99, 100, 7],
                "to": [100, 100, 7],
                "evidence": {"source": "reachability-bfs-predecessor"},
            }
        ]
    return {
        "format": mod.ROUTE_FORMAT,
        "executionStatus": "executable",
        "provenance": {
            "map": {"sha256": map_sha},
            "worldIndex": {"sha256": widx_sha},
        },
        "edges": edges,
    }


def make_artifact(
    path: Path,
    *,
    success: bool = True,
    map_sha: str = MAP,
    widx_sha: str = WIDX,
    transition: bool = True,
    zip_mode: bool = False,
    reference_route: bool = True,
) -> None:
    steps = [{"action": "follow_route", "route": "test"}] if reference_route else []
    files: dict[str, object] = {
        "result.json": {"status": "success" if success else "failure", "scenario": "movement/test"},
        "scenario-manifest.json": {"key": "movement/test", "scenario": {"steps": steps}},
        "map.sha256": map_sha,
        "route-test.json": route_plan(map_sha, widx_sha, transition=transition),
    }
    if zip_mode:
        with zipfile.ZipFile(path, "w") as archive:
            for name, value in files.items():
                archive.writestr(name, value if name == "map.sha256" else json.dumps(value))
        return
    path.mkdir()
    for name, value in files.items():
        if name == "map.sha256":
            (path / name).write_text(str(value), encoding="utf-8")
        else:
            write_json(path / name, value)


class CoverageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        write_json(self.root / "targets.json", target_doc())
        write_json(self.root / "world.json", world_doc())
        write_json(self.root / "item.json", item_doc())
        write_json(self.root / "script.json", script_doc())
        write_json(self.root / "reach.json", reach_doc())

    def tearDown(self) -> None:
        self.temp.cleanup()

    def build(
        self,
        *,
        reach: bool = True,
        artifact: Path | None = None,
        script: Path | None = None,
        item: Path | None = None,
    ) -> dict[str, object]:
        targets, targets_sha = mod._load_targets(self.root / "targets.json")
        current, world_sha = mod._world_identity(self.root / "world.json")
        item_doc_value, item_sha = mod._load_item_audit(item or self.root / "item.json", current)
        script_value, script_sha = mod._load_script_resolution(
            script or self.root / "script.json", current
        )
        reports, reach_provenance = mod._load_reachability(
            [self.root / "reach.json"] if reach else [], current
        )
        runs, physical_provenance = mod._load_physical_artifacts(
            [artifact] if artifact else [], current
        )
        return mod.build_matrix(
            targets=targets,
            item_audit=item_doc_value,
            script_resolution=script_value,
            reachability_reports=reports,
            physical_runs=runs,
            current=current,
            provenance={
                "targetsSha256": targets_sha,
                "worldManifestSha256": world_sha,
                "itemAuditSha256": item_sha,
                "scriptResolutionSha256": script_sha,
                "reachability": reach_provenance,
                "physicalArtifacts": physical_provenance,
            },
        )

    def test_current_static_reachability_and_physical_proof(self) -> None:
        artifact = self.root / "artifact"
        make_artifact(artifact)
        row = self.build(artifact=artifact)["mechanics"][0]
        self.assertTrue(row["static"]["indexed"])
        self.assertTrue(row["script"]["resolved"])
        self.assertEqual(row["reachability"]["status"], "confirmed")
        self.assertTrue(row["physical"]["scenarioPresent"])
        self.assertTrue(row["physical"]["runtimeProvenOnCurrentMap"])
        self.assertFalse(row["missingPhysicalScenario"])

    def test_unresolved_and_missing_coverage_fail_closed(self) -> None:
        write_json(self.root / "script-unresolved.json", script_doc("unresolved"))
        output = self.build(reach=False, script=self.root / "script-unresolved.json")
        row = output["mechanics"][0]
        self.assertFalse(row["script"]["resolved"])
        self.assertFalse(row["reachability"]["covered"])
        self.assertTrue(row["missingPhysicalScenario"])
        codes = {finding["code"] for finding in output["findings"]}
        self.assertIn("SCRIPT_NOT_RESOLVED", codes)
        self.assertIn("REACHABILITY_NOT_COVERED", codes)
        self.assertIn("PHYSICAL_SCENARIO_MISSING", codes)

    def test_reachability_world_index_manifest_provenance_is_current(self) -> None:
        document = reach_doc()
        document["provenance"] = {
            "worldIndex": {"sha256": WIDX},
            "worldIndexManifest": {
                "source": {"sha256": MAP},
                "index": {"sha256": WIDX},
            },
        }
        write_json(self.root / "reach.json", document)
        self.assertTrue(self.build()["mechanics"][0]["reachability"]["covered"])

    def test_stale_reachability_and_physical_are_not_current_proof(self) -> None:
        write_json(self.root / "reach.json", reach_doc(OLD_MAP, OLD_WIDX))
        artifact = self.root / "artifact"
        make_artifact(artifact, map_sha=OLD_MAP, widx_sha=OLD_WIDX)
        row = self.build(artifact=artifact)["mechanics"][0]
        self.assertFalse(row["reachability"]["covered"])
        self.assertTrue(row["physical"]["runtimeProven"])
        self.assertFalse(row["physical"]["runtimeProvenOnCurrentMap"])
        self.assertTrue(row["staleAgainstCurrentMapProvenance"])

    def test_stale_physical_remains_stale_with_current_reachability(self) -> None:
        artifact = self.root / "artifact"
        make_artifact(artifact, map_sha=OLD_MAP, widx_sha=OLD_WIDX)
        row = self.build(artifact=artifact)["mechanics"][0]
        self.assertTrue(row["reachability"]["covered"])
        self.assertTrue(row["staleAgainstCurrentMapProvenance"])

    def test_missing_runtime_map_hash_is_not_current_physical_proof(self) -> None:
        artifact = self.root / "artifact"
        make_artifact(artifact)
        (artifact / "map.sha256").unlink()
        output = self.build(artifact=artifact)
        row = output["mechanics"][0]
        self.assertTrue(row["physical"]["runtimeProven"])
        self.assertFalse(row["physical"]["runtimeProvenOnCurrentMap"])
        self.assertIn(
            "PHYSICAL_RUNTIME_NOT_PROVEN_ON_CURRENT_MAP",
            {finding["code"] for finding in output["findings"]},
        )

    def test_ambiguous_static_match_does_not_resolve_script(self) -> None:
        write_json(self.root / "item-duplicate.json", item_doc(duplicate=True))
        output = self.build(item=self.root / "item-duplicate.json")
        row = output["mechanics"][0]
        self.assertFalse(row["static"]["uniqueMatch"])
        self.assertFalse(row["script"]["resolved"])

    def test_pure_movement_route_does_not_claim_mechanic_proof(self) -> None:
        artifact = self.root / "artifact"
        make_artifact(artifact, transition=False)
        row = self.build(artifact=artifact)["mechanics"][0]
        self.assertFalse(row["physical"]["scenarioPresent"])
        self.assertFalse(row["physical"]["runtimeProven"])

    def test_unreferenced_route_plan_does_not_claim_physical_proof(self) -> None:
        artifact = self.root / "artifact"
        make_artifact(artifact, reference_route=False)
        row = self.build(artifact=artifact)["mechanics"][0]
        self.assertFalse(row["physical"]["scenarioPresent"])

    def test_zip_artifact_supported(self) -> None:
        artifact = self.root / "artifact.zip"
        make_artifact(artifact, zip_mode=True)
        row = self.build(artifact=artifact)["mechanics"][0]
        self.assertTrue(row["physical"]["runtimeProvenOnCurrentMap"])

    def test_target_requires_exact_position_and_identity(self) -> None:
        write_json(self.root / "targets.json", target_doc({"itemId": 1387}))
        with self.assertRaises(mod.CoverageError):
            mod._load_targets(self.root / "targets.json")
        write_json(self.root / "targets.json", target_doc({"position": [1, 2, 7]}))
        with self.assertRaises(mod.CoverageError):
            mod._load_targets(self.root / "targets.json")

    def test_house_door_selector_uses_world_index_width(self) -> None:
        with self.assertRaises(mod.CoverageError):
            mod._selector({"position": [1, 2, 7], "houseDoorId": 256}, "selector")
        value = mod._selector({"position": [1, 2, 7], "houseDoorId": 255}, "selector")
        self.assertEqual(value["houseDoorId"], 255)

    def test_duplicate_target_ids_rejected(self) -> None:
        document = target_doc()
        document["targets"].append(dict(document["targets"][0]))
        write_json(self.root / "targets.json", document)
        with self.assertRaises(mod.CoverageError):
            mod._load_targets(self.root / "targets.json")

    def test_item_audit_must_match_current_map(self) -> None:
        write_json(self.root / "item-stale.json", item_doc(map_sha=OLD_MAP))
        current, _ = mod._world_identity(self.root / "world.json")
        with self.assertRaises(mod.CoverageError):
            mod._load_item_audit(self.root / "item-stale.json", current)

    def test_script_resolution_must_match_current_map(self) -> None:
        write_json(self.root / "script-stale.json", script_doc(map_sha=OLD_MAP))
        current, _ = mod._world_identity(self.root / "world.json")
        with self.assertRaises(mod.CoverageError):
            mod._load_script_resolution(self.root / "script-stale.json", current)


if __name__ == "__main__":
    unittest.main()
