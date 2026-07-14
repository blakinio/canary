# Upstream source watch policy

## Purpose

Detect recent changes that may matter to `blakinio/canary` without treating external activity as implementation authority.

## Source roles

| Role | Meaning | Default trust |
|---|---|---|
| `upstream-server` | Closely related server implementation | useful architecture/convention signal, not official gameplay proof |
| `upstream-client` | Related client implementation | useful protocol/UI signal, not server truth |
| `donor-server` | External implementation donor | candidate implementation only |
| `editor` | Map/client tooling repository | tooling and format signal only |

Every watched source is configured with `writable: false`. The workflow token has no permission to push to those repositories.

## Watched object types

- commits on the configured default branch;
- pull requests in any state, sorted by recent updates;
- issues, excluding objects that are actually pull requests;
- releases.

The scanner records exact object revisions:

- commit and PR candidates use an exact 40-character Git SHA when available;
- issue and release candidates use a deterministic SHA-256 fingerprint of their mutable GitHub fields.

## Rolling windows and bounds

Daily scans use the configured rolling window, normally 30 days. Weekly deep scans use a longer window and fetch more changed-file details.

Each source defines:

- maximum objects per kind;
- maximum pages;
- daily changed-file detail count;
- deep changed-file detail count.

This prevents rate-limit exhaustion and unbounded reports. A missed run is recovered by the rolling window rather than a fragile single cursor.

## Baselines

`initial_baseline.sha` is the exact observed head when the source was registered. It is historical provenance, not a moving pointer and not an assertion that the baseline was fully audited.

Each scan re-fetches the live default-branch head. The report uses only:

- `unchanged` when it equals the initial baseline;
- `different` when it does not;
- `unknown` after a source failure.

It does not infer rebases or force-pushes without ancestry evidence.

## Local comparison

The workflow may fetch OpenTibiaBR Canary history into a temporary read-only remote ref so exact ancestry can be checked against local `HEAD`.

Local states are conservative:

- `exact-ancestor`: exact commit ancestry is proven;
- `reference-found`: the local Git history mentions the revision, URL or source object;
- `not-found`: no exact/reference evidence was found;
- `not-checked`: local Git evidence was unavailable.

No state claims semantic or patch equivalence.

## Errors and rate limits

A single-source failure is embedded in the report. If all sources fail, publication stops with an error.

No automatic retries with uncontrolled backoff, no scraping and no credential fallback are permitted.
