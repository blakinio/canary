---
task_id: CAN-20260723-tcr-001-client-package-manifest
program_id: CAN-PROGRAM-OTBM-TIBIA-CLIENT-REFERENCE
coordination_id: OTBM-TIBIA-CLIENT-REFERENCE
status: active
agent: GPT-5.6 Thinking
branch: feat/tcr-001-client-package-manifest-20260723
base_branch: main
created: 2026-07-23T16:48:37+02:00
updated: 2026-07-23T16:48:37+02:00
last_verified_commit: "014f156a8df4f7910a206f104c24842f3748cf99"
risk: medium
related_issue: ""
related_pr: ""
depends_on:
  - docs/ai-agent/OTBM_TIBIA_CLIENT_REFERENCE_ARCHITECTURE.md
  - docs/agents/programs/OTBM_TIBIA_CLIENT_REFERENCE_PROGRAM.md
  - docs/agents/REAL_TIBIA_EVIDENCE_SOURCES.md
  - docs/agents/REAL_TIBIA_PARITY_PLAYBOOK.md
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
    - tools/ai-agent/otbm_evidence_gateway.py
    - tools/ai-agent/otbm_evidence_gateway_tool.py
modules_touched:
  - OTBM analysis tooling
  - official-client reference evidence
reuses:
  - OTBM Tibia client reference architecture
  - existing SHA-256/path/symlink confinement patterns from OTBM Compact Evidence Gateway
  - existing create-new/atomic JSON output pattern from OTBM Compact Evidence Gateway
  - AI Agent Tools broad Python test workflow
public_interfaces:
  - canary-tibia-client-reference-manifest-v1
cross_repo_tasks: []
---

# Goal

Implement only TCR-001 — Client Package Manifest: a deterministic, fail-closed, read-only provenance manifest for explicitly selected files below one user-supplied Tibia client reference package root.

# Scope

Python 3.12 standard-library tooling, schema, focused tests, dedicated workflow and narrow discovery/program updates. No TCR-002/TCR-003/TCR-004 parser implementation, no recursive package ingestion, no execution of selected binaries/content, no OTBM or runtime mutation, and no proprietary client files committed.

# Acceptance criteria

- [ ] Emit `canary-tibia-client-reference-manifest-v1` with one explicit package root identity label, stable `referenceId`, explicit source role, explicit observed timestamp metadata and exact parser revision.
- [ ] Require 1..128 explicitly selected safe relative files below the package root; reject missing files, directories, absolute/path-escape paths, symlink roots/components and duplicate logical/resolved inputs.
- [ ] Record byte size and SHA-256 for every selected input after enforcing an explicit per-file size bound before hashing.
- [ ] Preserve client-build evidence exactly as `proven`, `declared`, `unknown` or `conflicting`; never infer a build from filenames or directory labels.
- [ ] Accept optional generated-index SHA-256 pins without opening arbitrary generated-index paths.
- [ ] Produce deterministic JSON for stable files and explicit arguments; do not synthesize a current timestamp.
- [ ] Default to create-new/no-clobber output; reject output symlinks and selected-input aliases; use atomic replacement only when overwrite is explicit.
- [ ] Add focused unit tests, `py_compile`, JSON schema syntax validation and a dedicated workflow; retain broad AI Agent Tools coverage.
- [ ] Update architecture/program/catalogue/changelog narrowly without claiming TCR-001 stable/merged before the delivery PR merges.
- [ ] Keep all user-supplied client files and proprietary assets outside Git.

# Evidence baseline

## PROVEN

- TCR-000 architecture/governance merged in PR #762 as `d5a08db0502fb85ff807c9c18f02bf92bd1faaed` and its lifecycle archived in PR #808 as `014f156a8df4f7910a206f104c24842f3748cf99`.
- Current task baseline is `main` at `014f156a8df4f7910a206f104c24842f3748cf99`.
- No existing repository implementation of `canary-tibia-client-reference-manifest-v1` was found in the bounded preflight.
- No open PR implementing TCR-001 was found in the bounded preflight.
- The existing `otbm-tooling` registry record already includes Tibia client reference manifest/index correlation and `tools/ai-agent/test_tibia_client_reference*.py`; no new module/taxonomy is required.
- OTBM Compact Evidence Gateway provides existing standard-library patterns for SHA-256, safe relative paths, symlink rejection and create-new/atomic JSON output that TCR-001 should reuse by convention rather than inventing incompatible behavior.
- OWA-001 PR #801 does not currently change the TCR-001 owned implementation paths.
- An isolated pre-publication prototype passed 11 focused unit tests and `py_compile`; exact repository-head validation remains required after publication.

## UNKNOWN / deferred

- Exact client build/version for any future user-supplied package remains unknown unless separately proven or declared at invocation time.
- Exact real package file selection remains operator/task input and must not be inferred recursively.
- Real proprietary-package smoke evidence is optional external evidence and is not required to commit or expose proprietary files.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: "2026-07-23T16:48:37+02:00"
head: "014f156a8df4f7910a206f104c24842f3748cf99"
branch: "feat/tcr-001-client-package-manifest-20260723"
pr: ""
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
  - "TCR-000 delivery PR 762 merged as d5a08db0502fb85ff807c9c18f02bf92bd1faaed."
  - "TCR-000 lifecycle PR 808 merged as 014f156a8df4f7910a206f104c24842f3748cf99."
  - "No equivalent canary-tibia-client-reference-manifest-v1 implementation or open TCR-001 implementation PR was found in bounded preflight."
  - "Existing otbm-tooling registry scope already covers client-reference manifest/index correlation and planned test glob."
  - "Isolated prototype: 11 focused tests PASS and py_compile PASS; not yet exact repository-head evidence."
derived:
  - "TCR-001 can remain inside the existing otbm-tooling module and should reuse established path/hash/output safety conventions."
unknown:
  - "Exact build/version and selected files for future proprietary user packages remain invocation evidence, not repository assumptions."
conflicts: []
first_failure:
  marker: "none"
  evidence: "No implementation or CI failure exists yet; exact-head validation begins after publication."
rejected_hypotheses:
  - "Rejected: TCR-001 requires a new Real Tibia module record; otbm-tooling already owns the scope."
  - "Rejected: a client package directory or filename proves an exact Tibia build; architecture requires explicit evidence state."
changed_paths:
  - "docs/agents/tasks/active/CAN-20260723-tcr-001-client-package-manifest.md"
validation:
  - command: "isolated prototype focused unittest"
    result: "PASS"
    evidence: "11 focused tests passed before repository publication; exact published-head rerun required"
  - command: "isolated prototype py_compile"
    result: "PASS"
    evidence: "three prototype Python files compiled before repository publication; exact published-head rerun required"
blockers: []
next_action: "Open an early draft PR from the dedicated task branch, then publish the bounded TCR-001 manifest implementation, schema, tests and workflow without starting TCR-002/TCR-003."
```
