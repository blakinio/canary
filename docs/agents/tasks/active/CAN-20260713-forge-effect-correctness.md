---
task_id: CAN-20260713-forge-effect-correctness
program_id: CAN-PROGRAM-EQUIPMENT-UPGRADE-PARITY
coordination_id: ""
status: ready_for_merge_pending_final_head_ci
agent: "GPT-5.6 Thinking"
branch: fix/forge-effect-correctness
base_branch: main
created: 2026-07-13T17:10:00+02:00
updated: 2026-07-13T17:29:00+02:00
last_verified_commit: "1e9d204e49cfba72e470682c6ed482ded5b9ed0c"
risk: medium
related_issue: ""
related_pr: "#267"
depends_on:
  - PR #250 Forge server authority, merged as 94f8a3b63271b3708e33496e937620a6cd4b9717
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

- [x] `triggerTranscendence` checks both `AVATAR_FORGE` and `AVATAR_SPELL` timers against one captured current time.
- [x] Momentum ignores unrelated conditions and unsupported spell-group cooldowns.
- [x] Momentum's triggered flag is set only after an eligible cooldown is updated.
- [x] Deterministic policy tests cover both Avatar timers and Momentum condition boundaries.
- [x] No chance, duration, visual effect or cooldown-reduction amount changes.
- [x] Full implementation-head CI `29262236043` passed after synchronization with `main`.
- [ ] Fresh final-head CI passes after this evidence-only task update.

# Confirmed result

- `ForgeEffectPolicy::isAvatarActive` treats either active Avatar timer as a blocker.
- `Player::triggerTranscendence` captures `OTSYS_TIME()` once and checks `AVATAR_FORGE` plus `AVATAR_SPELL` before rolling chance or creating conditions.
- `ForgeEffectPolicy::isMomentumCooldownEligible` accepts spell cooldowns and only spell-group cooldowns above `SPELLGROUP_SUPPORT`.
- `Player::triggerMomentum` sets `triggered` only after updating and sending an eligible cooldown.
- Existing chance, 2000 ms reduction, feedback message, visual effect and Avatar duration remain unchanged.

# Validation

- Permanent diff: this task, `player.cpp`, one internal policy header, one registered unit test and the players unit CMake file.
- Implementation-head CI: `29262236043` — success.
- Agent Task Ownership: `29262235490` — success.
- Imbuement Validation: `29262235377` — success.
- Temporary materialization PR #268 and main-sync PR #271 were closed without merge; all runner files were removed.
- No focused physical-client gameplay proof is claimed; this task provides deterministic policy tests plus repository compile/test/runtime-smoke evidence.

# Compatibility and rollback

- No protocol, persistence, Lua API, configuration, client or asset change.
- Rollback is a squash-revert of PR #267.

# Completion

- Final status: ready_for_merge_pending_final_head_ci
- PR: #267
- Merge commit:
- Archived at: pending lifecycle cleanup
