# Real Tibia Module Taxonomy

## Purpose

A module is a stable functional or technical domain that can be inventoried, related to source paths and evidence, and divided into independently testable tasks. It is not required to correspond to one directory, class, packet, quest, spell or PR.

A good module boundary:

- has a coherent responsibility and vocabulary;
- has identifiable implementation, data, tests or protocol surfaces;
- has meaningful dependencies or interactions;
- may require several bounded findings or PRs over time;
- can be handed to a new agent without loading the entire repository context.

A single formula, NPC, spell, packet field or map coordinate is normally a task inside a module, not a module by itself.

## Categories

The canonical category IDs live in `registry/categories.yaml`.

- `engine-foundation`: process lifecycle, configuration, Lua runtime, scheduling, services, build and platform contracts;
- `character-progression`: player growth, unlocks, vocation-facing progression and account-visible advancement;
- `combat`: damage, healing, conditions, weapons, spells and combat state;
- `items-economy`: items, upgrades, trade, shops, markets, loot and economic state;
- `world-content`: maps, quests, NPCs, spawns, houses and world mechanics;
- `social-account`: parties, guilds, communication, permissions and account/character lifecycle;
- `client-protocol`: wire formats, capability gates, login/game protocol and maintained-client interpretation;
- `platform-tooling`: persistence infrastructure, validation platforms, OTBM tooling and agent systems.

Categories are navigation labels. Cross-category relationships are expected.

## Umbrella and child convention

Broad existing module IDs may remain umbrella or discovery-compatibility modules while narrower records are added. Umbrellas preserve stable lookup and Upstream Intelligence behavior; they are not claims that one record owns every future finding in the domain.

The current schema does not encode parent/child relations. Until a concrete registry consumer needs that field, hierarchy is expressed through module scope, descriptions, program documentation and the decomposition classification report.

Rules:

- do not remove a broad ID merely because a narrower module is added;
- do not use `depends_on` to simulate parenthood;
- allow a verified path to match an umbrella and one or more children;
- keep multi-match output deterministic and treat every match as a discovery hint;
- add a schema field only when `lookup-path`, `affected`, generated navigation or Upstream Intelligence gains tested operational value.

## Relationship semantics

`depends_on` means the module cannot be correctly implemented or validated without the target module's contract. It must be acyclic.

`interacts_with` means behavior crosses a boundary, but neither module is necessarily foundational. It may be reciprocal.

Use the smallest defensible relationship set. Do not create a fully connected graph merely because systems share `Player`, `Game` or Lua.

## Path semantics

Module paths are glob-style discovery hints grouped as:

- `server` — Canary C++ and server runtime;
- `client` — maintained OTClient paths, informational and read-only unless separately authorized;
- `data` — active Lua/XML/datapack surfaces and verified root configuration files;
- `tests` — focused or integration validation;
- `docs` — authoritative module documentation.

A path can legitimately map to multiple modules. Path matches never grant edit ownership, prove completeness or prove parity.

Use real paths only. Planned modules with no verified implementation keep path lists empty until their bounded package inventories current source.

## Granularity rules

Create a new module when at least two of these hold:

- multiple independent findings are expected;
- it has a distinct persistence or protocol boundary;
- it has its own lifecycle/state machine;
- it has its own long-lived validation effort;
- it spans server/client/data with a coherent contract;
- agents repeatedly need the same source, dependency and handoff context.

Prefer a bounded task when the work is one independently testable state transition, formula family, handler, packet field, quest package or geometry region.

Do not create a module solely for a single vocation, spell, boss, chat channel, visual primitive, price, table, packet field, storage or map coordinate unless later evidence demonstrates a durable independent lifecycle and validation queue.

## Decomposition packages

`CAN-PROGRAM-TIBIA-SYSTEM-DECOMPOSITION` sequences additions through bounded packages. Candidate classification is prior evidence for registry work, not approval to create every deferred record.

Each package must re-fetch current source and prove exact paths, non-duplication, minimal relationships and conservative maturity before adding records.

## Bootstrap scope

The initial registry intentionally covers major domains already represented by code, documentation, programs or recurring work. It is not a claim that every Tibia system has been audited or that the taxonomy is complete. Additions must be evidence-driven and reviewed as normal registry changes.

TSD-001 adds only a small engine-foundation pilot. It does not claim full Tibia decomposition, runtime verification, Real Tibia parity or Oteryn migration readiness.
