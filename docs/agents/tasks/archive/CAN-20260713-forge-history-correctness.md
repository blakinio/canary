---
task_id: CAN-20260713-forge-history-correctness
program_id: CAN-PROGRAM-EQUIPMENT-UPGRADE-PARITY
coordination_id: ""
status: merged
agent: "GPT-5.6 Thinking"
branch: fix/forge-history-correctness
base_branch: main
created: 2026-07-13T21:35:00+02:00
updated: 2026-07-14T09:47:47+02:00
last_verified_commit: "82348f9faca788a8cbb5c13feb75b4e06d8da9dc"
risk: medium
related_issue: ""
related_pr: "#283"
depends_on:
  - PR #257 Forge transaction safety
  - PR #262 Forge Premium Dust
blocks: []
owned_paths:
  exclusive:
    - docs/agents/tasks/archive/CAN-20260713-forge-history-correctness.md
  shared:
    - docs/agents/programs/EQUIPMENT_UPGRADE_PARITY_PROGRAM.md
  read_only:
    - src/creatures/players/player.cpp
    - tests/integration/game/forge_it.cpp
modules_touched:
  - Forge Fusion history description
  - Forge resource-conversion history
reuses:
  - PR #110 stable history item IDs
  - PR #257 post-commit history registration
public_interfaces: []
cross_repo_tasks: []
---

# Goal

Resolve F-022 through F-024 by recording and rendering actual Forge action types and configured amounts.

# Final result

PR #283 was squash-merged on `2026-07-14T07:47:47Z`.

- Final feature head: `2ebe4f601ac627712384293ba45f707cbf945ba7`.
- Squash merge: `82348f9faca788a8cbb5c13feb75b4e06d8da9dc`.
- Failed Fusion history renders `history.dustCost` rather than hard-coded `100 dust`.
- Dust-to-Slivers stores the configured produced amount in `history.gained`.
- Sliver-to-Core retains `SLIVERSTOCORES`.
- Dust-limit increase retains `INCREASELIMIT`.
- Integration tests assert action type, cost, gained value and rendered description.

# Validation and review evidence

- Final ready-state CI `29314898366`: success.
- Earlier clean-head CI `29314793109`: success.
- Agent Task Ownership `29314792864`: success.
- Imbuement Validation `29314792917`: success.
- Autofix `29314898228`: success.
- Lua, Fast Checks, Linux debug/full tests, Linux release, macOS, Windows and Docker passed.
- Changed files: exactly three permanent files.
- Review threads and requested changes: none.

# Safety boundary

No resource cost/output rule, success probability, bonus selection, protocol, persistence schema or OTClient behavior changed.

# Completion

- Final status: merged.
- Feature PR: #283.
- Merge commit: `82348f9faca788a8cbb5c13feb75b4e06d8da9dc`.
- Merged at: `2026-07-14T07:47:47Z`.
- Archived at: `docs/agents/tasks/archive/CAN-20260713-forge-history-correctness.md`.
