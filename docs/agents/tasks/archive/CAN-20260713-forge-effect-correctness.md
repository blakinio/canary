---
task_id: CAN-20260713-forge-effect-correctness
program_id: CAN-PROGRAM-EQUIPMENT-UPGRADE-PARITY
coordination_id: ""
status: merged
agent: "GPT-5.6 Thinking"
branch: fix/forge-effect-correctness
base_branch: main
created: 2026-07-13T17:10:00+02:00
updated: 2026-07-13T18:32:38+02:00
last_verified_commit: "7771bbec22d970d9779bff740e3f7f2e0df42f19"
risk: medium
related_issue: ""
related_pr: "#267"
depends_on:
  - PR #250 Forge server authority
blocks: []
owned_paths:
  exclusive:
    - docs/agents/tasks/archive/CAN-20260713-forge-effect-correctness.md
  shared:
    - docs/agents/programs/EQUIPMENT_UPGRADE_PARITY_PROGRAM.md
  read_only:
    - src/creatures/players/player.cpp
    - src/game/functions/forge_effect_policy.hpp
    - tests/unit/players/forge_effect_policy_test.cpp
modules_touched:
  - Forge Momentum effect
  - Forge Transcendence and Avatar exclusion
reuses:
  - Player condition iteration
  - Wheel Avatar timers
public_interfaces:
  - internal Forge effect policy helper
cross_repo_tasks: []
---

# Goal

Resolve F-011 and F-012 without changing probabilities: block Transcendence while either Avatar source is active and report Momentum only after an eligible cooldown was actually reduced.

# Final result

PR #267 was squash-merged on `2026-07-13T16:32:38Z`.

- Final feature head: `4e6864fd333ca4cc4e4189dd94992bea3af7376b`.
- Squash merge: `7771bbec22d970d9779bff740e3f7f2e0df42f19`.
- `triggerTranscendence` checks both `AVATAR_FORGE` and `AVATAR_SPELL` against one captured time value before chance or effect processing.
- Momentum feedback is emitted only after a supported spell or spell-group cooldown was updated.
- Existing chance, duration, reduction amount, message and visual effect remain unchanged.

# Validation and review evidence

- CI `29262396073`: success.
- Agent Task Ownership `29262382247`: success.
- Imbuement Validation `29262382170`: success.
- Autofix `29262401203`: success.
- Deterministic policy tests cover both Avatar timers and supported/unsupported Momentum condition boundaries.
- Linux, macOS, Windows, Docker, Lua and Fast Checks passed.

# Safety boundary

No protocol, persistence, Lua API, configuration, client, map or asset change was included.

# Completion

- Final status: merged.
- Feature PR: #267.
- Merge commit: `7771bbec22d970d9779bff740e3f7f2e0df42f19`.
- Merged at: `2026-07-13T16:32:38Z`.
- Archived at: `docs/agents/tasks/archive/CAN-20260713-forge-effect-correctness.md`.
