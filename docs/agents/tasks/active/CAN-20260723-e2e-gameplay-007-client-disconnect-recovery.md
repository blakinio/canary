---
task_id: CAN-20260723-e2e-gameplay-007-client-disconnect-recovery
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-GAMEPLAY-007-FAULT-RECOVERY
status: ready
agent: "GPT-5.6 Thinking"
branch: feat/e2e-gameplay-007-client-disconnect-recovery
base_branch: main
created: 2026-07-23
updated: 2026-07-23
last_verified_commit: "d4b6090134491a857859749563f71e1281dbf120"
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
- [x] Pass pre-final exact-head Ownership, CI and Universal Physical E2E.
- [ ] Pass immutable exact-final-head gates after this checkpoint commit, then merge, register shared docs and archive lifecycle before E2E-GAMEPLAY-008.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-23T10:15:00+02:00
head: d4b6090134491a857859749563f71e1281dbf120
branch: feat/e2e-gameplay-007-client-disconnect-recovery
pr: 748
status: ready
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
  - PR 748 changed scope before the final checkpoint is exactly the active task record, one controlled-client automation, one recovery scenario manifest and one focused contract test.
  - The new automation preserves the existing two-login/two-packet-record evidence shape while marking the planned fault, expected disconnect, observed disconnect, expected-injected-failure classification, recovered login/online state and safe cleanup distinctly.
  - The recovery scenario uses only literal loopback, the existing @test1 fixture and password_env; no arbitrary command, database interruption or external target surface was added.
  - Agent Task Ownership run 29988871999 passed on exact pre-final head d4b6090134491a857859749563f71e1281dbf120.
  - CI run 29988872166 and autofix run 29988872033 passed on exact pre-final head d4b6090134491a857859749563f71e1281dbf120.
  - Universal Agent E2E run 29988872128 passed on exact pre-final head d4b6090134491a857859749563f71e1281dbf120; physical job 89151205713 proved the explicit client forceLogout disconnect, expected-failure classification, real second-session recovery and clean safe logout, and Required physical E2E completed successfully.
  - The earlier cancelled runs 29988717489, 29988737289 and 29988737243 were concurrency-only evidence and were superseded by the clean successful validation attempt.
derived:
  - The bounded client-disconnect recovery contract is physically proven on the pre-final feature head; the ci:final-gate label was applied before this final checkpoint commit so the immutable final head must now rerun the full required matrix.
unknown:
  - Exact-final-head Ownership, CI, autofix and Universal Agent E2E outcome after this checkpoint commit.
  - Shared MODULE_CATALOG and CHANGELOG registration plus lifecycle archive remain narrow governance follow-ups after feature merge.
conflicts: []
first_failure:
  marker: none
  evidence: No unresolved implementation or validation failure remains; the initial workflow-concurrency cancellations were superseded by successful clean runs.
rejected_hypotheses:
  - Initial Required failures prove a recovery implementation defect: rejected because clean run 29988872128 physically passed the selected recovery scenario.
  - A database or server crash seam is required for the first 007 recovery proof: rejected because the architecture permits a safe explicit client-side fault seam and the real-client recovery boundary is now physically proven.
changed_paths:
  - docs/agents/tasks/active/CAN-20260723-e2e-gameplay-007-client-disconnect-recovery.md
  - tools/e2e/client/agent_e2e_fault_recovery.lua
  - tests/e2e/scenarios/recovery/client-disconnect-recovery.json
  - tests/e2e/test_client_disconnect_recovery.py
validation:
  - command: Agent Task Ownership run 29988871999
    result: PASS
    evidence: Ownership and active task checkpoint validation passed on exact pre-final head d4b6090134491a857859749563f71e1281dbf120.
  - command: CI run 29988872166 and autofix run 29988872033
    result: PASS
    evidence: Repository checks and formatting passed on exact pre-final head.
  - command: Universal Agent E2E run 29988872128 / physical job 89151205713 / Required physical E2E
    result: PASS
    evidence: The real controlled OTClient completed the injected client disconnect, expected-failure classification, second-session recovery and clean safe logout with the existing evidence lifecycle.
blockers: []
next_action: Require exact-final-head Ownership, CI and Universal Agent E2E on this final checkpoint commit; if green, audit reviews and exact four-file scope, squash-merge PR 748, register 006/007 shared docs, archive both completed task records, then start E2E-GAMEPLAY-008 from fresh main.
```
