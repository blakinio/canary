# OAM-051 Wheel of Destiny revalidation

## Current disposition

```text
wheel-of-destiny → ADAPT (phase A complete; phase B pending)
```

OAM-051 is intentionally decomposed. OAM-051A delivered only the server-side Wheel safety and state-integrity boundary selected by the Canary preflight. It did not transfer the complete legacy Wheel subsystem and did not complete the separately client- and persistence-coupled Hunting Task Shop package.

## OAM-051A completed boundary

Otheryn feature PR #115 adapted:

- atomic validation of the complete Wheel allocation before mutation;
- server-side temple-only decrease enforcement;
- saturating point accounting;
- validated gem, grade, modifier-position, affinity and persisted-state handling;
- revealed-gem capacity and bounded restoration after failed money mutation;
- permanent point-source load ordering before persisted allocation validation;
- malformed current-protocol Wheel action rejection without changing opcode or payload layouts;
- focused deterministic behavior and source-boundary tests.

The target preserved Otheryn-specific protocol-profile, persistence and test-manifest work. The donor was pinned to Canary PR #220 squash `35ff51ac022e36d215db9d0fa86053b326a0bdf0`; no whole-file replacement was used.

## Exact evidence

- Canary OAM-051 preflight PR #951 merged as `a4a35495d4a8dc047bd3315b95c9fb577ac597af`.
- Otheryn exact final feature head `1f4ce3c11f6acf292775daac886e9dace7e8280f` passed autofix `30193154587`, full CI `30193154684` and Required `30193154608`.
- Full CI included Fast Checks, Lua, Linux debug and release, all C++ tests, schema import, Canary and Global runtime smoke, macOS, Windows CMake, Windows Solution and Docker image validation.
- Feature PR #115 changed exactly eight implementation/test paths plus its task and report, had no comments, reviews or unresolved review threads, and merged as `47863ce250bce73c1b9af3077f82e9bf6e99e3d1`.
- Otheryn lifecycle PR #118 changed only active/archive/report documentation, passed Required `30193946125` on exact head `299b85cddd61dc24054becc33a9188d4c2e38c99`, and merged as `bd0b58a362d89e449a6863ba299d1c50ad4e6685`.

## Preserved exclusions

OAM-051A did not import:

- Hunting Task Shop Promotion Points;
- Wheel balance constants, formulas, areas or effect ordering;
- full Vessel Resonance damage/healing bonuses;
- Gift of Life mana, Ballistic Mastery, Healing Link, Battle Healing or Blessing changes;
- critical healing, vocation stances, replacement spells or Strong Ice Wave geometry;
- legacy `src/game/game.cpp` parser changes;
- OTClient changes, generated Lua API output, map, schema or deployment changes.

The target retained the existing Supreme Grade II value `12000000`; no `WheelBalance` dependency or full-resonance helper was imported.

## OAM-051B retained boundary

The next bounded package is the Hunting Task Shop Bonus Promotion contract proven missing from current Otheryn. It remains separate because it combines:

- the Taskboard shop packet and maintained-client interpretation;
- purchase-cost progression for points 1 through 50;
- Hunting Task Point mutation;
- Wheel KV/cache/load/relog behavior;
- a new Player Lua binding;
- durability and failure semantics across resource mutation and persisted Wheel state.

Current Canary PR #230 is evidence and a candidate donor, not permission to copy the whole patch. Its sequence removes Hunting Task Points before writing Wheel KV, so OAM-051B must establish an explicit transaction/failure contract and must not claim atomic durable purchase behavior without rollback or recoverability proof.

## Governance checkpoint

Canary governance PR #956 owns only this report and the active OAM-051 task. The `ci:final-gate` label is applied; the final synchronized head must pass Agent Task Ownership and full CI before merge. OAM-051 remains active after that merge, and no target OAM-051B source change is authorized until its transaction and maintained-client preflight is complete.

## Nonclaims

OAM-051A does not prove complete Wheel parity, physical-client gameplay, Task Shop interoperability, DB/KV failure injection, current official balance behavior, critical-healing correctness, stance behavior, replacement-spell behavior or authoritative geometry.
