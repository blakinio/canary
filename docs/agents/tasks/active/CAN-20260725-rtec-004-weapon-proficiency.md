---
task_id: CAN-20260725-rtec-004-weapon-proficiency
program_id: CAN-PROGRAM-REAL-TIBIA-EVIDENCE-COLLECTION
coordination_id: RTEC-004-W1-WEAPON-PROFICIENCY
status: validating
agent: "GPT-5.6 Thinking"
branch: feat/rtec-004-weapon-proficiency-20260725
base_branch: main
created: 2026-07-25T20:18:00+02:00
updated: 2026-07-25T20:35:00+02:00
last_verified_commit: "6ea899e6a2e2dd097a519ea6da87808182340a3a"
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

- `MODULE.md` with explicit scope and proof boundaries.
- `BEHAVIOR_MODEL.md` separating current static-tree selection from official modified-slot manipulation.
- `DECISIONS.md` preserving the non-equivalence and client-isolation boundary.
- three records:
  - `RT-WEAPON-PROFICIENCY-0001`: official manipulation lifecycle, `PROVEN`, `definition-found`;
  - `RT-WEAPON-PROFICIENCY-0002`: current Canary static tree and player-scoped KV runtime path, `PROVEN`, `runtime-path-proven`;
  - `RT-WEAPON-PROFICIENCY-0003`: pending level-up character-switch isolation, `UNKNOWN`, `definition-found`.
- module evidence index, version history and pending structured-review checklist.

# Findings

- Official Summer Update 2026 permits up to two modified perk slots and defines refine, maximise, reshape and clear operations under resource, progression and protection-zone conditions.
- Current selected Canary paths load static proficiency trees, persist original-tree selections per player/weapon, normalise them and apply them through production code.
- The selected canonical paths do not model modified slots, dust costs, rolled replacement effects, refinement, maximisation, reshaping or clearing. This is a bounded selected-path finding, not an absolute repository-wide absence claim.
- Focused current tests cover mastery and achievement helpers, not manipulation or selected-perk persistence.
- The official 2026-07-14 character-switch display correction remains unproven for current Canary/OTClient; Player ownership does not prove client notification-state isolation.
- No owner request was created because the package can remain dossier-complete with the missing client/runtime dimensions explicit; the coordinator may nominate a later owner package without duplicating the active vocations request.

# Acceptance criteria

- [x] Refresh exact Canary definitions, registration, persistence, tests and retained reports.
- [x] Pin exact official URLs/dates and selected statements.
- [x] Decompose perk-slot modification and character-switch isolation into bounded claims.
- [x] Create only valid module-specific dossier files, version history, index, records and review material.
- [x] Separate official release, client build, protocol, Canary, OTClient, data/assets and schema axes.
- [x] Record proof/nonproof boundaries, unknowns, freshness and invalidation triggers.
- [x] Create no duplicate owner request.
- [ ] Pass exact-head evidence, deterministic-index, ownership and applicable CI gates.
- [ ] Complete structured review and accept or revise the three records.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-25T20:35:00+02:00
head: 6ea899e6a2e2dd097a519ea6da87808182340a3a
branch: feat/rtec-004-weapon-proficiency-20260725
pr: 930
status: validating
context_routes:
  - agent-governance
  - real-tibia-parity
owned_paths:
  - docs/agents/tasks/active/CAN-20260725-rtec-004-weapon-proficiency.md
  - docs/agents/real-tibia/evidence/modules/weapon-proficiency/**
  - docs/agents/real-tibia/evidence/generated/EVIDENCE_INDEXES.json
proven:
  - official 2026 manipulation has a distinct two-slot resource and operation lifecycle
  - current selected Canary paths implement static tree selection player-scoped per-weapon KV normalisation and perk application
  - the selected current component does not model the official manipulation lifecycle
  - focused tests do not cover manipulation or selected-perk persistence
  - official character-switch defect and correction date are source-pinned
  - current Canary and maintained-client character-switch conformance is unproven
  - three evidence records module index version history and review material are present on PR 930
derived:
  - setSelectedPerk is not equivalent to official modified-slot manipulation
  - Player-owned server state cannot establish maintained-client notification isolation
unknown:
  - exact maintained-client and protocol state for pending proficiency notifications
  - executed KV persistence and rollback behavior
  - exact-head corpus and deterministic global-index result
  - structured review outcome
conflicts: []
first_failure:
  marker: exact-head-validation-pending
  evidence: Real Tibia Evidence Contracts run 30169850402 and related checks are queued on 6ea899e6a2e2dd097a519ea6da87808182340a3a
rejected_hypotheses:
  - implement or test the feature in this Collector task: owner implementation paths remain read-only
  - equate static original-tree selection with modified-slot manipulation: source state and operations differ
  - infer character-switch isolation from Player ownership: client and session state are unproven
changed_paths:
  - docs/agents/tasks/active/CAN-20260725-rtec-004-weapon-proficiency.md
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
  - command: official Tibia source verification 2026-06-22 2026-07-13 and 2026-07-14
    result: PASS
    evidence: exact official URLs and publication dates retained in records
  - command: bounded Canary source data and test trace at 124b029d1a2498a64fa6612b16efa386b8786a83
    result: PASS
    evidence: exact paths and symbols retained in RT-WEAPON-PROFICIENCY-0002 and 0003
  - command: GitHub exact-head workflows on 6ea899e6a2e2dd097a519ea6da87808182340a3a
    result: NOT_RUN
    evidence: queued at checkpoint time
blockers: []
next_action: Inspect Real Tibia Evidence Contracts run 30169850402 on the current head, fix the first contract failure, and regenerate the shared global index through the coordinator-owned integration path if required.
```
