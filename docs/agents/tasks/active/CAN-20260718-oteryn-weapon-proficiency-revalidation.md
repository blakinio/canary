---
task_id: CAN-20260718-oteryn-weapon-proficiency-revalidation
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-011
status: review
agent: "GPT-5.5 Thinking"
branch: docs/oam-011-weapon-proficiency-revalidation
base_branch: main
created: 2026-07-18T08:17:00+02:00
updated: 2026-07-18T08:55:00+02:00
last_verified_commit: "a52b054533a6005cdbafd2d01b3cf722b4273f27"
risk: medium
related_issue: ""
related_pr: "519"
depends_on:
  - OAM-010
  - OAM-004
blocks:
  - OAM-012
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260718-oteryn-weapon-proficiency-revalidation.md
    - docs/agents/OTERYN_OAM_011_WEAPON_PROFICIENCY_REVALIDATION.md
  shared: []
  read_only:
    - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
    - docs/agents/OTERYN_TARGET_ARCHITECTURE_CONTRACT.md
    - docs/agents/OTERYN_OAM_010_CHARACTER_PROGRESSION_REVALIDATION.md
    - docs/agents/real-tibia/registry/modules/weapon-proficiency.yaml
    - docs/agents/real-tibia/TSD_003_ACCOUNT_CHARACTER_PROGRESSION_REPORT.md
    - docs/ai-agent/WEAPON_PROFICIENCY_ACHIEVEMENT_REPORT.md
    - src/creatures/players/components/weapon_proficiency.cpp
    - src/creatures/players/components/weapon_proficiency.hpp
    - data/items/proficiencies.json
    - tests/unit/players/components/weapon_proficiency_test.cpp
modules_touched:
  - weapon-proficiency
reuses:
  - OAM-004 player-persistence KV durability boundary
  - OAM-008 vocation ownership boundary
  - OAM-010 character-progression disposition and proof surface
  - existing Otheryn player-component unit-test harness
public_interfaces:
  - proficiency JSON definitions and level perks
  - per-weapon experience and mastery lifecycle
  - selected-perk normalization and application
  - player KV load/save serialization
  - mastery achievement reconciliation
  - combat and skill bonus integration points
cross_repo_tasks: []
---

# Goal

Revalidate exactly one canonical Oteryn migration unit, `weapon-proficiency`, against the target architecture and immutable task-start baselines. Determine and deliver the smallest evidence-backed target adaptation without wholesale copying later legacy behavior or violating persistence, progression, achievement-catalogue or generic-combat ownership boundaries.

# Task-start baselines

- governance/legacy Canary: `blakinio/canary@9586530202eb3e40569bf4f97d21c63c9d99b6cb`
- Oteryn target: `blakinio/Otheryn@a4d095e3880787233bd194616dc6d19e6b94faaf`
- upstream evidence: `opentibiabr/canary@e0ac98e399d0f7e483f3668f57b78fcc45b6e53f`
- maintained OTClient: `blakinio/otclient@2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`

# Acceptance criteria

- [x] Re-fetch exact Canary, Otheryn, upstream and maintained-client heads before task creation.
- [x] Verify no pre-existing open OAM-011 PR in Canary or Otheryn.
- [x] Audit open Canary PR scopes for ownership/path overlap.
- [x] Select exactly one canonical module: `weapon-proficiency`.
- [x] Confirm hard dependencies `character-progression` and `player-persistence` are completed OAM foundations.
- [x] Pin exact task-start provenance for component cpp/hpp, proficiency JSON and focused test surfaces.
- [x] Start from `REVALIDATE` and avoid inferring a decision from blob identity or broad divergence alone.
- [x] Publish draft Canary governance PR #519 and bind this task to it.
- [x] Decompose legacy differences into mastery correctness, KV/load normalization, achievement reconciliation and excluded later achievement behaviour.
- [x] Preserve OAM-004 KV durability/non-atomicity and OAM-010 character-progression ownership.
- [x] Determine portable focused target proof and exclude legacy-only achievement 567 behaviour.
- [x] Classify every applicable target architecture boundary with evidence.
- [x] Determine final disposition `weapon-proficiency → ADAPT`.
- [x] Create and merge separate bounded Otheryn target delivery PR #29.
- [x] Require exact-head target autofix/CI/Required plus actual Linux debug `Run Tests` and artifact-level focused proof.
- [ ] Synchronize Canary PR #519 cleanly to latest `main` with exactly two OAM-011 files and pass exact-head Ownership/CI plus ready-state gates.
- [ ] Squash-merge Canary PR #519 after clean final audit.
- [ ] Complete separate lifecycle/archive and durable program reconciliation before OAM-012.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-18T08:55:00+02:00
head: a52b054533a6005cdbafd2d01b3cf722b4273f27
branch: docs/oam-011-weapon-proficiency-revalidation
pr: 519
status: validating
context_routes:
  - agent-governance
  - oteryn-migration
  - weapon-proficiency
owned_paths:
  - docs/agents/tasks/active/CAN-20260718-oteryn-weapon-proficiency-revalidation.md
  - docs/agents/OTERYN_OAM_011_WEAPON_PROFICIENCY_REVALIDATION.md
proven:
  - OAM-010 feature lifecycle and durable program reconciliation are complete
  - immutable task-start baselines are Canary 9586530202eb3e40569bf4f97d21c63c9d99b6cb Otheryn a4d095e3880787233bd194616dc6d19e6b94faaf upstream e0ac98e399d0f7e483f3668f57b78fcc45b6e53f OTClient 2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f
  - canonical weapon-proficiency depends on character-progression and player-persistence and declares no client path
  - no pre-existing OAM-011 PR or canonical proficiency path overlap existed at task start
  - task-start proficiency JSON is exact-blob identical across legacy target upstream
  - task-start target cpp hpp equal pinned upstream while legacy differs
  - target first-gain addExperience path caps initial experience but did not mark the newly created state mastered when initial gain reached maximum
  - Canary PR 212 is the bounded provenance for createInitialState mastery correctness and getMasteredWeaponCount
  - Canary PR 272 is the bounded provenance for idempotent achievement reconciliation of existing IDs 564 565 566 on live mastery and silent load backfill
  - Canary PR 288 later adds achievement 567 The Forbidden Build and a twelve-weapon condition and is deliberately outside OAM-011 target scope
  - target achievement catalogue still treats 567 as unknown non-existent while existing PlayerAchievement add API supports 564 565 566 reconciliation without catalogue mutation
  - final disposition is weapon-proficiency ADAPT
  - Otheryn target branch was based on exact a4d095e3880787233bd194616dc6d19e6b94faaf and changed exactly component cpp hpp focused test and existing component CMake registration
  - target production cpp blob bd3ecad2b34fa5bc731e253718ef9185d372727b and hpp blob 451177df8ff3ef569f69c27dc2cd79d7d64918c8 exactly match the selected Canary PR 272 donor state before PR 288
  - target focused test blob 3b7310737c27b9b8865606baa4a6adfa0d324431 exactly matches the selected PR 272 proof state
  - autofix changed only canonical CMake formatting and moved final target head to c9f060a2020c3612f65f8e31c6e745a03aa3fe5f
  - final target head c9f060a2020c3612f65f8e31c6e745a03aa3fe5f passed autofix 29634273531 CI 29634273615 and Required 29634273523
  - Linux debug compile runtime smoke database import and Run Tests all passed on final target head
  - artifact 8426692510 digest sha256:f7602a97b67686e25f53e06974b08ee0c7646c4cba873999397437830f95c5cf proves seven WeaponProficiencyTest cases passed
  - full Linux debug suite passed 336 of 336 with zero failures
  - target PR 29 final audit had zero comments zero reviews zero review threads and target main had no pre-merge drift
  - Otheryn PR 29 squash-merged as 72f7bdc1a5afa9e9982c20bdcf3098c83dca543e
  - target issue 28 is closed completed
  - no proficiency JSON KV schema SQL persistence protocol client map or asset mutation was made
  - physical-client E2E is not required for the selected mastery correctness and existing-threshold reconciliation claim because no client protocol or UI boundary changed and deterministic target runtime tests cover the adapted state transitions
  - Canary PR 519 remains limited to the OAM-011 evidence report and active task before final synchronization
derived:
  - whole-module REUSE is invalid because the task-start target contains a proven mastery-state correctness defect
  - whole current legacy component transfer is also invalid because later achievement 567 behaviour crosses an unresolved achievement-catalogue boundary
  - the correct target strategy is a bounded ADAPT using the exact proven legacy state after PR 272 and before PR 288
  - existing OAM-004 persistence semantics and OAM-010 progression ownership remain unchanged
unknown:
  - whether Canary main advances before final PR 519 synchronization and merge
  - exact final Canary PR 519 head and gate run ids after synchronization
  - lifecycle and durable program reconciliation merge SHAs
conflicts: []
first_failure:
  marker: target-ready-autofix-cmake-formatting
  evidence: first ready-state target head d326d347e9ac219171ad7b6f99d484f0e0670894 was moved by autofix only to canonical CMake formatting; production donor blobs and focused test blob remained unchanged and all final gates were rerun on c9f060a2020c3612f65f8e31c6e745a03aa3fe5f
rejected_hypotheses:
  - exact proficiency JSON identity proves whole-module REUSE
  - target upstream component identity proves compatibility with accepted legacy mastery behaviour
  - broad current legacy component should be copied wholesale
  - achievement 567 should be migrated merely because later legacy Canary contains it
  - proficiency-side reconciliation transfers achievement catalogue ownership
  - proficiency integration permits generic combat migration
  - OAM-004 SQL and KV persistence may be treated as atomic
  - draft scope-only CI is sufficient target proof
changed_paths:
  - docs/agents/tasks/active/CAN-20260718-oteryn-weapon-proficiency-revalidation.md
  - docs/agents/OTERYN_OAM_011_WEAPON_PROFICIENCY_REVALIDATION.md
validation:
  - command: fresh OAM-011 repository dependency and PR preflight
    result: PASS
    evidence: exact heads pinned no pre-existing OAM-011 PR and no canonical proficiency ownership overlap found
  - command: function-level semantic and provenance revalidation
    result: PASS
    evidence: first-gain mastery bug isolated to target; PR 212 correctness and PR 272 564-566 reconciliation selected; PR 288 achievement 567 explicitly excluded
  - command: exact target content provenance
    result: PASS
    evidence: final production cpp hpp and focused test content match selected PR 272 donor blobs; only target CMake registration formatting differs as required by target formatter
  - command: Otheryn PR 29 exact-head target gates
    result: PASS
    evidence: autofix 29634273531 CI 29634273615 Required 29634273523 succeeded on c9f060a2020c3612f65f8e31c6e745a03aa3fe5f
  - command: Linux debug focused and full target tests
    result: PASS
    evidence: artifact 8426692510 proves seven focused WeaponProficiencyTest cases and 336 of 336 total tests passed; digest sha256:f7602a97b67686e25f53e06974b08ee0c7646c4cba873999397437830f95c5cf
  - command: Otheryn PR 29 final audit and squash merge
    result: PASS
    evidence: zero comments reviews and review threads; no target main drift; merged as 72f7bdc1a5afa9e9982c20bdcf3098c83dca543e
blockers: []
next_action: Synchronize Canary PR 519 cleanly onto latest main with exactly the two OAM-011 governance files; require exact-head Ownership and CI, ready-state final gates and clean audit, then squash merge and complete separate lifecycle/archive plus durable program reconciliation before OAM-012.
```
