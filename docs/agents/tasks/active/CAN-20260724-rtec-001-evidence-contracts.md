---
task_id: CAN-20260724-rtec-001-evidence-contracts
program_id: CAN-PROGRAM-REAL-TIBIA-EVIDENCE-COLLECTION
coordination_id: RTEC-001
status: active
agent: "GPT-5.6 Thinking"
branch: feat/rtec-001-evidence-contracts-20260724
base_branch: main
created: 2026-07-24T21:45:37+02:00
updated: 2026-07-24T22:35:00+02:00
last_verified_commit: "7932c0361a4764967fe8c9c036c1c5c5c680062f"
risk: medium
related_issue: ""
related_pr: "897"
depends_on:
  - RTEC-000
blocks:
  - RTEC-002
  - RTEC-003
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260724-rtec-001-evidence-contracts.md
    - docs/agents/programs/REAL_TIBIA_EVIDENCE_COLLECTION_PROGRAM.md
    - docs/agents/templates/REAL_TIBIA_EVIDENCE_RECORD.yaml
    - docs/agents/templates/REAL_TIBIA_EVIDENCE_REQUEST.yaml
    - docs/agents/real-tibia/evidence/**
    - tools/agents/real_tibia_evidence.py
    - tools/agents/real_tibia_evidence_lib.py
    - tools/agents/real_tibia_evidence_test_support.py
    - tools/agents/test_real_tibia_evidence.py
    - tools/agents/test_real_tibia_evidence_lifecycle.py
    - .github/workflows/real-tibia-evidence.yml
  shared:
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - AGENTS.md
    - docs/agents/REPOSITORY_MAP.md
    - docs/agents/CONTEXT_ROUTING.md
    - docs/agents/REAL_TIBIA_EVIDENCE_SOURCES.md
    - docs/agents/REAL_TIBIA_PARITY_PLAYBOOK.md
    - docs/agents/programs/REAL_TIBIA_PARITY_PROGRAM.md
    - docs/ai-agent/REAL_TIBIA_EVIDENCE_COLLECTOR_ARCHITECTURE.md
    - docs/agents/real-tibia/registry/**
    - tools/agents/real_tibia_registry.py
    - tools/agents/real_tibia_registry_lib.py
    - tools/agents/test_real_tibia_registry.py
    - tools/e2e/**
    - tools/ai-agent/otbm_*
    - tools/ai-agent/tibia_*
modules_touched:
  - real-tibia-evidence-collection
  - platform-tooling
reuses:
  - canary-real-tibia-module-registry
  - CAN-PROGRAM-E2E-PLATFORM
  - CAN-PROGRAM-OTBM-WORLD-ASSURANCE-OPERATIONS
  - CAN-PROGRAM-OTBM-TIBIA-CLIENT-REFERENCE
public_interfaces:
  - canary-real-tibia-evidence-record-v1
  - canary-real-tibia-owner-request-v1
  - canary-real-tibia-module-evidence-index-v1
  - canary-real-tibia-version-history-v1
  - canary-real-tibia-generated-indexes-v1
cross_repo_tasks: []
---

# Goal

Implement the versioned evidence, owner-request, module-index and version-history contracts plus a deterministic fail-closed validator/generator required before Real Tibia module dossiers may be populated at scale.

# Acceptance criteria

- [x] Publish strict version-1 Draft 2020-12 contracts for evidence records, owner requests, module evidence indexes, version history and generated factual indexes.
- [x] Validate canonical module IDs against the existing 62-module registry without creating another registry or a 63rd module.
- [x] Validate stable IDs, file placement, claim boundaries, proof levels, source locators, separate version axes, references, conflicts, freshness and supersession.
- [x] Reject duplicate evidence/request/history IDs, unsafe paths, symlink escapes, malformed SHA-256/commit/date/version values and unknown enum values.
- [x] Reject static/lower-proof promotion into gameplay or physical-client proof.
- [x] Validate owner-request lifecycle transitions and require owner evidence for owner-controlled states.
- [x] Reject missing references and supersession/dependency cycles.
- [x] Generate deterministic factual indexes atomically and independent of filesystem/input ordering.
- [x] Generate only evidence-by-module, authority, version-axis, unresolved-conflict, stale, active-request, superseded and independent proof-maturity facts.
- [x] Add focused positive/negative tests for malformed, conflicting, stale, duplicate, unsafe and ordering cases.
- [x] Keep external/proprietary artifacts outside Git and forbid committed artifact payloads.
- [x] Keep gameplay/runtime/client/protocol/database/map/datapack behavior unchanged.
- [ ] Complete current-head CI, full diff review, `ci:final-gate`, readiness and squash merge.
- [ ] Verify post-merge lifecycle archival.

# Confirmed context and boundaries

- Branch was created from exact `main@93413bd53e9a40f0ff3c4f55986036b10be44e0f` after refreshing main, open PRs, active tasks and programme state.
- RTEC-000 is merged and archived; no overlapping RTEC schema/validator/index task or PR was found.
- PR #885 owns only Universal E2E dashboard paths and remains read-only.
- The existing Real Tibia registry remains the sole canonical module-ID registry.
- Universal E2E, OTBM/OWA, TCR, protocol/client and feature programmes retain execution/result ownership.
- No Collector worker or module dossier population may start before RTEC-001 merges.
- No runtime, gameplay, protocol, client, map, datapack or database behavior is changed.

# Implemented contracts

1. `canary-real-tibia-evidence-record-v1`
2. `canary-real-tibia-owner-request-v1`
3. `canary-real-tibia-module-evidence-index-v1`
4. `canary-real-tibia-version-history-v1`
5. `canary-real-tibia-generated-indexes-v1`

All use `schema_version: 1`. `.yaml` records use the YAML 1.2 JSON-compatible subset so the Python 3.12 standard-library runtime can reject duplicate keys and unknown structure without implicit YAML normalization.

# Implemented validation and generation

- Fail-closed source-tree audit, UTF-8/stable-read/size checks, safe path validation and symlink-escape rejection.
- Exact stable IDs and canonical file placement for evidence, requests and history.
- Canonical module lookup from `docs/agents/real-tibia/registry/modules` read-only.
- Explicit authority, evidence-state, proof-level, source-type, `proves`, `does_not_prove`, confidence and uncertainty validation.
- Source proof caps and rejection of static/lower proof promotion to gameplay or physical-client proof.
- Exact source URL/path/SHA/build/report/artifact-hash locators and outside-Git artifact retention.
- Separate version lifecycle cells and separate official release/client build/protocol/commit/map/datapack/appearance/sidecar/database axes.
- Derived/bounded/unknown ranges when exact first version is not proven.
- Cross-record references, reciprocal supersession and cycle validation.
- Owner request routes and legal state transitions with owner evidence required for owner-controlled states.
- Deterministic atomic generation using sorted facts, temporary files, `fsync` and `os.replace`.
- Factual indexes only: module, authority, version axis, conflict, stale, active request, superseded and independent proof maturity.

# Validation

```text
python -m py_compile tools/agents/real_tibia_evidence.py tools/agents/real_tibia_evidence_lib.py tools/agents/real_tibia_evidence_test_support.py tools/agents/test_real_tibia_evidence.py tools/agents/test_real_tibia_evidence_lifecycle.py
PASS

python -m unittest discover -v -s tools/agents -p 'test_real_tibia_evidence*.py'
PASS: 22 tests

python tools/agents/real_tibia_evidence.py validate --as-of 2026-07-24
PASS: evidence corpus valid (0 evidence, 0 requests, 0 history events)

python tools/agents/real_tibia_evidence.py generate --check --as-of 2026-07-24
PASS
```

The dedicated workflow also runs the existing canonical registry validator and deterministic registry generation check on Python 3.12.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-24T22:35:00+02:00
head: 7932c0361a4764967fe8c9c036c1c5c5c680062f
branch: feat/rtec-001-evidence-contracts-20260724
pr: 897
status: implementation-published-draft-pr
context_routes:
  - agent-governance
  - real-tibia-parity
owned_paths:
  - docs/agents/tasks/active/CAN-20260724-rtec-001-evidence-contracts.md
  - docs/agents/programs/REAL_TIBIA_EVIDENCE_COLLECTION_PROGRAM.md
  - docs/agents/templates/REAL_TIBIA_EVIDENCE_RECORD.yaml
  - docs/agents/templates/REAL_TIBIA_EVIDENCE_REQUEST.yaml
  - docs/agents/real-tibia/evidence/**
  - tools/agents/real_tibia_evidence.py
  - tools/agents/real_tibia_evidence_lib.py
  - tools/agents/real_tibia_evidence_test_support.py
  - tools/agents/test_real_tibia_evidence.py
  - tools/agents/test_real_tibia_evidence_lifecycle.py
  - .github/workflows/real-tibia-evidence.yml
proven:
  - RTEC-000 is merged and archived.
  - PR 897 is open as a draft from the exact claimed base.
  - Five schema-version-1 contracts and the standard-library validator/generator are published.
  - Local compile, 22 focused tests, corpus validation and generated-index checks pass.
  - No module dossier, owner runner/parser or runtime behavior was added.
derived:
  - The empty generated index is the deterministic factual baseline until RTEC-002 creates the first bounded module records.
unknown:
  - Current-head GitHub Actions results and final review findings.
conflicts: []
first_failure:
  marker: local-checkout-dns
  evidence: sandbox could not resolve github.com; connector writes and bounded local tests were used
rejected_hypotheses:
  - Populate all module dossiers now: rejected because RTEC-001 stabilizes contracts first.
  - Reuse or edit Universal E2E, OTBM/OWA or TCR implementation paths: rejected because owners retain execution authority.
changed_paths:
  - .github/workflows/real-tibia-evidence.yml
  - docs/agents/real-tibia/evidence/**
  - docs/agents/templates/REAL_TIBIA_EVIDENCE_RECORD.yaml
  - docs/agents/templates/REAL_TIBIA_EVIDENCE_REQUEST.yaml
  - tools/agents/real_tibia_evidence.py
  - tools/agents/real_tibia_evidence_lib.py
  - tools/agents/real_tibia_evidence_test_support.py
  - tools/agents/test_real_tibia_evidence.py
  - tools/agents/test_real_tibia_evidence_lifecycle.py
validation:
  - command: local compile and focused unittest discovery
    result: PASS
    evidence: 22 tests passed
  - command: evidence validate and deterministic generate --check
    result: PASS
    evidence: empty factual baseline valid at 2026-07-24
blockers: []
next_action: Update programme state, inspect the complete PR diff and current-head CI, then resolve findings before applying ci:final-gate.
```

# Handoff

Re-fetch PR #897 head, checks and changed files before any edit. Do not create module dossiers, owner execution tooling, an alternate registry, an E2E runner, an OTBM parser/index/pathfinder/renderer/certifier or a TCR/client-package parser.
