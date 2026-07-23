---
task_id: CAN-20260723-oteryn-oam039-preflight
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
status: ready
agent: "GPT-5.6 Thinking"
branch: dudantas/oam-039-preflight
base_branch: main
created: 2026-07-23
updated: 2026-07-23
last_verified_commit: "efaa970229346c13c9ccfe17805e4b914ec6e8ad"
risk: high
related_issue: ""
related_pr: ""
depends_on:
  - OAM-038 formally complete
blocks:
  - OAM-039 target delivery selection
  - OAM-040 start
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260723-oteryn-oam039-preflight.md
  shared: []
  read_only:
    - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
    - docs/agents/real-tibia/registry/modules/**
modules_touched:
  - oteryn-architecture-migration
  - instances
cross_repo_tasks: []
---

# OAM-039 Fresh Preflight

## Selected package

`instances` is the selected dependency-valid OAM-039 canonical package.

Preflight disposition: `ADAPT candidate`.

The clean Otheryn target and fresh upstream do not contain the canonical `src/game/instance/instance_manager.{hpp,cpp}` roots, so `REUSE` is not available. Legacy Canary contains a bounded, tested implementation for region allocation, instance lifecycle, stable creature ownership, fail-closed relations, lazy event liveness and a bounded arena consumer. Final OAM-039 disposition and exact target edit boundary remain gated on target-side integration proof.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-23T12:30:00+02:00
head: efaa970229346c13c9ccfe17805e4b914ec6e8ad
branch: dudantas/oam-039-preflight
pr: null
status: ready
context_routes:
  - agent-governance
  - cpp-runtime
  - cross-repo
owned_paths:
  - docs/agents/tasks/active/CAN-20260723-oteryn-oam039-preflight.md
proven:
  - OAM-038 is formally complete after Canary durable reconciliation efaa970229346c13c9ccfe17805e4b914ec6e8ad and Otheryn target archive a275f1d788b50164ffc79b6f6143e13b9150c82e.
  - Fresh Canary baseline is efaa970229346c13c9ccfe17805e4b914ec6e8ad.
  - Fresh Otheryn baseline is a275f1d788b50164ffc79b6f6143e13b9150c82e.
  - Fresh upstream Canary baseline is 7323503b3dc61ed86bf1f04a611b2d0aec64b35a.
  - Fresh maintained OTClient baseline is 1e5305395159142634f182d9e888e5f9164228c6.
  - Canonical instances depends only on world-map-runtime which was completed in OAM-007.
  - Canonical ownership covers configured map-region allocation InstanceState lifecycle stable creature-id ownership isolation summon inheritance cleanup quarantine expiration and the bounded arena consumer; generic map loading quest/boss design dynamic map generation and physical-client orchestration remain excluded.
  - Otheryn and fresh upstream both lack src/game/instance/instance_manager.cpp and instance_manager.hpp at the fresh baselines.
  - Legacy Canary contains instance_manager.cpp blob bce417535552176d7d760118a038075f2e6667c5 and instance_manager.hpp blob d0fe2160fda02b88c7987b8cd5815788ec284f8e.
  - Legacy Canary contains instance_id.hpp blob 41cfa6dd8dd23c140b0787c945324110736574b7 instance_region_pool.hpp blob fd661edf45f88273393ac9ca5617fd284851f1a4 and instance_region_pool.inl blob 63931b9eede044b988805bb06b1277a5ebae7f37.
  - Legacy Canary contains instance_creature_binder.hpp blob c913d6c5309e74a885bfa8155e4aab3d34623bcc instance_scoped_event.hpp blob aae6dbca7103f2d44d12f4ca93a8cc3f513c0d91 instance_arena_service.hpp blob 5c565bcf56af63f53ee9bf64c02feafbfb165c2c and instance_arena_service.cpp blob b2f8c53ecc2de19967c15f7348bc43bf7579fa8e.
  - Legacy unit coverage includes InstanceRegionPool validation reservation reuse and concurrent reservation plus InstanceManager creation activation cleanup quarantine stable-id ownership fail-closed relation timeout sweeping and concurrency behavior.
  - Historical legacy PR evidence shows the implementation was deliberately staged through region pool lifecycle ownership binder liveness Game ownership periodic expiration and a bounded InstanceArenaService rather than introduced as a second global world runtime.
  - Fresh open-PR and branch searches found no overlapping OAM-039 instances owner in Canary or Otheryn.
  - Canonical instances has no direct client path so no maintained OTClient mutation is implied by the registry boundary.
derived:
  - instances is the smallest dependency-valid next package because its sole hard dependency is complete while spawns and NPCs still depend on otbm-tooling and quests depends on otbm-tooling plus player-persistence.
  - OAM-039 requires ADAPT rather than REUSE because the clean target lacks the canonical runtime roots.
  - The legacy implementation is a strong behavioral donor but must be adapted to the current Otheryn Game ownership scheduling and integration surfaces instead of blindly copied wholesale.
unknown:
  - Exact target integration path set required beyond src/game/instance/** including current Game ownership removal hooks scheduler ownership and arena consumer wiring.
  - Whether every legacy integration remains valid against current Otheryn architecture or some legacy arena/admin surface should be excluded while preserving the canonical instance lifecycle.
  - Final OAM-039 ADAPT delivery size and exact target CI evidence until bounded target implementation executes.
conflicts: []
first_failure:
  marker: none
  evidence: No OAM-039 target implementation has run; this task is preflight-only.
rejected_hypotheses:
  - Select spawns or NPCs first; both retain a hard otbm-tooling dependency and are broader data-placement surfaces.
  - Select quests first; quests also depends on otbm-tooling and is a larger cross-domain data/script progression boundary.
  - Classify instances as REUSE; target and fresh upstream do not contain the canonical InstanceManager roots.
  - Copy legacy instances wholesale without integration analysis; the legacy package includes staged Game scheduler creature and arena integrations that must be reconciled with current target architecture.
changed_paths:
  - docs/agents/tasks/active/CAN-20260723-oteryn-oam039-preflight.md
validation:
  - command: fresh dependency ownership and overlap preflight
    result: PASS
    evidence: world-map-runtime is complete and no overlapping OAM-039 instances writer was found
  - command: target upstream legacy root comparison
    result: PASS
    evidence: target and upstream lack canonical InstanceManager roots while legacy contains a tested bounded instance lifecycle package and supporting adapters
blockers: []
next_action: Open the one-file Canary OAM-039 preflight PR, bind its PR number, require exact-current-head Agent Task Ownership and CI, audit scope and review state, then expected-head squash merge before bounded instances ADAPT implementation in Otheryn.
```
