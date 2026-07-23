---
task_id: CAN-20260723-object-targeting-forum-evidence
program_id: CAN-PROGRAM-REAL-TIBIA-PARITY
coordination_id: PROTOCOL-OBJECT-TARGETING-EVIDENCE
status: completed
agent: "Codex"
branch: docs/can-20260723-object-targeting-forum-evidence
base_branch: main
created: 2026-07-23T19:04:22+02:00
updated: 2026-07-23T17:34:48Z
last_verified_commit: "0c053e8db5b175f2715a43d4eb26681c8d31aae1"
risk: low
related_issue: ""
related_pr: "824"
depends_on: []
blocks: []
owned_paths:
  exclusive:
    - docs/ai-agent/REAL_TIBIA_OBJECT_TARGETING_MULTI_ACTION_FORUM_ANALYSIS.md
    - docs/agents/tasks/active/CAN-20260723-object-targeting-forum-evidence.md
  shared: []
  read_only:
    - docs/agents/ACTIVE_WORK.md
    - docs/agents/REAL_TIBIA_EVIDENCE_SOURCES.md
    - docs/agents/real-tibia/registry/modules/protocol.yaml
module_ids:
  - protocol
primary_module: protocol
modules_touched:
  - official-client input and action-bar evidence
reuses:
  - Real Tibia evidence source registry
  - Real Tibia parity playbook
public_interfaces: []
cross_repo_tasks: []
completed: 2026-07-23T17:34:48Z
---

# Goal

Preserve a bounded, provenance-linked aggregation of the official Tibia forum evidence for Improved Object Targeting and the Multi-Action Button without asserting an unproven Canary or OTClient implementation contract.

# Evidence gate

- [x] Current `main`, open PRs and active tasks re-fetched.
- [x] Protocol module record and global parity program read.
- [x] Official news and forum sources identified.
- [x] The result is classified as client-visible announcement/community evidence, not runtime or protocol proof.
- [x] No donor code or binary material is used.

# Acceptance criteria

- [x] Record the official feature contract and official forum clarifications.
- [x] Separate observed community feedback from implementation requirements.
- [x] State the collection boundary and unresolved points explicitly.
- [x] Include actionable acceptance-test candidates without claiming implementation.
- [x] Pass local documentation, ownership, checkpoint and registry checks.
- [x] Publish the change through a PR targeting `blakinio/canary:main`.
- [ ] Verify current-head GitHub checks.

# Comparison matrix

| Mechanic | Official | Wiki | Canary | OTClient | Upstream | CrystalServer | Tests/runtime | Conclusion |
|---|---|---|---|---|---|---|---|---|
| Improved Object Targeting | News and forum thread | not used | not assessed | not assessed | not assessed | not used | none | announcement evidence only |
| Multi-Action Button | News and forum thread | not used | not assessed | not assessed | not assessed | not used | none | announcement evidence only |

# Ownership and overlap check

- Open PRs: searched by object, targeting, action, hotkey and cursor terms; no matching open PR found.
- Active tasks: searched by the same terms; no overlapping active task found.
- Ownership checker: 27 active records validated before this task was created.
- Exclusive claims: the evidence report and this task record only.
- Overlaps: none observed.
- Resulting PR: `blakinio/canary#824`, base `main`, same-repository head.

# Plan

1. Write the bounded evidence aggregation in the repository's existing `docs/ai-agent` forum-analysis area.
2. Validate links, Markdown, registry and ownership.
3. Commit, push and open a draft PR.

# Work log

## 2026-07-23T19:04:22+02:00

- Confirmed the source thread has 340 results and is closed.
- Captured the full first displayed page, including the official summary, the official-reply index and 18 community replies.
- Located the official 2025 feature announcement and Winter Update release summary.
- Classified the evidence as client-visible feature and feedback evidence; no server packet or runtime behavior is proven.

## 2026-07-23T19:08:32+02:00

- Rebased the initial task commit onto current `main` at `bd65e83540a7862427bbf46479e78b666aa01e29`.
- Added the official contract, first-page sample, requirements inventory, risk register, acceptance-test candidates and client/server boundary report.
- Confirmed that only the task record and the new documentation report are in scope.
- Local whitespace, ownership, checkpoint and Real Tibia registry checks pass.

## 2026-07-23T19:13:32+02:00

- Inspected the only failing current-head check, `Validate active ownership`.
- Confirmed the failure is limited to the task record frontmatter: records under `tasks/active` must retain an active lifecycle status.
- Restored the frontmatter status to the lifecycle-supported `implementing`; the evidence report itself required no correction.

# Validation and CI

| Commit | Command/check/workflow | Result | Evidence/notes |
|---|---|---|---|
| uncommitted | `git diff --check` | PASS | No whitespace errors. |
| uncommitted | documentation assertions | PASS | Exactly two documentation paths, 9 `IOT-*` requirements, 12 `MAB-*` requirements, source links and corpus-boundary statements verified. |
| uncommitted | `python tools/agents/task_ownership.py` | PASS | 29 active task records validated. |
| uncommitted | `python tools/agents/checkpoint.py --require-checkpoint docs/agents/tasks/active/CAN-20260723-object-targeting-forum-evidence.md` | PASS | One task checkpoint validated. |
| uncommitted | `python tools/agents/real_tibia_registry.py validate` | PASS | Registry valid with zero warnings. |
| uncommitted | `python tools/agents/task_lifecycle.py validate-changed ... --current-pr 824` | PASS | One changed active task checkpoint validated after restoring lifecycle-compatible status. |
| `f709456` | `Agent Task Ownership / Validate active ownership` | FAIL | Run `30028250493`, job `89278063881`: task record under `tasks/active` had non-active frontmatter status `validating`. |

# Risks and compatibility

- Runtime: none; documentation only.
- Data/migration: none.
- Security: no credentials, cookies or private data are recorded.
- Backward compatibility: no code or configuration changes.
- Cross-repo rollout: none; any future OTClient implementation needs a separately authorized task.
- Rollback: revert the documentation commit.

# Remaining work

1. Validate and push the lifecycle-status correction, then inspect final-head PR checks.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-23T19:13:32+02:00
head: f709456ea1038d4fc48bcec47255d62be8f9a89f
branch: docs/can-20260723-object-targeting-forum-evidence
pr: 824
status: validating
context_routes:
  - real-tibia-parity
  - agent-governance
owned_paths:
  - docs/ai-agent/REAL_TIBIA_OBJECT_TARGETING_MULTI_ACTION_FORUM_ANALYSIS.md
  - docs/agents/tasks/active/CAN-20260723-object-targeting-forum-evidence.md
proven:
  - Current main is bd65e83540a7862427bbf46479e78b666aa01e29.
  - The official thread reports 340 results and is closed.
  - The first displayed page and official-reply index were captured on 2026-07-23.
  - The report separates official statements, first-page community evidence, derived requirements and unresolved behavior.
derived:
  - The report can define test candidates but cannot prove Canary or maintained-client behavior.
unknown:
  - Full per-post content outside the captured first displayed page.
  - Exact current Canary and maintained OTClient implementation status.
conflicts: []
first_failure:
  marker: Validate active ownership
  evidence: Run 30028250493 job 89278063881 rejected frontmatter status validating under tasks/active.
rejected_hypotheses:
  - Forum feedback proves implementation parity: announcement and opinions do not prove runtime behavior.
changed_paths:
  - docs/ai-agent/REAL_TIBIA_OBJECT_TARGETING_MULTI_ACTION_FORUM_ANALYSIS.md
  - docs/agents/tasks/active/CAN-20260723-object-targeting-forum-evidence.md
validation:
  - command: git diff --check
    result: PASS
    evidence: No whitespace errors.
  - command: documentation assertions
    result: PASS
    evidence: Two documentation paths, 9 IOT requirements, 12 MAB requirements, source links and corpus boundary verified.
  - command: python tools/agents/task_ownership.py
    result: PASS
    evidence: 29 active task records validated.
  - command: python tools/agents/checkpoint.py --require-checkpoint docs/agents/tasks/active/CAN-20260723-object-targeting-forum-evidence.md
    result: PASS
    evidence: One checkpoint validated.
  - command: python tools/agents/real_tibia_registry.py validate
    result: PASS
    evidence: Registry valid with zero warnings.
  - command: python tools/agents/task_lifecycle.py validate-changed ... --current-pr 824
    result: PASS
    evidence: One changed active task checkpoint validated after restoring lifecycle-compatible status.
  - command: Agent Task Ownership / Validate active ownership
    result: FAIL
    evidence: Run 30028250493 job 89278063881 rejected frontmatter status validating under tasks/active; corrected to implementing.
blockers:
  - none
next_action: Validate and push the lifecycle-status correction, then inspect final-head PR checks.
```

# Handoff

Start with this task record and the evidence report. Do not infer packet fields, server changes, client code or automation semantics beyond the official statements.

## Automated lifecycle completion

- Feature PR: #824.
- Feature head: `2ddb9cec86558659627f331d07ec2861c17df5a5`.
- Merge commit: `0c053e8db5b175f2715a43d4eb26681c8d31aae1`.
- Merged at: `2026-07-23T17:34:48Z`.
- This record was moved from `tasks/active` by the post-merge lifecycle automation.
