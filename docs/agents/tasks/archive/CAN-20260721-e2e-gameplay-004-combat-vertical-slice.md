---
task_id: CAN-20260721-e2e-gameplay-004-combat-vertical-slice
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-GAMEPLAY-004-COMBAT-VERTICAL-SLICE
status: complete
agent: "GPT-5.6 Thinking"
branch: feat/e2e-gameplay-004-combat-vertical-slice
base_branch: main
created: 2026-07-21
updated: 2026-07-21
last_verified_commit: "8726107533e90507a40910efceb8f614392ecdbd"
risk: low
related_issue: ""
related_pr: "677"
depends_on:
  - merged Universal physical gameplay action contract PR 446
  - merged Universal scenario server-selection PR 468
  - merged Instanced Test Arena monster-spawn PR 304
blocks: []
owned_paths:
  exclusive: []
  read_only:
    - docs/agents/programs/E2E_AUTOMATION_PROGRAM.md
    - docs/architecture/universal-e2e-gameplay-validation.md
    - docs/e2e/PHYSICAL_GAMEPLAY_ACTION_PLANS.md
    - tools/e2e/run_agent_e2e.py
    - tools/e2e/run_physical_e2e.sh
    - tools/e2e/client/agent_e2e_scenario.lua
    - src/game/instance/instance_arena_service.cpp
    - src/game/instance/instance_arena_service.hpp
    - src/lua/creature/talkaction.cpp
    - data/scripts/talkactions/gm/instance_arena.lua
    - data-canary/monster/mammals/cave_rat.lua
    - docker/data/01-test_account.sql
    - docker/data/02-test_account_players.sql
    - tests/e2e/scenarios/combat/deterministic-combat.json
    - tests/e2e/test_deterministic_combat.py
modules_touched:
  - Universal E2E feature-owned combat scenario
  - deterministic administrative E2E fixture permissions
reuses:
  - canonical Universal E2E disposable Canary/MariaDB/controlled-OTClient lifecycle
  - existing scenario server selection for data-canary/canary
  - existing Instanced Test Arena deterministic Cave Rat fixture
  - existing physical gameplay plan actions
public_interfaces: []
cross_repo_tasks: []
---

# CAN-20260721 — E2E-GAMEPLAY-004 deterministic combat vertical slice

## Status

COMPLETE — the deterministic real-client combat vertical slice merged through PR #677.

## Delivered

- Added a bounded `combat/deterministic-combat` scenario using the repository-owned Instanced Test Arena and isolated 30-HP `Cave Rat` fixture.
- Authorized the dedicated `@test15` administrative test account through the `accounts.type` permission path actually used by TalkAction authorization.
- Used the existing level-500 `Paladin 15` fixture on account 115 for normal combat behavior.
- Reused existing `walk_edge`, `attack_visible`, `wait_creature` and `observe_attacking` actions without adding shared runner or workflow capability.
- Proved two exact movement edges, target visibility, acquisition, attacking state, deterministic target removal, cleared attacking state and explicit arena cleanup.
- Completed the canonical two-session safe logout/relog lifecycle plus SQL `lastlogin` and `lastlogout` assertions.
- Kept gameplay/datapack, OTBM/map, shared runner/workflow, OTClient source and client asset paths unchanged.

## Merge evidence

- Feature PR: #677 — `test(e2e): add deterministic combat vertical slice`.
- Final feature head: `8726107533e90507a40910efceb8f614392ecdbd`.
- Squash merge: `96abac79b10b8ccd19dd0915a074bd85710daea5`.
- Exact physical runtime run `29838496367`: success; artifact `8499077538` reports successful combat and complete canonical lifecycle.
- Checkpoint-only Universal Agent E2E run `29840520181`: success through validated immediate-parent physical evidence reuse.
- Agent Task Ownership run `29840518827`: success.
- Incremental CI run `29840521074`: success.
- Final-gate CI run `29840649522`: success across the full required matrix.
- Final-gate autofix.ci run `29840646703`: success.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-21T17:00:00+02:00
head: 8726107533e90507a40910efceb8f614392ecdbd
branch: feat/e2e-gameplay-004-combat-vertical-slice
pr: 677
status: complete
context_routes:
  - universal-e2e
owned_paths: []
proven:
  - PR #677 merged to main as 96abac79b10b8ccd19dd0915a074bd85710daea5.
  - E2E-GAMEPLAY-004 now has one deterministic bounded real-client combat lifecycle on the existing Universal E2E platform.
  - Instanced Test Arena provides the controlled Cave Rat fixture; no random public-world occupancy is used.
  - @test15 account type 6 authorizes /instancearena through the permission path used by TalkAction.
  - Paladin 15 exists on account 115 at level 500 and provides normal combat behavior for the scenario.
  - exact physical run 29838496367 proved target visibility, two exact walk edges, attack acquisition, observe_attacking=true, target removal, observe_attacking=false and explicit arena close.
  - the same run completed safe logout, persistence confirmation, second login, second safe logout and SQL lastlogin/lastlogout assertions.
  - artifact 8499077538 reports status=success, no missing required markers, client exit code 0 and no fatal runtime log hits.
  - checkpoint-only head 8726107533e90507a40910efceb8f614392ecdbd passed ownership run 29840518827, CI run 29840521074 and Universal Agent E2E run 29840520181 through validated immediate-parent evidence reuse.
  - final-gate CI run 29840649522 completed successfully on exact final feature head 8726107533e90507a40910efceb8f614392ecdbd.
  - final-gate autofix.ci run 29840646703 completed successfully without changing the feature head.
  - no shared runner, workflow, gameplay/datapack, OTBM/map, OTClient source or client asset expansion was required.
derived:
  - the bounded two-edge approach is the minimal stable route for the controlled normal-combat fixture because it avoids the creature-contested third tile while retaining target acquisition range.
unknown: []
conflicts: []
first_failure:
  marker: none on accepted exact-head runtime
  evidence: Universal Agent E2E run 29838496367 and artifact 8499077538 completed the full combat and canonical two-session lifecycle successfully
rejected_hypotheses:
  - add a generic creature-spawn fixture interface; the merged arena service already provides the deterministic target
  - extend target_defeated beyond the existing controlled-client ping seam
  - add privileged skill or spell setup for ADM1
  - use nonexistent Knight 15 on account 115
  - force a third exact approach edge into a creature-contested tile
changed_paths:
  - docker/data/01-test_account.sql
  - tests/e2e/scenarios/combat/deterministic-combat.json
  - tests/e2e/test_deterministic_combat.py
  - docs/agents/tasks/archive/CAN-20260721-e2e-gameplay-004-combat-vertical-slice.md
validation:
  - command: GitHub Actions Universal Agent E2E run 29838496367
    result: PASS
    evidence: Exact physical client completed combat, cleanup, canonical two-session lifecycle and SQL assertions.
  - command: GitHub Actions Agent Task Ownership run 29840518827
    result: PASS
    evidence: Ownership and checkpoint validation passed on the exact final feature head.
  - command: GitHub Actions CI run 29840649522
    result: PASS
    evidence: Full final-gate CI completed successfully on exact final feature head 8726107533e90507a40910efceb8f614392ecdbd.
  - command: GitHub Actions autofix.ci run 29840646703
    result: PASS
    evidence: Final-gate autofix workflow completed successfully without requiring a feature-head change.
blockers: []
next_action: Re-audit the current E2E gameplay programme queue and live repository state before starting the next bounded package from current main; do not continue PR #677 or its feature branch.
```
