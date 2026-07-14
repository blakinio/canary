---
task_id: CAN-20260714-upstream-intelligence-source-role-path-mapping
program_id: CAN-PROGRAM-UPSTREAM-INTELLIGENCE
coordination_id: UPSTREAM-INTELLIGENCE-SOURCE-ROLE-MAPPING
status: active
agent: "GPT-5.6 Thinking"
branch: fix/upstream-intelligence-source-role-path-mapping
base_branch: main
created: 2026-07-14T16:42:00+02:00
updated: 2026-07-14T16:57:00+02:00
last_verified_commit: "e8a86d1b95c0ca88b6ebc992a5f99a38679eac60"
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
  - source registry module_mapping.path_buckets policy
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

# Selected design

The existing Upstream Intelligence source registry now carries one explicit policy per watched source:

```text
module_mapping.path_buckets
```

The existing mapper receives the source record and keeps only matches from those buckets. No repository-name checks are hardcoded in mapping code.

Policy constraints:

- `upstream-server` and `donor-server`: may use `server`, `data`, `tests`, `docs`; never `client`;
- `upstream-client`: may use `client`, `data`, `tests`, `docs`; never `server`;
- `editor`: requires an explicit per-source subset; never `server`;
- unknown role, absent source record or invalid/empty policy: map no buckets and leave changed paths explicitly unmapped;
- no fallback to every bucket.

Editor evidence:

- Remere's Map Editor is map/data tooling whose implementation root uses `source/**`; its policy is `data`, `tests`, `docs` and is not treated as maintained-client code.
- Client Editor patches/repackages Tibia client artifacts and appearances data; its separate policy is `client`, `data`, `tests`, `docs`.

# Acceptance criteria

- [x] Existing source registry is the only mapping-policy registry.
- [x] Every configured source declares allowed path buckets explicitly.
- [x] Server roles cannot consume client buckets.
- [x] Client role cannot consume server buckets.
- [x] Remere's Map Editor and Client Editor have separately justified policies.
- [x] Unknown/unsupported role maps conservatively to no modules and explicit unmapped paths.
- [x] Existing mapper remains discovery-only and deterministic by construction.
- [x] `triage_status: needs-triage` and `decision_state` remain unchanged by mapping.
- [x] One path can still map to several modules inside allowed buckets.
- [x] Focused tests assert both valid matches and absence of invalid matches.
- [x] Source schema and domain validation reject unsafe role/bucket combinations.
- [ ] Upstream Intelligence validation and all focused tests pass.
- [ ] Real Tibia registry validation/generation remain unchanged and pass.
- [ ] Required current-head CI, ownership and review gates pass.
- [x] No module, `protocol.yaml`, gameplay, runtime, protocol implementation, client, DB, map, OTBM, datapack, asset, watcher or E2E change.

# Required focused cases

Covered by `test_upstream_intelligence_source_roles.py` and the actual-registry decomposition regression:

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
14. no client match solely through a server pattern.

# Safety boundary

This task changes discovery policy only. It does not confirm any upstream candidate, alter reviewed decision semantics, create implementation branches, write external repositories, modify Real Tibia module records, or change runtime behavior.

# Handoff

After this feature PR is merged, create a separate lifecycle-only archive PR. Only after that archive merges may TSD-002 start from then-current `main`.
