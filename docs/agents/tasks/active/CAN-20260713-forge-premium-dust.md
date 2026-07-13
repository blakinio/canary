---
task_id: CAN-20260713-forge-premium-dust
program_id: CAN-PROGRAM-EQUIPMENT-UPGRADE-PARITY
coordination_id: ""
status: in_progress
agent: "GPT-5.6 Thinking"
branch: fix/forge-premium-dust
base_branch: main
created: 2026-07-13T16:44:00+02:00
updated: 2026-07-13T21:10:00+02:00
last_verified_commit: "d4e8933b78587445afd9347a6d05b6e715c6c0e4"
risk: medium
related_issue: ""
related_pr: "#262"
depends_on:
  - PR #259 merged as 444aa8ae13edc01c6e77b03139a43d386b437308
blocks: []
owned_paths:
  exclusive:
    - src/lua/functions/creatures/player/player_functions.hpp
    - src/lua/functions/creatures/player/player_functions.cpp
    - docs/lua-api/lua_api.json
    - data/libs/systems/exaltation_forge.lua
    - tests/lua/test_exaltation_forge_premium.lua
    - docs/agents/tasks/active/CAN-20260713-forge-premium-dust.md
  shared: []
  read_only:
    - src/creatures/players/player.hpp
    - src/creatures/players/player.cpp
modules_touched:
  - Player Lua API
  - Exaltation Forge Dust eligibility
  - Lua API documentation
  - Lua reward regressions
reuses:
  - exact C++ `Player::isPremium()` semantics
  - PR #177 capped Dust credit and single party roll
  - PR #259 Forge Lua baseline
public_interfaces:
  - `Player:isPremium() -> boolean`
cross_repo_tasks: []
---

# Goal

Resolve F-006 by requiring exact Canary Premium eligibility before any player receives Exaltation Forge Dust.

# Acceptance criteria

- [x] Lua exposes `Player:isPremium()` as a direct delegation to `Player::isPremium()`.
- [x] The binding is documented in `docs/lua-api/lua_api.json`.
- [x] `ForgeMonster:creditDust` returns zero without Dust mutation for non-Premium players.
- [x] Free Premium, Always Premium and account-time semantics remain inherited from C++.
- [x] PR #177 cap-aware actual credit remains unchanged for eligible players.
- [x] Focused Lua tests cover rejection, eligible credit and cap truncation.
- [ ] Full clean-head CI passes before merge.

# Evidence boundary

The binding delegates to the existing C++ predicate. No Premium semantics are reconstructed in Lua. Repository CI and focused Lua tests are required; physical-client gameplay remains separate evidence.

# Completion

- Final status: in_progress
- PR: #262
- Merge commit:
- Archived at:
