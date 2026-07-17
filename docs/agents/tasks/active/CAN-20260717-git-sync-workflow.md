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
- PROVEN: no open PR was found matching the requested AGENTS.md Git synchronization change.
- PROVEN: task route is `agent-governance`.
- next_action: open a draft PR, add the final-gate label before the final checkpoint commit, update `AGENTS.md`, refresh this checkpoint, validate the final diff/checks, then squash-merge only when the merge gate is satisfied.
