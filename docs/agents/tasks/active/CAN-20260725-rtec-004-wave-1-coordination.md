---
task_id: CAN-20260725-rtec-004-wave-1-coordination
program_id: CAN-PROGRAM-REAL-TIBIA-EVIDENCE-COLLECTION
coordination_id: RTEC-004-WAVE-1
status: implementing
agent: "GPT-5.6 Thinking"
branch: feat/rtec-004-wave-1-coordinator-20260725
base_branch: main
created: 2026-07-25T20:11:38+02:00
updated: 2026-07-25T23:05:00+02:00
last_verified_commit: "a29bd6a05ea641f0a01cfdcd67fa8ac1b6fc7866"
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

# Final wave outcome

RTEC-004 wave 1 completed with two isolated Collector workers and one serialized global-index lane.

## Worker A — weapon proficiency

- Task: `CAN-20260725-rtec-004-weapon-proficiency`.
- PR: #930.
- Merge commit: `8ef88972fd1c473b9f3c0a5cfb9bed98c78bdbc9`.
- Delivered three accepted records, dossier, behavior model, decisions, version history, module index and deterministic global index.
- Current selected Canary paths implement original-tree perk selection and player-scoped per-weapon KV state; they do not establish the official 2026 modified-slot manipulation lifecycle.
- Character-switch pending-notification isolation remains `UNKNOWN`.
- Exact-head and Ready-state final gates passed before squash merge.

## Worker B — item definitions

- Task: `CAN-20260725-rtec-004-cloud-in-a-bottle`.
- PR: #931.
- Merge commit: `a29bd6a05ea641f0a01cfdcd67fa8ac1b6fc7866`.
- Delivered two accepted records, dossier, behavior model, decisions, version history, module index, deterministic global index and structured review.
- Official correction is pinned: Cloud in a Bottle is available from difficulty `10`, not `15`.
- Selected textual paths contain no official-name variant or exact candidate ID `54651`, but the miss is not promoted to item absence because base identity may originate from `appearances.dat`.
- `RTREQ-TCR-ITEM-DEFINITIONS-0001` is ready for owner triage to resolve exact official-client object identity and Canary appearances correspondence.
- Exact-head and Ready-state final gates passed before squash merge.

# Concurrency outcome

- Two workers were viable because they owned separate module roots and did not edit feature, client, protocol, map, TCR implementation or E2E owner paths.
- The shared deterministic global index could not safely be published concurrently. Worker B refreshed after Worker A merged and generated the combined index once.
- Review and CI load remained bounded by running only two Collector workers rather than the programme maximum of eight.
- No worker result was promoted beyond its strongest proof level; unresolved behavior and identity questions were preserved as `UNKNOWN` or owner requests.

# RTEC-005 decision

RTEC-005 will use a maximum of two concurrent Collector workers and exactly one serialized global-index integration lane. It may start only after a fresh repository, ownership, CI-load and evidence-corpus preflight selects two independent module roots. No RTEC-005 worker may publish the shared generated index concurrently with another worker.

This is a concurrency/governance decision only. It does not preselect module claims or authorize owner-path implementation.

# Shared boundaries

- `RTREQ-FEATURE-VOCATIONS-0001` remains an independent owner request.
- `RTREQ-TCR-ITEM-DEFINITIONS-0001` remains ready for TCR owner triage.
- Collector completion does not imply gameplay parity, release approval, item presence/absence or runtime behavior beyond accepted evidence records.
- Worker implementation, data, assets, map, maintained-client, protocol and E2E paths remained unchanged.

# Acceptance criteria

- [x] Verify main, programme, registry, evidence/request state and open PR ownership.
- [x] Pin the current official release/change baseline and proof limits.
- [x] Reduce wave 1 to two independent workers.
- [x] Create one branch, task and draft PR for each worker.
- [x] Assign exact package scopes, coordination IDs and dossier roots.
- [x] Establish shared-index serialisation between workers.
- [x] Merge PR #930 after structured review and exact-final-head gates.
- [x] Refresh PR #931 from main, finish its bounded dossier and pass exact-final-head gates.
- [x] Merge PR #931 without owner-path edits.
- [x] Refresh coordinator PR #929 from current main and reconcile wave state.
- [x] Record concurrency outcome and one exact RTEC-005 decision.
- [ ] Pass exact-final-head coordinator checks and merge PR #929.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-25T23:05:00+02:00
head: a29bd6a05ea641f0a01cfdcd67fa8ac1b6fc7866
branch: feat/rtec-004-wave-1-coordinator-20260725
pr: 929
status: implementing
context_routes:
  - agent-governance
  - real-tibia-parity
owned_paths:
  - docs/agents/tasks/active/CAN-20260725-rtec-004-wave-1-coordination.md
proven:
  - Worker A PR 930 merged as 8ef88972fd1c473b9f3c0a5cfb9bed98c78bdbc9 after exact-head and Ready-state final gates
  - Worker B PR 931 merged as a29bd6a05ea641f0a01cfdcd67fa8ac1b6fc7866 after exact-head and Ready-state final gates
  - Worker A and Worker B used separate module roots and did not edit owner implementation paths
  - Worker B refreshed after Worker A and published the combined deterministic global index once
  - RTEC-004 added five accepted evidence records and one bounded TCR request across two modules
  - RTREQ-TCR-ITEM-DEFINITIONS-0001 is ready for owner triage
  - all temporary diagnostic and export tooling was removed before each worker merge
derived:
  - two-worker Collector concurrency is viable when module roots are isolated and the global index is serialized
  - the programme maximum of eight workers is not appropriate under the observed repository CI and review load
  - RTEC-005 should retain a two-worker cap and one global-index lane until a later campaign proves a higher safe limit
unknown:
  - feature-owner runtime result for official weapon-proficiency manipulation
  - maintained-client character-switch pending-notification isolation
  - exact official-client Cloud in a Bottle object identity and Canary appearances correspondence
conflicts: []
first_failure:
  marker: owner-evidence-deferred
  evidence: Collector work completed, while runtime and proprietary client-reference questions remain correctly routed to owner evidence rather than guessed
rejected_hypotheses:
  - start eight workers immediately because current CI storage and review load supported only a bounded two-worker wave
  - permit both workers to publish the shared index concurrently because deterministic index serialization was required
  - promote selected textual search misses or secondary candidate identifiers into absence or identity claims
changed_paths:
  - docs/agents/tasks/active/CAN-20260725-rtec-004-wave-1-coordination.md
validation:
  - command: Worker A exact-head and Ready-state final gates
    result: PASS
    evidence: PR 930 merged as 8ef88972fd1c473b9f3c0a5cfb9bed98c78bdbc9
  - command: Worker B exact-head and Ready-state final gates
    result: PASS
    evidence: PR 931 merged as a29bd6a05ea641f0a01cfdcd67fa8ac1b6fc7866
  - command: concurrency and ownership reconciliation
    result: PASS
    evidence: separate module roots, no owner-path edits and one serialized combined index integration
blockers: []
next_action: Pass exact-final-head checks on PR 929, transition it to Ready, and merge without further scope changes.
```
