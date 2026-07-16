# OAM-005 — Account and Character Lifecycle Revalidation

Status: **active**

## Pinned baselines

- legacy/governance task-start: `blakinio/canary@c2ffe09dc8753734be00c3433fab6f2ebe25d2e8`
- governance integration base after CI #415: `blakinio/canary@0f25e7fd4d41e90f17fc95d13dba84b7e81d1681`
- target task-start: `blakinio/Otheryn@67212530b03c10175da2c0d9eabcee8991a05924`
- upstream evidence: `opentibiabr/canary@e0ac98e399d0f7e483f3668f57b78fcc45b6e53f`

## Canonical modules

| Module | Working disposition | Current evidence |
|---|---|---|
| `account-lifecycle` | `REUSE` | checked account implementation/repository blobs are identical across legacy, target and upstream |
| `account-authentication` | `ADAPT` | legacy secure single-use login-token primitive is absent from target/upstream; bounded target PR #19 ports the primitive and its tests |
| `character-lifecycle` | `ADAPT` | target character save lifecycle already contains OAM-004D adaptation; future pre-authenticated-account handoff must preserve ownership/deletion checks and is integrated with protocol work only after OAM-005 |

## Account lifecycle evidence

The OAM-005 registry boundary is `src/account/**`. The following exact blob comparisons are identical across all three pinned revisions:

- `src/account/account.cpp` → `c48a2884570b98c47e8f39253ff2bc634f6c2712`
- `src/account/account_repository.cpp` → `a3237b8e1a43fef3e1207443176a3423fb421563`
- `src/account/account_repository_db.cpp` → `4b4089848c35a7dde7bd04b474d643c47ca7034e`

No account schema or account-repository target adaptation is justified by the evidence currently found. Economy/coin ownership remains outside this module.

## Account authentication evidence

Legacy Canary contains `LoginSessionManager` while the pinned target and upstream do not.

Legacy PR #77 (`3c5268fe86fd9785e3feea192d70c8bd3d51ef87`) added the primitive in isolation with these properties:

- 256-bit mbedTLS CTR-DRBG generated tokens;
- raw token returned once; SHA-256 hash retained in memory;
- single-use redemption;
- account id, allowed character names and protocol-profile binding;
- TTL and bounded active-token count;
- constant-time hash comparison;
- focused tests for replay, expiry, invalid bindings, eviction, uniqueness and concurrent redemption.

Otheryn PR #19 ports only this primitive plus CMake registration, focused tests and a target boundary document. It deliberately does not modify `ProtocolLogin`, `ProtocolGame`, `IOLoginData` or packet layouts.

Legacy PR #82 (`9cafe7e945391a6f170f5b96bf68713d91d758be`) is retained as later integration evidence, not copied wholesale in OAM-005.

## Character lifecycle evidence

`character-lifecycle` overlaps `player-persistence` by design. The target `IOLoginData` save path is already deliberately different from upstream/legacy because OAM-004D separated player SQL transaction work from later wheel KV staging.

OAM-005 therefore does not restore a legacy whole-file version of `IOLoginData` and does not treat file equality as the correctness criterion. The existing OAM-004D save boundary remains authoritative.

Legacy PR #82 demonstrates a future optional pre-authenticated-account-id seam that still executes character ownership and deletion-state checks. Because actual token redemption and session-key transport are coupled to `ProtocolLogin`/`ProtocolGame`, final wire integration is reserved for OAM-006.

## Explicit boundaries and gaps

- No production credential or database access was used.
- No packet-layout/client rollout change is included in OAM-005.
- Password authentication and DB-backed `account_sessions` fallback remain unchanged by target PR #19.
- The secure token primitive is not effective on the live wire until OAM-006 integration is completed and proven.
- Old-protocol compatibility and modern protocol/session-key behavior require exact OAM-006 server/client evidence.
- Visual Studio project-file synchronization is not part of the current CMake-driven target slice and remains a build-tooling gap to verify against target CI/support policy.

## Current target work

- Otheryn issue #15 — OAM-005 parent tracking.
- Otheryn issue #17 — bounded primitive implementation tracking.
- Otheryn PR #19 — `feat(auth): add bounded login session primitive`.
- PR #19 task-start: `67212530b03c10175da2c0d9eabcee8991a05924`.
- PR #19 exact implementation head before ready gate: `2a2e1e5e22df697435e705d8a19d69dcbc46bbfd`.

## Required completion sequence

1. Complete PR #19 ready-triggered exact-head CI/autofix/review gate.
2. Merge PR #19 only with exact-head guard.
3. Pin final Otheryn `main`.
4. Finalize the three module dispositions in this report.
5. Update OAM program state while keeping OAM-006 inactive.
6. Pass Canary governance exact-head ownership/CI/review gate.
7. Merge Canary OAM-005 feature governance.
8. Complete a separate lifecycle-only archive PR.
9. Only after lifecycle merge may OAM-006 become the next eligible bounded package.
