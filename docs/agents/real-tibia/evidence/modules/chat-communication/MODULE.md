# Chat Communication evidence dossier — current Canary source path

## Status and scope

- Module: `chat-communication`.
- Campaign: RTEC-005 wave 2.
- Canary baseline: `18411a50e81d857fba8cf42bfa9b1f4c67a3904a`.
- Registry blob: `d736ff891a48315aa4bd7c34a5a553ca1d31ffd3`.
- Source blobs: `chat.cpp@152a40857f4b184e968eb51601a75634d8d37946`, `chat.hpp@09f8a727fef239b95b1bb5da20356801769732f0`.
- Verification date: `2026-07-29`.
- Dossier state: `candidate` (bounded source claim only).

This candidate covers only the exact current Canary channel registry, callback, membership and private-channel lifecycle source path. It does not claim configured data correctness, protocol/client delivery, privacy, moderation, party/guild authorization or Real Tibia parity.

## Bounded finding

`Chat::load()` reads configured normal channels and optional Lua callback identifiers. Runtime channel maps represent normal, guild, party and private channels. Membership methods invoke join/leave hooks, speaking is callback- and membership-gated, and private channels expose owner, invitation, exclusion and close operations.

## Evidence record

| ID | Claim | State | Proof | Publication |
|---|---|---|---|---|
| `RT-CHAT-COMMUNICATION-0001` | current Canary channel registry, callback, membership and private lifecycle path | `PROVEN` | `runtime-path-proven` | `review-needed` |

## Review boundary

The candidate proves a source-level path only. Configuration content, packet encoding, client behavior, delivery, privacy, moderation, authorization and physical gameplay remain nonclaims.
