---
task_id: CAN-20260725-rtec-002-vocations-pilot
program_id: CAN-PROGRAM-REAL-TIBIA-EVIDENCE-COLLECTION
coordination_id: RTEC-002
status: planned
agent: "GPT-5.6 Thinking"
branch: docs/rtec-002-vocations-pilot-20260725
base_branch: main
created: 2026-07-25T09:42:45+02:00
updated: 2026-07-25T09:42:45+02:00
last_verified_commit: "930e0a15767b7e5348bb36c679fa5e458a76f184"
risk: medium
related_issue: ""
related_pr: ""
depends_on:
  - RTEC-001
blocks:
  - RTEC-003
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260725-rtec-002-vocations-pilot.md
    - docs/agents/real-tibia/evidence/modules/vocations/**
    - docs/agents/real-tibia/evidence/requests/feature/RTR-VOCATIONS-0001.yaml
  shared:
    - docs/agents/real-tibia/evidence/generated/EVIDENCE_INDEXES.json
    - docs/agents/programs/REAL_TIBIA_EVIDENCE_COLLECTION_PROGRAM.md
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

- [ ] Create a complete `vocations` dossier whose required sections are evidence-backed or explicitly marked `UNKNOWN`, `CONFLICT`, `not-applicable` or `blocked-by-owner-request`.
- [ ] Publish bounded machine-readable evidence for official vocation identity/purpose and exact current Canary vocation definitions on a pinned commit.
- [ ] Publish version history without compressing release/build/protocol/commit axes into one generic version.
- [ ] Create exactly one feature-owner request only for proof that cannot be established by static Collector evidence.
- [ ] Regenerate deterministic module/global factual indexes from validated records.
- [ ] Include an independent review record covering provenance, claim decomposition, proof boundaries, conflicts, unknowns and owner-request correctness.
- [ ] Make no gameplay/runtime/client/protocol/database/map/datapack or owner-tooling changes.
- [ ] Relevant focused checks completed.
- [ ] Current-head GitHub checks verified.
- [ ] Module catalogue impact handled: no reusable interface change expected.
- [ ] Documentation/changelog impact handled: programme queue updated only at closeout; no changelog entry unless behavior changes.
- [ ] Cross-repository impact handled: all external repositories and official sources remain read-only.
- [ ] Autonomous merge gate satisfied.

# Confirmed context

- Current base is `main@930e0a15767b7e5348bb36c679fa5e458a76f184`.
- RTEC-001 contracts and validator merged in PR #897, lifecycle archived in PR #908, programme state reconciled in PR #909.
- No open PR or branch matching RTEC-002 existed at preflight.
- The canonical `vocations` registry record has no `depends_on` entries and confines current implementation discovery to `src/creatures/players/vocations/vocation.*` and `data/XML/vocations.xml`.
- Combat formula parity, spell/weapon eligibility and Wheel/client presentation are excluded from this pilot.
- Open PRs #815, #559, #526 and #514 were inspected; none owns the new dossier/request paths. Their authentication, transport, security-audit and lifecycle scopes remain independent and read-only.
- External official material may prove public identity, purpose and chronology but not hidden formulas or current Canary runtime behavior.

# Existing work to reuse

| Module/task/PR | Reuse | Evidence/path | Why it fits |
|---|---|---|---|
| RTEC-001 / PR #897 | v1 schemas, validator, generator and tests | `docs/agents/real-tibia/evidence/**`, `tools/agents/real_tibia_evidence*.py` | Canonical machine-readable contracts for the pilot. |
| Real Tibia module registry | canonical module ID, scope and source requirements | `docs/agents/real-tibia/registry/modules/vocations.yaml` | Prevents a duplicate or 63rd module. |
| TSD-003 | prior bounded Canary inventory | `docs/agents/real-tibia/TSD_003_ACCOUNT_CHARACTER_PROGRESSION_REPORT.md` | Reusable discovery evidence, subject to current-main refresh. |
| Current Canary vocation implementation | exact source definitions | `src/creatures/players/vocations/vocation.*`, `data/XML/vocations.xml` | Primary authority for current target implementation only. |

# Ownership and overlap check

- Program record: `CAN-PROGRAM-REAL-TIBIA-EVIDENCE-COLLECTION`; RTEC-002 was `planned` after PR #909.
- Open PRs inspected: #815, #559, #526, #514.
- Active tasks inspected: task records referenced by those four open PRs; no exact dossier/request path collision identified.
- Ownership checker result: pending first branch CI.
- Exclusive claims: this task record, `evidence/modules/vocations/**`, and one feature request ID/path.
- Shared claims: generated factual index and programme queue closeout only.
- Read-only dependencies: registry, schemas/templates/tooling, current Canary source, TSD report and external evidence.
- Overlaps: source-level thematic interaction with character progression/combat/spells/Wheel, but no write ownership and those behaviors are expressly excluded.
- Resolution: keep all source/owner paths read-only and record missing proof as one owner request.

# Current state

The pilot is claimed. No dossier or evidence record has been created yet.

# Plan

1. Pin current Canary source evidence and official vocation material.
2. Decompose bounded claims and explicit unknowns.
3. Create the dossier, behavior model, version history, decisions, evidence records and one owner request.
4. Generate and validate deterministic indexes.
5. Add independent review evidence, update the checkpoint, run exact-head CI/final gate and merge.

# Work log

## 2026-07-25T09:42:45+02:00

- Changed: claimed the bounded RTEC-002 `vocations` pilot on a dedicated branch.
- Learned: `vocations` has zero hard registry dependencies and narrow current-source paths.
- Failed/blocked: local network clone is unavailable; repository reads/writes use the GitHub connector and validation will run in repository CI.
- Result: ready to open an early draft PR and begin source-pinned collection.

# Decisions

| Decision | Reason/evidence | ADR |
|---|---|---|
| Select `vocations` for RTEC-002 | Zero hard dependencies, narrow source paths, explicit exclusions and available official/current-source evidence make it lower-coupling than persistence/protocol/map/economy candidates. | none |
| Keep runtime and interacting modules read-only | The Collector owns evidence, not implementation; missing behavior proof becomes an owner request. | none |

# Files and interfaces

| Path/interface/config/schema | Ownership mode | Purpose | Status |
|---|---|---|---|
| `docs/agents/real-tibia/evidence/modules/vocations/**` | exclusive | Pilot dossier, records, history and review | planned |
| `docs/agents/real-tibia/evidence/requests/feature/RTR-VOCATIONS-0001.yaml` | exclusive | One genuine owner-proof request | planned |
| `docs/agents/real-tibia/evidence/generated/EVIDENCE_INDEXES.json` | shared | Deterministic factual integration | planned |
| v1 RTEC contracts | read_only/reused | Validation and interchange | merged |

# Validation and CI

| Commit | Command/check/workflow | Result | Evidence/notes |
|---|---|---|---|
| `930e0a15767b7e5348bb36c679fa5e458a76f184` | preflight: main/open PRs/branches/program/registry | PASS | no existing RTEC-002 task/PR/branch; `vocations` canonical and dependency-free |
| branch head | Agent Task Ownership | NOT_RUN | runs after draft PR opens |
| branch head | Real Tibia Evidence Contracts | NOT_RUN | runs after corpus files exist |

Never write `passed` without verification on the stated commit.

# Failed approaches and dead ends

- A local sparse clone could not resolve `github.com`; no local repository state was used as evidence.

# Risks and compatibility

- Runtime: no runtime changes; static evidence must not be promoted to gameplay proof.
- Data/migration: no database or datapack changes.
- Security: no credentials, captures, binaries or proprietary packages are committed.
- Backward compatibility: no public/runtime interface changes.
- Cross-repo rollout: none; all external repositories are read-only.
- Rollback: close the draft PR and delete its branch; no production state is touched.

# Remaining work

1. Open the early draft PR and pin exact current-source/official evidence for bounded vocation claims.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-25T09:42:45+02:00
head: UNKNOWN
branch: docs/rtec-002-vocations-pilot-20260725
pr: none
status: investigating
context_routes:
  - real-tibia-evidence-collection
  - documentation-and-governance
owned_paths:
  - docs/agents/tasks/active/CAN-20260725-rtec-002-vocations-pilot.md
  - docs/agents/real-tibia/evidence/modules/vocations/**
  - docs/agents/real-tibia/evidence/requests/feature/RTR-VOCATIONS-0001.yaml
  - docs/agents/real-tibia/evidence/generated/EVIDENCE_INDEXES.json
  - docs/agents/programs/REAL_TIBIA_EVIDENCE_COLLECTION_PROGRAM.md
proven:
  - main base is 930e0a15767b7e5348bb36c679fa5e458a76f184
  - RTEC-001 is merged and archived
  - no open RTEC-002 PR or branch existed at preflight
  - canonical vocations has zero hard dependencies and narrow source paths
  - open PRs 815, 559, 526 and 514 do not own the new dossier/request paths
derived:
  - vocations is a lower-coupling pilot than modules requiring protocol, map, persistence or economy ownership
unknown:
  - exact current official vocation publication set and chronology to cite
  - exact current Canary values and symbols on the selected base
  - which single missing proof genuinely requires a feature-owner request
conflicts: []
first_failure:
  marker: none
  evidence: no validation run yet
rejected_hypotheses:
  - achievements is the safest pilot: it depends on player-persistence and interacts with combat, quests and spells
  - titles is the safest pilot: it depends on cyclopedia-character and player-persistence and has broad cross-domain unlock interactions
changed_paths:
  - docs/agents/tasks/active/CAN-20260725-rtec-002-vocations-pilot.md
validation:
  - command: fresh GitHub preflight
    result: PASS
    evidence: main/open PR/branch/program/registry state verified
  - command: Agent Task Ownership
    result: NOT_RUN
    evidence: draft PR not opened yet
blockers: []
next_action: Open a draft PR, then collect exact current-source and official evidence for bounded vocation claims.
```

# Handoff

## Start here

Read this checkpoint, the live draft PR, the v1 RTEC README/contracts, the canonical `vocations` registry record, current vocation source and TSD-003.

## Do not repeat

Do not restart broad module selection, create another registry, populate other module dossiers or edit runtime/owner paths.

## Required reads

- `AGENTS.md`
- `docs/agents/REPOSITORY_MAP.md`
- `docs/agents/CONTEXT_ROUTING.md`
- `docs/agents/programs/REAL_TIBIA_EVIDENCE_COLLECTION_PROGRAM.md`
- `docs/ai-agent/REAL_TIBIA_EVIDENCE_COLLECTOR_ARCHITECTURE.md`
- `docs/agents/real-tibia/evidence/README.md`
- `docs/agents/real-tibia/registry/modules/vocations.yaml`
- `docs/agents/real-tibia/TSD_003_ACCOUNT_CHARACTER_PROGRESSION_REPORT.md`

## Open questions

- Which current official pages provide exact source-pinned public vocation identity and purpose?
- Which current Canary values can be represented as static definition evidence without overclaiming runtime behavior?
- Which one missing proof should become `RTR-VOCATIONS-0001`?

# Completion

- Final status: active
- PR: pending
- Merge commit: pending
- Program record updated: pending closeout
- Catalogue updated: none expected
- Changelog updated: none expected
- Archived at: pending
