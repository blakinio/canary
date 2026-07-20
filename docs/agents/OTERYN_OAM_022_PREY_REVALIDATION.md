# Oteryn OAM-022 Prey Revalidation

Date: 2026-07-20

Coordination: `OAM-022`

Canonical module: `prey`

Final disposition: **UNRESOLVED AT TASK START**

## Immutable task-start baselines

- Canary legacy/governance: `800142e65c2975e57647bf34128ab468532218f0`
- clean Otheryn target: `b90e287a40413102c87e8c7fa3d5c01ad401cb6d`
- fresh upstream Canary: `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`
- maintained OTClient: `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`

## Canonical dependency gate

`prey` depends on completed `player-persistence` and completed `protocol`. Its interaction with `wheel-of-destiny` does not broaden OAM-022 and does not authorize Wheel-owned changes.

The canonical scope includes Prey state/rerolls, bonuses, Hunting Tasks and related persistence/packets, while excluding Wheel allocation except explicit Task Shop integration.

## Fresh ownership and overlap preflight

At task start:

- Canary `main` is exactly `800142e65c2975e57647bf34128ab468532218f0`;
- Otheryn `main` is exactly `b90e287a40413102c87e8c7fa3d5c01ad401cb6d`;
- upstream Canary remains `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`;
- maintained OTClient remains `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`;
- no open Otheryn or maintained-OTClient PR owns OAM-022 work;
- no open PR matched Prey ownership directly;
- Canary PR #514 owns security-validation tooling and treats protocol implementation paths as read-only evidence only;
- Canary PR #600 owns bounded OTBM/E2E route tooling and scenarios;
- Canary PR #526 and #559 are evidence/documentation-only security work;
- Canary PR #479 is an unrelated archive-only cleanup.

No reviewed open PR currently writes `src/creatures/players/components/prey/**`, `data/modules/scripts/taskboard/**`, or Prey-specific target tests. Any protocol/client mutation remains disallowed unless fresh contract evidence proves it is necessary and non-overlapping.

## Selection rationale

After OAM-021 durable completion, `prey` is the smallest reviewed dependency-valid canonical package among the immediately eligible character-progression candidates. `wheel-of-destiny` has a separately active parity program and broad shared protocol/client/combat ownership, while `cyclopedia` is a wider multi-surface client/server domain. OAM-022 therefore selects only `prey` and does not absorb those programs.

## Required revalidation

Before classification or target write, OAM-022 must:

1. compare the exact task-start Otheryn Prey boundary with fresh upstream and reviewed legacy Canary history;
2. inspect maintained-OTClient Prey/Hunting Task packet support only where the canonical boundary requires it;
3. review persistence ownership against completed OAM-004 without restoring broad legacy player save code;
4. classify `REUSE`, `ADAPT`, `REVALIDATE`, `REWRITE`, `DO_NOT_MIGRATE`, or `EXPERIMENTAL_ONLY` from evidence rather than path presence;
5. implement or prove only the smallest coherent accepted target boundary;
6. preserve Wheel allocation, generic protocol, generic player persistence, maps/assets/schema/deployment and unrelated E2E work outside this package unless a specific dependency defect is proven.

## Lifecycle gate

OAM-022 is now selected but not yet classified. Required order remains target revalidation/proof, Canary governance reconciliation, separate lifecycle archive, then separate one-file durable program reconciliation. OAM-023 must not start before those stages are complete.
