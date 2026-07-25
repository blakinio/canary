# OAM-046 configuration revalidation

## Final disposition

`configuration → ADAPT`

## Baselines and delivery

- Canary OAM-046 preflight merge: `a1af14078de0450eb138a2f087e71104c03da4ca`
- Canary governance task-start main: `5463786e682c7820d201eeaff268cb6ef6bfd4f7`
- Otheryn target task-start main: `e8f683e61427e9967cbc180b837220d4b7487d85`
- Reviewed current-upstream Canary: `7323503b3dc61ed86bf1f04a611b2d0aec64b35a`
- Otheryn feature final head: `f9aa4261302eb3a42b7b9d9d5bb8e907f5cde7f8`
- Otheryn feature merge: `e05109ac6b98fe6761ed7ed7e933b0610b219911`
- Otheryn lifecycle/archive merge: `415f559f829c83d79d9c609e7f421d2449e59d74`

## Canonical responsibility

Canonical `configuration` owns typed server configuration keys and defaults, `config.lua` loading and reload state, package-scoped default distribution, and the server-side OTCR feature-list snapshot parsed from configuration.

It does not own the gameplay, protocol or client behavior controlled by configuration values; production secret management; environment-specific deployment policy; exhaustive concurrent reload synchronization; or physical-client interpretation of every feature ID.

## Exact source evidence

Pre-adaptation roots were pinned across Otheryn, reviewed upstream and live legacy Canary:

- `src/config/CMakeLists.txt`: blob `7a5a5058a22447091dd20e6190911e7f95937a98` in all three baselines;
- target/upstream `configmanager.hpp`: blob `c3027c491cbc326a3f66d2ed39a19ad7856ca6cf`; live legacy `8c1e90a7f0f1f894879b54a2de9971ffaeb48e1f`;
- target/upstream `config_enums.hpp`: blob `1676d0ac445e4cd83e91fc57ca405b4a0dccfb55`; live legacy `4753549d77a2e97a774c90b3d2aed371f06f4e0d`;
- target `configmanager.cpp`: blob `48c0637ba870cb25d119c16fc21d4134d6bdac15`; upstream `b8d433b6a7f178864f4bd07c131fd78d5bccc832`; live legacy `74c8a6f558257aa8bddf57f56116838390dcb25c`;
- target `config.lua.dist`: blob `add3df239fb22592b7c63d166f880d0c31098ba2`; upstream `08ffe407ac4dadcfe787a13cc54df9c705565226`; live legacy `021dc3e49aadbecead4d5b6d7d3b7ca6243b776e`.

Target composition and Forge defaults remain accepted package-external deltas. Exact file identity or compilation alone was not accepted as `REUSE` proof because configuration loading retains mutable process state.

## Isolated target defect

`ConfigManager::loadLuaOTCFeatures()` appended parsed values directly into retained `enabledFeaturesOTC` and `disabledFeaturesOTC` vectors on every successful load. Repeated successful loads could therefore duplicate IDs, preserve IDs removed from a later custom table and retain disabled IDs when `OTCRFeatures` was later omitted.

A failed `luaL_dofile` returns before the feature parser, so failed-load retention already behaved consistently and was not changed.

## Bounded adaptation

The parser now builds local enabled and disabled vectors for the current successful Lua snapshot and moves both into the retained members after parsing. When `OTCRFeatures` is absent, the replacement snapshot is exactly enabled `{101, 102, 103, 118}` with no disabled IDs.

The adapted `src/config/configmanager.cpp` blob is `18a52bb1095576cc2147bf8581d1007fcef90215`. No key enum, public getter, unrelated default, feature behavior, production configuration, secret policy, protocol path or client implementation changed.

## Focused target contract

Otheryn feature PR #105 added deterministic coverage for:

- a first custom enabled/disabled snapshot;
- a second successful custom snapshot replacing rather than appending or preserving stale IDs;
- omission of `OTCRFeatures` replacing both lists with the bounded fallback;
- a repeated fallback load remaining idempotent.

The fixture uses the existing unit-test target and adds no production test seam or second harness.

## Rejected hypotheses

- Accept shared CMake/header roots or successful compilation as sufficient `REUSE` evidence.
- Import legacy-only keys or defaults without package-specific target requirements.
- Expand the correction into generic concurrent reload redesign, secret management or deployment policy.
- Claim controlled feature, protocol or client correctness from server-side list replacement.
- Rewrite the configuration subsystem when one bounded local correction preserves its structure.

## Exact-head target gates

Otheryn feature PR #105 final head `f9aa4261302eb3a42b7b9d9d5bb8e907f5cde7f8` passed:

- Autofix `30151341764`;
- CI `30151341862`;
- Required `30151341775`.

Comments, submitted reviews and review threads were empty; Otheryn `main` remained at task-start `e8f683e61427e9967cbc180b837220d4b7487d85`; expected-head squash merge produced `e05109ac6b98fe6761ed7ed7e933b0610b219911`.

Otheryn lifecycle PR #106 changed only the active/archive task path. Required `30158852271` succeeded, comments/reviews/threads were empty, target `main` remained at the feature merge, and expected-head squash merge produced `415f559f829c83d79d9c609e7f421d2449e59d74`.

## Final conclusion

OAM-046 is `configuration → ADAPT`. The inherited typed configuration model remains canonical, but successful OTCR feature loads could not be reused unchanged because retained feature vectors did not represent the current snapshot. One bounded parser correction and focused deterministic fixtures close the accepted package without expanding ownership.

## Nonclaims

OAM-046 does not claim exhaustive one-to-one correspondence for every enum, Lua identifier or default across target, upstream and legacy; concurrent reload/read safety or atomic replacement of the complete configuration map; production configuration correctness, secret handling or environment-specific behavior; gameplay, protocol, transport, login or economy correctness controlled by configuration values; maintained-client or physical-client correctness for every feature ID; complete rollback semantics after later parsing or callback failures; or full Oteryn production readiness.
