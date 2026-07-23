---
task_id: CAN-20260723-e2e-gameplay-007-client-disconnect-recovery
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-GAMEPLAY-007-FAULT-RECOVERY
status: ready
agent: "GPT-5.6 Thinking"
branch: feat/e2e-gameplay-007-client-disconnect-recovery-v2
base_branch: main
created: 2026-07-23
updated: 2026-07-23
last_verified_commit: "b0f83922a871ea9b6428dbbfad520c98f6d99c3d"
risk: medium
related_issue: ""
related_pr: "751"
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
- [ ] Pass immutable exact-final-head gates on successor PR #751, then merge, register shared docs and archive lifecycle before E2E-GAMEPLAY-008.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-23T10:20:00+02:00
head: b0f83922a871ea9b6428dbbfad520c98f6d99c3d
branch: feat/e2e-gameplay-007-client-disconnect-recovery-v2
pr: 751
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
  - Original PR 748 physically passed pre-final validation on head d4b6090134491a857859749563f71e1281dbf120 but its reported PR head failed to advance after final checkpoint commit b0f83922a871ea9b6428dbbfad520c98f6d99c3d, so it was closed unmerged rather than risking a stale-head merge.
  - Successor PR 751 starts exactly from b0f83922a871ea9b6428dbbfad520c98f6d99c3d and preserves the same exact four task-owned changed paths.
  - The new automation preserves the existing two-login/two-packet-record evidence shape while marking the planned fault, expected disconnect, observed disconnect, expected-injected-failure classification, recovered login/online state and safe cleanup distinctly.
  - The recovery scenario uses only literal loopback, the existing @test1 fixture and password_env; no arbitrary command, database interruption or external target surface was added.
  - Agent Task Ownership run 29988871999 passed on exact pre-final head d4b6090134491a857859749563f71e1281dbf120.
  - CI run 29988872166 and autofix run 29988872033 passed on exact pre-final head d4b6090134491a857859749563f71e1281dbf120.
  - Universal Agent E2E run 29988872128 passed on exact pre-final head d4b6090134491a857859749563f71e1281dbf120; physical job 89151205713 proved the explicit client forceLogout disconnect, expected-failure classification, real second-session recovery and clean safe logout, and Required physical E2E completed successfully.
derived:
  - The bounded client-disconnect recovery contract is physically proven on the predecessor feature head; successor PR 751 has ci:final-gate applied before this branch/PR checkpoint commit and must pass its own immutable exact-final-head matrix before merge.
unknown:
  - Exact-final-head Ownership, CI, autofix and Universal Agent E2E outcome on successor PR 751 after this checkpoint commit.
  - Shared MODULE_CATALOG and CHANGELOG registration plus lifecycle archive remain narrow governance follow-ups after feature merge.
conflicts: []
first_failure:
  marker: none
  evidence: No unresolved implementation or validation failure remains; stale PR metadata on PR 748 was handled by closing it unmerged and creating successor PR 751 from the exact final-checkpoint commit.
rejected_hypotheses:
  - Merge PR 748 despite its stale reported head: rejected because immutable exact-head merge evidence could not be trusted.
  - Initial Required failures prove a recovery implementation defect: rejected because clean run 29988872128 physically passed the selected recovery scenario.
  - A database or server crash seam is required for the first 007 recovery proof: rejected because the architecture permits a safe explicit client-side fault seam and the real-client recovery boundary is physically proven.
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
next_action: Mark successor PR 751 ready, require exact-final-head Ownership, CI and Universal Agent E2E on the resulting final checkpoint head; if green, audit reviews and exact four-file scope, squash-merge PR 751, register 006/007 shared docs, archive both completed task records, then start E2E-GAMEPLAY-008 from fresh main.
```
