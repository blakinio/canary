---
task_id: CAN-20260723-oteryn-oam038-preflight
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
status: ready
agent: "GPT-5.6 Thinking"
branch: dudantas/oam-038-preflight
base_branch: main
created: 2026-07-23
updated: 2026-07-23
last_verified_commit: "61163f5d9006351b9eaad799bd9dd0f825529db1"
risk: medium
related_issue: ""
related_pr: "763"
depends_on:
  - OAM-037 formally complete
blocks:
  - OAM-038 target proof/delivery selection
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260723-oteryn-oam038-preflight.md
  shared: []
  read_only:
    - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
    - docs/agents/real-tibia/registry/modules/**
modules_touched:
  - oteryn-architecture-migration
  - world-zones
cross_repo_tasks: []
---

# OAM-038 Fresh Preflight

## Goal

Perform a fresh dependency-valid canonical-module preflight after formal OAM-037 closure. Do not implement OAM-038 in this task.

## Selected package

`world-zones` is the selected dependency-valid OAM-038 canonical package.

Preflight disposition: `REUSE candidate`.

The final OAM-038 disposition still requires bounded target-side proof. This preflight does not claim zone membership or eviction correctness under all movement/reload/concurrency cases, tile protection/PvP semantics, quest/event behavior inside zones, instance-region allocation correctness, physical-client E2E or Real Tibia parity.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-23T11:22:00+02:00
head: c309f51f0ceead41c7b285fa04ee382f2631bb3d
branch: dudantas/oam-038-preflight
pr: 763
status: ready
context_routes:
  - agent-governance
  - cross-repo
owned_paths:
  - docs/agents/tasks/active/CAN-20260723-oteryn-oam038-preflight.md
proven:
  - OAM-037 is formally complete after Canary durable reconciliation merge 61163f5d9006351b9eaad799bd9dd0f825529db1 and Otheryn target archive merge 651ff1c6261eb25bd0992d7530e50e3690c2b5de.
  - Fresh Canary main baseline is 61163f5d9006351b9eaad799bd9dd0f825529db1.
  - Fresh Otheryn main baseline is 651ff1c6261eb25bd0992d7530e50e3690c2b5de.
  - Fresh upstream Canary baseline is 7323503b3dc61ed86bf1f04a611b2d0aec64b35a.
  - Fresh maintained OTClient baseline is 1e5305395159142634f182d9e888e5f9164228c6.
  - Canonical world-zones depends only on world-map-runtime; OAM-007 completed world-map-runtime as REUSE.
  - Canonical world-zones ownership is bounded to the Zone registry by name id and position static and dynamic zones area indexing membership caches remove destinations bulk creature/item removal refresh and monster-variant metadata.
  - Tile protection and PvP flag semantics quest/event scripting inside zones instance-region allocation and proof of complete gameplay correctness remain excluded ownership boundaries.
  - Otheryn and fresh upstream share exact canonical zone.cpp blob f80af238eb2b4b10193a9b5961652591d9dafeb5 and zone.hpp blob d413dccc690d37dc1a24af6c5d2e630b14b087d1.
  - Legacy Canary diverges on zone.cpp as blob 99346f8190a023964f027bf9ae1ac5ba4dce1a28 and zone.hpp as blob b8cbfdc9935fac88ee5288db04c4e6247293ee22.
  - Target and fresh upstream protect weak membership-cache reads writes removals and refresh with cacheMutex while the reviewed legacy core lacks the same mutex protection and typed weak-pointer removal safeguards.
  - Fresh open-PR searches found no overlapping world-zones or OAM-038 writer in Canary or Otheryn and branch searches found no OAM-038 or world-zones branch.
  - The world-zones registry has no client paths so the maintained OTClient head does not create a direct client mutation requirement for this preflight.
derived:
  - world-zones is the selected dependency-valid OAM-038 canonical package because it is a smaller independent lifecycle boundary than instances or broader spawn/NPC/quest content surfaces and its sole hard dependency is already complete.
  - Whole-module legacy import is not justified because the target matches fresh upstream on both canonical roots and the reviewed legacy roots are older at the membership-cache concurrency boundary.
  - The smallest evidence-backed preflight outcome is world-zones as a REUSE candidate pending bounded target-side semantic proof.
unknown:
  - Exact focused target proof boundary and resulting final REUSE or ADAPT disposition until OAM-038 target-side validation executes.
  - Whether bounded proof exposes a concrete world-zones-owned target defect outside the reviewed registry indexing and cache-synchronization core.
conflicts: []
first_failure:
  marker: none
  evidence: No OAM-038 implementation or target validation failure exists because this task is preflight-only.
rejected_hypotheses:
  - Select instances first; instances is a broader active runtime surface with additional isolation cleanup expiration and arena-consumer interactions while world-zones is the smaller independent dependency-valid boundary.
  - Select spawns or NPCs first; those are data-heavy placement/content surfaces and world-zones offers a tighter two-root runtime boundary with an already-completed hard dependency.
  - Infer final REUSE from blob identity alone; final disposition remains gated on target-side semantic proof.
  - Prefer divergent legacy zone roots as a stronger donor; target and fresh upstream contain cacheMutex protection and safer weak-cache removal behavior absent from the reviewed legacy core.
  - Expand world-zones into tile PvP flags quest/event scripting instance allocation or physical-client orchestration because those are separate ownership boundaries.
changed_paths:
  - docs/agents/tasks/active/CAN-20260723-oteryn-oam038-preflight.md
validation:
  - command: fresh dependency ownership baseline and open-PR/branch preflight
    result: PASS
    evidence: sole hard dependency world-map-runtime is complete exact baselines are pinned and no overlapping world-zones or OAM-038 writer was found
  - command: exact-root and semantic donor preflight
    result: PASS
    evidence: target and fresh upstream share both canonical zone roots while legacy diverges and lacks reviewed membership-cache synchronization safeguards
blockers: []
next_action: Require exact-current-head Agent Task Ownership and CI success on PR 763, audit the one-file preflight scope and review state, then expected-head squash merge before creating the bounded world-zones target proof in Otheryn.
```
