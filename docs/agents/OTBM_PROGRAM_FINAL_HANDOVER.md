# OTBM Programme Final Handover

> Repository: `blakinio/canary`  
> Programme: `OTS-OTBM-VALIDATION`  
> Final handover refreshed: 2026-07-18  
> Verified task-start `main`: `6df7f906ed6f8fef0aa326439a5494bd1e3d523c`  
> Status: functionally complete; one administrative lifecycle PR may still be pending

## Start here

A continuation agent must begin from current live GitHub state, not chat history.

Read first:

1. `AGENTS.md`;
2. `docs/agents/REPOSITORY_MAP.md`;
3. `docs/agents/CONTEXT_ROUTING.md`;
4. `docs/ai-agent/OTS_OTBM_TOOLING_ROADMAP.md`;
5. `docs/agents/OTBM_PHASE8_FINAL_HANDOFF.md`;
6. `docs/ai-agent/OTBM_REPAIR_MATERIALIZATION_PIPELINE.md`;
7. `docs/ai-agent/OTBM_HD_PIPELINE.md`;
8. `docs/ai-agent/OTBM_SCRIPT_RESOLUTION.md`;
9. relevant `MODULE_CATALOG.md` entries only when a new task needs them.

Do not reconstruct programme state from old conversations. Verify current `main`, open PRs, active task records, ownership and required CI before any new work.

## Final programme state

The bounded OTBM tooling programme is functionally complete.

Numbered phases:

| Phase | Scope | Final state | Delivery |
|---:|---|---|---|
| 1 | Unified OTBM World Index | merged and archived | #219 / #223 |
| 2 | Quest Map Validator | merged and archived | #225 / #236 |
| 3 | Teleports, floor transitions and reachability | merged and archived | #274 / #277 |
| 4 | Spawns, bosses and NPCs | merged and archived | #286 / #290 |
| 5 | Storage dependency graph | merged and archived | #299 / #309 |
| 6 | Semantic OTBM diff and factual visual evidence | merged and archived | #311 / #315 |
| 7 | Geometry and consistency audit | merged and archived | #322 / #323 |
| 8 | Safe bounded existing-attribute OTBM patch writer | merged and archived | #325 / #333 |

Later bounded extensions reused that architecture rather than creating a new numbered phase:

- #406 — read-only real-map repair preflight;
- #419 — static Map Quality Gate;
- #422 — repair sandbox verifier;
- #424 — read-only donor/region merge planner;
- #426 — approved zero-translation complete `OTBM_TILE_AREA` materialization;
- #456 — canonical repair/materialization finalization pipeline;
- #467 — complete raw tile replacement;
- #482 — complete raw tile insertion into an existing parent `TILE_AREA`;
- #488 — complete raw tile deletion while preserving the parent `TILE_AREA`;
- #498 — complete `OTBM_TILE ↔ OTBM_HOUSETILE` donor-subtree conversion;
- #506 — integration of replacement, insertion, deletion and tile-type conversion into the canonical pipeline;
- #508 — lifecycle cleanup for #506.

The authoritative roadmap was reconciled by PR #534 and its task archived by #535.

- #534 merge: `abbeb51433d33af7398a82f0cd2ab776d01e710f`;
- #535 merge: `3215a57d85bc83f982f489a764a9275e51447621`.

## Canonical capabilities to reuse

A future OTBM task must reuse the existing stack rather than reimplementing it:

- item/mechanic audit for item IDs, AID, UID, teleport destinations, house doors and exact `x,y,z` positions;
- script resolution for exact AID/UID/itemId/position correlation against active Lua/XML handlers;
- Unified World Index for deterministic indexed map evidence;
- Quest Map Validator for bounded source/map correlation;
- reachability and transition validation for teleports and reviewed floor changes;
- spawn/boss/NPC evidence and validation;
- storage dependency graph;
- Semantic OTBM Diff;
- geometry/consistency audit;
- factual renderer using real OTBM plus compatible client assets;
- bounded Phase 8 existing-attribute patcher;
- bounded raw-tile materializers and canonical repair/materialization finalization pipeline.

Do not create a second parser, scanner, World Index, script resolver, pathfinder, renderer, semantic diff engine or E2E runner.

## Canonical repair/materialization boundary

The canonical finalization pipeline supports exactly one reviewed mutation mode per run:

- `attribute`;
- `tile-area`;
- `tile-replacement`;
- `tile-insertion`;
- `tile-deletion`;
- `tile-type-conversion`.

Every approved real-map mutation must retain the established safety model:

- never write the source map in place;
- pin exact source identity and expected previous state;
- operate only in explicit bounded scope;
- create a new output artifact;
- fully reparse and validate the candidate;
- rebuild canonical World Index evidence when required;
- require exact Semantic OTBM Diff evidence;
- prove confinement/equality outside the intended mutation boundary;
- retain rollback evidence;
- use the factual renderer with real map/client assets when visual evidence is needed.

Static or structural success is not proof of gameplay correctness. Use physical-client E2E only when runtime behavior itself must be proven.

## Physical teleport E2E completion

PR #525 completed the remaining deterministic physical teleport proof using the existing Universal Agent E2E platform.

Final evidence recorded by the merged PR:

- final feature head: `f3fc1346a82da7b086a416f30c4e4eb5b135a365`;
- squash merge: `6df7f906ed6f8fef0aa326439a5494bd1e3d523c`;
- Universal Agent E2E run: `29656610078`;
- physical evidence artifact: `8433334056`;
- artifact digest: `sha256:2726f1180b687a40757574315c42b8125a01669ad0c8b5418b1ffda459368f0a`;
- initial position: `32369,32241,7`;
- runtime-proven destination: `32255,32204,8`;
- floor delta: `1`;
- two server logins and two packet records confirmed;
- persistence, relog, second safe logout and `e2e=success` confirmed;
- Agent Task Ownership, main CI required aggregator, exact Canary linux-release build, controlled OTClient build, physical client scenario and Required physical E2E all passed on the final reviewed head.

This closes the functional teleport-proof gap. It does not authorize arbitrary gameplay/map changes outside a separately reviewed bounded task.

## Remaining administrative state at handover creation

PR #558 is the automated lifecycle/archive cleanup for merged PR #525.

At handover task start:

- PR #558 state: open, non-draft, mergeable;
- head: `3a415ba0878b79ed638ef23926337b324004854a`;
- auto-merge: enabled by the handover agent;
- existing dispatched `Agent Task Ownership` and `CI` runs concluded `action_required`;
- a direct squash merge attempt was rejected by repository rules because required status check `Required` was still expected;
- `ci:final-gate` was added, but no new usable PR workflow run was observed immediately afterward.

This is an administrative lifecycle blocker only. Do not describe #525 or the OTBM programme as functionally incomplete because #558 remains open.

Exact next action for any continuation agent if #558 is still open:

1. re-read live PR #558 and exact head;
2. verify whether the required workflow approval/check state has changed;
3. allow the normal `Required` check to complete;
4. let auto-merge merge #558, or squash-merge only after the normal autonomous merge gate is satisfied;
5. never bypass branch protection or mark a failed/missing check successful.

## Explicit non-goals that are not unfinished work

The following remain outside the completed bounded programme and must not be reported as missing acceptance criteria:

- generic OTBM node serialization;
- a generic or full-map serializer/writer;
- direct in-place source-map mutation;
- direct production-map deployment/execution;
- non-zero coordinate translation in the canonical finalizer;
- automatic teleport-destination rewriting caused by translation;
- partial `TILE_AREA` import;
- arbitrary independent item insertion/deletion;
- arbitrary item-stack reordering/editing;
- guessing dynamic Lua expressions;
- promoting `unresolved` evidence to handled without direct proof.

A future task may propose one of these only as a new separately reviewed architecture scope. It is not continuation of unfinished Phase 8 work.

## Safety invariants

Always preserve these rules:

- repository writes only to `blakinio/canary` unless the user separately authorizes another repository;
- treat `opentibiabr/*` repositories as read-only upstream for this programme;
- never commit `.otbm`, `.widx`, `items.otb`, client asset packages, generated large reports or renders;
- never use AI image generation as map evidence;
- dynamic Lua is not executed or guessed;
- `unresolved` is never treated as handled without evidence;
- coordinates, item IDs, AID, UID, storage values, teleport destinations and transition offsets are never invented;
- do not manually edit `docs/agents/ACTIVE_WORK.md`;
- do not reopen completed historical OTBM PRs or continue their old branches;
- do not weaken CI, ownership, branch protection or validation gates to obtain a merge.

## Shared-document concurrency note

At handover creation, unrelated PR #514 remained open and had previously claimed shared `docs/agents/MODULE_CATALOG.md` and `docs/agents/CHANGELOG.md` changes.

Therefore this final handover intentionally does not edit either shared file. A future documentation-cleanup task must first verify live #514 state and current ownership before touching them.

## What a future OTBM agent should do

There is no automatic next implementation phase.

For any newly requested real-map repair or analysis:

1. verify current `main`, active tasks, open PRs and ownership;
2. create a fresh bounded task/branch/PR;
3. start with item/mechanic audit and script resolution;
4. prove the exact target and expected old state;
5. reuse World Index, Semantic Diff, reachability, geometry, Map Quality and the canonical bounded materialization pipeline as appropriate;
6. preserve unresolved/conflicting evidence explicitly;
7. use a new output copy, full validation and rollback evidence for any approved map mutation;
8. add physical-client E2E only when runtime proof is actually required.

Do not start work merely to extend the tooling programme. The programme is complete in its ratified bounded scope.

## Final handover summary

```text
OTBM core analysis tooling: COMPLETE
OTBM phases 1-8: MERGED + ARCHIVED
Post-Phase-8 bounded materializers/finalizer through #506: MERGED
Roadmap reconciliation #534: MERGED
Roadmap lifecycle #535: MERGED
Physical teleport E2E #525: MERGED + RUNTIME-PROVEN
Physical teleport lifecycle #558: ADMINISTRATIVE ONLY; verify live state
Generic/full-map serializer: OUT OF SCOPE
Non-zero translation finalizer: OUT OF SCOPE
Arbitrary item-stack editing: OUT OF SCOPE
Next implementation phase: NONE AUTOMATICALLY AUTHORIZED
```

A new agent should be able to continue solely from this file, the authoritative roadmap, current GitHub state and the standard agent startup documents, without access to the prior chat.
