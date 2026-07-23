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
last_verified_commit: "4f074077da44d1cc9d77db7ac768be0589313332"
risk: medium
related_issue: ""
related_pr: ""
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

- [ ] Reuse the existing disposable Canary/MariaDB/controlled-OTClient lifecycle and workflow.
- [ ] Inject exactly one explicit client-side transport fault through maintained `g_game.forceLogout()` after stable world entry.
- [ ] Distinguish the expected injected disconnect from an unexpected platform failure in machine-readable markers.
- [ ] Recover with a second real-client login, then perform a canonical safe logout and leave no connected test player.
- [ ] Retain two packet records, two server logins, SQL persistence evidence, logs and final result artifacts.
- [ ] Add focused contract tests and pass exact-final-head Ownership, CI and Universal Physical E2E.
- [ ] Merge, register shared docs, archive lifecycle, then start E2E-GAMEPLAY-008.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-23T09:30:00+02:00
head: 4f074077da44d1cc9d77db7ac768be0589313332
branch: feat/e2e-gameplay-007-client-disconnect-recovery
pr: none
status: implementing
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
  - The Universal Physical E2E final evaluator requires two server logins and two packet records; a first-session injected client disconnect followed by one recovered session and safe logout fits that existing evidence contract without runner changes.
  - Maintained controlled-client automation already uses g_game.loginWorld, g_game.forceLogout/safeLogout lifecycle surfaces and machine-readable client-events.tsv markers.
derived:
  - The smallest safe E2E-GAMEPLAY-007 vertical slice is a client-side forced disconnect after stable login, followed by a second real-client login and safe cleanup; server restart and database interruption remain out of scope because no additional safe seam is required for the first recovery proof.
unknown:
  - Exact physical behavior of g_game.forceLogout in the current maintained OTClient under the Universal runner until the new scenario executes.
  - Exact-final-head CI and Universal Physical E2E outcome for the new scenario.
conflicts: []
first_failure:
  marker: none
  evidence: No implementation or validation failure has occurred on this task yet.
rejected_hypotheses:
  - Inject database interruption in the first 007 slice: rejected because the architecture requires a safe isolated seam and the client-disconnect seam proves recovery with materially lower risk.
changed_paths:
  - docs/agents/tasks/active/CAN-20260723-e2e-gameplay-007-client-disconnect-recovery.md
validation:
  - command: Live main/PR preflight
    result: PASS
    evidence: main head is 4f074077da44d1cc9d77db7ac768be0589313332; no existing E2E-GAMEPLAY-007 PR was found.
blockers: []
next_action: Open the draft PR, bind its number into this task record, then add the bounded controlled-client forceLogout recovery automation, scenario and focused tests.
```
