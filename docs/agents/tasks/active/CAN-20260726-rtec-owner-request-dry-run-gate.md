---
task_id: CAN-20260726-rtec-owner-request-dry-run-gate
program_id: CAN-PROGRAM-REAL-TIBIA-EVIDENCE-COLLECTION
coordination_id: RTEC-005-OWNER-REQUEST-DRY-RUN-GATE
status: review
agent: "GPT-5.6 Thinking"
branch: fix/rtec-owner-request-dry-run-gate-20260726
base_branch: main
created: 2026-07-26T20:55:00+02:00
updated: 2026-07-28T22:18:37+02:00
last_verified_commit: "0251bc1e460966ce0eb238d34f0d11a6db3b1462"
risk: low
related_issue: ""
related_pr: "972"
depends_on: []
blocks:
  - RTEC-005 worker evidence validation
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260726-rtec-owner-request-dry-run-gate.md
    - .github/workflows/real-tibia-evidence.yml
  shared: []
  read_only:
    - tools/agents/real_tibia_owner_request.py
    - tools/agents/real_tibia_evidence_lib.py
    - docs/agents/real-tibia/evidence/requests/feature/RTREQ-FEATURE-VOCATIONS-0001.yaml
modules_touched:
  - Real Tibia evidence CI
reuses:
  - canary-real-tibia-owner-request-v1
public_interfaces: []
cross_repo_tasks: []
---

# Goal

Repair the non-mutating owner-request workflow exercise so it validates a corpus-valid candidate transition while leaving the production request unchanged.

# Acceptance criteria

- [x] Replace the invalid dry-run rejection with a corpus-valid owner acceptance candidate.
- [x] Keep the production request file unchanged.
- [ ] Pass exact-head ownership, evidence-contract and ordinary CI gates.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-28T22:18:37+02:00
head: 0251bc1e460966ce0eb238d34f0d11a6db3b1462
branch: fix/rtec-owner-request-dry-run-gate-20260726
pr: 972
status: validating
context_routes:
  - agent-governance
  - real-tibia-parity
  - ci-repair
owned_paths:
  - docs/agents/tasks/active/CAN-20260726-rtec-owner-request-dry-run-gate.md
  - .github/workflows/real-tibia-evidence.yml
proven:
  - PR 972 is open, mergeable and targets blakinio/canary main from the dedicated task branch at implementation head 0251bc1e460966ce0eb238d34f0d11a6db3b1462
  - the PR changed-file set contains only the active task record and .github/workflows/real-tibia-evidence.yml
  - CI run 30216236618 passed on implementation head 0251bc1e460966ce0eb238d34f0d11a6db3b1462
  - Real Tibia Evidence Contracts run 30216236462 passed on implementation head 0251bc1e460966ce0eb238d34f0d11a6db3b1462
  - Agent Task Ownership run 30216236513 failed only in Validate changed active task checkpoints
  - ownership artifact active-task-ownership from run 30216236513 reports missing checkpoint field derived
  - the workflow uses a non-writing accepted-by-owner candidate and the production vocations request remains outside changed paths
derived:
  - the current failing surface is the checkpoint schema rather than the bounded workflow behavior because CI and Evidence Contracts passed while Ownership rejected the task record
  - only a checkpoint repair and renewed exact-head gate are required before merge evaluation
unknown:
  - renewed exact-head GitHub check conclusions after the checkpoint-only commit
conflicts: []
first_failure:
  marker: checkpoint-field-derived-missing
  evidence: Agent Task Ownership run 30216236513 artifact active-task-ownership reports missing checkpoint field derived
rejected_hypotheses:
  - the production request must be mutated: it is outside changed paths and the workflow candidate is non-writing
  - the workflow implementation is the current failing surface: CI and Real Tibia Evidence Contracts passed on the implementation head
changed_paths:
  - docs/agents/tasks/active/CAN-20260726-rtec-owner-request-dry-run-gate.md
  - .github/workflows/real-tibia-evidence.yml
validation:
  - command: GitHub CI run 30216236618
    result: PASS
    evidence: completed success on implementation head 0251bc1e460966ce0eb238d34f0d11a6db3b1462
  - command: Real Tibia Evidence Contracts run 30216236462
    result: PASS
    evidence: completed success on implementation head 0251bc1e460966ce0eb238d34f0d11a6db3b1462
  - command: Agent Task Ownership run 30216236513
    result: FAIL
    evidence: checkpoint validator rejected missing required field derived
blockers:
  - renewed exact-head required checks are not yet verified after this checkpoint-only commit
next_action: Verify exact-head checks for PR 972 after this checkpoint commit and, if every required check passes, mark ready and squash-merge.
```
