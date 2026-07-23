---
task_id: CAN-20260722-oteryn-oam037-preflight
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
status: ready
agent: "GPT-5.6 Thinking"
branch: dudantas/oam-037-governance-finalize
base_branch: main
created: 2026-07-22
updated: 2026-07-23
last_verified_commit: "4f074077da44d1cc9d77db7ac768be0589313332"
risk: medium
related_issue: ""
related_pr: "749"
depends_on:
  - OAM-036 formally complete
blocks:
  - OAM-038 start
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260722-oteryn-oam037-preflight.md
    - docs/agents/OTERYN_OAM_037_RAIDS_REVALIDATION.md
  shared: []
  read_only:
    - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
    - docs/agents/real-tibia/registry/modules/**
modules_touched:
  - oteryn-architecture-migration
  - raids
cross_repo_tasks: []
---

# OAM-037 Raids governance

## Final disposition

`raids → REUSE`

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-23T09:52:00+02:00
head: 4a1fb8805d857c6e69fe11b45d5046ef37e0ef4f
branch: dudantas/oam-037-governance-finalize
pr: 749
status: validating
context_routes:
  - agent-governance
  - cross-repo
owned_paths:
  - docs/agents/tasks/active/CAN-20260722-oteryn-oam037-preflight.md
  - docs/agents/OTERYN_OAM_037_RAIDS_REVALIDATION.md
proven:
  - OAM-036 was formally complete before OAM-037 selection.
  - OAM-037 preflight merged as 8bdeb2747356727df80a3b95073aa29a4dca7818 and selected canonical raids as a REUSE candidate.
  - Canary bounded target-proof plan merged as 817da293a141880f7090194699a4ac38e567a2fb.
  - Otheryn target task-start main was 3aaf77fe27600b274d2b9c9e6bd30d887e0afd0e.
  - Otheryn and the reviewed fresh upstream baseline share exact raids.cpp blob d46a549a341e0872474bd723b10d1208fa22da8c and raids.hpp blob 777558e3e199816bb596636fc7487c38c29224ee.
  - Semantic review and bounded source-contract proof covered registry parsing reload maintenance-lane scheduling scheduling-failure recovery running and non-repeat lifecycle ordered event execution reset stop cleanup and all four canonical raid event kinds.
  - Otheryn PR 77 final head 133c12f61a1e5e392be9ee7faa9236755cbe0225 changed exactly four intended proof/task paths and no production path.
  - Exact-head autofix 29988627793 CI 29988627932 and Required 29988627768 succeeded; Linux release Linux debug full Run Tests both Windows build paths macOS Fast Checks Lua Tests and applicable runtime smokes all passed.
  - PR 77 comments reviews and review threads were empty and target main had no drift from immutable target base before merge.
  - Otheryn PR 77 squash-merged as d896141d084d381d12cc328d4b920c698eb1d55c.
derived:
  - OAM-037 final disposition is raids REUSE with proof-only target changes.
  - No production runtime maintained-client or protocol mutation was required.
  - OAM-038 remains blocked until governance merge separate Canary lifecycle archive durable program reconciliation and Otheryn target-task archive complete.
unknown:
  - Exact final Canary governance merge SHA until PR 749 completes.
conflicts: []
first_failure:
  marker: none
  evidence: No task-specific validation failure is currently open.
rejected_hypotheses:
  - Infer final REUSE from blob identity alone; semantic source-contract proof passed on the exact target head.
  - Import the divergent legacy raids.cpp wholesale; target and fresh upstream retain stronger maintenance-lane scheduling and scheduling-failure safeguards.
  - Expand OAM-037 into boss encounters generic spawns raid content parity Bosstiary quests or protocol/client work because canonical ownership excludes those boundaries.
changed_paths:
  - docs/agents/tasks/active/CAN-20260722-oteryn-oam037-preflight.md
  - docs/agents/OTERYN_OAM_037_RAIDS_REVALIDATION.md
validation:
  - command: Otheryn PR 77 exact-head target gates
    result: PASS
    evidence: final head 133c12f61a1e5e392be9ee7faa9236755cbe0225 passed autofix 29988627793 CI 29988627932 Required 29988627768 and Linux-debug full Run Tests before merge d896141d084d381d12cc328d4b920c698eb1d55c
  - command: target changed-path and interaction audit
    result: PASS
    evidence: exactly four intended proof/task paths no production changes and empty comments reviews threads with no target-main drift
blockers: []
next_action: Require exact-current-head Agent Task Ownership and CI success on PR 749, audit exactly two governance paths plus comments reviews threads and Canary main drift, then expected-head squash merge before separate lifecycle archive.
```
