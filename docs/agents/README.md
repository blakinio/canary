# Agent Coordination Documentation

This directory is the persistent operating memory for autonomous agents.

## Read order

1. `../../AGENTS.md`
2. `ACTIVE_WORK.md`
3. `MODULE_CATALOG.md`
4. `REPOSITORY_MAP.md`
5. `KNOWN_RISKS.md`
6. `BUILD_TEST_MATRIX.md`
7. `CROSS_REPO_CONTRACTS.md` when OTClient may be affected
8. relevant task records and ADRs

## Sources of truth

- Git and open PRs are authoritative for branches, commits, checks, and merge state.
- Active task records are authoritative for detailed progress, ownership, failures, decisions, and handoff.
- `ACTIVE_WORK.md` is a convenience index and can become stale.
- `MODULE_CATALOG.md` is the discovery index for reusable systems, not a substitute for source/tests.
- `CHANGELOG.md` records completed behavior/architecture changes, not every commit.
- ADRs record decisions that survive one task.

## Required lifecycle

### Start

- inspect open PRs and active tasks;
- search the module catalogue and repository for reusable work;
- create a task record from `templates/TASK.md`;
- claim exact paths/modules;
- publish branch and draft PR early.

### During work

- update the task after discoveries, failures, decisions, tests, and review feedback;
- keep the PR body current;
- update the module catalogue with new/changed reusable interfaces;
- link dependencies and cross-repository tasks.

### Finish

- satisfy the autonomous merge gate;
- update changelog/catalogue when applicable;
- move the task to `tasks/archive/` when final state is known;
- merge through the PR, never by pushing to `main`.

## Avoiding duplicate work

Search by responsibility, paths, symbols, protocol fields, configuration keys, tests, and recent PRs. Reuse similar work or record why it cannot be reused.
