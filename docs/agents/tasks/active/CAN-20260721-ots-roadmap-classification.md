---
task_id: CAN-20260721-ots-roadmap-classification
program_id: CAN-PROGRAM-OTS-FUTURE-GAMEPLAY-SYSTEMS
status: review
agent: "GPT-5.6 Thinking"
branch: docs/ots-roadmap-classification-20260721
base_branch: main
created: 2026-07-21
updated: 2026-07-21
last_verified_commit: "91c4ab3a7e29484ea213c777ea89e7a96bbf95a7"
risk: low
related_issue: ""
related_pr: "674"
depends_on: []
blocks: []
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260721-ots-roadmap-classification.md
    - docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS_CLASSIFICATION.md
  shared: []
  read_only:
    - docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS.md
    - docs/ai-agent/OTS_SKILL_PROGRESSION_2_0.md
modules_touched: []
reuses:
  - docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS.md
  - docs/ai-agent/OTS_SKILL_PROGRESSION_2_0.md
public_interfaces: []
cross_repo_tasks: []
---

# CAN-20260721 — OTS roadmap proposal classification

## Goal

Create a durable, authoritative classification index for every currently recorded OTS gameplay proposal so original-Tibia systems, Tibia extensions, OTS inspirations, our own designs and external/client/security tooling are not conflated.

## Scope

- Documentation only.
- Classify each currently listed proposal with `ORIGIN` and `TYPE`.
- Preserve Weapon Proficiency as `TIBIA-OFFICIAL`, not OTS-original.
- Use conservative `TIBIA-BASELINE` where exact current-Tibia parity has not been freshly proven.
- Keep discussed-but-not-approved OTS ideas in a separate candidate section rather than silently promoting them into the approved backlog.
- Do not implement gameplay/client/server behavior.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-21T13:25:00+02:00
head: b919111d1b8799c71aececd987034c0d01e8f526
branch: docs/ots-roadmap-classification-20260721
pr: 674
status: review
context_routes:
  - agent-governance
owned_paths:
  - docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS_CLASSIFICATION.md
  - docs/agents/tasks/active/CAN-20260721-ots-roadmap-classification.md
proven:
  - The durable roadmap is docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS.md.
  - The detailed skill/proficiency design is docs/ai-agent/OTS_SKILL_PROGRESSION_2_0.md.
  - The user requested consistent provenance/type classification for the proposals.
  - The new classification index contains 58 currently listed proposals with explicit ORIGIN and TYPE fields.
  - Weapon Proficiency is classified as TIBIA-OFFICIAL and PARITY-INTEGRATION, not an OTS invention.
  - Additional OTS systems discussed during research remain separated as candidates not automatically promoted into the approved roadmap backlog.
  - PR #674 targets blakinio/canary:main from docs/ots-roadmap-classification-20260721 and changes only the classification index plus this bounded task record.
derived:
  - A separate authoritative classification index avoids rewriting the large durable roadmap while preserving one-to-one proposal classification and can be maintained alongside it.
unknown:
  - Exact current-Tibia parity for entries marked TIBIA-BASELINE must be reverified before implementation.
  - Current Canary/OTClient implementation support for each proposal is outside this documentation-only task.
conflicts: []
first_failure:
  marker: none
  evidence: none
rejected_hypotheses:
  - Every system discussed in another OTS should be treated as OTS-original.
  - Weapon Proficiency should be attributed to TibiaScape or duplicated as a custom Weapon Mastery system.
changed_paths:
  - docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS_CLASSIFICATION.md
  - docs/agents/tasks/active/CAN-20260721-ots-roadmap-classification.md
validation:
  - command: Classification coverage review
    result: PASS
    evidence: All 58 proposals previously summarized from the durable roadmap and Skill Progression 2.0 are represented in the classification index.
  - command: PR #674 changed-file scope
    result: PASS
    evidence: Only the classification index and bounded task record are changed.
blockers:
  - Required current-head ownership, AI Agent Tools and CI checks must pass before merge.
next_action: Validate PR #674 current-head required checks; if all required gates pass and no review blockers remain, enable squash auto-merge.
```
