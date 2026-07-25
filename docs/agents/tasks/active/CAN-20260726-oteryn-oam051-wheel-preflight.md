---
task_id: CAN-20260726-oteryn-oam051-wheel-preflight
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-051
status: implementing
agent: "GPT-5.6 Thinking"
branch: dudantas/oam-051-wheel-of-destiny-preflight
base_branch: main
created: 2026-07-26
updated: 2026-07-26
last_verified_commit: "d0c76c6f964a5266789b252173eb24832a309e80"
risk: high
related_issue: ""
related_pr: ""
depends_on:
  - OAM-050 durably completed as d0c76c6f964a5266789b252173eb24832a309e80
blocks:
  - OAM-051 exact target adaptation scope
  - OAM-051 target feature, lifecycle, governance and durable reconciliation
  - OAM-052 start
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260726-oteryn-oam051-wheel-preflight.md
  shared: []
  read_only:
    - docs/agents/real-tibia/registry/modules/wheel-of-destiny.yaml
    - docs/agents/programs/WHEEL_OF_DESTINY_PARITY_PROGRAM.md
    - docs/ai-agent/OTS_AI_WHEEL_OF_DESTINY_VALIDATION.md
    - docs/ai-agent/OTS_AI_WHEEL_OF_DESTINY_VALIDATION_PROJECT.md
    - src/creatures/players/components/wheel/**
    - src/io/io_wheel.*
    - src/server/network/protocol/protocolgame.*
    - src/creatures/combat/**
    - data/scripts/spells/**
    - data/modules/scripts/taskboard/**
    - tests/unit/players/**
    - tests/integration/**
    - blakinio/Otheryn
    - blakinio/otclient
    - opentibiabr/canary
    - zimbadev/crystalserver
---

# OAM-051 Wheel of Destiny preflight

Select canonical `wheel-of-destiny → ADAPT candidate` after durable OAM-050 closure.

The target must not bulk-copy the legacy Wheel subsystem. Canary contains useful reviewed hardening and the bounded Hunting Task Shop Promotion Point package, but the canonical module remains partial across persistence, protocol, combat effects, stances, replacement spells and gameplay E2E. OAM-051 therefore starts by isolating only evidence-backed target gaps and their exact dependency/client boundaries.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-26T01:20:00+02:00
head: d0c76c6f964a5266789b252173eb24832a309e80
branch: dudantas/oam-051-wheel-of-destiny-preflight
pr: null
status: investigating
context_routes:
  - agent-governance
  - cross-repo
  - real-tibia-parity
  - universal-e2e
  - github-actions
owned_paths:
  - docs/agents/tasks/active/CAN-20260726-oteryn-oam051-wheel-preflight.md
proven:
  - OAM-050 is durably complete as d0c76c6f964a5266789b252173eb24832a309e80 and no OAM implementation task remains active.
  - Fresh Canary main is d0c76c6f964a5266789b252173eb24832a309e80 and fresh Otheryn main is ff90e93d872b6b47720f711483a9832203d5258d.
  - Fresh comparison heads are opentibiabr/canary@7644bcbcbbad4a09e52a5707ed531e4dd21d8a79, blakinio/otclient@ff36aa74324eddbe6a64a79b23bd42d6a185fb7f and zimbadev/crystalserver@75e9c72e33ce2c3f193e4f2d2ff17ebae4bbfaac.
  - Otheryn has no open PR. Canary open PRs 948, 815, 559, 526 and 514 do not claim Wheel implementation paths; PR 948 is separately governed E2E baseline work and PR 514 is the existing network-transport blocker.
  - The Wheel programme has no active task and names WHEEL-003 as its preferred next parity behavior package only after fresh evidence review.
  - OTClient PR 25 mentions later Wheel fixes, but exact current-main comparison ff36aa74324eddbe6a64a79b23bd42d6a185fb7f...99655274358c80ef2a0c4f585c30cb74d965d63f changes only two audit documents; current open client PRs do not own Wheel runtime paths.
  - Canonical Wheel depends on combat, player-persistence and protocol. Otheryn already has combat reuse proof in OAM-013 commit 3628effc5f22e7edbdc66dc5f514e4df5c9f0cda, persistence hardening through OAM-004 including 4b5b94eced0f3c5d88b9a4293e849d888333e0cb and 67212530b03c10175da2c0d9eabcee8991a05924, and secure/current protocol foundations including OAM-006 commit c547d8ad70ef1252624c255476e6cb83fa125e14 plus OAM-044 protocol-profile proof 5c8f48e2a7cb7f841cfb6614e8e804245f17c0ca.
  - Current Otheryn and current upstream use identical taskboard.lua blob 23ec7e00121695d4fb35941921a05478d7476cea and intentionally send a zero-offer Task Shop window.
  - Current Canary taskboard.lua blob b15bd734df796032047c247dea4e3451c462f199 adds the reviewed Bonus Promotion offer, bounded 1 through 50 purchase cost, player KV persistence, Wheel point accounting and purchase handling delivered by PR 230.
  - Current Canary and Otheryn player_wheel.cpp blobs differ as bdd5e3fd3247b015e83f71fce3ef9b2311178695 versus 755c8adf53af87d860c0eaaceaed850cd10c492e; blob difference is discovery evidence only and still requires exact semantic patch review.
  - Canary Wheel audit/hardening PR 220 and Task Shop PR 230 are explicitly bounded historical deliveries; the programme rejects the broad claim that all Wheel 15.25 behavior is complete.
derived:
  - REUSE is not valid because the target lacks at least one reviewed bounded Wheel behavior already proven in Canary.
  - ADAPT is the leading disposition because useful legacy behavior exists, while partial, blocked-by-reference and client-coupled surfaces prohibit whole-module transfer.
  - The first target package must be selected from exact PR 220/230 semantic deltas and must preserve target architecture, OAM-004 persistence non-atomicity boundaries and maintained-client compatibility.
unknown:
  - Exact minimal subset of PR 220 hardening that remains absent from current Otheryn after upstream and prior OAM changes.
  - Whether all PR 230 server-side Task Shop fields remain compatible with current maintained OTClient ff36aa74324eddbe6a64a79b23bd42d6a185fb7f without a client mutation.
  - Exact official-source authority and deterministic runtime proof required for any 15.25 behavior beyond already merged PR 220/230 packages.
  - Whether OAM-051 can remain one coherent target adaptation or must stop after one smaller independently gated Wheel boundary.
conflicts: []
first_failure:
  marker: target-missing-reviewed-wheel-package
  command: exact current Canary/Otheryn/upstream Taskboard comparison
  result: FAIL
  evidence: Otheryn and upstream blob 23ec7e00121695d4fb35941921a05478d7476cea emit zero shop offers; Canary blob b15bd734df796032047c247dea4e3451c462f199 contains the reviewed bounded Bonus Promotion purchase path.
rejected_hypotheses:
  - Mark Wheel REUSE from upstream-derived target code or file presence.
  - Bulk-copy all legacy Wheel, combat, protocol, spell or Taskboard paths.
  - Treat PR 220 or broad PR 230 titles as complete Tibia 15.25 parity.
  - Start WHEEL-003 critical healing implementation as an automatic consequence of OAM selection.
  - Modify blakinio/otclient or external comparison repositories from this OAM task.
changed_paths:
  - docs/agents/tasks/active/CAN-20260726-oteryn-oam051-wheel-preflight.md
validation:
  - command: fresh main, open-PR, ownership and canonical dependency audit
    result: PASS
    evidence: No live OAM or Wheel owner conflicts; required target foundations exist and separately blocked network/login work is not claimed.
  - command: exact target/upstream/legacy Taskboard comparison
    result: PASS
    evidence: Target/upstream empty-shop identity and Canary bounded Bonus Promotion divergence are directly proven by exact blobs and source contents.
  - command: maintained-client overlap audit
    result: PASS
    evidence: Current-main comparison of open OTClient PR 25 changes only its audit task/report; other open client PRs own character-list, actionbar or login-shell paths.
  - command: final OAM-051 adaptation manifest proof
    result: NOT_RUN
    evidence: Exact PR 220/230 delta inventory, target applicability, client contract and target test plan must be completed before opening a target feature PR.
blockers:
  - exact semantic inventory of PR 220 and PR 230 against current Otheryn
  - bounded target adaptation manifest and validation plan
  - Canary preflight exact-head Ownership and CI
next_action: Inventory every PR 220 and PR 230 changed path against current Otheryn and upstream, classify each delta as applicable already-present obsolete conflicting or out-of-scope, then prove the smallest coherent ADAPT manifest before any target source branch is opened.
```