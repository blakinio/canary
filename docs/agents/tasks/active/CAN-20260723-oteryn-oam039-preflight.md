---
task_id: CAN-20260723-oteryn-oam039-preflight
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
status: validating
agent: "GPT-5.6 Thinking"
branch: dudantas/oam-039-governance-finalize
base_branch: main
created: 2026-07-23
updated: 2026-07-23
last_verified_commit: "2b2eafcd0d7990f499f25acf74af6526ca72ceee"
risk: high
related_issue: ""
related_pr: ""
depends_on:
  - OAM-038 formally complete
blocks:
  - OAM-040 start
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260723-oteryn-oam039-preflight.md
    - docs/agents/OTERYN_OAM_039_INSTANCES_REVALIDATION.md
  shared: []
  read_only:
    - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
modules_touched:
  - oteryn-architecture-migration
  - instances
cross_repo_tasks: []
---

# OAM-039 Instances governance

## Final disposition

`instances → ADAPT`

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-23T13:30:00+02:00
head: c2debfd8f2604ccd6b4cc10f34b68c823a08317d
branch: dudantas/oam-039-governance-finalize
pr: null
status: validating
context_routes:
  - agent-governance
  - cpp-runtime
  - cross-repo
owned_paths:
  - docs/agents/tasks/active/CAN-20260723-oteryn-oam039-preflight.md
  - docs/agents/OTERYN_OAM_039_INSTANCES_REVALIDATION.md
proven:
  - OAM-038 is formally complete after Canary durable reconciliation efaa970229346c13c9ccfe17805e4b914ec6e8ad and Otheryn target archive a275f1d788b50164ffc79b6f6143e13b9150c82e.
  - Canary OAM-039 preflight PR 771 squash-merged as 5c0613fd853e85421a89f661e9b3774c4dd730ff and selected canonical instances as ADAPT candidate.
  - Clean Otheryn and fresh upstream lacked canonical InstanceManager roots while legacy Canary provided the staged behavioral donor.
  - Canonical target ownership remained bounded to src/game/instance subsystem behavior and focused tests/build registration; Game Creature Lua talkaction protocol client map-content asset schema and persistence paths were excluded.
  - Otheryn PR 81 changed exactly 19 intended bounded paths.
  - Initial target head 58c4d2cf2cb5f26d67974b78e9d8e16885eae702 exposed one owned Linux-debug lifecycle failure where Closing returned early and a quarantined region was not released after ownership drain.
  - Bounded repair changed Closing retries to skip duplicate cleanup while retrying finalization and region release when ownership becomes empty.
  - Otheryn PR 81 final head e216c3bb732bc6dc97374833bbfcb13a4f4ebc50 passed autofix 30002236999 CI 30002237279 Required 30002237057 Fast Checks Lua Linux release/debug full tests both Windows paths macOS and Docker validation.
  - Final target comments reviews and review threads were empty and Otheryn main had no drift from task-start base before merge.
  - Otheryn PR 81 squash-merged as a2a52e239d8e8a770ff7376fcbb9b5bfdcc8cc13.
derived:
  - OAM-039 final disposition is instances ADAPT.
  - The clean target now contains the bounded instance lifecycle isolation foundation with one evidence-driven lifecycle repair.
  - Cross-module production activation remains outside OAM-039 and is not implied by this governance closure.
  - OAM-040 remains blocked until this governance merge separate Canary lifecycle archive durable program reconciliation and Otheryn target-task archive all complete.
unknown:
  - Exact final Canary governance merge SHA until this PR completes.
conflicts: []
first_failure:
  marker: InstanceManagerTest.CleanupRunsExactlyOnceAndDirtyRegionIsQuarantined
  evidence: Initial target CI found Closing retry did not finalize a previously quarantined region after ownership drain; exact-head bounded repair passed full post-fix target validation.
rejected_hypotheses:
  - Classify instances as REUSE; clean target and fresh upstream lacked canonical runtime roots.
  - Copy legacy cross-module Game Creature Lua or talkaction wiring; those remain interaction boundaries outside canonical ownership.
  - Import hard-coded legacy data-canary arena coordinates; target map content requires separately owned evidence.
  - Weaken the failing lifecycle test; the failure represented a real finalization defect and was repaired in the owned subsystem.
changed_paths:
  - docs/agents/tasks/active/CAN-20260723-oteryn-oam039-preflight.md
  - docs/agents/OTERYN_OAM_039_INSTANCES_REVALIDATION.md
validation:
  - command: Otheryn PR 81 exact-head target gates
    result: PASS
    evidence: final head e216c3bb732bc6dc97374833bbfcb13a4f4ebc50 passed autofix 30002236999 CI 30002237279 Required 30002237057 and full Linux-debug Run Tests after the bounded lifecycle repair
  - command: target changed-path and interaction audit
    result: PASS
    evidence: exactly 19 intended bounded paths no comments reviews or threads and no Otheryn-main drift before merge a2a52e239d8e8a770ff7376fcbb9b5bfdcc8cc13
blockers: []
next_action: Open the two-path Canary OAM-039 governance PR with ci:final-gate, bind its PR number, require exact-current-head Agent Task Ownership and CI, audit scope interactions and Canary-main drift, then expected-head squash merge before separate lifecycle archive.
```
