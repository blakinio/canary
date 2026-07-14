---
task_id: CAN-20260714-tibia-system-decomposition-bootstrap
program_id: CAN-PROGRAM-TIBIA-SYSTEM-DECOMPOSITION
coordination_id: REAL-TIBIA-SYSTEM-DECOMPOSITION
status: active
agent: "GPT-5.6 Thinking"
branch: docs/tibia-system-decomposition
base_branch: main
created: 2026-07-14T15:43:00+02:00
updated: 2026-07-14T16:23:00+02:00
last_verified_commit: "4e1493dee36eca1b413ad64077480b3f76fa4587"
risk: low
related_issue: ""
related_pr: "335"
depends_on: []
blocks:
  - CAN-20260714-tibia-system-decomposition-engine-persistence
  - CAN-20260714-upstream-intelligence-source-role-path-mapping
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

Bootstrap a durable logical Tibia/Canary system-decomposition program, classify the requested candidate inventory, and add one bounded engine-foundation package to the existing Real Tibia registry without changing runtime behavior or creating a parallel registry, watcher, mapper, OTBM parser, renderer or E2E platform.

# Acceptance criteria

- [x] Work is based on `main@21c51174ded78b8f07ff07607a927b66de430246`, containing PR #331 and lifecycle PR #334.
- [x] Existing registry-as-code remains the sole module source of truth.
- [x] All 19 pre-existing module records were reviewed and all requested candidates classified.
- [x] TSD-001 adds only `engine-runtime-lifecycle`, `configuration` and `lua-runtime`.
- [x] No schema, generator, mapper or `protocol.yaml` change is included.
- [x] Generated indexes match deterministic generator output.
- [x] Upstream Intelligence focused coverage keeps deterministic ordering, required TSD-001 modules and `triage_status: needs-triage`.
- [x] The focused test does not require server paths to map to `protocol` through the broad client `src/**` glob.
- [x] The source-role-aware mapping defect is recorded as a separate planned follow-up task.
- [x] `ACTIVE_WORK.md` remains unchanged.
- [x] No gameplay/runtime, Lua gameplay, XML, database, protocol implementation, client, map, datapack, asset or production configuration change exists.
- [x] TSD-002 is not started.
- [ ] Exact current-head GitHub checks are green and PR #335 is marked ready for review.

# Commit and review heads

These commits have different roles and must not be conflated:

| Role | Commit | Meaning |
|---|---|---|
| Original implementation-reviewed head | `a8e6ae56b8b74e6b392a933f4e1d22ce63ff6a6d` | First complete implementation review and CI evidence. |
| Documentation-only consolidation head | `0b213fa306b2ad1f7569fc32b983f08a1f02f244` | Later documentation/evidence consolidation; no runtime or mapper change. |
| Review-fix functional head | `4e1493dee36eca1b413ad64077480b3f76fa4587` | Removes the `protocol` expectation from the focused test and adds the configuration path assertion. |
| Final reviewed PR head | Live PR #335 head after this task-record-only commit | GitHub PR metadata is authoritative for the exact self-referential final commit SHA; it must have green current-head CI before readiness. |

The task record cannot embed the SHA of the commit that contains itself. Therefore `last_verified_commit` records the final functional/test head, while the exact final documentation-only PR head and its checks are recorded in live PR metadata and the final handoff.

# Confirmed result

- Registry grew from 19 to 22 records.
- Added category: `engine-foundation`.
- Added records: `engine-runtime-lifecycle`, `configuration`, `lua-runtime`.
- Existing broad umbrella IDs remain intact.
- Schema version 1 and generator behavior remain unchanged.
- The decomposition is logical metadata and documentation, not a physical source-tree refactor.
- The PR-range affected set remains:

```text
configuration
engine-runtime-lifecycle
lua-runtime
```

# Focused Upstream Intelligence test contract

`tools/agents/test_upstream_intelligence_decomposition.py` now proves:

- `module_ids` are deterministically sorted;
- `mapped_paths` are deterministically sorted by path, module, bucket and pattern;
- `engine-runtime-lifecycle` is present for `src/canary_server.cpp`;
- `configuration` is present for `src/config/configmanager.cpp`;
- `lua-runtime` is present for `src/lua/scripts/lua_environment.hpp`;
- `triage_status` remains `needs-triage`;
- no assertion requires `protocol` to be present for server paths.

The current mapper may still emit `protocol` for those paths because `protocol.yaml` contains a broad client `src/**` bucket. TSD-001 does not declare that output correct and does not change the mapper or record.

# Separate follow-up finding/task

## `CAN-20260714-upstream-intelligence-source-role-path-mapping`

Status: **planned finding only; not started by PR #335**.

Finding:

- the existing path mapper is source-unaware;
- server source candidates can incorrectly consume general client path buckets such as `src/**`;
- client source candidates should use client path buckets;
- server source candidates should not automatically use generic client buckets.

Required boundaries for the future task:

- reuse the existing Real Tibia registry and Upstream Intelligence mapper;
- remain discovery-only;
- do not change triage into a confirmed defect, parity claim or edit authorization;
- add focused deterministic tests for server-only, client-only and mixed-source candidates;
- preserve `triage_status: needs-triage`;
- do not solve the problem by opportunistically restructuring `protocol.yaml` without separate evidence;
- add no modules and make no runtime, protocol implementation, client, map, data, asset or E2E change.

This finding is independent from TSD-002 and does not authorize starting either task.

# Validation history

Earlier complete evidence:

| Head | Workflow | Result |
|---|---|---|
| `a8e6ae56b8b74e6b392a933f4e1d22ce63ff6a6d` | Real Tibia Module Registry #103 | PASS |
| `a8e6ae56b8b74e6b392a933f4e1d22ce63ff6a6d` | Upstream Intelligence #92 | PASS |
| `a8e6ae56b8b74e6b392a933f4e1d22ce63ff6a6d` | Agent Task Ownership #926 | PASS |
| `a8e6ae56b8b74e6b392a933f4e1d22ce63ff6a6d` | repository CI #2035 | PASS |
| `0b213fa306b2ad1f7569fc32b983f08a1f02f244` | Real Tibia Module Registry #104 | PASS |
| `0b213fa306b2ad1f7569fc32b983f08a1f02f244` | Upstream Intelligence #93 | PASS |
| `0b213fa306b2ad1f7569fc32b983f08a1f02f244` | Agent Task Ownership #927 | PASS |
| `0b213fa306b2ad1f7569fc32b983f08a1f02f244` | repository CI #2036 | PASS |

Readiness requires fresh successful runs of the same four required workflows on the exact live final PR head after this task-record-only update. Live GitHub check data is authoritative for those run IDs and conclusions.

# Risks and compatibility

- Runtime: none; runtime paths remain read-only.
- Data/migration: none.
- Protocol/client implementation: none.
- Mapping: the known source-role defect remains unresolved by design; it is no longer asserted as expected behavior.
- Backward compatibility: all 19 pre-existing module IDs and records remain intact.
- Rollback: revert this documentation/registry PR; no runtime state exists.
- Evidence limitation: TSD-001 inventories implementation locations only and proves no parity, persistence safety, wire compatibility, runtime behavior or physical-client E2E behavior.

# Remaining work

1. Verify Real Tibia Module Registry, Upstream Intelligence, Agent Task Ownership and required repository CI on the exact final PR head.
2. Mark PR #335 ready for review only after all required current-head checks are green.
3. Do not merge as part of this review-fix request.
4. Archive this active task only in a separate lifecycle-only change after merge.
5. Do not start TSD-002 or the source-role-aware mapping follow-up from this PR.

# Completion

- Final status: active; implementation and requested review fix complete, awaiting exact current-head CI/readiness transition.
- PR: #335; live PR metadata is authoritative for draft/ready state.
- Final functional/test head: `4e1493dee36eca1b413ad64077480b3f76fa4587`.
- Final documentation-only head: the commit containing this record; exact SHA must be taken from live PR #335 metadata.
- Merge commit: none.
- Program record updated: yes.
- Catalogue updated: yes.
- Changelog updated: yes.
- Archived at: not archived; archive only after merge.
