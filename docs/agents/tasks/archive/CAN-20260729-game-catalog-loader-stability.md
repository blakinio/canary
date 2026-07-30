---
task_id: CAN-20260729-game-catalog-loader-stability
program_id: CAN-PROGRAM-GAME-CATALOG-COMPLETENESS
coordination_id: "OTS-20260728-game-catalog-v1"
status: completed
agent: "chatgpt"
related_pr: 1015
created: 2026-07-29T19:35:00Z
completed: 2026-07-29T21:14:39Z
risk: high
---

# CAN-20260729-game-catalog-loader-stability

## Goal

Remove the complete default-datapack export-only loader crash and prove repeatable schema `1.2.0` exports with startup loader telemetry disabled and enabled.

## Result

- The root cause was concurrent use of one Lua state: export-only definition loading ran on the process main thread while registered global events could execute Lua on the dispatcher.
- The complete export was moved into one serial dispatcher event.
- Exact-artifact validation passed 10 telemetry-disabled and 2 telemetry-enabled full-datapack exports.
- Every successful attempt produced byte-identical controlled snapshots, valid lowercase SHA-256 sidecars, zero database/network endpoint syscalls and the expected reviewed loot-threshold evidence.
- PR #1015 merged as `37942a3222d3c98bff32610e894640d584d4861a` from final head `1353cf5ebe1c34dec593422d929e2e38a374ecfe`.
- No schema bytes, datapack content, staging state, production state or activation state changed.

## Final checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-31T01:12:00+02:00
head: 1353cf5ebe1c34dec593422d929e2e38a374ecfe
branch: fix/CAN-20260729-game-catalog-loader-stability
pr: 1015
merge_sha: 37942a3222d3c98bff32610e894640d584d4861a
status: completed
context_routes:
  - agent-governance
  - cpp-runtime
  - ci-repair
proven:
  - Diagnostic run 30486191705 reproduced five failures in ten telemetry-disabled attempts while both telemetry-enabled controls passed.
  - Symbolized failures occurred in LuaJIT while the dispatcher concurrently executed GlobalEvents through LuaScriptInterface.
  - Dispatcher-thread serialization compiled and Game Catalog run 30487172289 passed ten telemetry-disabled and two telemetry-enabled attempts.
  - Final synchronized Game Catalog run 30490487339, CI run 30490487328, Agent Task Ownership run 30490487240 and Universal E2E run 30490487257 passed on head 1353cf5ebe1c34dec593422d929e2e38a374ecfe.
  - PR 1015 merged as 37942a3222d3c98bff32610e894640d584d4861a.
derived:
  - Export-only Lua definition loading must remain serialized on the dispatcher thread.
unknown: []
conflicts: []
first_failure:
  marker: none
  evidence: The implementation and exact-head merge gate completed successfully.
rejected_hypotheses:
  - Weapon proficiency loading was the proven faulting loader.
  - Startup telemetry was an acceptable correctness dependency.
  - Appearance protobuf loading or snapshot serialization caused the crash.
validation:
  - command: Game Catalog 30490487339
    result: PASS
    evidence: Exact final-head build and complete 10+2 runtime stability proof passed.
  - command: CI 30490487328
    result: PASS
    evidence: Required and repository CI passed on the final head.
  - command: squash merge PR 1015
    result: PASS
    evidence: Merged as 37942a3222d3c98bff32610e894640d584d4861a.
blockers: []
next_action: Preserve dispatcher-thread export serialization while extending the independent schema 1.3 NPC/shop producer.
```
