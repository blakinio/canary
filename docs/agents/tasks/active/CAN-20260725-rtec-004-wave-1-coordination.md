---
task_id: CAN-20260725-rtec-004-wave-1-coordination
program_id: CAN-PROGRAM-REAL-TIBIA-EVIDENCE-COLLECTION
coordination_id: RTEC-004-WAVE-1
status: implementing
agent: "GPT-5.6 Thinking"
branch: feat/rtec-004-wave-1-coordinator-20260725
base_branch: main
created: 2026-07-25T20:11:38+02:00
updated: 2026-07-25T21:02:00+02:00
last_verified_commit: "db865ac22906c839e5a52812251882cf1340ebf5"
risk: medium
related_issue: ""
related_pr: "929"
depends_on:
  - RTEC-002
  - RTEC-003
blocks:
  - RTEC-005
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260725-rtec-004-wave-1-coordination.md
  shared:
    - docs/agents/programs/REAL_TIBIA_EVIDENCE_COLLECTION_PROGRAM.md
    - docs/agents/real-tibia/evidence/generated/EVIDENCE_INDEXES.json
  read_only:
    - docs/agents/real-tibia/registry/**
    - docs/agents/real-tibia/generated/**
    - docs/agents/real-tibia/evidence/modules/**
    - docs/agents/real-tibia/evidence/requests/**
    - tools/e2e/**
    - tools/ai-agent/**
modules_touched:
  - real-tibia-evidence-collection
  - weapon-proficiency
  - item-definitions
reuses:
  - canary-real-tibia-evidence-record-v1
  - canary-real-tibia-owner-request-v1
  - canary-real-tibia-generated-indexes-v1
  - canonical Real Tibia module registry
public_interfaces: []
cross_repo_tasks: []
---

# Goal

Coordinate the first bounded parallel Collector campaign after RTEC-003 with two independent evidence-only packages while preserving owner boundaries and serialising the shared generated index.

# Wave decision

The programme permits up to eight workers and four concurrent Collector PRs. Wave 1 uses two workers because the repository already had six open PRs, including active OTBM PR #923 and Universal E2E PR #925. The reduced cap limits CI, storage and review pressure while still proving isolated dossier ownership.

# Worker state

## Worker A — weapon proficiency

- Task: `CAN-20260725-rtec-004-weapon-proficiency`.
- PR: #930.
- Exclusive module root: `docs/agents/real-tibia/evidence/modules/weapon-proficiency/**`.
- Delivered three records, dossier, behavior model, decisions, version history, module index and deterministic global index.
- Main finding: current selected Canary paths implement original-tree selection and per-player/per-weapon KV state, not the official 2026 modified-slot manipulation lifecycle.
- Character-switch pending-notification isolation remains `UNKNOWN`.
- Exact-head contract, registry, ownership, CI and upstream checks passed before structured-review integration.
- `ci:final-gate` is applied; structured review and final deterministic regeneration are in progress.

## Worker B — item definitions

- Task: `CAN-20260725-rtec-004-cloud-in-a-bottle`.
- PR: #931.
- Exclusive module root: `docs/agents/real-tibia/evidence/modules/item-definitions/**`.
- Official 2026-07-21 visible correction is pinned: availability begins at difficulty 10, not 15 as the description stated.
- Bounded Canary searches found no indexed match for the official name or secondary candidate identifiers; this is not an absolute absence claim.
- Worker B is serialised behind Worker A for the single global evidence index and will refresh from main after PR #930 merges.

# Shared boundaries

- `RTREQ-FEATURE-VOCATIONS-0001` remains unclaimed and unchanged.
- Workers do not edit OTBM/OWA, Universal E2E, TCR, protocol/client or feature-owner implementation paths.
- Shared generated index integration occurs only on one worker/final coordinator path at a time.

# Acceptance criteria

- [x] Verify main, programme, registry, evidence/request state and open PR ownership.
- [x] Pin the current official release/change baseline and proof limits.
- [x] Reduce wave 1 to two independent workers.
- [x] Create one branch, task and draft PR for each worker.
- [x] Assign exact package scopes, coordination IDs and dossier roots.
- [x] Establish shared-index serialisation between workers.
- [ ] Merge PR #930 after structured review and exact-final-head gates.
- [ ] Refresh PR #931 from main, finish its bounded dossier and pass exact-final-head gates.
- [ ] Merge PR #931 without owner-path edits.
- [ ] Refresh coordinator PR #929 from main and reconcile programme state.
- [ ] Record concurrency outcome and one exact RTEC-005 decision.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-25T21:02:00+02:00
head: db865ac22906c839e5a52812251882cf1340ebf5
branch: feat/rtec-004-wave-1-coordinator-20260725
pr: 929
status: implementing
context_routes:
  - agent-governance
  - real-tibia-parity
owned_paths:
  - docs/agents/tasks/active/CAN-20260725-rtec-004-wave-1-coordination.md
  - docs/agents/programs/REAL_TIBIA_EVIDENCE_COLLECTION_PROGRAM.md
  - docs/agents/real-tibia/evidence/generated/EVIDENCE_INDEXES.json
proven:
  - Worker A is PR 930 and Worker B is PR 931 with separate module roots
  - Worker A produced three records and a deterministic index package without owner-path edits
  - Worker A exact-head contract registry ownership CI and upstream checks passed before final review integration
  - Worker B official correction is source-pinned and repository search misses remain non-absence evidence
  - RTREQ-FEATURE-VOCATIONS-0001 remains unclaimed
  - the shared global evidence index requires worker serialization
derived:
  - two-worker concurrency is viable when module roots are isolated and the global index is serialized
  - Worker B should refresh after Worker A merges rather than publish a stale parallel generated index
unknown:
  - Worker A exact-final-head review integration result
  - Worker B exact current-main identity and definition findings
  - final merge SHAs and lifecycle outcomes
conflicts: []
first_failure:
  marker: worker-a-final-gate-pending
  evidence: PR 930 has final-gate label and reviewed index integration is not yet on a green exact final head
rejected_hypotheses:
  - start eight workers immediately: current repository load supports a lower cap
  - permit both workers to publish shared indexes concurrently: deterministic index serialization is required
  - treat Worker B code-search misses as item absence proof: alternate identity and indexing remain unresolved
changed_paths:
  - docs/agents/tasks/active/CAN-20260725-rtec-004-wave-1-coordination.md
validation:
  - command: worker ownership and independence review
    result: PASS
    evidence: PRs 930 and 931 own distinct module roots and implementation paths remain read-only
  - command: Worker A pre-review exact-head workflows
    result: PASS
    evidence: Evidence Contracts Module Registry Ownership CI and Upstream Intelligence passed on e1be6262698f6eaf07ba7a91070a9dcf4517f9af
  - command: Worker B official and bounded discovery review
    result: PASS
    evidence: exact visible correction retained; search misses not promoted to absence
blockers: []
next_action: Finish the self-removing structured-review integration on PR 930, write one final human checkpoint, and merge only after all exact-final-head checks pass.
```
