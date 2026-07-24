---
task_id: CAN-20260723-oteryn-oam041-preflight
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-041
status: ready
agent: "GPT-5.6 Thinking"
branch: dudantas/oam-041-spawns-governance
base_branch: main
created: 2026-07-23
updated: 2026-07-24
last_verified_commit: "879fbfaff75b4255b4164b5132a0987e9aec8358"
risk: medium
related_issue: ""
related_pr: "853"
depends_on:
  - OAM-040 formally complete
blocks:
  - OAM-041 lifecycle archive
  - OAM-041 durable program reconciliation
  - OAM-041 target-task archive
  - OAM-042 start
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260723-oteryn-oam041-preflight.md
    - docs/agents/OTERYN_OAM_041_SPAWNS_REVALIDATION.md
  shared: []
  read_only:
    - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
    - docs/agents/real-tibia/registry/modules/spawns.yaml
    - docs/ai-agent/OTBM_SPAWN_NPC_VALIDATION.md
    - tools/ai-agent/otbm_spawn_npc*.py
modules_touched:
  - oteryn-architecture-migration
  - spawns
cross_repo_tasks: []
---

# OAM-041 spawns governance

## Final disposition

`spawns → REUSE`

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-24T07:32:00+02:00
head: 3cdb448d865867e2ab75b729aa7dbdd798ad627f
branch: dudantas/oam-041-spawns-governance
pr: 853
status: ready
context_routes:
  - agent-governance
  - otbm
  - cross-repo
owned_paths:
  - docs/agents/tasks/active/CAN-20260723-oteryn-oam041-preflight.md
  - docs/agents/OTERYN_OAM_041_SPAWNS_REVALIDATION.md
proven:
  - OAM-040 is formally complete after Canary reconciliation 115f3ac2fffc36bb4e415c2a6fb45908d9538ba3 and Otheryn target archive 9369b0719ff94997a9cf5a2d62853939744e6338.
  - OAM-041 preflight PR 813 merged as 82da6f6c5284b13446c5e71d075e7b06c9252b67 and target-proof-plan PR 819 merged as 5c2ec1df1b5be9494fbf97ba389bea8fd9070f58.
  - Canonical spawns depends only on resolved external otbm-tooling evidence and excludes monster combat AI plus the already-separated raid lifecycle ownership.
  - Target and fresh upstream shared spawn_monster.cpp blob 4c82217631ddf479faa5443025d43f99a0c927d1 and spawn_npc.cpp blob 21718ad80827a16e9a1b29bc9d649ad603bcf216; semantic proof covered placement, interval/scaling, blocking, cleanup, maintenance scheduling, boss exclusivity and weighted selection.
  - Deterministic target proof run 30049543113 verified pinned Canary evidence revision d1ad83056ec7930f067986909f66b8f20f1a1f44, exact Phase 4 tool blobs, map SHA-256 a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2 and external World Index SHA-256 6c22cd26d4414aa094af1d00be7f62190a441e270ee7a478b55449bf92e55e7a.
  - Full active-datapack scan found 52903 groups and 84294 static placements with 318 untruncated findings; duplicate Harlow definition ambiguity and 310 nonliteral dynamic calls remain explicit unresolved boundaries.
  - Final bounded correlation confirmed 34/34 groups and 39/39 placements with complete reachability diagnostics and zero correlation findings.
  - Otheryn PR 92 final head 2168ff23a7415b9aea8f66b7051995e7fd148691 changed exactly four proof/task/test-registration paths and no production path.
  - Exact-head Otheryn autofix 30068408311, CI 30068408471 and Required 30068408289 succeeded, including Linux release/runtime smokes, Linux debug full tests, macOS and both Windows build paths.
  - Target comments reviews and review threads were empty, target main had no drift from 5b6f62b33957472afba16f377b94993389abd145, and PR 92 expected-head squash-merged as de061aa6c75114192f1ef6b33f7b4857e502936c.
derived:
  - Final OAM-041 disposition is spawns REUSE without runtime datapack map binary protocol client schema or deployment mutation.
  - Legacy Canary spawn runtime is not a stronger whole-module donor because reviewed target/upstream roots retain stronger maintenance-lane scheduling safeguards.
  - OAM-042 remains blocked until governance merge, separate lifecycle archive, durable program reconciliation and Otheryn target-task archive all merge.
unknown:
  - Exact Canary governance final merge SHA until PR 853 completes.
  - Which dependency-valid canonical package a future fresh OAM-042 preflight will select.
conflicts: []
first_failure:
  marker: none
  evidence: No spawns-owned target defect was isolated; earlier proof truncation and CI failures were evidence-harness or unrelated CI issues repaired outside production scope.
rejected_hypotheses:
  - Finalize REUSE from blob identity alone; semantic source-contract and deterministic placement evidence were required.
  - Import divergent legacy spawn runtime; reviewed legacy call sites lack target maintenance-lane safeguards.
  - Treat truncated reachability diagnostics as a target defect; incomplete evidence was rejected and rerun with a complete bound.
  - Guess the Harlow definition winner or execute unresolved dynamic Lua calls; both remain explicit boundaries.
  - Copy Canary OTBM tooling into Otheryn; OAM-040 established the external evidence contract.
changed_paths:
  - docs/agents/tasks/active/CAN-20260723-oteryn-oam041-preflight.md
  - docs/agents/OTERYN_OAM_041_SPAWNS_REVALIDATION.md
validation:
  - command: Otheryn PR 92 exact-final-head target proof gate
    result: PASS
    evidence: head 2168ff23a7415b9aea8f66b7051995e7fd148691 passed autofix 30068408311 CI 30068408471 and Required 30068408289 before merge de061aa6c75114192f1ef6b33f7b4857e502936c
  - command: deterministic external Canary OTBM proof
    result: PASS
    evidence: run 30049543113 produced complete source reachability and correlation evidence with 34/34 groups and 39/39 placements confirmed
  - command: target scope and interaction audit
    result: PASS
    evidence: exactly four proof/task/test-registration paths changed; comments reviews threads empty; no target-main drift or forbidden mutation
blockers: []
next_action: Require exact-current-head Agent Task Ownership and full final-gate CI success on PR 853, audit exactly two governance paths plus comments reviews threads and Canary-main drift, then expected-head squash merge before separate lifecycle archive.
```
