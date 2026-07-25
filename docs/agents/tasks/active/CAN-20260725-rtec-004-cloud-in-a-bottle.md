---
task_id: CAN-20260725-rtec-004-cloud-in-a-bottle
program_id: CAN-PROGRAM-REAL-TIBIA-EVIDENCE-COLLECTION
coordination_id: RTEC-004-W1-CLOUD-IN-A-BOTTLE
status: implementing
agent: "GPT-5.6 Thinking"
branch: feat/rtec-004-cloud-in-a-bottle-20260725
base_branch: main
created: 2026-07-25T20:18:30+02:00
updated: 2026-07-25T20:18:30+02:00
last_verified_commit: "124b029d1a2498a64fa6612b16efa386b8786a83"
risk: low
related_issue: ""
related_pr: ""
depends_on:
  - RTEC-004-WAVE-1
blocks: []
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260725-rtec-004-cloud-in-a-bottle.md
    - docs/agents/real-tibia/evidence/modules/item-definitions/**
  shared: []
  read_only:
    - docs/agents/programs/REAL_TIBIA_EVIDENCE_COLLECTION_PROGRAM.md
    - docs/agents/real-tibia/evidence/generated/**
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

# Boundaries

- Scope is only Cloud in a Bottle availability/description and exact definition/registration evidence.
- Do not expand into broad item catalogue, weapon proficiency, store delivery, map placement, asset import, gameplay remediation or physical E2E.
- Do not invent item IDs, appearance IDs, difficulty mechanics, description text, protocol fields or runtime authorization.
- Missing definition, registration, runtime or client evidence remains explicit `UNKNOWN` or becomes a separately coordinated owner request.

# Acceptance criteria

- [ ] Locate the exact current Canary definition, parser/registration path and any relevant tests or reports.
- [ ] Pin the exact official URL/date and selected statement.
- [ ] Separate the documented difficulty requirement from description display, item identity, unlock authorization and runtime acquisition.
- [ ] Create only the module-specific dossier files and bounded evidence records required by valid v1 contracts.
- [ ] Preserve separate official release, client build, Canary commit, maintained-client, assets/items and schema axes.
- [ ] Record what official and Canary sources prove and do not prove.
- [ ] Preserve absent/conflicting item identifiers or definitions without guessing.
- [ ] Pass focused evidence validation, deterministic-index check and ownership/CI gates on the final head.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-25T20:18:30+02:00
head: 124b029d1a2498a64fa6612b16efa386b8786a83
branch: feat/rtec-004-cloud-in-a-bottle-20260725
pr: none
status: implementing
context_routes:
  - agent-governance
  - real-tibia-parity
owned_paths:
  - docs/agents/tasks/active/CAN-20260725-rtec-004-cloud-in-a-bottle.md
  - docs/agents/real-tibia/evidence/modules/item-definitions/**
proven:
  - coordinator assigned one bounded item-definitions package under RTEC-004 wave 1
  - module registry identifies item registry parser and items.xml paths
  - official 2026-07-21 fixes state that Cloud in a Bottle is available from difficulty 10 rather than 15
  - the package is independent from the weapon-proficiency worker and active OTBM and E2E PRs
unknown:
  - whether Cloud in a Bottle exists in current Canary definitions
  - exact current Canary item and appearance identifiers
  - whether difficulty availability belongs to item definition feature state or external content
  - strongest proof level attainable without owner runtime or client evidence
conflicts: []
first_failure:
  marker: dossier-not-started
  evidence: branch and task exist but no module evidence files have been created
rejected_hypotheses:
  - correct Canary data in this Collector task: item implementation and data paths remain read-only
  - infer item IDs or runtime unlock logic from the official fix text: the statement proves only the documented visible correction
changed_paths:
  - docs/agents/tasks/active/CAN-20260725-rtec-004-cloud-in-a-bottle.md
validation:
  - command: coordinator ownership and module-registry preflight
    result: PASS
    evidence: exclusive item-definitions dossier root and bounded non-weapon item package
blockers: []
next_action: Search the exact current Canary item definitions parser paths tests and reports for Cloud in a Bottle before creating any evidence record.
```
