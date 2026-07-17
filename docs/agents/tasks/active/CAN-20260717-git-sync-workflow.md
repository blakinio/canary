# CAN-20260717 — Git synchronization workflow

- Status: active
- Branch: `docs/git-synchronization-workflow`
- Route: `agent-governance`
- Owned paths:
  - `AGENTS.md`
  - `docs/agents/tasks/active/CAN-20260717-git-sync-workflow.md`

## Goal

Add an explicit, safe synchronization contract for local agent work so a local checkout is refreshed from `origin/main` before new work, task branches remain isolated, dirty worktrees are not silently rewritten, and local `main` is refreshed after merges.

## Acceptance criteria

- Root `AGENTS.md` documents the Git synchronization workflow.
- The workflow uses `git fetch origin` and `git pull --ff-only origin main` for refreshing local `main`.
- Agents verify exact local and remote state rather than assuming synchronization.
- Dirty worktrees are not automatically reset, stashed, or discarded.
- Task work remains on dedicated branches and never pushes directly to `main`.
- The new guidance does not weaken the existing autonomous delivery or merge-gate policies.
- Required GitHub checks pass on the final PR head before squash merge.

## Context checkpoint

- PROVEN: `blakinio/canary` is the only writable repository for this task.
- PROVEN: root `AGENTS.md` already defines autonomous delivery, pull-request safety, and Git safety rules.
- PROVEN: no open PR was found matching the requested AGENTS.md Git synchronization change before task creation.
- PROVEN: task route is `agent-governance`.
- PROVEN: draft PR #490 targets `blakinio/canary:main` from `blakinio/canary:docs/git-synchronization-workflow`.
- PROVEN: PR #490 has the `ci:final-gate` label before this final checkpoint commit.
- PROVEN: `AGENTS.md` now requires fast-forward-only synchronization of local `main`, exact local/remote state verification, safe handling of dirty worktrees, dedicated task branches, and post-merge local resynchronization without weakening autonomous delivery.
- PROVEN: the change is documentation/agent-governance only; no runtime, build, map, datapack, binary, secret, or production configuration paths are changed.
- Validation: inspect the final changed-file list/full diff, required GitHub checks on the exact final head, mergeability, and unresolved review threads. No local compile is required for this documentation-only change.
- next_action: verify PR #490 on its exact final head, mark ready, and squash-merge only after every required check passes and the merge gate is satisfied.
