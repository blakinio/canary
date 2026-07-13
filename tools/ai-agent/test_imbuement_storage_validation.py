from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

MODULE_PATH = Path(__file__).with_name("imbuement_storage_validation.py")
REPOSITORY_ROOT = MODULE_PATH.parents[2]
SPEC = importlib.util.spec_from_file_location("imbuement_storage_validation", MODULE_PATH)
assert SPEC and SPEC.loader
validation = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = validation
SPEC.loader.exec_module(validation)


class FakeEntry:
    def __init__(self, name: str, base: int, storage: int) -> None:
        self.name = name
        self.base = base
        self.storage = storage


class FakeRegistry:
    def __init__(self, entries: tuple[FakeEntry, ...]) -> None:
        self.entries = entries


def mapped_entries() -> tuple[FakeEntry, ...]:
    entries = tuple(
        FakeEntry(name, 3, storage_id)
        for storage_id, names in validation.EXPECTED_FORGOTTEN_KNOWLEDGE_GROUPS.items()
        for name in names
    )
    return entries + (
        FakeEntry("Featherweight", 3, 0),
        FakeEntry("Vibrancy", 3, 0),
    )


def write_support_files(root: Path) -> None:
    (root / "data/XML").mkdir(parents=True)
    (root / validation.STORAGE_REGISTRY_PATH).parent.mkdir(parents=True)
    (root / validation.BOSS_UNLOCK_PATH).parent.mkdir(parents=True)
    (root / "data/XML/imbuements.xml").write_text(
        "<imbuements />", encoding="utf-8"
    )
    (root / validation.STORAGE_REGISTRY_PATH).write_text(
        """
        LadyTenebrisKilled = 45489,
        LloydKilled = 45490,
        ThornKnightKilled = 45491,
        DragonkingKilled = 45492,
        HorrorKilled = 45493,
        TimeGuardianKilled = 45494,
        LastLoreKilled = 45495,
        """,
        encoding="utf-8",
    )
    (root / validation.CONFIG_PATH).write_text(
        "toggleImbuementShrineStorage = false\n", encoding="utf-8"
    )
    (root / validation.BOSS_UNLOCK_PATH).write_text(
        " ".join(validation.EXPECTED_BOSS_STORAGE_TOKENS), encoding="utf-8"
    )


class ImbuementStorageValidationTests(unittest.TestCase):
    def test_declared_storage_ids_only_reads_named_numeric_fields(self) -> None:
        text = """
        Storage = {
            Foo = 123,
            Nested = {
                Bar = 456,
            },
            List = { 789, 790 },
            Dynamic = SOME_VALUE,
        }
        """
        self.assertEqual(validation.declared_storage_ids(text), {123, 456})

    def test_config_boolean(self) -> None:
        text = "toggleImbuementShrineStorage = false\nother = true\n"
        self.assertFalse(validation.config_boolean(text, "toggleImbuementShrineStorage"))
        self.assertTrue(validation.config_boolean(text, "other"))
        self.assertIsNone(validation.config_boolean(text, "missing"))

    def test_powerful_storage_groups_are_sorted_and_ignore_other_tiers(self) -> None:
        entries = (
            FakeEntry("Strike", 3, 45495),
            FakeEntry("Epiphany", 3, 45495),
            FakeEntry("Basic Strike", 1, 45495),
            FakeEntry("Vibrancy", 3, 0),
        )
        self.assertEqual(
            validation.powerful_storage_groups(entries),
            {45495: ("Epiphany", "Strike")},
        )

    def test_validate_accepts_confirmed_mapping_and_retains_zero_storage_warning(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_support_files(root)
            fake_module = mock.Mock()
            fake_module.parse_registry.return_value = FakeRegistry(mapped_entries())
            with mock.patch.object(
                validation, "_load_registry_parser", return_value=fake_module
            ):
                baseline, findings = validation.validate(root)

        by_code = {finding.code: finding for finding in findings}
        self.assertNotIn("UNDECLARED_IMBUEMENT_STORAGE", by_code)
        self.assertNotIn("LEGACY_IMBUEMENT_STORAGE", by_code)
        self.assertNotIn("FORGOTTEN_KNOWLEDGE_FAMILY_GROUP", by_code)
        self.assertIn("POWERFUL_UNLOCK_BYPASS", by_code)
        self.assertEqual(baseline["undeclared_storage_ids"], [])
        self.assertEqual(baseline["legacy_storage_ids_in_use"], [])
        self.assertEqual(baseline["family_group_mismatches"], [])
        self.assertEqual(baseline["powerful_with_nonzero_storage"], 22)
        self.assertEqual(
            baseline["powerful_with_zero_storage"], ["Featherweight", "Vibrancy"]
        )
        self.assertFalse(baseline["storage_filter_default"])
        self.assertTrue(baseline["boss_script_uses_named_storages"])

    def test_validate_rejects_legacy_and_wrong_family_mapping(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_support_files(root)
            fake_module = mock.Mock()
            fake_module.parse_registry.return_value = FakeRegistry(
                (
                    FakeEntry("Strike", 3, 50488),
                    FakeEntry("Featherweight", 3, 0),
                    FakeEntry("Vibrancy", 3, 0),
                )
            )
            with mock.patch.object(
                validation, "_load_registry_parser", return_value=fake_module
            ):
                baseline, findings = validation.validate(root)

        by_code = {finding.code: finding for finding in findings}
        self.assertIn("UNDECLARED_IMBUEMENT_STORAGE", by_code)
        self.assertIn("LEGACY_IMBUEMENT_STORAGE", by_code)
        self.assertIn("FORGOTTEN_KNOWLEDGE_FAMILY_GROUP", by_code)
        self.assertIn("POWERFUL_UNLOCK_BYPASS", by_code)
        self.assertEqual(baseline["legacy_storage_ids_in_use"], [50488])
        self.assertIn("50488", by_code["UNDECLARED_IMBUEMENT_STORAGE"].message)

    def test_expected_mapping_baseline(self) -> None:
        self.assertEqual(
            validation.LEGACY_STALE_STORAGE_IDS,
            {50488, 50490, 50492, 50494, 50496, 50498, 50501},
        )
        self.assertEqual(
            validation.EXPECTED_FORGOTTEN_KNOWLEDGE_GROUPS[45495],
            ("Epiphany", "Strike"),
        )
        self.assertEqual(
            sum(
                len(families)
                for families in validation.EXPECTED_FORGOTTEN_KNOWLEDGE_GROUPS.values()
            ),
            22,
        )

    def test_repository_uses_confirmed_forgotten_knowledge_mapping(self) -> None:
        baseline, findings = validation.validate(REPOSITORY_ROOT)
        errors = [finding for finding in findings if finding.severity == "error"]
        self.assertEqual(errors, [])
        self.assertEqual(baseline["undeclared_storage_ids"], [])
        self.assertEqual(baseline["legacy_storage_ids_in_use"], [])
        self.assertEqual(baseline["family_group_mismatches"], [])
        self.assertEqual(baseline["powerful_with_nonzero_storage"], 22)


if __name__ == "__main__":
    unittest.main()
