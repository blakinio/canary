---
task_id: CAN-20260714-upstream-intelligence-drift-tracking
program_id: CAN-PROGRAM-UPSTREAM-INTELLIGENCE
coordination_id: UPSTREAM-INTELLIGENCE-DRIFT-TRACKING
status: ready-for-review
agent: "GPT-5.6 Thinking"
branch: feat/upstream-intelligence-drift-tracking
base_branch: main
created: 2026-07-14T13:20:00+02:00
updated: 2026-07-14T15:18:00+02:00
last_verified_commit: "3dd8d17509e87a52de337f029b16508ad3363c45"
risk: medium
related_issue: ""
related_pr: "#331"
depends_on:
  - "merged Real Tibia module registry PR #324"
  - "archived registry lifecycle PR #329"
blocks:
  - "continuous read-only discovery of upstream and donor drift"
owned_paths:
  exclusive:
    - docs/agents/upstream/**
    - docs/agents/programs/UPSTREAM_INTELLIGENCE_PROGRAM.md
    - docs/agents/decisions/ADR-20260714-upstream-intelligence-read-only.md
    - tools/agents/upstream_intelligence.py
    - tools/agents/upstream_intelligence_common.py
    - tools/agents/upstream_intelligence_candidates.py
    - tools/agents/upstream_intelligence_scan.py
    - tools/agents/upstream_intelligence_render.py
    - tools/agents/upstream_intelligence_lib.py
    - tools/agents/test_upstream_intelligence.py
    - tools/agents/test_upstream_intelligence_hardening.py
    - .github/workflows/upstream-intelligence.yml
    - docs/agents/tasks/active/CAN-20260714-upstream-intelligence-drift-tracking.md
  shared:
    - docs/agents/README.md
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
    - docs/agents/REAL_TIBIA_EVIDENCE_SOURCES.md
    - docs/agents/programs/REAL_TIBIA_PARITY_PROGRAM.md
    - docs/agents/real-tibia/registry/sources.yaml
    - docs/agents/real-tibia/registry/modules/upstream-intelligence.yaml
    - docs/agents/real-tibia/generated/**
  read_only:
    - AGENTS.md
    - docs/agents/ACTIVE_WORK.md
    - docs/agents/REAL_TIBIA_PARITY_PLAYBOOK.md
    - docs/agents/CROSS_REPO_CONTRACTS.md
modules_touched:
  - upstream intelligence
  - Real Tibia registry-as-code
  - agent coordination and evidence governance
reuses:
  - merged Real Tibia module registry and path lookup
  - existing CrystalServer comparison program and source classifications
  - existing task ownership and required CI
public_interfaces:
  - "python tools/agents/upstream_intelligence.py validate"
  - "python tools/agents/upstream_intelligence.py scan --days 30"
  - "python tools/agents/upstream_intelligence.py render --input <snapshot.json>"
  - "scheduled GitHub Actions report issue and JSON/Markdown artifacts"
cross_repo_tasks: []
---

# Goal

Deliver a conservative, read-only Upstream Intelligence and Drift Tracking system that watches OpenTibiaBR Canary, OpenTibiaBR OTClient, CrystalServer, Remere's Map Editor and Client Editor; maps changes to the local module registry; records exact provenance; and produces actionable triage without automatically importing or implementing anything.

# Acceptance criteria

- [x] Add a durable program, source-watch policy, triage policy and read-only ADR.
- [x] Add machine-readable source, candidate, decision and snapshot schemas.
- [x] Add exact initial source baselines for all watched repositories.
- [x] Add deterministic standard-library tooling with mocked-network tests.
- [x] Scan commits, pull requests, issues and releases with bounded pagination and a rolling time window.
- [x] Fetch bounded PR file lists and map paths conservatively to Real Tibia modules.
- [x] Preserve explicit `unmapped`, `not-applicable` and `needs-triage` results instead of guessing.
- [x] Apply reviewed decision records only to an exact candidate revision and without treating automation as parity proof.
- [x] Generate bounded JSON and Markdown reports plus a stable local summary issue.
- [x] Add daily and weekly scheduled workflow with least-privilege per-job permissions.
- [x] Prevent auto-cherry-pick, auto-merge, gameplay modification and writes to watched repositories.
- [x] Register the tooling in the module registry, module catalogue, startup docs and changelog.
- [x] Refresh the long-lived branch onto current `main` without losing either side's changes.
- [x] Pass focused tests, source/schema validation, generated-registry drift, ownership and repository `Required` on reviewed code head.
- [x] Review the complete final path scope and current-main compatibility.
- [ ] Merge feature PR and archive this task in a separate lifecycle PR.

# Safety boundaries

- All watched repositories are read-only.
- An upstream PR, issue, commit or release is a candidate signal, not proof of a local defect.
- Automatic statuses may prioritize review but cannot authorize implementation.
- No workflow may cherry-pick, create implementation branches, modify gameplay or push to external repositories.
- The stable report issue may be created or updated only in `blakinio/canary`.
- Rolling-window scans are bounded, idempotent and safe after missed scheduled runs.
- Local-presence evidence indexes only target `HEAD` history; fetched donor refs cannot make a candidate look present locally.
- Untrusted external titles/errors are encoded before Markdown rendering and only canonical GitHub URLs become links.
- `ACTIVE_WORK.md` remains unchanged.
- The temporary refresh workflow was deleted before readiness and is not part of the final scope.

# Initial source baselines

| Source | Default branch | Observed SHA |
|---|---|---|
| `opentibiabr/canary` | `main` | `a879c9312e34381e8eedf397b8ed44510698b689` |
| `opentibiabr/otclient` | `main` | `bdea0b23b4a738809d698cb7e4f88a299dd6bffc` |
| `zimbadev/crystalserver` | `main` | `fc0d53b9f9965463b6082c07e6d3d482294541a7` |
| `opentibiabr/remeres-map-editor` | `main` | `57ee0e5b915909f207aa7a60968c8ed6e4f7f406` |
| `opentibiabr/client-editor` | `main` | `405f88343a33289ad06ba7749892ee91258925a2` |
| maintained `blakinio/otclient` comparison target | `main` | `afbaee5b9086b43e641a1eb5ff1c4be357278d45` |

These are task-start observations only. Every watcher run re-fetches live source heads.

# Work log

## 2026-07-14T13:20:00+02:00

Created from main `3a390c9d892c5b737d32711a71dbdf7fff1f06fe`. No competing Upstream Intelligence or Drift Tracking PR was found. External repositories were treated as read-only.

## 2026-07-14T13:34:00+02:00

Added program, policies, schemas, source registry, module registry integration and deterministic scanner/report tooling. Temporary bootstrap materialization inputs were removed.

## 2026-07-14T14:35:00+02:00

The first focused workflow failed because `unittest` launched from repository root without `tools/agents` on `sys.path`. Setting `PYTHONPATH=tools/agents` fixed it. On head `63044f3de0d23f4c47043af1c360d4f5e7e619eb`, Upstream Intelligence run `29333063776`, job `87085468560`, Registry `29333063625`, Ownership `29333063777`, CI `29333063994` and Required `87085532345` all passed.

## 2026-07-14T14:55:00+02:00

Review found and fixed two proof-boundary defects: local reference search used `--all`, which could include fetched donor refs, and Markdown rendering insufficiently escaped untrusted upstream titles. Local history now uses target `HEAD` only; rendering encodes Markdown/HTML delimiters and links only canonical GitHub URLs. Deterministic regressions cover both boundaries.

## 2026-07-14T15:12:00+02:00

A bounded same-branch force-with-lease refresh rebuilt the feature on main `9350f2fb7420f9af2ecf79ea7085ca4e094a3891`. The temporary refresh workflow was deleted. Final path review shows only agent docs, registry metadata/generated indexes, Python tooling/tests and the dedicated workflow; no gameplay, Lua runtime, protocol, database, map, OTBM, item, datapack, asset, binary, client or `ACTIVE_WORK.md` change.

## 2026-07-14T15:18:00+02:00

A new security regression initially failed because a backslash-escaped closing bracket still left the literal substring `](javascript:...)` in report text. The renderer now uses HTML entities for brackets, pipes, backticks and backslashes. On code head `3dd8d17509e87a52de337f029b16508ad3363c45`, all 13 focused tests and validations passed.

# Validation evidence

| Head | Evidence | Result |
|---|---|---|
| `3dd8d17509e87a52de337f029b16508ad3363c45` | Upstream Intelligence `29334253473`, job `87089438607` | success |
| same | Real Tibia Registry `29334253456` | success |
| same | Agent Task Ownership `29334253425` | success |
| same | CI `29334253750`; Required `87089491231` | success |
| task-only final documentation head | required workflows | pending before readiness |

# Remaining work

1. Verify workflows on the task-only final documentation head and review state.
2. Mark PR #331 ready and squash-merge.
3. Archive this task in a separate lifecycle PR.

# Handoff

Read this task, the Real Tibia registry README, `REAL_TIBIA_EVIDENCE_SOURCES.md`, `CRYSTALSERVER_COMPARISON_PROGRAM.md`, current open PRs and exact source heads. Treat every observed upstream item as a candidate requiring local-current and authoritative evidence; never convert observations directly into implementation.
