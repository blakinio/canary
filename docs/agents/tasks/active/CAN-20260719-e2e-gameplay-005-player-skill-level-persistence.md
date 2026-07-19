---
task_id: CAN-20260719-e2e-gameplay-005-player-skill-level-persistence
program_id: CAN-PROGRAM-E2E-AUTOMATION
coordination_id: E2E-GAMEPLAY-005-SKILL-LEVEL
status: implementing
agent: "GPT-5.5 Thinking"
branch: feat/e2e-player-skill-level-persistence
base_branch: main
created: 2026-07-19T22:25:00+02:00
updated: 2026-07-19T22:27:00+02:00
last_verified_commit: "1c639d0167476fee2871f8325beab5da48287046"
risk: medium
related_issue: ""
related_pr: "603"
depends_on:
  - merged E2E-GAMEPLAY-005 typed persistence foundation
  - merged PR #595 player_magic_level persistence
blocks: []
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260719-e2e-gameplay-005-player-skill-level-persistence.md
    - docs/e2e/PLAYER_SKILL_LEVEL_PERSISTENCE.md
    - tests/e2e/test_player_skill_level_persistence.py
  shared:
    - tools/e2e/persistence_assertions.py
    - tools/e2e/client/agent_e2e_scenario.lua
    - docs/agents/MODULE_CATALOG.md
  read_only:
    - tools/e2e/run_agent_e2e.py
    - tools/e2e/route_plan_execution.py
    - tests/e2e/scenarios/**
    - .github/workflows/**
    - docs/ai-agent/OTBM_*
modules_touched:
  - Universal OTS E2E physical gameplay action plans
reuses:
  - Universal Agent E2E two-session lifecycle
  - typed persistence assertion compiler
  - maintained OTClient LocalPlayer skill APIs
public_interfaces:
  - typed player_skill_level persistence assertion
cross_repo_tasks: []
---

# Goal

Add one bounded reusable `player_skill_level` persistence assertion for the seven classic durable player skills. The assertion must re-verify the persisted base skill level through the maintained real OTClient after relog and through final scalar SQL, without exposing arbitrary SQL or numeric skill IDs.

# Acceptance criteria

- [ ] Support exactly `fist`, `club`, `sword`, `axe`, `distance`, `shielding`, and `fishing`.
- [ ] Map each supported skill to one fixed Canary `players.skill_*` column and one fixed maintained-OTClient skill enum value.
- [ ] Accept exact levels only in the `0..65535` range.
- [ ] Re-verify after relog through maintained `LocalPlayer.getSkillBaseLevel`, not effective `getSkillLevel`.
- [ ] Compile final SQL only from the fixed skill-name-to-column mapping.
- [ ] Reject unknown skill names, arbitrary numeric skill IDs, unknown fields, booleans, negative values and values above `65535`.
- [ ] Keep `_tries`, percentages, loyalty, temporary/equipment bonuses, additional skills, Forge skills and progression/training mechanics out of scope.
- [ ] Preserve existing `player_field`, `player_storage`, `player_item_presence`, `player_balance` and `player_magic_level` behavior.
- [ ] Add focused regression coverage and a durable public contract document.
- [ ] Do not modify the E2E runner, workflows, route execution, OTBM tooling, map/client assets or reference repositories.
- [ ] Update the module catalogue narrowly.
- [ ] Apply `ci:final-gate` before the final checkpoint commit and make no post-final-head commits.
- [ ] Require exact-final-head Ownership, CI, Universal Agent E2E and autofix as applicable plus a clean review blocker audit before squash merge.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-19T22:27:00+02:00
head: 1c639d0167476fee2871f8325beab5da48287046
branch: feat/e2e-player-skill-level-persistence
pr: 603
status: implementing
next_action: Implement the fixed player_skill_level validator, SQL compiler, controlled-client base-skill reader, focused tests and contract documentation.
context_routes:
  - agent-governance
  - e2e
owned_paths:
  - docs/agents/tasks/active/CAN-20260719-e2e-gameplay-005-player-skill-level-persistence.md
  - docs/e2e/PLAYER_SKILL_LEVEL_PERSISTENCE.md
  - tests/e2e/test_player_skill_level_persistence.py
  - tools/e2e/persistence_assertions.py
  - tools/e2e/client/agent_e2e_scenario.lua
  - docs/agents/MODULE_CATALOG.md
proven:
  - live main at task start is 7b659fc3ad2de16374adf5450e97a731406f92e6
  - draft PR 603 owns branch feat/e2e-player-skill-level-persistence
  - no open PR matched player_skill_level or classic skill persistence ownership at task start
  - Canary schema stores the seven classic skill levels in fixed players.skill_* columns with separate *_tries columns
  - Canary load maps the seven fixed skill columns into player skills level values as uint16
  - Canary save writes the seven player skill level values back to the fixed skill columns
  - maintained OTClient exposes Lua-bound LocalPlayer.getSkillBaseLevel and LocalPlayer.getSkillLevel separately
  - maintained OTClient packet parsing reads and stores baseLevel separately for Fist through Fishing
  - maintained OTClient enum order for the seven classic skills is Fist 0 through Fishing 6
derived:
  - post-relog persistence verification should use getSkillBaseLevel rather than getSkillLevel so temporary or equipment bonuses cannot create a false mismatch against durable database state
unknown:
  - exact implementation head and CI outcomes are not known yet
conflicts: []
rejected_hypotheses:
  - expose a caller-provided SQL column
  - expose an arbitrary numeric skill id
  - compare persisted database state with effective skill level including runtime bonuses
changed_paths:
  - docs/agents/tasks/active/CAN-20260719-e2e-gameplay-005-player-skill-level-persistence.md
blockers: []
first_failure:
  marker: No material failure observed yet.
  evidence: Task has established the evidence contract and draft PR ownership but has not entered implementation validation yet.
validation:
  - command: evidence review of Canary schema and player skill save/load implementation
    result: PASS
    evidence: Fixed skill_fist through skill_fishing columns are loaded into and saved from the seven classic player skill level slots.
  - command: evidence review of maintained OTClient LocalPlayer and protocol parser
    result: PASS
    evidence: getSkillBaseLevel is Lua-bound and parsePlayerSkills stores separate baseLevel values for Fist through Fishing.
```
