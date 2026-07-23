---
task_id: CAN-20260723-oteryn-oam041-preflight
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-041
status: ready
agent: "GPT-5.6 Thinking"
branch: dudantas/oam-041-spawns-preflight
base_branch: main
created: 2026-07-23
updated: 2026-07-23
last_verified_commit: "3227ee1e3b5f323656b101a601f873ae21b61f27"
risk: medium
related_issue: ""
related_pr: "813"
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
updated_at: 2026-07-23T19:36:00+02:00
head: df7c6ef779881347822536734edcb76fa73f2f7c
branch: dudantas/oam-041-spawns-preflight
pr: 813
status: ready
context_routes:
  - agent-governance
  - otbm
  - cross-repo
owned_paths:
  - docs/agents/tasks/active/CAN-20260723-oteryn-oam041-preflight.md
proven:
  - OAM-040 is formally complete after Canary durable reconciliation 115f3ac2fffc36bb4e415c2a6fb45908d9538ba3 and Otheryn target-task archive 9369b0719ff94997a9cf5a2d62853939744e6338.
  - Fresh Canary task-start main is 3227ee1e3b5f323656b101a601f873ae21b61f27.
  - Fresh Otheryn baseline is 9369b0719ff94997a9cf5a2d62853939744e6338.
  - Fresh upstream Canary baseline is 7323503b3dc61ed86bf1f04a611b2d0aec64b35a.
  - Fresh maintained OTClient baseline is 1e5305395159142634f182d9e888e5f9164228c6.
  - Canonical spawns registry record blob is 10d69a10a66610a19116f96f4d32e88a41ced0b5; it is category world-content and depends only on otbm-tooling.
  - Canonical spawns owns static spawns dynamic creation inventory raids boss placement and definition-to-placement correlation while excluding monster combat AI and Bosstiary award logic.
  - Active global monster spawn root data-otservbr-global/world/otservbr-monster.xml is exact blob 65e87a4134a320d28b2270fa5a17917fc7b513a1 in Otheryn target upstream Canary and current Canary legacy evidence.
  - Active global NPC spawn root data-otservbr-global/world/otservbr-npc.xml is exact blob 0a72085b7bbdfca73b794e631cc2bab790d8fcef in Otheryn target upstream Canary and current Canary legacy evidence.
  - Current Canary external spawn proof tooling is pinned by otbm_spawn_npc.py blob 4339e94f5875f4d7fd443c2359c15d10f205004f otbm_spawn_npc_validation.py blob 7f66f74b68b66e9acabe1ea1a5cbd404b1637e9b and otbm_spawn_npc_tool.py blob 481c163d8048298900b33648b08b1fac5b60fefe.
  - Spawn/NPC validation documentation blob is 0bd5242d919550f0fd97424afef5a0f1ae2ca89b and defines explicit active-datapack inputs world/otservbr-monster.xml and world/otservbr-npc.xml with no datapack mixing and fail-closed path XML and unresolved-Lua handling.
  - The OTBM tooling roadmap records Phase 4 Spawns bosses and NPCs as merged and archived and requires static source/map evidence to remain distinct from live gameplay proof.
  - Module catalogue requires reuse of the existing OTBM spawn boss and NPC validator and existing reachability evidence; no second parser pathfinder or auto-repair path is allowed.
  - Known risk policy forbids guessing dynamic Lua registrations and OTBM-only identifiers and forbids binary map or generated report mutation without explicit authorization.
  - Fresh open-PR and branch searches found no overlapping OAM-041 or spawns owner in Canary or Otheryn.
  - Canonical spawns has no direct client path or protocol surface; no maintained OTClient mutation is implied by this preflight.
derived:
  - spawns is the smallest dependency-valid unresolved canonical package after OAM-040 because its only hard dependency otbm-tooling is resolved and it has a dedicated bounded deterministic evidence path.
  - REUSE is the leading disposition because the two explicit active spawn XML roots are exact-blob identical across target upstream and legacy evidence and no stronger delivered legacy donor delta has been identified in the reviewed roots.
  - Blob identity alone is insufficient; final REUSE requires a target-side source and placement proof over explicit Otheryn active inputs using exact Canary tool and report provenance.
  - The target proof should consume the Canary OTBM evidence stack cross-repository rather than copying tools/ai-agent into Otheryn.
  - ADAPT is permitted only if bounded proof isolates a concrete spawns-owned target defect; donor or map evidence must not authorize blind source or map replacement.
unknown:
  - Current full Otheryn spawn dynamic-creation raid and boss validation findings because the external deterministic scan has not yet been executed for OAM-041.
  - Exact current Otheryn World Index reachability and bounded validation artifact provenance to consume for final placement proof.
  - Exact target proof path set and whether Otheryn governance accepts documentation/task proof plus pinned external evidence or requires an additional target-local nonduplicative contract check.
  - Whether bounded target proof exposes a concrete spawns-owned defect requiring ADAPT.
conflicts: []
first_failure:
  marker: none
  evidence: OAM-041 target proof has not run; this task is preflight-only.
rejected_hypotheses:
  - Select npcs first; it is dependency-valid but owns broader dialogue shop travel and quest-hook behavior beyond the smaller spawn placement boundary.
  - Select quests first; it is broader and additionally depends on player-persistence.
  - Finalize spawns as REUSE from exact XML blob identity alone; the architecture contract requires semantic and target-side proof.
  - Copy Canary OTBM tooling into Otheryn; OAM-040 explicitly resolved otbm-tooling as an external Canary evidence dependency.
  - Import or replace spawn/map content from legacy or donor evidence without bounded proof; world-content safety forbids blind replacement.
changed_paths:
  - docs/agents/tasks/active/CAN-20260723-oteryn-oam041-preflight.md
validation:
  - command: fresh dependency ownership and overlap preflight
    result: PASS
    evidence: spawns depends only on resolved otbm-tooling and no overlapping OAM-041 or spawn branch PR owner was found
  - command: target upstream legacy active-root comparison
    result: PASS
    evidence: explicit active monster and NPC spawn XML roots are exact-blob identical across Otheryn upstream and Canary
  - command: external OTBM proof-tool provenance review
    result: PASS
    evidence: current Canary spawn validator entrypoints and documentation are pinned by exact blobs and define fail-closed explicit-datapack evidence boundaries
blockers: []
next_action: Require exact-current-head Agent Task Ownership and CI success on PR 813, audit the one-file preflight scope and review state, then expected-head squash merge before separately authorized Otheryn target proof.
```
