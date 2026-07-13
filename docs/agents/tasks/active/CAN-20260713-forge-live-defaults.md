---
task_id: CAN-20260713-forge-live-defaults
program_id: CAN-PROGRAM-EQUIPMENT-UPGRADE-PARITY
coordination_id: ""
status: ready_for_review_pending_final_ci
agent: "GPT-5.6 Thinking"
branch: fix/forge-live-defaults
base_branch: fix/forge-server-authority
created: 2026-07-13T16:28:00+02:00
updated: 2026-07-13T17:01:00+02:00
last_verified_commit: "a7d700922fa18bd78666d66a376cffb527fa9cf8"
risk: low
related_issue: ""
related_pr: "#259"
depends_on:
  - PR #250 Forge server authority lifecycle
blocks:
  - PR #262 Premium Dust, by shared Exaltation Forge Lua ownership
owned_paths:
  exclusive:
    - src/config/forge_config_defaults.hpp
    - src/config/configmanager.cpp
    - config.lua.dist
    - data/libs/systems/exaltation_forge.lua
    - tests/unit/game/forge_config_test.cpp
    - tests/unit/game/CMakeLists.txt
    - docs/agents/tasks/active/CAN-20260713-forge-live-defaults.md
  shared:
    - docs/agents/programs/EQUIPMENT_UPGRADE_PARITY_PROGRAM.md
    - docs/ai-agent/OTS_AI_EQUIPMENT_UPGRADE_VALIDATION.md
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - src/config/config_enums.hpp
modules_touched:
  - Forge configuration defaults
  - Exaltation Forge Lua Fiendish limit
  - Forge configuration regression tests
reuses:
  - existing ConfigManager keys and config.lua surface
public_interfaces:
  - internal constexpr Forge default values
cross_repo_tasks: []
---

# Goal

Resolve F-001 and F-002 by aligning Canary's retail Forge defaults with the selected live Tibia rules: Dust limit 325 and at most four Fiendish creatures.

# Acceptance criteria

- [x] `FORGE_MAX_DUST` fallback is 325.
- [x] `config.lua.dist` exposes `forgeMaxDust = 325`.
- [x] `FORGE_FIENDISH_CREATURES_LIMIT` fallback is 4.
- [x] `config.lua.dist` exposes `forgeFiendishLimit = 4`.
- [x] `ForgeMonster.maxFiendish` is 4.
- [x] Focused unit tests pin the C++ constants and parse both distributed Lua sources.
- [x] No runtime behavior outside default/fallback selection changes.
- [ ] Full current-head CI passes after final task bookkeeping.
- [ ] Retarget to `main` after #250 merges and rerun final gate.

# Confirmed changes

- Added `ForgeConfigDefaults::maxDust = 325`.
- Added `ForgeConfigDefaults::fiendishCreaturesLimit = 4`.
- `ConfigManager` uses those constants as fallbacks.
- `config.lua.dist` now advertises Dust 325 and Fiendish 4.
- `data/libs/systems/exaltation_forge.lua` no longer retains a stale `maxFiendish = 3`.
- `forge_config_test.cpp` reads repository files and prevents all three public/default surfaces from diverging.

# Evidence

- Before: C++ fallback Dust 225, Fiendish 3.
- Before: distributed config Dust 225, Fiendish 4.
- Before: Forge Lua library Fiendish 3.
- Selected live rule target: maximum Dust limit 325 and maximum four Fiendish creatures.
- Controlled materializer run `29258043389` succeeded; runner PR #260 was closed without merge and temporary files were removed.

# Safety boundary

- Existing server-owner overrides in `config.lua` remain supported.
- No Player Forge mutation, cost, chance, bonus, protocol, persistence or OTClient code changed.
- The branch is stacked on #250 only for lifecycle sequencing; implementation paths do not overlap #250 gameplay code.

# Completion

- Final status: ready_for_review_pending_final_ci
- PR: #259
- Merge commit:
- Archived at:
