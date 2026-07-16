---
task_id: CAN-20260715-tibia-system-decomposition-conversation-handoff
status: completed
kind: conversation-handoff
created: 2026-07-15
program_id: CAN-PROGRAM-TIBIA-SYSTEM-DECOMPOSITION
base_main_sha: "9fc11e04dc5040d1ea18d02e15dac1df47f3fe64"
owned_paths: []
shared_paths: []
read_only_paths:
  - docs/agents/real-tibia/**
  - docs/agents/programs/**
  - docs/agents/tasks/**
  - tools/agents/**
---

# Tibia System Decomposition conversation handoff

## Purpose

This archive preserves the durable context of the ChatGPT workstream that designed, reviewed and then autonomously advanced the Tibia/Canary system decomposition program from bootstrap through final closure.

It is a handoff for a future agent. It is not an active task, does not claim path ownership, and does not authorize further work inside the completed decomposition program.

## Repository and source boundaries

Writable repository used by this workstream:

- `blakinio/canary`.

Read-only reference/upstream repositories supplied for the wider project:

- `opentibiabr/canary`;
- `opentibiabr/otclient`;
- `opentibiabr/remeres-map-editor`;
- `opentibiabr/client-editor`.

CrystalServer may be used as donor/comparison evidence where an explicitly bounded task authorizes it, but donor code is not official Real Tibia behavior and must not be written to.

Never write to upstream/reference repositories from this workstream.

## User-level project intent

The legacy `blakinio/canary` repository is the development and evidence laboratory.

The long-term target is a clean new OTS engine/repository, Oteryn, based on then-current upstream Canary and populated selectively with components that have been audited, validated and proven sufficiently for migration.

Do not bulk-copy the legacy repository into Oteryn.

The intended future flow is:

```text
legacy inventory
-> evidence
-> deterministic validation
-> runtime proof
-> physical-client E2E where applicable
-> target-architecture comparison
-> migration classification
-> bounded Oteryn migration package
```

The user prefers autonomous execution by one capable agent across sequential bounded tasks, while still requiring a new task, branch and PR for each logical package and lifecycle-only archival after merge.

## Live state at handoff creation

Exact `main` used as the base of this handoff:

```text
9fc11e04dc5040d1ea18d02e15dac1df47f3fe64
feat(e2e): bootstrap universal agent test platform (#245)
```

Immediately preceding relevant main commits include:

```text
32b536abb3f65bfb9bfd5c049f3413ce7c46880d
  docs(agents): archive Oteryn migration classification (#380)

e3b08e36c503a36b0eb47696e50567155050c757
  docs(agents): classify Oteryn migration disposition (#379)
```

At handoff creation the only open PR found in `blakinio/canary` was draft PR #316:

```text
audit(otbm): isolate bounded Targuna donor clusters
```

PR #316 is independent of Tibia System Decomposition. It reuses existing OTBM tooling and must not be modified, absorbed or superseded by a future Oteryn/decomposition agent without a fresh ownership review.

## Final state of CAN-PROGRAM-TIBIA-SYSTEM-DECOMPOSITION

Canonical program file:

```text
docs/agents/programs/TIBIA_SYSTEM_DECOMPOSITION_PROGRAM.md
```

Final status:

```text
completed
```

The program explicitly states that no further package remains in `CAN-PROGRAM-TIBIA-SYSTEM-DECOMPOSITION`.

The canonical Real Tibia registry remains the only module source of truth:

```text
docs/agents/real-tibia/registry/**
```

Generated indexes remain derived artifacts and must not become a second registry.

Final canonical registry size:

```text
62 module records
```

The program started from 19 records and ended at 62.

All canonical modules received the final Oteryn migration disposition:

```text
REVALIDATE
```

This is deliberately conservative. `REVALIDATE` is not permission to copy, port, reuse, rewrite or drop a module.

No code was copied to Oteryn.

No module is declared Oteryn-ready.

`cross_repo_contracts` remained empty at program closure. Any stronger migration decision requires a new bounded task/program with an explicit Oteryn target repository, exact target baseline and target architecture contract.

## Completed package sequence

### TSD-001 — taxonomy and hierarchy foundation

Feature PR #335, lifecycle PR #336.

Registry:

```text
19 -> 22
```

Added:

- `engine-runtime-lifecycle`;
- `configuration`;
- `lua-runtime`.

The work established umbrella/child conventions, conservative maturity rules, discovery path rules and a classified candidate inventory rather than blindly creating hundreds of records.

### UI-001A prerequisite — source-role-aware Upstream Intelligence mapping

Feature PR #337, lifecycle PR #338.

This fixed the source-unaware path mapping problem discovered during TSD-001.

The existing mapper now uses source-registry policy to select permitted path buckets. It distinguishes server, client and editor source policies and does not silently fall back to all buckets for missing/unsupported context.

Important preserved rules:

- mapping is discovery-only;
- path matches do not prove ownership, defects, equivalence or parity;
- `triage_status` remains `needs-triage` until reviewed;
- external repositories remain read-only;
- no second mapper or source registry was created.

### TSD-002A — engine foundation

Feature PR #340, lifecycle PR #341.

Registry:

```text
22 -> 26
```

Added:

- `build-system`;
- `engine-scheduler`;
- `engine-service-container`;
- `lua-bindings`.

`data-registries` and `platform-compatibility` were intentionally not promoted into independent records where existing boundaries were more appropriate.

### TSD-002B — persistence and transactions

Feature PR #342, lifecycle PR #347.

Registry:

```text
26 -> 29
```

Added:

- `database-connection`;
- `database-migrations`;
- `world-persistence`.

`transaction-boundaries` remained a DB-core/call-site capability rather than an artificial helper-class module. Generic reconciliation was deferred and restart/reload remained a cross-module validation concern.

No transactionality, idempotency, crash consistency or restart safety was claimed from inventory evidence.

### TSD-003 — account, character and progression

Feature PR #355, lifecycle PR #358.

Registry:

```text
29 -> 35
```

Added:

- `account-lifecycle`;
- `account-authentication`;
- `character-lifecycle`;
- `character-progression`;
- `vocations`;
- `weapon-proficiency`.

Levels, skills, magic level, stamina, offline training, death loss and blessings remained capabilities/findings inside broader durable lifecycles rather than micro-modules.

### TSD-004 — Cyclopedia family

Feature PR #359, lifecycle PR #361.

Registry:

```text
35 -> 39
```

Added:

- `bestiary`;
- `bosstiary`;
- `cyclopedia-character`;
- `titles`.

The broad `cyclopedia` record remains an umbrella/discovery boundary.

Bosstiary, boss encounters and physical spawning remain separate concerns.

### TSD-005 — combat, weapons and vocations

Feature PR #362, lifecycle PR #363.

Registry:

```text
39 -> 41
```

Added:

- `combat-conditions`;
- `weapons`.

Targeting, PvP permissions, damage/healing, mitigation, critical/leech and similar surfaces remained capabilities inside the existing `combat` umbrella where current evidence did not justify independent durable modules.

### TSD-006 — creatures, hunting, raids and bosses

Feature PR #364, lifecycle PR #365.

Registry:

```text
41 -> 45
```

Added:

- `boss-encounters`;
- `creature-ai`;
- `creature-definitions`;
- `raids`.

Existing `spawns`, `prey`, `bestiary`, `bosstiary` and related records remained separate.

Physical spawn, encounter lifecycle, Bosstiary classification/credit and reward eligibility must not be collapsed into one subsystem.

### TSD-007 — items and economy

Feature PR #366, lifecycle PR #367.

Registry:

```text
45 -> 49
```

Added:

- `containers`;
- `item-decay`;
- `item-definitions`;
- `item-instances`.

Existing `market`, `imbuements`, `exaltation-forge` and other established boundaries were not duplicated.

### TSD-008 — world content

Feature PR #368, lifecycle PR #369.

Registry:

```text
49 -> 52
```

Added:

- `instances`;
- `world-map-runtime`;
- `world-zones`.

Important boundary:

```text
offline OTBM tooling
!= runtime world map
!= zones
!= instances
```

No second OTBM parser, renderer or map writer was introduced.

### TSD-009 — social, communication and trust

Feature PR #370, lifecycle PR #371.

Registry:

```text
52 -> 56
```

Added:

- `chat-communication`;
- `guilds`;
- `parties`;
- `sanctions`.

Planned AI/security concepts such as `chat-safety-intelligence`, `security-analytics` and `ai-investigation` were not falsely registered as implemented systems.

### TSD-010 — protocol and client

Feature PR #372, lifecycle PR #373.

Registry:

```text
56 -> 60
```

Added:

- `login-protocol`;
- `network-transport`;
- `protocol-compatibility`;
- `protocol-session-handoff`.

The broad `protocol` record remains an umbrella.

A matching parser, serializer, class name, compile result or unit test is not wire-compatibility proof.

### TSD-011 — analytics, security and AI

Feature PR #374, lifecycle PR #376.

Registry:

```text
60 -> 61
```

Added only:

- `gameplay-analytics`.

Planned `security-analytics`, `chat-safety-intelligence` and `ai-investigation` remain deferred/unimplemented because durable implementation boundaries were not yet present.

The long-term architecture discussed in this workstream is:

```text
Common Telemetry/Event Foundation
  -> Gameplay Analytics
  -> Security & Economic Analytics
  -> Chat Safety & Intelligence
  -> World Event / Raid Analytics
  -> read-only AI Investigation Layer
```

Deterministic systems collect evidence and enforce rules. AI may correlate, explain and recommend, but must not auto-ban, mutate balances/items, deploy code, execute generated Lua or call unrestricted game APIs.

### TSD-012 — validation and live operations

Feature PR #377, lifecycle PR #378.

Registry:

```text
61 -> 62
```

Added only:

- `deployment-operations`.

Existing `otbm-tooling`, `physical-client-e2e`, `upstream-intelligence` and domain-specific validators remained canonical. No duplicate parser, renderer, watcher, mapper, validator platform or E2E orchestrator was created.

### TSD-013 — Oteryn migration classification

Feature PR #379, lifecycle/final program-close PR #380.

Registry remained:

```text
62 -> 62
```

No records were added or modified.

Final classification rule:

```text
ALL_CANONICAL_MODULES -> REVALIDATE
```

Program closure is recorded in `TIBIA_SYSTEM_DECOMPOSITION_PROGRAM.md`.

## Key merge evidence from the canonical program

The program records the following feature/lifecycle progression:

```text
TSD-001   44fe3af9f29b3ae0164ac5d60fc1f14137b5cea5 / cc8b3bdc9b34fb8e6802bd1a0fc0d535de2dd9ba
UI-001A   09f7049401253dd38c8f34506946c2fbe287d220 / 6d368766cc47794ec0145b4b32613edaf7588adb
TSD-002A  82f35c0147fdd33c8d4e70d98d003385daf61de6 / 709693b4cca42214c52e63ea15a1a22b93f9a113
TSD-002B  1410a8622aaca5e4afe1bd15aa2695e2dbb7bb94 / d3dbca52ced28e747f1764167e1d479bd2568a6d
TSD-003   1098363a708a1f5f875850670a5aad411031e188 / 9f82f93977e82784370961a72104efacd497c8e0
TSD-004   6d6df89b02fca525ef76011369d8c6243de231d8 / f163ed8e3b3d51e65c7fef1bc03830b12b2e6bfa
TSD-005   68b9836cc8e6f55add9a6f3f8d7919e031defc50 / f68f826915882b0b20081b8fca5ed975ce303f45
TSD-006   8dfec274b0f460c1f0d6bee6c8a4b95a3ecf8c12 / 821f213038770d68cd95b1b22afa78937b974210
TSD-007   4932c48d5899ac246404f65e2017a86fc6a5324b / 350739e5df12db5f3c749540a36bb7c3922cc5ee
TSD-008   8692347930d86c5411dede46cb90251e5c677d96 / c68855a0c9ee33d454bb0d6bbab697693578bb0a
TSD-009   8425845f79d161cb2cd6aab2276aeb39c3616c3e / 381cc076fa35e138292197f751f26c2e7b89dd08
TSD-010   9a5f2ee0f1ed95c306876e868109f28848f0ae66 / c67c84749ffd1de04983be9ae9841b6ca5756aed
TSD-011   dd85d8f886b3e76ec9cc3d3e24c3cb0f7607181c / 145929ec7f438dc492d4b618a386a4418953d7ec
TSD-012   81fe5417345c64098e8bb4fd25b27ba234a8406e / 10d4bf63cf356a3cf912cbc8717854e6a6fd2895
TSD-013   e3b08e36c503a36b0eb47696e50567155050c757 / PR #380 lifecycle close
```

PR #380 later merged to `main` as:

```text
32b536abb3f65bfb9bfd5c049f3413ce7c46880d
```

## Universal Physical-Client E2E state after TSD closure

PR #245 subsequently merged as:

```text
9fc11e04dc5040d1ea18d02e15dac1df47f3fe64
feat(e2e): bootstrap universal agent test platform
```

This is important foundation for future module revalidation.

The merged platform provides one reusable, feature-neutral physical-client E2E orchestrator and a validated `login/relog` baseline using one OTClient process.

Final PR evidence reported two successful world entries, two safe logout lifecycles, transport closure, immediate first-session persistence, two packet records, persisted `lastlogin`/`lastlogout`, final online count zero and no fatal runtime/sequence-mismatch evidence.

Do not create a second generic physical-client E2E platform.

Future gameplay/module E2E should add bounded scenarios to the existing platform.

## Permanent architectural rules established by this workstream

1. `docs/agents/real-tibia/registry/**` is the canonical module inventory.
2. Generated indexes are derived, not independently editable truth.
3. Broad stable IDs may remain compatibility/discovery umbrellas.
4. A module is a durable responsibility/lifecycle boundary, not a file, class, formula, spell, NPC, boss or bug.
5. Path hints are discovery only, never ownership or edit authorization.
6. One path may correctly map to multiple modules.
7. `depends_on` must mean fundamental dependency and remain acyclic.
8. `interacts_with` should remain conservative rather than model every shared `Player`, `Game`, `Lua`, DB or protocol touchpoint.
9. Presence of code/schema/helpers/tests proves at most inventory unless stronger evidence exists.
10. Maturity is multidimensional; implementation, persistence, protocol, automated tests, runtime validation and gameplay E2E must not be collapsed into one optimistic status.
11. Upstream/donor findings are evidence candidates, not automatic local defects or parity proof.
12. No automatic cherry-pick or upstream adoption.
13. No second OTBM parser, renderer, source watcher, registry, mapper, generator or E2E orchestrator.
14. The legacy repository remains the evidence laboratory; Oteryn migration needs a target-side contract.
15. AI is advisory/investigative. Deterministic systems remain authoritative for gameplay, sanctions, economy mutation, deployment and execution safety.

## Important systems discussed but not implemented by TSD

The decomposition program intentionally did not implement these planned systems merely because they were architecturally discussed:

- `security-analytics`;
- economic ledger/item provenance;
- `chat-safety-intelligence`;
- `ai-investigation`;
- Adaptive World Event / Raid Director;
- generic runtime event trace;
- transaction fault injection;
- protocol differential analysis;
- combat differential simulation;
- quest state-machine analysis;
- new Oteryn runtime architecture.

Any of these requires a fresh bounded implementation program and must reuse existing infrastructure.

For future Adaptive World Event / Raid work, preserve these boundaries:

- deterministic validator/executor controls runtime;
- AI may compose only an approved bounded plan format;
- AI must not generate arbitrary items/monsters/rewards, arbitrary Lua or direct unrestricted runtime calls;
- Bosstiary classification/credit, physical spawn availability, boss participation/loot eligibility and player cooldowns are separate contracts;
- do not invent non-canonical reward cooldowns.

For Fiendish/Influenced creature work, keep Forge creature lifecycle separate from raid lifecycle.

## OTBM/tooling boundary

The repository already contains an extensive OTBM analysis pipeline, including a Unified OTBM World Index, mechanic/item audit, script resolution, reachability, spawn/NPC evidence, storage graph, Semantic OTBM Diff, geometry consistency audit and a bounded attribute patcher.

Future map work must reuse these tools.

Do not build a new OTBM parser or renderer from scratch.

Do not use AI image generation to fabricate map evidence.

Current open draft PR #316 is specifically a bounded Targuna donor-cluster audit and owns its own scope.

## What the next agent should do first

Before starting any new work, do a fresh live GitHub preflight. Do not assume the SHA or open-PR list in this handoff is still current.

Required first checks:

1. current `main` and exact SHA;
2. all open PRs and draft PRs;
3. all active tasks;
4. path ownership and shared-path conflicts;
5. `AGENTS.md` and current agent governance;
6. `docs/agents/programs/TIBIA_SYSTEM_DECOMPOSITION_PROGRAM.md`;
7. `docs/agents/real-tibia/registry/**` and generated indexes;
8. `docs/agents/MODULE_CATALOG.md`;
9. current Upstream Intelligence program/state;
10. current Universal Agent E2E state;
11. PR #316 and any later OTBM/map work;
12. any newly created Oteryn repository or target architecture contract.

## Recommended next strategic program

Do not reopen TSD-001 through TSD-013 and do not invent TSD-014 merely to continue the old queue.

The next strategic program should be a new bounded program, conceptually:

```text
CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
```

The exact name may follow then-current repository governance.

Before any migration classification stronger than `REVALIDATE`, the new program should establish:

1. explicit Oteryn repository identity;
2. exact target baseline SHA;
3. target architecture and directory/module contract;
4. build/runtime/toolchain contract;
5. persistence and migration contract;
6. client/protocol compatibility policy;
7. module evidence requirements;
8. migration decision vocabulary;
9. rollback and provenance rules;
10. bounded package ordering.

Only then should affected modules move from `REVALIDATE` toward decisions such as:

```text
REUSE
ADAPT
REWRITE
DO_NOT_MIGRATE
EXPERIMENTAL_ONLY
```

A reasonable first Oteryn program sequence is:

```text
OAM-001 target repository and architecture contract
OAM-002 engine/build/runtime baseline
OAM-003 persistence contract
OAM-004 protocol/client contract
OAM-005 first low-risk proven module migration
OAM-006 physical-client E2E target proof
... then bounded domain migrations based on evidence
```

Do not migrate all 62 modules at once.

Start with one low-risk, well-bounded module only after target architecture is explicit.

## Evidence limitations that remain true

The completed decomposition establishes architecture/inventory/discovery boundaries, not complete Real Tibia parity.

The 62 records do not by themselves prove:

- gameplay correctness;
- formula parity;
- persistence atomicity/completeness;
- transaction isolation or crash recovery;
- wire compatibility;
- maintained-client interoperability;
- production database behavior;
- runtime stability;
- physical-client E2E for every module;
- privacy/security correctness;
- Oteryn compatibility or readiness.

Future agents must preserve these distinctions.

## Final handoff instruction

Treat this file as historical context and navigation, not as live truth.

Always re-fetch current GitHub state before acting.

Preserve the completed TSD archives and canonical 62-module registry.

Do not reopen the completed decomposition program unless a genuinely new decomposition requirement appears and repository governance explicitly calls for a new bounded extension.

For Oteryn, begin with a new program and explicit target architecture contract, then revalidate modules one bounded package at a time.
