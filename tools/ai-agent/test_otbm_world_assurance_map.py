from __future__ import annotations

import json
import unittest

from otbm_world_assurance_map import (
    CAMPAIGN_FORMAT,
    WorldAssuranceMapError,
    build_world_assurance_map_plan,
    canonical_sha256,
)

MAP_SHA = "a" * 64
WORLD_SHA = "b" * 64
FILE_SHA = "c" * 64

DIMENSIONS = (
    "indexedOnExactMap",
    "sourceCorrelated",
    "scriptResolved",
    "staticallyReachable",
    "interactionResolved",
    "staticQualityCompatible",
    "executableRouteCovered",
    "physicallyRuntimeProven",
    "candidateMapValidated",
)


def campaign(*, freshness: str = "current", physical: str = "proven", status: str = "blocked") -> dict:
    blockers = [
        "QA005_LANDMARK_ROUTE_REQUIRES_REVIEWED_MECHANIC_IDS",
        "QA005_NO_REVIEWED_MECHANIC_BINDING_FOR_PURE_MOVEMENT_ROUTE",
        "QA006_REQUIRES_CANONICAL_QA005_TARGET",
    ]
    payload = {
        "format": CAMPAIGN_FORMAT,
        "schemaVersion": 1,
        "campaignId": "owa-001-real-world-certification-campaign",
        "provenance": {},
        "targets": [
            {
                "id": "owa-001.thais-temple-to-depot",
                "class": "landmark-route",
                "reviewedDefinition": {
                    "reviewStatus": "reviewed",
                    "fromLandmarkId": "thais.temple",
                    "toLandmarkId": "thais.depot",
                    "regionId": "thais.temple-depot",
                    "origin": [32369, 32241, 7],
                    "destination": [32352, 32226, 7],
                    "routingBounds": {"from": [32347, 32216, 7], "to": [32369, 32241, 7]},
                    "references": ["docs/ai-agent/OTBM_THAIS_LANDMARK_EVIDENCE.md"],
                },
                "exactProvenance": {"sourceMapSha256": MAP_SHA, "worldIndexSha256": WORLD_SHA},
                "qa005Coverage": {
                    "sourceReportPresent": False,
                    "targetId": None,
                    "dimensions": {
                        name: {
                            "state": "not-evaluated",
                            "evidence": [],
                            "memberIds": [],
                            "blockers": ["QA005_NO_REVIEWED_MECHANIC_BINDING_FOR_PURE_MOVEMENT_ROUTE"],
                        }
                        for name in DIMENSIONS
                    },
                    "currentMapProvenance": {"state": "not-evaluated", "evidence": [], "blockers": blockers},
                    "requirementsSatisfied": False,
                },
                "qa006Certification": {
                    "sourceReportPresent": False,
                    "targetId": None,
                    "certificationLevel": "C0_NOT_EVALUATED",
                    "certificationState": "not-evaluated",
                    "requestedMaximumLevel": "C5_PHYSICAL_ROUTE_PROVEN",
                    "blockers": ["QA006_REQUIRES_CANONICAL_QA005_TARGET"],
                },
                "qa016Freshness": {
                    "state": freshness,
                    "dimensions": [
                        {"dimensionId": "thais-route-physical-proof", "status": freshness, "changedDependencies": []},
                        {"dimensionId": "thais-route-static-proof", "status": freshness, "changedDependencies": []},
                    ],
                    "blockers": [],
                },
                "qa018Evidence": {"state": "proven", "verifiedExtractIds": ["thais.route-preflight"], "blockers": []},
                "routeEvidence": {
                    "routeId": "thais-temple-depot",
                    "routePlanSha256": "d" * 64,
                    "routePlanFileSha256": "e" * 64,
                    "preflightFileSha256": "f" * 64,
                    "preflightStatus": "passed",
                    "origin": [32369, 32241, 7],
                    "destination": [32352, 32226, 7],
                    "distance": 59,
                    "interactionRequired": False,
                    "transitionIds": [],
                },
                "physicalE2e": {
                    "status": "retained-success",
                    "scope": "landmark-route",
                    "runtimeMapSha256": MAP_SHA,
                    "workflowRunId": 29704821423,
                    "artifactId": 8447816376,
                    "artifactDigestSha256": "1" * 64,
                    "resultFileSha256": "2" * 64,
                    "scenarioManifestFileSha256": "3" * 64,
                    "evidenceExtractIds": ["thais.route-preflight"],
                    "state": physical,
                    "blockers": [],
                    "proofBoundary": "route-level Physical E2E only; not QA-005 mechanic proof and not candidate-change revalidation",
                },
                "unresolvedEvidence": [],
                "conflictingEvidence": [],
                "blockers": blockers,
                "status": status,
            }
        ],
        "summary": {},
        "policy": {},
        "notes": [],
    }
    payload["reportSha256"] = canonical_sha256(payload)
    return payload


class WorldAssuranceMapTests(unittest.TestCase):
    def test_pilot_keeps_proof_dimensions_separate_and_evidence_linked(self):
        plan = build_world_assurance_map_plan(campaign(), campaign_file_sha256=FILE_SHA)
        target = plan["targets"][0]
        panels = {item["id"]: item for item in target["overlay"]["panels"]}
        self.assertEqual(
            set(panels),
            {"qa006-certification", "qa005-coverage", "qa016-freshness", "physical-e2e", "blockers"},
        )
        self.assertIn("C0_NOT_EVALUATED", panels["qa006-certification"]["value"])
        self.assertIn("not-evaluated=9", panels["qa005-coverage"]["value"])
        self.assertEqual(panels["qa016-freshness"]["value"], "current")
        self.assertEqual(panels["physical-e2e"]["value"], "proven")
        self.assertEqual(panels["blockers"]["value"], "3 blocker(s)")
        for panel in panels.values():
            self.assertTrue(panel["evidenceRefs"])
            self.assertTrue(all(ref.startswith("campaign:") for ref in panel["evidenceRefs"]))
        annotations = {item["id"]: item for item in target["overlay"]["annotations"]}
        self.assertEqual(set(annotations), {"reviewed-routing-bounds", "origin", "destination"})
        self.assertTrue(all(item["evidenceRefs"] for item in annotations.values()))
        self.assertFalse(plan["policy"]["routeGeometryInferred"])
        self.assertFalse(plan["policy"]["pathfindingPerformed"])
        self.assertFalse(plan["policy"]["compositeHealthScoreProduced"])

    def test_identical_input_is_deterministic(self):
        first = build_world_assurance_map_plan(campaign(), campaign_file_sha256=FILE_SHA)
        second = build_world_assurance_map_plan(campaign(), campaign_file_sha256=FILE_SHA)
        self.assertEqual(first, second)
        self.assertEqual(first["reportSha256"], second["reportSha256"])

    def test_campaign_self_hash_mismatch_fails_closed(self):
        bad = campaign()
        bad["targets"][0]["status"] = "certified"
        with self.assertRaisesRegex(WorldAssuranceMapError, "reportSha256"):
            build_world_assurance_map_plan(bad, campaign_file_sha256=FILE_SHA)

    def test_unknown_target_fails_closed(self):
        with self.assertRaisesRegex(WorldAssuranceMapError, "unknown campaign target ids"):
            build_world_assurance_map_plan(campaign(), campaign_file_sha256=FILE_SHA, target_ids=["missing"])

    def test_stale_and_blocked_states_are_preserved_not_upgraded(self):
        plan = build_world_assurance_map_plan(
            campaign(freshness="stale", physical="stale", status="stale"),
            campaign_file_sha256=FILE_SHA,
        )
        target = plan["targets"][0]
        panels = {item["id"]: item for item in target["overlay"]["panels"]}
        self.assertEqual(target["status"], "stale")
        self.assertEqual(panels["qa016-freshness"]["value"], "stale")
        self.assertEqual(panels["physical-e2e"]["value"], "stale")
        self.assertIn("C0_NOT_EVALUATED", panels["qa006-certification"]["value"])

    def test_endpoint_outside_reviewed_bounds_fails_closed(self):
        bad = campaign()
        bad["targets"][0]["reviewedDefinition"]["origin"] = [32000, 32000, 7]
        bad.pop("reportSha256")
        bad["reportSha256"] = canonical_sha256(bad)
        with self.assertRaisesRegex(WorldAssuranceMapError, "origin is outside reviewed routing bounds"):
            build_world_assurance_map_plan(bad, campaign_file_sha256=FILE_SHA)

    def test_no_route_polyline_or_inferred_path_is_present(self):
        plan = build_world_assurance_map_plan(campaign(), campaign_file_sha256=FILE_SHA)
        serialized = json.dumps(plan, sort_keys=True)
        self.assertNotIn("polyline", serialized.lower())
        self.assertNotIn("routePath", serialized)
        self.assertFalse(plan["policy"]["routeGeometryInferred"])


if __name__ == "__main__":
    unittest.main()
