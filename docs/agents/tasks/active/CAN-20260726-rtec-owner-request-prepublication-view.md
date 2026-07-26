---
task_id: CAN-20260726-rtec-owner-request-prepublication-view
program_id: CAN-PROGRAM-REAL-TIBIA-EVIDENCE-COLLECTION
coordination_id: RTEC-OWNER-REQUEST-PREPUBLICATION-VIEW
status: implementing
agent: "GPT-5.6 Thinking"
branch: fix/rtec-owner-request-prepublication-view-20260726
base_branch: main
created: 2026-07-26T20:50:00+02:00
updated: 2026-07-26T21:15:00+02:00
last_verified_commit: "6a403bed0fdf840cee0bada5496c4ea50ada7d0f"
risk: medium
related_issue: ""
related_pr: "968"
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
    - tools/agents/test_real_tibia_owner_request_prepublication.py
  shared: []
  read_only:
    - tools/agents/real_tibia_evidence.py
    - tools/agents/real_tibia_evidence_lib.py
    - .github/workflows/real-tibia-evidence.yml
    - docs/agents/real-tibia/evidence/**
modules_touched:
  - real-tibia-evidence-collection
reuses:
  - publication_view
  - validate_for_publication
  - canary-real-tibia-owner-request-v1
public_interfaces:
  - owner-request lifecycle corpus validation and generated-index write boundary
cross_repo_tasks: []
---

# Goal

Make owner-request lifecycle dry-runs and mutations use the same prepublication-aware validation and index-generation boundary as the evidence CLI, without weakening candidate source-contract validation or changing request states.

# Delivered

- `_blocking_diagnostics()` reuses `validate_for_publication()`.
- Write-mode lifecycle operations generate from `publication_view()` and validate the complete-plus-published views after the transaction.
- Focused coverage proves a future-dated `review-needed` record does not block a request dry-run.
- Focused coverage proves an accepted future-dated record still emits `RTEC-FUTURE-EVIDENCE`.
- The existing transactional lifecycle test now validates the canonical publication boundary after successful writes and rollback.

# Acceptance criteria

- [x] Reuse the existing publication helpers; create no second publication filter.
- [x] Preserve complete source-contract validation for candidate evidence and requests.
- [x] Add focused owner-lifecycle coverage with a future-dated `review-needed` record.
- [x] Confirm an accepted future-dated record remains fail-closed.
- [x] Make write-mode generated indexes use the published view.
- [x] Update existing transactional coverage to assert the publication-aware post-write contract.
- [x] Change no workflow, schema, evidence/request data, request state, runtime, data, client, map or E2E path.
- [ ] Pass exact-head Evidence Contracts, Ownership and ordinary CI.
- [ ] Mark Ready and squash-merge before rerunning worker PRs #957 and #958.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-26T21:15:00+02:00
head: 6a403bed0fdf840cee0bada5496c4ea50ada7d0f
branch: fix/rtec-owner-request-prepublication-view-20260726
pr: 968
status: implementing
context_routes:
  - agent-governance
  - real-tibia-parity
  - ci-repair
owned_paths:
  - docs/agents/tasks/active/CAN-20260726-rtec-owner-request-prepublication-view.md
  - tools/agents/real_tibia_owner_request.py
  - tools/agents/test_real_tibia_owner_request.py
  - tools/agents/test_real_tibia_owner_request_prepublication.py
proven:
  - evidence CLI publication view is merged in PR 960
  - PR 957 corpus/index validation passed and failed only the production request dry-run
  - owner lifecycle previously called full Corpus.validate with published as_of
  - owner lifecycle write mode previously generated indexes from the full candidate corpus
  - the patch reuses publication_view and validate_for_publication for dry-run, write generation and post-write validation
  - new regression tests for future review-needed and accepted future records pass in workflow run 30215290057
  - the first patched run failed only because the legacy transactional test asserted full-corpus index bytes after publication-aware generation
  - that legacy assertion now uses validate_for_publication
unknown:
  - first exact-head workflow failure after the legacy assertion update
conflicts: []
first_failure:
  marker: repair-not-yet-revalidated
  evidence: the only observed test failure was corrected; exact-head workflow results for the corrected test suite are pending
rejected_hypotheses:
  - backdate candidate evidence
  - advance the published as_of date before review
  - disable or weaken the production request dry-run
  - generate indexes from the complete candidate corpus
changed_paths:
  - docs/agents/tasks/active/CAN-20260726-rtec-owner-request-prepublication-view.md
  - tools/agents/real_tibia_owner_request.py
  - tools/agents/test_real_tibia_owner_request.py
  - tools/agents/test_real_tibia_owner_request_prepublication.py
validation:
  - command: workflow run 30215290057 focused tests
    result: PARTIAL
    evidence: both new regressions passed; one legacy full-corpus assertion failed and was updated to the publication-aware contract
blockers: []
next_action: Pass exact-head Evidence Contracts, Ownership and ordinary CI for PR 968, then run the Ready-state final gate and squash-merge it before refreshing worker validation.
```
