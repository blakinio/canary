from __future__ import annotations

import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from materialize_promotion_overlay import OverlayMaterializationError, materialize


class PromotionOverlayTests(unittest.TestCase):
    def _fixture(self, root: Path) -> tuple[dict, Path, bytes]:
        generated = root / "generated"
        preview = generated / "task" / "npc" / "keeper.lua"
        preview.parent.mkdir(parents=True)
        content = b"return npc\n"
        preview.write_bytes(content)
        digest = hashlib.sha256(content).hexdigest()
        handoff = {
            "schemaVersion": "1.0",
            "taskId": "task-1",
            "targetDatapack": "data-canary",
            "handoffStatus": "ready-for-manual-review",
            "automaticApplyAllowed": False,
            "manualApprovalRequired": True,
            "blockers": [],
            "files": [
                {
                    "previewPath": "task/npc/keeper.lua",
                    "targetPath": "data-canary/npc/keeper.lua",
                    "sha256": digest,
                    "operation": "manual-copy-after-review",
                }
            ],
        }
        return handoff, generated, content

    def test_materializes_confirmed_review_into_atomic_overlay(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            handoff, generated, content = self._fixture(root)
            output = root / "overlay"

            result = materialize(handoff, generated, output, confirm_reviewed=True)

            self.assertEqual((output / "npc" / "keeper.lua").read_bytes(), content)
            self.assertEqual(result["targetDatapack"], "data-canary")
            self.assertTrue(result["manualReviewConfirmed"])
            self.assertEqual(result["fileCount"], 1)
            self.assertEqual(result["files"][0]["overlayPath"], "npc/keeper.lua")
            self.assertFalse(any(path.name.startswith(".overlay.tmp-") for path in root.iterdir()))

    def test_requires_explicit_manual_review_confirmation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            handoff, generated, _content = self._fixture(root)
            with self.assertRaisesRegex(OverlayMaterializationError, "confirmation"):
                materialize(handoff, generated, root / "overlay", confirm_reviewed=False)

    def test_rejects_blocked_or_automatically_applicable_handoff(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            handoff, generated, _content = self._fixture(root)
            handoff["blockers"] = [{"message": "placeholder remains"}]
            with self.assertRaisesRegex(OverlayMaterializationError, "blockers"):
                materialize(handoff, generated, root / "blocked", confirm_reviewed=True)

            handoff["blockers"] = []
            handoff["automaticApplyAllowed"] = True
            with self.assertRaisesRegex(OverlayMaterializationError, "forbid automatic"):
                materialize(handoff, generated, root / "automatic", confirm_reviewed=True)

    def test_rejects_checksum_mismatch_and_target_escape(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            handoff, generated, _content = self._fixture(root)
            handoff["files"][0]["sha256"] = "0" * 64
            with self.assertRaisesRegex(OverlayMaterializationError, "checksum mismatch"):
                materialize(handoff, generated, root / "bad-checksum", confirm_reviewed=True)

            handoff, generated, _content = self._fixture(root / "second")
            handoff["files"][0]["targetPath"] = "data-otservbr-global/npc/keeper.lua"
            with self.assertRaisesRegex(OverlayMaterializationError, "outside target datapack"):
                materialize(handoff, generated, root / "escape", confirm_reviewed=True)

    def test_rejects_absolute_and_parent_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            handoff, generated, _content = self._fixture(root)
            handoff["files"][0]["targetPath"] = "/data-canary/npc/keeper.lua"
            with self.assertRaisesRegex(OverlayMaterializationError, "unsafe target path"):
                materialize(handoff, generated, root / "absolute", confirm_reviewed=True)

            handoff, generated, _content = self._fixture(root / "second")
            handoff["files"][0]["previewPath"] = "../keeper.lua"
            with self.assertRaisesRegex(OverlayMaterializationError, "unsafe preview path"):
                materialize(handoff, generated, root / "parent", confirm_reviewed=True)

    def test_rejects_duplicate_target_and_symlinked_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            handoff, generated, content = self._fixture(root)
            second = dict(handoff["files"][0])
            second["previewPath"] = "task/npc/keeper-copy.lua"
            (generated / second["previewPath"]).write_bytes(content)
            handoff["files"].append(second)
            with self.assertRaisesRegex(OverlayMaterializationError, "duplicate overlay target"):
                materialize(handoff, generated, root / "duplicate", confirm_reviewed=True)

            handoff, generated, _content = self._fixture(root / "symlink")
            source = generated / "task" / "npc" / "keeper.lua"
            outside = root / "outside.lua"
            outside.write_text("outside", encoding="utf-8")
            source.unlink()
            try:
                source.symlink_to(outside)
            except OSError as exc:
                self.skipTest(f"symlinks are unavailable: {exc}")
            with self.assertRaisesRegex(OverlayMaterializationError, "symlinks"):
                materialize(handoff, generated, root / "symlink-output", confirm_reviewed=True)

    def test_copy_failure_removes_partial_overlay(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            handoff, generated, _content = self._fixture(root)
            output = root / "overlay"

            def partial_copy(source: Path, destination: Path) -> None:
                Path(destination).write_text("partial", encoding="utf-8")
                raise OSError("synthetic copy failure")

            with mock.patch("materialize_promotion_overlay.shutil.copy2", side_effect=partial_copy):
                with self.assertRaisesRegex(OSError, "synthetic copy failure"):
                    materialize(handoff, generated, output, confirm_reviewed=True)

            self.assertFalse(output.exists())
            self.assertFalse(any(path.name.startswith(".overlay.tmp-") for path in root.iterdir()))

    def test_cli_contract_can_be_serialized_without_embedding_source_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            handoff, generated, _content = self._fixture(root)
            result = materialize(handoff, generated, root / "overlay", confirm_reviewed=True)
            encoded = json.dumps(result)
            self.assertNotIn(str(generated), encoded)
            self.assertNotIn(os.sep + "tmp" + os.sep, encoded)


if __name__ == "__main__":
    unittest.main()
