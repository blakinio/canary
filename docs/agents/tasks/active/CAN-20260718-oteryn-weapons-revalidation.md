---
task_id: CAN-20260718-oteryn-weapons-revalidation
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-015
status: active
agent: "GPT-5.5 Thinking"
branch: docs/oam-015-virtual-module-revalidation
base_branch: main
created: 2026-07-18
updated: 2026-07-18T16:01:00+02:00
last_verified_commit: "1dd21117ce06cc4463e6185f4ff74546031b55e6"
risk: high
related_issue: "blakinio/Otheryn#36"
related_pr: "544"
depends_on:
  - OAM-013
blocks:
  - OAM-016
modules_touched:
  - weapons
---

# Goal

Revalidate canonical OAM-015 virtual MMORPG equipment-combat gameplay ownership against immutable task-start baselines and accept only the strongest evidence-backed target implementation.

# Final disposition

```text
weapons → REUSE
```

# Immutable task-start baselines

- Canary: `051f4101cac5250dd41d8aa0914fcc8761b08d64`
- Otheryn: `9d797b547c3f85f6d210c6123202c7cae32d5133`
- upstream: `691614c1a302aee776002ca3851eca399be1a82c`
- OTClient: `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`

# Evidence decision

OAM-002 whole-tree verification established the canonical OAM-015 production boundary from exact pinned upstream content, and no later target/upstream production change through the task-start pins touched that boundary. Representative exact blobs were `weapons.cpp` `4094a124e42263047b81a459d93b187aeca25c7f` and `weapons.hpp` `093c58aef02b4f2ea44b21796ba697ca0a2e7add`.

Merged legacy PR #78 was reviewed explicitly. Its virtual display-stat compatibility correction is a coordinated cross-module change spanning item parsing, the OAM-015 runtime file and protocol serialization. OAM-015 does not import only one fragment or reopen completed OAM-006/OAM-007 ownership. The related upstream #3645 display compatibility issue remains a separately recorded gap; no display-parity or physical-client closure is claimed here.

# Target proof

```text
Otheryn issue #36: CLOSED / completed
Otheryn PR #37 final head: 183800b4a83f86ec0b5eb160501f293d9ae59399
target squash merge: 1dd21117ce06cc4463e6185f4ff74546031b55e6
CI #121: 29646448123 SUCCESS
Required #111: 29646448049 SUCCESS
autofix.ci #104: 29646448054 SUCCESS
Linux debug runtime smoke: PASS
database schema import: PASS
full CTest: 353/353 PASS
focused OAM-015 tests: 2/2 PASS
primary artifact: 8430298608
digest: sha256:5e2bca685d11fce37b6e71a80fe82346c8a6b3d9a3bca95bf127122f2cf1e9b8
```

Final target diff contained exactly two test paths and no production runtime/data change. Immediately before expected-head squash merge, comments, reviews and review threads were all empty, and target `main` remained exactly the task-start baseline.

# Exclusions

- no exhaustive gameplay formula or hit-rate parity claim;
- no exhaustive resource-consumption or individual-script parity claim;
- no virtual display compatibility or upstream #3645 closure claim;
- no partial migration of PR #78;
- no generic combat, spell, vocation or proficiency redesign;
- no protocol/client/map/asset mutation;
- no persistence redesign;
- preserve OAM-004 SQL/KV non-atomicity and completed OAM-006/OAM-007/OAM-013/OAM-014 ownership.

# Lifecycle

Target proof is complete. Canary governance PR #544 must merge next, followed by a separate authoritative lifecycle archive and separate durable program reconciliation. OAM-016 remains blocked until all three remaining stages merge.

Any self-owned automatically opened `docs(agents): archive merged PR` duplicate must be closed after the authoritative manual lifecycle archive is established. Stale duplicates for completed OAM-010 through OAM-014 were closed during OAM-015 housekeeping.
