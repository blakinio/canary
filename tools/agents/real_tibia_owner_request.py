#!/usr/bin/env python3
"""Safely transition and consume Real Tibia evidence owner requests.

The tool is dry-run-first.  It reuses the canonical version-1 request and evidence
contracts, applies an optimistic expected-status guard, validates the complete
candidate corpus, and writes the request plus deterministic indexes as one
rollback-capable operation.
"""
from __future__ import annotations

import argparse
import copy
import datetime as dt
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

sys.path.insert(0, str(Path(__file__).resolve().parent))
from real_tibia_evidence_lib import (  # noqa: E402
    Corpus,
    EvidenceError,
    LoadedDocument,
    OWNER_CONTROLLED_STATUSES,
    PROOF_RANK,
    REQUEST_STATUSES,
    REQUEST_TRANSITIONS,
    ROOT,
    _atomic_write,
    safe_repo_path,
    write_generated,
)

REPAIRABLE_INDEX_CODES = frozenset(
    {
        "RTEC-GENERATED-INDEX-MISSING",
        "RTEC-GENERATED-INDEX-DRIFT",
        "RTEC-MODULE-INDEX-MISSING",
        "RTEC-MODULE-INDEX-DRIFT",
    }
)
OWNER_RESULT_SOURCE_TYPES = {
    "e2e": frozenset({"physical-e2e-result"}),
    "otbm": frozenset({"otbm-owner-result"}),
    "tcr": frozenset({"tcr-owner-result"}),
    "protocol": frozenset(
        {
            "maintained-client",
            "packet-capture",
            "canary-test-result",
            "runtime-result",
            "physical-e2e-result",
        }
    ),
    "feature": frozenset(
        {
            "feature-owner-result",
            "canary-test-result",
            "database-test-result",
            "runtime-result",
            "physical-e2e-result",
        }
    ),
}
REPOSITORY_RE = r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+"
SHA40_RE = re.compile(r"^[0-9a-f]{40}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
REQUEST_SHA_RE = SHA256_RE


class RequestLifecycleError(ValueError):
    """Raised when a lifecycle mutation would violate a durable contract."""


@dataclass(frozen=True)
class StableResultRef:
    raw: str
    kind: str
    repository: str | None = None
    commit_sha: str | None = None
    repository_path: str | None = None
    numeric_id: int | None = None
    sha256: str | None = None


def parse_date(value: str) -> dt.date:
    try:
        parsed = dt.date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("date must use YYYY-MM-DD") from exc
    if parsed.isoformat() != value:
        raise argparse.ArgumentTypeError("date must use YYYY-MM-DD")
    return parsed


def parse_timestamp(value: str) -> str:
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise argparse.ArgumentTypeError("timestamp must be timezone-aware ISO-8601") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise argparse.ArgumentTypeError("timestamp must be timezone-aware ISO-8601")
    return value


def _canonical_text(value: Mapping[str, Any]) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _unique_nonempty(values: Sequence[str], label: str) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()
    for value in values:
        if not isinstance(value, str) or not value.strip() or value != value.strip():
            raise RequestLifecycleError(f"{label} values must be non-empty and trimmed")
        if value in seen:
            raise RequestLifecycleError(f"{label} contains duplicate value {value!r}")
        seen.add(value)
        normalized.append(value)
    if not normalized:
        raise RequestLifecycleError(f"{label} must contain at least one value")
    return normalized


def parse_stable_result_ref(value: str) -> StableResultRef:
    if not isinstance(value, str) or not value or value != value.strip():
        raise RequestLifecycleError("stable result reference must be non-empty and trimmed")

    match = re.fullmatch(rf"github-pr:({REPOSITORY_RE})#([1-9][0-9]*)", value)
    if match:
        return StableResultRef(value, "github-pr", repository=match.group(1), numeric_id=int(match.group(2)))

    match = re.fullmatch(rf"github-commit:({REPOSITORY_RE})@([0-9a-f]{{40}})", value)
    if match:
        return StableResultRef(value, "github-commit", repository=match.group(1), commit_sha=match.group(2))

    match = re.fullmatch(rf"github-actions-(run|job):({REPOSITORY_RE})#([1-9][0-9]*)", value)
    if match:
        return StableResultRef(value, f"github-actions-{match.group(1)}", repository=match.group(2), numeric_id=int(match.group(3)))

    match = re.fullmatch(
        rf"github-actions-artifact:({REPOSITORY_RE})#([1-9][0-9]*)@sha256:([0-9a-f]{{64}})",
        value,
    )
    if match:
        return StableResultRef(
            value,
            "github-actions-artifact",
            repository=match.group(1),
            numeric_id=int(match.group(2)),
            sha256=match.group(3),
        )

    match = re.fullmatch(rf"repo-file:({REPOSITORY_RE})@([0-9a-f]{{40}}):(.+)", value)
    if match:
        repository_path = match.group(3)
        if not safe_repo_path(repository_path):
            raise RequestLifecycleError(f"repo-file reference contains unsafe repository path {repository_path!r}")
        return StableResultRef(
            value,
            "repo-file",
            repository=match.group(1),
            commit_sha=match.group(2),
            repository_path=repository_path,
        )

    match = re.fullmatch(r"external-report:sha256:([0-9a-f]{64})", value)
    if match:
        return StableResultRef(value, "external-report", sha256=match.group(1))

    raise RequestLifecycleError(
        "unsupported stable result reference; use github-pr, github-commit, "
        "github-actions-run/job/artifact, repo-file or external-report"
    )


def _validate_stable_refs(values: Sequence[str], label: str) -> tuple[list[str], list[StableResultRef]]:
    normalized = _unique_nonempty(values, label)
    return normalized, [parse_stable_result_ref(value) for value in normalized]


def _request_document(corpus: Corpus, request_id: str) -> LoadedDocument:
    matches = [document for document in corpus.request_documents if document.value.get("request_id") == request_id]
    if not matches:
        raise RequestLifecycleError(f"owner request {request_id!r} does not exist")
    if len(matches) != 1:
        raise RequestLifecycleError(f"owner request {request_id!r} is duplicated")
    return matches[0]


def _candidate_corpus(corpus: Corpus, document: LoadedDocument, value: dict[str, Any]) -> Corpus:
    content = _canonical_text(value).encode("utf-8")
    candidate = LoadedDocument(
        document.path,
        document.relative_path,
        value,
        hashlib.sha256(content).hexdigest(),
    )
    requests = tuple(candidate if item.relative_path == document.relative_path else item for item in corpus.request_documents)
    return Corpus(
        corpus.root,
        corpus.modules,
        corpus.evidence_documents,
        requests,
        corpus.history_documents,
        corpus.module_index_documents,
        corpus.generated_document,
    )


def _blocking_diagnostics(corpus: Corpus, as_of: dt.date) -> list[str]:
    result = corpus.validate(as_of)
    return [diagnostic.render() for diagnostic in result.errors if diagnostic.code not in REPAIRABLE_INDEX_CODES]


def _validate_candidate(corpus: Corpus, document: LoadedDocument, value: dict[str, Any], as_of: dt.date) -> Corpus:
    candidate = _candidate_corpus(corpus, document, value)
    blocking = _blocking_diagnostics(candidate, as_of)
    if blocking:
        raise RequestLifecycleError("candidate request violates the evidence corpus:\n" + "\n".join(blocking))
    return candidate


def _check_expected_document(document: LoadedDocument, expected_status: str, expected_sha256: str | None) -> None:
    current_status = document.value.get("status")
    if current_status != expected_status:
        raise RequestLifecycleError(
            f"stale request state: expected {expected_status!r}, current status is {current_status!r}"
        )
    if expected_sha256 is not None:
        if not REQUEST_SHA_RE.fullmatch(expected_sha256):
            raise RequestLifecycleError("expected document SHA-256 must be 64 lowercase hexadecimal characters")
        if document.sha256 != expected_sha256:
            raise RequestLifecycleError(
                f"stale request document: expected sha256 {expected_sha256}, current sha256 is {document.sha256}"
            )


def _history_event(
    *,
    at: str,
    actor: str,
    actor_role: str,
    actor_task: str,
    actor_pr: int | None,
    from_status: str,
    to_status: str,
    reason: str,
    owner_evidence_ref: str | None,
) -> dict[str, Any]:
    parse_timestamp(at)
    if not actor or actor != actor.strip():
        raise RequestLifecycleError("actor must be non-empty and trimmed")
    if actor_role not in {"collector", "owner", "reviewer", "automation"}:
        raise RequestLifecycleError(f"unsupported actor role {actor_role!r}")
    if not actor_task or actor_task != actor_task.strip():
        raise RequestLifecycleError("actor task must be non-empty and trimmed")
    if actor_pr is not None and (isinstance(actor_pr, bool) or actor_pr <= 0):
        raise RequestLifecycleError("actor PR must be null or a positive integer")
    if not reason or reason != reason.strip():
        raise RequestLifecycleError("transition reason must be non-empty and trimmed")
    return {
        "at": at,
        "actor": actor,
        "actor_role": actor_role,
        "actor_task": actor_task,
        "actor_pr": actor_pr,
        "from_status": from_status,
        "to_status": to_status,
        "reason": reason,
        "owner_evidence_ref": owner_evidence_ref,
    }


def transition_value(
    request: Mapping[str, Any],
    *,
    expected_status: str,
    to_status: str,
    at: str,
    actor: str,
    actor_role: str,
    actor_task: str,
    actor_pr: int | None,
    reason: str,
    owner_evidence_ref: str | None = None,
    owner_task: str | None = None,
    owner_pr: int | None = None,
) -> dict[str, Any]:
    if expected_status not in REQUEST_STATUSES or to_status not in REQUEST_STATUSES:
        raise RequestLifecycleError("expected and target statuses must use the canonical request status enum")
    if to_status in {"result-available", "consumed"}:
        raise RequestLifecycleError(f"use the dedicated command for transition to {to_status}")
    current = request.get("status")
    if current != expected_status:
        raise RequestLifecycleError(f"stale request state: expected {expected_status!r}, current status is {current!r}")
    if to_status not in REQUEST_TRANSITIONS.get(expected_status, frozenset()):
        raise RequestLifecycleError(f"invalid request transition {expected_status!r} -> {to_status!r}")

    if to_status in OWNER_CONTROLLED_STATUSES:
        if actor_role != "owner" or actor_pr is None:
            raise RequestLifecycleError(f"transition to {to_status} requires owner actor and positive owner PR")
        if owner_evidence_ref is None:
            raise RequestLifecycleError(f"transition to {to_status} requires stable owner evidence")
        parse_stable_result_ref(owner_evidence_ref)
    elif owner_evidence_ref is not None:
        parse_stable_result_ref(owner_evidence_ref)

    value = copy.deepcopy(dict(request))
    value["status"] = to_status
    value["history"].append(
        _history_event(
            at=at,
            actor=actor,
            actor_role=actor_role,
            actor_task=actor_task,
            actor_pr=actor_pr,
            from_status=expected_status,
            to_status=to_status,
            reason=reason,
            owner_evidence_ref=owner_evidence_ref,
        )
    )
    if actor_role == "owner":
        coordination = value["coordination"]
        coordination["owner_task"] = owner_task or actor_task
        coordination["owner_pr"] = owner_pr or actor_pr
    return value


def record_result_value(
    request: Mapping[str, Any],
    *,
    expected_status: str,
    at: str,
    actor: str,
    actor_task: str,
    actor_pr: int,
    reason: str,
    owner_evidence_ref: str,
    owner_task: str | None,
    owner_pr: int | None,
    result_refs: Sequence[str],
    proof_level: str,
    proves: Sequence[str],
    does_not_prove: Sequence[str],
    blockers: Sequence[str],
) -> dict[str, Any]:
    if expected_status != "active" or request.get("status") != "active":
        raise RequestLifecycleError("owner result may be recorded only from expected active status")
    if proof_level not in PROOF_RANK:
        raise RequestLifecycleError(f"unsupported proof level {proof_level!r}")
    normalized_refs, _ = _validate_stable_refs(result_refs, "result refs")
    normalized_proves = _unique_nonempty(proves, "proves")
    normalized_nonproof = _unique_nonempty(does_not_prove, "does_not_prove")
    normalized_blockers = [] if not blockers else _unique_nonempty(blockers, "blockers")
    parse_stable_result_ref(owner_evidence_ref)
    if actor_pr <= 0:
        raise RequestLifecycleError("owner result requires a positive actor PR")

    value = copy.deepcopy(dict(request))
    value["status"] = "result-available"
    value["result"] = {
        "available": True,
        "result_refs": normalized_refs,
        "consumed_by_evidence_records": [],
        "proof_level_reached": proof_level,
        "proves": normalized_proves,
        "does_not_prove": normalized_nonproof,
        "blockers": normalized_blockers,
    }
    value["coordination"]["owner_task"] = owner_task or actor_task
    value["coordination"]["owner_pr"] = owner_pr or actor_pr
    value["history"].append(
        _history_event(
            at=at,
            actor=actor,
            actor_role="owner",
            actor_task=actor_task,
            actor_pr=actor_pr,
            from_status="active",
            to_status="result-available",
            reason=reason,
            owner_evidence_ref=owner_evidence_ref,
        )
    )
    return value


def _source_matches_ref(source: Mapping[str, Any], reference: StableResultRef) -> bool:
    locator = source.get("locator")
    if not isinstance(locator, Mapping):
        return False
    if reference.kind == "github-commit":
        return locator.get("repository") == reference.repository and locator.get("commit_sha") == reference.commit_sha
    if reference.kind == "repo-file":
        return (
            locator.get("repository") == reference.repository
            and locator.get("commit_sha") == reference.commit_sha
            and locator.get("repository_path") == reference.repository_path
        )
    if reference.kind in {"github-pr", "github-actions-run", "github-actions-job"}:
        return locator.get("report_id") == reference.raw
    if reference.kind == "github-actions-artifact":
        repository_ok = locator.get("repository") in {None, reference.repository}
        artifact = source.get("external_artifact")
        external_digest = artifact.get("sha256") if isinstance(artifact, Mapping) else None
        return repository_ok and reference.sha256 in {locator.get("artifact_sha256"), external_digest}
    if reference.kind == "external-report":
        artifact = source.get("external_artifact")
        external_digest = artifact.get("sha256") if isinstance(artifact, Mapping) else None
        return reference.sha256 in {locator.get("artifact_sha256"), external_digest}
    return False


def consume_result_value(
    request: Mapping[str, Any],
    *,
    expected_status: str,
    at: str,
    actor: str,
    actor_role: str,
    actor_task: str,
    actor_pr: int | None,
    reason: str,
    evidence_ids: Sequence[str],
    evidence_documents: Sequence[LoadedDocument],
) -> dict[str, Any]:
    if expected_status != "result-available" or request.get("status") != "result-available":
        raise RequestLifecycleError("owner result may be consumed only from expected result-available status")
    if actor_role not in {"collector", "reviewer", "automation"}:
        raise RequestLifecycleError("result consumption must be recorded by collector, reviewer or automation")
    normalized_ids = _unique_nonempty(evidence_ids, "evidence IDs")
    result = request.get("result")
    if not isinstance(result, Mapping) or result.get("available") is not True:
        raise RequestLifecycleError("request has no available owner result")
    result_level = result.get("proof_level_reached")
    if result_level not in PROOF_RANK:
        raise RequestLifecycleError("request result has no valid proof level")
    _, parsed_refs = _validate_stable_refs(result.get("result_refs", []), "result refs")
    owner_kind = request.get("owner_kind")
    allowed_source_types = OWNER_RESULT_SOURCE_TYPES.get(str(owner_kind), frozenset())
    documents = {str(document.value.get("evidence_id")): document for document in evidence_documents}

    for evidence_id in normalized_ids:
        document = documents.get(evidence_id)
        if document is None:
            raise RequestLifecycleError(f"consuming evidence record {evidence_id!r} does not exist")
        record = document.value
        if request.get("request_id") not in record.get("owner_request_refs", []):
            raise RequestLifecycleError(
                f"evidence record {evidence_id} must link owner request {request.get('request_id')}"
            )
        record_level = record.get("proof_level")
        if record_level not in PROOF_RANK or PROOF_RANK[record_level] > PROOF_RANK[result_level]:
            raise RequestLifecycleError(
                f"evidence record {evidence_id} proof {record_level!r} exceeds owner result proof {result_level!r}"
            )
        matching_sources = []
        for source in record.get("sources", []):
            if not isinstance(source, Mapping) or source.get("source_type") not in allowed_source_types:
                continue
            source_level = source.get("proof_level_reached")
            if source_level not in PROOF_RANK or PROOF_RANK[source_level] > PROOF_RANK[result_level]:
                raise RequestLifecycleError(
                    f"evidence source in {evidence_id} exceeds owner result proof {result_level!r}"
                )
            if any(_source_matches_ref(source, reference) for reference in parsed_refs):
                matching_sources.append(source)
        if not matching_sources:
            raise RequestLifecycleError(
                f"evidence record {evidence_id} lacks a {owner_kind} owner-result source matching a stable result reference"
            )

    value = copy.deepcopy(dict(request))
    value["status"] = "consumed"
    value["result"]["consumed_by_evidence_records"] = sorted(normalized_ids)
    value["history"].append(
        _history_event(
            at=at,
            actor=actor,
            actor_role=actor_role,
            actor_task=actor_task,
            actor_pr=actor_pr,
            from_status="result-available",
            to_status="consumed",
            reason=reason,
            owner_evidence_ref=None,
        )
    )
    return value


def _restore_files(backups: Mapping[Path, bytes | None], root: Path) -> None:
    for path, content in sorted(backups.items(), key=lambda item: item[0].as_posix()):
        if content is None:
            if path.exists() or path.is_symlink():
                path.unlink()
            continue
        _atomic_write(path, content.decode("utf-8"), root)


def apply_candidate(
    *,
    root: Path,
    request_id: str,
    expected_status: str,
    expected_document_sha256: str | None,
    as_of: dt.date,
    write: bool,
    mutation: Any,
) -> dict[str, Any]:
    corpus = Corpus.load(root)
    baseline_errors = _blocking_diagnostics(corpus, as_of)
    if baseline_errors:
        raise RequestLifecycleError("current evidence corpus is invalid:\n" + "\n".join(baseline_errors))
    document = _request_document(corpus, request_id)
    _check_expected_document(document, expected_status, expected_document_sha256)
    candidate_value = mutation(copy.deepcopy(document.value), corpus)
    candidate = _validate_candidate(corpus, document, candidate_value, as_of)
    if not write:
        return candidate_value

    generated_paths = set(candidate.generated_files(as_of))
    generated_paths.update(item.path for item in corpus.module_index_documents)
    touched_paths = generated_paths | {document.path}
    backups = {path: path.read_bytes() if path.exists() else None for path in touched_paths}
    try:
        _atomic_write(document.path, _canonical_text(candidate_value), corpus.root)
        updated = Corpus.load(corpus.root)
        write_generated(updated, check=False, as_of=as_of)
        final = Corpus.load(corpus.root)
        final_errors = [diagnostic.render() for diagnostic in final.validate(as_of).errors]
        if final_errors:
            raise RequestLifecycleError("post-write corpus validation failed:\n" + "\n".join(final_errors))
    except Exception:
        _restore_files(backups, corpus.root)
        raise
    return candidate_value


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    root.add_argument("--root", type=Path, default=ROOT)
    commands = root.add_subparsers(dest="command", required=True)

    def common(command: argparse.ArgumentParser) -> None:
        command.add_argument("--request-id", required=True)
        command.add_argument("--expected-status", required=True, choices=sorted(REQUEST_STATUSES))
        command.add_argument("--expected-document-sha256")
        command.add_argument("--as-of", type=parse_date, required=True)
        command.add_argument("--at", type=parse_timestamp, required=True)
        command.add_argument("--actor", required=True)
        command.add_argument("--actor-task", required=True)
        command.add_argument("--actor-pr", type=int)
        command.add_argument("--reason", required=True)
        command.add_argument("--write", action="store_true")

    transition = commands.add_parser("transition", help="advance one non-result request state")
    common(transition)
    transition.add_argument("--to-status", required=True, choices=sorted(REQUEST_STATUSES))
    transition.add_argument("--actor-role", required=True, choices=("collector", "owner", "reviewer", "automation"))
    transition.add_argument("--owner-evidence-ref")
    transition.add_argument("--owner-task")
    transition.add_argument("--owner-pr", type=int)

    result = commands.add_parser("record-result", help="record an owner-produced stable result")
    common(result)
    result.add_argument("--owner-evidence-ref", required=True)
    result.add_argument("--owner-task")
    result.add_argument("--owner-pr", type=int)
    result.add_argument("--result-ref", action="append", required=True)
    result.add_argument("--proof-level", required=True, choices=tuple(PROOF_RANK))
    result.add_argument("--proves", action="append", required=True)
    result.add_argument("--does-not-prove", action="append", required=True)
    result.add_argument("--blocker", action="append", default=[])

    consume = commands.add_parser("consume-result", help="consume a stable owner result into linked evidence")
    common(consume)
    consume.add_argument("--actor-role", required=True, choices=("collector", "reviewer", "automation"))
    consume.add_argument("--evidence-id", action="append", required=True)
    return root


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "transition":
            mutation = lambda request, corpus: transition_value(
                request,
                expected_status=args.expected_status,
                to_status=args.to_status,
                at=args.at,
                actor=args.actor,
                actor_role=args.actor_role,
                actor_task=args.actor_task,
                actor_pr=args.actor_pr,
                reason=args.reason,
                owner_evidence_ref=args.owner_evidence_ref,
                owner_task=args.owner_task,
                owner_pr=args.owner_pr,
            )
        elif args.command == "record-result":
            mutation = lambda request, corpus: record_result_value(
                request,
                expected_status=args.expected_status,
                at=args.at,
                actor=args.actor,
                actor_task=args.actor_task,
                actor_pr=args.actor_pr,
                reason=args.reason,
                owner_evidence_ref=args.owner_evidence_ref,
                owner_task=args.owner_task,
                owner_pr=args.owner_pr,
                result_refs=args.result_ref,
                proof_level=args.proof_level,
                proves=args.proves,
                does_not_prove=args.does_not_prove,
                blockers=args.blocker,
            )
        else:
            mutation = lambda request, corpus: consume_result_value(
                request,
                expected_status=args.expected_status,
                at=args.at,
                actor=args.actor,
                actor_role=args.actor_role,
                actor_task=args.actor_task,
                actor_pr=args.actor_pr,
                reason=args.reason,
                evidence_ids=args.evidence_id,
                evidence_documents=corpus.evidence_documents,
            )
        value = apply_candidate(
            root=args.root,
            request_id=args.request_id,
            expected_status=args.expected_status,
            expected_document_sha256=args.expected_document_sha256,
            as_of=args.as_of,
            write=args.write,
            mutation=mutation,
        )
        print(
            json.dumps(
                {
                    "request_id": value["request_id"],
                    "status": value["status"],
                    "write": args.write,
                    "document_sha256": hashlib.sha256(_canonical_text(value).encode("utf-8")).hexdigest(),
                    "request": value if not args.write else None,
                },
                indent=2,
                sort_keys=True,
                ensure_ascii=False,
            )
        )
        return 0
    except (EvidenceError, RequestLifecycleError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
