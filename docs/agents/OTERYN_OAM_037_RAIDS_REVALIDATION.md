# OAM-037 Raids revalidation

## Final disposition

`raids → REUSE`

## Baselines

- Canary OAM-037 preflight merge: `8bdeb2747356727df80a3b95073aa29a4dca7818`
- Canary bounded target-proof plan merge: `817da293a141880f7090194699a4ac38e567a2fb`
- Canary fresh governance base: `4f074077da44d1cc9d77db7ac768be0589313332`
- Otheryn target task-start base: `3aaf77fe27600b274d2b9c9e6bd30d887e0afd0e`
- canonical target/upstream `src/lua/creature/raids.cpp` blob: `d46a549a341e0872474bd723b10d1208fa22da8c`
- canonical target/upstream `src/lua/creature/raids.hpp` blob: `777558e3e199816bb596636fc7487c38c29224ee`

## Selection and ownership

Canonical `raids` owns legacy raid registry loading, interval/margin/repeat metadata, periodic raid selection, single-running-raid state, ordered raid-event execution, lifecycle reset/cleanup, and announce/single-spawn/area-spawn/script event dispatch. Boss encounter reward lifecycle, generic creature AI and definitions, non-raid spawn scheduling, Bosstiary, quest access/cooldowns, protocol/client, maps, assets, schema and deployment remain outside OAM-037.

The clean Otheryn target and reviewed fresh upstream share exact canonical `raids.cpp` and `raids.hpp` roots. The older legacy Canary `raids.cpp` is not a stronger whole-module donor because the target retains `DispatcherLane::Maintenance` scheduling and explicit scheduling-failure safeguards for periodic checks and raid-event execution.

Identity alone was not accepted. The bounded target source-contract proof verified registry parsing/reload, maintenance-lane scheduling, scheduling-failure recovery, running/non-repeat lifecycle, ordered event execution, reset/stop cleanup, and all four canonical raid event kinds.

## Target proof

Otheryn PR #77 final head `133c12f61a1e5e392be9ee7faa9236755cbe0225` changed exactly four intended proof/task paths and no production runtime/data path. Exact-head autofix run `29988627793`, CI run `29988627932` and Required run `29988627768` all succeeded. Fast checks, Lua tests, Linux release, Linux debug including database import and full `Run Tests`, both Windows build paths, macOS, and applicable runtime smoke checks all succeeded.

Comments, submitted reviews and review threads were empty. Otheryn `main` had no drift from immutable target base before merge. PR #77 squash-merged as `d896141d084d381d12cc328d4b920c698eb1d55c`.

## Final conclusion

OAM-037 is `REUSE`: preserve the existing canonical raid registry, scheduler and event lifecycle and add proof only. No production repair, maintained-client mutation or protocol change was required.

## Nonclaims

OAM-037 does not claim exact official raid probability or timing parity, exact event timing under scheduler load, raid XML/data-definition completeness, restart/crash recovery semantics, distributed or multichannel raid coordination, exact spawn placement parity, webhook delivery guarantees, physical-client E2E closure or full Real Tibia parity.
