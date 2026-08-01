# Agent Coordination Rules

These rules apply to `docs/agents/**` and supplement the root `AGENTS.md` and repository-wide `README.md` in this directory.

## Prompt authoring and owner advisory

Before advising the repository owner or writing a prompt for another agent, read `PROMPTING_HANDOVER.md` and the normative `PROMPTING_STANDARD.md`. Use the handover to inspect live repository state and use the standard to construct the prompt. Return a direct recommendation in Polish, a compact reason, and one ready-to-paste worker prompt.

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

## Resilient worker execution

Before creating, claiming, resuming, updating, handing off, or closing any task under this directory:

1. read `EXECUTION_PROTOCOL.md`;
2. read `PROJECT_LANES.json`;
3. select or preserve the correct `project_lane`;
4. treat the task record and Git/PR state as durable and the worker session as disposable;
5. execute one bounded phase per session and persist a checkpoint before a long-running or failure-prone operation;
6. do not remain active while waiting for CI, dependencies, external evidence, deployment, or a user reply;
7. on a blocker, preserve coherent work, record `status`, evidence, blocker and exactly one `next_action`, then end the session;
8. record `execution_mode` and let the worker decide whether Chat/GitHub or Codex is appropriate;
9. at a synchronization barrier, run `python tools/agents/control_room.py --format markdown` and escalate only material decisions.

When rules overlap, follow the more restrictive safety requirement.
