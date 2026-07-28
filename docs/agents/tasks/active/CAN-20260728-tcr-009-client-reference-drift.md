---
task_id: CAN-20260728-tcr-009-client-reference-drift
program_id: CAN-PROGRAM-OTBM-TIBIA-CLIENT-REFERENCE
coordination_id: TCR-009
status: implementing
agent: "GPT-5.6 Thinking"
branch: docs/archive-tcr-009-blocked-20260728
base_branch: main
created: 2026-07-28T22:49:37+02:00
updated: 2026-07-28T23:31:00+02:00
last_verified_commit: "8644fc5ae56a661c0bd38d9a4a8bcd706abffc2a"
risk: low
related_issue: ""
related_pr: "993"
depends_on:
  - TCR-009 bounded evidence preflight merged via PR 992
blocks:
  - TCR-010
  - TCR-011
  - OWA-003
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260728-tcr-009-client-reference-drift.md
    - docs/agents/tasks/archive/CAN-20260728-tcr-009-client-reference-drift.md
    - .github/workflows/tcr009-lifecycle-closeout.yml
  shared:
    - docs/agents/programs/OTBM_TIBIA_CLIENT_REFERENCE_PROGRAM.md
    - docs/agents/MODULE_CATALOG.md
  read_only:
    - docs/agents/real-tibia/evidence/requests/tcr/RTREQ-TCR-ITEM-DEFINITIONS-0002.yaml
    - docs/agents/real-tibia/evidence/generated/EVIDENCE_INDEXES.json
    - docs/agents/real-tibia/evidence/modules/item-definitions/EVIDENCE_INDEX.yaml
    - docs/agents/programs/OTBM_WORLD_ASSURANCE_OPERATIONS_PROGRAM.md
modules_touched:
  - OTBM Tibia client reference architecture
  - Real Tibia owner-request lifecycle
reuses:
  - canary-real-tibia-owner-request-v1
public_interfaces: []
cross_repo_tasks: []
---

# Goal

Close the merged TCR-009 bounded evidence-preflight lifecycle without claiming the drift producer stable: archive the task as blocked-external-evidence, update programme/module discovery, and release ownership.

# Feature result

- Feature/preflight PR: `#992`.
- Exact feature head: `ada7a9e6f7d855a2d6f8c34d003b752a49251c1b`.
- Feature merge commit: `8a88e2f09257e620985770e5e053381df32f916d`.
- Ready-state protected CI: run `30399382989`, conclusion `success`.
- Exact blocker: `TCR009_REQUIRES_TWO_COMPLETE_EXACT_REFERENCE_SNAPSHOTS`.
- Evidence request: `RTREQ-TCR-ITEM-DEFINITIONS-0002`, status `ready-for-owner-triage`.
- Stable contracts remain TCR-000 through TCR-007 only; no `canary-tibia-client-reference-drift-v1` implementation or stability claim exists.

# Fresh post-merge preflight

- `main` HEAD is feature merge `8a88e2f09257e620985770e5e053381df32f916d`.
- Feature branch was removed after merge.
- No competing TCR-009 branch or lifecycle owner exists.
- TCR-010, TCR-011 and OWA-003 remain dependency-gated by stable TCR-009.
- Fresh search found no concrete minimap parity use case, so TCR-008 remains optional/deferred-no-concrete-use-case.
- Fresh search found no retained reviewed real before/current/candidate map-change chain, so OWA-006 retains `OWA006_NO_RETAINED_REVIEWED_REAL_CANDIDATE_CHAIN`.

# Acceptance criteria

- [x] Feature/preflight PR merged after exact-final-head and Ready-state protected CI.
- [x] Early draft lifecycle PR published.
- [ ] Task archived with `status: blocked` and exact feature/CI evidence.
- [ ] Programme queue, handoff and module discovery updated without claiming TCR-009 stable.
- [ ] Active task removed and ownership released.
- [ ] Lifecycle exact-final-head checks, Ready-state protected CI and merge completed.

# Planned closeout

1. Run the bounded self-removing lifecycle transformer.
2. Validate the archived task, programme/module records and released active ownership.
3. Freeze exact final head, transition Ready, obtain protected CI and merge PR #993.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-28T23:31:00+02:00
head: 8644fc5ae56a661c0bd38d9a4a8bcd706abffc2a
branch: docs/archive-tcr-009-blocked-20260728
pr: 993
status: implementing
context_routes:
  - agent-governance
  - otbm
  - real-tibia-parity
owned_paths:
  - docs/agents/tasks/active/CAN-20260728-tcr-009-client-reference-drift.md
  - docs/agents/tasks/archive/CAN-20260728-tcr-009-client-reference-drift.md
  - docs/agents/programs/OTBM_TIBIA_CLIENT_REFERENCE_PROGRAM.md
  - docs/agents/MODULE_CATALOG.md
  - .github/workflows/tcr009-lifecycle-closeout.yml
proven:
  - PR 992 merged the exact TCR-009 evidence request and blocker after Ready-state CI run 30399382989 succeeded.
  - Two complete exact client-reference snapshot sets do not exist in retained repository/workflow/supplied evidence.
  - TCR-009 implementation and all dependent packages remain unauthorized.
derived:
  - The correct lifecycle disposition is blocked-external-evidence, not completed/stable.
unknown:
  - Exact identities, hashes and retained generated reports for two distinct complete reference snapshots.
conflicts: []
first_failure:
  marker: TCR009_REQUIRES_TWO_COMPLETE_EXACT_REFERENCE_SNAPSHOTS
  evidence: RTREQ-TCR-ITEM-DEFINITIONS-0002
rejected_hypotheses:
  - Archive TCR-009 as completed or stable despite missing exact snapshot evidence.
  - Start TCR-010, TCR-011 or OWA-003 before TCR-009 is stable and merged.
  - Implement TCR-008 without a concrete non-duplicative minimap parity use case.
changed_paths:
  - docs/agents/tasks/active/CAN-20260728-tcr-009-client-reference-drift.md
  - docs/agents/tasks/archive/CAN-20260728-tcr-009-client-reference-drift.md
  - docs/agents/programs/OTBM_TIBIA_CLIENT_REFERENCE_PROGRAM.md
  - docs/agents/MODULE_CATALOG.md
  - .github/workflows/tcr009-lifecycle-closeout.yml
validation:
  - command: feature PR 992 Ready-state protected CI
    result: PASS
    evidence: run 30399382989 completed success on exact head ada7a9e6f7d855a2d6f8c34d003b752a49251c1b
  - command: fresh post-merge ownership and evidence preflight
    result: PASS
    evidence: main 8a88e2f09257e620985770e5e053381df32f916d; no competing TCR-009 owner or newly complete evidence chain
blockers:
  - TCR009_REQUIRES_TWO_COMPLETE_EXACT_REFERENCE_SNAPSHOTS
next_action: Run the self-removing lifecycle transformer, then exact-final-head validation and Ready-state protected CI for PR 993.
```
