---
task_id: CAN-20260724-oteryn-oam045-preflight
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-045
status: review
agent: "GPT-5.6 Thinking"
branch: dudantas/oam-045-protocol-session-handoff-preflight
base_branch: main
created: 2026-07-24
updated: 2026-07-24
last_verified_commit: "92c550b41d0f7d1c8c71f4b85dfa81dfb6488f4f"
risk: high
related_issue: ""
related_pr: "895"
depends_on:
  - OAM-044 durably completed as 92c550b41d0f7d1c8c71f4b85dfa81dfb6488f4f
  - canonical protocol-compatibility completed by OAM-044
blocks:
  - OAM-045 Otheryn target proof
  - OAM-045 lifecycle and durable reconciliation
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260724-oteryn-oam045-preflight.md
  shared: []
  read_only:
    - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
    - docs/agents/OTERYN_TARGET_ARCHITECTURE_CONTRACT.md
    - docs/agents/real-tibia/registry/modules/protocol-session-handoff.yaml
    - docs/agents/real-tibia/TSD_010_PROTOCOL_CLIENT_REPORT.md
    - src/server/network/protocol/protocol_session_hint.hpp
    - src/server/network/protocol/protocol_session_hint.cpp
modules_touched:
  - oteryn-architecture-migration
  - protocol-session-handoff
cross_repo_tasks:
  - planned bounded Otheryn target proof after this preflight merges
---

# OAM-045 protocol session handoff preflight

## Selected canonical package

`protocol-session-handoff`

## Preflight disposition

`REVALIDATE`

No leading `REUSE`, `ADAPT` or `REWRITE` hypothesis is authorized. The target proof must isolate the bounded profile-hint register/claim/consume/expiry state machine and distinguish source identity from runtime, replay, race and authentication claims.

## Why this package is dependency-valid now

The canonical record depends only on `protocol-compatibility`. OAM-044 durably completed `protocol-compatibility → REUSE` as Canary merge `92c550b41d0f7d1c8c71f4b85dfa81dfb6488f4f`, so the dependency is now satisfied.

Other candidates were not selected:

- `network-transport` is dependency-free but open Canary PR #514 still owns interacting authenticated sequence/XTEA transport validation;
- `login-protocol` remains blocked on `network-transport` even though account authentication is complete;
- `physical-client-e2e`, `wheel-of-destiny` and `upstream-intelligence` are active under separate programs and have broader ownership;
- `deployment-operations` and `gameplay-analytics` are platform packages with wider tool/runtime surfaces and do not provide the direct dependency continuation from OAM-044.

## Live repository state

- Canary task-start main: `92c550b41d0f7d1c8c71f4b85dfa81dfb6488f4f`.
- Otheryn target main: `e1eed52119ba21a29cb29cbac0793ed2a2b9d0c6`.
- Current upstream Canary main: `7323503b3dc61ed86bf1f04a611b2d0aec64b35a`.
- Otheryn has no open pull requests.
- Canary has no open pull request matching `protocol_session_hint`, `protocol-session-handoff` or protocol-session-hint ownership.
- Open Canary PR #526 mentions handoff only within an evidence-only shared-state/economy audit and does not own the target runtime paths.
- Open Canary PR #514 owns network transport security validation, not `protocol_session_hint.*`.

## Exact source preflight

The selected package owns exactly:

- `src/server/network/protocol/protocol_session_hint.hpp`;
- `src/server/network/protocol/protocol_session_hint.cpp`.

Exact blobs are identical across target, current upstream and live legacy Canary:

- header: `446e7769196fb9a750e13c8402b38c8752243729`;
- implementation: `3e57e16649e20121f52c6c4b67b632808b7af363`.

The same blobs were present at Otheryn OAM-006 physical-test revision `c547d8ad70ef1252624c255476e6cb83fa125e14`, whose run `29531221365` passed two current-profile protocol-1525 login/relog cycles. This is continuity evidence only: it does not prove that every login/relog exercised every hint branch, nor does it prove replay resistance, race freedom or legacy-profile physical parity.

## Target-proof requirements

The Otheryn proof must:

1. pin exact target/current-upstream/legacy baselines and the two selected blobs;
2. inventory all public operations and state transitions: register, capacity eviction, duplicate-character replacement, claim by IP/required behavior, ambiguous-wire rejection, account/session/character/version matching, one-shot consumption, reusable refresh, explicit reusable cleanup and expiry cleanup;
3. add focused deterministic target fixtures without broad production mutation;
4. preserve `login-protocol`, `network-transport`, `protocol`, account authentication and generic session fencing ownership;
5. classify each behavior as confirmed, source-only, conflicting or unresolved;
6. explicitly reject promoting hash presence, mutex use, TTLs or passing current-profile E2E into security, race-free or all-profile claims;
7. finish with exactly one `REUSE`, `ADAPT` or `REWRITE` disposition supported by target evidence.

## Explicit boundaries

This package does not own or prove:

- password/token authentication or credential policy;
- secure login-token issuance/redemption;
- transport framing, checksums, sequences, XTEA or compression;
- game-world player attach/detach ownership;
- generic cross-process session fencing;
- replay resistance, constant-time comparison or cryptographic token security;
- race freedom beyond the reviewed in-process mutex boundary;
- physical-client parity for Tibia 11.00, CipSoft 8.60 or OTCv8;
- production protocol-stack or gameplay readiness.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-24T20:25:00+02:00
head: 09b77dcb898fa420b88e2b7ccf6706c523bed236
branch: dudantas/oam-045-protocol-session-handoff-preflight
pr: 895
status: validating
context_routes:
  - agent-governance
  - cross-repo
  - protocol-client
owned_paths:
  - docs/agents/tasks/active/CAN-20260724-oteryn-oam045-preflight.md
proven:
  - OAM-044 is durably complete as 92c550b41d0f7d1c8c71f4b85dfa81dfb6488f4f.
  - protocol-session-handoff depends only on completed protocol-compatibility.
  - Canary main is 92c550b41d0f7d1c8c71f4b85dfa81dfb6488f4f and Otheryn main is e1eed52119ba21a29cb29cbac0793ed2a2b9d0c6 at preflight.
  - Otheryn has no open PRs and Canary has no open exact-path owner for protocol_session_hint.*.
  - Open PR 514 remains network-transport-owned; open PR 526 is evidence-only and does not mutate the selected paths.
  - Target, upstream and live legacy share header blob 446e7769196fb9a750e13c8402b38c8752243729 and implementation blob 3e57e16649e20121f52c6c4b67b632808b7af363.
  - The same blobs existed at physically tested OAM-006 target revision c547d8ad70ef1252624c255476e6cb83fa125e14.
  - Canary PR 895 changes exactly this active task record and carries ci:final-gate before this synchronization commit.
derived:
  - protocol-session-handoff is the next dependency-valid, bounded, non-colliding canonical package.
  - Exact identity and inherited current-profile continuity justify target revalidation, not an automatic REUSE decision.
unknown:
  - Which hint branches were exercised by OAM-006 physical login/relog.
  - Security strength and collision properties of the account-session hash usage in this state machine.
  - Replay resistance and race freedom across complete login-to-game orchestration.
  - Behavior under multi-process or distributed deployment.
  - Physical-client parity for non-current profiles.
conflicts: []
first_failure:
  marker: none
  evidence: No preflight dependency or exact-path ownership conflict was found.
rejected_hypotheses:
  - Select network-transport while PR 514 owns interacting validation.
  - Treat matching blobs as sufficient REUSE proof.
  - Treat the hint store as authentication-token ownership.
  - Extend current-profile physical evidence to every profile and branch.
changed_paths:
  - docs/agents/tasks/active/CAN-20260724-oteryn-oam045-preflight.md
validation:
  - command: live Canary/Otheryn main and open-PR review
    result: PASS
    evidence: Exact live heads and open ownership are recorded above.
  - command: canonical dependency and ownership review
    result: PASS
    evidence: protocol-session-handoff depends only on completed protocol-compatibility and owns isolated protocol_session_hint.* roots.
  - command: exact target/upstream/legacy/OAM-006 blob review
    result: PASS
    evidence: Both selected roots are byte-identical across all reviewed revisions.
  - command: Canary preflight exact-head gates and audit
    result: NOT_RUN
    evidence: Final PR 895 head must pass Agent Task Ownership and final-gate CI before merge.
blockers:
  - Canary preflight PR 895 merge
next_action: Require exact-head Agent Task Ownership and final-gate CI on PR 895, audit comments, reviews, threads and Canary-main drift, then squash-merge with the expected head.
```
