# Engine Scheduler evidence decisions

## Selected decision

Record one bounded current-Canary source claim covering event staging, grouped execution, delayed/cyclic scheduling, expiration/cancellation and ThreadPool integration.

## Evidence and constraints

The selected registry and six source blobs are exact. No runtime stress, timing trace, shutdown experiment or feature-specific call-site package is selected.

## Rejected alternatives

- Infer deterministic ordering or fairness from container types.
- Infer race freedom or shutdown correctness from synchronization primitives.
- Infer wall-clock accuracy or cyclic stability from due-time arithmetic.
- Create a broad runtime/E2E request without isolating one testable property.
