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
        structural_findings = [
            finding
            for finding in self.findings
            if finding.code in structural_codes
        ]
        self.assertFalse(
            structural_findings,
            [finding.message for finding in structural_findings],
        )

    def test_current_reference_differences_are_detected(self) -> None:
        grouped: dict[str, list[validation.Finding]] = {}
        for finding in self.findings:
            grouped.setdefault(finding.code, []).append(finding)

        self.assertEqual(len(grouped.get("WIKI_EFFECT", [])), 3)
        self.assertTrue(all("Strike" in finding.message for finding in grouped["WIKI_EFFECT"]))

        self.assertEqual(len(grouped.get("WIKI_MATERIALS", [])), 1)
        self.assertIn("Punch tier 1", grouped["WIKI_MATERIALS"][0].message)

        self.assertEqual(grouped.get("WIKI_SCROLL", []), [])

        unlock_messages = {
            finding.message
            for finding in grouped.get("WIKI_POWERFUL_UNLOCK", [])
        }
        self.assertTrue(any("Featherweight" in message for message in unlock_messages))
        self.assertTrue(any("Vibrancy" in message for message in unlock_messages))

        self.assertEqual(len(grouped.get("WIKI_FEE_MODEL", [])), 3)

    def test_vibrancy_scrolls_resolve_to_exact_tiers(self) -> None:
        for scroll_id, tier in ((51746, 2), (51466, 3)):
            with self.subTest(scroll_id=scroll_id):
                entry = validation.resolve_scroll_entry(self.registry, scroll_id)
                self.assertIsNotNone(entry)
                assert entry is not None
                self.assertEqual(entry.name, "Vibrancy")
                self.assertEqual(entry.base, tier)

        forbidden_codes = {
            "ORPHAN_REGISTERED_SCROLL",
            "UNREGISTERED_XML_SCROLL",
            "VIBRANCY_SCROLL_UNRESOLVED",
            "VIBRANCY_SCROLL_WRONG_TARGET",
            "SCROLL_APPLICATION_ATOMICITY",
        }
        failures = [
            finding for finding in self.findings if finding.code in forbidden_codes
        ]
        self.assertFalse(failures, [finding.message for finding in failures])

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
