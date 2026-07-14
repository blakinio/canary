---
task_id: CAN-20260714-upstream-intelligence-source-role-path-mapping
program_id: CAN-PROGRAM-UPSTREAM-INTELLIGENCE
coordination_id: UPSTREAM-INTELLIGENCE-SOURCE-ROLE-MAPPING
status: active
agent: "GPT-5.6 Thinking"
branch: fix/upstream-intelligence-source-role-path-mapping
base_branch: main
created: 2026-07-14T16:42:00+02:00
updated: 2026-07-14T17:10:00+02:00
last_verified_commit: "21e54186cef2825b91222fcf420ec4689fbf10d5"
risk: low
related_issue: ""
related_pr: "337"
depends_on:
  - merged TSD-001 feature PR #335
  - merged TSD-001 lifecycle PR #336
blocks:
  - CAN-20260714-tibia-system-decomposition-engine-persistence
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260714-upstream-intelligence-source-role-path-mapping.md
    - docs/agents/upstream/registry/sources.yaml
    - docs/agents/upstream/schemas/source.schema.json
    - tools/agents/upstream_intelligence_common.py
    - tools/agents/upstream_intelligence_candidates.py
    - tools/agents/upstream_intelligence_scan.py
    - tools/agents/test_upstream_intelligence_source_roles.py
  shared:
    - docs/agents/programs/UPSTREAM_INTELLIGENCE_PROGRAM.md
    - docs/agents/upstream/README.md
    - docs/agents/upstream/SOURCE_WATCH_POLICY.md
    - docs/agents/upstream/TRIAGE_POLICY.md
    - tools/agents/test_upstream_intelligence.py
    - tools/agents/test_upstream_intelligence_decomposition.py
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - AGENTS.md
    - docs/agents/ACTIVE_WORK.md
    - docs/agents/programs/TIBIA_SYSTEM_DECOMPOSITION_PROGRAM.md
    - docs/agents/real-tibia/**
    - tools/agents/real_tibia_registry*.py
    - .github/workflows/upstream-intelligence.yml
    - tools/e2e/**
    - tests/e2e/**
    - src/**
    - data/**
    - tests/**
    - opentibiabr/canary
    - opentibiabr/otclient
    - zimbadev/crystalserver
    - opentibiabr/remeres-map-editor
    - opentibiabr/client-editor
modules_touched:
  - upstream-intelligence
reuses:
  - existing Upstream Intelligence source registry
  - existing Upstream Intelligence mapper
  - existing Real Tibia registry path buckets
public_interfaces:
  - source registry v2 module_mapping.path_buckets policy
  - source-aware map_candidate contract
cross_repo_tasks: []
---

# Goal

Make the existing Upstream Intelligence module mapper source-role-aware so external paths are matched only against explicitly allowed Real Tibia registry path buckets, without changing module records, creating another mapper or promoting discovery results to defect or parity conclusions.

# Base and preflight

- Exact task-start main: `cc8b3bdc9b34fb8e6802bd1a0fc0d535de2dd9ba`.
- PR #335 merged as `44fe3af9f29b3ae0164ac5d60fc1f14137b5cea5`.
- Lifecycle PR #336 merged as task-start main `cc8b3bdc9b34fb8e6802bd1a0fc0d535de2dd9ba`.
- Open PRs inspected: #316, #308 and #245.
- None claims `docs/agents/upstream/**` or `tools/agents/upstream_intelligence*.py`.
- `ACTIVE_WORK.md` remains read-only.

# Confirmed defect

`map_candidate()` previously called `Registry.matched_modules(path)` without source context. `matched_modules()` searches every bucket (`server`, `client`, `data`, `tests`, `docs`). Therefore a server path such as `src/canary_server.cpp` could match the broad client pattern `src/**` in `protocol.yaml`.

PR #335 removed the incorrect test expectation but intentionally did not change the mapper or `protocol.yaml`.

# Delivered design

The existing Upstream Intelligence source registry was upgraded atomically to schema version 2 and now carries one explicit policy per watched source:

```text
module_mapping.path_buckets
```

The existing mapper receives the configured source record and keeps only matches from those buckets. No repository-name checks are hardcoded in mapping code, no second registry or mapper exists, and the Real Tibia registry API remains unchanged.

Policy constraints:

- `upstream-server` and `donor-server`: `server`, `data`, `tests`, `docs`; never `client`;
- `upstream-client`: `client`, `data`, `tests`, `docs`; never `server`;
- `editor`: explicit per-source subset of `client`, `data`, `tests`, `docs`; never `server`;
- unknown role, absent source record or invalid/empty policy: no allowed buckets and explicit unmapped paths;
- no fallback to every bucket.

Editor evidence:

- Remere's Map Editor is map/data tooling whose implementation root uses `source/**`; its policy is `data`, `tests`, `docs` and is not treated as maintained-client code.
- Client Editor patches/repackages Tibia client artifacts and appearances data; its separate policy is `client`, `data`, `tests`, `docs`.

# Acceptance criteria

- [x] Existing source registry is the only mapping-policy registry.
- [x] Every configured source declares allowed path buckets explicitly.
- [x] Source registry format is versioned as schema v2.
- [x] Server roles cannot consume client buckets.
- [x] Client role cannot consume server buckets.
- [x] Remere's Map Editor and Client Editor have separately justified policies.
- [x] Unknown/unsupported role maps conservatively to no modules and explicit unmapped paths.
- [x] Existing mapper remains discovery-only and deterministic.
- [x] `triage_status: needs-triage` and `decision_state` remain unchanged by mapping.
- [x] One path can still map to several modules inside allowed buckets.
- [x] Focused tests assert both valid matches and absence of invalid matches.
- [x] Source schema and domain validation reject unsafe role/bucket combinations.
- [x] Upstream Intelligence focused tests, source validation and Real Tibia registry integration passed on implementation head `9820615f76d9892f645b21748feaa610cafe78f1` in run #122.
- [ ] Required current-head CI, ownership and review gates pass on the final live PR head.
- [x] No module, `protocol.yaml`, gameplay, runtime, protocol implementation, client, DB, map, OTBM, datapack, asset, watcher or E2E change.

# Focused test matrix

Covered by `test_upstream_intelligence_source_roles.py`, the actual-registry decomposition regression and existing scan tests:

1. `upstream-server`;
2. `donor-server`;
3. `upstream-client`;
4. `opentibiabr-rme`;
5. `opentibiabr-client-editor`;
6. unknown/unsupported role and absent source record;
7. multiple valid modules in one allowed bucket;
8. deterministic `module_ids` sorting;
9. deterministic `mapped_paths` sorting;
10. explicit `unmapped_paths`;
11. preserved `triage_status: needs-triage`;
12. preserved `decision_state`;
13. no server match solely through client `src/**`;
14. no client match solely through a server pattern;
15. source validation rejects a server role configured with the client bucket;
16. full scan passes the exact configured source record into the mapper.

# Validation history

- First complete functional/docs head `9820615f76d9892f645b21748feaa610cafe78f1`:
  - Upstream Intelligence #122: success;
  - focused tests: success;
  - source registry and decisions validation: success;
  - Real Tibia registry `validate` and `generate --check`: success;
  - Agent Task Ownership #949: success.
- Source registry was then explicitly versioned from v1 to v2 because the required `module_mapping` field changes the source-format contract.
- Exact final task-record commit cannot be embedded in itself; live PR #337 metadata and current-head workflows are authoritative for readiness and merge.

# Scope review

Allowed implementation/configuration paths:

- existing source registry and its source schema;
- existing mapper/common/scan modules;
- focused Upstream Intelligence tests;
- source watch, triage, program, catalogue, changelog and task documentation.

Explicitly unchanged:

- Real Tibia module records, categories, schemas, generator and generated indexes;
- `protocol.yaml`;
- Upstream Intelligence workflow and watcher collection behavior;
- candidate and snapshot schemas;
- gameplay/runtime/C++/Lua/protocol implementation/client/DB/map/OTBM/datapack/assets/E2E;
- external repositories and `ACTIVE_WORK.md`.

# Known limitations

- Bucket policy assumes external paths are meaningfully comparable to the corresponding local server/client/data/test/doc namespace; non-corresponding editor paths remain unmapped rather than guessed.
- Mapping remains path-based discovery and cannot establish semantic equivalence, a local defect, compatibility, ownership or parity.
- Source policy changes require an explicit source-registry update and validation; there is no heuristic repository-name fallback.

# Handoff

After PR #337 passes exact current-head checks, review threads and changed-file scope, mark ready and squash merge. Then create a separate lifecycle-only archive PR for this task. Only after that archive merges may TSD-002 start from then-current `main`.
