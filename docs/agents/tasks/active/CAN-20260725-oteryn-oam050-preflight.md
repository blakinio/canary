---
task_id: CAN-20260725-oteryn-oam050-preflight
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-050
status: implementing
agent: "GPT-5.6 Thinking"
branch: dudantas/oam-050-physical-client-e2e-preflight
base_branch: main
created: 2026-07-25
updated: 2026-07-26
last_verified_commit: "c5eac78b962829ae88640771f022c5b1a6671f01"
risk: high
related_issue: ""
related_pr: "944"
depends_on:
  - OAM-049 durably completed as f8a96b8b7c80528e9129bdfbd5778d606f762d19
blocks:
  - OAM-050 target disposition and lifecycle
  - OAM-050 Canary governance and lifecycle
  - OAM-050 durable program reconciliation
  - OAM-051 start
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260725-oteryn-oam050-preflight.md
  shared: []
  read_only:
    - docs/agents/real-tibia/registry/modules/physical-client-e2e.yaml
    - docs/agents/programs/E2E_AUTOMATION_PROGRAM.md
    - docs/agents/OTERYN_TARGET_ARCHITECTURE_CONTRACT.md
    - docs/agents/CROSS_REPO_CONTRACTS.md
    - tools/e2e/**
    - tests/e2e/**
    - .github/workflows/**e2e**
    - blakinio/Otheryn
    - blakinio/otclient
---

# OAM-050 Physical Client E2E preflight

Select canonical `physical-client-e2e → DO_NOT_MIGRATE candidate` after durable OAM-049 closure.

Universal Physical-Client E2E is separately governed validation platform tooling. It owns the reusable scenario registry, controlled client automation, disposable database lifecycle, deterministic evidence and cleanup. Its canonical module scope excludes production deployment and has no server, client or data implementation roots to transfer into Otheryn.

Otheryn already participates as a controlled exact-SHA server target through the Canary-owned Universal Agent E2E workflow. The workflow explicitly accepts `server_repository=blakinio/Otheryn` plus an exact 40-character `server_ref`; therefore no Otheryn-side platform adapter, duplicate runner or additional invocation contract is required for this package. Existing feature/session contracts remain separately authoritative.

Draft PR #925 remains authoritative for its QRI-022 login/relog baseline paths. Its exact-head dossier records nine clean retained attempts and one failed tenth attempt whose evidence was not retained. That finding proves a separate E2E-platform failure-retention gap; it does not create Otheryn runtime ownership or block this non-overlapping migration disposition.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-26T00:00:00+02:00
head: c5eac78b962829ae88640771f022c5b1a6671f01
branch: dudantas/oam-050-physical-client-e2e-preflight
pr: 944
status: validating
context_routes:
  - agent-governance
  - cross-repo
  - universal-e2e
  - ci-repair
owned_paths:
  - docs/agents/tasks/active/CAN-20260725-oteryn-oam050-preflight.md
proven:
  - OAM-049 durably completed as f8a96b8b7c80528e9129bdfbd5778d606f762d19.
  - Fresh Canary main is 0b65d2e6045c26c5e5295c12a74c627a5f67668f, fresh Otheryn main is 877816a64e31c6d25815ebf6b7543e001648ca52 and upstream Canary is 7644bcbcbbad4a09e52a5707ed531e4dd21d8a79.
  - Canonical physical-client-e2e is platform-tooling with no server, client or data roots; its scope excludes production deployment and duplicate module-specific orchestration.
  - The Oteryn target architecture requires future target proof to reuse the merged Universal Physical-Client E2E platform; generic orchestration changes remain separate E2E-platform tasks.
  - Universal Agent E2E already accepts blakinio/Otheryn as the controlled server repository when pinned to an exact SHA.
  - Existing cross-repository contracts already cover Otheryn login/session producer behavior and exact maintained-client evidence without transferring the E2E platform.
  - PR 925 remains open and draft at 9bb202793f9d9726103cbf21a67792c4e519b927 with exact-head Ownership, CI and Universal Agent E2E successful.
  - PR 925 records nine clean retained login/relog attempts and one failed tenth attempt with missing failure/cancellation evidence; its first failure is physical-failure-evidence-not-retained.
  - PR 944 changes only this task record, has no comments, reviews or review threads, and current-head Ownership and CI were successful before this final checkpoint update.
derived:
  - DO_NOT_MIGRATE is the evidence-backed target disposition because the responsibility is validation infrastructure external to Otheryn production runtime.
  - No bounded Otheryn-side adapter or new invocation contract is needed: exact-SHA target selection already exists in the Canary-owned workflow.
  - PR 925 failure-retention repair must remain under a separate E2E-platform task and must not be absorbed into OAM-050.
unknown:
  - Physical-client behavior outside exact maintained client, server, datapack and scenario cells remains unproven.
  - Future feature packages may require new feature-specific scenarios or assertions, but that does not imply migration of the orchestration platform.
conflicts: []
first_failure:
  marker: final-head-gates-pending
  command: PR 944 exact-head Ownership and CI after ci:final-gate checkpoint update
  result: NOT_RUN
  evidence: Final checkpoint commit has not yet completed its synchronize-triggered gates.
rejected_hypotheses:
  - Copy the Universal Physical-Client E2E platform into Otheryn production runtime.
  - Add an Otheryn-side duplicate runner or generic orchestration adapter.
  - Treat PR 925 failure-retention gap as an Otheryn runtime responsibility.
  - Treat partial physical-client coverage as complete gameplay or protocol parity.
changed_paths:
  - docs/agents/tasks/active/CAN-20260725-oteryn-oam050-preflight.md
validation:
  - command: fresh live-state, dependency and canonical-scope review
    result: PASS
    evidence: Package is dependency-valid platform tooling with production deployment explicitly excluded.
  - command: PR 925 exact-head evidence and ownership review
    result: PASS
    evidence: Its blocked QRI-022 result and failure-retention finding are reviewable; OAM-050 owns none of its paths.
  - command: target invocation-contract proof
    result: PASS
    evidence: Universal Agent E2E explicitly accepts blakinio/Otheryn with an exact server_ref; no target-side adapter is required.
  - command: PR 944 exact-head Ownership and CI
    result: NOT_RUN
    evidence: Required after this ci:final-gate checkpoint update.
blockers:
  - PR 944 exact-head Ownership and CI
  - Current user repository-write scope permits mutations only in blakinio/canary, so a later Otheryn target-disposition PR is not authorized by this task.
next_action: Require exact-head Ownership and CI on PR 944, audit discussions and Canary-main drift, then merge the completed preflight.
```
