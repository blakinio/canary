---
task_id: CAN-20260726-rtec-owner-request-dry-run-gate
program_id: CAN-PROGRAM-REAL-TIBIA-EVIDENCE-COLLECTION
coordination_id: RTEC-005-OWNER-REQUEST-DRY-RUN-GATE
status: review
agent: "GPT-5.6 Thinking"
branch: fix/rtec-owner-request-dry-run-gate-20260726
base_branch: main
created: 2026-07-26T20:55:00+02:00
updated: 2026-07-28T22:27:12+02:00
last_verified_commit: "48bbe5a6c4900906569f65a75542d34c336d0ae5"
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
- [x] Pass exact-head ownership, evidence-contract and ordinary CI gates.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-28T22:27:12+02:00
head: 48bbe5a6c4900906569f65a75542d34c336d0ae5
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
  - PR 972 is open, mergeable and targets blakinio/canary main from the dedicated task branch at head 48bbe5a6c4900906569f65a75542d34c336d0ae5
  - the PR changed-file set contains only the active task record and .github/workflows/real-tibia-evidence.yml
  - Agent Task Ownership run 30395908867 passed on head 48bbe5a6c4900906569f65a75542d34c336d0ae5, including changed checkpoint validation
  - Real Tibia Evidence Contracts run 30395908924 passed on head 48bbe5a6c4900906569f65a75542d34c336d0ae5, including the non-mutating production-request dry-run
  - CI run 30395909042 passed on head 48bbe5a6c4900906569f65a75542d34c336d0ae5 with Required successful and checkpoint-only heavy validation reused from the successful immediate parent
  - autofix.ci run 30395908883 passed on head 48bbe5a6c4900906569f65a75542d34c336d0ae5 without applying formatting changes
  - the workflow uses a non-writing accepted-by-owner candidate and the production vocations request remains outside changed paths
  - PR 972 has no submitted reviews or unresolved review threads
  - label ci:final-gate was applied before this final checkpoint-only commit
derived:
  - the bounded workflow repair and all acceptance criteria are satisfied on verified implementation head 48bbe5a6c4900906569f65a75542d34c336d0ae5
  - only renewed final-gate checks on this checkpoint-only commit and squash merge remain
unknown:
  - exact-head final-gate conclusions for the checkpoint-only commit created by this update
conflicts: []
first_failure:
  marker: none
  evidence: all exact-head ownership, evidence-contract, ordinary CI and formatting workflows passed on verified implementation head 48bbe5a6c4900906569f65a75542d34c336d0ae5
rejected_hypotheses: []
changed_paths:
  - docs/agents/tasks/active/CAN-20260726-rtec-owner-request-dry-run-gate.md
  - .github/workflows/real-tibia-evidence.yml
validation:
  - command: GitHub Agent Task Ownership run 30395908867
    result: PASS
    evidence: completed success on verified implementation head 48bbe5a6c4900906569f65a75542d34c336d0ae5
  - command: GitHub Real Tibia Evidence Contracts run 30395908924
    result: PASS
    evidence: completed success on verified implementation head 48bbe5a6c4900906569f65a75542d34c336d0ae5
  - command: GitHub CI run 30395909042
    result: PASS
    evidence: Required completed successfully on verified implementation head 48bbe5a6c4900906569f65a75542d34c336d0ae5
  - command: GitHub autofix.ci run 30395908883
    result: PASS
    evidence: formatting completed successfully without an autofix commit on verified implementation head 48bbe5a6c4900906569f65a75542d34c336d0ae5
blockers: []
next_action: Verify all final-gate checks on the checkpoint-only commit created by this update and squash-merge PR 972 if they pass.
```
