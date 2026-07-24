---
task_id: CAN-20260724-real-tibia-evidence-collector-architecture
program_id: CAN-PROGRAM-REAL-TIBIA-EVIDENCE-COLLECTION
coordination_id: RT-EVIDENCE-COLLECTOR-ARCHITECTURE
status: active
agent: "GPT-5.6 Thinking"
branch: docs/real-tibia-evidence-collector-architecture-20260724
base_branch: main
created: 2026-07-24T20:15:00+02:00
updated: 2026-07-24T20:15:00+02:00
last_verified_commit: "UNKNOWN"
risk: low
related_issue: ""
related_pr: ""
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
cross_repo_tasks: []
---

# Goal

Define a complete documentation-only architecture, durable file layout, concurrency model and reusable operating prompt for a Real Tibia Evidence Collector that can build version-aware, source-pinned module dossiers for all 62 canonical modules without taking ownership from Universal E2E, OTBM, TCR or feature programmes.

# Acceptance criteria

- [ ] Define the Collector mission, authority boundaries and fail-closed evidence rules.
- [ ] Define detailed per-module behavior, state-transition, persistence, protocol, map, client, edge-case and rationale documentation.
- [ ] Define mandatory version history with introduced/changed/deprecated/removed/observed states and proof boundaries.
- [ ] Define source-of-truth precedence by evidence dimension.
- [ ] Define structured evidence and owner-request templates.
- [ ] Define cooperation contracts with Universal E2E, OTBM/OWA and TCR without duplicating their work.
- [ ] Define a safe parallel-agent model for the 62-module campaign.
- [ ] Deliver a reusable prompt for coordinator and worker agents.
- [ ] Keep this package documentation-only: no runtime, E2E, OTBM, TCR, map, client, datapack or schema implementation changes.
- [ ] Verify exact changed files and current-head CI before completion.

# Confirmed context

- The Real Tibia registry currently contains 62 canonical modules.
- The global parity programme already owns source roles, module discovery, bounded delivery and proof-level rules.
- Universal E2E owns physical execution, controlled OTClient, runtime/SQL/client evidence and reusable lifecycle infrastructure.
- OTBM/OWA owns canonical static map evidence, World Index, Script Resolution, Reachability, Semantic Diff and bounded map certification.
- TCR owns official-client reference package parsing, normalization and correlation contracts.
- The new Collector must consume stable outputs from those programmes and may create evidence requests, but must not implement or rerun their responsibilities.

# Existing work to reuse

| Module/task/PR | Reuse | Evidence/path | Why it fits |
|---|---|---|---|
| Real Tibia parity governance | source precedence, evidence levels, bounded tasks | `docs/agents/REAL_TIBIA_PARITY_PLAYBOOK.md` | canonical parity rules |
| Real Tibia registry | 62 module identities, dependencies, freshness | `docs/agents/real-tibia/registry/**` | canonical module discovery |
| Universal E2E | physical/runtime proof and result envelopes | `docs/agents/programs/E2E_AUTOMATION_PROGRAM.md` | no duplicate runner or orchestration |
| OTBM World Assurance | static map evidence and certification | `docs/agents/programs/OTBM_WORLD_ASSURANCE_OPERATIONS_PROGRAM.md` | no duplicate parser/pathfinder/certifier |
| Tibia Client Reference | client-reference provenance and correlation | `docs/agents/programs/OTBM_TIBIA_CLIENT_REFERENCE_PROGRAM.md` | no duplicate official-client parsers |

# Ownership and overlap check

- Program record: new bounded evidence-collection programme.
- Open PRs inspected: current open repository PR inventory; no matching evidence-collector architecture PR found.
- Active tasks inspected: targeted search found no matching collector task.
- Exclusive claims: only the seven new documentation/template paths in this task.
- Read-only dependencies: global parity, E2E, OTBM/OWA, TCR and registry paths.
- Overlaps: none identified for owned paths.
- Resolution: no shared programme/index path will be edited in this package.

# Current state

Architecture drafting in progress.

# Plan

1. Add the long-lived programme and complete architecture document.
2. Add evidence, request, dossier and prompt templates.
3. Open a draft PR, review the exact diff and update the checkpoint.
4. Run/inspect applicable current-head validation and complete the merge gate when safe.

# Decisions

| Decision | Reason/evidence | ADR |
|---|---|---|
| Collector is a coordination/evidence layer, not a gameplay executor | preserves E2E/OTBM/TCR ownership | architecture document |
| YAML is the durable machine-readable source; Markdown is the human behavior/rationale layer | supports validation, deduplication and detailed explanation | architecture document |
| Version history is mandatory per claim and behavior contract | enables comparison against current and future Canary baselines | architecture document |
| Default concurrency is bounded and shared paths are coordinator-only | prevents multi-agent overwrite and CI/review overload | architecture document |

# Files and interfaces

| Path/interface/config/schema | Ownership mode | Purpose | Status |
|---|---|---|---|
| `docs/agents/programs/REAL_TIBIA_EVIDENCE_COLLECTION_PROGRAM.md` | exclusive | long-lived queue and boundaries | planned |
| `docs/ai-agent/REAL_TIBIA_EVIDENCE_COLLECTOR_ARCHITECTURE.md` | exclusive | full architecture | planned |
| evidence/request templates | exclusive | proposed structured contracts | planned |
| dossier template | exclusive | detailed module documentation contract | planned |
| collector prompt | exclusive | reusable autonomous operating prompt | planned |

# Validation and CI

| Commit | Command/check/workflow | Result | Evidence/notes |
|---|---|---|---|
| UNKNOWN | changed-file and documentation review | not-run | pending final head |
| UNKNOWN | Agent Task Ownership | not-run | pending PR |
| UNKNOWN | CI / AI Agent Tools | not-run | pending PR |

# Failed approaches and dead ends

- An initial draft-PR creation was attempted before the branch existed and GitHub correctly rejected the invalid head. The branch was then created from `main`; no repository content was changed by the failed PR calls.

# Risks and compatibility

- Runtime: none; documentation only.
- Data/migration: none.
- Security: no credentials, captures, proprietary assets or raw client files may be committed.
- Backward compatibility: proposed contracts are architecture-only until a later schema/tooling task implements them.
- Cross-repo rollout: none; `blakinio/otclient` remains read-only unless separately authorized.
- Rollback: close the documentation PR without merge.

# Remaining work

1. Create all planned architecture and template files.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-24T20:15:00+02:00
head: UNKNOWN
branch: docs/real-tibia-evidence-collector-architecture-20260724
pr: none
status: implementing
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
  - No matching open evidence-collector architecture PR was found.
derived:
  - A separate evidence coordination layer can improve coverage without duplicating execution systems when it only emits owner requests and consumes stable outputs.
unknown:
  - Final current-head CI result.
conflicts: []
first_failure:
  marker: none
  evidence: none
rejected_hypotheses:
  - Collector should run its own E2E or OTBM analysis: rejected because canonical owner programmes already exist.
changed_paths:
  - docs/agents/tasks/active/CAN-20260724-real-tibia-evidence-collector-architecture.md
validation:
  - command: targeted repository/PR/ownership discovery
    result: PASS
    evidence: no matching open collector architecture task or PR found
blockers: []
next_action: Create the long-lived programme record.
```

# Handoff

## Start here

Read this task, the new programme and architecture document, then verify the live PR/head.

## Do not repeat

Do not create a second E2E runner, OTBM parser/index/pathfinder/certifier, TCR parser or alternate Real Tibia module registry.

## Required reads

- `AGENTS.md`
- `docs/agents/REPOSITORY_MAP.md`
- `docs/agents/CONTEXT_ROUTING.md`
- `docs/agents/REAL_TIBIA_EVIDENCE_SOURCES.md`
- `docs/agents/REAL_TIBIA_PARITY_PLAYBOOK.md`
- `docs/agents/programs/REAL_TIBIA_PARITY_PROGRAM.md`
- `docs/agents/programs/E2E_AUTOMATION_PROGRAM.md`
- `docs/agents/programs/OTBM_WORLD_ASSURANCE_OPERATIONS_PROGRAM.md`

## Open questions

- None for the docs-only architecture package.
