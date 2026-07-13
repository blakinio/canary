---
task_id: CAN-20260713-achievement-567-forbidden-build
status: completed
agent: "GPT-5.6 Thinking"
branch: fix/achievement-567-forbidden-build
base_branch: main
created: 2026-07-13T19:30:00+02:00
updated: 2026-07-14T00:20:00+02:00
last_verified_commit: "67ac28ee314ccc31671344515633c9411c3fe9df"
risk: medium
related_issue: ""
related_pr: "#288"
merge_commit: "c9b607bdc5b9253f3eaf75b0f4a513877b8a42d7"
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
modules_touched:
  - WeaponProficiency runtime
  - achievement registry
  - achievement validation evidence
reuses:
  - WeaponProficiency normalized mastery state
  - PlayerAchievement::add(uint16_t, ...)
  - reviewed twelve-item evidence from PR #195/#238
  - reconciliation pattern from PR #272
  - persisted-point reconciliation from PR #264
public_interfaces: []
cross_repo_tasks: []
---

# Goal

Implement achievement ID 567 `The Forbidden Build` with externally observable Real Tibia behavior: award it when the exact reviewed twelve Weapon Proficiency item IDs have normalized `mastered=true` state, with live awards and silent existing-player reconciliation.

# Completed implementation

- Added the canonical achievement definition: grade 1, 3 points, secret.
- Added one exact twelve-item ID constant.
- Required every target entry to exist and have normalized `mastered=true` state.
- Awarded through canonical idempotent `PlayerAchievement::add(567, message)`.
- Reused the same reconciliation surface for live mastery transitions and login-time backfill.
- Added focused exact-set, partial-set, complete-set, unmastered-entry and non-target-substitution tests.
- Updated the dedicated Weapon Proficiency audit and comprehensive achievement audit.
- Classified ID 567 as `partially-confirmed`; real-client E2E remains a separate proof layer.
- Preserved all achievement point corrections and persisted-point reconciliation from PR #264.

# Exact condition

```text
9385  Club of the Fury
21179 Glooth Blade
9373  Glutton's Mace
21178 Glooth Club
3284  Ice Rapier
9396  Incredible Mumpiz Slayer
9378  Musician's Bow
26073 Ornate Carving Rod
26009 Ornate Mayhem Wand
9375  Pointed Rabbitslayer
1781  Small Stone
2992  Snowball
```

Every exact ID must have `mastered=true`. Extra entries, duplicate writes and unrelated mastered weapons cannot replace a missing target.

# Sources

- TibiaWiki/Fandom `The Forbidden Build`, observed 2026-07-13.
- Achievement reference revision `1188274`.
- `docs/ai-agent/WEAPON_PROFICIENCY_ACHIEVEMENT_REPORT.md`.
- `docs/ai-agent/ACHIEVEMENT_REVIEWED_EVIDENCE.json`.
- Active item and Weapon Proficiency definitions.
- Merged PRs #195, #212, #238, #264 and #272.

# Validation

Final head:

```text
67ac28ee314ccc31671344515633c9411c3fe9df
```

| Workflow | Run | Result |
|---|---:|---|
| Weapon Proficiency Achievement Audit | 29288222087 | passed |
| Achievement Validation | 29288222088 | passed |
| AI Agent Tools | 29288222109 | passed |
| Agent Task Ownership | 29288222118 | passed |
| autofix.ci | 29288222092 | passed |
| Full CI | 29288222261 | passed |

Full CI covered Fast Checks, Lua tests, Linux debug/release, `canary_ut`, datapack smoke, Windows CMake/MSBuild, macOS and Docker validation. Review threads and submitted reviews were empty.

Preparation evidence:

- materializer run `29284389744` passed focused validators and evidence invariants;
- diagnostic artifact `8292576204`;
- artifact digest `sha256:d57191ba9b51e2358d053b47ff130a3db00761cbdfd74808af19c952196c7aa1`.

# Commands

```text
python -m unittest discover -s tools/ai-agent -p "test_weapon_proficiency_achievement_audit.py" -v
python -m unittest discover -s tools/ai-agent -p "test_achievement_validation.py" -v
python -m py_compile tools/ai-agent/weapon_proficiency_achievement_audit.py tools/ai-agent/test_weapon_proficiency_achievement_audit.py
python -m json.tool docs/ai-agent/ACHIEVEMENT_REVIEWED_EVIDENCE.json
python tools/ai-agent/weapon_proficiency_achievement_audit.py --repository-root . --output artifacts/WEAPON_PROFICIENCY_ACHIEVEMENT_AUDIT.json --markdown artifacts/WEAPON_PROFICIENCY_ACHIEVEMENT_AUDIT.md
python tools/ai-agent/achievement_validation.py --repository-root . --reference-baseline docs/ai-agent/ACHIEVEMENT_REFERENCE_BASELINE.json --reference-catalog docs/ai-agent/ACHIEVEMENT_REFERENCE_CATALOG.json --reviewed-evidence docs/ai-agent/ACHIEVEMENT_REVIEWED_EVIDENCE.json --output artifacts/ACHIEVEMENT_AUDIT.json --markdown artifacts/ACHIEVEMENT_AUDIT.md --allow-findings
git diff --check
```

# Failed approaches and resolutions

1. The first materializer used obsolete `definition.present` instead of v2 `definition.status`; no gameplay commit was pushed.
2. A direct workflow-patch attempt failed before branch mutation; a reviewed extractor runner replaced it.
3. Bot commits produced `action_required`; API-authored synchronization commits triggered authoritative workflows.
4. A naive rebase would have overwritten point corrections from #264. The branch was rebuilt from the latest `main` and only the ID 567 placeholder was replaced.
5. All temporary workflows removed themselves and are absent from the merged diff.

# Decisions

| Decision | Reason |
|---|---|
| Use exact item IDs | stable runtime identity and no name/localization ambiguity |
| Require normalized historical mastery | matches the observed condition, unlike inventory/equipment checks |
| Reuse one reconciliation surface | live awards and existing-player backfill cannot drift |
| Award through `PlayerAchievement::add` | canonical idempotence, persistence and notification behavior |
| Preserve #264 registry baseline | prevents regression of achievement point reconciliation |
| Keep status `partially-confirmed` | server/unit proof is not real-client E2E |

# Remaining work

No implementation blocker remains for ID 567. Optional future proof work is a real-client gameplay E2E covering the final mastery transition, notification, relog persistence and silent historical backfill.

# Handoff

- implementation PR: #288
- merge commit: `c9b607bdc5b9253f3eaf75b0f4a513877b8a42d7`
- completed: definition, exact condition, live award, backfill, tests, validators, reports, overlap resolution and full CI
- not completed by design: real-client E2E
- blocker: none
- next step: select another bounded unresolved achievement package from the comprehensive audit; do not reopen ID 567 unless new contradictory evidence appears

# Completion

- Final status: completed
- PR: #288
- Merge commit: `c9b607bdc5b9253f3eaf75b0f4a513877b8a42d7`
- Archived at: 2026-07-14T00:20:00+02:00
