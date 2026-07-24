---
task_id: CAN-20260724-e2e-qri-006-cleanup-certification
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-QRI-006
status: implementing
agent: "GPT-5.6 Thinking"
branch: fix/e2e-qri-006-client-event-paths
base_branch: main
created: 2026-07-24
updated: 2026-07-24
last_verified_commit: "6ad2172eb8e4d5a9fcda0d69f2b6c88906082bfb"
risk: medium
related_issue: ""
related_pr: "875"
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
    - tools/e2e/client/agent_e2e.lua
  shared:
    - tools/e2e/run_physical_e2e.sh
  - tools/e2e/client/agent_e2e.lua
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
  - exact runner-owned PID files, dedicated process group, exit evidence and fixed disposable MariaDB authority
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
- After the lifecycle trap completes, terminate only residual members of that exact runner-owned process group with bounded TERM/KILL escalation and certify group emptiness.
- Certify exact recorded process/PID cleanup, disposable database session/transaction state, fixture ghost-session absence, workspace restoration, temporary marker removal and explicit workflow-owned service handoff.
- Emit `canary-universal-e2e-cleanup-certification-v1` in `cleanup-certification.json` and integrate the same evidence into QRI-005 `cleanup_summary` and the orthogonal cleanup quality dimension.
- Preserve gameplay status, failure classification, attempt history and all earlier QRI-005 evidence.
- Add focused deterministic, invalid-PID, residual-process, multi-client, database, workspace, fault-marker, process-group reaping and envelope-integration tests.
- Physically validate through the existing `login/relog` scenario and existing artifact upload.

## Non-goals

- No process discovery or termination by executable/name/substring.
- No caller-selected PID, process group, command, SQL, host, table or target surface.
- No production/staging cleanup, container lifecycle ownership or external service shutdown.
- No second E2E runner, workflow, artifact or result-envelope implementation.
- No gameplay maturity or non-cleanup quality-dimension promotion.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-24T13:05:00+02:00
head: 4a6d7c418f3dead8616862476971a2a8ee23e606
branch: fix/e2e-qri-006-client-event-paths
pr: 875
status: implementing
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
  - Versioned cleanup certifier and focused process, database, workspace, marker, multi-client, gameplay-independence and result-envelope tests are committed.
  - The canonical wrapper captures a logical-path pre-run baseline, executes the unchanged lifecycle in a dedicated process group, invokes the certifier after its trap, and finalizes the same schema-v3 result.json.
  - The QRI-005 shim consumes only the exact cleanup contract/schema, promotes only the cleanup quality dimension and retains gameplay status.
  - Local focused cleanup suite passes 15 tests; certifier/shim py_compile and wrapper bash syntax pass.
  - Exact-head CI run 30085762248 and Agent Task Ownership run 30085762141 passed at b4555cc1f0283dd2c180dcd699224d8aef511b2d.
  - Physical run 30085762318 proved gameplay success, client exit zero, two login sessions, persistence, zero players_online, zero active transactions, restored workspace and 17 of 18 required cleanup checks.
  - The only physical cleanup failure was runner_process_group_empty with residual PID 4872 in dedicated PGID 4780; all recorded primary client, Canary wrapper, Xvfb and tcpdump PIDs were stopped.
  - The certifier now reaps only residual members of the exact dedicated PGID with bounded SIGTERM then SIGKILL escalation and records members_before, signals, members_after and errors.
  - Exact-head Universal Agent E2E run 30088384760 passed on 49b6d190eaa15353d2220c2b5f5f18246ebaa982; cleanup contract schema 1 reported certified=true with 18/18 required checks, gameplay success, PGID 4839 member 4911 reaped by SIGTERM, no remaining members, no warnings and no unknowns.
  - Artifact 8595225850 has digest sha256:6a188e536610fa420d3e1ed7c41cfefd8f88a93dca2bd980b0d833cc73161a6d and the schema-v3 envelope reports execution_tier=pr-required and quality_dimensions.cleanup=pass.
  - Delivery PR 871 merged as 6ad2172eb8e4d5a9fcda0d69f2b6c88906082bfb after exact-head gates; post-merge artifact 8597198699 proved cleanup 18/18 but exposed absolute packet_record_1/2 values only in raw client-events.tsv, so PR 875 keeps the full loginWorld path while emitting only session-N.record events.
  - Cleanup baseline evidence now stores only logical repo/otclient roots and relative paths, not absolute runner paths.
  - Branch is synchronized with main commit 13ec3077babba0ac81bb1e30e79f0ea4827ae2fe through merge commit 8cd80cd92b3c5a904f3bfea910328ca828604a3a.
derived:
  - A post-trap certifier with an exact-PGID reaper is the smallest safe seam that can independently evaluate and complete runner-owned cleanup after gameplay-success and gameplay-failure runs.
  - Dedicated process-group ownership permits bounded cleanup of untracked descendants without scanning or killing unrelated host processes.
  - Database queries remain fixed code-owned statements against the disposable E2E schema and manifest-declared fixture identities.
unknown:
  - Raw client-events.tsv basename hardening is not physically re-proven until the follow-up login/relog artifact is inspected.
conflicts: []
first_failure:
  marker: runner_process_group_empty
  evidence: Physical run 30085762318 retained PID 4872 in dedicated PGID 4780 after the existing lifecycle trap; gameplay status was success and all other 17 required cleanup checks passed.
  resolution: Exact-PGID bounded reaping was added and physical run 30088384760 proved 18/18 cleanup checks with no remaining members.
rejected_hypotheses:
  - Treat the existing teardown trap as certification without independent post-trap evidence.
  - Kill residual processes by name, executable scan or host-wide process matching.
  - Modify the shared lifecycle when exact dedicated-PGID ownership can safely close residual descendants in the QRI-006 certifier.
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
    evidence: 15 cleanup tests; certifier/shim syntax; canonical wrapper syntax.
  - command: exact-head CI and Agent Task Ownership at b4555cc1f0283dd2c180dcd699224d8aef511b2d
    result: PASS
    evidence: CI 30085762248; ownership 30085762141.
  - command: Universal Agent E2E at b4555cc1f0283dd2c180dcd699224d8aef511b2d
    result: FAIL
    evidence: run 30085762318; gameplay success and 17/18 cleanup checks, residual dedicated-group PID 4872.
blockers: []
next_action: Run exact-head ownership, CI and physical login/relog; inspect raw client-events.tsv for zero absolute runner paths; merge the hardening PR and archive QRI-006.
```
