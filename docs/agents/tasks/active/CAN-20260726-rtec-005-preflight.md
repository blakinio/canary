---
task_id: CAN-20260726-rtec-005-preflight
program_id: CAN-PROGRAM-REAL-TIBIA-EVIDENCE-COLLECTION
coordination_id: RTEC-005-PREFLIGHT
status: implementing
agent: "GPT-5.6 Thinking"
branch: docs/rtec-005-preflight-20260726
base_branch: main
created: 2026-07-26T10:00:00+02:00
updated: 2026-07-26T10:00:00+02:00
last_verified_commit: "d0c76c6f964a5266789b252173eb24832a309e80"
risk: medium
related_issue: ""
related_pr: ""
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

# Preflight result

- Repository baseline: `main@d0c76c6f964a5266789b252173eb24832a309e80`.
- RTEC-004 lifecycle is durably complete through PR #945, merge `0b65d2e6045c26c5e5295c12a74c627a5f67668f`.
- Current evidence corpus contains ten accepted/retained evidence records across `vocations`, `weapon-proficiency` and `item-definitions`, plus two active owner requests.
- Open PRs #951, #948, #815, #559, #526 and #514 do not own the proposed RTEC task, programme or dossier paths.
- The selected RTEC-005 roots are `item-decay` and `parties`.
- Neither selected dossier currently exists.
- Current registry/source roots are present and disjoint:
  - `item-decay`: `docs/agents/real-tibia/registry/modules/item-decay.yaml`, `src/items/decay/**`;
  - `parties`: `docs/agents/real-tibia/registry/modules/parties.yaml`, `src/creatures/players/grouping/party.*`.
- Workers must own only their task, one dossier root and their own owner-request records. They must not edit the programme or shared generated index.
- The coordinator must serialize `docs/agents/real-tibia/evidence/generated/EVIDENCE_INDEXES.json` after worker merges.

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
- [ ] Reconcile RTEC-004/RTEC-005 state and handoff in the programme record.
- [ ] Open a draft PR and pass exact-head ownership/CI checks.
- [ ] Complete review, apply `ci:final-gate`, pass the final head, squash merge and archive this preflight task.
- [ ] Create the next active RTEC-005 wave coordinator task only after this task is durably complete.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-26T10:00:00+02:00
head: d0c76c6f964a5266789b252173eb24832a309e80
branch: docs/rtec-005-preflight-20260726
pr: none
status: implementing
context_routes:
  - agent-governance
  - real-tibia-parity
owned_paths:
  - docs/agents/tasks/active/CAN-20260726-rtec-005-preflight.md
  - docs/agents/programs/REAL_TIBIA_EVIDENCE_COLLECTION_PROGRAM.md
proven:
  - RTEC-004 worker PRs 930 and 931, coordinator PR 929 and lifecycle PR 945 are merged
  - main baseline for this preflight is d0c76c6f964a5266789b252173eb24832a309e80
  - evidence index has ten records across vocations, weapon-proficiency and item-definitions and two active owner requests
  - item-decay and parties dossier roots are absent at the pinned baseline
  - registry and source roots exist for item-decay and parties and are disjoint
  - current open PRs do not own the proposed RTEC programme/task/dossier paths
derived:
  - item-decay and parties are suitable independent candidates for a two-worker RTEC-005 wave
  - the shared deterministic evidence index must remain coordinator-only
  - programme state must be reconciled before starting worker branches
unknown:
  - exact evidence claims each worker will accept after source collection and review
  - whether either worker will require a new owner request
conflicts: []
first_failure:
  marker: programme-state-stale
  evidence: programme queue still marks RTEC-004 planned and RTEC-005 planned despite merged RTEC-004 lifecycle
rejected_hypotheses:
  - start eight workers because RTEC-004 proved only a two-worker safe cap under observed CI and review load
  - select wheel-of-destiny because open PR 951 owns current OAM Wheel preflight state
  - allow workers to publish the shared global index concurrently
changed_paths:
  - docs/agents/tasks/active/CAN-20260726-rtec-005-preflight.md
validation:
  - command: connector-based repository, PR, module and evidence preflight
    result: PASS
    evidence: main d0c76c6f964a5266789b252173eb24832a309e80; PRs 951, 948, 815, 559, 526, 514; canonical registry and evidence index
blockers: []
next_action: Open the draft PR, reconcile the programme queue and handoff, then validate ownership and CI on the exact head.
```
