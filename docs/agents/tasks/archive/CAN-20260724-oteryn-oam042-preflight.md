---
task_id: CAN-20260724-oteryn-oam042-preflight
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-042
status: completed
agent: "GPT-5.6 Thinking"
branch: dudantas/oam-042-npcs-revalidation
base_branch: main
created: 2026-07-24
updated: 2026-07-24
completed: 2026-07-24T10:46:00+02:00
last_verified_commit: "2f42260258f84b323bcd2a74d6107b10d4e01142"
risk: medium
related_issue: ""
related_pr: "862"
owned_paths:
  exclusive:
    - docs/agents/tasks/archive/CAN-20260724-oteryn-oam042-preflight.md
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

## Final disposition

`npcs → REUSE` with explicit evidence boundaries.

No Canary or Otheryn runtime, datapack, map, binary, protocol, client, schema or deployment adaptation was required. OAM-041 deterministic placement evidence remained external Canary evidence; no OTBM tooling or generated evidence was copied into Otheryn.

Duplicate Harlow definition ambiguity, the exact NPC-owned subset of nonliteral dynamic creation/quest-hook calls, factual completeness of every NPC conversation and production/physical-client parity remain explicit unknowns.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-24T10:46:00+02:00
head: 2f42260258f84b323bcd2a74d6107b10d4e01142
branch: main
pr: 862
status: completed
context_routes:
  - agent-governance
  - otbm
  - cross-repo
owned_paths:
  - docs/agents/tasks/archive/CAN-20260724-oteryn-oam042-preflight.md
  - docs/agents/OTERYN_OAM_042_NPCS_REVALIDATION.md
proven:
  - Canary preflight PR 859 merged as c86e805910d87dc8db9a212b18645e27c28c779c.
  - Otheryn target proof PR 96 exact head e7b8f3a121f931a83ef016ceb6d30ad21dcdf74d passed autofix 30077147255, CI 30077147345 and Required 30077147262 across Fast Checks, Lua, Linux release/debug, full tests, runtime smokes, macOS and both Windows paths.
  - Otheryn target proof PR 96 merged as 0d01f077f80c2d4cd3d4231d2ffb9416874ba54e.
  - Otheryn lifecycle PR 97 Required 30078308339 succeeded without application build and merged as 3a37f3d5e4c01ddf4469f1c71461c40ca749142f.
  - Canary governance PR 862 exact head 28cc1fcda89025411e94b7d94004e02519292394 passed Agent Task Ownership 30078712841 and final-gate CI 30078791535.
  - Final Canary CI passed Fast Checks, Lua, Linux release/debug with tests and smokes, Windows Solution/CMake, Docker, Docker Quickstart Smoke and Required; no macOS job was emitted.
  - PR 862 had no comments, submitted reviews or review threads; unrelated main drift did not overlap OAM-042 paths.
  - PR 862 squash-merged as 2f42260258f84b323bcd2a74d6107b10d4e01142.
derived:
  - Semantic source-contract evidence and exact-head platform gates support bounded canonical npcs REUSE.
  - No target-local ADAPT or REWRITE action is justified.
unknown:
  - Full factual completeness of every individual NPC conversation.
  - Exact active-root resolution of duplicate Harlow definitions.
  - Exact NPC-owned subset and runtime correctness of nonliteral dynamic creation and quest-hook calls.
  - Production and physical-client NPC parity.
conflicts: []
first_failure:
  marker: none
  evidence: Otheryn proof, Otheryn lifecycle and Canary governance all passed their exact applicable gates.
rejected_hypotheses:
  - Infer REUSE from blob identity alone.
  - Treat OAM-041 placement evidence as proof of every dialogue, shop, travel or quest hook.
  - Guess duplicate Harlow or nonliteral dynamic calls as handled.
  - Copy Canary OTBM tooling into Otheryn.
changed_paths:
  - docs/agents/OTERYN_OAM_042_NPCS_REVALIDATION.md
  - docs/agents/tasks/archive/CAN-20260724-oteryn-oam042-preflight.md
validation:
  - command: Otheryn exact-head target proof CI and Required
    result: PASS
    evidence: autofix 30077147255; CI 30077147345; Required 30077147262.
  - command: Canary exact-head governance ownership and final-gate CI
    result: PASS
    evidence: Agent Task Ownership 30078712841 and CI 30078791535 succeeded on head 28cc1fcda89025411e94b7d94004e02519292394.
  - command: squash merge PR 862
    result: PASS
    evidence: GitHub created merge commit 2f42260258f84b323bcd2a74d6107b10d4e01142.
blockers: []
next_action: NONE
```
