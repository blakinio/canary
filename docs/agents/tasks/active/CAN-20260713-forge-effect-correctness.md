---
task_id: CAN-20260713-forge-effect-correctness
program_id: CAN-PROGRAM-EQUIPMENT-UPGRADE-PARITY
coordination_id: ""
status: in_progress
agent: "GPT-5.6 Thinking"
branch: fix/forge-effect-correctness
base_branch: fix/forge-server-authority
created: 2026-07-13T17:10:00+02:00
updated: 2026-07-13T17:10:00+02:00
last_verified_commit: "c79ed3792d2c3f1acfd36fc9dd4485b956d68624"
risk: medium
related_issue: ""
related_pr: ""
depends_on:
  - PR #250 Forge server authority lifecycle
blocks: []
owned_paths:
  exclusive:
    - src/creatures/players/player.cpp
    - src/game/functions/forge_effect_policy.hpp
    - tests/unit/players/forge_effect_policy_test.cpp
    - tests/unit/players/CMakeLists.txt
    - docs/agents/tasks/active/CAN-20260713-forge-effect-correctness.md
  shared:
    - docs/agents/programs/EQUIPMENT_UPGRADE_PARITY_PROGRAM.md
    - docs/ai-agent/OTS_AI_EQUIPMENT_UPGRADE_VALIDATION.md
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - src/creatures/players/components/wheel
modules_touched:
  - Forge Momentum effect
  - Forge Transcendence/Avatar exclusion
  - Forge effect policy tests
reuses:
  - existing Player condition iteration
  - existing Wheel Avatar timers
public_interfaces:
  - internal constexpr Forge effect policy helper
cross_repo_tasks: []
---

# Goal

Resolve F-011 and F-012 without changing probabilities: prevent Forge Transcendence while either spell or Forge Avatar is active, and emit Momentum feedback only when an eligible cooldown was actually reduced.

# Acceptance criteria

- [ ] `triggerTranscendence` checks both `AVATAR_FORGE` and `AVATAR_SPELL` timers against one captured current time.
- [ ] Momentum ignores unrelated conditions and unsupported spell-group cooldowns.
- [ ] Momentum's triggered flag is set only after an eligible cooldown is updated.
- [ ] Deterministic policy tests cover both Avatar timers and Momentum condition boundaries.
- [ ] No chance, duration, visual effect or cooldown-reduction amount changes.
- [ ] Full current-head CI passes before merge.

# Completion

- Final status: in_progress
- PR:
- Merge commit:
- Archived at:
