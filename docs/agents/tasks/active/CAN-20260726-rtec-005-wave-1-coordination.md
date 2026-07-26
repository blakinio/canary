---
task_id: CAN-20260726-rtec-005-wave-1-coordination
program_id: CAN-PROGRAM-REAL-TIBIA-EVIDENCE-COLLECTION
coordination_id: RTEC-005-WAVE-1
status: review
agent: "GPT-5.6 Thinking"
branch: docs/rtec-005-wave-1-coordinator-20260726
base_branch: main
created: 2026-07-26T11:30:00+02:00
updated: 2026-07-27T00:08:00+02:00
last_verified_commit: "d8df7b21adabcf959858a13bc1fbb5caa1fe764d"
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
    - docs/agents/real-tibia/evidence/modules/item-definitions/EVIDENCE_INDEX.yaml
    - docs/agents/real-tibia/evidence/modules/vocations/EVIDENCE_INDEX.yaml
    - docs/agents/real-tibia/evidence/modules/weapon-proficiency/EVIDENCE_INDEX.yaml
    - tools/agents/real_tibia_evidence_test_support.py
    - tools/agents/test_real_tibia_evidence.py
    - tools/agents/test_real_tibia_owner_request_prepublication.py
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
- [x] Independently adjudicate `RT-ITEM-DECAY-0001`, `RT-PARTIES-0001` and `RT-PARTIES-0002` without broadening their claims.
- [x] Preserve runtime, persistence, formulas, protocol/client and physical gameplay dimensions as explicit nonclaims.
- [x] Keep both existing owner requests unchanged and create no new request without a narrowed non-duplicative owner contract.
- [x] Advance the canonical Evidence Contracts `as_of` date and shared test support to 2026-07-26 without backdating evidence.
- [x] Generate deterministic item-decay, parties and global indexes exactly once from accepted source records.
- [x] Reconcile the programme queue and restore read-only, check-only Evidence Contracts CI.
- [ ] Pass exact-head Evidence Contracts, Ownership, Registry, Upstream and CI.
- [ ] Pass the Ready-state final gate, squash-merge PR #955 and archive this coordinator task.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-27T00:08:00+02:00
head: d8df7b21adabcf959858a13bc1fbb5caa1fe764d
branch: docs/rtec-005-wave-1-coordinator-20260726
pr: 955
status: validating
context_routes:
  - agent-governance
  - real-tibia-parity
owned_paths:
  - docs/agents/tasks/active/CAN-20260726-rtec-005-wave-1-coordination.md
  - docs/agents/real-tibia/evidence/modules/item-decay/**
  - docs/agents/real-tibia/evidence/modules/parties/**
  - docs/agents/real-tibia/evidence/modules/item-definitions/EVIDENCE_INDEX.yaml
  - docs/agents/real-tibia/evidence/modules/vocations/EVIDENCE_INDEX.yaml
  - docs/agents/real-tibia/evidence/modules/weapon-proficiency/EVIDENCE_INDEX.yaml
  - docs/agents/real-tibia/evidence/generated/EVIDENCE_INDEXES.json
  - docs/agents/programs/REAL_TIBIA_EVIDENCE_COLLECTION_PROGRAM.md
  - .github/workflows/real-tibia-evidence.yml
  - tools/agents/real_tibia_evidence_test_support.py
  - tools/agents/test_real_tibia_evidence.py
  - tools/agents/test_real_tibia_owner_request_prepublication.py
proven:
  - worker PRs 957 and 958 passed Ready-state Required and merged; lifecycle PRs 973 and 976 archived both worker tasks
  - artifact run 30220767816 validated the bounded acceptance view and generated deterministic indexes
  - artifact 8637133045 has digest sha256:4adeb6625a0953223d3fed469c32b65b439061cbcddb9879a9b6079a9451c82a
  - commit 2a74acaa57413a3fb95529ba9c8c4196d6907d9b publishes the exact validated artifact outputs
  - RT-ITEM-DECAY-0001 is accepted only for the selected current Canary duration-bucket and transform/removal source path at runtime-path-proven
  - RT-PARTIES-0001 is accepted only for current official visible party and Shared Experience requirements at definition-found
  - RT-PARTIES-0002 is accepted only for the selected current Canary party lifecycle and Shared Experience source path at runtime-path-proven
  - the global index is as_of 2026-07-26 with 13 evidence records, 2 owner requests and 10 version-history records
  - generated input_sha256 is 8572712a873048c4385e471008c42c97fe09310bafb6d7a0874e8aa6b2ade03b
  - RTREQ-FEATURE-VOCATIONS-0001 and RTREQ-TCR-ITEM-DEFINITIONS-0001 remain unchanged; no new owner request was created
  - final workflow is contents-read, uses non-persistent checkout credentials and validates deterministically at as_of 2026-07-26
  - Evidence Contracts, Module Registry, Upstream Intelligence and ordinary CI passed on head 7d71cceb807c24d64af39088f09fc1da934878fc
  - Ownership run 30222445667 isolated only the unsupported checkpoint result value PARTIAL
  - no validator, schema or evidence-rule change was made
derived:
  - the wave publishes three bounded evidence records but makes no whole-module or Real Tibia parity claim
  - the next RTEC-005 wave requires a fresh ownership preflight and the same single serialized shared-index lane
unknown:
  - runtime timing and restart behavior for item decay
  - exact active party configuration, bonus/distribution formulas, activity call sites and battle-sign behavior
  - protocol/client interpretation and physical gameplay parity for both modules
conflicts: []
first_failure:
  marker: unsupported-checkpoint-validation-result
  evidence: Ownership run 30222445667 rejected only validation.result PARTIAL; supported fail-closed value FAIL now records the same historical outcome
rejected_hypotheses:
  - backdate evidence to 2026-07-25
  - weaken future-evidence validation
  - claim whole-module parity from static source and current web documentation
  - create broad owner requests without a narrowed, non-duplicative question
  - retain temporary contents-write or materialization logic in the final workflow
changed_paths:
  - docs/agents/tasks/active/CAN-20260726-rtec-005-wave-1-coordination.md
  - docs/agents/programs/REAL_TIBIA_EVIDENCE_COLLECTION_PROGRAM.md
  - docs/agents/real-tibia/evidence/modules/*/EVIDENCE_INDEX.yaml
  - docs/agents/real-tibia/evidence/modules/item-decay/**
  - docs/agents/real-tibia/evidence/modules/parties/**
  - docs/agents/real-tibia/evidence/generated/EVIDENCE_INDEXES.json
  - .github/workflows/real-tibia-evidence.yml
  - tools/agents/real_tibia_evidence_test_support.py
  - tools/agents/test_real_tibia_evidence.py
  - tools/agents/test_real_tibia_owner_request_prepublication.py
validation:
  - command: worker Ready-state and lifecycle gates
    result: PASS
    evidence: Required runs 30216659464 and 30219648745; lifecycle PRs 973 and 976 merged
  - command: bounded adjudication artifact generation
    result: PASS
    evidence: Evidence Contracts run 30220767816 generated, validated and rechecked artifact 8637133045
  - command: exact-head standard gates on 7d71cceb807c24d64af39088f09fc1da934878fc
    result: FAIL
    evidence: Evidence Contracts, Registry, Upstream and CI passed; Ownership failed only because validation result PARTIAL is unsupported
blockers: []
next_action: Pass exact-head standard gates, then run the Ready-state final gate, squash-merge PR 955 and archive its coordinator task.
```
