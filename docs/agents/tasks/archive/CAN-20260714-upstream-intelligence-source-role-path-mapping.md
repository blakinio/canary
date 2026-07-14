---
task_id: CAN-20260714-upstream-intelligence-source-role-path-mapping
program_id: CAN-PROGRAM-UPSTREAM-INTELLIGENCE
coordination_id: UPSTREAM-INTELLIGENCE-SOURCE-ROLE-MAPPING
status: merged
agent: "GPT-5.6 Thinking"
branch: fix/upstream-intelligence-source-role-path-mapping
base_branch: main
created: 2026-07-14T16:42:00+02:00
updated: 2026-07-14T17:19:27+02:00
last_verified_commit: "09f7049401253dd38c8f34506946c2fbe287d220"
risk: low
related_issue: ""
related_pr: "#337"
depends_on:
  - merged TSD-001 feature PR #335
  - merged TSD-001 lifecycle PR #336
blocks:
  - CAN-20260714-tibia-system-decomposition-engine-persistence
owned_paths:
  exclusive:
    - docs/agents/tasks/archive/CAN-20260714-upstream-intelligence-source-role-path-mapping.md
    - docs/agents/programs/UPSTREAM_INTELLIGENCE_PROGRAM.md
    - docs/agents/programs/TIBIA_SYSTEM_DECOMPOSITION_PROGRAM.md
  shared: []
  read_only:
    - docs/agents/ACTIVE_WORK.md
    - docs/agents/upstream/**
    - docs/agents/real-tibia/**
    - tools/agents/**
    - .github/workflows/**
    - src/**
    - data/**
    - tests/**
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

# Final result

PR #337 completed UI-001A and was squash-merged on 2026-07-14 at `15:19:27Z`.

- Task-start base: `cc8b3bdc9b34fb8e6802bd1a0fc0d535de2dd9ba`.
- Final feature head: `f8a501a3362ae42079e899b03848a606f7224626`.
- Squash merge SHA: `09f7049401253dd38c8f34506946c2fbe287d220`.
- Pull request: #337.
- Changed files: 15.
- Registry modules added: 0.
- Registry modules modified: 0.
- Real Tibia registry schema/generator/generated indexes changed: no.
- `protocol.yaml` changed: no.
- Runtime/gameplay/client/database/map/OTBM/datapack/assets changed: no.

# Delivered contract

The existing source registry was upgraded to schema version 2 and now requires:

```text
module_mapping.path_buckets
```

Per-source policies:

- `opentibiabr-canary`: `server`, `data`, `tests`, `docs`;
- `crystalserver`: `server`, `data`, `tests`, `docs`;
- `opentibiabr-otclient`: `client`, `data`, `tests`, `docs`;
- `opentibiabr-rme`: `data`, `tests`, `docs`;
- `opentibiabr-client-editor`: `client`, `data`, `tests`, `docs`.

The existing mapper receives the exact source record and filters matches to allowed buckets. Missing, invalid or unsupported source context maps no modules and preserves explicit `unmapped_paths`; there is no fallback to all buckets.

# Review and validation history

## Functional implementation head

`9820615f76d9892f645b21748feaa610cafe78f1`

- Upstream Intelligence #122: success;
- focused tests: success;
- source registry/decision validation: success;
- Real Tibia registry `validate` and `generate --check`: success;
- Agent Task Ownership #949: success.

## Reviewed implementation/docs head

`2ddf83161a358a72bf4a9f37d2747fd2acd4f31b`

- Upstream Intelligence #128: success;
- Agent Task Ownership #953: success;
- repository CI #2063: success;
- 15 changed files, all inside the declared task scope.

## Final feature head

`f8a501a3362ae42079e899b03848a606f7224626`

- Upstream Intelligence #129: success;
- Agent Task Ownership #954: success;
- repository CI #2064: success;
- ready-state repository CI #2065: success;
- ready-state Lua Tests: success;
- ready-state Fast Checks: success;
- ready-state Linux release: success;
- ready-state Required: success;
- PR comments: none;
- submitted reviews requesting changes: none;
- unresolved review threads: none;
- mergeable before merge: yes;
- exact-head merge guard used.

# Focused regression coverage

1. `upstream-server`;
2. `donor-server`;
3. `upstream-client`;
4. Remere's Map Editor policy;
5. Client Editor policy;
6. unknown/unsupported role;
7. absent source record;
8. multiple valid modules in an allowed bucket;
9. deterministic `module_ids`;
10. deterministic `mapped_paths`;
11. explicit `unmapped_paths`;
12. preserved `triage_status: needs-triage`;
13. preserved `decision_state`;
14. no server match solely through client `src/**`;
15. no client match solely through server patterns;
16. role-incompatible source policy rejection;
17. full scan passes the configured source record into the mapper;
18. actual registry mapping retains `engine-runtime-lifecycle`, `configuration` and `lua-runtime` while excluding `protocol` for server paths.

# Safety boundary confirmed

- one source registry;
- one mapper;
- one watcher;
- discovery-only behavior;
- no automatic branch/cherry-pick/implementation;
- no candidate promotion to confirmed defect;
- no parity/equivalence/ownership claim;
- reviewed decisions remain revision-pinned;
- external repositories remain read-only;
- no `ACTIVE_WORK.md` change;
- no gameplay/runtime/C++/Lua/protocol implementation/client/DB/map/OTBM/datapack/asset/E2E change.

# Known limitations

- Mapping remains path-based discovery and does not establish semantic equivalence, compatibility, ownership, a local defect or parity.
- Editor paths without a justified local namespace remain explicitly unmapped rather than guessed.
- Future policy changes require an explicit source-registry update and validation; no repository-name heuristic exists.

# Next exact task

```text
task: CAN-20260714-tibia-system-decomposition-engine-persistence
program: CAN-PROGRAM-TIBIA-SYSTEM-DECOMPOSITION
package: TSD-002
branch: docs/tibia-system-decomposition-engine-persistence
```

Start only after this lifecycle archive PR is merged and current `main` is re-read.

# Completion

- Final status: merged.
- Feature PR: #337.
- Feature head: `f8a501a3362ae42079e899b03848a606f7224626`.
- Merge commit: `09f7049401253dd38c8f34506946c2fbe287d220`.
- Merged at: `2026-07-14T15:19:27Z`.
- Archived at: `docs/agents/tasks/archive/CAN-20260714-upstream-intelligence-source-role-path-mapping.md`.
