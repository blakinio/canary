---
task_id: CAN-20260723-oteryn-oam039-preflight
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-039
status: archived
created: 2026-07-23
updated: 2026-07-23
related_pr: "779"
modules_touched:
  - instances
---

# OAM-039 Instances governance — archived

Final disposition: `instances → ADAPT`.

Canary preflight PR #771 selected canonical `instances` as an `ADAPT candidate` and squash-merged as `5c0613fd853e85421a89f661e9b3774c4dd730ff`.

Otheryn target delivery PR #81 changed exactly 19 bounded task/evidence, canonical `src/game/instance/**`, CMake and focused unit-test paths. Initial exact head `58c4d2cf2cb5f26d67974b78e9d8e16885eae702` exposed one owned Linux-debug lifecycle defect in `InstanceManagerTest.CleanupRunsExactlyOnceAndDirtyRegionIsQuarantined`: a quarantined `Closing` instance did not retry finalization after creature ownership was drained. The bounded repair preserved exactly-once cleanup while allowing a later `close()` to retry finalization and release the region. Final head `e216c3bb732bc6dc97374833bbfcb13a4f4ebc50` passed autofix `30002236999`, CI `30002237279`, Required `30002237057`, Linux release/debug including full `Run Tests`, both Windows build paths, macOS and Docker. Comments, reviews and review threads were empty, target `main` had no task-start drift, and PR #81 squash-merged as `a2a52e239d8e8a770ff7376fcbb9b5bfdcc8cc13`.

Canary governance PR #779 final head `f07951fbb7475779347e2721931cb8f0adf1a612` changed exactly the OAM-039 revalidation report and active task checkpoint. Final exact-head Agent Task Ownership `30003789254` and full `ci:final-gate` CI `30003789351` succeeded, including Linux release/debug, both Windows paths, macOS and Docker. Comments, reviews and review threads were empty. Concurrent Canary drift was limited to unrelated documentation/task paths with no OAM-039 overlap, and PR #779 squash-merged as `7f5fcfb77c35f83f0841ee1d57a70878b5e544d0`.

A separate one-file durable program reconciliation and separate Otheryn target-task archive remain required before OAM-040 may start.
