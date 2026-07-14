---
task_id: CAN-20260713-forge-live-defaults
program_id: CAN-PROGRAM-EQUIPMENT-UPGRADE-PARITY
coordination_id: ""
status: merged
agent: "GPT-5.6 Thinking"
branch: fix/forge-live-defaults
base_branch: main
created: 2026-07-13T16:28:00+02:00
updated: 2026-07-13T18:35:39+02:00
last_verified_commit: "444aa8ae13edc01c6e77b03139a43d386b437308"
risk: low
related_issue: ""
related_pr: "#259"
depends_on:
  - PR #250 Forge server authority
blocks: []
owned_paths:
  exclusive:
    - docs/agents/tasks/archive/CAN-20260713-forge-live-defaults.md
  shared:
    - docs/agents/programs/EQUIPMENT_UPGRADE_PARITY_PROGRAM.md
  read_only:
    - src/config/forge_config_defaults.hpp
    - src/config/configmanager.cpp
    - config.lua.dist
    - data/libs/systems/exaltation_forge.lua
    - tests/unit/game/forge_config_test.cpp
modules_touched:
  - Forge configuration defaults
  - Forge Lua Fiendish limit
reuses:
  - existing ConfigManager keys
public_interfaces:
  - internal Forge default constants
cross_repo_tasks: []
---

# Goal

Resolve F-001 and F-002 by aligning the selected live defaults to maximum Dust `325` and maximum Fiendish creatures `4`.

# Final result

PR #259 was squash-merged on `2026-07-13T16:35:39Z`.

- Final feature head: `9d8a82cc25450b58a85619e0f3c520a9bbf964b3`.
- Squash merge: `444aa8ae13edc01c6e77b03139a43d386b437308`.
- C++ fallback and `config.lua.dist` now use Dust limit `325`.
- C++ fallback, distributed config and Forge Lua library now use Fiendish limit `4`.
- Focused tests read all maintained default surfaces to prevent drift.
- Server-owner overrides remain supported.

# Validation and review evidence

- CI `29266052589`: success.
- Agent Task Ownership `29266053829`: success.
- Imbuement Validation `29266052596`: success.
- Autofix `29266053916`: success.
- Lua, Fast Checks, Linux, macOS, Windows and Docker paths passed.

# Safety boundary

No Player mutation, resource price, chance, bonus, protocol, persistence or OTClient behavior changed.

# Completion

- Final status: merged.
- Feature PR: #259.
- Merge commit: `444aa8ae13edc01c6e77b03139a43d386b437308`.
- Merged at: `2026-07-13T16:35:39Z`.
- Archived at: `docs/agents/tasks/archive/CAN-20260713-forge-live-defaults.md`.
