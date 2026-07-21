# OAM-030 Bosstiary Revalidation

## Final disposition

```text
bosstiary → ADAPT
```

## Immutable task-start baselines

- legacy/governance Canary: `419d0848448c641561e7bc06392a4b17b95213b2`
- Otheryn target: `68d48deea999990b1eab30858f3a85fc9fef7067`
- fresh upstream Canary: `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`
- maintained OTClient: `a6868920443dc285656bd016acdb2c1ea566e511`

Canary drifted once after task start to `af27845b130a87d92f2794c2817d77cfe6d84825`; the single independent commit only archived the completed OTBM E2E route programme task. No Bosstiary, OAM-030 or shared migration-program path overlapped, so governance was reconstructed cleanly on that current `main` before final gating.

Canonical `bosstiary` depends only on completed `cyclopedia` and `player-persistence` and owns `src/io/io_bosstiary.*`. Fresh open-PR audit found no writer over that root; Otheryn and maintained OTClient had no pre-existing open PRs.

## Adaptation evidence

Task-start Otheryn and fresh upstream shared exact `src/io/io_bosstiary.cpp` blob `8e89ce79316e5c193e918661c50278f50d476c83`.

Merged legacy PR #188 was decomposed by canonical ownership. Its Bosstiary portion is one production correction in `IOBosstiary::loadBoostedBoss`: target/upstream returned immediately when the `boosted_boss` query yielded no row, making their later `if (!result)` recovery branch unreachable. The accepted donor removes that early return, initializes the missing singleton row with deterministic default values, fails closed if initialization fails, and then continues the existing reroll path.

Current legacy later added independent multichannel cluster-leadership logic around the global boosted-boss reroll. That later logic was deliberately not imported. Bestiary, Charms, monster-definition data, protocol and maintained OTClient changes were also excluded.

## Target delivery

Otheryn PR #61 final head `4b6dd3fdca907d2f521cb366322dd5b007aca668` changed exactly five intended paths:

- `docs/agents/tasks/active/OTH-20260721-oam030-bosstiary-adapt.md`
- `docs/oam-030-bosstiary-adapt.md`
- `src/io/io_bosstiary.cpp`
- `tests/unit/game/CMakeLists.txt`
- `tests/unit/game/oam_030_bosstiary_adapt_test.cpp`

Temporary materialization helpers/workflows were absent from the final diff. The exact final head passed autofix.ci #185 run `29812625663`, CI #223 run `29812626058`, and Required #208 run `29812625664`. Linux debug full `Run Tests` succeeded; artifact `8488418806` has digest `sha256:1bf24e4a4d61bb8f0aab3769b2b19cfe7abd9c98507b691d9d034de07b476e29`.

Target comments, submitted reviews and review threads were empty. Otheryn `main` remained at immutable target base `68d48deea999990b1eab30858f3a85fc9fef7067` through the merge gate. PR #61 merged by expected-head squash as `dc483d6e8d659d61482da2af7abda9b46b1766ff`.

## Explicit non-claims

OAM-030 does not claim exhaustive Bosstiary parity, boosted-boss cluster-singleton correctness, multiwriter safety, boss slot persistence, boss point or loot-bonus arithmetic parity, schema migration correctness, packet compatibility, maintained-client rendering correctness, physical-client Bosstiary E2E closure, or full Real Tibia parity.
