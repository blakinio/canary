#!/usr/bin/env python3
from pathlib import Path

path = Path("docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md")
text = path.read_text(encoding="utf-8")

replacements = [
    ('updated: 2026-07-21T12:30:00+02:00\nlast_verified_commit: "994d1ffdfd6828688b1acc6cd7c0c519eab052ba"', 'updated: 2026-07-21T21:30:00+02:00\nlast_verified_commit: "0fca8ced2d952eab744238f826af81cb9ee135b1"'),
    ('| OAM-030 | `bosstiary → ADAPT` | target `dc483d6e8d659d61482da2af7abda9b46b1766ff`; feature `6c092568e44dcb0b13959a8f22c14a992565aa7b`; lifecycle `994d1ffdfd6828688b1acc6cd7c0c519eab052ba` |', '| OAM-030 | `bosstiary → ADAPT` | target `dc483d6e8d659d61482da2af7abda9b46b1766ff`; feature `6c092568e44dcb0b13959a8f22c14a992565aa7b`; lifecycle `994d1ffdfd6828688b1acc6cd7c0c519eab052ba` |\n| OAM-031 | `bestiary → ADAPT` | target `86e4b08c28ede2f35c215a7c2327a579f4a61419`; feature `e55e0d548d6013da6676cc7b06cbb8d459ccdd1f`; lifecycle `0fca8ced2d952eab744238f826af81cb9ee135b1` |'),
    ('# Current state', '''# OAM-031 durable completion

Final disposition:

```text
bestiary ADAPT
```

Task-start baselines were Canary `9aa582eb6b8ab9444294e08798f628cd053d2428`, Otheryn `6a7e54ee3c9597e3ab265a14c2b783631ef3776f`, fresh upstream Canary `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`, and maintained OTClient `a6868920443dc285656bd016acdb2c1ea566e511`. Canonical `bestiary` depends on completed `cyclopedia` and `player-persistence`, owns the narrow server root `src/io/iobestiary.*`, and keeps Charm policy plus monster-definition data outside this package boundary.

Task-start Otheryn and fresh upstream shared exact `src/io/iobestiary.cpp` blob `c0497c4d1814e7950ad8fc27b9a4ec1f86d4a5cd`. Semantic decomposition of merged legacy PR #188 selected exactly two Bestiary-owned corrections: `IOBestiary::addBestiaryKill` validates `player` and `mtype` before dereferencing `mtype->info.raceid`, and `IOBestiary::calculateDifficult` converts `chance` to `double` before division by `1000.0` so fractional thresholds are not truncated. The PR #188 all-Charm reset-price correction and PR #192 monster-definition data were deliberately excluded; whole-file legacy reuse was rejected because the file also hosts separately owned Charm helpers and behavior.

Otheryn PR #63 final head `c49796d696448aa168c34629dc9ebcd9fd7a9465` changed exactly five intended OAM-031 paths, with production diff limited to `src/io/iobestiary.cpp`. Exact-head autofix.ci #187 run `29825053904`, CI #226 run `29825054221`, and Required #211 run `29825053840` succeeded; Linux debug full `Run Tests` succeeded. Test-log artifact `8493329878` has digest `sha256:e99f341683bc432512ddd0dc235204f8b13510cd48eaf9f06c9cdf53d7dbc432`. Comments/reviews/threads were empty, target `main` had no task-start drift, and PR #63 merged by expected-head squash as `86e4b08c28ede2f35c215a7c2327a579f4a61419`.

Canary governance PR #675 final head `1ce09da615e703ff72062c60093ae8b5173cf80b` was reconstructed on non-overlapping Canary `main` `87c4f71b0deb880da7ba4228bc29e769db2c5818`. It changed exactly the OAM-031 revalidation report and active-task record. Agent Task Ownership #3069 run `29826443473` and final-gate CI #4222 run `29826443642` succeeded; comments/reviews/threads were empty, and PR #675 merged by expected-head squash as `e55e0d548d6013da6676cc7b06cbb8d459ccdd1f`.

Authoritative lifecycle PR #676 final head `7e722d1872db8e4e7beeb31feae28b1060ea4cde` changed exactly the active-delete/archive-add lifecycle paths. Agent Task Ownership #3073 run `29826706123` and CI #4225 run `29826706339` succeeded; comments/reviews/threads were empty, and PR #676 merged by expected-head squash as `0fca8ced2d952eab744238f826af81cb9ee135b1`.

OAM-031 does not claim full Bestiary parity, exhaustive kill-stage/reward correctness, Charm correctness, monster-definition parity, exact protocol/client rendering compatibility, persistence completeness, tracker refresh correctness under every runtime state, database durability, physical-client Bestiary E2E closure, or full Real Tibia parity.

# Current state'''),
    ('''Canary reconciliation base: 994d1ffdfd6828688b1acc6cd7c0c519eab052ba
Otheryn target head after OAM-030: dc483d6e8d659d61482da2af7abda9b46b1766ff
maintained OTClient: a6868920443dc285656bd016acdb2c1ea566e511
OAM-001..OAM-030: feature/lifecycle complete
OAM-030 task: archived
OAM-031: NOT STARTED''', '''Canary reconciliation base: 0fca8ced2d952eab744238f826af81cb9ee135b1
Otheryn target head after OAM-031: 86e4b08c28ede2f35c215a7c2327a579f4a61419
maintained OTClient: a6868920443dc285656bd016acdb2c1ea566e511
OAM-001..OAM-031: feature/lifecycle complete
OAM-031 task: archived
OAM-032: NOT STARTED'''),
    ('| OAM-001..OAM-030 | completed | preserve durable evidence |\n| OAM-031+ | planned, not active | only after this reconciliation merges: perform fresh live-state/open-PR/ownership and exact target/upstream/legacy preflight, then select one dependency-valid canonical package |', '| OAM-001..OAM-031 | completed | preserve durable evidence |\n| OAM-032+ | planned, not active | only after this reconciliation merges: perform fresh live-state/open-PR/ownership and exact target/upstream/legacy preflight, then select one dependency-valid canonical package |'),
    ('- OAM-030 does not claim full Bosstiary parity, exhaustive boosted-boss selection correctness, distributed or multiwriter leader election, cross-channel Bosstiary safety, Bestiary or Charms child correctness, exact protocol/client compatibility, maintained-client rendering correctness, monster-data parity, database availability or crash-recovery guarantees, physical-client Bosstiary E2E closure, or full Real Tibia parity.', '- OAM-030 does not claim full Bosstiary parity, exhaustive boosted-boss selection correctness, distributed or multiwriter leader election, cross-channel Bosstiary safety, Bestiary or Charms child correctness, exact protocol/client compatibility, maintained-client rendering correctness, monster-data parity, database availability or crash-recovery guarantees, physical-client Bosstiary E2E closure, or full Real Tibia parity.\n- OAM-031 does not claim full Bestiary parity, exhaustive kill-stage/reward correctness, Charm correctness, monster-definition parity, exact protocol/client rendering compatibility, persistence completeness, tracker refresh correctness under every runtime state, database durability, physical-client Bestiary E2E closure, or full Real Tibia parity.'),
    ('Merge this program-only OAM-030 completion reconciliation after exact-head Ownership/CI/review gates. Only then may a fresh OAM-031 preflight begin. OAM-031 is NOT STARTED by this record.', 'Merge this program-only OAM-031 completion reconciliation after exact-head Ownership/CI/review gates. Only then may a fresh OAM-032 preflight begin. OAM-032 is NOT STARTED by this record.'),
]

for old, new in replacements:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"expected exactly one match, found {count}: {old[:100]!r}")
    text = text.replace(old, new, 1)

path.write_text(text, encoding="utf-8")
