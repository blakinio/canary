---
task_id: CAN-20260723-otbm-tibia-client-reference-architecture
program_id: CAN-PROGRAM-OTBM-TIBIA-CLIENT-REFERENCE
coordination_id: OTBM-TIBIA-CLIENT-REFERENCE
status: completed
agent: GPT-5.6 Thinking
branch: docs/otbm-tibia-client-reference-20260723
base_branch: main
created: 2026-07-23T10:00:00+02:00
updated: 2026-07-23T16:25:23+02:00
last_verified_commit: "d5a08db0502fb85ff807c9c18f02bf92bd1faaed"
risk: low
related_issue: ""
related_pr: "762"
depends_on:
  - docs/agents/REAL_TIBIA_EVIDENCE_SOURCES.md
  - docs/agents/REAL_TIBIA_PARITY_PLAYBOOK.md
  - docs/agents/programs/REAL_TIBIA_PARITY_PROGRAM.md
  - docs/ai-agent/OTS_OTBM_TOOLING_ROADMAP.md
  - Unified OTBM World Index and existing OTBM QA/repair stack
blocks: []
owned_paths:
  exclusive: []
  shared: []
  read_only: []
modules_touched:
  - OTBM analysis tooling
  - Real Tibia parity governance
  - official-client reference evidence
reuses:
  - canary-otbm-world-index-v1
  - canary-appearances-index-v1
  - canary-client-assets-index-v1
  - canary-otbm-asset-compatibility-v1
  - OTBM Script Resolution
  - OTBM Reachability
  - Semantic OTBM Diff
  - Universal Physical E2E
public_interfaces:
  - TCR architecture and programme queue only; no producer output format delivered
cross_repo_tasks: []
---

# Goal

Define and merge the durable architecture and bounded programme for using exact user-supplied Tibia 15.x client files as read-only reference evidence without creating a second OTBM parser, pathfinder, renderer, mutation engine or E2E platform.

# Completion

- Final status: completed
- PR: #762
- Merge commit: `d5a08db0502fb85ff807c9c18f02bf92bd1faaed`
- Program record updated: yes, in the TCR-000 lifecycle closure PR
- Catalogue updated: yes, in PR #762
- Changelog updated: yes, in PR #762
- Archived at: `docs/agents/tasks/archive/CAN-20260723-otbm-tibia-client-reference-architecture.md`

# Delivered

- merged `docs/ai-agent/OTBM_TIBIA_CLIENT_REFERENCE_ARCHITECTURE.md`;
- merged `docs/agents/programs/OTBM_TIBIA_CLIENT_REFERENCE_PROGRAM.md` with bounded TCR-000..TCR-011 queue;
- extended the existing `otbm-tooling` registry record instead of creating a duplicate module;
- preserved proof boundaries for StaticData, StaticMapData, proficiency and minimap evidence;
- preserved exact provenance, fail-closed unresolved states and deterministic-contract requirements for future producers;
- documented reuse of canonical World Index, appearances/assets indexes, Script Resolution, Reachability, Semantic Diff, repair/materialization and Physical E2E owners;
- delivered no parser, no TCR producer artifact, no proprietary client input and no map/runtime mutation.

# Final validation evidence

Exact final PR head: `aa92eb3f111060b6abff6e8ba2ad8950ed458842`.

- Agent Task Ownership: PASS, run `30014055193`.
- Real Tibia Module Registry: PASS, run `30014055198`.
- Upstream Intelligence: PASS, run `30014055018`.
- OTBM Map Tools: PASS, run `30014054983`.
- AI Agent Tools: PASS, run `30014054831`.
- Repository CI candidate-head run: PASS, run `30014055277`.
- Protected ready-state repository CI / Required run: PASS, run `30014228463`.
- Final pre-merge check: `main` remained `b8a88f073b2609b444fa15370aae30ac9f80b908`, PR head remained `aa92eb3f111060b6abff6e8ba2ad8950ed458842`, PR was non-draft and mergeable.
- Squash merge completed as `d5a08db0502fb85ff807c9c18f02bf92bd1faaed`.

# Stable producer contract state

TCR-000 merged architecture/governance only. No TCR producer/report format is stable/merged yet for OWA-003 consumption.

The following remain planned and non-consumable until their owning bounded packages merge:

- `canary-tibia-client-reference-manifest-v1`;
- `canary-tibia-staticdata-index-v1`;
- `canary-tibia-staticmapdata-index-v1`;
- `canary-tibia-proficiency-index-v1`;
- `canary-otbm-house-reference-parity-v1`;
- `canary-tibia-content-reference-correlation-v1`;
- `canary-tibia-proficiency-reference-correlation-v1`;
- `canary-tibia-client-reference-drift-v1`;
- later evidence-gateway/adoption-routing outputs.

# Remaining programme work

The next eligible package is TCR-001 Client Package Manifest, but it must begin only from then-current `main` after a fresh preflight proving no equivalent canonical manifest exists and no active owner already claims the package.

TCR-002/TCR-003 must not be bundled into TCR-001.
