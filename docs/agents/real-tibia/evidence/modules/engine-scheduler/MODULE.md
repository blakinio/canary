# Engine Scheduler evidence dossier — current Canary source path

## Status and scope

- Module: `engine-scheduler`.
- Campaign: RTEC-005 wave 2.
- Canary baseline: `18411a50e81d857fba8cf42bfa9b1f4c67a3904a`.
- Registry blob: `bcf728df9999d2bda9019918066200a69f1daad5`.
- Source blobs: `dispatcher.cpp@8a537385a76095104c3ab71e19a770f6ad282c38`, `dispatcher.hpp@22ffa032c2bb3fac4ad4189569a7dc1d43c0d699`, `task.cpp@7747d584370a25f2569da987225b31d556b69472`, `task.hpp@9435a7704a0da81ae12ffef5d18f9dc29bdbf882`, `thread_pool.cpp@c753278ae0e1b4f439e1ad72bbca599d575bbda6`, `thread_pool.hpp@a5e3c54fadecb53367b9d5580de2b1a053f94572`.
- Verification date: `2026-07-29`.
- Dossier state: `candidate` (bounded source claim only).

This candidate covers only the exact current Canary dispatcher/task/thread-pool source path. It does not claim ordering, fairness, race freedom, timing accuracy, shutdown correctness, feature-specific timers, persistence scheduling or Real Tibia parity.

## Bounded finding

The dispatcher stages per-thread events, merges them into serial, budgeted and parallel execution groups, executes due scheduled tasks, requeues successful cyclic tasks, removes non-requeued references and supports event-ID cancellation. `Task` contains expiration and cancellation checks, and `ThreadPool` supplies the execution substrate and shutdown path.

## Evidence record

| ID | Claim | State | Proof | Publication |
|---|---|---|---|---|
| `RT-ENGINE-SCHEDULER-0001` | current Canary dispatch, schedule, cancel and thread-pool path | `PROVEN` | `runtime-path-proven` | `review-needed` |

## Review boundary

The candidate proves source structure only. Concurrency properties, wall-clock behavior, lifecycle correctness and feature-visible outcomes remain nonclaims.
