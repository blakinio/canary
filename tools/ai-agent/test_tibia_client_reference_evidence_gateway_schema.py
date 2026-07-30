from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

from tibia_client_reference_evidence_gateway import (
    BINDINGS_FORMAT,
    EXPECTED_FORMAT_BY_KIND,
    REPORT_FORMAT,
    build_evidence_plan,
    execute_evidence_plan,
    load_bindings,
    normalize_bindings,
    sha256_path,
)

ROOT = Path(__file__).resolve().parents[2]


class ClientReferenceEvidenceGatewaySchemaTests(unittest.TestCase):
    def setUp(self) -> None:
        self.bindings_schema = json.loads(
            (
                ROOT
                / "docs/ai-agent/TIBIA_CLIENT_REFERENCE_EVIDENCE_BINDINGS.schema.json"
            ).read_text(encoding="utf-8")
        )
        self.report_schema = json.loads(
            (
                ROOT
                / "docs/ai-agent/TIBIA_CLIENT_REFERENCE_EVIDENCE_GATEWAY.schema.json"
            ).read_text(encoding="utf-8")
        )

    def test_formats_match_public_contracts(self) -> None:
        self.assertEqual(
            self.bindings_schema["properties"]["format"]["const"],
            BINDINGS_FORMAT,
        )
        self.assertEqual(
            self.report_schema["properties"]["format"]["const"],
            REPORT_FORMAT,
        )
        Draft202012Validator.check_schema(self.bindings_schema)
        Draft202012Validator.check_schema(self.report_schema)

    def test_schema_preserves_qa018_and_read_only_boundaries(self) -> None:
        policy = self.report_schema["properties"]["policy"]["properties"]
        self.assertEqual(policy["qa018EvidenceGatewayReused"]["const"], True)
        self.assertEqual(policy["reviewedBindingIdOnly"]["const"], True)
        for key in (
            "parsesClientFiles",
            "parsesOtbm",
            "parsesSourceReports",
            "reinterpretsSourceSemantics",
            "infersIdentifiers",
            "fuzzySelection",
            "validatesSourceSemantics",
            "mutatesSourceOrGameState",
            "runsE2e",
            "ownsDownstreamAcceptance",
            "routesAdoption",
        ):
            self.assertEqual(policy[key]["const"], False)

    def test_plan_and_executed_reports_validate(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "drift.json"
            source.write_text(
                json.dumps(
                    {
                        "format": EXPECTED_FORMAT_BY_KIND["drift"],
                        "findings": [{"id": "schema-family-change"}],
                    }
                ),
                encoding="utf-8",
            )
            bindings = {
                "format": BINDINGS_FORMAT,
                "schemaVersion": 1,
                "bindings": [
                    {
                        "id": "drift.schema-family",
                        "kind": "drift",
                        "sources": [
                            {
                                "id": "drift.schema-family.source",
                                "path": "drift.json",
                                "sha256": hashlib.sha256(
                                    source.read_bytes()
                                ).hexdigest(),
                                "format": EXPECTED_FORMAT_BY_KIND["drift"],
                                "extracts": [
                                    {
                                        "id": "drift.schema-family.finding",
                                        "pointer": "/findings/0",
                                    }
                                ],
                            }
                        ],
                        "contextReferences": ["TCR-009"],
                    }
                ],
            }
            bindings_path = root / "bindings.json"
            bindings_path.write_text(json.dumps(bindings), encoding="utf-8")
            normalized = normalize_bindings(load_bindings(bindings_path))
            Draft202012Validator(self.bindings_schema).validate(normalized)
            plan = build_evidence_plan(
                normalized,
                "drift.schema-family",
                bindings_file_sha256=sha256_path(bindings_path),
            )
            Draft202012Validator(self.report_schema).validate(plan)
            executed = execute_evidence_plan(bindings_path, plan)
            Draft202012Validator(self.report_schema).validate(executed)


if __name__ == "__main__":
    unittest.main()
