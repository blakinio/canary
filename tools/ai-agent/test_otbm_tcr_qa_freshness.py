from __future__ import annotations

import copy
import unittest

from otbm_tcr_qa_freshness import (
    MANIFEST_FORMAT,
    PROVENANCE_FORMAT,
    REPORT_FORMAT,
    ROUTING_FORMAT,
    TcrQaFreshnessError,
    build_freshness_impact_report,
    canonical_sha256,
)

ROUTING_FILE_SHA = "1" * 64
PROVENANCE_FILE_SHA = "2" * 64
MANIFEST_FILE_SHA = "3" * 64
CURRENT_BOM_SHA = "4" * 64
PREVIOUS_BOM_SHA = "5" * 64
VALUE_SHA = "6" * 64

TARGET_REPAIR = {
    "owner": "otbm-repair-recommendation",
    "capability": "canary-otbm-repair-recommendation-v1",
}
TARGET_HOUSE = {
    "owner": "tcr-house-parity",
    "capability": "canary-otbm-house-reference-parity-v1",
}


def _sign(document: dict[str, object]) -> dict[str, object]:
    document["reportSha256"] = canonical_sha256(document)
    return document


def make_route(
    *,
    route_id: str = "route.house",
    extract_id: str = "extract.house",
    disposition: str = "routed",
    targets: list[dict[str, str]] | None = None,
    reason_code: str = "reviewed-existing-owner-capability",
) -> dict[str, object]:
    return {
        "id": route_id,
        "extract": {
            "id": extract_id,
            "sourceId": "source.house",
            "pointer": "/findings/0",
            "valueSha256": VALUE_SHA,
        },
        "disposition": disposition,
        "targets": copy.deepcopy(targets if targets is not None else [TARGET_REPAIR]),
        "reasonCode": reason_code,
        "contextReferences": ["TCR-011", "reviewed:fixture"],
    }


def make_routing(
    routes: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    return _sign(
        {
            "format": ROUTING_FORMAT,
            "schemaVersion": 1,
            "gateway": {"reportSha256": "7" * 64},
            "request": {"fileSha256": "8" * 64},
            "routes": copy.deepcopy(routes if routes is not None else [make_route()]),
            "summary": {"routeCount": len(routes if routes is not None else [1])},
            "policy": {"readOnlyComposition": True},
        }
    )


def make_provenance(
    *,
    component_changes: list[dict[str, object]] | None = None,
    dimension_freshness: list[dict[str, object]] | None = None,
    removed_dimensions: list[str] | None = None,
) -> dict[str, object]:
    changes = component_changes if component_changes is not None else [
        {
            "componentId": "tcr.house-reference",
            "status": "changed",
            "before": {"sha256": "9" * 64},
            "after": {"sha256": "a" * 64},
        }
    ]
    dimensions = dimension_freshness if dimension_freshness is not None else [
        {
            "dimensionId": "qa006.house-certification",
            "status": "stale",
            "changedDependencies": ["tcr.house-reference"],
        },
        {
            "dimensionId": "qa006.unrelated",
            "status": "current",
            "changedDependencies": [],
        },
    ]
    return _sign(
        {
            "format": PROVENANCE_FORMAT,
            "schemaVersion": 1,
            "currentReleaseId": "release.current",
            "previousReleaseId": "release.previous",
            "currentBomSha256": CURRENT_BOM_SHA,
            "previousBomSha256": PREVIOUS_BOM_SHA,
            "componentChanges": copy.deepcopy(changes),
            "dimensionFreshness": copy.deepcopy(dimensions),
            "removedDimensions": copy.deepcopy([] if removed_dimensions is None else removed_dimensions),
            "summary": {
                "changedComponentCount": len(changes),
                "staleDimensionCount": sum(
                    1 for row in dimensions if row["status"] == "stale"
                ),
            },
            "policy": {
                "timestampsUsedAsFreshnessEvidence": False,
                "rerunsValidators": False,
            },
        }
    )


def make_mapping(
    route: dict[str, object],
    *,
    mapping_id: str = "mapping.house",
    target: dict[str, str] | None = TARGET_REPAIR,
    component_ids: list[str] | None = None,
    dimension_ids: list[str] | None = None,
) -> dict[str, object]:
    return {
        "id": mapping_id,
        "routeId": route["id"],
        "extract": copy.deepcopy(route["extract"]),
        "target": copy.deepcopy(target),
        "componentIds": copy.deepcopy(
            component_ids if component_ids is not None else ["tcr.house-reference"]
        ),
        "dimensionIds": copy.deepcopy(
            dimension_ids
            if dimension_ids is not None
            else ["qa006.house-certification"]
        ),
        "contextReferences": ["OWA-003A", "reviewed:fixture"],
    }


def make_manifest(
    routing: dict[str, object],
    provenance: dict[str, object],
    *,
    mappings: list[dict[str, object]] | None = None,
    routing_file_sha: str = ROUTING_FILE_SHA,
    provenance_file_sha: str = PROVENANCE_FILE_SHA,
) -> dict[str, object]:
    routes = routing["routes"]
    assert isinstance(routes, list)
    default_mappings = [make_mapping(routes[0])]
    return {
        "format": MANIFEST_FORMAT,
        "schemaVersion": 1,
        "routing": {
            "fileSha256": routing_file_sha,
            "reportSha256": routing["reportSha256"],
        },
        "releaseProvenance": {
            "fileSha256": provenance_file_sha,
            "reportSha256": provenance["reportSha256"],
            "currentBomSha256": provenance["currentBomSha256"],
            "previousBomSha256": provenance["previousBomSha256"],
        },
        "review": {
            "reviewId": "owa003a.review.fixture",
            "statement": "Exact reviewed route-to-QA freshness mapping fixture.",
        },
        "mappings": copy.deepcopy(mappings or default_mappings),
    }


def build_fixture(
    routing: dict[str, object],
    provenance: dict[str, object],
    manifest: dict[str, object],
) -> dict[str, object]:
    return build_freshness_impact_report(
        routing,
        provenance,
        manifest,
        routing_file_sha256=ROUTING_FILE_SHA,
        provenance_file_sha256=PROVENANCE_FILE_SHA,
        manifest_file_sha256=MANIFEST_FILE_SHA,
    )


class TcrQaFreshnessTests(unittest.TestCase):
    def test_builds_exact_routed_stale_impact(self) -> None:
        routing = make_routing()
        provenance = make_provenance()
        manifest = make_manifest(routing, provenance)
        report = build_fixture(routing, provenance, manifest)

        self.assertEqual(report["format"], REPORT_FORMAT)
        self.assertEqual(report["summary"]["routeCount"], 1)
        self.assertEqual(report["summary"]["routedImpactCount"], 1)
        self.assertEqual(
            report["summary"]["mappedChangedComponentIds"],
            ["tcr.house-reference"],
        )
        self.assertEqual(
            report["summary"]["mappedStaleDimensionIds"],
            ["qa006.house-certification"],
        )
        impact = report["impacts"][0]
        self.assertEqual(impact["freshnessStatus"], "stale")
        self.assertEqual(impact["target"], TARGET_REPAIR)
        self.assertEqual(impact["downstreamEvidence"]["qa002"], "not-evaluated")
        self.assertTrue(report["policy"]["exactChangedDependencyEqualityRequired"])
        self.assertFalse(report["policy"]["selectsQa002Validators"])
        self.assertFalse(report["policy"]["runsPhysicalE2e"])
        unsigned = dict(report)
        report_sha = unsigned.pop("reportSha256")
        self.assertEqual(report_sha, canonical_sha256(unsigned))

    def test_preserves_unsupported_route_as_targetless_review(self) -> None:
        route = make_route(
            disposition="unsupported",
            targets=[],
            reason_code="unsupported-fragment-shape",
        )
        routing = make_routing([route])
        provenance = make_provenance()
        manifest = make_manifest(
            routing,
            provenance,
            mappings=[
                make_mapping(
                    route,
                    target=None,
                    component_ids=[],
                    dimension_ids=[],
                )
            ],
        )
        report = build_fixture(routing, provenance, manifest)
        impact = report["impacts"][0]
        self.assertEqual(impact["disposition"], "unsupported")
        self.assertEqual(impact["freshnessStatus"], "not-mapped")
        self.assertEqual(impact["componentIds"], [])
        self.assertEqual(impact["dimensionIds"], [])
        self.assertEqual(report["summary"]["unsupportedImpactCount"], 1)

    def test_preserves_blocked_route_as_targetless_review(self) -> None:
        route = make_route(
            disposition="blocked",
            targets=[],
            reason_code="stale-evidence",
        )
        routing = make_routing([route])
        provenance = make_provenance()
        manifest = make_manifest(
            routing,
            provenance,
            mappings=[
                make_mapping(
                    route,
                    mapping_id="mapping.blocked",
                    target=None,
                    component_ids=[],
                    dimension_ids=[],
                )
            ],
        )
        report = build_fixture(routing, provenance, manifest)
        self.assertEqual(report["summary"]["blockedImpactCount"], 1)
        self.assertEqual(report["impacts"][0]["downstreamEvidence"]["qa007"], "not-evaluated")

    def test_requires_every_route_and_exact_target_once(self) -> None:
        route_a = make_route(route_id="route.a", extract_id="extract.a")
        route_b = make_route(
            route_id="route.b", extract_id="extract.b", targets=[TARGET_HOUSE]
        )
        routing = make_routing([route_a, route_b])
        provenance = make_provenance()
        manifest = make_manifest(
            routing, provenance, mappings=[make_mapping(route_a)]
        )
        with self.assertRaisesRegex(TcrQaFreshnessError, "cover every routing route"):
            build_fixture(routing, provenance, manifest)

        wrong_target = make_mapping(route_b, mapping_id="mapping.wrong-target", target=TARGET_REPAIR)
        manifest = make_manifest(
            routing,
            provenance,
            mappings=[make_mapping(route_a), wrong_target],
        )
        with self.assertRaisesRegex(TcrQaFreshnessError, "map every exact target once"):
            build_fixture(routing, provenance, manifest)

    def test_requires_exact_extract_pin(self) -> None:
        routing = make_routing()
        provenance = make_provenance()
        routes = routing["routes"]
        assert isinstance(routes, list)
        mapping = make_mapping(routes[0])
        mapping["extract"]["pointer"] = "/findings/1"
        manifest = make_manifest(routing, provenance, mappings=[mapping])
        with self.assertRaisesRegex(TcrQaFreshnessError, "exact route extract"):
            build_fixture(routing, provenance, manifest)

    def test_requires_changed_component_and_stale_dimension(self) -> None:
        routing = make_routing()
        routes = routing["routes"]
        assert isinstance(routes, list)

        provenance = make_provenance(component_changes=[])
        manifest = make_manifest(routing, provenance)
        with self.assertRaisesRegex(TcrQaFreshnessError, "unchanged or unknown component"):
            build_fixture(routing, provenance, manifest)

        provenance = make_provenance(
            dimension_freshness=[
                {
                    "dimensionId": "qa006.house-certification",
                    "status": "current",
                    "changedDependencies": [],
                }
            ]
        )
        manifest = make_manifest(routing, provenance)
        with self.assertRaisesRegex(TcrQaFreshnessError, "non-stale dimension"):
            build_fixture(routing, provenance, manifest)

    def test_rejects_removed_component_and_dimension(self) -> None:
        routing = make_routing()
        provenance = make_provenance(
            component_changes=[
                {"componentId": "tcr.house-reference", "status": "removed"}
            ]
        )
        manifest = make_manifest(routing, provenance)
        with self.assertRaisesRegex(TcrQaFreshnessError, "cannot bind removed component"):
            build_fixture(routing, provenance, manifest)

        provenance = make_provenance(
            dimension_freshness=[],
            removed_dimensions=["qa006.house-certification"],
        )
        manifest = make_manifest(routing, provenance)
        with self.assertRaisesRegex(TcrQaFreshnessError, "references removed dimension"):
            build_fixture(routing, provenance, manifest)

    def test_requires_exact_aggregate_changed_dependencies(self) -> None:
        routing = make_routing()
        provenance = make_provenance(
            component_changes=[
                {"componentId": "tcr.house-reference", "status": "changed"},
                {"componentId": "tcr.staticmapdata", "status": "changed"},
            ],
            dimension_freshness=[
                {
                    "dimensionId": "qa006.house-certification",
                    "status": "stale",
                    "changedDependencies": [
                        "tcr.house-reference",
                        "tcr.staticmapdata",
                    ],
                }
            ],
        )
        manifest = make_manifest(routing, provenance)
        with self.assertRaisesRegex(
            TcrQaFreshnessError, "do not exactly equal QA-016 changedDependencies"
        ):
            build_fixture(routing, provenance, manifest)

    def test_requires_exact_file_and_report_identities(self) -> None:
        routing = make_routing()
        provenance = make_provenance()
        manifest = make_manifest(
            routing, provenance, routing_file_sha="f" * 64
        )
        with self.assertRaisesRegex(TcrQaFreshnessError, "routing identity"):
            build_fixture(routing, provenance, manifest)

        manifest = make_manifest(routing, provenance)
        manifest["releaseProvenance"]["currentBomSha256"] = "e" * 64
        with self.assertRaisesRegex(TcrQaFreshnessError, "releaseProvenance identity"):
            build_fixture(routing, provenance, manifest)

    def test_rejects_tampered_signed_inputs(self) -> None:
        routing = make_routing()
        routing["routes"][0]["reasonCode"] = "tampered"
        provenance = make_provenance()
        manifest = make_manifest(routing, provenance)
        with self.assertRaisesRegex(TcrQaFreshnessError, "reportSha256"):
            build_fixture(routing, provenance, manifest)

    def test_output_is_deterministic_under_mapping_order_permutation(self) -> None:
    route_a = make_route(route_id="route.a", extract_id="extract.a")
    route_b = make_route(
        route_id="route.b", extract_id="extract.b", targets=[TARGET_HOUSE]
    )
    routing = make_routing([route_b, route_a])
    provenance = make_provenance(
        component_changes=[
            {"componentId": "tcr.staticmapdata", "status": "changed"},
            {"componentId": "tcr.house-reference", "status": "changed"},
        ],
        dimension_freshness=[
            {
                "dimensionId": "qa006.house-certification",
                "status": "stale",
                "changedDependencies": ["tcr.house-reference"],
            },
            {
                "dimensionId": "qa006.staticmap",
                "status": "stale",
                "changedDependencies": ["tcr.staticmapdata"],
            },
        ],
    )
    mapping_a = make_mapping(route_a)
    mapping_b = make_mapping(
        route_b,
        mapping_id="mapping.staticmap",
        target=TARGET_HOUSE,
        component_ids=["tcr.staticmapdata"],
        dimension_ids=["qa006.staticmap"],
    )
    manifest_a = make_manifest(
        routing, provenance, mappings=[mapping_b, mapping_a]
    )
    manifest_b = make_manifest(
        routing, provenance, mappings=[mapping_a, mapping_b]
    )
    report_a = build_fixture(routing, provenance, manifest_a)
    report_b = build_fixture(routing, provenance, manifest_b)
    self.assertEqual(report_a, report_b)


if __name__ == "__main__":
    unittest.main()
