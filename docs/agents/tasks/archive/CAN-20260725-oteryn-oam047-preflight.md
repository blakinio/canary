---
task_id: CAN-20260725-oteryn-oam047-preflight
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-047
status: completed
agent: "GPT-5.6 Thinking"
branch: dudantas/oam-047-lua-runtime-governance
base_branch: main
created: 2026-07-25
updated: 2026-07-25
completed: 2026-07-25T20:30:00+02:00
last_verified_commit: "06f3f78724f8f74b704272b9b97837b2ba1819d7"
risk: high
related_issue: ""
related_pr: "928"
depends_on:
  - OAM-046 durably completed as 2b09ef1acfe23d1ef4027c85f44b0093420d7434
blocks:
  - OAM-047 durable program reconciliation
  - OAM-048 start
owned_paths:
  exclusive:
    - docs/agents/tasks/archive/CAN-20260725-oteryn-oam047-preflight.md
    - docs/agents/OTERYN_OAM_047_LUA_RUNTIME_REVALIDATION.md
  shared: []
  read_only:
    - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
    - docs/agents/OTERYN_TARGET_ARCHITECTURE_CONTRACT.md
    - docs/agents/real-tibia/registry/modules/lua-runtime.yaml
modules_touched:
  - oteryn-architecture-migration
  - lua-runtime
cross_repo_tasks:
  - Otheryn PR 107 feature merge 5b3bee0dd6eedf8c2f9578c686ca85c0fde519cf
  - Otheryn PR 108 lifecycle merge 68e2b233b02356a79a03422ed51d757b85915bc5
---

# OAM-047 Lua Runtime governance

Final disposition: `lua-runtime → ADAPT`.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-25T20:30:00+02:00
head: 06f3f78724f8f74b704272b9b97837b2ba1819d7
branch: main
pr: 928
status: ready
context_routes:
  - agent-governance
  - cross-repo
  - lua-runtime
owned_paths:
  - docs/agents/tasks/archive/CAN-20260725-oteryn-oam047-preflight.md
  - docs/agents/OTERYN_OAM_047_LUA_RUNTIME_REVALIDATION.md
proven:
  - Canary preflight PR 922 selected dependency-valid lua-runtime and merged as bc8d7827f652b8b8b3200f7ef81818e8d5d149f5.
  - Attached child LuaScriptInterface objects retained closed shared-state pointers and registry references across LuaEnvironment::reInitState.
  - Otheryn now closes attached child registry tables before lua_close and rebinds the same live children after creating the replacement main state.
  - Focused fixtures cover active, dormant and destroyed interfaces, stale registry IDs, new event registration and the shared test interface.
  - The build-path correction folded registry code into existing lua_environment.cpp so CMake and Visual Studio use one supported translation unit.
  - Otheryn head a7349190a51d627e4668af56912337ff8cadec46 passed Autofix 30167797667, CI 30167797744 and Required 30167797642.
  - Otheryn PR 107 merged as 5b3bee0dd6eedf8c2f9578c686ca85c0fde519cf after clean discussions and zero main drift.
  - Otheryn lifecycle PR 108 passed Required 30169112582 and merged as 68e2b233b02356a79a03422ed51d757b85915bc5.
  - Canary governance head 4ed59d4d11bd8d9f82f95c25ddb50a08f6103c7b passed Ownership 30169261944 and CI 30169262061.
  - Canary PR 928 had no comments, reviews or review threads and zero main drift before expected-head merge.
  - Canary governance PR 928 merged as 06f3f78724f8f74b704272b9b97837b2ba1819d7.
derived:
  - lua-runtime requires ADAPT because main-state replacement did not preserve attached child-interface validity.
  - The correction belongs to shared Lua lifecycle and excludes feature-specific script reload policy.
unknown:
  - Complete production subsystem reload ordering and callback timing.
  - Concurrent reload/read/callback safety and race freedom.
  - Exhaustive userdata, timer parameter and external wrapper lifetime safety.
  - Physical-client, protocol and production gameplay effects.
conflicts: []
first_failure:
  marker: untracked-child-interface-reset
  evidence: LuaEnvironment::reInitState closed the main state while attached children retained pointers and registry IDs unless separately reinitialized.
rejected_hypotheses:
  - Finalize REUSE from source identity or compilation alone.
  - Reload all gameplay scripts inside the main-state primitive.
  - Expand into feature bindings, userdata redesign or concurrent reload orchestration.
  - Claim physical-client or production safety from focused lifecycle proof.
changed_paths:
  - docs/agents/tasks/archive/CAN-20260725-oteryn-oam047-preflight.md
  - docs/agents/OTERYN_OAM_047_LUA_RUNTIME_REVALIDATION.md
validation:
  - command: Otheryn focused contract and maintained build matrix
    result: PASS
    evidence: CI 30167797744 passed focused fixtures and all maintained builds/runtime smokes.
  - command: Otheryn feature and lifecycle gates and audits
    result: PASS
    evidence: PR 107 and PR 108 merged after required exact-head gates and clean discussions.
  - command: Canary governance exact-head gates and audit
    result: PASS
    evidence: Head 4ed59d4d11bd8d9f82f95c25ddb50a08f6103c7b passed Ownership 30169261944 and CI 30169262061 and merged as 06f3f78724f8f74b704272b9b97837b2ba1819d7.
blockers:
  - durable OAM-047 program reconciliation
next_action: Merge this lifecycle-only archive and reconcile OAM-047 in the program document before starting OAM-048.
```
