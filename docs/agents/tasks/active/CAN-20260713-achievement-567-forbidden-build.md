---
task_id: CAN-20260713-achievement-567-forbidden-build
status: ready-for-review
agent: "GPT-5.6 Thinking"
branch: fix/achievement-567-forbidden-build
base_branch: main
created: 2026-07-13T19:30:00+02:00
updated: 2026-07-13T23:25:00+02:00
last_verified_commit: "4ce65855d514d68703e0e36000bde85d1ef2ba63"
risk: medium
related_issue: ""
related_pr: "#288"
depends_on:
  - "merged comprehensive achievement audit #238"
  - "merged Weapon Proficiency audit #195"
  - "merged mastery-state/count API fix #212"
  - "merged mastery threshold awards #272"
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
public_interfaces: []
cross_repo_tasks: []
---

# Goal and exact scope

Implement achievement ID 567 `The Forbidden Build` only when the exact reviewed twelve-item set has normalized `mastered=true` Weapon Proficiency state. Add the canonical registry definition, live award path, silent existing-player reconciliation and focused regression coverage without changing item/proficiency data, persistence format or unrelated gameplay.

# Acceptance criteria

- [x] Re-read exact reviewed 12-item/proficiency evidence and current active definitions.
- [x] Confirm canonical registry metadata for ID 567 from the current reference baseline and active source page.
- [x] Add exactly one registry definition with grade 1, 3 points and `secret=true`.
- [x] Keep the twelve reviewed item IDs in one deterministic constant.
- [x] Require normalized `mastered=true` for every exact reviewed item ID.
- [x] Do not infer possession, equipment or inventory semantics not present in the evidence.
- [x] Award through canonical idempotent `PlayerAchievement::add`.
- [x] Reuse live false-to-true mastery reconciliation.
- [x] Support silent existing-player reconciliation after stored state normalization in `load()`.
- [x] Test exact set identity, partial set, all twelve, one unmastered, duplicate/non-target substitution and extra entries.
- [x] Update dedicated validator, validator tests and reviewed evidence.
- [x] Regenerate comprehensive per-achievement report with ID 567 `partially-confirmed`.
- [x] Keep gameplay/data changes limited to this one achievement.
- [x] Remove all temporary workflows from the final diff.
- [x] Focused Python tests, validator generation, JSON validation and `git diff --check` pass.
- [x] Full C++ build and `canary_ut` pass on validated head `4ce65855d514d68703e0e36000bde85d1ef2ba63`.
- [x] Canary/global datapack smoke, Windows, macOS and Docker gates pass where selected.
- [x] Dedicated Achievement Validation and Weapon Proficiency Achievement Audit pass on validated head.
- [x] AI Agent Tools, Agent Task Ownership, autofix and review gates pass.
- [x] Exact ten-file diff and current `main` overlap were reviewed; intervening OTBM/instance commits were unrelated.
- [ ] Auto-merge is enabled only after all gates pass on the final task-record head.
- [ ] Task is archived after merge.

# Sources and observation dates

| Source | Read | Purpose |
|---|---|---|
| `docs/ai-agent/WEAPON_PROFICIENCY_ACHIEVEMENT_REPORT.md` | 2026-07-13 | reviewed exact item/proficiency contract and implementation order |
| `docs/ai-agent/ACHIEVEMENT_REVIEWED_EVIDENCE.json` | 2026-07-13 | previous ID 567 conflict and proof boundary |
| `docs/ai-agent/ACHIEVEMENT_REFERENCE_CATALOG.json` revision `1188274` | 2026-07-13 | canonical ID, name, grade, secrecy, points, implementation date and linked item entities |
| `https://tibia.fandom.com/wiki/The_Forbidden_Build` | 2026-07-13 | active externally observable condition and description |
| `data/scripts/lib/register_achievements.lua` | 2026-07-13 | active registry gap at ID 567 |
| `data/items/items.xml` and active proficiency data | inherited from audited evidence, revalidated by dedicated workflow | item identity/proficiency eligibility |
| `src/creatures/players/components/weapon_proficiency.*` | 2026-07-13 | normalized state, live transition and login reconciliation surfaces |
| merged PRs #195, #212, #238, #272 | 2026-07-13 | prerequisite audit/runtime contracts |

# Confirmed findings

- Reference revision `1188274` defines ID 567 as `The Forbidden Build`, grade 1, secret, premium, 3 points, implemented July 21, 2025.
- The active source condition is earning Mastery with the exact twelve reviewed weapons; it does not require simultaneous equipment, possession or inventory scanning.
- The exact active item/proficiency contract is:

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

- `WeaponProficiency::load()` normalizes each accepted persisted entry before calling the silent reconciliation surface.
- Live reconciliation runs only after a false-to-true mastery transition or a newly-created already-mastered entry.
- `PlayerAchievement::add` is idempotent and preserves the existing name-keyed achievement persistence contract.
- The implementation checks every exact item ID through `std::ranges::all_of`; extra entries and repeated writes cannot substitute for a missing target.
- Generated comprehensive audit reports 542 definitions, 349 public, 193 secret, 1431 points and ID 567 as `partially-confirmed`.
- Full repository CI compiled and tested the implementation on Linux debug/release, Windows CMake/MSBuild and macOS; selected runtime smoke and Docker validation passed.

# Uncertain findings requiring further proof

- Full real-client E2E remains unproven.
- CipSoft historical backfill notification behavior is not public; Canary follows the established silent login reconciliation policy from PR #272.
- Exact internal CipSoft implementation details are unavailable; this PR targets externally observable functional equivalence.

# Conflicts between sources and engine

Before this PR, the reference defined ID 567 but Canary had no registry definition, award path or backfill. The exact twelve-item proficiency contract was already proven. This PR resolves that bounded conflict; it does not claim complete Real Tibia parity for unrelated achievements.

# Changed files and purpose

| Path | Purpose |
|---|---|
| `data/scripts/lib/register_achievements.lua` | canonical ID 567 definition |
| `src/creatures/players/components/weapon_proficiency.hpp` | private exact-set/condition helper declarations |
| `src/creatures/players/components/weapon_proficiency.cpp` | exact item set, all-mastered condition and canonical award reconciliation |
| `tests/unit/players/components/weapon_proficiency_test.cpp` | exact, partial, complete, unmastered and substitution tests |
| `tools/ai-agent/weapon_proficiency_achievement_audit.py` | exact metadata/item-set/condition/award validation |
| `tools/ai-agent/test_weapon_proficiency_achievement_audit.py` | registry and real-repository validator regressions |
| `docs/ai-agent/ACHIEVEMENT_REVIEWED_EVIDENCE.json` | status, path/line evidence, backfill and test state for ID 567 |
| `docs/ai-agent/ACHIEVEMENT_COMPREHENSIVE_VALIDATION.md` | regenerated full current per-achievement evidence report |
| `docs/ai-agent/WEAPON_PROFICIENCY_ACHIEVEMENT_REPORT.md` | focused implementation update and remaining E2E boundary |
| this task | durable execution record and Handoff |

# Commands and tests executed

Successful materializer run `29284389744` executed:

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

Repository CI additionally executed the configured CMake builds, `canary_ut`, Canary/global datapack smoke, schema import, Windows builds, macOS build/smoke and Docker validation.

# Validation and CI

| Commit/run | Check | Result |
|---|---|---|
| `8aee4b81229de99249dd5004f929da7e5eadb59d` / `29284052697` | first materializer | implementation applied; validation failed on stale comprehensive-report schema assertion |
| `09f9692d6675bffaebbc5774f9eb4f90d9b35348` / `29284307006` | exact workflow patch attempt | failed before updating materializer; replaced by extractor runner |
| `bb7134c7fd1ea1e93c516719817c64d1a5b44d42` / `29284389744` | safe extraction, implementation, focused tests, both audits, invariants, commit and push | passed |
| same run / artifact `8292576204` | diagnostic log | published, digest `sha256:d57191ba9b51e2358d053b47ff130a3db00761cbdfd74808af19c952196c7aa1` |
| `17240b51569daa6b861a3af811bee900eb84cd19` | clean rebuild on `main` `360d79ebad5802edd4d89e99d0f210ab19b36b60` | exact ten-file diff; no overlap with intervening OTBM/instance commits |
| `4ce65855d514d68703e0e36000bde85d1ef2ba63` / `29285133587` | Achievement Validation | passed |
| same / `29285133664` | Weapon Proficiency Achievement Audit | passed |
| same / `29285133588` | AI Agent Tools | passed |
| same / `29285133746` | Agent Task Ownership | passed |
| same / `29285133718` | autofix.ci | passed |
| same / `29285133895` | full CI: Fast Checks, Lua, Linux debug/release, `canary_ut`, datapack smoke, Windows, macOS and Docker | passed |

Never represent skipped, cancelled or superseded runs as passed.

# Failed approaches and causes

1. Run `29284052697` used `row["definition"]["present"]`; the v2 comprehensive schema represents this as `row["definition"]["status"]`. Gameplay changes had applied correctly, but no commit was pushed.
2. Run `29284307006` attempted an exact in-place workflow patch and failed before producing a branch update. It was superseded by a safe runner that extracted the already-reviewed implementation block and used the correct invariant.
3. Superseded concurrent materializer runs are not validation evidence and are not cited as passing.
4. All temporary workflow files were removed by successful run `29284389744` and the later handoff refresh workflow removed itself.

# Design decisions

| Decision | Reason |
|---|---|
| Keep ID 567 separate from thresholds 564–566 | different condition, definition and test boundary |
| Reuse reviewed exact item/proficiency evidence | avoid inventing item sets or duplicating validators |
| Use exact item IDs, not names | stable runtime identity and no localization/name ambiguity |
| Require stored normalized `mastered` state for every ID | matches externally observable Mastery condition and existing persistence |
| Reuse one reconciliation surface | live transitions and existing-player backfill cannot drift |
| Award only through `PlayerAchievement::add` | canonical idempotence, notification and persistence behavior |
| Do not scan possession/equipment | source condition is historical Mastery, not current inventory state |
| No item/proficiency data mutation | consume previously verified active contract rather than rewrite it |
| Keep status `partially-confirmed` | static/unit/server-CI proof is not full real-client E2E |

# Exact remaining work

1. Run the final task-record head through current-head repository gates.
2. Recheck `main`, exact diff, mergeability and review state.
3. Enable auto-merge only after those final gates pass.
4. Confirm merge commit on `main`.
5. Move this task to `docs/agents/tasks/archive/` in a focused cleanup PR unless already done by another agent.

# Handoff

- branch: `fix/achievement-567-forbidden-build`
- validated implementation head: `4ce65855d514d68703e0e36000bde85d1ef2ba63`
- PR: #288
- completed: evidence review; canonical definition; exact 12-item all-mastered condition; live award; silent login reconciliation; focused C++ tests; both validators; reviewed evidence; comprehensive report; full repository CI
- not completed: final task-record-head gates, auto-merge, merge confirmation and archival
- last correct result: full CI run `29285133895` success; dedicated runs listed above
- blocker: none
- first concrete next step: inspect workflows triggered by this task update, then compare against current `main` and enable auto-merge if all gates remain green
- exact reproduction commands: listed above

# Completion

- Final status: ready-for-review
- PR: #288
- Merge commit:
- Archived at:
