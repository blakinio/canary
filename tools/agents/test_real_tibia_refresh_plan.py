from __future__ import annotations

import copy
import datetime as dt
import hashlib
import importlib.util
from pathlib import Path

from real_tibia_evidence_test_support import *

PLAN_PATH = Path(__file__).with_name("real_tibia_refresh_plan.py")
PLAN_SPEC = importlib.util.spec_from_file_location("real_tibia_refresh_plan", PLAN_PATH)
assert PLAN_SPEC and PLAN_SPEC.loader
planner = importlib.util.module_from_spec(PLAN_SPEC)
PLAN_SPEC.loader.exec_module(planner)

NEW_COMMIT = "b" * 40
OTHER_COMMIT = "c" * 40


class RealTibiaRefreshPlanTests(EvidenceTestCase):
    def accepted_record(
        self,
        evidence_id: str = "RT-COMBAT-0001",
        module: str = "combat",
        *,
        observed: dt.date = AS_OF,
        path: str = "src/game/combat/example.cpp",
        source_id: str = "current-canary-combat",
        commit: str | None = COMMIT,
    ) -> dict[str, object]:
        record = self.record(evidence_id, module)
        record.update(
            record_status="accepted",
            evidence_state="PROVEN",
            confidence="HIGH",
        )
        record["freshness"]["observed_or_verified_at"] = observed.isoformat()
        record["review"].update(
            status="accepted",
            task_id="CAN-TEST",
            pr=1,
            reviewer="test-reviewer",
            reviewed_at=f"{observed.isoformat()}T10:00:00+00:00",
        )
        record["sources"][0]["source_id"] = source_id
        record["sources"][0]["selected"]["files"] = [path]
        record["sources"][0]["locator"].update(
            repository="blakinio/canary",
            repository_path=path,
            commit_sha=commit,
        )
        record["current_canary_comparison"]["exact_paths"] = [path]
        record["current_canary_comparison"]["baseline"]["canary_commit"] = commit
        return record

    def snapshot(self) -> dict[str, str]:
        evidence_root = self.root / "docs/agents/real-tibia/evidence"
        return {
            path.relative_to(self.root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(evidence_root.rglob("*"))
            if path.is_file()
        }

    def test_freshness_boundaries_and_explicit_stale_are_prioritized(self) -> None:
        warning = self.accepted_record(
            "RT-COMBAT-0001",
            observed=AS_OF - dt.timedelta(days=30),
        )
        warning["freshness"].update(warning_after_days=30, invalid_after_days=90)
        invalid = self.accepted_record(
            "RT-COMBAT-0002",
            observed=AS_OF - dt.timedelta(days=90),
            path="src/game/combat/invalid.cpp",
            source_id="current-canary-combat-invalid",
        )
        invalid["freshness"].update(warning_after_days=30, invalid_after_days=90)
        explicit = self.accepted_record(
            "RT-COMBAT-0003",
            path="src/game/combat/explicit.cpp",
            source_id="current-canary-combat-explicit",
        )
        explicit.update(record_status="stale", evidence_state="STALE")
        self.write_record(warning)
        self.write_record(invalid)
        self.write_record(explicit)
        self.refresh()

        plan = planner.build_refresh_plan(self.root, as_of=AS_OF)
        by_id = {item["evidence_id"]: item for item in plan["items"]}
        self.assertEqual(by_id["RT-COMBAT-0001"]["priority"], "normal")
        self.assertEqual(
            by_id["RT-COMBAT-0001"]["reasons"][0]["code"],
            "freshness-warning-window-reached",
        )
        self.assertEqual(by_id["RT-COMBAT-0002"]["priority"], "critical")
        self.assertEqual(
            by_id["RT-COMBAT-0002"]["reasons"][0]["code"],
            "invalidation-window-expired",
        )
        self.assertEqual(by_id["RT-COMBAT-0003"]["priority"], "critical")
        self.assertEqual(
            by_id["RT-COMBAT-0003"]["reasons"][0]["code"],
            "explicit-state",
        )

    def test_version_delta_uses_exact_current_anchors_and_preserves_history(self) -> None:
        current = self.accepted_record("RT-COMBAT-0001")
        historical = self.accepted_record(
            "RT-PROTOCOL-0001",
            "protocol",
            path="docs/history/protocol.md",
            source_id="official-protocol-history",
            commit=None,
        )
        historical["authority_dimension"] = "historical-version"
        historical["sources"][0]["source_type"] = "official-news"
        historical["sources"][0]["locator"]["repository"] = None
        historical["sources"][0]["locator"]["repository_path"] = None
        historical["sources"][0]["locator"]["url"] = "https://example.com/history"
        historical["sources"][0]["selected"]["files"] = []
        historical["current_canary_comparison"]["exact_paths"] = []
        historical["applicability"]["observed_in"] = [
            marker(
                "EXACT",
                "RT-PROTOCOL-0001",
                official_tibia_release="Historical Release",
            )
        ]
        unknown = self.accepted_record(
            "RT-COMBAT-0002",
            path="src/game/combat/unknown.cpp",
            source_id="current-canary-combat-unknown",
            commit=None,
        )
        unknown["sources"][0]["locator"]["commit_sha"] = COMMIT
        self.write_record(current)
        self.write_record(historical)
        self.write_record(unknown)
        self.refresh()

        plan = planner.build_refresh_plan(
            self.root,
            as_of=AS_OF,
            target_versions=[
                f"canary_commit={NEW_COMMIT}",
                "official_tibia_release=Current Release",
            ],
        )
        self.assertEqual(
            [item["evidence_id"] for item in plan["items"]],
            ["RT-COMBAT-0001"],
        )
        reason = plan["items"][0]["reasons"][0]
        self.assertEqual(reason["kind"], "version-delta")
        self.assertEqual(reason["axis"], "canary_commit")
        self.assertEqual(reason["recorded_values"], [COMMIT])
        self.assertEqual(reason["target_value"], NEW_COMMIT)

    def test_changed_path_source_and_module_selectors_are_exact_and_read_only(self) -> None:
        record = self.accepted_record("RT-COMBAT-0001")
        self.write_record(record)
        self.refresh()
        before = self.snapshot()

        plan = planner.build_refresh_plan(
            self.root,
            as_of=AS_OF,
            changed_paths=["src/game/combat"],
            changed_source_ids=["current-canary-combat"],
            module_ids=["combat"],
        )
        after = self.snapshot()

        self.assertEqual(before, after)
        self.assertEqual(plan["summary"]["selected_evidence_records"], 1)
        self.assertEqual(plan["items"][0]["priority"], "high")
        self.assertEqual(
            {reason["kind"] for reason in plan["items"][0]["reasons"]},
            {"changed-path", "changed-source", "module"},
        )
        self.assertEqual(plan["items"][0]["exact_paths"], ["src/game/combat/example.cpp"])

    def test_argument_order_does_not_change_plan_or_digests(self) -> None:
        combat = self.accepted_record("RT-COMBAT-0001")
        protocol = self.accepted_record(
            "RT-PROTOCOL-0001",
            "protocol",
            path="src/server/network/protocol.cpp",
            source_id="current-canary-protocol",
            commit=OTHER_COMMIT,
        )
        self.write_record(protocol)
        self.write_record(combat)
        self.refresh()

        first = planner.build_refresh_plan(
            self.root,
            as_of=AS_OF,
            target_versions=[
                f"canary_commit={NEW_COMMIT}",
                "official_tibia_release=Current Release",
            ],
            changed_paths=["src/server", "src/game"],
            changed_source_ids=["current-canary-protocol", "current-canary-combat"],
            module_ids=["protocol", "combat"],
        )
        second = planner.build_refresh_plan(
            self.root,
            as_of=AS_OF,
            target_versions=[
                "official_tibia_release=Current Release",
                f"canary_commit={NEW_COMMIT}",
            ],
            changed_paths=["src/game", "src/server"],
            changed_source_ids=["current-canary-combat", "current-canary-protocol"],
            module_ids=["combat", "protocol"],
        )

        self.assertEqual(first, second)
        self.assertTrue(planner.verify_plan_sha256(first))
        tampered = copy.deepcopy(first)
        tampered["items"][0]["priority"] = "normal"
        self.assertFalse(planner.verify_plan_sha256(tampered))

    def test_prepublication_rejected_and_superseded_records_are_not_actionable(self) -> None:
        candidate = self.record("RT-COMBAT-0001")
        candidate["current_canary_comparison"]["exact_paths"] = ["src/candidate.cpp"]

        old = self.accepted_record(
            "RT-COMBAT-0002",
            path="src/old.cpp",
            source_id="current-canary-old",
        )
        old.update(
            record_status="superseded",
            evidence_state="SUPERSEDED",
            superseded_by=["RT-COMBAT-0003"],
        )
        current = self.accepted_record(
            "RT-COMBAT-0003",
            path="src/current.cpp",
            source_id="current-canary-current",
        )
        current["supersedes"] = ["RT-COMBAT-0002"]
        rejected = self.accepted_record(
            "RT-PROTOCOL-0001",
            "protocol",
            path="src/rejected.cpp",
            source_id="current-canary-rejected",
        )
        rejected.update(record_status="rejected", evidence_state="REJECTED")

        self.write_record(candidate)
        self.write_record(old)
        self.write_record(current)
        self.write_record(rejected)
        self.refresh()

        plan = planner.build_refresh_plan(
            self.root,
            as_of=AS_OF,
            module_ids=["combat", "protocol"],
        )
        self.assertEqual(
            [item["evidence_id"] for item in plan["items"]],
            ["RT-COMBAT-0003"],
        )
        self.assertEqual(plan["summary"]["prepublication_evidence_records"], 1)
        self.assertEqual(plan["summary"]["nonactionable_published_records"], 2)

    def test_selector_and_corpus_errors_fail_closed(self) -> None:
        with self.assertRaisesRegex(planner.RefreshPlanError, "duplicate target version axis"):
            planner.parse_target_versions(
                [f"canary_commit={COMMIT}", f"canary_commit={NEW_COMMIT}"]
            )
        with self.assertRaisesRegex(planner.RefreshPlanError, "unknown target version axis"):
            planner.parse_target_versions(["invented=value"])
        with self.assertRaisesRegex(planner.RefreshPlanError, "safe exact"):
            planner.normalize_changed_paths(["../secret"])
        with self.assertRaisesRegex(planner.RefreshPlanError, "without wildcards"):
            planner.normalize_changed_paths(["src/*.cpp"])
        with self.assertRaisesRegex(planner.RefreshPlanError, "unknown canonical module_id"):
            planner.normalize_module_ids(["missing"], frozenset({"combat"}))

        invalid = self.accepted_record("RT-COMBAT-0001")
        invalid["sources"][0]["locator"]["repository_path"] = "../secret"
        self.write_record(invalid)
        with self.assertRaisesRegex(planner.RefreshPlanError, "RTEC-UNSAFE-PATH"):
            planner.build_refresh_plan(self.root, as_of=AS_OF)


if __name__ == "__main__":
    import unittest

    unittest.main()
