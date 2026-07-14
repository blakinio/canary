# ADR-20260714: Upstream intelligence remains read-only

- Status: accepted
- Date: 2026-07-14
- Owners: repository-wide agent governance
- Related task/PR: `CAN-20260714-upstream-intelligence-drift-tracking` / #331

## Context

The fork must notice useful fixes and features from OpenTibiaBR and CrystalServer without blindly importing unfinished, incompatible or lower-quality changes.

Simple commit-count drift is misleading because the local fork uses squash merges, independent implementations and different architecture. Fully automatic cherry-picking would turn external activity into unreviewed local behavior.

## Decision

Adopt a two-layer system:

1. automatic read-only discovery, provenance, module mapping, conservative flags and local exact/reference evidence;
2. reviewed decision records and normal bounded local tasks for any implementation.

The scheduled workflow receives only `contents: read`, `pull-requests: read` and local `issues: write`. It cannot push code and external repositories remain outside the writable trust boundary.

A single stable local issue is updated with the current report. Full bounded snapshots are uploaded as workflow artifacts rather than committed.

## Alternatives rejected

| Alternative | Rejection reason |
|---|---|
| automatic upstream merge/cherry-pick | unsafe, incompatible with local architecture and evidence rules |
| commit-count dashboard only | cannot detect squash/equivalent/local-superior implementations |
| one issue per external object | creates unbounded noise and duplicate state |
| persistent moving cursor only | missed runs can permanently lose events |
| copy external issue labels/statuses as conclusions | external triage is not local proof |

## Consequences

- The fork receives continuous visibility without automatic behavior changes.
- Rolling windows recover missed runs.
- Exact ancestry and history references speed review but do not prove equivalence.
- Human/agent triage remains necessary for implementation decisions.
- The stable report issue is operational state; reviewed decision files are durable repository state.
