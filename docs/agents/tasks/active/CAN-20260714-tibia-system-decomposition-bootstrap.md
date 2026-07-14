---
task_id: CAN-20260714-tibia-system-decomposition-bootstrap
program_id: CAN-PROGRAM-TIBIA-SYSTEM-DECOMPOSITION
coordination_id: REAL-TIBIA-SYSTEM-DECOMPOSITION
status: active
agent: "GPT-5.6 Thinking"
branch: docs/tibia-system-decomposition
base_branch: main
created: 2026-07-14T15:43:00+02:00
updated: 2026-07-14T15:43:00+02:00
last_verified_commit: "21c51174ded78b8f07ff07607a927b66de430246"
risk: low
related_issue: ""
related_pr: ""
depends_on: []
blocks:
  - CAN-20260714-tibia-system-decomposition-engine-persistence
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260714-tibia-system-decomposition-bootstrap.md
    - docs/agents/programs/TIBIA_SYSTEM_DECOMPOSITION_PROGRAM.md
    - docs/agents/real-tibia/TIBIA_SYSTEM_DECOMPOSITION_REPORT.md
    - docs/agents/real-tibia/registry/modules/engine-runtime-lifecycle.yaml
    - docs/agents/real-tibia/registry/modules/configuration.yaml
    - docs/agents/real-tibia/registry/modules/lua-runtime.yaml
  shared:
    - docs/agents/real-tibia/registry/categories.yaml
    - docs/agents/real-tibia/TAXONOMY.md
    - docs/agents/real-tibia/MATURITY_MODEL.md
    - docs/agents/real-tibia/generated/**
    - tools/agents/test_real_tibia_registry.py
    - tools/agents/test_upstream_intelligence.py
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - AGENTS.md
    - docs/agents/README.md
    - docs/agents/ACTIVE_WORK.md
    - docs/agents/REAL_TIBIA_EVIDENCE_SOURCES.md
    - docs/agents/REAL_TIBIA_PARITY_PLAYBOOK.md
    - docs/agents/programs/REAL_TIBIA_PARITY_PROGRAM.md
    - docs/agents/programs/UPSTREAM_INTELLIGENCE_PROGRAM.md
    - docs/agents/programs/E2E_AUTOMATION_PROGRAM.md
    - docs/agents/upstream/**
    - tools/agents/real_tibia_registry.py
    - tools/agents/real_tibia_registry_lib.py
    - tools/agents/upstream_intelligence*.py
    - tools/e2e/**
    - tests/e2e/**
    - src/**
    - data/**
    - tests/**
modules_touched:
  - Real Tibia module registry
  - engine-runtime-lifecycle
  - configuration
  - lua-runtime
  - upstream-intelligence
reuses:
  - Real Tibia registry-as-code
  - existing deterministic registry generator and lookup/affected commands
  - existing Upstream Intelligence path mapper
  - Universal Physical-Client E2E as a shared read-only platform
public_interfaces:
  - Real Tibia module discovery taxonomy
  - logical umbrella/child convention
cross_repo_tasks: []
---

# Goal

Bootstrap a durable logical Tibia/Canary system-decomposition program, classify the full requested candidate inventory, and add one bounded engine-foundation package to the existing Real Tibia registry without changing runtime behavior or creating a parallel registry, watcher, OTBM parser, renderer or E2E platform.

# Acceptance criteria

- [ ] Work is based on current `main` containing PR #331 and lifecycle PR #334.
- [ ] One active task, one architecture program and one draft PR exist on a new branch.
- [ ] Existing registry-as-code remains the sole module source of truth.
- [ ] All 19 existing module records are reviewed and classified.
- [ ] Every requested candidate is classified before any record is added.
- [ ] TSD-001 documents hierarchy, umbrella compatibility, path-discovery and maturity rules.
- [ ] The first package adds only `engine-runtime-lifecycle`, `configuration` and `lua-runtime`.
- [ ] No hierarchy schema field is added unless a concrete generator/mapping need is proven.
- [ ] `depends_on` remains acyclic and relationships stay minimal.
- [ ] Generated indexes are regenerated, deterministic and not hand-edited.
- [ ] Registry and Upstream Intelligence focused tests cover deterministic multi-module mapping.
- [ ] `validate`, `generate --check`, `stale`, representative `module`, `lookup-path` and `affected` checks are recorded.
- [ ] Upstream Intelligence remains a discovery-only, revision-pinned, read-only system; UI-002 is not implemented.
- [ ] `ACTIVE_WORK.md` is unchanged.
- [ ] No C++, Lua gameplay, XML, database, protocol, client, map, datapack, assets or production configuration changes exist.
- [ ] Exact next bounded package and handoff are recorded.
- [ ] Current-head GitHub checks are reviewed before the PR is declared ready.

# Confirmed context

- Writable repository: `blakinio/canary` only.
- Base branch: `main`.
- Exact task-start base: `21c51174ded78b8f07ff07607a927b66de430246`.
- PR #331 merge: `73d1408176ef69abddde475cee5e0642ed4a69e9`.
- PR #334 merge: `21c51174ded78b8f07ff07607a927b66de430246`.
- Current registry contains 19 module records.
- Current module schema has no parent/child field and already permits overlapping path matches.
- `map_candidate()` sorts mapped paths and module IDs, and registry `affected_modules()` sorts/deduplicates results.
- The decomposition is logical metadata and documentation; it is not a physical source-tree refactor.
- The local environment cannot resolve `github.com`; repository reads/writes use the approved GitHub connector and local validation is limited to reconstructed or CI-backed checks.

# Existing work to reuse

| Existing work | Reuse | Boundary |
|---|---|---|
| Real Tibia registry-as-code | module IDs, categories, paths, relationships, maturity, generated indexes | no second registry or generator |
| Upstream Intelligence | changed-path mapping and revision-pinned candidate triage | no watcher changes beyond focused compatibility tests |
| Universal Physical-Client E2E | future module-owned scenarios | platform paths remain read-only |
| OTBM tooling suite | future world-content discovery and validation | no parser, renderer or map changes |
| Real Tibia Parity Program | evidence and proof-level contract | decomposition does not claim parity |
| PR #331/#334 lifecycle | current watcher implementation and archived task state | do not reactivate task or implement UI-002 |

# Ownership and overlap check

- Program record: new `CAN-PROGRAM-TIBIA-SYSTEM-DECOMPOSITION`.
- Open PRs inspected: #316, #308 and #245.
- Active task records inspected for those PRs.
- PR #316 does not claim registry/decomposition paths and treats `MODULE_CATALOG.md` as read-only.
- PR #245 owns universal E2E paths, which remain read-only here.
- PR #308 has a shared claim on `MODULE_CATALOG.md`; this task will make one narrow independent catalogue entry and must rebase/resolve from current `main` before readiness.
- No open PR claims `docs/agents/real-tibia/registry/**`, the new program/report paths or focused registry tests.
- `ACTIVE_WORK.md` is stale convenience data and remains unchanged.
- Local `task_ownership.py` execution is unavailable without a full checkout; CI ownership validation is required.

# Plan

1. Publish this task and architecture program on the dedicated branch.
2. Publish an early draft PR.
3. Add the complete existing-module and candidate classification report.
4. Document umbrella/child, path-discovery, maturity and Oteryn-migration rules.
5. Add the bounded three-record TSD-001 engine-foundation pilot.
6. Regenerate indexes and add focused registry/Upstream Intelligence tests.
7. Run available checks, inspect current-head CI and repair only scope-related failures.
8. Leave the PR as a draft unless all acceptance and CI gates are verified.

# Decisions

| Decision | Reason |
|---|---|
| Keep schema version 1 unchanged | Parent/child metadata has no proven consumer; scope/documentation conventions preserve hierarchy without generator churn. |
| Add an `engine-foundation` category | Existing categories have no accurate navigation home for runtime lifecycle, configuration and Lua technical contracts. |
| Add only three records in TSD-001 | This proves hierarchy and mapping behavior without a giant speculative registry expansion. |
| Preserve broad IDs as umbrella modules | Existing tasks, path lookups and Upstream Intelligence depend on stable discovery identities. |
| Do not encode parenthood through `depends_on` | Dependency semantics are architectural necessity, not taxonomy. |
| Keep all maturity values conservative | File presence and static inventory do not prove runtime, persistence, protocol or E2E behavior. |

# Validation and CI

| Commit/head | Command/check | Result | Notes |
|---|---|---|---|
| pending | `python tools/agents/real_tibia_registry.py validate` | not-run | required |
| pending | `python tools/agents/real_tibia_registry.py generate --check` | not-run | required |
| pending | `python tools/agents/real_tibia_registry.py stale` | not-run | required |
| pending | representative `module` and `lookup-path` commands | not-run | required |
| pending | `affected --base 21c511... --head HEAD` | not-run | required |
| pending | `python -m unittest tools.agents.test_real_tibia_registry tools.agents.test_upstream_intelligence tools.agents.test_upstream_intelligence_hardening` | not-run | required |
| pending | Agent Task Ownership | not-run | CI required |
| pending | current-head required GitHub checks | not-run | no green claim yet |

# Failed approaches and dead ends

- Direct local `git clone` failed because the execution environment could not resolve `github.com`. Per the parity playbook, no repeated clone/fetch loop will be attempted.
- A schema-level `parent` field was considered and rejected for TSD-001 because no current command, generator or watcher requires it.
- A giant first PR containing every candidate was rejected because it would create speculative path hints, relationships and maturity claims.

# Risks and compatibility

- Runtime: none; runtime paths are read-only.
- Data/migration: none.
- Protocol/client: none.
- Upstream mapping: intentional increase in multi-match discovery for exact engine/config/Lua paths; results must remain sorted and hints only.
- Ownership: narrow shared-file conflict risk in `MODULE_CATALOG.md` with PR #308.
- Backward compatibility: existing module IDs and broad path matches remain intact.
- Rollback: revert the documentation/registry commit; no runtime state exists.
- Evidence limitation: TSD-001 inventories implementation locations only and makes no Real Tibia parity claim.

# Remaining work

1. Complete TSD-001 implementation and validation.
2. Review current-head CI.
3. Keep this task active until the draft PR is ready for human review; archive only in a separate lifecycle change after merge.

# Handoff

## Start here

Read this task, `TIBIA_SYSTEM_DECOMPOSITION_PROGRAM.md`, `TIBIA_SYSTEM_DECOMPOSITION_REPORT.md`, the generated module indexes and the current PR diff.

## Do not repeat

- Do not create another registry, hierarchy graph, generator, watcher, OTBM parser/renderer or E2E orchestrator.
- Do not reactivate `CAN-20260714-upstream-intelligence-drift-tracking`.
- Do not implement UI-002.
- Do not physically move `src/**`, `data/**` or `tests/**`.
- Do not promote inventory evidence to parity or runtime proof.

## Exact next bounded package

`CAN-20260714-tibia-system-decomposition-engine-persistence` / `TSD-002`: classify and, only where real paths and long-lived boundaries are proven, add the remaining engine-foundation and persistence records. Start with `engine-scheduler`, `engine-service-container`, `lua-bindings`, `data-registries`, `build-system`, `platform-compatibility`, `database-connection`, `database-migrations`, `transaction-boundaries` and `save-restart-reload`.

# Completion

- Final status: active
- PR: pending
- Final reviewed head: pending
- Merge commit: none
- Program record updated: pending
- Catalogue updated: pending
- Changelog updated: pending
- Archived at: not archived
