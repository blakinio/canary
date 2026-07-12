from __future__ import annotations

import hashlib
import json
import os
import shutil
import unittest
from pathlib import Path


class EquipmentUpgradeSourceExportTest(unittest.TestCase):
    """Temporary read-only source exporter for the Equipment Upgrade audit."""

    def test_export_current_sources(self) -> None:
        if os.environ.get("GITHUB_ACTIONS") != "true" or os.environ.get("GITHUB_HEAD_REF") != "validation/equipment-upgrade":
            self.skipTest("source export runs only for the Equipment Upgrade validation PR")

        root = Path.cwd()
        output = root / "artifacts/first-real-content-pack/generated-content/equipment-upgrade-audit"
        output.mkdir(parents=True, exist_ok=True)

        extensions = {".cpp", ".hpp", ".h", ".lua", ".sql", ".xml"}
        content_markers = (
            b"ForgeMonster",
            b"ForgeSystemMonster",
            b"forgeDust",
            b"ForgeDust",
            b"FORGE_",
            b"forgeStack",
            b"ForgeStack",
            b"forgeFuseItems",
            b"forgeTransferItemTier",
            b"onslaughtChanceFormula",
            b"ruseChanceFormula",
            b"momentumChanceFormula",
            b"transcendenceChanceFormula",
            b"amplificationChanceFormula",
            b"getFatalChance",
            b"damage.fatal",
            b"getDodgeChance",
            b"triggerMomentum",
            b"triggerTranscendence",
            b"getAmplificationChance",
            b"quadraticPoly",
            b"avatarTimer(",
            b"WHEEL_AVATAR",
        )

        files: dict[str, dict[str, int | str]] = {}
        ignored_parts = {".git", "build", "vcpkg_installed", "artifacts"}
        for source in root.rglob("*"):
            if not source.is_file() or source.suffix.lower() not in extensions:
                continue
            relative = source.relative_to(root)
            if any(part in ignored_parts for part in relative.parts):
                continue
            if source.stat().st_size > 2_000_000:
                continue

            data = source.read_bytes()
            path_match = "forge" in relative.as_posix().lower()
            content_match = any(marker in data for marker in content_markers)
            if not path_match and not content_match:
                continue

            target = output / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            files[relative.as_posix()] = {
                "size": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
            }

        self.assertGreater(len(files), 10, "unexpectedly few Forge-related sources found")
        (output / "MANIFEST.json").write_text(
            json.dumps({"fileCount": len(files), "files": files}, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )


if __name__ == "__main__":
    unittest.main()
