# OAM-042 NPCs revalidation

## Final disposition

`npcs → REUSE`

## Baselines and delivery

- Canary OAM-042 preflight merge: `c86e805910d87dc8db9a212b18645e27c28c779c`
- Canary reconciliation task-start main: `f28acc8e959e79448ea99dead2500a64460f3aff`
- Otheryn target task-start main: `7c54172adfa612fa143d11630f5a341ff4c82338`
- Otheryn final proof head: `e7b8f3a121f931a83ef016ceb6d30ad21dcdf74d`
- Otheryn target proof merge: `0d01f077f80c2d4cd3d4231d2ffb9416874ba54e`
- Otheryn lifecycle/archive merge: `3a37f3d5e4c01ddf4469f1c71461c40ca749142f`

## Canonical responsibility

Canonical `npcs` owns NPC definitions and registration, dialogue state, shops, travel, NPC-owned quest hooks and placement evidence. Generic quest progression, storage/action/map-mechanic/reward ownership outside NPC contracts remains assigned to canonical `quests`.

The only hard dependency, canonical `otbm-tooling`, was resolved by OAM-040 as external Canary evidence infrastructure. OAM-042 reused OAM-041 deterministic placement/definition evidence and did not copy the OTBM parser, scanner, world index or generated evidence into Otheryn.

## Exact reviewed target/upstream identity

The clean Otheryn target and reviewed current `opentibiabr/canary` upstream shared exact Git blobs for the bounded contract paths:

- `src/creatures/npcs/npcs.cpp`: `5a5d37d4085c9b564936f721469c831b12fee6a4`
- `src/creatures/npcs/npc.cpp`: `2aee02b7b0ff6b69c868365ac4ba102b5b115f40`
- `data/npclib/load.lua`: `ad7cb718531212facdca6b842cbf03e63945f379`
- `data/npclib/npc_system/modules.lua`: `40a58c2ca7c74e28c51565604390ad80dcdb30af`
- `data-otservbr-global/npc/harlow.lua`: `c8eae6fe74881ab4c08305cd383e92517d14feae`
- `data-otservbr-global/npc/rashid.lua`: `b1f8b022e07f83cbe401c410efb3efa10f3ec697`
- `data-otservbr-global/world/otservbr-npc.xml`: `0a72085b7bbdfca73b794e631cc2bab790d8fcef`

Identity alone was not accepted. The target-local source-contract proof covered:

- core npclib and active datapack NPC loading;
- case-insensitive NPC type registration;
- think, appear, disappear, move, say, buy, sell, item-inspection and channel-close callbacks;
- Lua interaction and shop-window surfaces;
- canonical shop normalization and duplicate rejection;
- dialogue module loading;
- travel interaction, premium, level, PZ-lock, cost, cooldown, destination, teleport and reset behavior;
- Harlow's Blood Brothers `VengothAccess` gate, 100-gold fare and destination `Position(32858, 31549, 7)`;
- Rashid's travelling-trader storage transitions, trade gate and explicit shop catalogue.

No concrete `npcs`-owned target defect was isolated. No target-local runtime, datapack, map, protocol, client, schema or deployment adaptation was justified.

## Reused deterministic OTBM evidence

OAM-041 remains authoritative for the static NPC placement and definition-correlation layer. Its full active-datapack scan included `1,008` static NPC placements and retained the duplicate `Harlow` definition ambiguity plus `310` nonliteral dynamic creation calls as explicit unresolved evidence.

OAM-042 did not reinterpret those findings as handled. They remain bounded unknowns and must fail closed in later package work unless exact active-root or runtime evidence resolves them.

## Exact-head target gates

Otheryn PR #96 final head `e7b8f3a121f931a83ef016ceb6d30ad21dcdf74d` changed exactly the proof document, active task, focused unit contract and existing unit-test target registration. It changed no production runtime, datapack, map, binary, protocol, client, schema or deployment path.

Exact-head gates succeeded:

- autofix: `30077147255`;
- CI: `30077147345`;
- Required: `30077147262`;
- Fast Checks and Lua Tests;
- Linux release and Linux debug;
- Linux debug full unit tests, including OAM-042;
- Canary/global runtime smoke paths selected by the workflow;
- macOS build/runtime smoke;
- Windows Solution and CMake paths.

Comments, submitted reviews and review threads were empty. Otheryn `main` remained at target task-start base `7c54172adfa612fa143d11630f5a341ff4c82338` until expected-head squash merge `0d01f077f80c2d4cd3d4231d2ffb9416874ba54e`.

Otheryn lifecycle PR #97 changed only active-delete/archive-add task paths. Required `30078308339` succeeded without an application build, and PR #97 squash-merged as `3a37f3d5e4c01ddf4469f1c71461c40ca749142f`.

## Final conclusion

OAM-042 is `npcs → REUSE`. The evidence supports retaining the clean target implementation and reviewed current-upstream NPC contracts without adopting legacy runtime or copying Canary tooling.

## Nonclaims

OAM-042 does not claim factual completeness of every individual NPC conversation, resolution of the duplicate Harlow definition ambiguity, execution/correctness of every nonliteral dynamic NPC or quest-hook call, generic quest progression correctness, exact Real Tibia shop/dialogue/travel parity, protocol/client UI parity, production gameplay parity, physical-client NPC E2E closure or full world-content parity.
