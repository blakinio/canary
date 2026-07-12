from __future__ import annotations

import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from manifest import DeploymentManifest, build_file_entries, read_manifest, sha256_file


class ManifestTests(unittest.TestCase):
    def test_sha256_file_matches_hashlib(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.txt"
            content = b"hello canary"
            path.write_bytes(content)
            self.assertEqual(sha256_file(path), hashlib.sha256(content).hexdigest())

    def test_build_file_entries_covers_nested_files_sorted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "npc").mkdir()
            (root / "npc" / "b.lua").write_text("b", encoding="utf-8")
            (root / "npc" / "a.lua").write_text("a", encoding="utf-8")
            (root / "top.lua").write_text("top", encoding="utf-8")

            entries = build_file_entries(root)
            paths = [entry.relative_path for entry in entries]
            self.assertEqual(paths, sorted(paths))
            self.assertIn("npc/a.lua", paths)
            self.assertIn("npc/b.lua", paths)
            self.assertIn("top.lua", paths)

    def test_manifest_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest = DeploymentManifest(
                schema_version="1.1",
                release_id="rel-1",
                created_at="2026-01-01T00:00:00+00:00",
                source_description="unit test",
                dry_run=False,
            )
            manifest.preflight_status = "passed"
            manifest.preflight_detail = "Canary started cleanly"
            manifest.outcome = "deployed"
            output_path = Path(tmp) / "manifest.json"
            manifest.write(output_path)

            loaded = read_manifest(output_path)
            self.assertEqual(loaded["releaseId"], "rel-1")
            self.assertEqual(loaded["outcome"], "deployed")
            self.assertEqual(loaded["fileCount"], 0)
            self.assertEqual(loaded["preflightStatus"], "passed")
            self.assertEqual(loaded["preflightDetail"], "Canary started cleanly")

    def test_write_is_atomic_no_partial_file_left_behind(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest = DeploymentManifest(
                schema_version="1.1",
                release_id="rel-1",
                created_at="2026-01-01T00:00:00+00:00",
                source_description="unit test",
                dry_run=False,
            )
            output_path = Path(tmp) / "manifest.json"
            manifest.write(output_path)
            self.assertTrue(output_path.exists())
            self.assertFalse(output_path.with_name(output_path.name + ".tmp").exists())


if __name__ == "__main__":
    unittest.main()
