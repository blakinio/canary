---
task_id: CAN-20260712-cyclopedia-validation
coordination_id: ""
status: active
agent: "GPT-5.6 Thinking"
branch: feat/cyclopedia-validation-audit
base_branch: main
created: 2026-07-12T19:41:00+02:00
updated: 2026-07-12T21:01:00+02:00
last_verified_commit: "741ffed81275d37fd700cacdb05cbae05a0a1356"
risk: low
related_issue: ""
related_pr: "#170"
depends_on:
  - "OTS AI World Validation methodology"
  - "Merged Achievement Validation #165 for the Achievements subdomain"
blocks: []
owned_paths:
  - tools/ai-agent/cyclopedia_validation.py
  - tools/ai-agent/test_cyclopedia_validation.py
  - .github/workflows/cyclopedia-validation.yml
  - docs/ai-agent/OTS_AI_CYCLOPEDIA_VALIDATION_PROJECT.md
  - docs/ai-agent/CYCLOPEDIA_VALIDATION_REPORT.md
  - docs/ai-agent/CYCLOPEDIA_RUNTIME_TEST_PLAN.json
  - docs/agents/tasks/active/CAN-20260712-cyclopedia-validation.md
  - docs/agents/ACTIVE_WORK.md
  - docs/agents/MODULE_CATALOG.md
modules_touched:
  - AI world validation
  - Cyclopedia static/runtime/protocol audit
public_interfaces:
  - Cyclopedia validation CLI
  - Cyclopedia JSON report schema version 1
  - Cyclopedia runtime plan schema version 1
cross_repo_tasks:
  - "Read-only maintained OTClient inventory; no OTClient mutation"
---

# Goal

Create a deterministic, evidence-based, read-only audit of Canary Cyclopedia across Items, Bestiary, Charms, Bosstiary, Map, Character/Titles and Houses.

# Acceptance criteria

- [x] Parse and validate the active Charm registry.
- [x] Parse active Bestiary/Bosstiary definitions without `data-canary` contamination.
- [x] Validate IDs, thresholds, rarity and duplicate groups.
- [x] Inventory Canary and maintained OTClient static protocol surfaces.
- [x] Create project document, evidence report and runtime plan.
- [x] Add focused tests, workflow and catalogue entries.
- [x] Keep #170 free of gameplay/protocol/DB/map/asset changes.
- [x] Align with current main and preserve merged Achievement Validation state.
- [x] Verify final full-checkout Cyclopedia workflow, repository CI and AI Agent Tools.
- [x] Review duplicate IDs `1946` and `1225` against reference/runtime semantics.
- [ ] Source authoritative replacement IDs.
- [ ] Create separate focused fix PRs.
- [ ] Execute disposable runtime/DB/packet scenarios.

# Confirmed context

- Writable repo: `blakinio/canary`; upstream repositories are read-only.
- Draft PR: `https://github.com/blakinio/canary/pull/170`.
- Verified audit code head `741ffed81275d37fd700cacdb05cbae05a0a1356` is one commit ahead of and zero behind `main` commit `ab0ca005625ca4f80fc5931d86a3f8d0b0304299`.
- Active monster roots: `data/monster`, `data-otservbr-global/monster`.
- Local shell cannot clone GitHub due DNS; connector writes and GitHub Actions are functional.
- No runtime, protocol, DB schema, monster, map, asset or OTClient behavior is changed in #170.

# Implemented work

| Path | Purpose | Status |
|---|---|---|
| `tools/ai-agent/cyclopedia_validation.py` | stdlib-only read-only scanner | verified |
| `tools/ai-agent/test_cyclopedia_validation.py` | parser/classifier/read-only tests | 9/9 verified |
| `.github/workflows/cyclopedia-validation.yml` | Canary + read-only OTClient audit | success |
| `docs/ai-agent/CYCLOPEDIA_VALIDATION_REPORT.md` | counts/evidence/dispositions | current |
| `docs/ai-agent/CYCLOPEDIA_RUNTIME_TEST_PLAN.json` | 10 disposable scenarios | created |
| `docs/ai-agent/OTS_AI_CYCLOPEDIA_VALIDATION_PROJECT.md` | methodology/changelog/handoff | current |

# Final scan evidence

Workflow run `29204136200` on code head `741ffed81275d37fd700cacdb05cbae05a0a1356` succeeded.

- 7 domains;
- 1,656 active monster Lua files;
- 749 Bestiary definitions;
- 249 Bosstiary definitions;
- 25 Charms;
- 18 scanner findings: 3 errors and 15 warnings;
- no scanned server/client declaration-definition gaps;
- artifact `8263239684`;
- JSON digest `sha256:e3fad997b2c1104e221807a596e48638a4a3992ea0f85d75d4bb72bc61b8574f`.

Repository CI run `29204136318` and AI Agent Tools run `29204136186` also succeeded on the same code head. PR mergeability was `true`.

# Confirmed findings

## Runtime/data defects — high confidence

1. `BESTIARY-DIFFICULTY-INTEGER-DIVISION`.
2. `CHARACTER-RECENT-PVP-COUNT-WINDOW-MISMATCH`.
3. Crypt Warrior has Bestiary data without a positive `raceId`.
4. Druid's Apparition and Monk's Apparition are distinct Bestiary entries sharing `raceId 1946`; kill/Charm state collides.
5. Eradicator and Rupture are distinct Bosstiary bosses sharing `bossRaceId 1225`; progress/slot state collides.

Correct replacement IDs are unknown and must not be invented.

## Display metadata defects — high confidence

Missing numeric `Bestiary.race` metadata:

- Agrestic Chicken `1979`;
- Terrified Elephant `771`;
- Haunted Dragon `1376`;
- Crypt Warrior.

## Latent helper/resilience — high confidence

- Charm category registration is guarded by `mask.type` instead of `mask.category`.
- `addBestiaryKill` dereferences `mtype` before the null guard.
- boosted-boss empty-result fallback is unreachable after an earlier return.

## Needs evidence — medium confidence

- full Charm reset formula requires current authoritative rule and 100/101/102 boundary tests.

## Likely intentional shared forms

Bestiary `213`, `227`; Bosstiary `1406`, `1811`, `1969` remain visible review warnings.

# Validation

| Code head/context | Check | Result |
|---|---|---|
| `741ffed812...` | focused tests | passed, 9/9 |
| `741ffed812...` | `py_compile` | passed |
| `741ffed812...` | Cyclopedia Validation run `29204136200` | success |
| `741ffed812...` | repository CI run `29204136318` | success |
| `741ffed812...` | AI Agent Tools run `29204136186` | success |
| `741ffed812...` | generated JSON/invariants/artifact | success |
| `741ffed812...` | compare to main | ahead 1, behind 0 |
| `741ffed812...` | PR mergeable | true |

# Work log

## 2026-07-12T21:01:00+02:00

- Rebuilt #170 directly on current main after Achievement Validation task archival.
- Preserved Achievement module status `merged` and removed its closed Active Work row.
- Verified one-commit diff, zero-behind state and mergeability.
- Cyclopedia Validation, repository CI and AI Agent Tools all passed.
- Downloaded and parsed final artifact; counts and finding classifications are unchanged.
- Updated project, evidence report, task and PR body.
- No gameplay/data/protocol/client fix was added.

## 2026-07-12T20:33:00+02:00

- Corrected optional Bestiary race classification and recent-PvP function detection.
- Expanded tests from 8 to 9.

## 2026-07-12T20:12:00+02:00

- Published scanner, tests, workflow, report, runtime plan and catalogue entry.

## 2026-07-12T19:41:00+02:00

- Created branch, dedicated project document, task and draft PR #170.

# Decisions

| Decision | Reason |
|---|---|
| #170 remains read-only | evidence and behavior fixes must be independently reviewable |
| scan active roots only | avoid alternate-datapack false positives |
| duplicate aliases remain warnings | shared forms can be intentional |
| IDs `1946`/`1225` are confirmed collisions | reference entries are distinct and runtime state is keyed by these IDs |
| missing Bestiary race is metadata defect | loader accepts it but numeric classification is affected |
| no replacement IDs guessed | authoritative client/server data is required |

# Remaining work

1. Source correct replacement IDs for `1946` and `1225`.
2. Open separate focused fix PRs for five confirmed defects.
3. Execute P0 disposable DB/runtime scenarios.
4. Packet-smoke seven domains with maintained OTClient.
5. Update persistent docs after every batch.

# Handoff

Start with the project document, this task, evidence report, runtime plan, PR #170 and workflow runs `29204136200`, `29204136318`, `29204136186`. Preserve the read-only boundary. Never write upstream, never duplicate merged #165 and never infer missing IDs or current rules.

# Completion

- Final status: active; static audit phase complete
- PR: #170 draft
- Catalogue updated: yes
- Static CI/artifact: verified
- Gameplay/runtime fixes: separate follow-up work
- Archived at:
