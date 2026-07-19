---
task_id: CAN-20260719-e2e-gameplay-005-player-vocation-persistence
program_id: CAN-PROGRAM-E2E-AUTOMATION
coordination_id: E2E-GAMEPLAY-005-VOCATION
status: implementing
agent: "GPT-5.5 Thinking"
branch: feat/e2e-player-vocation-persistence
base_branch: main
created: 2026-07-19T23:38:00+02:00
updated: 2026-07-19T23:38:00+02:00
last_verified_commit: "183d7224cb5de57585294d72631f37783b93dc89"
risk: medium
related_issue: ""
related_pr: ""
depends_on:
  - merged E2E-GAMEPLAY-005 typed persistence foundation
  - merged PR #603 player_skill_level persistence
blocks: []
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260719-e2e-gameplay-005-player-vocation-persistence.md
    - docs/e2e/PLAYER_VOCATION_PERSISTENCE.md
    - tests/e2e/test_player_vocation_persistence.py
  shared:
    - tools/e2e/persistence_assertions.py
    - docs/agents/MODULE_CATALOG.md
  read_only:
    - tools/e2e/run_agent_e2e.py
    - tools/e2e/client/agent_e2e_scenario.lua
    - tools/e2e/route_plan_execution.py
    - tests/e2e/scenarios/**
    - .github/workflows/**
    - docs/ai-agent/OTBM_*
modules_touched:
  - Universal OTS E2E physical gameplay action plans
reuses:
  - Universal Agent E2E two-session lifecycle
  - typed persistence assertion compiler
  - existing runtime player_field vocation read path
  - maintained OTClient LocalPlayer.getVocation API
public_interfaces:
  - typed player_vocation persistence assertion
cross_repo_tasks: []
---

# Goal

Add one bounded reusable `player_vocation` persistence assertion that accepts only fixed semantic vocation names, maps each name to one fixed Canary `players.vocation` server ID and one fixed maintained-OTClient client vocation ID, verifies the client-facing normalized vocation after relog through the existing `LocalPlayer.getVocation()` path, and verifies final durable state through fixed scalar SQL.

# Acceptance criteria

- [ ] Support exactly `none`, `sorcerer`, `druid`, `paladin`, `knight`, `master_sorcerer`, `elder_druid`, `royal_paladin`, `elite_knight`, `monk`, and `exalted_monk`.
- [ ] Map every supported semantic vocation to one fixed Canary server vocation ID and one fixed maintained-OTClient client vocation ID.
- [ ] Re-verify after relog through the existing maintained `LocalPlayer.getVocation()` runtime surface using the fixed client vocation ID.
- [ ] Compile final scalar SQL only against the fixed Canary `players.vocation` column and fixed server vocation ID mapping.
- [ ] Reject unknown vocation names, arbitrary numeric vocation IDs, booleans, empty values and unknown fields.
- [ ] Do not expose caller-controlled SQL columns or caller-controlled server/client vocation IDs.
- [ ] Keep vocation-change/promotion mechanics, custom dynamic vocations and unrelated progression state out of scope.
- [ ] Preserve existing `player_field`, `player_storage`, `player_item_presence`, `player_balance`, `player_magic_level` and `player_skill_level` behavior.
- [ ] Add focused regression coverage and a durable public contract document.
- [ ] Do not modify the E2E runner, controlled-client Lua driver, workflows, route execution, OTBM tooling, map/client assets or reference repositories.
- [ ] Update the module catalogue narrowly.
- [ ] Apply `ci:final-gate` before the final checkpoint commit and make no post-final-head commits.
- [ ] Require exact-final-head Ownership, CI, Universal Agent E2E and autofix as applicable plus a clean review blocker audit before squash merge.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-19T23:38:00+02:00
head: 183d7224cb5de57585294d72631f37783b93dc89
branch: feat/e2e-player-vocation-persistence
pr: null
status: implementing
next_action: Publish the draft PR, implement fixed semantic server/client vocation normalization in the existing typed persistence compiler, add focused tests and docs, then audit the exact diff.
context_routes:
  - agent-governance
  - universal-e2e
  - cross-repo
owned_paths:
  - docs/agents/tasks/active/CAN-20260719-e2e-gameplay-005-player-vocation-persistence.md
  - docs/e2e/PLAYER_VOCATION_PERSISTENCE.md
  - tests/e2e/test_player_vocation_persistence.py
  - tools/e2e/persistence_assertions.py
  - docs/agents/MODULE_CATALOG.md
proven:
  - live main at task start is 183d7224cb5de57585294d72631f37783b93dc89
  - PR 600 remains separately owned OTBM route work and is not touched
  - no open E2E persistence PR owns this player_vocation contract
  - Canary data/XML/vocations.xml declares fixed server id and clientid pairs for the eleven maintained vocations
  - maintained blakinio/otclient defines matching VocationsServer and VocationsClient constants
  - maintained OTClient Player.getVocation returns the client-facing vocation ID domain
  - existing Universal E2E Lua driver already reads player:getVocation() for runtime player_field vocation checks
  - existing typed persistence compiler and two-session relog verification are reusable
  - an earlier speculative player_soul draft PR 606 was closed without merge before implementation and is superseded by this evidence-backed vocation slice
unknown:
  - exact final-head validation outcomes are not known yet
conflicts: []
rejected_hypotheses:
  - compare raw Canary server vocation IDs directly to LocalPlayer.getVocation
  - expose caller-provided numeric server or client vocation IDs
  - mutate maintained OTClient for an already available getter and mapping
  - add a second E2E runner or lifecycle
changed_paths:
  - docs/agents/tasks/active/CAN-20260719-e2e-gameplay-005-player-vocation-persistence.md
blockers: []
validation:
  - command: evidence review of current Canary vocations.xml and maintained OTClient vocation constants/getter
    result: PASS
    evidence: The eleven server vocation IDs map deterministically to explicit client IDs, and LocalPlayer.getVocation exposes the client-facing domain used by maintained client logic.
```
