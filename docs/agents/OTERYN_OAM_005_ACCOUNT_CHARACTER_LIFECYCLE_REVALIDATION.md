# OAM-005 — Account and Character Lifecycle Revalidation

Status: **ready**

## Pinned baselines

- legacy/governance task-start: `blakinio/canary@c2ffe09dc8753734be00c3433fab6f2ebe25d2e8`
- governance integration base after CI #415: `blakinio/canary@0f25e7fd4d41e90f17fc95d13dba84b7e81d1681`
- target task-start: `blakinio/Otheryn@67212530b03c10175da2c0d9eabcee8991a05924`
- final target: `blakinio/Otheryn@a6d42f6cec024f81a7541084425ec1d43d66d2b8`
- upstream evidence: `opentibiabr/canary@e0ac98e399d0f7e483f3668f57b78fcc45b6e53f`

## Final dispositions

| Module | Disposition | Result |
|---|---|---|
| `account-lifecycle` | `REUSE` | checked account implementation/repository blobs are identical across legacy, target task-start and upstream; no bounded account repository adaptation was justified |
| `account-authentication` | `ADAPT` | bounded secure single-use login-session primitive delivered by Otheryn PR #19; live wire integration remains OAM-006 work |
| `character-lifecycle` | `ADAPT` | existing OAM-004D player save boundary remains authoritative; authenticated account handoff must preserve character ownership/deletion checks and is deferred to OAM-006 protocol integration |

## Account lifecycle evidence

The OAM-005 registry boundary is `src/account/**`. The following exact blob comparisons are identical across all three pinned task-start/evidence revisions:

- `src/account/account.cpp` → `c48a2884570b98c47e8f39253ff2bc634f6c2712`
- `src/account/account_repository.cpp` → `a3237b8e1a43fef3e1207443176a3423fb421563`
- `src/account/account_repository_db.cpp` → `4b4089848c35a7dde7bd04b474d643c47ca7034e`

No account schema or account-repository target adaptation is justified by this evidence. Economy/coin ownership remains outside this module.

## Account authentication target delivery

Legacy Canary contains `LoginSessionManager` while the pinned target task-start and upstream do not.

Legacy PR #77 (`3c5268fe86fd9785e3feea192d70c8bd3d51ef87`) added the primitive in isolation with these properties:

- 256-bit mbedTLS CTR-DRBG generated tokens;
- raw token returned once; SHA-256 hash retained in memory;
- single-use redemption;
- account id, allowed character names and protocol-profile binding;
- TTL and bounded active-token count;
- constant-time hash comparison;
- focused tests for replay, expiry, invalid bindings, eviction, uniqueness and concurrent redemption.

Otheryn PR #19 ported only this bounded primitive plus CMake registration, focused tests and a target boundary document. It deliberately did not modify `ProtocolLogin`, `ProtocolGame`, `IOLoginData` or packet layouts.

Final PR #19 gate on exact head `2a2e1e5e22df697435e705d8a19d69dcbc46bbfd`:

- ready-triggered CI #76: PASS;
- Required #75: PASS;
- autofix.ci #68: PASS;
- Linux release: PASS;
- Linux debug compile/runtime/database/tests: PASS;
- macOS build/runtime smoke: PASS;
- Windows CMake build/runtime smoke: PASS;
- comments: none;
- submitted reviews: none;
- unresolved review threads: none;
- mergeable: true.

PR #19 was squash-merged with exact-head guard as `a6d42f6cec024f81a7541084425ec1d43d66d2b8`. `Otheryn:main` was verified identical to that commit immediately after merge. Otheryn issue #17 was closed as completed.

Legacy PR #82 (`9cafe7e945391a6f170f5b96bf68713d91d758be`) and compatibility follow-up PR #80 (`d2e02a3d533bfdfdedc3a81a8f4e4801bc828f22`) remain integration evidence for OAM-006; they are not copied wholesale in OAM-005.

## Character lifecycle evidence

`character-lifecycle` overlaps `player-persistence` by design. The target `IOLoginData` save path is deliberately different from upstream/legacy because OAM-004D separated player SQL transaction work from later wheel KV staging.

OAM-005 therefore does not restore a legacy whole-file version of `IOLoginData` and does not treat file equality as the correctness criterion. The existing OAM-004D save boundary remains authoritative.

Legacy PR #82 demonstrates a future optional pre-authenticated-account-id seam that still executes character ownership and deletion-state checks. Because actual token redemption and session-key transport are coupled to `ProtocolLogin`/`ProtocolGame`, final wire integration is reserved for OAM-006.

## Explicit boundaries and gaps

- No production credential or database access was used.
- No packet-layout/client rollout change is included in OAM-005.
- Password authentication and DB-backed `account_sessions` fallback remain unchanged by target PR #19.
- The secure token primitive is not effective on the live wire until OAM-006 integration is completed and proven.
- Old-protocol compatibility and modern protocol/session-key behavior require exact OAM-006 server/client evidence.
- No claim is made that a token primitive alone completes authentication hardening.
- OAM-004D player SQL / wheel KV persistence semantics remain unchanged.

## OAM-005 governance completion sequence

Target delivery is complete at `blakinio/Otheryn@a6d42f6cec024f81a7541084425ec1d43d66d2b8`.

Remaining sequence:

1. Update the OAM-005 active task and authoritative program record with final target delivery and dispositions.
2. Keep OAM-006 inactive.
3. Verify Canary PR #432 exact changed files and ownership.
4. Verify exact-head ownership/CI, comments, submitted reviews and unresolved review threads.
5. Mark PR #432 ready.
6. Use the latest ready-triggered exact-head final gate.
7. Squash-merge PR #432 with exact-head guard.
8. Complete a separate lifecycle-only PR moving OAM-005 `active → archive` and marking OAM-005 completed in the program queue.
9. Only after that lifecycle merge may OAM-006 become the next eligible bounded package.
