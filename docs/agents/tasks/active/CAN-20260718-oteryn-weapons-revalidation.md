---
task_id: CAN-20260718-oteryn-weapons-revalidation
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-015
status: active
agent: "GPT-5.5 Thinking"
branch: docs/oam-015-weapons-revalidation
base_branch: main
created: 2026-07-18
updated: 2026-07-18T15:18:00+02:00
last_verified_commit: "051f4101cac5250dd41d8aa0914fcc8761b08d64"
risk: high
related_issue: "blakinio/Otheryn#36"
related_pr: "pending"
depends_on:
  - OAM-013
blocks:
  - OAM-016
modules_touched:
  - weapons
---

# Goal

Revalidate the canonical Oteryn MMORPG `weapons` gameplay module against immutable task-start baselines and accept only the strongest evidence-backed target implementation.

# Baselines

- Canary: `051f4101cac5250dd41d8aa0914fcc8761b08d64`
- Otheryn: `9d797b547c3f85f6d210c6123202c7cae32d5133`
- upstream: `691614c1a302aee776002ca3851eca399be1a82c`
- OTClient: `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`

# Canonical boundary

The virtual MMORPG gameplay module owns `src/items/weapons/**` and `data/scripts/weapons/**`. Its only hard dependency is completed canonical module `combat`.

# Provisional disposition

`weapons → REUSE`, pending exact-target proof.

Otheryn and latest upstream share exact `weapons.cpp` blob `4094a124e42263047b81a459d93b187aeca25c7f` and `weapons.hpp` blob `093c58aef02b4f2ea44b21796ba697ca0a2e7add`. Legacy Canary has the same header but runtime blob `ba3bc8f564601993780c15ac532b52b433f33944`; reviewed legacy difference omits current upstream/target wand metadata publication and is not a stronger donor.

# Target proof

Otheryn issue #36 owns a tests-only proof package. Add focused unit coverage under `tests/unit/items/` and mutate no production gameplay module file unless new isolated evidence proves a target defect.

Required gates: exact-head CI/Required/autofix, standard Linux debug build/runtime/database/test proof, full CTest with zero failures, focused test pass, exact accepted diff, clean comments/reviews/threads, target-main drift check and exact-head merge.

# Exclusions

No exhaustive gameplay formula, hit-chance, resource-consumption or individual script parity claim. No generic combat, spell/rune, vocation, proficiency, protocol, client, map, asset or persistence redesign. Preserve OAM-004 SQL/KV non-atomicity.

# Lifecycle

OAM-016 remains blocked until target proof, Canary governance feature, separate lifecycle archive and separate durable program reconciliation all merge.
