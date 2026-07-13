---
task_id: CAN-20260712-weapon-proficiency-achievement-audit
status: ready-for-review
agent: "GPT-5.6 Thinking"
branch: feat/weapon-proficiency-achievement-audit
base_branch: main
created: 2026-07-12T20:40:00Z
updated: 2026-07-12T21:10:00Z
last_verified_commit: "3f41429f0a96cc6ac280391e64752c0fe08b8f6a"
risk: low
related_issue: ""
related_pr: "#195"
depends_on:
  - "merged achievement audit PR #165"
  - "merged helper repair PR #176"
  - "merged trigger repair PR #184"
  - "merged post-trigger cleanup PR #193"
blocks: []
owned_paths:
  - .github/workflows/weapon-proficiency-achievement-audit.yml
  - tools/ai-agent/weapon_proficiency_achievement_audit.py
  - tools/ai-agent/test_weapon_proficiency_achievement_audit.py
  - tools/ai-agent/weapon_proficiency_forbidden_build_validation.py
  - tools/ai-agent/test_weapon_proficiency_forbidden_build_validation.py
  - docs/ai-agent/WEAPON_PROFICIENCY_ACHIEVEMENT_REPORT.md
  - docs/ai-agent/WEAPON_PROFICIENCY_ACHIEVEMENT_RUNTIME_PLAN.json
  - docs/ai-agent/WEAPON_PROFICIENCY_FORBIDDEN_BUILD_BASELINE.json
  - docs/agents/tasks/active/CAN-20260712-weapon-proficiency-achievement-audit.md
  - docs/agents/ACTIVE_WORK.md
  - docs/agents/MODULE_CATALOG.md
modules_touched:
  - achievement validation
  - weapon proficiency
reuses:
  - merged achievement validation scanner
  - existing WeaponProficiency persistence and mastery state
  - existing PlayerAchievement component
public_interfaces:
  - canary-weapon-proficiency-achievement-audit-v1
  - canary-weapon-proficiency-forbidden-build-validation-v1
  - canary-weapon-proficiency-forbidden-build-baseline-v1
cross_repo_tasks: []
---

# Goal

Produce a deterministic, read-only evidence report for Weapon Proficiency achievements 564–567 before adding any registry definition or C++ award hook.

# Acceptance criteria

- [x] Confirm active registry metadata for IDs 564–567.
- [x] Record reference thresholds for mastery counts 1, 10 and 50.
- [x] Record the reviewed 12-weapon secret set without guessing item IDs.
- [x] Inspect mastery transition and load/normalization paths.
- [x] Detect whether achievements 564–566 have an active award path.
- [x] Detect the one-gain-to-mastery edge case in `addExperience`.
- [x] Identify load normalization as input for an explicit historical backfill decision.
- [x] Inventory all 12 server item IDs and protobuf `proficiency_id` values with source hashes.
- [x] Verify all 12 mappings against active `items.xml` and `proficiencies.json`.
- [x] Add deterministic runtime and asset/server validators with nine focused tests.
- [x] Produce a runtime implementation/test plan without modifying runtime.
- [x] Keep the PR read-only: no registry, C++, datapack, map, binary asset, database or production configuration changes.
- [x] Update module catalogue and durable report.
- [ ] Final ready-head dedicated workflow and required CI pass.
- [ ] Exact changed-file list and review threads checked on final head.
- [ ] Autonomous merge gate satisfied.

# Confirmed findings

## Definitions and runtime

- IDs 564, 565 and 566 are defined; ID 567 is absent.
- No active textual or WeaponProficiency C++ award hook exists for 564–566.
- Existing entries set `mastered=true` at maximum XP.
- The initial `try_emplace` path caps XP and returns without setting `mastered=true`.
- Load normalization derives `mastered` from stored XP.
- No public mastered-count API exists.
- `PlayerAchievement::add(uint16_t, ...)` is available for a later idempotent implementation.

## Secret-set evidence

- All twelve reviewed item IDs/names match active `items.xml`.
- All twelve protobuf proficiency IDs exist in active `proficiencies.json`.
- Asset `proficiencies.json` is byte-identical to the active server file by Git blob SHA-1 `49ec7edc6dacdee4a055fc0f3a9544f15eafabdd`.
- No binary asset is committed or exposed; only hashes and extracted metadata are versioned.

# Validation completed

## First runtime audit

```text
commit: dfde6885a1cef673b9a0d30e40ae7cbb02db44ea
run: 29208321129
artifact: 8264397432
artifact sha256: 39d18c0b38775f0a6245f8de028b3b810087ca403fa26eec5b43800758d6380c
```

Result: 3/4 definitions, 0/3 award paths, initial-mastery defect confirmed, load normalization available, no count API.

## Combined final evidence artifact

```text
run: 29208968551
artifact: 8264580164
artifact sha256: 27055d467bee7da8a9e32f3bbd5a4d78c8cb09f03e995717803740112ee71696
```

Verified:

- both validators completed successfully;
- nine focused tests passed;
- runtime findings: 5 errors, 2 warnings, 1 info;
- asset/server validator `ok=true`;
- 12/12 baseline entries verified;
- 420 active proficiency definitions;
- zero asset/server findings.

The runtime audit's XML-only eligibility count remains zero by design because these items use protobuf metadata. The independent asset/server validator is authoritative and reports 12/12.

# Decisions

| Decision | Reason/evidence |
|---|---|
| Audit before hooks | Mastery correctness, backfill and secret eligibility cross runtime, persistence and asset boundaries. |
| Separate runtime and asset validators | Missing hooks and invalid item/proficiency mappings are distinct failure modes. |
| Commit hashes and metadata only | Binary assets must not enter the repository. |
| Require exact active-server identity | Name discovery alone is insufficient for secret achievement implementation. |
| Split implementation | Mastery state/count API, threshold awards/backfill and ID 567 have different risks. |

# Required follow-up PR order

1. Fix initial-entry mastery state and expose one canonical normalized mastered-count API.
2. Implement IDs 564–566 threshold awards plus explicit existing-player backfill.
3. Add verified ID 567 definition and exact twelve-item condition.
4. Run the machine-readable runtime plan for each implementation PR.

# Risks and compatibility

- Runtime/data: unchanged by this audit.
- Security: no player data or secrets.
- Assets: no binary file committed or shared.
- Rollback: revert PR #195.

# Remaining work

1. Mark PR #195 ready and run all final checks on the current task-record head.
2. Review exact changed files, review threads and main overlap.
3. Merge only after all gates pass.
4. Archive this task in a documentation-only follow-up.

# Handoff

Read this task, `WEAPON_PROFICIENCY_ACHIEVEMENT_REPORT.md`, both validator sources, both test files and the runtime plan.

Do not add ID 567, award hooks or persistence migration inside this audit PR.

# Completion

- Final status: ready-for-review
- PR: #195
- Merge commit:
- Catalogue updated: yes, active entry
- Archived at:
