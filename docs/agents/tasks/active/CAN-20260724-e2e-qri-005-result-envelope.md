---
task_id: CAN-20260724-e2e-qri-005-result-envelope
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-QRI-005
status: active
agent: "GPT-5.6 Thinking"
branch: feat/e2e-qri-005-result-envelope
base_branch: main
created: 2026-07-24
updated: 2026-07-24
last_verified_commit: "332e47da1b1d8fb0d98fa4cf1e6698acb26f8e05"
risk: medium
related_issue: ""
related_pr: ""
depends_on:
  - canonical Universal Physical E2E lifecycle
  - merged E2E-QRI-001, E2E-QRI-002 and E2E-QRI-003 physical consumers
blocks:
  - E2E-QRI-006
owned_paths:
  exclusive:
    - tools/e2e/result_envelope.py
    - tests/e2e/test_result_envelope.py
    - docs/agents/tasks/active/CAN-20260724-e2e-qri-005-result-envelope.md
  shared:
    - tools/e2e/run_physical_e2e.sh
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/programs/E2E_AUTOMATION_PROGRAM.md
    - docs/agents/CHANGELOG.md
  read_only:
    - .github/workflows/universal-agent-e2e.yml
    - tools/e2e/disposable_canary_restart.sh
    - tools/e2e/multi_client_orchestration.py
    - tests/e2e/scenarios/**
modules_touched:
  - Universal E2E machine-readable result envelope
reuses:
  - existing result.json artifact path and Universal Agent E2E artifact upload
  - existing scenario manifest, client events, SQL assertion evidence and restart recovery evidence
  - existing canonical physical lifecycle and cleanup trap
public_interfaces:
  - canary-universal-e2e-result-envelope-v1
cross_repo_tasks: []
---

# CAN-20260724 — E2E-QRI-005 result envelope

## Goal

Deliver one stable, versioned, machine-readable Universal E2E result envelope with deterministic serialization, richer first-failure evidence, explicit unknowns, preserved attempt history and compatibility with the existing `result.json` artifact.

## Scope

- Add one Python result-envelope module under the canonical `tools/e2e` platform.
- Preserve current top-level legacy fields as a compatibility superset while adding the versioned contract.
- Normalize successful, assertion-failing and bootstrap/infrastructure failing physical runs through the canonical lifecycle trap.
- Use one existing physical scenario as the first real consumer without creating another runner or workflow.
- Add focused contract, validation, sanitization, deterministic serialization, first-failure and multiple-attempt tests.

## Non-goals

- No QRI-006 cleanup certification claim.
- No maturity promotion beyond the scenario's existing M0-M5 evidence.
- No new workflow, runner, artifact system, arbitrary command surface or production fault interface.
- No migration of every historical artifact producer in this package.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-24T05:30:00Z
head: 332e47da1b1d8fb0d98fa4cf1e6698acb26f8e05
branch: feat/e2e-qri-005-result-envelope
pr: none
status: implementing
context_routes:
  - agent-governance
  - universal-e2e
owned_paths:
  - tools/e2e/result_envelope.py
  - tests/e2e/test_result_envelope.py
  - tools/e2e/run_physical_e2e.sh
  - docs/agents/tasks/active/CAN-20260724-e2e-qri-005-result-envelope.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/programs/E2E_AUTOMATION_PROGRAM.md
  - docs/agents/CHANGELOG.md
proven:
  - main HEAD is 332e47da1b1d8fb0d98fa4cf1e6698acb26f8e05.
  - No open QRI pull request or active QRI-005/QRI-006 implementation was found.
  - Open PR 841 owns only its native-auth rehearsal workflow and tests and does not modify the canonical Universal E2E runner.
  - Current physical result.json uses schema_version 2 for evaluated runs and schema_version 1 for bootstrap failures.
  - Restart recovery augments the same result.json with restart_evidence after base evaluation.
derived:
  - The smallest shared seam is a dedicated result-envelope module invoked from the canonical runner cleanup trap after all scenario-specific augmenters have run or after bootstrap failure materialization.
unknown:
  - Exact current repository CI failures, if any, after the first implementation commit.
conflicts: []
first_failure:
  marker: none
  evidence: preflight only
rejected_hypotheses:
  - A second workflow is required: the existing result.json artifact and runner trap provide a sufficient integration seam.
changed_paths:
  - docs/agents/tasks/active/CAN-20260724-e2e-qri-005-result-envelope.md
validation:
  - command: live GitHub preflight
    result: PASS
    evidence: main 332e47da; open PR and changed-path audit
blockers:
  - Local sandbox cannot resolve github.com, so local full-repository build/runtime execution is unavailable; repository CI will provide authoritative integration and physical validation.
next_action: Implement tools/e2e/result_envelope.py with deterministic contract validation and focused unit tests.
```
