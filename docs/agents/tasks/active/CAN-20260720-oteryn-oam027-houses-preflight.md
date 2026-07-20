---
task_id: CAN-20260720-oteryn-oam027-houses-preflight
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-027
status: ready
agent: "GPT-5.5 Thinking"
branch: docs/oam-027-houses-preflight
base_branch: main
created: 2026-07-20
updated: 2026-07-20
last_verified_commit: "6b1bbadf5c9fdc9c4b5831dcfbdef9c9ed894b3d"
risk: medium
related_pr: "644"
depends_on:
  - canonical otbm-tooling active/mapped/audited foundation
  - completed OAM player-persistence foundation
blocks:
  - OAM-028
modules_touched:
  - houses
---

# Goal

Revalidate canonical OAM-027 `houses` from exact live baselines, adapt only independently reviewed house-runtime correctness that fits the clean target architecture, close target/governance/lifecycle, then reconcile the durable Oteryn migration program before OAM-028 starts.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-20T22:22:00Z
head: e6efb626e61b74ddc17be1a382832aaf60fec2c2
branch: docs/oam-027-houses-preflight
pr: 644
status: ready
context_routes:
  - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
  - docs/agents/OTERYN_TARGET_ARCHITECTURE_CONTRACT.md
  - docs/agents/real-tibia/registry/modules/houses.yaml
  - docs/agents/real-tibia/registry/modules/otbm-tooling.yaml
owned_paths:
  - docs/agents/tasks/active/CAN-20260720-oteryn-oam027-houses-preflight.md
  - docs/agents/OTERYN_OAM_027_HOUSES_REVALIDATION.md
proven:
  - OAM-001..OAM-026 are durably complete; OAM-026 lifecycle and target checkpoint are archived.
  - Task-start Canary main is 0251b96105720cb67d5ed7a1b3ec8350baa8e312.
  - Task-start Otheryn main is 5003753e491250732910e9d5857b20293d1bd9ab.
  - Fresh upstream Canary is 71a0f92b4da3f550b292fa7536a0e35c2769f1ae.
  - Maintained OTClient is a6868920443dc285656bd016acdb2c1ea566e511.
  - Canonical houses depends on otbm-tooling and player-persistence; otbm-tooling is active/mapped/audited and player-persistence is completed by the OAM foundation.
  - Open house-related PR 526 is evidence-only security audit documentation and does not own house production paths.
  - Target and upstream house.cpp share blob 25fa954a55763bc9473234682d143c9761843403; legacy current house.cpp differs.
  - Merged legacy PR 60 is the bounded accepted house-transfer correctness donor; legacy multichannel house ownership/mirroring is excluded.
  - Otheryn PR 55 final head 3cfc133a835f7ad14ed8a94cc720c1f0b1a31a65 passed autofix 167 run 29782520081, CI 202 run 29782520156 and Required 184 run 29782520075.
  - Final Linux debug Run Tests passed after removal of one invalid synthetic House proof harness; test-log artifact 8477497565 digest is sha256:548c9077d94c94c515bff2e33c574bcb67b5b9a31eb09124b152976eb048b349.
  - Target PR 55 changed exactly five intended paths, had no comments/reviews/threads, no target-main drift, and merged by expected-head squash as c140c4bb9f40067acc36bc446c9e664e6f791c5a.
  - Canary main advanced to 6b1bbadf5c9fdc9c4b5831dcfbdef9c9ed894b3d only through independently owned OTBM/E2E work with no overlap in OAM-027 governance or house runtime; this branch was reconstructed onto that current main.
derived:
  - Final OAM-027 disposition is houses ADAPT using only the reviewed PR 60 transfer-safety boundary.
  - The first target CTest failure was a proof-harness defect, not evidence against the production adaptation.
unknown:
  - Final Canary governance exact-head gate outcome until PR 644 ready-state Ownership and CI complete.
conflicts: []
first_failure:
  marker: Oam027HousesAdaptTest.PreservesBasicHouseIdentityAndState SEGFAULT
  evidence: target CI 200 linux-debug CTest 411/412 on superseded head e3c18e52940df481521ae9c8c413c3f5420a383f; source-contract proof passed; harness removed before final green head
rejected_hypotheses:
  - Whole-file legacy house.cpp is a safe donor; rejected because legacy also contains separately owned multichannel house architecture.
  - Blob identity is sufficient for REUSE; rejected because merged PR 60 proves an independent house-runtime correctness delta absent from target/upstream.
  - The synthetic House-construction SEGFAULT proves a production defect; rejected after the donor-contract test passed and final full CTest passed with only the invalid harness removed.
changed_paths:
  - docs/agents/tasks/active/CAN-20260720-oteryn-oam027-houses-preflight.md
  - docs/agents/OTERYN_OAM_027_HOUSES_REVALIDATION.md
validation:
  - command: live-state and canonical dependency audit
    result: PASS
    evidence: exact task-start SHAs and registry records pinned in report
  - command: open PR ownership overlap audit
    result: PASS
    evidence: no active PR owns canonical house production paths; PR 526 is evidence-only docs
  - command: Otheryn PR 55 exact-head target gate
    result: PASS
    evidence: autofix 167, CI 202, Required 184 on final head 3cfc133a835f7ad14ed8a94cc720c1f0b1a31a65; squash merge c140c4bb9f40067acc36bc446c9e664e6f791c5a
  - command: Canary main drift audit 0251b961..6b1bbadf
    result: PASS
    evidence: only independent OTBM/E2E paths; no OAM-027 governance or canonical house runtime overlap
blockers: []
next_action: Mark Canary PR 644 ready, require Agent Task Ownership and final-gate CI success on the resulting exact final head, audit exactly two governance files plus comments/reviews/threads and Canary-main drift, then expected-head squash merge if all gates remain clean.
```
