# Item Decay decisions

## Decision: accept the bounded source-path finding

`RT-ITEM-DECAY-0001` is accepted at `runtime-path-proven` only for the selected current-Canary duration-bucket and transform/removal source path. Acceptance does not promote scheduler execution, timing, restart recovery, persistence, item metadata, gameplay, client behavior or Real Tibia parity.

## Decision: do not create an owner request

No owner request is created in this wave. The unresolved dimensions remain broad and no single non-duplicative owner contract has been narrowed sufficiently.

## Decision: publish through the serialized coordinator lane

The accepted record is included in deterministic module/global indexes at `as_of=2026-07-26`.
