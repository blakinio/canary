# OAM-029 Cyclopedia Character Revalidation

## Final disposition

```text
cyclopedia-character ADAPT
```

## Immutable task-start baselines

- legacy/governance Canary: `ad267a87b3f565daf7e5901d80fbafb5a02b623c`
- Otheryn target: `1521906ffa8bd83ff2b35b0feadab4a44ea6df05`
- fresh upstream Canary: `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`
- maintained OTClient: `a6868920443dc285656bd016acdb2c1ea566e511`

Canonical `cyclopedia-character` depends only on completed `cyclopedia` and `player-persistence`. Its narrow server root is `src/creatures/players/components/player_cyclopedia.*`; the Character-tab client presentation directory is intentionally shared with the independent `titles` record.

## Adaptation evidence

Task-start Otheryn and fresh upstream shared exact `player_cyclopedia.cpp` blob `91a3235e53e5f7ca4da22649bff6bad34cf44e3a`. Current legacy differed with blob `b2b6d0f3283380f450b3c79874d5ce38ac2734a0`.

Merged legacy PR #188 was decomposed by canonical ownership. Its Cyclopedia Character portion is exactly one production hunk in `PlayerCyclopedia::loadRecentKills`: the outer recent-PvP row query already restricts results to the last 70 days, but the `count(*)` subquery historically counted all matching deaths. That mismatch can advertise pages backed only by stale historical rows. The accepted donor adds the same 70-day predicate to the count subquery so page count and returned rows use one presentation window.

The remaining PR #188 Bestiary, Bosstiary and Charms changes remain owned by their independent canonical packages and were not imported. No Titles, protocol, schema, map, asset, deployment or maintained OTClient change was included.

After the isolated adaptation, target `player_cyclopedia.cpp` matched reviewed current legacy blob `b2b6d0f3283380f450b3c79874d5ce38ac2734a0` at this path. This identity is corroborating evidence for the isolated donor, not a whole-module reuse claim.

Fresh open-PR audit found no active writer over `player_cyclopedia.*`. Open Canary work remained independently owned OTBM programme closure, NPC E2E and security/audit work.

## Target delivery

Otheryn PR #59 final head `5f8f629ca78bcaf8636e2751ef60ae5ce9ab9a85` changed exactly five intended paths:

- `docs/agents/tasks/active/OTH-20260721-oam029-cyclopedia-character-adapt.md`
- `docs/oam-029-cyclopedia-character-adapt.md`
- `src/creatures/players/components/player_cyclopedia.cpp`
- `tests/unit/game/CMakeLists.txt`
- `tests/unit/game/oam_029_cyclopedia_character_adapt_test.cpp`

Temporary materialization helper/workflow paths were removed before target PR creation. The focused proof requires the 70-day predicate in both the count subquery and outer result filter.

Draft CI #208 run `29807218934` and Required #192 run `29807218828` succeeded on draft head `e24c3d58cbae5d19102e8b048e744fc6ec88908a`.

The exact final head passed autofix.ci #173 run `29807291416`. CI #210 run `29807291563` initially concluded failure even though Linux debug compilation, runtime smoke, schema import and full `Run Tests` passed, as did Linux release, macOS, Windows and Docker image build. The failed-job retry isolated the failure to Docker Quickstart Smoke; on retry the PR-image quickstart smoke succeeded without any code or head change, and CI #210 concluded success. Required #194 run `29807291333` was then rerun so it could evaluate the updated green CI and concluded success. Linux debug test-log artifact `8486265013` has digest `sha256:c4eb1f8815e77b3cb7fb243beea00d3e17d2c7a66183ad057b28d1fad59dbb47`.

Target comments, submitted reviews and review threads were empty. Otheryn `main` remained at immutable target base `1521906ffa8bd83ff2b35b0feadab4a44ea6df05` through the merge gate. PR #59 merged by expected-head squash as `908834adc7d7e7e4ced7404391c7966b1c961b18`.

## Explicit non-claims

OAM-029 does not claim full Cyclopedia Character parity, exact packet-byte compatibility, death-history correctness, KV/store-summary parity, database query performance, retained-history policy, maintained-client rendering correctness, physical-client Cyclopedia Character E2E closure, or full Real Tibia parity.
