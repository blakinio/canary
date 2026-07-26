# Item Decay evidence dossier — current Canary source path

## Status and scope

- Module: `item-decay`.
- Campaign: RTEC-005 wave 1.
- Canary baseline: `80d5daebd1804edc6208e2312733b5b484490587`.
- Registry blob: `03901f5a28e0dbc4a8db55fdf892410b730558b7`.
- Source blobs: `decay.hpp@0d540e10dc73b65f2ce1aa00bfb9dd72994dcc5f`, `decay.cpp@458cda4ac92f21289ca1072447e79c71de645ae8`.
- Verification date: `2026-07-26`.
- Dossier state: `review-needed`.

This candidate covers only the exact current Canary source path from duration registration to scheduled due-item handling and transform/removal handoff. It does not claim item-specific metadata correctness or Real Tibia parity.

## Bounded finding

`Decay::startDecay()` records a duration timestamp, inserts the item into an ordered timestamp bucket and schedules `Decay::checkDecay()`. Due items are passed to `Decay::internalDecayItem()`, which follows a configured `decayTo` transform branch or the bounded removal branch.

## Evidence record

| ID | Claim | State | Proof | Publication |
|---|---|---|---|---|
| `RT-ITEM-DECAY-0001` | current Canary duration-bucket and transform/removal path | `PROVEN` | `runtime-path-proven` | `review-needed` |

## Review boundary

The record proves a source-level runtime path, not scheduler execution, wall-clock accuracy, restart recovery, persistence, item metadata, gameplay or client behavior. The candidate is intentionally absent from published module/global indexes until coordinator adjudication.
