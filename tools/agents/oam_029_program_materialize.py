#!/usr/bin/env python3
from pathlib import Path

path = Path("docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md")
text = path.read_text(encoding="utf-8")

replacements = [
    (
        'updated: 2026-07-21T01:12:00+02:00\nlast_verified_commit: "ff694b9e908148fb12cca69a76fc2786d9a0f2c3"',
        'updated: 2026-07-21T09:05:00+02:00\nlast_verified_commit: "2a4b717448e55e1a2c24578df44eb981f8ae4bfd"',
    ),
    (
        '| OAM-028 | `cyclopedia → REUSE` | target `7e03405aea50d88fdbc27d0d2a7d95c7f1745946`; feature `a28e661c4119857eff36948c4549045f57eae545`; lifecycle `ff694b9e908148fb12cca69a76fc2786d9a0f2c3` |',
        '| OAM-028 | `cyclopedia → REUSE` | target `7e03405aea50d88fdbc27d0d2a7d95c7f1745946`; feature `a28e661c4119857eff36948c4549045f57eae545`; lifecycle `ff694b9e908148fb12cca69a76fc2786d9a0f2c3` |\n| OAM-029 | `cyclopedia-character → ADAPT` | target `908834adc7d7e7e4ced7404391c7966b1c961b18`; feature `a5e5565d546a530fc3a3010deb65e9283f6eacab`; lifecycle `2a4b717448e55e1a2c24578df44eb981f8ae4bfd` |',
    ),
    (
        '# Current state',
        '''# OAM-029 durable completion

Final disposition:

```text
cyclopedia-character ADAPT
```

Task-start baselines were Canary `ad267a87b3f565daf7e5901d80fbafb5a02b623c`, Otheryn `1521906ffa8bd83ff2b35b0feadab4a44ea6df05`, fresh upstream Canary `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`, and maintained OTClient `a6868920443dc285656bd016acdb2c1ea566e511`. Canonical `cyclopedia-character` depends only on completed `cyclopedia` and `player-persistence` and owns the narrow server root `src/creatures/players/components/player_cyclopedia.*`.

Task-start Otheryn and fresh upstream shared `player_cyclopedia.cpp` blob `91a3235e53e5f7ca4da22649bff6bad34cf44e3a`; reviewed current legacy differed with blob `b2b6d0f3283380f450b3c79874d5ce38ac2734a0`. Semantic decomposition of merged legacy PR #188 identified exactly one Cyclopedia Character production hunk: the recent-PvP outer row query already uses a 70-day window, while its `count(*)` subquery historically counted all matching deaths. OAM-029 adds the same 70-day predicate to the count subquery so page count and returned rows share one presentation window. Bestiary, Bosstiary, Charms, Titles, protocol and maintained-client changes were excluded.

Otheryn PR #59 final head `5f8f629ca78bcaf8636e2751ef60ae5ce9ab9a85` changed exactly five intended paths. Autofix.ci #173 run `29807291416` succeeded. Linux debug compilation, runtime smoke, schema import and full `Run Tests` succeeded; test-log artifact `8486265013` has digest `sha256:c4eb1f8815e77b3cb7fb243beea00d3e17d2c7a66183ad057b28d1fad59dbb47`. CI #210 run `29807291563` initially concluded failure only because Docker Quickstart Smoke failed after all code/build/test gates had passed; a failed-job retry passed on the unchanged exact head and CI #210 concluded success. Required #194 run `29807291333` was then rerun to evaluate the recovered CI and concluded success. Comments/reviews/threads were empty, target-main drift was none, and PR #59 merged by expected-head squash as `908834adc7d7e7e4ced7404391c7966b1c961b18`.

Canary governance PR #655 final head `1dd84ff459d29a7c734fed8e16f01be20363e73f` changed exactly the OAM-029 report and active-task record. Agent Task Ownership #2969 run `29808583515` and final-gate CI #4123 run `29808618659` succeeded. Comments/reviews/threads were empty, Canary `main` had no task-start drift, and PR #655 merged by expected-head squash as `a5e5565d546a530fc3a3010deb65e9283f6eacab`.

Authoritative lifecycle PR #656 final head `ed14520d265efa00128437e99df1b76b4df7b8ca` changed exactly the active-delete/archive-add lifecycle paths. Agent Task Ownership #2972 run `29808898548` and final-gate CI #4126 run `29808909750` succeeded. Comments/reviews/threads were empty, Canary `main` had no drift from the governance merge, and PR #656 merged by expected-head squash as `2a4b717448e55e1a2c24578df44eb981f8ae4bfd`.

OAM-029 does not claim full Cyclopedia Character parity, exact packet-byte compatibility, death-history correctness, KV/store-summary parity, database query performance, retained-history policy, maintained-client rendering correctness, physical-client Cyclopedia Character E2E closure, or full Real Tibia parity.

# Current state''',
    ),
    (
        '''Canary reconciliation base: ff694b9e908148fb12cca69a76fc2786d9a0f2c3
Otheryn target head after OAM-028: 7e03405aea50d88fdbc27d0d2a7d95c7f1745946
maintained OTClient: a6868920443dc285656bd016acdb2c1ea566e511
OAM-001..OAM-028: feature/lifecycle complete
OAM-028 task: archived
OAM-029: NOT STARTED''',
        '''Canary reconciliation base: 2a4b717448e55e1a2c24578df44eb981f8ae4bfd
Otheryn target head after OAM-029: 908834adc7d7e7e4ced7404391c7966b1c961b18
maintained OTClient: a6868920443dc285656bd016acdb2c1ea566e511
OAM-001..OAM-029: feature/lifecycle complete
OAM-029 task: archived
OAM-030: NOT STARTED''',
    ),
    (
        '| OAM-001..OAM-028 | completed | preserve durable evidence |\n| OAM-029+ | planned, not active | only after this reconciliation merges: perform fresh live-state/open-PR/ownership and exact target/upstream/legacy preflight, then select one dependency-valid canonical package |',
        '| OAM-001..OAM-029 | completed | preserve durable evidence |\n| OAM-030+ | planned, not active | only after this reconciliation merges: perform fresh live-state/open-PR/ownership and exact target/upstream/legacy preflight, then select one dependency-valid canonical package |',
    ),
    (
        '- OAM-028 does not claim Bestiary, Bosstiary, Charm, Cyclopedia Character, Titles or Houses child correctness, exact packet-byte compatibility, maintained-client parsing/rendering correctness, item/map/house presentation correctness, persistence completeness, runtime behavior, physical-client Cyclopedia E2E closure, or full Real Tibia parity.',
        '- OAM-028 does not claim Bestiary, Bosstiary, Charm, Cyclopedia Character, Titles or Houses child correctness, exact packet-byte compatibility, maintained-client parsing/rendering correctness, item/map/house presentation correctness, persistence completeness, runtime behavior, physical-client Cyclopedia E2E closure, or full Real Tibia parity.\n- OAM-029 does not claim full Cyclopedia Character parity, exact packet-byte compatibility, death-history correctness, KV/store-summary parity, database query performance, retained-history policy, maintained-client rendering correctness, physical-client Cyclopedia Character E2E closure, or full Real Tibia parity.',
    ),
    (
        'Merge this program-only OAM-028 completion reconciliation after exact-head Ownership/CI/review gates. Only then may a fresh OAM-029 preflight begin. OAM-029 is NOT STARTED by this record.',
        'Merge this program-only OAM-029 completion reconciliation after exact-head Ownership/CI/review gates. Only then may a fresh OAM-030 preflight begin. OAM-030 is NOT STARTED by this record.',
    ),
]

for old, new in replacements:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"expected exactly one match, found {count}: {old[:160]!r}")
    text = text.replace(old, new, 1)

path.write_text(text, encoding="utf-8")
print("materialized OAM-029 durable program reconciliation")
