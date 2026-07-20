# OAM-028 Cyclopedia Revalidation

## Final disposition

```text
cyclopedia REUSE
```

## Immutable task-start baselines

- legacy/governance Canary: `85b26b41510101259f6138f2c864bf0c4a473f2a`
- Otheryn target: `2a008f1c8cfa679c9b70281e4c8c16120a7567fa`
- fresh upstream Canary: `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`
- maintained OTClient: `a6868920443dc285656bd016acdb2c1ea566e511`

Canonical `cyclopedia` depends only on completed `protocol` and `player-persistence`. TSD-004 deliberately preserves `cyclopedia` as a broad compatibility/discovery umbrella while assigning independent durable implementation roots to `bestiary`, `bosstiary`, `cyclopedia-character` and `titles`; `charms` and `houses` retain their existing independent canonical records.

## Reuse evidence

Task-start Otheryn and fresh upstream shared exact `src/server/network/protocol/protocolgame.hpp` blob `082d66596a424fc44143298c41fe01ff4007a439`. Task-start Otheryn, fresh upstream and legacy shared exact `src/enums/player_cyclopedia.hpp` blob `45fed9ad2f3b7e35bdc7afd9dbd52d5d1b736311`. Blob identity was supporting evidence only and was not accepted as sufficient by itself.

Delivered legacy Cyclopedia remediation was reviewed semantically:

- merged PR #188 fixes Bestiary arithmetic/null safety, Charm rules/registration, Bosstiary bootstrap and Cyclopedia Character recent-PvP pagination. TSD-004 assigns those production roots to `bestiary`, `charms`, `bosstiary` and `cyclopedia-character`; PR #188 changes no umbrella protocol or maintained-OTClient path;
- merged PR #192 repairs Bestiary/Bosstiary monster data and validator allowlists and likewise changes no umbrella protocol or maintained-OTClient path;
- PR #243 hardens the existing Cyclopedia validation gate and is validator/workflow control, not an umbrella runtime donor.

Fresh live-state ownership review also found no conflicting active writer over the selected proof-only target boundary. Open Canary PR #514 changes security runtime tooling/tests/docs only and does not touch production protocol paths; the open NPC and OTBM E2E work is separately owned.

No reviewed delivered legacy change requires replacing the pinned target/upstream umbrella protocol surface. OAM-028 therefore preserves completed OAM-006 protocol architecture and does not partially import child fixes before their own canonical OAM packages.

## Target delivery

Otheryn PR #57 final head `19c286762fb89ba3ed8d47ebf58538ff070a4d7f` changed exactly four proof-only paths:

- `docs/agents/tasks/active/OTH-20260720-oam028-cyclopedia-reuse.md`
- `docs/oam-028-cyclopedia-reuse.md`
- `tests/unit/game/CMakeLists.txt`
- `tests/unit/game/oam_028_cyclopedia_reuse_test.cpp`

No production runtime, protocol, child runtime/data, schema, map, asset, deployment or maintained OTClient path changed. The focused proof verifies representative cross-tab `ProtocolGame` declarations for Cyclopedia Character, Map, Bestiary, Bosstiary and Houses plus independent TSD-004 child roots for `IOBestiary`, `IOBosstiary`, `PlayerCyclopedia` and `PlayerTitle`.

Final autofix.ci #170 run `29785109223`, CI #206 run `29785109355`, and Required #189 run `29785109193` all succeeded on the exact final head. Linux debug compilation, Canary runtime smoke, database schema import and full `Run Tests` succeeded; the focused OAM-028 proof was compiled and executed within that suite. Fast Checks, Lua Tests and the complete platform matrix also passed. Linux debug test-log artifact `8478394189` has digest `sha256:152b153430d5ccd7953647f37e2d462b16c7aed30a7a027248195e698bdfa9cb`.

Target comments, submitted reviews and review threads were empty. Otheryn `main` remained at immutable target base `2a008f1c8cfa679c9b70281e4c8c16120a7567fa` through the merge gate. PR #57 merged by expected-head squash as `7e03405aea50d88fdbc27d0d2a7d95c7f1745946`.

## Explicit non-claims

OAM-028 does not claim Bestiary, Bosstiary, Charm, Cyclopedia Character, Titles or Houses child correctness; exact packet-byte compatibility; maintained-client parsing/rendering correctness; item/map/house presentation correctness; persistence completeness; runtime behavior; physical-client Cyclopedia E2E closure; or full Real Tibia parity. It changes no production runtime, protocol, data, schema, map, asset, deployment or maintained OTClient path.
