# Equipment Upgrade / Exaltation Forge handoff — 2026-07-14

## Purpose

This file is the durable handoff for the GPT-5.6 Thinking work cycle that audited and remediated Canary's Equipment Upgrade / Exaltation Forge implementation.

The work cycle is archived, but the parity program is **not complete**. Completed behavior and remaining evidence-backed gaps are separated below so a later agent does not repeat merged work or claim full retail parity prematurely.

## Repository boundary

- Writable repository used: `blakinio/canary` only.
- `opentibiabr/canary` and other upstream repositories remained read-only.
- No production deployment, map, OTBM, binary asset, credential or database dump was changed.
- Maintained OTClient changes were not attempted because the coordinated bonus/result contract remains a separate authorized scope.

## Merged work

| Findings/scope | PR | Merge commit | Result |
|---|---:|---|---|
| Normal Transfer policy baseline | #89 | `209289d38e64aafe7ce3e036867bb632cd0363b8` | Preserve donor-tier/classification behavior and costs. |
| Forge history item identity | #110 | `84f5c09263f459d726fbc7b9f79557b2cbb0801d` | Preserve ID-based history identity. |
| Dust killer/party/cap remediation | #177 | `f1d217c43e8e302978f533212e6aa9d1ce2b77c8` | Direct/summon killer resolution, one shared party roll and actual capped credit. |
| F-003–F-005 server authority | #250 | `94f8a3b63271b3708e33496e937620a6cd4b9717` | Normal Fusion same-ID authority; class-4 Convergence Fusion/Transfer; rejection before mutation. |
| F-001–F-002 live defaults | #259 | `444aa8ae13edc01c6e77b03139a43d386b437308` | Dust maximum `325`; Fiendish maximum `4`; synchronized C++/Lua/config tests. |
| F-011–F-012 effects | #267 | `7771bbec22d970d9779bff740e3f7f2e0df42f19` | Avatar mutual exclusion and truthful Momentum feedback. |
| F-020–F-021 transaction safety | #257 | `e16c9f769b1bcdd05e1719e861f0a52cc2594560` | Transactional Fusion, Transfer and Sliver-to-Core with rollback. |
| F-006 Premium Dust | #262 | `ded1830b143388d65c895ad30918faf128df66ed` | Exact `Player::isPremium()` Lua delegation and non-Premium rejection. |
| F-022–F-024 history correctness | #283 | `82348f9faca788a8cbb5c13feb75b4e06d8da9dc` | Actual Dust/configured amounts and preserved conversion action types. |

## Invariants that later work must preserve

1. Every client-supplied Fusion/Transfer choice is validated again in C++ before resource or inventory mutation.
2. Normal Fusion uses two distinct instances of the same item ID and requested tier.
3. Convergence Fusion uses different class-4 item IDs with the same tier and normalized equipment slot.
4. Convergence Transfer requires class 4.
5. Active imbuements remain disallowed.
6. Valid Fusion, Transfer and Sliver-to-Core mutations are all-or-nothing.
7. History, metrics and result packets occur only after a successful transaction.
8. Dust reward eligibility delegates to the exact C++ Premium predicate.
9. One creature death produces one Dust roll; shared-exp recipients receive the same rolled amount, capped by actual remaining capacity.
10. Transcendence is blocked by either Forge Avatar or spell Avatar.
11. Momentum feedback is emitted only after a real eligible cooldown reduction.
12. Server-owner configuration overrides remain supported.

## Validation evidence

The merged feature heads passed repository-required checks before merge. Important final runs include:

- #250 CI `29259842029` — success;
- #259 CI `29266052589` — success;
- #267 CI `29262396073` — success;
- #257 CI `29278815631` — success;
- #262 CI `29278644231` — success;
- #283 ready-state CI `29314898366` — success.

Coverage included Lua tests, Fast Checks, Linux debug compilation/runtime/schema/full tests, Linux release, macOS, Windows CMake/MSBuild, Docker, Agent Task Ownership and relevant validation workflows.

This evidence proves compilation, deterministic regressions and generic runtime smoke. It does **not** prove complete physical-client gameplay parity.

## Remaining findings and evidence gaps

### Runtime/gameplay proof still required

- F-007: focused proof that logout/combat-block behavior for party Dust matches the selected live rules.
- F-008: focused gameplay proof of actual credited amount at the Dust cap.
- F-013: focused proof that a creature death performs exactly one shared Dust roll across direct, summon and party cases.

The implementation foundation comes from PR #177 and PR #262. Do not rewrite it without a reproduced defect.

### Blocked by authoritative rule evidence

- F-009: exact Fiendish difficulty-to-Sliver reward mapping.
- F-010: exact percentage precision and rounding behavior for Ruse.

Do not implement either from memory, an unversioned wiki summary or inference from current code. Pin the selected live version and evidence first.

### Coordinated server/client bonus work

F-014 through F-019 remain the largest unfinished package:

- missing Fusion bonus that refills Dust to the player's current maximum;
- incorrect `+2 tier` cap comparison;
- bonus selection is not sufficiently tier-aware;
- remaining Fusion history/result-state inconsistencies;
- maintained OTClient currently presents only a subset of server bonus results;
- decreased-tier/result payload and client presentation require a versioned Canary ↔ OTClient contract.

Before implementation:

1. re-read current `main`, open PRs and active ownership;
2. inspect the current server result enum, packet field order, history semantics and maintained client decoder/UI;
3. update `docs/agents/CROSS_REPO_CONTRACTS.md` with exact values, compatibility behavior and rollout order;
4. obtain explicit authorization before writing to another repository;
5. use separate bounded server and client tasks or an explicitly atomic cross-repository plan;
6. add deterministic server tests plus maintained-client parsing/presentation tests;
7. do not claim completion until a physical-client scenario passes.

### E2E dependency

Reuse the universal E2E platform program and PR #245 when it is merged and stable. Do not copy its orchestration into a Forge-specific workflow. Add only a Forge scenario and assertions under the platform's extension contract.

## Exact next task

Create one new bounded task from then-current `main` for the coordinated F-014–F-019 contract audit. The first task should be evidence/contract-first and must not change protocol bytes until both server and maintained-client behavior are mapped.

Suggested identity:

```text
task: CAN-YYYYMMDD-forge-bonus-result-contract
branch: docs/forge-bonus-result-contract
scope: F-014 through F-019 evidence, enum/payload/client mapping and rollout plan
```

After that contract is reviewed, split implementation into independently testable server and client packages.

## Do not repeat

- Do not reopen or continue helper PRs #252, #253, #254, #258, #260, #266, #268, #269, #270, #271, #280, #281 or #284.
- Do not reopen completed feature PRs #250, #257, #259, #262, #267 or #283.
- Do not bypass `ForgeFusionPolicy`, `ForgeTransferPolicy`, `ForgeTransaction` or `ForgeEffectPolicy`.
- Do not treat client-side filtering as server authority.
- Do not merge bonus, protocol, client UI, reward mapping and rounding work into one unbounded PR.
- Do not mark the module fully retail-compatible from aggregate CI alone.

## Archive index

Completed task records are stored under:

- `docs/agents/tasks/archive/CAN-20260713-forge-server-authority.md`;
- `docs/agents/tasks/archive/CAN-20260713-forge-live-defaults.md`;
- `docs/agents/tasks/archive/CAN-20260713-forge-effect-correctness.md`;
- `docs/agents/tasks/archive/CAN-20260713-forge-transaction-safety.md`;
- `docs/agents/tasks/archive/CAN-20260713-forge-premium-dust.md`;
- `docs/agents/tasks/archive/CAN-20260713-forge-history-correctness.md`.

The long-lived source of truth remains `docs/agents/programs/EQUIPMENT_UPGRADE_PARITY_PROGRAM.md` plus `docs/ai-agent/OTS_AI_EQUIPMENT_UPGRADE_VALIDATION.md`.
