# Agent Coordination Documentation

This directory is the persistent operating memory for autonomous agents. The root `AGENTS.md` requires every agent to read this file before implementation, so the coordination rules here apply repository-wide.

## Read order

1. `../../AGENTS.md`
2. this file
3. for any task that compares or changes behavior against Real Tibia, TibiaWiki/Fandom, CrystalServer, OpenTibiaBR, another donor server, a packet capture, a map, a video or an official-client observation:
   - `REAL_TIBIA_EVIDENCE_SOURCES.md`
   - `REAL_TIBIA_PARITY_PLAYBOOK.md`
   - `programs/REAL_TIBIA_PARITY_PROGRAM.md`
   - `real-tibia/README.md`
   - `real-tibia/generated/MODULE_INDEX.md`
   - the relevant record under `real-tibia/registry/modules/`
   - the relevant module program under `programs/`, when one exists
4. for upstream/donor monitoring, synchronization proposals or claims that this fork is behind:
   - `programs/UPSTREAM_INTELLIGENCE_PROGRAM.md`
   - `upstream/README.md`
   - `upstream/SOURCE_WATCH_POLICY.md`
   - `upstream/TRIAGE_POLICY.md`
   - the latest stable Upstream Intelligence issue/artifact
5. `ACTIVE_WORK.md` as a possibly stale snapshot
6. all relevant records under `tasks/active/**` and live open PRs
7. the relevant long-lived record under `programs/`, when the work belongs to an autonomous program
8. `MODULE_CATALOG.md`
9. `REPOSITORY_MAP.md`
10. `KNOWN_RISKS.md`
11. `BUILD_TEST_MATRIX.md`
12. `CROSS_REPO_CONTRACTS.md` when OTClient may be affected
13. relevant source, tests, system documentation, task records, and ADRs

## Sources of truth

- Git and open PRs are authoritative for branches, commits, checks, changed files, and merge state.
- Active task records are authoritative for exact path ownership, detailed progress, failures, decisions, and handoff.
- Program records are authoritative for long-lived scope, exclusions, task queue, sequencing, and chat-to-chat continuity.
- `ACTIVE_WORK.md` is a convenience index and can become stale; normal task branches must not use it as a writable lock.
- Generated ownership indexes are derived artifacts and must not be edited manually.
- `MODULE_CATALOG.md` is the discovery index for reusable systems, not a substitute for source and tests.
- `CHANGELOG.md` records completed behavior or architecture changes, not every commit.
- ADRs record decisions that survive one task.
- For Real Tibia parity work, the evidence registry, parity playbook, module registry, global parity program, relevant module program, active task, validation report and live PR state together form the durable handoff. Chat history is never the authoritative record.
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

Use it before claiming that this fork is behind or before proposing an upstream/donor import:

- inspect the latest bounded scan artifact and stable report issue;
- re-fetch the exact candidate and current local `main`;
- confirm module mapping and active-task overlap;
- treat issues as signals and exact ancestry as ancestry only;
- record a reviewed decision pinned to the exact candidate revision;
- create a normal bounded task only after proving a current local gap.

The watcher never cherry-picks, creates implementation branches or writes to watched repositories.

## Autonomous programs

Create a record from `templates/PROGRAM.md` under `programs/` when one autonomous agent or ChatGPT chat will deliver many related tasks or PRs over time. Examples include quest audits, Cyclopedia, Wheel of Destiny, OTBM tooling, upstream maintenance, runtime architecture, and the universal E2E platform.

A program may own a long-lived area, but exact edit rights always belong to individual active task records. One active task still means one branch, one worktree, and one PR.

For modules with multiple Real Tibia parity findings, use `programs/REAL_TIBIA_PARITY_PROGRAM.md`, `REAL_TIBIA_PARITY_PLAYBOOK.md`, and the registry record. Do not create one broad task such as “complete the whole module”; create one independently testable task and PR per bounded package.

## Required lifecycle

### Start

- inspect open PRs, all active task records, and the relevant program record;
- search the Real Tibia module registry, module catalogue and repository for reusable work;
- run `python tools/agents/task_ownership.py` and `python tools/agents/real_tibia_registry.py validate` when a local checkout is available;
- create a task record from `templates/TASK.md` or the bounded parity task template;
- use structured ownership claims for new tasks:
  - `exclusive` for paths this task may edit;
  - `shared` for narrow coordinated edits;
  - `read_only` for dependencies the task must not edit;
- publish the branch and draft PR early.

Legacy flat `owned_paths` lists remain readable during migration. They are shown as `legacy_exclusive` and produce overlap warnings, but only new structured `exclusive` claims are hard-blocked by default. Use `--strict-legacy` for a full migration audit.

### During work

- update the task after discoveries, failures, decisions, tests, and review feedback;
- keep the program queue and handoff current when the result changes the long-lived plan;
- keep module registry metadata current when scope, relationships, linked documents, maturity or freshness conclusions change;
- regenerate derived Real Tibia indexes instead of editing them manually;
- keep the PR body current;
- rerun ownership validation before claiming additional files;
- update the module catalogue with new or changed reusable interfaces;
- link dependencies and cross-repository tasks.

### Finish

- satisfy the autonomous merge gate;
- update changelog, catalogue, registry, contracts, and program record when applicable;
- move the task to `tasks/archive/` when its final state is known;
- merge through the PR, never by pushing to `main`.

## Universal E2E ownership

`programs/E2E_AUTOMATION_PROGRAM.md` defines one reusable platform for disposable database, Canary, global datapack, real OTClient, login, scenario execution, SQL checks, screenshots, logs, and cleanup. Feature agents own only their scenario suites and assertions. They must not copy or silently modify the common E2E orchestration in feature-specific PRs.

## Avoiding duplicate work

Search by module ID, responsibility, paths, symbols, protocol fields, configuration keys, test suites, task IDs, upstream candidate IDs and recent PRs. Reuse similar work or record why it cannot be reused. Resolve overlapping structured exclusive claims before editing.
