---
task_id: CAN-20260713-achievements-validation
program_id: ""
coordination_id: ""
status: ready-for-review
agent: "GPT-5.6 Thinking"
branch: feat/achievements-comprehensive-validation
base_branch: main
created: 2026-07-13T08:00:00Z
updated: 2026-07-13T13:10:00+02:00
last_verified_commit: "87060be37c7412752ea7936fc8303a73aa112a25"
risk: medium
related_issue: ""
related_pr: "#238"
depends_on:
  - "merged achievement audit PR #165"
  - "merged achievement helper repair PR #176"
  - "merged static trigger repair PR #184"
  - "merged Weapon Proficiency audit/fix PRs #195 and #212"
blocks:
  - "evidence-backed achievement metadata repair PRs"
  - "evidence-backed achievement definition/handler PRs"
  - "existing-player backfill and runtime/E2E work packages"
owned_paths:
  exclusive:
    - .github/workflows/achievement-validation.yml
    - tools/ai-agent/achievement_validation.py
    - tools/ai-agent/test_achievement_validation.py
    - docs/ai-agent/ACHIEVEMENT_REFERENCE_BASELINE.json
    - docs/ai-agent/ACHIEVEMENT_REFERENCE_CATALOG.json
    - docs/ai-agent/ACHIEVEMENT_REVIEWED_EVIDENCE.json
    - docs/ai-agent/ACHIEVEMENT_COMPREHENSIVE_VALIDATION.md
    - docs/ai-agent/ACHIEVEMENT_RUNTIME_TEST_PLAN.json
    - docs/agents/tasks/active/CAN-20260713-achievements-validation.md
  shared:
    - docs/ai-agent/OTS_AI_ACHIEVEMENT_VALIDATION_PROJECT.md
    - docs/ai-agent/ACHIEVEMENT_VALIDATION_REPORT.md
    - docs/agents/MODULE_CATALOG.md
  read_only:
    - data/scripts/lib/register_achievements.lua
    - data/**/*.lua
    - data-otservbr-global/**/*.lua
    - src/creatures/players/components/player_achievement.*
    - src/game/game.cpp
    - src/lua/functions/core/game/game_functions.cpp
modules_touched:
  - achievement validation audit
  - AI world validation evidence model
reuses:
  - canary-achievement-audit-v1 from PR #165
  - Achievement Validation workflow and focused tests
  - Quest Map Validator conservative evidence semantics from PR #225
  - Weapon Proficiency reviewed evidence from PR #195
public_interfaces:
  - canary-achievement-audit-v2
  - canary-achievement-reference-catalog-v1
  - canary-achievement-reviewed-evidence-v1
cross_repo_tasks: []
---

# Goal and exact scope

Create a comprehensive, evidence-based validation of every current TibiaWiki/Fandom achievement without changing gameplay. For every row, keep definition, source condition, active handler, persistence/backfill, current/new-player attainability, runtime registration and tests as separate proof layers.

Allowed final classifications:

```text
confirmed
partially-confirmed
definition-only
handler-missing
unresolved
conflicting
intentionally-unsupported
```

`unresolved` is an accepted completed-audit result when dynamic Lua, indirect C++, semantic reachability, persistence/backfill or runtime/E2E evidence is insufficient.

# Acceptance criteria

- [x] Mandatory repository/agent docs and relevant `docs/ai-agent/**` read.
- [x] Existing validator/reports/tasks/PRs inspected before implementation.
- [x] Dedicated branch, task and draft PR opened early.
- [x] Canonical validator extended; no duplicate parser/scanner.
- [x] `docs/agents/ACTIVE_WORK.md` not edited.
- [x] External page ID, revision, date, bytes and SHA-256 recorded.
- [x] Factual catalogue covers all 564 listed/discovered rows.
- [x] Raw source payload and long descriptions/spoilers excluded from Git.
- [x] Every reference row joined to Canary definition or marked absent/conflicting.
- [x] Exact registry path/line evidence retained.
- [x] Both active datapacks scanned for achievement APIs.
- [x] Exact static API path/line evidence retained.
- [x] Unknown static achievement references equal zero.
- [x] Dynamic/indirect paths remain unresolved without reviewed proof.
- [x] Persistence/backfill, attainability, registration and tests are separate per row.
- [x] All seven status values validated.
- [x] Weapon Proficiency IDs 564–567 reuse reviewed evidence.
- [x] Thirteen focused tests and bytecode compilation pass.
- [x] All committed JSON validates.
- [x] Dedicated workflow publishes JSON/Markdown artifact.
- [x] Complete Markdown table, project/report docs, runtime plan and module catalogue updated.
- [x] Exact PR diff contains only 12 intended validation/tooling/documentation files.
- [x] Temporary source/materializer/chunk files removed.
- [x] Related open PRs rechecked after implementation.
- [x] Full CI, dedicated audit, AI Agent Tools, ownership and autofix passed on `87060be37c7412752ea7936fc8303a73aa112a25`.
- [x] Review threads and submitted reviews were empty before final gate recording.
- [x] Gameplay, metadata repairs, definitions, handlers, backfill and E2E remain separate follow-ups.

# Sources and provenance

| Source | Date | Purpose | Boundary |
|---|---|---|---|
| mandatory `AGENTS.md` / `docs/agents/**` | 2026-07-13 | safety, ownership, lifecycle, test matrix | repository policy |
| relevant `docs/ai-agent/**` | 2026-07-13 | validation methodology and reuse | static evidence is not runtime proof |
| registry, both datapacks and PlayerAchievement C++ | 2026-07-13 | engine evidence | read-only |
| TibiaWiki/Fandom `Achievements` | 2026-07-13 | external comparison | not gameplay authority |
| MediaWiki parse API revision `1188274` | 2026-07-13 | deterministic full table | raw payload not committed |
| live GitHub PR/task state | 2026-07-13 | overlap and readiness review | current repository state |

```text
page: https://tibia.fandom.com/wiki/Achievements
retrieval: https://tibia.fandom.com/api.php?action=parse&page=Achievements&prop=text%7Crevid&format=json&formatversion=2
page ID: 49280
revision ID: 1188274
source bytes: 1,026,270
source SHA-256: 8a429425ab7b088758646b07f036afdd1d579188d056491aed8e77650306ae8b
```

# Confirmed findings

## Reference baseline

```text
listed/discovered: 564
total including undiscovered secret: 565
common: 363
secret discovered/total: 201/202
known theoretical points: 1475
maximum excluding coinciding: 1430
unknown point rows: 5
conditions available/unavailable: 558/6
ID range/gaps: 1..595 / 31
```

## Canary baseline and scan

```text
definitions: 541
public/secret: 350/191
points: 1428
ID range/gaps: 1..570 / 29
active API references: 182
resolved static references: 160
unknown static references: 0
dynamic references: 22
admin references: 2
direct-static-award definitions: 89
static-progress-path definitions: 32
referenced-without-static-award definitions: 1
no-direct-static-reference definitions: 419
```

## Status counts

```text
confirmed: 0
partially-confirmed: 121
definition-only: 0
handler-missing: 3
unresolved: 409
conflicting: 31
intentionally-unsupported: 0
```

No row is `confirmed` because the static audit does not jointly prove condition reachability, persistence/backfill and runtime/E2E.

## Missing definitions

```text
195 Smart Thinking
550 A Friend in Need
551 Holzkopf
567 The Forbidden Build
572 Errand Runner
573 Workhorse
574 Taskaholic
575 Pest Control
576 Mimic
577 Bastard
578 Razor's Edge
579 Lost Letters
580 Stagmeister
581 Feral Trapper
582 Castle Crasher
585 A reliable Friend
586 Echo Initiate
587 Echo Hunter
588 Echo Walker
591 Purrfectly Addicted
592 Six Steps Ahead
593 Radiant Nimbus
594 Amati's Echo
595 Enlightened, Indeed
```

A missing definition does not prove active content or safe implementability.

## Metadata conflicts

```text
406 The More the Merrier: reference grade 0, Canary grade 1
513 Soul Mender: reference secret true, Canary false
526 King's Council: reference points 2, Canary 0
555 Inner Peace: reference points 3, Canary 2
556 Fiend Rider: reference points 3, Canary 2
559 Hope of the Merudri: reference points 2, Canary 3
562 Alpha Rider: reference points 3, Canary 2
```

No metadata was changed.

## Incomplete source cells

- unknown points: `574`, `587`, `588`, `591`, `595`;
- unavailable conditions: `195`, `561`, `574`, `587`, `588`, `595`.

No value was inferred.

## Persistence and Weapon Proficiency

```text
src/creatures/players/components/player_achievement.cpp:35  save by canonical name
src/creatures/players/components/player_achievement.cpp:103 load stored name
src/creatures/players/components/player_achievement.cpp:87  points persistence
```

Renames require migration/aliases. IDs 564–566 are `handler-missing`; ID 567 is `conflicting`; #212 fixed mastery state/count only.

# Uncertain findings requiring future proof

- semantic reachability of 121 static candidates;
- deterministic resolution of 22 dynamic references and other wrappers/state machines;
- existing-player backfill for nearly all rows;
- runtime registration/reload equality and denied-path behavior;
- event-only, mutually exclusive, retired or intentionally unsupported conditions;
- current/new-player attainability for 409 unresolved rows;
- supported-version interpretation of seven metadata conflicts;
- content readiness for 24 missing definitions.

# Source/engine conflicts

| Area | Source | Canary | Disposition |
|---|---|---|---|
| catalogue | 564 listed / 565 total | 541 definitions | conflicting; 24 missing |
| metadata | revision `1188274` | seven differences | conflicting |
| 564–566 | mastery thresholds | definitions, no reviewed award hook | handler-missing |
| 567 | secret twelve-item condition | data contract proven, definition/award/backfill absent | conflicting |
| blank source cells | five points, six conditions | no safe comparison | unresolved |

# Related open PR review

Repeated searches used `achievement`, `achievement_validation.py`, `register_achievements.lua`, `player_achievement.cpp` and `weapon proficiency`.

| PR | Relationship | Verified result | Action |
|---|---|---|---|
| #234 multichannel runtime | initially looked like shared catalogue overlap | direct comparison to current `main` shows 12 multichannel-only paths and no achievement/catalogue change | no repair required |
| #243 Cyclopedia validation gate | same validation discipline | Cyclopedia-only paths; no overlap | no repair required |
| #245 universal E2E platform | possible future runtime infrastructure | draft, feature-neutral, no owned-path overlap | optional future dependency only |
| #224 paused Cyclopedia E2E | historical experiment | unrelated and paused | no action |

No other open PR modifies `achievement_validation.py`, `register_achievements.lua` or `player_achievement.cpp`. No related PR needed a code repair. Stale PR/task metadata after `main` refreshes was corrected in #238.

# Changed files

Exactly 12 intended files:

```text
.github/workflows/achievement-validation.yml
docs/agents/MODULE_CATALOG.md
docs/agents/tasks/active/CAN-20260713-achievements-validation.md
docs/ai-agent/ACHIEVEMENT_COMPREHENSIVE_VALIDATION.md
docs/ai-agent/ACHIEVEMENT_REFERENCE_BASELINE.json
docs/ai-agent/ACHIEVEMENT_REFERENCE_CATALOG.json
docs/ai-agent/ACHIEVEMENT_REVIEWED_EVIDENCE.json
docs/ai-agent/ACHIEVEMENT_RUNTIME_TEST_PLAN.json
docs/ai-agent/ACHIEVEMENT_VALIDATION_REPORT.md
docs/ai-agent/OTS_AI_ACHIEVEMENT_VALIDATION_PROJECT.md
tools/ai-agent/achievement_validation.py
tools/ai-agent/test_achievement_validation.py
```

No gameplay, registry, KV schema, DB, map, asset or production configuration file changed.

# Commands and tests

```text
python -m unittest discover -s tools/ai-agent -p "test_achievement_validation.py" -v
python -m py_compile tools/ai-agent/achievement_validation.py tools/ai-agent/test_achievement_validation.py
python -m json.tool docs/ai-agent/ACHIEVEMENT_REFERENCE_BASELINE.json
python -m json.tool docs/ai-agent/ACHIEVEMENT_REFERENCE_CATALOG.json
python -m json.tool docs/ai-agent/ACHIEVEMENT_REVIEWED_EVIDENCE.json
python -m json.tool docs/ai-agent/ACHIEVEMENT_RUNTIME_TEST_PLAN.json
python tools/ai-agent/achievement_validation.py --repository-root . --reference-baseline docs/ai-agent/ACHIEVEMENT_REFERENCE_BASELINE.json --reference-catalog docs/ai-agent/ACHIEVEMENT_REFERENCE_CATALOG.json --reviewed-evidence docs/ai-agent/ACHIEVEMENT_REVIEWED_EVIDENCE.json --output artifacts/ACHIEVEMENT_AUDIT.json --markdown artifacts/ACHIEVEMENT_AUDIT.md --allow-findings
git diff --check
git diff --cached --check
```

# Final validated CI evidence

```text
commit: 87060be37c7412752ea7936fc8303a73aa112a25
Achievement Validation: 29244592265 — success
artifact: 8276808405
artifact digest: sha256:728052e75a04554a669a3951030d96e215e7c76a92c0091614f7cc97cf27214a
AI Agent Tools: 29244592260 — success
Agent Task Ownership: 29244592288 — success
autofix.ci: 29244592245 — success
CI: 29244592415 — success
CI Fast Checks: success
CI Lua Tests: success
CI Linux release compile: success
CI Required: success
Windows/macOS/Docker/runtime smoke: skipped by changed-path scope, not claimed as passed
review threads before record commit: 0
reviews before record commit: 0
```

# Failed approaches

1. Task creation before branch creation returned 404; no write occurred.
2. Direct-main task write returned 409; branch protection prevented mutation.
3. Direct rendered Fandom fetch returned HTTP 403; MediaWiki parse API fallback succeeded.
4. First document generator had a malformed f-string.
5. First dynamic import omitted `sys.modules` registration and caused a Python 3.13 dataclass error.
6. First test snapshot lacked exact repository paths; exact inputs were supplied without weakening tests.
7. Two materializer runs passed validation but failed Git transport.
8. Trailing whitespace blocked `git diff --cached --check`; deterministic normalization fixed it.
9. Temporary fetch/materializer/chunk files were removed.
10. Branch was refreshed on current `main`; unrelated main commits are not in PR diff.
11. A stale changed-file signal for #234 was checked against current `main`; no real overlap existed, so no false repair was applied.

# Design decisions

| Decision | Reason |
|---|---|
| extend canonical validator | avoid duplicate parsers/scanners and preserve v1 consumers |
| version enriched output as v2 | additive evidence model |
| store facts/hashes, not prose | reproducibility and source boundary |
| use explicit revision/hash | stale/blocked rendered source |
| separate every proof layer | prevent definition-only false positives |
| reviewed evidence required for stronger overrides | auditable subsystem claims |
| no handler inference from text absence | dynamic Lua/C++ may exist |
| `confirmed=0` without E2E | static evidence cannot prove full behavior |
| gameplay fixes remain separate | different risks and tests |
| do not modify related PRs without real overlap | preserve independent work |

# Remaining follow-up work

Audit scope is complete. Separate future tasks/PRs must:

1. review seven metadata conflicts against the supported version;
2. prove content readiness for 24 missing definitions;
3. add bounded dynamic resolvers;
4. validate handlers semantically by subsystem;
5. design existing-player backfill;
6. add runtime/E2E and denied-path tests, optionally using #245 after it independently merges;
7. implement only evidence-backed changes in focused PRs.

# Handoff

- branch: `feat/achievements-comprehensive-validation`
- PR: `#238`
- last fully validated commit: `87060be37c7412752ea7936fc8303a73aa112a25`
- this CI-record update is documentation-only and must receive normal final PR checks before merge
- source revision/hash: `1188274` / `8a429425ab7b088758646b07f036afdd1d579188d056491aed8e77650306ae8b`

Completed: all audit tooling, catalogue, 564-row evidence table, classifications, tests, docs, related-PR review and full required CI.

Not completed by design: gameplay changes, metadata corrections, new definitions, handlers, historical backfill and per-achievement physical-client E2E.

Current blocker: none in the audit content; only normal final checks on this documentation-only record commit.

First next step: after final checks, recheck exact diff/reviews and squash-merge #238. Then archive this task in a bounded cleanup PR. The safest gameplay follow-up is a metadata-only review of the seven conflicts.

# Completion

- Final status: ready-for-review
- PR: #238
- Merge commit:
- Program record updated: not applicable
- Catalogue updated: yes
- Changelog updated: not required for read-only validation tooling/docs
- Archived at:
