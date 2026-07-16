from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from otbm_repair_preflight import build_preflight_report, diff_script_resolution_placements
from otbm_repair_preflight_tool import _build_input_pins, _repository_git_pin, _script_corpus_pin


def _item_audit(status_value: int = 1000) -> dict:
    return {
        "format": "canary-otbm-item-audit-v1",
        "mechanicPlacements": [
            {
                "itemId": 100,
                "position": [1025, 2050, 7],
                "itemDepth": 0,
                "actionId": status_value,
            }
        ],
    }


def _anchors(value: int = 1000) -> dict:
    return {
        "format": "canary-otbm-patch-anchors-native-v1",
        "source": {
            "path": "world.otbm",
            "size": 123,
            "otbmVersion": 4,
            "itemsMajor": 3,
            "itemsMinor": 57,
        },
        "anchors": [
            {
                "position": [1025, 2050, 7],
                "tilePlacementIndex": 3,
                "itemId": 100,
                "itemDepth": 0,
                "attribute": "actionId",
                "value": value,
                "bytes": [],
            }
        ],
    }


def _resolution(status: str = "handled-directly") -> dict:
    return {
        "format": "canary-otbm-script-resolution-v1",
        "placements": [
            {
                "index": 0,
                "itemId": 100,
                "position": [1025, 2050, 7],
                "depth": 0,
                "status": status,
                "resolutions": {
                    "actionId": {
                        "status": status,
                        "handlers": [],
                    }
                },
                "selectedByEvent": {},
                "handlers": [],
                "shadowedHandlers": [],
                "references": [],
            }
        ],
    }


def _source() -> dict:
    return {
        "fileName": "world.otbm",
        "sha256": "a" * 64,
        "size": 123,
        "otbmVersion": 4,
        "itemsMajor": 3,
        "itemsMinor": 57,
    }


class ReadinessTests(unittest.TestCase):
    def test_exact_handled_candidate_exposes_explicit_readiness(self) -> None:
        report = build_preflight_report(
            item_audit=_item_audit(),
            anchor_report=_anchors(),
            script_resolution=_resolution(),
            selector={"actionId": 1000},
            source=_source(),
            operation_kind="set-action-id",
            replacement=1001,
        )

        readiness = report["summary"]["readiness"]
        self.assertTrue(report["ok"])
        self.assertTrue(readiness["matched"])
        self.assertTrue(readiness["correlated"])
        self.assertTrue(readiness["runtimeResolved"])
        self.assertEqual(readiness["runtimeStatus"], "handled-directly")
        self.assertTrue(readiness["patchable"])
        self.assertTrue(readiness["reviewReady"])

    def test_unresolved_candidate_can_be_patchable_without_being_runtime_resolved(self) -> None:
        report = build_preflight_report(
            item_audit=_item_audit(),
            anchor_report=_anchors(),
            script_resolution=_resolution("unresolved"),
            selector={"actionId": 1000},
            source=_source(),
            operation_kind="set-action-id",
            replacement=1001,
        )

        readiness = report["summary"]["readiness"]
        self.assertTrue(readiness["matched"])
        self.assertTrue(readiness["correlated"])
        self.assertFalse(readiness["runtimeResolved"])
        self.assertTrue(readiness["patchable"])
        self.assertTrue(readiness["reviewReady"])
        self.assertEqual(report["summary"]["runtimeUnresolvedCandidates"], 1)

    def test_multiple_candidates_are_matched_but_not_correlated_or_patchable(self) -> None:
        audit = _item_audit()
        audit["mechanicPlacements"].append(
            {"itemId": 100, "position": [1026, 2050, 7], "itemDepth": 0, "actionId": 1000}
        )
        anchor = _anchors()
        anchor["anchors"].append(
            {
                "position": [1026, 2050, 7],
                "tilePlacementIndex": 1,
                "itemId": 100,
                "itemDepth": 0,
                "attribute": "actionId",
                "value": 1000,
                "bytes": [],
            }
        )
        script = _resolution()
        script["placements"].append(
            {
                "index": 1,
                "itemId": 100,
                "position": [1026, 2050, 7],
                "depth": 0,
                "status": "handled-directly",
                "resolutions": {},
            }
        )
        report = build_preflight_report(
            item_audit=audit,
            anchor_report=anchor,
            script_resolution=script,
            selector={"actionId": 1000},
            source=_source(),
            operation_kind="set-action-id",
            replacement=1001,
        )

        readiness = report["summary"]["readiness"]
        self.assertTrue(readiness["matched"])
        self.assertFalse(readiness["correlated"])
        self.assertFalse(readiness["runtimeResolved"])
        self.assertFalse(readiness["patchable"])
        self.assertFalse(readiness["reviewReady"])


class RuntimeDiffTests(unittest.TestCase):
    def test_same_status_handler_change_is_detected(self) -> None:
        before = {
            "status": "handled-directly",
            "resolutions": {
                "actionId": {
                    "status": "handled-directly",
                    "handlers": [
                        {
                            "eventType": "Action:onUse",
                            "handler": "first",
                            "mode": "literal",
                            "confidence": "high",
                            "source": {"path": "data/a.lua", "line": 10, "context": "a"},
                        }
                    ],
                }
            },
            "handlers": [],
            "references": [],
        }
        after = {
            "status": "handled-directly",
            "resolutions": {
                "actionId": {
                    "status": "handled-directly",
                    "handlers": [
                        {
                            "eventType": "Action:onUse",
                            "handler": "second",
                            "mode": "literal",
                            "confidence": "medium",
                            "source": {"path": "data/b.lua", "line": 20, "context": "b"},
                        }
                    ],
                }
            },
            "handlers": [],
            "references": [],
        }

        diff = diff_script_resolution_placements(before, after)

        self.assertTrue(diff["changed"])
        self.assertNotEqual(diff["beforeFingerprint"], diff["afterFingerprint"])
        self.assertTrue(any(change["path"].startswith("resolutions.actionId.handlers") for change in diff["changes"]))

    def test_handler_order_alone_does_not_change_runtime_fingerprint(self) -> None:
        handler_a = {"handler": "a", "source": {"path": "a.lua", "line": 1}}
        handler_b = {"handler": "b", "source": {"path": "b.lua", "line": 2}}
        before = {"status": "handled-multiple", "handlers": [handler_a, handler_b]}
        after = {"status": "handled-multiple", "handlers": [handler_b, handler_a]}

        diff = diff_script_resolution_placements(before, after)

        self.assertFalse(diff["changed"])
        self.assertEqual(diff["beforeFingerprint"], diff["afterFingerprint"])


class EvidencePinTests(unittest.TestCase):
    def test_script_corpus_pin_is_deterministic_and_content_sensitive(self) -> None:
        with tempfile.TemporaryDirectory(prefix="otbm-preflight-pins-") as temporary:
            root = Path(temporary)
            scripts = root / "data" / "scripts"
            scripts.mkdir(parents=True)
            first = scripts / "a.lua"
            second = scripts / "b.xml"
            first.write_text("return true\n", encoding="utf-8")
            second.write_text("<actions/>\n", encoding="utf-8")
            ignored = root / "data" / "node_modules" / "ignored.lua"
            ignored.parent.mkdir(parents=True)
            ignored.write_text("ignored\n", encoding="utf-8")

            before = _script_corpus_pin(root, ["data"])
            repeat = _script_corpus_pin(root, ["data"])
            self.assertEqual(before, repeat)
            self.assertEqual(before["files"], 2)

            first.write_text("return false\n", encoding="utf-8")
            after = _script_corpus_pin(root, ["data"])
            self.assertNotEqual(before["sha256"], after["sha256"])

    def test_non_git_repository_is_reported_as_unknown_not_clean(self) -> None:
        with tempfile.TemporaryDirectory(prefix="otbm-preflight-git-pin-") as temporary:
            pin = _repository_git_pin(Path(temporary))
            self.assertFalse(pin["available"])
            self.assertIsNone(pin["commit"])
            self.assertIsNone(pin["branch"])
            self.assertIsNone(pin["dirty"])

    def test_input_pins_cover_required_metadata_and_script_corpus(self) -> None:
        with tempfile.TemporaryDirectory(prefix="otbm-preflight-input-pins-") as temporary:
            root = Path(temporary)
            appearances = root / "appearances.json"
            items = root / "items.xml"
            rules = root / "rules.json"
            scripts = root / "data" / "scripts"
            scripts.mkdir(parents=True)
            appearances.write_text("{}\n", encoding="utf-8")
            items.write_text("<items/>\n", encoding="utf-8")
            rules.write_text("{}\n", encoding="utf-8")
            (scripts / "action.lua").write_text("return true\n", encoding="utf-8")

            pins = _build_input_pins(
                appearances_index=appearances,
                items_xml=items,
                repository_root=root,
                script_roots=["data"],
                rules=rules,
                review_rules=None,
            )

            self.assertEqual(pins["appearancesIndex"]["fileName"], "appearances.json")
            self.assertEqual(len(pins["appearancesIndex"]["sha256"]), 64)
            self.assertEqual(pins["itemsXml"]["fileName"], "items.xml")
            self.assertEqual(pins["rules"]["fileName"], "rules.json")
            self.assertIsNone(pins["reviewRules"])
            self.assertEqual(pins["scriptCorpus"]["files"], 1)
            self.assertEqual(len(pins["scriptCorpus"]["sha256"]), 64)


if __name__ == "__main__":
    unittest.main()
