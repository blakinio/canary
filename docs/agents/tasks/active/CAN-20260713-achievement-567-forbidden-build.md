---
task_id: CAN-20260713-achievement-567-forbidden-build
status: ready-for-review
agent: "GPT-5.6 Thinking"
branch: fix/achievement-567-forbidden-build
base_branch: main
created: 2026-07-13T19:30:00+02:00
updated: 2026-07-13T23:58:00+02:00
last_verified_commit: "d8e8d145342819dc924b0b0b5e7102f7876ef458"
risk: medium
related_issue: ""
related_pr: "#288"
depends_on:
  - "merged comprehensive achievement audit #238"
  - "merged Weapon Proficiency audit #195"
  - "merged mastery-state/count API fix #212"
  - "merged mastery threshold awards #272"
  - "merged achievement point reconciliation #264"
blocks: []
owned_paths:
  - data/scripts/lib/register_achievements.lua
  - src/creatures/players/components/weapon_proficiency.hpp
  - src/creatures/players/components/weapon_proficiency.cpp
  - tests/unit/players/components/weapon_proficiency_test.cpp
  - tools/ai-agent/weapon_proficiency_achievement_audit.py
  - tools/ai-agent/test_weapon_proficiency_achievement_audit.py
  - docs/ai-agent/ACHIEVEMENT_REVIEWED_EVIDENCE.json
  - docs/ai-agent/ACHIEVEMENT_COMPREHENSIVE_VALIDATION.md
  - docs/ai-agent/WEAPON_PROFICIENCY_ACHIEVEMENT_REPORT.md
  - docs/agents/tasks/active/CAN-20260713-achievement-567-forbidden-build.md
modules_touched:
  - WeaponProficiency runtime
  - achievement registry
  - achievement validation evidence
reuses:
  - existing WeaponProficiency normalized mastery state
  - PlayerAchievement::add(uint16_t, ...)
  - reviewed 12-item/proficiency evidence from PR #195/#238
  - threshold reconciliation pattern from PR #272
  - persisted-point reconciliation from PR #264
public_interfaces: []
cross_repo_tasks: []
---

# Goal and exact scope

Implement achievement ID 567 `The Forbidden Build` only when the exact reviewed twelve-item set has normalized `mastered=true` Weapon Proficiency state. Add the canonical registry definition, live award path, silent existing-player reconciliation and focused regression coverage without changing item/proficiency data, persistence format or unrelated gameplay.

# Acceptance criteria

- [x] Re-read exact reviewed 12-item/proficiency evidence and current active definitions.
- [x] Confirm canonical registry metadata for ID 567 from reference revision `1188274` and the active source page.
- [x] Add exactly one registry definition with grade 1, 3 points and `secret=true`.
- [x] Keep the twelve reviewed item IDs in one deterministic constant.
- [x] Require normalized `mastered=true` for every exact reviewed item ID.
- [x] Do not infer possession, equipment or inventory semantics not present in the evidence.
- [x] Award through canonical idempotent `PlayerAchievement::add`.
- [x] Reuse live false-to-true mastery reconciliation.
- [x] Support silent existing-player reconciliation after stored state normalization in `load()`.
- [x] Test exact set identity, partial set, all twelve, one unmastered and non-target substitution.
- [x] Update dedicated validator, validator tests and reviewed evidence.
- [x] Regenerate comprehensive per-achievement report with ID 567 `partially-confirmed`.
- [x] Keep gameplay/data changes limited to this one achievement.
- [x] Remove all temporary workflows from the final diff.
- [x] Focused Python tests, validator generation, JSON validation and diff checks pass.
- [x] Full C++ build and `canary_ut` pass on validated implementation heads.
- [x] Canary/global datapack smoke, Windows, macOS and Docker gates pass where selected.
- [x] Dedicated Achievement Validation and Weapon Proficiency Achievement Audit pass.
- [x] AI Agent Tools, Agent Task Ownership and autofix pass.
- [x] Exact ten-file diff was reviewed.
- [x] Real overlap with point-reconciliation PR #264 was detected and resolved by taking the latest `main` registry and changing only placeholder `[567]`.
- [x] The resulting registry patch preserves Fiend Rider, Hope of the Merudri, Alpha Rider and the other #264 point corrections.
- [ ] All gates pass on the final API-authored task-update head.
- [ ] Auto-merge is enabled after final gates pass.
- [ ] Task is archived after merge.

# Sources and observation dates

| Source | Read | Purpose |
|---|---|---|
| `docs/ai-agent/WEAPON_PROFICIENCY_ACHIEVEMENT_REPORT.md` | 2026-07-13 | reviewed exact item/proficiency contract |
| `docs/ai-agent/ACHIEVEMENT_REVIEWED_EVIDENCE.json` | 2026-07-13 | prior ID 567 evidence boundary |
| `docs/ai-agent/ACHIEVEMENT_REFERENCE_CATALOG.json` revision `1188274` | 2026-07-13 | canonical metadata and linked item entities |
| `https://tibia.fandom.com/wiki/The_Forbidden_Build` | 2026-07-13 | externally observable condition and description |
| `data/scripts/lib/register_achievements.lua` | 2026-07-13 | registry definition and overlap resolution |
| active item/proficiency data | 2026-07-13 | exact item identity and active proficiency eligibility |
| `src/creatures/players/components/weapon_proficiency.*` | 2026-07-13 | normalized state, live transition and login reconciliation |
| PR #264 and cleanup #296 | 2026-07-13 | preservation of current achievement point corrections |
| merged PRs #195, #212, #238 and #272 | 2026-07-13 | prerequisite audit/runtime contracts |

# Confirmed findings

- ID 567 is `The Forbidden Build`, grade 1, secret, premium and worth 3 points.
- The observed condition is Mastery with all twelve reviewed weapons; current possession or equipment is not required.
- Exact item/proficiency contract:

```text
9385  Club of the Fury              proficiency 245
21179 Glooth Blade                  proficiency 413
9373  Glutton's Mace                proficiency 244
21178 Glooth Club                   proficiency 411
3284  Ice Rapier                    proficiency 161
9396  Incredible Mumpiz Slayer      proficiency 242
9378  Musician's Bow                proficiency 331
26073 Ornate Carving Rod            proficiency 162
26009 Ornate Mayhem Wand            proficiency 177
9375  Pointed Rabbitslayer          proficiency 259
1781  Small Stone                   proficiency 125
2992  Snowball                      proficiency 126
```

- `WeaponProficiency::load()` normalizes accepted persisted entries before silent reconciliation.
- Live reconciliation runs after a false-to-true mastery transition or a newly-created already-mastered entry.
- `PlayerAchievement::add` is idempotent and preserves the existing name-keyed achievement persistence contract.
- `std::ranges::all_of` requires every exact ID; extras and repeated writes cannot replace a missing target.
- The comprehensive audit reports ID 567 as `partially-confirmed`, not `confirmed`, because real-client E2E remains absent.
- PR #264 changed achievement point metadata and point reconciliation. Its registry changes are preserved.
- After overlap repair, the registry diff is exactly one replacement: `-- [567] = Unknown/non-existent` becomes the canonical ID 567 definition.

# Uncertain findings requiring further proof

- Full real-client gameplay E2E remains unproven.
- CipSoft historical-backfill notification behavior is not public; Canary follows the silent login reconciliation policy established in PR #272.
- Internal CipSoft implementation details are unavailable; this work targets externally observable functional equivalence.

# Conflicts between sources and engine

Before this PR, the reference defined ID 567 but Canary had no registry definition, award path or backfill. The exact item/proficiency contract was already proven. This PR resolves that bounded conflict. A later concurrent change, PR #264, touched the same registry for point reconciliation; the branch was rebuilt from latest `main` and only the ID 567 placeholder was changed.

# Changed files and purpose

| Path | Purpose |
|---|---|
| `data/scripts/lib/register_achievements.lua` | canonical ID 567 definition, based on the latest point-reconciled registry |
| `src/creatures/players/components/weapon_proficiency.hpp` | private exact-set/condition declarations |
| `src/creatures/players/components/weapon_proficiency.cpp` | exact item set, all-mastered condition and award reconciliation |
| `tests/unit/players/components/weapon_proficiency_test.cpp` | exact, partial, complete, unmastered and substitution tests |
| `tools/ai-agent/weapon_proficiency_achievement_audit.py` | metadata/item-set/condition/award validation |
| `tools/ai-agent/test_weapon_proficiency_achievement_audit.py` | validator regressions |
| `docs/ai-agent/ACHIEVEMENT_REVIEWED_EVIDENCE.json` | reviewed ID 567 status and path/line evidence |
| `docs/ai-agent/ACHIEVEMENT_COMPREHENSIVE_VALIDATION.md` | regenerated per-achievement evidence report |
| `docs/ai-agent/WEAPON_PROFICIENCY_ACHIEVEMENT_REPORT.md` | focused implementation update and E2E boundary |
| this task | durable execution record and Handoff |

# Commands and tests executed

```text
clang-format -i src/creatures/players/components/weapon_proficiency.hpp src/creatures/players/components/weapon_proficiency.cpp tests/unit/players/components/weapon_proficiency_test.cpp
python -m py_compile tools/ai-agent/weapon_proficiency_achievement_audit.py tools/ai-agent/test_weapon_proficiency_achievement_audit.py
python -m unittest discover -s tools/ai-agent -p "test_weapon_proficiency_achievement_audit.py" -v
python -m unittest discover -s tools/ai-agent -p "test_achievement_validation.py" -v
python -m json.tool docs/ai-agent/ACHIEVEMENT_REVIEWED_EVIDENCE.json
python tools/ai-agent/weapon_proficiency_achievement_audit.py --repository-root . --output artifacts/WEAPON_PROFICIENCY_ACHIEVEMENT_AUDIT.json --markdown artifacts/WEAPON_PROFICIENCY_ACHIEVEMENT_AUDIT.md
python tools/ai-agent/achievement_validation.py --repository-root . --reference-baseline docs/ai-agent/ACHIEVEMENT_REFERENCE_BASELINE.json --reference-catalog docs/ai-agent/ACHIEVEMENT_REFERENCE_CATALOG.json --reviewed-evidence docs/ai-agent/ACHIEVEMENT_REVIEWED_EVIDENCE.json --output artifacts/ACHIEVEMENT_AUDIT.json --markdown artifacts/ACHIEVEMENT_AUDIT.md --allow-findings
git diff --check
git diff --cached --check
```

Repository CI also executes CMake builds, `canary_ut`, datapack smoke, schema import, Windows, macOS and Docker validation.

# Validation and CI

| Commit/run | Check | Result |
|---|---|---|
| `8aee4b81229de99249dd5004f929da7e5eadb59d` / `29284052697` | first materializer | implementation applied; validation failed on stale `definition.present` assertion |
| `09f9692d6675bffaebbc5774f9eb4f90d9b35348` / `29284307006` | exact workflow patch attempt | failed before branch update; superseded |
| `bb7134c7fd1ea1e93c516719817c64d1a5b44d42` / `29284389744` | safe materializer, focused tests, both audits, invariants, commit | passed |
| same run / artifact `8292576204` | diagnostic log | digest `sha256:d57191ba9b51e2358d053b47ff130a3db00761cbdfd74808af19c952196c7aa1` |
| `4ce65855d514d68703e0e36000bde85d1ef2ba63` / `29285133895` | full platform CI and `canary_ut` | passed |
| `5feb736d979a76f43815da99bd5945c74c1a4a60` / `29286262746` | full task-record-head CI | passed |
| `caf9b515b75dd1237caadae275f78bea6a971511` / `29287113024` | full CI before #264 overlap repair | passed |
| `d8e8d145342819dc924b0b0b5e7102f7876ef458` | rebuilt from latest `main` `7cc47983cc78e06587fee09d1dcc5cc597836ade` | exact ten-file diff; registry patch only adds 567 and preserves #264 |

Never represent skipped, cancelled, `action_required` or superseded runs as passed.

# Failed approaches and causes

1. First materializer used a stale comprehensive schema assertion; no gameplay commit was pushed.
2. Exact workflow patch attempt failed and was replaced by a safe extractor runner.
3. Bot-authored commits produced `action_required`; final validation is triggered by this API-authored task update.
4. A naive rebase using the old registry blob would have reverted PR #264 point corrections. It was rejected. The successful rebase starts from latest `main` and patches only ID 567.
5. All temporary workflow files remove themselves and are absent from the final diff.

# Design decisions

| Decision | Reason |
|---|---|
| Keep ID 567 separate from thresholds 564–566 | different condition, definition and test boundary |
| Use reviewed exact item IDs, not names | stable identity and no localization ambiguity |
| Require normalized `mastered` state for every ID | matches the observed historical Mastery condition |
| Reuse one reconciliation surface | live transitions and existing-player backfill cannot drift |
| Award through `PlayerAchievement::add` | canonical idempotence, notification and persistence |
| Do not scan possession/equipment | not part of the observed condition |
| Preserve latest `main` registry and patch one placeholder | prevents regression of point reconciliation #264 |
| Keep status `partially-confirmed` | server/unit proof is not real-client E2E |

# Exact remaining work

1. Run all workflows on the API-authored task-update head.
2. Recheck latest `main`, exact diff, mergeability and review state.
3. Enable auto-merge when every current-head gate is green.
4. Confirm merge commit on `main`.
5. Move this task to `docs/agents/tasks/archive/` in a focused cleanup PR unless already archived automatically.

# Handoff

- branch: `fix/achievement-567-forbidden-build`
- overlap-resolved implementation tree: `d8e8d145342819dc924b0b0b5e7102f7876ef458`
- PR: #288
- completed: source review, canonical definition, exact 12-item condition, live award, silent login reconciliation, tests, both validators, reports, full CI and #264 overlap resolution
- not completed: final API-head gates, auto-merge, merge confirmation and archival
- last correct result: full CI `29287113024` success before overlap repair; overlap repair changes only registry source baseline and keeps the same ID 567 patch
- blocker: none
- first concrete next step: inspect workflows triggered by this task update and enable auto-merge after all current-head gates pass
- reproduction commands: listed above

# Completion

- Final status: ready-for-review
- PR: #288
- Merge commit:
- Archived at:
