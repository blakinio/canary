---
task_id: CAN-20260720-oteryn-sanctions-revalidation
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-024
status: ready
agent: "GPT-5.5 Thinking"
branch: docs/oam-024-sanctions-revalidation
base_branch: main
created: 2026-07-20
updated: 2026-07-20
last_verified_commit: "3fe0130a408d201d0ca846f86a37b0ab20479932"
risk: medium
related_pr: "621"
depends_on:
  - OAM-004 database-connection
blocks:
  - OAM-025
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260720-oteryn-sanctions-revalidation.md
    - docs/agents/OTERYN_OAM_024_SANCTIONS_REVALIDATION.md
  shared: []
  read_only:
    - src/creatures/players/management/ban.cpp
    - src/creatures/players/management/ban.hpp
    - blakinio/Otheryn
    - opentibiabr/canary
    - blakinio/otclient
modules_touched:
  - sanctions
reuses:
  - OAM-004 database-connection boundary
  - existing sanctions enforcement core
public_interfaces: []
cross_repo_tasks: []
---

# Goal

Revalidate canonical OAM-024 `sanctions`, classify the smallest dependency-valid clean-target disposition from current evidence, deliver only the bounded target implementation or proof required by that disposition, and complete target, governance, lifecycle archive and durable program reconciliation without absorbing protocol transport, account authentication, generic security analytics or unrelated E2E work.

# Final disposition

```text
sanctions → ADAPT
```

# Immutable task-start baselines

- Canary: `3fe0130a408d201d0ca846f86a37b0ab20479932`
- Otheryn: `bcc3e9f7e3e704f3c012bda8693648d52741630f`
- fresh upstream Canary: `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`
- maintained OTClient: `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`

# Canonical boundary

Canonical registry record: `docs/agents/real-tibia/registry/modules/sanctions.yaml`.

Production boundary:

```text
src/creatures/players/management/ban.*
```

Canonical dependency: completed OAM-004 `database-connection`.

Explicit exclusions include account credential verification, PvP skull/frag rules, chat moderation policy, generic security analytics, AI investigation, protocol packet redesign, maintained-client changes and any claim that every sanction is enforced at every entry point.

# Fresh preflight and evidence

- OAM-023 durable reconciliation was merged at Canary `3fe0130a408d201d0ca846f86a37b0ab20479932` before OAM-024 began.
- Durable program state recorded OAM-001..OAM-023 complete, OAM-023 archived and OAM-024 NOT STARTED before this task.
- Task-start Otheryn main was `bcc3e9f7e3e704f3c012bda8693648d52741630f`.
- Fresh upstream Canary was `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`.
- Maintained OTClient was `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`.
- Task-start open Canary PRs #620, #559, #526 and #514 had no changed-file overlap with canonical `ban.*` or these governance paths.
- Otheryn, maintained OTClient and upstream Canary had no open PRs at task start.
- Parallel security work treated source/runtime paths as read-only evidence or owned separate validation tooling; no active task claimed `ban.*` for mutation.
- OTBM/E2E work remained independent and out of scope.
- At immutable task-start baselines, `ban.cpp` blob `ca4c11ea98d6a8f4b6281f0bb5e84d742ff21ecc` and `ban.hpp` blob `48086b3efef370b2c0e1fab8f85513a95e47dcad` were identical across legacy, target and fresh upstream. Blob identity was not accepted as sufficient `REUSE` evidence.
- Semantic review confirmed socket-accept throttling, login IP-ban lookup, game-login account-ban/namelock lookup and the expired account-ban history handoff.
- Relevant target and legacy history identified no stronger independent donor for canonical `ban.*`.
- The existing expired account-ban history `INSERT` and active-ban `DELETE` were two independent asynchronous writes without one rollback boundary.
- Completed OAM-004 already provides the target `DBTransaction` primitive, making a bounded `ADAPT` the smallest valid disposition.

# Target delivery

Otheryn PR #48 final head:

```text
58ba19e0affe75f47c4185c41327880f8403503b
```

The final target diff has exactly four paths:

```text
docs/oam-024-sanctions-adapt.md
src/creatures/players/management/ban.cpp
tests/integration/database/CMakeLists.txt
tests/integration/database/sanctions_it.cpp
```

The adaptation moves only expired account-ban history insertion and active-row deletion into one `DBTransaction` under `SELECT ... FOR UPDATE`; active/permanent ban behavior is preserved and IP-ban behavior is unchanged.

Exact-head gates:

- autofix.ci #153 run `29734614481`: SUCCESS
- CI #179 run `29734614607`: SUCCESS
- Required #160 run `29734614503`: SUCCESS
- Linux debug CTest: `406/406 PASS`
- `SanctionsRepositoryDBTest`: `3/3 PASS`
- test-log artifact `8458101363`
- digest `sha256:97b9aeb5e93bac69461720671ee58bfe5742fd20df2710b139d0aa2298cd30fc`
- target comments/reviews/review threads: 0/0/0
- target-main drift from immutable target baseline before merge: 0

PR #48 merged by expected-head squash as:

```text
65d364b216843db27e84a19a673eee4e6d766c68
```

# Remaining lifecycle

1. Merge this governance reconciliation only after exact-head Ownership/CI/review/changed-file/main-drift gates.
2. Archive this task in a separate authoritative lifecycle PR.
3. Merge a separate one-file durable program reconciliation recording OAM-024 complete and OAM-025 NOT STARTED.
4. Do not begin OAM-025 before that durable reconciliation is merged.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-20
head: d22ccb90b46f5f348c696eb40040376d27c70ec5
branch: docs/oam-024-sanctions-revalidation
pr: 621
status: ready
context_routes:
  - agent-governance
  - cpp-runtime
owned_paths:
  - docs/agents/tasks/active/CAN-20260720-oteryn-sanctions-revalidation.md
  - docs/agents/OTERYN_OAM_024_SANCTIONS_REVALIDATION.md
proven:
  - OAM-023 durable reconciliation preceded OAM-024 task start
  - canonical sanctions depends only on completed OAM-004 database-connection
  - canonical production boundary is src/creatures/players/management/ban.*
  - task-start open PR and ownership audits found no overlapping ban.* writer
  - blob identity was treated only as supporting evidence
  - semantic and history review found no stronger independent legacy donor
  - original account-ban expiry used separate asynchronous history insert and active-row delete writes
  - bounded target adaptation uses existing OAM-004 DBTransaction for the expiry handoff
  - final target head is 58ba19e0affe75f47c4185c41327880f8403503b
  - target exact-head autofix CI and Required gates passed
  - Linux debug CTest passed 406 of 406 and focused sanctions tests passed 3 of 3
  - target merge is 65d364b216843db27e84a19a673eee4e6d766c68
  - Canary main has no drift from immutable task-start baseline before final governance update
derived:
  - sanctions ADAPT is narrower and better supported than selecting broader dependency-valid candidates
  - rollback-safe expiry archival closes only the account-ban history handoff and does not claim generic persistence redesign
unknown:
  - final governance merge SHA until PR 621 passes exact-head gates and merges
  - lifecycle merge SHA until separate archive PR completes
  - durable reconciliation merge SHA until separate program-only PR completes
blockers: []
conflicts: []
rejected_hypotheses:
  - sanctions REUSE solely from blob identity is rejected
  - broad protocol or authentication changes are rejected as outside canonical sanctions ownership
  - IP-ban cleanup changes are rejected from OAM-024 because they were independent of the focused proven defect
changed_paths:
  - docs/agents/tasks/active/CAN-20260720-oteryn-sanctions-revalidation.md
  - docs/agents/OTERYN_OAM_024_SANCTIONS_REVALIDATION.md
validation:
  - command: target exact-head CI and focused integration proof
    result: PASS
    evidence: CI 179 run 29734614607; Required 160 run 29734614503; CTest 406/406; SanctionsRepositoryDBTest 3/3
  - command: target review and main-drift audit
    result: PASS
    evidence: comments reviews threads 0/0/0; Otheryn main remained bcc3e9f7e3e704f3c012bda8693648d52741630f before merge
first_failure: {}
next_action: pass final exact-head governance gates on PR 621, audit and expected-head squash merge, then perform separate lifecycle archive
```
