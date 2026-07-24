---
task_id: CAN-20260724-e2e-qri-006-cleanup-certification
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-QRI-006
status: review
agent: "GPT-5.6 Thinking"
branch: feat/e2e-qri-006-cleanup-certification
base_branch: main
created: 2026-07-24
updated: 2026-07-24
last_verified_commit: "b1d24ec362ec52652886f6be6129234ff44e7d4d"
risk: medium
related_issue: ""
related_pr: ""
depends_on:
  - merged and lifecycle-closed E2E-QRI-005 result envelope
  - canonical Universal Physical E2E lifecycle
blocks:
  - cleanup quality-dimension promotion in downstream E2E packages
owned_paths:
  exclusive:
    - tools/e2e/cleanup_certification.py
    - tests/e2e/test_cleanup_certification.py
    - docs/agents/tasks/active/CAN-20260724-e2e-qri-006-cleanup-certification.md
  shared:
    - tools/e2e/run_physical_e2e.sh
    - tools/e2e/result_envelope.py
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
    - docs/agents/programs/E2E_AUTOMATION_PROGRAM.md
  read_only:
    - tools/e2e/run_physical_e2e_lifecycle.sh
    - tools/e2e/result_envelope_impl.py
    - tools/e2e/multi_client_orchestration.py
    - tools/e2e/disposable_canary_restart.sh
    - .github/workflows/universal-agent-e2e.yml
    - tests/e2e/scenarios/**
modules_touched:
  - Universal E2E resource cleanup certification
reuses:
  - canary-universal-e2e-result-envelope-v1 schema version 3
  - canonical Universal Physical E2E wrapper, lifecycle and existing artifact upload
  - exact runner-owned PID files, exit evidence and fixed disposable MariaDB authority
public_interfaces:
  - canary-universal-e2e-cleanup-certification-v1
cross_repo_tasks: []
---

# CAN-20260724 — E2E-QRI-006 resource cleanup certification

## Goal

Deliver deterministic first-class cleanup certification after every canonical Universal Physical E2E lifecycle attempt, independent of gameplay success or failure, without introducing another runner, workflow, result path, arbitrary process surface or production target.

## Scope

- Capture a bounded pre-run workspace baseline for files the canonical lifecycle may temporarily replace.
- Run the unchanged lifecycle in one dedicated runner-owned process group.
- After the lifecycle trap completes, certify exact process/PID cleanup, process-group emptiness, disposable database session/transaction state, fixture ghost-session absence, workspace restoration, temporary marker removal and explicit workflow-owned service handoff.
- Emit `canary-universal-e2e-cleanup-certification-v1` in `cleanup-certification.json` and integrate the same evidence into QRI-005 `cleanup_summary` and the orthogonal cleanup quality dimension.
- Preserve gameplay status, failure classification, attempt history and all earlier QRI-005 evidence.
- Add focused deterministic, invalid-PID, residual-process, multi-client, database, workspace, fault-marker and envelope-integration tests.
- Physically validate through the existing `login/relog` scenario and existing artifact upload.

## Non-goals

- No process discovery or termination by executable/name/substring.
- No caller-selected PID, command, SQL, host, table or target surface.
- No production/staging cleanup, container lifecycle ownership or external service shutdown.
- No second E2E runner, workflow, artifact or result-envelope implementation.
- No gameplay maturity or non-cleanup quality-dimension promotion.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-24T10:05:00Z
head: b1d24ec362ec52652886f6be6129234ff44e7d4d
branch: feat/e2e-qri-006-cleanup-certification
pr: null
status: implementing
context_routes:
  - agent-governance
  - universal-e2e
owned_paths:
  - tools/e2e/cleanup_certification.py
  - tests/e2e/test_cleanup_certification.py
  - tools/e2e/run_physical_e2e.sh
  - tools/e2e/result_envelope.py
  - docs/agents/tasks/active/CAN-20260724-e2e-qri-006-cleanup-certification.md
proven:
  - QRI-005 delivery PR 850 merged as f28acc8e959e79448ea99dead2500a64460f3aff.
  - QRI-005 lifecycle closure PR 861 merged as cb5a22bb4319608a1b1c64b40dd274cac94e0002.
  - QRI-005 discovery registration PR 869 merged as b1d24ec362ec52652886f6be6129234ff44e7d4d.
  - Current main records cleanup_summary as not-certified and cleanup_certified false until QRI-006 evidence exists.
  - Existing lifecycle owns exact CLIENT_PID, CANARY_PID, XVFB_PID and TCPDUMP_PID values and bounded restoration through its trap.
  - Existing wrapper is the only public physical entrypoint and finalizes the same result.json after lifecycle completion.
  - Fresh open-PR and active-task search found no QRI-006 implementation owner.
derived:
  - A post-trap read-only certifier is the smallest seam that can independently evaluate both gameplay-success and gameplay-failure runs.
  - Dedicated process-group execution proves absence of untracked descendants without scanning or killing unrelated host processes.
  - Database queries must remain fixed code-owned statements against the disposable E2E schema and manifest-declared fixture identities.
unknown:
  - Exact first physical cleanup result on the GitHub runner.
  - Whether every existing optional secondary actor emits the expected exact PID and exit evidence names.
conflicts: []
first_failure:
  marker: none
  evidence: QRI-006 physical validation has not run.
rejected_hypotheses:
  - Treat the existing teardown trap as certification without independent post-trap evidence.
  - Kill residual processes by name, executable scan or host-wide process matching.
  - Mark cleanup certified merely because gameplay status is success or players_online is zero.
  - Add another workflow, runner or result artifact.
changed_paths:
  - docs/agents/tasks/active/CAN-20260724-e2e-qri-006-cleanup-certification.md
validation:
  - command: fresh main, open-PR and active-task preflight
    result: PASS
    evidence: QRI-005 is merged/archived/registered; no QRI-006 owner found.
blockers: []
next_action: Open the draft PR, implement the bounded certifier and focused tests, then run exact-head CI, ownership and Universal Physical E2E.
```
