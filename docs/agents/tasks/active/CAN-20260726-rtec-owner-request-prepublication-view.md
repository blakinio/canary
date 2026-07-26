---
task_id: CAN-20260726-rtec-owner-request-prepublication-view
program_id: CAN-PROGRAM-REAL-TIBIA-EVIDENCE-COLLECTION
coordination_id: RTEC-OWNER-REQUEST-PREPUBLICATION-VIEW
status: implementing
agent: "GPT-5.6 Thinking"
branch: fix/rtec-owner-request-prepublication-view-20260726
base_branch: main
created: 2026-07-26T20:50:00+02:00
updated: 2026-07-26T20:50:00+02:00
last_verified_commit: "b5a45d32b015965fd79aece734857edf4bdc0bac"
risk: medium
related_issue: ""
related_pr: "pending"
depends_on:
  - PR-960-PREPUBLICATION-INDEX-GATE
blocks:
  - CAN-20260726-rtec-005-item-decay
  - CAN-20260726-rtec-005-parties
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260726-rtec-owner-request-prepublication-view.md
    - tools/agents/real_tibia_owner_request.py
    - tools/agents/test_real_tibia_owner_request.py
  shared: []
  read_only:
    - tools/agents/real_tibia_evidence.py
    - tools/agents/real_tibia_evidence_lib.py
    - .github/workflows/real-tibia-evidence.yml
    - docs/agents/real-tibia/evidence/**
modules_touched:
  - real-tibia-evidence-collection
reuses:
  - validate_for_publication
  - canary-real-tibia-owner-request-v1
public_interfaces:
  - owner-request lifecycle corpus validation
cross_repo_tasks: []
---

# Goal

Make owner-request lifecycle dry-runs and mutations use the same prepublication-aware validation boundary as the evidence CLI, without weakening candidate source-contract validation or changing request states.

# Proven failure

- PR #960 separated full source-contract validation from published freshness/index validation.
- `real_tibia_owner_request.py::_blocking_diagnostics()` still calls `Corpus.validate(as_of)` directly.
- An honest `review-needed` record dated 2026-07-26 therefore blocks the workflow dry-run fixed at published `as_of=2026-07-25`, even though the evidence CLI validates the package successfully.

# Acceptance criteria

- [ ] Reuse the existing `validate_for_publication()` helper; do not create a second publication filter.
- [ ] Preserve complete source-contract validation for candidate evidence and requests.
- [ ] Add a focused owner-lifecycle test with a future-dated `review-needed` record.
- [ ] Confirm an accepted future-dated record still blocks lifecycle validation.
- [ ] Change no workflow, schema, evidence record, request state, runtime, data, client, map or E2E path.
- [ ] Pass exact-head Evidence Contracts, Ownership and ordinary CI.
- [ ] Mark Ready and squash-merge before rerunning worker PRs #957 and #958.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-26T20:50:00+02:00
head: b5a45d32b015965fd79aece734857edf4bdc0bac
branch: fix/rtec-owner-request-prepublication-view-20260726
pr: pending
status: implementing
context_routes:
  - agent-governance
  - real-tibia-parity
  - ci-repair
owned_paths:
  - docs/agents/tasks/active/CAN-20260726-rtec-owner-request-prepublication-view.md
  - tools/agents/real_tibia_owner_request.py
  - tools/agents/test_real_tibia_owner_request.py
proven:
  - evidence CLI publication view is merged in PR 960
  - owner-request lifecycle still calls full Corpus.validate with the published as_of date
  - PR 957 evidence corpus validation passed but the production request dry-run failed
  - the failure is caused by a future review-needed record, not a request mutation or index drift
derived:
  - owner lifecycle must reuse validate_for_publication before applying request transition checks
unknown:
  - first focused-test failure after the minimal patch
conflicts: []
first_failure:
  marker: owner-lifecycle-bypasses-prepublication-view
  evidence: workflow run 30214892792 passed corpus/index validation and failed only the production request dry-run
rejected_hypotheses:
  - backdate candidate evidence
  - advance the published as_of date before review
  - disable the workflow dry-run
changed_paths:
  - docs/agents/tasks/active/CAN-20260726-rtec-owner-request-prepublication-view.md
validation:
  - command: inspect workflow and owner-request validation call path
    result: PASS
    evidence: .github/workflows/real-tibia-evidence.yml step 12 invokes the lifecycle tool at as_of 2026-07-25; _blocking_diagnostics calls Corpus.validate directly
blockers: []
next_action: Reuse validate_for_publication in owner-request validation and add focused future review-needed versus accepted regression coverage.
```
