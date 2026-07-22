---
task_id: CAN-20260722-oteryn-oam037-preflight
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
status: blocked
agent: "GPT-5.6 Thinking"
branch: dudantas/oam-037-target-proof-plan
base_branch: main
created: 2026-07-22
updated: 2026-07-23
last_verified_commit: "6b23be9f4eeb513cd181dba8ccbc9a96b98e739f"
risk: medium
related_issue: ""
related_pr: "744"
depends_on:
  - OAM-036 formally complete
blocks:
  - OAM-037 target proof and final disposition
  - OAM-038 through OAM-040
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260722-oteryn-oam037-preflight.md
  shared: []
  read_only:
    - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
    - docs/agents/real-tibia/registry/modules/**
modules_touched:
  - oteryn-architecture-migration
  - raids
cross_repo_tasks: []
---

# OAM-037 Fresh Preflight

## Goal

Perform a fresh dependency-valid canonical-module preflight after formal OAM-036 closure. Do not implement OAM-037 production code in this task.

## Selected package

`raids` is the selected dependency-valid OAM-037 canonical package.

Preflight disposition: `REUSE candidate`.

The final OAM-037 disposition still requires bounded target-side proof. This preflight does not claim raid probability or timing parity, data-definition completeness, restart behavior, distributed or multichannel raid safety, physical-client E2E or Real Tibia parity.

## Bounded target-proof plan

Read-only target analysis establishes the smallest evidence-backed Otheryn package as four proof/task paths with no production mutation expected:

- `docs/agents/tasks/active/OTH-20260723-oam037-raids-reuse.md`;
- `docs/oam-037-raids-reuse.md`;
- `tests/unit/game/oam_037_raids_reuse_test.cpp`;
- `tests/unit/game/CMakeLists.txt`.

The source-contract proof should bind the canonical `src/lua/creature/raids.cpp` and `src/lua/creature/raids.hpp` lifecycle by checking registry load/reload and interval/margin/repeat parsing, maintenance-lane periodic selection, scheduling-failure handling, running/non-repeat state, ordered event scheduling and reset/stop cleanup, plus announce/single-spawn/area-spawn/script event dispatch surfaces. The final disposition remains `REUSE` only if this bounded proof and exact-head target gates pass without production repair; otherwise the target task must reclassify to `ADAPT` based on concrete failing evidence.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-23T00:15:00+02:00
head: 6b23be9f4eeb513cd181dba8ccbc9a96b98e739f
branch: dudantas/oam-037-target-proof-plan
pr: 744
status: blocked
context_routes:
  - agent-governance
  - cross-repo
owned_paths:
  - docs/agents/tasks/active/CAN-20260722-oteryn-oam037-preflight.md
proven:
  - OAM-036 is formally complete after Otheryn target archive merge 3aaf77fe27600b274d2b9c9e6bd30d887e0afd0e.
  - OAM-037 selected canonical raids as a REUSE candidate after dependency ownership exact-root semantic donor and open-PR preflight.
  - Otheryn main remains 3aaf77fe27600b274d2b9c9e6bd30d887e0afd0e and has no OAM-037 branch or open OAM-037 raids PR.
  - Otheryn and fresh upstream share exact canonical raids.cpp blob d46a549a341e0872474bd723b10d1208fa22da8c and raids.hpp blob 777558e3e199816bb596636fc7487c38c29224ee.
  - Read-only source review confirms registry load reload interval margin repeat running state periodic selection event ordering reset cleanup and announce single-spawn area-spawn script dispatch are contained in the two canonical raids roots.
  - Target scheduling uses DispatcherLane::Maintenance for periodic checks and raid events and resets raid state when initial or subsequent scheduling fails.
  - Prior OAM-036 REUSE delivery establishes the target pattern of exactly four proof/task paths with no production mutation and source-contract regression coverage registered in tests/unit/game/CMakeLists.txt.
  - PR 744 final head 5879eeda0772bdb95cb95082ada1a3eba7652d33 passed Agent Task Ownership run 29960802967 and full CI run 29960803165 and was squash-merged as 6b23be9f4eeb513cd181dba8ccbc9a96b98e739f.
  - Program ordering requires bounded OAM-037 target proof final governance lifecycle durable reconciliation and target checkpoint archive before OAM-038 may start.
derived:
  - The smallest evidence-backed OAM-037 target package is an expected four-path REUSE proof with no production code change unless the bounded source-contract test exposes a concrete target defect.
  - The proof should assert registry parsing maintenance-lane scheduling failure recovery running and non-repeat lifecycle ordered event execution reset stop cleanup and all four canonical event kinds without claiming exact probability timing or content parity.
  - OAM-038 OAM-039 and OAM-040 cannot be started without violating the program ordering invariant.
unknown:
  - Final OAM-037 REUSE or ADAPT disposition until the four-path target proof is implemented and target gates execute.
  - Whether bounded proof execution exposes a concrete raids-owned target defect requiring production repair.
conflicts: []
first_failure:
  marker: OAM-037 target proof repository write boundary
  evidence: Current execution authority permits repository writes only in blakinio/canary while the mandatory four-path target proof must be created and validated in blakinio/Otheryn.
rejected_hypotheses:
  - Start OAM-038 through OAM-040 in Canary while OAM-037 target proof is pending; this would violate the program sequence and durable closure invariant.
  - Treat source blob identity or the read-only proof plan as final REUSE; final disposition remains gated on bounded target proof and exact-head target validation.
  - Import the divergent legacy raids.cpp wholesale; target and fresh upstream already retain stronger maintenance-lane scheduling and scheduling-failure handling.
changed_paths:
  - docs/agents/tasks/active/CAN-20260722-oteryn-oam037-preflight.md
validation:
  - command: PR 744 exact-final-head Agent Task Ownership and full CI
    result: PASS
    evidence: exact head 5879eeda0772bdb95cb95082ada1a3eba7652d33 completed runs 29960802967 and 29960803165 successfully
  - command: PR 744 review audit and expected-head squash merge
    result: PASS
    evidence: zero inline review threads zero submitted reviews and merge 6b23be9f4eeb513cd181dba8ccbc9a96b98e739f
  - command: fresh Otheryn main branch and PR search
    result: PASS
    evidence: main remains 3aaf77fe27600b274d2b9c9e6bd30d887e0afd0e with no oam-037 branch and no open OAM-037 raids PR
  - command: read-only raids source-contract boundary analysis
    result: PASS
    evidence: canonical blobs and lifecycle surfaces support a four-path REUSE proof package without expected production mutation
  - command: prior OAM-036 target proof pattern audit
    result: PASS
    evidence: PR 74 used task proof document source-contract unit test and CMake registration as the bounded no-production-change REUSE package
blockers:
  - Current execution authority permits writes only in blakinio/canary; the mandatory OAM-037 raids target proof requires a separately authorized blakinio/Otheryn write context.
next_action: Continue OAM-037 in a separately authorized blakinio/Otheryn context by creating the four-path raids REUSE proof package, run exact-head target gates, and reclassify to ADAPT only if concrete raids-owned proof failure requires production repair.
```
