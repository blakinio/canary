---
task_id: CAN-20260725-rtec-002-vocations-pilot
program_id: CAN-PROGRAM-REAL-TIBIA-EVIDENCE-COLLECTION
coordination_id: RTEC-002
status: implementing
agent: "GPT-5.6 Thinking"
branch: docs/rtec-002-vocations-pilot-20260725
base_branch: main
created: 2026-07-25T09:42:45+02:00
updated: 2026-07-25T10:05:00+02:00
last_verified_commit: "930e0a15767b7e5348bb36c679fa5e458a76f184"
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
- [x] Regenerate deterministic module/global factual indexes from the source records.
- [x] Include a structured independent review pass covering provenance, claim decomposition, proof boundaries, conflicts, unknowns and owner-request correctness.
- [x] Make no gameplay/runtime/client/protocol/database/map/datapack or owner-tooling changes.
- [ ] Relevant focused checks completed on the current head.
- [ ] Current-head GitHub checks verified.
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
- Open PRs #815, #559, #526 and #514 do not own the dossier, request, generated index or workflow paths changed here.

# Delivered evidence package

| Artifact | Result |
|---|---|
| `MODULE.md` | complete bounded dossier with explicit unknowns/nonclaims |
| `BEHAVIOR_MODEL.md` | source-visible registry, lookup, level-gain and promotion transition model |
| `DECISIONS.md` | selected authorities, exclusions and rejected overclaims |
| `RT-VOCATIONS-0001` | current official five-vocation table |
| `RT-VOCATIONS-0002` | Monk announcement and release chronology |
| `RT-VOCATIONS-0003` | exact Canary registry/XML source evidence |
| `RT-VOCATIONS-0004` | static official/Canary gain and promotion correspondence |
| `RT-VOCATIONS-0005` | explicit UNKNOWN runtime application claim |
| `RTREQ-FEATURE-VOCATIONS-0001` | one non-blocking feature-owner runtime proof request |
| `VERSION_HISTORY.yaml` | two separate-axis history entries |
| `EVIDENCE_INDEX.yaml` and global index | deterministic factual indexes as of 2026-07-25 |
| structured review | accepted for repository validation; no external human approval claim |

# Ownership and overlap check

- Exclusive: this task, one module dossier tree and one request.
- Shared: global generated index, programme closeout path and evidence workflow date.
- Read-only: schemas, validator, registry, source/runtime, TSD report and all external sources.
- The workflow date moved from 2026-07-24 to 2026-07-25 because the validator correctly rejects evidence dated after `as_of`.
- No broad module population, alternate registry, runtime test infrastructure or owner implementation was added.

# Current state

The first complete pilot corpus exists on PR #910: five evidence records, one active owner request, two version-history records and deterministic module/global indexes. Static official/Canary correspondence is bounded to the published HP/mana/capacity table and promotion names. Runtime level-gain and promotion application remain `UNKNOWN` pending owner evidence.

# Validation and CI

| Commit | Command/check/workflow | Result | Evidence/notes |
|---|---|---|---|
| `930e0a15767b7e5348bb36c679fa5e458a76f184` | preflight: main/open PRs/branches/program/registry | PASS | no existing RTEC-002 work; canonical `vocations` dependency-free |
| `755715fc726b8c7f781418dde31097591bab56a2` | corpus/index construction and workflow as-of integration | NOT_RUN | exact-head GitHub validation pending after this checkpoint |

Never write `PASS` without verification on the stated commit.

# Risks and compatibility

- Static evidence is capped at `registration-proven` and cannot become gameplay proof.
- The owner request is `ready-for-owner-triage`, non-blocking for this pilot and blocking only for promotion of the runtime claim.
- No runtime, database, protocol, client, map, datapack, proprietary artifact or production state is changed.
- Rollback is the closure of PR #910; no deployment rollback is required.

# Remaining work

1. Read exact current-head workflow failures, correct only grounded contract/index/ownership issues, then perform final review/gate/merge and lifecycle archival.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-25T10:05:00+02:00
head: 755715fc726b8c7f781418dde31097591bab56a2
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
proven:
  - current official manual defines five vocations and the bounded gain/promotion table
  - official Monk announcement and release dates are separately pinned
  - exact Canary baseline contains the XML-backed shared vocation registry and promotion relationships
  - deterministic source corpus contains five evidence records, one request and two history records
derived:
  - the selected official and Canary definitions correspond for the bounded gain and promotion fields
unknown:
  - executed level-gain and promotion application on the exact Canary baseline
  - promotion eligibility, payment, persistence, protocol, client, combat, spells and Wheel behavior
conflicts: []
first_failure:
  marker: pending-current-head-ci
  evidence: no current-head workflow result has been accepted yet
rejected_hypotheses:
  - static source correspondence proves runtime or gameplay parity
  - one module dossier proves whole-game parity or release readiness
changed_paths:
  - .github/workflows/real-tibia-evidence.yml
  - docs/agents/tasks/active/CAN-20260725-rtec-002-vocations-pilot.md
  - docs/agents/real-tibia/evidence/generated/EVIDENCE_INDEXES.json
  - docs/agents/real-tibia/evidence/modules/vocations/**
  - docs/agents/real-tibia/evidence/requests/feature/RTREQ-FEATURE-VOCATIONS-0001.yaml
validation:
  - command: fresh GitHub preflight
    result: PASS
    evidence: main/open PR/branch/program/registry state verified
  - command: exact current-head GitHub workflows
    result: NOT_RUN
    evidence: checkpoint commit will trigger validation
blockers: []
next_action: Inspect exact current-head ownership, schema, corpus and deterministic-index workflow results; fix only verified failures.
```

# Handoff

Read this checkpoint, PR #910, the v1 RTEC contracts, canonical `vocations` registry record, current source and the generated indexes. Do not restart module selection, create another registry, populate other modules or edit runtime/owner paths.

# Completion

- Final status: active
- PR: #910
- Merge commit: pending
- Program record updated: pending post-merge closeout
- Catalogue/changelog: no change expected
- Archived at: pending
