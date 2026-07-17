---
task_id: CAN-20260717-physical-teleport-e2e
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: "OTS-E2E-PHYSICAL-TELEPORT"
status: implementing
agent: "GPT-5.5 Thinking"
branch: test/e2e-physical-teleport
base_branch: main
created: 2026-07-17T21:35:00+02:00
updated: 2026-07-17T21:35:00+02:00
last_verified_commit: "dbe0346d84d4aef695490515ea7106c1a940aba7"
risk: high
related_issue: ""
related_pr: ""
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
- [ ] Obtain real physical-client evidence that the bounded route triggers the teleport.
- [ ] Record real `step_position-changed_detail` and require the exact destination only after artifact discovery.
- [ ] Pass exact-final-head Ownership, CI, selected physical E2E, and Required physical E2E.
- [ ] Squash merge, then archive through lifecycle automation.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-17T21:35:00+02:00
head: dbe0346d84d4aef695490515ea7106c1a940aba7
branch: test/e2e-physical-teleport
pr: null
status: implementing
context_routes:
  - universal-e2e
  - otbm
  - agent-governance
owned_paths:
  - tests/e2e/scenarios/movement/physical-teleport.json
  - docs/agents/tasks/active/CAN-20260717-physical-teleport-e2e.md
proven:
  - uploaded discovery map SHA-256 a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2 exactly matches the map SHA recorded by the accepted physical movement artifact
  - existing repository scanner reports 17972761 tiles 23359571 placements 23852 unique item IDs and 9339 mechanic placements on that exact map, matching the documented real-map validation counts
  - nearest nonzero OTBM teleport destination candidate to the proven start is source 32353,32223,7 item 1959 destination 32255,32204,8
  - controlled client minimap data yields a bounded candidate route from 32369,32241,7 to the audited source without using generated imagery
  - scenario preserves canonical two-session safe logout persistence and relog markers
  - exact post-teleport destination is deliberately not asserted before real physical artifact evidence
  - no shared E2E platform file is modified
  - no OTBM or client asset is committed
  - no external reference repository is modified
derived:
  - a successful floor delta of 1 plus exact physical position detail matching the audited destination will distinguish actual traversal from merely walking near the source
  - the static OTBM audit selects the candidate but does not itself prove runtime teleport behavior
unknown:
  - whether the candidate minimap route is accepted step-for-step by the physical server runtime
  - exact real post-teleport position until the physical artifact is produced
  - first selected physical workflow conclusion on this branch
conflicts: []
first_failure:
  marker: physical-teleport-discovery-pending
  evidence: no selected physical-client run has executed this new scenario yet
rejected_hypotheses:
  - treating OTBM teleportDestination as runtime proof
  - guessing a destination from sprites or item names
  - building a second OTBM parser or physical E2E runner
  - pinning an exact destination marker before physical artifact evidence
changed_paths:
  - tests/e2e/scenarios/movement/physical-teleport.json
  - docs/agents/tasks/active/CAN-20260717-physical-teleport-e2e.md
validation:
  - command: existing otbm_item_audit_scan.cpp against exact movement map SHA
    result: PASS
    evidence: 17972761 tiles, 23359571 placements, 23852 unique item IDs, 9339 mechanics; source 32353,32223,7 -> destination 32255,32204,8
blockers: []
next_action: Open a same-repository draft PR so automatic scenario selection runs movement/physical-teleport through the existing Universal Agent E2E physical lifecycle; inspect the first physical artifact and fix only the first concrete runtime blocker.
```
