#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one match, found {count}")
    return text.replace(old, new)


def patch_cli() -> None:
    path = ROOT / "tools/agents/real_tibia_owner_request.py"
    text = path.read_text(encoding="utf-8")
    text = once(text, '''def _positive_pr(value: int | None, label: str) -> int:
    if value is None or isinstance(value, bool) or value <= 0:
        raise RequestLifecycleError(f"{label} requires a positive actor PR")
    return value


def _history_event(
''', '''def _positive_pr(value: int | None, label: str) -> int:
    if value is None or isinstance(value, bool) or value <= 0:
        raise RequestLifecycleError(f"{label} requires a positive actor PR")
    return value


def _owner_identity(
    *,
    actor_task: str,
    actor_pr: int | None,
    owner_task: str | None,
    owner_pr: int | None,
) -> tuple[str, int]:
    resolved_pr = _positive_pr(actor_pr, "owner action")
    if owner_task is not None and owner_task != actor_task:
        raise RequestLifecycleError("owner task metadata must match the owner actor task")
    if owner_pr is not None and owner_pr != resolved_pr:
        raise RequestLifecycleError("owner PR metadata must match the owner actor PR")
    return actor_task, resolved_pr


def _history_event(
''', "owner identity helper")
    text = once(text, '''    if to_status in OWNER_CONTROLLED_STATUSES:
        if actor_role != "owner":
            raise RequestLifecycleError(
                f"transition to {to_status} requires owner actor and positive owner PR"
            )
        actor_pr = _positive_pr(actor_pr, f"transition to {to_status}")
        if owner_evidence_ref is None:
            raise RequestLifecycleError(
                f"transition to {to_status} requires stable owner evidence"
            )
        parse_stable_result_ref(owner_evidence_ref)
    elif owner_evidence_ref is not None:
        parse_stable_result_ref(owner_evidence_ref)
''', '''    resolved_owner: tuple[str, int] | None = None
    if to_status in OWNER_CONTROLLED_STATUSES:
        if actor_role != "owner":
            raise RequestLifecycleError(
                f"transition to {to_status} requires owner actor and positive owner PR"
            )
        resolved_owner = _owner_identity(
            actor_task=actor_task,
            actor_pr=actor_pr,
            owner_task=owner_task,
            owner_pr=owner_pr,
        )
        actor_pr = resolved_owner[1]
        if owner_evidence_ref is None:
            raise RequestLifecycleError(
                f"transition to {to_status} requires stable owner evidence"
            )
        parse_stable_result_ref(owner_evidence_ref)
    elif actor_role == "owner":
        resolved_owner = _owner_identity(
            actor_task=actor_task,
            actor_pr=actor_pr,
            owner_task=owner_task,
            owner_pr=owner_pr,
        )
        actor_pr = resolved_owner[1]
        if owner_evidence_ref is not None:
            parse_stable_result_ref(owner_evidence_ref)
    elif owner_evidence_ref is not None:
        parse_stable_result_ref(owner_evidence_ref)
''', "transition owner identity")
    text = once(text, '''    if actor_role == "owner":
        value["coordination"]["owner_task"] = owner_task or actor_task
        value["coordination"]["owner_pr"] = owner_pr or actor_pr
''', '''    if resolved_owner is not None:
        value["coordination"]["owner_task"], value["coordination"]["owner_pr"] = resolved_owner
''', "transition owner assignment")
    text = once(text, '''    actor_pr = _positive_pr(actor_pr, "owner result")
    if proof_level not in PROOF_RANK:
''', '''    actor_pr = _positive_pr(actor_pr, "owner result")
    resolved_owner = _owner_identity(
        actor_task=actor_task,
        actor_pr=actor_pr,
        owner_task=owner_task,
        owner_pr=owner_pr,
    )
    if proof_level not in PROOF_RANK:
''', "result identity validation")
    text = once(text, '''    value["coordination"]["owner_task"] = owner_task or actor_task
    value["coordination"]["owner_pr"] = owner_pr or actor_pr
''', '''    value["coordination"]["owner_task"], value["coordination"]["owner_pr"] = resolved_owner
''', "result owner assignment")
    text = once(text, '''    if reference.kind in {
        "github-actions-artifact",
        "external-report",
    }:
        artifact = source.get("external_artifact")
        external_digest = (
            artifact.get("sha256") if isinstance(artifact, Mapping) else None
        )
        repository_ok = (
            reference.repository is None
            or locator.get("repository") in {None, reference.repository}
        )
        return repository_ok and reference.sha256 in {
            locator.get("artifact_sha256"),
            external_digest,
        }
''', '''    if reference.kind in {
        "github-actions-artifact",
        "external-report",
    }:
        artifact = source.get("external_artifact")
        external_digest = (
            artifact.get("sha256") if isinstance(artifact, Mapping) else None
        )
        repository_ok = (
            reference.repository is None
            or locator.get("repository") in {None, reference.repository}
        )
        report_ok = (
            reference.kind != "github-actions-artifact"
            or locator.get("report_id") in {None, reference.raw}
        )
        return repository_ok and report_ok and reference.sha256 in {
            locator.get("artifact_sha256"),
            external_digest,
        }
''', "artifact identity")
    text = once(text, '''    _, parsed_refs = _stable_refs(result.get("result_refs", []), "result refs")
    owner_kind = str(request.get("owner_kind"))
''', '''    _, parsed_refs = _stable_refs(result.get("result_refs", []), "result refs")
    result_proves = set(_unique_nonempty(result.get("proves", []), "result proves"))
    result_nonproof = set(
        _unique_nonempty(result.get("does_not_prove", []), "result does_not_prove")
    )
    owner_kind = str(request.get("owner_kind"))
''', "result boundaries")
    text = once(text, '''            if any(
                _source_matches_ref(source, reference)
                for reference in parsed_refs
            ):
                matching = True
''', '''            if any(
                _source_matches_ref(source, reference)
                for reference in parsed_refs
            ):
                source_proves = set(
                    _unique_nonempty(source.get("proves", []), f"{evidence_id} source proves")
                )
                source_nonproof = set(
                    _unique_nonempty(
                        source.get("does_not_prove", []),
                        f"{evidence_id} source does_not_prove",
                    )
                )
                extra_proves = sorted(source_proves - result_proves)
                if extra_proves:
                    raise RequestLifecycleError(
                        f"evidence source in {evidence_id} claims owner proof absent from the retained result: {extra_proves}"
                    )
                missing_nonproof = sorted(result_nonproof - source_nonproof)
                if missing_nonproof:
                    raise RequestLifecycleError(
                        f"evidence source in {evidence_id} drops retained result nonproof boundaries: {missing_nonproof}"
                    )
                matching = True
''', "consumption boundaries")
    text = once(text, '''    generated_paths = set(candidate.generated_files(as_of))
''', '''    fenced = Corpus.load(corpus.root)
    fenced_document = _request_document(fenced, request_id)
    _check_expected(fenced_document, expected_status, document.sha256)

    generated_paths = set(candidate.generated_files(as_of))
''', "pre-write fence")
    path.write_text(text, encoding="utf-8")


def patch_tests() -> None:
    path = ROOT / "tools/agents/test_real_tibia_owner_request.py"
    text = path.read_text(encoding="utf-8")
    text = text.replace(
        'proves=["The bounded owner observation completed."],\n            does_not_prove=["No broader module or whole-game parity is proven."],',
        'proves=["The bounded owner observation completed."],\n            does_not_prove=["No broader module or whole-game parity is proven."],',
    )
    text = once(text, '''            proves=["The retained owner result proves the bounded observation."],
            does_not_prove=["The result does not prove unrelated behavior."],
''', '''            proves=["The bounded owner observation completed."],
            does_not_prove=["No broader module or whole-game parity is proven."],
''', "test source boundaries")
    anchor = '''    def test_all_owner_routes_reach_consumed_with_matching_evidence(self) -> None:
'''
    additions = '''    def test_owner_metadata_must_match_history_actor(self) -> None:
        request = self.route_request("feature")
        ready = owner.transition_value(
            request, expected_status="draft", to_status="ready-for-owner-triage",
            at="2026-07-25T10:00:00+02:00", actor="collector",
            actor_role="collector", actor_task="CAN-COLLECTOR", actor_pr=10,
            reason="Ready.",
        )
        with self.assertRaisesRegex(owner.RequestLifecycleError, "owner PR metadata must match"):
            owner.transition_value(
                ready, expected_status="ready-for-owner-triage",
                to_status="accepted-by-owner", at="2026-07-25T10:10:00+02:00",
                actor="owner", actor_role="owner", actor_task="CAN-OWNER",
                actor_pr=11, owner_pr=12, owner_evidence_ref=OWNER_REF,
                reason="Mismatched metadata.",
            )
        active = self.advance_to_active(request)
        with self.assertRaisesRegex(owner.RequestLifecycleError, "owner task metadata must match"):
            owner.record_result_value(
                active, expected_status="active", at="2026-07-25T11:00:00+02:00",
                actor="owner", actor_task="CAN-OWNER", actor_pr=11,
                reason="Mismatched metadata.", owner_evidence_ref=OWNER_REF,
                owner_task="CAN-OTHER", owner_pr=11, result_refs=[RESULT_REF],
                proof_level="behavior-proven", proves=["Bounded."],
                does_not_prove=["No broader claim."], blockers=[],
            )

    def test_all_owner_routes_reach_consumed_with_matching_evidence(self) -> None:
'''
    text = once(text, anchor, additions, "owner identity tests")
    anchor = '''    def test_dry_run_write_and_rollback_are_transactional(self) -> None:
'''
    additions = '''    def test_consumption_preserves_retained_proof_boundaries(self) -> None:
        request = self.result_available(self.route_request("feature"), "feature")
        record = self.owner_record("feature", request["request_id"])
        record["sources"][0]["proves"].append("Unretained extra claim.")
        with self.assertRaisesRegex(owner.RequestLifecycleError, "claims owner proof absent"):
            self.consume(request, record)
        record = self.owner_record("feature", request["request_id"])
        record["sources"][0]["does_not_prove"] = ["Different caveat."]
        with self.assertRaisesRegex(owner.RequestLifecycleError, "drops retained result nonproof"):
            self.consume(request, record)

    def test_write_rechecks_document_after_candidate_validation(self) -> None:
        request = self.route_request("feature")
        self.write_record(self.record())
        self.write_request(request, "feature")
        self.refresh()
        request_path = self.root / f"docs/agents/real-tibia/evidence/requests/feature/{request['request_id']}.yaml"
        original_validate = owner._validate_candidate

        def concurrent_edit(corpus, document, value, as_of):
            candidate = original_validate(corpus, document, value, as_of)
            current = json.loads(request_path.read_text())
            current["history"][0]["reason"] = "Concurrent same-status edit."
            dump(request_path, current)
            return candidate

        with mock.patch.object(owner, "_validate_candidate", side_effect=concurrent_edit):
            with self.assertRaisesRegex(owner.RequestLifecycleError, "stale request document"):
                owner.apply_candidate(
                    root=self.root, request_id=request["request_id"],
                    expected_status="draft", expected_document_sha256=None,
                    as_of=AS_OF, write=True,
                    mutation=lambda value, corpus: owner.transition_value(
                        value, expected_status="draft", to_status="ready-for-owner-triage",
                        at="2026-07-25T10:00:00+02:00", actor="collector",
                        actor_role="collector", actor_task="CAN-COLLECTOR",
                        actor_pr=10, reason="Ready.",
                    ),
                )

    def test_dry_run_write_and_rollback_are_transactional(self) -> None:
'''
    text = once(text, anchor, additions, "boundary and fence tests")
    path.write_text(text, encoding="utf-8")


def patch_docs_task_catalog() -> None:
    doc = ROOT / "docs/agents/real-tibia/evidence/OWNER_REQUEST_LIFECYCLE.md"
    text = doc.read_text(encoding="utf-8")
    text = once(text, '''- use a record and source proof level no higher than the owner result;
- pass the full evidence corpus validator.
''', '''- use a record and source proof level no higher than the owner result;
- copy no owner `proves` claim absent from the retained result;
- preserve every retained `does_not_prove` boundary;
- pass the full evidence corpus validator.
''', "operator boundary docs")
    text = once(text, "The Collector must never fabricate owner metadata merely to move a request forward.\n", "The Collector must never fabricate owner metadata merely to move a request forward. Owner task and PR fields must exactly match the owner actor recorded in history.\n", "operator owner identity")
    doc.write_text(text, encoding="utf-8")

    catalog = ROOT / "docs/agents/MODULE_CATALOG.md"
    text = catalog.read_text(encoding="utf-8")
    anchor = "| Real Tibia module registry | merged (#324) | Registry-as-code discovery for stable module IDs, categories, source roles, immutable baselines, multidimensional maturity, freshness, dependencies, path/affected-module lookup and deterministic generated indexes | `docs/agents/real-tibia/**`, `tools/agents/real_tibia_registry*.py`, focused tests, `.github/workflows/real-tibia-registry.yml`, ADR | Reuse before any parity task. One JSON-compatible YAML record per module; generated Markdown is read-only; path matches are discovery hints, never ownership or parity proof. |\n"
    row = "| Real Tibia owner-request lifecycle | active (#921) | Dry-run-first schema-v1 transitions, optimistic status/content fencing, retained-result references, exact evidence consumption and rollback-capable request/index writes | `tools/agents/real_tibia_owner_request.py`, focused tests, `docs/agents/real-tibia/evidence/OWNER_REQUEST_LIFECYCLE.md`, `.github/workflows/real-tibia-evidence.yml` | Reuse this CLI; do not hand-edit lifecycle state, invent owner evidence, execute owner work from a Collector task or promote proof beyond explicit boundaries. |\n"
    if row not in text:
        text = once(text, anchor, anchor + row, "catalog row")
    catalog.write_text(text, encoding="utf-8")

    task = ROOT / "docs/agents/tasks/active/CAN-20260725-rtec-003-owner-request-lifecycle.md"
    text = task.read_text(encoding="utf-8")
    text = text.replace("status: implementing", "status: review", 1)
    text = text.replace("updated: 2026-07-25T15:35:00+02:00", "updated: 2026-07-25T16:20:00+02:00", 1)
    for item in (
        "Add a standard-library CLI for request transition, owner-result recording and Collector consumption.",
        "Require optimistic expected-status checks so stale agents cannot overwrite newer request state.",
        "Enforce the existing legal transition graph and owner-controlled state evidence rules.",
        "Require stable result references, explicit proof/nonproof boundaries and exact owner task/PR metadata.",
        "Permit `consumed` only when referenced evidence records exist, link the request and contain owner-result sources consistent with the request owner kind.",
        "Prevent result proof from being promoted beyond owner-produced proof.",
        "Keep writes atomic, regenerate deterministic indexes and restore prior files on failure.",
        "Add focused positive/negative tests for E2E, OTBM, TCR, protocol and feature routes.",
        "Document the operator workflow and keep the existing vocations request unchanged until real owner evidence exists.",
        "Preserve all owner implementation paths as read-only and start no RTEC-004 campaign workers.",
    ):
        text = once(text, f"- [ ] {item}", f"- [x] {item}", f"acceptance {item}")
    text = once(text, "status: implementing\ncontext_routes:", "status: validating\ncontext_routes:", "checkpoint status")
    text = once(text, "Implement the bounded lifecycle CLI and tests, then validate the exact diff and current head.", "Verify exact implementation-head CI, complete structured review and protected final gate, then squash-merge and verify lifecycle archival before RTEC-004.", "remaining work")
    text = once(text, "  - exact focused and CI results for the implementation head\n", "  - exact GitHub Actions results for the implementation head\n", "unknown")
    text = once(text, "next_action: Implement the lifecycle CLI and focused tests.", "next_action: Verify exact implementation-head CI, review the complete diff, apply the protected final gate and merge without feature expansion.", "next action")
    task.write_text(text, encoding="utf-8")


def cleanup() -> None:
    for rel in (
        ".github/workflows/rtec-003-bootstrap.yml",
        ".github/workflows/rtec-003-implementation.yml",
        "tools/agents/rtec_003_apply_patch.py",
        "tools/agents/rtec_003_hardening.py",
    ):
        path = ROOT / rel
        if path.exists():
            path.unlink()


def main() -> None:
    patch_cli()
    patch_tests()
    patch_docs_task_catalog()
    cleanup()


if __name__ == "__main__":
    main()
