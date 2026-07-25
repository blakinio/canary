#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one match, found {count}")
    return text.replace(old, new)


def patch_cli() -> None:
    path = ROOT / "tools/agents/real_tibia_owner_request.py"
    text = path.read_text(encoding="utf-8")
    text = replace_once(
        text,
        "def _history_event(\n",
        '''def _owner_identity(
    *,
    actor_task: str,
    actor_pr: int | None,
    owner_task: str | None,
    owner_pr: int | None,
) -> tuple[str, int]:
    if actor_pr is None or isinstance(actor_pr, bool) or actor_pr <= 0:
        raise RequestLifecycleError("owner action requires a positive actor PR")
    if owner_task is not None and owner_task != actor_task:
        raise RequestLifecycleError("owner task metadata must match the owner actor task")
    if owner_pr is not None and owner_pr != actor_pr:
        raise RequestLifecycleError("owner PR metadata must match the owner actor PR")
    return actor_task, actor_pr


def _history_event(
''',
        "owner identity helper",
    )
    text = replace_once(
        text,
        '''    if to_status in OWNER_CONTROLLED_STATUSES:
        if actor_role != "owner" or actor_pr is None:
            raise RequestLifecycleError(f"transition to {to_status} requires owner actor and positive owner PR")
        if owner_evidence_ref is None:
            raise RequestLifecycleError(f"transition to {to_status} requires stable owner evidence")
        parse_stable_result_ref(owner_evidence_ref)
    elif owner_evidence_ref is not None:
        parse_stable_result_ref(owner_evidence_ref)
''',
        '''    resolved_owner: tuple[str, int] | None = None
    if to_status in OWNER_CONTROLLED_STATUSES:
        if actor_role != "owner":
            raise RequestLifecycleError(f"transition to {to_status} requires an owner actor")
        resolved_owner = _owner_identity(
            actor_task=actor_task,
            actor_pr=actor_pr,
            owner_task=owner_task,
            owner_pr=owner_pr,
        )
        if owner_evidence_ref is None:
            raise RequestLifecycleError(f"transition to {to_status} requires stable owner evidence")
        parse_stable_result_ref(owner_evidence_ref)
    elif actor_role == "owner":
        resolved_owner = _owner_identity(
            actor_task=actor_task,
            actor_pr=actor_pr,
            owner_task=owner_task,
            owner_pr=owner_pr,
        )
        if owner_evidence_ref is not None:
            parse_stable_result_ref(owner_evidence_ref)
    elif owner_evidence_ref is not None:
        parse_stable_result_ref(owner_evidence_ref)
''',
        "owner transition validation",
    )
    text = replace_once(
        text,
        '''    if actor_role == "owner":
        coordination = value["coordination"]
        coordination["owner_task"] = owner_task or actor_task
        coordination["owner_pr"] = owner_pr or actor_pr
''',
        '''    if resolved_owner is not None:
        coordination = value["coordination"]
        coordination["owner_task"], coordination["owner_pr"] = resolved_owner
''',
        "owner transition assignment",
    )
    text = text.replace("    actor_pr: int,\n", "    actor_pr: int | None,\n", 1)
    text = replace_once(
        text,
        '''    parse_stable_result_ref(owner_evidence_ref)
    if actor_pr <= 0:
        raise RequestLifecycleError("owner result requires a positive actor PR")

    value = copy.deepcopy(dict(request))
''',
        '''    parse_stable_result_ref(owner_evidence_ref)
    resolved_owner = _owner_identity(
        actor_task=actor_task,
        actor_pr=actor_pr,
        owner_task=owner_task,
        owner_pr=owner_pr,
    )

    value = copy.deepcopy(dict(request))
''',
        "record result owner validation",
    )
    text = replace_once(
        text,
        '''    value["coordination"]["owner_task"] = owner_task or actor_task
    value["coordination"]["owner_pr"] = owner_pr or actor_pr
''',
        '''    value["coordination"]["owner_task"], value["coordination"]["owner_pr"] = resolved_owner
''',
        "record result owner assignment",
    )
    text = replace_once(
        text,
        '''    if reference.kind == "github-actions-artifact":
        repository_ok = locator.get("repository") in {None, reference.repository}
        artifact = source.get("external_artifact")
        external_digest = artifact.get("sha256") if isinstance(artifact, Mapping) else None
        return repository_ok and reference.sha256 in {locator.get("artifact_sha256"), external_digest}
''',
        '''    if reference.kind == "github-actions-artifact":
        repository_ok = locator.get("repository") in {None, reference.repository}
        report_ok = locator.get("report_id") in {None, reference.raw}
        artifact = source.get("external_artifact")
        external_digest = artifact.get("sha256") if isinstance(artifact, Mapping) else None
        return repository_ok and report_ok and reference.sha256 in {locator.get("artifact_sha256"), external_digest}
''',
        "artifact reference matching",
    )
    text = replace_once(
        text,
        '''    _, parsed_refs = _validate_stable_refs(result.get("result_refs", []), "result refs")
    owner_kind = request.get("owner_kind")
''',
        '''    _, parsed_refs = _validate_stable_refs(result.get("result_refs", []), "result refs")
    result_proves = set(_unique_nonempty(result.get("proves", []), "result proves"))
    result_nonproof = set(_unique_nonempty(result.get("does_not_prove", []), "result does_not_prove"))
    owner_kind = request.get("owner_kind")
''',
        "result boundaries",
    )
    text = replace_once(
        text,
        '''            if any(_source_matches_ref(source, reference) for reference in parsed_refs):
                matching_sources.append(source)
''',
        '''            if any(_source_matches_ref(source, reference) for reference in parsed_refs):
                source_proves = set(_unique_nonempty(source.get("proves", []), f"{evidence_id} source proves"))
                source_nonproof = set(
                    _unique_nonempty(source.get("does_not_prove", []), f"{evidence_id} source does_not_prove")
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
                matching_sources.append(source)
''',
        "source proof boundaries",
    )
    text = replace_once(
        text,
        "    generated_paths = set(candidate.generated_files(as_of))\n",
        '''    fenced = Corpus.load(corpus.root)
    fenced_document = _request_document(fenced, request_id)
    _check_expected_document(fenced_document, expected_status, document.sha256)

    generated_paths = set(candidate.generated_files(as_of))
''',
        "write fence",
    )
    path.write_text(text, encoding="utf-8")


def write_tests() -> None:
    path = ROOT / "tools/agents/test_real_tibia_owner_request.py"
    path.write_text(r'''from __future__ import annotations

import copy
import hashlib
import json
from unittest import mock

import real_tibia_owner_request as lifecycle
from real_tibia_evidence_test_support import AS_OF, Corpus, EvidenceTestCase

OWNER_TASK = "CAN-OWNER-TEST"
OWNER_PR = 77
AT = "2026-07-25T15:45:00+02:00"
COMMIT = "b" * 40
DIGEST = "c" * 64


class RealTibiaOwnerRequestLifecycleTests(EvidenceTestCase):
    def prepared_request(self, owner_kind: str = "e2e") -> dict[str, object]:
        request = self.request(f"RTREQ-{owner_kind.upper()}-COMBAT-0001")
        request["owner_kind"] = owner_kind
        request["status"] = "active"
        request["coordination"]["owner_task"] = OWNER_TASK
        request["coordination"]["owner_pr"] = OWNER_PR
        request["history"].append({
            "at": AT, "actor": "owner", "actor_role": "owner",
            "actor_task": OWNER_TASK, "actor_pr": OWNER_PR,
            "from_status": "planned", "to_status": "active",
            "reason": "Owner began bounded execution.",
            "owner_evidence_ref": f"github-pr:blakinio/canary#{OWNER_PR}",
        })
        return request

    def owner_source(self, owner_kind: str, reference: str) -> dict[str, object]:
        source_type = {
            "e2e": "physical-e2e-result", "otbm": "otbm-owner-result",
            "tcr": "tcr-owner-result", "protocol": "packet-capture",
            "feature": "feature-owner-result",
        }[owner_kind]
        source = copy.deepcopy(self.record()["sources"][0])
        source["source_id"] = f"{owner_kind}-owner-result"
        source["source_type"] = source_type
        source["proof_level_reached"] = "protocol-proven" if owner_kind in {"tcr", "protocol"} else "behavior-proven"
        source["proves"] = ["Bounded owner result proves the selected behavior."]
        source["does_not_prove"] = ["The retained result does not prove whole-game parity."]
        source["external_artifact"] = None
        source["locator"] = {"url": None, "repository": None, "commit_sha": None,
            "repository_path": None, "build": None, "report_id": None, "artifact_sha256": None}
        parsed = lifecycle.parse_stable_result_ref(reference)
        if parsed.kind == "repo-file":
            source["locator"].update(repository=parsed.repository, commit_sha=parsed.commit_sha,
                                     repository_path=parsed.repository_path)
        elif parsed.kind == "github-commit":
            source["locator"].update(repository=parsed.repository, commit_sha=parsed.commit_sha)
        elif parsed.kind in {"github-pr", "github-actions-run", "github-actions-job"}:
            source["locator"]["report_id"] = parsed.raw
        elif parsed.kind == "github-actions-artifact":
            source["locator"].update(repository=parsed.repository, report_id=parsed.raw,
                                     artifact_sha256=parsed.sha256)
        else:
            source["locator"]["artifact_sha256"] = parsed.sha256
        return source

    def result_available(self, owner_kind: str, reference: str) -> dict[str, object]:
        request = self.prepared_request(owner_kind)
        proof = "protocol-proven" if owner_kind in {"tcr", "protocol"} else "behavior-proven"
        return lifecycle.record_result_value(
            request, expected_status="active", at=AT, actor="owner",
            actor_task=OWNER_TASK, actor_pr=OWNER_PR,
            reason="Owner retained a bounded result.",
            owner_evidence_ref=f"github-pr:blakinio/canary#{OWNER_PR}",
            owner_task=OWNER_TASK, owner_pr=OWNER_PR, result_refs=[reference],
            proof_level=proof,
            proves=["Bounded owner result proves the selected behavior."],
            does_not_prove=["The retained result does not prove whole-game parity."],
            blockers=[],
        )

    def evidence_document(self, request_id: str, owner_kind: str, reference: str):
        record = self.record()
        record["owner_request_refs"] = [request_id]
        record["proof_level"] = "protocol-proven" if owner_kind in {"tcr", "protocol"} else "behavior-proven"
        record["sources"] = [self.owner_source(owner_kind, reference)]
        path = self.root / "docs/agents/real-tibia/evidence/modules/combat/records/RT-COMBAT-0001.yaml"
        content = json.dumps(record, indent=2, sort_keys=True) + "\n"
        return lifecycle.LoadedDocument(path, path.relative_to(self.root).as_posix(), record,
                                        hashlib.sha256(content.encode()).hexdigest())

    def test_stable_result_reference_grammar(self) -> None:
        accepted = [
            "github-pr:blakinio/canary#921", f"github-commit:blakinio/canary@{COMMIT}",
            "github-actions-run:blakinio/canary#123", "github-actions-job:blakinio/canary#456",
            f"github-actions-artifact:blakinio/canary#789@sha256:{DIGEST}",
            f"repo-file:blakinio/canary@{COMMIT}:reports/result.json",
            f"external-report:sha256:{DIGEST}",
        ]
        self.assertEqual([lifecycle.parse_stable_result_ref(item).raw for item in accepted], accepted)
        for rejected in ("", " github-pr:blakinio/canary#1", "github-pr:bad#1",
                         f"repo-file:blakinio/canary@{COMMIT}:../secret"):
            with self.subTest(rejected=rejected), self.assertRaises(lifecycle.RequestLifecycleError):
                lifecycle.parse_stable_result_ref(rejected)

    def test_owner_transition_requires_exact_owner_identity(self) -> None:
        request = self.request(); request["status"] = "ready-for-owner-triage"
        with self.assertRaisesRegex(lifecycle.RequestLifecycleError, "owner actor"):
            lifecycle.transition_value(request, expected_status="ready-for-owner-triage",
                to_status="accepted-by-owner", at=AT, actor="collector", actor_role="collector",
                actor_task="CAN-COLLECTOR", actor_pr=1, reason="invalid",
                owner_evidence_ref="github-pr:blakinio/canary#1")
        with self.assertRaisesRegex(lifecycle.RequestLifecycleError, "must match"):
            lifecycle.transition_value(request, expected_status="ready-for-owner-triage",
                to_status="accepted-by-owner", at=AT, actor="owner", actor_role="owner",
                actor_task=OWNER_TASK, actor_pr=OWNER_PR, reason="accepted",
                owner_evidence_ref=f"github-pr:blakinio/canary#{OWNER_PR}", owner_pr=OWNER_PR + 1)
        value = lifecycle.transition_value(request, expected_status="ready-for-owner-triage",
            to_status="accepted-by-owner", at=AT, actor="owner", actor_role="owner",
            actor_task=OWNER_TASK, actor_pr=OWNER_PR, reason="accepted",
            owner_evidence_ref=f"github-pr:blakinio/canary#{OWNER_PR}")
        self.assertEqual((value["coordination"]["owner_task"], value["coordination"]["owner_pr"]),
                         (OWNER_TASK, OWNER_PR))

    def test_record_result_requires_positive_actor_pr_and_exact_metadata(self) -> None:
        request = self.prepared_request("feature")
        kwargs = dict(expected_status="active", at=AT, actor="owner", actor_task=OWNER_TASK,
            reason="result", owner_evidence_ref=f"github-pr:blakinio/canary#{OWNER_PR}",
            owner_task=OWNER_TASK, owner_pr=OWNER_PR,
            result_refs=[f"repo-file:blakinio/canary@{COMMIT}:reports/result.json"],
            proof_level="behavior-proven", proves=["Bounded owner result proves the selected behavior."],
            does_not_prove=["The retained result does not prove whole-game parity."], blockers=[])
        with self.assertRaisesRegex(lifecycle.RequestLifecycleError, "positive actor PR"):
            lifecycle.record_result_value(request, actor_pr=None, **kwargs)
        with self.assertRaisesRegex(lifecycle.RequestLifecycleError, "must match"):
            lifecycle.record_result_value(request, actor_pr=OWNER_PR, **{**kwargs, "owner_task": "OTHER"})
        self.assertEqual(lifecycle.record_result_value(request, actor_pr=OWNER_PR, **kwargs)["status"],
                         "result-available")

    def test_consumption_succeeds_for_all_owner_routes(self) -> None:
        refs = {
            "e2e": f"github-actions-artifact:blakinio/canary#9@sha256:{DIGEST}",
            "otbm": f"repo-file:blakinio/canary@{COMMIT}:reports/otbm.json",
            "tcr": f"github-commit:blakinio/canary@{COMMIT}",
            "protocol": "github-actions-job:blakinio/canary#44",
            "feature": f"external-report:sha256:{DIGEST}",
        }
        for owner_kind, reference in refs.items():
            with self.subTest(owner_kind=owner_kind):
                request = self.result_available(owner_kind, reference)
                document = self.evidence_document(str(request["request_id"]), owner_kind, reference)
                consumed = lifecycle.consume_result_value(request, expected_status="result-available",
                    at=AT, actor="collector", actor_role="collector", actor_task="CAN-COLLECTOR",
                    actor_pr=921, reason="Consumed exact retained owner result.",
                    evidence_ids=["RT-COMBAT-0001"], evidence_documents=[document])
                self.assertEqual(consumed["status"], "consumed")

    def test_consumption_rejects_wrong_link_type_level_and_boundaries(self) -> None:
        reference = f"repo-file:blakinio/canary@{COMMIT}:reports/result.json"
        request = self.result_available("feature", reference)
        document = self.evidence_document(str(request["request_id"]), "feature", reference)
        cases = []
        value = copy.deepcopy(document.value); value["owner_request_refs"] = []
        cases.append((value, "must link owner request"))
        value = copy.deepcopy(document.value); value["sources"][0]["source_type"] = "current-canary"
        cases.append((value, "lacks a feature owner-result source"))
        value = copy.deepcopy(document.value); value["proof_level"] = "gameplay-proven"
        cases.append((value, "exceeds owner result proof"))
        value = copy.deepcopy(document.value); value["sources"][0]["proves"].append("Unretained extra claim.")
        cases.append((value, "claims owner proof absent"))
        value = copy.deepcopy(document.value); value["sources"][0]["does_not_prove"] = ["Different caveat."]
        cases.append((value, "drops retained result nonproof"))
        for value, message in cases:
            content = json.dumps(value, indent=2, sort_keys=True) + "\n"
            changed = lifecycle.LoadedDocument(document.path, document.relative_path, value,
                                               hashlib.sha256(content.encode()).hexdigest())
            with self.subTest(message=message), self.assertRaisesRegex(lifecycle.RequestLifecycleError, message):
                lifecycle.consume_result_value(request, expected_status="result-available", at=AT,
                    actor="collector", actor_role="collector", actor_task="CAN-COLLECTOR", actor_pr=921,
                    reason="consume", evidence_ids=["RT-COMBAT-0001"], evidence_documents=[changed])

    def test_apply_candidate_dry_run_sha_fence_rollback_and_write(self) -> None:
        record = self.record(); record["owner_request_refs"] = ["RTREQ-E2E-COMBAT-0001"]
        self.write_record(record); self.write_request(self.request()); self.refresh()
        request_path = self.root / "docs/agents/real-tibia/evidence/requests/e2e/RTREQ-E2E-COMBAT-0001.yaml"
        original = request_path.read_bytes()
        mutation = lambda value, corpus: lifecycle.transition_value(value, expected_status="draft",
            to_status="ready-for-owner-triage", at=AT, actor="reviewer", actor_role="reviewer",
            actor_task="CAN-REVIEW", actor_pr=1, reason="bounded and ready")
        dry = lifecycle.apply_candidate(root=self.root, request_id="RTREQ-E2E-COMBAT-0001",
            expected_status="draft", expected_document_sha256=None, as_of=AS_OF, write=False,
            mutation=mutation)
        self.assertEqual(dry["status"], "ready-for-owner-triage")
        self.assertEqual(request_path.read_bytes(), original)
        with self.assertRaisesRegex(lifecycle.RequestLifecycleError, "expected sha256"):
            lifecycle.apply_candidate(root=self.root, request_id="RTREQ-E2E-COMBAT-0001",
                expected_status="draft", expected_document_sha256="d" * 64, as_of=AS_OF,
                write=True, mutation=mutation)
        with mock.patch.object(lifecycle, "write_generated", side_effect=RuntimeError("boom")):
            with self.assertRaisesRegex(RuntimeError, "boom"):
                lifecycle.apply_candidate(root=self.root, request_id="RTREQ-E2E-COMBAT-0001",
                    expected_status="draft", expected_document_sha256=None, as_of=AS_OF,
                    write=True, mutation=mutation)
        self.assertEqual(request_path.read_bytes(), original)
        self.assertEqual(Corpus.load(self.root).validate(AS_OF).errors, ())
        lifecycle.apply_candidate(root=self.root, request_id="RTREQ-E2E-COMBAT-0001",
            expected_status="draft", expected_document_sha256=None, as_of=AS_OF,
            write=True, mutation=mutation)
        self.assertEqual(json.loads(request_path.read_text())["status"], "ready-for-owner-triage")
        self.assertEqual(Corpus.load(self.root).validate(AS_OF).errors, ())

    def test_repository_vocations_request_remains_unexecuted(self) -> None:
        request = next(item.value for item in Corpus.load(self.repo).request_documents
                       if item.value["request_id"] == "RTREQ-FEATURE-VOCATIONS-0001")
        self.assertEqual(request["status"], "ready-for-owner-triage")
        self.assertIsNone(request["coordination"]["owner_task"])
        self.assertIsNone(request["coordination"]["owner_pr"])
        self.assertFalse(request["result"]["available"])
        self.assertEqual(request["result"]["result_refs"], [])
''', encoding="utf-8")


def write_docs() -> None:
    (ROOT / "docs/agents/real-tibia/evidence/OWNER_REQUEST_LIFECYCLE.md").write_text('''# Real Tibia owner-request lifecycle

`tools/agents/real_tibia_owner_request.py` is the single dry-run-first mutation surface for schema-version-1 owner requests. It coordinates evidence; it never executes owner work.

## Safety contract

Every command requires `--expected-status`. `--expected-document-sha256` adds a caller-supplied content fence. A write re-reads the request and rejects any status or content change after the initial load. Candidate state is validated against the complete corpus before writing. The request and deterministic indexes are backed up and restored if validation or generation fails.

Omit `--write` for the default dry run. Dry run prints the candidate request and its canonical SHA-256 without changing the repository.

## Roles and transitions

The canonical transition graph remains in `real_tibia_evidence_lib.py`.

- Collector/reviewer states advance only where that graph permits.
- `accepted-by-owner`, `active` and `result-available` require an owner actor, a positive exact owner PR and stable owner evidence.
- Owner task/PR metadata must exactly match the actor recorded in history.
- `result-available` is created only by `record-result`; `consumed` only by `consume-result`.

## Stable retained-result references

```text
github-pr:<owner>/<repo>#<pr>
github-commit:<owner>/<repo>@<40-hex-sha>
github-actions-run:<owner>/<repo>#<run-id>
github-actions-job:<owner>/<repo>#<job-id>
github-actions-artifact:<owner>/<repo>#<artifact-id>@sha256:<64-hex>
repo-file:<owner>/<repo>@<40-hex-sha>:<safe-repository-path>
external-report:sha256:<64-hex>
```

Large or proprietary payloads stay outside Git. Git stores compact references, hashes, proof boundaries and owner metadata.

## Transition example

```sh
python tools/agents/real_tibia_owner_request.py transition \
  --request-id RTREQ-E2E-COMBAT-0001 \
  --expected-status ready-for-owner-triage \
  --as-of 2026-07-25 \
  --at 2026-07-25T16:00:00+02:00 \
  --actor "Universal E2E owner" \
  --actor-role owner \
  --actor-task CAN-OWNER-EXAMPLE \
  --actor-pr 123 \
  --to-status accepted-by-owner \
  --owner-evidence-ref github-pr:blakinio/canary#123 \
  --reason "Owner accepted the bounded request."
```

Review dry-run JSON, then repeat with `--write` and preferably the printed document SHA-256.

## Owner result and consumption

`record-result` is valid only from `active`. It requires retained references, the strongest proof level reached, non-empty `proves`, non-empty `does_not_prove`, and optional blockers. A lower-than-requested result remains valid evidence but does not satisfy a higher requested proof level.

Before `consume-result`, the Collector adds or updates the exact evidence records. Consumption verifies that each selected record exists, links the request, stays below the result proof ceiling, uses the correct owner-route source type, matches a retained reference, introduces no unretained owner claim and preserves every retained nonproof boundary.

## Current vocations request

`RTREQ-FEATURE-VOCATIONS-0001` remains `ready-for-owner-triage`. RTEC-003 does not accept it, execute it, fabricate a result or alter `RT-VOCATIONS-0005`. Runtime level-gain and promotion application remain `UNKNOWN` until the feature owner produces retained evidence.
''', encoding="utf-8")


def patch_docs_and_task() -> None:
    readme = ROOT / "docs/agents/real-tibia/evidence/README.md"
    text = readme.read_text(encoding="utf-8")
    old = "Requests are contracts directed to Universal E2E, OTBM/OWA, TCR, protocol/client owners or feature programmes. The Collector may create and advance Collector-controlled states, but transitions to `accepted-by-owner`, `active` and `result-available` require an owner actor and stable owner evidence reference.\n"
    new = old + "\nUse the dry-run-first `tools/agents/real_tibia_owner_request.py` CLI and `OWNER_REQUEST_LIFECYCLE.md`. Direct manual lifecycle mutation is not supported.\n"
    readme.write_text(replace_once(text, old, new, "README"), encoding="utf-8")

    catalog = ROOT / "docs/agents/MODULE_CATALOG.md"
    text = catalog.read_text(encoding="utf-8")
    anchor = "| Real Tibia module registry | merged (#324) | Registry-as-code discovery for stable module IDs, categories, source roles, immutable baselines, multidimensional maturity, freshness, dependencies, path/affected-module lookup and deterministic generated indexes | `docs/agents/real-tibia/**`, `tools/agents/real_tibia_registry*.py`, focused tests, `.github/workflows/real-tibia-registry.yml`, ADR | Reuse before any parity task. One JSON-compatible YAML record per module; generated Markdown is read-only; path matches are discovery hints, never ownership or parity proof. |\n"
    row = "| Real Tibia owner-request lifecycle | active (#921) | Dry-run-first schema-v1 transitions, optimistic status/content fencing, retained-result references, exact evidence consumption and rollback-capable request/index writes | `tools/agents/real_tibia_owner_request.py`, focused tests, `docs/agents/real-tibia/evidence/OWNER_REQUEST_LIFECYCLE.md`, `.github/workflows/real-tibia-evidence.yml` | Reuse this CLI; do not hand-edit lifecycle state, invent owner evidence, execute owner work from a Collector task or promote proof beyond explicit boundaries. |\n"
    catalog.write_text(replace_once(text, anchor, anchor + row, "catalog"), encoding="utf-8")

    task = ROOT / "docs/agents/tasks/active/CAN-20260725-rtec-003-owner-request-lifecycle.md"
    text = task.read_text(encoding="utf-8")
    text = text.replace("status: implementing", "status: review", 1)
    text = text.replace("updated: 2026-07-25T15:35:00+02:00", "updated: 2026-07-25T16:05:00+02:00", 1)
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
        text = replace_once(text, f"- [ ] {item}", f"- [x] {item}", f"acceptance {item}")
    text = replace_once(text, "status: implementing\ncontext_routes:", "status: validating\ncontext_routes:", "checkpoint status")
    text = replace_once(text,
        "Implement the bounded lifecycle CLI and tests, then validate the exact diff and current head.",
        "Verify exact implementation-head CI, complete structured review and the protected final gate, then squash-merge and verify lifecycle archival before RTEC-004.", "remaining work")
    text = replace_once(text,
        "  - the v1 request schema and runtime validator already define legal transitions\n",
        "  - the v1 request schema and runtime validator already define legal transitions\n  - the dry-run-first CLI enforces exact owner identity, stable references, source-route matching, proof ceilings and nonproof preservation\n  - transactional writes re-check the request and restore request/index backups on failure\n  - focused tests cover E2E, OTBM, TCR, protocol and feature routes without mutating the real vocations request\n", "checkpoint proven")
    text = replace_once(text,
        "  - exact focused and CI results for the implementation head\n",
        "  - exact GitHub Actions results for the implementation commit\n", "checkpoint unknown")
    text = replace_once(text,
        "next_action: Implement the lifecycle CLI and focused tests.",
        "next_action: Verify exact implementation-head CI, review the complete diff, apply the protected final gate and merge without feature expansion.", "next action")
    task.write_text(text, encoding="utf-8")


def write_permanent_workflow() -> None:
    (ROOT / ".github/workflows/real-tibia-evidence.yml").write_text('''name: Real Tibia Evidence Contracts

on:
  push:
    branches:
      - main
      - "feat/**"
      - "fix/**"
      - "docs/**"
      - "ci/**"
    paths:
      - "docs/agents/real-tibia/evidence/**"
      - "docs/agents/templates/REAL_TIBIA_EVIDENCE_RECORD.yaml"
      - "docs/agents/templates/REAL_TIBIA_EVIDENCE_REQUEST.yaml"
      - "tools/agents/real_tibia_evidence.py"
      - "tools/agents/real_tibia_evidence_lib.py"
      - "tools/agents/real_tibia_evidence_test_support.py"
      - "tools/agents/real_tibia_owner_request.py"
      - "tools/agents/test_real_tibia_owner_request.py"
      - "tools/agents/test_real_tibia_evidence.py"
      - "tools/agents/test_real_tibia_evidence_lifecycle.py"
      - ".github/workflows/real-tibia-evidence.yml"
  pull_request:
    paths:
      - "docs/agents/real-tibia/evidence/**"
      - "docs/agents/templates/REAL_TIBIA_EVIDENCE_RECORD.yaml"
      - "docs/agents/templates/REAL_TIBIA_EVIDENCE_REQUEST.yaml"
      - "tools/agents/real_tibia_evidence.py"
      - "tools/agents/real_tibia_evidence_lib.py"
      - "tools/agents/real_tibia_evidence_test_support.py"
      - "tools/agents/real_tibia_owner_request.py"
      - "tools/agents/test_real_tibia_owner_request.py"
      - "tools/agents/test_real_tibia_evidence.py"
      - "tools/agents/test_real_tibia_evidence_lifecycle.py"
      - ".github/workflows/real-tibia-evidence.yml"
  workflow_dispatch:

permissions:
  contents: read

jobs:
  validate:
    name: Validate evidence contracts and indexes
    runs-on: ubuntu-24.04
    timeout-minutes: 10
    steps:
      - name: Checkout exact head
        uses: actions/checkout@v6
        with:
          persist-credentials: false
          fetch-depth: 0

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install Draft 2020-12 schema checker
        run: python -m pip install --disable-pip-version-check jsonschema

      - name: Compile standard-library tooling
        run: |
          python -m py_compile \
            tools/agents/real_tibia_evidence.py \
            tools/agents/real_tibia_evidence_lib.py \
            tools/agents/real_tibia_evidence_test_support.py \
            tools/agents/real_tibia_owner_request.py \
            tools/agents/test_real_tibia_owner_request.py \
            tools/agents/test_real_tibia_evidence.py \
            tools/agents/test_real_tibia_evidence_lifecycle.py

      - name: Run focused positive and negative tests
        run: python -m unittest discover -v -s tools/agents -p 'test_real_tibia*.py'

      - name: Validate canonical Real Tibia registry
        run: |
          python tools/agents/real_tibia_registry.py validate
          python tools/agents/real_tibia_registry.py generate --check

      - name: Validate evidence corpus
        run: python tools/agents/real_tibia_evidence.py validate --as-of 2026-07-25

      - name: Verify deterministic generated indexes
        run: python tools/agents/real_tibia_evidence.py generate --check --as-of 2026-07-25

      - name: Exercise factual index output
        run: python tools/agents/real_tibia_evidence.py show-index --as-of 2026-07-25 > /tmp/real-tibia-evidence-index.json
''', encoding="utf-8")


def cleanup() -> None:
    for rel in (
        ".github/workflows/rtec-003-implementation.yml",
        ".github/workflows/rtec-003-bootstrap.yml",
        "tools/agents/rtec_003_apply_patch.py",
    ):
        path = ROOT / rel
        if path.exists():
            path.unlink()


def main() -> None:
    patch_cli()
    write_tests()
    write_docs()
    patch_docs_and_task()
    write_permanent_workflow()
    cleanup()


if __name__ == "__main__":
    main()
