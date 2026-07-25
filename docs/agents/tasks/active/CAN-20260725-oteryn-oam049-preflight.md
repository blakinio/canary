---
task_id: CAN-20260725-oteryn-oam049-preflight
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-049
status: review
agent: "GPT-5.6 Thinking"
branch: dudantas/oam-049-upstream-intelligence-governance
base_branch: main
created: 2026-07-25
updated: 2026-07-25
last_verified_commit: "255856e361ee018b9bf3cedb590673ba3744e742"
risk: medium
related_issue: ""
related_pr: ""
depends_on:
  - OAM-048 durably completed as a22563088ebad86602dbd8cb9af0b120dcbfc94d
blocks:
  - OAM-049 Canary governance and lifecycle
  - OAM-049 durable program reconciliation
  - OAM-050 start
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260725-oteryn-oam049-preflight.md
    - docs/agents/OTERYN_OAM_049_UPSTREAM_INTELLIGENCE_REVALIDATION.md
  shared: []
  read_only:
    - docs/agents/real-tibia/registry/modules/upstream-intelligence.yaml
    - docs/agents/programs/UPSTREAM_INTELLIGENCE_PROGRAM.md
    - docs/agents/upstream/**
    - tools/agents/upstream_intelligence*.py
    - .github/workflows/upstream-intelligence.yml
    - blakinio/Otheryn
    - opentibiabr/canary
    - opentibiabr/otclient
    - zimbadev/crystalserver
---

# OAM-049 Upstream Intelligence governance

Final disposition: `upstream-intelligence → DO_NOT_MIGRATE`.

This keeps Upstream Intelligence active in Canary and excludes only duplication of its repository-governance machinery in production Otheryn.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-25T23:09:00+02:00
head: 255856e361ee018b9bf3cedb590673ba3744e742
branch: dudantas/oam-049-upstream-intelligence-governance
pr: null
status: validating
context_routes:
  - agent-governance
  - cross-repo
  - github-actions
owned_paths:
  - docs/agents/tasks/active/CAN-20260725-oteryn-oam049-preflight.md
  - docs/agents/OTERYN_OAM_049_UPSTREAM_INTELLIGENCE_REVALIDATION.md
proven:
  - Canary preflight head c5765904930c17be6131fe9459d9eaf67aafd321 passed Ownership 30172288302 and CI 30172288416 and PR 939 merged as 4ba73d72a26e10c8ff1a873a8267291fb2d93cf9.
  - Otheryn disposition head d3d95828a4067012b87af9b8015cb7a420f70120 passed Required 30172471373 and PR 111 merged as 9632bf1a0721fb28f3596c57495ba008604587ec after clean audit.
  - Otheryn lifecycle head 5daf45e3a3c4bd5a32aec3ac24351bee7c905dde passed Required 30172564823 and PR 112 merged as 877816a64e31c6d25815ebf6b7543e001648ca52 after clean audit.
  - Otheryn added no runtime, workflow, scanner, registry, mapper, report publisher, data or deployment path.
  - Canary Upstream Intelligence remains active and all watched external repositories remain read-only.
  - Reviewed revision-pinned fixes may still reach Otheryn through separate bounded tasks and normal gates.
derived:
  - Repository-watching infrastructure belongs to Canary development governance rather than Otheryn production runtime.
  - DO_NOT_MIGRATE preserves upstream discovery while preventing duplicate sources of policy and triage truth.
unknown:
  - UI-002 production-scan and stable-report verification remains separate.
  - Future candidate correctness and target applicability remain unproven until reviewed against then-current state.
conflicts: []
first_failure:
  marker: ownership-checkpoint-schema
  command: Canary preflight changed-task validation
  result: FAIL
  evidence: Early preflight heads exposed checkpoint-schema and unsupported lifecycle-status values; final preflight head corrected them and passed Ownership 30172288302.
rejected_hypotheses:
  - Disable or remove Upstream Intelligence.
  - Duplicate the watcher and workflow in Otheryn.
  - Automatically import external changes or infer correctness from source activity.
changed_paths:
  - docs/agents/tasks/active/CAN-20260725-oteryn-oam049-preflight.md
  - docs/agents/OTERYN_OAM_049_UPSTREAM_INTELLIGENCE_REVALIDATION.md
validation:
  - command: Otheryn target disposition and lifecycle gates
    result: PASS
    evidence: PR 111 and PR 112 passed Required, clean audits and expected-head merges.
  - command: monitoring preservation and external write-boundary review
    result: PASS
    evidence: Canary programme remains active and watched repositories remain read-only.
  - command: Canary governance exact-head gates
    result: NOT_RUN
    evidence: Governance PR must pass Ownership and full CI on the synchronized head.
blockers:
  - Canary governance exact-head Ownership and CI
  - clean discussion and Canary-main drift audit
  - governance merge, lifecycle archive and durable reconciliation
next_action: Open the Canary governance PR, require exact-head Ownership and full CI, audit discussions and main drift, then merge and complete lifecycle plus durable reconciliation before OAM-050.
```
