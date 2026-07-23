---
task_id: CAN-20260723-owa-001-real-world-certification-campaign
program_id: CAN-PROGRAM-OTBM-WORLD-ASSURANCE-OPERATIONS
coordination_id: OWA-001
status: completed
agent: "GPT-5.6 Thinking"
branch: feat/owa-001-real-world-certification-campaign-20260723
base_branch: main
created: 2026-07-23T15:53:12+02:00
updated: 2026-07-23T17:08:00+02:00
last_verified_commit: "3115185e4eaf95f0ff6319ec9949274e7573065d"
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

# Completion

PR #801 was squash-merged as `3115185e4eaf95f0ff6319ec9949274e7573065d` after exact-final-head protected validation.

Delivered:

- reviewed target manifest `canary-otbm-world-assurance-campaign-manifest-v1`;
- deterministic external report/ledger composition `canary-otbm-world-assurance-campaign-v1`;
- exact fail-closed composition over canonical QA-005, QA-006, QA-016, QA-018 and retained Physical E2E evidence;
- focused determinism, provenance-mismatch, stale-evidence, fail-closed, exact-target, output-safety and schema tests;
- documentation and schemas;
- no new parser, World Index, Script Resolution engine, pathfinder, renderer, mutation path or E2E runner/workflow;
- no generated campaign report, `.otbm`, `.widx`, render or proprietary asset committed.

# Certified campaign target state

Target: `owa-001.thais-temple-to-depot` (`thais.temple -> thais.depot`), class `landmark-route`.

Exact reviewed provenance:

- source map SHA-256 `a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2`;
- World Index SHA-256 `6c22cd26d4414aa094af1d00be7f62190a441e270ee7a478b55449bf92e55e7a`;
- origin `[32369,32241,7]`;
- destination `[32352,32226,7]`;
- route plan SHA-256 `0736a819ef656f9040ea14c51f1ab474beabe9e4da50435e1eb9e7fd0c28974b`;
- route preflight `passed`;
- route distance `59`;
- transition IDs: none;
- route interactions: none.

Retained route-level Physical E2E:

- workflow run `29704821423`;
- artifact ID `8447816376`;
- artifact ZIP SHA-256 `131faa08eaaccdacda62788b2e173b0f9ecc422a62ecd4769e874e4d136aeb40`;
- exact runtime map SHA-256 matches the reviewed source map;
- proof state: `proven` for this exact landmark route only.

Formal campaign outcome:

- QA-005 dimensions: all `not-evaluated`;
- QA-006 certification: `C0_NOT_EVALUATED`;
- QA-016 static-route freshness: `current`;
- QA-016 route-level Physical E2E freshness: `current`;
- retained route-level Physical E2E: `proven`;
- target state: `blocked`.

Exact blockers:

- `QA005_LANDMARK_ROUTE_REQUIRES_REVIEWED_MECHANIC_IDS`;
- `QA005_NO_REVIEWED_MECHANIC_BINDING_FOR_PURE_MOVEMENT_ROUTE`;
- `QA006_REQUIRES_CANONICAL_QA005_TARGET`.

The successful walk is not mechanic coverage and is not candidate-change revalidation. It does not raise QA-006 above C0 because the reviewed pure-movement route has no canonical QA-005 mechanic binding.

No alternative target was substituted because no stronger reviewed QA-005/QA-006 binding with equally exact current provenance was found. No coordinates, landmarks or mechanic IDs were invented.

# Validation

- focused local suite: 14 tests passed;
- repeated external campaign composition: byte-identical outputs;
- generated external report field `reportSha256`: `d5bda59b5a6f46695ed9d4037bbbdf5c825b3aae214e4430fd2580d2eb4fc86d`;
- final feature head: `8d9d5608e2708e14530e531497ace63323a4af09`;
- Agent Task Ownership: success;
- OTBM Map Tools: success;
- AI Agent Tools: success;
- protected full CI run `30017520600`: success;
- PR #801: merged, no requested-change review or unresolved review thread recorded before merge.

# Handoff

OWA-002 must visualize the factual OWA-001 state exactly as delivered:

- C0 formal certification, not C5;
- QA-005 `not-evaluated`, not implicitly proven;
- QA-016 freshness `current` for the exact static-route and retained route-level Physical E2E evidence;
- route-level Physical E2E `proven` as a separate proof channel;
- the three exact QA-005/QA-006 blockers visible and evidence-linked.

OWA-002 must reuse the factual renderer and must not convert the retained successful route into a green mechanic/certification claim or a single health score.

A future package may raise formal certification only after an existing or newly reviewed canonical QA-005 target legitimately binds the target class to exact mechanic evidence; OWA-001 itself does not create such a binding.
