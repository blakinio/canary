---
task_id: CAN-20260723-owa-004-runtime-incident-otbm-evidence-bridge
program_id: CAN-PROGRAM-OTBM-WORLD-ASSURANCE-OPERATIONS
coordination_id: OWA-004
status: implementing
agent: "GPT-5.6 Thinking"
branch: feat/owa-004-runtime-incident-evidence-bridge-20260723
base_branch: main
created: 2026-07-23T19:55:32+02:00
updated: 2026-07-23T19:57:00+02:00
last_verified_commit: "ef434d829409b0808357cf067a7a39b24961f3c8"
risk: medium
related_issue: ""
related_pr: "838"
depends_on:
  - "OWA-002 lifecycle PR #834"
  - "QA-018 Compact Evidence Gateway"
  - "existing OTBM route/preflight/failure-triage evidence contracts"
blocks:
  - "OWA-004 lifecycle closure and programme queue advance"
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260723-owa-004-runtime-incident-otbm-evidence-bridge.md
    - docs/ai-agent/OTBM_RUNTIME_INCIDENT_EVIDENCE_BRIDGE.md
    - docs/ai-agent/OTBM_RUNTIME_INCIDENT_EVIDENCE_BINDINGS.schema.json
    - docs/ai-agent/OTBM_RUNTIME_INCIDENT_EVIDENCE_BRIDGE.schema.json
    - tools/ai-agent/otbm_runtime_incident_evidence_bridge.py
    - tools/ai-agent/otbm_runtime_incident_evidence_bridge_tool.py
    - tools/ai-agent/test_otbm_runtime_incident_evidence_bridge.py
    - tools/ai-agent/test_otbm_runtime_incident_evidence_bridge_output_safety.py
    - tools/ai-agent/test_otbm_runtime_incident_evidence_bridge_schema.py
  shared:
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - AGENTS.md
    - docs/agents/REPOSITORY_MAP.md
    - docs/agents/CONTEXT_ROUTING.md
    - docs/agents/programs/OTBM_WORLD_ASSURANCE_OPERATIONS_PROGRAM.md
    - docs/ai-agent/OTBM_WORLD_ASSURANCE_OPERATIONS_ROADMAP.md
    - docs/ai-agent/OTBM_EVIDENCE_GATEWAY.md
    - tools/ai-agent/otbm_evidence_gateway.py
    - tools/e2e/otbm_route_failure_triage.py
cross_repo_tasks: []
---

# Goal

Implement `OWA-004 — Runtime Incident to OTBM Evidence Bridge` as a bounded deterministic bridge from one explicit reviewed incident selector to an exact QA-018 evidence bundle over existing OTBM reports.

The bridge must not parse logs or reinterpret source-report semantics. It resolves an exact reviewed selector binding, composes the existing `canary-otbm-evidence-gateway-manifest-v1` source/extract specification, and delegates extraction to the canonical QA-018 `build_evidence_bundle()` implementation.

# Supported v1 selector classes

Exactly one selector per request:

- `position` — exact `[x,y,z]`;
- `transition-id` — exact non-empty transition identifier;
- `interaction-id` — exact non-empty route-interaction identifier;
- `landmark-id` — exact non-empty semantic landmark identifier;
- `route-id` — exact non-empty route identifier;
- `preflight-reference` — exact non-empty reviewed preflight reference.

Bindings are reviewed static metadata. The bridge never discovers a selector from free-form logs, error text, screenshots or runtime telemetry.

# Planned public contracts

- `canary-otbm-runtime-incident-evidence-bindings-v1` — reviewed unique selector bindings to exact QA-018-compatible source/extract specifications and optional opaque downstream context references;
- `canary-otbm-runtime-incident-evidence-v1` — selected binding plus the exact embedded `canary-otbm-evidence-bundle-v1`, deterministic provenance and explicit no-diagnosis policy flags.

# Hard boundaries

The package must not:

- parse OTBM or rebuild the World Index;
- parse arbitrary runtime logs or infer incident selectors;
- classify root cause or replace `canary-otbm-e2e-failure-triage-v1`;
- reinterpret or validate source-report semantics beyond QA-018's existing exact hash/format/pointer checks;
- pathfind or regenerate routes/preflight;
- execute Physical E2E;
- emit `NEXT_ACTION` or automated repair instructions;
- mutate maps, reports, assets or datapacks;
- commit generated evidence bundles or proprietary inputs.

# Acceptance criteria

- [ ] exact selector bindings are deterministic and unique;
- [ ] unsupported, missing and ambiguous selectors fail closed;
- [ ] source/extract specifications are normalized by the existing QA-018 contract;
- [ ] actual extraction delegates to `otbm_evidence_gateway.build_evidence_bundle()`;
- [ ] exact source SHA-256, format and JSON Pointer mismatches retain QA-018 fail-closed behavior;
- [ ] output retains the selected binding ID, selector and exact QA-018 bundle hash;
- [ ] optional failure-triage references remain opaque references and do not trigger reclassification;
- [ ] plan-only mode can emit the exact QA-018 manifest without reading evidence sources;
- [ ] executed mode produces deterministic output for identical exact inputs;
- [ ] create-new/no-clobber, explicit atomic overwrite, symlink/path/input-output collision protections pass focused tests;
- [ ] schemas and documentation are delivered;
- [ ] `MODULE_CATALOG.md` and `CHANGELOG.md` receive one narrow reusable/public-interface entry each;
- [ ] no `.otbm`, `.widx`, generated evidence bundle, render or proprietary asset is committed;
- [ ] exact final head passes Agent Task Ownership, OTBM Map Tools, AI Agent Tools and repository CI before merge.

# Preflight evidence

- fresh `main` at task claim: `c35ba8dc2b684559f996e12bf4bdc1aa34321a7f`;
- OWA-002 feature PR #817 and lifecycle PR #834 are merged;
- programme queue marks OWA-004 `ready for next bounded task`;
- no OWA-004 task or PR was found;
- current open PR inventory has no owner of the declared OWA-004 exclusive paths;
- TCR-002 remains draft/open and stable TCR parity/drift producer outputs required by OWA-003 are not yet available, so OWA-003 remains blocked;
- QA-018 already owns safe relative paths, exact source SHA-256 and format validation, JSON Pointer extraction, extraction size limits, deterministic source/extract ordering and `canary-otbm-evidence-bundle-v1` hashing;
- existing `tools/e2e/otbm_route_failure_triage.py` owns deterministic OTBM Physical E2E failure classification and remains read-only/downstream from this bridge.

# Reuse decision

`PROVEN`: use QA-018 `normalize_manifest()` and `build_evidence_bundle()` as the only source extraction implementation.

`REJECTED`: a generic log parser, fuzzy selector matcher, report-semantic interpreter, root-cause engine or duplicate evidence extractor would violate programme boundaries and duplicate canonical ownership.

`DERIVED`: reviewed selector-to-extract bindings are the narrowest safe bridge because they make runtime-origin selectors explicit while leaving evidence extraction and runtime diagnosis with their existing owners.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-23T17:57:00Z
head: ef434d829409b0808357cf067a7a39b24961f3c8
branch: feat/owa-004-runtime-incident-evidence-bridge-20260723
pr: 838
status: implementing
context_routes:
  - agent-governance
  - otbm
owned_paths:
  - docs/agents/tasks/active/CAN-20260723-owa-004-runtime-incident-otbm-evidence-bridge.md
  - docs/ai-agent/OTBM_RUNTIME_INCIDENT_EVIDENCE_BRIDGE.md
  - docs/ai-agent/OTBM_RUNTIME_INCIDENT_EVIDENCE_BINDINGS.schema.json
  - docs/ai-agent/OTBM_RUNTIME_INCIDENT_EVIDENCE_BRIDGE.schema.json
  - tools/ai-agent/otbm_runtime_incident_evidence_bridge.py
  - tools/ai-agent/otbm_runtime_incident_evidence_bridge_tool.py
  - tools/ai-agent/test_otbm_runtime_incident_evidence_bridge.py
  - tools/ai-agent/test_otbm_runtime_incident_evidence_bridge_output_safety.py
  - tools/ai-agent/test_otbm_runtime_incident_evidence_bridge_schema.py
proven:
  - QA-018 already provides exact hash/format/pointer-validated bounded evidence extraction and deterministic canary-otbm-evidence-bundle-v1 output.
  - Existing OTBM route failure triage owns runtime failure classification and OWA-004 must not replace it.
  - No OWA-004 task or PR and no exclusive-path collision was found in the fresh preflight.
  - Draft PR 838 is open for the claimed branch.
derived:
  - A reviewed unique selector-to-QA018-source/extract binding is sufficient to bridge explicit incident context to compact static evidence without log parsing or semantic reinterpretation.
unknown:
  - Exact final public schema shape until focused implementation/tests settle normalization details.
conflicts:
  - none
first_failure:
  marker: none
  evidence: no implementation validation has run yet.
rejected_hypotheses:
  - Parse arbitrary runtime logs to discover selectors.
  - Reclassify Physical E2E failures inside OWA-004.
  - Add a second evidence extraction implementation instead of QA-018.
changed_paths:
  - docs/agents/tasks/active/CAN-20260723-owa-004-runtime-incident-otbm-evidence-bridge.md
validation: []
blockers:
  - Implementation and exact-head validation remain.
next_action: Implement the reviewed selector binding resolver and direct QA-018 evidence-bundle delegation on the claimed exclusive paths, then add focused fail-closed/output-safety/schema tests.
```
