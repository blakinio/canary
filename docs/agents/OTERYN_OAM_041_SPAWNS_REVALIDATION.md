# OAM-041 spawns revalidation

## Final disposition

`spawns → REUSE`

## Baselines and delivery

- Canary OAM-041 preflight merge: `82da6f6c5284b13446c5e71d075e7b06c9252b67`
- Canary target-proof-plan merge: `5c2ec1df1b5be9494fbf97ba389bea8fd9070f58`
- Canary pinned evidence revision: `d1ad83056ec7930f067986909f66b8f20f1a1f44`
- Otheryn target task-start main: `9369b0719ff94997a9cf5a2d62853939744e6338`
- Otheryn final proof head: `2168ff23a7415b9aea8f66b7051995e7fd148691`
- Otheryn target proof merge: `de061aa6c75114192f1ef6b33f7b4857e502936c`

## Canonical responsibility

Canonical `spawns` owns static monster/NPC placement definitions, dynamic creation inventory and definition-to-placement evidence. Raid registry scheduling and ordered raid-event lifecycle remain owned by completed canonical `raids` / OAM-037; monster combat AI remains outside this package.

The only hard dependency, `otbm-tooling`, was formally resolved by OAM-040 as a cross-repository Canary evidence responsibility. OAM-041 consumed exact pinned Canary tools and reports without copying that toolchain into Otheryn.

## Target runtime proof

Otheryn and the reviewed fresh upstream shared exact canonical runtime roots:

- `spawn_monster.cpp`: `4c82217631ddf479faa5443025d43f99a0c927d1`
- `spawn_npc.cpp`: `21718ad80827a16e9a1b29bc9d649ad603bcf216`

Identity alone was not accepted. The target source-contract proof covers monster/NPC XML center-plus-offset placement, interval/default/rate scaling, player-presence blocking, removed-creature cleanup, maintenance-lane scheduling, monster boss exclusivity and weighted selection. The divergent legacy Canary runtime was rejected as a stronger whole-module donor because the reviewed target/upstream paths retain `DispatcherLane::Maintenance` scheduling safeguards absent at the corresponding legacy call sites.

## Deterministic external OTBM evidence

Successful Otheryn proof workflow run `30049543113` used pinned Canary Phase 4 tool blobs:

- `otbm_spawn_npc.py`: `4339e94f5875f4d7fd443c2359c15d10f205004f`
- `otbm_spawn_npc_validation.py`: `7f66f74b68b66e9acabe1ea1a5cbd404b1637e9b`
- `otbm_spawn_npc_tool.py`: `481c163d8048298900b33648b08b1fac5b60fefe`

It verified the target-configured map SHA-256 `a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2`, generated World Index SHA-256 `6c22cd26d4414aa094af1d00be7f62190a441e270ee7a478b55449bf92e55e7a` outside Git and emitted artifact digest `sha256:24997761f2140054606abf116b277f7af0ddeceefa7a59fcffb434ea31375be8`.

The full active `data-otservbr-global` scan found:

- `52,903` spawn groups;
- `84,294` static placements (`83,286` monsters and `1,008` NPCs);
- `318` complete untruncated findings;
- `310` nonliteral dynamic creation calls retained as unresolved.

The two error findings are the known duplicate `Harlow` NPC-definition ambiguity, not a newly isolated target runtime defect. OAM-041 does not guess which definition should win.

The final complete bounded region `32824,31275,7` through `32873,31324,7` produced untruncated reachability evidence and confirmed `34/34` selected groups plus `39/39` selected static placements with zero correlation findings.

Earlier over-broad/default-limit proof attempts correctly failed closed on truncated reachability diagnostics. They were rejected rather than treated as target defects; the final proof raised the diagnostic bound and required complete evidence.

## Exact-head target gates

Otheryn PR #92 final head `2168ff23a7415b9aea8f66b7051995e7fd148691` changed exactly four proof/task/test-registration paths and no production runtime, datapack, map, binary, protocol, client, schema or deployment path.

Exact-head gates succeeded:

- autofix: `30068408311`;
- CI: `30068408471`;
- Required: `30068408289`;
- Linux release and global/Canary runtime smokes;
- Linux debug schema, runtime smoke and full tests;
- macOS build/runtime smoke;
- Windows Solution and CMake paths.

Comments, submitted reviews and review threads were empty. Otheryn `main` remained at the PR base `5b6f62b33957472afba16f377b94993389abd145` until expected-head squash merge `de061aa6c75114192f1ef6b33f7b4857e502936c`.

## Final conclusion

No concrete `spawns`-owned target defect was isolated. OAM-041 is `REUSE`; no legacy runtime, datapack, map or generated evidence artifact was migrated.

## Nonclaims

OAM-041 does not claim execution or correctness of unresolved dynamic Lua calls, exhaustive live validation of all static placements, exact Real Tibia population/timing/placement parity, scheduler fairness under production load, raid lifecycle correctness beyond the separated OAM-037 boundary, physical-client gameplay E2E closure or full world-content parity.
