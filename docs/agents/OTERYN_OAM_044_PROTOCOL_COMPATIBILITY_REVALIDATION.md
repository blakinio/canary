# OAM-044 protocol compatibility revalidation

## Final disposition

`protocol-compatibility → REUSE`

## Baselines and delivery

- Canary OAM-044 preflight merge: `47611c10be8a2262d66421c9da65de6cc5c7264d`
- Canary governance task-start main: `ad8b978236e6dfa8c40b06170f19f281b84b395d`
- Otheryn target task-start main: `3f3c15917610e45430aa3902d110806dd25e10a8`
- Reviewed current-upstream Canary: `7323503b3dc61ed86bf1f04a611b2d0aec64b35a`
- Legacy Canary baseline: `a5cafe1b7ce148af59c64d1382963ac6ac633334`
- Maintained-client baseline: `b3bcea2a95959bb4e92cc0b80cd49f36b63699b2`
- Otheryn feature ready head: `29d196e1b7d084813e24d368bd9e70329e16d0b3`
- Otheryn feature final-sync head: `62a42372e2225b71aaa0066cc934f684e830913c`
- Otheryn feature merge: `5c8f48e2a7cb7f841cfb6614e8e804245f17c0ca`
- Otheryn lifecycle/archive merge: `e1eed52119ba21a29cb29cbac0793ed2a2b9d0c6`

## Canonical responsibility

Canonical `protocol-compatibility` owns protocol-profile discovery, version/wire-family/asset-signature resolution, support and item-mapper policy, account/game login-layout metadata, transport/challenge selection metadata, server `ProtocolFeature` inventories and the maintained-client version-gated `GameFeature` inventory.

It does not own socket framing, checksum, sequence, XTEA or compression runtime; account authentication and serialized login exchange; session-handoff leases; broad gameplay packet semantics; physical-client orchestration; or deployment behavior. Those boundaries remain assigned to `network-transport`, `login-protocol`, `protocol-session-handoff`, completed canonical `protocol`, and later E2E work.

## Exact source continuity

Target and reviewed current upstream have identical canonical server roots:

- `protocol_profile.hpp` blob `b9f1eec01e1ba348c22315be43ccefe74b210e45`;
- `protocol_profile.cpp` blob `5405c343cfa2c2d75a173d6678ecf8afc7690120`.

The maintained-client feature root `modules/game_features/features.lua` is blob `8b458b864ad765185fd856414f2c097d565a5a22`.

These three roots are also byte-identical to the roots exercised by OAM-006 physical run `29531221365`, which passed two current-profile protocol-1525 login/relog cycles. This proves bounded continuity for the current profile only. It does not extend that physical result to Tibia 11.00, CipSoft 8.60 variants or OTCv8.

Legacy Canary diverges at the profile roots and includes more granular transport-profile hardening. Those differences were reviewed but rejected from this package because they belong to transport or login ownership and no target-owned compatibility defect was isolated.

## Bounded profile and feature contract

Otheryn feature PR #100 added a focused non-production unit contract covering:

- all six registered profiles: current, Tibia 11.00, CipSoft 8.60 vanilla, extended-assets, Canary-extended and blocked OTCv8 8.60;
- deterministic resolution by client version, wire family and reviewed asset signatures;
- enabled/blocked support states and item-mapper policies;
- account/game login-layout metadata for current, 1100 and 860 boundaries;
- selected reviewed current server/client feature pairs;
- explicit fail-closed behavior for unsupported or blocked combinations.

The contract is intentionally not an exhaustive one-to-one mapping between every server `ProtocolFeature` and client `GameFeature`. Similar names were not treated as semantic or byte-layout proof.

## Rejected hypotheses

- Import legacy transport-profile splitting into `protocol-compatibility`.
- Infer semantic compatibility from similar server/client feature names.
- Extend OAM-006 current-profile physical evidence to Tibia 11.00 or 8.60.
- Claim byte-level compatibility for every packet or registered profile.
- Claim provenance or factual correctness for every proprietary asset signature.
- Absorb transport, login authentication or session-handoff behavior.
- Treat blocked OTCv8 8.60 as ready.

## Exact-head target gates

Otheryn feature PR #100 passed two exact-head matrices:

- ready head `29d196e1b7d084813e24d368bd9e70329e16d0b3`: Autofix `30106675779`, CI `30106676001`, Required `30106675816`;
- final-sync head `62a42372e2225b71aaa0066cc934f684e830913c`: Autofix `30111297337`, CI `30111297597`, Required `30111297475`.

Fast Checks, Lua Tests, Linux debug/release with registered unit tests, Windows CMake/Solution, macOS and applicable runtime smokes succeeded. Comments, submitted reviews and review threads were empty; Otheryn `main` remained at task-start `3f3c15917610e45430aa3902d110806dd25e10a8`; expected-head squash merge produced `5c8f48e2a7cb7f841cfb6614e8e804245f17c0ca`.

Otheryn lifecycle PR #101 changed only the active/archive task path. Required `30112638532` succeeded, comments/reviews/threads were empty, target `main` had no drift from the feature merge, and the lifecycle PR squash-merged as `e1eed52119ba21a29cb29cbac0793ed2a2b9d0c6`.

## Final conclusion

OAM-044 is `protocol-compatibility → REUSE`. The target/current-upstream registry is retained without production mutation. Exact current-profile source continuity, inherited physical evidence and focused profile fixtures are sufficient for the bounded package, while legacy physical parity and broad packet semantics remain explicit unknowns.

## Nonclaims

OAM-044 does not claim exhaustive correspondence between every `ProtocolFeature` and `GameFeature`; byte-level compatibility for every packet/profile; factual provenance of all asset signatures; physical-client login/world-entry parity for Tibia 11.00 or CipSoft 8.60 variants; OTCv8 readiness; transport/login/session-handoff closure; production gameplay parity; or full protocol-stack readiness.
