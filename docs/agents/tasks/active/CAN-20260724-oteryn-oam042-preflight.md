---
task_id: CAN-20260724-oteryn-oam042-preflight
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-042
status: implementing
agent: "GPT-5.6 Thinking"
branch: dudantas/oam-042-npcs-revalidation
base_branch: main
created: 2026-07-24
updated: 2026-07-24
last_verified_commit: "f28acc8e959e79448ea99dead2500a64460f3aff"
risk: medium
related_issue: ""
related_pr: ""
depends_on:
  - Canary OAM-042 preflight merged as c86e805910d87dc8db9a212b18645e27c28c779c
  - Otheryn OAM-042 target proof merged as 0d01f077f80c2d4cd3d4231d2ffb9416874ba54e
  - Otheryn OAM-042 lifecycle archived as 3a37f3d5e4c01ddf4469f1c71461c40ca749142f
blocks:
  - Canary OAM-042 lifecycle archive
  - durable program reconciliation
  - OAM-043 start
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260724-oteryn-oam042-preflight.md
    - docs/agents/OTERYN_OAM_042_NPCS_REVALIDATION.md
  shared: []
  read_only:
    - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
    - docs/agents/OTERYN_TARGET_ARCHITECTURE_CONTRACT.md
    - docs/agents/real-tibia/registry/modules/npcs.yaml
    - docs/agents/OTERYN_OAM_041_SPAWNS_REVALIDATION.md
    - docs/ai-agent/OTBM_SPAWN_NPC_VALIDATION.md
modules_touched:
  - oteryn-architecture-migration
  - npcs
cross_repo_tasks:
  - OTH-20260724-oam042-npcs-reuse
---

# OAM-042 NPC revalidation

## Goal

Reconcile the completed Otheryn OAM-042 target proof into Canary governance without mutating target/runtime/datapack/map/protocol/client/schema/deployment paths. Preserve the bounded `npcs → REUSE` disposition, exact delivery and validation evidence, and all unresolved evidence boundaries before lifecycle archive and durable program reconciliation.

## Acceptance criteria

- [x] Otheryn target proof and lifecycle merges are exact and current.
- [x] Final `npcs → REUSE` is supported by semantic source-contract evidence, not blob identity alone.
- [x] Exact-head Otheryn build/test matrix and review hygiene are recorded.
- [x] OAM-041 placement evidence is reused without copying OTBM tooling into Otheryn.
- [x] Duplicate Harlow and nonliteral dynamic-call findings remain unresolved.
- [ ] Canary governance PR passes exact-head ownership and final-gate CI.
- [ ] Separate Canary lifecycle/archive PR merges.
- [ ] Durable program reconciliation records OAM-042 and selects no OAM-043 implementation before prerequisites close.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-24T10:18:00+02:00
head: c76dbdb43825479fbee034ca27aa26a3eff04fe3
branch: dudantas/oam-042-npcs-revalidation
status: implementing
context_routes:
  - agent-governance
  - otbm
  - cross-repo
owned_paths:
  - docs/agents/tasks/active/CAN-20260724-oteryn-oam042-preflight.md
  - docs/agents/OTERYN_OAM_042_NPCS_REVALIDATION.md
proven:
  - Canary preflight PR 859 merged as c86e805910d87dc8db9a212b18645e27c28c779c after full final-gate CI 30075782045 with no macOS job.
  - Otheryn task-start main was 7c54172adfa612fa143d11630f5a341ff4c82338.
  - Otheryn PR 96 final head e7b8f3a121f931a83ef016ceb6d30ad21dcdf74d changed only proof/task/test-registration paths and no production path.
  - Otheryn exact-head autofix 30077147255, CI 30077147345 and Required 30077147262 succeeded across Fast Checks, Lua, Linux release/debug, full tests, runtime smokes, macOS and both Windows paths.
  - Otheryn PR 96 had no comments, reviews or review threads and no target-main drift before expected-head squash merge 0d01f077f80c2d4cd3d4231d2ffb9416874ba54e.
  - Otheryn lifecycle PR 97 Required 30078308339 succeeded without application build and merged as 3a37f3d5e4c01ddf4469f1c71461c40ca749142f.
  - Reviewed target/current-upstream NPC runtime, npclib, Harlow, Rashid and placement paths shared the exact blobs recorded in the revalidation report.
  - The target-local source-contract test covered loader/registration callbacks, Lua NPC interaction/shop surfaces, dialogue/travel, Harlow storage-gated travel and Rashid quest/shop gating.
  - OAM-041 deterministic placement/definition evidence remains external Canary evidence and retains duplicate Harlow plus 310 nonliteral dynamic calls as unresolved boundaries.
derived:
  - No concrete npcs-owned target defect was isolated; bounded final disposition is npcs REUSE.
  - No legacy runtime, target adaptation, OTBM tool copy or generated evidence migration is justified.
unknown:
  - Full factual completeness of every individual NPC conversation.
  - Exact active-root resolution of duplicate Harlow definitions.
  - Exact NPC-owned subset and runtime correctness of nonliteral dynamic creation and quest-hook calls.
  - Production/physical-client NPC parity.
conflicts: []
first_failure:
  marker: none
  evidence: Otheryn target proof, full exact-head gates and lifecycle archive all succeeded.
rejected_hypotheses:
  - Infer REUSE from blob identity alone; semantic source-contract proof was required and delivered.
  - Treat OAM-041 placement evidence as proof of every NPC conversation/shop/travel/quest hook.
  - Guess duplicate Harlow or nonliteral calls as handled.
  - Copy Canary OTBM tooling into Otheryn.
  - Start quests or another OAM package before governance, lifecycle and durable reconciliation close.
changed_paths:
  - docs/agents/tasks/active/CAN-20260724-oteryn-oam042-preflight.md
  - docs/agents/OTERYN_OAM_042_NPCS_REVALIDATION.md
validation:
  - command: exact cross-repository merge and workflow audit
    result: PASS
    evidence: Canary preflight c86e8059; Otheryn proof 0d01f077; Otheryn archive 3a37f3d5 with exact successful workflow IDs recorded above.
  - command: target proof scope, comments, reviews, threads and drift audit
    result: PASS
    evidence: PR 96 had four intended proof/task/test paths, empty discussion/review surfaces and unchanged target main before merge.
  - command: bounded NPC semantic evidence review
    result: PASS
    evidence: registration, callback, Lua runtime, dialogue/travel, Harlow and Rashid contracts are source-covered while unresolved findings remain fail-closed.
blockers: []
next_action: Open the two-file Canary governance PR, bind its PR number into this checkpoint, apply ci:final-gate before the final checkpoint commit, then require exact-head ownership and CI before merge.
```
