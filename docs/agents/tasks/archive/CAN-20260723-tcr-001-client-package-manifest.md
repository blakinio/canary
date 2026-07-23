---
task_id: CAN-20260723-tcr-001-client-package-manifest
program_id: CAN-PROGRAM-OTBM-TIBIA-CLIENT-REFERENCE
coordination_id: OTBM-TIBIA-CLIENT-REFERENCE
status: completed
agent: GPT-5.6 Thinking
branch: feat/tcr-001-client-package-manifest-20260723
base_branch: main
created: 2026-07-23T16:48:37+02:00
updated: 2026-07-23T17:40:00+02:00
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

Deliver TCR-001 Client Package Manifest as the deterministic, fail-closed, read-only provenance boundary for explicitly selected files below one user-supplied Tibia client reference package root.

# Completion

- Final status: completed
- Delivery PR: #809
- Delivery final head: `87612fa0209a490a16bb7da9d58599f9aca424f8`
- Delivery merge commit: `3227ee1e3b5f323656b101a601f873ae21b61f27`
- Lifecycle closure PR: pending
- Archived at: `docs/agents/tasks/archive/CAN-20260723-tcr-001-client-package-manifest.md`

# Delivered

- stable public format `canary-tibia-client-reference-manifest-v1`;
- explicit package root and explicit 1..128 selected safe relative files;
- SHA-256 and byte size per selected input with bounded pre-hash size checks and file-identity/change detection;
- fail-closed path escape, symlink, missing/non-file, duplicate resolved target and hardlink rejection;
- exact client build evidence states `proven`, `declared`, `unknown`, `conflicting`, with no filename-based build inference;
- optional generated-index SHA-256 pins without arbitrary generated-index path reads;
- deterministic JSON, explicit observed timestamp metadata and exact parser revision;
- create-new/no-clobber default with output symlink/input alias rejection and explicit atomic overwrite;
- JSON schema, contract documentation, 13 focused safety/determinism tests and dedicated `Tibia Client Reference` workflow;
- no TCR-002/TCR-003/TCR-004 parser implementation, no proprietary client inputs, no OTBM/runtime mutation.

# Final validation evidence

Exact final delivery head: `87612fa0209a490a16bb7da9d58599f9aca424f8`.

- Agent Task Ownership: PASS, run `30018945592`.
- Tibia Client Reference: PASS, run `30018945493`.
- AI Agent Tools: PASS, run `30018945525`.
- Exact-final-head repository CI / Required: PASS, run `30018946278`.
- Protected ready-state full repository CI: PASS, run `30019230636`.
- PR #809 was non-draft and mergeable immediately before squash merge.
- Squash merge completed as `3227ee1e3b5f323656b101a601f873ae21b61f27`.

# Stable producer contract state

`canary-tibia-client-reference-manifest-v1` is now `stable/merged` and may be used as the TCR package-identity/provenance producer contract by later bounded consumers.

This does **not** make any later TCR producer or parity output stable. The following remain planned/non-consumable until their own bounded packages merge:

- `canary-tibia-staticdata-index-v1`;
- `canary-tibia-staticmapdata-index-v1`;
- `canary-tibia-proficiency-index-v1`;
- `canary-otbm-house-reference-parity-v1`;
- `canary-tibia-content-reference-correlation-v1`;
- `canary-tibia-proficiency-reference-correlation-v1`;
- `canary-tibia-client-reference-drift-v1`;
- later evidence-gateway/adoption-routing outputs.

OWA-003 may later consume the stable manifest contract only where package/reference identity and exact provenance are required. It must not treat the manifest as StaticData, StaticMapData, map authority, gameplay parity, or evidence that any later TCR contract is stable.

# Remaining programme work

The next bounded package must be selected from the then-current programme queue after a fresh ownership/dependency preflight. Do not bundle TCR-002 and TCR-003 in one task or PR.
