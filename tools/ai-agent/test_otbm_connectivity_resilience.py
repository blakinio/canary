from __future__ import annotations

import unittest

from otbm_connectivity_resilience import (
    MANIFEST_FORMAT,
    REPORT_FORMAT,
    ConnectivityContext,
    ConnectivityResilienceError,
    ModeGraph,
    build_connectivity_resilience_report,
    canonical_report_sha256,
)
from otbm_reachability_graph import _transition_edges
from otbm_reachability_types import TileState, TransitionSpec, TransitionState


def sha(char: str) -> str:
    return char * 64


def tile(position: tuple[int, int, int], *, strict: bool = True, optimistic: bool = True) -> TileState:
    return TileState(
        position=position,
        tile_index=0,
        kind="tile",
        house_id=None,
        flags=0,
        placement_ordinals=(),
        item_ids=(),
        has_ground=True,
        strict_walkable=strict,
        optimistic_walkable=optimistic,
        static_blockers=(),
        conditional_blockers=() if strict else (1000,),
        unknown_appearances=(),
        avoid_items=(),
        uncertainties=() if strict else ("door-state",),
    )


def transition(
    transition_id: str,
    source: tuple[int, int, int],
    destination: tuple[int, int, int],
    *,
    bidirectional: bool = False,
    uncertainties: tuple[str, ...] = (),
) -> TransitionState:
    spec = TransitionSpec(
        transition_id=transition_id,
        kind="teleport",
        source=source,
        destination=destination,
        origin="manifest",
        item_id=None,
        expected_item_ids=(),
        bidirectional=bidirectional,
        uncertainties=uncertainties,
        evidence={"review": "fixture"},
        script_status=None,
    )
    return TransitionState(
        spec=spec,
        valid=True,
        strict_eligible=True,
        optimistic_eligible=True,
        status="valid",
        issues=(),
    )


def context(
    tiles: dict[tuple[int, int, int], TileState],
    *,
    transitions: tuple[TransitionState, ...] = (),
    executable: bool = False,
) -> ConnectivityContext:
    positions = sorted(tiles)
    lower = tuple(min(value[i] for value in positions) for i in range(3))
    upper = tuple(max(value[i] for value in positions) for i in range(3))
    strict_edges = _transition_edges(transitions, lower, upper, strict=True)
    optimistic_edges = _transition_edges(transitions, lower, upper, strict=False)
    modes = {
        "strict": ModeGraph("strict", True, strict_edges),
        "optimistic": ModeGraph("optimistic", False, optimistic_edges),
    }
    if executable:
        modes["executable"] = ModeGraph("executable", True, strict_edges)
    return ConnectivityContext(
        lower=lower,
        upper=upper,
        allow_diagonal=False,
        tiles=tiles,
        transitions=transitions,
        modes=modes,
        provenance={"mapSha256": sha("a"), "worldIndexSha256": sha("b")},
        canonical_findings=(),
        canonical_finding_summary={"total": 0, "bySeverity": {}, "byCode": {}, "truncated": False},
    )


def manifest_for(
    ctx: ConnectivityContext,
    *,
    routes: list[dict] | None = None,
    entrapment: list[dict] | None = None,
    topology: dict | None = None,
) -> dict:
    return {
        "format": MANIFEST_FORMAT,
        "schemaVersion": 1,
        "source": {"mapSha256": sha("a"), "worldIndexSha256": sha("b")},
        "region": {"from": list(ctx.lower), "to": list(ctx.upper), "allowDiagonal": False},
        "routes": routes or [],
        "entrapmentTargets": entrapment or [],
        "topology": topology,
    }


def build(ctx: ConnectivityContext, manifest: dict) -> dict:
    return build_connectivity_resilience_report(
        manifest=manifest,
        context=ctx,
        input_pins={"manifest": {"sha256": sha("c")}},
    )


class ConnectivityResilienceTests(unittest.TestCase):
    def test_line_route_reports_single_edge_fragility(self) -> None:
        points = [(0, 0, 7), (1, 0, 7), (2, 0, 7)]
        ctx = context({value: tile(value) for value in points})
        report = build(
            ctx,
            manifest_for(
                ctx,
                routes=[
                    {
                        "id": "route.line",
                        "reason": "Reviewed line",
                        "mode": "strict",
                        "start": list(points[0]),
                        "goal": list(points[-1]),
                    }
                ],
            ),
        )
        route = report["routes"][0]
        self.assertEqual(report["format"], REPORT_FORMAT)
        self.assertEqual(route["classification"], "single-edge-fragile")
        self.assertEqual(len(route["criticalEdges"]), 2)
        self.assertEqual(report["findings"][0]["code"], "ROUTE_SINGLE_EDGE_FRAGILE")
        self.assertTrue(report["policy"]["canonicalReachabilityBfsReused"])
        self.assertFalse(report["policy"]["secondPathfinderImplemented"])

    def test_diamond_route_proves_edge_disjoint_alternative(self) -> None:
        points = [(0, 0, 7), (1, 0, 7), (0, 1, 7), (1, 1, 7)]
        ctx = context({value: tile(value) for value in points})
        report = build(
            ctx,
            manifest_for(
                ctx,
                routes=[
                    {
                        "id": "route.diamond",
                        "reason": "Reviewed diamond",
                        "mode": "strict",
                        "start": [0, 0, 7],
                        "goal": [1, 1, 7],
                    }
                ],
            ),
        )
        route = report["routes"][0]
        self.assertEqual(route["classification"], "edge-disjoint-alternative")
        self.assertEqual(route["criticalEdges"], [])
        self.assertTrue(route["alternativeEdgeDisjointPath"])
        baseline = {
            (tuple(edge["from"]), tuple(edge["to"]), edge["transitionId"])
            for edge in route["baselineEdges"]
        }
        alternative = {
            (tuple(edge["from"]), tuple(edge["to"]), edge["transitionId"])
            for edge in route["alternativeEdgeDisjointEdges"]
        }
        self.assertFalse(baseline & alternative)

    def test_optimistic_only_route_preserves_conditional_boundary(self) -> None:
        points = [(0, 0, 7), (1, 0, 7), (2, 0, 7)]
        tiles = {
            points[0]: tile(points[0]),
            points[1]: tile(points[1], strict=False, optimistic=True),
            points[2]: tile(points[2]),
        }
        ctx = context(tiles)
        report = build(
            ctx,
            manifest_for(
                ctx,
                routes=[
                    {
                        "id": "route.conditional",
                        "reason": "Reviewed conditional crossing",
                        "mode": "optimistic",
                        "start": list(points[0]),
                        "goal": list(points[-1]),
                    }
                ],
            ),
        )
        route = report["routes"][0]
        self.assertTrue(route["reachable"])
        self.assertFalse(route["strictReachable"])
        self.assertTrue(route["optimisticReachable"])
        self.assertTrue(route["conditionalOnly"])
        self.assertIn("ROUTE_REQUIRES_CONDITIONAL_EVIDENCE", {value["code"] for value in report["findings"]})

    def test_unavailable_executable_mode_fails_closed(self) -> None:
        points = [(0, 0, 7), (1, 0, 7)]
        ctx = context({value: tile(value) for value in points})
        manifest = manifest_for(
            ctx,
            routes=[
                {
                    "id": "route.exec",
                    "reason": "Needs reviewed executable evidence",
                    "mode": "executable",
                    "start": [0, 0, 7],
                    "goal": [1, 0, 7],
                }
            ],
        )
        with self.assertRaisesRegex(ConnectivityResilienceError, "unavailable"):
            build(ctx, manifest)

    def test_entrapment_candidate_is_static_only(self) -> None:
        points = [(0, 0, 7), (2, 0, 7)]
        ctx = context({value: tile(value) for value in points})
        report = build(
            ctx,
            manifest_for(
                ctx,
                entrapment=[
                    {
                        "id": "entry.isolated",
                        "reason": "Reviewed isolated entry",
                        "mode": "strict",
                        "entry": [0, 0, 7],
                        "exits": [[2, 0, 7]],
                    }
                ],
            ),
        )
        target = report["entrapmentTargets"][0]
        self.assertEqual(target["classification"], "static-entrapment-candidate")
        self.assertFalse(target["runtimeEntrapmentProven"])
        self.assertFalse(report["policy"]["runtimeEntrapmentClaimed"])
        self.assertFalse(report["ok"])

    def test_entrapment_exit_path_is_proven(self) -> None:
        points = [(0, 0, 7), (1, 0, 7), (2, 0, 7)]
        ctx = context({value: tile(value) for value in points})
        report = build(
            ctx,
            manifest_for(
                ctx,
                entrapment=[
                    {
                        "id": "entry.open",
                        "reason": "Reviewed exit",
                        "mode": "strict",
                        "entry": [0, 0, 7],
                        "exits": [[2, 0, 7]],
                    }
                ],
            ),
        )
        self.assertEqual(report["entrapmentTargets"][0]["classification"], "exit-proven")
        self.assertEqual(report["entrapmentTargets"][0]["nearestReachableExit"], [2, 0, 7])

    def test_transition_topology_reports_one_way_dead_end_and_cycle(self) -> None:
        positions = [(0, 0, 7), (2, 0, 7), (10, 0, 7), (12, 0, 7)]
        transitions = (
            transition("teleport.one-way", positions[0], positions[1]),
            transition("teleport.cycle-a", positions[2], positions[3]),
            transition("teleport.cycle-b", positions[3], positions[2]),
        )
        ctx = context({value: tile(value) for value in positions}, transitions=transitions)
        report = build(
            ctx,
            manifest_for(ctx, topology={"mode": "strict", "kinds": ["teleport"]}),
        )
        topology = report["topology"]
        self.assertEqual(len(topology["oneWayEdges"]), 1)
        self.assertEqual(topology["oneWayEdges"][0]["transitionId"], "teleport.one-way")
        self.assertEqual(len(topology["deadEnds"]), 1)
        self.assertTrue(any(value["closed"] for value in topology["cycles"]))
        codes = {value["code"] for value in report["findings"]}
        self.assertIn("TRANSITION_ONE_WAY_REVIEW_CANDIDATE", codes)
        self.assertIn("TRANSITION_DEAD_END_REVIEW_CANDIDATE", codes)
        self.assertIn("TRANSITION_CLOSED_CYCLE_REVIEW_CANDIDATE", codes)

    def test_reviewed_intentional_one_way_is_not_finding(self) -> None:
        points = [(0, 0, 7), (2, 0, 7)]
        transitions = (transition("teleport.intentional", points[0], points[1], uncertainties=("one-way-intended",)),)
        ctx = context({value: tile(value) for value in points}, transitions=transitions)
        report = build(ctx, manifest_for(ctx, topology={"mode": "strict", "kinds": ["teleport"]}))
        self.assertEqual(report["topology"]["oneWayEdges"][0]["classification"], "reviewed-one-way-intended")
        self.assertNotIn("TRANSITION_ONE_WAY_REVIEW_CANDIDATE", {value["code"] for value in report["findings"]})

    def test_manifest_provenance_mismatch_fails_closed(self) -> None:
        points = [(0, 0, 7), (1, 0, 7)]
        ctx = context({value: tile(value) for value in points})
        manifest = manifest_for(ctx, topology={"mode": "strict", "kinds": ["teleport"]})
        manifest["source"]["mapSha256"] = sha("f")
        with self.assertRaisesRegex(ConnectivityResilienceError, "source map SHA-256"):
            build(ctx, manifest)

    def test_output_is_deterministic(self) -> None:
        points = [(0, 0, 7), (1, 0, 7), (0, 1, 7), (1, 1, 7)]
        ctx = context({value: tile(value) for value in points})
        manifest = manifest_for(
            ctx,
            routes=[
                {
                    "id": "route.deterministic",
                    "reason": "Stable fixture",
                    "mode": "strict",
                    "start": [0, 0, 7],
                    "goal": [1, 1, 7],
                }
            ],
        )
        first = build(ctx, manifest)
        second = build(ctx, manifest)
        self.assertEqual(canonical_report_sha256(first), canonical_report_sha256(second))


if __name__ == "__main__":
    unittest.main()
