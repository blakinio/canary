---
task_id: CAN-20260724-real-tibia-evidence-collector-architecture
program_id: CAN-PROGRAM-REAL-TIBIA-EVIDENCE-COLLECTION
coordination_id: RT-EVIDENCE-COLLECTOR-ARCHITECTURE
status: review
agent: "GPT-5.6 Thinking"
branch: docs/real-tibia-evidence-collector-architecture-20260724
base_branch: main
created: 2026-07-24T20:15:00+02:00
updated: 2026-07-24T20:50:00+02:00
last_verified_commit: "b8a00ea792d0316a8419eac380db4aab6dd21355"
risk: low
related_issue: ""
related_pr: "889"
depends_on: []
blocks: []
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260724-real-tibia-evidence-collector-architecture.md
    - docs/agents/programs/REAL_TIBIA_EVIDENCE_COLLECTION_PROGRAM.md
    - docs/ai-agent/REAL_TIBIA_EVIDENCE_COLLECTOR_ARCHITECTURE.md
    - docs/agents/templates/REAL_TIBIA_EVIDENCE_RECORD.yaml
    - docs/agents/templates/REAL_TIBIA_EVIDENCE_REQUEST.yaml
    - docs/agents/templates/REAL_TIBIA_MODULE_DOSSIER.md
    - docs/agents/templates/REAL_TIBIA_EVIDENCE_COLLECTOR_PROMPT.md
  shared: []
  read_only:
    - docs/agents/programs/REAL_TIBIA_PARITY_PROGRAM.md
    - docs/agents/programs/E2E_AUTOMATION_PROGRAM.md
    - docs/agents/programs/OTBM_WORLD_ASSURANCE_OPERATIONS_PROGRAM.md
    - docs/agents/programs/OTBM_TIBIA_CLIENT_REFERENCE_PROGRAM.md
    - docs/agents/REAL_TIBIA_EVIDENCE_SOURCES.md
    - docs/agents/REAL_TIBIA_PARITY_PLAYBOOK.md
    - docs/agents/real-tibia/**
modules_touched:
  - real-tibia-evidence-collection
  - platform-tooling
reuses:
  - CAN-PROGRAM-REAL-TIBIA-PARITY
  - CAN-PROGRAM-E2E-PLATFORM
  - CAN-PROGRAM-OTBM-WORLD-ASSURANCE-OPERATIONS
  - CAN-PROGRAM-OTBM-TIBIA-CLIENT-REFERENCE
public_interfaces:
  - proposed evidence record contract
  - proposed evidence request contract
  - proposed module dossier contract
  - coordinator, worker and reviewer prompts
cross_repo_tasks: []
---

# Goal

Define a complete documentation-only architecture, durable file layout, concurrency model and reusable operating prompts for a Real Tibia Evidence Collector that can build version-aware, source-pinned module dossiers for all 62 canonical modules without taking ownership from Universal E2E, OTBM/OWA, TCR or feature programmes.

# Acceptance criteria

- [x] Define the Collector mission, authority boundaries and fail-closed evidence rules.
- [x] Define detailed per-module behavior, state-transition, persistence, protocol, map, client, edge-case and rationale documentation.
- [x] Define mandatory version history with announced/introduced/observed/changed/deprecated/removed states and proof boundaries.
- [x] Define source-of-truth precedence by evidence dimension.
- [x] Define structured evidence and owner-request templates.
- [x] Define cooperation contracts with Universal E2E, OTBM/OWA and TCR without duplicating their work.
- [x] Define a safe parallel-agent model for the 62-module campaign.
- [x] Deliver reusable coordinator, worker and reviewer prompts.
- [x] Keep this package documentation-only: no runtime, E2E, OTBM, TCR, map, client, datapack or schema implementation changes.
- [ ] Verify current-head required CI and autonomous merge gate.

# Confirmed context

- The canonical Real Tibia registry contains 62 modules.
- The global parity programme already owns source roles, proof levels, module routing and bounded delivery.
- Universal E2E owns physical execution, controlled OTClient, runtime/SQL/UI evidence and reusable lifecycle infrastructure.
- OTBM/OWA owns World Index, Script Resolution, Reachability, Semantic Diff, factual rendering and map certification.
- TCR owns official-client reference parsing, normalization and identifier correlation.
- Collector output must preserve separate official release, client build, protocol profile, Canary commit, map hash, datapack, appearances, spawn/NPC sidecar and database schema axes.

# Existing work to reuse

| Programme | Reuse | Boundary |
|---|---|---|
| Real Tibia parity | sources, proof levels, bounded findings | Collector does not replace parity governance |
| Real Tibia registry | 62 module IDs, dependencies, freshness | no 63rd module in this architecture PR |
| Universal E2E | physical/runtime proof and result envelopes | no runner/scenario/platform edits |
| OTBM/OWA | static map evidence and certification | no parser/pathfinder/renderer/certifier edits |
| TCR | client-reference evidence and correlation | no client parser or identifier inference |

# Ownership and overlap check

- Open PR inventory was inspected before branch creation.
- No matching open Collector architecture PR or active task was found.
- PR #889 changes exactly the seven task-owned documentation/template paths.
- E2E PR #885 and OAM PR #888 remain independent and their paths are read-only for this task.
- No shared registry, generated index, E2E, OTBM, TCR, runtime, client, map or datapack path is changed.

# Current state

Architecture package delivered on draft PR #889. Current head before this checkpoint commit: `b8a00ea792d0316a8419eac380db4aab6dd21355`.

Delivered:

1. `CAN-PROGRAM-REAL-TIBIA-EVIDENCE-COLLECTION` with RTEC-000..007 queue.
2. Full Collector architecture and detailed module behavior contract.
3. Mandatory version history and separate revision axes.
4. Source authority and proof-level rules.
5. Evidence and owner-request YAML templates.
6. Detailed module dossier template.
7. Explicit E2E, OTBM/OWA and TCR cooperation boundaries and expansion suggestions.
8. Parallel model: one coordinator, up to eight workers, up to two reviewers and at most four open Collector PRs.
9. Coordinator, worker and reviewer prompts.

# Decisions

| Decision | Reason/evidence | Durable record |
|---|---|---|
| Collector is coordination/evidence only | avoids duplicate E2E/OTBM/TCR execution systems | architecture/programme |
| YAML records plus Markdown dossiers | machine validation plus detailed human-readable behavior/rationale | templates/architecture |
| Version history is mandatory | supports current and future Canary comparison across changing Tibia behavior | architecture/templates |
| Version axes remain separate | protocol, map, datapack and official release can evolve independently | architecture/templates |
| Default cap is 8 workers and 4 open PRs | balances 62-module scale against ownership, CI/storage and review pressure | programme/architecture |
| Shared files are coordinator-only | allows safe module-level parallelism | programme/prompts |
| Store decision rationale, not hidden reasoning | preserves auditable constraints/trade-offs/rejections without chain-of-thought | dossier/architecture |

# Files and interfaces

| Path | Purpose | Status |
|---|---|---|
| `docs/agents/programs/REAL_TIBIA_EVIDENCE_COLLECTION_PROGRAM.md` | long-lived queue, boundaries and concurrency | delivered |
| `docs/ai-agent/REAL_TIBIA_EVIDENCE_COLLECTOR_ARCHITECTURE.md` | complete architecture | delivered |
| `docs/agents/templates/REAL_TIBIA_EVIDENCE_RECORD.yaml` | proposed claim/evidence contract | delivered |
| `docs/agents/templates/REAL_TIBIA_EVIDENCE_REQUEST.yaml` | proposed owner-request lifecycle | delivered |
| `docs/agents/templates/REAL_TIBIA_MODULE_DOSSIER.md` | detailed behavior/version/comparison dossier | delivered |
| `docs/agents/templates/REAL_TIBIA_EVIDENCE_COLLECTOR_PROMPT.md` | coordinator/worker/reviewer prompts | delivered |

# Validation and CI

| Commit | Command/check/workflow | Result | Evidence/notes |
|---|---|---|---|
| `b8a00ea792d0316a8419eac380db4aab6dd21355` | PR changed-file inventory | PASS | exactly seven intended documentation/template paths |
| current | full diff boundary review | PASS | no runtime/client/map/datapack/E2E/OTBM/TCR paths |
| current | Agent Task Ownership | NOT_RUN | awaiting final-head PR checks |
| current | AI Agent Tools / CI | NOT_RUN | awaiting final-head PR checks |

# Failed approaches and dead ends

- Draft PR creation before branch creation was rejected by GitHub with invalid head. The branch was then created from `main`; no content mutation resulted from the failed calls.
- The architecture intentionally does not create empty dossier directories or add a 63rd registry module before schemas, validator and tests exist.

# Risks and compatibility

- Runtime: none; documentation only.
- Data/migration: none.
- Security: external/proprietary files remain outside Git; records retain only bounded metadata and hashes.
- Backward compatibility: contracts are proposed architecture until RTEC-001 implements schemas and validation.
- Cross-repository rollout: none; OTClient remains read-only.
- CI/storage: future campaign is capped at four open Collector PRs by default.
- Rollback: close PR #889 without merge.

# Remaining work

1. Run and inspect exact-final-head required checks.
2. Resolve any review or validation findings.
3. Mark ready and merge only if the autonomous merge gate is satisfied.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-24T20:50:00+02:00
head: b8a00ea792d0316a8419eac380db4aab6dd21355
branch: docs/real-tibia-evidence-collector-architecture-20260724
pr: 889
status: validating
context_routes:
  - agent-governance
  - real-tibia-parity
owned_paths:
  - docs/agents/tasks/active/CAN-20260724-real-tibia-evidence-collector-architecture.md
  - docs/agents/programs/REAL_TIBIA_EVIDENCE_COLLECTION_PROGRAM.md
  - docs/ai-agent/REAL_TIBIA_EVIDENCE_COLLECTOR_ARCHITECTURE.md
  - docs/agents/templates/REAL_TIBIA_EVIDENCE_RECORD.yaml
  - docs/agents/templates/REAL_TIBIA_EVIDENCE_REQUEST.yaml
  - docs/agents/templates/REAL_TIBIA_MODULE_DOSSIER.md
  - docs/agents/templates/REAL_TIBIA_EVIDENCE_COLLECTOR_PROMPT.md
proven:
  - The canonical registry contains 62 modules.
  - E2E, OTBM/OWA and TCR already own physical, static-map and official-client-reference execution domains.
  - PR 889 changes exactly seven intended documentation/template paths.
  - The architecture records detailed behavior, version history, owner requests and bounded concurrency without modifying owner implementation paths.
derived:
  - Eight workers with four open PRs is a conservative default that permits parallel research while limiting ownership, CI/storage and review pressure.
unknown:
  - Final current-head required check results.
conflicts: []
first_failure:
  marker: none
  evidence: none
rejected_hypotheses:
  - Collector should run its own E2E or OTBM analysis: rejected because canonical owner programmes already exist.
  - All 62 modules should receive empty placeholder dossiers now: rejected because placeholders would imply coverage before schemas and evidence exist.
changed_paths:
  - docs/agents/programs/REAL_TIBIA_EVIDENCE_COLLECTION_PROGRAM.md
  - docs/agents/tasks/active/CAN-20260724-real-tibia-evidence-collector-architecture.md
  - docs/agents/templates/REAL_TIBIA_EVIDENCE_COLLECTOR_PROMPT.md
  - docs/agents/templates/REAL_TIBIA_EVIDENCE_RECORD.yaml
  - docs/agents/templates/REAL_TIBIA_EVIDENCE_REQUEST.yaml
  - docs/agents/templates/REAL_TIBIA_MODULE_DOSSIER.md
  - docs/ai-agent/REAL_TIBIA_EVIDENCE_COLLECTOR_ARCHITECTURE.md
validation:
  - command: GitHub PR changed-file inventory and full documentation boundary review
    result: PASS
    evidence: PR 889 has seven intended docs/template paths and no owner implementation path
  - command: exact-final Agent Task Ownership, AI Agent Tools and CI
    result: NOT_RUN
    evidence: required after this checkpoint commit
blockers: []
next_action: Apply the final-gate label and inspect exact-head PR checks.
```

# Handoff

## Start here

Read this task, PR #889, the evidence collection programme and Collector architecture. Verify the current head and checks before any edit.

## Do not repeat

Do not create a second E2E runner, OTBM parser/index/pathfinder/certifier, TCR parser, alternate registry, 62 empty dossiers or unbounded all-modules task.

## Required reads

- `AGENTS.md`
- `docs/agents/REPOSITORY_MAP.md`
- `docs/agents/CONTEXT_ROUTING.md`
- `docs/agents/programs/REAL_TIBIA_EVIDENCE_COLLECTION_PROGRAM.md`
- `docs/ai-agent/REAL_TIBIA_EVIDENCE_COLLECTOR_ARCHITECTURE.md`
- `docs/agents/REAL_TIBIA_EVIDENCE_SOURCES.md`
- `docs/agents/REAL_TIBIA_PARITY_PLAYBOOK.md`

## Open questions

- None for architecture content; only current-head validation remains.
