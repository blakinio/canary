---
task_id: CAN-20260725-rtec-004-cloud-in-a-bottle
program_id: CAN-PROGRAM-REAL-TIBIA-EVIDENCE-COLLECTION
coordination_id: RTEC-004-W1-CLOUD-IN-A-BOTTLE
status: implementing
agent: "GPT-5.6 Thinking"
branch: feat/rtec-004-cloud-in-a-bottle-20260725
base_branch: main
created: 2026-07-25T20:18:30+02:00
updated: 2026-07-25T20:55:00+02:00
last_verified_commit: "c1a36d8bbcd0b37f74c2cca9947199749cbb1294"
risk: low
related_issue: ""
related_pr: "931"
depends_on:
  - RTEC-004-WAVE-1
blocks: []
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260725-rtec-004-cloud-in-a-bottle.md
    - docs/agents/real-tibia/evidence/modules/item-definitions/**
  shared:
    - docs/agents/real-tibia/evidence/generated/EVIDENCE_INDEXES.json
  read_only:
    - docs/agents/programs/REAL_TIBIA_EVIDENCE_COLLECTION_PROGRAM.md
    - docs/agents/real-tibia/evidence/requests/**
    - docs/agents/real-tibia/registry/modules/item-definitions.yaml
    - src/items/items.*
    - src/items/functions/item/item_parse.*
    - data/items/items.xml
    - tools/e2e/**
    - tools/ai-agent/**
modules_touched:
  - item-definitions
reuses:
  - canary-real-tibia-evidence-record-v1
  - canary-real-tibia-owner-request-v1
  - canary-real-tibia-generated-indexes-v1
  - RTEC-002 vocations dossier structure
public_interfaces: []
cross_repo_tasks: []
---

# Goal

Collect one bounded evidence package for the official Cloud in a Bottle difficulty/description correction and compare it with exact current Canary item-definition and registration evidence without changing item data, assets, map, runtime, client or owner paths.

# Assignment

- Official target: 2026-07-21 fix statement that Cloud in a Bottle is available from difficulty 10 rather than 15.
- Canary baseline at task start: `124b029d1a2498a64fa6612b16efa386b8786a83`.
- Module record: `item-definitions`, inventory maturity, fast freshness class, refresh required before task.
- Canonical current paths: `src/items/items.*`, item parser paths and `data/items/items.xml`.
- Dossier root: `docs/agents/real-tibia/evidence/modules/item-definitions/`.

# Current bounded discovery

- Exact repository searches for `Cloud in a Bottle`, `cloud bottle`, `54651`, `Radiant Nimbus` and `Moonsilver` returned no indexed Canary match at the selected baseline.
- A secondary community item-ID page associates `Cloud In a Bottle` with `54651`; this remains discovery-only and is not accepted as official or Canary identity proof.
- The official 2026-07-21 fix proves only the visible correction: the description incorrectly stated difficulty 15, while availability begins at difficulty 10.
- No absolute absence claim is permitted from code-search results. Exact current definition/registration evidence must remain `UNKNOWN` until the branch is refreshed after Worker A merges and selected source files are inspected on the new baseline.

# Serialization boundary

Worker A and Worker B use separate module roots, but both require the single deterministic global evidence index. Worker B will not publish its dossier/global-index package on the stale pre-Worker-A baseline. After PR #930 merges, this branch must be advanced safely to current `main`, then the item package and combined index can be generated once.

# Boundaries

- Scope is only Cloud in a Bottle availability/description and exact definition/registration evidence.
- Do not expand into broad item catalogue, weapon proficiency, store delivery, map placement, asset import, gameplay remediation or physical E2E.
- Do not invent item IDs, appearance IDs, difficulty mechanics, description text, protocol fields or runtime authorization.
- Missing definition, registration, runtime or client evidence remains explicit `UNKNOWN` or becomes a separately coordinated owner request.

# Acceptance criteria

- [ ] Refresh this branch from current main after PR #930 merges.
- [ ] Locate the exact current Canary definition, parser/registration path and relevant tests or reports.
- [x] Pin the exact official URL/date and bounded visible correction.
- [x] Preserve secondary item-ID material as discovery-only.
- [ ] Separate documented difficulty requirement from description display, item identity, unlock authorization and runtime acquisition.
- [ ] Create only module-specific dossier files and bounded evidence records required by valid v1 contracts.
- [ ] Preserve separate official release, client build, Canary commit, maintained-client, assets/items and schema axes.
- [ ] Record what official and Canary sources prove and do not prove.
- [ ] Preserve absent/conflicting item identifiers or definitions without guessing.
- [ ] Generate the combined deterministic global index after Worker A is present in main.
- [ ] Pass focused evidence validation, ownership and exact-final-head CI gates.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-25T20:55:00+02:00
head: c1a36d8bbcd0b37f74c2cca9947199749cbb1294
branch: feat/rtec-004-cloud-in-a-bottle-20260725
pr: 931
status: implementing
context_routes:
  - agent-governance
  - real-tibia-parity
owned_paths:
  - docs/agents/tasks/active/CAN-20260725-rtec-004-cloud-in-a-bottle.md
  - docs/agents/real-tibia/evidence/modules/item-definitions/**
  - docs/agents/real-tibia/evidence/generated/EVIDENCE_INDEXES.json
proven:
  - coordinator assigned one bounded item-definitions package under RTEC-004 wave 1
  - module registry identifies item registry parser and items.xml paths
  - official 2026-07-21 fixes state that Cloud in a Bottle is available from difficulty 10 rather than 15
  - bounded Canary code searches found no indexed match for the official name secondary candidate id or related item names
  - secondary material associates candidate id 54651 but is not authority for official or Canary identity
  - Worker A and Worker B have separate module roots but serialize on one global evidence index
derived:
  - code-search misses do not prove absolute absence from current Canary
  - publishing Worker B global indexes before Worker A merges would create avoidable stale-base conflict
unknown:
  - whether Cloud in a Bottle exists under another current Canary name or identifier
  - exact current Canary item and appearance identifiers
  - whether difficulty availability belongs to item definition feature state or external content
  - strongest proof level attainable without owner runtime or client evidence
conflicts: []
first_failure:
  marker: worker-a-not-merged
  evidence: PR 930 is the first serialized global-index package and must enter main before Worker B final source/index work
rejected_hypotheses:
  - correct Canary data in this Collector task: item implementation and data paths remain read-only
  - infer item id 54651 from secondary material as authoritative: no official or Canary identity proof exists
  - treat search misses as an absence result: repository indexing and alternate naming remain unresolved
changed_paths:
  - docs/agents/tasks/active/CAN-20260725-rtec-004-cloud-in-a-bottle.md
validation:
  - command: coordinator ownership and module-registry preflight
    result: PASS
    evidence: exclusive item-definitions dossier root and bounded non-weapon item package
  - command: official 2026-07-21 source verification
    result: PASS
    evidence: visible description and difficulty correction retained without implementation inference
  - command: bounded Canary and secondary identifier discovery
    result: PASS
    evidence: no indexed Canary match; candidate id retained only as discovery lead
blockers:
  - shared global index must serialize after PR 930 merge
next_action: After PR 930 merges, advance this branch to current main without discarding the task record, then inspect exact item-definition and parser sources for alternate Cloud in a Bottle identity before creating records.
```
