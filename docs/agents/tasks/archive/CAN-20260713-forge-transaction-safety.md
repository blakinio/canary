---
task_id: CAN-20260713-forge-transaction-safety
program_id: CAN-PROGRAM-EQUIPMENT-UPGRADE-PARITY
coordination_id: ""
status: merged
agent: "GPT-5.6 Thinking"
branch: fix/forge-transaction-safety
base_branch: main
created: 2026-07-13T16:02:00+02:00
updated: 2026-07-13T22:30:50+02:00
last_verified_commit: "e16c9f769b1bcdd05e1719e861f0a52cc2594560"
risk: high
related_issue: ""
related_pr: "#257"
depends_on:
  - PR #250 Forge server authority
blocks: []
owned_paths:
  exclusive:
    - docs/agents/tasks/archive/CAN-20260713-forge-transaction-safety.md
  shared:
    - docs/agents/programs/EQUIPMENT_UPGRADE_PARITY_PROGRAM.md
  read_only:
    - src/creatures/players/player.cpp
    - src/game/functions/forge_transaction.hpp
    - tests/unit/players/forge_transaction_test.cpp
    - tests/integration/game/forge_it.cpp
modules_touched:
  - Forge Fusion transaction
  - Forge Transfer transaction
  - Sliver-to-Core transaction
reuses:
  - PR #250 authority policies
  - Game add/remove test mode
public_interfaces:
  - internal Forge transaction helper
cross_repo_tasks: []
---

# Goal

Resolve F-020 and F-021 by making Fusion, Transfer and Sliver-to-Core mutations all-or-nothing.

# Final result

PR #257 was squash-merged on `2026-07-13T20:30:50Z`.

- Final feature head: `501024a25d4538a3e21dee88e8e9219260c77ef2`.
- Squash merge: `e16c9f769b1bcdd05e1719e861f0a52cc2594560`.
- Prices, output tiers and output items are prepared before mutation.
- Supported item operations are preflighted.
- Failed or throwing commit steps restore prior item, stackable-resource and money state in reverse order.
- History, metrics and result packets are emitted only after commit success.
- Sliver-to-Core cannot consume Slivers when the Core cannot be placed.

# Validation and review evidence

- CI `29278815631`: success.
- Agent Task Ownership `29278815411`: success.
- Imbuement Validation `29278815364`: success.
- Autofix `29278815372`: success.
- Linux debug compiled, ran Canary smoke, imported schema and passed full tests.
- Linux release, macOS, Windows and Docker paths passed.
- Focused unit tests cover successful commit, partial failure, exception rollback, reverse ordering and one-shot commit.
- Integration tests cover successful and rejected Sliver-to-Core conversion.

# Safety boundary

No costs, chances, bonus meanings, history text, Premium rule, protocol, persistence schema or client behavior changed.

# Completion

- Final status: merged.
- Feature PR: #257.
- Merge commit: `e16c9f769b1bcdd05e1719e861f0a52cc2594560`.
- Merged at: `2026-07-13T20:30:50Z`.
- Archived at: `docs/agents/tasks/archive/CAN-20260713-forge-transaction-safety.md`.
