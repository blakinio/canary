---
task_id: CAN-20260724-e2e-qri-005-result-envelope
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-QRI-005
status: review
agent: "GPT-5.6 Thinking"
branch: feat/e2e-qri-005-result-envelope
base_branch: main
created: 2026-07-24
updated: 2026-07-24
last_verified_commit: "cc074e7001324c2ad55e4d549f2cb7c43118cfa7"
risk: medium
related_issue: ""
related_pr: "850"
depends_on:
  - canonical Universal Physical E2E lifecycle
  - merged E2E-QRI-001, E2E-QRI-002 and E2E-QRI-003 physical consumers
blocks:
  - E2E-QRI-006
owned_paths:
  exclusive:
    - tools/e2e/result_envelope.py
    - tools/e2e/result_envelope_impl.py
    - tests/e2e/test_result_envelope.py
    - docs/agents/tasks/active/CAN-20260724-e2e-qri-005-result-envelope.md
  shared:
    - tools/e2e/run_physical_e2e.sh
    - tools/e2e/run_physical_e2e_lifecycle.sh
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
  - existing canonical physical lifecycle and teardown behavior
public_interfaces:
  - canary-universal-e2e-result-envelope-v1
cross_repo_tasks: []
---

# CAN-20260724 — E2E-QRI-005 result envelope

## Goal

Deliver one stable, versioned, machine-readable Universal E2E result envelope with deterministic serialization, richer first-failure evidence, explicit unknowns, preserved attempt history and compatibility with the existing `result.json` artifact.

## Scope

- Add one canonical Python result-envelope entrypoint plus a private implementation module under `tools/e2e`.
- Preserve current top-level legacy fields as a compatibility superset while adding the versioned contract.
- Normalize successful, assertion-failing and bootstrap/infrastructure failing physical runs after the canonical lifecycle completes.
- Keep `tools/e2e/run_physical_e2e.sh` as the only canonical entrypoint; the prior script body is retained byte-for-byte as the internal lifecycle implementation and the entrypoint performs only contract tests and result finalization.
- Use one existing physical scenario as the first real consumer without creating another workflow or alternative orchestration.
- Add focused contract, validation, sanitization, deterministic serialization, first-failure and multiple-attempt tests.

## Non-goals

- No QRI-006 cleanup certification claim.
- No maturity promotion beyond the scenario's existing M0-M5 evidence.
- No new workflow, independent runner, artifact system, arbitrary command surface or production fault interface.
- No migration of every historical artifact producer in this package.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-24T07:00:00Z
head: cc074e7001324c2ad55e4d549f2cb7c43118cfa7
branch: feat/e2e-qri-005-result-envelope
pr: 850
status: final-gate
context_routes:
  - agent-governance
  - universal-e2e
owned_paths:
  - tools/e2e/result_envelope.py
  - tools/e2e/result_envelope_impl.py
  - tests/e2e/test_result_envelope.py
  - tools/e2e/run_physical_e2e.sh
  - tools/e2e/run_physical_e2e_lifecycle.sh
  - docs/agents/tasks/active/CAN-20260724-e2e-qri-005-result-envelope.md
proven:
  - Fresh preflight found no open QRI pull request or active QRI-005/QRI-006 implementation before PR 850.
  - Open PR 841 does not modify the canonical Universal E2E runner or shared result contract.
  - The pre-QRI physical result.json used schema_version 2 for evaluated runs and schema_version 1 for bootstrap failures.
  - Restart recovery augments the same result.json with restart_evidence after base evaluation.
  - canary-universal-e2e-result-envelope-v1 implementation and focused unit tests are committed.
  - The canonical entrypoint executes focused contract tests and finalizes the same result.json after the unchanged physical lifecycle exits.
  - First physical attempt 30070070463 failed before gameplay because focused tests exposed an IndexError when optional map.sha256 evidence was absent.
  - The empty map identity path now returns sha256 null instead of indexing an empty token list.
  - Exact-head CI, Agent Task Ownership and Universal Agent E2E run 30072005495 passed at cc074e7001324c2ad55e4d549f2cb7c43118cfa7.
  - Physical login/relog result.json uses schema_version 3, contract canary-universal-e2e-result-envelope-v1 and status success.
  - Physical artifact universal-agent-e2e-login-relog has digest sha256:28b028874be14a88f05e532dcdbbfe3e3a34bf008ee71e7d9c03433d5a09f4bd.
  - cleanup_summary remains status not-certified with cleanup_certified false and an explicit QRI-006 unknown.
  - Current main changes since the merge base do not overlap the six implementation paths and PR 850 is mergeable.
derived:
  - Post-lifecycle finalization is the smallest seam that observes normal, bootstrap and scenario-specific augmented results without adding a second result path.
  - The first failure was a test-contract defect, not gameplay, server startup or client startup evidence.
  - QRI-006 may safely consume the explicit cleanup_summary boundary only after QRI-005 delivery and lifecycle closure.
unknown:
  - Final-head workflow outcomes for the checkpoint commit created after applying ci:final-gate.
conflicts: []
first_failure:
  marker: result-envelope-contract-tests.map-identity-empty
  evidence: workflow 30070070463 artifact universal-agent-e2e-login-relog/result-envelope-contract-tests.log
rejected_hypotheses:
  - A second workflow is required: the existing artifact upload consumes the canonical result.json.
  - Result generation can happen only in the success evaluator: that would omit bootstrap and infrastructure failures.
  - The first failed physical attempt proves a gameplay regression: no physical client step ran because the focused contract tests failed first.
changed_paths:
  - docs/agents/tasks/active/CAN-20260724-e2e-qri-005-result-envelope.md
  - tests/e2e/test_result_envelope.py
  - tools/e2e/result_envelope.py
  - tools/e2e/result_envelope_impl.py
  - tools/e2e/run_physical_e2e.sh
  - tools/e2e/run_physical_e2e_lifecycle.sh
validation:
  - command: live GitHub preflight and exact changed-path audit
    result: PASS
    evidence: PR 850 and main/open-PR audit
  - command: CI / Agent Task Ownership / Universal Agent E2E at 20909292263db26df73c8ff9bd4697527b8c99e6
    result: FAIL
    evidence: CI and ownership passed; physical run 30070070463 failed at focused contract tests with absent map.sha256 IndexError
  - command: CI / Agent Task Ownership / Universal Agent E2E at cc074e7001324c2ad55e4d549f2cb7c43118cfa7
    result: PASS
    evidence: workflow runs 30072005498, 30072005323 and 30072005495; physical artifact digest sha256:28b028874be14a88f05e532dcdbbfe3e3a34bf008ee71e7d9c03433d5a09f4bd
blockers:
  - Local sandbox cannot resolve github.com, so repository CI provides authoritative full integration and physical validation.
next_action: Wait for exact final-head checks triggered by this ci:final-gate commit; make no further implementation commit, then mark ready and squash-merge if all gates remain green.
```