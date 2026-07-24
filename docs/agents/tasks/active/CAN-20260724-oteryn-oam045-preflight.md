---
task_id: CAN-20260724-oteryn-oam045-preflight
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-045
status: review
agent: "GPT-5.6 Thinking"
branch: dudantas/oam-045-protocol-session-handoff-governance
base_branch: main
created: 2026-07-24
updated: 2026-07-24
last_verified_commit: "e1ef6dcb8704ebd72e5fdc4576a03e7df6329aea"
risk: high
related_issue: ""
related_pr: "899"
depends_on:
  - OAM-044 durably completed as 92c550b41d0f7d1c8c71f4b85dfa81dfb6488f4f
  - Canary OAM-045 preflight merged as 2798dce948d8bf27f9b1325356d6db4676a8b6ba
  - Otheryn OAM-045 target and lifecycle completed
blocks:
  - OAM-045 Canary lifecycle archive
  - OAM-045 durable program reconciliation
  - OAM-046 start
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260724-oteryn-oam045-preflight.md
    - docs/agents/OTERYN_OAM_045_PROTOCOL_SESSION_HANDOFF_REVALIDATION.md
  shared: []
  read_only:
    - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
    - docs/agents/OTERYN_TARGET_ARCHITECTURE_CONTRACT.md
    - docs/agents/real-tibia/registry/modules/protocol-session-handoff.yaml
    - docs/agents/real-tibia/TSD_010_PROTOCOL_CLIENT_REPORT.md
modules_touched:
  - oteryn-architecture-migration
  - protocol-session-handoff
cross_repo_tasks:
  - Otheryn PR 103 feature merge 597ba62c558ed4e35db38502903ae83e0b2921ec
  - Otheryn PR 104 lifecycle merge e8f683e61427e9967cbc180b837220d4b7487d85
---

# OAM-045 protocol session handoff revalidation

## Final disposition

`protocol-session-handoff → ADAPT`

The inherited hint-store structure is retained, but two package-owned invariants required bounded corrections: an expired 30-second lease could consume a still-valid reusable hint, and replacement at full capacity could evict an unrelated oldest hint before deleting the superseded entry. Otheryn now fails closed on expired leases and performs replacement cleanup before applying the unchanged capacity limit.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-24T23:10:00+02:00
head: e1ef6dcb8704ebd72e5fdc4576a03e7df6329aea
branch: dudantas/oam-045-protocol-session-handoff-governance
pr: 899
status: validating
context_routes:
  - agent-governance
  - cross-repo
  - protocol-client
owned_paths:
  - docs/agents/tasks/active/CAN-20260724-oteryn-oam045-preflight.md
  - docs/agents/OTERYN_OAM_045_PROTOCOL_SESSION_HANDOFF_REVALIDATION.md
proven:
  - OAM-044 is durably complete as 92c550b41d0f7d1c8c71f4b85dfa81dfb6488f4f.
  - Canary OAM-045 preflight selected protocol-session-handoff with REVALIDATE and merged as 2798dce948d8bf27f9b1325356d6db4676a8b6ba.
  - Otheryn target task-start was e1eed52119ba21a29cb29cbac0793ed2a2b9d0c6 and reviewed upstream was 7323503b3dc61ed86bf1f04a611b2d0aec64b35a.
  - Before adaptation, target, upstream, live legacy Canary and the OAM-006 tested target shared header blob 446e7769196fb9a750e13c8402b38c8752243729 and implementation blob 3e57e16649e20121f52c6c4b67b632808b7af363.
  - The inherited consume path did not enforce the 30-second lease deadline while reusable hints can live for 24 hours.
  - The inherited registration path enforced capacity before removing overlapping-character replacements, allowing unrelated eviction at full capacity.
  - Otheryn enforces lease expiry and performs replacement cleanup before the unchanged capacity check; the adapted implementation blob is e53e430122c746ee9254e4e80eac66a247a59317.
  - Focused fixtures cover one-shot and reusable flows, lease expiry, ordinary replacement, replacement at capacity, mixed-wire ambiguity, blocked profiles and true capacity overflow.
  - Otheryn feature final head 77c46466c79fd5bda02ee7cdf9c07af97c110705 passed Autofix 30125033564, CI 30125033725 and Required 30125033619.
  - Otheryn PR 103 had no comments, reviews or review threads, no target-main drift and squash-merged as 597ba62c558ed4e35db38502903ae83e0b2921ec.
  - Otheryn lifecycle PR 104 changed one logical active/archive path, passed Required 30126189758, had a clean audit and merged as e8f683e61427e9967cbc180b837220d4b7487d85.
  - Canary governance task-start main is 93413bd53e9a40f0ff3c4f55986036b10be44e0f.
  - Canary governance PR 899 was opened from head e1ef6dcb8704ebd72e5fdc4576a03e7df6329aea with ci:final-gate applied before this synchronization commit.
  - docs/agents/OTERYN_OAM_045_PROTOCOL_SESSION_HANDOFF_REVALIDATION.md records the exact evidence and nonclaim boundaries.
derived:
  - protocol-session-handoff requires ADAPT rather than REUSE because two package-owned invariants were ineffective.
  - Two bounded local corrections preserve the inherited state machine; no rewrite or ownership expansion is justified.
unknown:
  - Security strength, collision behavior and timing properties of session-hash comparison.
  - Replay resistance and race freedom across complete login-to-game orchestration.
  - Multi-process or distributed consistency.
  - Which hint branches were physically exercised by OAM-006.
  - Physical-client parity for non-current profiles.
conflicts: []
first_failure:
  marker: ignored-lease-expiry
  evidence: The target consume path accepted a structurally valid expired lease while reusable candidates could outlive it; subsequent bounded review also isolated premature unrelated eviction during replacement at full capacity.
rejected_hypotheses:
  - Finalize REUSE from exact source identity alone.
  - Expand the adaptation into authentication, transport, login serialization or generic session fencing.
  - Claim cryptographic, replay or race-freedom properties from SHA-256 storage, mutex use or TTLs.
  - Extend OAM-006 current-profile physical evidence to every hint branch or legacy profile.
  - Rewrite the store when two bounded local corrections preserve the canonical structure.
changed_paths:
  - docs/agents/tasks/active/CAN-20260724-oteryn-oam045-preflight.md
  - docs/agents/OTERYN_OAM_045_PROTOCOL_SESSION_HANDOFF_REVALIDATION.md
validation:
  - command: exact target/upstream/legacy/OAM-006 source and ownership review
    result: PASS
    evidence: Exact roots, continuity and bounded ownership are recorded in the governance report.
  - command: Otheryn focused protocol session handoff contract
    result: PASS
    evidence: CI 30125033725 compiled and executed the registered unit-test matrix.
  - command: Otheryn feature and lifecycle exact-head gates and audits
    result: PASS
    evidence: PR 103 merged as 597ba62c558ed4e35db38502903ae83e0b2921ec and PR 104 merged as e8f683e61427e9967cbc180b837220d4b7487d85 after green gates and clean audits.
  - command: Canary governance exact-head gates and audit
    result: NOT_RUN
    evidence: The final governance head must pass Agent Task Ownership and final-gate CI before merge.
blockers:
  - Canary governance exact-head validation and merge
  - Canary lifecycle archive merge
  - durable OAM-045 program reconciliation
next_action: Mark PR 899 ready, require exact-head Agent Task Ownership and final-gate CI, audit discussions and Canary-main drift, then squash-merge with the expected head.
```
