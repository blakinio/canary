---
task_id: CAN-20260719-e2e-gameplay-005-player-vocation-persistence
program_id: CAN-PROGRAM-E2E-AUTOMATION
coordination_id: E2E-GAMEPLAY-005-VOCATION
status: implementing
agent: "GPT-5.5 Thinking"
branch: feat/e2e-player-vocation-persistence
base_branch: main
created: 2026-07-19T23:38:00+02:00
updated: 2026-07-19T23:52:00+02:00
last_verified_commit: "183d7224cb5de57585294d72631f37783b93dc89"
risk: medium
related_issue: ""
related_pr: "608"
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

- [x] Support exactly `none`, `sorcerer`, `druid`, `paladin`, `knight`, `master_sorcerer`, `elder_druid`, `royal_paladin`, `elite_knight`, `monk`, and `exalted_monk`.
- [x] Map every supported semantic vocation to one fixed Canary server vocation ID and one fixed maintained-OTClient client vocation ID.
- [x] Re-verify after relog through the existing maintained `LocalPlayer.getVocation()` runtime surface using the fixed client vocation ID.
- [x] Compile final scalar SQL only against the fixed Canary `players.vocation` column and fixed server vocation ID mapping.
- [x] Reject unknown vocation names, arbitrary numeric vocation IDs, booleans, empty values and unknown fields.
- [x] Do not expose caller-controlled SQL columns or caller-controlled server/client vocation IDs.
- [x] Keep vocation-change/promotion mechanics, custom dynamic vocations and unrelated progression state out of scope.
- [x] Preserve existing `player_field`, `player_storage`, `player_item_presence`, `player_balance`, `player_magic_level` and `player_skill_level` behavior in the compiler contract and focused mixed-type regression coverage.
- [x] Add focused regression coverage and a durable public contract document.
- [x] Do not modify the E2E runner, controlled-client Lua driver, workflows, route execution, OTBM tooling, map/client assets or reference repositories.
- [x] Update the module catalogue narrowly.
- [x] Apply `ci:final-gate` before the final checkpoint commit and make no post-final-head commits after a green final checkpoint sequence.
- [ ] Require exact-final-head Ownership, CI, Universal Agent E2E and autofix as applicable plus a clean review blocker audit before squash merge.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-19T23:52:00+02:00
head: 28f92e2736b854df1b57e95637d634cf0a464fef
branch: feat/e2e-player-vocation-persistence
pr: 608
status: implementing
next_action: Inspect exact-final-head Ownership, CI, Universal Agent E2E and autofix outcomes for this repaired active-task checkpoint commit; if all required gates pass, perform the clean review blocker audit and squash merge with the frozen head SHA.
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
  - live main at task start and immediately before final checkpoint sequencing is 183d7224cb5de57585294d72631f37783b93dc89
  - PR 600 remains separately owned OTBM route work and was not modified
  - no open E2E persistence PR owns this player_vocation contract
  - Canary data/XML/vocations.xml declares fixed server id and clientid pairs for the eleven maintained vocations
  - maintained blakinio/otclient defines matching VocationsServer and VocationsClient constants
  - maintained OTClient Player.getVocation returns the client-facing vocation ID domain
  - existing Universal E2E Lua driver already reads player:getVocation() for runtime player_field vocation checks
  - implementation keeps raw player_field vocation unavailable to callers and normalizes only typed player_vocation checks into the existing runtime path
  - implementation SQL uses only the fixed players.vocation column and fixed server vocation mapping
  - focused regression coverage checks all eleven mappings, numeric and unknown-name rejection, mapping/SQL surface rejection, raw player_field vocation rejection, SQL escaping, mixed existing-type preservation, normalized manifest rendering and reuse of the existing Lua vocation getter path
  - the final MODULE_CATALOG patch changes only the Universal OTS E2E physical gameplay action plans row
  - pre-final-head Agent Task Ownership succeeded after the checkpoint governance repair
  - ci:final-gate was applied before the final checkpoint sequence and remains present
  - the first attempted final head 28f92e2736b854df1b57e95637d634cf0a464fef was rejected only because an active-task record used status validating; this checkpoint restores the required active status
  - an earlier speculative player_soul draft PR 606 was closed without merge before implementation and is superseded by this evidence-backed vocation slice
derived:
  - client-side equality must use the fixed client vocation ID while post-cycle SQL must use the fixed Canary server vocation ID for the same semantic vocation
  - retaining vocation outside caller-accessible player_field prevents bypassing the normalization boundary with a raw numeric equality check
  - no maintained-client or controlled-client driver mutation is required because the existing player_field vocation path already reads LocalPlayer.getVocation
unknown:
  - the SHA produced by this repaired checkpoint commit becomes the new frozen final PR head and is not known inside the commit itself
  - exact-final-head Ownership, CI, Universal Agent E2E and autofix outcomes are pending after this commit
  - review/comment/thread blocker state must be re-audited against the frozen final head before merge
conflicts: []
rejected_hypotheses:
  - compare raw Canary server vocation IDs directly to LocalPlayer.getVocation
  - expose caller-provided numeric server or client vocation IDs
  - mutate maintained OTClient for an already available getter and mapping
  - add a second E2E runner or lifecycle
changed_paths:
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/tasks/active/CAN-20260719-e2e-gameplay-005-player-vocation-persistence.md
  - docs/e2e/PLAYER_VOCATION_PERSISTENCE.md
  - tests/e2e/test_player_vocation_persistence.py
  - tools/e2e/persistence_assertions.py
blockers: []
first_failure:
  marker: The first attempted exact-final-head Agent Task Ownership run rejected the task checkpoint because a record under tasks/active used non-active status validating.
  evidence: Ownership artifact active-task-ownership from run 29704996648 reported exactly that status error. The earlier implementation checkpoint had already passed ownership after adding required derived and first_failure fields.
validation:
  - command: evidence review of current Canary vocations.xml and maintained OTClient vocation constants/getter
    result: PASS
    evidence: The eleven server vocation IDs map deterministically to explicit client IDs, and LocalPlayer.getVocation exposes the client-facing domain used by maintained client logic.
  - command: PR 608 implementation patch audit for tools/e2e/persistence_assertions.py
    result: PASS
    evidence: The patch is limited to the fixed vocation mapping, typed validation, normalized client check emission, fixed SQL compilation and related documentation strings.
  - command: PR 608 MODULE_CATALOG patch audit
    result: PASS
    evidence: The catalogue diff changes only the Universal OTS E2E physical gameplay action plans row and preserves unrelated OTBM catalogue material.
  - command: Agent Task Ownership on pre-final head d92c23596203ca419ab89340c9e53d7616cb0e53
    result: PASS
    evidence: Workflow run 29704946030 completed successfully after the checkpoint governance repair.
  - command: Agent Task Ownership on first attempted final head 28f92e2736b854df1b57e95637d634cf0a464fef
    result: FAIL
    evidence: Workflow run 29704996648 rejected only the non-active validating status in the active task record; this commit restores implementing.
  - command: exact-final-head Ownership, CI, Universal Agent E2E and autofix sequence
    result: NOT_RUN
    evidence: This repaired checkpoint commit creates the new frozen final head; exact-head workflow outcomes necessarily occur after the commit and are recorded externally before merge.
```
