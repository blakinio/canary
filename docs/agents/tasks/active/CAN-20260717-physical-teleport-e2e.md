---
task_id: CAN-20260717-physical-teleport-e2e
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: "OTS-E2E-PHYSICAL-TELEPORT"
status: implementing
agent: "GPT-5.5 Thinking"
branch: test/e2e-physical-teleport
base_branch: main
created: 2026-07-17T21:35:00+02:00
updated: 2026-07-18T08:17:00+02:00
last_verified_commit: "7a25fbe19b0c1ee974634eb1222a063d70f0f354"
risk: high
related_issue: ""
related_pr: "511"
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
- [x] Select an explicit teleport source and destination from static OTBM mechanic evidence.
- [x] Keep the maintained OTClient and canonical physical login/logout/persistence/relog lifecycle unchanged.
- [x] Obtain real physical-client evidence that the bounded route triggers the teleport.
- [x] Record real `step_position-changed_detail` and require the exact destination only after artifact discovery.
- [ ] Pass exact-final-head Ownership, CI, selected physical E2E, and Required physical E2E.
- [ ] Squash merge, then archive through lifecycle automation.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-18T08:17:00+02:00
head: 7a25fbe19b0c1ee974634eb1222a063d70f0f354
branch: test/e2e-physical-teleport
pr: 511
status: validating
context_routes:
  - universal-e2e
  - otbm
  - agent-governance
owned_paths:
  - tests/e2e/scenarios/movement/physical-teleport.json
  - docs/agents/tasks/active/CAN-20260717-physical-teleport-e2e.md
proven:
  - uploaded discovery map SHA-256 a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2 exactly matches the map SHA recorded by the accepted physical movement artifact
  - existing repository scanner reports 17972761 tiles 23359571 placements 23852 unique item IDs and 9339 mechanic placements on that exact map
  - audited teleport source is 32353,32223,7 item 1959 with teleportDestination 32255,32204,8
  - initial 350 ms and 800 ms route attempts did not reach the teleport and were rejected as runtime proof
  - a 1500 ms attempt exceeded the server ping timeout and was rejected without changing shared transport infrastructure
  - segmented 1000 ms discovery run 29618756104 passed Physical client movement/physical-teleport and Required physical E2E
  - discovery artifact 8421982161 has digest sha256:fef57aea0b47df739bce2636b68f996915c84cdb01c5241cf12518d8b9cea2fe
  - client-events.tsv proves initial_position=32369,32241,7
  - segment probes prove route positions 32367,32241,7 then 32367,32218,7 then 32365,32218,7 then 32365,32217,7 then 32358,32217,7 then 32358,32216,7 then 32353,32216,7
  - final south segment physically triggered the teleport and step_probe-south-1_detail became 32255,32204,8
  - step_endpoint-position_detail and step_position-changed_detail both equal 32255,32204,8
  - step_floor-delta_detail equals 1
  - plan success was followed by safe logout server persistence relog second safe logout and e2e success
  - exact destination 32255,32204,8 was pinned into required markers only after physical artifact evidence
  - exact-final attempt on head 50239329663623a60035c282d78837ec19c21f6e passed Ownership and CI but physical run 29620535521 failed at the first intermediate probe after route-west-1
  - failure artifact 8422447484 shows route-west-1 action success followed immediately by probe-west-1 failure because the observed position had not updated yet
  - intermediate segment probes were diagnostic discovery instrumentation and are not required to prove the final teleport destination
  - final scenario now removes only the asynchronous intermediate probes while retaining all bounded walk segments exact endpoint 32255,32204,8 floor delta 1 canonical safe logout persistence relog and e2e markers
  - no shared E2E platform file is modified
  - no OTBM or client asset is committed
  - no external reference repository is modified
derived:
  - runtime evidence independently matches the OTBM-audited teleportDestination and therefore proves actual teleport traversal rather than merely approaching the source
  - exact endpoint and floor-delta assertions are the authoritative final teleport proof; intermediate observe_position_changed probes can race server position propagation and create false negatives
  - removing diagnostic probes reduces flakiness and runtime without weakening the final teleport assertion or canonical lifecycle proof
unknown:
  - whether current main advanced after the previous synchronization and therefore requires another non-force feature-tree sync before the next exact-final checkpoint
conflicts: []
first_failure:
  marker: exact-final-intermediate-probe-race
  evidence: run 29620535521 artifact 8422447484 failed at probe-west-1 immediately after route-west-1 action success with error position did not change; the earlier discovery run proved the complete identical bounded route and exact teleport destination
rejected_hypotheses:
  - treating OTBM teleportDestination as runtime proof
  - guessing a destination from sprites or item names
  - building a second OTBM parser or physical E2E runner
  - pinning an exact destination marker before physical artifact evidence
  - assuming walk action success means every server step completed
  - solving the long-route ping timeout by modifying shared E2E transport infrastructure
  - retaining asynchronous intermediate position probes as mandatory final-gate assertions after discovery evidence showed they can false-negative
changed_paths:
  - tests/e2e/scenarios/movement/physical-teleport.json
  - docs/agents/tasks/active/CAN-20260717-physical-teleport-e2e.md
validation:
  - command: existing otbm_item_audit_scan.cpp against exact movement map SHA
    result: PASS
    evidence: source 32353,32223,7 -> destination 32255,32204,8
  - command: Universal Agent E2E selected physical scenario on discovery head 6529e78189193473086570aa1ea6e3b0712bb96c
    result: PASS
    evidence: run 29618756104; artifact 8421982161; destination 32255,32204,8; delta 1; canonical persistence and relog markers complete
  - command: Required physical E2E
    result: PASS
    evidence: run 29618756104
  - command: exact-final Universal Agent E2E on head 50239329663623a60035c282d78837ec19c21f6e
    result: FAIL
    evidence: run 29620535521; artifact 8422447484; first failure probe-west-1 observe_position_changed position did not change immediately after route-west-1
  - command: evidence-backed scenario correction
    result: PASS
    evidence: commit 7a25fbe19b0c1ee974634eb1222a063d70f0f354 removes only intermediate diagnostic probes and their required markers; exact endpoint floor delta persistence and relog assertions remain
blockers: []
next_action: Synchronize the two feature-owned files to current main without force push, create one task-only exact-final checkpoint, require green Ownership CI selected physical teleport and Required physical E2E on that exact head, then ready, fresh ready-state CI, squash merge, and lifecycle archive.
```
