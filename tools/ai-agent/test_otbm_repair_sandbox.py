from __future__ import annotations

import json
import shutil
import struct
import subprocess
import tempfile
import unittest
from pathlib import Path

from otbm_binary import (
    ATTR_ACTION_ID,
    OTBM_ITEM,
    OTBM_MAP_DATA,
    OTBM_TILE,
    OTBM_TILE_AREA,
    encode_item_attributes,
    encode_node,
    encode_tile_properties,
)
from otbm_bounded_patch_types import PatchPlan, sha256_file
from otbm_repair_sandbox import RepairSandboxError, validate_phase8_result
from otbm_repair_sandbox_tool import main as sandbox_main


class Phase8ResultValidationTests(unittest.TestCase):
    def test_rejects_missing_confinement_proof(self) -> None:
        plan = PatchPlan.from_raw(
            {
                "format": "canary-otbm-bounded-patch-plan-v1",
                "source": {
                    "fileName": "world.otbm",
                    "sha256": "a" * 64,
                    "size": 100,
                    "otbmVersion": 4,
                    "itemsMajor": 4,
                    "itemsMinor": 4,
                },
                "region": {"from": [300, 600, 7], "to": [300, 600, 7]},
                "operations": [
                    {
                        "id": "action",
                        "kind": "set-action-id",
                        "position": [300, 600, 7],
                        "tilePlacementIndex": 0,
                        "itemId": 100,
                        "itemDepth": 0,
                        "expected": 1000,
                        "replacement": 1001,
                    }
                ],
            }
        )
        result = {
            "format": "canary-otbm-bounded-patch-result-v1",
            "ok": True,
            "plan": {"format": "canary-otbm-bounded-patch-plan-v1", "sha256": "b" * 64},
            "source": {"sha256": "a" * 64, "size": 100, "unchanged": True},
            "output": {"atomicCopyOnly": True},
            "proof": {
                "fileLengthPreserved": True,
                "outsideScannerSpansEqual": True,
                "fullScannerReparse": True,
                "worldIndexBeforeAfterBuilt": True,
                "boundedSemanticDiffExact": False,
            },
            "operations": [
                {
                    "id": "action",
                    "kind": "set-action-id",
                    "position": [300, 600, 7],
                    "tilePlacementIndex": 0,
                    "itemId": 100,
                    "itemDepth": 0,
                    "attribute": "actionId",
                    "expected": 1000,
                    "replacement": 1001,
                }
            ],
            "policy": {
                "sourceModifiedInPlace": False,
                "newOtbmParserCreated": False,
                "existingNativeScannerReused": True,
                "existingWorldIndexReused": True,
                "existingSemanticDiffReused": True,
            },
        }
        with self.assertRaisesRegex(RepairSandboxError, "boundedSemanticDiffExact"):
            validate_phase8_result(result, plan)


@unittest.skipUnless(shutil.which("c++") or shutil.which("g++"), "a C++ compiler is required")
class RepairSandboxIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.compiler = shutil.which("c++") or shutil.which("g++")
        cls.build = tempfile.TemporaryDirectory(prefix="otbm-repair-sandbox-scanner-")
        cls.scanner = Path(cls.build.name) / "otbm_item_audit_scan"
        scanner_source = Path(__file__).with_name("otbm_item_audit_scan.cpp")
        completed = subprocess.run(
            [
                str(cls.compiler),
                "-O2",
                "-std=c++20",
                "-Wall",
                "-Wextra",
                "-Wpedantic",
                "-Werror",
                str(scanner_source),
                "-o",
                str(cls.scanner),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode != 0:
            raise RuntimeError(completed.stderr or completed.stdout)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.build.cleanup()

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="otbm-repair-sandbox-test-")
        self.root = Path(self.temporary.name)
        self.source = self.root / "source.otbm"
        self.plan = self.root / "plan.json"
        self.appearances = self.root / "appearances.json"
        self.items_xml = self.root / "items.xml"
        self.repository = self.root / "repository"
        self.artifacts = self.root / "artifacts"
        self._write_map()
        self._write_metadata()
        self._write_script()
        self._write_plan()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _write_map(self) -> None:
        item = encode_node(
            OTBM_ITEM,
            struct.pack("<H", 100) + encode_item_attributes([{"type": ATTR_ACTION_ID, "value": 1000}]),
        )
        tile = encode_node(
            OTBM_TILE,
            encode_tile_properties(
                node_type=OTBM_TILE,
                offset_x=44,
                offset_y=88,
                house_id=None,
                flags=0,
                inline_item_id=None,
            ),
            [item],
        )
        area = encode_node(OTBM_TILE_AREA, struct.pack("<HHB", 256, 512, 7), [tile])
        map_data = encode_node(OTBM_MAP_DATA, b"", [area])
        root = encode_node(0, struct.pack("<IHHII", 4, 1024, 1024, 4, 4), [map_data])
        self.source.write_bytes(b"\0\0\0\0" + root)

    def _write_metadata(self) -> None:
        self.appearances.write_text(
            json.dumps(
                {
                    "format": "canary-appearances-index-v1",
                    "ok": True,
                    "source": {"path": "appearances.dat", "size": 1, "sha256": "0" * 64},
                    "appearances": [
                        {
                            "category": "object",
                            "id": 100,
                            "name": "test action item",
                            "frameGroups": [],
                            "flags": {"usable": True},
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        self.items_xml.write_text('<items><item id="100" name="test action item"/></items>', encoding="utf-8")

    def _write_script(self) -> None:
        script = self.repository / "data" / "scripts" / "actions" / "test_action.lua"
        script.parent.mkdir(parents=True)
        script.write_text(
            "local action = Action()\n"
            "function action.onUse(player, item, fromPosition, target, toPosition, isHotkey)\n"
            "    return true\n"
            "end\n"
            "action:aid(1000)\n"
            "action:register()\n",
            encoding="utf-8",
        )

    def _write_plan(self) -> None:
        self.plan.write_text(
            json.dumps(
                {
                    "format": "canary-otbm-bounded-patch-plan-v1",
                    "source": {
                        "fileName": self.source.name,
                        "sha256": sha256_file(self.source),
                        "size": self.source.stat().st_size,
                        "otbmVersion": 4,
                        "itemsMajor": 4,
                        "itemsMinor": 4,
                    },
                    "region": {"from": [300, 600, 7], "to": [300, 600, 7]},
                    "operations": [
                        {
                            "id": "repair-action",
                            "kind": "set-action-id",
                            "position": [300, 600, 7],
                            "tilePlacementIndex": 0,
                            "itemId": 100,
                            "itemDepth": 0,
                            "expected": 1000,
                            "replacement": 1001,
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )

    def test_real_phase8_copy_is_audited_and_source_remains_unchanged(self) -> None:
        original = self.source.read_bytes()
        result = sandbox_main(
            [
                str(self.source),
                str(self.plan),
                "--scanner",
                str(self.scanner),
                "--artifact-root",
                str(self.artifacts),
                "--appearances-index",
                str(self.appearances),
                "--items-xml",
                str(self.items_xml),
                "--repository-root",
                str(self.repository),
                "--script-root",
                "data",
                "--timeout",
                "60",
            ]
        )
        self.assertEqual(result, 0)
        self.assertEqual(self.source.read_bytes(), original)

        verification = json.loads((self.artifacts / "sandbox-verification.json").read_text(encoding="utf-8"))
        self.assertEqual(verification["format"], "canary-otbm-repair-sandbox-verification-v1")
        self.assertTrue(verification["ok"])
        self.assertTrue(verification["source"]["unchanged"])
        self.assertTrue(verification["phase8"]["proof"]["boundedSemanticDiffExact"])
        self.assertEqual(verification["summary"]["operations"], 1)
        self.assertEqual(verification["summary"]["runtimeRegressionOperations"], 1)
        operation = verification["operations"][0]
        self.assertEqual(operation["before"]["placement"]["actionId"], 1000)
        self.assertEqual(operation["after"]["placement"]["actionId"], 1001)
        self.assertEqual(operation["before"]["runtimeStatus"], "handled-directly")
        self.assertEqual(operation["after"]["runtimeStatus"], "unresolved")
        self.assertTrue(operation["runtimeResolutionChanged"])
        self.assertTrue(operation["runtimeRegression"])
        self.assertFalse(operation["replacementRuntimeResolved"])
        self.assertTrue((self.artifacts / "patched.otbm").is_file())
        self.assertTrue((self.artifacts / "phase8-evidence" / "semantic-diff.json").is_file())

    def test_existing_verification_output_fails_before_phase8_publication(self) -> None:
        self.artifacts.mkdir()
        (self.artifacts / "sandbox-verification.json").write_text("occupied\n", encoding="utf-8")
        with self.assertRaises(SystemExit):
            sandbox_main(
                [
                    str(self.source),
                    str(self.plan),
                    "--scanner",
                    str(self.scanner),
                    "--artifact-root",
                    str(self.artifacts),
                    "--appearances-index",
                    str(self.appearances),
                    "--items-xml",
                    str(self.items_xml),
                    "--repository-root",
                    str(self.repository),
                    "--script-root",
                    "data",
                    "--timeout",
                    "60",
                ]
            )
        self.assertFalse((self.artifacts / "patched.otbm").exists())
        self.assertFalse((self.artifacts / "phase8-result.json").exists())


if __name__ == "__main__":
    unittest.main()
