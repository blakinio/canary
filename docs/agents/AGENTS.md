# Agent Coordination Rules

These rules apply to `docs/agents/**` and supplement the root `AGENTS.md` and repository-wide `README.md` in this directory.

## Prompt authoring and owner advisory

Before advising the repository owner or writing a prompt for another agent, read `PROMPTING_HANDOVER.md` and the normative `PROMPTING_STANDARD.md`. Use the handover to inspect live repository state and use the standard to construct the prompt. Return a direct recommendation in Polish, a compact reason, and one ready-to-paste worker prompt.

Before substantial implementation, product-facing validation, audit, E2E, PR cleanup, or task closeout, read and follow `DELIVERY_COMPLETENESS_AND_CLOSEOUT.md`. It is mandatory for prompt eval discipline, trust boundaries, delivery classification, frontend/backend or producer/consumer completeness, independent audit, real E2E, exact-head validation, terminal PR states, and archival. A worker summary is not terminal evidence.

Before autonomous, long-running, retry-prone, CI-waiting, repair, continuation, or multi-task work, read and follow `ANTI_STALL_AND_EXECUTION_BUDGET.md`. Its runtime, no-progress, CI-check, retry, repair-cycle, context-reconstruction, command-timeout, and next-task limits are mandatory. Budget exhaustion or unchanged pending state is a real stop condition even when another contract says to continue autonomously.

Before treating the absence of Codex or a local terminal as a blocker, read and follow `GITHUB_ONLY_EXECUTION.md`. Use the GitHub connection and GitHub Actions on a dedicated branch, select the smallest proving validation, inspect full failed-job logs, keep repairs bounded, preserve required artifacts, and report an exact technical blocker only after the contract's alternatives are exhausted. Autonomous merge or auto-merge of the current task's own PR is authorized only after every required gate in that contract and this repository passes; production deployment, secret changes, protected-environment approval, and protection bypass remain unauthorized without separate authority.

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

- perform the independent audit and required E2E from `DELIVERY_COMPLETENESS_AND_CLOSEOUT.md`;
- reconcile every related or superseded PR to an intentional terminal state;
- archive its task record using the existing repository lifecycle;
- release ownership, leases, temporary branches and worktrees where policy permits;
- update the program record with the result, merge commit, remaining queue, and exact handoff;
- select the next task only after repeating the ownership and overlap preflight and satisfying the remaining-budget and no-stall requirements in `ANTI_STALL_AND_EXECUTION_BUDGET.md`.

A user-facing or cross-layer capability is not complete while a required backend, frontend/client, integration or consumer layer is missing.

## E2E lifecycle

- The reusable environment belongs to `CAN-PROGRAM-E2E-PLATFORM`.
- Feature agents own only their suite-specific scenarios and assertions.
- A generic platform change and a feature scenario change use separate task records and PRs when both are required.
- Use `templates/E2E_SCENARIO.md` for new physical-client scenarios.
- Backend/API checks do not replace real client/frontend E2E for user-facing work.

## Resilient worker execution

Before creating, claiming, resuming, updating, handing off, or closing any task under this directory:

1. read `EXECUTION_PROTOCOL.md`;
2. read `PROJECT_LANES.json`;
3. select or preserve the correct `project_lane`;
4. treat the task record and Git/PR state as durable and the worker session as disposable;
5. execute one bounded phase per session and persist a checkpoint before a long-running or failure-prone operation;
6. record anti-stall timestamps and counters required by `ANTI_STALL_AND_EXECUTION_BUDGET.md`;
7. do not remain active while waiting for CI, dependencies, external evidence, deployment, or a user reply;
8. on a blocker or exhausted budget, preserve coherent work, record `status`, evidence, blocker and exactly one `next_action`, then end the session;
9. record `execution_mode` and let the worker decide whether Chat/GitHub or Codex is appropriate;
10. at a synchronization barrier, run `python tools/agents/control_room.py --format markdown` and escalate only material decisions;
11. before `completed`, verify independent audit PASS, required E2E PASS, exact-head required CI PASS, zero unresolved review threads, zero unintentionally open related PRs, terminal task state and released ownership.

When rules overlap, follow the more restrictive safety requirement.
