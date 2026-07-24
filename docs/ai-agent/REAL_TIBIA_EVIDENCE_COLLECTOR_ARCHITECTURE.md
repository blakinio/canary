# Real Tibia Evidence Collector Architecture

## Status

Architecture and governance contract for a future deterministic Real Tibia evidence-collection system in `blakinio/canary`.

This document defines what the Collector must know, record, request and preserve before any broad 62-module evidence campaign starts. It does not implement a collector executable, create module dossiers, run gameplay tests, parse maps or authorize runtime changes.

## Problem

The repository already contains strong but distributed evidence systems:

- a canonical 62-module Real Tibia registry;
- source precedence and proof-level rules;
- module programmes and validation reports;
- Universal Physical E2E;
- OTBM World Index, Script Resolution, Reachability, Semantic Diff and certification;
- official-client reference parsing and correlation through TCR;
- upstream/donor monitoring;
- historical point-in-time forum and official-source analyses.

The missing layer is a durable, repeatable process that can gather and normalize module-specific facts, explain detailed behavior, preserve historical version changes, compare those facts with current Canary and ask the correct owning programme for missing proof without creating duplicate tooling.

## Goals

The Collector must enable an agent to answer, for every bounded mechanic:

1. What does current Real Tibia visibly and officially do?
2. In which version was the behavior announced, introduced, changed, deprecated or removed?
3. What does the exact current Canary baseline do?
4. Which dimensions agree, differ, conflict or remain unknown?
5. What implementation or architecture decision follows from the evidence?
6. Why is that decision defensible?
7. Which alternative was rejected and on what evidence?
8. Which E2E, OTBM, TCR, protocol, persistence or feature-owner proof is still needed?
9. What exactly may be claimed now, and what must not be claimed?

## Non-goals

The Collector is not:

- an autonomous gameplay implementation agent;
- a second Real Tibia registry;
- a replacement for module programmes or validation reports;
- an E2E runner or scenario platform;
- an OTBM parser, pathfinder, renderer or certifier;
- a TCR parser or client-asset importer;
- a packet sniffer or maintained-client owner;
- a web scraper that stores unbounded copied content;
- a hidden-reasoning archive;
- an opaque parity score;
- authority to import CrystalServer or upstream code;
- authority to merge, deploy or promote a release based only on documentation.

## Core principle: claim-oriented evidence

The atomic unit is not a webpage, file or module. The atomic unit is a bounded claim.

Examples:

- `weekly-task-generation-is-character-scoped`;
- `quest-reward-is-granted-exactly-once`;
- `spell-area-changed-in-version-X`;
- `client-field-order-for-feature-Y`;
- `house-layout-origin-for-reference-Z`;
- `boss-cooldown-persists-through-relog`.

Each claim has:

- one primary module;
- optional related modules;
- an authority dimension;
- exact source references;
- source and observation dates;
- version applicability;
- a concise factual statement;
- conditions and exceptions;
- what the evidence proves;
- what it does not prove;
- evidence state and proof level;
- conflicts and superseding records;
- current Canary comparison;
- required owner requests;
- freshness metadata.

Large sources must be decomposed into claims. One source may support many claims. One claim may require several sources.

## Evidence authority dimensions

### Official feature identity

Use exact official Tibia news, update notes, game guides and direct official staff clarifications.

Proves:

- feature name;
- public release existence;
- officially described purpose;
- announced or documented visible rules;
- official chronology.

Does not prove:

- hidden formulas;
- packet layout;
- server persistence;
- exact map attributes;
- final live behavior when later release changes superseded the preview.

### Visible gameplay behavior

Use reproducible official-client observation, preferably repeated under controlled conditions and reconciled with official material.

Record:

- client build;
- world type and relevant configuration;
- character state;
- exact preconditions;
- action sequence;
- observed result;
- repetitions;
- known confounders;
- capture hashes or references kept outside Git.

A screenshot is evidence of visible state at one moment. It is not persistence, rollback, authorization or server-state proof.

### Current Canary behavior

Use exact `blakinio/canary` commit, active registrations, code paths, tests, runtime evidence, database schema and migration state.

Record separately:

- definition;
- registration;
- runtime path;
- persistence;
- protocol;
- behavior test;
- physical gameplay proof.

Source similarity or matching names do not establish runtime equivalence.

### Protocol and maintained-client behavior

Use byte-exact tests, controlled captures and exact maintained `blakinio/otclient` code/build when authorized as evidence.

The maintained client may prove field interpretation, width/order, capability gates and UI reaction. It does not prove server authorization, atomicity or formulas.

### Persistence and rollback

Use current Canary load/save code, schema, migrations, transaction boundaries, failure-injection tests, round trips, restart/relog evidence and corruption/legacy-state behavior.

The Collector must explicitly ask:

- what is the storage scope: account, character, world, guild, house or session?
- when is state committed?
- what happens after partial failure?
- can an action be repeated?
- is settlement exactly once?
- what happens after disconnect, relog, restart or server save?
- how are old rows migrated or rejected?

### Map geometry and mechanics

Geometry, walkability and mechanic semantics are separate dimensions.

Geometry authority may use official-client-derived minimap data and repeated observation. Mechanics require canonical OTBM evidence, handler resolution and, where needed, runtime proof.

Never infer from a visual map:

- item stack order;
- AID/UID;
- teleport destination;
- house metadata;
- spawn/NPC placement;
- quest logic;
- active handlers.

### Implementation candidates

Pinned upstream Canary or CrystalServer may supply architecture and implementation candidates.

Every candidate must state:

- exact repository and SHA;
- selected paths/symbols;
- candidate behavior unit;
- required Canary APIs and assumptions;
- whether Canary already has an equivalent or safer implementation;
- official/independent evidence supporting the behavior;
- deterministic failing test or proof boundary;
- reason for reuse, adaptation or rejection.

A donor is never the authority for current Real Tibia.

## Detailed module behavior model

Every module dossier must describe how the system works, not only list facts.

### Scope and boundary

Define:

- module purpose;
- included behavior;
- excluded behavior;
- owning server/client/map/datapack components;
- external dependencies;
- security and trust boundary;
- actor types.

### Inputs and outputs

Record:

- player actions;
- client messages;
- timers and server-save triggers;
- world events;
- item/NPC/map interactions;
- database state;
- configuration and feature gates;
- outputs visible to player, client, server and database.

### State model

Define named states and all known transitions.

Example form:

```text
state A
  -- trigger + conditions --> state B
  effects:
    - server mutation
    - database mutation
    - client response
    - world effect
  failure:
    - rollback or retained partial state
```

For every transition record:

- trigger;
- authorization;
- preconditions;
- guards;
- consumed resources;
- generated resources;
- in-memory changes;
- persisted changes;
- packets/UI updates;
- map/world dependencies;
- repeatability/idempotency;
- timeout/cooldown;
- failure behavior;
- concurrency behavior;
- relevant versions;
- supporting evidence IDs.

### Rules, formulas and values

Each numeric or categorical rule is its own claim or referenced claim group.

Do not write one unaudited paragraph containing many values. Values must be independently sourceable because they may change in different releases.

Record:

- units;
- rounding;
- min/max/caps;
- order of operations;
- random distribution or selection rule;
- level/vocation/world modifiers;
- party and PvP/PvE differences;
- server-save/time-zone boundary;
- historical value changes;
- current Canary value and exact source path.

Hidden formulas remain `UNKNOWN` unless reproducible evidence establishes a bounded model. Approximation must be labelled and must not be used as exact parity authority.

### Persistence model

Document:

- canonical state owner;
- table/column/storage key or abstract persistence contract;
- load timing;
- save timing;
- transaction boundary;
- migration path;
- legacy/missing/corrupt state;
- duplicate and stale writes;
- exactly-once and retry behavior;
- rollback and recovery;
- relog/restart/server-save behavior;
- concurrent actor behavior.

### Protocol and client model

Document:

- relevant opcodes/messages;
- capability/version gates;
- field ordering and widths;
- optional fields;
- malformed/unsupported behavior;
- client UI state;
- login/relog resynchronization;
- backward compatibility;
- server/client rollout ordering.

No packet bytes may be invented. Missing packet evidence becomes a protocol-owner request.

### Map/content model

Document applicable:

- exact positions and bounds only when proven;
- towns, regions, zones, houses and floors;
- item/appearance identifier namespaces;
- AID/UID/teleport/door/transition mechanics;
- NPC, spawn, boss and raid dependencies;
- quest/storage/item dependencies;
- route and reachability requirements;
- current map/index provenance;
- static versus physical proof boundary.

### Failure and edge-case model

At minimum evaluate:

- repeated action/double click;
- disconnect during action;
- relog before/after settlement;
- server restart;
- server save;
- full inventory or missing capacity;
- missing item/NPC/spawn/map handler;
- duplicate reward;
- death;
- party membership change;
- multi-client/concurrent actors;
- stale database state;
- unsupported client;
- malformed packet;
- map/datapack mismatch;
- feature disabled or partially deployed.

### Security and abuse model

Record:

- server-side authorization;
- client-trust assumptions;
- replay and duplicate request behavior;
- economy duplication risk;
- rate/cooldown bypass;
- account/character scope escalation;
- visibility versus authority;
- cross-channel/multiwriter behavior where applicable.

## Version history architecture

Version history is first-class because a faithful current implementation must also understand historical changes and compatibility boundaries.

### Separate version axes

Do not use one `version` field for the entire server.

Track separately:

- official Tibia release/update identifier;
- official client build;
- protocol compatibility profile;
- Canary commit/release;
- maintained OTClient commit/build;
- datapack revision;
- map SHA-256;
- items/appearances revision;
- spawn/NPC sidecar revision;
- database schema/migration revision.

### Event types

Every history entry uses one of:

- `announced`;
- `introduced`;
- `enabled`;
- `changed`;
- `rebalanced`;
- `fixed`;
- `deprecated`;
- `compatibility-only`;
- `disabled`;
- `removed`;
- `observed`;
- `unknown-first-version`.

### Evidence confidence

Each version event is:

- `proven-official`;
- `proven-observation`;
- `supported-secondary`;
- `derived-range`;
- `conflicting`;
- `unknown`.

A `derived-range` may say the change occurred after version A and by version B, but must not invent the exact release.

### Supersession

New records do not overwrite historical claims. They reference superseded evidence and preserve the valid applicability interval.

This supports future comparisons such as:

- Canary matches Tibia 15.00 behavior but not current 15.25 behavior;
- protocol profile retains old field shape intentionally;
- map content predates server/client protocol target;
- a donor candidate implements an older rule that official material later changed.

## Decision and rationale records

Detailed rationale is required, but private chain-of-thought is not stored.

A durable decision contains:

- decision ID and status;
- bounded question;
- chosen option;
- factual constraints;
- evidence references;
- trade-offs;
- compatibility consequences;
- rejected alternatives and concrete rejection reasons;
- unknowns that remain;
- required tests and owner requests;
- rollback/revisit trigger.

Good rationale:

```text
Choose transactional settlement after state persistence because the current
Canary architecture supports one atomic boundary, the official visible result
requires exactly-once reward behavior, and failure before commit must not grant
a duplicate reward. Reject pre-save reward mutation because a crash between
reward and state commit creates a reproducible duplication window.
```

Bad rationale:

```text
The agent thought for a long time and preferred option A.
```

## Evidence record lifecycle

States:

1. `discovered`;
2. `normalized`;
3. `review-needed`;
4. `accepted`;
5. `conflicting`;
6. `blocked-by-owner-request`;
7. `superseded`;
8. `rejected`;
9. `stale`.

Transitions require explicit reason and actor/task/PR reference.

An accepted record may still have low proof level. Acceptance means the record accurately describes its bounded evidence, not that parity is proven.

## Evidence request lifecycle

Requests are compact contracts between the Collector and an owning programme.

States:

- `draft`;
- `ready-for-owner-triage`;
- `accepted-by-owner`;
- `planned`;
- `active`;
- `blocked`;
- `result-available`;
- `consumed`;
- `rejected`;
- `superseded`.

Every request identifies:

- exact question;
- requested owner programme;
- required evidence dimension and minimum level;
- why existing evidence is insufficient;
- source claim IDs;
- inputs/provenance available to owner;
- requested output contract;
- paths Collector may not edit;
- priority and version impact;
- blocking status;
- result references when complete.

The Collector cannot set `accepted-by-owner`, `active` or `result-available` without owner evidence.

## Integration with Universal E2E

### Collector to E2E

The Collector should provide a scenario request, not a platform patch.

A good request says:

- observable behavior to prove;
- setup state;
- action sequence;
- server/client/SQL/UI assertions required;
- required relog/restart/recovery scope;
- minimum M0-M5 maturity;
- relevant version/capability matrix;
- evidence IDs and unknowns;
- whether a generic platform capability appears missing.

The feature programme remains responsible for feature-specific fixtures, actions and expected values. The E2E platform programme remains responsible for generic lifecycle and interfaces.

### E2E to Collector

The Collector consumes stable:

- scenario ID;
- owning programme;
- exact server/client revisions;
- result envelope version;
- run/job/artifact identifiers;
- maturity reached;
- orthogonal quality dimensions;
- first failure;
- cleanup result;
- freshness;
- explicit proof/nonproof statement.

A successful physical action is not automatically persistence, concurrency, compatibility or recovery proof.

### Suggested future E2E capabilities

The Collector may record suggestions when repeated gaps appear:

- deterministic official-observation comparison envelopes;
- reusable visible-UI assertion primitives;
- controlled clock/server-save advancement;
- exact server restart and post-restart state checks;
- generalized state-delta assertions across SQL/server/client/UI;
- supported-version compatibility matrices;
- deterministic packet/event capture references;
- scenario parameterization by historical compatibility profile;
- cross-module journey dependency reporting.

These are proposals only. E2E owners decide whether and how to implement them.

## Integration with OTBM/OWA

### Collector to OTBM/OWA

A map evidence request identifies:

- selected module and mechanic;
- exact current/candidate map provenance if known;
- positions/bounds/landmarks only when already reviewed;
- required World Index fields;
- required Script Resolution findings;
- Reachability or route question;
- Semantic Diff need;
- certification/coverage dimension;
- runtime proof still required after static evidence.

### OTBM/OWA to Collector

The Collector consumes exact stable outputs and preserves:

- source map hash;
- index/report format and hash;
- finding IDs/pointers;
- `resolved`, `partial`, `conflicting`, `unresolved`, `stale` states;
- certification level and independent coverage dimensions;
- proof/nonproof boundary;
- freshness and invalidation dependencies.

The Collector must not convert static success into gameplay success.

### Suggested future OTBM/OWA capabilities

The Collector may record:

- recurring evidence selector types absent from QA-018;
- module-to-map dependency mappings needed for freshness;
- reviewed certification target classes needed by repeated dossiers;
- stable TCR drift outputs that should invalidate selected QA dimensions;
- compact map evidence packages needed by E2E scenario preflight.

OTBM/OWA owners decide implementation.

## Integration with TCR

The Collector references exact stable TCR contracts for:

- package provenance;
- StaticData registries;
- StaticMapData layouts;
- proficiency data;
- appearance/assets coverage;
- content registry correlation;
- stable parity/drift findings.

Identifier spaces remain distinct until exact reviewed mapping proves a join.

The Collector may request new TCR coverage only by defining:

- missing client-reference dimension;
- exact user-supplied external input class;
- expected normalized output;
- downstream module claim;
- security/proprietary-data boundary;
- why existing TCR outputs are insufficient.

## Cross-module dependency model

A claim may be primary to one module and referenced by others. Do not copy the claim into several dossiers.

Example:

- one `player-persistence` claim owns character-scoped exactly-once state;
- `quests`, `achievements` and `prey` reference it;
- module-specific claims add their own keys, transitions and visible outcomes.

Dependencies must be one of:

- `requires`;
- `consumes`;
- `produces`;
- `authorizes`;
- `persists-through`;
- `represented-by-client`;
- `located-on-map`;
- `validated-by`;
- `conflicts-with`;
- `supersedes`.

Unproven dependency edges remain review-needed.

## Concurrency design

### Why not 62 agents

Launching one agent per module would create:

- excessive duplicate source collection;
- shared-path conflicts;
- inconsistent terminology and version baselines;
- GitHub Actions/storage pressure;
- reviewer overload;
- uncontrolled E2E/OTBM request queues;
- premature claims from uneven evidence quality.

### Recommended topology

```text
1 Coordinator
  ├── up to 8 Collector workers
  ├── up to 2 evidence reviewers
  └── owner request queues
       ├── Universal E2E
       ├── OTBM/OWA
       ├── TCR
       ├── protocol/client
       └── feature programmes
```

### Hard defaults

- maximum eight simultaneous Collector workers;
- maximum four open Collector worker PRs;
- one module dossier or one bounded behavior package per worker;
- one branch/worktree/task/PR per worker;
- shared schema/program/index files coordinator-only;
- no worker edits owner-programme implementation paths;
- no more than one active Collector request touching the same exact behavior/identifier/version tuple;
- coupled module groups require a coordination ID and explicit ordering.

### Parallel-safe work

Usually parallel-safe when paths and claims are independent:

- separate module dossiers;
- unrelated historical source collection;
- independent official release timelines;
- separate formula/value families;
- review of already merged stable owner outputs;
- secondary source reconciliation with no shared records.

### Work requiring serialization

- schema/template changes;
- programme queue changes;
- generated indexes;
- source taxonomy changes;
- one shared protocol family;
- one shared persistence state;
- one map region/mechanic package;
- one client-reference identifier mapping;
- one cross-module decision record;
- any owner request already active.

### Wave planning

The Coordinator selects waves after checking:

- module dependencies;
- source availability;
- open owner requests;
- shared identifiers;
- current PR ownership;
- freshness urgency;
- current Tibia release changes;
- current Canary roadmap priorities;
- CI/storage/reviewer capacity.

A recommended first campaign uses a low-coupling pilot before eight-worker operation. The default cap may be reduced immediately. Increasing above eight requires an explicit experiment and durable evidence that ownership, CI and review remain safe.

## Proposed repository structure

```text
docs/agents/real-tibia/evidence/
├── README.md
├── modules/
│   └── <module-id>/
│       ├── MODULE.md
│       ├── BEHAVIOR_MODEL.md
│       ├── VERSION_HISTORY.yaml
│       ├── EVIDENCE_INDEX.yaml
│       ├── DECISIONS.md
│       ├── GAPS_AND_REQUESTS.yaml
│       ├── records/
│       │   └── RT-<MODULE>-NNNN.yaml
│       └── reviews/
│           └── <review-id>.md
├── requests/
│   ├── e2e/
│   ├── otbm/
│   ├── tcr/
│   ├── protocol/
│   └── feature/
└── shared/
    ├── glossary.yaml
    ├── claim-links.yaml
    └── version-baselines.yaml
```

Only a later implementation task may create this tree broadly. Empty directories and placeholder dossiers are forbidden.

## Validation architecture for future tooling

A future RTEC-001 implementation should provide deterministic standard-library tooling where practical:

- schema validation;
- unique evidence/request/decision IDs;
- module ID validation against the canonical registry;
- source ID validation against the existing source registry;
- version-axis validation;
- applicability interval checks;
- supersession cycle detection;
- duplicate claim fingerprint warnings;
- cross-module reference validation;
- evidence-level monotonicity checks;
- owner-request state validation;
- freshness/staleness selection;
- deterministic Markdown/index generation;
- changed-module selection;
- no-network unit tests using synthetic fixtures.

The tool must not browse sources, execute E2E, parse OTBM/TCR inputs or determine gameplay truth automatically.

## Review contract

Every worker PR requires review of:

- exact module/package scope;
- source provenance and dates;
- version-history correctness;
- claim decomposition;
- proof and nonproof boundaries;
- Canary baseline freshness;
- conflicts and unknowns;
- duplicate claims;
- owner-request correctness;
- no owner-path edits;
- no proprietary/large source material committed;
- no invented values, IDs, packet fields, coordinates or formulas.

The reviewer may accept a record containing unknowns. The reviewer must reject a record that hides or guesses them.

## Completion semantics

### Record complete

A record is structurally valid, source-pinned, reviewed and explicit about proof limits.

### Dossier complete

Every required dossier section is populated or explicitly marked `not-applicable`, `UNKNOWN`, `CONFLICT`, `STALE` or `blocked-by-owner-request`.

### Module evidence mature

The dossier has current evidence at the appropriate levels for the module's required dimensions.

### Module parity proven

All bounded required behaviors and dependencies are proven against the selected current official baseline with current compatible Canary evidence.

### Whole-game faithful reproduction

This remains a separate, much stronger claim. It requires compatible evidence across all modules, cross-module journeys, supported versions, persistence, protocol, map/content, resilience and physical-client behavior. The Collector cannot award this status automatically.

## Safety invariants

- Write only to `blakinio/canary` through task branches and PRs.
- Treat upstream, donors and maintained-client repositories as read-only unless separately authorized.
- Never commit proprietary client packages, binaries, maps, captures, credentials, database dumps or large generated reports.
- Record URL, author/date, filename, byte size and SHA-256 for external downloads retained outside Git.
- Never infer a Tibia version from a filename, donor branch, OTBM label or directory.
- Never infer identifier equivalence across namespaces.
- Never promote static evidence into runtime/gameplay evidence.
- Never turn forum frequency into numeric authority.
- Never hide source conflict, missing pages or unavailable fixtures.
- Never create parallel E2E, OTBM, TCR or registry infrastructure.
- Never implement a gameplay change directly from an unreviewed Collector record.

## First implementation recommendation

After this architecture merges:

1. implement RTEC-001 schemas, validator and deterministic indexes;
2. select one low-coupling pilot module after fresh preflight;
3. create one complete dossier and at least one owner request if genuinely needed;
4. review the data model and workflow;
5. run a two-worker concurrency experiment;
6. expand gradually to the default eight-worker/four-PR cap;
7. only then begin broad 62-module waves.
