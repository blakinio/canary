from __future__ import annotations

import copy
import hashlib
import json
import unittest

from otbm_world_assurance_campaign import (
    CERTIFICATION_FORMAT,
    COVERAGE_FORMAT,
    EVIDENCE_BUNDLE_FORMAT,
    FRESHNESS_FORMAT,
    MANIFEST_FORMAT,
    WorldAssuranceCampaignError,
    build_campaign_report,
)


MAP_SHA = "a" * 64
WORLD_SHA = "b" * 64
ROUTE_PLAN_SHA = "c" * 64
ROUTE_FILE_SHA = "d" * 64
PREFLIGHT_SHA = "e" * 64
ARTIFACT_SHA = "f" * 64
SOURCE_SHA = "1" * 64
VALUE_SHA = "2" * 64


def pin(name: str, fmt: str, content: object | None = None) -> dict:
    raw = json.dumps(content if content is not None else {"format": fmt}, sort_keys=True).encode()
    return {"fileName": name, "size": len(raw), "sha256": hashlib.sha256(raw).hexdigest(), "format": fmt}


def manifest(*, qa005_state: str = "unavailable", qa006_state: str = "unavailable", maximum: str = "C5_PHYSICAL_ROUTE_PROVEN") -> dict:
    qa005 = {
        "bindingState": qa005_state,
        "targetId": "qa005.thais" if qa005_state == "bound" else None,
        "blockers": [] if qa005_state == "bound" else ["QA005_NO_REVIEWED_MECHANIC_BINDING"],
    }
    qa006 = {
        "bindingState": qa006_state,
        "targetId": "qa005.thais" if qa006_state == "bound" else None,
        "maximumLevel": maximum,
        "blockers": [] if qa006_state == "bound" else ["QA006_REQUIRES_QA005_TARGET"],
    }
    return {
        "format": MANIFEST_FORMAT,
        "schemaVersion": 1,
        "campaignId": "owa-001-test",
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
                    "routingBounds": {
                        "from": [32347, 32216, 7],
                        "to": [32369, 32241, 7],
                    },
                    "references": ["docs/ai-agent/OTBM_THAIS_LANDMARK_EVIDENCE.md"],
                },
                "provenance": {
                    "sourceMapSha256": MAP_SHA,
                    "worldIndexSha256": WORLD_SHA,
                },
                "qa005": qa005,
                "qa006": qa006,
                "qa016": {
                    "freshnessDimensionIds": [
                        "thais-route-physical-proof",
                        "thais-route-static-proof",
                    ]
                },
                "qa018": {
                    "requiredExtracts": [
                        {
                            "id": "thais.route-preflight",
                            "sourceSha256": SOURCE_SHA,
                            "valueSha256": VALUE_SHA,
                        }
                    ]
                },
                "routeEvidence": {
                    "routeId": "thais-temple-depot",
                    "routePlanSha256": ROUTE_PLAN_SHA,
                    "routePlanFileSha256": ROUTE_FILE_SHA,
                    "preflightFileSha256": PREFLIGHT_SHA,
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
                    "workflowRunId": 123,
                    "artifactId": 456,
                    "artifactDigestSha256": ARTIFACT_SHA,
                    "resultFileSha256": "3" * 64,
                    "scenarioManifestFileSha256": "4" * 64,
                    "evidenceExtractIds": ["thais.route-preflight"],
                },
                "unresolvedEvidence": [],
                "conflictingEvidence": [],
                "blockers": [],
            }
        ],
    }


def freshness(status: str = "current") -> dict:
    return {
        "format": FRESHNESS_FORMAT,
        "schemaVersion": 1,
        "dimensionFreshness": [
            {
                "dimensionId": "thais-route-physical-proof",
                "status": status,
                "changedDependencies": ["source-map"] if status == "stale" else [],
            },
            {
                "dimensionId": "thais-route-static-proof",
                "status": status,
                "changedDependencies": ["source-map"] if status == "stale" else [],
            },
        ],
    }


def bundle(*, source_sha: str = SOURCE_SHA, value_sha: str = VALUE_SHA) -> dict:
    return {
        "format": EVIDENCE_BUNDLE_FORMAT,
        "schemaVersion": 1,
        "sources": [
            {
                "id": "preflight",
                "path": "route-preflight.json",
                "sha256": source_sha,
                "format": "canary-otbm-e2e-route-preflight-v1",
            }
        ],
        "extracts": [
            {
                "id": "thais.route-preflight",
                "sourceId": "preflight",
                "pointer": "",
                "value": {"ok": True},
                "valueSha256": value_sha,
            }
        ],
    }


def coverage() -> dict:
    proven = {"state": "proven", "evidence": [], "memberIds": ["m1"], "blockers": []}
    not_applicable = {"state": "not-applicable", "evidence": [], "memberIds": ["m1"], "blockers": []}
    return {
        "format": COVERAGE_FORMAT,
        "schemaVersion": 1,
        "currentMap": {"mapSha256": MAP_SHA, "worldIndexSha256": WORLD_SHA},
        "policy": {"formalCertificationAssigned": False},
        "targets": [
            {
                "id": "qa005.thais",
                "kind": "landmark-route",
                "dimensions": {
                    "indexedOnExactMap": copy.deepcopy(proven),
                    "sourceCorrelated": copy.deepcopy(proven),
                    "scriptResolved": copy.deepcopy(proven),
                    "staticallyReachable": copy.deepcopy(proven),
                    "interactionResolved": copy.deepcopy(not_applicable),
                    "staticQualityCompatible": copy.deepcopy(proven),
                    "executableRouteCovered": copy.deepcopy(proven),
                    "physicallyRuntimeProven": copy.deepcopy(proven),
                    "candidateMapValidated": {
                        "state": "not-evaluated",
                        "evidence": [],
                        "memberIds": ["m1"],
                        "blockers": ["CANDIDATE_VALIDATION_EVIDENCE_NOT_BOUND"],
                    },
                },
                "staleAgainstCurrentMap": {"state": "current", "evidence": [], "blockers": []},
                "requirementsSatisfied": True,
            }
        ],
    }


def certification(coverage_sha: str, level: str = "C5_PHYSICAL_ROUTE_PROVEN") -> dict:
    return {
        "format": CERTIFICATION_FORMAT,
        "schemaVersion": 1,
        "currentMap": {"mapSha256": MAP_SHA, "worldIndexSha256": WORLD_SHA},
        "certifications": [
            {
                "targetId": "qa005.thais",
                "kind": "landmark-route",
                "reason": "reviewed",
                "requestedMaximumLevel": "C5_PHYSICAL_ROUTE_PROVEN",
                "certificationLevel": level,
                "certificationState": "certified",
                "staleAgainstCurrentMap": False,
                "coverageRequirementsSatisfied": True,
                "evaluatedLevels": [],
                "blockers": [],
                "evidence": {
                    "format": COVERAGE_FORMAT,
                    "reportSha256": coverage_sha,
                    "sourceId": "qa005.thais",
                },
            }
        ],
    }


class WorldAssuranceCampaignTests(unittest.TestCase):
    def _build(self, *, man=None, cov=None, cert=None, fresh=None, bundles=None):
        man = man or manifest()
        fresh = freshness() if fresh is None else fresh
        bundles = [bundle()] if bundles is None else bundles
        pins = {
            "manifest": pin("manifest.json", MANIFEST_FORMAT, man),
            "evidenceBundles": [pin("bundle.json", EVIDENCE_BUNDLE_FORMAT, item) for item in bundles],
            "physicalArtifacts": [{"fileName": "physical.zip", "size": 1, "sha256": ARTIFACT_SHA}],
        }
        if cov is not None:
            pins["coverageDashboard"] = pin("coverage.json", COVERAGE_FORMAT, cov)
        if cert is not None:
            pins["certification"] = pin("certification.json", CERTIFICATION_FORMAT, cert)
        if fresh is not None:
            pins["freshness"] = pin("freshness.json", FRESHNESS_FORMAT, fresh)
        return build_campaign_report(
            manifest=man,
            coverage_dashboard=cov,
            certification_report=cert,
            freshness_report=fresh,
            evidence_bundles=bundles,
            input_pins=pins,
        )

    def test_pure_movement_pilot_fails_closed_at_c0_despite_physical_route_proof(self):
        report = self._build()
        target = report["targets"][0]
        self.assertEqual(target["qa006Certification"]["certificationLevel"], "C0_NOT_EVALUATED")
        self.assertEqual(target["physicalE2e"]["state"], "proven")
        self.assertEqual(target["qa016Freshness"]["state"], "current")
        self.assertEqual(target["status"], "blocked")
        self.assertFalse(target["qa005Coverage"]["sourceReportPresent"])
        self.assertTrue(
            all(
                dimension["state"] == "not-evaluated"
                for dimension in target["qa005Coverage"]["dimensions"].values()
            )
        )
        self.assertIn("QA005_NO_REVIEWED_MECHANIC_BINDING", target["blockers"])
        self.assertIn("QA006_REQUIRES_QA005_TARGET", target["blockers"])

    def test_output_is_deterministic(self):
        first = self._build()
        second = self._build()
        self.assertEqual(first, second)
        self.assertEqual(first["reportSha256"], second["reportSha256"])

    def test_bound_qa005_provenance_mismatch_fails_closed(self):
        man = manifest(qa005_state="bound", qa006_state="bound")
        cov = coverage()
        cov["currentMap"]["mapSha256"] = "9" * 64
        cov_pin = pin("coverage.json", COVERAGE_FORMAT, cov)
        cert = certification(cov_pin["sha256"])
        with self.assertRaisesRegex(WorldAssuranceCampaignError, "map/World Index provenance"):
            self._build(man=man, cov=cov, cert=cert)

    def test_stale_qa016_marks_target_and_physical_proof_stale(self):
        report = self._build(fresh=freshness("stale"))
        target = report["targets"][0]
        self.assertEqual(target["qa016Freshness"]["state"], "stale")
        self.assertEqual(target["physicalE2e"]["state"], "stale")
        self.assertEqual(target["status"], "stale")
        self.assertIn("QA016_DIMENSION_STALE:thais-route-static-proof", target["blockers"])

    def test_qa018_hash_mismatch_blocks_exact_evidence(self):
        bad = bundle(value_sha="8" * 64)
        report = self._build(bundles=[bad])
        target = report["targets"][0]
        self.assertEqual(target["qa018Evidence"]["state"], "blocked")
        self.assertEqual(target["physicalE2e"]["state"], "blocked")
        self.assertEqual(target["status"], "blocked")
        self.assertIn("QA018_VALUE_SHA_MISMATCH:thais.route-preflight", target["blockers"])

    def test_exact_bound_target_preserves_canonical_c5_certification(self):
        man = manifest(qa005_state="bound", qa006_state="bound")
        cov = coverage()
        cov_pin = pin("coverage.json", COVERAGE_FORMAT, cov)
        cert = certification(cov_pin["sha256"])
        report = self._build(man=man, cov=cov, cert=cert)
        target = report["targets"][0]
        self.assertEqual(target["qa006Certification"]["certificationLevel"], "C5_PHYSICAL_ROUTE_PROVEN")
        self.assertEqual(target["qa006Certification"]["certificationState"], "certified")
        self.assertEqual(target["qa005Coverage"]["dimensions"]["physicallyRuntimeProven"]["state"], "proven")
        self.assertEqual(target["status"], "certified")

    def test_missing_exact_physical_artifact_digest_does_not_claim_runtime_proof(self):
        man = manifest()
        fresh = freshness()
        bundles = [bundle()]
        pins = {
            "manifest": pin("manifest.json", MANIFEST_FORMAT, man),
            "freshness": pin("freshness.json", FRESHNESS_FORMAT, fresh),
            "evidenceBundles": [pin("bundle.json", EVIDENCE_BUNDLE_FORMAT, bundles[0])],
            "physicalArtifacts": [],
        }
        report = build_campaign_report(
            manifest=man,
            coverage_dashboard=None,
            certification_report=None,
            freshness_report=fresh,
            evidence_bundles=bundles,
            input_pins=pins,
        )
        target = report["targets"][0]
        self.assertEqual(target["physicalE2e"]["state"], "missing")
        self.assertIn("PHYSICAL_E2E_ARTIFACT_DIGEST_NOT_SUPPLIED", target["blockers"])

    def test_landmark_route_cannot_request_c6(self):
        man = manifest(maximum="C6_FEATURE_OR_MECHANIC_PHYSICALLY_PROVEN")
        with self.assertRaisesRegex(WorldAssuranceCampaignError, "invalid maximum certification level"):
            self._build(man=man)

    def test_bound_qa006_must_reference_exact_supplied_qa005_file(self):
        man = manifest(qa005_state="bound", qa006_state="bound")
        cov = coverage()
        cert = certification("7" * 64)
        with self.assertRaisesRegex(WorldAssuranceCampaignError, "does not pin supplied QA-005 report"):
            self._build(man=man, cov=cov, cert=cert)


if __name__ == "__main__":
    unittest.main()
