# Agent Coordination Documentation

This directory is the persistent operating memory for autonomous agents. Chat history is never authoritative; Git, task records, live PR state, deterministic evidence, and durable program/ADR records are.

## Lean startup order

Before implementation, load only:

1. root `../../AGENTS.md`;
2. `REPOSITORY_MAP.md`;
3. `CONTEXT_ROUTING.md`;
4. the existing active task record and live PR for the current task, when present;
5. the nearest nested `AGENTS.md`, when the affected paths are covered by one.

Then classify the task using `CONTEXT_ROUTING.md` and load only the matching routed context.

Do not preload all of `ACTIVE_WORK.md`, `MODULE_CATALOG.md`, `KNOWN_RISKS.md`, `BUILD_TEST_MATRIX.md`, `CROSS_REPO_CONTRACTS.md`, all active tasks, all programs, or all open PRs. Search them narrowly by module, path, symbol, task ID, protocol field, responsibility, workflow, or ownership overlap and open only matching records/sections.

Use `CONTEXT_HANDOFF.md` whenever context pressure grows, the session becomes slow, the model starts rereading/repeating work, or a new agent must continue the task.

## Route-specific context

For work that compares or changes behavior against Real Tibia, TibiaWiki/Fandom, CrystalServer, OpenTibiaBR, another donor server, a packet capture, a map, a video or an official-client observation, use the `real-tibia-parity` route and load:

- `REAL_TIBIA_EVIDENCE_SOURCES.md`;
- `REAL_TIBIA_PARITY_PLAYBOOK.md`;
- `programs/REAL_TIBIA_PARITY_PROGRAM.md`;
- `real-tibia/README.md`;
- the relevant record under `real-tibia/registry/modules/`;
- the relevant module program under `programs/`, when one exists.

For upstream/donor monitoring, synchronization proposals, or claims that this fork is behind, use the `upstream-intelligence` route and load:

- `programs/UPSTREAM_INTELLIGENCE_PROGRAM.md`;
- `upstream/README.md`;
- `upstream/SOURCE_WATCH_POLICY.md`;
- `upstream/TRIAGE_POLICY.md`;
- the latest stable Upstream Intelligence issue/artifact.

For physical-client/login/scenario E2E work, use the `universal-e2e` route and load `programs/E2E_AUTOMATION_PROGRAM.md`, the current task/PR, the relevant workflow and runner/scenario files only.

## Sources of truth

- Git and open PRs are authoritative for branches, commits, checks, changed files, and merge state.
- Active task records are authoritative for exact path ownership, detailed progress, failures, decisions, checkpoint state, and handoff.
- Program records are authoritative for long-lived scope, exclusions, task queue, sequencing, and chat-to-chat continuity.
- `ACTIVE_WORK.md` is a convenience index and can become stale; normal task branches must not use it as a writable lock.
- Generated ownership indexes are derived artifacts and must not be edited manually.
- `MODULE_CATALOG.md` is the discovery index for reusable systems, not a substitute for source and tests. Search it before designing a reusable abstraction; do not read it in full by default.
- `CHANGELOG.md` records completed behavior or architecture changes, not every commit.
- ADRs record decisions that survive one task.
- For Real Tibia parity work, the evidence registry, parity playbook, module registry, global parity program, relevant module program, active task, validation report and live PR state together form the durable handoff.
- Real Tibia module records are inventory and discovery metadata. They do not prove gameplay parity and do not override active task ownership.
- Upstream Intelligence reports are recent candidate inventories. They do not prove a local defect, patch equivalence, official behavior or permission to import code.

## Real Tibia registry-as-code

`real-tibia/` provides one machine-readable record per major domain, formal schemas, dependency and path discovery, multidimensional maturity, source roles and freshness. Human-readable indexes under `real-tibia/generated/` are derived and must not be edited manually.

Before creating a new parity task:

- locate the module with `python tools/agents/real_tibia_registry.py module <module-id>` or `lookup-path <path>`;
- inspect its dependencies, source requirements, linked program and validation reports;
- re-fetch current GitHub and external-source baselines;
- create or update only the bounded module record that is actually affected;
- create a detailed module program only when several independent packages or long-lived blockers justify one.

Registry path patterns are discovery hints only. Structured claims in the active task remain the edit authorization contract.

## Upstream Intelligence

`upstream/` and `programs/UPSTREAM_INTELLIGENCE_PROGRAM.md` define the read-only watch layer for OpenTibiaBR Canary, OpenTibiaBR OTClient, CrystalServer, Remere's Map Editor and Client Editor.

Use it before claiming that this fork is behind or before proposing an upstream/donor import. Confirm the exact candidate and current local `main`, module mapping and active-task overlap. The watcher never cherry-picks, creates implementation branches or writes to watched repositories.

## Autonomous programs

Create a record from `templates/PROGRAM.md` under `programs/` when one autonomous agent or ChatGPT chat will deliver many related tasks or PRs over time. A program may own a long-lived area, but exact edit rights always belong to individual active task records. One active task still means one branch, one worktree, and one PR.

For modules with multiple Real Tibia parity findings, use the global parity program/playbook/registry and create one independently testable task and PR per bounded package.

## Required lifecycle

### Start

- load the lean startup context and select routes;
- search active task records and open PRs only for overlapping paths/modules/identifiers/contracts;
- search the module catalogue and repository for reusable work;
- run `python tools/agents/task_ownership.py` and `python tools/agents/real_tibia_registry.py validate` when applicable and a local checkout is available;
- create a task record from `templates/TASK.md` or the bounded parity task template;
- use structured ownership claims for new tasks: `exclusive`, `shared`, and `read_only`;
- publish the branch and draft PR early.

Legacy flat `owned_paths` lists remain readable during migration. They are shown as `legacy_exclusive` and produce overlap warnings, but only new structured `exclusive` claims are hard-blocked by default. Use `--strict-legacy` for a full migration audit.

### During work

- maintain the compact `## Context checkpoint` defined by `CONTEXT_HANDOFF.md` after material discoveries, failures, decisions, patches, validation changes, review feedback, head changes, and before context exhaustion;
- keep the program queue and handoff current when the result changes the long-lived plan;
- keep module registry metadata current when scope, relationships, linked documents, maturity or freshness conclusions change;
- regenerate derived Real Tibia indexes instead of editing them manually;
- keep the PR body current when externally visible status changes;
- rerun ownership validation before claiming additional files;
- update the module catalogue with new or changed reusable interfaces;
- link dependencies and cross-repository tasks;
- when context pressure appears, stop broad exploration and follow `CONTEXT_HANDOFF.md` instead of trying to carry the entire conversation forward.

### Finish

- satisfy the autonomous merge gate;
- update changelog, catalogue, registry, contracts, and program record when applicable;
- move the task to `tasks/archive/` when its final state is known;
- merge through the PR, never by pushing to `main`.

## Universal E2E ownership

`programs/E2E_AUTOMATION_PROGRAM.md` defines one reusable platform for disposable database, Canary, global datapack, real OTClient, login, scenario execution, SQL checks, screenshots, logs, and cleanup. Feature agents own only their scenario suites and assertions. They must not copy or silently modify the common E2E orchestration in feature-specific PRs.

## Avoiding duplicate work

Search by module ID, responsibility, paths, symbols, protocol fields, configuration keys, test suites, task IDs, upstream candidate IDs and recent PRs. Reuse similar work or record why it cannot be reused. Resolve overlapping structured exclusive claims before editing.
