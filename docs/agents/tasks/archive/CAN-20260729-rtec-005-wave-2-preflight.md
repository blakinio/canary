---
task_id: CAN-20260729-rtec-005-wave-2-preflight
program_id: CAN-PROGRAM-REAL-TIBIA-EVIDENCE-COLLECTION
coordination_id: RTEC-005-WAVE-2-PREFLIGHT
status: completed
agent: "GPT-5.6 Thinking"
branch: docs/rtec-005-wave-2-preflight-20260729
base_branch: main
created: 2026-07-29T09:05:00+02:00
updated: 2026-07-29T09:41:14+02:00
last_verified_commit: "02d7aafa0dd9a9880b0ff82ccb950d6cb0c792ca"
risk: medium
related_issue: ""
related_pr: "995"
depends_on:
  - RTEC-005 wave 1
blocks: []
owned_paths:
  exclusive:
    - docs/agents/tasks/archive/CAN-20260729-rtec-005-wave-2-preflight.md
  shared: []
  read_only:
    - docs/agents/programs/REAL_TIBIA_EVIDENCE_COLLECTION_PROGRAM.md
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

# Result

- Selected `chat-communication` and `engine-scheduler` as the RTEC-005 wave 2 Collector roots.
- Proved both dossier roots were absent and their registry/source paths were disjoint.
- Preserved the bounded cap of two Collector workers, two worker PRs and one coordinator-only serialized global-index lane.
- Preserved all three active owner requests without lifecycle or content changes:
  - `RTREQ-FEATURE-VOCATIONS-0001`;
  - `RTREQ-TCR-ITEM-DEFINITIONS-0001`;
  - `RTREQ-TCR-ITEM-DEFINITIONS-0002`.
- Updated the durable programme queue and handoff through PR #995.
- PR #995 passed exact-head ownership, full Linux release/debug, Docker image/quickstart, Lua, Fast Checks and the repository `Required` gate.
- PR #995 squash-merged to `main` as `02d7aafa0dd9a9880b0ff82ccb950d6cb0c792ca` on 2026-07-29.

# Selected Collector boundaries

## Collector A — `chat-communication`

- Registry record: `docs/agents/real-tibia/registry/modules/chat-communication.yaml` blob `d736ff891a48315aa4bd7c34a5a553ca1d31ffd3`.
- Current-Canary source pins:
  - `src/creatures/interactions/chat.cpp` blob `152a40857f4b184e968eb51601a75634d8d37946`;
  - `src/creatures/interactions/chat.hpp` blob `09f8a727fef239b95b1bb5da20356801769732f0`.
- Bounded scope: channel registry, join/leave/speak callbacks and private-channel lifecycle discovery.
- Nonclaims: protocol framing, party/guild membership, delivery, privacy, moderation and physical gameplay.

## Collector B — `engine-scheduler`

- Registry record: `docs/agents/real-tibia/registry/modules/engine-scheduler.yaml` blob `bcf728df9999d2bda9019918066200a69f1daad5`.
- Current-Canary source pins:
  - `src/game/scheduling/dispatcher.cpp` blob `8a537385a76095104c3ab71e19a770f6ad282c38`;
  - `src/game/scheduling/dispatcher.hpp` blob `22ffa032c2bb3fac4ad4189569a7dc1d43c0d699`;
  - `src/game/scheduling/task.cpp` blob `7747d584370a25f2569da987225b31d556b69472`;
  - `src/game/scheduling/task.hpp` blob `9435a7704a0da81ae12ffef5d18f9dc29bdbf882`;
  - `src/lib/thread/thread_pool.cpp` blob `c753278ae0e1b4f439e1ad72bbca599d575bbda6`;
  - `src/lib/thread/thread_pool.hpp` blob `a5e3c54fadecb53367b9d5580de2b1a053f94572`.
- Bounded scope: dispatcher/task/thread-pool delayed and cyclic scheduling, cancellation, execution grouping and shutdown-path discovery.
- Nonclaims: ordering, fairness, race freedom, shutdown correctness, gameplay timers and persistence scheduling.

# Final checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-29T09:41:14+02:00
head: 5de77197d69050bd5480efd428b8a6ae352cc739
branch: docs/rtec-005-wave-2-preflight-20260729
pr: 995
merge_sha: 02d7aafa0dd9a9880b0ff82ccb950d6cb0c792ca
status: completed
context_routes:
  - agent-governance
  - real-tibia-parity
proven:
  - the published evidence baseline contains 13 evidence records, 3 active owner requests and 10 version-history records at as_of 2026-07-26
  - chat-communication and engine-scheduler dossier roots were absent at preflight
  - both selected registry records and all selected current-Canary source files existed at the pinned blobs recorded above
  - open PR changed-file sets did not overlap the selected dossier, registry or source paths
  - the intervening main advance through Game Catalog PR 991 was disjoint from both selected roots
  - RTEC-005 remains limited to two workers, two worker PRs and one serialized coordinator index lane
  - Agent Task Ownership run 30431391742 passed on final head 5de77197d69050bd5480efd428b8a6ae352cc739
  - CI run 30431436375 passed Lua, Fast Checks, Linux release/debug, Docker image, Docker quickstart and Required on the final head
  - PR 995 squash-merged as 02d7aafa0dd9a9880b0ff82ccb950d6cb0c792ca
derived:
  - chat-communication and engine-scheduler are a safe bounded RTEC-005 wave 2 pair
  - one coordinator task must precede worker branches and alone owns later shared-index adjudication
unknown:
  - exact evidence claims each Collector will submit
  - whether either Collector will need a new owner request
conflicts: []
first_failure:
  marker: Agent Task Ownership / Validate changed active task checkpoints
  evidence: early runs 30430981753 and 30431112170 established the distinction between frontmatter lifecycle status and checkpoint execution status; the accepted final lifecycle state was ready
rejected_hypotheses:
  - reuse the merged wave 1 task or PR
  - select sanctions while the security audit covered related trust behavior
  - let workers update the shared global index
  - replace the branch after the disjoint main advance
  - use active or validating as frontmatter lifecycle status
validation:
  - command: Agent Task Ownership
    result: PASS
    evidence: run 30431391742 at 5de77197d69050bd5480efd428b8a6ae352cc739
  - command: repository full final gate
    result: PASS
    evidence: CI run 30431436375 at 5de77197d69050bd5480efd428b8a6ae352cc739
  - command: squash merge
    result: PASS
    evidence: PR 995 merged as 02d7aafa0dd9a9880b0ff82ccb950d6cb0c792ca
blockers: []
next_action: Create one RTEC-005 wave 2 coordinator task before any chat-communication or engine-scheduler worker branch.
```
