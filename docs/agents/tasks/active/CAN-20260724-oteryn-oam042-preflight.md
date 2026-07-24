---
task_id: CAN-20260724-oteryn-oam042-preflight
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-042
status: active
agent: "GPT-5.6 Thinking"
branch: dudantas/oam-042-npcs-preflight
base_branch: main
created: 2026-07-24
updated: 2026-07-24
last_verified_commit: "deceb2c451aaf101945b067d45042e5866f98cbf"
risk: medium
related_issue: ""
related_pr: ""
depends_on:
  - OAM-041 formally complete
blocks:
  - OAM-042 target proof and final disposition
  - OAM-043 start
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260724-oteryn-oam042-preflight.md
  shared: []
  read_only:
    - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
    - docs/agents/OTERYN_TARGET_ARCHITECTURE_CONTRACT.md
    - docs/agents/real-tibia/registry/modules/npcs.yaml
    - docs/agents/real-tibia/registry/modules/quests.yaml
    - docs/agents/OTERYN_OAM_041_SPAWNS_REVALIDATION.md
    - docs/ai-agent/OTBM_SPAWN_NPC_VALIDATION.md
    - tools/ai-agent/otbm_spawn_npc.py
    - tools/ai-agent/otbm_spawn_npc_validation.py
    - tools/ai-agent/otbm_spawn_npc_tool.py
modules_touched:
  - oteryn-architecture-migration
  - npcs
cross_repo_tasks: []
---

# OAM-042 Fresh Preflight

## Selected package

`npcs` is the selected dependency-valid OAM-042 canonical package.

Preflight disposition: `REVALIDATE`, with `REUSE` as the leading hypothesis only if bounded target proof confirms semantic equivalence and closes or explicitly bounds the known NPC-definition ambiguities.

Canonical `npcs` is a world-content module owning NPC definitions and registration, dialogue state, shops, travel, quest hooks and placement evidence. Its only hard dependency is canonical `otbm-tooling`, formally resolved by OAM-040 as an external Canary laboratory/evidence responsibility. Completed OAM-041 already proved the shared spawn-placement runtime boundary and produced reusable deterministic NPC placement/definition evidence, but it did not prove NPC dialogue, shop, travel or quest-hook correctness.

`npcs` is selected ahead of `quests` because it is the smaller dependency-valid remaining boundary. Canonical `quests` additionally owns storage transitions, actions, map mechanics, rewards and access, and depends on both `otbm-tooling` and `player-persistence`. Open Canary PR #789 is an independent quest-journal/postal/market-logistics design document; it does not overlap this task path, but reinforces that the broader quest domain should not be selected while the narrower NPC boundary remains unresolved.

This preflight performs no target, runtime, datapack, map, binary, protocol or client mutation. Final `REUSE`, `ADAPT`, `REWRITE` or another disposition requires a separately ordered Otheryn target proof on exact pinned baselines.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-24T09:35:00+02:00
head: pending-initial-commit
branch: dudantas/oam-042-npcs-preflight
pr: pending
status: active
context_routes:
  - agent-governance
  - otbm
  - cross-repo
owned_paths:
  - docs/agents/tasks/active/CAN-20260724-oteryn-oam042-preflight.md
proven:
  - OAM-041 is formally complete after Canary durable reconciliation bc4ae5861d7b9c172d9c15ce78181cb4c2be4ead and Otheryn target-task archive dcc3ae0075bf7b04f81b548fd68eaa865e3b9305.
  - Fresh Canary task-start main is deceb2c451aaf101945b067d45042e5866f98cbf.
  - Fresh Otheryn target baseline is dcc3ae0075bf7b04f81b548fd68eaa865e3b9305.
  - Fresh upstream Canary baseline is 7323503b3dc61ed86bf1f04a611b2d0aec64b35a.
  - Canonical npcs registry blob is 7b890b9daa42856a30d87785906f7cbe809643a8; it is category world-content and depends only on otbm-tooling.
  - Canonical npcs owns definitions registration dialogue shops travel quest hooks and placement evidence while excluding generic quest progression outside NPC contracts.
  - Canonical quests registry blob is 61f3f8249a1b7b2efef956cbcec2b78da9dafc08 and additionally depends on player-persistence.
  - OAM-040 keeps OTBM tooling as an external Canary evidence responsibility; no toolchain copy into Otheryn is permitted.
  - OAM-041 deterministic evidence covered 1008 static NPC placements and retained the duplicate Harlow definition ambiguity plus 310 nonliteral dynamic creation calls as explicit unresolved boundaries.
  - The existing OTBM NPC scanner supports explicit active datapack roots, NPC definition resolution, literal dynamic Game.createNpc calls and fail-closed unresolved evidence without executing Lua.
  - Fresh open-PR and branch searches found no OAM-042 or npcs owner in Canary or Otheryn.
  - Otheryn PR #93 changes only AGENTS.md and its validation-cost task record and does not overlap NPC evidence or this Canary task path.
  - Canary PR #789 changes only docs/ai-agent/OTS_QUEST_JOURNAL_POSTAL_AND_MARKET_LOGISTICS.md and does not overlap this task path.
  - Canonical npcs declares no direct client path; maintained OTClient mutation is not implied by this preflight.
derived:
  - npcs is the smallest dependency-valid unresolved canonical package after OAM-041 because its only hard dependency is resolved and its placement/definition evidence can reuse the existing deterministic Canary OTBM stack.
  - The completed spawns proof may be reused only for placement and definition-correlation evidence; it does not prove dialogue state shops travel or quest hooks.
  - REUSE is only a hypothesis until exact target upstream and legacy NPC source inventories are pinned and semantically reviewed.
  - ADAPT is permitted only if bounded proof isolates a concrete npcs-owned target defect; unresolved Harlow or dynamic-call evidence must not be guessed away.
  - quests should remain queued until the narrower NPC package is resolved and its interaction boundary is explicit.
unknown:
  - Exact current Otheryn upstream and legacy NPC definition/dialogue/shop/travel source inventories and blob relationships.
  - Whether the duplicate Harlow definitions are both active under the exact target datapack configuration and which configuration/registration rule resolves or exposes them.
  - Exact count and classification of npcs-owned nonliteral dynamic creation or quest-hook calls after excluding non-NPC responsibilities.
  - Whether target-local source-contract tests are sufficient or a bounded runtime/physical-client NPC dialogue or shop proof is required for final disposition.
  - Whether bounded proof isolates any concrete npcs-owned target defect requiring ADAPT.
conflicts: []
first_failure:
  marker: none
  evidence: OAM-042 target proof has not run; this task is preflight-only.
rejected_hypotheses:
  - Select quests first; it is broader, depends on player-persistence in addition to otbm-tooling, and owns storage/action/map/reward boundaries outside the smaller NPC package.
  - Finalize npcs as REUSE from OAM-041 placement evidence; that proof explicitly did not execute or validate dialogue shops travel or quest hooks.
  - Resolve duplicate Harlow or nonliteral dynamic calls by guessing which source wins; deterministic evidence must remain fail-closed.
  - Copy Canary OTBM tooling into Otheryn; OAM-040 established it as external evidence infrastructure.
changed_paths:
  - docs/agents/tasks/active/CAN-20260724-oteryn-oam042-preflight.md
validation:
  - command: fresh dependency ordering and formal-closure verification
    result: PASS
    evidence: OAM-041 archive merge dcc3ae0075bf7b04f81b548fd68eaa865e3b9305 is on Otheryn main and npcs depends only on completed otbm-tooling
  - command: fresh ownership open-PR and branch overlap audit
    result: PASS
    evidence: no OAM-042 or npcs owner exists; Otheryn PR 93 and Canary PR 789 have non-overlapping paths
  - command: reusable external NPC evidence contract review
    result: PASS
    evidence: existing fail-closed OTBM scanner covers explicit NPC definitions placements and literal dynamic calls while preserving unresolved evidence
blockers: []
next_action: Open the one-file Canary preflight PR, attach ci:final-gate before the final checkpoint commit, require exact-head Agent Task Ownership and CI, audit comments reviews threads scope and main drift, then expected-head squash merge before starting a separate Otheryn target-proof task.
```
