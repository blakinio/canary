---
task_id: CAN-20260725-rtec-004-cloud-in-a-bottle
program_id: CAN-PROGRAM-REAL-TIBIA-EVIDENCE-COLLECTION
coordination_id: RTEC-004-W1-CLOUD-IN-A-BOTTLE
status: implementing
agent: "GPT-5.6 Thinking"
branch: feat/rtec-004-cloud-in-a-bottle-20260725
base_branch: main
created: 2026-07-25T20:18:30+02:00
updated: 2026-07-25T21:38:00+02:00
last_verified_commit: "6b80b3f835515667a5a807c499a56aca24c11e65"
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
    - docs/agents/real-tibia/evidence/requests/tcr/RTREQ-TCR-CLOUD-IN-A-BOTTLE-0001.yaml
  shared:
    - docs/agents/real-tibia/evidence/generated/EVIDENCE_INDEXES.json
  read_only:
    - docs/agents/programs/REAL_TIBIA_EVIDENCE_COLLECTION_PROGRAM.md
    - docs/agents/real-tibia/evidence/requests/feature/RTREQ-FEATURE-VOCATIONS-0001.yaml
    - docs/agents/real-tibia/registry/modules/item-definitions.yaml
    - docs/agents/programs/OTBM_TIBIA_CLIENT_REFERENCE_PROGRAM.md
    - docs/ai-agent/OTBM_TIBIA_CLIENT_REFERENCE_ARCHITECTURE.md
    - src/items/items.*
    - src/items/functions/item/item_parse.*
    - data/items/items.xml
    - data/items/appearances.dat
    - tools/ai-agent/**
    - tools/e2e/**
modules_touched:
  - item-definitions
reuses:
  - canary-real-tibia-evidence-record-v1
  - canary-real-tibia-owner-request-v1
  - canary-real-tibia-generated-indexes-v1
  - CAN-PROGRAM-OTBM-TIBIA-CLIENT-REFERENCE
  - RTEC-002 vocations dossier structure
public_interfaces: []
cross_repo_tasks: []
---

# Goal

Collect one bounded evidence package for the official Cloud in a Bottle difficulty/description correction and compare it with exact current Canary item-definition and registration evidence without changing item data, assets, map, runtime, client or owner paths.

# Current baselines

- Initial Canary baseline: `124b029d1a2498a64fa6612b16efa386b8786a83`.
- Refreshed Worker B baseline after Worker A merge: `8ef88972fd1c473b9f3c0a5cfb9bed98c78bdbc9`.
- Worker A PR #930 is merged; the shared deterministic evidence index is no longer blocked by Worker A.
- Official target: 2026-07-21 fix statement that Cloud in a Bottle is available from difficulty 10 rather than 15.

# Proven bounded discovery

- Canonical scan run `30171827237`, diagnostics artifact `8623126188`, executed against merge workspace `9236b5adfa5c40f170901d79d897f8b6694f4ba6` composed from Worker B and `main@8ef88972fd1c473b9f3c0a5cfb9bed98c78bdbc9`.
- Exact selected-path searches found no `Cloud in a Bottle`, bounded spelling variant, `Radiant Nimbus`, `Moonsilver` or candidate ID `54651` in:
  - `data/items/items.xml`;
  - `src/items/items.cpp`;
  - `src/items/items.hpp`;
  - `src/items/functions/item/item_parse.cpp`;
  - `src/items/functions/item/item_parse.hpp`.
- `data/items/items.xml` contains no exact `id="54651"` entry. Other names containing `cloud` or `bottle` are unrelated and do not resolve the official item.
- Repository grep matches are limited to the Collector task/discovery diagnostics and achievement-audit references; no selected item-definition match was found.
- Search misses are not absolute absence proof.

# Loader boundary

- `Items::loadFromProtobuf()` loads item IDs, names and descriptions from the selected `appearances.dat` package and registers lower-case names.
- `Items::loadFromXml()` and `Items::parseItemNode()` overlay XML IDs, names and parsed attributes; `ItemParse::parseDescription()` overlays XML description attributes.
- Therefore an XML/search miss cannot establish that the official item is absent, renamed or assigned candidate ID `54651` in the exact client-derived appearances registry.
- `data/items/appearances.dat` is proprietary/binary reference material and remains read-only. The Collector will not parse it or infer identifiers.

# Owner request decision

Create one TCR client-reference request, `RTREQ-TCR-CLOUD-IN-A-BOTTLE-0001`, for the existing `CAN-PROGRAM-OTBM-TIBIA-CLIENT-REFERENCE` owner. It must identify the exact official-client object/name/description/build and compare that evidence with the exact Canary appearances revision without importing or mutating assets. No duplicate request was found.

# Boundaries

- Scope is only Cloud in a Bottle identity, visible difficulty/description correction and selected item registration evidence.
- Do not expand into broad item catalogue, weapon proficiency, store delivery, map placement, asset import, gameplay remediation or physical E2E.
- Do not invent item IDs, appearance IDs, difficulty mechanics, description text, protocol fields or runtime authorization.
- Missing definition, registration, runtime or client evidence remains explicit `UNKNOWN` or `blocked-by-owner-request`.

# Acceptance criteria

- [x] Refresh the branch after Worker A merge without discarding the task record.
- [x] Pin the exact official URL/date and bounded visible correction.
- [x] Preserve secondary candidate ID `54651` as discovery-only.
- [x] Run an exact selected-path scan and retain its diagnostics artifact.
- [x] Trace protobuf/XML/name/description loader boundaries.
- [x] Separate documented difficulty requirement from description display, item identity, unlock authorization and runtime acquisition.
- [ ] Create the module dossier, bounded evidence records and version history.
- [ ] Create one non-duplicative TCR owner request for exact client-reference identity.
- [ ] Generate and verify the combined deterministic global index.
- [ ] Complete structured review while preserving `UNKNOWN` boundaries.
- [ ] Remove temporary scan tooling and pass exact-final-head CI gates.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-25T21:38:00+02:00
head: 6b80b3f835515667a5a807c499a56aca24c11e65
branch: feat/rtec-004-cloud-in-a-bottle-20260725
pr: 931
status: implementing
context_routes:
  - agent-governance
  - real-tibia-parity
owned_paths:
  - docs/agents/tasks/active/CAN-20260725-rtec-004-cloud-in-a-bottle.md
  - docs/agents/real-tibia/evidence/modules/item-definitions/**
  - docs/agents/real-tibia/evidence/requests/tcr/RTREQ-TCR-CLOUD-IN-A-BOTTLE-0001.yaml
  - docs/agents/real-tibia/evidence/generated/EVIDENCE_INDEXES.json
proven:
  - Worker A PR 930 merged and Worker B refreshed from main 8ef88972fd1c473b9f3c0a5cfb9bed98c78bdbc9
  - official 2026-07-21 fix states Cloud in a Bottle is available from difficulty 10 rather than 15
  - exact selected-path scan run 30171827237 artifact 8623126188 found no official name variants or candidate id 54651 in canonical textual item-definition paths
  - scan misses do not establish absolute absence
  - current Canary item names and descriptions may originate from appearances.dat through Items::loadFromProtobuf
  - XML overlays names and descriptions but cannot resolve a missing client-derived identity alone
  - no duplicate Cloud in a Bottle owner request was found
  - CAN-PROGRAM-OTBM-TIBIA-CLIENT-REFERENCE owns exact user-supplied client reference evidence
derived:
  - the current comparison is blocked by exact client-reference identity rather than proven item absence
  - candidate id 54651 cannot be promoted without TCR evidence
  - one TCR request is the narrowest safe route
unknown:
  - exact official client build object id name and description for Cloud in a Bottle
  - exact matching Canary appearances identity and revision
  - unlock authorization acquisition runtime and maintained-client behavior
conflicts: []
first_failure:
  marker: exact-client-reference-missing
  evidence: selected textual definitions do not resolve the item while names and descriptions may be loaded from proprietary appearances.dat
rejected_hypotheses:
  - correct Canary data in this Collector task: item implementation and data paths remain read-only
  - infer item id 54651 from secondary material: no official or Canary identity proof exists
  - treat selected search misses as absence: protobuf appearances may supply the identity
changed_paths:
  - docs/agents/tasks/active/CAN-20260725-rtec-004-cloud-in-a-bottle.md
  - docs/agents/real-tibia/evidence/modules/item-definitions/DISCOVERY.md
  - tools/agents/test_real_tibia_rtec_004_cloud_scan.py
validation:
  - command: safe Worker B merge refresh from main
    result: PASS
    evidence: merge commit 8bf62092d6d8bc0221e765f9efa7faa829f117c8 without force update
  - command: bounded selected-path item scan
    result: PASS
    evidence: run 30171827237 artifact 8623126188; no bounded identity or candidate-id match
  - command: current Canary item loader trace at 8ef88972fd1c473b9f3c0a5cfb9bed98c78bdbc9
    result: PASS
    evidence: Items::loadFromProtobuf loadFromXml parseItemNode getItemIdByName and ItemParse::parseDescription
blockers:
  - exact official client reference identity requires TCR owner evidence
next_action: Create the two bounded item-definition records, the TCR owner request, module indexes and version history without promoting candidate ID 54651.
```
