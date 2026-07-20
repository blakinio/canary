# Universal E2E agent continuation

Use this file together with the `universal-e2e` context route. It supplements, and does not replace, root `AGENTS.md`, the durable E2E architecture, the active task checkpoint, and live Git/PR/CI state.

## Required continuation rule

A continuation agent must distinguish **per-agent task isolation** from **programme-wide blocking**.

- `one agent = one branch/worktree` means one agent must not run two bounded task branches concurrently.
- It does **not** create a global mutex for all tasks in `CAN-PROGRAM-E2E-PLATFORM`, `CAN-PROGRAM-OTBM-E2E-ROUTING`, or another related programme.
- An active task owned by another agent blocks new work only when there is a real `owned_paths` overlap, an unresolved dependency/order constraint, an `atomic-required` hold, or another explicit repository stop condition.
- Same-program or related-program membership by itself is not a blocker.

## Lifecycle cleanup after a merged feature PR

A merged feature whose task record still remains under `docs/agents/tasks/active/` has lifecycle debt.

A fresh agent may take a separate minimal governance-only cleanup task when all of the following are true:

1. the feature PR is already merged;
2. no open PR is still modifying or owning that feature task record;
3. the cleanup touches only the stale task lifecycle paths required by current repository policy;
4. no live task has overlapping ownership on those cleanup paths;
5. no dependency, cross-repository atomic hold, or manual production gate blocks the cleanup.

The existence of a different active E2E or OTBM-E2E PR with non-overlapping owned paths does not prevent this cleanup.

If the continuation agent itself already owns another open bounded task/branch, it must finish or hand off that task before starting the cleanup. Do not take over another agent's active branch or PR merely to perform unrelated lifecycle cleanup.

## Resume order

For a Universal E2E continuation:

1. read every path emitted in `REQUIRED_READS`;
2. read the current task checkpoint and live PR/head;
3. verify only live state that can invalidate `NEXT_ACTION`;
4. perform a narrow ownership/overlap check against relevant active tasks and PRs;
5. execute `NEXT_ACTION` when no real blocker exists.

Do not rebuild a long handover from chat history. Do not copy the whole E2E architecture, programme queue, persistence matrix, or OTBM contracts into the handover; keep those as repository reads selected by context routing.
