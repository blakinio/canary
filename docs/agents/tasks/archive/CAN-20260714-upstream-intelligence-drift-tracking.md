---
task_id: CAN-20260714-upstream-intelligence-drift-tracking
program_id: CAN-PROGRAM-UPSTREAM-INTELLIGENCE
coordination_id: UPSTREAM-INTELLIGENCE-DRIFT-TRACKING
status: merged
agent: "GPT-5.6 Thinking"
branch: feat/upstream-intelligence-drift-tracking
base_branch: main
created: 2026-07-14T13:20:00+02:00
updated: 2026-07-14T15:30:00+02:00
last_verified_commit: "73d1408176ef69abddde475cee5e0642ed4a69e9"
risk: medium
related_issue: ""
related_pr: "#331"
depends_on:
  - "merged Real Tibia module registry PR #324"
  - "archived registry lifecycle PR #329"
blocks: []
owned_paths:
  exclusive:
    - docs/agents/upstream/**
    - docs/agents/programs/UPSTREAM_INTELLIGENCE_PROGRAM.md
    - docs/agents/decisions/ADR-20260714-upstream-intelligence-read-only.md
    - tools/agents/upstream_intelligence*.py
    - .github/workflows/upstream-intelligence.yml
    - docs/agents/tasks/archive/CAN-20260714-upstream-intelligence-drift-tracking.md
  shared:
    - docs/agents/README.md
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
    - docs/agents/REAL_TIBIA_EVIDENCE_SOURCES.md
    - docs/agents/programs/REAL_TIBIA_PARITY_PROGRAM.md
    - docs/agents/real-tibia/**
  read_only:
    - AGENTS.md
    - docs/agents/ACTIVE_WORK.md
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

Deliver a conservative, read-only Upstream Intelligence and Drift Tracking system for OpenTibiaBR Canary, OpenTibiaBR OTClient, CrystalServer, Remere's Map Editor and Client Editor.

# Final result

PR #331 merged with:

- bounded rolling-window collection of commits, pull requests, issues and releases;
- exact observed source heads and task-start baselines;
- bounded PR-file retrieval and conservative mapping to the Real Tibia module registry;
- explicit unresolved, unmapped, not-applicable, stale-decision and needs-triage states;
- reviewed decision records pinned to exact candidate revisions;
- target-`HEAD`-only local-history evidence so fetched donor refs cannot imply local presence;
- encoded external Markdown/HTML delimiters and canonical-GitHub-only links;
- deterministic JSON/Markdown artifacts and one stable local report issue;
- daily lightweight and weekly deep scheduled scans;
- schemas, policies, ADR, focused mocked-network/hardening tests and registry/startup/catalogue/changelog integration.

The watcher never writes to external repositories, cherry-picks candidates, creates implementation branches or treats upstream activity as proof of a local defect or official Tibia behavior.

# Delivery history

- Task-start main: `3a390c9d892c5b737d32711a71dbdf7fff1f06fe`.
- Current-main refresh base: `9350f2fb7420f9af2ecf79ea7085ca4e094a3891`.
- Final feature head: `f9a159a0ba55aca047160c77dea017549c69512f`.
- Squash merge: `73d1408176ef69abddde475cee5e0642ed4a69e9`.
- Pull request: #331.
- Final changed-file count: 31.
- Temporary branch-refresh workflow was removed before readiness and is not part of the merge.

# CI and review evidence

| Workflow/job | Result |
|---|---|
| Upstream Intelligence run `29334363187`, job `87089794471` | success |
| Real Tibia Module Registry run `29334363168` | success |
| Agent Task Ownership run `29334363174` | success |
| Ready-state CI run `29334504937` | success |
| Lua Tests job `87090270716` | success |
| Fast Checks job `87090270745` | success |
| Linux release job `87090597075` | success |
| Required job `87092023511` | success |
| review comments, review threads and requested changes | none |

# Red CI repairs retained for handoff

1. The initial focused workflow ran `unittest` without `tools/agents` on `sys.path`; the workflow now sets `PYTHONPATH=tools/agents`.
2. A hardening regression showed that backslash-only escaping still left a literal Markdown-link delimiter sequence. External brackets, pipes, backticks and backslashes are now encoded as entities, and non-canonical URLs never become links.

# Safety boundary confirmed

- no `ACTIVE_WORK.md` edit;
- no gameplay, Lua runtime, protocol, database, map, OTBM, item, datapack, binary, asset, client or production-configuration change;
- all watched repositories remain read-only;
- no automatic implementation, cherry-pick or merge of candidates;
- scan artifacts are bounded evidence inventories, not completeness or parity proof.

# Handoff

The next program item is UI-002: verify the first production `main` scan, its immutable artifact and the stable report issue. Scheduled scans run daily at `03:17 UTC` and weekly deep scans at `04:47 UTC` on Mondays. Any candidate adoption requires a separate bounded task after current-local and authoritative-evidence review.

# Completion

- Final status: merged
- Feature PR: #331
- Feature head: `f9a159a0ba55aca047160c77dea017549c69512f`
- Merge commit: `73d1408176ef69abddde475cee5e0642ed4a69e9`
- Archived at: `docs/agents/tasks/archive/CAN-20260714-upstream-intelligence-drift-tracking.md`
