from __future__ import annotations

import unittest

from otbm_static_hotspots import HotspotContext, TileMetric, build_static_hotspot_report, normalize_policy


POLICY = {
    "format": "canary-otbm-static-hotspot-policy-v1",
    "sourceMapSha256": "a" * 64,
    "worldIndexSha256": "b" * 64,
    "thresholds": {
        "placementsPerTile": 5,
        "maxItemDepth": 4,
        "mechanicsPerTile": 2,
        "tilesPerArea": 2,
        "placementsPerArea": 8,
    },
}


def _context(metrics: list[TileMetric]) -> HotspotContext:
    return HotspotContext(normalize_policy(POLICY), tuple(metrics), {"sourceMapSha256": "a" * 64, "worldIndexSha256": "b" * 64})


class StaticHotspotTests(unittest.TestCase):
    def test_dense_tile_and_area_candidates(self) -> None:
        report = build_static_hotspot_report(
            _context([
                TileMetric((10, 10, 7), 6, 5, 2),
                TileMetric((11, 10, 7), 3, 1, 0),
            ])
        )
        codes = {entry["code"] for entry in report["candidates"]}
        self.assertEqual(codes, {"tile-placement-density", "tile-item-depth", "tile-mechanic-density", "area-tile-density", "area-placement-density"})
        self.assertFalse(report["policy"]["runtimePerformanceImpactProven"])

    def test_sparse_metrics_produce_no_candidates(self) -> None:
        report = build_static_hotspot_report(_context([TileMetric((10, 10, 7), 1, 0, 0)]))
        self.assertEqual(report["summary"]["candidateCount"], 0)

    def test_area_aggregation_is_floor_specific(self) -> None:
        report = build_static_hotspot_report(
            _context([
                TileMetric((10, 10, 7), 4, 0, 0),
                TileMetric((11, 10, 8), 4, 0, 0),
            ])
        )
        codes = [entry["code"] for entry in report["candidates"]]
        self.assertNotIn("area-placement-density", codes)
        self.assertNotIn("area-tile-density", codes)

    def test_policy_rejects_nonpositive_threshold(self) -> None:
        policy = {**POLICY, "thresholds": {**POLICY["thresholds"], "placementsPerTile": 0}}
        with self.assertRaises(Exception):
            normalize_policy(policy)

    def test_report_hash_is_deterministic(self) -> None:
        context = _context([TileMetric((10, 10, 7), 1, 0, 0)])
        self.assertEqual(build_static_hotspot_report(context)["reportSha256"], build_static_hotspot_report(context)["reportSha256"])


if __name__ == "__main__":
    unittest.main()
