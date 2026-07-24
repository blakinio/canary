---
task_id: CAN-20260724-tcr-004-proficiency-reference-index
program_id: CAN-PROGRAM-OTBM-TIBIA-CLIENT-REFERENCE
coordination_id: OTBM-TIBIA-CLIENT-REFERENCE
status: completed
agent: "GPT-5.6 Thinking"
branch: feat/tcr-004-proficiency-reference-index
base_branch: main
created: 2026-07-24T09:15:00+02:00
updated: 2026-07-24T10:08:00+02:00
last_verified_commit: "ce2c6e611f98f82c4f84e948372da0e1d324761f"
risk: medium
related_issue: ""
related_pr: 858
depends_on:
  - TCR-001 merged stable canary-tibia-client-reference-manifest-v1
  - TCR-003 merged stable canary-tibia-staticmapdata-index-v1
blocks: []
owned_paths:
  exclusive: []
  shared: []
  read_only: []
modules_touched:
  - OTBM Tibia client reference architecture
  - official-client proficiency reference evidence
reuses:
  - canary-tibia-client-reference-manifest-v1 exact provenance contract
  - TCR-003 stable-file, bounded-compression and deterministic-output safety patterns
  - canary-appearances-index-v1 as the future TCR-007 correlation authority
public_interfaces:
  - canary-tibia-proficiency-index-v1
cross_repo_tasks: []
---

# Goal

Deliver and merge TCR-004 Proficiency Reference Index as deterministic, fail-closed, read-only `canary-tibia-proficiency-index-v1` evidence bound to exact stable TCR-001 manifest provenance.

# Completion

- Final status: completed.
- Delivery PR: #858.
- Delivery merge commit: `ce2c6e611f98f82c4f84e948372da0e1d324761f`.
- Delivery final head: `7ca341da78889e6a322de121d8d45a61f96fb542`.
- `ci:final-gate` was applied before the final checkpoint commit.
- Protected ready-state milestone CI passed without macOS.
- Lifecycle/discovery closure PR: #860.
- Lifecycle/discovery closure branch: `docs/tcr-004-lifecycle-closure-20260724`.
- Programme queue and stable-contract state are updated by PR #860.
- Archived at: `docs/agents/tasks/archive/CAN-20260724-tcr-004-proficiency-reference-index.md`.

# Delivered

- `canary-tibia-proficiency-index-v1` library and CLI;
- exact manifest selected-input ID, size and SHA-256 binding;
- bounded raw UTF-8 JSON, XZ, LZMA-alone and reviewed Tibia LZMA-header handling;
- strict duplicate JSON-key, unsupported-field, malformed-value and configured-bound rejection;
- deterministic preservation of proficiency IDs, names, optional versions, ordered levels, optional XP requirements and reviewed ordered perk fields;
- explicit duplicate proficiency-ID and duplicate-name findings without record overwrite;
- explicit definition-only `client-reference.proficiency-id` namespace;
- create-new/no-clobber output safety and atomic explicit overwrite;
- JSON schema, documentation, module-catalog registration and 15 focused tests plus one opt-in real-file test;
- no proprietary client input or generated real-file report committed;
- no appearance reparsing, `items.xml` writing, runtime registration, persistence/protocol claim or gameplay conclusion.

# Final delivery validation evidence

Exact final delivery PR head: `7ca341da78889e6a322de121d8d45a61f96fb542`.

- Fixture-only focused validation: PASS, 15 tests passed and one opt-in real-file test skipped.
- External opt-in validation: PASS, all 15 tests passed against source SHA-256 `1a915dffd9265cd1c18d39e55da7ede691b2e58add534bc186238ae028a73f22` outside Git.
- Real-file evidence summary: 420 definitions, 2052 levels, 3287 perks, zero `XpRequired`, duplicate-ID or duplicate-name findings.
- Agent Task Ownership: PASS, run `30075468652`.
- Tibia Client Reference: PASS, run `30075468696`.
- AI Agent Tools: PASS, run `30075468703`.
- Final-checkpoint repository CI/Required: PASS, run `30075468811`.
- Protected ready-state milestone CI: PASS, run `30075569304`.
- Autofix: PASS with no changes, run `30075569144`.
- Squash merge: `ce2c6e611f98f82c4f84e948372da0e1d324761f`.

# Stable producer contract state

`canary-tibia-proficiency-index-v1` is `stable/merged` as exact manifest-bound proficiency-definition reference evidence. It does not prove equivalence with appearance IDs or Canary runtime bindings, XP/mastery formulas, perk application, persistence, protocol/UI behavior or gameplay parity.

# Preserved unknowns and conflicts

- UNKNOWN: exact client build identity unless separately proven by the stable manifest.
- UNKNOWN: whether later client proficiency files introduce fields beyond the independently reviewed JSON shape.
- UNKNOWN: numeric proficiency-ID equivalence across client reference, appearance and Canary runtime evidence until TCR-007 proves an explicit join.
- UNKNOWN: the StaticMapData `object_id` mapping and exact reviewed house-ID resolver required by TCR-005.
- CONFLICTS: none.

# Next package

After this lifecycle closure merges, TCR-005 — OTBM House Reference Parity is the next programme candidate only after a fresh ownership/PR/reuse/house-ID-resolver preflight. It must start as a separate bounded task, branch and PR; this closure does not implement TCR-005 or TCR-007.
