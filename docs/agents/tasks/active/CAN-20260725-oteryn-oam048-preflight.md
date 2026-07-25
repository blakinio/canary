---
task_id: CAN-20260725-oteryn-oam048-preflight
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-048
status: active
agent: "GPT-5.6 Thinking"
branch: dudantas/oam-048-gameplay-analytics-preflight
base_branch: main
created: 2026-07-25
updated: 2026-07-25
last_verified_commit: "913a056058273bdd538f01c93b4cbb068759290e"
risk: high
related_issue: ""
related_pr: ""
depends_on:
  - OAM-047 durably completed as 913a056058273bdd538f01c93b4cbb068759290e
blocks:
  - OAM-048 Otheryn target disposition proof
  - OAM-049 start
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260725-oteryn-oam048-preflight.md
  shared: []
  read_only:
    - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
    - docs/agents/OTERYN_TARGET_ARCHITECTURE_CONTRACT.md
    - docs/agents/real-tibia/registry/modules/gameplay-analytics.yaml
    - docs/systems/gameplay-analytics-dry-run.md
modules_touched:
  - oteryn-architecture-migration
  - gameplay-analytics
cross_repo_tasks: []
---

# OAM-048 gameplay analytics preflight

## Selection

Canonical package: `gameplay-analytics`.

Initial disposition: `EXPERIMENTAL_ONLY candidate`.

The package is now dependency-valid after OAM-047 completed `lua-runtime`. It is optional platform tooling rather than core gameplay responsibility, owns only legacy Global datapack, analytics tools/workflows and documentation paths, is disabled by default, and has no target implementation root at the pinned Otheryn head. The current relational model may retain player identifiers and its privacy, retention and production-readiness contracts remain explicitly unresolved.

Final disposition requires bounded target-side proof that Otheryn core does not depend on this telemetry, that the package can remain isolated outside core, and that no consumer requires target-local migration.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-25T20:42:00+02:00
head: 913a056058273bdd538f01c93b4cbb068759290e
branch: dudantas/oam-048-gameplay-analytics-preflight
pr: pending
status: investigating
context_routes:
  - agent-governance
  - cross-repo
  - lua-runtime
owned_paths:
  - docs/agents/tasks/active/CAN-20260725-oteryn-oam048-preflight.md
proven:
  - OAM-047 durably completed as 913a056058273bdd538f01c93b4cbb068759290e before OAM-048 selection.
  - Canary task-start main is 913a056058273bdd538f01c93b4cbb068759290e.
  - Otheryn task-start main is 68e2b233b02356a79a03422ed51d757b85915bc5.
  - Reviewed current upstream is 7644bcbcbbad4a09e52a5707ed531e4dd21d8a79.
  - gameplay-analytics depends only on completed lua-runtime and interacts with existing combat, database, party, persistence and world-map boundaries.
  - The module is optional platform tooling and excludes gameplay formula correctness, complete telemetry coverage, production stability, privacy assurance and retention assurance.
  - Legacy config blob 939b8b8b51fdf0c1157afb7df8af5cccf1d3ebdf sets enabled=false and anonymizePlayers=false.
  - Legacy loader blob 86f6ae164077ce616e87f278e553475225a52f8a composes core, context, schema, batching, reliability and correctness layers.
  - The representative target config path is absent from Otheryn at task start.
  - Otheryn has no open pull request and current open Canary work does not own analytics implementation paths or this checkpoint.
derived:
  - gameplay-analytics is dependency-valid but does not yet satisfy core target ownership or privacy/production criteria.
  - EXPERIMENTAL_ONLY is the strongest current candidate because the legacy laboratory implementation is useful but should remain isolated from Otheryn core unless separately approved.
unknown:
  - Whether any target startup path or operator workflow has an undocumented dependency on analytics Lua globals.
  - Exact privacy, retention, schema migration and deletion requirements for a future target analytics product.
  - Production performance and failure-isolation behavior under realistic telemetry volume.
conflicts: []
first_failure:
  marker: missing-core-target-contract
  evidence: The optional disabled-by-default telemetry implementation has no target root and unresolved privacy, retention and production-readiness boundaries.
rejected_hypotheses:
  - Select network-transport while Canary PR 514 owns overlapping authenticated transport validation.
  - Treat existing dry-run or MariaDB tests as production readiness or target ownership.
  - Import the full legacy analytics stack merely because lua-runtime is now complete.
  - Claim anonymization, privacy or retention safety from disabled-by-default configuration.
changed_paths:
  - docs/agents/tasks/active/CAN-20260725-oteryn-oam048-preflight.md
validation:
  - command: fresh live-state, open-PR and ownership review
    result: PASS
    evidence: Exact Canary/Otheryn/upstream heads were pinned and no overlapping analytics writer was found.
  - command: canonical dependency and scope review
    result: PASS
    evidence: lua-runtime is complete; gameplay-analytics remains optional platform tooling with explicit production/privacy exclusions.
  - command: exact legacy and target root review
    result: PASS
    evidence: Legacy config/loader blobs were pinned and the representative target config path is absent.
blockers:
  - Canary preflight exact-head Ownership and CI
  - bounded Otheryn core-isolation and target-consumer proof
next_action: Open and validate the OAM-048 preflight PR, then create the bounded Otheryn disposition task from current target main.
```
