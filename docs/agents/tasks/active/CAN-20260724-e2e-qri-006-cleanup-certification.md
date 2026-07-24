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
last_verified_commit: "0182ca6531e9639c73594f0426e2171aab392d58"
risk: medium
related_issue: ""
related_pr: "871"
depends_on:
  - merged and lifecycle-closed E2E-QRI-005 result envelope
  - canonical Universal Physical E2E lifecycle
blocks:
  - cleanup quality-dimension promotion in downstream E2E packages
owned_paths:
  exclusive:
    - tools/e2e/cleanup_certification.py
    - tests/e2e/test_cleanup_certification.py
    - tests/e2e/test_cleanup_result_envelope.py
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
updated_at: 2026-07-24T10:18:00Z
head: 0182ca6531e9639c73594f0426e2171aab392d58
branch: feat/e2e-qri-006-cleanup-certification
pr: 871
status: validating
context_routes:
  - agent-governance
  - universal-e2e
owned_paths:
  - tools/e2e/cleanup_certification.py
  - tests/e2e/test_cleanup_certification.py
  - tests/e2e/test_cleanup_result_envelope.py
  - tools/e2e/run_physical_e2e.sh
  - tools/e2e/result_envelope.py
  - docs/agents/tasks/active/CAN-20260724-e2e-qri-006-cleanup-certification.md
proven:
  - QRI-005 delivery PR 850 merged as f28acc8e959e79448ea99dead2500a64460f3aff.
  - QRI-005 lifecycle closure PR 861 merged as cb5a22bb4319608a1b1c64b40dd274cac94e0002.
  - QRI-005 discovery registration PR 869 merged as b1d24ec362ec52652886f6be6129234ff44e7d4d.
  - Fresh open-PR and active-task search found no prior QRI-006 implementation owner.
  - Versioned cleanup certifier and focused deterministic process, database, workspace, marker, multi-client and gameplay-independence tests are committed.
  - The canonical wrapper captures a pre-run baseline, executes the unchanged lifecycle in a dedicated process group, certifies after its trap, and finalizes the same schema-v3 result.json.
  - The QRI-005 shim consumes only the exact cleanup contract/schema, promotes only the cleanup quality dimension and retains gameplay status.
  - Local focused cleanup suite passed 13 tests; certifier/shim py_compile and wrapper bash syntax passed.
  - Exact-head CI run 30085549360 passed at 0182ca6531e9639c73594f0426e2171aab392d58.
derived:
  - A post-trap read-only certifier is the smallest seam that independently evaluates gameplay-success and gameplay-failure runs.
  - Dedicated process-group execution proves absence of in-group untracked descendants without scanning or killing unrelated host processes.
  - Database queries remain fixed code-owned statements against the disposable E2E schema and manifest-declared fixture identities.
unknown:
  - Exact first physical cleanup outcome from Universal Agent E2E run 30085549306.
  - Whether every optional secondary actor currently emits the exact PID and exit evidence paths required by the new contract.
conflicts: []
first_failure:
  marker: ownership.missing-exclusive-test-path
  evidence: Agent Task Ownership run 30085549088 did not include tests/e2e/test_cleanup_result_envelope.py in the task claim.
rejected_hypotheses:
  - Treat the existing teardown trap as certification without independent post-trap evidence.
  - Kill residual processes by name, executable scan or host-wide process matching.
  - Mark cleanup certified merely because gameplay status is success or players_online is zero.
  - Add another workflow, runner or result artifact.
changed_paths:
  - docs/agents/tasks/active/CAN-20260724-e2e-qri-006-cleanup-certification.md
  - tests/e2e/test_cleanup_certification.py
  - tests/e2e/test_cleanup_result_envelope.py
  - tools/e2e/cleanup_certification.py
  - tools/e2e/result_envelope.py
  - tools/e2e/run_physical_e2e.sh
validation:
  - command: fresh main, open-PR and active-task preflight
    result: PASS
    evidence: QRI-005 merged/archived/registered; no prior QRI-006 owner.
  - command: local focused cleanup contract suite plus py_compile and bash -n
    result: PASS
    evidence: 13 cleanup tests; certifier/shim syntax; canonical wrapper syntax.
  - command: exact-head CI at 0182ca6531e9639c73594f0426e2171aab392d58
    result: PASS
    evidence: run 30085549360.
  - command: Agent Task Ownership at 0182ca6531e9639c73594f0426e2171aab392d58
    result: FAIL
    evidence: run 30085549088; missing ownership declaration for the new envelope-integration test.
blockers: []
next_action: Re-run exact-head ownership and Universal Physical E2E after the ownership and focused-wrapper corrections, then inspect cleanup-certification.json and result.json.
```
