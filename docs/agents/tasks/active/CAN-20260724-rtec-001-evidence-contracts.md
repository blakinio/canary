---
task_id: CAN-20260724-rtec-001-evidence-contracts
program_id: CAN-PROGRAM-REAL-TIBIA-EVIDENCE-COLLECTION
coordination_id: RTEC-001
status: active
agent: "GPT-5.6 Thinking"
branch: feat/rtec-001-evidence-contracts-20260724
base_branch: main
created: 2026-07-24T21:45:37+02:00
updated: 2026-07-24T21:45:37+02:00
last_verified_commit: "93413bd53e9a40f0ff3c4f55986036b10be44e0f"
risk: medium
related_issue: ""
related_pr: ""
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
    - tools/agents/test_real_tibia_evidence.py
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

Implement the versioned machine-readable evidence, owner-request, module-index and version-history contracts plus a deterministic fail-closed validator/generator required before Real Tibia module dossiers may be populated at scale.

# Acceptance criteria

- [ ] Publish strict version-1 JSON Schema contracts for evidence records, owner requests, module evidence indexes, version history and generated factual indexes.
- [ ] Validate canonical module IDs against the existing 62-module registry without creating another registry or a 63rd module.
- [ ] Validate stable IDs, file placement, claim boundaries, proof levels, source locators, separate version axes, references, conflicts, freshness and supersession.
- [ ] Reject duplicate evidence/request/history IDs, unsafe paths, symlink escapes, malformed SHA-256/commit/date/version values and unknown enum values.
- [ ] Reject static/lower-proof promotion into gameplay or physical-client proof.
- [ ] Validate owner-request lifecycle transitions and require owner evidence for owner-controlled states.
- [ ] Reject missing references and supersession cycles.
- [ ] Generate deterministic factual indexes atomically and independent of filesystem/input ordering.
- [ ] Generate only evidence-by-module, authority, version-axis, unresolved-conflict, stale, active-request, superseded and independent proof-maturity facts.
- [ ] Add focused positive/negative tests for malformed, conflicting, stale, duplicate, unsafe and ordering cases.
- [ ] Keep external/proprietary artifacts outside Git and forbid committed artifact payloads.
- [ ] Keep gameplay/runtime/client/protocol/database/map/datapack behavior unchanged.
- [ ] Run exact applicable checks, review the complete diff, apply `ci:final-gate`, and merge only after current-head checks pass.

# Confirmed context

- `main` was refreshed to `93413bd53e9a40f0ff3c4f55986036b10be44e0f` before branch creation.
- RTEC-000 architecture is merged and its lifecycle task is archived.
- RTEC-001 is the first planned unimplemented package in the programme queue.
- The existing Real Tibia registry owns canonical module IDs and deterministic registry indexes.
- Universal E2E, OTBM/OWA, TCR, protocol/client and feature programmes retain execution and result ownership; this task only validates requests and consumes explicit references.

# Ownership and overlap check

- Open PRs were refreshed before branch creation.
- No open PR or active task matching RTEC-001 evidence/request schema, validator or generated-index ownership was found.
- PR #885 owns only Universal E2E coverage-dashboard paths and remains read-only for this task.
- Shared programme and generated-index paths are coordinator-exclusive for RTEC-001.
- No Collector module worker may start until this contract package merges.

# Design constraints

1. Use Python 3.12 standard library for runtime validation/generation.
2. Treat `.yaml` records as the YAML 1.2 JSON-compatible subset and reject duplicate JSON object keys.
3. Keep exact official release, client build, protocol profile, Canary commit, maintained OTClient commit, map SHA-256, datapack, appearances/items, spawn/NPC sidecar and database schema axes separate.
4. Preserve `UNKNOWN`, `CONFLICT`, `STALE`, `SUPERSEDED` and `REJECTED`; never normalize them into success.
5. Do not infer gameplay, physical-client or whole-game parity from static files, registrations, names or generated indexes.

# Planned changed paths

- `docs/agents/real-tibia/evidence/README.md`
- `docs/agents/real-tibia/evidence/schemas/*.schema.json`
- `docs/agents/real-tibia/evidence/generated/EVIDENCE_INDEXES.json`
- `docs/agents/templates/REAL_TIBIA_EVIDENCE_RECORD.yaml`
- `docs/agents/templates/REAL_TIBIA_EVIDENCE_REQUEST.yaml`
- `tools/agents/real_tibia_evidence.py`
- `tools/agents/real_tibia_evidence_lib.py`
- `tools/agents/test_real_tibia_evidence.py`
- `.github/workflows/real-tibia-evidence.yml`
- narrow programme/catalogue/changelog updates

# Validation plan

```text
python -m py_compile tools/agents/real_tibia_evidence.py tools/agents/real_tibia_evidence_lib.py tools/agents/test_real_tibia_evidence.py
python -m unittest -v tools/agents/test_real_tibia_evidence.py
python tools/agents/real_tibia_evidence.py validate
python tools/agents/real_tibia_evidence.py generate --check --as-of 2026-07-24
python tools/agents/real_tibia_registry.py validate
python tools/agents/real_tibia_registry.py generate --check
```

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-24T21:45:37+02:00
head: 93413bd53e9a40f0ff3c4f55986036b10be44e0f
branch: feat/rtec-001-evidence-contracts-20260724
pr: null
status: claimed
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
  - tools/agents/test_real_tibia_evidence.py
  - .github/workflows/real-tibia-evidence.yml
proven:
  - RTEC-000 is merged and archived.
  - Current main is 93413bd53e9a40f0ff3c4f55986036b10be44e0f.
  - No overlapping open RTEC schema/validator/index PR was found.
  - Existing registry tooling provides canonical module IDs and standard-library deterministic patterns.
derived:
  - A dedicated evidence validator can reuse registry records read-only without extending the registry contract.
unknown:
  - Final implementation diff and current-head CI results.
conflicts: []
first_failure:
  marker: local-checkout-dns
  evidence: sandbox could not resolve github.com; GitHub connector remains available
rejected_hypotheses:
  - Populate all module dossiers now: rejected because RTEC-001 must stabilize contracts first.
  - Reuse Universal E2E or OTBM paths for implementation: rejected because those owners remain read-only.
changed_paths:
  - docs/agents/tasks/active/CAN-20260724-rtec-001-evidence-contracts.md
validation:
  - command: startup repository/PR/task/architecture preflight
    result: PASS
    evidence: current main, open PRs, programme, architecture, templates and registry tooling inspected
blockers: []
next_action: Open the early draft PR, then implement schemas and the standard-library validator/generator.
```

# Handoff

Start from this task, the live PR, the evidence collection programme and Collector architecture. Re-fetch current head/PR/CI state before edits. Do not create module dossiers, owner execution tooling, an alternate registry, an E2E runner, an OTBM parser/index/pathfinder/renderer/certifier or a TCR parser.
