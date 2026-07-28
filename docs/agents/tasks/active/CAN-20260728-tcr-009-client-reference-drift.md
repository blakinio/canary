---
task_id: CAN-20260728-tcr-009-client-reference-drift
program_id: CAN-PROGRAM-OTBM-TIBIA-CLIENT-REFERENCE
coordination_id: TCR-009
status: implementing
agent: "GPT-5.6 Thinking"
branch: docs/tcr-009-client-reference-drift-blocker-20260728
base_branch: main
created: 2026-07-28T22:49:37+02:00
updated: 2026-07-28T22:53:00+02:00
last_verified_commit: "b3e7f91cf0220b5648a48ec79d128d48d95b2971"
risk: medium
related_issue: ""
related_pr: "992"
depends_on:
  - TCR-002 merged stable canary-tibia-staticdata-index-v1
  - TCR-003 merged stable canary-tibia-staticmapdata-index-v1
  - TCR-004 merged stable canary-tibia-proficiency-index-v1
blocks:
  - TCR-010
  - TCR-011
  - OWA-003
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260728-tcr-009-client-reference-drift.md
    - docs/agents/real-tibia/evidence/requests/tcr/RTREQ-TCR-CLIENT-REFERENCE-DRIFT-0001.yaml
    - .github/workflows/tcr009-evidence-request-generate.yml
  shared:
    - docs/agents/programs/OTBM_TIBIA_CLIENT_REFERENCE_PROGRAM.md
    - docs/agents/real-tibia/evidence/generated/EVIDENCE_INDEXES.json
    - docs/agents/real-tibia/evidence/modules/item-definitions/EVIDENCE_INDEX.yaml
  read_only:
    - tools/ai-agent/tibia_client_reference_manifest.py
    - tools/ai-agent/tibia_staticdata_reference_index.py
    - tools/ai-agent/tibia_staticmapdata_reference_index.py
    - tools/ai-agent/tibia_proficiency_reference_index.py
    - tools/agents/real_tibia_owner_request.py
    - tools/agents/real_tibia_evidence.py
    - docs/ai-agent/OTBM_TIBIA_CLIENT_REFERENCE_ARCHITECTURE.md
    - docs/agents/programs/OTBM_WORLD_ASSURANCE_OPERATIONS_PROGRAM.md
modules_touched:
  - OTBM Tibia client reference architecture
  - Real Tibia owner-request lifecycle
reuses:
  - canary-tibia-client-reference-manifest-v1
  - canary-tibia-staticdata-index-v1
  - canary-tibia-staticmapdata-index-v1
  - canary-tibia-proficiency-index-v1
  - canary-real-tibia-owner-request-v1
public_interfaces: []
cross_repo_tasks: []
---

# Goal

Perform the fresh TCR-009 input-evidence preflight, implement the drift producer only if two complete exact reference snapshot sets exist, and otherwise record the exact external-evidence request and fail-closed blocker without synthesizing snapshots.

# Acceptance criteria

- [x] Current `main`, open PRs, branches, programme state and retained TCR evidence searched.
- [x] User-supplied external inputs inspected without committing proprietary bytes or generated reports.
- [ ] Exact owner/evidence request created through the existing lifecycle.
- [ ] First failure and dependency impact recorded without claiming `canary-tibia-client-reference-drift-v1` stable.
- [ ] Current-head ownership and repository checks verified.
- [ ] Feature/preflight PR merged, followed by a separate lifecycle closeout.

# Confirmed context

- Current preflight base is `main` `87149c6b527f43025860c20cca0a440091ee8730`.
- Draft PR #992 owns this bounded package.
- TCR-000..007 are merged/stable; TCR-009, TCR-010 and TCR-011 are not stable/merged.
- No TCR-009 task branch or PR existed at preflight.
- One external official-client package is available outside Git with package metadata `15.25.bd5a04` and exact selected source hashes:
  - StaticData `0bd51e1660f9d58594eb10000c35ea51113fc668aa3ee416c8c6b7ebb59b78ff`;
  - StaticMapData `0967af2eacdd8f2a608e738b9042362676167d6c6455e60d08db7ae16cf7ea53`;
  - proficiency `1a915dffd9265cd1c18d39e55da7ede691b2e58add534bc186238ae028a73f22`.
- That package contains no retained `canary-tibia-client-reference-manifest-v1`, generated StaticData/StaticMapData/proficiency indexes, or drift report.
- TCR-003 and TCR-004 final validation workflow runs retain no artifacts.
- No second exact client package or complete exact snapshot set was found.

# Existing work to reuse

| Module/task/PR | Reuse | Evidence/path | Why it fits |
|---|---|---|---|
| TCR-001..004 | Exact manifest and index contracts | `tools/ai-agent/tibia_*reference*.py` | Own the required snapshot producers; no new parser is justified. |
| RTEC-003 owner-request lifecycle | External evidence request and state machine | `tools/agents/real_tibia_owner_request.py` | Existing fail-closed path for missing owner evidence. |
| Real Tibia evidence generator | Deterministic request index regeneration | `tools/agents/real_tibia_evidence.py` | Generated indexes must not be edited by hand. |
| QA-016 | Future dependency-scoped staleness | `docs/ai-agent/OTBM_RELEASE_PROVENANCE.md` | Consumer only after TCR-009 is stable. |

# Ownership and overlap check

- Program record: TCR-009 planned and explicitly gated by two complete exact snapshot sets.
- Open PRs inspected: no TCR-009 overlap; unrelated open work remains separately owned.
- Branch search: no existing `tcr-009` branch before this task.
- Exclusive claims: task record, one new TCR owner request, and a self-removing index-generation helper.
- Shared claims: deterministic evidence indexes and the later narrow programme status update.
- Overlaps: none found.

# Current state

`BLOCKED_EXTERNAL_EVIDENCE`

First failure: `TCR009_REQUIRES_TWO_COMPLETE_EXACT_REFERENCE_SNAPSHOTS`.

The available external package can seed one future snapshot, but it is not itself a complete generated snapshot set and no second exact package/snapshot is available. TCR-009 implementation is therefore not authorized.

# Plan

1. Create one exact TCR owner/evidence request for two complete provenance-pinned snapshot sets.
2. Regenerate evidence indexes with the existing canonical generator; remove the temporary helper in the same generated commit.
3. Validate the bounded docs/request change, merge it, then close ownership in a separate lifecycle PR.

# Validation and CI

| Commit | Command/check/workflow | Result | Evidence/notes |
|---|---|---|---|
| `87149c6b527f43025860c20cca0a440091ee8730` | fresh repository/PR/branch/programme preflight | passed | no TCR-009 owner or complete two-snapshot evidence found |
| external package | bounded archive inventory and SHA-256 verification | passed | no manifest/index/drift outputs; proprietary input remains outside Git |
| TCR-003 run `30070199240` | retained workflow artifacts | passed | artifact list empty |
| TCR-004 run `30074847288` | retained workflow artifacts | passed | artifact list empty |
| `b3e7f91cf0220b5648a48ec79d128d48d95b2971` | early draft PR publication | passed | PR #992 created |

# Risks and compatibility

- Runtime: none; no runtime code changes.
- Data/migration: none; no source or generated client data committed.
- Backward compatibility: stable TCR-001..007 contracts remain unchanged.
- Rollback: revert the docs/request commits.

# Remaining work

1. Add the exact request, regenerate its deterministic indexes, and update the final blocked checkpoint.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-28T22:53:00+02:00
head: b3e7f91cf0220b5648a48ec79d128d48d95b2971
branch: docs/tcr-009-client-reference-drift-blocker-20260728
pr: 992
status: blocked
context_routes:
  - agent-governance
  - otbm
  - real-tibia-parity
owned_paths:
  - docs/agents/tasks/active/CAN-20260728-tcr-009-client-reference-drift.md
  - docs/agents/real-tibia/evidence/requests/tcr/RTREQ-TCR-CLIENT-REFERENCE-DRIFT-0001.yaml
  - .github/workflows/tcr009-evidence-request-generate.yml
  - docs/agents/real-tibia/evidence/generated/EVIDENCE_INDEXES.json
  - docs/agents/real-tibia/evidence/modules/item-definitions/EVIDENCE_INDEX.yaml
  - docs/agents/programs/OTBM_TIBIA_CLIENT_REFERENCE_PROGRAM.md
proven:
  - TCR-009 requires two complete exact manifest/index snapshot sets; TCR-010, TCR-011 and OWA-003 depend on stable TCR-009.
  - One external package is available, but it contains source inputs only and no retained generated TCR manifest/index set.
  - TCR-003 and TCR-004 final validation runs expose no retained artifacts.
  - No second exact package or complete snapshot set was found in repository, PR, branch, workflow-artifact or supplied-input evidence.
  - Draft PR 992 is the sole bounded TCR-009 owner.
derived:
  - TCR-009 implementation cannot start without fabricating evidence, so the only valid bounded output is an external-evidence request and blocked lifecycle.
unknown:
  - Exact identity, hashes and generated reports for a second client reference snapshot.
conflicts: []
first_failure:
  marker: TCR009_REQUIRES_TWO_COMPLETE_EXACT_REFERENCE_SNAPSHOTS
  evidence: only one source package is available and neither two complete generated snapshot sets nor a second exact package are retained
rejected_hypotheses:
  - Reuse the same snapshot as baseline and current to produce zero drift.
  - Invent a synthetic second snapshot or infer client build identity from filenames.
  - Start TCR-010, TCR-011 or OWA-003 before TCR-009 is stable/merged.
changed_paths:
  - docs/agents/tasks/active/CAN-20260728-tcr-009-client-reference-drift.md
validation:
  - command: fresh repository and external-input preflight
    result: PASS
    evidence: exact first-failure marker established without input mutation
  - command: early draft PR publication
    result: PASS
    evidence: PR 992 on branch docs/tcr-009-client-reference-drift-blocker-20260728
blockers:
  - TCR009_REQUIRES_TWO_COMPLETE_EXACT_REFERENCE_SNAPSHOTS
next_action: Add the exact owner request and run the canonical deterministic evidence-index generator before final validation.
```
