---
task_id: CAN-20260713-forge-server-authority
program_id: CAN-PROGRAM-EQUIPMENT-UPGRADE-PARITY
coordination_id: ""
status: merged
agent: "GPT-5.6 Thinking"
branch: fix/forge-server-authority
base_branch: main
created: 2026-07-13T13:15:00+02:00
updated: 2026-07-13T17:12:24+02:00
last_verified_commit: "94f8a3b63271b3708e33496e937620a6cd4b9717"
risk: medium
related_issue: ""
related_pr: "#250"
depends_on:
  - PR #89 normal Transfer policy
  - PR #110 Forge history item identity
  - PR #177 Dust reward remediation
blocks: []
owned_paths:
  exclusive:
    - docs/agents/tasks/archive/CAN-20260713-forge-server-authority.md
  shared:
    - docs/agents/programs/EQUIPMENT_UPGRADE_PARITY_PROGRAM.md
  read_only:
    - src/creatures/players/player.cpp
    - src/game/functions/forge_fusion_policy.hpp
    - src/game/functions/forge_transfer_policy.hpp
    - tests/unit/players/forge_test.cpp
    - tests/integration/game/forge_it.cpp
modules_touched:
  - Player Forge Fusion authority
  - Player Forge Transfer authority
  - Forge authority policy helpers
reuses:
  - existing `Player::getForgeItemFromId` validation
  - PR #89 transfer policy
public_interfaces:
  - internal Forge Fusion and Transfer authority policies
cross_repo_tasks: []
---

# Goal

Resolve F-003 through F-005 by making Canary authoritative for normal Fusion, Convergence Fusion and Convergence Transfer before any mutation.

# Final result

PR #250 was squash-merged on `2026-07-13T15:12:24Z`.

- Final feature head: `c79ed3792d2c3f1acfd36fc9dd4485b956d68624`.
- Squash merge: `94f8a3b63271b3708e33496e937620a6cd4b9717`.
- Normal Fusion requires two instances of the same item ID and tier.
- Convergence Fusion requires different class-4 item IDs, the same requested tier and normalized slot.
- Convergence Transfer requires class-4 donor and receiver items.
- Invalid crafted or stale requests are rejected before item, Dust, Core, money, chest or history mutation.

# Validation and review evidence

- CI `29259842029`: success.
- Agent Task Ownership `29259840819`: success.
- Imbuement Validation `29259841072`: success.
- AI Agent Tools `29259840867`: success.
- Lua, Fast Checks, Linux debug/full tests, Linux release, macOS, Windows and Docker passed.
- No unresolved review threads or requested changes remained before merge.

# Safety boundary

No protocol, OTClient, persistence schema, map, binary asset or upstream repository change was included.

# Completion

- Final status: merged.
- Feature PR: #250.
- Merge commit: `94f8a3b63271b3708e33496e937620a6cd4b9717`.
- Merged at: `2026-07-13T15:12:24Z`.
- Archived at: `docs/agents/tasks/archive/CAN-20260713-forge-server-authority.md`.
