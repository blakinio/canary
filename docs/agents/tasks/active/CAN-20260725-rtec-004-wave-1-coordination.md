---
task_id: CAN-20260725-rtec-004-wave-1-coordination
program_id: CAN-PROGRAM-REAL-TIBIA-EVIDENCE-COLLECTION
coordination_id: RTEC-004-WAVE-1
status: implementing
agent: "GPT-5.6 Thinking"
branch: feat/rtec-004-wave-1-coordinator-20260725
base_branch: main
created: 2026-07-25T20:11:38+02:00
updated: 2026-07-25T20:11:38+02:00
last_verified_commit: "124b029d1a2498a64fa6612b16efa386b8786a83"
risk: medium
related_issue: ""
related_pr: ""
depends_on:
  - RTEC-002
  - RTEC-003
blocks:
  - RTEC-005
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260725-rtec-004-wave-1-coordination.md
  shared:
    - docs/agents/programs/REAL_TIBIA_EVIDENCE_COLLECTION_PROGRAM.md
    - docs/agents/real-tibia/evidence/generated/EVIDENCE_INDEXES.json
  read_only:
    - docs/agents/real-tibia/registry/**
    - docs/agents/real-tibia/generated/**
    - docs/agents/real-tibia/evidence/modules/**
    - docs/agents/real-tibia/evidence/requests/**
    - tools/e2e/**
    - tools/ai-agent/**
modules_touched:
  - real-tibia-evidence-collection
  - weapon-proficiency
  - item-definitions
reuses:
  - canary-real-tibia-evidence-record-v1
  - canary-real-tibia-owner-request-v1
  - canary-real-tibia-generated-indexes-v1
  - canonical Real Tibia module registry
public_interfaces: []
cross_repo_tasks: []
---

# Goal

Coordinate the first bounded parallel Collector campaign after RTEC-003 with two independent evidence-only packages. Preserve owner boundaries and reduce concurrency to match current CI and review load.

# Fresh preflight

- Writable target: `blakinio/canary` only.
- Current `main`: `124b029d1a2498a64fa6612b16efa386b8786a83`.
- RTEC-003 feature, archival and programme closeout are merged through PRs #921, #926 and #927.
- RTEC-004 is `planned`; no open RTEC PR or RTEC-004 branch existed before this task.
- The registry contains 62 modules.
- Only `vocations` has Collector evidence: five records and one active request.
- `RTREQ-FEATURE-VOCATIONS-0001` remains `ready-for-owner-triage` without owner task, PR or result.
- Six unrelated PRs are open. PR #923 owns active OTBM work and PR #925 owns active Universal E2E work.

# Current official baseline

Observed on 2026-07-25:

- Summer Update 2026 was released on 2026-07-13.
- It introduced modification of up to two weapon-proficiency perk slots per weapon.
- The 2026-07-14 fixes include pending weapon-proficiency level-up display isolation after switching characters.
- The 2026-07-21 fixes state that Cloud in a Bottle is available from difficulty 10 rather than 15.

Official references:

- `https://www.tibia.com/news/?id=8845&subtopic=newsarchive`
- `https://www.tibia.com/news/?subtopic=latestnews`

These statements prove public release identity and documented visible changes only. They do not prove formulas, persistence, protocol, current Canary behavior or physical gameplay.

# Wave decision

Start two workers rather than the maximum eight because six PRs are already open, including OTBM and E2E work. This still tests parallel dossier ownership while limiting CI, storage and review pressure.

# Assignments

## Worker A — weapon proficiency

- Module: `weapon-proficiency`.
- Package: Summer Update 2026 perk-slot modification and pending-level-up character-isolation behavior.
- Coordination ID: `RTEC-004-W1-WEAPON-PROFICIENCY`.
- Exclusive dossier root: `docs/agents/real-tibia/evidence/modules/weapon-proficiency/**`.
- Do not share perk identifiers, formulas, persistence state or character-switch UI state with another Collector package.
- Do not touch the active vocations owner request.

## Worker B — item definitions

- Module: `item-definitions`.
- Package: Cloud in a Bottle difficulty availability and description correction (`10`, not `15`) with exact Canary definition and registration comparison.
- Coordination ID: `RTEC-004-W1-CLOUD-IN-A-BOTTLE`.
- Exclusive dossier root: `docs/agents/real-tibia/evidence/modules/item-definitions/**`.
- Do not expand into weapon perks, map content or broad item-catalogue remediation.

The packages have separate module roots and behavior surfaces. Neither requires the OTBM paths owned by PR #923 or the E2E paths owned by PR #925. Missing proof must become a structured owner request.

# Acceptance criteria

- [x] Verify main, programme, registry, evidence/request state and open PR ownership.
- [x] Pin the current official release/change baseline and proof limits.
- [x] Reduce wave 1 to two independent workers.
- [x] Assign exact package scopes, coordination IDs and dossier roots.
- [ ] Create one branch, task and draft PR for each worker.
- [ ] Validate source provenance, separate version axes and proof/nonproof boundaries.
- [ ] Pass corpus, deterministic-index, ownership and applicable CI checks on each final head.
- [ ] Review and merge worker PRs without owner-path edits.
- [ ] Integrate shared indexes and programme state only after worker merges.
- [ ] Record the concurrency result and one exact RTEC-005 decision.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-25T20:11:38+02:00
head: 124b029d1a2498a64fa6612b16efa386b8786a83
branch: feat/rtec-004-wave-1-coordinator-20260725
pr: none
status: implementing
context_routes:
  - agent-governance
  - real-tibia-parity
owned_paths:
  - docs/agents/tasks/active/CAN-20260725-rtec-004-wave-1-coordination.md
  - docs/agents/programs/REAL_TIBIA_EVIDENCE_COLLECTION_PROGRAM.md
  - docs/agents/real-tibia/evidence/generated/EVIDENCE_INDEXES.json
proven:
  - main is 124b029d1a2498a64fa6612b16efa386b8786a83 after RTEC-003 closeout
  - RTEC-004 was planned with no open RTEC PR or RTEC-004 branch
  - the registry contains 62 modules
  - only vocations currently has Collector evidence records
  - RTREQ-FEATURE-VOCATIONS-0001 remains ready-for-owner-triage without owner evidence
  - six PRs are open including active OTBM and Universal E2E work
  - Summer Update 2026 provides current official leads for both selected packages
  - the two packages use distinct module roots and behavior surfaces
derived:
  - two workers are safer than eight under current CI and review load
  - the selected packages can run concurrently without sharing one behavior identifier formula persistence state map package or owner request
unknown:
  - worker branch heads and PR numbers
  - current Canary comparison results
  - whether either package needs an owner request
  - final validation and review outcomes
conflicts: []
first_failure:
  marker: worker-tasks-not-created
  evidence: assignments exist but worker branches tasks and draft PRs do not
rejected_hypotheses:
  - start eight workers immediately: current repository load supports a lower cap
  - assign world-map work while PR 923 is active: avoidable OTBM coordination pressure
  - assign physical-client work while PR 925 is active: E2E retains execution ownership
changed_paths:
  - docs/agents/tasks/active/CAN-20260725-rtec-004-wave-1-coordination.md
validation:
  - command: live main open-PR active-RTEC branch and programme preflight
    result: PASS
    evidence: main 124b029d1a2498a64fa6612b16efa386b8786a83; no pre-existing RTEC-004 work
  - command: registry and evidence generated-index review
    result: PASS
    evidence: 62 modules; vocations-only evidence corpus with five records and one active request
  - command: official Tibia current-release review as of 2026-07-25
    result: PASS
    evidence: official 2026-07-13 update and 2026-07-14/21 fixes
blockers: []
next_action: Create the weapon-proficiency worker branch, active task record and early draft PR with exclusive ownership of docs/agents/real-tibia/evidence/modules/weapon-proficiency/**.
```
