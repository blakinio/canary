---
task_id: CAN-20260717-physical-teleport-e2e
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: "OTS-E2E-PHYSICAL-TELEPORT"
status: validating
agent: "Codex GPT-5"
branch: test/e2e-physical-teleport-final-v2
base_branch: main
created: 2026-07-17T21:35:00+02:00
updated: 2026-07-18T15:28:44+02:00
last_verified_commit: "68c590a4fa671f678f087063b9e43278443569cf"
risk: high
related_issue: ""
related_pr: "525"
depends_on:
  - CAN-20260717-physical-movement-e2e-v2
  - CAN-PROGRAM-E2E-PLATFORM
blocks: []
owned_paths:
  exclusive:
    - tests/e2e/scenarios/movement/physical-teleport.json
    - docs/agents/tasks/active/CAN-20260717-physical-teleport-e2e.md
  shared: []
  read_only:
    - .github/workflows/universal-agent-e2e.yml
    - tools/e2e/run_agent_e2e.py
    - tools/e2e/run_physical_e2e.sh
    - tools/e2e/client/agent_e2e_scenario.lua
modules_touched:
  - Universal OTS E2E physical gameplay scenarios
reuses:
  - existing Universal Agent E2E lifecycle
  - existing controlled OTClient action-plan driver
  - existing OTBM item/mechanic audit scanner
  - existing two-session login logout persistence relog sentinel
public_interfaces: []
cross_repo_tasks: []
---

# Goal

Prove one deterministic real-client teleport traversal on the exact Canary map used by the accepted physical movement scenario, without creating another parser, renderer, workflow, orchestrator, or physical runner.

# Acceptance criteria

- [x] Reuse the existing `otbm_item_audit_scan.cpp` scanner on the exact map SHA used by physical movement.
- [x] Select explicit teleport source `32353,32223,7` and destination `32255,32204,8` from static OTBM mechanic evidence.
- [x] Keep the maintained OTClient and canonical physical login/logout/persistence/relog lifecycle unchanged.
- [x] Obtain real physical-client evidence that the bounded route triggers the teleport.
- [x] Pin exact destination only after real physical artifact evidence.
- [ ] Pass exact-final-head Ownership, CI, selected physical E2E, and Required physical E2E on the latest-main reconstruction.
- [ ] Squash merge, then archive through lifecycle automation.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-18T15:28:44+02:00
head: 68c590a4fa671f678f087063b9e43278443569cf
branch: test/e2e-physical-teleport-final-v2
pr: 525
status: validating
context_routes:
  - universal-e2e
  - otbm
  - agent-governance
owned_paths:
  - tests/e2e/scenarios/movement/physical-teleport.json
  - docs/agents/tasks/active/CAN-20260717-physical-teleport-e2e.md
proven:
  - OTBM audit selected source 32353,32223,7 item 1959 with teleportDestination 32255,32204,8 on the exact physical-movement map SHA a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2
  - discovery run 29618756104 physically proved initial_position=32369,32241,7 endpoint=32255,32204,8 floor_delta=1 plan success safe logout persistence relog second safe logout and e2e success
  - discovery artifact 8421982161 digest sha256:fef57aea0b47df739bce2636b68f996915c84cdb01c5241cf12518d8b9cea2fe
  - exact destination 32255,32204,8 was pinned only after discovery artifact evidence
  - exact-final attempt 29620535521 exposed an asynchronous intermediate observe_position_changed false negative and artifact 8422447484 isolated the first failure at probe-west-1
  - intermediate diagnostic probes were removed without changing bounded route endpoint floor delta or lifecycle assertions
  - corrected exact-final run 29633781590 passed Physical client movement/physical-teleport and Required physical E2E on head ab8138490c6a6fd8dee15b2e07451710201cd5af
  - corrected exact-final artifact 8426633331 digest sha256:9dbfda5d6358bc0efbf20df2c4e09d197256e7018cce85db4fde0899a38ad111 proved endpoint 32255,32204,8 delta 1 persistence relog and e2e success
  - synchronized run 29634778752 passed Physical client movement/physical-teleport and Required physical E2E on head 0bdc15202ac389ef1e0afe3005a5d3e1da273d2c
  - synchronized artifact 8426999692 digest sha256:a737d6aa293e996c9578107843e1e8fc57afb6b8d6d6b8e2da41e8f196f35868 again proves initial_position=32369,32241,7 endpoint=32255,32204,8 floor_delta=1 plan success persistence relog and e2e success
  - PR 525 run 29635866062 passed the selected physical teleport and Required physical E2E on head 08dc51bcda21786f144624e959fe2a0bf41292be
  - PR 525 run 29638112035 passed the selected physical teleport and Required physical E2E on head fdf17d8e63cd9f17ca15b6201f97c256404c97e1
  - later exact-head runs 29638851693, 29639687754, and 29640869875 accepted every scheduled walk request but stopped at three different non-teleport positions 32360,32217,7, 32365,32225,7, and 32362,32217,7
  - current-head final-gate run 29640869875 first failed at floor-delta after endpoint-position reported 32362,32217,7; artifact 8428812587 digest sha256:87ecc2e7ecca37ba89307097c1f14065d35a7cda54c974bd1cfeed07f814d62e
  - the action driver treats a walk step as successful after accepted requests and its configured delays; it does not confirm arrival at each intermediate tile
  - branch merged current origin/main 051f4101cdd90b36c7f550d7f9f73c31db2a6575 before repair commit 68c590a4fa671f678f087063b9e43278443569cf
  - repair commit 68c590a4fa671f678f087063b9e43278443569cf preserves the proven 48-tile route and uses 2500 ms pacing for a 121500 ms action plan inside the unchanged 180000 ms global timeout
  - original PR 511 accumulated stale merge-base history while main advanced and was never force-pushed
  - replacement PR 525 starts directly from main d9c967d6e9b778da11a206d134d559f38ec1b8c8 and changes exactly the two feature-owned files
  - no shared E2E platform file is modified
  - no OTBM or client asset is committed
  - no external reference repository is modified
derived:
  - runtime evidence independently matches the OTBM-audited teleportDestination and proves actual teleport traversal
  - exact endpoint and floor-delta assertions are authoritative final proof; intermediate position probes are unnecessary and race-prone
  - clean reconstruction on latest main is safer than force-rebasing the stale-history PR 511 branch
  - the identical route's divergent endpoints after accepted walk requests make 800-1100 ms request pacing nondeterministic for this 48-tile physical traversal
unknown:
  - whether conservative 2500 ms pacing reaches the proven teleport endpoint reliably on the next exact-head physical run
conflicts: []
first_failure:
  marker: exact-final-teleport-source-not-reached
  evidence: current-head run 29640869875 artifact 8428812587 reported endpoint 32362,32217,7 and floor delta 0 instead of proven destination 32255,32204,8 and delta 1
rejected_hypotheses:
  - treating OTBM teleportDestination as runtime proof
  - guessing a destination from sprites or item names
  - building a second OTBM parser or physical E2E runner
  - pinning exact destination before physical artifact evidence
  - solving long-route ping timeout by modifying shared E2E transport infrastructure
  - force-pushing the stale-history PR 511 branch
  - treating accepted walk requests as proof of completed movement
changed_paths:
  - tests/e2e/scenarios/movement/physical-teleport.json
  - docs/agents/tasks/active/CAN-20260717-physical-teleport-e2e.md
validation:
  - command: OTBM item/mechanic audit on exact movement map
    result: PASS
    evidence: source 32353,32223,7 -> destination 32255,32204,8
  - command: Universal Agent E2E discovery
    result: PASS
    evidence: run 29618756104 artifact 8421982161
  - command: corrected exact-final Universal Agent E2E
    result: PASS
    evidence: run 29633781590 artifact 8426633331
  - command: synchronized exact-final Universal Agent E2E
    result: PASS
    evidence: run 29634778752 artifact 8426999692
  - command: PR 525 selected physical teleport and Required physical E2E
    result: PASS
    evidence: runs 29635866062 and 29638112035
  - command: PR 525 current-head final-gate selected physical teleport and Required physical E2E
    result: FAIL
    evidence: run 29640869875 artifact 8428812587; endpoint 32362,32217,7 and floor delta 0
  - command: python tools/agents/task_ownership.py
    result: PASS
    evidence: 13 active task records validated after merging origin/main 051f4101c
  - command: python tools/agents/checkpoint.py docs/agents/tasks/active/CAN-20260717-physical-teleport-e2e.md --require-checkpoint
    result: PASS
    evidence: checkpoint validated locally before final commit
  - command: python -m unittest tests.e2e.test_agent_e2e_pr_scenario_selection tests.e2e.test_agent_e2e_scenario_plan
    result: PASS
    evidence: 30 tests passed after merging origin/main 051f4101c
  - command: python tools/e2e/run_agent_e2e.py validate and resolve --suite movement --scenario physical-teleport
    result: PASS
    evidence: 5 scenarios validated and movement/physical-teleport resolved with 2500 ms pacing
  - command: deterministic route and timing calculation
    result: PASS
    evidence: route endpoint equals audited source 32353,32223,7 and planned action time 121500 ms is below global timeout 180000 ms
blockers: []
next_action: Commit and push this final checkpoint with ci:final-gate already applied, then require exact-head Ownership, CI, selected physical teleport, and Required physical E2E success before readiness or merge.
```
