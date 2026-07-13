---
task_id: CAN-20260713-forge-live-defaults
program_id: CAN-PROGRAM-EQUIPMENT-UPGRADE-PARITY
coordination_id: ""
status: in_progress
agent: "GPT-5.6 Thinking"
branch: fix/forge-live-defaults
base_branch: fix/forge-server-authority
created: 2026-07-13T16:28:00+02:00
updated: 2026-07-13T16:28:00+02:00
last_verified_commit: "d5ca8d3ecfa1d83f69184e1f7ba58dd7906693e5"
risk: low
related_issue: ""
related_pr: ""
depends_on:
  - PR #250 Forge server authority lifecycle
blocks: []
owned_paths:
  exclusive:
    - src/config/forge_config_defaults.hpp
    - src/config/configmanager.cpp
    - config.lua.dist
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

- [ ] `FORGE_MAX_DUST` fallback is 325.
- [ ] `config.lua.dist` exposes `forgeMaxDust = 325`.
- [ ] `FORGE_FIENDISH_CREATURES_LIMIT` fallback is 4, matching the existing `config.lua.dist` value.
- [ ] Focused unit test checks both C++ constants and the distributed Lua configuration.
- [ ] No runtime behavior outside default/fallback selection changes.
- [ ] Full current-head CI passes before merge.

# Evidence

- Current C++ fallback: `forgeMaxDust = 225`, `forgeFiendishLimit = 3`.
- Current distributed config: `forgeMaxDust = 225`, `forgeFiendishLimit = 4`.
- Selected live rule target: maximum Dust limit 325 and maximum four Fiendish creatures.

# Design

Centralize the two retail defaults in an internal constexpr header. `ConfigManager` uses those constants as fallback values, while a focused test also parses `config.lua.dist` to prevent the C++ and distributed Lua defaults from diverging.

# Completion

- Final status: in_progress
- PR:
- Merge commit:
- Archived at:
