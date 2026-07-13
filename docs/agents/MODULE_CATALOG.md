# Canary Module and System Catalogue

Last reviewed: 2026-07-14

This catalogue makes reusable work visible across agents. Verify current source, tests, and PR state before use.

## Maintenance contract

Update this file in the same PR that adds a reusable module/service/manager/parser/library/tool/workflow abstraction/test utility; changes a public API/config/schema/format/protocol; deprecates or replaces a module; or introduces active work another agent could duplicate.

## Runtime and architecture

| Module/system | Status | Purpose/public surface | Source/tests/docs | Reuse notes |
|---|---|---|---|---|
| InstanceManager | merged (#107, #151, #159, #163, #168, #174, #201, #231, #233) | Strong instance IDs, region-backed lifecycle, stable-ID creature ownership registry, summon inheritance policy, idempotent close, automatic unregister on removal (`Game::removeCreature()`), periodic timeout sweep (`Game::start()`); owned by `Game::getInstanceManager()` | `src/game/instance/instance_id.hpp`, `instance_manager.{hpp,cpp}`, `instance_creature_binder.hpp`, `instance_scoped_event.hpp`, focused tests, `docs/architecture/instance-manager.md` | One manager instance via `Game::getInstanceManager()`; do not create a second registry/manager/binder/global singleton. |
| InstanceRegionPool | merged (#121, #151) | Thread-safe reservation of pre-carved non-overlapping 3D regions | `src/game/instance/instance_region_pool.{hpp,cpp}`, tests, architecture doc | Reuse for physical instance regions; it does not copy maps or own tiles. |
| InstanceArenaService | active (Instanced Test Arena program) | Administrator-only real consumer of `InstanceManager`: fixed two-region configuration, arena create/activate/close lifecycle | `src/game/instance/instance_arena_service.{hpp,cpp}`, focused tests, `docs/architecture/instanced-test-arena.md`, `docs/agents/programs/INSTANCED_TEST_ARENA_PROGRAM.md` | Reuse for the arena feature only; not a generic dungeon framework. Region coordinates live in exactly one place (`InstanceArenaService::configuredRegions()`); do not duplicate them elsewhere. |
| DI service access | merged (#117, #119) | DI resolution for `SharedPtrManager` and `Scripts` | relevant sources/audit/tests | Extend existing DI; do not add raw Meyers singletons. |
| Gameplay Analytics | merged correctness hardening (#135) and dry-run audit (#140); operator enablement remains manual | Runtime telemetry with UTC rollover/combat eligibility, bounded persistence, configurable maintenance brackets, dimension-safe reporting and database-free configuration validation | `data-otservbr-global/scripts/lib/gameplay_analytics_*.lua`, `tools/analytics/**`, deploy workflows/docs, `docs/systems/ai-content-deployment.md` | Canonical deployment path; extend rather than duplicate. |
| Hunt-area catalogue tooling | merged (#105 and hardening) | Validates/generates verified static hunt rectangles | `tools/analytics/gameplay_analytics_hunt_area*`, fixtures/tests/docs | Never invent coordinates; placeholders are rejected. |

## CI and test infrastructure

| Module/system | Status | Purpose | Paths | Reuse notes |
|---|---|---|---|---|
| Gameplay Analytics dry-run audit | merged (#140) | Deterministic Analytics logic/configuration tests without Canary or MariaDB | `.github/workflows/gameplay-analytics-dry-run.yml`, `tools/analytics/test_gameplay_analytics_correctness_edge_cases.lua`, `tools/analytics/test_gameplay_analytics_maintenance_config_dry_run.sh` | Run before staging; it complements rather than replaces real engine/database integration. |
| Required Linux check emission | merged (#132) | Ensures branch protection receives the nested Linux release check | `.github/workflows/ci.yml` | Preserve the unconditional required Linux release check when editing path filters. |
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
