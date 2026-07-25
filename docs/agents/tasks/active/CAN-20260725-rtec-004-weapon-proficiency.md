---
task_id: CAN-20260725-rtec-004-weapon-proficiency
program_id: CAN-PROGRAM-REAL-TIBIA-EVIDENCE-COLLECTION
coordination_id: RTEC-004-W1-WEAPON-PROFICIENCY
status: ready
agent: "GPT-5.6 Thinking"
branch: feat/rtec-004-weapon-proficiency-20260725
base_branch: main
created: 2026-07-25T20:18:00+02:00
updated: 2026-07-25T21:08:00+02:00
last_verified_commit: "e04123fff617aa6bb9b59f33533c12f5728a6be1"
risk: medium
related_issue: ""
related_pr: "930"
depends_on:
  - RTEC-004-WAVE-1
blocks: []
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260725-rtec-004-weapon-proficiency.md
    - docs/agents/real-tibia/evidence/modules/weapon-proficiency/**
  shared:
    - docs/agents/real-tibia/evidence/generated/EVIDENCE_INDEXES.json
  read_only:
    - docs/agents/programs/REAL_TIBIA_EVIDENCE_COLLECTION_PROGRAM.md
    - docs/agents/real-tibia/evidence/requests/**
    - docs/agents/real-tibia/registry/modules/weapon-proficiency.yaml
    - data/items/proficiencies.json
    - src/creatures/players/components/weapon_proficiency.*
    - tests/unit/players/components/weapon_proficiency_test.cpp
    - tools/ai-agent/weapon_proficiency_achievement_audit.py
    - tools/ai-agent/test_weapon_proficiency_achievement_audit.py
    - tools/e2e/**
modules_touched:
  - weapon-proficiency
reuses:
  - canary-real-tibia-evidence-record-v1
  - canary-real-tibia-owner-request-v1
  - canary-real-tibia-generated-indexes-v1
  - RTEC-002 vocations dossier structure
public_interfaces: []
cross_repo_tasks: []
---

# Goal

Collect one bounded, version-aware evidence package for Summer Update 2026 weapon-proficiency perk-slot modification and pending-level-up character-isolation behavior without changing gameplay, protocol, client, persistence or E2E owner paths.

# Delivered package

- `MODULE.md`, `BEHAVIOR_MODEL.md` and `DECISIONS.md`.
- `RT-WEAPON-PROFICIENCY-0001`: official manipulation lifecycle, `PROVEN`, `definition-found`, accepted.
- `RT-WEAPON-PROFICIENCY-0002`: current Canary static tree and player-scoped KV runtime path, `PROVEN`, `runtime-path-proven`, accepted.
- `RT-WEAPON-PROFICIENCY-0003`: pending level-up character-switch isolation, `UNKNOWN`, `definition-found`, accepted as an accurate unknown.
- Version history, module index, structured review and deterministic global index.

# Findings

- Official Summer Update 2026 permits up to two modified perk slots and defines refine, maximise, reshape and clear operations under resource, progression and protection-zone conditions.
- Current selected Canary paths load static proficiency trees, persist original-tree selections per player/weapon, normalise them and apply them through production code.
- The selected canonical paths do not model modified slots, dust costs, rolled replacement effects, refinement, maximisation, reshaping or clearing. This is a bounded selected-path finding, not an absolute repository-wide absence claim.
- Focused current tests cover mastery and achievement helpers, not manipulation or selected-perk persistence.
- The official 2026-07-14 character-switch display correction remains unproven for current Canary/OTClient; Player ownership does not prove client notification-state isolation.
- No owner request was created. Missing client/runtime dimensions remain explicit and do not duplicate `RTREQ-FEATURE-VOCATIONS-0001`.

# Validation and review

- The canonical generator and validator materialised the accepted records and exact deterministic index in CI artifact `8622861856` from run `30170815276`; all six exported file SHA-256 values were verified before repository integration.
- Temporary export and workflow scaffolding was removed before readiness.
- The final diff contains exactly eleven declared task, dossier and generated-index paths.
- Exact head `e04123fff617aa6bb9b59f33533c12f5728a6be1` passed:
  - Real Tibia Evidence Contracts run `30170995206`;
  - Agent Task Ownership run `30170995211`;
  - Real Tibia Module Registry run `30170995239`;
  - CI run `30170995303`;
  - Upstream Intelligence run `30170995200`.
- Structured review accepted the three records while preserving all `UNKNOWN` and nonclaim boundaries.
- `ci:final-gate` was applied before this final checkpoint commit.

# Acceptance criteria

- [x] Refresh exact Canary definitions, registration, persistence, tests and retained reports.
- [x] Pin exact official URLs/dates and selected statements.
- [x] Decompose perk-slot modification and character-switch isolation into bounded claims.
- [x] Create only valid module-specific dossier files, version history, index, records and review material.
- [x] Separate official release, client build, protocol, Canary, OTClient, data/assets and schema axes.
- [x] Record proof/nonproof boundaries, unknowns, freshness and invalidation triggers.
- [x] Create no duplicate owner request.
- [x] Regenerate and verify the shared factual index with the canonical tooling.
- [x] Complete structured review and accept the three bounded records.
- [x] Pass evidence, ownership, registry, CI and upstream checks on the clean pre-checkpoint head.
- [ ] Pass the renewed exact-final-head gate triggered by this checkpoint, then squash merge.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-25T21:08:00+02:00
head: e04123fff617aa6bb9b59f33533c12f5728a6be1
branch: feat/rtec-004-weapon-proficiency-20260725
pr: 930
status: ready
context_routes:
  - agent-governance
  - real-tibia-parity
owned_paths:
  - docs/agents/tasks/active/CAN-20260725-rtec-004-weapon-proficiency.md
  - docs/agents/real-tibia/evidence/generated/EVIDENCE_INDEXES.json
  - docs/agents/real-tibia/evidence/modules/weapon-proficiency/**
proven:
  - official manipulation and current Canary static-tree selection are separate bounded behaviors
  - three source-pinned records are accepted with explicit proof and nonproof boundaries
  - character-switch client isolation remains UNKNOWN
  - deterministic module and global indexes match the accepted record bytes
  - the final diff contains exactly eleven declared paths and no temporary scaffolding or owner implementation path
  - RTREQ-FEATURE-VOCATIONS-0001 remains unchanged and unclaimed
  - all clean pre-checkpoint workflows passed on e04123fff617aa6bb9b59f33533c12f5728a6be1
derived:
  - the dossier is complete without claiming full weapon-proficiency parity
  - no implementation or owner request is authorized by this evidence package
unknown:
  - exact maintained-client and protocol state for pending proficiency notifications
  - executed KV persistence rollback and physical-client behavior
conflicts: []
first_failure:
  marker: none
  evidence: all current clean pre-checkpoint checks are green; renewed exact-final-head checks are pending
rejected_hypotheses:
  - equate static original-tree selection with modified-slot manipulation: source state and operations differ
  - infer character-switch isolation from Player ownership: client and session state are unproven
  - treat selected-path findings as repository-wide absence: the records preserve bounded scope
changed_paths:
  - docs/agents/tasks/active/CAN-20260725-rtec-004-weapon-proficiency.md
  - docs/agents/real-tibia/evidence/generated/EVIDENCE_INDEXES.json
  - docs/agents/real-tibia/evidence/modules/weapon-proficiency/BEHAVIOR_MODEL.md
  - docs/agents/real-tibia/evidence/modules/weapon-proficiency/DECISIONS.md
  - docs/agents/real-tibia/evidence/modules/weapon-proficiency/EVIDENCE_INDEX.yaml
  - docs/agents/real-tibia/evidence/modules/weapon-proficiency/MODULE.md
  - docs/agents/real-tibia/evidence/modules/weapon-proficiency/VERSION_HISTORY.yaml
  - docs/agents/real-tibia/evidence/modules/weapon-proficiency/records/RT-WEAPON-PROFICIENCY-0001.yaml
  - docs/agents/real-tibia/evidence/modules/weapon-proficiency/records/RT-WEAPON-PROFICIENCY-0002.yaml
  - docs/agents/real-tibia/evidence/modules/weapon-proficiency/records/RT-WEAPON-PROFICIENCY-0003.yaml
  - docs/agents/real-tibia/evidence/modules/weapon-proficiency/reviews/RTEC-004-W1-REVIEW.md
validation:
  - command: canonical reviewed-package export and validation
    result: PASS
    evidence: run 30170815276 artifact 8622861856; six exported SHA-256 values verified
  - command: Real Tibia Evidence Contracts
    result: PASS
    evidence: run 30170995206 on e04123fff617aa6bb9b59f33533c12f5728a6be1
  - command: Agent Task Ownership and Real Tibia Module Registry
    result: PASS
    evidence: runs 30170995211 and 30170995239
  - command: CI and Upstream Intelligence
    result: PASS
    evidence: runs 30170995303 and 30170995200
  - command: renewed exact-final-head workflows after this checkpoint
    result: NOT_RUN
    evidence: pending final checkpoint head
blockers: []
next_action: Mark PR #930 ready and squash-merge its exact final head after every renewed final-gate workflow passes.
```
