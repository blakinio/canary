---
task_id: CAN-20260714-tibia-system-decomposition-bootstrap
program_id: CAN-PROGRAM-TIBIA-SYSTEM-DECOMPOSITION
coordination_id: REAL-TIBIA-SYSTEM-DECOMPOSITION
status: active
agent: "GPT-5.6 Thinking"
branch: docs/tibia-system-decomposition
base_branch: main
created: 2026-07-14T15:43:00+02:00
updated: 2026-07-14T16:10:00+02:00
last_verified_commit: "a8e6ae56b8b74e6b392a933f4e1d22ce63ff6a6d"
risk: low
related_issue: ""
related_pr: "335"
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
    - tools/agents/test_upstream_intelligence_decomposition.py
  shared:
    - docs/agents/real-tibia/registry/categories.yaml
    - docs/agents/real-tibia/TAXONOMY.md
    - docs/agents/real-tibia/MATURITY_MODEL.md
    - docs/agents/real-tibia/generated/**
    - tools/agents/test_real_tibia_registry.py
    - .github/workflows/real-tibia-registry.yml
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

- [x] Work is based on current `main` containing PR #331 and lifecycle PR #334.
- [x] One active task, one architecture program and one draft PR exist on a new branch.
- [x] Existing registry-as-code remains the sole module source of truth.
- [x] All 19 existing module records are reviewed and classified.
- [x] Every requested candidate is classified before a record is selected for TSD-001.
- [x] TSD-001 documents hierarchy, umbrella compatibility, path-discovery and maturity rules.
- [x] The first package adds only `engine-runtime-lifecycle`, `configuration` and `lua-runtime`.
- [x] No hierarchy schema field is added because no concrete generator/mapping need was proven.
- [x] `depends_on` remains acyclic and relationships stay minimal.
- [x] Generated indexes match deterministic generator output and `generate --check` passes.
- [x] Registry and Upstream Intelligence focused tests cover deterministic multi-module mapping.
- [x] `validate`, `generate --check`, `stale`, representative `module`, `lookup-path` and `affected` checks are recorded.
- [x] Upstream Intelligence remains a discovery-only, revision-pinned, read-only system; UI-002 is not implemented.
- [x] `ACTIVE_WORK.md` is unchanged.
- [x] No C++, Lua gameplay, XML, database, protocol, client, map, datapack, assets or production configuration changes exist.
- [x] Exact next bounded package and handoff are recorded.
- [x] Current-head GitHub checks were reviewed before the draft was declared ready for human review.

# Confirmed context

- Writable repository: `blakinio/canary` only.
- Base branch: `main`.
- Exact task-start and current base: `21c51174ded78b8f07ff07607a927b66de430246`.
- PR #331 merge: `73d1408176ef69abddde475cee5e0642ed4a69e9`.
- PR #334 merge: `21c51174ded78b8f07ff07607a927b66de430246`.
- Registry grew from 19 to 22 module records.
- Current module schema has no parent/child field and already permits overlapping path matches.
- `map_candidate()` sorts mapped paths and module IDs, and registry `affected_modules()` sorts/deduplicates results.
- The decomposition is logical metadata and documentation; it is not a physical source-tree refactor.
- The local environment could not resolve `github.com`; repository reads/writes used the approved GitHub connector and executable validation used repository CI.

# Existing work reused

| Existing work | Reuse | Boundary |
|---|---|---|
| Real Tibia registry-as-code | module IDs, categories, paths, relationships, maturity, generated indexes | no second registry or generator |
| Upstream Intelligence | changed-path mapping and revision-pinned candidate triage | no watcher implementation change; focused compatibility test only |
| Universal Physical-Client E2E | future module-owned scenarios | platform paths remained read-only |
| OTBM tooling suite | future world-content discovery and validation | no parser, renderer or map changes |
| Real Tibia Parity Program | evidence and proof-level contract | decomposition makes no parity claim |
| PR #331/#334 lifecycle | current watcher implementation and archived task state | archived task remained archived; UI-002 excluded |

# Ownership and overlap check

- Open PRs inspected at task start: #316, #308 and #245.
- PR #316 does not claim registry/decomposition paths and treats `MODULE_CATALOG.md` as read-only.
- PR #245 owns universal E2E paths, which remained read-only here.
- PR #308 has a shared claim on `MODULE_CATALOG.md`; this task added one narrow independent catalogue row.
- No open PR claimed `docs/agents/real-tibia/registry/**`, the new program/report paths or focused registry tests.
- Agent Task Ownership run #926 passed on reviewed head `a8e6ae56b8b74e6b392a933f4e1d22ce63ff6a6d`.
- `ACTIVE_WORK.md` was not modified.

# Delivered TSD-001

1. Created program `CAN-PROGRAM-TIBIA-SYSTEM-DECOMPOSITION` and bounded package queue TSD-001 through TSD-013.
2. Reviewed all 19 existing records and preserved every current ID.
3. Classified 302 candidate mentions, consolidated into 294 unique candidates.
4. Preserved `combat`, `cyclopedia`, `market`, `prey`, `protocol`, `quests` and `spawns` as umbrella/discovery compatibility modules.
5. Added the `engine-foundation` category and three records: `engine-runtime-lifecycle`, `configuration`, `lua-runtime`.
6. Kept schema version 1 unchanged and documented hierarchy as a convention, not a fake dependency graph.
7. Regenerated the four affected generated indexes and preserved `SOURCE_INDEX.md` unchanged.
8. Added focused registry and Upstream Intelligence multi-match tests.
9. Extended the existing registry workflow to exercise the new modules, paths and PR-range `affected` command.
10. Updated taxonomy, maturity guidance, module catalogue and changelog.

# Decisions

| Decision | Reason |
|---|---|
| Keep schema version 1 unchanged | Parent/child metadata has no proven consumer; scope/documentation conventions preserve hierarchy without generator churn. |
| Add an `engine-foundation` category | Existing categories had no accurate navigation home for runtime lifecycle, configuration and Lua technical contracts. |
| Add only three records in TSD-001 | This proves hierarchy and mapping behavior without a giant speculative registry expansion. |
| Preserve broad IDs as umbrella modules | Existing tasks, path lookups and Upstream Intelligence depend on stable discovery identities. |
| Do not encode parenthood through `depends_on` | Dependency semantics are architectural necessity, not taxonomy. |
| Keep all maturity values conservative | File presence and static inventory do not prove runtime, persistence, protocol or E2E behavior. |

# Validation and CI

Reviewed head: `a8e6ae56b8b74e6b392a933f4e1d22ce63ff6a6d`.

| Command/check | Result | Evidence |
|---|---|---|
| `python tools/agents/real_tibia_registry.py validate` | PASS | Real Tibia Module Registry run #103, step `Validate registry contracts` |
| `python tools/agents/real_tibia_registry.py generate --check` | PASS | run #103, step `Verify generated indexes are current` |
| `python tools/agents/real_tibia_registry.py stale --as-of 2026-08-15` | PASS | run #103, step `Exercise discovery commands` |
| representative `module` commands for Wheel and all three TSD-001 records | PASS | run #103, step `Exercise discovery commands` |
| representative `lookup-path` commands for protocol, lifecycle, configuration and Lua paths | PASS | run #103, step `Exercise discovery commands` |
| `affected --base 21c51174ded78b8f07ff07607a927b66de430246 --head a8e6ae56b8b74e6b392a933f4e1d22ce63ff6a6d` | PASS | run #103, step `Exercise affected modules` |
| `python -m unittest -v tools/agents/test_real_tibia_registry.py` | PASS | run #103, focused tests |
| `PYTHONPATH=tools/agents python -m unittest discover -v -s tools/agents -p 'test_upstream_intelligence*.py'` | PASS | Upstream Intelligence run #92 |
| Upstream registry/decision validation and Real Tibia registry integration | PASS | Upstream Intelligence run #92 |
| Agent Task Ownership | PASS | run #926 |
| repository CI | PASS | CI run #2035 |

Representative deterministic lookup results:

```text
src/canary_server.cpp
  engine-runtime-lifecycle  server  src/canary_server.*
  protocol                  client  src/**

src/config/configmanager.cpp
  configuration  server  src/config/**
  protocol       client  src/**

src/lua/scripts/lua_environment.hpp
  lua-runtime  server  src/lua/**
  protocol     client  src/**
```

The PR-range `affected` result is the sorted set:

```text
configuration
engine-runtime-lifecycle
lua-runtime
```

# Failed approaches and repairs

- Direct local `git clone` failed because the execution environment could not resolve `github.com`. Per the parity playbook, no repeated clone/fetch loop was attempted.
- A schema-level `parent` field was considered and rejected because no current command, generator or watcher needs it.
- A giant first PR containing every candidate was rejected because it would create speculative path hints, relationships and maturity claims.
- Initial records used unsupported freshness class `standard`; schema CI rejected it. All three were corrected to the existing `medium` enum and validation then passed.
- An initial standalone mixed test file was removed; coverage was consolidated into the existing registry test and an automatically discovered Upstream Intelligence focused test.

# Risks and compatibility

- Runtime: none; runtime paths are read-only.
- Data/migration: none.
- Protocol/client: none.
- Upstream mapping: intentional increase in multi-match discovery for exact engine/config/Lua paths; sorted results remain hints only.
- Ownership: narrow shared-file conflict risk in `MODULE_CATALOG.md` with PR #308; current main remained unchanged during final verification.
- Backward compatibility: all 19 existing module IDs and broad path matches remain intact.
- Rollback: revert the documentation/registry PR; no runtime state exists.
- Evidence limitation: TSD-001 inventories implementation locations only and makes no Real Tibia parity claim.

# Remaining work

1. Human review and merge of draft PR #335.
2. Archive this active task only in a separate lifecycle-only change after merge.
3. Start TSD-002 only after re-fetching the then-current main, PRs and task ownership.

# Handoff

## Start here

Read this task, `TIBIA_SYSTEM_DECOMPOSITION_PROGRAM.md`, `TIBIA_SYSTEM_DECOMPOSITION_REPORT.md`, the generated module indexes and PR #335 diff.

## Do not repeat

- Do not create another registry, hierarchy graph, generator, watcher, OTBM parser/renderer or E2E orchestrator.
- Do not reactivate `CAN-20260714-upstream-intelligence-drift-tracking`.
- Do not implement UI-002.
- Do not physically move `src/**`, `data/**` or `tests/**`.
- Do not promote inventory evidence to parity or runtime proof.
- Do not add every deferred candidate merely because it appears in the report.

## Exact next bounded package

`CAN-20260714-tibia-system-decomposition-engine-persistence` / `TSD-002`: classify and, only where real paths and long-lived boundaries are proven, add the remaining engine-foundation and persistence records. Start with `engine-scheduler`, `engine-service-container`, `lua-bindings`, `data-registries`, `build-system`, `platform-compatibility`, `database-connection`, `database-migrations`, `transaction-boundaries` and `save-restart-reload`.

# Completion

- Final status: active; implementation complete, awaiting human review/merge.
- PR: #335 (draft).
- Final reviewed implementation head: `a8e6ae56b8b74e6b392a933f4e1d22ce63ff6a6d`.
- Merge commit: none.
- Program record updated: yes.
- Catalogue updated: yes.
- Changelog updated: yes.
- Archived at: not archived; archive only after merge.
