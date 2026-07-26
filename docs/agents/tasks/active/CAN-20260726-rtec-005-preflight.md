---
task_id: CAN-20260726-rtec-005-preflight
program_id: CAN-PROGRAM-REAL-TIBIA-EVIDENCE-COLLECTION
coordination_id: RTEC-005-PREFLIGHT
status: review
agent: "GPT-5.6 Thinking"
branch: docs/rtec-005-preflight-20260726
base_branch: main
created: 2026-07-26T10:00:00+02:00
updated: 2026-07-26T10:35:00+02:00
last_verified_commit: "265dac0c8edbdda83050be8a2da64dbc38d9d86a"
risk: medium
related_issue: ""
related_pr: "952"
depends_on:
  - RTEC-004
blocks:
  - RTEC-005-WAVE-1
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260726-rtec-005-preflight.md
  shared:
    - docs/agents/programs/REAL_TIBIA_EVIDENCE_COLLECTION_PROGRAM.md
  read_only:
    - docs/agents/tasks/archive/CAN-20260725-rtec-004-wave-1-coordination.md
    - docs/agents/real-tibia/evidence/generated/EVIDENCE_INDEXES.json
    - docs/agents/real-tibia/evidence/modules/**
    - docs/agents/real-tibia/evidence/requests/**
    - docs/agents/real-tibia/registry/modules/item-decay.yaml
    - docs/agents/real-tibia/registry/modules/parties.yaml
    - src/items/decay/**
    - src/creatures/players/grouping/party.*
modules_touched:
  - real-tibia-evidence-collection
  - item-decay
  - parties
reuses:
  - canary-real-tibia-evidence-record-v1
  - canary-real-tibia-owner-request-v1
  - canary-real-tibia-generated-indexes-v1
  - canonical Real Tibia module registry
  - RTEC-004 two-worker serialized-index result
public_interfaces: []
cross_repo_tasks: []
---

# Goal

Reconcile the durable RTEC programme state after RTEC-004 and perform one fresh bounded preflight that selects two independent module roots for RTEC-005 without creating evidence records, modifying owner implementation paths or starting concurrent shared-index writes.

# Final preflight result

- Repository baseline: `main@a4a35495d4a8dc047bd3315b95c9fb577ac597af`.
- RTEC-004 lifecycle is durably complete through PR #945, merge `0b65d2e6045c26c5e5295c12a74c627a5f67668f`.
- Current evidence corpus contains ten evidence records across `vocations`, `weapon-proficiency` and `item-definitions`, plus two active owner requests.
- Open PRs #951, #948, #815, #559, #526 and #514 do not own the RTEC task, programme or proposed dossier paths.
- Selected RTEC-005 roots: `item-decay` and `parties`.
- Neither selected dossier currently exists.
- Registry/source roots are present and disjoint:
  - `item-decay`: `docs/agents/real-tibia/registry/modules/item-decay.yaml`, `src/items/decay/**`;
  - `parties`: `docs/agents/real-tibia/registry/modules/parties.yaml`, `src/creatures/players/grouping/party.*`.
- Workers must own only their task, one dossier root and their own owner-request records. They must not edit the programme or shared generated index.
- The coordinator must serialize `docs/agents/real-tibia/evidence/generated/EVIDENCE_INDEXES.json` after worker merges.
- PR #952 contains exactly this task record and the reconciled programme record.

# RTEC-005 wave contract

- Maximum concurrent Collector workers: `2`.
- Maximum concurrently open RTEC-005 worker PRs: `2`.
- Shared global-index publishers: exactly `1` coordinator integration lane.
- Worker A candidate: `item-decay`.
- Worker B candidate: `parties`.
- No runtime, data, map, protocol, maintained-client, workflow, TCR implementation or E2E path is authorized for modification.
- Search misses, file presence and static source paths remain bounded evidence and may not be promoted to Real Tibia parity or absence claims.

# Acceptance criteria

- [x] Read repository and nested agent governance plus routed handoff contracts.
- [x] Pin fresh `main`, RTEC-004 archive/merge state and evidence/request index.
- [x] Inspect open PRs for path/module/contract overlap.
- [x] Select exactly two independent absent dossier roots.
- [x] Verify exact registry and source roots for both selections.
- [x] Preserve the RTEC-004 two-worker and serialized-index constraint.
- [x] Reconcile RTEC-004/RTEC-005 state and handoff in the programme record.
- [x] Open draft PR #952 and refresh its branch to current main.
- [x] Restore the concurrent OAM-051 task byte-for-byte after detecting incomplete tree integration.
- [x] Pass exact-head ownership and CI on `265dac0c8edbdda83050be8a2da64dbc38d9d86a`.
- [ ] Pass renewed exact-final-head checks triggered by this checkpoint.
- [ ] Complete review, mark Ready, squash merge and archive this preflight task.
- [ ] Create the next active RTEC-005 wave coordinator task only after this task is durably complete.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-26T10:35:00+02:00
head: 265dac0c8edbdda83050be8a2da64dbc38d9d86a
branch: docs/rtec-005-preflight-20260726
pr: 952
status: ready
context_routes:
  - agent-governance
  - real-tibia-parity
owned_paths:
  - docs/agents/tasks/active/CAN-20260726-rtec-005-preflight.md
  - docs/agents/programs/REAL_TIBIA_EVIDENCE_COLLECTION_PROGRAM.md
proven:
  - RTEC-004 worker PRs 930 and 931, coordinator PR 929 and lifecycle PR 945 are merged
  - synchronized main baseline is a4a35495d4a8dc047bd3315b95c9fb577ac597af
  - evidence index has ten records across vocations, weapon-proficiency and item-definitions and two active owner requests
  - item-decay and parties dossier roots are absent at the pinned baseline
  - registry and source roots exist for item-decay and parties and are disjoint
  - current open PRs do not own the RTEC programme task or selected dossier paths
  - programme queue records RTEC-004 merged and RTEC-005 active with the two-worker serialized-index constraint
  - incomplete merge-tree integration was detected from the PR diff and the concurrent OAM-051 task was restored with its exact main blob
  - PR 952 changed-file list contains exactly the RTEC programme and preflight task records
  - Agent Task Ownership 30192269253 and CI 30192269348 passed on 265dac0c8edbdda83050be8a2da64dbc38d9d86a
derived:
  - item-decay and parties are suitable independent candidates for a two-worker RTEC-005 wave
  - the shared deterministic evidence index must remain coordinator-only
  - worker branches must wait until this preflight is merged and archived
unknown:
  - exact evidence claims each worker will accept after source collection and review
  - whether either worker will require a new owner request
conflicts: []
first_failure:
  marker: none
  evidence: preflight scope, ownership and ordinary exact-head CI are green; renewed final-head checks are pending
rejected_hypotheses:
  - start eight workers because RTEC-004 proved only a two-worker safe cap under observed CI and review load
  - select wheel-of-destiny because OAM-051 owns current Wheel preflight state
  - allow workers to publish the shared global index concurrently
  - accept a merge commit based only on parent topology because its tree omitted a concurrently added active task
changed_paths:
  - docs/agents/tasks/active/CAN-20260726-rtec-005-preflight.md
  - docs/agents/programs/REAL_TIBIA_EVIDENCE_COLLECTION_PROGRAM.md
validation:
  - command: connector-based repository PR module and evidence preflight
    result: PASS
    evidence: main a4a35495d4a8dc047bd3315b95c9fb577ac597af; relevant open PRs; canonical registry and evidence index
  - command: programme queue and handoff reconciliation
    result: PASS
    evidence: RTEC-004 merged, RTEC-005 active, two-worker cap and one serialized index lane recorded
  - command: current-main drift and changed-file reconciliation
    result: PASS
    evidence: concurrent OAM-051 task restored exactly; PR 952 contains only two declared RTEC paths
  - command: Agent Task Ownership
    result: PASS
    evidence: run 30192269253 on 265dac0c8edbdda83050be8a2da64dbc38d9d86a
  - command: CI
    result: PASS
    evidence: run 30192269348 on 265dac0c8edbdda83050be8a2da64dbc38d9d86a
  - command: renewed exact-final-head workflows after this checkpoint
    result: NOT_RUN
    evidence: pending final checkpoint head
blockers: []
next_action: Require renewed exact-final-head checks on PR 952, audit discussions and changed paths, then mark Ready and squash merge without another commit.
```
