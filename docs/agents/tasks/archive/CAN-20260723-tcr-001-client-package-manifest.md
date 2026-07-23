---
task_id: CAN-20260723-tcr-001-client-package-manifest
program_id: CAN-PROGRAM-OTBM-TIBIA-CLIENT-REFERENCE
coordination_id: OTBM-TIBIA-CLIENT-REFERENCE
status: completed
agent: GPT-5.6 Thinking
branch: feat/tcr-001-client-package-manifest-20260723
base_branch: main
created: 2026-07-23T16:48:37+02:00
updated: 2026-07-23T17:43:45+02:00
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
- `ci:final-gate` applied before final-head validation and merge.
- Post-ready repository CI run `30019230636` passed on the same immutable final head before merge.
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

# Final validation evidence

Exact final delivery PR head: `87612fa0209a490a16bb7da9d58599f9aca424f8`.

- Tibia Client Reference: PASS, run `30018945493`.
- Agent Task Ownership: PASS, run `30018945592`.
- AI Agent Tools: PASS, run `30018945525`.
- Repository CI final-gate: PASS, run `30018946278`.
- Post-ready repository CI: PASS, run `30019230636`.

# Next package

TCR-002 — StaticData Reference Index is the next programme package. It must start as a separate bounded task/branch/PR and consume the merged `canary-tibia-client-reference-manifest-v1` provenance contract; this lifecycle closure does not implement TCR-002.
