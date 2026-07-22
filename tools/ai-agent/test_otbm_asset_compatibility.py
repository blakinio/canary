from __future__ import annotations

import unittest

from otbm_asset_compatibility import AssetCompatibilityContext, build_asset_compatibility_report


def _appearance(item_id: int, *, sprite_id: int = 10, unpassable: bool = False, ground: bool = False) -> dict:
    flags = {"unpassable": True} if unpassable else {}
    if ground:
        flags["bank"] = {"waypoints": 1}
    return {
        "category": "object",
        "id": item_id,
        "flags": flags,
        "frameGroups": [{"spriteInfo": {"spriteIds": [sprite_id]}}],
    }


def _context(*, used=(100,), appearances=None, assets=None, baseline=None) -> AssetCompatibilityContext:
    return AssetCompatibilityContext(
        manifest={"format": "canary-otbm-asset-compatibility-manifest-v1"},
        world_manifest={"format": "canary-otbm-world-index-v1"},
        used_item_ids=tuple(used),
        appearances={"format": "canary-appearances-index-v1", "appearances": appearances or [_appearance(100)]},
        assets={
            "format": "canary-client-assets-index-v1",
            "sprites": assets if assets is not None else [{"firstSpriteId": 1, "lastSpriteId": 100, "exists": True, "relativePath": "sprites-1.dat"}],
        },
        baseline_appearances={"format": "canary-appearances-index-v1", "appearances": baseline} if baseline is not None else None,
        provenance={"sourceMapSha256": "a" * 64, "worldIndexSha256": "b" * 64, "appearancesSha256": "c" * 64, "assetIndexSha256": "d" * 64, "baselineAppearancesSha256": None},
    )


class AssetCompatibilityTests(unittest.TestCase):
    def test_clean_used_item_is_compatible(self) -> None:
        report = build_asset_compatibility_report(_context())
        self.assertTrue(report["ok"])
        self.assertEqual(report["summary"]["findings"], 0)
        self.assertFalse(report["scope"]["baselineCompared"])

    def test_missing_used_appearance_is_error(self) -> None:
        report = build_asset_compatibility_report(_context(used=(100, 101), appearances=[_appearance(100)]))
        self.assertFalse(report["ok"])
        self.assertEqual(report["summary"]["missingObjectAppearances"], 1)
        self.assertEqual(report["findings"][0]["code"], "missing-object-appearance")

    def test_uncovered_sprite_is_error(self) -> None:
        report = build_asset_compatibility_report(_context(appearances=[_appearance(100, sprite_id=999)]))
        self.assertFalse(report["ok"])
        self.assertEqual(report["summary"]["uncoveredSpriteIds"], 1)

    def test_missing_covering_asset_file_is_error(self) -> None:
        report = build_asset_compatibility_report(
            _context(assets=[{"firstSpriteId": 1, "lastSpriteId": 100, "exists": False, "relativePath": "missing.dat"}])
        )
        self.assertFalse(report["ok"])
        self.assertEqual(report["summary"]["missingSpriteAssetFiles"], 1)

    def test_used_walkability_flag_delta_is_reported(self) -> None:
        report = build_asset_compatibility_report(
            _context(appearances=[_appearance(100, unpassable=True)], baseline=[_appearance(100, unpassable=False)])
        )
        self.assertTrue(report["ok"])
        self.assertEqual(report["summary"]["appearanceSemanticDeltas"], 1)
        finding = next(entry for entry in report["findings"] if entry["code"] == "appearance-semantics-changed")
        self.assertEqual(finding["changedFlags"], ["unpassable"])

    def test_unused_baseline_delta_is_not_reported(self) -> None:
        report = build_asset_compatibility_report(
            _context(used=(100,), appearances=[_appearance(100), _appearance(200, unpassable=True)], baseline=[_appearance(100), _appearance(200)])
        )
        self.assertEqual(report["summary"]["appearanceSemanticDeltas"], 0)

    def test_report_hash_is_deterministic(self) -> None:
        first = build_asset_compatibility_report(_context())
        second = build_asset_compatibility_report(_context())
        self.assertEqual(first["reportSha256"], second["reportSha256"])


if __name__ == "__main__":
    unittest.main()
