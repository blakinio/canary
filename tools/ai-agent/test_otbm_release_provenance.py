from __future__ import annotations

import unittest

from otbm_release_provenance import ReleaseProvenanceError, build_release_provenance_report, normalize_bom


def _bom(release: str, *, map_sha: str = "a", appearance_sha: str = "b") -> dict:
    return {
        "format": "canary-otbm-release-bom-v1",
        "releaseId": release,
        "components": [
            {"id": "map", "kind": "source-map", "sha256": map_sha * 64},
            {"id": "appearances", "kind": "appearances", "sha256": appearance_sha * 64},
        ],
        "dimensions": [
            {"id": "reachability", "dependsOn": ["map", "appearances"]},
            {"id": "source-correlation", "dependsOn": ["map"]},
        ],
    }


class ReleaseProvenanceTests(unittest.TestCase):
    def test_no_previous_is_not_compared(self) -> None:
        report = build_release_provenance_report(_bom("r1"))
        self.assertFalse(report["summary"]["comparisonPerformed"])
        self.assertEqual({entry["status"] for entry in report["dimensionFreshness"]}, {"not-compared"})

    def test_appearance_change_stales_only_dependent_dimension(self) -> None:
        report = build_release_provenance_report(_bom("r2", appearance_sha="c"), _bom("r1"))
        statuses = {entry["dimensionId"]: entry for entry in report["dimensionFreshness"]}
        self.assertEqual(statuses["reachability"]["status"], "stale")
        self.assertEqual(statuses["source-correlation"]["status"], "current")
        self.assertEqual(statuses["reachability"]["changedDependencies"], ["appearances"])

    def test_added_component_is_change(self) -> None:
        previous = _bom("r1")
        current = _bom("r2")
        current["components"].append({"id": "assets", "kind": "asset-index", "sha256": "d" * 64})
        current["dimensions"].append({"id": "render", "dependsOn": ["assets", "appearances"]})
        report = build_release_provenance_report(current, previous)
        self.assertEqual(report["componentChanges"][0]["status"], "added")
        self.assertEqual(next(entry for entry in report["dimensionFreshness"] if entry["dimensionId"] == "render")["status"], "stale")

    def test_unknown_dimension_dependency_rejected(self) -> None:
        value = _bom("r1")
        value["dimensions"][0]["dependsOn"].append("missing")
        with self.assertRaises(ReleaseProvenanceError):
            normalize_bom(value)

    def test_timestamps_are_not_policy_evidence(self) -> None:
        report = build_release_provenance_report(_bom("r1"))
        self.assertFalse(report["policy"]["timestampsUsedAsFreshnessEvidence"])
        self.assertFalse(report["policy"]["runtimeCompatibilityProven"])

    def test_hash_is_deterministic(self) -> None:
        first = build_release_provenance_report(_bom("r1"))
        second = build_release_provenance_report(_bom("r1"))
        self.assertEqual(first["reportSha256"], second["reportSha256"])


if __name__ == "__main__":
    unittest.main()
