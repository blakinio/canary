---
task_id: CAN-20260725-oteryn-oam050-preflight
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-050
status: blocked
agent: "GPT-5.6 Thinking"
branch: dudantas/oam-050-physical-client-e2e-preflight
base_branch: main
created: 2026-07-25
updated: 2026-07-25
last_verified_commit: "69f5db10b3944c6ace14a4a9aa3e35fc4c610f5c"
risk: high
related_issue: ""
related_pr: "944"
depends_on:
  - OAM-049 durably completed as f8a96b8b7c80528e9129bdfbd5778d606f762d19
blocks:
  - OAM-050 target disposition
  - OAM-050 lifecycle, governance and durable reconciliation
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260725-oteryn-oam050-preflight.md
  shared: []
  read_only:
    - docs/agents/real-tibia/registry/modules/physical-client-e2e.yaml
    - docs/agents/programs/E2E_AUTOMATION_PROGRAM.md
    - tools/e2e/**
    - tests/e2e/**
    - .github/workflows/**e2e**
    - blakinio/Otheryn
    - blakinio/otclient
---

# OAM-050 Physical Client E2E preflight

Select canonical `physical-client-e2e → DO_NOT_MIGRATE candidate` after durable OAM-049 closure.

The package is a reusable exact-head validation platform for Canary and a controlled OTClient, disposable databases and evidence artifacts. Its canonical scope explicitly excludes production deployment and duplicate module-specific orchestration. Otheryn should consume evidence and scenario outcomes, not duplicate the orchestration platform inside production runtime.

Fresh ownership review found active draft Canary PR #925 performing the QRI-022 login/relog repeated-run baseline on the same separately governed E2E programme. OAM-050 owns only this preflight task and will not edit, supersede or reinterpret PR #925 files. Final target classification is blocked until the active evidence work is reconciled against its then-current exact head.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-25T23:58:00+02:00
head: 69f5db10b3944c6ace14a4a9aa3e35fc4c610f5c
branch: dudantas/oam-050-physical-client-e2e-preflight
pr: 944
status: blocked
context_routes:
  - agent-governance
  - cross-repo
  - github-actions
  - physical-client-e2e
owned_paths:
  - docs/agents/tasks/active/CAN-20260725-oteryn-oam050-preflight.md
proven:
  - OAM-049 durably completed as f8a96b8b7c80528e9129bdfbd5778d606f762d19.
  - Fresh Canary main is f8a96b8b7c80528e9129bdfbd5778d606f762d19 and fresh Otheryn main is 877816a64e31c6d25815ebf6b7543e001648ca52.
  - Canonical physical-client-e2e is platform-tooling and depends on protocol plus player-persistence, both already represented in completed OAM history.
  - Its scope includes scenario registry, controlled client automation, disposable database, evidence artifacts and cleanup, and excludes production deployment and duplicate module-specific orchestration.
  - Otheryn has no proven need to own the GitHub/client orchestration platform as production runtime.
  - Draft Canary PR 925 is open at head 9bb202793f9d9726103cbf21a67792c4e519b927 and owns QRI-022 login/relog baseline task and evidence paths.
  - This OAM task claims no PR 925 path and makes no change to E2E runtime, scenarios, workflow, client, server or evidence.
derived:
  - DO_NOT_MIGRATE is the leading target disposition because validation orchestration is external platform tooling whose outputs can validate Otheryn without becoming Otheryn runtime.
  - The active PR 925 evidence stream must remain authoritative for its exact QRI-022 scope and cannot be silently absorbed by OAM-050.
unknown:
  - Final state, gates and reviewed findings of PR 925.
  - Whether any bounded Otheryn-side adapter or invocation contract is required after the E2E programme evidence stabilizes.
  - Physical-client behavior outside the exact maintained client, server, datapack and scenario cells proven by the platform.
conflicts:
  - Draft PR 925 is active under the separately governed E2E programme and touches QRI-022 physical-client evidence surfaces.
first_failure:
  marker: active-e2e-program-overlap
  command: fresh open-PR and ownership audit
  result: BLOCKED
  evidence: PR 925 remains active at 9bb202793f9d9726103cbf21a67792c4e519b927; OAM-050 must not claim its task, baseline or evidence paths.
rejected_hypotheses:
  - Copy the Universal Physical-Client E2E platform into Otheryn production runtime.
  - Close, supersede or modify PR 925 from this OAM package.
  - Treat partial E2E coverage as complete gameplay or protocol parity.
  - Duplicate scenario orchestration for individual target modules.
changed_paths:
  - docs/agents/tasks/active/CAN-20260725-oteryn-oam050-preflight.md
validation:
  - command: fresh live-state, dependency and canonical-scope review
    result: PASS
    evidence: Package is dependency-valid platform tooling with production deployment explicitly excluded.
  - command: open-PR and ownership audit
    result: PASS
    evidence: PR 925 overlap is recorded; this task owns only its preflight record and does not edit E2E surfaces.
  - command: final target disposition proof
    result: NOT_RUN
    evidence: Reconcile PR 925 exact-head outcome and determine whether any target-side invocation contract is needed before finalizing DO_NOT_MIGRATE.
blockers:
  - active draft PR 925 QRI-022 evidence work
  - final proof of whether Otheryn needs any bounded adapter rather than the full platform
next_action: Re-fetch PR 925 and fresh Canary/Otheryn heads, preserve its ownership, review the completed exact-head QRI-022 evidence when available, then prove whether Otheryn needs no platform code or only a bounded invocation contract before opening any target disposition PR.
```
