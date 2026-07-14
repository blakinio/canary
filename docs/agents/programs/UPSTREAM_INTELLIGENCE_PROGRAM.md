---
program_id: CAN-PROGRAM-UPSTREAM-INTELLIGENCE
name: Upstream Intelligence and Drift Tracking
status: active
owner: repository-wide
created: 2026-07-14T13:20:00+02:00
updated: 2026-07-14T15:30:00+02:00
last_verified_commit: "73d1408176ef69abddde475cee5e0642ed4a69e9"
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
cross_repo_contracts: []
---

# Mission

Continuously surface relevant changes from selected OpenTibiaBR and CrystalServer repositories, compare them conservatively with the local fork, and preserve reviewed adoption decisions without automatically importing code.

# Watched sources

| Source | Role | Initial baseline |
|---|---|---|
| `opentibiabr/canary` | upstream server | `a879c9312e34381e8eedf397b8ed44510698b689` |
| `opentibiabr/otclient` | upstream client | `bdea0b23b4a738809d698cb7e4f88a299dd6bffc` |
| `zimbadev/crystalserver` | donor server | `fc0d53b9f9965463b6082c07e6d3d482294541a7` |
| `opentibiabr/remeres-map-editor` | editor/tooling | `57ee0e5b915909f207aa7a60968c8ed6e4f7f406` |
| `opentibiabr/client-editor` | editor/tooling | `405f88343a33289ad06ba7749892ee91258925a2` |

All baselines are historical task-start observations. Every run re-fetches live heads.

# Operating model

```text
scheduled/API-triggered scan
        |
        v
bounded candidate inventory
        |
        v
module mapping + local exact/reference evidence
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
- exact ancestry is not semantic equivalence;
- stale decisions are not reused silently;
- all implementation still uses one bounded task and normal CI.

# Program queue

| ID | Scope | Status | Evidence baseline | Exact next action |
|---|---|---|---|---|
| UI-001 | Read-only source registry, schemas, scanner, reports, workflow and policies | merged | PR #331; feature head `f9a159a0ba55aca047160c77dea017549c69512f`; merge `73d1408176ef69abddde475cee5e0642ed4a69e9` | preserve contracts; do not reopen the feature branch |
| UI-002 | First production scan and report-issue verification | planned | merged UI-001 | verify the next scheduled or manually dispatched `main` scan, immutable artifact and stable report issue |
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

None. UI-002 begins only when a production `main` scan exists to verify. Do not create a feature implementation task from an upstream candidate before that candidate is reviewed against current local behavior and authoritative evidence.

# Handoff

Start with the stable report issue, latest JSON artifact, source-watch policy, triage policy, current main and active task records. Do not treat an old snapshot as current state and do not create a broad “sync upstream” PR.
