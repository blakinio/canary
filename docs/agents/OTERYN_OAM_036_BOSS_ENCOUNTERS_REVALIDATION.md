# OAM-036 Boss Encounters revalidation

## Final disposition

`boss-encounters → REUSE`

## Baselines

- Canary task-start/preflight base: `27b49fbbdafda9c365bc25b0c2adb790337d42d4`
- Canary fresh governance base: `fce787f7427bc2d824cf528b7801d4b369089adc`
- Otheryn target task-start base: `6275021bbb83dc28d2f5d6cf8db5b16aa7206544`
- fresh upstream Canary: `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`
- maintained OTClient: `a6868920443dc285656bd016acdb2c1ea566e511`

## Selection and ownership

Canonical `boss-encounters` depends only on completed `creature-definitions` and `player-persistence`. Its reviewed boundary covers reward-boss participant state, contribution tracking, target-list reconciliation, boss-death score normalization, reward generation, reward-container insertion and offline persistence handoff. Generic boss AI/definitions, spawns, raids, Bosstiary, quest access/cooldowns, protocol/client, maps and assets remain outside OAM-036.

The selected roots were exact-identical across task-start Otheryn, fresh upstream and legacy Canary: `data/libs/systems/reward_boss.lua` blob `72476dfcbdd8fd92d6b5bd3ad3015efef87cf2f3` and `data/scripts/systems/reward_chest.lua` blob `4abe17ad2f3103f30f172f23ebdca391197f8646`. Identity alone was not accepted; semantic review and a bounded target source-contract proof verified the owned lifecycle and found no stronger delivered legacy donor.

## Target proof

Otheryn PR #74 final head `18153ce36b0d84e2b6b73e68579b2167c91fc03f` changed exactly four intended proof/task paths and no production runtime/data path. Exact-head autofix run `29907996264`, CI run `29907997057`, Required run `29907996378`, Linux-debug runtime smoke/schema/full `Run Tests`, Linux release, both Windows build paths and macOS all succeeded. Comments, reviews and review threads were empty, and target `main` had no drift from immutable base before merge.

PR #74 squash-merged as `c0a84977b574f287db2fb970a25e8041343b99c8`.

## Final conclusion

OAM-036 is `REUSE`: preserve the existing reward-boss encounter/reward lifecycle and add proof only. No production repair, maintained-client mutation or protocol change was required.

## Nonclaims

OAM-036 does not claim exact participant eligibility, contribution-score arithmetic, loot factor/roll parity, reward-table correctness, Bosstiary bonus correctness, persistence atomicity, crash recovery, generic boss AI correctness, spawn/raid correctness, quest/cooldown behavior, protocol/client compatibility, physical-client boss E2E closure or full Real Tibia parity.
