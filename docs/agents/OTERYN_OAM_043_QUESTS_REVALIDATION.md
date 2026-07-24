# OAM-043 quests revalidation

## Final disposition

`quests → ADAPT`

## Baselines and delivery

- Canary OAM-043 preflight merge: `df7abb0cfe4b05ed11da7b3a6a0dcddbefb62375`
- Canary post-preflight reconciliation merge: `13ec3077babba0ac81bb1e30e79f0ea4827ae2fe`
- Canary governance task-start main: `5641a7ac2420f5a3d512325423088890e92ac3cb`
- Otheryn target task-start main: `3a37f3d5e4c01ddf4469f1c71461c40ca749142f`
- Otheryn feature ready head: `7a783c65e83a9fead651e38f336b10cbffe7a19b`
- Otheryn validation-sync head: `333b7047f8ecc660a84b215e9a4149b10d083c35`
- Otheryn feature merge: `6512d78004ae2540784b3e67592a92a903554cf6`
- Otheryn lifecycle/archive merge: `3f3c15917610e45430aa3902d110806dd25e10a8`

## Canonical responsibility

Canonical `quests` owns quest scripts and storage transitions, AID/UID/item/position mechanics, rewards and access, and NPC/spawn/map dependencies. It excludes whole-world parity claims and forbids promoting unresolved dynamic handlers to implemented behavior.

Its hard dependencies, canonical `otbm-tooling` and `player-persistence`, were formally completed by OAM-040 and OAM-004. OAM-043 reused Canary's quest-map validator and deterministic Unified OTBM World Index as external evidence infrastructure; no parser, scanner, generated map evidence or OTBM binary was copied into Otheryn.

## Exact inventory and complete evidence

The exact three-way inventory covered the two canonical quest roots at pinned target, current-upstream and legacy baselines. Manifest SHA-256 `391e38d963b1a791e4fd59edf8ce6adbb4a75dfc8e8a34da351c50f080267925` recorded:

- target: `978` files;
- current upstream: `978` files;
- legacy: `981` files;
- `973` paths identical in all three repositories;
- `5` paths where target and current upstream are identical and legacy diverges;
- `3` legacy-only paths;
- no target-only, upstream-only, all-divergent or target/legacy-only class.

Identity alone was not accepted. Complete source scan digest `a97442a2e77aee6cd02ba094a8158965a1da9681d0426114c7cd1c3546e3ef40` covered all `978` selected target files and produced `12,027` static evidence entries, including `2,016` storage references. It retained `1,045` dynamic expressions as unresolved rather than evaluating them.

Configured map SHA-256 `a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2` produced World Index SHA-256 `6c22cd26d4414aa094af1d00be7f62190a441e270ee7a478b55449bf92e55e7a` with zero unknown attribute tails. Complete correlation recorded `8,860` confirmed, `484` script-only and `2,683` unresolved findings, with zero map-only and zero conflicting findings.

## Accepted bounded adaptation

OAM-043 changed exactly six quest-source paths:

1. `hero_of_rathleton/actions_reward.lua`
   - corrected the reward hook from the unregistered spelling `The Professors Nut` to canonical catalogue entry `The Professor's Nut`.

2. `soulpit/soulpit_fight.lua`
   - corrected an undefined `creature` reference inside `onUse(player, ...)` to the actual `player` parameter;
   - retained the target's generic `Encounter:countMonsters` implementation and rejected the redundant legacy-local override.

3. `the_ancient_tombs/actions_oasis_lever_door.lua`
   - restored timed transformation of open door item `1663` back to closed item `1662` with lever/carrot cleanup;
   - retained only map-backed AID `12107`.

4–6. Restored exactly three legacy-only `The Beginning` handlers:
   - tutorial movement/stop AIDs;
   - Zirella UID `50085` door gate;
   - Zirella dead-tree/branch/cart item mechanics.

Dedicated candidate-donor correlation recorded `47` confirmed and zero script-only findings for those three missing handlers. The resulting canonical quest inventory is `981` files.

## Rejected donor hypotheses

- Legacy Ancient Tomb AID `12108` was classified `script-only` with zero configured-map placements and was not registered.
- Legacy Ape City and Wrath of the Emperor variants call `hasAccountQuestAccess` and `unlockAccountQuestAccess`; exact target search proved those prerequisite APIs do not exist, so existing character-storage behavior was retained.
- The legacy Soulpit-local monster counter was not imported because target generic Encounter/Zone ownership already implements that contract.
- The full legacy quest tree and all five divergent legacy variants were not copied.
- The `484` shared script-only findings and `1,045` dynamic expressions remain evidence boundaries, not authorization for broad remediation.

## Source-contract proof

The focused Otheryn contract verifies:

- canonical achievement lookup and the corrected Soulpit receiver;
- generic Encounter counter ownership without a duplicate local override;
- timed oasis-door closure while rejecting AID `12108`;
- exact map-backed `The Beginning` AID/UID/item/position contracts;
- absence of unavailable account-wide quest APIs;
- representative Blue Valley KV persistence handoff;
- final `981`-file canonical quest inventory.

## Exact-head target gates

Otheryn feature PR #98 passed two exact-head matrices:

- ready head `7a783c65e83a9fead651e38f336b10cbffe7a19b`: autofix `30090686762`, CI `30090686923`, Required `30090686740`, Repository Audit `30090564163`;
- validation-sync head `333b7047f8ecc660a84b215e9a4149b10d083c35`: autofix `30091648723`, CI `30091648878`, Required `30091648720`, Repository Audit `30091648732`.

Fast Checks, Lua Tests, Linux debug/release, Linux full unit tests, Windows CMake/Solution, macOS and selected runtime smokes succeeded. Comments, submitted reviews and review threads were empty, and target `main` had no task-start drift before expected-head squash merge `6512d78004ae2540784b3e67592a92a903554cf6`.

Otheryn lifecycle PR #99 changed only the task active/archive lifecycle path. Required `30093061770` succeeded, comments/reviews/threads were empty, target `main` had no drift from the feature merge, and the lifecycle PR squash-merged as `3f3c15917610e45430aa3902d110806dd25e10a8`.

## Final conclusion

OAM-043 is `quests → ADAPT`. The accepted package is limited to six exact quest-source changes supported by complete inventory, deterministic source/map evidence and focused target contracts. It does not authorize broad quest remediation or architecture changes.

## Nonclaims

OAM-043 does not claim exhaustive correctness of every quest, reward, access gate, storage transition or NPC/spawn dependency; execution or ownership closure for the `484` shared script-only findings or `1,045` unresolved dynamic expressions; a proven progression graph from lexical storage evidence; exact Real Tibia quest/dialogue/timing parity; protocol/client UI parity; physical-client quest E2E closure; production gameplay parity; or full world-content readiness.
