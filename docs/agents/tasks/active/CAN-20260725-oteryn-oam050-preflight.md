---
task_id: CAN-20260725-oteryn-oam050-preflight
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-050
status: review
agent: "GPT-5.6 Thinking"
branch: dudantas/oam-050-physical-client-e2e-governance
base_branch: main
created: 2026-07-25
updated: 2026-07-26
last_verified_commit: "82b443cb67b55a696572b9bb4399ff735bcc80e7"
risk: high
related_issue: ""
related_pr: "947"
depends_on:
  - OAM-049 durably completed as f8a96b8b7c80528e9129bdfbd5778d606f762d19
blocks:
  - OAM-050 Canary governance and lifecycle
  - OAM-050 durable program reconciliation
  - OAM-051 start
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260725-oteryn-oam050-preflight.md
    - docs/agents/OTERYN_OAM_050_PHYSICAL_CLIENT_E2E_REVALIDATION.md
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

# OAM-050 Physical Client E2E governance

Final disposition: `physical-client-e2e → DO_NOT_MIGRATE`.

Universal Physical-Client E2E remains active in Canary as the single reusable validation platform. Otheryn consumes exact-revision validation results and does not duplicate the runner, workflow, controlled-client harness, disposable database lifecycle, evidence schemas or cleanup orchestration.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-26T00:44:00+02:00
head: 82b443cb67b55a696572b9bb4399ff735bcc80e7
branch: dudantas/oam-050-physical-client-e2e-governance
pr: 947
status: validating
context_routes:
  - agent-governance
  - cross-repo
  - universal-e2e
  - github-actions
owned_paths:
  - docs/agents/tasks/active/CAN-20260725-oteryn-oam050-preflight.md
  - docs/agents/OTERYN_OAM_050_PHYSICAL_CLIENT_E2E_REVALIDATION.md
proven:
  - Canary preflight PR 944 passed exact-head Ownership 30176758049 and full CI 30176758136 and merged as 515af061dda97173cb5ac6cc7885b7cdc3c4504f.
  - Otheryn disposition PR 113 passed Required 30177667228 and merged as 92cc602332f0ea86dbb669541020112c299ec66c.
  - Otheryn lifecycle PR 114 passed Required 30177733797 and merged as ff90e93d872b6b47720f711483a9832203d5258d.
  - Otheryn added no runtime, build, startup, workflow, E2E runner, client harness, evidence schema, database fixture or deployment path.
  - Universal Agent E2E already accepts blakinio/Otheryn with an exact server_ref.
  - Canary PR 925 remains authoritative for its original nine retained clean login/relog attempts and the unretained failed tenth attempt.
  - E2E repair PR 940 delivered and lifecycle-closed capture-upload-propagate failure evidence retention as ad647f040a0f0b5b515c2416bf8aa11705dd7e8e with controlled success and failure proofs.
  - The original PR 925 population remains historically blocked; any replacement baseline requires fresh separately governed attempts.
derived:
  - Physical-client-e2e belongs to Canary development and release validation, not Otheryn production runtime.
  - DO_NOT_MIGRATE preserves one canonical lifecycle while allowing exact Otheryn revisions to be validated externally.
  - The merged retention repair strengthens the external platform and does not create target runtime ownership.
unknown:
  - Complete stability and compatibility outside exact executed scenario/server/client/datapack cells remain unproven.
  - A replacement ten-attempt baseline has not yet been executed and classified.
  - Future feature packages may require new feature-owned scenarios or assertions.
conflicts: []
first_failure:
  marker: no-target-runtime-responsibility
  command: target ownership and invocation-contract review
  result: PASS
  evidence: Otheryn has no production consumer for the platform and the canonical Canary workflow already accepts exact Otheryn SHAs.
rejected_hypotheses:
  - Copy the Universal Physical-Client E2E platform into Otheryn.
  - Add a duplicate target runner, workflow or invocation adapter.
  - Retroactively reclassify or replace PR 925's original failed population.
  - Treat the merged retention repair as an Otheryn migration requirement.
  - Treat partial physical coverage as complete gameplay or protocol parity.
changed_paths:
  - docs/agents/tasks/active/CAN-20260725-oteryn-oam050-preflight.md
  - docs/agents/OTERYN_OAM_050_PHYSICAL_CLIENT_E2E_REVALIDATION.md
validation:
  - command: Otheryn target disposition and lifecycle gates
    result: PASS
    evidence: PR 113 and PR 114 passed Required, clean audits and expected-head merges.
  - command: canonical E2E ownership and invocation review
    result: PASS
    evidence: Canary retains the platform and exact Otheryn server_ref selection already exists.
  - command: current-main failure-retention reconciliation
    result: PASS
    evidence: PR 940 merged as ad647f040a0f0b5b515c2416bf8aa11705dd7e8e with controlled success/failure retention proof.
  - command: Canary governance exact-head gates
    result: NOT_RUN
    evidence: PR 947 must rerun Ownership and CI after this material reconciliation update.
blockers:
  - Canary governance exact-head Ownership and CI
  - clean discussion and Canary-main drift audit
  - governance merge, lifecycle archive and durable reconciliation
next_action: Require exact-head Ownership and CI on PR 947 after the retention-repair reconciliation, then audit and merge before lifecycle plus durable reconciliation.
```