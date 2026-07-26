---
task_id: CAN-20260726-rtec-owner-request-dry-run-gate
program_id: CAN-PROGRAM-REAL-TIBIA-EVIDENCE-COLLECTION
coordination_id: RTEC-005-OWNER-REQUEST-DRY-RUN-GATE
status: implementing
agent: "GPT-5.6 Thinking"
branch: fix/rtec-owner-request-dry-run-gate-20260726
base_branch: main
created: 2026-07-26T20:55:00+02:00
updated: 2026-07-26T20:55:00+02:00
last_verified_commit: "191d628259c05048cae3c9b9a0a9b233de6294f4"
risk: low
related_issue: ""
related_pr: ""
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

- [ ] Replace the invalid dry-run rejection with a corpus-valid owner acceptance candidate.
- [ ] Keep the production request file unchanged.
- [ ] Pass exact-head ownership, evidence-contract and ordinary CI gates.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-26T20:55:00+02:00
head: 191d628259c05048cae3c9b9a0a9b233de6294f4
branch: fix/rtec-owner-request-dry-run-gate-20260726
pr: null
status: implementing
context_routes:
  - agent-governance
  - real-tibia-parity
owned_paths:
  - docs/agents/tasks/active/CAN-20260726-rtec-owner-request-dry-run-gate.md
  - .github/workflows/real-tibia-evidence.yml
proven:
  - worker PRs 957 and 958 pass corpus validation and deterministic index checks
  - both fail only at the owner-request dry-run step
  - rejecting the still-referenced request correctly violates corpus integrity
unknown: []
conflicts: []
first_failure:
  marker: owner-request-dry-run-invalid-candidate
  evidence: the workflow constructs a rejected candidate for an owner request still referenced by accepted evidence
changed_paths:
  - docs/agents/tasks/active/CAN-20260726-rtec-owner-request-dry-run-gate.md
validation: []
blockers: []
next_action: Update the workflow to exercise a corpus-valid non-writing transition and run exact-head gates.
```
