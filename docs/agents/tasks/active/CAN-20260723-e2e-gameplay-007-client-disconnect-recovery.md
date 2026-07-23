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
last_verified_commit: "06f506627b58f7e12d030cd852f44528e406dd13"
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
updated_at: 2026-07-23T09:58:00+02:00
head: 06f506627b58f7e12d030cd852f44528e406dd13
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
  - PR 748 changed scope is exactly the active task record, one controlled-client automation, one recovery scenario manifest and one focused contract test.
  - The new automation preserves the existing two-login/two-packet-record evidence shape while marking the planned fault, expected disconnect, observed disconnect, expected-injected-failure classification, recovered login/online state and safe cleanup distinctly.
  - The recovery scenario uses only literal loopback, the existing @test1 fixture and password_env; no arbitrary command, database interruption or external target surface was added.
  - Agent Task Ownership run 29988737172 passed on head 06f506627b58f7e12d030cd852f44528e406dd13.
  - CI runs 29988717489 and 29988737289 and Universal Agent E2E run 29988737243 were cancelled by overlapping PR synchronize/ready events; their Required aggregators failed only because prerequisite jobs were cancelled before validation completed.
derived:
  - The cancellation evidence is infrastructural/concurrency-related rather than an implementation failure; a single subsequent synchronize event should produce a clean validation attempt on the next checkpoint head.
unknown:
  - Exact physical outcome of the new recovery scenario.
  - CI and Universal Agent E2E outcome on the next non-overlapping validation attempt.
conflicts: []
first_failure:
  marker: workflow-concurrency-cancellation
  evidence: CI 29988717489/29988737289 and Universal Agent E2E 29988737243 had prerequisite jobs cancelled during overlapping PR events; no code/test assertion failure was observed.
rejected_hypotheses:
  - Initial Required failures prove a recovery implementation defect: rejected because the required prerequisite jobs were cancelled, while Ownership 29988737172 passed.
changed_paths:
  - docs/agents/tasks/active/CAN-20260723-e2e-gameplay-007-client-disconnect-recovery.md
  - tools/e2e/client/agent_e2e_fault_recovery.lua
  - tests/e2e/scenarios/recovery/client-disconnect-recovery.json
  - tests/e2e/test_client_disconnect_recovery.py
validation:
  - command: Agent Task Ownership run 29988737172
    result: PASS
    evidence: Active ownership, checkpoint validation and four-file task scope passed on head 06f506627b58f7e12d030cd852f44528e406dd13.
  - command: CI runs 29988717489 and 29988737289
    result: BLOCKED
    evidence: Overlapping PR events cancelled prerequisite jobs and caused secondary Required failures before meaningful CI completion.
  - command: Universal Agent E2E run 29988737243
    result: BLOCKED
    evidence: Physical prerequisite jobs were cancelled during overlapping PR events; no scenario failure executed.
blockers: []
next_action: Inspect the single synchronize-triggered Ownership, CI and Universal Agent E2E runs on this checkpoint commit and fix the first evidence-backed implementation failure if one appears.
```
