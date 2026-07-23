# Universal E2E Quality, Resilience and Test Intelligence Roadmap

## Purpose

This document is the durable successor roadmap for the Universal OTS E2E platform after delivery and lifecycle closure of `E2E-GAMEPLAY-001` through `E2E-GAMEPLAY-008`.

The first roadmap established one reusable disposable Canary/MariaDB/controlled-OTClient lifecycle and proved the core progression from physical actions through persistence, bounded multi-client orchestration, controlled client-disconnect recovery and one representative cross-system journey.

The next phase is not another platform bootstrap. Its purpose is to make the existing E2E system:

- broader in representative gameplay coverage;
- stronger under restart, retry, concurrency and failure;
- more deterministic and reproducible;
- easier for an autonomous agent to diagnose;
- capable of detecting regressions in behavior, stability and performance;
- useful as a release-certification system without running every expensive scenario on every pull request.

This roadmap extends, and does not replace, `docs/architecture/universal-e2e-gameplay-validation.md`.

## Non-negotiable architecture rules

1. **One canonical physical lifecycle.** All packages reuse the existing Universal E2E Canary/MariaDB/controlled-OTClient orchestration. Do not create a second runner or complete per-feature workflow.
2. **Feature intent stays feature-owned.** Generic infrastructure does not hard-code quest storages, rewards, NPC names, monsters, map landmarks or expected gameplay values.
3. **OTBM remains map truth.** Nontrivial navigation consumes the existing World Index, Reachability, route-plan, interaction and preflight boundaries. E2E never implements an independent pathfinder.
4. **M0-M5 remains the evidence maturity model.** New quality checks do not invent higher maturity levels. Determinism, stability, resilience, cleanup, performance, compatibility and diagnostic quality are orthogonal dimensions.
5. **Failures remain evidence.** Retries may measure stability but must never hide a failed attempt or convert an unstable scenario into a clean pass.
6. **Fault injection is fixed-purpose and isolated.** No production targets, arbitrary shell commands, arbitrary SQL, arbitrary network targets or external systems.
7. **Every expensive capability starts bounded.** One concrete deterministic consumer first; broad matrices and fuzzing are scheduled only after the primitive is proven.
8. **No committed proprietary or transient runtime artifacts.** OTBM files, client assets, DB snapshots/dumps, crash dumps and generated run evidence remain workflow artifacts or temporary files unless a sanitized small fixture is explicitly repository-owned.

## Delivered foundation

The roadmap assumes the following merged capabilities and treats them as reuse-only unless a later bounded task proves a generic gap:

- disposable MariaDB/MySQL + exact Canary + controlled OTClient physical lifecycle;
- declarative bounded action plans;
- exact physical movement, floor change and teleport;
- OTBM-aware executable route plans, exact-map preflight and `follow_route` execution;
- typed persistence assertions;
- deterministic combat and Canary NPC promotion vertical slices;
- bounded two-client orchestration for exactly one secondary controlled OTClient;
- fixed-purpose client `forceLogout()` disconnect and real recovery login;
- one representative combat -> NPC promotion -> relog/persistence cross-system journey;
- changed-scenario and OTBM/Semantic-Diff-informed selection foundations.

## Quality dimensions

Every future scenario may continue to claim only its strongest proven M0-M5 level. Separately, tooling may report these orthogonal quality dimensions:

| Dimension | Question |
|---|---|
| determinism | Does the same pinned input and seed reproduce the same relevant action/result trace? |
| stability | Does the scenario pass consistently across repeated clean executions without hidden retries? |
| resilience | Does the system recover, roll back or fail safely under one explicit controlled fault? |
| exactly-once | Does retry/reconnect/replay create exactly one authorized durable effect? |
| concurrency | Do concurrent actors/processes preserve declared invariants and ownership rules? |
| cleanup | Are clients, sessions, players, DB fixtures and temporary processes/resources fully cleaned? |
| performance | Are latency/resource metrics within an evidence-backed baseline or threshold? |
| compatibility | Does the scenario remain valid across an explicitly supported client/server/datapack/schema matrix? |
| diagnostics | Does a failure retain enough machine-readable evidence to identify the first failed invariant? |

Recommended dimension states are `not-evaluated`, `pass`, `fail`, `unstable` and `blocked`. A dimension state must never be inferred from an unrelated M-level proof.

## Execution tiers

The platform should distinguish suite cost and purpose instead of forcing all scenarios into every PR.

### PR-required

Use for deterministic, bounded scenarios selected by changed paths/contracts/evidence. The goal is fast regression prevention on directly impacted behavior.

Typical contents:

- focused feature scenarios;
- critical login/relog smoke;
- impacted route/mechanic scenarios;
- focused persistence checks;
- bounded exactly-once or multi-client cases when directly affected.

### Scheduled/nightly

Use for expensive repeated or exploratory-but-reproducible validation:

- flake/stability certification;
- soak tests;
- performance trend runs;
- bounded seeded gameplay fuzzing;
- wider compatibility and datapack matrices;
- selected concurrency stress cases.

Nightly failures remain real failures or instability evidence; scheduled execution is not permission to ignore them.

### Release certification

Use before a release candidate or explicitly requested certification point:

- gold gameplay scenarios;
- migration/upgrade validation;
- supported client/server matrix;
- supported datapack smoke matrix;
- restart/recovery and exactly-once sentinels;
- cleanup certification;
- selected performance guardrails.

### On-demand investigation

Use when a failure or high-risk change justifies additional cost:

- deterministic replay;
- failure minimization;
- expanded differential runs;
- crash bundle analysis;
- controlled DB interruption;
- focused fuzzing around one state machine.

## Priority strategy

The recommended order is intentionally dependency-aware.

### Phase A — representative gameplay and evidence quality

Deliver a real multi-client feature, a stronger recovery seam, a broader journey and a standardized result/cleanup model before adding large-scale repetition.

### Phase B — transactional and recovery correctness

Add deterministic state reset, exactly-once, concurrency and controlled infrastructure faults only after the evidence/cleanup primitives are reliable.

### Phase C — test intelligence and reproducibility

Add differential comparison, replay, minimization, invariant checking and seeded fuzzing after deterministic inputs/results are available.

### Phase D — operational confidence and release certification

Add soak, performance, compatibility, datapack, migration and release matrices once core scenarios are stable enough that large repeated suites provide signal rather than noise.

# Ordered packages

## E2E-QRI-001 — Real two-player trade and persistence

**Workstream:** gameplay coverage / multi-client

**Default tier:** PR-required when trade/economy/container code is impacted; release certification otherwise.

**Goal:** consume the existing bounded two-client orchestration in a real player-to-player feature instead of only proving simultaneous presence and visibility.

Reference flow:

```text
login actor A
login actor B
prepare deterministic item or balance fixture
A opens trade with B
B observes and accepts
both commit the exchange
assert immediate ownership/balance conservation
safe logout both clients
relog relevant actors
assert durable item/balance ownership
cleanup_certified=true
```

Acceptance direction:

- distinct deterministic actor identities and actor-scoped logs;
- one real trade request/accept/commit path;
- exact conservation assertions for transferred item count and/or balance;
- no duplicated or lost item/economy state;
- canonical cleanup leaves no connected test players.

Do not generalize actor count beyond the existing contract merely to implement this package.

---

## E2E-QRI-002 — Canary restart, reconnect and recovery M5

**Workstream:** reliability/resilience

**Default tier:** release certification; PR-required only for directly affected session/restart/save paths.

**Goal:** add one fixed-purpose safe Canary restart seam inside the disposable E2E environment and prove expected reconnect/relog behavior.

Reference flow:

```text
login
establish stable online state
perform one durable bounded action
request canonical save/settle when required
inject controlled Canary restart
observe expected disconnect
restart same pinned Canary revision/config
reconnect or relog through the declared supported path
assert no ghost session and correct durable state
safe logout
```

Acceptance direction:

- restart seam targets only the disposable test Canary process;
- expected disconnect is classified separately from unexpected platform failure;
- stale `players_online`/session ownership is detected;
- no duplicate reward or repeated side effect after recovery;
- server/client/DB cleanup remains complete.

---

## E2E-QRI-003 — Representative real-player Journey 002

**Workstream:** gameplay coverage / cross-system

**Default tier:** release certification plus targeted PR selection when impacted.

**Goal:** compose a longer representative player journey from already proven capabilities.

Target shape:

```text
login at deterministic origin
follow evidence-backed route to depot
perform deterministic inventory/depot preparation
follow route to NPC or quest entry
perform bounded dialogue/quest interaction
navigate through supported route mechanics
fight deterministic encounter
receive or observe deterministic reward/state
return, safe logout
relog
assert durable quest/inventory/economy/progression result
```

The exact quest/reward must be selected by a separate feature-owned task from current evidence. Do not invent coordinates, NPCs, storages or rewards in the shared platform.

---

## E2E-QRI-004 — Evidence maturity and coverage dashboard

**Workstream:** test intelligence

**Default tier:** generated from CI/nightly/release artifacts.

**Goal:** produce a factual machine-readable and human-readable view of E2E coverage without treating missing evidence as success.

For each reviewed system/scenario, report:

- strongest proven M0-M5 level;
- last exact relevant revision/run;
- determinism/stability/resilience/exactly-once/concurrency/cleanup/performance/compatibility/diagnostics dimension state;
- last success and last failure where available;
- stale or missing evidence;
- explicitly known coverage gaps.

The dashboard consumes retained evidence; it does not rerun scenarios or promote static evidence into physical success.

---

## E2E-QRI-005 — Standard machine-readable result envelope and richer first-failure evidence

**Workstream:** diagnostics / platform evidence

**Default tier:** all physical runs.

**Goal:** converge physical scenario output on one bounded result envelope such as `e2e-result.json`.

Minimum fields should include, when applicable:

- scenario ID and schema version;
- Canary revision, OTClient revision and datapack identity;
- map/World Index/route-plan provenance hashes;
- actor/client identity;
- lifecycle phase;
- last successful step;
- first failed step and failure class;
- expected and observed bounded state;
- expected/observed position;
- first divergence marker;
- assertion and persistence result summary;
- cleanup result;
- references to retained server log, client log, packet/session record and screenshot artifacts.

The envelope references large artifacts instead of embedding unrestricted logs or secrets.

---

## E2E-QRI-006 — Resource cleanup certification

**Workstream:** reliability/diagnostics

**Default tier:** all physical runs where the environment exposes the required checks.

**Goal:** make cleanup a first-class machine-readable result rather than an implicit best effort.

Candidate checks:

- zero expected test players online after teardown;
- no orphan controlled OTClient process;
- no orphan Canary child/test process;
- no stale reserved test port or lifecycle lock owned by the run;
- disposable DB/container resources stopped or removed as declared;
- scenario-owned temporary files removed or retained only as declared artifacts.

A gameplay assertion pass with cleanup failure must not be reported as a fully clean run.

---

## E2E-QRI-007 — Deterministic OTClient UI-state assertions

**Workstream:** gameplay coverage / client evidence

**Default tier:** targeted PR/release scenarios only.

**Goal:** verify UI state when server/SQL evidence is insufficient.

Preferred evidence order:

1. maintained OTClient widget/model state through bounded test APIs;
2. deterministic UI event/state markers;
3. bounded screenshot comparison where appropriate;
4. OCR only as a last-resort auxiliary signal, never the sole authoritative proof for critical state.

Candidate first consumers:

- trade window opened and actor identities visible;
- expected NPC dialogue/channel state;
- target present in battle/attack state;
- inventory/container slot visibly reflects a deterministic reward;
- expected system notification is present.

Do not turn the shared platform into feature-specific UI knowledge; feature suites own expected labels/values.

---

## E2E-QRI-008 — Deterministic fixture snapshot and restore

**Workstream:** reliability / test isolation

**Default tier:** infrastructure primitive used by selected suites.

**Goal:** allow complex scenarios to start from and return to a deterministic known state without manually resetting many tables.

Constraints:

- snapshots are generated from disposable repository-owned fixtures;
- no production/user DB dumps;
- no committed live database snapshots containing secrets or personal data;
- restoration is bounded to the isolated test environment;
- schema/revision compatibility is verified before restore;
- a scenario may still choose explicit fixture seeding when that is clearer and safer.

This package should support later differential, exactly-once, concurrency and failure-minimization work.

---

## E2E-QRI-009 — Exactly-once gameplay and economy validation

**Workstream:** reliability / transactional correctness

**Default tier:** targeted PR and release certification.

**Goal:** prove that retry, reconnect or replay of a bounded operation produces exactly one authorized durable effect.

Candidate consumers:

- quest/reward claim;
- bank transfer;
- market purchase;
- player trade commit;
- store purchase;
- daily reward;
- deterministic loot/reward container claim.

Reference shape:

```text
capture before-state invariant
start operation
inject one declared disconnect/timeout/retry boundary
retry through the supported client/server path
capture after-state
assert exactly one effect
assert conservation/idempotency invariants
relog and verify persistence
```

No arbitrary packet replay interface should be added merely for this package; use a feature-approved bounded retry seam.

---

## E2E-QRI-010 — Concurrency and race E2E

**Workstream:** reliability / multi-actor and multi-process correctness

**Default tier:** scheduled or targeted high-risk PR validation.

**Goal:** prove selected invariants under deterministic concurrent attempts.

Candidate first cases:

- two controlled players compete for one explicitly fixture-owned market quantity;
- two actors attempt a mutually exclusive instance/resource entry;
- concurrent claim of a reviewed single-use/shared reward;
- concurrent updates to an explicitly selected global/shared state;
- cross-channel or multi-process writer ownership where the runtime architecture supports it.

Requirements:

- explicit barrier/synchronization points instead of timing guesses;
- machine-readable actor/process traces;
- conservation/uniqueness invariants;
- bounded attempts and cleanup;
- no claim of global concurrency safety from one selected race.

---

## E2E-QRI-011 — Controlled database interruption and recovery

**Workstream:** resilience

**Default tier:** on-demand and release certification; never routine on every PR initially.

**Goal:** prove safe behavior for one explicitly supported isolated DB availability fault.

Prerequisites:

- stable baseline scenario;
- fixed-purpose disposable DB interruption seam;
- declared expected server/client behavior;
- restart/recovery package already proven where required.

Candidate assertions:

- operation fails or pauses in the documented safe way;
- no partial durable mutation;
- reconnect/retry does not duplicate the effect;
- DB connection pool recovers or server terminates safely according to contract;
- cleanup succeeds.

Never target a shared, staging or production database.

---

## E2E-QRI-012 — Save/restart consistency

**Workstream:** resilience / persistence

**Default tier:** release certification and targeted persistence PRs.

**Goal:** prove selected durable state remains consistent across an explicit save and Canary restart.

Candidate domains:

- position where persistence is expected;
- inventory/depot;
- bank/economy;
- vocation/progression;
- quest/storage;
- house/guild state where deterministic fixtures exist.

The scenario must define which fields are expected to persist and which are intentionally transient.

---

## E2E-QRI-013 — Controlled test-time abstraction

**Workstream:** testability / time-dependent gameplay

**Default tier:** targeted feature suites.

**Goal:** test time-dependent behavior without waiting real days and without changing the host/global wall clock.

Candidate consumers:

- daily reset/reward;
- cooldowns;
- boss lockouts;
- market expiry;
- house rent;
- stamina/reward streaks.

Rules:

- prefer a bounded injectable domain clock or explicit test-only time source;
- never mutate production time or external NTP/system clock;
- real-time and test-time modes must be explicit;
- persistence across time advance must remain testable.

---

## E2E-QRI-014 — Property and invariant E2E

**Workstream:** test intelligence / correctness

**Default tier:** targeted PR plus scheduled broader checks.

**Goal:** assert system invariants even when the exact final value is not the primary contract.

Examples:

- total traded item count is conserved;
- total balance across an internal transfer is conserved except explicit fees;
- a single character cannot own two simultaneous authoritative sessions where prohibited;
- an item cannot appear in two exclusive containers after one move;
- durable quantities never become negative when the domain forbids it;
- one-time claims remain at-most-once.

Invariant definitions remain feature/domain owned and must be explicit, not inferred from names or general MMO assumptions.

---

## E2E-QRI-015 — Differential runtime E2E

**Workstream:** test intelligence / regression detection

**Default tier:** on-demand high-risk PRs, selected release certification.

**Goal:** run the same deterministic scenario against an approved baseline and candidate revision and compare normalized runtime outcomes.

Possible normalized comparisons:

- final typed persistence assertions;
- bounded DB rows/scalars;
- inventory/economy conservation summaries;
- position/route trace;
- protocol/event markers;
- first-failure classification;
- selected latency metrics.

The system must distinguish:

- expected reviewed behavior change;
- unexpected regression;
- non-comparable evidence due to schema/datapack/client/provenance mismatch.

Differential output is review evidence, not automatic authorization to accept a behavior change.

---

## E2E-QRI-016 — Deterministic replay artifact

**Workstream:** diagnostics / reproducibility

**Default tier:** generated by eligible runs; replay invoked on demand.

**Goal:** retain a bounded replay description such as `e2e-replay.json` that can reproduce the same approved scenario inputs and declared action plan.

Include:

- scenario and fixture identity;
- revisions/provenance;
- random seed where used;
- route-plan identity;
- ordered bounded actions and actor ownership;
- declared fault phase when applicable;
- expected assertions.

Do not serialize secrets, raw passwords, unrestricted packet payloads or arbitrary commands.

---

## E2E-QRI-017 — Failure minimization

**Workstream:** test intelligence / diagnostics

**Default tier:** on-demand after a reproducible failure.

**Goal:** reduce a deterministic failing action sequence to the smallest still-valid reproducer without changing the failure class.

Rules:

- start only from a replayable failure;
- preserve mandatory lifecycle/dependency steps;
- never remove setup required to keep the scenario semantically valid;
- require the same first-failure marker/class across confirmation runs;
- output the minimized scenario as an artifact or reviewable proposal, not an automatic source commit.

---

## E2E-QRI-018 — Seeded reproducible gameplay fuzzing

**Workstream:** test intelligence / exploratory robustness

**Default tier:** nightly/on-demand only.

**Goal:** explore bounded action/state combinations while preserving exact reproducibility.

Possible allowed action vocabulary may include only already-safe bounded actions such as:

- movement within a declared region;
- open/close container;
- bounded item move among fixture-owned containers;
- selected NPC interaction;
- target/attack against a deterministic fixture;
- safe logout/relog.

Every run records a seed and exact trace. A discovered crash/failure must be replayable before promotion into a regression scenario. No arbitrary Lua, shell, SQL, packet or external-network fuzz commands.

---

## E2E-QRI-019 — Protocol and gameplay state-machine misuse E2E

**Workstream:** reliability / protocol-state correctness

**Default tier:** targeted PR/nightly.

**Goal:** exercise invalid or stale action ordering through maintained bounded client/protocol surfaces.

Candidate cases:

- action before world entry;
- second login while a session is still authoritative;
- trade accept after disconnect/cancel;
- container/item action after the source container is closed or invalidated;
- attack/interaction after target despawn;
- stale request after explicit state transition.

This is state-machine validation, not unrestricted malformed-packet fuzzing.

---

## E2E-QRI-020 — Dependency-graph-driven scenario selection

**Workstream:** test intelligence / CI efficiency

**Default tier:** PR selection layer.

**Goal:** select relevant E2E scenarios from reviewed code/module/data dependencies, not only from changed scenario files.

Example intent:

```text
change in bank/economy implementation
  -> bank persistence scenario
  -> NPC banking scenario
  -> trade/economy exactly-once sentinel
  -> impacted cross-system journey
```

The selector may compose existing module/dependency, OTBM Semantic Diff and scenario ownership evidence but must fail closed when impact is unknown. It must not infer dependency edges from filenames alone when no reviewed mapping exists.

---

## E2E-QRI-021 — Crash artifact bundle

**Workstream:** diagnostics

**Default tier:** automatically on Canary/OTClient crash where supported.

**Goal:** retain a bounded crash evidence bundle tied to the scenario result.

Candidate contents:

- crash process identity and revision;
- sanitized stack/backtrace or minidump reference;
- last successful and first failing step;
- actor and position;
- bounded server/client log tails;
- route/fault context;
- DB assertion/cleanup state;
- replay identity when available.

Large core/minidump files remain workflow artifacts and must not be committed.

---

## E2E-QRI-022 — Flake and stability certification

**Workstream:** test intelligence / operational quality

**Default tier:** nightly and pre-release.

**Goal:** measure repeatability instead of hiding instability behind retries.

For each selected scenario, record across clean executions:

- run count;
- pass/fail count;
- success ratio;
- failure-class distribution;
- latency distribution for key phases;
- cleanup failures;
- first divergence frequency.

A scenario such as `9/10 pass` is `unstable`, not equivalent to a clean pass. Automatic retry may collect evidence but must preserve every original failure.

---

## E2E-QRI-023 — Long-running soak E2E

**Workstream:** operational reliability

**Default tier:** nightly/weekly/on-demand; never every PR.

**Goal:** detect leaks and state accumulation over repeated normal gameplay lifecycles.

Candidate cycle:

```text
login
route
bounded combat or feature action
inventory/container interaction
safe logout
relog
assert persistence
cleanup
repeat
```

Collect bounded trends such as:

- Canary/OTClient memory;
- CPU utilization;
- DB connection counts;
- file descriptors/handles where supported;
- online-player/session counts;
- per-cycle latency;
- cleanup certification.

Soak thresholds require baseline evidence and must account for normal caches/warm-up rather than using arbitrary numbers.

---

## E2E-QRI-024 — Performance regression E2E

**Workstream:** operational performance

**Default tier:** nightly trend plus selected release/PR guardrails.

**Goal:** detect material runtime regressions in stable representative scenarios.

Candidate metrics:

- login latency;
- world-entry latency;
- route-step or route-completion latency;
- NPC response latency;
- save/logout latency;
- relog latency;
- selected SQL/persistence assertion latency;
- resource usage where comparable.

Use pinned environments and statistical/baseline rules. A single noisy run should not become an arbitrary hard gate.

---

## E2E-QRI-025 — Canary/OTClient compatibility matrix

**Workstream:** compatibility

**Default tier:** nightly and release certification.

**Goal:** prove selected supported combinations rather than assuming server/client head compatibility.

Candidate matrix:

- Canary candidate x OTClient stable;
- Canary candidate x OTClient candidate/head where explicitly authorized;
- Canary stable/baseline x OTClient candidate for client-side regression isolation.

Use exact pinned revisions and the existing cross-repository contract rules. A matrix cell must be marked unsupported/blocked rather than silently skipped when artifacts are unavailable.

---

## E2E-QRI-026 — Datapack compatibility matrix

**Workstream:** compatibility

**Default tier:** nightly/release smoke.

**Goal:** run a small approved smoke set against each supported datapack/profile without duplicating workflows.

Candidate smoke capabilities:

- startup/readiness;
- login/world entry;
- one movement/navigation check where fixture evidence exists;
- one representative feature assertion owned by that datapack;
- safe logout/relog/cleanup.

Do not assume feature fixtures or coordinates are portable between datapacks; each cell needs explicit compatible fixture evidence.

---

## E2E-QRI-027 — Database migration and upgrade E2E

**Workstream:** release reliability

**Default tier:** release certification and migration PRs.

**Goal:** prove upgrade of an approved old schema/fixture state into the candidate Canary revision, followed by real-client gameplay and persistence.

Reference shape:

```text
bootstrap approved historical schema/fixture
run canonical migration path
start candidate Canary
login existing character
exercise selected gameplay/persistence surfaces
safe logout/relog
assert migrated durable state and invariants
```

Candidate domains include characters, storages, depot/inbox, houses, guilds and market only when deterministic repository-owned fixtures exist.

Historical fixtures must be sanitized, versioned and repository-authorized; never use a production dump.

---

## E2E-QRI-028 — Release certification gold suite

**Workstream:** release operations

**Default tier:** explicit release-candidate gate.

**Goal:** define a compact high-value certification set instead of running every scenario indiscriminately.

Initial target categories:

- login/world entry/relog;
- movement and OTBM-aware route execution;
- NPC/quest vertical slice;
- deterministic combat;
- persistence;
- economy/trade multi-client;
- exactly-once sentinel;
- restart recovery;
- cleanup certification;
- supported migration smoke;
- supported client/server compatibility cells;
- supported datapack smoke cells.

A gold suite is a reviewed selection of independently maintained focused scenarios. It must not become one giant monolithic scenario or replace lower-level feature tests.

# Cross-package dependency guidance

Recommended dependency order:

```text
Delivered 001..008 foundation
        |
        +--> QRI-005 result envelope ----> QRI-004 coverage dashboard
        |          |                       QRI-016 replay
        |          |                       QRI-021 crash bundle
        |          +---------------------> QRI-017 minimizer
        |
        +--> QRI-006 cleanup certification
        |
        +--> QRI-001 real trade ----------> QRI-009 exactly-once
        |                                   QRI-010 concurrency
        |
        +--> QRI-002 Canary restart ------> QRI-012 save/restart consistency
        |                                   QRI-011 DB interruption
        |
        +--> QRI-003 Journey 002
        +--> QRI-007 UI assertions
        +--> QRI-008 snapshot/restore ----> QRI-015 differential
        |                                   QRI-017 minimizer
        |                                   QRI-009/QRI-010 repeatability
        |
        +--> QRI-014 invariants ----------> QRI-018 seeded fuzzing
        +--> QRI-019 state-machine misuse
        +--> QRI-020 dependency selection
        |
        +--> QRI-022 stability certification
        +--> QRI-023 soak
        +--> QRI-024 performance
        +--> QRI-025 client/server matrix
        +--> QRI-026 datapack matrix
        +--> QRI-027 migration E2E
                    |
                    v
             QRI-028 release gold suite
```

This graph is sequencing guidance, not permission to start every package immediately. Each implementation task must verify current `main`, concrete consumer demand, ownership and dependencies.

# Recommended first implementation wave

The highest-value first wave after this roadmap is:

1. `E2E-QRI-005` standard result envelope and richer first-failure evidence;
2. `E2E-QRI-006` cleanup certification;
3. `E2E-QRI-001` real two-player trade + persistence;
4. `E2E-QRI-002` Canary restart/reconnect recovery;
5. `E2E-QRI-003` broader representative Journey 002;
6. `E2E-QRI-004` factual M0-M5 + quality-dimension coverage dashboard;
7. `E2E-QRI-022` flake/stability certification after the selected scenarios are stable enough to measure.

The transactional/resilience wave should then prioritize `E2E-QRI-008`, `009`, `010`, `011` and `012`.

The intelligence wave should prioritize `E2E-QRI-015`, `016`, `017`, `014`, `018`, `019`, `020` and `021`.

The operational/release wave should prioritize `E2E-QRI-023` through `028`.

# Safety requirements for fault and stress work

Any package involving faults, restart, DB interruption, concurrency, fuzzing or soak must satisfy all of the following:

- literal isolated/disposable targets only;
- explicit bounded fixture and actor identities;
- fixed-purpose code-owned fault/action vocabulary;
- no arbitrary host, command, SQL or packet-payload surface;
- declared fault phase and expected result before execution;
- bounded timeout;
- cleanup attempt on success and failure;
- retained first-failure evidence;
- no production/staging mutation;
- no external third-party system;
- no hidden retries that erase instability evidence.

# Scenario-selection and cost policy

The mature platform should minimize cost by running the smallest evidence-backed relevant suite:

1. direct changed-scenario ownership;
2. reviewed module/dependency impact;
3. OTBM Semantic Diff/mechanic impact where applicable;
4. explicitly registered cross-system journey dependencies;
5. release/scheduled policies.

When impact cannot be determined safely, selection fails closed to a broader approved suite rather than silently skipping validation.

# Completion definition for this roadmap phase

This roadmap is not complete when every package has merely a document or synthetic unit test. A mature implementation should eventually provide:

- at least one real two-player feature with durable persistence proof;
- controlled Canary restart recovery;
- one broader representative navigation/depot/NPC-or-quest/combat/reward/persistence journey;
- standardized result and cleanup evidence;
- factual M0-M5 plus orthogonal quality-dimension coverage reporting;
- stability certification for the gold scenarios;
- at least one exactly-once and one deterministic concurrency proof;
- at least one safe infrastructure-fault recovery proof beyond client disconnect;
- deterministic replay and minimization for eligible failures;
- differential runtime evidence for selected high-risk changes;
- bounded reproducible fuzz/state-machine robustness coverage;
- soak and performance trend evidence;
- supported client/server, datapack and migration certification cells;
- one reviewed release gold suite assembled from focused independently owned scenarios.

No package may claim delivery solely because it appears in this roadmap. Runtime capability and evidence claims require their own bounded task, exact-head validation and physical proof where applicable.
