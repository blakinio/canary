---
task_id: CAN-20260723-tcr-001-client-package-manifest
program_id: CAN-PROGRAM-OTBM-TIBIA-CLIENT-REFERENCE
coordination_id: OTBM-TIBIA-CLIENT-REFERENCE
status: review
agent: GPT-5.6 Thinking
branch: feat/tcr-001-client-package-manifest-20260723
base_branch: main
created: 2026-07-23T16:48:37+02:00
updated: 2026-07-23T17:05:00+02:00
last_verified_commit: "07d84bbd6f2ac5e6ab28690c39308a403c8b75f5"
risk: medium
related_issue: ""
related_pr: "809"
depends_on:
  - TCR-000 merged architecture/governance
blocks:
  - TCR-002
  - TCR-003
  - TCR-004
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260723-tcr-001-client-package-manifest.md
    - tools/ai-agent/tibia_client_reference_manifest.py
    - tools/ai-agent/tibia_client_reference_manifest_tool.py
    - tools/ai-agent/test_tibia_client_reference_manifest.py
    - docs/ai-agent/TIBIA_CLIENT_REFERENCE_MANIFEST.md
    - docs/ai-agent/TIBIA_CLIENT_REFERENCE_MANIFEST.schema.json
    - .github/workflows/tibia-client-reference.yml
  shared:
    - docs/ai-agent/OTBM_TIBIA_CLIENT_REFERENCE_ARCHITECTURE.md
    - docs/agents/programs/OTBM_TIBIA_CLIENT_REFERENCE_PROGRAM.md
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - AGENTS.md
    - docs/agents/REPOSITORY_MAP.md
    - docs/agents/CONTEXT_ROUTING.md
    - docs/agents/KNOWN_RISKS.md
    - docs/agents/BUILD_TEST_MATRIX.md
    - docs/agents/REAL_TIBIA_EVIDENCE_SOURCES.md
    - docs/agents/REAL_TIBIA_PARITY_PLAYBOOK.md
    - tools/ai-agent/otbm_evidence_gateway.py
    - tools/ai-agent/otbm_evidence_gateway_tool.py
modules_touched:
  - OTBM analysis tooling
  - official-client reference evidence
reuses:
  - OTBM Tibia client reference architecture
  - OTBM Compact Evidence Gateway path/hash/output safety conventions
  - AI Agent Tools broad Python test workflow
public_interfaces:
  - canary-tibia-client-reference-manifest-v1
cross_repo_tasks: []
---

# Goal

Implement only TCR-001 Client Package Manifest: deterministic, fail-closed, read-only provenance for explicitly selected files below one user-supplied Tibia client reference package root.

# Acceptance

- [x] `canary-tibia-client-reference-manifest-v1` library and CLI.
- [x] Explicit package root and 1..128 selected safe relative files only.
- [x] Symlink/path-escape/missing/non-file/duplicate/hardlink rejection.
- [x] Per-file size bound before streaming SHA-256; exact applied bound recorded.
- [x] Build evidence states remain `proven`, `declared`, `unknown` or `conflicting`.
- [x] Optional generated-index SHA-256 pins do not open arbitrary output paths.
- [x] Deterministic JSON with explicit timezone-aware observation metadata and exact parser revision.
- [x] Create-new/no-clobber default, output symlink/input-alias rejection, atomic explicit overwrite.
- [x] Focused tests, `py_compile`, JSON schema syntax validation and dedicated workflow.
- [x] Keep the feature PR discovery state truthful: durable programme/catalogue/changelog wording that claims TCR-001 is merged/stable is deferred to the post-merge lifecycle/discovery closure.
- [x] No proprietary client input committed; no TCR-002/TCR-003 implementation.
- [ ] Exact-final-head checks green, PR ready/mergeable, and no unresolved review or ownership blocker remains.

# Evidence

## PROVEN

- TCR-000 delivery PR #762 merged as `d5a08db0502fb85ff807c9c18f02bf92bd1faaed`; lifecycle PR #808 merged as `014f156a8df4f7910a206f104c24842f3748cf99`.
- No equivalent manifest implementation or competing TCR-001 PR existed at preflight.
- Existing `otbm-tooling` registry already owns client-reference manifest/index correlation and `test_tibia_client_reference*.py`.
- The feature PR is bounded to seven TCR-001 paths: manifest library/CLI, focused tests, contract/schema, dedicated workflow and this task record.
- Pre-final head `07d84bbd6f2ac5e6ab28690c39308a403c8b75f5`: Agent Task Ownership run `30018708498` PASS.
- Pre-final head `07d84bbd6f2ac5e6ab28690c39308a403c8b75f5`: repository CI run `30018709068` PASS.
- Pre-final head `07d84bbd6f2ac5e6ab28690c39308a403c8b75f5`: Tibia Client Reference run `30018706676` PASS.
- Earlier published implementation head `76eeae87d483ddfae5f141663c739a95cf4413c5`: AI Agent Tools run `30017906729` PASS.
- Historical ownership failures `30017905484`, `30018169688` and `30018357957` were lifecycle/checkpoint metadata failures and have been corrected; the fresh ownership run above is green.
- `ci:final-gate` was applied to PR #809 before this final task/checkpoint commit.

## UNKNOWN

- Exact client build/version and selected files for future proprietary packages remain invocation evidence.
- Real proprietary-package smoke evidence remains optional external evidence and must stay outside Git.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: "2026-07-23T17:05:00+02:00"
head: "07d84bbd6f2ac5e6ab28690c39308a403c8b75f5"
branch: "feat/tcr-001-client-package-manifest-20260723"
pr: "809"
status: "validating"
context_routes:
  - "agent-governance"
  - "otbm"
  - "real-tibia-parity"
owned_paths:
  - "docs/agents/tasks/active/CAN-20260723-tcr-001-client-package-manifest.md"
  - "tools/ai-agent/tibia_client_reference_manifest.py"
  - "tools/ai-agent/tibia_client_reference_manifest_tool.py"
  - "tools/ai-agent/test_tibia_client_reference_manifest.py"
  - "docs/ai-agent/TIBIA_CLIENT_REFERENCE_MANIFEST.md"
  - "docs/ai-agent/TIBIA_CLIENT_REFERENCE_MANIFEST.schema.json"
  - ".github/workflows/tibia-client-reference.yml"
  - "docs/ai-agent/OTBM_TIBIA_CLIENT_REFERENCE_ARCHITECTURE.md"
  - "docs/agents/programs/OTBM_TIBIA_CLIENT_REFERENCE_PROGRAM.md"
  - "docs/agents/MODULE_CATALOG.md"
  - "docs/agents/CHANGELOG.md"
proven:
  - "Pre-final head 07d84bbd6f2ac5e6ab28690c39308a403c8b75f5 passed Agent Task Ownership 30018708498, repository CI 30018709068 and Tibia Client Reference 30018706676."
  - "Earlier implementation head 76eeae87d483ddfae5f141663c739a95cf4413c5 passed AI Agent Tools 30017906729."
  - "ci:final-gate was applied to PR 809 before this final checkpoint commit."
derived:
  - "No further feature-branch commit is allowed after the exact final-head gate turns green; the next code-state transition is readiness and squash merge if all gates pass."
unknown:
  - "Exact future proprietary package build and selected files remain invocation evidence."
conflicts: []
first_failure:
  marker: "none"
  evidence: "Historical lifecycle metadata failures are corrected; exact-final-head validation is now the remaining gate."
rejected_hypotheses:
  - "Rejected: TCR-001 needs a new module record; otbm-tooling already owns the scope."
  - "Rejected: filenames/directories prove client build; explicit evidence state remains mandatory."
  - "Rejected: OWA-003 may consume planned later TCR indexes before merge; only individually merged/stable producer contracts may be consumed."
changed_paths:
  - ".github/workflows/tibia-client-reference.yml"
  - "docs/agents/tasks/active/CAN-20260723-tcr-001-client-package-manifest.md"
  - "docs/ai-agent/TIBIA_CLIENT_REFERENCE_MANIFEST.md"
  - "docs/ai-agent/TIBIA_CLIENT_REFERENCE_MANIFEST.schema.json"
  - "tools/ai-agent/test_tibia_client_reference_manifest.py"
  - "tools/ai-agent/tibia_client_reference_manifest.py"
  - "tools/ai-agent/tibia_client_reference_manifest_tool.py"
validation:
  - command: "GitHub Actions Agent Task Ownership"
    result: "PASS"
    evidence: "run 30018708498 on pre-final head 07d84bbd6f2ac5e6ab28690c39308a403c8b75f5"
  - command: "GitHub Actions repository CI"
    result: "PASS"
    evidence: "run 30018709068 on pre-final head 07d84bbd6f2ac5e6ab28690c39308a403c8b75f5"
  - command: "GitHub Actions Tibia Client Reference"
    result: "PASS"
    evidence: "run 30018706676 on pre-final head 07d84bbd6f2ac5e6ab28690c39308a403c8b75f5"
  - command: "GitHub Actions AI Agent Tools"
    result: "PASS"
    evidence: "run 30017906729 on implementation head 76eeae87d483ddfae5f141663c739a95cf4413c5; exact-final-head rerun required"
blockers: []
next_action: "Verify all exact-final-head workflows for PR #809, then mark ready and squash-merge without another feature-branch commit if every required gate is green."
```
