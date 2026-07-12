---
task_id: CAN-20260712-cyclopedia-validation
coordination_id: ""
status: completed
agent: "GPT-5.6 Thinking"
branch: feat/cyclopedia-validation-audit
base_branch: main
created: 2026-07-12T19:41:00+02:00
updated: 2026-07-12T23:02:00+02:00
last_verified_commit: "020a42118de9f8e5e48107567bb9b899aa26b4c7"
risk: low
related_issue: ""
related_pr:
  - "#170"
  - "#188"
  - "#192"
depends_on:
  - "OTS AI World Validation methodology"
  - "Merged Achievement Validation #165 for the Achievements subdomain"
blocks: []
modules_touched:
  - AI world validation
  - Cyclopedia static/runtime/protocol audit
  - Bestiary and Bosstiary data validation
public_interfaces:
  - Cyclopedia validation CLI
  - Cyclopedia JSON report schema version 1
  - Cyclopedia runtime plan schema version 1
cross_repo_tasks:
  - "Read-only maintained OTClient inventory; no OTClient mutation"
---

# Goal

Create a deterministic Cyclopedia validation layer, classify all findings, fix every confirmed scanner defect in focused PRs and preserve durable evidence for future agents.

# Completion summary

## Merged work

| PR | Result | Merge commit |
|---:|---|---|
| #170 | read-only seven-domain Cyclopedia audit, workflow, tests, report and runtime plan | `589a2f4809d665969e9af02a0f421f14563db23f` |
| #188 | six runtime/helper corrections and four source-contract tests | `f105c8b44603d4ad640263a8971ebf2b71b06df2` |
| #192 | Bestiary/Bosstiary IDs, race metadata, exact shared-form allowlists and full-inventory tests | `fb334741327f494b635a11cb110327439bdfea8f` |

## Corrected runtime/helper defects

1. Bestiary difficulty now preserves fractional thresholds.
2. Full-Charm reset charges 11,000 gold only for levels above 100.
3. Bestiary kill attribution checks `player` and `mtype` before dereferencing.
4. Charm category registration is guarded by `mask.category`.
5. Recent-PvP pagination count uses the same 70-day window as displayed rows.
6. Missing boosted-boss rows are initialized before normal daily selection.

## Corrected data defects

1. Monk's Apparition uses Bestiary ID `2636`; Druid's Apparition remains `1946`.
2. Crypt Warrior uses Bestiary ID `1995` and `BESTY_RACE_UNDEAD`.
3. Agrestic Chicken, Terrified Elephant and Haunted Dragon have numeric Bestiary race metadata.
4. Alternate Eradicator form uses boss ID `1226`; Rupture remains `1225`.
5. Intentional shared forms are accepted only when the complete active path set exactly matches reviewed allowlists.

# Final verification

Reviewed source head before squash merge: `020a42118de9f8e5e48107567bb9b899aa26b4c7`.

| Check | Result |
|---|---|
| Cyclopedia Validation run `29208312948` | success |
| repository CI run `29208313154` | success |
| AI Agent Tools run `29208313096` | success |
| Achievement Validation run `29208312904` | success |
| review threads / change requests | none |
| branch state | mergeable, zero behind |

Final artifact:

```text
artifact id: 8264392418
archive digest: sha256:d81adab07ef4cb3b8602790075473649be4bb8017f04e8b85f79ba54a6de6881
JSON digest: sha256:79bc4054aaf5750a764c140b911f79a3bb7d61fe15b633ba5d6ddb6b64c89cc9
```

Parsed result:

```text
domains: 7
active monster files: 1656
Bestiary entries: 749
Bosstiary entries: 249
Charms: 25
maintained OTClient: scanned
findingCount: 0
findings: []
```

# Compatibility decisions

- Replacement IDs were sourced from independent datasets and existing registry occupancy; none were invented.
- Historical ambiguous counters were not copied or duplicated:
  - `1946` remains Druid's Apparition;
  - `1225` remains Rupture;
  - Eradicator forms use `1226`.
- No protocol, DB schema, map, asset or OTClient change was required.
- Scanner completion does not prove every live gameplay scenario. Disposable DB/relog/packet E2E scenarios in `CYCLOPEDIA_RUNTIME_TEST_PLAN.json` remain optional operational acceptance work.

# Durable handoff

Start with:

- `docs/ai-agent/OTS_AI_CYCLOPEDIA_VALIDATION_PROJECT.md`
- `docs/ai-agent/CYCLOPEDIA_VALIDATION_REPORT.md`
- `docs/ai-agent/CYCLOPEDIA_FIX_LOG.md`
- `docs/ai-agent/CYCLOPEDIA_RUNTIME_TEST_PLAN.json`
- merged PRs #170, #188 and #192

Do not replace exact shared-form allowlists with broad duplicate suppression. Do not migrate historical counters without a separately reviewed compatibility plan.

# Completion

- Final status: completed
- Scanner findings: 0
- Catalogue updated: yes
- Active Work row removed: yes
- Archived at: `docs/agents/tasks/archive/CAN-20260712-cyclopedia-validation.md`
