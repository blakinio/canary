# Agent Coordination Rules

These rules apply to `docs/agents/**` and supplement the root `AGENTS.md` and repository-wide `README.md` in this directory.

## Autonomous program startup

Before selecting or creating work in a long-lived autonomous workstream:

1. read `programs/README.md`;
2. read the relevant program record under `programs/` when one exists;
3. inspect every active task record under `tasks/active/**` and all open pull requests whose paths, modules, identifiers, or contracts may overlap;
4. run `python tools/agents/task_ownership.py` when the repository is locally available;
5. create one task record, branch, worktree, and draft PR for the selected bounded task;
6. declare exact `owned_paths.exclusive`, `owned_paths.shared`, and `owned_paths.read_only` claims before implementation.

## Ownership rules

- New structured `exclusive` claims are advisory locks enforced by deterministic validation. Two active tasks must not hold overlapping structured exclusive claims.
- `shared` claims identify narrow coordinated edits to catalogues, contracts, changelogs, workflows, or registries. Refresh from current `main` and preserve other agents' entries.
- `read_only` claims identify dependencies that the task may inspect but must not edit.
- Legacy flat `owned_paths` lists are indexed as `legacy_exclusive` and produce migration warnings. They are enforced only with `--strict-legacy` until the old records are migrated.
- Broad claims such as `src/**`, `data-otservbr-global/**`, `tools/e2e/**`, or `docs/**` require a documented reason and should normally be replaced by exact paths or bounded globs.
- Program records describe long-lived responsibility but never override an active task's exact ownership claim.
- Generated ownership indexes are artifacts. Do not commit or edit them as shared locks.

## Program lifecycle

A program may create many task PRs. After each task reaches a final state:

- archive its task record using the existing repository lifecycle;
- update the program record with the result, merge commit, remaining queue, and exact handoff;
- select the next task only after repeating the ownership and overlap preflight.

## E2E lifecycle

- The reusable environment belongs to `CAN-PROGRAM-E2E-PLATFORM`.
- Feature agents own only their suite-specific scenarios and assertions.
- A generic platform change and a feature scenario change use separate task records and PRs when both are required.
- Use `templates/E2E_SCENARIO.md` for new physical-client scenarios.
