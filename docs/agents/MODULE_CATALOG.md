# Canary Module and System Catalogue

Last reviewed: 2026-07-12

This catalogue makes reusable work visible across agents. Verify current source, tests, and PR state before use.

## Maintenance contract

Update this file in the same PR that adds a reusable module/service/manager/parser/library/tool/workflow abstraction/test utility; changes a public API/config/schema/format/protocol; deprecates or replaces a module; or introduces active work another agent could duplicate.

## Runtime and architecture

| Module/system | Status | Purpose/public surface | Source/tests/docs | Reuse notes |
|---|---|---|---|---|
| InstanceManager | merged (#107) | Strong instance IDs, lifecycle, bounded slots, idempotent close, timeout sweep | `src/game/instance/instance_id.hpp`, `instance_manager.{hpp,cpp}`, focused tests, `docs/architecture/instance-manager.md` | Foundation for future map/player/scheduler/Lua integration; do not create a second registry. |
| InstanceRegionPool | merged (#121) | Thread-safe reservation of pre-carved non-overlapping 3D regions | `src/game/instance/instance_region_pool.{hpp,cpp}`, tests, architecture doc | Reuse for physical instance regions; it does not copy maps or own tiles. |
| DI service access | merged (#117, #119) | DI resolution for `SharedPtrManager` and `Scripts` | relevant sources/audit/tests | Extend existing DI; do not add raw Meyers singletons. |
| Gameplay Analytics | merged; operator enablement remains manual | Runtime telemetry, aggregation, maintenance, reporting, hunt-area tooling | `tools/analytics/**`, gameplay analytics scripts/workflows/docs | Reuse live `GameplayAnalytics`; do not reload its core via `dofile`. |
| Account-wide quest access | active hardening (#124) | Approved account-shared access, atomic claims, migration/validation/admin paths | `data-otservbr-global/scripts/custom/account_quest_system.lua`, `tools/account-quests/**`, DB/config/API/docs | Use existing APIs/store; do not create a second account quest system. |
| Multi-channel architecture | merged phases; safeguards documented | Shared/per-channel state architecture | current source and multichannel handoffs | Read latest handoff and production gates before changes. |
| Forge history ID resolution | merged (#110) | Resolves history item types by ID with name fallback | Forge sources/integration test | Reuse ID-based lookup for custom/duplicate names. |

## AI, map, and deployment tooling

| Module/tool | Status | Purpose/public surface | Source/tests/docs | Reuse notes |
|---|---|---|---|---|
| OTBM script-resolution audit | merged (#104) | Read-only mapping of OTBM AID/UID placements to active Lua/XML handlers | `tools/ai-agent/otbm_script_resolution*`, tests, `docs/ai-agent/OTBM_SCRIPT_RESOLUTION*` | Reuse for map mechanic audits; dynamic registrations remain explicit, never guessed. |
| Promotion overlay materializer | active (#125) | Atomic, hash-verified materialization of reviewed AI-content overlays | `tools/ai-agent/materialize_promotion_overlay.py` and tests | Feeds deploy pipeline; does not deploy or approve production. |
| Canary staging/deployment pipeline | active (#118), atomic base merged | Trusted-base assembly, real Canary smoke, atomic switch/rollback, manifest | `tools/deploy/**`, workflows, `docs/systems/ai-content-deployment.md` | Canonical deployment path; extend rather than duplicate. |
| Hunt-area catalogue tooling | merged (#105 and hardening) | Validates/generates verified static hunt rectangles | `tools/analytics/gameplay_analytics_hunt_area*`, fixtures/tests/docs | Never invent coordinates; placeholders are rejected. |

## CI and test infrastructure

| Module/system | Status | Purpose | Paths | Reuse notes |
|---|---|---|---|---|
| Required Linux check emission | active (#132) | Ensures branch protection receives the nested Linux release check | `.github/workflows/ci.yml` | Coordinate workflow/path-filter changes with #132. |
| CMake preset matrix | maintained | Canonical configure/build/test entry points | `CMakePresets.json`, CMake, `vcproj/canary.vcxproj` | Update every maintained build entry point for new C++ files. |

## Entry template

```md
### Module name
- Status:
- Responsibility/public surface:
- Source paths:
- Tests:
- Documentation:
- Depends on / used by:
- Task/PR:
- Last verified commit:
```
