from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from otbm_map_quality import MapQualityError, build_quality_report
from otbm_map_quality_tool import main as quality_main

MAP_SHA = "a" * 64
OTHER_SHA = "b" * 64


def _pin(report_format: str, name: str) -> dict:
    return {
        "fileName": name,
        "size": 123,
        "sha256": "c" * 64,
        "format": report_format,
    }


def geometry_report(*, source_sha: str = MAP_SHA, by_severity: dict | None = None, findings: list | None = None) -> dict:
    counts = by_severity or {"error": 0, "warning": 0, "info": 0}
    rows = findings or []
    return {
        "format": "canary-otbm-geometry-audit-v1",
        "schemaVersion": 1,
        "ok": counts.get("error", 0) == 0,
        "complete": True,
        "policy": {},
        "scope": {"from": [100, 100, 7], "to": [110, 110, 7]},
        "provenance": {"source": {"path": "world.otbm", "size": 1, "sha256": source_sha}},
        "summary": {
            "findings": {
                "total": sum(counts.values()),
                "byKind": {},
                "bySeverity": counts,
                "byConfidence": {},
                "sampled": len(rows),
                "truncated": sum(counts.values()) > len(rows),
            }
        },
        "rules": [],
        "findings": rows,
    }


def reachability_report(
    *,
    source_sha: str = MAP_SHA,
    by_severity: dict | None = None,
    findings: list | None = None,
    region_from: list[int] | None = None,
) -> dict:
    counts = by_severity or {"error": 0, "warning": 0, "info": 0}
    rows = findings or []
    return {
        "format": "canary-otbm-reachability-v1",
        "schemaVersion": 1,
        "ok": counts.get("error", 0) == 0,
        "provenance": {
            "worldIndex": {"sha256": "d" * 64},
            "worldIndexManifest": {
                "source": {"path": "world.otbm", "size": 1, "sha256": source_sha},
                "index": {"sha256": "d" * 64},
            },
        },
        "region": {"from": region_from or [100, 100, 7], "to": [110, 110, 7]},
        "policy": {},
        "summary": {
            "findings": {
                "total": sum(counts.values()),
                "bySeverity": counts,
                "byCode": {},
                "truncated": sum(counts.values()) > len(rows),
            }
        },
        "routes": [],
        "transitions": [],
        "transitionsTruncated": False,
        "transitionLoops": [],
        "transitionLoopsTruncated": False,
        "mechanics": [],
        "mechanicsTruncated": False,
        "tileDiagnostics": [],
        "tileDiagnosticsTruncated": False,
        "findings": rows,
    }


def script_report(
    *,
    source_sha: str = MAP_SHA,
    placements: list | None = None,
    unreviewed_identifiers: int = 0,
) -> dict:
    rows = placements or []
    conflicts = sum(row.get("status") == "conflicting" for row in rows)
    unresolved = sum(
        row.get("status") in {"unresolved", "referenced-only", "partially-resolved"}
        for row in rows
    )
    return {
        "format": "canary-otbm-script-resolution-v1",
        "ok": conflicts == 0 and unreviewed_identifiers == 0,
        "sources": {
            "itemAudit": {
                "map": {"path": "world.otbm", "size": 1, "sha256": source_sha},
            },
            "repositoryRoot": ".",
            "scriptRoots": ["data"],
        },
        "summary": {
            "conflictingPlacements": conflicts,
            "runtimeUnresolvedPlacements": unresolved,
            "unreviewedIdentifiers": unreviewed_identifiers,
            "unresolvedDynamicRegistrations": 0,
        },
        "placements": rows,
    }


def input_pins() -> dict:
    return {
        "geometry": _pin("canary-otbm-geometry-audit-v1", "geometry.json"),
        "reachability": _pin("canary-otbm-reachability-v1", "reachability.json"),
        "scriptResolution": _pin("canary-otbm-script-resolution-v1", "script.json"),
    }


class SourceIdentityTests(unittest.TestCase):
    def test_mismatched_component_map_sha_fails_closed(self) -> None:
        with self.assertRaisesRegex(MapQualityError, "do not prove the same source map"):
            build_quality_report(
                geometry=geometry_report(),
                reachability=reachability_report(source_sha=OTHER_SHA),
                script_resolution=script_report(),
                input_pins=input_pins(),
            )

    def test_missing_reachability_world_manifest_source_fails_closed(self) -> None:
        report = reachability_report()
        del report["provenance"]["worldIndexManifest"]
        with self.assertRaisesRegex(MapQualityError, "worldIndexManifest"):
            build_quality_report(
                geometry=geometry_report(),
                reachability=report,
                script_resolution=script_report(),
                input_pins=input_pins(),
            )


class AggregationTests(unittest.TestCase):
    def test_exact_summary_counts_do_not_depend_on_component_samples(self) -> None:
        geometry = geometry_report(
            by_severity={"error": 1, "warning": 2, "info": 3},
            findings=[
                {
                    "id": "1" * 24,
                    "kind": "item-without-floor",
                    "severity": "error",
                    "confidence": "high",
                    "message": "missing floor",
                    "position": [102, 101, 7],
                }
            ],
        )
        reachability = reachability_report(
            by_severity={"error": 0, "warning": 1, "info": 0},
            findings=[
                {
                    "severity": "warning",
                    "code": "one-way-transition",
                    "message": "one way",
                    "source": [101, 101, 7],
                }
            ],
        )
        script = script_report(
            placements=[
                {
                    "index": 0,
                    "itemId": 100,
                    "position": [104, 100, 7],
                    "depth": 0,
                    "status": "conflicting",
                    "resolutions": {},
                },
                {
                    "index": 1,
                    "itemId": 101,
                    "position": [105, 100, 7],
                    "depth": 0,
                    "status": "unresolved",
                    "resolutions": {},
                },
                {
                    "index": 2,
                    "itemId": 102,
                    "position": [106, 100, 7],
                    "depth": 0,
                    "status": "partially-resolved",
                    "resolutions": {},
                },
            ]
        )
        report = build_quality_report(
            geometry=geometry,
            reachability=reachability,
            script_resolution=script,
            input_pins=input_pins(),
            sample_limit=2,
        )
        self.assertEqual(
            report["summary"]["outcomeCounts"],
            {"error": 2, "warning": 3, "unresolved": 2, "info": 3},
        )
        self.assertEqual(report["summary"]["total"], 10)
        self.assertEqual(report["summary"]["sampled"], 2)
        self.assertTrue(report["summary"]["truncated"])
        self.assertFalse(report["ok"])

    def test_reviewed_unresolved_is_not_promoted_to_handled(self) -> None:
        script = script_report(
            placements=[
                {
                    "index": 0,
                    "itemId": 100,
                    "position": [100, 100, 7],
                    "depth": 0,
                    "status": "unresolved",
                    "resolutions": {"actionId": {"status": "unresolved"}},
                }
            ],
            unreviewed_identifiers=0,
        )
        report = build_quality_report(
            geometry=geometry_report(),
            reachability=reachability_report(),
            script_resolution=script,
            input_pins=input_pins(),
        )
        self.assertTrue(report["ok"])
        self.assertEqual(report["summary"]["outcomeCounts"]["unresolved"], 1)
        self.assertEqual(report["findings"][0]["outcome"], "unresolved")

    def test_unresolved_gate_is_independent_from_severity_gate(self) -> None:
        script = script_report(
            placements=[
                {
                    "index": 0,
                    "itemId": 100,
                    "position": [100, 100, 7],
                    "depth": 0,
                    "status": "referenced-only",
                    "resolutions": {},
                }
            ]
        )
        default_report = build_quality_report(
            geometry=geometry_report(),
            reachability=reachability_report(),
            script_resolution=script,
            input_pins=input_pins(),
        )
        strict_report = build_quality_report(
            geometry=geometry_report(),
            reachability=reachability_report(),
            script_resolution=script,
            input_pins=input_pins(),
            fail_on_unresolved=True,
        )
        self.assertTrue(default_report["ok"])
        self.assertFalse(strict_report["ok"])

    def test_warning_threshold_and_sample_order_are_deterministic(self) -> None:
        geometry = geometry_report(
            by_severity={"error": 0, "warning": 1, "info": 0},
            findings=[
                {
                    "id": "2" * 24,
                    "kind": "warning-b",
                    "severity": "warning",
                    "confidence": "medium",
                    "message": "b",
                    "position": [110, 100, 7],
                }
            ],
        )
        reachability = reachability_report(
            by_severity={"error": 1, "warning": 0, "info": 0},
            findings=[
                {
                    "severity": "error",
                    "code": "error-a",
                    "message": "a",
                    "source": [105, 100, 7],
                }
            ],
        )
        first = build_quality_report(
            geometry=geometry,
            reachability=reachability,
            script_resolution=script_report(),
            input_pins=input_pins(),
            fail_on_severity="warning",
        )
        second = build_quality_report(
            geometry=geometry,
            reachability=reachability,
            script_resolution=script_report(),
            input_pins=input_pins(),
            fail_on_severity="warning",
        )
        self.assertFalse(first["ok"])
        self.assertEqual(first["findings"], second["findings"])
        self.assertEqual(first["findings"][0]["outcome"], "error")
        self.assertEqual(first["findings"][1]["outcome"], "warning")
        self.assertTrue(first["coverage"]["sameRegion"])

    def test_different_bounded_regions_are_reported_not_guessed_as_global(self) -> None:
        report = build_quality_report(
            geometry=geometry_report(),
            reachability=reachability_report(region_from=[101, 100, 7]),
            script_resolution=script_report(),
            input_pins=input_pins(),
        )
        self.assertFalse(report["coverage"]["sameRegion"])
        self.assertFalse(report["coverage"]["globalCoverageProven"])


class CliTests(unittest.TestCase):
    def _write_inputs(self, root: Path, *, unresolved: bool = False) -> tuple[Path, Path, Path]:
        geometry = root / "geometry.json"
        reachability = root / "reachability.json"
        script = root / "script.json"
        geometry.write_text(json.dumps(geometry_report()), encoding="utf-8")
        reachability.write_text(json.dumps(reachability_report()), encoding="utf-8")
        placements = []
        if unresolved:
            placements.append(
                {
                    "index": 0,
                    "itemId": 100,
                    "position": [100, 100, 7],
                    "depth": 0,
                    "status": "unresolved",
                    "resolutions": {},
                }
            )
        script.write_text(json.dumps(script_report(placements=placements)), encoding="utf-8")
        return geometry, reachability, script

    def test_cli_writes_pinned_report_and_respects_unresolved_exit_policy(self) -> None:
        with tempfile.TemporaryDirectory(prefix="otbm-map-quality-cli-") as temporary:
            root = Path(temporary)
            geometry, reachability, script = self._write_inputs(root, unresolved=True)
            output = root / "quality.json"
            result = quality_main(
                [
                    "--geometry",
                    str(geometry),
                    "--reachability",
                    str(reachability),
                    "--script-resolution",
                    str(script),
                    "--output",
                    str(output),
                    "--fail-on-unresolved",
                ]
            )
            self.assertEqual(result, 2)
            report = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(report["format"], "canary-otbm-map-quality-v1")
            self.assertEqual(report["source"]["sha256"], MAP_SHA)
            self.assertEqual(report["components"]["geometry"]["input"]["format"], "canary-otbm-geometry-audit-v1")
            self.assertEqual(len(report["components"]["geometry"]["input"]["sha256"]), 64)
            self.assertEqual(report["summary"]["outcomeCounts"]["unresolved"], 1)

    def test_cli_rejects_output_equal_to_input(self) -> None:
        with tempfile.TemporaryDirectory(prefix="otbm-map-quality-cli-collision-") as temporary:
            root = Path(temporary)
            geometry, reachability, script = self._write_inputs(root)
            with self.assertRaises(SystemExit):
                quality_main(
                    [
                        "--geometry",
                        str(geometry),
                        "--reachability",
                        str(reachability),
                        "--script-resolution",
                        str(script),
                        "--output",
                        str(geometry),
                    ]
                )


if __name__ == "__main__":
    unittest.main()
