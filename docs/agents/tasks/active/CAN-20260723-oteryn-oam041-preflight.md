---
task_id: CAN-20260723-oteryn-oam041-preflight
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-041
status: blocked
agent: "GPT-5.6 Thinking"
branch: dudantas/oam-041-compact-handover
base_branch: main
created: 2026-07-23
updated: 2026-07-23
last_verified_commit: "0a2ae8e3d504ab2398395820512cd45f3b169722"
risk: medium
related_issue: ""
related_pr: "840"
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
    - docs/ai-agent/OTBM_SPAWN_NPC_VALIDATION.md
    - tools/ai-agent/otbm_spawn_npc*.py
modules_touched:
  - oteryn-architecture-migration
  - spawns
cross_repo_tasks: []
---

# OAM-041 Fresh Preflight

Selected package: `spawns`.

Preflight disposition: `REUSE candidate`.

Final disposition remains gated on bounded target-side proof in `blakinio/Otheryn`. Current execution authority permits repository writes only in `blakinio/canary`.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-23T23:59:00+02:00
head: c67f0e6e62636b1f80601c068c97478e57324288
branch: dudantas/oam-041-compact-handover
pr: 840
status: blocked
context_routes:
  - agent-governance
  - otbm
  - cross-repo
owned_paths:
  - docs/agents/tasks/active/CAN-20260723-oteryn-oam041-preflight.md
proven:
  - OAM-040 is formally complete after Canary durable reconciliation 115f3ac2fffc36bb4e415c2a6fb45908d9538ba3 and Otheryn target-task archive 9369b0719ff94997a9cf5a2d62853939744e6338.
  - OAM-041 preflight PR 813 final head d2fcc0572d2268d7f88ab8faae9eec8006697f5b passed Agent Task Ownership 30023734524 and ready-state full final-gate CI 30023784205 and squash-merged as 82da6f6c5284b13446c5e71d075e7b06c9252b67.
  - OAM-041 target-proof-plan PR 819 final head 61262b1f2ac03bd04d41221e7d3983b4dcad124b passed Agent Task Ownership 30026360598 and CI 30026360872 and squash-merged as 5c2ec1df1b5be9494fbf97ba389bea8fd9070f58.
  - Current Canary main verified at 0a2ae8e3d504ab2398395820512cd45f3b169722; later unrelated main drift does not change the OAM-041 blocker.
  - Current Otheryn main remains 9369b0719ff94997a9cf5a2d62853939744e6338 with no OAM-041 target delivery found.
  - Canonical spawns depends only on resolved otbm-tooling; active global monster and NPC spawn XML roots remain exact across Otheryn upstream and Canary at blobs 65e87a4134a320d28b2270fa5a17917fc7b513a1 and 0a72085b7bbdfca73b794e631cc2bab790d8fcef.
  - Otheryn and fresh upstream share spawn_monster.cpp blob 4c82217631ddf479faa5443025d43f99a0c927d1 and spawn_npc.cpp blob 21718ad80827a16e9a1b29bc9d649ad603bcf216; reviewed legacy Canary roots differ and omit DispatcherLane::Maintenance scheduling at the corresponding call sites.
  - Current Canary spawn proof tooling remains pinned by otbm_spawn_npc.py 4339e94f5875f4d7fd443c2359c15d10f205004f otbm_spawn_npc_validation.py 7f66f74b68b66e9acabe1ea1a5cbd404b1637e9b and otbm_spawn_npc_tool.py 481c163d8048298900b33648b08b1fac5b60fefe.
  - Expected target REUSE proof package is four paths: docs/agents/tasks/active/OTH-20260723-oam041-spawns-reuse.md, docs/oam-041-spawns-reuse.md, tests/unit/game/oam_041_spawns_reuse_test.cpp and tests/unit/game/CMakeLists.txt, with no production mutation unless proof isolates a concrete spawns-owned defect.
  - Raid registry scheduling and ordered event lifecycle remain owned by canonical raids and the completed OAM-037 proof; OAM-041 must not duplicate that ownership.
derived:
  - REUSE remains the leading disposition because target and upstream runtime roots align and active spawn XML roots match, while legacy is not a stronger donor on maintenance-lane scheduling.
  - The target proof must consume external Canary OTBM evidence provenance rather than copy the toolchain into Otheryn.
  - ADAPT is allowed only for a concrete spawns-owned proof failure; donor or map evidence cannot authorize blind source datapack or map replacement.
  - OAM-042 must not start until OAM-041 target proof governance lifecycle durable reconciliation and target-task archive are complete.
unknown:
  - Actual Otheryn OAM-041 deterministic scan findings because the pinned Canary validator has not been executed against the current target checkout and exact World Index/reachability artifacts.
  - Exact target evidence artifact hashes until separately authorized local execution occurs.
  - Whether bounded target proof exposes a concrete spawns-owned defect requiring ADAPT.
conflicts: []
first_failure:
  marker: OAM-041 target proof repository write and execution boundary
  evidence: Repository writes are allowed only in blakinio/canary while the mandatory four-path proof must be created and validated in blakinio/Otheryn; the deterministic scan also requires a target checkout and pinned local evidence artifacts.
rejected_hypotheses:
  - Finalize REUSE from XML blob identity alone: target-side semantic and placement proof is mandatory.
  - Import legacy Canary spawn runtime as a stronger donor: reviewed legacy call sites lack the target upstream Maintenance lane scheduling.
  - Copy Canary OTBM tooling into Otheryn: OAM-040 resolved otbm-tooling as an external Canary evidence dependency.
  - Re-prove raid scheduling inside OAM-041: canonical raids owns that lifecycle and OAM-037 already delivered it.
changed_paths:
  - docs/agents/tasks/active/CAN-20260723-oteryn-oam041-preflight.md
validation:
  - command: PR 813 exact-final-head ownership and full final-gate CI
    result: PASS
    evidence: head d2fcc0572d2268d7f88ab8faae9eec8006697f5b passed runs 30023734524 and 30023784205 before merge 82da6f6c5284b13446c5e71d075e7b06c9252b67
  - command: PR 819 exact-final-head ownership and CI
    result: PASS
    evidence: head 61262b1f2ac03bd04d41221e7d3983b4dcad124b passed runs 30026360598 and 30026360872 before merge 5c2ec1df1b5be9494fbf97ba389bea8fd9070f58
  - command: fresh Otheryn main and OAM-041 delivery search
    result: PASS
    evidence: Otheryn main remains 9369b0719ff94997a9cf5a2d62853939744e6338 and no OAM-041 target PR was found
  - command: read-only target upstream legacy spawn comparison
    result: PASS
    evidence: target/upstream runtime roots align and legacy lacks reviewed Maintenance-lane scheduling arguments
blockers:
  - Current authority permits writes only in blakinio/canary; OAM-041 requires a separately authorized blakinio/Otheryn write and local evidence-execution context.
next_action: Continue OAM-041 in a separately authorized blakinio/Otheryn context by creating the four-path spawns REUSE proof package, execute the pinned Canary OTBM validator against explicit current Otheryn active datapack and exact World Index/reachability provenance, run exact-head target gates, and reclassify to ADAPT only if a concrete spawns-owned proof failure requires bounded repair.
```
