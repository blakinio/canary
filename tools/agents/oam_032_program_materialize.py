#!/usr/bin/env python3
from pathlib import Path

path = Path("docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md")
text = path.read_text(encoding="utf-8")

replacements = [
    (
        'updated: 2026-07-21T21:30:00+02:00\nlast_verified_commit: "0fca8ced2d952eab744238f826af81cb9ee135b1"',
        'updated: 2026-07-21T22:45:00+02:00\nlast_verified_commit: "fda6d01b93929ea998965354908062eb6e4e1424"',
    ),
    (
        '| OAM-031 | `bestiary → ADAPT` | target `86e4b08c28ede2f35c215a7c2327a579f4a61419`; feature `e55e0d548d6013da6676cc7b06cbb8d459ccdd1f`; lifecycle `0fca8ced2d952eab744238f826af81cb9ee135b1` |',
        '| OAM-031 | `bestiary → ADAPT` | target `86e4b08c28ede2f35c215a7c2327a579f4a61419`; feature `e55e0d548d6013da6676cc7b06cbb8d459ccdd1f`; lifecycle `0fca8ced2d952eab744238f826af81cb9ee135b1` |\n| OAM-032 | `titles → REUSE` | target `f5f21347c578a382cf0c52dbb4c69673ab3b05a9`; feature `212d5e5c4ecbb0bd392880019747e2370299c748`; lifecycle `fda6d01b93929ea998965354908062eb6e4e1424` |',
    ),
    (
        '# Current state',
        '''# OAM-032 durable completion

Final disposition:

```text
titles REUSE
```

Task-start baselines were Canary `db7cf6af480285ad4a87c3be2981a873f175eab6`, Otheryn `ad2bd2f187df057c47d05c121351159ce30cc457`, fresh upstream Canary `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`, and maintained OTClient `a6868920443dc285656bd016acdb2c1ea566e511`. Canonical `titles` depends only on completed `cyclopedia-character` and `player-persistence`; TSD-004 owns the narrow server root `src/creatures/players/components/player_title.*` while Bestiary, Bosstiary, character progression, houses and protocol remain interactions rather than ownership transfers.

Task-start target, current legacy and fresh upstream shared exact `player_title.cpp` blob `c885d5ee55970d8ce93a80bb477bc317fb9faa98` and `player_title.hpp` blob `118806fee9ca6d939d73067af14c63c59d291f25`. Blob identity was supporting evidence only. Semantic donor-history review found no accepted Titles-root delta: merged Cyclopedia runtime PR #188 contains no `player_title` path, PR #192 is monster-data remediation, and PR #243 is validator/workflow control. The final Cyclopedia zero-finding scan was not promoted into a claim about title definitions, thresholds, persistence, protocol, runtime behavior or maintained-client correctness.

Otheryn PR #65 final head `3244c8b0993047d9fe72ed56125a6f9e218defbb` changed exactly four proof/task paths and no production path. Autofix.ci #188 run `29863062941`, CI #228 run `29863063433`, and Required #213 run `29863063406` succeeded; Linux debug full `Run Tests` succeeded. Test-log artifact `8508497986` has digest `sha256:2c2b98f96fe73bd8b2e9123f662779534a70ec7b0a5b7ebe895f1769b05ae9b3`. Comments/reviews/threads were empty, target `main` had no task-start drift, and PR #65 merged by expected-head squash as `f5f21347c578a382cf0c52dbb4c69673ab3b05a9`.

Canary governance PR #691 final head `62af0071f777fd029c7c0718914375928ecf2389` changed exactly the OAM-032 report and active-task record. Three earlier Ownership attempts exposed only checkpoint metadata-contract issues and caused no scope or evidence change. Final Agent Task Ownership #3186 run `29864789104` and final-gate CI #4343 run `29864789391` succeeded; comments/reviews/threads were empty, Canary `main` had no task-start drift, and PR #691 merged by expected-head squash as `212d5e5c4ecbb0bd392880019747e2370299c748`.

Authoritative lifecycle PR #692 final head `18751315a53c5f0af82581b447b14f90f9c9c742` changed exactly the active-delete/archive-add lifecycle paths. Agent Task Ownership #3188 run `29865034951` and final-gate CI #4344 run `29865035270` succeeded; comments/reviews/threads were empty, Canary `main` had no drift from the governance merge, and PR #692 merged by expected-head squash as `fda6d01b93929ea998965354908062eb6e4e1424`.

OAM-032 does not claim title-definition or unlock-threshold parity, completeness of every cross-domain eligibility check, map/Drome/Goshnar or other TODO-backed title conditions, persistence atomicity or crash recovery, exact protocol compatibility, maintained-client parsing/rendering correctness, physical-client Titles E2E closure, or full Real Tibia parity.

# Current state''',
    ),
    (
        '''Canary reconciliation base: 0fca8ced2d952eab744238f826af81cb9ee135b1
Otheryn target head after OAM-031: 86e4b08c28ede2f35c215a7c2327a579f4a61419
maintained OTClient: a6868920443dc285656bd016acdb2c1ea566e511
OAM-001..OAM-031: feature/lifecycle complete
OAM-031 task: archived
OAM-032: NOT STARTED''',
        '''Canary reconciliation base: fda6d01b93929ea998965354908062eb6e4e1424
Otheryn target head after OAM-032: f5f21347c578a382cf0c52dbb4c69673ab3b05a9
maintained OTClient: a6868920443dc285656bd016acdb2c1ea566e511
OAM-001..OAM-032: feature/lifecycle complete
OAM-032 task: archived
OAM-033: NOT STARTED''',
    ),
    (
        '| OAM-001..OAM-031 | completed | preserve durable evidence |\n| OAM-032+ | planned, not active | only after this reconciliation merges: perform fresh live-state/open-PR/ownership and exact target/upstream/legacy preflight, then select one dependency-valid canonical package |',
        '| OAM-001..OAM-032 | completed | preserve durable evidence |\n| OAM-033+ | planned, not active | only after this reconciliation merges: perform fresh live-state/open-PR/ownership and exact target/upstream/legacy preflight, then select one dependency-valid canonical package |',
    ),
    (
        '- OAM-031 does not claim full Bestiary parity, exhaustive kill-stage/reward correctness, Charm correctness, monster-definition parity, exact protocol/client rendering compatibility, persistence completeness, tracker refresh correctness under every runtime state, database durability, physical-client Bestiary E2E closure, or full Real Tibia parity.',
        '- OAM-031 does not claim full Bestiary parity, exhaustive kill-stage/reward correctness, Charm correctness, monster-definition parity, exact protocol/client rendering compatibility, persistence completeness, tracker refresh correctness under every runtime state, database durability, physical-client Bestiary E2E closure, or full Real Tibia parity.\n- OAM-032 does not claim title-definition or unlock-threshold parity, completeness of every cross-domain eligibility check, map/Drome/Goshnar or other TODO-backed title conditions, persistence atomicity or crash recovery, exact protocol compatibility, maintained-client parsing/rendering correctness, physical-client Titles E2E closure, or full Real Tibia parity.',
    ),
    (
        'Merge this program-only OAM-031 completion reconciliation after exact-head Ownership/CI/review gates. Only then may a fresh OAM-032 preflight begin. OAM-032 is NOT STARTED by this record.',
        'Merge this program-only OAM-032 completion reconciliation after exact-head Ownership/CI/review gates. Only then may a fresh OAM-033 preflight begin. OAM-033 is NOT STARTED by this record.',
    ),
]

for old, new in replacements:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"expected exactly one match, found {count}: {old[:100]!r}")
    text = text.replace(old, new, 1)

path.write_text(text, encoding="utf-8")
