from __future__ import annotations

import copy
import unittest

from tibia_reference_adoption_router import (
    AdoptionRoutingError,
    BUNDLE_FORMAT,
    GATEWAY_FORMAT,
    REPORT_FORMAT,
    REQUEST_FORMAT,
    TARGET_ACHIEVEMENT,
    TARGET_CYCLOPEDIA,
    TARGET_OTBM_REPAIR,
    TARGET_SPAWN_NPC,
    TARGET_TCR_HOUSE,
    TARGET_WEAPON_PROFICIENCY,
    build_routing_report,
    canonical_sha256,
)

GATEWAY_FILE_SHA = "1" * 64
REQUEST_FILE_SHA = "2" * 64
SOURCE_SHA = "3" * 64
MANIFEST_SHA = "4" * 64


def _target(pair: tuple[str, str]) -> dict[str, str]:
    return {"owner": pair[0], "capability": pair[1]}


def make_gateway(
    kind: str,
    value: object,
    *,
    binding_id: str = "reviewed.binding",
    extract_id: str = "reviewed.binding.finding",
    source_id: str = "reviewed.binding.source",
    pointer: str = "/records/0",
) -> dict[str, object]:
    value_sha = canonical_sha256(value)
    bundle: dict[str, object] = {
        "format": BUNDLE_FORMAT,
        "schemaVersion": 1,
        "manifestSha256": MANIFEST_SHA,
        "sources": [
            {
                "id": source_id,
                "path": "retained-report.json",
                "sha256": SOURCE_SHA,
                "format": {
                    "house": "canary-otbm-house-reference-parity-v1",
                    "content": "canary-tibia-content-reference-correlation-v1",
                    "proficiency": "canary-tibia-proficiency-reference-correlation-v1",
                    "drift": "canary-tibia-client-reference-drift-v1",
                }[kind],
            }
        ],
        "extracts": [
            {
                "id": extract_id,
                "sourceId": source_id,
                "pointer": pointer,
                "value": value,
                "valueSha256": value_sha,
            }
        ],
        "summary": {"sourceCount": 1, "extractCount": 1},
        "policy": {
            "readOnlyComposition": True,
            "parsesOtbm": False,
            "validatesSourceSemantics": False,
            "pathfinds": False,
            "runsE2e": False,
            "ownsDownstreamAcceptance": False,
        },
    }
    bundle["bundleSha256"] = canonical_sha256(bundle)
    gateway: dict[str, object] = {
        "format": GATEWAY_FORMAT,
        "schemaVersion": 1,
        "mode": "executed",
        "bindings": {
            "format": "canary-tibia-client-reference-evidence-bindings-v1",
            "fileSha256": "5" * 64,
            "canonicalSha256": "6" * 64,
        },
        "bindingId": binding_id,
        "kind": kind,
        "contextReferences": ["TCR-010", "reviewed:fixture"],
        "gatewayManifest": {
            "format": "canary-otbm-evidence-gateway-manifest-v1",
            "schemaVersion": 1,
            "sources": [],
        },
        "evidenceBundle": bundle,
        "evidenceBundleSha256": bundle["bundleSha256"],
        "policy": {
            "reviewedBindingIdOnly": True,
            "parsesClientFiles": False,
            "parsesOtbm": False,
            "parsesSourceReports": False,
            "reinterpretsSourceSemantics": False,
            "infersIdentifiers": False,
            "fuzzySelection": False,
            "validatesSourceSemantics": False,
            "mutatesSourceOrGameState": False,
            "runsE2e": False,
            "ownsDownstreamAcceptance": False,
            "routesAdoption": False,
            "qa018EvidenceGatewayReused": True,
        },
    }
    gateway["reportSha256"] = canonical_sha256(gateway)
    return gateway


def make_request(
    gateway: dict[str, object],
    *,
    disposition: str = "routed",
    targets: list[tuple[str, str]] | None = None,
    reason_code: str = "reviewed-existing-owner-capability",
) -> dict[str, object]:
    bundle = gateway["evidenceBundle"]
    assert isinstance(bundle, dict)
    extracts = bundle["extracts"]
    assert isinstance(extracts, list)
    extract = extracts[0]
    assert isinstance(extract, dict)
    return {
        "format": REQUEST_FORMAT,
        "schemaVersion": 1,
        "gateway": {
            "fileSha256": GATEWAY_FILE_SHA,
            "reportSha256": gateway["reportSha256"],
            "evidenceBundleSha256": gateway["evidenceBundleSha256"],
            "bindingId": gateway["bindingId"],
            "kind": gateway["kind"],
        },
        "review": {
            "reviewId": "tcr011.review.fixture",
            "statement": "Exact reviewed routing fixture.",
        },
        "routes": [
            {
                "id": "route.fixture",
                "extract": {
                    "id": extract["id"],
                    "sourceId": extract["sourceId"],
                    "pointer": extract["pointer"],
                    "valueSha256": extract["valueSha256"],
                },
                "disposition": disposition,
                "targets": [_target(pair) for pair in (targets or [])],
                "reasonCode": reason_code,
                "contextReferences": ["TCR-011", "reviewed:fixture"],
            }
        ],
    }


class AdoptionRouterTests(unittest.TestCase):
    def build(
        self, gateway: dict[str, object], request: dict[str, object]
    ) -> dict[str, object]:
        return build_routing_report(
            gateway,
            request,
            gateway_file_sha256=GATEWAY_FILE_SHA,
            request_file_sha256=REQUEST_FILE_SHA,
        )

    def test_routes_house_only_to_existing_qa003_boundary(self) -> None:
        gateway = make_gateway("house", {"state": "mismatch", "dimensions": ["footprint"]})
        request = make_request(gateway, targets=[TARGET_OTBM_REPAIR])
        report = self.build(gateway, request)
        self.assertEqual(report["format"], REPORT_FORMAT)
        self.assertEqual(report["summary"]["routedCount"], 1)
        self.assertEqual(report["routes"][0]["targets"], [_target(TARGET_OTBM_REPAIR)])
        self.assertTrue(report["policy"]["mapChangesRouteThroughQa003"])
        self.assertFalse(report["policy"]["generatesApproval"])

    def test_routes_content_creature_to_existing_owner_subset(self) -> None:
        gateway = make_gateway(
            "content",
            {
                "sourceCategory": "creatures",
                "sourceId": 12,
                "sourceName": "Rat",
                "state": "confirmed-reference",
            },
        )
        request = make_request(
            gateway, targets=[TARGET_CYCLOPEDIA, TARGET_SPAWN_NPC]
        )
        report = self.build(gateway, request)
        self.assertEqual(report["summary"]["targetCount"], 2)
        self.assertEqual(
            report["summary"]["ownerCounts"],
            {"cyclopedia-validation": 1, "otbm-spawn-npc-validation": 1},
        )

    def test_routes_content_achievement_to_achievement_owner(self) -> None:
        gateway = make_gateway(
            "content",
            {
                "sourceCategory": "achievements",
                "sourceId": 42,
                "sourceName": "Reviewed",
                "state": "partial",
            },
        )
        request = make_request(gateway, targets=[TARGET_ACHIEVEMENT])
        report = self.build(gateway, request)
        self.assertEqual(report["routes"][0]["targets"], [_target(TARGET_ACHIEVEMENT)])

    def test_routes_proficiency_to_weapon_proficiency_owner(self) -> None:
        gateway = make_gateway(
            "proficiency", {"rowKind": "source", "state": "reference-only"}
        )
        request = make_request(gateway, targets=[TARGET_WEAPON_PROFICIENCY])
        report = self.build(gateway, request)
        self.assertEqual(
            report["routes"][0]["targets"], [_target(TARGET_WEAPON_PROFICIENCY)]
        )

    def test_routes_staticmap_drift_back_to_house_parity_owner(self) -> None:
        gateway = make_gateway(
            "drift",
            {
                "id": "tcr-drift.0123456789abcdef",
                "family": "houses",
                "component": "staticmapdata",
                "recordKey": "1",
                "changeType": "changed",
                "comparisonState": "compared",
                "dependencies": ["tcr.house-reference-parity"],
                "evidence": {"beforePointer": "/houses/0", "afterPointer": "/houses/0"},
            },
        )
        request = make_request(gateway, targets=[TARGET_TCR_HOUSE])
        report = self.build(gateway, request)
        self.assertEqual(report["routes"][0]["targets"], [_target(TARGET_TCR_HOUSE)])

    def test_preserves_unsupported_house_shape_without_target(self) -> None:
        gateway = make_gateway("house", {"state": "mismatch", "dimensions": ["object-id"]})
        request = make_request(
            gateway,
            disposition="unsupported",
            targets=[],
            reason_code="unsupported-map-change-shape",
        )
        report = self.build(gateway, request)
        self.assertEqual(report["summary"]["unsupportedCount"], 1)
        self.assertEqual(report["summary"]["targetCount"], 0)

    def test_preserves_blocked_fragment_without_target(self) -> None:
        gateway = make_gateway(
            "content",
            {"sourceCategory": "quests", "state": "unresolved-id-space"},
        )
        request = make_request(
            gateway,
            disposition="blocked",
            targets=[],
            reason_code="unresolved-id-space",
        )
        report = self.build(gateway, request)
        self.assertEqual(report["summary"]["blockedCount"], 1)

    def test_rejects_cross_kind_owner(self) -> None:
        gateway = make_gateway(
            "content", {"sourceCategory": "achievements", "state": "partial"}
        )
        request = make_request(gateway, targets=[TARGET_OTBM_REPAIR])
        with self.assertRaisesRegex(AdoptionRoutingError, "not supported"):
            self.build(gateway, request)

    def test_rejects_unrecognized_routed_fragment_shape(self) -> None:
        gateway = make_gateway("content", {"state": "partial"})
        request = make_request(gateway, targets=[TARGET_ACHIEVEMENT])
        with self.assertRaisesRegex(AdoptionRoutingError, "not supported"):
            self.build(gateway, request)

    def test_rejects_unknown_direct_writer_target(self) -> None:
        gateway = make_gateway("house", {"state": "mismatch"})
        request = make_request(gateway, targets=[TARGET_OTBM_REPAIR])
        request["routes"][0]["targets"] = [
            {
                "owner": "otbm-area-materializer",
                "capability": "canary-otbm-area-materialization-result-v1",
            }
        ]
        with self.assertRaisesRegex(AdoptionRoutingError, "unknown owner/capability"):
            self.build(gateway, request)

    def test_rejects_stale_gateway_report_hash(self) -> None:
        gateway = make_gateway("house", {"state": "mismatch"})
        request = make_request(gateway, targets=[TARGET_OTBM_REPAIR])
        gateway["contextReferences"] = ["changed"]
        with self.assertRaisesRegex(AdoptionRoutingError, "reportSha256"):
            self.build(gateway, request)

    def test_rejects_stale_extract_value_hash(self) -> None:
        gateway = make_gateway("house", {"state": "mismatch"})
        request = make_request(gateway, targets=[TARGET_OTBM_REPAIR])
        bundle = gateway["evidenceBundle"]
        assert isinstance(bundle, dict)
        extracts = bundle["extracts"]
        assert isinstance(extracts, list)
        extracts[0]["value"] = {"state": "conforming"}
        bundle.pop("bundleSha256")
        bundle["bundleSha256"] = canonical_sha256(bundle)
        gateway["evidenceBundleSha256"] = bundle["bundleSha256"]
        gateway.pop("reportSha256")
        gateway["reportSha256"] = canonical_sha256(gateway)
        request["gateway"]["reportSha256"] = gateway["reportSha256"]
        request["gateway"]["evidenceBundleSha256"] = gateway["evidenceBundleSha256"]
        with self.assertRaisesRegex(AdoptionRoutingError, "valueSha256"):
            self.build(gateway, request)

    def test_rejects_missing_extract_coverage(self) -> None:
        gateway = make_gateway("house", {"state": "mismatch"})
        bundle = gateway["evidenceBundle"]
        assert isinstance(bundle, dict)
        first = copy.deepcopy(bundle["extracts"][0])
        first["id"] = "reviewed.binding.second"
        first["pointer"] = "/records/1"
        bundle["extracts"].append(first)
        bundle["summary"]["extractCount"] = 2
        bundle.pop("bundleSha256")
        bundle["bundleSha256"] = canonical_sha256(bundle)
        gateway["evidenceBundleSha256"] = bundle["bundleSha256"]
        gateway.pop("reportSha256")
        gateway["reportSha256"] = canonical_sha256(gateway)
        request = make_request(gateway, targets=[TARGET_OTBM_REPAIR])
        with self.assertRaisesRegex(AdoptionRoutingError, "cover every gateway extract"):
            self.build(gateway, request)

    def test_report_is_deterministic(self) -> None:
        gateway = make_gateway(
            "content", {"sourceCategory": "bosses", "state": "partial"}
        )
        request = make_request(
            gateway, targets=[TARGET_SPAWN_NPC, TARGET_CYCLOPEDIA]
        )
        first = self.build(gateway, request)
        second = self.build(gateway, copy.deepcopy(request))
        self.assertEqual(first, second)
        unsigned = dict(first)
        report_sha = unsigned.pop("reportSha256")
        self.assertEqual(report_sha, canonical_sha256(unsigned))


if __name__ == "__main__":
    unittest.main()
