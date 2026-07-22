from __future__ import annotations

import json
import unittest
from pathlib import Path

from otbm_identifier_integrity import EXPECTATIONS, NAMESPACES, POLICY_FORMAT, REPORT_FORMAT

REPO_ROOT = Path(__file__).resolve().parents[2]
POLICY_SCHEMA = REPO_ROOT / "docs/ai-agent/OTBM_IDENTIFIER_INTEGRITY_POLICY.schema.json"
REPORT_SCHEMA = REPO_ROOT / "docs/ai-agent/OTBM_IDENTIFIER_INTEGRITY.schema.json"


class IdentifierIntegritySchemaTests(unittest.TestCase):
    def test_policy_schema_matches_public_contract(self) -> None:
        schema = json.loads(POLICY_SCHEMA.read_text(encoding="utf-8"))
        self.assertEqual(schema["properties"]["format"]["const"], POLICY_FORMAT)
        expectation = schema["$defs"]["expectation"]["properties"]
        self.assertEqual(set(expectation["namespace"]["enum"]), NAMESPACES)
        self.assertEqual(set(expectation["expectation"]["enum"]), EXPECTATIONS)
        self.assertEqual(schema["properties"]["expectations"]["maxItems"], 4096)
        self.assertEqual(schema["properties"]["placementRoles"]["maxItems"], 8192)

    def test_report_schema_matches_public_contract(self) -> None:
        schema = json.loads(REPORT_SCHEMA.read_text(encoding="utf-8"))
        self.assertEqual(schema["properties"]["format"]["const"], REPORT_FORMAT)
        required = set(schema["required"])
        for field in (
            "expectations",
            "reviewRequired",
            "scriptConflicts",
            "scriptUnresolved",
            "transitionConflicts",
            "selectorAmbiguities",
            "roleConflicts",
            "conflicts",
        ):
            self.assertIn(field, required)
        counts = schema["$defs"]["counts"]
        self.assertEqual(set(counts["required"]), NAMESPACES)


if __name__ == "__main__":
    unittest.main()
