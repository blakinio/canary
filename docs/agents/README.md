# Agent Coordination Documentation

This directory is the persistent operating memory for autonomous agents. The root `AGENTS.md` requires every agent to read this file before implementation, so the coordination rules here apply repository-wide.

## Read order

1. `../../AGENTS.md`
2. this file
3. for any task that compares or changes behavior against Real Tibia, TibiaWiki/Fandom, CrystalServer, OpenTibiaBR, another donor server, a packet capture, a map, a video or an official-client observation:
   - `REAL_TIBIA_EVIDENCE_SOURCES.md`
   - `REAL_TIBIA_PARITY_PLAYBOOK.md`
   - `programs/REAL_TIBIA_PARITY_PROGRAM.md`
   - the relevant module program under `programs/`, when one exists
4. `ACTIVE_WORK.md` as a possibly stale snapshot
5. all relevant records under `tasks/active/**` and live open PRs
6. the relevant long-lived record under `programs/`, when the work belongs to an autonomous program
7. `MODULE_CATALOG.md`
8. `REPOSITORY_MAP.md`
9. `KNOWN_RISKS.md`
10. `BUILD_TEST_MATRIX.md`
11. `CROSS_REPO_CONTRACTS.md` when OTClient may be affected
12. relevant source, tests, system documentation, task records, and ADRs

## Sources of truth

- Git and open PRs are authoritative for branches, commits, checks, changed files, and merge state.
- Active task records are authoritative for exact path ownership, detailed progress, failures, decisions, and handoff.
- Program records are authoritative for long-lived scope, exclusions, task queue, sequencing, and chat-to-chat continuity.
- `ACTIVE_WORK.md` is a convenience index and can become stale; normal task branches must not use it as a writable lock.
- Generated ownership indexes are derived artifacts and must not be edited manually.
- `MODULE_CATALOG.md` is the discovery index for reusable systems, not a substitute for source and tests.
- `CHANGELOG.md` records completed behavior or architecture changes, not every commit.
- ADRs record decisions that survive one task.
- For Real Tibia parity work, the evidence registry, parity playbook, global parity program, relevant module program, active task, validation report and live PR state together form the durable handoff. Chat history is never the authoritative record.

## Autonomous programs

Create a record from `templates/PROGRAM.md` under `programs/` when one autonomous agent or ChatGPT chat will deliver many related tasks or PRs over time. Examples include quest audits, Cyclopedia, Wheel of Destiny, OTBM tooling, upstream maintenance, runtime architecture, and the universal E2E platform.

A program may own a long-lived area, but exact edit rights always belong to individual active task records. One active task still means one branch, one worktree, and one PR.

For modules with multiple Real Tibia parity findings, use `programs/REAL_TIBIA_PARITY_PROGRAM.md` and `REAL_TIBIA_PARITY_PLAYBOOK.md`. Do not create one broad task such as “complete the whole module”; create one independently testable task and PR per bounded package.

## Required lifecycle

### Start

- inspect open PRs, all active task records, and the relevant program record;
- search the module catalogue and repository for reusable work;
- run `python tools/agents/task_ownership.py` when a local checkout is available;
- create a task record from `templates/TASK.md`;
- use structured ownership claims for new tasks:
  - `exclusive` for paths this task may edit;
  - `shared` for narrow coordinated edits;
  - `read_only` for dependencies the task must not edit;
- publish the branch and draft PR early.

Legacy flat `owned_paths` lists remain readable during migration. They are shown as `legacy_exclusive` and produce overlap warnings, but only new structured `exclusive` claims are hard-blocked by default. Use `--strict-legacy` for a full migration audit.

### During work

- update the task after discoveries, failures, decisions, tests, and review feedback;
- keep the program queue and handoff current when the result changes the long-lived plan;
- keep the PR body current;
- rerun ownership validation before claiming additional files;
- update the module catalogue with new or changed reusable interfaces;
- link dependencies and cross-repository tasks.

### Finish

- satisfy the autonomous merge gate;
- update changelog, catalogue, contracts, and program record when applicable;
- move the task to `tasks/archive/` when its final state is known;
- merge through the PR, never by pushing to `main`.

## Universal E2E ownership

`programs/E2E_AUTOMATION_PROGRAM.md` defines one reusable platform for disposable database, Canary, global datapack, real OTClient, login, scenario execution, SQL checks, screenshots, logs, and cleanup. Feature agents own only their scenario suites and assertions. They must not copy or silently modify the common E2E orchestration in feature-specific PRs.

## Avoiding duplicate work

Search by responsibility, paths, symbols, protocol fields, configuration keys, test suites, task IDs, and recent PRs. Reuse similar work or record why it cannot be reused. Resolve overlapping structured exclusive claims before editing.