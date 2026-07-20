---
task_id: CAN-20260720-oteryn-parties-revalidation
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-023
status: implementing
agent: "GPT-5.5 Thinking"
branch: docs/oam-023-parties-revalidation
base_branch: main
created: 2026-07-20
updated: 2026-07-20
last_verified_commit: "0a39a0f76d5f811098dfaa7be9deea40347279d5"
risk: medium
related_pr: "616"
depends_on:
  - OAM-005 character-lifecycle
blocks:
  - OAM-024
modules_touched:
  - parties
owned_paths:
  exclusive:
    - docs/agents/OTERYN_OAM_023_PARTIES_REVALIDATION.md
    - docs/agents/tasks/active/CAN-20260720-oteryn-parties-revalidation.md
---

# Goal

Revalidate canonical OAM-023 `parties`, classify the smallest dependency-valid clean-target disposition from current evidence, deliver only the bounded target implementation or proof required by that disposition, and complete target → governance → lifecycle archive → durable program reconciliation before OAM-024 starts.

# Immutable task-start baselines

- Canary: `0a39a0f76d5f811098dfaa7be9deea40347279d5`
- Otheryn: `50dfa248251f245f5519495a4fbd430b6814ffe4`
- fresh upstream Canary: `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`
- maintained OTClient: `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`

# Selection evidence

Canonical `parties` depends only on `character-lifecycle`, completed under OAM-005. Its canonical production boundary is narrowly scoped to `src/creatures/players/grouping/party.*`; it excludes party chat transport, protocol packet compatibility, persistent guild membership, Wheel/vocation correctness and generic combat formula correctness.

Compared with other currently eligible candidates, `parties` is the smallest bounded source boundary found in the fresh registry/ownership preflight. `cyclopedia` is a broad server/client/protocol surface and is not selected. `wheel-of-destiny` remains under a separate active parity program and is not selected. Current Canary open PR changed-file audits show no overlap with `src/creatures/players/grouping/party.*`.

# Current evidence state

- `PROVEN`: OAM-022 target, governance, lifecycle and durable program reconciliation are merged; durable state says OAM-023 was not started before this task.
- `PROVEN`: Canary and Otheryn task-start heads equal the last OAM-022 durable/target merges, so task-start drift is zero.
- `PROVEN`: canonical `parties` depends only on completed OAM-005 `character-lifecycle`.
- `PROVEN`: current target, upstream and legacy `party.cpp` share blob `c3493c962548bffa5e393adc3359137b200b6384`; `party.hpp` shares blob `52b08e7321dd4e35bfb68415254239245ed236ee`.
- `UNKNOWN`: final OAM-023 disposition until reviewed semantic/history evidence and focused target proof are complete. Blob identity alone is not sufficient for `REUSE`.

# Boundaries

- No maintained OTClient write unless a concrete client-contract requirement is proven.
- No protocol, persistence, combat, vocation, Wheel, chat, guild, map/OTBM, `items.otb`, asset, schema or deployment expansion.
- Preserve OAM-004 player SQL / later KV non-atomicity limitation.
- Do not start OAM-024 until the separate OAM-023 lifecycle archive and durable program reconciliation are both merged.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-20T10:38:00+02:00
head: 2dae43289aeb80b97cde0b76cd53e1d149ac0e35
branch: docs/oam-023-parties-revalidation
pr: "616"
status: validating
next_action: Complete exact-head Otheryn PR #47 CI and merge only after all target gates pass.
context_routes:
  - agent-governance
  - cpp-runtime
owned_paths:
  - docs/agents/OTERYN_OAM_023_PARTIES_REVALIDATION.md
  - docs/agents/tasks/active/CAN-20260720-oteryn-parties-revalidation.md
proven:
  - OAM-022 is fully and durably complete and OAM-023 had not started before this task.
  - Immutable task-start baselines are Canary 0a39a0f76d5f811098dfaa7be9deea40347279d5 and Otheryn 50dfa248251f245f5519495a4fbd430b6814ffe4.
  - Canonical parties depends only on completed OAM-005 character-lifecycle.
  - No current Canary open PR changed-file audit overlaps src/creatures/players/grouping/party.*.
  - Target upstream and legacy party.cpp and party.hpp are exact-identical at the pinned baselines.
derived: []
unknown:
  - Final OAM-023 disposition remains conditional on exact-head target proof completion.
conflicts: []
rejected_hypotheses:
  - Blob identity alone is sufficient to classify parties as REUSE.
  - wheel-of-destiny should be selected despite separate active parity ownership.
changed_paths:
  - docs/agents/tasks/active/CAN-20260720-oteryn-parties-revalidation.md
blockers:
  - Otheryn PR #47 exact-head full CI is still running.
first_failure:
  marker: Agent Task Ownership #2774
  evidence: The task checkpoint heading lacked the required fenced machine-readable YAML block.
validation:
  - command: GitHub Actions Agent Task Ownership #2774
    result: FAIL
    evidence: active-task-ownership artifact 8455265118 isolated the checkpoint-format failure.
  - command: Otheryn PR #47 ready-state CI #172
    result: NOT_RUN
    evidence: Run 29728346757 is in progress on exact target head c3ff8bb09b736ec835ce1f49ee0d96b8e208ea88.
```
