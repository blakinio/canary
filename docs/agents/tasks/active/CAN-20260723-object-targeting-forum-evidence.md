---
task_id: CAN-20260723-object-targeting-forum-evidence
program_id: CAN-PROGRAM-REAL-TIBIA-PARITY
coordination_id: PROTOCOL-OBJECT-TARGETING-EVIDENCE
status: in-progress
agent: "Codex"
branch: docs/can-20260723-object-targeting-forum-evidence
base_branch: main
created: 2026-07-23T19:04:22+02:00
updated: 2026-07-23T19:04:22+02:00
last_verified_commit: "5c2ec1df1b5be9494fbf97ba389bea8fd9070f58"
risk: low
related_issue: ""
related_pr: ""
depends_on: []
blocks: []
owned_paths:
  exclusive:
    - docs/agents/real-tibia/IMPROVED_OBJECT_TARGETING_MULTI_ACTION_FORUM_EVIDENCE.md
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

- [ ] Record the official feature contract and official forum clarifications.
- [ ] Separate observed community feedback from implementation requirements.
- [ ] State the collection boundary and unresolved points explicitly.
- [ ] Include actionable acceptance-test candidates without claiming implementation.
- [ ] Pass documentation, ownership and registry checks.
- [ ] Publish the change through a PR targeting `blakinio/canary:main`.

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

# Plan

1. Write the bounded evidence aggregation.
2. Validate links, Markdown, registry and ownership.
3. Commit, push and open a draft PR.

# Work log

## 2026-07-23T19:04:22+02:00

- Confirmed the source thread has 340 results and is closed.
- Captured the full first displayed page, including the official summary, the official-reply index and 18 community replies.
- Located the official 2025 feature announcement and Winter Update release summary.
- Classified the evidence as client-visible feature and feedback evidence; no server packet or runtime behavior is proven.

# Validation and CI

| Commit | Command/check/workflow | Result | Evidence/notes |
|---|---|---|---|
| pending | `git diff --check` | NOT_RUN | Documentation validation pending. |
| pending | `python tools/agents/task_ownership.py` | NOT_RUN | Must include this task record. |
| pending | `python tools/agents/real_tibia_registry.py validate` | NOT_RUN | Registry must remain valid. |

# Risks and compatibility

- Runtime: none; documentation only.
- Data/migration: none.
- Security: no credentials, cookies or private data are recorded.
- Backward compatibility: no code or configuration changes.
- Cross-repo rollout: none; any future OTClient implementation needs a separately authorized task.
- Rollback: revert the documentation commit.

# Remaining work

1. Create and validate the evidence report.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-23T19:04:22+02:00
head: 5c2ec1df1b5be9494fbf97ba389bea8fd9070f58
branch: docs/can-20260723-object-targeting-forum-evidence
pr: none
status: implementing
context_routes:
  - real-tibia-parity
  - agent-governance
owned_paths:
  - docs/agents/real-tibia/IMPROVED_OBJECT_TARGETING_MULTI_ACTION_FORUM_EVIDENCE.md
  - docs/agents/tasks/active/CAN-20260723-object-targeting-forum-evidence.md
proven:
  - Current main is 5c2ec1df1b5be9494fbf97ba389bea8fd9070f58.
  - The official thread reports 340 results and is closed.
  - The first displayed page and official-reply index were captured on 2026-07-23.
derived:
  - The report can define test candidates but cannot prove Canary or maintained-client behavior.
unknown:
  - Full per-post content outside the captured first displayed page.
  - Exact current Canary and maintained OTClient implementation status.
conflicts: []
first_failure:
  marker: none
  evidence: none
rejected_hypotheses:
  - Forum feedback proves implementation parity: announcement and opinions do not prove runtime behavior.
changed_paths:
  - docs/agents/tasks/active/CAN-20260723-object-targeting-forum-evidence.md
validation:
  - command: git diff --check
    result: NOT_RUN
    evidence: pending
blockers:
  - none
next_action: Write docs/agents/real-tibia/IMPROVED_OBJECT_TARGETING_MULTI_ACTION_FORUM_EVIDENCE.md.
```

# Handoff

Start with this task record and the evidence report. Do not infer packet fields, server changes, client code or automation semantics beyond the official statements.

