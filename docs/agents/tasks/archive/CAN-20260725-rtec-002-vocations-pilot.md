---
task_id: CAN-20260725-rtec-002-vocations-pilot
program_id: CAN-PROGRAM-REAL-TIBIA-EVIDENCE-COLLECTION
coordination_id: RTEC-002
status: completed
agent: "GPT-5.6 Thinking"
branch: docs/rtec-002-vocations-pilot-20260725
base_branch: main
created: 2026-07-25T09:42:45+02:00
updated: 2026-07-25T08:52:56Z
last_verified_commit: "fe35eda9c14766c80d13c161d38ce13a1db6e0d5"
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
completed: 2026-07-25T08:52:56Z
---

# Goal

Prove the complete RTEC collection/review workflow on one canonical low-coupling module by publishing a source-pinned `vocations` dossier, bounded evidence records, separate-axis history, deterministic indexes and one genuine feature-owner proof request without changing implementation paths.

# Acceptance criteria

- [x] Complete one canonical module dossier with explicit evidence, `UNKNOWN` and nonclaim boundaries.
- [x] Publish five validated evidence records and two validated version-history entries.
- [x] Publish exactly one non-blocking feature-owner request for missing runtime proof.
- [x] Generate deterministic module/global indexes using repository tooling.
- [x] Complete a structured review pass without claiming external human approval.
- [x] Preserve all runtime, gameplay, client, protocol, database, map, datapack and owner-tool paths as read-only.
- [x] Advance evidence `as_of` fixtures to 2026-07-25 while retaining a relative future-date regression test.
- [x] Verify focused contracts, ownership, registry, upstream and CI on exact head `3c832c018b10882bb3a89af0c5d26fa697b35c29`.
- [x] Verify no review threads, submitted review blockers or overlapping `main` drift.
- [ ] Verify the exact final checkpoint head after the protected `ci:final-gate` run; no further commit is permitted after it turns green.

# Delivered package

| Artifact | Factual result |
|---|---|
| `MODULE.md` | bounded dossier with all applicable sections |
| `BEHAVIOR_MODEL.md` | source-visible registry/lookup model and explicit runtime gaps |
| `DECISIONS.md` | authorities, exclusions and rejected overclaims |
| `RT-VOCATIONS-0001` | current official five-vocation gain/promotion table observation |
| `RT-VOCATIONS-0002` | Monk announcement and release chronology |
| `RT-VOCATIONS-0003` | exact Canary XML-backed registry evidence |
| `RT-VOCATIONS-0004` | static official/Canary correspondence, `DERIVED` and capped at `registration-proven` |
| `RT-VOCATIONS-0005` | runtime level-gain/promotion application retained as `UNKNOWN` |
| `RTREQ-FEATURE-VOCATIONS-0001` | one feature-owner runtime-proof request, ready for triage |
| `VERSION_HISTORY.yaml` | separate official and Canary version axes |
| generated indexes | five evidence records, one request and two history records as of 2026-07-25 |

# Evidence boundaries

- The official manual observation proves the public five-vocation table and promotion titles, not hidden implementation or Canary execution.
- Official news separately proves Monk announcement on 2025-02-10 and release on 2025-04-08.
- Current Canary source at `930e0a15767b7e5348bb36c679fa5e458a76f184` proves registry/XML definitions and code paths, not executed character-state transitions.
- Static correspondence does not prove gameplay, promotion authorization/payment, persistence, protocol/client behavior, combat, spells, weapons, Wheel or physical-client parity.
- The live official manual has no source-pinned publication date; the record preserves its URL, author and 2026-07-25 observation without inventing publication metadata.

# Ownership and overlap

- Exclusive writes are limited to this task, `evidence/modules/vocations/**` and one `RTREQ-FEATURE-*` request.
- Shared integration is limited to the global factual index, evidence workflow date and two date-relative test fixtures.
- Temporary diagnostics were removed and are absent from the 17-file net diff.
- `main` drift after the selected base consists only of the unrelated OAM-046 active-task record and does not overlap this package.

# Validation

| Head | Check | Result |
|---|---|---|
| `4ed45d88c729c669356fe23d050edeb0b059ca89` | 27 tests, Draft 2020-12, registry, corpus, deterministic generator/check, show-index | PASS |
| `4ed45d88c729c669356fe23d050edeb0b059ca89` | CI, ownership, registry, upstream | PASS |
| `3c832c018b10882bb3a89af0c5d26fa697b35c29` | CI, ownership, Real Tibia Evidence Contracts, registry, upstream | PASS |
| final checkpoint head | protected final gate | NOT_RUN at commit creation |

Never promote `NOT_RUN` to `PASS` without exact-head verification.

# Remaining work

The `ci:final-gate` label is already applied. This is the final checkpoint commit. Do not create another commit after the exact final-head gate is green. Then mark PR ready, squash-merge with expected-head protection and verify lifecycle archival before any RTEC-003 work.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-25T10:40:00+02:00
head: 3c832c018b10882bb3a89af0c5d26fa697b35c29
branch: docs/rtec-002-vocations-pilot-20260725
pr: 910
status: ready
context_routes:
  - real-tibia-evidence-collection
  - documentation-and-governance
owned_paths:
  - docs/agents/tasks/active/CAN-20260725-rtec-002-vocations-pilot.md
  - docs/agents/real-tibia/evidence/modules/vocations/**
  - docs/agents/real-tibia/evidence/requests/feature/RTREQ-FEATURE-VOCATIONS-0001.yaml
  - docs/agents/real-tibia/evidence/generated/EVIDENCE_INDEXES.json
  - .github/workflows/real-tibia-evidence.yml
  - tools/agents/real_tibia_evidence_test_support.py
  - tools/agents/test_real_tibia_evidence_lifecycle.py
proven:
  - five evidence records, one owner request and two history records validate
  - repository generator accepts the committed module and global indexes
  - current official and Canary source observations are independently pinned
  - exact pre-final head 3c832c018b10882bb3a89af0c5d26fa697b35c29 is green
  - no review blockers or overlapping main drift exist
derived:
  - selected official and Canary definitions correspond for bounded gain and promotion fields
unknown:
  - executed level-gain and promotion application on the exact Canary baseline
  - promotion eligibility, payment, persistence, protocol, client, combat, spells and Wheel behavior
conflicts: []
first_failure:
  marker: resolved-generated-index-drift
  evidence: repository-generated digest 8986f61407977df1ecb394c2568245d917cc8a185a8e96c0cf5e994d4a01aac0
rejected_hypotheses:
  - static correspondence proves runtime or gameplay parity
  - one dossier proves whole-game parity or release readiness
changed_paths:
  - .github/workflows/real-tibia-evidence.yml
  - docs/agents/tasks/active/CAN-20260725-rtec-002-vocations-pilot.md
  - docs/agents/real-tibia/evidence/generated/EVIDENCE_INDEXES.json
  - docs/agents/real-tibia/evidence/modules/vocations/**
  - docs/agents/real-tibia/evidence/requests/feature/RTREQ-FEATURE-VOCATIONS-0001.yaml
  - tools/agents/real_tibia_evidence_test_support.py
  - tools/agents/test_real_tibia_evidence_lifecycle.py
validation:
  - command: Real Tibia Evidence Contracts at 3c832c018b10882bb3a89af0c5d26fa697b35c29
    result: PASS
    evidence: all contract, schema, registry, corpus and index stages succeeded
  - command: CI and ownership at 3c832c018b10882bb3a89af0c5d26fa697b35c29
    result: PASS
    evidence: all required workflows succeeded
  - command: protected exact final-head gate
    result: NOT_RUN
    evidence: this commit triggers the final run
blockers: []
next_action: Verify the exact final checkpoint head, make no further commits, mark PR ready and squash-merge with expected-head protection.
```

# Completion

- Final status: ready
- PR: #910
- Merge commit: pending
- Program closeout: pending after feature/lifecycle merge
- Catalogue/changelog: no change required
- Archive: pending post-merge lifecycle

## Automated lifecycle completion

- Feature PR: #910.
- Feature head: `a3ff7430e190a61ab2c6465b4ba1daa4526d6743`.
- Merge commit: `fe35eda9c14766c80d13c161d38ce13a1db6e0d5`.
- Merged at: `2026-07-25T08:52:56Z`.
- This record was moved from `tasks/active` by the post-merge lifecycle automation.
