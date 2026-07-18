---
task_id: CAN-20260718-oteryn-weapons-revalidation
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-015
status: active
agent: "GPT-5.5 Thinking"
branch: docs/oam-015-weapons-revalidation
base_branch: main
created: 2026-07-18
updated: 2026-07-18T15:38:00+02:00
last_verified_commit: "9d797b547c3f85f6d210c6123202c7cae32d5133"
risk: high
related_issue: "blakinio/Otheryn#36"
related_pr: "blakinio/Otheryn#37"
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

OAM-002 whole-tree evidence establishes the target weapons server/data boundary from exact pinned upstream content, and no later target or upstream production change through the task-start pins touches that canonical boundary. Representative target/upstream blobs are `weapons.cpp` `4094a124e42263047b81a459d93b187aeca25c7f` and `weapons.hpp` `093c58aef02b4f2ea44b21796ba697ca0a2e7add`.

Merged legacy PR #78 is explicitly reviewed rather than ignored. Its wand/Cyclopedia display fix is a coordinated cross-module change across item parsing, `weapons.cpp` and protocol serialization; it removes the wand `const_cast` only after moving metadata publication into item parsing and changing displayed attack totals, and it explicitly does not alter the actual wand damage roll. Importing only the `weapons.cpp` deletion would split the fix. OAM-015 therefore records the unresolved upstream #3645 wand-display/client-crash risk but does not partially migrate or claim closure of that cross-module gap.

# Target proof

Otheryn issue #36 and PR #37 own a tests-only runtime proof package. Accepted target scope is limited to `tests/unit/items/CMakeLists.txt` and `tests/unit/items/weapon_reuse_test.cpp`; no production gameplay module file is mutated.

Focused proof covers deterministic core damage helpers and deterministic wand maximum damage only. An earlier metadata-display assertion was removed after PR #78 provenance review so the test does not freeze the unresolved display implementation as a correctness invariant.

Required gates: exact-head CI/Required/autofix, standard Linux debug build/runtime/database/test proof, full CTest with zero failures, focused test pass, exact accepted diff, clean comments/reviews/threads, target-main drift check and exact-head merge.

# Exclusions

No exhaustive gameplay formula, hit-chance, resource-consumption or individual script parity claim. No wand/Cyclopedia display compatibility or upstream #3645 closure claim. No partial PR #78 migration. No generic combat, spell/rune, vocation, proficiency, protocol, client, map, asset or persistence redesign. Preserve OAM-004 SQL/KV non-atomicity and completed OAM-006/OAM-007 ownership.

# Lifecycle

OAM-016 remains blocked until target proof, Canary governance feature, separate lifecycle archive and separate durable program reconciliation all merge. Any self-owned automatically opened `docs(agents): archive merged PR` must also be closed after it has served its lifecycle purpose.
