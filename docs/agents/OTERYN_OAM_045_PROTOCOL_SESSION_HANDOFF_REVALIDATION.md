# OAM-045 protocol session handoff revalidation

## Final disposition

`protocol-session-handoff → ADAPT`

## Baselines and delivery

- Canary OAM-045 preflight merge: `2798dce948d8bf27f9b1325356d6db4676a8b6ba`
- Canary governance task-start main: `93413bd53e9a40f0ff3c4f55986036b10be44e0f`
- Otheryn target task-start main: `e1eed52119ba21a29cb29cbac0793ed2a2b9d0c6`
- Reviewed current-upstream Canary: `7323503b3dc61ed86bf1f04a611b2d0aec64b35a`
- Otheryn feature final head: `77c46466c79fd5bda02ee7cdf9c07af97c110705`
- Otheryn feature merge: `597ba62c558ed4e35db38502903ae83e0b2921ec`
- Otheryn lifecycle/archive merge: `e8f683e61427e9967cbc180b837220d4b7487d85`

## Canonical responsibility

Canonical `protocol-session-handoff` owns the bounded in-process profile-hint state machine: registration by remote IP/profile/session/character set, profile-allowance filtering, overlapping-character replacement, bounded capacity, claim selection by IP and optional wire behavior, mixed-wire ambiguity rejection, session/character/version matching, one-shot consumption, reusable refresh and cleanup, and enforcement of hint and lease expiry.

It does not own password or token authentication, secure token issuance/redemption, login packet serialization, socket framing, checksum, sequence, XTEA or compression, game-world player ownership, generic cross-process fencing, distributed consistency or physical-client orchestration.

## Exact source evidence

Before target adaptation, Otheryn, reviewed current upstream, live legacy Canary and the OAM-006 physically tested Otheryn revision shared exact roots:

- `protocol_session_hint.hpp` blob `446e7769196fb9a750e13c8402b38c8752243729`;
- `protocol_session_hint.cpp` blob `3e57e16649e20121f52c6c4b67b632808b7af363`.

Exact source identity established continuity but did not prove every state invariant. The adapted Otheryn implementation is blob `e53e430122c746ee9254e4e80eac66a247a59317`.

## Isolated target defects

The target proof isolated two package-owned correctness defects.

### Lease deadline was ineffective

`claimByIp()` issued a lease with a 30-second `expiresAt`, while reusable hints can remain valid for 24 hours. The inherited consume path checked only whether the lease was structurally non-empty and then searched the still-valid hint collection. It did not reject `lease.expiresAt <= now`, allowing a stale lease to consume a reusable candidate after its claim window.

The adaptation fails closed before locking or candidate lookup when the lease deadline has passed.

### Replacement could evict an unrelated hint

The inherited registration path enforced the 512-entry capacity limit before removing an overlapping-character hint being replaced. At full capacity, a normal replacement could therefore evict the unrelated oldest entry and only then remove the superseded entry.

The adaptation performs overlapping-character cleanup first and applies the unchanged capacity check to the resulting collection. A true 513th independent entry still evicts the oldest hint.

## Focused target contract

Otheryn feature PR #103 added deterministic coverage for:

- exact session, case-insensitive character and client-version matching;
- current-profile one-shot consumption and removal;
- reusable profile reclaim, refresh and behavior-scoped cleanup;
- rejection of an expired lease while retaining the independently valid reusable hint;
- ordinary overlapping-character replacement;
- replacement at full capacity without unrelated eviction;
- mixed-wire ambiguity rejection and explicit behavior filtering;
- blocked-profile registration rejection;
- true capacity overflow and oldest-entry eviction.

The fixtures use local store instances and the existing unit-test target. They add no production test seam or second harness.

## Rejected hypotheses

- Accept exact target/upstream/legacy identity as sufficient `REUSE` proof.
- Expand the adaptation into authentication, transport, login serialization or generic session fencing.
- Treat SHA-256 storage, mutex use or TTLs as cryptographic, replay or race-freedom proof.
- Extend OAM-006 current-profile physical continuity to every hint branch or legacy profile.
- Rewrite the state machine when two bounded local corrections preserve its structure.

## Exact-head target gates

Otheryn feature PR #103 final head `77c46466c79fd5bda02ee7cdf9c07af97c110705` passed:

- Autofix `30125033564`;
- CI `30125033725`;
- Required `30125033619`.

Fast Checks, Lua Tests, Docker, Linux release, Linux debug with registered unit tests, Windows CMake/Solution, macOS and applicable runtime smokes succeeded. Comments, submitted reviews and review threads were empty; Otheryn `main` remained at task-start `e1eed52119ba21a29cb29cbac0793ed2a2b9d0c6`; expected-head squash merge produced `597ba62c558ed4e35db38502903ae83e0b2921ec`.

Otheryn lifecycle PR #104 changed only the active/archive task path. Required `30126189758` succeeded, comments/reviews/threads were empty, target `main` remained at the feature merge, and expected-head squash merge produced `e8f683e61427e9967cbc180b837220d4b7487d85`.

## Final conclusion

OAM-045 is `protocol-session-handoff → ADAPT`. The inherited state machine remains the canonical structure, but it cannot be reused unchanged because lease expiry and replacement-at-capacity invariants were ineffective. Two bounded local changes and focused deterministic fixtures close the accepted package without expanding ownership.

## Nonclaims

OAM-045 does not claim cryptographic strength, collision resistance or constant-time session-hash comparison; replay resistance across complete login-to-game orchestration; race freedom beyond the reviewed process-local mutex; multi-process or distributed consistency; secure authentication-token behavior; transport or login-protocol closure; physical-client parity for Tibia 11.00, CipSoft 8.60 or OTCv8; production protocol-stack readiness; or full gameplay parity.
