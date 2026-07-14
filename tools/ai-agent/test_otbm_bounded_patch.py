from __future__ import annotations

import json
import os
import shutil
import struct
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import otbm_bounded_patch
from otbm_bounded_patch import apply_bounded_patch
from otbm_bounded_patch_types import BoundedPatchError, PatchPlan, sha256_file

NODE_ESCAPE = 0xFD
NODE_START = 0xFE
NODE_END = 0xFF
OTBM_ROOT = 0
OTBM_MAP_DATA = 2
OTBM_TILE_AREA = 4
OTBM_TILE = 5
OTBM_ITEM = 6
ATTR_ACTION_ID = 4
ATTR_UNIQUE_ID = 5
ATTR_TELE_DEST = 8
ATTR_HOUSEDOOR_ID = 14
POSITION = (1025, 2050, 7)


def _logical(values: bytes) -> bytes:
    output = bytearray()
    for value in values:
        if value in (NODE_ESCAPE, NODE_START, NODE_END):
            output.append(NODE_ESCAPE)
        output.append(value)
    return bytes(output)


def _node(node_type: int, properties: bytes = b"", children: bytes = b"") -> bytes:
    return bytes((NODE_START, node_type)) + _logical(properties) + children + bytes((NODE_END,))


def _item(item_id: int, attributes: list[tuple[int, object]]) -> bytes:
    properties = bytearray(struct.pack("<H", item_id))
    for attribute, value in attributes:
        properties.append(attribute)
        if attribute in (ATTR_ACTION_ID, ATTR_UNIQUE_ID):
            properties.extend(struct.pack("<H", int(value)))
        elif attribute == ATTR_HOUSEDOOR_ID:
            properties.append(int(value))
        elif attribute == ATTR_TELE_DEST:
            x, y, z = value  # type: ignore[misc]
            properties.extend(struct.pack("<HHB", x, y, z))
        else:
            raise AssertionError(attribute)
    return _node(OTBM_ITEM, bytes(properties))


def build_map(
    *,
    action_id: int = 1000,
    duplicate_action: bool = False,
) -> bytes:
    action_attributes: list[tuple[int, object]] = [(ATTR_ACTION_ID, action_id)]
    if duplicate_action:
        action_attributes.append((ATTR_ACTION_ID, action_id))
    items = b"".join(
        (
            _item(100, action_attributes),
            _item(101, [(ATTR_UNIQUE_ID, 2000)]),
            _item(102, [(ATTR_HOUSEDOOR_ID, 3)]),
            _item(103, [(ATTR_TELE_DEST, (1100, 2100, 7))]),
        )
    )
    tile = _node(OTBM_TILE, bytes((1, 2)), items)
    area = _node(OTBM_TILE_AREA, struct.pack("<HHB", 1024, 2048, 7), tile)
    map_data = _node(OTBM_MAP_DATA, children=area)
    header = struct.pack("<IHHII", 4, 256, 256, 3, 57)
    return b"\x00\x00\x00\x00" + _node(OTBM_ROOT, header, map_data)


def operation(
    operation_id: str,
    kind: str,
    placement: int,
    item_id: int,
    expected: object,
    replacement: object,
) -> dict[str, object]:
    return {
        "id": operation_id,
        "kind": kind,
        "position": list(POSITION),
        "tilePlacementIndex": placement,
        "itemId": item_id,
        "itemDepth": 0,
        "expected": expected,
        "replacement": replacement,
    }


@unittest.skipUnless(shutil.which("g++"), "g++ is required for native scanner integration tests")
class BoundedPatchIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.build_directory = Path(tempfile.mkdtemp(prefix="otbm-bounded-patch-scanner-"))
        cls.scanner = cls.build_directory / "otbm_item_audit_scan"
        source = Path(__file__).with_name("otbm_item_audit_scan.cpp")
        completed = subprocess.run(
            [
                "g++",
                "-std=c++20",
                "-O2",
                "-Wall",
                "-Wextra",
                "-Wpedantic",
                "-Werror",
                str(source),
                "-o",
                str(cls.scanner),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode != 0:
            raise AssertionError(completed.stderr or completed.stdout)

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.build_directory, ignore_errors=True)

    def setUp(self) -> None:
        self.temporary = Path(tempfile.mkdtemp(prefix="otbm-bounded-patch-test-"))
        self.source = self.temporary / "source.otbm"
        self.artifacts = self.temporary / "artifacts"

    def tearDown(self) -> None:
        shutil.rmtree(self.temporary, ignore_errors=True)

    def write_map(self, **kwargs: object) -> None:
        self.source.write_bytes(build_map(**kwargs))

    def make_plan(self, operations: list[dict[str, object]], **source_overrides: object) -> PatchPlan:
        source = {
            "fileName": self.source.name,
            "sha256": sha256_file(self.source),
            "size": self.source.stat().st_size,
            "otbmVersion": 4,
            "itemsMajor": 3,
            "itemsMinor": 57,
            **source_overrides,
        }
        return PatchPlan.from_raw(
            {
                "format": "canary-otbm-bounded-patch-plan-v1",
                "source": source,
                "region": {"from": [1024, 2048, 7], "to": [1030, 2060, 7]},
                "operations": operations,
            }
        )

    def apply(self, plan: PatchPlan) -> dict[str, object]:
        return apply_bounded_patch(
            plan=plan,
            source_path=self.source,
            scanner_path=self.scanner,
            artifact_root=self.artifacts,
            output_path=Path("patched.otbm"),
            evidence_directory=Path("evidence"),
            result_path=Path("result.json"),
            timeout_seconds=60,
        )

    def test_round_trip_all_supported_attributes(self) -> None:
        self.write_map()
        original = self.source.read_bytes()
        plan = self.make_plan(
            [
                operation("action", "set-action-id", 0, 100, 1000, 1001),
                operation("unique", "set-unique-id", 1, 101, 2000, 2001),
                operation("door", "set-house-door-id", 2, 102, 3, 4),
                operation(
                    "teleport",
                    "set-teleport-destination",
                    3,
                    103,
                    [1100, 2100, 7],
                    [1101, 2101, 8],
                ),
            ]
        )

        result = self.apply(plan)

        self.assertEqual(self.source.read_bytes(), original)
        output = self.artifacts / "patched.otbm"
        self.assertTrue(output.is_file())
        self.assertEqual(output.stat().st_size, self.source.stat().st_size)
        self.assertTrue(result["proof"]["outsideScannerSpansEqual"])  # type: ignore[index]
        self.assertTrue(result["proof"]["boundedSemanticDiffExact"])  # type: ignore[index]
        self.assertTrue((self.artifacts / "evidence" / "semantic-diff.json").is_file())
        self.assertTrue((self.artifacts / "evidence" / "before.widx").is_file())
        self.assertTrue((self.artifacts / "evidence" / "after.widx").is_file())
        persisted = json.loads((self.artifacts / "result.json").read_text(encoding="utf-8"))
        self.assertEqual(persisted["format"], "canary-otbm-bounded-patch-result-v1")
        changed_offsets = persisted["proof"]["changedPhysicalOffsets"]
        self.assertTrue(changed_offsets)
        actual_differences = [
            index
            for index, (before, after) in enumerate(zip(original, output.read_bytes(), strict=True))
            if before != after
        ]
        self.assertEqual(changed_offsets, actual_differences)

        anchors = self.artifacts / "verified-after.json"
        subprocess.run(
            [str(self.scanner), "--patch-anchors", str(output), str(anchors)],
            check=True,
            capture_output=True,
            text=True,
        )
        values = {
            (entry["tilePlacementIndex"], entry["attribute"]): entry["value"]
            for entry in json.loads(anchors.read_text(encoding="utf-8"))["anchors"]
        }
        self.assertEqual(values[(0, "actionId")], 1001)
        self.assertEqual(values[(1, "uniqueId")], 2001)
        self.assertEqual(values[(2, "houseDoorId")], 4)
        self.assertEqual(values[(3, "teleportDestination")], [1101, 2101, 8])

    def test_rejects_wrong_source_hash(self) -> None:
        self.write_map()
        wrong_hash = "0" * 64
        if wrong_hash == sha256_file(self.source):
            wrong_hash = "1" * 64
        plan = self.make_plan(
            [operation("action", "set-action-id", 0, 100, 1000, 1001)],
            sha256=wrong_hash,
        )
        with self.assertRaisesRegex(BoundedPatchError, "source pin mismatch"):
            self.apply(plan)
        self.assertFalse((self.artifacts / "patched.otbm").exists())

    def test_rejects_expected_old_value_mismatch(self) -> None:
        self.write_map()
        plan = self.make_plan([operation("action", "set-action-id", 0, 100, 999, 1001)])
        with self.assertRaisesRegex(BoundedPatchError, "old value"):
            self.apply(plan)
        self.assertFalse((self.artifacts / "evidence").exists())

    def test_rejects_escape_width_change(self) -> None:
        self.write_map(action_id=0x00FC)
        plan = self.make_plan([operation("action", "set-action-id", 0, 100, 0x00FC, 0x00FD)])
        with self.assertRaisesRegex(BoundedPatchError, "escape width"):
            self.apply(plan)
        self.assertFalse((self.artifacts / "patched.otbm").exists())

    def test_rejects_ambiguous_repeated_attribute(self) -> None:
        self.write_map(duplicate_action=True)
        plan = self.make_plan([operation("action", "set-action-id", 0, 100, 1000, 1001)])
        with self.assertRaisesRegex(BoundedPatchError, "ambiguous"):
            self.apply(plan)

    def test_rejects_existing_output_and_path_escape(self) -> None:
        self.write_map()
        plan = self.make_plan([operation("action", "set-action-id", 0, 100, 1000, 1001)])
        self.artifacts.mkdir()
        (self.artifacts / "patched.otbm").write_bytes(b"occupied")
        with self.assertRaisesRegex(BoundedPatchError, "already exists"):
            self.apply(plan)
        with self.assertRaisesRegex(BoundedPatchError, "escapes artifact root"):
            apply_bounded_patch(
                plan=plan,
                source_path=self.source,
                scanner_path=self.scanner,
                artifact_root=self.artifacts,
                output_path=Path("../escaped.otbm"),
                evidence_directory=Path("evidence-two"),
                result_path=Path("result-two.json"),
                timeout_seconds=60,
            )

    def test_post_validation_failure_removes_all_published_artifacts(self) -> None:
        self.write_map()
        original = self.source.read_bytes()
        plan = self.make_plan([operation("action", "set-action-id", 0, 100, 1000, 1001)])
        with mock.patch(
            "otbm_bounded_patch.analyze_index_paths",
            return_value={"format": "canary-otbm-semantic-diff-v1", "ok": True},
        ):
            with self.assertRaisesRegex(BoundedPatchError, "incomplete"):
                self.apply(plan)
        self.assertEqual(self.source.read_bytes(), original)
        self.assertFalse((self.artifacts / "patched.otbm").exists())
        self.assertFalse((self.artifacts / "evidence").exists())
        self.assertFalse((self.artifacts / "result.json").exists())

    def test_result_publication_failure_removes_output_and_evidence(self) -> None:
        self.write_map()
        original = self.source.read_bytes()
        plan = self.make_plan([operation("action", "set-action-id", 0, 100, 1000, 1001)])
        original_write_json = otbm_bounded_patch._write_json

        def fail_result(path: Path, value: object) -> None:
            if path.name == "result.json":
                raise OSError("simulated result publication failure")
            original_write_json(path, value)  # type: ignore[arg-type]

        with mock.patch("otbm_bounded_patch._write_json", side_effect=fail_result):
            with self.assertRaisesRegex(OSError, "simulated result publication failure"):
                self.apply(plan)
        self.assertEqual(self.source.read_bytes(), original)
        self.assertFalse((self.artifacts / "patched.otbm").exists())
        self.assertFalse((self.artifacts / "evidence").exists())
        self.assertFalse((self.artifacts / "result.json").exists())

    @unittest.skipUnless(hasattr(os, "symlink"), "symlinks are unavailable")
    def test_rejects_symlink_output(self) -> None:
        self.write_map()
        plan = self.make_plan([operation("action", "set-action-id", 0, 100, 1000, 1001)])
        self.artifacts.mkdir()
        target = self.temporary / "outside.otbm"
        os.symlink(target, self.artifacts / "patched.otbm")
        with self.assertRaisesRegex(BoundedPatchError, "symlink"):
            self.apply(plan)


class BoundedPatchPlanTests(unittest.TestCase):
    def test_rejects_operation_outside_region(self) -> None:
        raw = {
            "format": "canary-otbm-bounded-patch-plan-v1",
            "source": {
                "fileName": "map.otbm",
                "sha256": "0" * 64,
                "size": 10,
                "otbmVersion": 4,
                "itemsMajor": 3,
                "itemsMinor": 57,
            },
            "region": {"from": [1, 1, 7], "to": [2, 2, 7]},
            "operations": [operation("action", "set-action-id", 0, 100, 1, 2)],
        }
        with self.assertRaisesRegex(BoundedPatchError, "outside the bounded region"):
            PatchPlan.from_raw(raw)

    def test_rejects_duplicate_target(self) -> None:
        source = {
            "fileName": "map.otbm",
            "sha256": "0" * 64,
            "size": 10,
            "otbmVersion": 4,
            "itemsMajor": 3,
            "itemsMinor": 57,
        }
        first = operation("one", "set-action-id", 0, 100, 1, 2)
        second = operation("two", "set-action-id", 0, 100, 1, 3)
        raw = {
            "format": "canary-otbm-bounded-patch-plan-v1",
            "source": source,
            "region": {"from": [1000, 2000, 7], "to": [1100, 2200, 7]},
            "operations": [first, second],
        }
        with self.assertRaisesRegex(BoundedPatchError, "distinct attributes"):
            PatchPlan.from_raw(raw)


if __name__ == "__main__":
    unittest.main()
