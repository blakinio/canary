---
task_id: CAN-20260718-oteryn-achievements-revalidation
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-012
status: ready
agent: "GPT-5.5 Thinking"
branch: docs/oam-012-achievements-revalidation
base_branch: main
created: 2026-07-18T09:20:00+02:00
updated: 2026-07-18T11:26:00+02:00
last_verified_commit: "93064fda744b41d3dc96f231847f89cbe2f64f50"
risk: medium
related_issue: "blakinio/Otheryn#30"
related_pr: "524"
depends_on:
  - OAM-004
  - OAM-011
blocks:
  - OAM-013
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260718-oteryn-achievements-revalidation.md
    - docs/agents/OTERYN_OAM_012_ACHIEVEMENTS_REVALIDATION.md
  shared: []
  read_only:
    - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
    - docs/agents/OTERYN_TARGET_ARCHITECTURE_CONTRACT.md
    - docs/agents/OTERYN_OAM_011_WEAPON_PROFICIENCY_REVALIDATION.md
    - docs/agents/real-tibia/registry/modules/achievements.yaml
    - docs/ai-agent/ACHIEVEMENT_POINT_RECONCILIATION.md
    - src/creatures/players/components/player_achievement.cpp
    - src/creatures/players/components/player_achievement.hpp
    - data/scripts/lib/register_achievements.lua
    - src/creatures/players/components/weapon_proficiency.cpp
    - src/creatures/players/components/weapon_proficiency.hpp
    - tests/unit/players/components/player_achievement_test.cpp
    - tests/unit/players/components/weapon_proficiency_test.cpp
modules_touched:
  - achievements
reuses:
  - OAM-004 player-persistence KV durability boundary
  - OAM-011 accepted Weapon Proficiency mastery and 564-566 reconciliation boundary
  - existing Otheryn player-component unit-test harness
public_interfaces:
  - achievement catalogue IDs names grades secret flags and points
  - PlayerAchievement add remove query and point aggregation behavior
  - unlocked achievement KV names and timestamps
  - aggregate achievement points KV
  - achievement attainability evidence and bounded award hooks
cross_repo_tasks: []
---

# Goal

Revalidate exactly one canonical Oteryn migration unit, `achievements`, against current target architecture and immutable task-start baselines. Deliver only the smallest evidence-backed adaptation for catalogue metadata, point persistence reconciliation and proven attainability, without copying unrelated gameplay mechanics or weakening OAM-004 persistence boundaries.

# Immutable task-start baselines

- governance/legacy Canary: `blakinio/canary@d9c967d6e9b778da11a206d134d559f38ec1b8c8`
- Oteryn target: `blakinio/Otheryn@72f7bdc1a5afa9e9982c20bdcf3098c83dca543e`
- upstream evidence: `opentibiabr/canary@e0ac98e399d0f7e483f3668f57b78fcc45b6e53f`
- maintained OTClient: `blakinio/otclient@2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`

# Final disposition

```text
achievements → ADAPT
```

Selected coherent donor chain:

```text
Canary PR #256 → Canary PR #264 → Canary PR #288
```

Target delivery:

```text
blakinio/Otheryn PR #31
final head: 8ee4bfe3c6b867834447a5b9e206e1dbd44f66d2
squash merge: 4a16ca17ebd098cf9763bb3c07755bfd31ac1c43
issue #30: CLOSED / completed
```

# Acceptance criteria

- [x] Re-fetch exact Canary, Otheryn, upstream and maintained-client heads before task creation.
- [x] Verify no pre-existing open OAM-012 PR in Canary or Otheryn.
- [x] Audit task-start open Canary PR changed paths for canonical achievement overlap.
- [x] Select exactly one canonical module: `achievements`.
- [x] Confirm hard dependency `player-persistence` is a completed OAM foundation.
- [x] Pin exact task-start provenance for player-achievement component, runtime catalogue and legacy audit tooling.
- [x] Record initial disposition as `REVALIDATE`.
- [x] Publish draft governance PR #524 and bind this task to it.
- [x] Decompose accepted achievement work into the coherent #256 → #264 → #288 donor boundary.
- [x] Prove that five point metadata corrections and persisted aggregate reconciliation must migrate together.
- [x] Verify exact PR #264 donor blobs for PlayerAchievement production and focused test files.
- [x] Correct the revalidated `player_achievement_test.cpp` donor blob to `c10d90aa649322520739696507ba8a0ff2d05a06` after fail-closed mismatch detection.
- [x] Verify exact PR #288 donor blobs for the central catalogue and Weapon Proficiency integration/tests.
- [x] Prove ID 567 `The Forbidden Build` catalogue definition and exact twelve-weapon attainability integration belong in OAM-012.
- [x] Resolve the runtime catalogue-path question without creating a duplicate registry or overlay.
- [x] Classify every applicable architecture boundary with evidence.
- [x] Determine final disposition `ADAPT`.
- [x] Create a separate bounded Otheryn target delivery.
- [x] Keep final Otheryn PR diff to exactly eight bounded runtime/test paths.
- [x] Remove temporary donor-materialization plumbing before target proof.
- [x] Reverify all seven donor-controlled Git blob SHAs on the final target head after autofix.
- [x] Pass exact-head target CI and Required gates.
- [x] Pass Linux debug build, Canary runtime smoke, DB schema import and actual CTest execution.
- [x] Pass 7/7 `PlayerAchievementTest` cases.
- [x] Pass 10/10 `WeaponProficiencyTest` cases including the three `The Forbidden Build` cases.
- [x] Pass full target suite 346/346.
- [x] Record workflow run IDs and test/runtime/build artifact IDs and digests.
- [x] Audit target PR comments, reviews and review threads: zero blockers and zero unresolved threads.
- [x] Perform race-safe target `main` drift check immediately before merge.
- [x] Squash-merge Otheryn PR #31 with `expected_head_sha`.
- [x] Close Otheryn issue #30 as completed.
- [x] Clean-sync Canary governance branch directly onto current `main`, preserving only the two OAM-012 governance paths.
- [ ] Pass exact-head Canary Agent Task Ownership, CI and ready-state final gate as applicable.
- [ ] Audit Canary PR #524 comments, reviews and review threads immediately before merge.
- [ ] Squash-merge Canary governance PR #524 and record its merge SHA.
- [ ] Archive this active task in a separate lifecycle-only PR with target and Canary feature merge SHAs.
- [ ] Merge the lifecycle-only PR after Ownership + CI + review/thread audit.
- [ ] Reconcile the durable migration program in a separate program-only PR.
- [ ] Mark OAM-012 COMPLETE and keep OAM-013 NOT STARTED until durable program reconciliation merges.

# Exact target proof

GitHub Actions on final target head `8ee4bfe3c6b867834447a5b9e206e1dbd44f66d2`:

```text
CI #111                     run 29638502030  SUCCESS
Required #104               run 29638501951  SUCCESS
Repository Audit #7         run 29638501958  SUCCESS
autofix.ci #97              run 29638501946  SUCCESS
```

Linux debug:

```text
configure/build: PASS
Canary datapack runtime smoke: PASS
database schema import: PASS
CTest: 346/346 PASS
PlayerAchievementTest: 7/7 PASS
WeaponProficiencyTest: 10/10 PASS
```

Artifacts:

```text
linux-debug-test-logs
8427980477
sha256:170df7911fd928bb6af90c7f703e00554eccb4625a56d9fd54cc20e0854e0d3e

linux-linux-debug-runtime-smoke-logs
8427980648
sha256:ef03229e25ce6d4e7290627161d0043f8680f4d52f7757d5c7ef5bfe7ae8b0d5

canary-linux-debug
8427981926
sha256:f50ab03ace6982253968f47e34e8d64ee86ce5fc9f3e6c9b9bbe1a4e00b042a9
```

# Explicit exclusions

- no unrelated quest achievement hooks;
- no unrelated combat achievement hooks;
- no unrelated spell achievement hooks;
- no governance validator copied to Otheryn runtime;
- no duplicate achievement catalogue;
- no permanent achievement overlay/override;
- no generic KV schema redesign;
- no SQL/KV atomicity claim;
- no client changes;
- no protocol changes;
- no map changes;
- no asset changes;
- no claim of full Real Tibia achievement attainability parity;
- no OAM-013 work before OAM-012 feature, lifecycle and durable program reconciliation complete.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-18T11:26:00+02:00
head: 93064fda744b41d3dc96f231847f89cbe2f64f50
branch: docs/oam-012-achievements-revalidation
pr: 524
status: ready
context_routes:
  - agent-governance
  - oteryn-migration
  - achievements
owned_paths:
  - docs/agents/tasks/active/CAN-20260718-oteryn-achievements-revalidation.md
  - docs/agents/OTERYN_OAM_012_ACHIEVEMENTS_REVALIDATION.md
proven:
  - final disposition is achievements ADAPT
  - immutable task-start baselines remain Canary d9c967d6e9b778da11a206d134d559f38ec1b8c8 Otheryn 72f7bdc1a5afa9e9982c20bdcf3098c83dca543e upstream e0ac98e399d0f7e483f3668f57b78fcc45b6e53f OTClient 2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f
  - PR 264 point metadata corrections and persisted aggregate reconciliation are one compatibility boundary
  - unresolved stored achievement names fail closed during reconciliation
  - PR 288 supplies achievement 567 and an exact reviewed twelve-weapon attainability condition
  - one authoritative central catalogue is preserved at data/scripts/lib/register_achievements.lua
  - all seven donor-controlled final target files match exact pinned Git blob SHAs
  - exact-head target CI Required Repository Audit and autofix gates passed
  - Linux debug build runtime smoke DB import and actual CTest passed
  - full target suite passed 346 of 346
  - PlayerAchievement focused surface passed 7 of 7
  - WeaponProficiency focused surface passed 10 of 10
  - target PR review audit was clean and target main had no task-start drift immediately before merge
  - target PR 31 squash-merged with expected head protection as 4a16ca17ebd098cf9763bb3c07755bfd31ac1c43
  - target issue 30 is closed completed
  - governance branch was clean-synced directly to Canary main 417571a0a3990ed406d894211f8f0d78b190eb33
  - governance PR final scope contains only the evidence report and active OAM-012 task
derived:
  - catalogue metadata correction and persisted aggregate reconciliation must remain coupled
  - achievement 567 catalogue ownership belongs to OAM-012 and its exact reviewed Weapon Proficiency attainability integration is bounded to this package
  - the canonical data glob mismatch is governance metadata drift rather than permission for a second runtime catalogue
  - no physical-client E2E is required because no client or protocol boundary changed
unknown:
  - canonical module registry metadata should eventually name the proven central catalogue path explicitly
  - Canary governance feature merge SHA remains pending
  - lifecycle archive merge SHA remains pending
  - durable program reconciliation merge SHA remains pending
conflicts: []
first_failure:
  marker: none
  evidence: target delivery and target proof are complete; only Canary governance lifecycle and durable program closeout remain
rejected_hypotheses:
  - target upstream identity proves whole-module REUSE
  - catalogue-only point edits are safe with incrementally persisted aggregate points
  - defining achievement 567 alone proves attainability
  - all legacy achievement hooks belong in one target copy
  - a second catalogue or overlay is acceptable
  - legacy governance validators must be copied into Otheryn runtime
  - OAM-004 SQL and KV persistence may be treated as atomic
changed_paths:
  - docs/agents/OTERYN_OAM_012_ACHIEVEMENTS_REVALIDATION.md
  - docs/agents/tasks/active/CAN-20260718-oteryn-achievements-revalidation.md
validation:
  - command: exact donor provenance revalidation for OAM-012 target files
    result: PASS
    evidence: seven donor-controlled files match pinned Git blob SHAs including corrected player achievement test blob c10d90aa649322520739696507ba8a0ff2d05a06
  - command: exact-head Otheryn target CI and runtime proof
    result: PASS
    evidence: CI 29638502030 Required 29638501951 full CTest 346 of 346 PlayerAchievement 7 of 7 WeaponProficiency 10 of 10
  - command: target merge race-safe audit
    result: PASS
    evidence: zero blocking comments reviews and review threads; target main identical to immutable baseline immediately before expected-head squash merge
  - command: Canary governance clean synchronization
    result: PASS
    evidence: branch reset directly to Canary main 417571a0a3990ed406d894211f8f0d78b190eb33 before recreating only the two owned OAM-012 governance paths
blockers: []
next_action: Pass exact-head Canary Agent Task Ownership and CI for PR 524 then audit comments reviews and review threads and squash-merge; do not start OAM-013.
```
