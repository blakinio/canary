# GPT-5.6 Thinking — The Beginning handoff

Archived: 2026-07-14 18:56 Europe/Warsaw
Repository: `blakinio/canary`
Archive PR: supersedes #351

## User direction

Continue toward authentic Tibia behavior for the relevant historical version, while treating current Canary map/code and proved runtime behavior as authoritative. Historical sources may corroborate intent, but must not override current coordinates, item IDs, AIDs, UIDs, storages, town IDs, or engine APIs without evidence.

## Mandatory rules

- Read `AGENTS.md`, `docs/agents/README.md`, Real Tibia evidence/parity docs, `docs/ai-agent/OTBM_HD_PIPELINE.md`, `docs/ai-agent/OTBM_SCRIPT_RESOLUTION.md`, and `docs/agents/MODULE_CATALOG.md`.
- Use the existing OTBM item/mechanic audit, script resolver, renderer, and sprite export.
- Do not build another parser or renderer.
- Do not use AI-generated map imagery.
- Do not edit OTBM during an audit.
- Do not guess coordinates, item IDs, AIDs, UIDs, or storages.
- Classify findings only as `confirmed`, `map-only`, `script-only`, `unresolved`, or `conflicting`.
- Prepare evidence report first, repair plan second, and bounded implementation PRs last.

## Verified inputs

- Map SHA-256: `a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2`
- Asset catalogue SHA-256: `93ea5888174ef44b352d7c2b1f8061573a4a260bfaba4b7ec32ea836b9e411ab`
- Appearances SHA-256: `aa44a154f30c7ed59acc25f246286396e4043851ef0b54ef3cf3951e46d1ce50`

## Confirmed merged gameplay work

| PR | Merge commit | Result |
|---:|---|---|
| #145 | `b1992c7380416139f4a0a2eb7ea0d593be47fdb2` | 24 map-present tutorial MoveEvents restored; absent AIDs `50073` and `50089` not registered. |
| #149 | `19602c90128f8295d84a8dd673ea71222dcaed2d` | Dead tree `7753` → branch `7772` → Zirella cart `7751` progression restored. |
| #157 | `813a2ce39daced46802e6801e4abd275709b8672` | Carlos outfit/trade flow repaired; successful meat/ham sale advances stage 6 → 7. |
| #186 | `c654781f21269f557889ffab393a1e9ab2383b56` | Zirella door UID `50085` and reward tutorial UIDs `50093/50094` restored. |

## Critical correction

PR #204 (audit, merge `dfa535cbfdcb14a6fe4f19880a1281016d35b4c9`) and PR #207 (repair plan, merge `f96680987955cde24d4264e9473bde70501ed534`) contain a stale Carlos statement.

They say Carlos is still broken / PR #157 is stale candidate work. This is false: PR #157 is merged and current `data-otservbr-global/npc/carlos.lua` contains the repair.

Before using #204/#207 as the current queue, create a documentation-only correction PR that:

1. removes Carlos from outstanding defects;
2. records #157 as confirmed baseline;
3. removes the planned fresh Carlos repair package;
4. reorders the remaining work;
5. changes no gameplay, OTBM, assets, or tooling implementation.

## Remaining work requiring fresh current-main validation

1. Santiago `easy` persistence parity.
2. Rope-success hint state 22.
3. AID `50999` terminal-border crossing contract.
4. `skip tutorial` current contract.
5. Cockroach kill/chase/corpse tutorial events.
6. Static branch on Zirella's cart.
7. Extra dead trees outside the bounded whitelist.
8. Two teleport attributes with destination `0,0,0`.
9. Full clean-character E2E and reconnect testing.

## Correct continuation order

1. Correct the merged #204/#207 documentation.
2. Revalidate Santiago `easy`; implement only if still broken.
3. Revalidate rope hint state 22; implement only if still missing.
4. Resolve AID `50999` with existing OTBM audit/resolver, real-asset renders, and disposable live-world traces before coding.
5. Keep `skip tutorial`, cockroach hints, static cart branch, extra trees, and `0,0,0` teleports blocked until their current contracts are proved.
6. Run full E2E: Santiago → Zirella → cave → Carlos → Rookgaard, including reconnects and repeated interactions.

## AID 50999 evidence required before implementation

- exact permitted crossing direction;
- destination walkability/floor/PZ semantics;
- rejection before Carlos stage 7;
- log-7 crossing and idempotent log-8 behavior;
- whether current Rookgaard town ID 3 must be assigned;
- tutorial 14 timing;
- reverse-side behavior;
- no effect on nearby AID `50998`;
- live traces at Carlos logs 6, 7, and 8.

Never copy historical `Town(6)` or absent historical AID `50089`.

## Validation truthfulness

- #204 report head `12d5860530a7792c04872bc35ace693f407cfc60` passed CI 1076, AI Agent Tools 494, and Agent Task Ownership 45.
- Later #204 task-status head passed AI Agent Tools 508 and Agent Task Ownership 68; CI 1106 was cancelled and must not be called passed.
- #207 passed CI 1096/1097, AI Agent Tools 506/507, Agent Task Ownership 60/61, and CI 1098 after ready-for-review.
- Original archive PR #351 passed CI 2144 and Agent Task Ownership 1027, but became unmergeable after `main` advanced; this replacement branch is based on current `main`.

## Do not repeat

- Do not open another Carlos repair.
- Do not build replacement OTBM tooling.
- Do not use historical coordinates or town IDs without current-map proof.
- Do not treat unresolved as handled because a historical server had a script.
- Do not edit `.otbm` as part of this continuation without a separately approved map-edit task.
