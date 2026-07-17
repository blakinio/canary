---
task_id: CAN-20260717-oteryn-character-progression-revalidation
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-010
status: completed
agent: "GPT-5.5 Thinking"
branch: docs/oam-010-character-progression-revalidation
base_branch: main
created: 2026-07-17T22:03:00+02:00
updated: 2026-07-17T23:25:01Z
last_verified_commit: "f140a0e62cdcd1eaac39ab9b721d83e528ac3dae"
risk: medium
related_issue: ""
related_pr: "509"
depends_on:
  - OAM-009
  - OAM-005
  - OAM-004
blocks:
  - OAM-011
  - weapon-proficiency migration revalidation
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260717-oteryn-character-progression-revalidation.md
    - docs/agents/OTERYN_OAM_010_CHARACTER_PROGRESSION_REVALIDATION.md
  shared: []
  read_only:
    - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
    - docs/agents/OTERYN_TARGET_ARCHITECTURE_CONTRACT.md
    - docs/agents/OTERYN_OAM_004_PERSISTENCE_FOUNDATION_REVALIDATION.md
    - docs/agents/OTERYN_OAM_005_ACCOUNT_CHARACTER_LIFECYCLE_REVALIDATION.md
    - docs/agents/OTERYN_OAM_008_VOCATIONS_MIGRATION.md
    - docs/agents/OTERYN_OAM_009_VOCATIONS_PHYSICAL_E2E.md
    - docs/agents/real-tibia/registry/modules/character-progression.yaml
    - docs/agents/real-tibia/generated/MODULE_DEPENDENCIES.md
    - docs/agents/real-tibia/TSD_003_ACCOUNT_CHARACTER_PROGRESSION_REPORT.md
    - src/creatures/players/player.cpp
    - src/creatures/players/player.hpp
    - src/io/functions/iologindata_load_player.cpp
    - src/io/functions/iologindata_save_player.cpp
modules_touched:
  - character-progression
reuses:
  - OAM-004 player-persistence transaction and SQL/KV boundary
  - OAM-005 character-lifecycle ownership and load/save boundary
  - OAM-008 vocations REUSE decision
  - OAM-009 exact-target physical vocation/login proof
  - existing Otheryn Player unit-test surface
public_interfaces:
  - shared character level and experience progression state
  - skill and magic-level advancement state
  - stamina and experience-boost state
  - offline-training state
  - death-loss and blessing-related progression consequences
cross_repo_tasks: []
completed: 2026-07-17T23:25:01Z
---

# Goal

Revalidate exactly one canonical Oteryn migration unit, `character-progression`, against the current target architecture and exact task-start baselines. Determine an evidence-backed final disposition without copying the broad legacy `Player` surface or overriding the already-proven OAM-004/OAM-005 persistence and character-lifecycle contracts.

# Task-start baselines

- governance/legacy Canary: `blakinio/canary@cb149d427e6a954ee3ab163758465627bc1e643c`
- Oteryn target: `blakinio/Otheryn@f59a58426b4d3910ba0cdc0d2332c24f31a1db4f`
- upstream evidence: `opentibiabr/canary@e0ac98e399d0f7e483f3668f57b78fcc45b6e53f`
- maintained OTClient: `blakinio/otclient@2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`

# Acceptance criteria

- [x] Re-fetch exact Canary, Otheryn, upstream and maintained-client heads before task creation.
- [x] Verify no pre-existing open OAM-010 PR in Canary or Otheryn.
- [x] Audit open Canary PR changed paths for overlap with the canonical progression boundary.
- [x] Select exactly one canonical module: `character-progression`.
- [x] Confirm hard dependencies `character-lifecycle` and `player-persistence` are completed OAM foundations.
- [x] Start from `REVALIDATE` and avoid inferring a decision from whole-file blob differences.
- [x] Pin exact task-start provenance for Player and IOLoginData load/save surfaces.
- [x] Isolate progression-specific behavior from unrelated legacy additions inside broad Player/IOLoginData files.
- [x] Preserve OAM-004D and OAM-005 boundaries; no whole legacy IOLoginData/Player restore.
- [x] Classify the applicable target architecture boundaries with evidence.
- [x] Create a separate bounded proof-only Otheryn target delivery without production runtime mutation.
- [x] Execute focused deterministic target proof for XP thresholds, offline-training bounds, regular-skill advancement and magic-level advancement.
- [x] Reject non-isolated test-harness failures rather than treating them as target defects.
- [x] Determine final disposition `character-progression → ADAPT` from bounded evidence.
- [x] Merge Otheryn proof PR #27 as `a4d095e3880787233bd194616dc6d19e6b94faaf` after exact-head target gates and clean review audit.
- [x] Synchronize Canary PR #509 cleanly to current `main@354abbbeeff7f7c3470987b32e873527fc6e1a2f` with exactly two OAM-010 files and pass clean-head Ownership/CI.
- [ ] Pass exact-head gates on this ready checkpoint head, mark PR #509 ready, pass ready-state gates, and complete final review audit.
- [ ] Squash-merge Canary PR #509 after clean final audit.
- [ ] Complete separate lifecycle/archive and durable program reconciliation before OAM-011.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-17T23:21:00+02:00
head: f4889ab38cc3d39f1cf82d5eddea84c1442f0fe4
branch: docs/oam-010-character-progression-revalidation
pr: 509
status: ready
context_routes:
  - agent-governance
  - oteryn-migration
  - character-progression
owned_paths:
  - docs/agents/tasks/active/CAN-20260717-oteryn-character-progression-revalidation.md
  - docs/agents/OTERYN_OAM_010_CHARACTER_PROGRESSION_REVALIDATION.md
proven:
  - OAM-009 feature lifecycle and durable program reconciliation are complete
  - immutable OAM-010 task-start baselines are Canary cb149d427e6a954ee3ab163758465627bc1e643c Otheryn f59a58426b4d3910ba0cdc0d2332c24f31a1db4f upstream e0ac98e399d0f7e483f3668f57b78fcc45b6e53f and OTClient 2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f
  - character-progression depends on completed character-lifecycle and player-persistence foundations
  - player save blob is exact-identical across task-start legacy target and upstream
  - target Player and load-player broad blobs match pinned upstream while legacy broad blobs differ
  - progression-specific XP magic offline-training and selected persistence semantics are compatible across pinned target and legacy evidence
  - legacy disconnect-death protection is a real death-loss divergence introduced by Canary PR 40 and is not present in pinned target or upstream
  - whole legacy Player or IOLoginData transfer is rejected
  - Otheryn PR 27 changed only focused tests existing test registration and proof-scope documentation; no production runtime source changed
  - first target proof attempt exposed stack Player bad_weak_ptr in shared-ownership runtime paths and was rejected
  - second target proof proved regular-skill and magic advancement after shared ownership but direct gainExperience remained unsuitable for the minimal unit harness
  - final target proof removed the non-isolated gainExperience test rather than creating a second harness
  - final Otheryn head 4152ee997e4ab6e1b8ca8c4b18ab86853ebeea58 passed autofix run 29619165369 Required run 29619165343 and CI run 29619165487
  - final Linux debug Run Tests passed with four CharacterProgressionTest cases and 329 of 329 total tests passing
  - final test artifact 8421885698 digest sha256:b40a497f337a050312fa01632fefbfff7bb94e59f32449bb52131f197f759954
  - Otheryn PR 27 final audit had zero comments zero reviews and zero review threads
  - Otheryn PR 27 squash-merged as a4d095e3880787233bd194616dc6d19e6b94faaf
  - final migration disposition is character-progression ADAPT
  - legacy disconnect-death protection remains deliberately unadopted and requires separate session/protocol/runtime evidence if reconsidered
  - physical-client E2E is not required for this bounded compatibility disposition because no client protocol or UI mutation is made
  - Canary main advanced after task start only through non-overlapping security documentation and movement/floor-change E2E lifecycle/scenario work
  - PR 509 was reconstructed directly on current main 354abbbeeff7f7c3470987b32e873527fc6e1a2f with exactly the OAM-010 evidence report and active task
  - clean synchronized head f4889ab38cc3d39f1cf82d5eddea84c1442f0fe4 passed Agent Task Ownership run 29620401456 and CI run 29620401573

derived:
  - the clean target progression core is retained while the legacy module is classified ADAPT because a session-coupled death-loss policy is deliberately excluded rather than wholesale reused
  - target proof-only tests are sufficient for the selected core compatibility claims without production mutation
  - OAM-004D and OAM-005 remain authoritative for persistence and character lifecycle
unknown:
  - exact-head Ownership and CI conclusions after this ready checkpoint commit
  - ready-state final gate conclusions and whether main advances before merge
  - lifecycle and durable program reconciliation merge SHAs
conflicts: []
first_failure:
  marker: target-proof-harness-ownership-and-runtime-boundary
  evidence: initial focused target tests used stack-allocated Player objects and produced bad_weak_ptr in paths that require shared ownership; shared_ptr fixed real skill and magic advancement tests, while direct gainExperience still crossed broader runtime callback/global-service boundaries and was removed from executable proof rather than misclassified as a target defect
rejected_hypotheses:
  - exact file presence or target-upstream identity proves whole-module REUSE
  - broad Player file divergence alone proves ADAPT
  - legacy Canary should replace target Player or IOLoginData wholesale
  - target proof harness failures prove a production target bug
  - a second test/runtime harness should be created merely to force direct gainExperience coverage
  - legacy disconnect-death protection should be imported without separate session/runtime evidence
  - OAM-004D persistence boundaries may be reverted
  - combat weapon-proficiency or Wheel should be bundled into OAM-010
changed_paths:
  - docs/agents/tasks/active/CAN-20260717-oteryn-character-progression-revalidation.md
  - docs/agents/OTERYN_OAM_010_CHARACTER_PROGRESSION_REVALIDATION.md
validation:
  - command: fresh OAM-010 repository dependency and PR preflight
    result: PASS
    evidence: exact task-start heads pinned and no pre-existing OAM-010 ownership or canonical source overlap found
  - command: progression-specific semantic and persistence revalidation
    result: PASS
    evidence: selected XP magic offline-training and load-save semantics isolated from unrelated broad-file divergence; disconnect-death policy identified as the bounded legacy divergence
  - command: Otheryn PR 27 exact-head target proof
    result: PASS
    evidence: autofix 29619165369 Required 29619165343 CI 29619165487 all succeeded on 4152ee997e4ab6e1b8ca8c4b18ab86853ebeea58
  - command: final Linux debug focused/full test artifact 8421885698
    result: PASS
    evidence: four CharacterProgressionTest cases passed and full suite completed 329 of 329; artifact digest sha256:b40a497f337a050312fa01632fefbfff7bb94e59f32449bb52131f197f759954
  - command: Otheryn PR 27 final review audit and squash merge
    result: PASS
    evidence: zero comments reviews and review threads; merged as a4d095e3880787233bd194616dc6d19e6b94faaf
  - command: Canary PR 509 clean synchronization and pre-ready gates
    result: PASS
    evidence: head f4889ab38cc3d39f1cf82d5eddea84c1442f0fe4 is directly based on main 354abbbeeff7f7c3470987b32e873527fc6e1a2f with exactly two OAM-010 files; Ownership 29620401456 and CI 29620401573 passed
blockers: []
next_action: Require exact-head Ownership and CI on this ready checkpoint head; if green, mark PR 509 ready, require ready-state gates, audit comments reviews threads and current main, then squash merge with expected_head_sha and complete separate lifecycle/archive plus durable program reconciliation before OAM-011.
```

## Automated lifecycle completion

- Feature PR: #509.
- Feature head: `3d39b70ec5ae1271c3d1063c6d332b219adef338`.
- Merge commit: `f140a0e62cdcd1eaac39ab9b721d83e528ac3dae`.
- Merged at: `2026-07-17T23:25:01Z`.
- This record was moved from `tasks/active` by the post-merge lifecycle automation.
