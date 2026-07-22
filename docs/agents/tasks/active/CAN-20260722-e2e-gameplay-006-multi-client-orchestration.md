---
task_id: CAN-20260722-e2e-gameplay-006-multi-client-orchestration
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-GAMEPLAY-006-MULTI-CLIENT
status: implementing
agent: "GPT-5.6 Thinking"
branch: feat/e2e-gameplay-006-multi-client-orchestration
base_branch: main
created: 2026-07-22
updated: 2026-07-22
last_verified_commit: "663de1726e82145f5b8027126dbe434cfa74440b"
risk: medium
related_issue: ""
related_pr: ""
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
    - docs/e2e/PHYSICAL_GAMEPLAY_ACTION_PLANS.md
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

- [ ] Reuse the existing single Canary/MariaDB lifecycle; do not create a second server orchestrator or workflow.
- [ ] Support exactly one secondary controlled OTClient in v1 with distinct account, character, scenario key and artifact directory.
- [ ] Keep raw passwords out of scenario data, generated evidence and process-command materialization; reuse `password_env`.
- [ ] Bound the secondary process with a timeout and terminate it when the primary client dies unexpectedly.
- [ ] Prove simultaneous primary/secondary presence and mutual creature visibility with deterministic markers.
- [ ] Preserve the canonical primary two-session safe logout/relog lifecycle and final SQL assertions.
- [ ] Ensure normal completion leaves no connected secondary client and no `players_online` rows.
- [ ] Add focused contract tests and physical Universal Agent E2E evidence on the exact final head.
- [ ] Merge through the normal autonomous gate, then archive this task before starting E2E-GAMEPLAY-007.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-22T23:30:00+02:00
head: 663de1726e82145f5b8027126dbe434cfa74440b
branch: feat/e2e-gameplay-006-multi-client-orchestration
pr: none
status: implementing
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
  - Current main is 663de1726e82145f5b8027126dbe434cfa74440b.
  - E2E-GAMEPLAY-003, E2E-GAMEPLAY-004 and E2E-GAMEPLAY-005 feature work is merged and archived.
  - No existing E2E-GAMEPLAY-006 implementation or competing multi-client PR was found.
  - The canonical run_physical_e2e.sh owns one server/database lifecycle and evaluates only the primary character login/session artifacts, allowing a bounded secondary client to coexist without changing the primary sentinel.
  - Deterministic fixtures @test1/Knight 1 and @test2/Knight 2 exist on distinct accounts and share the standard test password contract.
derived:
  - A secondary OTClient can be layered inside the existing physical runtime without a second server orchestrator if it has isolated artifacts and bounded cleanup.
unknown:
  - Exact physical mutual visibility of Knight 1 and Knight 2 on the current global datapack has not yet been proven on this task head.
conflicts: []
first_failure:
  marker: none
  evidence: No implementation or validation failure has occurred yet.
rejected_hypotheses:
  - A second full run_physical_e2e.sh invocation is required; it would duplicate database/server lifecycle and violate the single-orchestrator boundary.
changed_paths:
  - docs/agents/tasks/active/CAN-20260722-e2e-gameplay-006-multi-client-orchestration.md
validation: []
blockers: []
next_action: Implement the bounded secondary-client materializer, Lua process helper, primary/secondary visibility automations, committed scenario and focused tests, then open the draft PR for exact-head CI and Universal Physical E2E.
```
