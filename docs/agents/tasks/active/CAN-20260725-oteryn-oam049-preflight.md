---
task_id: CAN-20260725-oteryn-oam049-preflight
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-049
status: in_progress
agent: "GPT-5.6 Thinking"
branch: dudantas/oam-049-upstream-intelligence-preflight
base_branch: main
created: 2026-07-25
updated: 2026-07-25
last_verified_commit: "36292e3e87f87e56f5fdfe02b307e4efee64c6b2"
risk: medium
related_issue: ""
related_pr: "939"
depends_on:
  - OAM-048 durably completed as a22563088ebad86602dbd8cb9af0b120dcbfc94d
blocks:
  - OAM-049 target disposition and lifecycle
  - OAM-049 Canary governance and lifecycle
  - OAM-049 durable program reconciliation
  - OAM-050 start
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260725-oteryn-oam049-preflight.md
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

# OAM-049 Upstream Intelligence preflight

Select canonical `upstream-intelligence → DO_NOT_MIGRATE candidate` after durable OAM-048 closure.

The package is repository-governance tooling: read-only source discovery, provenance, bounded drift inventory, source-policy-aware module mapping, reviewed triage, immutable workflow artifacts and a stable report issue. It is intentionally not server runtime. Otheryn may consume reviewed, revision-pinned conclusions through normal bounded tasks, but should not own or duplicate the watcher, mapper, report publisher or GitHub workflow.

This disposition does **not** disable Upstream Intelligence. The existing Canary programme remains active and continues to check external repositories for potentially missed fixes, crashes, protocol changes, security signals and useful implementation ideas. External repositories remain read-only.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-25T22:31:00+02:00
head: 36292e3e87f87e56f5fdfe02b307e4efee64c6b2
branch: dudantas/oam-049-upstream-intelligence-preflight
pr: 939
status: validating
context_routes:
  - agent-governance
  - cross-repo
  - github-actions
owned_paths:
  - docs/agents/tasks/active/CAN-20260725-oteryn-oam049-preflight.md
proven:
  - OAM-048 durably completed as a22563088ebad86602dbd8cb9af0b120dcbfc94d.
  - Fresh Canary main is 8ef88972fd1c473b9f3c0a5cfb9bed98c78bdbc9 and fresh Otheryn main is fc93848796f05108684dfbb218f7434a8cb88755.
  - Canonical upstream-intelligence has no dependencies and is classified as platform-tooling.
  - Its registry scope includes bounded discovery, provenance, module mapping, exact local ancestry/reference probes, reviewed decisions, report issues and immutable artifacts.
  - Its explicit exclusions include automatic cherry-picks, automatic gameplay or protocol conclusions, implementation branches, writes to watched repositories and semantic-equivalence claims.
  - The workflow grants watched-source access only for reading; its only write is the stable report issue in blakinio/canary.
  - Otheryn has no upstream-intelligence implementation root or runtime consumer.
  - Open Canary PR 925 owns physical-client E2E surfaces and PRs 929-931 own RTEC evidence surfaces; none owns this OAM task path or proposes an Otheryn watcher.
derived:
  - Upstream Intelligence is valuable development governance but is not part of the Otheryn production-server architecture.
  - DO_NOT_MIGRATE preserves monitoring in Canary while preventing duplicate scanners, registries, mappers and GitHub workflows in Otheryn.
unknown:
  - Operational success of the next scheduled production scan and stable report issue remains governed by UI-002.
  - Individual future upstream candidates still require revision-pinned review and bounded implementation proof.
conflicts: []
first_failure:
  marker: ownership-checkpoint-schema
  command: changed active task checkpoint validation
  result: FAIL
  evidence: Initial head a13f20ef4dc4a3c9e02dee314fc6460a750f637f used null for first_failure; Ownership run 30171895810 required a YAML mapping. Head 06c4c41ca401a7d7eb6d9a8fd0a0076f09bc1bde then proved the mapping also requires marker and supported validation result values. Head 36292e3e87f87e56f5fdfe02b307e4efee64c6b2 proved active task records require a supported lifecycle status rather than the literal value active.
rejected_hypotheses:
  - Disable or remove Upstream Intelligence because it is not migrated to Otheryn.
  - Copy the watcher and workflow into Otheryn for convenience.
  - Treat an external commit, issue or PR as automatic proof that Canary or Otheryn is wrong.
  - Allow automatic cherry-picks or writes to watched repositories.
changed_paths:
  - docs/agents/tasks/active/CAN-20260725-oteryn-oam049-preflight.md
validation:
  - command: fresh main, open-PR, ownership, dependency and exact-root review
    result: PASS
    evidence: No conflicting OAM-049 ownership; package is dependency-valid and target has no implementation root.
  - command: external repository write-boundary review
    result: PASS
    evidence: Watched repositories are read-only and the workflow cannot push to them.
  - command: changed active task checkpoint validation
    result: NOT_RUN
    evidence: Exact-head Ownership must confirm the supported frontmatter status and checkpoint schema.
blockers:
  - Canary preflight exact-head Ownership and CI
  - clean discussion and Canary-main drift audit
next_action: Require exact-head Ownership and full CI on PR 939, audit discussions and main drift, then merge before creating the Otheryn disposition task.
```
