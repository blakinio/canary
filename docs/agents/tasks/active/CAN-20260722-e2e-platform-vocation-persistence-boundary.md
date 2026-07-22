---
task_id: CAN-20260722-e2e-platform-vocation-persistence-boundary
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-PLATFORM-VOCATION-PERSISTENCE-BOUNDARY
status: implementing
agent: "GPT-5.6 Thinking"
branch: fix/e2e-platform-vocation-persistence-boundary
base_branch: main
created: 2026-07-22
updated: 2026-07-22
last_verified_commit: "27a2f87d1a329d95f0d0e40622208dffbf42031f"
risk: low
related_issue: ""
related_pr: ""
depends_on:
  - PR #718 Universal E2E run 29914323150 artifact 8527963786
blocks:
  - CAN-20260721-e2e-gameplay-003-canary-promotion
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260722-e2e-platform-vocation-persistence-boundary.md
    - tools/e2e/persistence_assertions.py
    - tests/e2e/test_player_vocation_persistence.py
    - docs/e2e/PERSISTENCE_ASSERTION_MATRIX.md
  read_only:
    - tools/e2e/run_agent_e2e.py
    - tools/e2e/client/agent_e2e_scenario.lua
    - data/XML/vocations.xml
    - tests/e2e/scenarios/npc/canary-promotion.json
modules_touched:
  - Universal E2E typed persistence assertion contract
reuses:
  - canonical two-session M3 lifecycle
  - fixed semantic player_vocation to Canary server vocation mapping
  - existing post-cycle scalar SQL evaluator
public_interfaces:
  - player_vocation remains a semantic typed assertion but moves to the database-only post-cycle evidence boundary
cross_repo_tasks: []
---

# CAN-20260722 — Correct player_vocation persistence evidence boundary

## Goal

Correct the Universal Physical E2E `player_vocation` M3 contract so it does not claim exact promoted-vocation equality from `LocalPlayer.getVocation()` when physical evidence shows that getter exposes the base vocation family after relog. Preserve the exact semantic server-vocation SQL assertion and the full two-session lifecycle.

## Acceptance criteria

- [ ] Keep the feature-owned `player_vocation` semantic input and fixed Canary server vocation mapping unchanged.
- [ ] Stop materializing `player_vocation` as a controlled-client phase-two `player_field` equality check.
- [ ] Keep exact post-cycle SQL equality against `players.vocation` after the canonical two-session lifecycle.
- [ ] Preserve all other client-readable persistence assertion types unchanged.
- [ ] Update focused tests to prove `player_vocation` is database-only while its semantic SQL mapping remains fixed.
- [ ] Update the canonical persistence matrix to describe the corrected evidence boundary without claiming exact promoted-vocation client equality.
- [ ] Do not modify feature-owned PR #718 scenario, shared runner lifecycle, controlled OTClient automation, Canary vocation configuration, or production gameplay behavior.
- [ ] Pass ownership, focused tests, CI and applicable Universal E2E gates on the exact final head before merge.
- [ ] Merge through the normal autonomous gate, then return to PR #718 for a fresh physical run.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-22T11:45:00Z
head: 27a2f87d1a329d95f0d0e40622208dffbf42031f
branch: fix/e2e-platform-vocation-persistence-boundary
pr: none
status: implementing
context_routes:
  - universal-e2e
  - agent-governance
owned_paths:
  - docs/agents/tasks/active/CAN-20260722-e2e-platform-vocation-persistence-boundary.md
  - tools/e2e/persistence_assertions.py
  - tests/e2e/test_player_vocation_persistence.py
  - docs/e2e/PERSISTENCE_ASSERTION_MATRIX.md
proven:
  - PR #718 exact-head run 29914323150 reached the real npc/canary-promotion physical scenario after Canary and controlled OTClient builds passed.
  - artifact 8527963786 records successful public hi plus NPC-private promot and yes actions, safe first logout, second login, and then client persistence failure actual=2 expected=12 for royal_paladin.
  - the same artifact's final SQL assertions all passed, including players.vocation=7 and players.balance=0, proving the promotion and durable economy effect succeeded on the server.
  - data/XML/vocations.xml maps Royal Paladin server id 7 to configured clientid 12 and baseid 3.
  - controlled OTClient parsePlayerInfo reads one vocation byte and stores it in LocalPlayer; physical post-relog LocalPlayer.getVocation() nevertheless exposed 2 for the promoted Royal Paladin session.
  - therefore LocalPlayer.getVocation() is not a trustworthy exact promoted-vocation equality surface for the current physical protocol path.
derived:
  - the smallest truthful reusable correction is to keep player_vocation semantic SQL verification after the full relog cycle but remove its exact controlled-client equality claim.
  - changing the feature scenario wait cadence or expected value to 2 would not prove Royal Paladin; 2 is also the base Paladin client value.
unknown:
  - whether another future client-visible surface can independently distinguish promoted vocation without relying on SQL; none is proven by current evidence.
conflicts: []
first_failure:
  marker: persistence check promoted-vocation (vocation) failed: actual=2 expected=12
  evidence: PR #718 Universal Agent E2E run 29914323150, Physical client job 88909987894, artifact 8527963786; final SQL simultaneously passed vocation=7 and balance=0.
rejected_hypotheses:
  - NPC-private speech still fails to promote: final SQL proves vocation=7 and balance=0.
  - a longer wait is required for promotion persistence: the durable SQL state is already correct after the canonical logout/relog cycle.
  - change royal_paladin client expectation from 12 to 2: that would collapse Royal Paladin onto base Paladin and make the client check non-discriminating.
changed_paths:
  - docs/agents/tasks/active/CAN-20260722-e2e-platform-vocation-persistence-boundary.md
validation:
  - command: PR #718 Universal Agent E2E run 29914323150 / Physical client job 88909987894
    result: FAIL
    evidence: exact client vocation equality failed actual=2 expected=12 while final server vocation=7 and balance=0 SQL assertions passed.
blockers: []
next_action: Implement the smallest platform contract correction, add focused regression coverage, open a draft PR, bind this task record, apply ci:final-gate, and validate the exact final head.
```
