# Agent Task Lifecycle

This contract keeps `docs/agents/tasks/active/**` truthful without forcing every historical task record to migrate at once.

## Changed-task checkpoint gate

Agent Task Ownership CI validates checkpoint quality only for active task Markdown files changed by the current PR/push.

For a changed active task:

- `## Context checkpoint` is required;
- checkpoint syntax and evidence-state separation must pass `tools/agents/checkpoint.py` rules;
- frontmatter `branch` and checkpoint `branch` must match;
- when `related_pr` is known, checkpoint `pr` must match it and checkpoint `head` must be a concrete 40-hex commit;
- on a pull request, every changed active task must declare that current PR number as `related_pr`;
- checkpoint `owned_paths` entries must be declared by frontmatter ownership;
- the active task status and checkpoint status must be lifecycle-compatible.

Untouched historical active records are still validated by the existing ownership parser, but they are not forced to add a checkpoint until they are changed. This is intentional migration containment.

Run locally:

```sh
python tools/agents/task_lifecycle.py validate-changed \
  --changed-files-file artifacts/agent-coordination/CHANGED_FILES.txt \
  --current-pr <pr-number>
```

## Post-merge archive automation

`.github/workflows/agent-task-lifecycle.yml` listens for merged same-repository pull requests.

Security boundary:

1. The workflow runs from the trusted default-branch workflow definition.
2. It checks out the trusted default branch after merge.
3. It never checks out or executes the merged feature PR head.
4. It parses active task records and selects only records whose `related_pr` exactly equals the merged PR number.
5. It moves exact matches from `tasks/active` to `tasks/archive` and updates lifecycle metadata.
6. It pushes the cleanup to a dedicated automation branch.
7. It opens a normal cleanup PR.
8. Because a PR created with the repository `GITHUB_TOKEN` does not reliably produce usable recursive PR-triggered checks, the workflow explicitly dispatches `agent-task-ownership.yml` and `ci.yml` on the exact cleanup branch.
9. Only after dispatching those checks does it enable squash auto-merge.
10. Required check contexts and branch protection remain authoritative; the automation never pushes directly to protected `main`.

Fork-origin pull requests are excluded from automated write execution by the same-repository job condition.

The workflow requires repository-scoped `actions: write` only to dispatch the two existing trusted workflows. It does not dynamically construct arbitrary workflow names or execute code from the merged feature branch.

### Why explicit dispatch is required

The first real ACO-002 cleanup created PR #392 correctly after feature PR #391 merged. Its PR-triggered `Agent Task Ownership` and `CI` runs concluded `action_required`, so auto-merge could not satisfy branch protection. This is a recursion/automation-token behavior, not evidence that the feature task itself failed.

The repair keeps the cleanup PR model and normal protection gates. It does not replace them with a direct `main` push. Instead, the trusted lifecycle workflow invokes the existing `workflow_dispatch` entrypoints on the cleanup branch and lets the same required check names report on that exact head.

If explicit dispatch is rejected by future repository permissions or the dispatched checks fail, the cleanup PR remains open and unmerged. An agent must inspect the failure; it must not weaken the gate.

## Deterministic archive command

Preview exact matches without writing:

```sh
python tools/agents/task_lifecycle.py archive-pr \
  --pr-number <number> \
  --merge-commit <40-hex-sha> \
  --merged-at <timestamp> \
  --feature-head <40-hex-sha>
```

Write the archive transition:

```sh
python tools/agents/task_lifecycle.py archive-pr \
  --pr-number <number> \
  --merge-commit <40-hex-sha> \
  --merged-at <timestamp> \
  --feature-head <40-hex-sha> \
  --write
```

The command is fail-closed for invalid SHA inputs, mismatched `related_pr`, archive destination collisions and source/archive path escapes.

## Agent workflow

For substantial work:

1. Create the active task before implementation.
2. Open the draft PR early.
3. Update task frontmatter `related_pr` and checkpoint `pr` to the real PR number.
4. Keep a concrete checkpoint head once the PR is known; it is evidence of the last verified head, not a self-referential requirement to equal the commit that edits the checkpoint.
5. Keep exactly one concrete `next_action`.
6. Merge only after required gates pass.
7. Let post-merge automation create the lifecycle cleanup PR, explicitly dispatch its required checks, and enable auto-merge.

If the automatic workflow cannot create, dispatch checks for, or auto-merge a cleanup PR because repository policy or permissions change, the feature merge remains valid, but the task record must be archived manually before overlapping work claims the same exclusive paths.

## Program records

Task archival is generic and deterministic. Free-form program documents are not automatically rewritten because a generic workflow cannot safely infer program-specific package tables or narrative state.

Feature PRs should update their program record to the most accurate pre-merge state. A subsequent bounded task or lifecycle cleanup may record exact merge evidence when needed.
