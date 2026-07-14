# Upstream Intelligence and Drift Tracking

This subsystem watches selected read-only upstream and donor repositories and turns recent GitHub activity into a bounded triage report for `blakinio/canary`.

It is **not** a synchronizer, cherry-pick bot, parity engine or proof that a local defect exists.

## Watched repositories

- `opentibiabr/canary`
- `opentibiabr/otclient`
- `zimbadev/crystalserver`
- `opentibiabr/remeres-map-editor`
- `opentibiabr/client-editor`

The maintained comparison target `blakinio/otclient` is inspected during human triage when protocol or client behavior matters. It is not treated as an external writable target by this workflow.

## Data flow

```text
GitHub commits / PRs / issues / releases
                 |
                 v
bounded rolling-window scanner
                 |
                 v
changed-file mapping through Real Tibia registry
                 |
                 v
automation flags + local exact/reference probe
                 |
                 v
reviewed decision records
                 |
                 v
JSON artifact + Markdown artifact + one stable local report issue
```

## Commands

```bash
python tools/agents/upstream_intelligence.py validate

python tools/agents/upstream_intelligence.py scan \
  --mode daily \
  --days 30 \
  --output-json /tmp/upstream-snapshot.json \
  --output-markdown /tmp/upstream-report.md \
  --issue-body /tmp/upstream-issue.md

python tools/agents/upstream_intelligence.py render \
  --input /tmp/upstream-snapshot.json \
  --output /tmp/upstream-report.md

python tools/agents/upstream_intelligence.py validate-snapshot \
  --input /tmp/upstream-snapshot.json
```

## Report semantics

- `needs-triage` means only that the object is new or changed in the rolling window.
- `mapping_state: mapped` means at least one changed path matched a registry pattern; it is not ownership or parity proof.
- `unmapped` remains explicit and must not be guessed into a module.
- `local_reference.state: exact-ancestor` proves only that the exact external commit is an ancestor of local `HEAD`.
- `reference-found` means local history mentions the revision or URL; it is not patch equivalence.
- reviewed decisions apply only while their pinned candidate revision still matches.
- a stale reviewed decision is surfaced as `stale-decision` and never silently reused.

## Failure behavior

A failed source is reported independently. The scan continues when at least one source succeeds. If every source fails, the tool refuses to publish an empty report.

The scanner uses bounded page counts, bounded object counts and a rolling time window so a missed scheduled run does not permanently lose events.

## Durable records

- source definitions: `registry/sources.yaml`
- reviewed decisions: `registry/decisions/*.yaml`
- schemas: `schemas/*.json`
- program: `docs/agents/programs/UPSTREAM_INTELLIGENCE_PROGRAM.md`
- policies: `SOURCE_WATCH_POLICY.md`, `TRIAGE_POLICY.md`
- architecture decision: `docs/agents/decisions/ADR-20260714-upstream-intelligence-read-only.md`

Generated scan results are workflow artifacts and a stable GitHub issue. They are not committed to the repository.
