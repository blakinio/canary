---
task_id: CAN-20260717-physical-teleport-e2e
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: "OTS-E2E-PHYSICAL-TELEPORT"
status: implementing
agent: "GPT-5.5 Thinking"
branch: test/e2e-physical-teleport-final-v2
base_branch: main
created: 2026-07-17T21:35:00+02:00
updated: 2026-07-18T09:30:00+02:00
last_verified_commit: "52e3164ceceed431f8d08652100635e77515c416"
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
updated_at: 2026-07-18T09:30:00+02:00
head: 52e3164ceceed431f8d08652100635e77515c416
branch: test/e2e-physical-teleport-final-v2
pr: 525
status: implementing
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
  - original PR 511 accumulated stale merge-base history while main advanced and was never force-pushed
  - replacement PR 525 starts directly from main d9c967d6e9b778da11a206d134d559f38ec1b8c8 and changes exactly the two feature-owned files
  - no shared E2E platform file is modified
  - no OTBM or client asset is committed
  - no external reference repository is modified
derived:
  - runtime evidence independently matches the OTBM-audited teleportDestination and proves actual teleport traversal
  - exact endpoint and floor-delta assertions are authoritative final proof; intermediate position probes are unnecessary and race-prone
  - clean reconstruction on latest main is safer than force-rebasing the stale-history PR 511 branch
unknown:
  - exact final-gate workflow run identifiers on PR 525 after this task checkpoint commit
conflicts: []
first_failure:
  marker: exact-final-intermediate-probe-race
  evidence: run 29620535521 artifact 8422447484 failed at probe-west-1 immediately after route-west-1 action success; corrected scenario later passed two independent exact physical runs
rejected_hypotheses:
  - treating OTBM teleportDestination as runtime proof
  - guessing a destination from sprites or item names
  - building a second OTBM parser or physical E2E runner
  - pinning exact destination before physical artifact evidence
  - solving long-route ping timeout by modifying shared E2E transport infrastructure
  - force-pushing the stale-history PR 511 branch
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
blockers: []
next_action: Close superseded PR 511, apply ci:final-gate to PR 525, require green Ownership CI selected physical teleport and Required physical E2E on the resulting exact head, then ready, fresh ready-state CI, squash merge, and lifecycle archive.
```
