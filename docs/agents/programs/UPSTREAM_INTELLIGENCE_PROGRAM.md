---
program_id: CAN-PROGRAM-UPSTREAM-INTELLIGENCE
name: Upstream Intelligence and Drift Tracking
status: active
owner: repository-wide
created: 2026-07-14T13:20:00+02:00
updated: 2026-07-14T17:02:00+02:00
last_verified_commit: "cc8b3bdc9b34fb8e6802bd1a0fc0d535de2dd9ba"
primary_paths:
  - docs/agents/upstream/**
  - tools/agents/upstream_intelligence*.py
  - .github/workflows/upstream-intelligence.yml
shared_integration_paths:
  - docs/agents/real-tibia/**
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/CHANGELOG.md
related_programs:
  - CAN-PROGRAM-REAL-TIBIA-PARITY
  - CAN-PROGRAM-CRYSTALSERVER-COMPARISON
  - CAN-PROGRAM-TIBIA-SYSTEM-DECOMPOSITION
cross_repo_contracts: []
---

# Mission

Continuously surface relevant changes from selected OpenTibiaBR and CrystalServer repositories, compare them conservatively with the local fork, and preserve reviewed adoption decisions without automatically importing code.

# Watched sources

| Source | Role | Mapping policy | Initial baseline |
|---|---|---|---|
| `opentibiabr/canary` | upstream server | `server`, `data`, `tests`, `docs` | `a879c9312e34381e8eedf397b8ed44510698b689` |
| `opentibiabr/otclient` | upstream client | `client`, `data`, `tests`, `docs` | `bdea0b23b4a738809d698cb7e4f88a299dd6bffc` |
| `zimbadev/crystalserver` | donor server | `server`, `data`, `tests`, `docs` | `fc0d53b9f9965463b6082c07e6d3d482294541a7` |
| `opentibiabr/remeres-map-editor` | editor/tooling | `data`, `tests`, `docs` | `57ee0e5b915909f207aa7a60968c8ed6e4f7f406` |
| `opentibiabr/client-editor` | editor/tooling | `client`, `data`, `tests`, `docs` | `405f88343a33289ad06ba7749892ee91258925a2` |

All baselines are historical task-start observations. Every run re-fetches live heads.

Mapping policies live in the existing source registry. They select permitted Real Tibia path buckets for discovery only; they are not ownership, correctness, parity or import authority.

# Operating model

```text
scheduled/API-triggered scan
        |
        v
bounded candidate inventory
        |
        v
source-policy-filtered module mapping + local exact/reference evidence
        |
        v
stable report issue + artifacts
        |
        v
human/agent reviewed decision
        |
        v
optional bounded local task and PR
```

# Required invariants

- watched repositories remain read-only;
- report automation may update only the stable issue in `blakinio/canary`;
- no automatic cherry-pick, implementation branch or gameplay edit;
- issues are signals, not confirmed bugs;
- CrystalServer is never official-behavior authority;
- path mapping is discovery, not ownership;
- source roles and explicit source mapping policies restrict eligible path buckets;
- missing or unsupported source policy never falls back to all path buckets;
- mapping never changes `triage_status` or `decision_state`;
- exact ancestry is not semantic equivalence;
- stale decisions are not reused silently;
- all implementation still uses one bounded task and normal CI.

# Program queue

| ID | Scope | Status | Evidence baseline | Exact next action |
|---|---|---|---|---|
| UI-001 | Read-only source registry, schemas, scanner, reports, workflow and policies | merged | PR #331; feature head `f9a159a0ba55aca047160c77dea017549c69512f`; merge `73d1408176ef69abddde475cee5e0642ed4a69e9` | preserve contracts; do not reopen the feature branch |
| UI-001A | Source-role-aware module path mapping | active | TSD-001 finding; `main@cc8b3bdc9b34fb8e6802bd1a0fc0d535de2dd9ba`; PR #337 | finish focused positive/negative tests, current-head CI, squash merge and lifecycle archive |
| UI-002 | First production scan and report-issue verification | planned | merged UI-001 plus UI-001A mapping policy | verify the next scheduled or manually dispatched `main` scan, immutable artifact and stable report issue |
| UI-003 | Reviewed candidate bootstrap | blocked-by-UI-002 | first valid deep snapshot | triage only high/urgent candidates into revision-pinned decisions |
| UI-004 | Patch-equivalence research | planned | proven need after several scans | design separately; do not infer equivalence from commit count |
| UI-005 | Release-gap dashboard | planned | stable candidate history | add only after the watcher proves useful and bounded |

# Delivery evidence

UI-001 was delivered by task `CAN-20260714-upstream-intelligence-drift-tracking` and PR #331.

- final feature head: `f9a159a0ba55aca047160c77dea017549c69512f`;
- squash merge: `73d1408176ef69abddde475cee5e0642ed4a69e9`;
- Upstream Intelligence run `29334363187`, job `87089794471`: success;
- ready-state CI run `29334504937`: success;
- Lua Tests `87090270716`, Fast Checks `87090270745`, Linux release `87090597075`, Required `87092023511`: success;
- archived task: `docs/agents/tasks/archive/CAN-20260714-upstream-intelligence-drift-tracking.md`.

# Current active task

`CAN-20260714-upstream-intelligence-source-role-path-mapping` / PR #337.

The task repairs only discovery mapping:

- keep one source registry and one mapper;
- configure explicit bucket policies per source;
- reject role-incompatible policies;
- keep unsupported or missing source context explicitly unmapped;
- preserve deterministic output, `needs-triage`, decision state and external read-only boundaries;
- add no modules and do not change `protocol.yaml` or runtime.

The task blocks TSD-002 until both its feature and lifecycle PRs are merged.

# Handoff

Finish PR #337 from its exact live head. Validate all Upstream Intelligence tests, source schema, Real Tibia registry integration, ownership and required repository CI. After squash merge, archive the task in a separate lifecycle-only PR. Do not start TSD-002 before that archive is merged.
