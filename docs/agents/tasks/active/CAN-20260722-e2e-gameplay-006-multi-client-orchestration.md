---
task_id: CAN-20260722-e2e-gameplay-006-multi-client-orchestration
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-GAMEPLAY-006-MULTI-CLIENT
status: ready
agent: "GPT-5.6 Thinking"
branch: feat/e2e-gameplay-006-multi-client-orchestration-v2
base_branch: main
created: 2026-07-22
updated: 2026-07-22
last_verified_commit: "6821946357ea08ab6e2988f052324c7ad287b652"
risk: medium
related_issue: ""
related_pr: "747"
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
modules_touched:
  - Universal E2E bounded two-client orchestration
reuses:
  - existing disposable Canary/MariaDB/controlled-OTClient lifecycle
  - existing deterministic @test1 and @test2 fixtures
  - existing safe logout and primary two-session persistence sentinel
public_interfaces:
  - canary-universal-e2e-two-client-orchestration-v1
cross_repo_tasks: []
---

# CAN-20260722 — E2E-GAMEPLAY-006 bounded multi-client orchestration

## Goal

Add exactly one bounded secondary controlled OTClient to the existing Universal Physical E2E lifecycle, prove simultaneous two-client presence and mutual visibility, then preserve clean secondary shutdown plus the primary canonical two-session relog/persistence sentinel.

## Acceptance criteria

- [x] Reuse the existing single Canary/MariaDB lifecycle; do not create a second server orchestrator or workflow.
- [x] Support exactly one secondary controlled OTClient with distinct account, character and artifact directory.
- [x] Keep raw passwords out of scenario data and materialized actor evidence by reusing `password_env`.
- [x] Bound the secondary process with timeout and primary-death watchdog.
- [x] Preserve exact behavior of the physically successful predecessor implementation while replaying on clean current main.
- [ ] Pass exact-final-head Ownership, CI and Universal Physical E2E on clean PR #747 after formatter stabilization.
- [ ] Merge, register shared docs, archive lifecycle, then start E2E-GAMEPLAY-007.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-23T00:12:00+02:00
head: 6821946357ea08ab6e2988f052324c7ad287b652
branch: feat/e2e-gameplay-006-multi-client-orchestration-v2
pr: 747
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
  - The six implementation/test/scenario blobs on clean PR 747 preserve the physically successful PR 738 behavior; the only post-replay mutation was StyLua formatting in agent_e2e_multi_client.lua.
  - Historical Universal Agent E2E run 29960268146 passed physical job 89066632624 and Required physical E2E 89067453724, proving simultaneous Knight 1 and Knight 2 presence, mutual visibility, clean secondary exit and primary relog/persistence.
  - PR 738 was closed unmerged because technical squash synchronization polluted its diff with unrelated main changes; clean PR 747 starts directly from current main 6b23be9f4eeb513cd181dba8ccbc9a96b98e739f.
  - Clean PR 747 changed-file scope is exactly the task record plus six bounded implementation/test/scenario paths.
  - Agent Task Ownership run 29963530379 and CI run 29963530548 passed on clean pre-format final-checkpoint head 5e8772f5a9fe9cbf9f6fb742f2b577cfa27ddc44.
  - Ready-triggered CI 29963602067 failed only because StyLua proposed quote normalization in agent_e2e_multi_client.lua; autofix applied that formatting as head 6821946357ea08ab6e2988f052324c7ad287b652.
  - ci:final-gate remains applied to PR 747 before this post-format final checkpoint commit.
derived:
  - The ready-triggered CI failure was formatting-only and did not invalidate the already-proven multi-client runtime contract; exact-final gates must still run on the formatter-stabilized head.
unknown:
  - Exact-final-head Ownership, CI and Universal Agent E2E outcome after this post-format checkpoint commit.
  - Shared MODULE_CATALOG and CHANGELOG registration remains a narrow governance follow-up before lifecycle archive and E2E-GAMEPLAY-007.
conflicts: []
first_failure:
  marker: none
  evidence: No unresolved implementation failure remains; the only ready-triggered failure was deterministic StyLua formatting and has been applied.
rejected_hypotheses:
  - Merge polluted PR 738; its changed-file scope included unrelated OTBM/OAM drift and therefore failed the autonomous merge scope gate.
  - Treat ready-triggered CI 29963602067 as a runtime defect; the sole failing Fast Checks step reported formatter changes and the patch only normalized Lua string quoting.
changed_paths:
  - docs/agents/tasks/active/CAN-20260722-e2e-gameplay-006-multi-client-orchestration.md
  - tools/e2e/multi_client_orchestration.py
  - tools/e2e/client/agent_e2e_multi_client.lua
  - tools/e2e/client/agent_e2e_multi_client_secondary.lua
  - tools/e2e/client/agent_e2e_multi_client_visibility.lua
  - tests/e2e/scenarios/multiclient/shared-world-visibility.json
  - tests/e2e/test_multi_client_orchestration.py
validation:
  - command: Historical Universal Agent E2E run 29960268146 / physical job 89066632624 / Required physical E2E 89067453724
    result: PASS
    evidence: The bounded real two-client scenario completed successfully on the predecessor implementation.
  - command: Clean PR 747 Agent Task Ownership run 29963530379
    result: PASS
    evidence: Ownership and exact seven-file scope validation succeeded on the clean replay pre-format head.
  - command: Clean PR 747 CI run 29963530548
    result: PASS
    evidence: Repository CI succeeded before ready transition on the clean replay pre-format head.
  - command: Ready-triggered CI run 29963602067
    result: FAIL
    evidence: Fast Checks failed only because StyLua produced a formatting diff; no functional or build failure occurred.
blockers: []
next_action: Require exact-final Ownership, CI and Universal Agent E2E on this formatter-stabilized final checkpoint head; if green, audit reviews and exact seven-file scope, allow auto-merge, then complete shared-doc governance and lifecycle archive before E2E-GAMEPLAY-007.
```
