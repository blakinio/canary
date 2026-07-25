# Real Tibia owner-request lifecycle

This document is the operator contract for `tools/agents/real_tibia_owner_request.py` and `canary-real-tibia-owner-request-v1`.

The tool coordinates evidence. It does not execute Universal E2E, parse OTBM, parse official-client packages, alter protocol/client code or implement feature behavior.

## Safety model

Every command is a dry run unless `--write` is supplied. A dry run loads the complete corpus, checks the requested mutation and prints the candidate request without changing Git.

A write requires:

- one exact request ID;
- the current expected status;
- optionally the exact SHA-256 of the current request document;
- a timezone-aware event timestamp;
- actor, task, PR and reason metadata where required;
- a legal status transition;
- a corpus-valid candidate;
- successful deterministic index regeneration;
- successful post-write corpus validation.

The expected status and optional document digest are optimistic locks. A stale agent cannot overwrite a request that another task has already advanced.

Writes are rollback-capable. The request and every affected generated index are restored when generation or final validation fails.

## State ownership

```text
null -> draft -> ready-for-owner-triage
                    |-> accepted-by-owner -> planned -> active -> result-available -> consumed
                    |-> rejected
                    |-> superseded
```

The full graph, including `blocked` recovery paths, is enforced by the canonical validator.

Collector-controlled operations may create or advance states that do not claim owner execution. Transitions to these states require an owner actor, a positive owner PR and a stable owner evidence reference:

- `accepted-by-owner`;
- `active`;
- `result-available`.

`result-available` is accepted only through `record-result`. `consumed` is accepted only through `consume-result`.

The Collector must never fabricate owner metadata merely to move a request forward.

## Stable result references

Mutable labels such as `latest`, branch-only references and unpinned web URLs are not accepted as retained-result identity.

Supported references are:

```text
github-pr:<owner/repository>#<positive-pr-number>
github-commit:<owner/repository>@<40-character-commit-sha>
github-actions-run:<owner/repository>#<positive-run-id>
github-actions-job:<owner/repository>#<positive-job-id>
github-actions-artifact:<owner/repository>#<positive-artifact-id>@sha256:<64-character-sha256>
repo-file:<owner/repository>@<40-character-commit-sha>:<safe-repository-path>
external-report:sha256:<64-character-sha256>
```

External/proprietary payloads remain outside Git. Git stores compact metadata, stable references and hashes only.

## Transition example

The command below is a dry run because `--write` is absent:

```sh
python tools/agents/real_tibia_owner_request.py transition \
  --request-id RTREQ-FEATURE-VOCATIONS-0001 \
  --expected-status ready-for-owner-triage \
  --as-of 2026-07-25 \
  --at 2026-07-25T16:00:00+02:00 \
  --actor feature-owner \
  --actor-role owner \
  --actor-task CAN-REPLACE-WITH-REAL-OWNER-TASK \
  --actor-pr 123 \
  --to-status accepted-by-owner \
  --owner-evidence-ref github-pr:blakinio/canary#123 \
  --reason "Owner accepted the bounded request after reviewing its exact inputs."
```

Do not run that example with `--write` unless PR `#123` and the named task really are the owner evidence for this request.

For a write, first capture the exact document digest from the dry-run/current file and add:

```text
--expected-document-sha256 <current-request-sha256> --write
```

## Recording an owner result

Only an `active` request may receive an owner result:

```sh
python tools/agents/real_tibia_owner_request.py record-result \
  --request-id RTREQ-FEATURE-EXAMPLE-0001 \
  --expected-status active \
  --expected-document-sha256 <current-request-sha256> \
  --as-of 2026-07-25 \
  --at 2026-07-25T17:00:00+02:00 \
  --actor feature-owner \
  --actor-task CAN-OWNER-TASK \
  --actor-pr 124 \
  --owner-task CAN-OWNER-TASK \
  --owner-pr 124 \
  --owner-evidence-ref github-pr:blakinio/canary#124 \
  --result-ref repo-file:blakinio/canary@<40-character-sha>:reports/result.json \
  --proof-level behavior-proven \
  --proves "The bounded state transition was observed on the pinned baseline." \
  --does-not-prove "No physical-client, compatibility or whole-module parity is proven."
```

The result must include stable references, the strongest proof level actually reached, explicit `proves` and explicit `does_not_prove` boundaries.

## Consuming a result

Before consumption, the Collector creates or updates one exact evidence record. That record must:

- list the request ID in `owner_request_refs`;
- use a source type allowed for the owner route;
- point to one of the request's stable result references;
- use a record and source proof level no higher than the owner result;
- pass the full evidence corpus validator.

Then run a dry-run consumption:

```sh
python tools/agents/real_tibia_owner_request.py consume-result \
  --request-id RTREQ-FEATURE-EXAMPLE-0001 \
  --expected-status result-available \
  --expected-document-sha256 <current-request-sha256> \
  --as-of 2026-07-25 \
  --at 2026-07-25T18:00:00+02:00 \
  --actor collector \
  --actor-role collector \
  --actor-task CAN-COLLECTOR-TASK \
  --actor-pr 125 \
  --evidence-id RT-EXAMPLE-0001 \
  --reason "Collector normalized the pinned owner result into the linked evidence record."
```

Add `--write` only after reviewing the candidate JSON and exact diff.

## Owner-route source requirements

| Owner route | Accepted owner-result source types |
|---|---|
| Universal E2E | `physical-e2e-result` |
| OTBM/OWA | `otbm-owner-result` |
| TCR | `tcr-owner-result` |
| protocol/client | `maintained-client`, `packet-capture`, `canary-test-result`, `runtime-result`, `physical-e2e-result` |
| feature programme | `feature-owner-result`, `canary-test-result`, `database-test-result`, `runtime-result`, `physical-e2e-result` |

These source types constrain routing. Their existing proof caps still apply independently.

## Operational sequence

1. Re-fetch current `main`, request, owner PR/task and retained result.
2. Verify no task already owns the exact request/behavior/version tuple.
3. Validate the corpus.
4. Run the intended command without `--write`.
5. Review candidate status, history, proof boundaries and document SHA-256.
6. Re-run with expected status, expected digest and `--write`.
7. Review the exact Git diff and regenerated indexes.
8. Commit through the owning task branch and normal PR lifecycle.

Do not run several writes against the same request concurrently. One request is a serialization boundary.

## Current vocations request

`RTREQ-FEATURE-VOCATIONS-0001` remains `ready-for-owner-triage`. RTEC-003 does not accept it, execute it or fabricate a result. It may advance only after a real feature owner creates a bounded owner task/PR and produces the required evidence.
