---
task_id: CAN-20260729-rtec-005-wave-2-coordination
program_id: CAN-PROGRAM-REAL-TIBIA-EVIDENCE-COLLECTION
coordination_id: RTEC-005-WAVE-2
status: implementing
agent: "GPT-5.6 Thinking"
branch: docs/rtec-005-wave-2-coordinator-20260729
base_branch: main
created: 2026-07-29T10:08:00+02:00
updated: 2026-07-29T11:37:00+02:00
last_verified_commit: "03d483055c135bcd62246c3db1083444eae9799e"
risk: medium
related_issue: ""
related_pr: "1000"
depends_on:
  - CAN-20260729-rtec-005-wave-2-preflight
  - CAN-20260729-rtec-005-chat-communication
  - CAN-20260729-rtec-005-engine-scheduler
blocks: []
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260729-rtec-005-wave-2-coordination.md
  shared:
    - docs/agents/programs/REAL_TIBIA_EVIDENCE_COLLECTION_PROGRAM.md
    - docs/agents/real-tibia/evidence/generated/EVIDENCE_INDEXES.json
    - docs/agents/real-tibia/evidence/modules/chat-communication/**
    - docs/agents/real-tibia/evidence/modules/engine-scheduler/**
    - .github/workflows/real-tibia-evidence.yml
    - tools/agents/real_tibia_evidence_test_support.py
    - tools/agents/test_real_tibia_evidence.py
    - tools/agents/test_real_tibia_owner_request_prepublication.py
  read_only:
    - docs/agents/tasks/archive/CAN-20260729-rtec-005-wave-2-preflight.md
    - docs/agents/tasks/archive/CAN-20260729-rtec-005-chat-communication.md
    - docs/agents/tasks/archive/CAN-20260729-rtec-005-engine-scheduler.md
    - docs/agents/real-tibia/evidence/requests/**
modules_touched:
  - real-tibia-evidence-collection
  - chat-communication
  - engine-scheduler
reuses:
  - canary-real-tibia-evidence-record-v1
  - canary-real-tibia-generated-indexes-v1
  - RTEC-005 wave 1 serialized coordinator lane
public_interfaces: []
cross_repo_tasks: []
---

# Goal

Complete RTEC-005 wave 2 through two independent worker packages, serialized coordinator adjudication and one deterministic publication update, without broadening source-scoped claims or mutating owner-request paths.

# Acceptance criteria

- [x] Start one coordinator task before either worker branch.
- [x] Merge and archive the `chat-communication` worker package.
- [x] Merge and archive the `engine-scheduler` worker package.
- [ ] Independently adjudicate both worker records without claiming ordering, privacy, delivery, timing, fairness, race freedom, shutdown correctness, gameplay or Real Tibia parity.
- [ ] Preserve all three existing active owner requests unchanged and create no new broad request.
- [ ] Advance canonical evidence publication to `2026-07-29` and regenerate module/global indexes exactly once.
- [ ] Pass exact-head Evidence Contracts, Agent Task Ownership and ordinary CI.
- [ ] Pass ready-state full final gate, squash-merge and archive this coordinator task.

# Worker outcomes

- Chat worker PR #1001 passed its exact-head final gate and merged as `dea75ab7390fbc90c5c1ab24b76bfd5b89d1867f`.
- Engine worker PR #1002 passed its exact-head final gate and merged as `9fe1d19c82b81df067d453cc32efe19fded3257e`.
- Lifecycle PR #1003 archived both worker tasks and merged as `03d483055c135bcd62246c3db1083444eae9799e`.
- Both candidates remain bounded `review-needed` records until this coordinator adjudicates and regenerates publication indexes.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-29T11:37:00+02:00
head: 03d483055c135bcd62246c3db1083444eae9799e
branch: docs/rtec-005-wave-2-coordinator-20260729
pr: 1000
status: implementing
context_routes:
  - agent-governance
  - real-tibia-parity
owned_paths:
  - docs/agents/tasks/active/CAN-20260729-rtec-005-wave-2-coordination.md
  - docs/agents/programs/REAL_TIBIA_EVIDENCE_COLLECTION_PROGRAM.md
  - docs/agents/real-tibia/evidence/generated/EVIDENCE_INDEXES.json
  - docs/agents/real-tibia/evidence/modules/chat-communication/**
  - docs/agents/real-tibia/evidence/modules/engine-scheduler/**
proven:
  - coordinator PR 1000 existed before worker branches
  - worker PRs 1001 and 1002 passed exact-head final gates and merged
  - lifecycle PR 1003 archived both workers
  - current published view remains as_of 2026-07-26 with 13 evidence records, 3 active owner requests and 10 version-history records
  - exactly one coordinator owns shared-index publication
derived:
  - both bounded source records are eligible for independent coordinator adjudication
unknown:
  - final deterministic index output at as_of 2026-07-29
conflicts: []
first_failure:
  marker: none
  evidence: worker and lifecycle stages completed within the wave contract
rejected_hypotheses:
  - let workers update the shared global index
  - mutate existing owner requests during source-only collection
changed_paths:
  - docs/agents/tasks/active/CAN-20260729-rtec-005-wave-2-coordination.md
validation:
  - command: worker merge and lifecycle reconciliation
    result: PASS
    evidence: PRs 1001, 1002 and 1003 merged
blockers: []
next_action: Adjudicate both bounded records, generate deterministic indexes at as_of 2026-07-29 and validate the exact coordinator head.
```