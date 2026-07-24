from __future__ import annotations

import hashlib
import json
import os
import shutil
import struct
import subprocess
import tempfile
import unittest
from pathlib import Path

from otbm_house_reference_parity import (
    CLIENT_HOUSE_NAMESPACE,
    OTBM_HOUSE_NAMESPACE,
    PARITY_FORMAT,
    RESOLVER_FORMAT,
    HouseReferenceParityError,
    build_parity,
    derive_resolver,
    deterministic_json,
    write_output,
)
from otbm_world_index import build_world_index

NODE_ESCAPE = 0xFD
NODE_START = 0xFE
NODE_END = 0xFF
OTBM_MAP_DATA = 2
OTBM_TILE_AREA = 4
OTBM_ITEM = 6
OTBM_HOUSETILE = 14
ATTR_HOUSEDOOR_ID = 14


def escape(data: bytes) -> bytes:
    output = bytearray()
    for value in data:
        if value in (NODE_ESCAPE, NODE_START, NODE_END):
            output.append(NODE_ESCAPE)
        output.append(value)
    return bytes(output)


def node(node_type: int, properties: bytes, children: list[bytes] | None = None) -> bytes:
    return bytes((NODE_START, node_type)) + escape(properties) + b"".join(children or []) + bytes((NODE_END,))


def item(item_id: int, attributes: bytes = b"") -> bytes:
    return node(OTBM_ITEM, struct.pack("<H", item_id) + attributes)


def make_map(path: Path) -> None:
    base_x, base_y, floor = 256, 512, 7
    door = item(203, bytes((ATTR_HOUSEDOOR_ID, 7)))
    house = node(OTBM_HOUSETILE, bytes((45, 88)) + struct.pack("<I", 99), [door])
    area = node(OTBM_TILE_AREA, struct.pack("<HHB", base_x, base_y, floor), [house])
    map_data = node(OTBM_MAP_DATA, b"", [area])
    root = node(0, struct.pack("<IHHII", 4, 1024, 1024, 4, 4), [map_data])
    path.write_bytes(b"\0\0\0\0" + root)


class HouseReferenceParityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        compiler = shutil.which("c++") or shutil.which("g++")
        if compiler is None:
            raise unittest.SkipTest("A C++ compiler is required")
        cls.build = tempfile.TemporaryDirectory()
        cls.scanner = Path(cls.build.name) / "otbm_item_audit_scan"
        source = Path(__file__).with_name("otbm_item_audit_scan.cpp")
        completed = subprocess.run(
            [compiler, "-O2", "-std=c++20", "-Wall", "-Wextra", "-Wpedantic", "-Werror", str(source), "-o", str(cls.scanner)],
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode != 0:
            raise RuntimeError(completed.stderr)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.build.cleanup()

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.map = self.root / "fixture.otbm"
        self.world_index = self.root / "world.widx"
        self.world_manifest = self.root / "world.json"
        make_map(self.map)
        build_world_index(
            map_path=self.map,
            scanner=self.scanner,
            output=self.world_index,
            manifest_output=self.world_manifest,
        )
        self.client_manifest = self.root / "client-manifest.json"
        self.staticdata_index = self.root / "staticdata-index.json"
        self.staticmap_index = self.root / "staticmap-index.json"
        self._write_client_manifest()
        self._write_staticdata()
        self._write_staticmap()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _write_client_manifest(self) -> None:
        self.client_manifest.write_text(
            json.dumps(
                {
                    "format": "canary-tibia-client-reference-manifest-v1",
                    "schemaVersion": 1,
                    "referenceId": "fixture-reference",
                    "selectedInputs": [
                        {"id": "staticdata", "path": "fixture-staticdata.dat", "sizeBytes": 10, "sha256": "1" * 64},
                        {"id": "staticmapdata", "path": "fixture-staticmapdata.dat", "sizeBytes": 20, "sha256": "2" * 64},
                    ],
                },
                sort_keys=True,
            ),
            encoding="utf-8",
        )

    def _manifest_sha(self) -> str:
        return hashlib.sha256(self.client_manifest.read_bytes()).hexdigest()

    def _write_staticdata(self, *, order: str = "newer", records: list[dict[str, object]] | None = None) -> None:
        evidence = (
            {"state": "unresolved"}
            if order == "unresolved"
            else {"state": "reviewed", "reviewId": "fixture-house-order", "statement": "Fixture field order review."}
        )
        if records is None:
            base = {
                "id": 10,
                "sourceOrdinal": 1,
                "name": "Fixture House",
                "position": {"x": 301, "y": 600, "z": 7},
            }
            if order == "unresolved":
                base.update({"houseField5": 1, "houseField7": 1})
            else:
                base.update({"beds": 1, "size": 1})
            records = [base]
        payload = {
            "format": "canary-tibia-staticdata-index-v1",
            "schemaVersion": 2,
            "source": {
                "manifestFormat": "canary-tibia-client-reference-manifest-v1",
                "manifestSha256": self._manifest_sha(),
                "referenceId": "fixture-reference",
                "inputId": "staticdata",
                "manifestPath": "fixture-staticdata.dat",
                "sizeBytes": 10,
                "sha256": "1" * 64,
                "schemaFamily": "legacy",
                "houseFieldOrder": order,
                "houseFieldOrderEvidence": evidence,
            },
            "categories": {
                "houses": {
                    "count": len(records),
                    "sourceCategory": "houses",
                    "sourceSchema": "legacy",
                    "houseFieldOrder": order,
                    "records": records,
                }
            },
            "findings": {
                "duplicateIds": [],
                "duplicateSingularFields": [],
                "missingRequiredFields": [],
                "unresolvedHouseFieldOrder": [] if order != "unresolved" else [{"category": "houses"}],
            },
            "summary": {"categoryCounts": {"houses": len(records)}},
            "policy": {
                "houseFieldOrderResolution": order,
                "houseFieldOrderHeuristics": False,
                "gameplayConclusions": False,
            },
        }
        self.staticdata_index.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")

    def _write_staticmap(self, *, object_resolution: str = "unresolved") -> None:
        payload = {
            "format": "canary-tibia-staticmapdata-index-v1",
            "schemaVersion": 1,
            "source": {
                "manifestFormat": "canary-tibia-client-reference-manifest-v1",
                "manifestSha256": self._manifest_sha(),
                "referenceId": "fixture-reference",
                "inputId": "staticmapdata",
                "manifestPath": "fixture-staticmapdata.dat",
                "sizeBytes": 20,
                "sha256": "2" * 64,
            },
            "objectIdNamespace": {
                "name": "staticmapdata.object_id",
                "resolution": object_resolution,
                "otbmItemIdEquivalent": False,
            },
            "houses": [
                {
                    "sourceOrdinal": 1,
                    "houseId": 10,
                    "layout": {
                        "position": {"x": 301, "y": 600, "z": 7},
                        "size": {"width": 1, "height": 1, "floors": 1},
                        "validation": {"matchesDeclaredDimensions": True},
                        "tiles": {"floorData": {"rows": []}},
                    },
                }
            ],
            "findings": {},
            "summary": {"houseCount": 1},
            "policy": {"objectIdMapping": "unresolved", "otbmParsing": False, "otbmWriting": False},
        }
        self.staticmap_index.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")

    def _derive(self) -> tuple[dict[str, object], tuple[Path, ...]]:
        return derive_resolver(
            client_manifest_path=self.client_manifest,
            staticdata_index_path=self.staticdata_index,
            staticmapdata_index_path=self.staticmap_index,
            world_index_path=self.world_index,
            world_manifest_path=self.world_manifest,
            review_id="fixture-registry-position-review",
            review_statement="Exact registry position tile and canonical World Index house ID only.",
        )

    def _resolver_path(self) -> Path:
        payload, _ = self._derive()
        path = self.root / "resolver.json"
        path.write_text(deterministic_json(payload), encoding="utf-8")
        return path

    def _parity(self, resolver: Path | None = None) -> dict[str, object]:
        payload, _ = build_parity(
            client_manifest_path=self.client_manifest,
            staticdata_index_path=self.staticdata_index,
            staticmapdata_index_path=self.staticmap_index,
            world_index_path=self.world_index,
            world_manifest_path=self.world_manifest,
            resolver_path=resolver or self._resolver_path(),
        )
        return payload

    def test_derives_exact_registry_position_resolver(self) -> None:
        payload, _ = self._derive()
        self.assertEqual(payload["format"], RESOLVER_FORMAT)
        self.assertEqual(payload["namespaces"]["source"], CLIENT_HOUSE_NAMESPACE)
        self.assertEqual(payload["namespaces"]["target"], OTBM_HOUSE_NAMESPACE)
        self.assertEqual(payload["summary"], {"clientHouseCount": 1, "mappingCount": 1, "unresolvedCount": 0, "conflictCount": 0})
        self.assertEqual(payload["mappings"][0]["clientHouseId"], 10)
        self.assertEqual(payload["mappings"][0]["otbmHouseId"], 99)
        self.assertEqual(payload["mappings"][0]["position"], [301, 600, 7])
        self.assertFalse(payload["policy"]["nameMapping"])
        self.assertFalse(payload["policy"]["numericIdentityInference"])

    def test_builds_conforming_parity_and_groups_house_door(self) -> None:
        payload = self._parity()
        self.assertEqual(payload["format"], PARITY_FORMAT)
        self.assertEqual(payload["summary"]["stateCounts"]["conforming"], 1)
        self.assertEqual(payload["summary"]["findingCount"], 0)
        row = payload["houses"][0]
        self.assertEqual(row["state"], "conforming")
        self.assertEqual(row["otbm"]["houseDoorPlacementCount"], 1)
        self.assertTrue(row["comparisons"]["registrySizeVsOtbmHouseTiles"]["matches"])
        self.assertEqual(payload["provenance"]["staticdataHouseFieldOrder"], "newer")
        self.assertFalse(payload["policy"]["otbmParsing"])
        self.assertFalse(payload["policy"]["objectIdMapping"])

    def test_unresolved_house_field_order_preserves_raw_values_and_skips_size_comparison(self) -> None:
        self._write_staticdata(order="unresolved")
        payload = self._parity()
        row = payload["houses"][0]
        self.assertEqual(row["state"], "conforming")
        self.assertEqual(row["registry"]["houseField5"], 1)
        self.assertNotIn("registrySizeVsOtbmHouseTiles", row["comparisons"])
        self.assertEqual(payload["summary"]["staticdataHouseFieldOrder"], "unresolved")

    def test_unresolved_registry_position_is_explicit(self) -> None:
        records = [
            {"id": 10, "sourceOrdinal": 1, "name": "Mapped", "position": {"x": 301, "y": 600, "z": 7}, "beds": 1, "size": 1},
            {"id": 11, "sourceOrdinal": 2, "name": "Missing", "position": {"x": 400, "y": 700, "z": 7}, "beds": 1, "size": 1},
        ]
        self._write_staticdata(records=records)
        payload, _ = self._derive()
        self.assertEqual(payload["summary"]["mappingCount"], 1)
        self.assertEqual(payload["summary"]["unresolvedCount"], 1)
        self.assertEqual(payload["findings"]["unresolved"][0]["reason"], "registry-position-has-no-otbm-tile")

    def test_rejects_staticdata_schema_before_explicit_house_field_order(self) -> None:
        payload = json.loads(self.staticdata_index.read_text(encoding="utf-8"))
        payload["schemaVersion"] = 1
        self.staticdata_index.write_text(json.dumps(payload), encoding="utf-8")
        with self.assertRaisesRegex(HouseReferenceParityError, "schemaVersion must be at least 2"):
            self._derive()

    def test_rejects_disagreeing_house_field_order_declarations(self) -> None:
        payload = json.loads(self.staticdata_index.read_text(encoding="utf-8"))
        payload["categories"]["houses"]["houseFieldOrder"] = "legacy"
        self.staticdata_index.write_text(json.dumps(payload), encoding="utf-8")
        with self.assertRaisesRegex(HouseReferenceParityError, "declarations disagree"):
            self._derive()

    def test_rejects_resolved_house_order_without_reviewed_evidence(self) -> None:
        payload = json.loads(self.staticdata_index.read_text(encoding="utf-8"))
        payload["source"]["houseFieldOrderEvidence"] = {"state": "unresolved"}
        self.staticdata_index.write_text(json.dumps(payload), encoding="utf-8")
        with self.assertRaisesRegex(HouseReferenceParityError, "requires reviewed evidence"):
            self._derive()

    def test_rejects_staticmap_object_id_equivalence_claim(self) -> None:
        self._write_staticmap(object_resolution="resolved")
        with self.assertRaisesRegex(HouseReferenceParityError, "must remain unresolved"):
            self._derive()

    def test_rejects_stale_resolver_provenance(self) -> None:
        resolver = self._resolver_path()
        payload = json.loads(resolver.read_text(encoding="utf-8"))
        payload["provenance"]["staticdataIndexSha256"] = "0" * 64
        resolver.write_text(json.dumps(payload), encoding="utf-8")
        with self.assertRaisesRegex(HouseReferenceParityError, "resolver is stale"):
            self._parity(resolver)

    def test_rejects_unknown_and_duplicate_resolver_mappings(self) -> None:
        for mode in ("unknown", "duplicate"):
            with self.subTest(mode=mode):
                resolver = self._resolver_path()
                payload = json.loads(resolver.read_text(encoding="utf-8"))
                row = dict(payload["mappings"][0])
                if mode == "unknown":
                    row["clientHouseId"] = 999
                    payload["mappings"] = [row]
                    pattern = "unknown client house ID"
                else:
                    payload["mappings"] = [row, dict(row)]
                    pattern = "duplicate client house ID"
                resolver.write_text(json.dumps(payload), encoding="utf-8")
                with self.assertRaisesRegex(HouseReferenceParityError, pattern):
                    self._parity(resolver)

    def test_duplicate_json_keys_fail_closed(self) -> None:
        resolver = self.root / "resolver-duplicate.json"
        resolver.write_text('{"format":"canary-otbm-house-id-resolver-v1","format":"duplicate"}', encoding="utf-8")
        with self.assertRaisesRegex(HouseReferenceParityError, "duplicate JSON object key"):
            self._parity(resolver)

    def test_output_is_no_clobber_atomic_and_protects_inputs(self) -> None:
        payload, protected = self._derive()
        output = self.root / "resolver-output.json"
        write_output(output, payload, protected_inputs=protected)
        self.assertEqual(json.loads(output.read_text(encoding="utf-8"))["format"], RESOLVER_FORMAT)
        with self.assertRaisesRegex(HouseReferenceParityError, "already exists"):
            write_output(output, payload, protected_inputs=protected)
        write_output(output, payload, protected_inputs=protected, overwrite=True)
        with self.assertRaisesRegex(HouseReferenceParityError, "collides"):
            write_output(self.client_manifest, payload, protected_inputs=protected, overwrite=True)

    def test_deterministic_outputs(self) -> None:
        first, _ = self._derive()
        second, _ = self._derive()
        self.assertEqual(deterministic_json(first), deterministic_json(second))
        resolver = self._resolver_path()
        self.assertEqual(deterministic_json(self._parity(resolver)), deterministic_json(self._parity(resolver)))

    def test_opt_in_exact_inputs(self) -> None:
        exact_dir = os.environ.get("CANARY_TCR005_EXACT_DIR")
        staticdata_path = os.environ.get("CANARY_TCR005_STATICDATA_INDEX")
        if not exact_dir or not staticdata_path:
            self.skipTest("set CANARY_TCR005_EXACT_DIR and CANARY_TCR005_STATICDATA_INDEX")
        root = Path(exact_dir)
        resolver_payload, _ = derive_resolver(
            client_manifest_path=root / "client-manifest.json",
            staticdata_index_path=Path(staticdata_path),
            staticmapdata_index_path=root / "staticmap-index.json",
            world_index_path=root / "world.widx",
            world_manifest_path=root / "world.json",
            review_id="tcr005-exact-registry-position-20260724",
            review_statement="Exact registry position tile and canonical World Index house ID only.",
        )
        self.assertEqual(resolver_payload["summary"]["mappingCount"], 993)
        self.assertEqual(resolver_payload["summary"]["unresolvedCount"], 2)
        resolver_path = self.root / "exact-resolver.json"
        resolver_path.write_text(deterministic_json(resolver_payload), encoding="utf-8")
        parity_payload, _ = build_parity(
            client_manifest_path=root / "client-manifest.json",
            staticdata_index_path=Path(staticdata_path),
            staticmapdata_index_path=root / "staticmap-index.json",
            world_index_path=root / "world.widx",
            world_manifest_path=root / "world.json",
            resolver_path=resolver_path,
        )
        self.assertEqual(parity_payload["summary"]["houseRecordCount"], 995)
        self.assertEqual(parity_payload["summary"]["otbmHouseCount"], 993)
        self.assertEqual(parity_payload["summary"]["stateCounts"]["mismatch"], 993)
        self.assertEqual(parity_payload["summary"]["stateCounts"]["unresolved-id-space"], 2)
        self.assertEqual(parity_payload["summary"]["orphanHouseDoorPlacementCount"], 42)
        self.assertEqual(parity_payload["summary"]["staticdataHouseFieldOrder"], "newer")


if __name__ == "__main__":
    unittest.main()
