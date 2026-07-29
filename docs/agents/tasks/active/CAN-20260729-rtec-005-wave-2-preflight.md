---
task_id: CAN-20260729-rtec-005-wave-2-preflight
program_id: CAN-PROGRAM-REAL-TIBIA-EVIDENCE-COLLECTION
coordination_id: RTEC-005-WAVE-2-PREFLIGHT
status: active
agent: "GPT-5.6 Thinking"
branch: docs/rtec-005-wave-2-preflight-20260729
base_branch: main
created: 2026-07-29T09:05:00+02:00
updated: 2026-07-29T09:05:00+02:00
last_verified_commit: "b19d8fb41c8390c1f672fde6403203ce97590955"
risk: medium
related_issue: ""
related_pr: ""
depends_on:
  - RTEC-005 wave 1
blocks:
  - RTEC-005 wave 2 coordinator and Collector workers
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260729-rtec-005-wave-2-preflight.md
    - docs/agents/programs/REAL_TIBIA_EVIDENCE_COLLECTION_PROGRAM.md
  shared: []
  read_only:
    - docs/agents/real-tibia/evidence/generated/EVIDENCE_INDEXES.json
    - docs/agents/real-tibia/evidence/modules/**
    - docs/agents/real-tibia/evidence/requests/**
    - docs/agents/real-tibia/registry/modules/chat-communication.yaml
    - docs/agents/real-tibia/registry/modules/engine-scheduler.yaml
    - src/creatures/interactions/chat.cpp
    - src/creatures/interactions/chat.hpp
    - src/game/scheduling/dispatcher.cpp
    - src/game/scheduling/dispatcher.hpp
    - src/game/scheduling/task.cpp
    - src/game/scheduling/task.hpp
    - src/lib/thread/thread_pool.cpp
    - src/lib/thread/thread_pool.hpp
modules_touched:
  - real-tibia-evidence-collection
  - chat-communication
  - engine-scheduler
reuses:
  - canary-real-tibia-evidence-record-v1
  - canary-real-tibia-owner-request-v1
  - canary-real-tibia-generated-indexes-v1
  - RTEC-004 and RTEC-005 wave 1 two-worker serialized-index result
public_interfaces: []
cross_repo_tasks: []
---

# Goal

Reconcile the live Real Tibia evidence programme after RTEC-005 wave 1 and select one fresh bounded wave of two independent absent dossier roots without changing evidence, owner requests, runtime, data, client, protocol, map, workflow or E2E paths.

# Acceptance criteria

- [x] Pin current `main` and the current published evidence/request state.
- [x] Select two absent dossier roots with disjoint registry and source paths.
- [x] Verify the selected paths do not overlap current open PR changed files.
- [x] Preserve the RTEC-005 cap of two Collector workers, two worker PRs and one coordinator-only serialized global-index lane.
- [x] Preserve every active owner request without lifecycle or content changes.
- [ ] Publish the bounded preflight through a draft PR and pass exact-head ownership and ordinary CI gates.

# Preflight result

## Current baseline

- Current `main`: `b19d8fb41c8390c1f672fde6403203ce97590955`.
- Published evidence view: `as_of=2026-07-26` with 13 evidence records, 3 active owner requests and 10 version-history records.
- Active owner requests remain:
  - `RTREQ-FEATURE-VOCATIONS-0001`;
  - `RTREQ-TCR-ITEM-DEFINITIONS-0001`;
  - `RTREQ-TCR-ITEM-DEFINITIONS-0002`.
- Open PRs inspected for changed-path overlap: #993, #991, #815, #559 and #526. None changes either selected dossier root, its registry record or its selected current-Canary source paths.

## Selected Collector A — `chat-communication`

- Dossier root `docs/agents/real-tibia/evidence/modules/chat-communication/` is absent.
- Registry record: `docs/agents/real-tibia/registry/modules/chat-communication.yaml` blob `d736ff891a48315aa4bd7c34a5a553ca1d31ffd3`.
- Current-Canary source pins at the preflight baseline:
  - `src/creatures/interactions/chat.cpp` blob `152a40857f4b184e968eb51601a75634d8d37946`;
  - `src/creatures/interactions/chat.hpp` blob `09f8a727fef239b95b1bb5da20356801769732f0`.
- Worker scope is the bounded channel registry, join/leave/speak callback and private-channel lifecycle source path. Protocol framing, party/guild membership, delivery, privacy, moderation and physical gameplay remain nonclaims.

## Selected Collector B — `engine-scheduler`

- Dossier root `docs/agents/real-tibia/evidence/modules/engine-scheduler/` is absent.
- Registry record: `docs/agents/real-tibia/registry/modules/engine-scheduler.yaml` blob `bcf728df9999d2bda9019918066200a69f1daad5`.
- Current-Canary source pins at the preflight baseline:
  - `src/game/scheduling/dispatcher.cpp` blob `8a537385a76095104c3ab71e19a770f6ad282c38`;
  - `src/game/scheduling/dispatcher.hpp` blob `22ffa032c2bb3fac4ad4189569a7dc1d43c0d699`;
  - `src/game/scheduling/task.cpp` blob `7747d584370a25f2569da987225b31d556b69472`;
  - `src/game/scheduling/task.hpp` blob `9435a7704a0da81ae12ffef5d18f9dc29bdbf882`;
  - `src/lib/thread/thread_pool.cpp` blob `c753278ae0e1b4f439e1ad72bbca599d575bbda6`;
  - `src/lib/thread/thread_pool.hpp` blob `a5e3c54fadecb53367b9d5580de2b1a053f94572`.
- Worker scope is the bounded dispatcher/task/thread-pool scheduling source path. Ordering, fairness, race freedom, shutdown correctness, gameplay timers and persistence scheduling remain nonclaims.

## Concurrency and write boundaries

- The two selected modules are outside the same serialization group and have disjoint dossier, registry and source roots.
- Each Collector owns only its task record, one module dossier directory and any request record it creates for that module.
- Workers must not edit the programme, shared generated index, existing owner requests, another worker dossier, runtime, data, client, protocol, map, workflow or E2E paths.
- One later coordinator task alone may adjudicate merged worker evidence and update `docs/agents/real-tibia/evidence/generated/EVIDENCE_INDEXES.json`.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-29T09:05:00+02:00
head: b19d8fb41c8390c1f672fde6403203ce97590955
branch: docs/rtec-005-wave-2-preflight-20260729
pr: none
status: implementing
context_routes:
  - agent-governance
  - real-tibia-parity
owned_paths:
  - docs/agents/tasks/active/CAN-20260729-rtec-005-wave-2-preflight.md
  - docs/agents/programs/REAL_TIBIA_EVIDENCE_COLLECTION_PROGRAM.md
proven:
  - current main is b19d8fb41c8390c1f672fde6403203ce97590955
  - the published evidence view contains 13 evidence records, 3 active owner requests and 10 version-history records at as_of 2026-07-26
  - chat-communication and engine-scheduler dossier roots are absent
  - both selected registry records and all selected current-Canary source files exist at the pinned blobs recorded above
  - open PR changed-file sets do not overlap the selected dossier, registry or source paths
  - RTEC-005 remains limited to two workers, two worker PRs and one serialized coordinator index lane
derived:
  - chat-communication and engine-scheduler form a safe bounded wave 2 candidate pair
  - no existing owner-request transition or shared-index mutation belongs in the preflight
unknown:
  - exact evidence claims each Collector will submit
  - whether either Collector will need a new owner request
  - pull request number and exact post-commit head for this preflight
conflicts: []
first_failure:
  marker: none
  evidence: no ownership or changed-path conflict found during connector-based preflight
rejected_hypotheses:
  - reuse the merged wave 1 task or PR: archived tasks and merged PRs are not continuation branches
  - select sanctions concurrently: the open security audit reviews related trust/security behavior, so a less coupled candidate is preferred
  - let workers update the shared global index: RTEC-005 requires one serialized coordinator lane
changed_paths:
  - docs/agents/tasks/active/CAN-20260729-rtec-005-wave-2-preflight.md
  - docs/agents/programs/REAL_TIBIA_EVIDENCE_COLLECTION_PROGRAM.md
validation:
  - command: connector-based current-main, registry, dossier and source-pin preflight
    result: PASS
    evidence: exact paths and blobs recorded in this task
  - command: open PR changed-file overlap review
    result: PASS
    evidence: PRs 993, 991, 815, 559 and 526 inspected
  - command: Agent Task Ownership and ordinary CI on the preflight head
    result: NOT_RUN
    evidence: pending published PR head
blockers: []
next_action: Update the programme queue and handoff, open the draft preflight PR, then verify exact-head ownership and ordinary CI before readiness.
```
