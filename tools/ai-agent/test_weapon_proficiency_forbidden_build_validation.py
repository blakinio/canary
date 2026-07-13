from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from weapon_proficiency_forbidden_build_validation import EXPECTED_NAMES, validate


class ForbiddenBuildValidationTests(unittest.TestCase):
    def write_fixture(self, root: Path, *, invalid_profile: bool = False, wrong_name: bool = False) -> None:
        baseline = root / "docs/ai-agent/WEAPON_PROFICIENCY_FORBIDDEN_BUILD_BASELINE.json"
        baseline.parent.mkdir(parents=True)
        entries = []
        item_lines = ["<items>"]
        profiles = []
        for index, name in enumerate(EXPECTED_NAMES, start=1):
            item_id = 1000 + index
            proficiency_id = 2000 + index
            entries.append(
                {
                    "referenceName": name,
                    "itemId": item_id,
                    "appearanceName": name.casefold(),
                    "proficiencyId": proficiency_id,
                }
            )
            active_name = "Wrong Name" if wrong_name and index == 1 else name
            item_lines.append(f'  <item id="{item_id}" name="{active_name}"></item>')
            if not invalid_profile or index != 1:
                profiles.append({"ProficiencyId": proficiency_id, "Levels": []})
        item_lines.append("</items>")
        baseline.write_text(json.dumps({"source": {"archiveSha256": "abc"}, "items": entries}), encoding="utf-8")
        items = root / "data/items/items.xml"
        items.parent.mkdir(parents=True)
        items.write_text("\n".join(item_lines), encoding="utf-8")
        (root / "data/items/proficiencies.json").write_text(json.dumps(profiles), encoding="utf-8")

    def test_valid_fixture_verifies_all_entries(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_fixture(root)
            report = validate(root)
            self.assertTrue(report["ok"])
            self.assertEqual(report["summary"]["verifiedEntryCount"], 12)
            self.assertEqual(report["findings"], [])

    def test_invalid_profile_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_fixture(root, invalid_profile=True)
            report = validate(root)
            self.assertFalse(report["ok"])
            self.assertEqual(report["summary"]["verifiedEntryCount"], 11)
            self.assertIn("active-proficiency-missing", {finding["code"] for finding in report["findings"]})

    def test_wrong_active_item_name_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_fixture(root, wrong_name=True)
            report = validate(root)
            self.assertFalse(report["ok"])
            self.assertIn("active-item-mismatch", {finding["code"] for finding in report["findings"]})

    def test_real_repository_verifies_reviewed_asset_contract(self) -> None:
        root = Path(__file__).resolve().parents[2]
        report = validate(root)
        self.assertTrue(report["ok"], report["findings"])
        self.assertEqual(report["summary"]["baselineEntryCount"], 12)
        self.assertEqual(report["summary"]["verifiedEntryCount"], 12)
        self.assertTrue(all(item["eligibilityProven"] for item in report["items"]))


if __name__ == "__main__":
    unittest.main()
