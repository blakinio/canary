---
task_id: CAN-20260717-oteryn-character-progression-revalidation
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-010
status: completed
agent: "GPT-5.5 Thinking"
branch: docs/oam-010-character-progression-revalidation
base_branch: main
created: 2026-07-17T22:03:00+02:00
updated: 2026-07-17T23:24:00+02:00
completed: 2026-07-17T23:24:00+02:00
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
    - docs/agents/OTERYN_OAM_010_CHARACTER_PROGRESSION_REVALIDATION.md
  shared: []
  read_only:
    - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
    - docs/agents/OTERYN_TARGET_ARCHITECTURE_CONTRACT.md
    - src/creatures/players/player.cpp
    - src/creatures/players/player.hpp
    - src/io/functions/iologindata_load_player.cpp
    - src/io/functions/iologindata_save_player.cpp
modules_touched:
  - character-progression
cross_repo_tasks: []
---

# OAM-010 — Character Progression Revalidation

## Completed result

Final disposition:

```text
character-progression ADAPT
```

The clean Otheryn/upstream progression core is retained. Whole-module legacy `REUSE` is rejected because legacy Canary contains a session-coupled disconnect-death-protection policy that is not present in the pinned clean target/upstream and was deliberately not imported without separate session/protocol/runtime evidence.

No broad legacy `Player` or IOLoginData file was copied into Otheryn. OAM-004D persistence and OAM-005 character-lifecycle boundaries remain authoritative.

## Exact baselines

```text
Canary task-start: cb149d427e6a954ee3ab163758465627bc1e643c
Otheryn task-start: f59a58426b4d3910ba0cdc0d2332c24f31a1db4f
upstream evidence: e0ac98e399d0f7e483f3668f57b78fcc45b6e53f
maintained OTClient: 2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f
```

## Target proof delivery

Otheryn PR #27 was proof-only and changed no production runtime source.

```text
final PR head: 4152ee997e4ab6e1b8ca8c4b18ab86853ebeea58
autofix run 29619165369: PASS
Required run 29619165343: PASS
CI run 29619165487: PASS
Linux debug Run Tests: PASS
focused CharacterProgressionTest cases: 4/4 PASS
full suite: 329/329 PASS
artifact: 8421885698
artifact digest: sha256:b40a497f337a050312fa01632fefbfff7bb94e59f32449bb52131f197f759954
review comments: 0
submitted reviews: 0
review threads: 0
target squash merge: a4d095e3880787233bd194616dc6d19e6b94faaf
```

The accepted focused proof covers XP thresholds, offline-training time bounds, regular-skill advancement and magic-level advancement. The zero-stamina XP gate remains source-reviewed evidence because direct `gainExperience` crosses broader runtime callback/global-service boundaries in the minimal unit harness; OAM-010 did not create a second harness merely to force that path.

## Canary governance completion

PR #509 was synchronized directly onto `main@354abbbeeff7f7c3470987b32e873527fc6e1a2f` with exactly the task and durable OAM-010 evidence report.

```text
pre-ready synchronized head: f4889ab38cc3d39f1cf82d5eddea84c1442f0fe4
pre-ready Ownership 29620401456: PASS
pre-ready CI 29620401573: PASS
final ready checkpoint head: 3d39b70ec5ae1271c3d1063c6d332b219adef338
final Ownership 29620482703: PASS
ready-state CI 29620514952: PASS
Required: PASS
final comments: 0
final reviews: 0
final review threads: 0
feature squash merge: f140a0e62cdcd1eaac39ab9b721d83e528ac3dae
```

## Boundaries preserved

- OAM-004D player SQL versus later KV durability semantics remain unchanged.
- OAM-005 character ownership/load/save lifecycle remains unchanged.
- OAM-008 `vocations → REUSE` remains unchanged.
- OAM-009 physical vocation/login proof remains a separate proof boundary.
- No Real Tibia progression formula/value parity is claimed.
- No protocol/client/UI mutation is included.
- No new physical-client E2E claim is made for OAM-010.
- Legacy disconnect-death protection remains deliberately unadopted.

## Lifecycle

Feature delivery and Canary governance are complete. This record was moved from `tasks/active` to `tasks/archive` by the separate OAM-010 lifecycle change after feature PR #509 merged.

OAM-011 remains inactive until this lifecycle archive and the separate durable Oteryn program reconciliation are both merged.
