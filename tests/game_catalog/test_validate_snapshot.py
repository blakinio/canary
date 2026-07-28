from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "tools/game-catalog/validate_snapshot.py"
SPEC = importlib.util.spec_from_file_location("game_catalog_validate_snapshot", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
validator = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = validator
SPEC.loader.exec_module(validator)


class ValidateSnapshotTest(unittest.TestCase):
    fixture = ROOT / "tests/game_catalog/fixtures/minimal-snapshot.json"
    schema = ROOT / "schemas/game-catalog/v1/game-catalog-snapshot.schema.json"

    def test_shared_fixture_and_schema_hash_are_pinned(self) -> None:
        document, digest, size = validator.load_and_validate(self.fixture, self.schema)
        self.assertEqual("76b61b167e77a0c0379c5c1d179c3fec808ae1cf3d996e30be5784fde699691e", digest)
        self.assertGreater(size, 0)
        self.assertEqual(4, document["snapshot"]["entity_count"])
        self.assertEqual(2, document["snapshot"]["relation_count"])

    def test_removed_in_is_an_exclusive_later_bound(self) -> None:
        document = self._document()
        document["entities"][0]["removed_in"] = "15.20"
        self._assert_rejected(document, "semantic.invalid_version_range")

    def test_duplicate_canonical_key_is_rejected(self) -> None:
        document = self._document()
        document["entities"][1]["canonical_key"] = "creature:dragon"
        self._assert_rejected(document, "semantic.duplicate_entity")

    def test_dangling_relation_is_rejected(self) -> None:
        document = self._document()
        document["relations"][0]["target"] = "item:missing"
        self._assert_rejected(document, "semantic.dangling_relation")

    def test_invalid_probability_and_count_range_are_rejected(self) -> None:
        document = self._document()
        document["relations"][0]["data"]["chance_numerator"] = 100001
        document["relations"][0]["data"]["minimum_count"] = 2
        document["relations"][0]["data"]["maximum_count"] = 1
        codes = self._rejection_codes(document)
        self.assertIn("semantic.invalid_probability", codes)
        self.assertIn("semantic.invalid_count_range", codes)

    def test_unknown_schema_property_is_rejected(self) -> None:
        document = self._document()
        document["unexpected"] = True
        self._assert_rejected(document, "schema.additional_property")

    def test_release_order_is_integer_and_not_float(self) -> None:
        document = self._document()
        document["releases"][0]["release_order"] = 15.20
        self._assert_rejected(document, "schema.type")

    def test_hash_mismatch_is_rejected(self) -> None:
        with self.assertRaises(validator.CatalogValidationError):
            validator.load_and_validate(self.fixture, self.schema, "f" * 64)

    def _document(self) -> dict[str, object]:
        return json.loads(self.fixture.read_text(encoding="utf-8"))

    def _assert_rejected(self, document: dict[str, object], expected_code: str) -> None:
        self.assertIn(expected_code, self._rejection_codes(document))

    def _rejection_codes(self, document: dict[str, object]) -> list[str]:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "snapshot.json"
            path.write_text(json.dumps(document, separators=(",", ":")) + "\n", encoding="utf-8")
            with self.assertRaises(validator.CatalogValidationError) as caught:
                validator.load_and_validate(path, self.schema)
            return [finding.code for finding in caught.exception.findings]


if __name__ == "__main__":
    unittest.main()
