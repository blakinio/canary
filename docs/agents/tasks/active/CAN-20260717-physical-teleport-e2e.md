---
task_id: CAN-20260717-physical-teleport-e2e
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: "OTS-E2E-PHYSICAL-TELEPORT"
status: review
agent: "GPT-5.5 Thinking"
branch: test/e2e-physical-teleport
base_branch: main
created: 2026-07-17T21:35:00+02:00
updated: 2026-07-18T01:22:00+02:00
last_verified_commit: "07d985a3f390a5145bdad1fccb5beac627f8911c"
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
updated_at: 2026-07-18T01:22:00+02:00
head: 07d985a3f390a5145bdad1fccb5beac627f8911c
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
  - segmented 1000 ms discovery run 29618756104 physically reached the teleport and passed Physical client movement/physical-teleport plus Required physical E2E
  - discovery artifact 8421982161 has digest sha256:fef57aea0b47df739bce2636b68f996915c84cdb01c5241cf12518d8b9cea2fe
  - client-events.tsv proves initial_position=32369,32241,7
  - segment probes prove route positions 32367,32241,7 then 32367,32218,7 then 32365,32218,7 then 32365,32217,7 then 32358,32217,7 then 32358,32216,7 then 32353,32216,7
  - the final south segment physically triggered the teleport and step_probe-south-1_detail became 32255,32204,8
  - step_endpoint-position_detail and step_position-changed_detail both equal 32255,32204,8
  - step_floor-delta_detail equals 1
  - plan success was followed by safe logout server persistence relog second safe logout and e2e success
  - exact destination 32255,32204,8 was pinned into required markers only after physical artifact evidence
  - PR 511 changes only the feature-owned task and physical-teleport scenario
  - no shared E2E platform file is modified
  - no OTBM or client asset is committed
  - no external reference repository is modified
derived:
  - runtime evidence independently matches the OTBM-audited teleportDestination and therefore proves actual teleport traversal rather than merely approaching the source
  - segmented probes are deterministic route evidence and keep total runtime below the server ping timeout without changing canonical transport settings
unknown:
  - current main SHA after floor-change lifecycle completion
  - exact final head after required non-force synchronization and final checkpoint
  - exact-final workflow run identifiers
conflicts: []
first_failure:
  marker: final-gate-pending
  evidence: physical teleport discovery is proven and pinned; synchronization to current main and exact-final-head validation remain before merge
rejected_hypotheses:
  - treating OTBM teleportDestination as runtime proof
  - guessing a destination from sprites or item names
  - building a second OTBM parser or physical E2E runner
  - pinning an exact destination marker before physical artifact evidence
  - assuming walk action success means every server step completed
  - solving the long-route ping timeout by modifying shared E2E transport infrastructure
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
blockers: []
next_action: Synchronize PR 511 to current main without force push, create one task-only exact final checkpoint, apply ci:final-gate, and require Ownership CI selected physical teleport and Required physical E2E on that exact head before ready and squash merge.
```
