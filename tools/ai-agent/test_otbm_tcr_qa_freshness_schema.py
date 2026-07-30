from __future__ import annotations

import json
import unittest
from pathlib import Path

from otbm_tcr_qa_freshness import (
    MANIFEST_FORMAT,
    REPORT_FORMAT,
    TcrQaFreshnessError,
    canonical_sha256,
)
from test_otbm_tcr_qa_freshness import (
    build_fixture,
    make_manifest,
    make_provenance,
    make_routing,
)

ROOT = Path(__file__).resolve().parents[2]
MANIFEST_SCHEMA = (
    ROOT / "docs/ai-agent/OTBM_TCR_QA_FRESHNESS_MANIFEST.schema.json"
)
REPORT_SCHEMA = ROOT / "docs/ai-agent/OTBM_TCR_QA_FRESHNESS.schema.json"


class TcrQaFreshnessSchemaTests(unittest.TestCase):
    def load(self, path: Path) -> dict[str, object]:
        document = json.loads(path.read_text(encoding="utf-8"))
        self.assertIsInstance(document, dict)
        return document

    def test_manifest_schema_contract_and_closed_mapping(self) -> None:
        schema = self.load(MANIFEST_SCHEMA)
        self.assertEqual(schema["properties"]["format"]["const"], MANIFEST_FORMAT)
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(schema["properties"]["mappings"]["maxItems"], 128)
        mapping = schema["$defs"]["mapping"]
        self.assertFalse(mapping["additionalProperties"])
        self.assertEqual(
            set(mapping["required"]),
            {
                "id",
                "routeId",
                "extract",
                "target",
                "componentIds",
                "dimensionIds",
                "contextReferences",
            },
        )
        condition = mapping["allOf"][0]
        self.assertEqual(condition["then"]["properties"]["componentIds"]["maxItems"], 0)
        self.assertEqual(condition["then"]["properties"]["dimensionIds"]["maxItems"], 0)
        self.assertEqual(condition["else"]["properties"]["componentIds"]["minItems"], 1)
        self.assertEqual(condition["else"]["properties"]["dimensionIds"]["minItems"], 1)

    def test_report_schema_policy_inventory_matches_generated_report(self) -> None:
        schema = self.load(REPORT_SCHEMA)
        self.assertEqual(schema["properties"]["format"]["const"], REPORT_FORMAT)
        self.assertFalse(schema["additionalProperties"])
        routing = make_routing()
        provenance = make_provenance()
        report = build_fixture(
            routing, provenance, make_manifest(routing, provenance)
        )
        policy_schema = schema["properties"]["policy"]
        self.assertEqual(set(policy_schema["required"]), set(report["policy"]))
        self.assertEqual(set(policy_schema["properties"]), set(report["policy"]))
        for name, value in report["policy"].items():
            self.assertEqual(policy_schema["properties"][name]["const"], value)

    def test_report_schema_preserves_non_execution_boundary(self) -> None:
        schema = self.load(REPORT_SCHEMA)
        policy = schema["properties"]["policy"]["properties"]
        self.assertTrue(policy["readOnlyComposition"]["const"])
        self.assertTrue(policy["reviewedDependencyMappingRequired"]["const"])
        self.assertTrue(policy["exactRouteTargetCoverageRequired"]["const"])
        self.assertTrue(policy["exactChangedDependencyEqualityRequired"]["const"])
        self.assertFalse(policy["parsesClientInputs"]["const"])
        self.assertFalse(policy["parsesOtbm"]["const"])
        self.assertFalse(policy["discoversDependencyEdges"]["const"])
        self.assertFalse(policy["invokesQa008"]["const"])
        self.assertFalse(policy["selectsQa002Validators"]["const"])
        self.assertFalse(policy["createsQa007ExecutionEvidence"]["const"])
        self.assertFalse(policy["runsPhysicalE2e"]["const"])
        self.assertFalse(policy["refreshesQa006Certification"]["const"])
        self.assertFalse(policy["authorizesDeployment"]["const"])
        self.assertFalse(policy["claimsGameplayParity"]["const"])

    def test_non_finite_numbers_are_not_canonical_json(self) -> None:
        with self.assertRaisesRegex(TcrQaFreshnessError, "not canonical JSON"):
            canonical_sha256({"value": float("nan")})
        with self.assertRaisesRegex(TcrQaFreshnessError, "not canonical JSON"):
            canonical_sha256({"value": float("inf")})


if __name__ == "__main__":
    unittest.main()
