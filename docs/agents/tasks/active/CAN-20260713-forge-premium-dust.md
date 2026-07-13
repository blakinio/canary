---
task_id: CAN-20260713-forge-premium-dust
program_id: CAN-PROGRAM-EQUIPMENT-UPGRADE-PARITY
coordination_id: ""
status: in_progress
agent: "GPT-5.6 Thinking"
branch: fix/forge-premium-dust
base_branch: fix/forge-live-defaults
created: 2026-07-13T16:44:00+02:00
updated: 2026-07-13T16:44:00+02:00
last_verified_commit: "a7d700922fa18bd78666d66a376cffb527fa9cf8"
risk: medium
related_issue: ""
related_pr: ""
depends_on:
  - PR #259 Forge live defaults and shared `exaltation_forge.lua` ownership
blocks: []
owned_paths:
  exclusive:
    - src/lua/functions/creatures/player/player_functions.hpp
    - src/lua/functions/creatures/player/player_functions.cpp
    - docs/lua-api/lua_api.json
    - data/libs/systems/exaltation_forge.lua
    - tests/lua/test_exaltation_forge_premium.lua
    - docs/agents/tasks/active/CAN-20260713-forge-premium-dust.md
  shared:
    - docs/agents/programs/EQUIPMENT_UPGRADE_PARITY_PROGRAM.md
    - docs/ai-agent/OTS_AI_EQUIPMENT_UPGRADE_VALIDATION.md
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - src/creatures/players/player.hpp
    - src/creatures/players/player.cpp
    - src/config/configmanager.cpp
modules_touched:
  - Player Lua API
  - Exaltation Forge Dust eligibility
  - Lua API documentation
  - Lua reward regressions
reuses:
  - exact C++ `Player::isPremium()` semantics
  - PR #177 capped Dust credit and single party roll
  - PR #259 Forge Lua library baseline
public_interfaces:
  - `Player:isPremium() -> boolean` Lua method
cross_repo_tasks: []
---

# Goal

Resolve F-006 by requiring exact Canary Premium eligibility before any player receives Exaltation Forge Dust.

# Acceptance criteria

- [ ] Lua exposes `Player:isPremium()` as a direct delegation to `Player::isPremium()`.
- [ ] The binding is documented in `docs/lua-api/lua_api.json`.
- [ ] `ForgeMonster:creditDust` returns zero and does not mutate Dust for a non-Premium player.
- [ ] Free Premium, Always Premium and account-time semantics remain inherited from C++ rather than duplicated in Lua.
- [ ] Existing cap-aware actual credit behavior from #177 remains unchanged for eligible players.
- [ ] Focused Lua tests cover non-Premium rejection, eligible credit and cap truncation.
- [ ] Full current-head CI passes before merge.

# Evidence

- Current `ForgeMonster:creditDust` checks only the player's Dust cap.
- `getPremiumDays()` is insufficient because `Player::isPremium()` also accounts for Free Premium, `IsAlwaysPremium` and the account premium timestamp.
- The selected retail rule requires Premium status to receive Dust.

# Design

Add a read-only Lua binding that calls the existing C++ predicate. Use it as the first eligibility gate in `creditDust`, before reading or mutating Dust. Do not calculate Premium state independently in Lua.

# Completion

- Final status: in_progress
- PR:
- Merge commit:
- Archived at:
