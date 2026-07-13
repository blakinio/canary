---
task_id: CAN-20260713-forge-history-correctness
program_id: CAN-PROGRAM-EQUIPMENT-UPGRADE-PARITY
coordination_id: ""
status: in_progress
agent: "GPT-5.6 Thinking"
branch: fix/forge-history-correctness
base_branch: fix/forge-transaction-safety
created: 2026-07-13T21:35:00+02:00
updated: 2026-07-13T21:35:00+02:00
last_verified_commit: "501024a25d4538a3e21dee88e8e9219260c77ef2"
risk: medium
related_issue: ""
related_pr: ""
depends_on:
  - PR #257 Forge transaction safety
blocks:
  - final Forge parity audit
owned_paths:
  exclusive:
    - src/creatures/players/player.cpp
    - tests/integration/game/forge_it.cpp
    - docs/agents/tasks/active/CAN-20260713-forge-history-correctness.md
  shared: []
  read_only:
    - src/creatures/players/player.hpp
    - src/enums/forge.hpp
modules_touched:
  - Forge Fusion history description
  - Forge resource-conversion history
  - Forge history integration tests
reuses:
  - PR #110 stable item IDs in Forge history
  - PR #257 post-commit history registration
public_interfaces: []
cross_repo_tasks: []
---

# Goal

Resolve F-022 through F-024 by recording and rendering the actual Forge action and configured resource amounts without changing transaction behavior, costs or protocol.

# Acceptance criteria

- [ ] Failed Fusion history renders `history.dustCost`, never a hard-coded 100.
- [ ] Dust-to-Slivers stores the configured produced amount in `history.gained`.
- [ ] Sliver-to-Core history retains `SLIVERSTOCORES`.
- [ ] Dust-limit increase history retains `INCREASELIMIT`.
- [ ] Integration tests assert action type, cost, gained value and description for every resource conversion.
- [ ] Existing transaction and authority regressions stay green.
- [ ] Full final-head CI passes before merge.

# Scope boundary

No change to resource prices, output quantities, Fusion success/bonus selection, protocol fields, OTClient presentation or persistence schema.

# Completion

- Final status: in_progress
- PR:
- Merge commit:
- Archived at:
