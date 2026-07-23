---
task_id: CAN-20260723-oteryn-oam041-preflight
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-041
status: blocked
agent: "GPT-5.6 Thinking"
branch: dudantas/oam-041-target-proof-plan
base_branch: main
created: 2026-07-23
updated: 2026-07-23
last_verified_commit: "82da6f6c5284b13446c5e71d075e7b06c9252b67"
risk: medium
related_issue: ""
related_pr: "819"
depends_on:
  - OAM-040 formally complete
blocks:
  - OAM-041 target proof and final disposition
  - OAM-042 start
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260723-oteryn-oam041-preflight.md
  shared: []
  read_only:
    - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
    - docs/agents/OTERYN_TARGET_ARCHITECTURE_CONTRACT.md
    - docs/agents/real-tibia/registry/modules/spawns.yaml
    - docs/agents/real-tibia/registry/modules/raids.yaml
    - docs/agents/real-tibia/registry/modules/npcs.yaml
    - docs/agents/real-tibia/registry/modules/quests.yaml
    - docs/ai-agent/OTS_OTBM_TOOLING_ROADMAP.md
    - docs/ai-agent/OTBM_SPAWN_NPC_VALIDATION.md
    - tools/ai-agent/otbm_spawn_npc.py
    - tools/ai-agent/otbm_spawn_npc_validation.py
    - tools/ai-agent/otbm_spawn_npc_tool.py
modules_touched:
  - oteryn-architecture-migration
  - spawns
cross_repo_tasks: []
---

# OAM-041 Fresh Preflight

## Selected package

`spawns` is the selected dependency-valid OAM-041 canonical package.

Preflight disposition: `REUSE candidate`.

Canonical `spawns` is a world-content module whose only hard dependency is canonical `otbm-tooling`, now formally resolved as an external Canary laboratory/evidence responsibility by OAM-040. The active global monster and NPC spawn XML roots are exact-blob identical across the fresh Otheryn target, fresh upstream Canary baseline and current Canary legacy/evidence baseline. This identity is selection evidence only: final `REUSE` remains gated on bounded target-side proof using pinned Canary OTBM tooling/report provenance, explicit active datapack selection and evidence that no concrete spawns-owned target defect requires `ADAPT`.

`spawns` is selected ahead of `npcs` and `quests` because it is the smaller dependency-valid world-content boundary with dedicated deterministic spawn/boss/NPC evidence tooling already available. `npcs` additionally owns dialogue, shops, travel and quest hooks; `quests` owns storage transitions, actions, map mechanics, rewards and depends on both `otbm-tooling` and `player-persistence`.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-23T18:44:00+02:00
head: b1727677e6534c5f2c71d63db3cd2661e84d8cea
branch: dudantas/oam-041-target-proof-plan
pr: 819
status: blocked
context_routes:
  - agent-governance
  - otbm
  - cross-repo
owned_paths:
  - docs/agents/tasks/active/CAN-20260723-oteryn-oam041-preflight.md
proven:
  - OAM-040 is formally complete after Canary durable reconciliation 115f3ac2fffc36bb4e415c2a6fb45908d9538ba3 and Otheryn target-task archive 9369b0719ff94997a9cf5a2d62853939744e6338.
  - OAM-041 preflight PR 813 final head d2fcc0572d2268d7f88ab8faae9eec8006697f5b changed exactly one task path, passed Agent Task Ownership run 30023734524, initial CI run 30023735027 and ready-state full final-gate CI run 30023784205, had zero comments reviews and review threads, and squash-merged as 82da6f6c5284b13446c5e71d075e7b06c9252b67.
  - Fresh Otheryn main remains 9369b0719ff94997a9cf5a2d62853939744e6338 with no open OAM-041 spawns PR and no OAM-041 branch.
  - Fresh upstream Canary baseline is 7323503b3dc61ed86bf1f04a611b2d0aec64b35a and maintained OTClient baseline is 1e5305395159142634f182d9e888e5f9164228c6.
  - Canonical spawns registry record blob 10d69a10a66610a19116f96f4d32e88a41ced0b5 depends only on otbm-tooling and owns static spawns dynamic creation inventory raids boss placement and definition-to-placement correlation while excluding monster combat AI and Bosstiary award logic.
  - Canonical raids is a separate interacting module whose scope owns raid registry scheduling event ordering reset and reload lifecycle while explicitly excluding generic static spawn placement; OAM-041 must not remigrate or duplicate the OAM-037 raid lifecycle proof.
  - Active global monster and NPC spawn roots are exact across Otheryn target upstream Canary and current Canary legacy evidence: otservbr-monster.xml blob 65e87a4134a320d28b2270fa5a17917fc7b513a1 and otservbr-npc.xml blob 0a72085b7bbdfca73b794e631cc2bab790d8fcef.
  - Otheryn and fresh upstream share spawn_monster.cpp blob 4c82217631ddf479faa5443025d43f99a0c927d1 and spawn_npc.cpp blob 21718ad80827a16e9a1b29bc9d649ad603bcf216 while current Canary legacy differs at blobs 8513d3c60d43021ee8b1305552b0e6294f8d4451 and 5d7c6c809f9eea339bea9b260691f0f15b6e9dd5 respectively.
  - Target and fresh upstream schedule periodic monster checks delayed non-blockable monster spawns periodic NPC checks and delayed NPC spawns on DispatcherLane::Maintenance, while the reviewed current Canary legacy call sites omit the Maintenance lane argument; legacy is therefore not a stronger whole-module donor for the reviewed scheduling surface.
  - Target monster spawn lifecycle loads center coordinates radius direction x-y offsets fixed center z weight and spawntime, uses default respawn fallback and configured rate/event/boost scaling with one-second to one-day bounds, enforces boss exclusivity in a spawn block, blocks configured spawns around players, cleans removed monsters, and preserves weighted monster selection.
  - Target NPC spawn lifecycle loads center coordinates radius direction x-y offsets fixed center z and bounded spawntime, resolves NPC types, blocks respawns around players, cleans removed NPCs, and runs respawn scheduling on the maintenance lane.
  - Current Canary external spawn proof tooling is pinned by otbm_spawn_npc.py blob 4339e94f5875f4d7fd443c2359c15d10f205004f otbm_spawn_npc_validation.py blob 7f66f74b68b66e9acabe1ea1a5cbd404b1637e9b and otbm_spawn_npc_tool.py blob 481c163d8048298900b33648b08b1fac5b60fefe.
  - Spawn/NPC validation documentation blob 0bd5242d919550f0fd97424afef5a0f1ae2ca89b defines explicit active-datapack inputs world/otservbr-monster.xml and world/otservbr-npc.xml with no datapack mixing and fail-closed path XML and unresolved-Lua handling.
  - The OTBM tooling roadmap records Phase 4 Spawns bosses and NPCs as merged and archived and requires static source/map evidence to remain distinct from live gameplay proof.
  - Prior OAM-037 and OAM-038 REUSE deliveries establish a target pattern of task record proof document source-contract unit test and tests/unit/game/CMakeLists.txt registration with no production mutation when the target implementation is already canonical.
derived:
  - REUSE remains the leading disposition because explicit active spawn XML roots match target upstream and legacy exactly and the reviewed target runtime spawn scheduling surface is at least as strong as fresh upstream and stronger than legacy on maintenance-lane isolation.
  - The smallest evidence-backed target package is expected to be four paths with no production mutation: docs/agents/tasks/active/OTH-20260723-oam041-spawns-reuse.md, docs/oam-041-spawns-reuse.md, tests/unit/game/oam_041_spawns_reuse_test.cpp and tests/unit/game/CMakeLists.txt.
  - The source-contract test should assert monster and NPC XML load/startup/clear lifecycle, center-plus-offset placement with center z, interval validation and scaling, player blocking, removed-creature cleanup, boss exclusivity and weighted monster selection, plus maintenance-lane periodic and delayed respawn scheduling.
  - The target proof document should pin the exact Canary validator tool blobs, explicit Otheryn active datapack inputs, exact World Index/reachability artifact provenance used for the run, and bounded scan results for static spawn placement definition correlation boss placement and supported literal dynamic creation.
  - Dynamic Lua registrations not resolved by the existing validator must remain explicitly unresolved rather than guessed, and no binary map or generated report mutation is authorized by OAM-041 proof.
  - Raid scheduling and ordered event execution remain owned by the already-proven raids module; OAM-041 may consume raid-created-monster placement evidence but must not duplicate or broaden OAM-037 lifecycle ownership.
  - ADAPT is permitted only if bounded target proof isolates a concrete spawns-owned target defect; donor evidence does not authorize blind source datapack or map replacement.
unknown:
  - Actual Otheryn OAM-041 deterministic scan findings because the pinned Canary validator has not yet been executed against the current target checkout and its exact World Index/reachability artifact set.
  - Exact evidence artifact hashes for the target proof run until that separately authorized execution occurs.
  - Whether bounded target proof exposes a concrete spawns-owned defect requiring ADAPT.
conflicts: []
first_failure:
  marker: OAM-041 target proof repository write and execution boundary
  evidence: Current execution authority permits repository writes only in blakinio/canary while the mandatory target proof package must be created and validated in blakinio/Otheryn; the deterministic OTBM scan also requires a target checkout and pinned local evidence artifacts not available through the read-only GitHub connector alone.
rejected_hypotheses:
  - Finalize spawns as REUSE from exact XML blob identity alone; architecture requires semantic and target-side proof.
  - Import the current Canary legacy spawn runtime as a stronger donor; reviewed legacy scheduling lacks the target upstream Maintenance lane arguments.
  - Copy Canary OTBM tooling into Otheryn; OAM-040 explicitly resolved otbm-tooling as an external Canary evidence dependency.
  - Re-prove or migrate raid scheduling inside OAM-041; canonical raids owns that lifecycle and OAM-037 already delivered its target proof.
  - Guess unresolved dynamic Lua placements or modify OTBM binaries generated reports or maps; world-content safety and OTBM tooling contracts forbid this.
changed_paths:
  - docs/agents/tasks/active/CAN-20260723-oteryn-oam041-preflight.md
validation:
  - command: PR 813 exact-final-head ownership and ready-state full final-gate CI
    result: PASS
    evidence: head d2fcc0572d2268d7f88ab8faae9eec8006697f5b passed runs 30023734524 30023735027 and 30023784205 before squash merge 82da6f6c5284b13446c5e71d075e7b06c9252b67
  - command: PR 813 scope and review audit
    result: PASS
    evidence: exactly one changed task path with zero comments submitted reviews and inline review threads
  - command: fresh Otheryn overlap and main check
    result: PASS
    evidence: main remains 9369b0719ff94997a9cf5a2d62853939744e6338 with no open OAM-041 spawns PR and no OAM-041 branch
  - command: read-only target upstream legacy spawn runtime comparison
    result: PASS
    evidence: target and upstream share exact spawn runtime blobs and Maintenance-lane scheduling absent from the reviewed current Canary legacy call sites
  - command: target REUSE proof boundary analysis
    result: PASS
    evidence: prior REUSE pattern plus current source and external evidence contracts support an expected four-path no-production-mutation target proof package
blockers:
  - Current execution authority permits writes only in blakinio/canary; OAM-041 target proof requires a separately authorized blakinio/Otheryn write and local evidence-execution context.
next_action: Continue OAM-041 in a separately authorized blakinio/Otheryn context by creating the expected four-path spawns REUSE proof package, execute the pinned Canary OTBM spawn validator against explicit current Otheryn active datapack and exact World Index/reachability provenance, run exact-head target gates, and reclassify to ADAPT only if a concrete spawns-owned proof failure requires bounded production or data repair.
```
