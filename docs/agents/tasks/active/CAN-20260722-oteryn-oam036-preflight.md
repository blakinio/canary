---
task_id: CAN-20260722-oteryn-oam036-preflight
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
status: ready
agent: "GPT-5.6 Thinking"
branch: dudantas/oam-036-preflight
base_branch: main
created: 2026-07-22
updated: 2026-07-22
last_verified_commit: "27b49fbbdafda9c365bc25b0c2adb790337d42d4"
risk: medium
related_issue: ""
related_pr: "715"
depends_on:
  - OAM-035 formally complete
blocks:
  - OAM-036 target proof/delivery selection
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260722-oteryn-oam036-preflight.md
  shared: []
  read_only:
    - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
    - docs/agents/real-tibia/registry/modules/**
modules_touched:
  - oteryn-architecture-migration
  - boss-encounters
cross_repo_tasks: []
---

# OAM-036 Fresh Preflight

## Goal

Perform a fresh dependency-valid canonical-module preflight after formal OAM-035 closure. Do not implement OAM-036 in this task.

## Selected package

`boss-encounters` is the selected dependency-valid OAM-036 canonical package.

Preflight disposition: `REUSE candidate`.

The final OAM-036 disposition still requires bounded target-side proof. This preflight does not claim participant eligibility, scoring arithmetic, loot correctness, persistence atomicity, runtime correctness, physical-client E2E or Real Tibia parity.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-22T11:25:00+02:00
head: 6fc9c7042b1e472d1c32c9f6986d67eb25f25089
branch: dudantas/oam-036-preflight
pr: 715
status: ready
context_routes:
  - agent-governance
  - cross-repo
owned_paths:
  - docs/agents/tasks/active/CAN-20260722-oteryn-oam036-preflight.md
proven:
  - OAM-035 is formally complete after Otheryn target archive merge 6275021bbb83dc28d2f5d6cf8db5b16aa7206544.
  - Fresh Canary main baseline is 27b49fbbdafda9c365bc25b0c2adb790337d42d4.
  - Fresh Otheryn main baseline is 6275021bbb83dc28d2f5d6cf8db5b16aa7206544.
  - Fresh upstream Canary baseline is 71a0f92b4da3f550b292fa7536a0e35c2769f1ae.
  - Fresh maintained OTClient baseline is a6868920443dc285656bd016acdb2c1ea566e511.
  - Canonical boss-encounters depends only on completed creature-definitions and player-persistence.
  - Canonical ownership is bounded to reward-boss participation contribution scoring reward generation reward-container persistence handoff and encounter lifecycle discovery; generic boss AI definitions spawns raids cooldowns and Bosstiary remain excluded.
  - Otheryn fresh upstream and legacy Canary share exact reward_boss.lua blob 72476dfcbdd8fd92d6b5bd3ad3015efef87cf2f3.
  - Otheryn fresh upstream and legacy Canary share exact reward_chest.lua blob 4abe17ad2f3103f30f172f23ebdca391197f8646.
  - Fresh open-PR searches found no OAM-036 or selected boss-encounter writer in Canary and no open Otheryn pull request.
  - Semantic review confirms the selected scripts own target-list participation state contribution aggregation boss-death score normalization reward generation reward chest insertion and offline-player save handoff.
  - Reviewed delivered-PR searches for reward boss reward chest GlobalBosses and BossParticipation surfaced no stronger bounded legacy donor for the selected canonical roots.
derived:
  - boss-encounters is the next selected dependency-valid OAM-036 canonical package.
  - Whole-module legacy import is not justified because all three reviewed server states share the exact selected roots and no stronger delivered legacy delta was identified.
  - The smallest evidence-backed preflight outcome is boss-encounters as a REUSE candidate pending bounded target-side proof.
unknown:
  - Exact focused target proof boundary and resulting final REUSE or ADAPT disposition until OAM-036 target-side validation executes.
  - Whether bounded proof exposes an existing target defect outside the reviewed exact roots that still belongs to boss-encounters ownership.
conflicts: []
first_failure:
  marker: none
  evidence: No OAM-036 implementation or target validation failure exists because this task is preflight-only.
rejected_hypotheses:
  - Select raids before reviewing boss-encounters; both are dependency-valid but boss-encounters is the next independent TSD-006 boundary after completed creature definitions and Creature AI and has a smaller two-root proof surface.
  - Infer final REUSE from blob identity alone; final disposition remains gated on target-side semantic proof.
  - Expand boss-encounters into Bosstiary boss AI spawn scheduling quest cooldowns or raid orchestration; canonical registry excludes those ownership boundaries.
changed_paths:
  - docs/agents/tasks/active/CAN-20260722-oteryn-oam036-preflight.md
validation:
  - command: fresh dependency ownership baseline and open-PR preflight
    result: PASS
    evidence: both hard dependencies completed exact baselines pinned and no overlapping open writer found
  - command: exact-root and semantic donor preflight
    result: PASS
    evidence: both canonical roots match target upstream and legacy while semantic review and delivered-PR searches found no stronger bounded donor
blockers: []
next_action: Require exact-current-head Agent Task Ownership and CI success on PR 715, audit the one-file preflight scope and review state, then expected-head squash merge before creating the bounded OAM-036 target proof in Otheryn.
```
