---
task_id: CAN-20260725-oteryn-oam046-preflight
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-046
status: active
agent: "GPT-5.6 Thinking"
branch: dudantas/oam-046-lua-runtime-preflight
base_branch: main
created: 2026-07-25
updated: 2026-07-25
last_verified_commit: "930e0a15767b7e5348bb36c679fa5e458a76f184"
risk: high
related_issue: ""
related_pr: ""
depends_on:
  - OAM-045 durably completed as d103add3c3a0f9cb026f3ec5b0aad73f13a71e18
blocks:
  - OAM-046 Otheryn target proof
  - OAM-047 start
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260725-oteryn-oam046-preflight.md
  shared: []
  read_only:
    - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
    - docs/agents/OTERYN_TARGET_ARCHITECTURE_CONTRACT.md
    - docs/agents/real-tibia/registry/modules/lua-runtime.yaml
modules_touched:
  - oteryn-architecture-migration
  - lua-runtime
cross_repo_tasks: []
---

# OAM-046 fresh preflight: Lua Runtime

## Selection

Canonical package: `lua-runtime`

Initial disposition: `REVALIDATE`

The package has no canonical dependencies and owns the shared `src/lua/**` runtime boundary. It is selected only for exact target/upstream/legacy revalidation; this preflight does not infer `REUSE` from path presence or source similarity.

## Fresh live-state preflight

- Canary task-start main: `930e0a15767b7e5348bb36c679fa5e458a76f184`.
- Otheryn target main: `e8f683e61427e9967cbc180b837220d4b7487d85`.
- reviewed current upstream: `opentibiabr/canary@7323503b3dc61ed86bf1f04a611b2d0aec64b35a`.
- OAM-045 durable completion: `d103add3c3a0f9cb026f3ec5b0aad73f13a71e18`.
- Otheryn has no open pull request.
- Open Canary PRs `#514`, `#526`, `#559` and `#815` do not own `src/lua/**` or this task path.

## Candidate evaluation

- `network-transport` is rejected because open Canary PR `#514` owns authenticated-session transport validation surfaces.
- `login-protocol` is dependency-invalid because it depends on `network-transport`.
- `physical-client-e2e` is active under the separate E2E Automation Program.
- `gameplay-analytics` is dependency-invalid because it depends on `lua-runtime`.
- `deployment-operations` is dependency-invalid because it depends on `build-system`.
- `lua-runtime` has no dependencies, no live ownership collision and is therefore the next bounded dependency-valid package.

## Canonical boundary

Includes:

- shared Lua state and environment lifecycle;
- script-interface initialization and teardown;
- runtime callback ownership boundaries;
- reload and shutdown safety inventory.

Excludes:

- individual gameplay scripts;
- feature-specific Lua registration families;
- a separate package for every binding family;
- arbitrary Lua execution by analytics or AI systems;
- object-lifetime, serialization, race-freedom or reload-safety claims without focused evidence.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-25T15:20:00+02:00
head: 930e0a15767b7e5348bb36c679fa5e458a76f184
branch: dudantas/oam-046-lua-runtime-preflight
pr: null
status: selected
context_routes:
  - agent-governance
  - cross-repo
  - lua-runtime
owned_paths:
  - docs/agents/tasks/active/CAN-20260725-oteryn-oam046-preflight.md
proven:
  - OAM-045 is durably complete as d103add3c3a0f9cb026f3ec5b0aad73f13a71e18.
  - The canonical lua-runtime registry record has no dependencies and owns src/lua/**.
  - Otheryn has no open pull request.
  - Open Canary PRs 514, 526, 559 and 815 do not overlap src/lua/** or this checkpoint.
  - Network transport, login protocol, physical-client E2E, gameplay analytics and deployment operations are currently collision-blocked, active elsewhere or dependency-invalid.
derived:
  - lua-runtime is the next bounded dependency-valid canonical package.
  - Exact target/upstream/legacy review is required before a final REUSE, ADAPT or DO_NOT_MIGRATE disposition.
unknown:
  - Complete target/upstream/legacy src/lua inventory and exact blob correspondence.
  - Shared-state initialization, teardown and child-interface reload semantics.
  - Object lifetime, userdata safety, callback ownership and shutdown behavior.
  - Runtime behavior under concurrent reload, callback execution or failure paths.
conflicts: []
first_failure: null
rejected_hypotheses:
  - Select network-transport while PR 514 owns related validation surfaces.
  - Select login-protocol before network-transport is dependency-complete.
  - Treat existing E2E, analytics or deployment tooling as dependency-complete OAM packages.
  - Infer Lua runtime reuse from broad path presence or successful unrelated gameplay tests.
changed_paths:
  - docs/agents/tasks/active/CAN-20260725-oteryn-oam046-preflight.md
validation:
  - command: live main, open-PR and ownership review
    result: PASS
    evidence: Exact live baselines and all open PR path sets were reviewed before selection.
  - command: canonical dependency review
    result: PASS
    evidence: lua-runtime has no dependencies; rejected candidates are active, collision-blocked or dependency-invalid.
blockers:
  - Canary preflight exact-head gates and merge
next_action: Open the Canary OAM-046 preflight PR, require exact-head Ownership and CI, audit discussions and main drift, then squash-merge before target work starts.
```
