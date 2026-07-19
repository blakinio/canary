---
task_id: CAN-20260719-oteryn-imbuements-revalidation
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-019
status: implementing
agent: "GPT-5.5 Thinking"
branch: docs/oam-019-imbuements-revalidation
base_branch: main
created: 2026-07-19
updated: 2026-07-19T14:05:00+02:00
last_verified_commit: "e551f3fd33c9642399bb1e70d1f2f6383464b936"
risk: high
related_pr: "588"
depends_on:
  - OAM-013
blocks:
  - OAM-020
modules_touched:
  - imbuements
owned_paths:
  exclusive:
    - docs/agents/OTERYN_OAM_019_IMBUEMENTS_REVALIDATION.md
    - docs/agents/tasks/active/CAN-20260719-oteryn-imbuements-revalidation.md
---

# Goal

Revalidate canonical OAM-019 `imbuements` against immutable fresh task-start baselines and migrate only the strongest coherent dependency-valid implementation into Otheryn.

# Immutable task-start baselines

```text
Canary:   e551f3fd33c9642399bb1e70d1f2f6383464b936
Otheryn:  7ba76d2754a060a9a9eec0a23c686aefac725af2
upstream: 691614c1a302aee776002ca3851eca399be1a82c
OTClient: 2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f
```

# Dependency and ownership preflight

Canonical `imbuements` depends on completed `combat` and `player-persistence` boundaries and interacts with `protocol`.

Otheryn had no open PRs at preflight. No live Canary PR claimed Imbuement runtime/data paths. The open shared-state/economy security audit is evidence-only and does not own this migration boundary.

# Current candidate evidence

Merged legacy repair chain under exact review:
- PR #86 storage filter correctness;
- PR #206 Powerful unlock storage mapping;
- PR #239 Vibrancy scroll mappings;
- PR #251 current-live fees/Strike/Punch/unlock markers;
- PR #282 direct numeric-ID authorization.

Target task-start does not contain `src/creatures/players/imbuements/imbuement_storage_policy.hpp`. A stronger-than-target legacy delta therefore exists, but final `ADAPT`/`REUSE` disposition remains evidence-driven until the complete bounded donor chain and target tests are verified.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-19T14:05:00+02:00
head: bb27b2592619a966280e63f85daa23d09f3dd4ac
branch: docs/oam-019-imbuements-revalidation
pr: 588
status: validating
next_action: Open the Canary governance draft PR, verify exact merged donor PR heads and path-level current blobs, then create the bounded Otheryn target branch and materialize only the coherent Imbuement adaptation with focused tests.
first_failure:
  marker: none
  evidence: No OAM-019 validation failure has occurred yet; the target is known to lack the legacy storage-policy helper, which is migration evidence rather than a test failure.
context_routes:
  - docs/agents/OTERYN_OAM_019_IMBUEMENTS_REVALIDATION.md
  - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
  - docs/agents/real-tibia/registry/modules/imbuements.yaml
  - docs/ai-agent/IMBUEMENT_VALIDATION_REPORT.md
owned_paths:
  - docs/agents/OTERYN_OAM_019_IMBUEMENTS_REVALIDATION.md
  - docs/agents/tasks/active/CAN-20260719-oteryn-imbuements-revalidation.md
proven:
  - OAM-018 is fully complete through target, governance, lifecycle and durable program reconciliation.
  - Fresh OAM-019 task-start baselines are pinned above.
  - Canonical imbuements depends on completed combat and player-persistence boundaries.
  - Otheryn has no open pull requests at task start.
  - No live Canary PR claims Imbuement runtime/data write ownership.
  - Legacy Canary PR #86 is merged and fixes configured-storage filtering through an isolated policy helper absent from task-start Otheryn.
  - Legacy Canary PR #282 is merged and adds direct numeric-ID premium/storage authorization before resource mutation.
derived:
  - Imbuements is a dependency-valid and more bounded OAM-019 candidate than market or Exaltation Forge.
  - Whole-module REUSE cannot be accepted without evaluating the delivered legacy repair chain because the target lacks at least one proven correctness helper.
unknown:
  - The exact smallest coherent donor subset across PRs #86, #206, #239, #251 and #282.
  - Final OAM-019 disposition and exact target changed paths.
conflicts: []
rejected_hypotheses:
  - Selecting market merely because it is adjacent in the items-economy inventory despite its additional protocol/client dependency burden.
  - Treating target/upstream file presence as sufficient evidence for Imbuement REUSE.
changed_paths:
  - docs/agents/OTERYN_OAM_019_IMBUEMENTS_REVALIDATION.md
  - docs/agents/tasks/active/CAN-20260719-oteryn-imbuements-revalidation.md
blockers: []
validation:
  - command: OAM-019 fresh live-state and ownership preflight
    result: PASS
    evidence: Canary/Otheryn/upstream baselines pinned; Otheryn has no open PRs and no overlapping live Imbuement write ownership was found.
  - command: Canonical registry dependency gate
    result: PASS
    evidence: Imbuements depends on completed combat and player-persistence; protocol is an interaction boundary.
```

# Next-agent sequence

1. Keep Canary writes bounded to this report and task record until target proof is complete.
2. Verify final merged donor evidence and exact current blobs before target mutation.
3. Create a dedicated Otheryn target branch and draft PR using repository branch policy.
4. Run exact-head focused/full target gates and repair only evidence-backed defects.
5. Finalize Canary governance with `ci:final-gate`, then separate lifecycle and one-file durable program reconciliation.
6. Do not start OAM-020 until every OAM-019 stage is merged.
