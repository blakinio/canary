from __future__ import annotations

import json
import unittest
from pathlib import Path

from otbm_dependency_graph import MANIFEST_FORMAT, NODE_KINDS, RELATIONS, REPORT_FORMAT

REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_SCHEMA = REPO_ROOT / "docs/ai-agent/OTBM_DEPENDENCY_GRAPH_MANIFEST.schema.json"
REPORT_SCHEMA = REPO_ROOT / "docs/ai-agent/OTBM_DEPENDENCY_GRAPH.schema.json"


class DependencyGraphSchemaTests(unittest.TestCase):
    def test_manifest_schema_supports_reviewed_graph_contract(self) -> None:
        schema = json.loads(MANIFEST_SCHEMA.read_text(encoding="utf-8"))
        self.assertEqual(schema["properties"]["format"]["const"], MANIFEST_FORMAT)
        self.assertEqual(set(schema["$defs"]["node"]["properties"]["kind"]["enum"]), NODE_KINDS)
        self.assertEqual(set(schema["$defs"]["edge"]["properties"]["relation"]["enum"]), RELATIONS)
        evidence = schema["$defs"]["evidenceRef"]
        self.assertEqual(set(evidence["required"]), {"reportSha256", "pointer"})
        self.assertEqual(set(schema["$defs"]["expectation"]["properties"]["mode"]["enum"]), {"equals", "subset"})

    def test_report_schema_preserves_unresolved_boundaries_and_paths(self) -> None:
        schema = json.loads(REPORT_SCHEMA.read_text(encoding="utf-8"))
        self.assertEqual(schema["properties"]["format"]["const"], REPORT_FORMAT)
        query = schema["$defs"]["query"]
        self.assertIn("transitiveImpacts", query["required"])
        self.assertIn("unresolvedBoundaries", query["required"])
        impact = schema["$defs"]["impact"]
        self.assertIn("pathNodeIds", impact["required"])
        self.assertIn("pathEdgeIds", impact["required"])

    def test_report_policy_forbids_inference_and_execution_ownership(self) -> None:
        schema = json.loads(REPORT_SCHEMA.read_text(encoding="utf-8"))
        policy = schema["$defs"]["policy"]["properties"]
        self.assertTrue(policy["readOnly"]["const"])
        self.assertFalse(policy["mapModified"]["const"])
        self.assertFalse(policy["otbmParsedIndependently"]["const"])
        self.assertFalse(policy["scriptResolutionRecomputed"]["const"])
        self.assertFalse(policy["storageGraphRecomputed"]["const"])
        self.assertFalse(policy["pathfindingExecuted"]["const"])
        self.assertFalse(policy["routePlanningExecuted"]["const"])
        self.assertFalse(policy["physicalE2eSelectionRecomputed"]["const"])
        self.assertFalse(policy["physicalE2eExecuted"]["const"])
        self.assertFalse(policy["dependencyEdgesInferred"]["const"])
        self.assertFalse(policy["unprovenEdgesTraversed"]["const"])
        self.assertFalse(policy["scenarioPrioritizationDirected"]["const"])


if __name__ == "__main__":
    unittest.main()
