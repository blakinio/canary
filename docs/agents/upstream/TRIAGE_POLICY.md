# Upstream candidate triage policy

## Core rule

An external issue, pull request, commit or release is a **signal**. It is never enough by itself to declare the local fork behind, broken or incomplete.

## Automatic layer

Automation may:

- record exact provenance;
- fetch bounded metadata and changed paths;
- map paths to current registry modules;
- flag security, crash, protocol, database, performance, breaking, draft, release and client-source terms;
- detect exact local ancestry or history references;
- prioritize review;
- apply an existing reviewed decision only when the pinned revision still matches.

Automation may not:

- classify gameplay correctness;
- claim patch equivalence;
- cherry-pick;
- open implementation branches;
- edit gameplay, protocol, database, map or client code;
- write to watched repositories;
- close the report issue merely because the queue is empty.

## Reviewed statuses

| Status | Meaning |
|---|---|
| `needs-triage` | no reviewed conclusion yet |
| `already-present` | exact behavior is proven present locally |
| `equivalent-local` | local implementation is proven semantically equivalent |
| `canary-superior` | local implementation is demonstrably safer/newer |
| `valid-fix-missing` | a real current-main gap is proven |
| `partial-value` | only a bounded subset is useful |
| `client-coupled` | requires coordinated server/client work |
| `blocked-by-version` | incompatible protocol/content/version baseline |
| `blocked-by-dependency` | prerequisite package is missing |
| `conflicting` | sources or local behavior disagree |
| `donor-only` | implementation idea without official-behavior authority |
| `dangerous` | unsafe or excessively coupled candidate |
| `rejected` | reviewed and intentionally not adopted |
| `implemented-local` | delivered by a local task/PR |
| `superseded` | replaced by another candidate or local package |
| `no-longer-applicable` | source or local architecture moved on |

## Required review sequence

1. Re-fetch the candidate and current `blakinio/canary:main`.
2. Confirm affected modules, current local behavior and existing PR/task overlap.
3. Check official Tibia evidence when gameplay behavior is involved.
4. Check maintained `blakinio/otclient` when protocol or UI matters.
5. Compare OpenTibiaBR and CrystalServer only as implementation evidence.
6. Prove whether the local implementation is absent, partial, equivalent or superior.
7. Record a decision pinned to the exact candidate revision.
8. Create one bounded local task only for a proven still-valid package.

## Decision record contract

Decision files live under `registry/decisions/` and use the JSON-compatible YAML subset.

A decision must include:

- stable `candidate_id`;
- exact `source_id`;
- exact 40- or 64-character `candidate_revision`;
- reviewed status;
- evidence and reason;
- affected module IDs;
- reviewer identity and timestamp;
- local merge SHA when implemented.

When the candidate revision changes, the old decision becomes stale automatically.

## High-risk handling

Security, crash, protocol, database and breaking flags raise priority only. They do not bypass normal proof, review, tests or merge gates.
