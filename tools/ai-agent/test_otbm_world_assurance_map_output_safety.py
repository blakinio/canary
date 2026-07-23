from __future__ import annotations

import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from otbm_world_assurance_map import (
    WorldAssuranceMapError,
    build_world_assurance_map_plan,
    canonical_sha256,
    materialize_world_assurance_map,
)
from otbm_world_assurance_map_tool import main as tool_main
from test_otbm_world_assurance_map import FILE_SHA, campaign


def _campaign_for_map(map_sha: str) -> dict:
    payload = campaign()
    payload["targets"][0]["exactProvenance"]["sourceMapSha256"] = map_sha
    payload["targets"][0]["physicalE2e"]["runtimeMapSha256"] = map_sha
    payload.pop("reportSha256")
    payload["reportSha256"] = canonical_sha256(payload)
    return payload


def _fake_renderer(source_map: Path, assets: Path, bounds, output: Path, *, padding_tiles: int, max_tiles: int):
    output.write_bytes(b"FAKE-PNG")
    return {
        "format": "canary-otbm-render-report-v1",
        "ok": True,
        "source": {
            "map": str(source_map),
            "mapSha256": hashlib.sha256(source_map.read_bytes()).hexdigest(),
            "assetsRoot": str(assets),
            "assetCatalogSha256": "4" * 64,
            "appearancesSha256": "5" * 64,
        },
        "bounds": {"from": list(bounds[0]), "to": list(bounds[1])},
        "output": {"path": str(output), "width": 736, "height": 832, "paddingPixels": 0},
        "summary": {
            "requestedPositions": 598,
            "mapTiles": 1,
            "renderedItems": 1,
            "renderedSprites": 1,
            "decodedSheetCount": 1,
            "missingAppearanceCount": 0,
            "missingSpriteCount": 0,
        },
        "decodedSheets": [],
        "warnings": [],
        "errors": [],
    }


class WorldAssuranceMapOutputSafetyTests(unittest.TestCase):
    def _fixture(self, root: Path):
        source_map = root / "world.otbm"
        source_map.write_bytes(b"synthetic-map")
        map_sha = hashlib.sha256(source_map.read_bytes()).hexdigest()
        assets = root / "assets"
        assets.mkdir()
        plan = build_world_assurance_map_plan(_campaign_for_map(map_sha), campaign_file_sha256=FILE_SHA)
        return source_map, assets, plan

    def test_materialization_uses_sibling_base_href_and_is_deterministic(self):
        with tempfile.TemporaryDirectory() as left_dir, tempfile.TemporaryDirectory() as right_dir:
            reports = []
            for raw in (left_dir, right_dir):
                root = Path(raw)
                source_map, assets, plan = self._fixture(root)
                report = materialize_world_assurance_map(
                    plan,
                    artifact_root=root,
                    map_path=source_map,
                    assets_root=assets,
                    output_directory=Path("out"),
                    renderer=_fake_renderer,
                )
                reports.append(report)
                target = report["targets"][0]
                svg_path = root / target["overlay"]["output"]
                svg = svg_path.read_text(encoding="utf-8")
                base_name = Path(target["baseRender"]["output"]).name
                self.assertIn(f'href="{base_name}"', svg)
                self.assertNotIn('href="out/out/', svg)
                self.assertIn("campaign:", svg)
                self.assertNotIn("polyline", svg.lower())
            self.assertEqual(reports[0], reports[1])

    def test_no_clobber_by_default_and_explicit_atomic_overwrite(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            source_map, assets, plan = self._fixture(root)
            first = materialize_world_assurance_map(
                plan,
                artifact_root=root,
                map_path=source_map,
                assets_root=assets,
                output_directory=Path("out"),
                renderer=_fake_renderer,
            )
            with self.assertRaisesRegex(WorldAssuranceMapError, "output already exists"):
                materialize_world_assurance_map(
                    plan,
                    artifact_root=root,
                    map_path=source_map,
                    assets_root=assets,
                    output_directory=Path("out"),
                    renderer=_fake_renderer,
                )
            second = materialize_world_assurance_map(
                plan,
                artifact_root=root,
                map_path=source_map,
                assets_root=assets,
                output_directory=Path("out"),
                overwrite=True,
                renderer=_fake_renderer,
            )
            self.assertEqual(first, second)

    def test_map_hash_mismatch_fails_before_renderer_runs(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            source_map, assets, _plan = self._fixture(root)
            plan = build_world_assurance_map_plan(campaign(), campaign_file_sha256=FILE_SHA)
            calls = []

            def renderer(*args, **kwargs):
                calls.append(True)
                return _fake_renderer(*args, **kwargs)

            with self.assertRaisesRegex(WorldAssuranceMapError, "source map SHA-256 does not match"):
                materialize_world_assurance_map(
                    plan,
                    artifact_root=root,
                    map_path=source_map,
                    assets_root=assets,
                    output_directory=Path("out"),
                    renderer=renderer,
                )
            self.assertEqual(calls, [])

    def test_output_directory_inside_assets_is_rejected(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            source_map, assets, plan = self._fixture(root)
            with self.assertRaisesRegex(WorldAssuranceMapError, "inside the client assets root"):
                materialize_world_assurance_map(
                    plan,
                    artifact_root=root,
                    map_path=source_map,
                    assets_root=assets,
                    output_directory=Path("assets/generated"),
                    renderer=_fake_renderer,
                )

    def test_tampered_plan_hash_is_rejected(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            source_map, assets, plan = self._fixture(root)
            plan["targets"][0]["status"] = "certified"
            with self.assertRaisesRegex(WorldAssuranceMapError, "plan reportSha256"):
                materialize_world_assurance_map(
                    plan,
                    artifact_root=root,
                    map_path=source_map,
                    assets_root=assets,
                    output_directory=Path("out"),
                    renderer=_fake_renderer,
                )

    @unittest.skipUnless(hasattr(os, "symlink"), "symlinks unavailable")
    def test_symlink_artifact_root_is_rejected(self):
        with tempfile.TemporaryDirectory() as raw:
            parent = Path(raw)
            real_root = parent / "real-root"
            real_root.mkdir()
            source_map, assets, plan = self._fixture(real_root)
            link = parent / "root-link"
            link.symlink_to(real_root, target_is_directory=True)
            with self.assertRaisesRegex(WorldAssuranceMapError, "artifact root must not be a symlink"):
                materialize_world_assurance_map(
                    plan,
                    artifact_root=link,
                    map_path=source_map,
                    assets_root=assets,
                    output_directory=Path("out"),
                    renderer=_fake_renderer,
                )

    @unittest.skipUnless(hasattr(os, "symlink"), "symlinks unavailable")
    def test_symlink_output_directory_is_rejected(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            source_map, assets, plan = self._fixture(root)
            real = root / "real-out"
            real.mkdir()
            link = root / "out-link"
            link.symlink_to(real, target_is_directory=True)
            with self.assertRaisesRegex(WorldAssuranceMapError, "must not be a symlink"):
                materialize_world_assurance_map(
                    plan,
                    artifact_root=root,
                    map_path=source_map,
                    assets_root=assets,
                    output_directory=link,
                    renderer=_fake_renderer,
                )

    def test_cli_resolves_relative_map_and_assets_under_artifact_root(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            source_map, assets, _plan = self._fixture(root)
            campaign_payload = _campaign_for_map(hashlib.sha256(source_map.read_bytes()).hexdigest())
            campaign_path = root / "campaign.json"
            campaign_path.write_text(json.dumps(campaign_payload), encoding="utf-8")
            with patch("otbm_world_assurance_map_tool.materialize_world_assurance_map") as mocked:
                mocked.side_effect = lambda plan, **kwargs: plan
                rc = tool_main(
                    [
                        "--campaign", str(campaign_path),
                        "--artifact-root", str(root),
                        "--output-dir", "out",
                        "--manifest", "manifest.json",
                        "--map", "world.otbm",
                        "--assets", "assets",
                        "--execute",
                    ]
                )
            self.assertEqual(rc, 0)

    def test_cli_rejects_manifest_collision_with_campaign_input(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            campaign_path = root / "campaign.json"
            campaign_path.write_text(json.dumps(campaign()), encoding="utf-8")
            rc = tool_main(
                [
                    "--campaign", str(campaign_path),
                    "--artifact-root", str(root),
                    "--output-dir", "out",
                    "--manifest", str(campaign_path),
                ]
            )
            self.assertEqual(rc, 2)
            loaded = json.loads(campaign_path.read_text(encoding="utf-8"))
            self.assertEqual(loaded["format"], "canary-otbm-world-assurance-campaign-v1")


if __name__ == "__main__":
    unittest.main()
