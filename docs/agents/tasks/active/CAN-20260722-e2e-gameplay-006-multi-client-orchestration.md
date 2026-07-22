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
last_verified_commit: "4e06849bd15bdb614e48a97112ee8d7e30c42f20"
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
- [x] Preserve exact byte identity with the physically successful predecessor implementation while replaying on clean current main.
- [ ] Pass exact-final-head Ownership, CI and Universal Physical E2E on clean PR #747.
- [ ] Merge, register shared docs, archive lifecycle, then start E2E-GAMEPLAY-007.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-23T00:05:00+02:00
head: 4e06849bd15bdb614e48a97112ee8d7e30c42f20
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
  - The six implementation/test/scenario blobs on clean PR 747 are byte-identical to the physically successful PR 738 implementation.
  - Historical Universal Agent E2E run 29960268146 passed physical job 89066632624 and Required physical E2E 89067453724, proving simultaneous Knight 1 and Knight 2 presence, mutual visibility, clean secondary exit and primary relog/persistence.
  - PR 738 was closed unmerged because technical squash synchronization polluted its diff with unrelated main changes; clean PR 747 starts directly from current main 6b23be9f4eeb513cd181dba8ccbc9a96b98e739f.
  - Clean PR 747 changed-file scope is exactly the task record plus six bounded implementation/test/scenario paths.
  - Agent Task Ownership run 29963381681 passed on clean head 4e06849bd15bdb614e48a97112ee8d7e30c42f20.
  - ci:final-gate was applied to PR 747 before this final checkpoint commit.
derived:
  - The clean replay removes the predecessor scope defect without changing the physically proven implementation blobs.
unknown:
  - Exact-final-head CI and Universal Agent E2E outcome after this checkpoint commit.
  - Shared MODULE_CATALOG and CHANGELOG registration remains a narrow governance follow-up before lifecycle archive and E2E-GAMEPLAY-007.
conflicts: []
first_failure:
  marker: none
  evidence: No unresolved implementation failure remains; predecessor PR 738 was superseded solely for polluted scope.
rejected_hypotheses:
  - Merge polluted PR 738; its changed-file scope included unrelated OTBM/OAM drift and therefore failed the autonomous merge scope gate.
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
    evidence: Byte-identical implementation passed the full real two-client scenario on predecessor PR 738.
  - command: Clean PR 747 Agent Task Ownership run 29963381681
    result: PASS
    evidence: Active task ownership and exact seven-file scope validation succeeded on the clean replay head before final checkpoint.
blockers: []
next_action: Require exact-final Ownership, CI and Universal Agent E2E on this final checkpoint head; if green, audit reviews and exact seven-file scope, mark PR 747 ready and squash-merge, then complete shared-doc governance and lifecycle archive before E2E-GAMEPLAY-007.
```
