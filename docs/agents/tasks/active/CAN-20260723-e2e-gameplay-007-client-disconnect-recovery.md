---
task_id: CAN-20260723-e2e-gameplay-007-client-disconnect-recovery
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-GAMEPLAY-007-FAULT-RECOVERY
status: implementing
agent: "GPT-5.6 Thinking"
branch: feat/e2e-gameplay-007-client-disconnect-recovery
base_branch: main
created: 2026-07-23
updated: 2026-07-23
last_verified_commit: "3e8090e8e03bf170a179cac04d9a4960f59a7e7d"
risk: medium
related_issue: ""
related_pr: "748"
depends_on:
  - stable Universal Physical E2E two-session lifecycle
  - explicit controlled-client forceLogout seam
blocks:
  - E2E-GAMEPLAY-008 representative cross-system journeys
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260723-e2e-gameplay-007-client-disconnect-recovery.md
    - tools/e2e/client/agent_e2e_fault_recovery.lua
    - tests/e2e/scenarios/recovery/client-disconnect-recovery.json
    - tests/e2e/test_client_disconnect_recovery.py
  shared:
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - tools/e2e/run_physical_e2e.sh
    - tools/e2e/run_agent_e2e.py
    - .github/workflows/universal-agent-e2e.yml
modules_touched:
  - Universal E2E controlled client disconnect/recovery
reuses:
  - existing disposable Canary/MariaDB/controlled-OTClient lifecycle
  - existing two packet-record evaluation and cleanup evidence
  - maintained OTClient g_game.forceLogout and loginWorld surfaces
public_interfaces:
  - canary-universal-e2e-client-disconnect-recovery-v1
cross_repo_tasks: []
---

# CAN-20260723 — E2E-GAMEPLAY-007 client disconnect recovery

## Goal

Prove one explicit, reproducible controlled-client disconnect and recovery flow inside the existing Universal Physical E2E environment without adding a second orchestrator, arbitrary manifest commands, external targets, or database fault injection.

## Acceptance criteria

- [x] Reuse the existing disposable Canary/MariaDB/controlled-OTClient lifecycle and workflow.
- [x] Inject exactly one explicit client-side transport fault through maintained `g_game.forceLogout()` after stable world entry.
- [x] Distinguish the expected injected disconnect from an unexpected platform failure in machine-readable markers.
- [x] Recover with a second real-client login, then perform a canonical safe logout and leave no connected test player.
- [x] Retain two packet records, two server logins, SQL persistence evidence, logs and final result artifacts.
- [x] Add focused contract tests.
- [ ] Pass exact-final-head Ownership, CI and Universal Physical E2E.
- [ ] Merge, register shared docs, archive lifecycle, then start E2E-GAMEPLAY-008.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-23T09:50:00+02:00
head: 3e8090e8e03bf170a179cac04d9a4960f59a7e7d
branch: feat/e2e-gameplay-007-client-disconnect-recovery
pr: 748
status: validating
context_routes:
  - universal-e2e
  - agent-governance
  - cpp-runtime
owned_paths:
  - docs/agents/tasks/active/CAN-20260723-e2e-gameplay-007-client-disconnect-recovery.md
  - tools/e2e/client/agent_e2e_fault_recovery.lua
  - tests/e2e/scenarios/recovery/client-disconnect-recovery.json
  - tests/e2e/test_client_disconnect_recovery.py
proven:
  - PR 747 merged E2E-GAMEPLAY-006 to main as 4f074077da44d1cc9d77db7ac768be0589313332 with final CI, Ownership and Universal Agent E2E success.
  - The Universal Physical E2E final evaluator requires two server logins and two packet records; the implemented first-session injected client disconnect followed by one recovered session and safe logout preserves that evidence shape without runner or workflow changes.
  - PR 748 changed scope is bounded to the active task record, one controlled-client automation, one recovery scenario manifest and one focused contract test; an accidentally created noop file was removed before PR creation and is absent from the net diff.
  - The new automation marks planned fault, expected disconnect, observed disconnect, expected-injected-failure classification, recovered login/online state and safe cleanup distinctly.
  - The recovery scenario uses only literal loopback, the existing @test1 fixture and password_env; no arbitrary command, database interruption or external target surface was added.
derived:
  - The implementation is ready for repository CI and physical validation; successful physical execution must still prove that maintained g_game.forceLogout produces the expected onGameEnd recovery transition in this runtime.
unknown:
  - Exact physical outcome of the new recovery scenario.
  - Exact-head Ownership and CI outcome on PR 748.
conflicts: []
first_failure:
  marker: none
  evidence: No implementation or validation failure has occurred on this task yet.
rejected_hypotheses:
  - Inject database interruption in the first 007 slice: rejected because the architecture requires a safe isolated seam and the client-disconnect seam proves recovery with materially lower risk.
changed_paths:
  - docs/agents/tasks/active/CAN-20260723-e2e-gameplay-007-client-disconnect-recovery.md
  - tools/e2e/client/agent_e2e_fault_recovery.lua
  - tests/e2e/scenarios/recovery/client-disconnect-recovery.json
  - tests/e2e/test_client_disconnect_recovery.py
validation:
  - command: PR 748 creation and exact changed-file scope review
    result: PASS
    evidence: Draft PR 748 targets blakinio/canary:main from the dedicated same-repository task branch with four net changed files.
blockers: []
next_action: Inspect PR 748 Ownership, CI and Universal Agent E2E results on the current head and fix the first evidence-backed failure if any.
```
