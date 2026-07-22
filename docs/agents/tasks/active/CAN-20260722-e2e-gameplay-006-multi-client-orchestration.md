---
task_id: CAN-20260722-e2e-gameplay-006-multi-client-orchestration
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-GAMEPLAY-006-MULTI-CLIENT
status: ready
agent: "GPT-5.6 Thinking"
branch: feat/e2e-gameplay-006-multi-client-orchestration
base_branch: main
created: 2026-07-22
updated: 2026-07-22
last_verified_commit: "53d7d01e0da3b1bb244ecfd9284482de45ad0cf0"
risk: medium
related_issue: ""
related_pr: "738"
depends_on:
  - stable Universal Physical E2E single-client lifecycle
  - merged deterministic gameplay vertical slices
blocks:
  - E2E-GAMEPLAY-008 representative cross-system journeys
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260722-e2e-gameplay-006-multi-client-orchestration.md
    - tools/e2e/multi_client_orchestration.py
    - tools/e2e/client/agent_e2e_multi_client.lua
    - tools/e2e/client/agent_e2e_multi_client_secondary.lua
    - tools/e2e/client/agent_e2e_multi_client_visibility.lua
    - tests/e2e/scenarios/multiclient/shared-world-visibility.json
    - tests/e2e/test_multi_client_orchestration.py
  shared:
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - tools/e2e/run_physical_e2e.sh
    - tools/e2e/run_agent_e2e.py
    - .github/workflows/universal-agent-e2e.yml
    - docker/data/01-test_account.sql
    - docker/data/02-test_account_players.sql
modules_touched:
  - Universal E2E bounded two-client orchestration
reuses:
  - existing disposable Canary/MariaDB/controlled-OTClient lifecycle
  - existing deterministic @test1 and @test2 fixtures
  - existing exact password environment reference contract
  - existing safe logout and primary two-session persistence sentinel
public_interfaces:
  - canary-universal-e2e-two-client-orchestration-v1
cross_repo_tasks: []
---

# CAN-20260722 — E2E-GAMEPLAY-006 bounded multi-client orchestration

## Goal

Add the first bounded two-client capability to the existing Universal Physical E2E lifecycle without creating a second server/database runner. The primary controlled OTClient remains owned by the canonical runner; a reusable helper launches exactly one secondary controlled OTClient with a distinct deterministic identity, artifact directory, log set, timeout and parent-death watchdog. The first proof requires both clients to be online concurrently and mutually visible before either is released.

## Acceptance criteria

- [x] Reuse the existing single Canary/MariaDB lifecycle; do not create a second server orchestrator or workflow.
- [x] Support exactly one secondary controlled OTClient in v1 with distinct account, character, scenario key and artifact directory.
- [x] Keep raw passwords out of scenario data, generated evidence and process-command materialization; reuse `password_env`.
- [x] Bound the secondary process with a timeout and terminate it when the primary client dies unexpectedly.
- [x] Prove simultaneous primary/secondary presence and mutual creature visibility with deterministic markers.
- [x] Preserve the canonical primary two-session safe logout/relog lifecycle and final SQL assertions.
- [x] Ensure normal completion leaves no connected secondary client and no `players_online` rows through physical evidence.
- [x] Add focused contract tests and physical Universal Agent E2E evidence on the validated implementation head.
- [ ] Merge through the normal autonomous gate, complete the narrow shared-doc governance follow-up, then archive this task before starting E2E-GAMEPLAY-007.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-22T23:45:00+02:00
head: 53d7d01e0da3b1bb244ecfd9284482de45ad0cf0
branch: feat/e2e-gameplay-006-multi-client-orchestration
pr: 738
status: ready
context_routes:
  - universal-e2e
  - agent-governance
owned_paths:
  - docs/agents/tasks/active/CAN-20260722-e2e-gameplay-006-multi-client-orchestration.md
  - tools/e2e/multi_client_orchestration.py
  - tools/e2e/client/agent_e2e_multi_client.lua
  - tools/e2e/client/agent_e2e_multi_client_secondary.lua
  - tools/e2e/client/agent_e2e_multi_client_visibility.lua
  - tests/e2e/scenarios/multiclient/shared-world-visibility.json
  - tests/e2e/test_multi_client_orchestration.py
proven:
  - E2E-GAMEPLAY-003, E2E-GAMEPLAY-004 and E2E-GAMEPLAY-005 feature work is merged and archived.
  - The v1 materializer exposes exactly one secondary actor, validates distinct account/character identity, carries only password_env, and writes isolated actor artifacts.
  - The Lua process helper bounds the child with timeout and a primary-process watchdog; primary and secondary automations coordinate mutual visibility and secondary safe release before the primary relog cycle.
  - Focused materializer compilation and representative @test1/@test2 materialization passed without serializing a raw password value.
  - Agent Task Ownership run 29960267954 passed on 546d63fdd859a3b2831d31a73ad4ebc5c1d59b70.
  - CI run 29960268153 passed on 546d63fdd859a3b2831d31a73ad4ebc5c1d59b70.
  - Universal Agent E2E run 29960268146 passed the physical multiclient/shared-world-visibility job 89066632624 and Required physical E2E job 89067453724.
  - The physical scenario proved simultaneous @test1/Knight 1 and @test2/Knight 2 presence, mutual visibility, clean secondary exit, primary safe logout/relog, both actors persisted login/logout evidence and zero remaining players_online rows.
  - Technical sync PR 746 squash-merged current main into this feature branch as 53d7d01e0da3b1bb244ecfd9284482de45ad0cf0; intervening drift is unrelated task documentation with no E2E owned-path overlap.
  - ci:final-gate was applied to PR 738 before this final checkpoint commit.
derived:
  - The bounded two-client capability is physically proven without introducing a second Canary/MariaDB orchestrator or workflow.
unknown:
  - Shared MODULE_CATALOG and CHANGELOG registration remains a narrow post-feature governance follow-up before lifecycle archive and E2E-GAMEPLAY-007.
conflicts: []
first_failure:
  marker: none
  evidence: No unresolved implementation or physical validation failure remains; earlier ownership failures were corrected task-record metadata only.
rejected_hypotheses:
  - A second full run_physical_e2e.sh invocation is required; the successful physical run proves the secondary client can coexist inside the canonical server/database lifecycle.
changed_paths:
  - docs/agents/tasks/active/CAN-20260722-e2e-gameplay-006-multi-client-orchestration.md
  - tools/e2e/multi_client_orchestration.py
  - tools/e2e/client/agent_e2e_multi_client.lua
  - tools/e2e/client/agent_e2e_multi_client_secondary.lua
  - tools/e2e/client/agent_e2e_multi_client_visibility.lua
  - tests/e2e/scenarios/multiclient/shared-world-visibility.json
  - tests/e2e/test_multi_client_orchestration.py
validation:
  - command: Agent Task Ownership run 29960267954
    result: PASS
    evidence: Current implementation-head ownership validation succeeded after task-record contract corrections.
  - command: CI run 29960268153
    result: PASS
    evidence: Full repository CI succeeded on the validated implementation head.
  - command: Universal Agent E2E run 29960268146 / Physical job 89066632624 / Required physical job 89067453724
    result: PASS
    evidence: Real two-client shared-world visibility, coordinated cleanup and primary relog/persistence completed successfully.
blockers: []
next_action: Require exact-final Ownership, CI and Universal Agent E2E on this final checkpoint head; if green, audit reviews and scope, mark PR 738 ready and squash-merge, then complete the narrow shared-doc governance follow-up and lifecycle archive before starting E2E-GAMEPLAY-007.
```
