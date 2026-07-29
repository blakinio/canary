---
task_id: CAN-20260730-rtec-005-wave-3-configuration
program_id: CAN-PROGRAM-REAL-TIBIA-EVIDENCE-COLLECTION
coordination_id: RTEC-005-WAVE-3
status: ready
agent: "GPT-5.6 Thinking"
branch: docs/rtec-005-wave-3-configuration-20260730
base_branch: main
created: 2026-07-30T00:11:00+02:00
updated: 2026-07-30T00:24:00+02:00
last_verified_commit: "8d97385ed91aad418683c16450eb2ca48ba41876"
risk: medium
related_issue: ""
related_pr: "1021"
depends_on:
  - CAN-20260730-rtec-005-wave-3-coordination
blocks:
  - CAN-20260730-rtec-005-wave-3-coordination
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260730-rtec-005-wave-3-configuration.md
    - docs/agents/real-tibia/evidence/modules/configuration/**
  shared: []
  read_only:
    - docs/agents/tasks/active/CAN-20260730-rtec-005-wave-3-coordination.md
    - docs/agents/real-tibia/registry/modules/configuration.yaml
    - src/config/configmanager.cpp
    - src/config/configmanager.hpp
    - config.lua.dist
modules_touched:
  - configuration
reuses:
  - canary-real-tibia-evidence-record-v1
  - canary-real-tibia-module-evidence-index-v1
  - canary-real-tibia-version-history-v1
public_interfaces: []
cross_repo_tasks: []
---

# Goal

Create the bounded `configuration` evidence dossier and one coordinator-reviewable current-Canary candidate record without editing shared programme, global index, owner-request, runtime, data, client, protocol, map, workflow or E2E paths.

# Claim boundary

The candidate proves only the selected source path for typed configuration loading/access, default handling, reload/cache behavior and OTC feature-list discovery at `runtime-path-proven`.

It does not claim production configuration correctness, secrets handling, controlled feature behavior, protocol correctness, runtime feature validation, gameplay or Real Tibia parity.

# Acceptance criteria

- [x] Worker branch and active task created after coordinator PR #1020.
- [x] Draft worker PR #1021 opened.
- [x] Added MODULE, behavior model, decisions, empty publication index, candidate version history, candidate record and pending review.
- [x] Kept record `review-needed` and review `pending` for coordinator adjudication.
- [x] Applied `ci:final-gate` before final checkpoint commits.
- [ ] Pass exact-head ownership, Evidence Contracts, Module Registry and final CI.
- [ ] Squash-merge, then archive through the shared worker lifecycle PR.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-30T00:24:00+02:00
head: 3d87e061c153076f913780477ce5400ce54d8234
branch: docs/rtec-005-wave-3-configuration-20260730
pr: 1021
status: ready
context_routes:
  - agent-governance
  - real-tibia-parity
owned_paths:
  - docs/agents/tasks/active/CAN-20260730-rtec-005-wave-3-configuration.md
  - docs/agents/real-tibia/evidence/modules/configuration/**
changed_paths:
  - docs/agents/tasks/active/CAN-20260730-rtec-005-wave-3-configuration.md
  - docs/agents/real-tibia/evidence/modules/configuration/MODULE.md
  - docs/agents/real-tibia/evidence/modules/configuration/BEHAVIOR_MODEL.md
  - docs/agents/real-tibia/evidence/modules/configuration/DECISIONS.md
  - docs/agents/real-tibia/evidence/modules/configuration/EVIDENCE_INDEX.yaml
  - docs/agents/real-tibia/evidence/modules/configuration/VERSION_HISTORY.yaml
  - docs/agents/real-tibia/evidence/modules/configuration/records/RT-CONFIGURATION-0001.yaml
  - docs/agents/real-tibia/evidence/modules/configuration/reviews/RTEC-005-W3-CONFIGURATION-REVIEW.md
proven:
  - coordinator PR 1020 existed before this worker branch
  - configuration registry and selected sources were pinned by merged wave 3 preflight
  - configuration dossier root was absent at preflight
  - PR 1021 contains only the owned task and configuration dossier root
  - RT-CONFIGURATION-0001 remains review-needed with pending coordinator review
  - module evidence index remains empty before coordinator publication
  - candidate version history records only the exact current-Canary observation baseline
  - worker did not modify shared programme, generated index or owner-request paths
  - ci:final-gate was applied before the final checkpoint commits
derived:
  - the worker output remains a candidate package until coordinator adjudication
unknown:
  - exact corrected-head check identifiers and conclusions
  - coordinator acceptance, narrowing or rejection outcome
conflicts: []
first_failure:
  marker: Real Tibia Evidence Contracts / Validate evidence contracts and indexes
  evidence: run 30495526058 rejected an empty version-history entries array and a module-index as_of date that drifted from canonical 2026-07-29; the candidate history and index date are corrected in this head
rejected_hypotheses:
  - claim production configuration or runtime feature correctness from static source inspection
  - edit shared global publication paths
  - publish the candidate in module/global evidence indexes before coordinator review
  - rerun the failed contract without correcting its deterministic inputs
validation:
  - command: merged wave 3 preflight
    result: PASS
    evidence: PRs 1016 and 1019
  - command: candidate package path and state audit
    result: PASS
    evidence: eight changed paths are inside the declared worker boundary and the candidate evidence index is unpublished
  - command: Real Tibia Evidence Contracts
    result: FAIL_CORRECTED
    evidence: run 30495526058 supplied the exact history/index diagnostics corrected by this checkpoint
blockers: []
next_action: Verify corrected exact-head checks, mark PR 1021 ready, squash-merge, and include this task in the shared worker lifecycle archive.
```
