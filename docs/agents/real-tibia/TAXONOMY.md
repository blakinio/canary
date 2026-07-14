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

- `character-progression`: player growth, unlocks, vocation-facing progression and account-visible advancement;
- `combat`: damage, healing, conditions, weapons, spells and combat state;
- `items-economy`: items, upgrades, trade, shops, markets, loot and economic state;
- `world-content`: maps, quests, NPCs, spawns, houses and world mechanics;
- `social-account`: parties, guilds, communication, permissions and account/character lifecycle;
- `client-protocol`: wire formats, capability gates, login/game protocol and maintained-client interpretation;
- `platform-tooling`: persistence infrastructure, validation platforms, OTBM tooling and agent systems.

Categories are navigation labels. Cross-category relationships are expected.

## Relationship semantics

`depends_on` means the module cannot be correctly implemented or validated without the target module's contract. It must be acyclic.

`interacts_with` means behavior crosses a boundary, but neither module is necessarily foundational. It may be reciprocal.

Use the smallest defensible relationship set. Do not create a fully connected graph merely because systems share `Player`, `Game` or Lua.

## Path semantics

Module paths are glob-style discovery hints grouped as:

- `server` — Canary C++ and server runtime;
- `client` — maintained OTClient paths, informational and read-only unless separately authorized;
- `data` — active Lua/XML/datapack surfaces;
- `tests` — focused or integration validation;
- `docs` — authoritative module documentation.

A path can legitimately map to multiple modules. Path matches never grant edit ownership.

## Granularity rules

Create a new module when at least two of these hold:

- multiple independent findings are expected;
- it has a distinct persistence or protocol boundary;
- it has its own lifecycle/state machine;
- it has its own long-lived validation effort;
- it spans server/client/data with a coherent contract;
- agents repeatedly need the same source, dependency and handoff context.

Prefer a bounded task when the work is one independently testable state transition, formula family, handler, packet field, quest package or geometry region.

## Bootstrap scope

The initial registry intentionally covers major domains already represented by code, documentation, programs or recurring work. It is not a claim that every Tibia system has been audited or that the taxonomy is complete. Additions must be evidence-driven and reviewed as normal registry changes.
