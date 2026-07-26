---
task_id: CAN-20260726-rtec-005-wave-1-coordination
program_id: CAN-PROGRAM-REAL-TIBIA-EVIDENCE-COLLECTION
coordination_id: RTEC-005-WAVE-1
status: implementing
agent: "GPT-5.6 Thinking"
branch: docs/rtec-005-wave-1-coordinator-20260726
base_branch: main
created: 2026-07-26T11:30:00+02:00
updated: 2026-07-26T23:15:00+02:00
last_verified_commit: "86ad1fc0e69ef4450871173735346af6a20d4eba"
risk: medium
related_issue: ""
related_pr: "955"
depends_on:
  - PR-957-ITEM-DECAY-MERGED
  - PR-973-ITEM-DECAY-TASK-ARCHIVED
  - PR-958-PARTIES-MERGED
  - PR-976-PARTIES-TASK-ARCHIVED
blocks: []
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260726-rtec-005-wave-1-coordination.md
    - docs/agents/real-tibia/evidence/modules/item-decay/**
    - docs/agents/real-tibia/evidence/modules/parties/**
    - .github/workflows/real-tibia-evidence.yml
  shared:
    - docs/agents/programs/REAL_TIBIA_EVIDENCE_COLLECTION_PROGRAM.md
    - docs/agents/real-tibia/evidence/generated/EVIDENCE_INDEXES.json
  read_only:
    - docs/agents/tasks/archive/CAN-20260726-rtec-005-item-decay.md
    - docs/agents/tasks/archive/CAN-20260726-rtec-005-parties.md
    - docs/agents/real-tibia/evidence/requests/**
    - docs/agents/real-tibia/registry/modules/item-decay.yaml
    - docs/agents/real-tibia/registry/modules/parties.yaml
    - src/items/decay/**
    - src/creatures/players/grouping/party.*
    - tools/agents/real_tibia_evidence.py
    - tools/agents/real_tibia_evidence_lib.py
modules_touched:
  - real-tibia-evidence-collection
  - item-decay
  - parties
reuses:
  - canary-real-tibia-evidence-record-v1
  - canary-real-tibia-generated-indexes-v1
  - RTEC-005 worker candidate packages
  - prepublication publication view merged in PR 960
  - owner-request publication view merged in PR 968
public_interfaces: []
cross_repo_tasks: []
---

# Goal

Complete RTEC-005 wave 1 by independently adjudicating the merged `item-decay` and `parties` candidates, publishing only their bounded accepted claims, advancing the canonical evidence date to 2026-07-26 and integrating deterministic module/global indexes exactly once.

# Acceptance criteria

- [x] Merge item-decay worker PR #957 after exact-head and Ready-state gates.
- [x] Archive the completed item-decay task through PR #973.
- [x] Refresh the parties worker after the first merge and lifecycle cleanup.
- [x] Merge parties worker PR #958 after exact-head and Ready-state gates.
- [x] Archive the completed parties task through PR #976.
- [ ] Independently adjudicate `RT-ITEM-DECAY-0001`, `RT-PARTIES-0001` and `RT-PARTIES-0002` without broadening their claims.
- [ ] Preserve runtime, persistence, formulas, protocol/client and physical gameplay dimensions as explicit nonclaims.
- [ ] Keep both existing owner requests unchanged and create no new request without a narrowed non-duplicative owner contract.
- [ ] Advance the canonical Evidence Contracts `as_of` date to 2026-07-26 without backdating evidence.
- [ ] Generate deterministic item-decay, parties and global indexes exactly once from accepted source records.
- [ ] Reconcile the programme queue and pass exact-head Evidence Contracts, Ownership, Registry, Upstream and CI.
- [ ] Pass the Ready-state final gate, squash-merge PR #955 and archive this coordinator task.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-26T23:15:00+02:00
head: 86ad1fc0e69ef4450871173735346af6a20d4eba
branch: docs/rtec-005-wave-1-coordinator-20260726
pr: 955
status: implementing
context_routes:
  - agent-governance
  - real-tibia-parity
owned_paths:
  - docs/agents/tasks/active/CAN-20260726-rtec-005-wave-1-coordination.md
  - docs/agents/real-tibia/evidence/modules/item-decay/**
  - docs/agents/real-tibia/evidence/modules/parties/**
  - docs/agents/real-tibia/evidence/generated/EVIDENCE_INDEXES.json
  - docs/agents/programs/REAL_TIBIA_EVIDENCE_COLLECTION_PROGRAM.md
  - .github/workflows/real-tibia-evidence.yml
proven:
  - item-decay PR 957 passed Required run 30216659464 and merged as 7e6d0078d7ad87a82aea092ff4285256fcae746f
  - item-decay lifecycle PR 973 merged as ad734f81772eb840c7e1ce18b27ac9ed0d2a4c50
  - parties PR 958 passed Required run 30219648745 and merged as 7a09367589dfc08e482edadbe77e556ecf0cfaa7
  - parties lifecycle PR 976 passed Ownership run 30220366677 and CI run 30220366776 and merged as 86ad1fc0e69ef4450871173735346af6a20d4eba
  - RT-ITEM-DECAY-0001 is bounded to the selected current Canary duration-bucket and transform/removal source path
  - RT-PARTIES-0001 is bounded to current official visible party and Shared Experience requirements
  - RT-PARTIES-0002 is bounded to the selected current Canary party lifecycle and Shared Experience source path
  - all three records preserve explicit whole-module and parity nonclaims
  - no worker created an owner request or edited the shared global index
  - RTREQ-FEATURE-VOCATIONS-0001 and RTREQ-TCR-ITEM-DEFINITIONS-0001 remain unchanged
derived:
  - the coordinator may now review and publish the three bounded records because worker ownership has been released
  - the fixed 2026-07-25 workflow date must advance before honest 2026-07-26 evidence can be accepted
unknown:
  - runtime timing and restart behavior for item decay
  - exact active party configuration, bonus/distribution formulas, activity call sites and battle-sign behavior
  - protocol/client interpretation and physical gameplay parity for both modules
conflicts: []
first_failure:
  marker: accepted-records-and-indexes-not-yet-materialized
  evidence: worker candidates are merged and archived, but remain review-needed and absent from the published indexes
rejected_hypotheses:
  - backdate evidence to 2026-07-25
  - claim whole-module parity from static source and current web documentation
  - create broad owner requests without a narrowed, non-duplicative question
changed_paths:
  - docs/agents/tasks/active/CAN-20260726-rtec-005-wave-1-coordination.md
validation:
  - command: worker Ready-state final gates
    result: PASS
    evidence: runs 30216659464 and 30219648745
  - command: worker lifecycle cleanup gates
    result: PASS
    evidence: PRs 973 and 976 merged after Ownership and CI
blockers: []
next_action: Materialize the bounded coordinator acceptance view, generate deterministic indexes at as_of 2026-07-26, then commit the reviewed outputs and restore fail-closed check-only CI.
```
