---
task_id: CAN-20260725-rtec-004-cloud-in-a-bottle
program_id: CAN-PROGRAM-REAL-TIBIA-EVIDENCE-COLLECTION
coordination_id: RTEC-004-W1-CLOUD-IN-A-BOTTLE
status: implementing
agent: "GPT-5.6 Thinking"
branch: feat/rtec-004-cloud-in-a-bottle-20260725
base_branch: main
created: 2026-07-25T20:18:30+02:00
updated: 2026-07-25T22:35:00+02:00
last_verified_commit: "9da81d1d5782486b6ee4610c1867487cd06c5c1e"
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
    - docs/agents/real-tibia/evidence/requests/tcr/RTREQ-TCR-ITEM-DEFINITIONS-0001.yaml
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

# Final bounded result

- Official correction: Cloud in a Bottle is available from difficulty `10`, not `15`; record `RT-ITEM-DEFINITIONS-0001` is `PROVEN` at `definition-found`.
- Current Canary loader boundary and exact selected-path scan: record `RT-ITEM-DEFINITIONS-0002` is `PROVEN` at `definition-found`.
- Exact selected textual paths contain no official-name variant or exact candidate ID `54651` entry.
- The miss is not promoted to item absence because `Items::loadFromProtobuf()` loads base ID, name and description from `appearances.dat` before XML overlays.
- Candidate ID `54651` remains discovery-only.
- Exact official-client identity and correspondence with the pinned Canary appearances revision remain `blocked-by-reference`.
- `RTREQ-TCR-ITEM-DEFINITIONS-0001` is ready for owner triage under the existing `CAN-PROGRAM-OTBM-TIBIA-CLIENT-REFERENCE` programme.

# Evidence and provenance

- Refreshed Canary baseline after Worker A merge: `8ef88972fd1c473b9f3c0a5cfb9bed98c78bdbc9`.
- Selected appearances blob: `2cc2f4910af4f002f99f39e486d1a91b1b56a728`.
- Exact bounded scan: GitHub Actions run `30171827237`, artifact `8623126188`.
- Scan artifact SHA-256: `2ea96bb5feeaec8022ba5bbedb4a74c1fdd3af0019ba1473f3610d0a5541d637`.
- Validated package export: run `30173389633`, artifact `8623535515`.
- The canonical generator and corpus validator passed in the export workspace before exact bytes were integrated and the exporter removed.

# Loader boundary

- `Items::loadFromProtobuf()` assigns client-derived item IDs, names and descriptions and registers lower-case names.
- `Items::loadFromXml()` and `Items::parseItemNode()` process XML IDs, names and attributes.
- `ItemParse::parseDescription()` may overlay an XML description.
- Therefore selected XML and source-search misses cannot resolve the proprietary appearances object or establish absence.

# Boundaries

- Scope is only Cloud in a Bottle identity, the visible difficulty/description correction and selected item-registration evidence.
- No item data, assets, parser, runtime, client, map or E2E owner path was modified.
- No item ID, appearance ID, difficulty mechanic, protocol field, authorization or runtime behavior was invented.
- The owner request does not import or commit proprietary client payloads.

# Acceptance criteria

- [x] Refresh the branch after Worker A merge without discarding the task record.
- [x] Pin the exact official URL/date and bounded visible correction.
- [x] Preserve candidate ID `54651` as discovery-only.
- [x] Run an exact selected-path scan and retain its diagnostics artifact.
- [x] Trace protobuf/XML/name/description loader boundaries.
- [x] Separate documented difficulty requirement from description display, item identity, unlock authorization and runtime acquisition.
- [x] Create the module dossier, behavior model, decisions, bounded records and version history.
- [x] Create one non-duplicative TCR owner request for exact client-reference identity.
- [x] Generate and verify the combined deterministic module/global indexes in the validated export workspace.
- [x] Complete structured review while preserving blocked and unknown boundaries.
- [x] Remove all temporary scan/export tooling.
- [ ] Pass exact-final-head repository checks and merge PR #931.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-25T22:35:00+02:00
head: 9da81d1d5782486b6ee4610c1867487cd06c5c1e
branch: feat/rtec-004-cloud-in-a-bottle-20260725
pr: 931
status: implementing
context_routes:
  - agent-governance
  - real-tibia-parity
owned_paths:
  - docs/agents/tasks/active/CAN-20260725-rtec-004-cloud-in-a-bottle.md
  - docs/agents/real-tibia/evidence/modules/item-definitions/**
  - docs/agents/real-tibia/evidence/requests/tcr/RTREQ-TCR-ITEM-DEFINITIONS-0001.yaml
  - docs/agents/real-tibia/evidence/generated/EVIDENCE_INDEXES.json
proven:
  - Worker A PR 930 merged and Worker B was refreshed from main 8ef88972fd1c473b9f3c0a5cfb9bed98c78bdbc9
  - official 2026-07-21 correction states difficulty 10 rather than 15
  - exact selected-path scan run 30171827237 artifact 8623126188 found no bounded identity or candidate id 54651 match
  - scan misses do not establish absolute absence
  - current Canary item names and descriptions may originate from appearances.dat through Items::loadFromProtobuf
  - two evidence records and their structured review are accepted
  - deterministic module and global indexes were generated and validated in run 30173389633
  - RTREQ-TCR-ITEM-DEFINITIONS-0001 is ready for TCR owner triage
  - all temporary diagnostic and export tests are removed
derived:
  - current item correspondence is blocked by exact client-reference identity rather than proven absent
  - candidate id 54651 cannot be promoted across identifier namespaces without accepted TCR evidence
  - one bounded TCR request is the narrowest safe continuation because no new parser or capability is required
unknown:
  - exact official client build object id name and description for Cloud in a Bottle
  - exact matching or conflicting Canary appearances identity
  - unlock authorization acquisition runtime and maintained-client behavior
conflicts: []
first_failure:
  marker: exact-client-reference-missing
  evidence: textual definitions cannot resolve identity because base names and descriptions may originate from proprietary appearances.dat
rejected_hypotheses:
  - infer candidate id 54651 from secondary material
  - treat selected textual misses as item absence
  - mutate item data or proprietary assets in the Collector task
changed_paths:
  - docs/agents/tasks/active/CAN-20260725-rtec-004-cloud-in-a-bottle.md
  - docs/agents/real-tibia/evidence/modules/item-definitions/**
  - docs/agents/real-tibia/evidence/requests/tcr/RTREQ-TCR-ITEM-DEFINITIONS-0001.yaml
  - docs/agents/real-tibia/evidence/generated/EVIDENCE_INDEXES.json
validation:
  - command: bounded selected-path item scan
    result: PASS
    evidence: run 30171827237 artifact 8623126188
  - command: canonical generator and corpus validator in clean export workspace
    result: PASS
    evidence: run 30173389633 artifact 8623535515; 45 canonical tests passed before intentional export stop
  - command: structured evidence review
    result: PASS
    evidence: docs/agents/real-tibia/evidence/modules/item-definitions/reviews/RTEC-004-W1-CLOUD-REVIEW.md
blockers:
  - exact final head checks are pending
next_action: Pass all exact-final-head checks, transition PR 931 to ready, and merge without further content changes.
```
