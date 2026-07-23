---
task_id: CAN-20260723-owa-001-real-world-certification-campaign
program_id: CAN-PROGRAM-OTBM-WORLD-ASSURANCE-OPERATIONS
coordination_id: OWA-001
status: implementing
agent: "GPT-5.6 Thinking"
branch: feat/owa-001-real-world-certification-campaign-20260723
base_branch: main
created: 2026-07-23T15:53:12+02:00
updated: 2026-07-23T15:53:12+02:00
last_verified_commit: "489607174f22b8b36663fe2251cdba0423388fbd"
risk: medium
related_issue: ""
related_pr: ""
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
  - planned canary-otbm-world-assurance-campaign-manifest-v1
  - planned canary-otbm-world-assurance-campaign-v1
cross_repo_tasks: []
---

# Goal

Deliver the first reproducible reviewed OTBM world-assurance certification campaign over exact current-compatible evidence, beginning with `thais.temple -> thais.depot` only if the existing QA contracts can represent and certify it without invented mechanics or stale provenance.

# Acceptance criteria

- [ ] Add one reviewed target manifest with target ID/class, semantic definition, exact source-map and World Index provenance, existing route/preflight references and retained Physical E2E reference where applicable.
- [ ] Compose existing QA-005, QA-006, QA-016 and QA-018 contracts without adding a parser, World Index, pathfinder, Script Resolution implementation, renderer or E2E runner.
- [ ] Emit deterministic external campaign ledger/report data with explicit QA-005 dimensions, C0-C7, freshness, blockers and unresolved/conflicting evidence.
- [ ] Fail closed on provenance mismatch, stale/mixed/not-evaluated freshness, missing required evidence and unsupported target composition.
- [ ] Preserve region/landmark-route QA-006 certification caps and never promote static evidence to Physical E2E proof or Physical E2E proof to candidate revalidation.
- [ ] Keep generated campaign reports, `.otbm`, `.widx`, renders and proprietary assets outside Git.
- [ ] Add focused determinism, provenance mismatch, stale evidence, blocker and exact target certification tests.
- [ ] Relevant focused checks completed.
- [ ] Current-head GitHub checks verified.
- [ ] Module catalogue impact handled.
- [ ] Documentation/changelog impact handled.
- [ ] Program queue/handoff updated with exact certified state and remaining gaps.
- [ ] Cross-repository impact: none.
- [ ] Autonomous merge gate satisfied.

# Confirmed context

- Current `main` at task start is `489607174f22b8b36663fe2251cdba0423388fbd`.
- `CAN-PROGRAM-OTBM-WORLD-ASSURANCE-OPERATIONS` is active and OWA-001 is the first planned package.
- Programme bootstrap PR #795 and lifecycle archive PR #798 are merged; no existing OWA-001 PR was found.
- Reviewed semantic landmarks on current `main` pin `thais.temple` at `[32369,32241,7]` and `thais.depot` route destination at `[32352,32226,7]` to source map SHA-256 `a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2` and World Index SHA-256 `6c22cd26d4414aa094af1d00be7f62190a441e270ee7a478b55449bf92e55e7a`.
- Merged OTBM-E2E-005 PR #600 retains a successful exact-map physical route proof; Universal E2E run `29704821423` artifact `8447816376` is currently unexpired and pins the same map/World Index provenance in the archived task evidence.
- The reviewed Thais route is a same-floor movement route with no transition IDs and no route interactions.
- QA-005 `landmark-route` targets require explicit reviewed Coverage Matrix `mechanicIds`; whether the current pure-movement pilot has a valid existing mechanic binding is not yet proven and must fail closed rather than inventing one.

# Existing work to reuse

| Module/task/PR | Reuse | Evidence/path | Why it fits |
|---|---|---|---|
| QA-005 Coverage Dashboard | exact factual dimensions | `tools/ai-agent/otbm_coverage_dashboard.py` | Canonical coverage composition; does not assign certification. |
| QA-006 Region and Quest Certification | C0-C7 | `tools/ai-agent/otbm_region_quest_certification.py` | Canonical contiguous certification and target-class caps. |
| QA-016 Release Provenance | freshness | `tools/ai-agent/otbm_release_provenance.py` | Exact component hashes and dependency-scoped staleness. |
| QA-018 Evidence Gateway | compact evidence | `tools/ai-agent/otbm_evidence_gateway.py` | Exact read-only evidence transport without reinterpretation. |
| OTBM-E2E-005 / PR #600 | retained runtime proof | archived task + Universal E2E artifact `8447816376` | Existing Physical E2E for the preferred pilot. |

# Ownership and overlap check

- Program record: `docs/agents/programs/OTBM_WORLD_ASSURANCE_OPERATIONS_PROGRAM.md`.
- Open PRs inspected: current open PR inventory, including TCR #762.
- Active tasks inspected: TCR #762 task record for shared OTBM governance paths; no OWA-001 task existed.
- Ownership checker result: local checkout unavailable in this connector-only session; current-main task/PR ownership was checked directly and exact-head Agent Task Ownership CI remains mandatory.
- Exclusive claims: OWA-001 task, campaign composer/CLI/tests/docs/schema/reviewed target manifest listed in frontmatter.
- Shared claims: OWA programme record, `MODULE_CATALOG.md`, `CHANGELOG.md`.
- Read-only dependencies: existing QA, landmark, route, preflight and E2E contracts/evidence.
- Overlaps: TCR #762 also declares `MODULE_CATALOG.md` and `CHANGELOG.md` as shared.
- Resolution: any OWA edits to shared files must be narrow additive/current-main edits preserving TCR changes; no TCR-exclusive path will be edited. Recheck live PR overlap before final commit/merge.

# Current state

Investigating whether the preferred reviewed Thais route can be represented by existing QA-005 without an invented Coverage Matrix mechanic binding, and locating current-compatible retained evidence needed for the first campaign run.

# Plan

1. Establish the exact compatible evidence set and pilot representability, then implement the smallest deterministic campaign composition over existing QA contracts.
2. Add focused fail-closed/determinism tests and documentation; generate real campaign results externally only.
3. Update programme handoff and shared discovery records, run exact-head validation, final gate, merge, then archive this task.

# Work log

## 2026-07-23T15:53:12+02:00

- Changed: created dedicated OWA-001 branch and active ownership record.
- Learned: preferred Thais route has exact reviewed semantic/map/World Index and retained Physical E2E evidence, but QA-005 mechanic binding remains unproven.
- Failed/blocked: no local checkout is available for direct `python tools/agents/task_ownership.py`; GitHub ownership/PR records were inspected and CI validation remains required.
- Result: bounded implementation ownership is claimed without touching any active task's exclusive paths.

# Decisions

| Decision | Reason/evidence | ADR |
|---|---|---|
| Reuse QA-005/006/016/018 directly | Programme invariant forbids parallel QA infrastructure. | none |
| Keep generated campaign ledger external | Programme and user require generated campaign results outside Git. | none |
| Do not invent a Thais mechanic binding | QA-005 landmark-route requires explicit mechanic IDs and proof rules fail closed. | none |

# Files and interfaces

| Path/interface/config/schema | Ownership mode | Purpose | Status |
|---|---|---|---|
| `tools/ai-agent/otbm_world_assurance_campaign.py` | exclusive | deterministic campaign composition | planned |
| `docs/ai-agent/OTBM_WORLD_ASSURANCE_CAMPAIGN_TARGETS.json` | exclusive | reviewed durable campaign target manifest | planned |
| `docs/agents/programs/OTBM_WORLD_ASSURANCE_OPERATIONS_PROGRAM.md` | shared | queue/handoff | planned |
| `docs/agents/MODULE_CATALOG.md` | shared | reusable interface discovery | planned |

# Validation and CI

| Commit | Command/check/workflow | Result | Evidence/notes |
|---|---|---|---|
| `489607174f22b8b36663fe2251cdba0423388fbd` | current-main preflight | pass | GitHub repository/main/open PR/task records inspected |
| pending | focused OWA-001 tests | not-run | implementation pending |
| pending | Agent Task Ownership | not-run | exact PR head required |
| pending | OTBM Map Tools | not-run | exact PR head required |
| pending | AI Agent Tools | not-run | exact PR head if scope selects it |
| pending | CI / Required | not-run | exact final head required |

# Failed approaches and dead ends

- No guessed coordinates, mechanic IDs or landmark definitions are accepted.
- Historical Physical E2E success will not be treated as QA-005 coverage or QA-006 certification by itself.

# Risks and compatibility

- Runtime: campaign only consumes retained Physical E2E evidence and does not execute runtime.
- Data/migration: none; no map or datapack mutation.
- Security: evidence paths/hashes must fail closed; generated reports remain external.
- Backward compatibility: existing QA formats remain canonical and unchanged.
- Cross-repo rollout: none.
- Rollback: remove the additive campaign layer and reviewed manifest; source evidence remains untouched.

# Remaining work

1. Resolve pilot QA-005 representability and exact current-compatible evidence set.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: "2026-07-23T15:53:12+02:00"
head: "489607174f22b8b36663fe2251cdba0423388fbd"
branch: "feat/owa-001-real-world-certification-campaign-20260723"
pr: none
status: investigating
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
  - docs/agents/programs/OTBM_WORLD_ASSURANCE_OPERATIONS_PROGRAM.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/CHANGELOG.md
proven:
  - "Current main at task start is 489607174f22b8b36663fe2251cdba0423388fbd."
  - "Reviewed Thais landmarks pin exact map a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2 and World Index 6c22cd26d4414aa094af1d00be7f62190a441e270ee7a478b55449bf92e55e7a."
  - "Merged OTBM-E2E-005 retains successful physical route proof in currently unexpired artifact 8447816376 from run 29704821423."
  - "The reviewed Thais route uses no transition IDs or route interactions."
  - "QA-005 landmark-route manifests require explicit mechanicIds."
derived:
  - "Physical route proof alone cannot establish QA-005 coverage or QA-006 C5."
unknown:
  - "Whether an existing reviewed Coverage Matrix mechanic ID validly represents thais.temple -> thais.depot."
  - "Whether all QA-005 required external evidence reports for the pilot remain retained and current-compatible."
conflicts: []
first_failure:
  marker: "OWA-001 pilot formal QA-005 representation not yet proven"
  evidence: "QA-005 requires explicit mechanicIds for landmark-route targets while the reviewed Thais path has no transition/interaction IDs."
rejected_hypotheses:
  - "Invent a synthetic mechanic ID for the pure movement route: rejected because QA-005 requires reviewed Coverage Matrix mechanics."
  - "Promote retained Physical E2E directly to C5: rejected because QA-006 consumes contiguous QA-005 dimensions."
changed_paths:
  - docs/agents/tasks/active/CAN-20260723-owa-001-real-world-certification-campaign.md
validation:
  - command: "GitHub current-main/task/PR ownership preflight"
    result: PASS
    evidence: "main 489607174f22b8b36663fe2251cdba0423388fbd; no OWA-001 PR/task; TCR #762 shared overlap only on MODULE_CATALOG.md and CHANGELOG.md"
  - command: "python tools/agents/task_ownership.py"
    result: NOT_RUN
    evidence: "no local checkout available; exact-head Agent Task Ownership CI is mandatory"
blockers:
  - "Pilot QA-005 mechanic binding and current-compatible external evidence must be proven or formal certification must fail closed."
next_action: "Inspect retained OTBM-E2E-007/QA evidence and QA-005 target semantics to determine the exact first certifiable target state without invented bindings."
```

# Handoff

## Start here

Read this task checkpoint, the live PR, the OTBM World Assurance Operations programme and only QA-005/006/016/018 plus the reviewed Thais route evidence.

## Do not repeat

Do not build a parser, World Index, pathfinder, Script Resolution engine, renderer or E2E runner. Do not invent a mechanic binding to make the pilot certify.

## Required reads

- `AGENTS.md`
- `docs/agents/README.md`
- `docs/agents/programs/OTBM_WORLD_ASSURANCE_OPERATIONS_PROGRAM.md`
- `docs/ai-agent/OTBM_WORLD_ASSURANCE_OPERATIONS_ROADMAP.md`
- QA-005/006/016/018 implementation/docs
- reviewed Thais landmark and OTBM-E2E-005 evidence

## Open questions

- Can the preferred pure movement landmark route be represented by existing QA-005 without an existing reviewed mechanic ID?
- Which exact retained current-compatible QA-005 inputs are available for the first campaign composition?
