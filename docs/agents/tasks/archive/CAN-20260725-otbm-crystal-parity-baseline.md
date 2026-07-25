---
task_id: CAN-20260725-otbm-crystal-parity-baseline
program_id: CAN-PROGRAM-REAL-TIBIA-PARITY
status: completed
agent: "GPT-5.6 Thinking"
owner: OTBM analysis tooling / Real Tibia parity
created: 2026-07-25T08:00:00+02:00
updated: 2026-07-25T20:50:00+02:00
last_verified_commit: "5aaeb2373c4d5e2c8f5c592b629b646085277414"
branch: docs/otbm-crystal-parity-lifecycle
base_branch: main
related_pr: "923, 935"
module_id: otbm-tooling
routes:
  - otbm
  - real-tibia-parity
owned_paths:
  exclusive: []
  shared: []
  read_only: []
reuse:
  - Unified OTBM World Index
  - Semantic OTBM Diff
  - OTBM item/mechanic audit
dependencies: []
blockers: []
---

# OTServBR ↔ CrystalServer global OTBM parity baseline

## Completion

- Final status: completed.
- Delivery PR: #923.
- Exact final delivery head: `68ec4b58bc407979e7c03eb5eb9a280b74c06e24`.
- Squash merge commit: `5aaeb2373c4d5e2c8f5c592b629b646085277414`.
- Lifecycle closure PR: #935.
- Final Agent Task Ownership: PASS, run `30169021582`.
- Final OTBM Semantic Diff: PASS, run `30169021566`.
- Final OTBM Map Tools: PASS, run `30169021595`.
- Final AI Agent Tools: PASS, run `30169021570`.
- Final full `ci:final-gate` CI: PASS, run `30169021661` after one bounded rerun of the failed Docker Quickstart path.

## Delivered baseline

- Target map: external `otservbr(4).otbm`, size `184776037`, SHA-256 `a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2`.
- Reference: `zimbadev/crystalserver@75e9c72e33ce2c3f193e4f2d2ff17ebae4bbfaac`, exact `data-global/world/world.otbm` blob `ca281acba48de2ebdf785b2d025f1e4696d3cc5f`.
- Tracked gzip SHA-256: `3bd40d14fefec41f24c4b3ae879e420be1a831ef55b95dcbec721e587a09b034`.
- Verified decompressed OTBM SHA-256: `4b2099f38df05d4be68d1ba1265754e9fd6da09742025d92644fa4b1a12eb120`.
- Crystal global: `18997668` tiles, `24504223` placements and `1197` canonical areas.
- OTServBR: `17972761` tiles, `23359571` placements and `1171` canonical areas.
- Shared area keys: `1159`; shared exact tile positions: `17871388`; unchanged tiles: `17214872`.
- Positions with at least one finding: `1884169`; exact findings: `3277274`.
- Exact report SHA-256: `e093fefdf603120933a52faf3bcd625cb94c650f7acba87acf4d95f66a56b04a`.

## Delivered implementation

- Corrected full-index `canary-otbm-semantic-diff-v1` comparison to respect canonical area-major World Index storage and exact compound area/tile ordering.
- Preserved exact counters after the bounded sample budget was full and bulk-counted validated unmatched areas without constructing discarded findings.
- Added focused adjacent-area, bounded-sample and disjoint-area regressions; the focused suite contains 34 passing tests.
- Reused the existing scanner and World Index. No second parser, renderer, pathfinder or mutation path was added.
- No OTBM, gzip transport, `.widx`, generated full report, render or external asset was committed.

## Failure history retained

- The first draft selected `data-crystal/world/world.otbm`, the separate small Crystal custom/test world. The user identified the correct global map before merge; every map-derived count was invalidated and regenerated from `data-global/world/world.otbm`.
- PR #913 accumulated delayed temporary-workflow commits and was closed without merge. Clean PR #923 rebuilt the authoritative seven-path diff from current `main`.
- One checkpoint used unsupported status `final-gate`; Agent Task Ownership rejected it and the status was corrected to `validating`.
- The first final CI attempt failed in Docker Quickstart Smoke while all focused checks and platform builds were green. The failed path was rerun once on the unchanged exact head and passed; CI run `30169021661` then completed successfully.

## Evidence boundaries

- The report proves exact static structural, item and mechanic differences in a shared broad coordinate frame.
- It does not prove Crystal Lua/XML runtime behavior, gameplay parity, walkability without compatible appearance evidence, identifier intent or that Crystal-only content should be copied.
- Any city, quest, mechanic or repair follow-up requires a separate bounded task using current Script Resolution, reachability and relevant subsystem evidence.

## Lifecycle closure

Delivery PR #923 is merged. Lifecycle closure PR #935 releases every task-owned path and records the global-world baseline as durable read-only evidence.
