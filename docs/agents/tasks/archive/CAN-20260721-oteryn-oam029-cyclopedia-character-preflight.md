---
task_id: CAN-20260721-oteryn-oam029-cyclopedia-character-preflight
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-029
status: completed
agent: "GPT-5.6 Thinking"
branch: docs/oam-029-cyclopedia-character-lifecycle
base_branch: main
created: 2026-07-21
updated: 2026-07-21
completed: 2026-07-21
last_verified_commit: "a5e5565d546a530fc3a3010deb65e9283f6eacab"
risk: medium
related_pr: "655"
depends_on:
  - completed OAM-028 cyclopedia
  - completed OAM player-persistence
blocks:
  - OAM-030
modules_touched:
  - cyclopedia-character
---

# OAM-029 Cyclopedia Character lifecycle archive

Final disposition:

```text
cyclopedia-character → ADAPT
```

## Immutable task-start baselines

- Canary `ad267a87b3f565daf7e5901d80fbafb5a02b623c`
- Otheryn `1521906ffa8bd83ff2b35b0feadab4a44ea6df05`
- fresh upstream Canary `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`
- maintained OTClient `a6868920443dc285656bd016acdb2c1ea566e511`

## Accepted boundary

OAM-029 imported only the reviewed PR #188 Cyclopedia Character hunk in `PlayerCyclopedia::loadRecentKills`: the recent-PvP `count(*)` subquery now uses the same 70-day window as the returned rows. Bestiary, Bosstiary, Charms, Titles, protocol and maintained-client changes were excluded.

## Target evidence

```text
Otheryn PR #59 final head: 5f8f629ca78bcaf8636e2751ef60ae5ce9ab9a85
autofix.ci #173 run 29807291416: SUCCESS
CI #210 run 29807291563: SUCCESS after retry of transient Docker Quickstart Smoke only
Required #194 run 29807291333: SUCCESS after re-evaluation
Linux debug Run Tests: SUCCESS
test artifact: 8486265013
test digest: sha256:c4eb1f8815e77b3cb7fb243beea00d3e17d2c7a66183ad057b28d1fad59dbb47
target squash merge: 908834adc7d7e7e4ced7404391c7966b1c961b18
```

The Docker Quickstart Smoke retry passed without any code or head change. Target comments/reviews/threads were empty and Otheryn `main` had no task-start drift before expected-head squash merge.

## Canary governance evidence

```text
governance PR #655 final head: 1dd84ff459d29a7c734fed8e16f01be20363e73f
Agent Task Ownership #2969 run 29808583515: SUCCESS
final-gate CI #4123 run 29808618659: SUCCESS
governance changed paths: exactly 2
comments: 0
reviews: 0
review threads: 0
governance squash merge: a5e5565d546a530fc3a3010deb65e9283f6eacab
```

Canary `main` had no task-start drift through the governance merge gate.

## Explicit non-claims

OAM-029 does not claim full Cyclopedia Character parity, exact packet-byte compatibility, death-history correctness, KV/store-summary parity, database query performance, retained-history policy, maintained-client rendering correctness, physical-client Cyclopedia Character E2E closure, or full Real Tibia parity.

## Lifecycle state

Target and governance stages are merged. This lifecycle change owns only active-task deletion and archive addition. Separate one-file durable program reconciliation remains mandatory. OAM-030 remains NOT STARTED until reconciliation merges.
