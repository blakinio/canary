---
task_id: CAN-20260723-tcr-001-client-package-manifest
program_id: CAN-PROGRAM-OTBM-TIBIA-CLIENT-REFERENCE
coordination_id: OTBM-TIBIA-CLIENT-REFERENCE
status: completed
agent: GPT-5.6 Thinking
branch: feat/tcr-001-client-package-manifest-20260723
base_branch: main
created: 2026-07-23T16:48:37+02:00
updated: 2026-07-23T17:52:00+02:00
last_verified_commit: "3227ee1e3b5f323656b101a601f873ae21b61f27"
risk: medium
related_issue: ""
related_pr: "809"
depends_on:
  - TCR-000 merged architecture/governance
blocks: []
owned_paths:
  exclusive: []
  shared: []
  read_only: []
modules_touched:
  - OTBM analysis tooling
  - official-client reference evidence
reuses:
  - OTBM Tibia client reference architecture
  - OTBM Compact Evidence Gateway path/hash/output safety conventions
  - AI Agent Tools broad Python test workflow
public_interfaces:
  - canary-tibia-client-reference-manifest-v1
cross_repo_tasks: []
---

# Goal

Deliver and merge TCR-001 Client Package Manifest: deterministic, fail-closed, read-only provenance for explicitly selected files below one user-supplied Tibia client reference package root.

# Completion

- Final status: completed
- Delivery PR: #809
- Delivery merge commit: `3227ee1e3b5f323656b101a601f873ae21b61f27`
- Delivery final head: `87612fa0209a490a16bb7da9d58599f9aca424f8`
- Lifecycle/discovery closure PR: #812
- `ci:final-gate` applied to PR #812 before this final lifecycle checkpoint commit.
- Programme queue/stable-state updated in PR #812.
- Existing `otbm-tooling`/TCR discovery module is reused; no duplicate registry or catalogue module was created.
- Archived at: `docs/agents/tasks/archive/CAN-20260723-tcr-001-client-package-manifest.md`

# Delivered

- merged Python 3.12 standard-library `canary-tibia-client-reference-manifest-v1` library and CLI;
- explicit one-package-root and 1..128 explicitly selected safe-relative-file provenance;
- fail-closed path escape, symlink root/ancestor/component, missing/non-file, duplicate and hardlink rejection;
- bounded streaming SHA-256 with file identity/change detection and exact applied file-size bound;
- explicit `proven`, `declared`, `unknown` and `conflicting` client-build evidence states without filename/directory inference;
- optional generated-index SHA-256 pins without arbitrary generated-output reads;
- deterministic JSON with explicit observation timestamp and exact parser revision;
- create-new/no-clobber output by default plus output symlink/input-alias rejection and atomic explicit overwrite;
- JSON schema, contract documentation, 13 focused safety/determinism tests and dedicated `Tibia Client Reference` workflow;
- no TCR-002/TCR-003 parser, no recursive package ingestion, no selected-content execution, no proprietary client input and no OTBM/runtime mutation.

# Final delivery validation evidence

Exact final delivery PR head: `87612fa0209a490a16bb7da9d58599f9aca424f8`.

- Tibia Client Reference: PASS, run `30018945493`.
- Agent Task Ownership: PASS, run `30018945592`.
- AI Agent Tools: PASS, run `30018945525`.
- Repository CI exact-final-gate: PASS, run `30018946278`.
- Protected post-ready full repository CI: PASS, run `30019230636`.
- Squash merge completed as `3227ee1e3b5f323656b101a601f873ae21b61f27`.

# Stable producer contract state

`canary-tibia-client-reference-manifest-v1` is now `stable/merged` and may be used by later bounded consumers only as the exact client package/reference provenance contract.

This does not make any later TCR producer or parity output stable. The following remain planned/non-consumable until their own bounded packages merge:

- `canary-tibia-staticdata-index-v1`;
- `canary-tibia-staticmapdata-index-v1`;
- `canary-tibia-proficiency-index-v1`;
- `canary-otbm-house-reference-parity-v1`;
- `canary-tibia-content-reference-correlation-v1`;
- `canary-tibia-proficiency-reference-correlation-v1`;
- `canary-tibia-client-reference-drift-v1`;
- later evidence-gateway/adoption-routing outputs.

OWA-003 may later consume the stable manifest only for package/reference identity and exact provenance where required. It must not treat the manifest as StaticData, StaticMapData, canonical OTBM geometry, gameplay parity, or proof that any later TCR contract is stable. This lifecycle closure does not implement OWA-003.

# Next package

After PR #812 merges, a continuation agent must perform a fresh current-main ownership/PR/reuse preflight. TCR-002 — StaticData Reference Index is the next programme candidate only if it remains the first unowned, unblocked and dependency-satisfied package. It must start as a separate bounded task/branch/PR and consume the merged `canary-tibia-client-reference-manifest-v1` provenance contract; TCR-003 must not be bundled into it.
