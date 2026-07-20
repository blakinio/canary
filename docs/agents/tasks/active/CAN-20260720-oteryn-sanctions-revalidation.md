---
task_id: CAN-20260720-oteryn-sanctions-revalidation
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-024
status: implementing
agent: "GPT-5.5 Thinking"
branch: docs/oam-024-sanctions-revalidation
base_branch: main
created: 2026-07-20
updated: 2026-07-20
last_verified_commit: "3fe0130a408d201d0ca846f86a37b0ab20479932"
risk: medium
related_pr: ""
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
  - existing target/upstream sanctions core pending evidence-driven disposition
public_interfaces: []
cross_repo_tasks: []
---

# Goal

Revalidate canonical OAM-024 `sanctions`, classify the smallest dependency-valid clean-target disposition from current evidence, deliver only the bounded target implementation or proof required by that disposition, and complete target, governance, lifecycle archive and durable program reconciliation without absorbing protocol transport, account authentication, generic security analytics or unrelated E2E work.

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

# Fresh preflight

- OAM-023 durable reconciliation is merged at Canary `3fe0130a408d201d0ca846f86a37b0ab20479932`.
- Durable program state records OAM-001..OAM-023 complete, OAM-023 archived and OAM-024 NOT STARTED before this task.
- Otheryn main is `bcc3e9f7e3e704f3c012bda8693648d52741630f`.
- Fresh upstream Canary is `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`.
- Maintained OTClient is `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`.
- Open Canary PRs #620, #559, #526 and #514 have no changed-file overlap with canonical `ban.*` or these OAM-024 governance paths.
- Otheryn, maintained OTClient and upstream Canary have no open PRs at task start.
- Parallel security work treats source/runtime paths as read-only evidence or owns separate validation tooling; no active task claims `ban.*` for mutation.
- OTBM/E2E work remains independent and out of scope.

# Initial evidence

At immutable task-start baselines, both canonical files are blob-identical across legacy, target and fresh upstream:

- `ban.cpp`: `ca4c11ea98d6a8f4b6281f0bb5e84d742ff21ecc`
- `ban.hpp`: `48086b3efef370b2c0e1fab8f85513a95e47dcad`

Blob identity is supporting evidence only and does not establish `REUSE`. Semantic/history review and focused target proof remain required.

# Plan

1. Bind this task to its early draft governance PR and freeze the current task head.
2. Audit target/upstream/legacy sanctions semantics and relevant delivered legacy history for a stronger donor or blocking coupling.
3. Classify `REUSE`, `ADAPT`, `REWRITE`, `DO_NOT_MIGRATE`, `EXPERIMENTAL_ONLY` or remain `REVALIDATE` strictly from evidence.
4. Create one `dudantas/` target branch and the smallest target implementation/proof required by the disposition.
5. Require exact-head target CI/review/changed-file/main-drift gates and expected-head squash merge.
6. Reconcile Canary governance, then perform a separate active-to-archive lifecycle PR and separate one-file durable program reconciliation.
7. Do not start OAM-025 before durable OAM-024 closure.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-20
head: 3fe0130a408d201d0ca846f86a37b0ab20479932
branch: docs/oam-024-sanctions-revalidation
pr: null
status: implementing
context_routes:
  - agent-governance
  - cpp-runtime
owned_paths:
  - docs/agents/tasks/active/CAN-20260720-oteryn-sanctions-revalidation.md
  - docs/agents/OTERYN_OAM_024_SANCTIONS_REVALIDATION.md
proven:
  - OAM-023 durable reconciliation is merged at Canary 3fe0130a408d201d0ca846f86a37b0ab20479932
  - OAM-024 was not started in the durable program record before this task
  - canonical sanctions depends only on completed OAM-004 database-connection
  - canonical production boundary is src/creatures/players/management/ban.*
  - task-start Otheryn main is bcc3e9f7e3e704f3c012bda8693648d52741630f
  - fresh upstream Canary is 71a0f92b4da3f550b292fa7536a0e35c2769f1ae
  - maintained OTClient is 2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f
  - task-start ban.cpp and ban.hpp blobs are identical across legacy target and fresh upstream
  - current open PR changed-file audits show no overlap with canonical ban.*
derived:
  - sanctions is narrower than the other dependency-valid candidates chat-communication cyclopedia guilds and creature-definitions
  - blob identity alone is insufficient for REUSE and a stronger legacy donor or enforcement coupling would change the disposition
unknown:
  - exact governance PR number until the early draft PR is opened
  - final migration disposition until semantic and legacy-history review completes
  - exact target proof shape and final target head until classification completes
blockers: []
conflicts: []
rejected_hypotheses:
  - selecting cyclopedia solely because it is the next broad progression family is rejected
  - selecting wheel-of-destiny while its separate parity programme is active is rejected
  - inferring REUSE solely from path or blob identity is rejected
changed_paths:
  - docs/agents/tasks/active/CAN-20260720-oteryn-sanctions-revalidation.md
validation:
  - command: live repository head and open-PR preflight
    result: PASS
    evidence: exact task-start SHAs and open-PR changed-file audits recorded above
first_failure: null
next_action: open the early draft governance PR, bind related_pr/checkpoint metadata, then continue sanctions semantic and history review
```
