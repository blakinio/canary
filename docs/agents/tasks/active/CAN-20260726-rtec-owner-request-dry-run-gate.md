---
task_id: CAN-20260726-rtec-owner-request-dry-run-gate
program_id: CAN-PROGRAM-REAL-TIBIA-EVIDENCE-COLLECTION
coordination_id: RTEC-005-OWNER-REQUEST-DRY-RUN-GATE
status: implementing
agent: "GPT-5.6 Thinking"
branch: fix/rtec-owner-request-dry-run-gate-20260726
base_branch: main
created: 2026-07-26T20:55:00+02:00
updated: 2026-07-26T21:12:00+02:00
last_verified_commit: "02a58848cf3f608516b164c4352c2b0416df84da"
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
updated_at: 2026-07-26T21:12:00+02:00
head: 02a58848cf3f608516b164c4352c2b0416df84da
branch: fix/rtec-owner-request-dry-run-gate-20260726
pr: 972
status: implementing
context_routes:
  - agent-governance
  - real-tibia-parity
  - ci-repair
owned_paths:
  - docs/agents/tasks/active/CAN-20260726-rtec-owner-request-dry-run-gate.md
  - .github/workflows/real-tibia-evidence.yml
proven:
  - worker PRs 957 and 958 pass corpus validation and deterministic index checks
  - both fail only at the owner-request dry-run step
  - rejecting the still-referenced request correctly violates corpus integrity
  - workflow now constructs a non-writing accepted-by-owner candidate with required owner provenance
  - the production request remains outside changed paths
unknown:
  - exact-head workflow results after this checkpoint update
conflicts: []
first_failure:
  marker: checkpoint-changed-paths-incomplete
  evidence: initial ownership run 30216188951 found the checkpoint omitted the changed workflow path
rejected_hypotheses:
  - mutate the production request
  - weaken lifecycle validation
  - suppress the failing workflow step
changed_paths:
  - docs/agents/tasks/active/CAN-20260726-rtec-owner-request-dry-run-gate.md
  - .github/workflows/real-tibia-evidence.yml
validation:
  - command: Agent Task Ownership
    result: FAIL
    evidence: run 30216188951 rejected the incomplete initial checkpoint before task correction
blockers: []
next_action: Run renewed exact-head ownership, evidence-contract and ordinary CI gates, then merge PR 972 and refresh workers 957 and 958.
```
