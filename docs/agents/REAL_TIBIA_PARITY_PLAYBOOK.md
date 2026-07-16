# Real Tibia Parity Playbook

> Mandatory operational procedure for any task that validates or changes a Tibia mechanic, module, quest, map region, protocol surface or gameplay value against Real Tibia or another public implementation.

This document exists so agents do not need a previous chat or a multi-page prompt. The repository, current PR, task record and module program must contain enough information for another agent to continue safely.

## 1. When this playbook applies

Use this playbook for work involving, among other areas:

- Wheel of Destiny;
- Cyclopedia, Bestiary, Bosstiary and Charms;
- Equipment Upgrade and Exaltation Forge;
- Imbuements;
- Achievements;
- quests, storages, NPCs, bosses and spawns;
- spells, combat formulas and vocation mechanics;
- protocol and maintained-client behavior;
- market, task systems, persistence and database state;
- OTBM geometry, mechanics, reachability and map content;
- any claim that Canary should match a specific Tibia version.

It also applies when CrystalServer, OpenTibiaBR, TibiaWiki/Fandom, OTLand, a video, a packet capture or another server is proposed as evidence.

## 2. Required startup reads

Before implementation, read in this order:

1. `AGENTS.md` and the nearest nested `AGENTS.md`;
2. `docs/agents/README.md`;
3. `docs/agents/REAL_TIBIA_EVIDENCE_SOURCES.md`;
4. this playbook;
5. `docs/agents/programs/REAL_TIBIA_PARITY_PROGRAM.md`;
6. the relevant module program under `docs/agents/programs/`, when one exists;
7. the relevant validation report under `docs/ai-agent/`;
8. `docs/agents/MODULE_CATALOG.md`;
9. `docs/agents/REPOSITORY_MAP.md`, `KNOWN_RISKS.md`, `BUILD_TEST_MATRIX.md` and `CROSS_REPO_CONTRACTS.md`;
10. current active task records and every open PR whose paths, identifiers, module or contract overlap the requested work.

Live GitHub state, current task records and current PR diffs override stale summary indexes.

## 3. Repository roles and write safety

### Writable target

`blakinio/canary` is the server implementation target. Write only through a task branch and PR targeting `blakinio/canary:main`.

`blakinio/otclient` may be writable only when the user explicitly authorizes a separate client task. A server task must not silently mutate it.

### Read-only sources

Treat these as read-only unless the user explicitly authorizes otherwise:

- `opentibiabr/canary`;
- `opentibiabr/otclient`;
- `zimbadev/crystalserver`;
- `opentibiabr/remeres-map-editor`;
- `opentibiabr/client-editor`;
- every other donor repository, forum attachment, map or datapack.

Before each write, verify the target repository, base repository, head repository and base branch. Never write to an upstream or donor repository.

## 4. There is no single universal source of truth

Evidence precedence depends on the question.

| Question | Strongest useful evidence | Secondary evidence | Insufficient by itself |
|---|---|---|---|
| Feature existence, official name, release date | official Tibia news and update material | maintained wiki, independent captures | donor code |
| Visible gameplay values and behavior | official material plus reproducible official-client observation | maintained wiki, multiple independent captures | one server implementation |
| Current Canary behavior | current `blakinio/canary` source, registrations, tests and runtime evidence | upstream Canary | wiki description |
| Packet shape and client interpretation | maintained `blakinio/otclient`, byte-exact tests, controlled capture | official-client observation, upstream client | server constant alone |
| Persistence and rollback | current Canary load/save code, schema, migrations and failure-injection tests | donor implementation | UI behavior |
| Map geometry and walkability | official-client-derived minimap/pathfinding data plus repeated observation | audited donor OTBM, factual render | screenshot alone |
| Map mechanics | exact OTBM attributes, active handler resolution and runtime test | donor scripts, wiki | geometry alone |
| Candidate implementation | current Canary architecture and tests | CrystalServer or upstream Canary | text similarity or commit message |
| Gameplay proof | deterministic runtime/integration test and, where needed, physical-client E2E | source-contract tests | definition or green compile only |

When sources conflict, record the conflict. Do not automatically choose the newest, most complete-looking or easiest source.

## 5. Mandatory source pinning and provenance

For every repository used as evidence, record:

- repository name and role;
- exact commit SHA, tag or client build;
- date and time observed;
- selected files;
- selected functions, symbols, registrations or packet fields;
- related PR, issue or release note;
- what the source proves;
- what it does not prove.

For downloaded files, also record URL, author, publication date, filename, byte size and SHA-256. Keep downloads outside Git and treat them as untrusted.

Do not base a durable conclusion on a moving `main` without recording the observed SHA.

## 6. Required comparison set

For each module finding, check every applicable column rather than stopping after the first matching source:

| Mechanic | Official Tibia | TibiaWiki/Fandom | CrystalServer | OpenTibiaBR Canary | `blakinio/canary` | maintained OTClient | Tests/runtime | Conclusion |
|---|---|---|---|---|---|---|---|---|

A cell may be `not applicable`, but it must not be silently skipped when the source could materially change the conclusion.

Each populated cell should identify the source SHA/build, path or URL, symbol or section, observed behavior and proof level.

## 7. Evidence levels

Use explicit levels:

1. `definition-found` — constant, table, enum, XML or registry entry exists;
2. `registration-proven` — active loader or registry reaches it;
3. `runtime-path-proven` — production code consumes it;
4. `persistence-proven` — load/save, migration and stale-state behavior are traced;
5. `protocol-proven` — server and maintained-client byte contract is traced;
6. `behavior-proven` — deterministic automated test confirms behavior;
7. `gameplay-proven` — an end-to-end scenario confirms observable gameplay;
8. `physical-client-proven` — a real maintained client completes the scenario.

Never promote a lower level into a higher one. Examples:

- a definition is not runtime proof;
- registration is not persistence proof;
- source agreement is not gameplay proof;
- a compile is not a behavior test;
- an aggregate `Required` job with skipped builds is not a full build proof;
- a physical-client screenshot is not server-state or rollback proof.

## 8. Conclusion and candidate classifications

Use one primary classification at a recorded baseline:

- `CONFIRMED`;
- `CONFORMING`;
- `ALREADY_PRESENT`;
- `CANARY_SUPERIOR`;
- `VALID_FIX_MISSING`;
- `PARTIAL_VALUE`;
- `CLIENT_COUPLED`;
- `CONTENT_ONLY`;
- `CONFLICTING`;
- `UNVERIFIED`;
- `BLOCKED_BY_REFERENCE`;
- `INTENTIONALLY_UNSUPPORTED`;
- `DANGEROUS`;
- `REJECTED`;
- `REPAIRED`;
- `NO_LONGER_APPLICABLE`.

Do not classify a candidate `VALID_FIX_MISSING` until current Canary lacks the behavior and a deterministic failing test or comparably strong proof exists.

## 9. CrystalServer comparison contract

CrystalServer is a high-value read-only donor, not an authority.

For every CrystalServer candidate:

1. pin the exact CrystalServer SHA;
2. open the actual diff and related discussion;
3. split bundled commits into independent behavior units;
4. identify the trigger, state transition and impact;
5. locate corresponding current Canary code and tests;
6. check whether Canary already has an equivalent or safer implementation;
7. identify Crystal-only APIs, datapack assumptions, IDs, client coupling or schema dependencies;
8. verify the candidate against official or independent behavior evidence;
9. define a failing test or deterministic proof;
10. adapt the smallest architecture-native unit.

Never:

- copy an entire module or file because names align;
- mass cherry-pick donor commits;
- assume CrystalServer is newer or more authentic;
- infer official constants from CrystalServer alone;
- transplant custom content as a core-engine fix;
- replace safer Canary behavior with a donor workaround.

Record rejected and already-present candidates so later agents do not repeat the investigation.

## 10. Wiki and community-source contract

TibiaWiki/Fandom is a secondary maintained reference. It is useful for terminology, visible values, thresholds, costs, examples and change history.

A wiki value that changes damage, healing, chance, cooldown, cost, geometry, persistence, protocol or restrictions requires a second independent source or remains `UNVERIFIED`/`BLOCKED_BY_REFERENCE`.

Forum code, OTLand attachments, YouTube videos and screenshots are discovery or donor evidence. Record their limitations and do not convert them directly into authoritative IDs, positions, formulas or handlers.

## 11. Maintained-client and cross-repository contract

Use `blakinio/otclient` to determine packet layout, field width/order, opcode handling, capability gates and UI interpretation.

Do not use the client as authority for server-side authorization, formulas, atomicity or persistence.

When a server correction requires a client change:

- stop the single-repository merge path;
- create or reference a cross-repository coordination ID;
- record server and client PRs, rollout order and compatibility behavior;
- require byte-exact tests on both sides;
- use an atomic cross-repository hold where partial deployment would break clients.

Do not mutate upstream clients.

## 12. Program, finding and task structure

### Repository-wide program

`docs/agents/programs/REAL_TIBIA_PARITY_PROGRAM.md` defines the common registry and module-program rules.

### Module program

A module with more than one independent finding must have a program file under `docs/agents/programs/`. It stores:

- module scope and target version;
- current pinned baselines;
- authoritative validation report;
- completed PRs and merges;
- active task, if any;
- bounded queue;
- blockers and unresolved references;
- reusable modules and contracts;
- exact next action.

Do not make a single task mean “complete the whole module” when the work contains independently testable findings.

### Bounded task

Each implementation task must address one independently testable finding or tightly coupled atomic package. It declares:

- `program_id`;
- branch and PR;
- owned paths;
- evidence and source pins;
- acceptance criteria;
- tests and CI;
- decisions, failures and remaining work;
- a handoff that does not require the old chat.

After merge, archive the task in a separate lifecycle PR. A broad task that delivered only part of its scope must be archived as superseded/partially completed according to current repository conventions, not falsely marked fully complete.

## 13. Preflight before creating a task

1. Fetch current `main` SHA.
2. List all open PRs and active tasks.
3. Inspect changed files for likely overlaps.
4. Check module catalogue and existing program files.
5. Check identifiers, storage, AID/UID and item reservations when applicable.
6. Check current upstream and donor SHAs.
7. Confirm no previous task or PR already delivered the finding.
8. Select the smallest bounded scope.
9. Create a fresh branch from current `main`.
10. Create a task record and early draft PR.

Do not continue a merged PR, deleted historical branch or archived task.

## 14. Implementation gate

Implementation may begin only when:

- the target behavior is defined well enough to test;
- current Canary behavior is proven;
- source conflicts are resolved or explicitly excluded;
- no active owner overlaps the paths;
- the change fits current Canary architecture;
- required client/protocol/schema/map coupling is identified;
- rollback is understood;
- acceptance criteria are bounded.

Do not invent missing spell names, item IDs, storage IDs, AID/UID values, map positions, packet bytes, formulas or geometry.

## 15. Validation by changed surface

Use `BUILD_TEST_MATRIX.md`, then add module-specific tests.

At minimum:

- documentation: exact diff, links, provenance and ownership checks;
- Python tooling: focused unit tests, compilation, schema validation, determinism and security boundaries;
- Lua/data: syntax, registration, focused behavior/contract tests and datapack smoke;
- C++ runtime: focused failing regression, debug tests, release build and platform matrix;
- persistence: clean schema import, round trip, legacy/missing/corrupt state and rollback/failure injection;
- protocol: byte-exact server/client tests, version/capability behavior and malformed input;
- OTBM/map: reuse existing parser, World Index, script resolution, reachability, spawn/NPC and factual renderer tools;
- physical-client E2E: reuse the universal E2E platform after it is merged and stable; do not create a module-specific duplicate platform.

No AI-generated image may be presented as an OTBM render or map proof.

## 16. CI evidence contract

For every claimed result record:

| Head SHA | Workflow run | Job ID/name | Result | What it proves | What it does not prove |
|---|---|---|---|---|---|

Rules:

- never write `passed` without verifying the current head;
- inspect the actual jobs, not only the workflow conclusion;
- confirm heavy jobs were not skipped because the PR remained draft;
- inspect logs before rerunning or fixing a failure;
- a second identical failure requires investigation;
- do not weaken, skip or delete checks to obtain green CI.

## 17. Local DNS and environment limitation

If the environment cannot resolve `github.com`, perform one bounded diagnostic such as:

```text
git ls-remote https://github.com/blakinio/canary.git refs/heads/main
```

After a confirmed DNS failure, do not loop clone/fetch/pull attempts.

If a local checkout already exists, DNS failure alone does not prevent reading, editing or running installed local tests. Record `pwd`, `git status`, branch, remote and head before claiming the checkout is unusable.

GitHub API may be used for file, branch, PR and CI operations, but record:

- the exact failed command and error;
- which operations used GitHub API;
- which isolated checks ran;
- workflow run IDs, job IDs and head SHA;
- all tests not run.

Never write “CI replaced local tests.” State the exact proof boundary.

Do not create cross-branch staging workflows or temporary PRs merely to apply a patch to another branch.

## 18. Delivery and lifecycle

For each bounded PR:

1. keep task, program, validation report and PR body synchronized;
2. commit and push every safe state before context exhaustion;
3. review full diff and changed-file list;
4. confirm no forbidden binaries, map, assets, secrets or unrelated files;
5. mark ready only after acceptance criteria are complete;
6. wait for full current-head CI;
7. fix failures and resolve review threads;
8. update `last_verified_commit`;
9. enable auto-merge only after the autonomous merge gate passes;
10. squash-merge;
11. create a separate lifecycle PR to archive the task and update the program queue.

A real blocker permits a draft handoff, but the branch, head SHA, tests, CI, blocker and exact next step must be durable in GitHub.

## 19. Minimum handoff

Every task handoff must state:

- repository, main SHA, branch, PR and head SHA;
- program and finding ID;
- source baselines and evidence matrix;
- changed files and behavior;
- completed and incomplete acceptance criteria;
- exact tests and CI evidence;
- failed approaches;
- blockers and excluded areas;
- the first next file, symbol and command;
- explicit instructions not to reopen merged PRs or archived tasks.

## 20. Compact prompt for future agents

After this playbook and a module program exist, a new prompt should only need to say:

> Continue the named module program in `blakinio/canary`. Read `AGENTS.md`, `REAL_TIBIA_EVIDENCE_SOURCES.md`, `REAL_TIBIA_PARITY_PLAYBOOK.md`, the module program, validation report, active task and PR. Reconstruct current GitHub state, continue the first active bounded scope, and deliver it through tests, full CI, merge and lifecycle cleanup. Do not restart the full audit or rely on chat history.
