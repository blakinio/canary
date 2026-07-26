#!/usr/bin/env python3
"""Validate and generate Real Tibia evidence contracts and factual indexes."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import sys
from pathlib import Path
from typing import Sequence

sys.path.insert(0, str(Path(__file__).resolve().parent))
from real_tibia_evidence_lib import (
    Corpus,
    EvidenceError,
    ROOT,
    ValidationResult,
    write_generated,
)


PREPUBLICATION_RECORD_STATUSES = frozenset({"discovered", "normalized", "review-needed"})
PUBLICATION_VIEW_DIAGNOSTICS = frozenset(
    {
        "RTEC-FUTURE-EVIDENCE",
        "RTEC-GENERATED-INDEX-MISSING",
        "RTEC-GENERATED-INDEX-DRIFT",
        "RTEC-MODULE-INDEX-MISSING",
        "RTEC-MODULE-INDEX-DRIFT",
    }
)


def parse_date(value: str) -> dt.date:
    try:
        parsed = dt.date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("date must use YYYY-MM-DD") from exc
    if parsed.isoformat() != value:
        raise argparse.ArgumentTypeError("date must use YYYY-MM-DD")
    return parsed


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    root.add_argument("--root", type=Path, default=ROOT)
    commands = root.add_subparsers(dest="command", required=True)
    validate = commands.add_parser("validate")
    validate.add_argument("--as-of", type=parse_date)
    generate = commands.add_parser("generate")
    generate.add_argument("--check", action="store_true")
    generate.add_argument("--as-of", type=parse_date)
    show = commands.add_parser("show-index")
    show.add_argument("--as-of", type=parse_date, required=True)
    return root


def _filtered_document(document: object, value: dict[str, object]) -> object:
    """Return an immutable corpus document with a deterministic filtered digest."""
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return type(document)(
        document.path,
        document.relative_path,
        value,
        hashlib.sha256(encoded).hexdigest(),
    )


def publication_view(corpus: Corpus) -> Corpus:
    """Build the adjudicated subset used by deterministic factual indexes.

    Candidate records remain in the source-contract validation corpus, but
    discovered, normalized and review-needed records are not factual index
    inputs until their review state advances. Requests and history entries are
    published only when every referenced claim is already published.
    """
    published_evidence = tuple(
        document
        for document in corpus.evidence_documents
        if document.value.get("record_status") not in PREPUBLICATION_RECORD_STATUSES
    )
    published_ids = {
        document.value["evidence_id"]
        for document in published_evidence
        if isinstance(document.value.get("evidence_id"), str)
    }

    published_requests = tuple(
        document
        for document in corpus.request_documents
        if isinstance(document.value.get("claim_refs"), list)
        and all(reference in published_ids for reference in document.value["claim_refs"])
    )

    published_histories = []
    for document in corpus.history_documents:
        entries = document.value.get("entries")
        if not isinstance(entries, list):
            published_histories.append(document)
            continue
        retained = []
        for entry in entries:
            if not isinstance(entry, dict):
                retained.append(entry)
                continue
            references = set(entry.get("claim_refs", [])) | set(entry.get("evidence_refs", []))
            if references and references.issubset(published_ids):
                retained.append(entry)
        if not retained:
            continue
        if len(retained) == len(entries):
            published_histories.append(document)
            continue
        filtered_value = dict(document.value)
        filtered_value["entries"] = retained
        published_histories.append(_filtered_document(document, filtered_value))

    return Corpus(
        corpus.root,
        corpus.modules,
        published_evidence,
        published_requests,
        tuple(published_histories),
        corpus.module_index_documents,
        corpus.generated_document,
    )


def validate_for_publication(corpus: Corpus, as_of: dt.date | None) -> tuple[Corpus, ValidationResult]:
    """Validate all candidate contracts and the independently published view."""
    complete_result = corpus.validate(as_of)
    published = publication_view(corpus)
    published_result = published.validate(as_of)

    candidate_contract_errors = {
        diagnostic
        for diagnostic in complete_result.errors
        if diagnostic.code not in PUBLICATION_VIEW_DIAGNOSTICS
    }
    errors = tuple(sorted(candidate_contract_errors | set(published_result.errors)))
    warnings = tuple(sorted(set(complete_result.warnings) | set(published_result.warnings)))
    return published, ValidationResult(errors, warnings)


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        corpus = Corpus.load(args.root)
        published, result = validate_for_publication(corpus, args.as_of)
        if args.command == "validate":
            for diagnostic in result.warnings:
                print(f"warning: {diagnostic.render()}", file=sys.stderr)
            for diagnostic in result.errors:
                print(f"error: {diagnostic.render()}", file=sys.stderr)
            if not result.ok:
                return 1
            print(
                "evidence corpus valid "
                f"({len(corpus.evidence_documents)} evidence, "
                f"{len(corpus.request_documents)} requests, "
                f"{sum(len(doc.value.get('entries', [])) for doc in corpus.history_documents)} history records; "
                f"{len(published.evidence_documents)} published evidence)"
            )
            return 0
        if args.command == "generate":
            # Missing/drift diagnostics are expected to be repaired by generation,
            # but all source-contract errors remain fail-closed.
            repairable = {
                "RTEC-GENERATED-INDEX-MISSING",
                "RTEC-GENERATED-INDEX-DRIFT",
                "RTEC-MODULE-INDEX-MISSING",
                "RTEC-MODULE-INDEX-DRIFT",
            }
            blocking = [item for item in result.errors if item.code not in repairable]
            if blocking:
                for diagnostic in blocking:
                    print(f"error: {diagnostic.render()}", file=sys.stderr)
                return 1
            return write_generated(published, check=args.check, as_of=args.as_of)
        if args.command == "show-index":
            blocking = [
                item
                for item in result.errors
                if item.code
                not in {
                    "RTEC-GENERATED-INDEX-MISSING",
                    "RTEC-GENERATED-INDEX-DRIFT",
                    "RTEC-MODULE-INDEX-MISSING",
                    "RTEC-MODULE-INDEX-DRIFT",
                }
            ]
            if blocking:
                for diagnostic in blocking:
                    print(f"error: {diagnostic.render()}", file=sys.stderr)
                return 1
            print(json.dumps(published.generated_indexes(args.as_of), indent=2, sort_keys=True, ensure_ascii=False))
            return 0
    except EvidenceError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
