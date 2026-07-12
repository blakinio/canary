from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("imbuement_validation.py")
SPEC = importlib.util.spec_from_file_location("imbuement_validation", MODULE_PATH)
assert SPEC and SPEC.loader
validation = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = validation
SPEC.loader.exec_module(validation)


class ImbuementValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.repository_root = Path(__file__).resolve().parents[2]
        cls.registry = validation.parse_registry(
            cls.repository_root / "data/XML/imbuements.xml"
        )
        cls.findings = validation.validate_registry(
            cls.registry, cls.repository_root
        )

    def test_active_registry_structural_baseline(self) -> None:
        self.assertEqual(set(self.registry.bases), {1, 2, 3})
        self.assertEqual(set(self.registry.categories), set(range(20)))
        self.assertEqual(len(self.registry.entries), 72)
        self.assertEqual(len({entry.name for entry in self.registry.entries}), 24)
        structural_codes = {
            "BASE_ID_SET",
            "CATEGORY_ID_SET",
            "ENTRY_COUNT",
            "FAMILY_SET",
            "INCOMPLETE_FAMILY",
            "UNKNOWN_BASE",
            "UNKNOWN_CATEGORY",
            "DUPLICATE_FAMILY_TIER",
            "DUPLICATE_SCROLL_ID",
            "MISSING_RUNTIME_PATH",
            "MISSING_RUNTIME_MARKER",
        }
        self.assertFalse(
            structural_codes.intersection(finding.code for finding in self.findings)
        )

    def test_current_reference_differences_are_detected(self) -> None:
        grouped: dict[str, list[validation.Finding]] = {}
        for finding in self.findings:
            grouped.setdefault(finding.code, []).append(finding)

        self.assertEqual(len(grouped.get("WIKI_EFFECT", [])), 3)
        self.assertTrue(all("Strike" in finding.message for finding in grouped["WIKI_EFFECT"]))

        self.assertEqual(len(grouped.get("WIKI_MATERIALS", [])), 1)
        self.assertIn("Punch tier 1", grouped["WIKI_MATERIALS"][0].message)

        self.assertEqual(len(grouped.get("WIKI_SCROLL", [])), 2)
        self.assertTrue(all("Vibrancy" in finding.message for finding in grouped["WIKI_SCROLL"]))

        unlock_messages = {
            finding.message
            for finding in grouped.get("WIKI_POWERFUL_UNLOCK", [])
        }
        self.assertTrue(any("Featherweight" in message for message in unlock_messages))
        self.assertTrue(any("Vibrancy" in message for message in unlock_messages))

        self.assertEqual(len(grouped.get("WIKI_FEE_MODEL", [])), 3)

    def test_active_scroll_action_exposes_unresolved_vibrancy_ids(self) -> None:
        orphan_findings = [
            finding
            for finding in self.findings
            if finding.code == "ORPHAN_REGISTERED_SCROLL"
        ]
        self.assertEqual(len(orphan_findings), 1)
        self.assertIn("[51466, 51746]", orphan_findings[0].message)

    def test_scroll_range_parser(self) -> None:
        text = """
        for scrollId = 100, 102 do
            imbuement:id(scrollId)
        end
        imbuement:id(200, 201)
        """
        self.assertEqual(
            validation._registered_scroll_ids(text),
            {100, 101, 102, 200, 201},
        )

    def test_duplicate_base_is_rejected(self) -> None:
        xml = """\
<imbuements>
  <base id="1" name="A" price="1" protectionPrice="0" percent="100" removecost="1" duration="1" />
  <base id="1" name="B" price="1" protectionPrice="0" percent="100" removecost="1" duration="1" />
</imbuements>
"""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "imbuements.xml"
            path.write_text(xml, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate base id 1"):
                validation.parse_registry(path)

    def test_runtime_plan_has_required_scenarios(self) -> None:
        plan = validation.build_runtime_plan(self.registry, self.findings)
        scenario_ids = {scenario["id"] for scenario in plan["scenarios"]}
        self.assertTrue(
            {
                "shrine-access-gate",
                "application-cost-and-atomicity",
                "vibrancy-scrolls",
                "duration-combat",
                "duration-noncombat",
                "persistence",
            }.issubset(scenario_ids)
        )


if __name__ == "__main__":
    unittest.main()
