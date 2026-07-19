---
task_id: CAN-20260719-e2e-gameplay-005-player-skill-level-persistence
program_id: CAN-PROGRAM-E2E-AUTOMATION
coordination_id: E2E-GAMEPLAY-005-SKILL-LEVEL
status: implementing
agent: "GPT-5.5 Thinking"
branch: feat/e2e-player-skill-level-persistence
base_branch: main
created: 2026-07-19T22:25:00+02:00
updated: 2026-07-19T22:49:00+02:00
last_verified_commit: "644fc0ec79bd89fae93bd14a6a443cfe57c7b004"
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

- [x] Support exactly `fist`, `club`, `sword`, `axe`, `distance`, `shielding`, and `fishing`.
- [x] Map each supported skill to one fixed Canary `players.skill_*` column and one fixed maintained-OTClient skill enum value.
- [x] Accept exact levels only in the `0..65535` range.
- [x] Re-verify after relog through maintained `LocalPlayer.getSkillBaseLevel`, not effective `getSkillLevel`.
- [x] Compile final SQL only from the fixed skill-name-to-column mapping.
- [x] Reject unknown skill names, arbitrary numeric skill IDs, unknown fields, booleans, negative values and values above `65535`.
- [x] Keep `_tries`, percentages, loyalty, temporary/equipment bonuses, additional skills, Forge skills and progression/training mechanics out of scope.
- [x] Preserve existing `player_field`, `player_storage`, `player_item_presence`, `player_balance` and `player_magic_level` behavior.
- [x] Add focused regression coverage and a durable public contract document.
- [x] Do not modify the E2E runner, workflows, route execution, OTBM tooling, map/client assets or reference repositories.
- [x] Update the module catalogue narrowly.
- [x] Apply `ci:final-gate` before the final checkpoint commit and make no post-final-head commits.
- [ ] Require exact-final-head Ownership, CI, Universal Agent E2E and autofix as applicable plus a clean review blocker audit before squash merge.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-19T22:49:00+02:00
head: 644fc0ec79bd89fae93bd14a6a443cfe57c7b004
branch: feat/e2e-player-skill-level-persistence
pr: 603
status: validating
next_action: Freeze this checkpoint commit as the final head, mark PR ready, require exact-final-head Ownership, CI, Universal Agent E2E and applicable autofix, then perform a clean review blocker and expected-head merge audit.
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
  - PR 603 owns branch feat/e2e-player-skill-level-persistence
  - Canary schema stores the seven classic skill levels in fixed players.skill_* columns with separate *_tries columns
  - Canary load maps the seven fixed skill columns into player skills level values as uint16
  - Canary save writes the seven player skill level values back to the fixed skill columns
  - maintained OTClient exposes Lua-bound LocalPlayer.getSkillBaseLevel and LocalPlayer.getSkillLevel separately
  - maintained OTClient packet parsing reads and stores baseLevel separately for Fist through Fishing
  - maintained OTClient enum order for the seven classic skills is Fist 0 through Fishing 6
  - implementation adds one fixed seven-skill player_skill_level validator and compiler with exact 0..65535 bounds and no caller-controlled SQL columns or numeric skill ids
  - controlled-client persistence verification reads maintained LocalPlayer.getSkillBaseLevel with the fixed client skill id after relog
  - focused regression coverage and PLAYER_SKILL_LEVEL_PERSISTENCE.md document the exact contract and exclusions
  - MODULE_CATALOG.md is updated only in the Universal OTS E2E physical gameplay action plans row after correcting and auditing an intermediate full-file write
  - current main advanced from task start to 2b6ae86539640dfc52323e9d5abbde31d6610c5f only through two unrelated OAM-020 documentation paths with no overlap with PR 603
  - implementation head 806412abc94163f6070649e21c41e5bb22ff80ca passed Agent Task Ownership and CI while autofix.ci was skipped
  - pre-final-checkpoint head 644fc0ec79bd89fae93bd14a6a443cfe57c7b004 passed Agent Task Ownership
  - ci:final-gate was applied to PR 603 before this final checkpoint commit
derived:
  - post-relog persistence verification uses getSkillBaseLevel rather than getSkillLevel so temporary or equipment bonuses cannot create a false mismatch against durable database state
  - fixed skill-name mappings keep both SQL column selection and maintained-client skill ids outside caller control
unknown:
  - exact-final-head Ownership, CI, Universal Agent E2E and applicable autofix outcomes are not known yet
  - final review blocker audit and expected-head squash merge remain pending
conflicts: []
rejected_hypotheses:
  - expose a caller-provided SQL column
  - expose an arbitrary numeric skill id
  - compare persisted database state with effective skill level including runtime bonuses
  - fold skill tries or percentage progress into the same scalar level contract
changed_paths:
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/tasks/active/CAN-20260719-e2e-gameplay-005-player-skill-level-persistence.md
  - docs/e2e/PLAYER_SKILL_LEVEL_PERSISTENCE.md
  - tests/e2e/test_player_skill_level_persistence.py
  - tools/e2e/client/agent_e2e_scenario.lua
  - tools/e2e/persistence_assertions.py
blockers:
  - exact-final-head Ownership, CI, Universal Agent E2E and applicable autofix must pass before merge
  - final review blocker audit and expected-head squash merge remain pending
first_failure:
  marker: The first full-file MODULE_CATALOG.md update accidentally removed the phrase before create-new publication from the unrelated OTBM bounded raw tile insertion materializer row.
  evidence: PR file-patch audit exposed the unrelated hunk immediately; the following correction restored the exact baseline phrase and the current catalog patch contains only the intended Universal OTS E2E row change.
validation:
  - command: evidence review of Canary schema and player skill save/load implementation
    result: PASS
    evidence: Fixed skill_fist through skill_fishing columns are loaded into and saved from the seven classic player skill level slots, with tries stored separately.
  - command: evidence review of maintained OTClient LocalPlayer and protocol parser
    result: PASS
    evidence: getSkillBaseLevel is Lua-bound and parsePlayerSkills stores separate baseLevel values for Fist through Fishing.
  - command: CI workflow on implementation head 806412abc94163f6070649e21c41e5bb22ff80ca
    result: PASS
    evidence: Agent Task Ownership and CI completed successfully; autofix.ci was skipped and the later documentation-only finalization commits did not change the persistence implementation.
  - command: PR 603 MODULE_CATALOG.md file-patch audit after correction
    result: PASS
    evidence: The current patch changes only the Universal OTS E2E physical gameplay action plans row to add PR 603, player_skill_level paths and the bounded fixed mapping/base-level contract.
  - command: Agent Task Ownership on pre-final-checkpoint head 644fc0ec79bd89fae93bd14a6a443cfe57c7b004
    result: PASS
    evidence: Workflow completed successfully before the final checkpoint commit.
  - command: exact-final-head required gate and review audit
    result: WARN
    evidence: Must run after this final checkpoint commit; no merge is permitted until Ownership, CI, Universal Agent E2E and applicable autofix are resolved on the exact frozen head and review blockers are clean.
```
