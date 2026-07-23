---
task_id: CAN-20260723-tcr-001-client-package-manifest
program_id: CAN-PROGRAM-OTBM-TIBIA-CLIENT-REFERENCE
coordination_id: OTBM-TIBIA-CLIENT-REFERENCE
status: implementing
agent: GPT-5.6 Thinking
branch: feat/tcr-001-client-package-manifest-20260723
base_branch: main
created: 2026-07-23T16:48:37+02:00
updated: 2026-07-23T17:02:20+02:00
last_verified_commit: "16d0f28344163a08bfc41df10aacb1abc1ad592c"
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
- [ ] Finish narrow discovery/program updates and exact-final-head CI before merge.
- [x] No proprietary client input committed; no TCR-002/TCR-003 implementation.

# Evidence

## PROVEN

- TCR-000 delivery PR #762 merged as `d5a08db0502fb85ff807c9c18f02bf92bd1faaed`; lifecycle PR #808 merged as `014f156a8df4f7910a206f104c24842f3748cf99`.
- No equivalent manifest implementation or competing TCR-001 PR existed at preflight.
- Existing `otbm-tooling` registry already owns client-reference manifest/index correlation and `test_tibia_client_reference*.py`.
- Isolated prototype: 12 focused tests PASS and `py_compile` PASS.
- Dedicated Tibia Client Reference run `30017905949` PASS on published head `76eeae87d483ddfae5f141663c739a95cf4413c5`.
- First ownership run `30017905484` failed only because checkpoint `pr` was empty.
- Second ownership run `30018169688` failed only because frontmatter used unsupported active-task status `active`; repository `ACTIVE_STATUSES` requires `planned|implementing|blocked|review|ready`.
- Third ownership run `30018357957` failed only because checkpoint field `derived` was missing; artifact `active-task-ownership` recorded the exact error.

## UNKNOWN

- Exact client build/version and selected files for future proprietary packages remain invocation evidence.
- Real proprietary-package smoke evidence remains optional external evidence and must stay outside Git.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: "2026-07-23T17:02:20+02:00"
head: "16d0f28344163a08bfc41df10aacb1abc1ad592c"
branch: "feat/tcr-001-client-package-manifest-20260723"
pr: "809"
status: "implementing"
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
  - "Tibia Client Reference run 30017905949 PASS on 76eeae87d483ddfae5f141663c739a95cf4413c5."
  - "Ownership failures 30017905484, 30018169688 and 30018357957 are checkpoint/frontmatter metadata failures, not implementation-path conflicts."
derived:
  - "After restoring the required derived checkpoint field, the remaining bounded work is discovery/program integration and final-head validation."
unknown:
  - "Exact future proprietary package build and selected files remain invocation evidence."
conflicts: []
first_failure:
  marker: "Agent Task Ownership lifecycle metadata"
  evidence: "run 30018357957 artifact CHANGED_TASK_VALIDATION.txt: missing checkpoint field derived; corrected in this commit"
rejected_hypotheses:
  - "Rejected: TCR-001 needs a new module record; otbm-tooling already owns the scope."
  - "Rejected: filenames/directories prove client build; explicit evidence state remains mandatory."
changed_paths:
  - ".github/workflows/tibia-client-reference.yml"
  - "docs/agents/tasks/active/CAN-20260723-tcr-001-client-package-manifest.md"
  - "docs/ai-agent/TIBIA_CLIENT_REFERENCE_MANIFEST.md"
  - "docs/ai-agent/TIBIA_CLIENT_REFERENCE_MANIFEST.schema.json"
  - "tools/ai-agent/test_tibia_client_reference_manifest.py"
  - "tools/ai-agent/tibia_client_reference_manifest.py"
  - "tools/ai-agent/tibia_client_reference_manifest_tool.py"
validation:
  - command: "isolated focused unittest + py_compile"
    result: "PASS"
    evidence: "12 tests PASS; py_compile PASS before publication"
  - command: "GitHub Actions Tibia Client Reference"
    result: "PASS"
    evidence: "run 30017905949 on head 76eeae87d483ddfae5f141663c739a95cf4413c5"
  - command: "GitHub Actions Agent Task Ownership"
    result: "FAIL"
    evidence: "run 30018357957 on f5b971178b0ed6e60648b876b7461edc2a0c708c; missing required checkpoint field derived; corrected here"
blockers: []
next_action: "Verify fresh ownership and broad tool/CI checks, then complete narrow discovery/program integration and final-gate validation without starting TCR-002/TCR-003."
```
