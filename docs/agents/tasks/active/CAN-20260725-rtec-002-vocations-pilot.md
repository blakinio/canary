---
task_id: CAN-20260725-rtec-002-vocations-pilot
program_id: CAN-PROGRAM-REAL-TIBIA-EVIDENCE-COLLECTION
coordination_id: RTEC-002
status: review
agent: "GPT-5.6 Thinking"
branch: docs/rtec-002-vocations-pilot-20260725
base_branch: main
created: 2026-07-25T09:42:45+02:00
updated: 2026-07-25T10:30:00+02:00
last_verified_commit: "4ed45d88c729c669356fe23d050edeb0b059ca89"
risk: medium
related_issue: ""
related_pr: "910"
depends_on:
  - RTEC-001
blocks:
  - RTEC-003
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260725-rtec-002-vocations-pilot.md
    - docs/agents/real-tibia/evidence/modules/vocations/**
    - docs/agents/real-tibia/evidence/requests/feature/RTREQ-FEATURE-VOCATIONS-0001.yaml
  shared:
    - docs/agents/real-tibia/evidence/generated/EVIDENCE_INDEXES.json
    - docs/agents/programs/REAL_TIBIA_EVIDENCE_COLLECTION_PROGRAM.md
    - .github/workflows/real-tibia-evidence.yml
    - tools/agents/real_tibia_evidence_test_support.py
    - tools/agents/test_real_tibia_evidence_lifecycle.py
  read_only:
    - AGENTS.md
    - docs/agents/REPOSITORY_MAP.md
    - docs/agents/CONTEXT_ROUTING.md
    - docs/agents/REAL_TIBIA_EVIDENCE_SOURCES.md
    - docs/agents/REAL_TIBIA_PARITY_PLAYBOOK.md
    - docs/ai-agent/REAL_TIBIA_EVIDENCE_COLLECTOR_ARCHITECTURE.md
    - docs/agents/real-tibia/registry/modules/vocations.yaml
    - docs/agents/real-tibia/registry/sources.yaml
    - docs/agents/real-tibia/registry/versions.yaml
    - docs/agents/real-tibia/evidence/schemas/**
    - docs/agents/templates/REAL_TIBIA_EVIDENCE_RECORD.yaml
    - docs/agents/templates/REAL_TIBIA_EVIDENCE_REQUEST.yaml
    - tools/agents/real_tibia_evidence.py
    - tools/agents/real_tibia_evidence_lib.py
    - tools/agents/test_real_tibia_evidence.py
    - src/creatures/players/vocations/vocation.*
    - data/XML/vocations.xml
    - docs/agents/real-tibia/TSD_003_ACCOUNT_CHARACTER_PROGRESSION_REPORT.md
modules_touched:
  - vocations
  - real-tibia-evidence-collection
reuses:
  - canary-real-tibia-evidence-record-v1
  - canary-real-tibia-owner-request-v1
  - canary-real-tibia-module-evidence-index-v1
  - canary-real-tibia-version-history-v1
  - canary-real-tibia-generated-indexes-v1
  - canary-real-tibia-module-registry
public_interfaces: []
cross_repo_tasks: []
---

# Goal

Prove the complete RTEC collection/review workflow on exactly one canonical low-coupling module by publishing a source-pinned `vocations` dossier, bounded evidence records, version history, deterministic indexes and one genuine feature-owner proof request without changing gameplay or owner implementation paths.

# Acceptance criteria

- [x] Create a complete `vocations` dossier whose required sections are evidence-backed or explicitly marked `UNKNOWN`, `CONFLICT`, `not-applicable` or `blocked-by-owner-request`.
- [x] Publish bounded machine-readable evidence for official vocation identity/purpose and exact current Canary vocation definitions on a pinned commit.
- [x] Publish version history without compressing release/build/protocol/commit axes into one generic version.
- [x] Create exactly one feature-owner request only for proof that cannot be established by static Collector evidence.
- [x] Regenerate deterministic module/global factual indexes with the repository generator.
- [x] Include a structured independent review pass covering provenance, claim decomposition, proof boundaries, conflicts, unknowns and owner-request correctness.
- [x] Make no gameplay/runtime/client/protocol/database/map/datapack or owner-tooling changes.
- [x] Relevant focused checks completed on validated implementation head `4ed45d88c729c669356fe23d050edeb0b059ca89`.
- [ ] Exact current-head GitHub checks verified after cleanup/checkpoint commits.
- [x] Module catalogue impact handled: no reusable interface change.
- [x] Documentation/changelog impact handled: programme queue changes only after feature merge; no behavior changelog entry.
- [x] Cross-repository impact handled: external repositories and official sources remain read-only.
- [ ] Autonomous merge gate satisfied.

# Confirmed context

- Base: `main@930e0a15767b7e5348bb36c679fa5e458a76f184`.
- Draft PR: #910.
- RTEC-001 contracts, validator and lifecycle are merged and archived.
- The canonical `vocations` record has no hard dependency edges and confines current implementation discovery to `vocation.*` and `vocations.xml`.
- Combat formulas, spell/weapon eligibility, Wheel/client presentation, protocol, persistence and physical-client execution are outside this pilot.
- Open PRs #815, #559, #526 and #514 do not own the dossier, request, generated index, fixture or workflow paths changed here.

# Delivered evidence package

| Artifact | Result |
|---|---|
| `MODULE.md` | complete bounded dossier with explicit unknowns/nonclaims |
| `BEHAVIOR_MODEL.md` | source-visible registry, lookup, level-gain and promotion transition model |
| `DECISIONS.md` | selected authorities, exclusions and rejected overclaims |
| `RT-VOCATIONS-0001` | current official five-vocation table observation |
| `RT-VOCATIONS-0002` | Monk announcement and release chronology |
| `RT-VOCATIONS-0003` | exact Canary registry/XML source evidence |
| `RT-VOCATIONS-0004` | static official/Canary gain and promotion correspondence |
| `RT-VOCATIONS-0005` | explicit UNKNOWN runtime application claim |
| `RTREQ-FEATURE-VOCATIONS-0001` | one non-blocking feature-owner runtime proof request |
| `VERSION_HISTORY.yaml` | two separate-axis history entries |
| generated indexes | repository-generated deterministic module/global indexes as of 2026-07-25 |
| structured review | accepted for repository validation; no external human approval claim |

# Ownership and overlap check

- Exclusive: this task, one module dossier tree and one request.
- Shared: global generated index, programme closeout path, evidence workflow date and the two date-relative evidence test fixtures.
- Read-only: schemas, validator, registry, source/runtime, TSD report and all external sources.
- The workflow and fixture `as_of` moved from 2026-07-24 to 2026-07-25 because the validator correctly rejects evidence dated after `as_of`.
- The future-date regression test now derives its future date from `AS_OF`, preserving the tested invariant.
- No broad module population, alternate registry, runtime test infrastructure or owner implementation was added.
- The temporary diagnostic workflow was removed; it is absent from the final net diff.

# Current state

The complete pilot corpus validates: five evidence records, one active owner request, two version-history records and deterministic module/global indexes. Static official/Canary correspondence is bounded to the published HP/mana/capacity table and promotion names. Runtime level-gain and promotion application remain `UNKNOWN` pending owner evidence.

# Validation and CI

| Commit | Command/check/workflow | Result | Evidence/notes |
|---|---|---|---|
| `930e0a15767b7e5348bb36c679fa5e458a76f184` | preflight: main/open PRs/branches/program/registry | PASS | no existing RTEC-002 work; canonical `vocations` dependency-free |
| `4ed45d88c729c669356fe23d050edeb0b059ca89` | Real Tibia Evidence Contracts | PASS | compile, 27 focused tests, Draft 2020-12, 62-module registry, corpus validation, deterministic generate/check and show-index |
| `4ed45d88c729c669356fe23d050edeb0b059ca89` | CI / Agent Task Ownership / Module Registry / Upstream Intelligence | PASS | all required workflows completed successfully |
| current cleanup/checkpoint head | exact current-head workflows | NOT_RUN | must be reverified before final gate |

Never write `PASS` without verification on the stated commit.

# Review findings

- The live official manual URL has no source-pinned publication date; the evidence retains URL, author and observation date without inventing publication metadata.
- The official/Canary comparison is `DERIVED` and capped at `registration-proven`.
- The runtime claim remains `UNKNOWN` and links to one feature-owner request.
- The generator-produced global input digest is `8986f61407977df1ecb394c2568245d917cc8a185a8e96c0cf5e994d4a01aac0`.
- No review threads or submitted review blockers were present at the implementation checkpoint.

# Risks and compatibility

- Static evidence cannot become gameplay proof.
- The owner request is `ready-for-owner-triage`, non-blocking for this pilot and blocking only for promotion of the runtime claim.
- No runtime, database, protocol, client, map, datapack, proprietary artifact or production state is changed.
- Rollback is the closure of PR #910; no deployment rollback is required.

# Remaining work

1. Verify exact current-head checks, apply final gate, make one final checkpoint commit, then make no further commits after the green exact-head gate.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-25T10:30:00+02:00
head: 99e69ddcbf1b20c7d700b8fa01d11495ac11c572
branch: docs/rtec-002-vocations-pilot-20260725
pr: 910
status: validating
context_routes:
  - real-tibia-evidence-collection
  - documentation-and-governance
owned_paths:
  - docs/agents/tasks/active/CAN-20260725-rtec-002-vocations-pilot.md
  - docs/agents/real-tibia/evidence/modules/vocations/**
  - docs/agents/real-tibia/evidence/requests/feature/RTREQ-FEATURE-VOCATIONS-0001.yaml
  - docs/agents/real-tibia/evidence/generated/EVIDENCE_INDEXES.json
  - docs/agents/programs/REAL_TIBIA_EVIDENCE_COLLECTION_PROGRAM.md
  - .github/workflows/real-tibia-evidence.yml
  - tools/agents/real_tibia_evidence_test_support.py
  - tools/agents/test_real_tibia_evidence_lifecycle.py
proven:
  - current official manual defines five vocations and the bounded gain/promotion table
  - official Monk announcement and release dates are separately pinned
  - exact Canary baseline contains the XML-backed shared vocation registry and promotion relationships
  - repository validation accepts five evidence records, one request and two history records
  - deterministic repository generator accepts the committed indexes
derived:
  - the selected official and Canary definitions correspond for the bounded gain and promotion fields
unknown:
  - executed level-gain and promotion application on the exact Canary baseline
  - promotion eligibility, payment, persistence, protocol, client, combat, spells and Wheel behavior
conflicts: []
first_failure:
  marker: resolved-generated-index-drift
  evidence: repository generator output accepted at 4ed45d88c729c669356fe23d050edeb0b059ca89
rejected_hypotheses:
  - static source correspondence proves runtime or gameplay parity
  - one module dossier proves whole-game parity or release readiness
changed_paths:
  - .github/workflows/real-tibia-evidence.yml
  - docs/agents/tasks/active/CAN-20260725-rtec-002-vocations-pilot.md
  - docs/agents/real-tibia/evidence/generated/EVIDENCE_INDEXES.json
  - docs/agents/real-tibia/evidence/modules/vocations/**
  - docs/agents/real-tibia/evidence/requests/feature/RTREQ-FEATURE-VOCATIONS-0001.yaml
  - tools/agents/real_tibia_evidence_test_support.py
  - tools/agents/test_real_tibia_evidence_lifecycle.py
validation:
  - command: fresh GitHub preflight
    result: PASS
    evidence: main/open PR/branch/program/registry state verified
  - command: Real Tibia Evidence Contracts at 4ed45d88c729c669356fe23d050edeb0b059ca89
    result: PASS
    evidence: 27 tests, schemas, registry, corpus and deterministic indexes passed
  - command: exact current-head GitHub workflows
    result: NOT_RUN
    evidence: cleanup/checkpoint head requires verification
blockers: []
next_action: Verify exact current-head workflows, apply ci:final-gate before the final checkpoint commit and do not commit after the green final-head gate.
```

# Handoff

Read this checkpoint, PR #910, the v1 RTEC contracts, canonical `vocations` registry record, current source and generated indexes. Do not restart module selection, create another registry, populate other modules or edit runtime/owner paths.

# Completion

- Final status: active
- PR: #910
- Merge commit: pending
- Program record updated: pending post-merge closeout
- Catalogue/changelog: no change expected
- Archived at: pending
