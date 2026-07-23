---
task_id: CAN-20260723-owa-001-real-world-certification-campaign
program_id: CAN-PROGRAM-OTBM-WORLD-ASSURANCE-OPERATIONS
coordination_id: OWA-001
status: ready
agent: "GPT-5.6 Thinking"
branch: feat/owa-001-real-world-certification-campaign-20260723
base_branch: main
created: 2026-07-23T15:53:12+02:00
updated: 2026-07-23T16:47:00+02:00
last_verified_commit: "924eaa0ad4f439351658cfcdc8943a3496f2d981"
risk: medium
related_issue: ""
related_pr: "801"
depends_on:
  - OTBM-QA-005 Coverage Dashboard
  - OTBM-QA-006 Region and Quest Certification
  - OTBM-QA-016 Release Provenance and Certification Freshness
  - OTBM-QA-018 Compact Evidence Gateway
  - Unified OTBM World Index
  - Semantic Landmark Registry
  - canonical OTBM Reachability and route preflight
  - retained Universal Physical E2E evidence
blocks:
  - OWA-002
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260723-owa-001-real-world-certification-campaign.md
    - tools/ai-agent/otbm_world_assurance_campaign.py
    - tools/ai-agent/otbm_world_assurance_campaign_tool.py
    - tools/ai-agent/test_otbm_world_assurance_campaign.py
    - tools/ai-agent/test_otbm_world_assurance_campaign_output_safety.py
    - tools/ai-agent/test_otbm_world_assurance_campaign_schema.py
    - docs/ai-agent/OTBM_WORLD_ASSURANCE_CAMPAIGN.md
    - docs/ai-agent/OTBM_WORLD_ASSURANCE_CAMPAIGN.schema.json
    - docs/ai-agent/OTBM_WORLD_ASSURANCE_CAMPAIGN_MANIFEST.schema.json
    - docs/ai-agent/OTBM_WORLD_ASSURANCE_CAMPAIGN_TARGETS.json
  shared:
    - docs/agents/programs/OTBM_WORLD_ASSURANCE_OPERATIONS_PROGRAM.md
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - AGENTS.md
    - docs/agents/README.md
    - docs/agents/REPOSITORY_MAP.md
    - docs/agents/CONTEXT_ROUTING.md
    - docs/ai-agent/OTBM_WORLD_ASSURANCE_OPERATIONS_ROADMAP.md
    - docs/ai-agent/OTBM_WORLD_QUALITY_REPAIR_ROADMAP.md
    - docs/ai-agent/OTBM_SEMANTIC_LANDMARKS.json
    - docs/ai-agent/OTBM_THAIS_LANDMARK_EVIDENCE.md
    - tools/ai-agent/otbm_coverage_dashboard.py
    - tools/ai-agent/otbm_region_quest_certification.py
    - tools/ai-agent/otbm_release_provenance.py
    - tools/ai-agent/otbm_evidence_gateway.py
    - tools/ai-agent/otbm_reachability*.py
    - tools/ai-agent/otbm_route_preflight.py
    - tests/e2e/routes/thais-temple-depot.json
    - tests/e2e/scenarios/movement/physical-thais-temple-depot.json
    - docs/agents/tasks/archive/CAN-20260719-otbm-e2e-005-thais-temple-depot.md
modules_touched:
  - OTBM world assurance campaign composition
  - OTBM QA evidence composition
reuses:
  - canary-otbm-coverage-dashboard-v1
  - canary-otbm-region-quest-certification-v1
  - canary-otbm-release-provenance-v1
  - canary-otbm-evidence-bundle-v1
  - canary-otbm-world-index-v1
  - canary-otbm-semantic-landmarks-v1
  - canary-otbm-e2e-route-plan-v1
  - canary-otbm-e2e-route-preflight-v1
  - Universal Physical E2E retained evidence
public_interfaces:
  - canary-otbm-world-assurance-campaign-manifest-v1
  - canary-otbm-world-assurance-campaign-v1
cross_repo_tasks: []
---

# Goal

Deliver the first reproducible reviewed OTBM world-assurance certification campaign over exact current-compatible evidence without creating parallel canonical QA infrastructure.

# Acceptance criteria

- [x] Add one reviewed target manifest with target ID/class, semantic definition, exact source-map and World Index provenance, route/preflight references and retained Physical E2E reference.
- [x] Compose existing QA-005, QA-006, QA-016 and QA-018 contracts without adding a parser, World Index, pathfinder, Script Resolution implementation, renderer or E2E runner.
- [x] Emit deterministic external campaign ledger/report data with explicit QA-005 dimensions, C0-C7, freshness, blockers and unresolved/conflicting evidence.
- [x] Fail closed on provenance mismatch, stale/not-current evidence, missing exact evidence and unsupported target composition.
- [x] Preserve region/landmark-route QA-006 C5 cap and separate static evidence, Physical E2E and candidate-change revalidation.
- [x] Keep generated campaign reports, `.otbm`, `.widx`, renders and proprietary assets outside Git.
- [x] Add focused determinism, provenance mismatch, stale evidence, blocker, output-safety, schema and exact-target tests.
- [x] Focused local checks completed.
- [x] Prefinal exact-current-main GitHub checks passed on `924eaa0ad4f439351658cfcdc8943a3496f2d981`.
- [x] Changed-file scope reviewed against current `main`; only the ten bounded OWA-001 files differ.
- [x] Post-merge lifecycle closure is explicitly required to archive this task and update programme queue/handoff plus discovery/changelog records.
- [ ] Final-head protected CI after `ci:final-gate`.
- [ ] Squash merge PR #801 and complete lifecycle closure.

# Confirmed campaign result

Target: `owa-001.thais-temple-to-depot` (`thais.temple -> thais.depot`), class `landmark-route`.

Exact provenance:

- source map SHA-256 `a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2`;
- World Index SHA-256 `6c22cd26d4414aa094af1d00be7f62190a441e270ee7a478b55449bf92e55e7a`.

Exact route/runtime evidence:

- origin `[32369,32241,7]`;
- destination `[32352,32226,7]`;
- route distance `59`;
- canonical route plan hash `0736a819ef656f9040ea14c51f1ab474beabe9e4da50435e1eb9e7fd0c28974b`;
- route preflight `passed`;
- transition IDs: none;
- route interactions: none;
- retained Physical E2E workflow run `29704821423`;
- retained artifact ID `8447816376`;
- artifact ZIP SHA-256 `131faa08eaaccdacda62788b2e173b0f9ecc422a62ecd4769e874e4d136aeb40`;
- exact runtime-map hash matches reviewed source map.

Current campaign state:

- QA-005 dimensions: all `not-evaluated`;
- QA-006: `C0_NOT_EVALUATED`;
- QA-016 static-route freshness: `current`;
- QA-016 route-level Physical E2E freshness: `current`;
- retained route-level Physical E2E: `proven`;
- target state: `blocked`.

Exact formal blockers:

- `QA005_LANDMARK_ROUTE_REQUIRES_REVIEWED_MECHANIC_IDS`;
- `QA005_NO_REVIEWED_MECHANIC_BINDING_FOR_PURE_MOVEMENT_ROUTE`;
- `QA006_REQUIRES_CANONICAL_QA005_TARGET`.

No alternative target was substituted because no stronger reviewed QA-005/QA-006 binding with equally exact current provenance was found. No coordinates, landmarks or mechanic IDs were invented.

# Implementation

- `tools/ai-agent/otbm_world_assurance_campaign.py`: deterministic read-only composition over supplied canonical QA reports, QA-016 freshness, QA-018 exact evidence extracts and retained artifact digests.
- `tools/ai-agent/otbm_world_assurance_campaign_tool.py`: create-new/no-clobber CLI with atomic overwrite.
- `docs/ai-agent/OTBM_WORLD_ASSURANCE_CAMPAIGN_TARGETS.json`: durable reviewed target manifest.
- `docs/ai-agent/OTBM_WORLD_ASSURANCE_CAMPAIGN*.schema.json`: manifest/report schemas.
- `docs/ai-agent/OTBM_WORLD_ASSURANCE_CAMPAIGN.md`: usage and exact OWA-001 outcome.
- focused tests cover deterministic output, exact provenance mismatch, stale QA-016, QA-018 hash mismatch, missing artifact digest, canonical C5 preservation, target-class cap, QA-006-to-QA-005 pinning, output safety and schemas.

Generated QA-016, QA-018 and campaign result artifacts remain outside Git.

# Validation

- Local focused suite: 14 tests passed.
- Repeated external campaign composition: byte-identical outputs.
- External generated report field `reportSha256`: `d5bda59b5a6f46695ed9d4037bbbdf5c825b3aae214e4430fd2580d2eb4fc86d`.
- Prefinal head `924eaa0ad4f439351658cfcdc8943a3496f2d981`, based on current `main` `b9414cadf0b9cce263b3e79c4ac4e3829ba53769`:
  - Agent Task Ownership: PASS;
  - OTBM Map Tools: PASS;
  - AI Agent Tools: PASS;
  - CI: PASS.
- PR #801 has no review threads or requested-change reviews and is mergeable.
- `ci:final-gate` applied before this final checkpoint commit.

# Decisions

- Physical route success is retained as route-level Physical E2E only and cannot manufacture QA-005 mechanic coverage.
- Formal certification remains C0 until a canonical reviewed QA-005 target exists and QA-006 consumes it.
- QA-016 freshness is explicit and hash/dependency based; timestamps are not proof.
- Generated campaign results stay external.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: "2026-07-23T16:47:00+02:00"
head: "924eaa0ad4f439351658cfcdc8943a3496f2d981"
branch: "feat/owa-001-real-world-certification-campaign-20260723"
pr: 801
status: ready
context_routes:
  - agent-governance
  - otbm
  - universal-e2e
owned_paths:
  - docs/agents/tasks/active/CAN-20260723-owa-001-real-world-certification-campaign.md
  - tools/ai-agent/otbm_world_assurance_campaign.py
  - tools/ai-agent/otbm_world_assurance_campaign_tool.py
  - tools/ai-agent/test_otbm_world_assurance_campaign.py
  - tools/ai-agent/test_otbm_world_assurance_campaign_output_safety.py
  - tools/ai-agent/test_otbm_world_assurance_campaign_schema.py
  - docs/ai-agent/OTBM_WORLD_ASSURANCE_CAMPAIGN.md
  - docs/ai-agent/OTBM_WORLD_ASSURANCE_CAMPAIGN.schema.json
  - docs/ai-agent/OTBM_WORLD_ASSURANCE_CAMPAIGN_MANIFEST.schema.json
  - docs/ai-agent/OTBM_WORLD_ASSURANCE_CAMPAIGN_TARGETS.json
proven:
  - "Exact reviewed route/static provenance is current on map a80de1dd... and World Index 6c22cd26...."
  - "Retained exact route-level Physical E2E artifact 8447816376 is available and proven."
  - "Formal QA-005 is not evaluated and QA-006 remains C0 because no reviewed mechanic binding exists for this pure-movement route."
  - "Prefinal ownership, OTBM Map Tools, AI Agent Tools and CI passed on current-main-integrated head 924eaa0a...."
derived:
  - "Route-level Physical E2E cannot independently raise QA-006 certification."
unknown: []
conflicts: []
first_failure:
  marker: "QA005_NO_REVIEWED_MECHANIC_BINDING_FOR_PURE_MOVEMENT_ROUTE"
  evidence: "The reviewed route has no transition IDs or interactions, while QA-005 landmark-route coverage requires reviewed mechanicIds."
rejected_hypotheses:
  - "Invent a synthetic mechanicId for the pure-movement route: rejected because QA-005 critical mechanic membership is reviewed evidence and may not be guessed."
  - "Promote retained route-level Physical E2E directly to QA-006 C5: rejected because QA-006 consumes contiguous canonical QA-005 dimensions and does not infer them from a successful walk."
changed_paths:
  - docs/agents/tasks/active/CAN-20260723-owa-001-real-world-certification-campaign.md
  - docs/ai-agent/OTBM_WORLD_ASSURANCE_CAMPAIGN.md
  - docs/ai-agent/OTBM_WORLD_ASSURANCE_CAMPAIGN.schema.json
  - docs/ai-agent/OTBM_WORLD_ASSURANCE_CAMPAIGN_MANIFEST.schema.json
  - docs/ai-agent/OTBM_WORLD_ASSURANCE_CAMPAIGN_TARGETS.json
  - tools/ai-agent/otbm_world_assurance_campaign.py
  - tools/ai-agent/otbm_world_assurance_campaign_tool.py
  - tools/ai-agent/test_otbm_world_assurance_campaign.py
  - tools/ai-agent/test_otbm_world_assurance_campaign_output_safety.py
  - tools/ai-agent/test_otbm_world_assurance_campaign_schema.py
validation:
  - command: "focused OWA-001 unittest suite"
    result: PASS
    evidence: "14 tests passed"
  - command: "external campaign run repeated with exact evidence"
    result: PASS
    evidence: "byte-identical reports; reportSha256 d5bda59b5a6f46695ed9d4037bbbdf5c825b3aae214e4430fd2580d2eb4fc86d"
  - command: "prefinal exact-current-main GitHub validation on 924eaa0ad4f439351658cfcdc8943a3496f2d981"
    result: PASS
    evidence: "Agent Task Ownership, OTBM Map Tools, AI Agent Tools and CI all passed"
blockers:
  - "Formal QA-005/QA-006 certification remains blocked by missing reviewed mechanic binding for the pure movement route."
next_action: "Wait for full final-head protected CI on the commit created from this checkpoint, mark PR #801 ready, squash-merge if green, then archive the task and update programme queue/handoff plus discovery/changelog in lifecycle closure."
```
