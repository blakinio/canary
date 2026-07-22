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
last_verified_commit: "f54bf6b93144b90d5c980000908d11590e316946"
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

- [x] Reuse the existing single Canary/MariaDB lifecycle; do not create a second server orchestrator or workflow.
- [x] Support exactly one secondary controlled OTClient in v1 with distinct account, character, scenario key and artifact directory.
- [x] Keep raw passwords out of scenario data, generated evidence and process-command materialization; reuse `password_env`.
- [x] Bound the secondary process with a timeout and terminate it when the primary client dies unexpectedly.
- [ ] Prove simultaneous primary/secondary presence and mutual creature visibility with deterministic markers.
- [x] Preserve the canonical primary two-session safe logout/relog lifecycle and final SQL assertions by design; physical proof pending.
- [ ] Ensure normal completion leaves no connected secondary client and no `players_online` rows through physical evidence.
- [ ] Add focused contract tests and physical Universal Agent E2E evidence on the exact final head.
- [ ] Merge through the normal autonomous gate, then archive this task before starting E2E-GAMEPLAY-007.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-22T23:41:00+02:00
head: f54bf6b93144b90d5c980000908d11590e316946
branch: feat/e2e-gameplay-006-multi-client-orchestration
pr: 738
status: validating
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
  - No existing E2E-GAMEPLAY-006 implementation or competing multi-client PR was found before branch creation.
  - The canonical run_physical_e2e.sh owns one server/database lifecycle and evaluates the primary character login/session artifacts, allowing a bounded secondary client to coexist without a second server orchestrator.
  - Deterministic fixtures @test1/Knight 1 and @test2/Knight 2 exist on distinct accounts and share the standard password environment contract.
  - The implemented v1 materializer exposes only one secondary actor, validates distinct account/character identity, carries only password_env, and writes isolated actor artifacts.
  - The implemented Lua process helper bounds the child with timeout and a primary-process watchdog; primary and secondary automations coordinate mutual-visibility markers and secondary safe release before the primary canonical relog cycle.
  - PR 738 was opened from feature head 8f6482c57ddae1faee4e0feae15a20f5426d2dc5.
  - Main advanced once to 8bdeb2747356727df80a3b95073aa29a4dca7818 only by adding the unrelated OAM-037 task record; no E2E owned path overlap exists.
  - Initial Ownership run 29959275464 failed only because related_pr was still empty after PR creation.
  - Ownership run 29959566082 failed only because frontmatter status was validating; Ownership run 29959841690 confirmed that arbitrary status active is also invalid, and source inspection proves implementing is the correct active work status.
derived:
  - All observed Ownership failures are task-record contract debt, not evidence of a multi-client implementation defect.
unknown:
  - Exact physical mutual visibility of Knight 1 and Knight 2 remains unproven until the Universal Agent E2E physical job completes.
  - Exact current-head ownership and Universal Agent E2E remain pending after the final frontmatter status correction.
conflicts: []
first_failure:
  marker: active task frontmatter status mismatch
  evidence: task_ownership.py ACTIVE_STATUSES is planned, implementing, blocked, review, ready; validating belongs only to checkpoint.py, while arbitrary active is also rejected.
rejected_hypotheses:
  - A second full run_physical_e2e.sh invocation is required; it would duplicate database/server lifecycle and violate the single-orchestrator boundary.
changed_paths:
  - docs/agents/tasks/active/CAN-20260722-e2e-gameplay-006-multi-client-orchestration.md
  - tools/e2e/multi_client_orchestration.py
  - tools/e2e/client/agent_e2e_multi_client.lua
  - tools/e2e/client/agent_e2e_multi_client_secondary.lua
  - tools/e2e/client/agent_e2e_multi_client_visibility.lua
  - tests/e2e/scenarios/multiclient/shared-world-visibility.json
  - tests/e2e/test_multi_client_orchestration.py
validation:
  - command: Agent Task Ownership run 29959275464
    result: FAIL
    evidence: Changed-task metadata validation failed because related_pr was empty; focused ownership tooling setup/tests passed.
  - command: Agent Task Ownership run 29959566082
    result: FAIL
    evidence: Changed-task metadata validation failed because active-task frontmatter status was validating; focused ownership tooling setup/tests passed.
  - command: Agent Task Ownership run 29959841690
    result: FAIL
    evidence: Changed-task metadata validation failed because arbitrary frontmatter status active is not one of task_ownership.py ACTIVE_STATUSES.
  - command: local bounded materializer py_compile and representative materialization
    result: PASS
    evidence: Python helper compiled; @test1/@test2 plan materialized with password_env only and no AGENT_E2E_PASSWORD value.
blockers: []
next_action: Require exact-head Ownership, CI and Universal Agent E2E after this implementing-status correction; fix the first implementation or physical failure if present, then synchronize unrelated main drift before final-head gating.
```
