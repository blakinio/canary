---
task_id: CAN-20260722-oteryn-oam037-preflight
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
status: ready
agent: "GPT-5.6 Thinking"
branch: dudantas/oam-037-preflight
base_branch: main
created: 2026-07-22
updated: 2026-07-22
last_verified_commit: "663de1726e82145f5b8027126dbe434cfa74440b"
risk: medium
related_issue: ""
related_pr: "733"
depends_on:
  - OAM-036 formally complete
blocks:
  - OAM-037 target proof/delivery selection
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260722-oteryn-oam037-preflight.md
  shared: []
  read_only:
    - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
    - docs/agents/real-tibia/registry/modules/**
modules_touched:
  - oteryn-architecture-migration
  - raids
cross_repo_tasks: []
---

# OAM-037 Fresh Preflight

## Goal

Perform a fresh dependency-valid canonical-module preflight after formal OAM-036 closure. Do not implement OAM-037 in this task.

## Selected package

`raids` is the selected dependency-valid OAM-037 canonical package.

Preflight disposition: `REUSE candidate`.

The final OAM-037 disposition still requires bounded target-side proof. This preflight does not claim raid probability or timing parity, event-order correctness, data-definition completeness, restart behavior, distributed or multichannel raid safety, physical-client E2E or Real Tibia parity.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-22T23:04:40+02:00
head: 928d551497b716a6224b25da6c09717730e1a419
branch: dudantas/oam-037-preflight
pr: 733
status: ready
context_routes:
  - agent-governance
  - cross-repo
owned_paths:
  - docs/agents/tasks/active/CAN-20260722-oteryn-oam037-preflight.md
proven:
  - OAM-036 is formally complete after Otheryn target archive merge 3aaf77fe27600b274d2b9c9e6bd30d887e0afd0e.
  - Fresh Canary main baseline is 663de1726e82145f5b8027126dbe434cfa74440b.
  - Fresh Otheryn main baseline is 3aaf77fe27600b274d2b9c9e6bd30d887e0afd0e.
  - Fresh upstream Canary baseline is 7323503b3dc61ed86bf1f04a611b2d0aec64b35a.
  - Fresh maintained OTClient baseline is 1e5305395159142634f182d9e888e5f9164228c6.
  - Canonical raids depends only on completed creature-definitions and engine-scheduler; OAM-034 completed creature-definitions and OAM-003 completed engine-scheduler as REUSE.
  - The OAM-036 preflight already established raids as dependency-valid but selected boss-encounters first because it was the smaller independent TSD-006 proof surface.
  - Canonical raids ownership is bounded to raid XML registry load and reload interval margin repeat and running-state lifecycle periodic selection ordered announce spawn and script events plus stop reset and last-end state; static spawns individual raid definitions boss rewards and proof of exact probability or timing remain excluded.
  - Otheryn and fresh upstream share exact canonical raids.cpp blob d46a549a341e0872474bd723b10d1208fa22da8c and raids.hpp blob 777558e3e199816bb596636fc7487c38c29224ee.
  - Legacy Canary shares raids.hpp blob 777558e3e199816bb596636fc7487c38c29224ee but diverges on raids.cpp as blob 57628effc46743000eab4e4c004cfdfa376114aa.
  - Target and fresh upstream schedule raid checks on DispatcherLane::Maintenance and detect failed initial or repeat scheduling; the reviewed legacy Canary baseline lacks those safeguards in the same core scheduling path.
  - Fresh open-PR searches found no overlapping raids writer in Canary or Otheryn and no separate OAM-037 pull request besides PR 733.
  - The raids registry has no client paths, so the maintained OTClient head change does not create a direct client mutation requirement for this preflight.
derived:
  - raids is the next selected dependency-valid OAM-037 canonical package after completed boss-encounters.
  - Whole-module legacy import is not justified because the target matches fresh upstream on the canonical core and the reviewed legacy core is older at the scheduler boundary.
  - The smallest evidence-backed preflight outcome is raids as a REUSE candidate pending bounded target-side proof.
unknown:
  - Exact focused target proof boundary and resulting final REUSE or ADAPT disposition until OAM-037 target-side validation executes.
  - Whether bounded proof exposes a target defect that still belongs to raids ownership outside the reviewed scheduler and lifecycle core.
conflicts: []
first_failure:
  marker: none
  evidence: No OAM-037 implementation or target validation failure exists because this task is preflight-only.
rejected_hypotheses:
  - Keep OAM-037 package selection UNKNOWN after OAM-036 closure; the canonical registry plus completed dependency chain now make raids the next bounded TSD-006 package.
  - Infer final REUSE from blob identity alone; final disposition remains gated on target-side semantic proof.
  - Prefer the divergent legacy raids.cpp as a stronger donor; targeted review shows the target and fresh upstream contain newer maintenance-lane and scheduling-failure safeguards absent from the legacy core.
  - Expand raids into static spawns individual raid definitions boss rewards quests or multichannel redesign; the canonical registry excludes those ownership boundaries.
changed_paths:
  - docs/agents/tasks/active/CAN-20260722-oteryn-oam037-preflight.md
validation:
  - command: fresh dependency ownership baseline and open-PR preflight
    result: PASS
    evidence: hard dependencies are completed exact baselines are pinned and no overlapping raids writer was found
  - command: exact-root and semantic donor preflight
    result: PASS
    evidence: target and fresh upstream share the canonical core while the divergent legacy core lacks reviewed scheduler safeguards and is not a stronger whole-module donor
  - command: PR 733 prior-head Agent Task Ownership run 29956286283 and CI run 29956286653
    result: PASS
    evidence: exact prior head 928d551497b716a6224b25da6c09717730e1a419 completed both workflows successfully before this final preflight checkpoint update
blockers: []
next_action: Require exact-current-head Agent Task Ownership and full final-gate CI success on PR 733, audit the one-file preflight scope and review state, then expected-head squash merge before creating the bounded OAM-037 target proof in Otheryn.
```
