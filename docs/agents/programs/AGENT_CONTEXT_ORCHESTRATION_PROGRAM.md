---
program_id: CAN-PROGRAM-AGENT-ORCHESTRATION
status: active
owner: "GPT-5.5 Thinking"
created: 2026-07-15T16:00:00Z
updated: 2026-07-15T17:04:00Z
---

# Agent Context Orchestration Program

## Mission

Keep autonomous Canary work fast, resumable and economical across Chat, Codex and Work by minimizing default context, preserving durable checkpoints, and spending scarce agentic usage only on tasks that materially benefit from agentic execution.

## Source of truth

- Git, current branch/head, live PR and required CI are authoritative for repository state.
- Active task records are authoritative for path ownership and bounded task state.
- `docs/agents/CONTEXT_ROUTING.md` and `docs/agents/CONTEXT_HANDOFF.md` are the human contracts.
- `docs/agents/CONTEXT_ROUTES.json` is the machine-readable routing profile consumed by agent tooling.
- Chat history is disposable and must never be required for continuation.

## Default operating model

```text
CHAT supervisor
  -> classify task and resolve minimal context
  -> keep GitHub/PR/CI/architecture/triage work in CHAT when sufficient
  -> hand a bounded evidence bundle to CODEX only for local edit/build/test/runtime execution
  -> hand a bounded evidence bundle to WORK only for broad multi-source research or a large deliverable
  -> receive checkpoint/result back in CHAT
  -> coordinate PR, CI, review and merge
```

This model does not assume that one ordinary Chat conversation can create or control other chats. A higher-license Codex or external orchestrator may run workers in parallel, but repository task records, ownership and checkpoints remain the durable coordination boundary.

## Budget policy

Default: `minimize_agentic_usage`.

Rules:

1. Prefer CHAT when connector-based analysis, planning, GitHub, PR, CI and narrow repository edits are sufficient.
2. Recommend CODEX only when local execution has concrete value: iterative code edits, compilation, tests, runtime debugging, physical-client/E2E execution, or isolated parallel coding workers.
3. Recommend WORK only for genuinely broad multi-source research or a large final deliverable.
4. Never send whole chat history, whole-repository dumps, full logs or unrelated docs to CODEX/WORK.
5. Pass only task identity, head/branch/PR, routed reads, PROVEN facts, UNKNOWN/CONFLICT items, first failure, changed paths, validation evidence, blockers and one `next_action`.
6. Do not make CODEX/WORK rediscover facts already marked PROVEN unless current Git/PR evidence changed.
7. Return coordination to CHAT after the bounded CODEX execution loop or WORK research/deliverable package completes.
8. Escalate context only on evidence of need.

## Packages

| Package | Scope | Status |
|---|---|---|
| ACO-001 | Machine routing, checkpoint validation, resume bundles and CHAT/CODEX/WORK budget-aware advisor | completed by PR #389 |
| ACO-002 | Changed-task-aware CI checkpoint enforcement and lifecycle automation | completed by PR #391; bot-cleanup check dispatch repair in PR #394 |
| ACO-003 | Agent efficiency evals: files read, repeated reads, tool calls, time-to-first-action, handoff success | queued |
| ACO-004 | Optional multi-agent supervisor queue for higher-license Codex/worktree execution | queued |

## ACO-001 result

ACO-001 merged in PR #389 as `7d50b58dad10c81d7e414172e965158781f11ce1` and delivered deterministic Python 3.12 standard-library tools under `tools/agents/**`, machine-readable routing configuration, focused tests, and narrow agent-governance documentation/CI integration.

The package did not:

- create an unrestricted shell executor;
- assume access to Codex or Work when unavailable;
- automatically spawn external agents from ordinary Chat;
- bypass repository ownership, CI or merge gates;
- infer exact token counts that are not exposed by the platform;
- claim that CHAT/CODEX/WORK pricing or limits are stable repository facts.

## ACO-002 result and repair boundary

ACO-002 merged in PR #391 as `0d47a18e2cf1e4d81a3c16f85947299bda4afc0e` and added deterministic changed-task validation, exact-`related_pr` task archival, and trusted post-merge cleanup PR creation.

The first production cleanup PR #392 proved that PRs created by the repository `GITHUB_TOKEN` did not receive usable recursive PR-triggered CI in this repository: both Agent Task Ownership #1389 and CI #2516 concluded `action_required` on cleanup head `e61f6691e5bdd4440f3a00b3ca26493658ba5511`.

Repair PR #394 keeps the protected cleanup-PR model and adds explicit `workflow_dispatch` calls for the existing trusted Agent Task Ownership and CI workflows on the exact cleanup branch before enabling auto-merge. The repair must be proven by a real post-merge cleanup before ACO-003 starts.

ACO-002 and its repair do not:

- checkout or execute an untrusted contributor head from `pull_request_target`;
- push lifecycle cleanup directly to protected `main`;
- auto-edit free-form program records based on guessed semantics;
- force all untouched historical task records to migrate checkpoints at once;
- weaken ownership conflict detection or branch protection.

## Context pressure policy

When an agent slows down, repeats searches, rereads the same files, loses earlier facts, or approaches context exhaustion:

1. stop broad discovery;
2. verify current Git/PR/CI state;
3. validate/update the task checkpoint;
4. generate a compact resume bundle;
5. leave one `next_action`;
6. continue in a fresh session/worker from repository state rather than replaying old chat history.

## Multi-agent policy

For future higher-license operation:

- one worker = one task branch/worktree/PR;
- supervisor creates bounded tasks and ownership claims before dispatch;
- workers receive only their routed evidence bundle;
- workers checkpoint before handoff;
- supervisor resolves ownership conflicts and merge ordering;
- independent workers may run in parallel only when owned paths and contracts do not overlap.

## Exact handoff

A continuation or worker starts with:

```text
python tools/agents/resume.py --task <active-task-path> [task capability flags]
```

The generated bundle is intentionally bounded. The worker verifies live head/PR/CI before acting, loads only required routed context, and does not reconstruct state from previous chat history.

## Current task

- Repair task: `CAN-20260715-agent-task-lifecycle-bot-pr-checks`
- PR: #394
- State: implementing explicit required-workflow dispatch for bot-created lifecycle cleanup PRs.
- ACO-003 and ACO-004 remain queued until PR #394 merges and its own generated cleanup PR proves the repaired lifecycle end to end.

## Handoff

Complete PR #394 through normal CI and branch protection. Then verify the generated cleanup PR for #394 receives explicitly dispatched required checks on its exact head and auto-merges. Only after the repair task disappears from `tasks/active` on `main` should ACO-003 start as a separate bounded task/branch/PR.
