---
task_id: CAN-20260719-oteryn-imbuements-revalidation
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-019
status: implementing
agent: "GPT-5.5 Thinking"
branch: docs/oam-019-imbuements-revalidation
base_branch: main
created: 2026-07-19
updated: 2026-07-19T15:15:10+02:00
last_verified_commit: "0db6289cc55069ddb0194a58758bcc97c242bf8b"
risk: high
related_pr: "588"
depends_on:
  - OAM-013
blocks:
  - OAM-020
modules_touched:
  - imbuements
owned_paths:
  exclusive:
    - docs/agents/OTERYN_OAM_019_IMBUEMENTS_REVALIDATION.md
    - docs/agents/tasks/active/CAN-20260719-oteryn-imbuements-revalidation.md
---

# Goal

Revalidate canonical OAM-019 `imbuements` against immutable fresh task-start baselines and migrate only the strongest coherent dependency-valid implementation into Otheryn.

# Final disposition

```text
imbuements → ADAPT
```

# Immutable task-start baselines

```text
Canary:   e551f3fd33c9642399bb1e70d1f2f6383464b936
Otheryn:  7ba76d2754a060a9a9eec0a23c686aefac725af2
upstream: 691614c1a302aee776002ca3851eca399be1a82c
OTClient: 2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f
```

# Dependency and ownership result

Canonical `imbuements` depends on completed `combat` and `player-persistence` boundaries and interacts with `protocol`. No overlapping live Imbuement runtime/data write ownership existed at task start.

# Accepted donor chain

Merged legacy Canary repairs accepted as one coherent bounded adaptation:
- PR #86 — configured-storage filter correctness;
- PR #206 — Powerful Forgotten Knowledge unlock storage reconciliation;
- PR #239 — Vibrancy scroll mappings;
- PR #251 — confirmed fee/Strike/Punch/Featherweight/Vibrancy data;
- PR #282 — direct numeric-ID premium/storage authorization before relevant resource mutation.

The target retained its existing architecture. No whole-file legacy `player.cpp` import was performed.

# Target completion

Otheryn PR #43 final head:

```text
4e993c4ee160fe03d8575c1b830ef71dde450562
```

Final exact-head gates:
- autofix.ci #121 / `29687711140`: PASS;
- Repository Audit #12 / `29687711133`: PASS;
- CI #142 / `29687711219`: PASS after one same-head macOS smoke rerun;
- Required #128 / `29687711131`: PASS;
- full Linux debug CTest: 367/367 PASS;
- new focused OAM-019 tests: 8/8 PASS;
- primary test artifact `8442743109`, digest `sha256:a0ef33bd15be8d004dce89ce5014782990961cb239c50e9f48f19d906694c6e0`.

The first macOS smoke attempt was a transient wrapper/timing failure: its artifact proved online startup and clean shutdown with empty stderr, and one permitted same-head rerun passed with no code change.

PR #43 changed exactly ten intended runtime/data/test paths, had zero comments/reviews/threads, no target-main drift, and merged by expected-head squash as:

```text
63547f30fc21e495217b8a92fa44aaad2db188ef
```

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-19T15:15:10+02:00
head: 68bb2e1b7b7bbf8edb70f6d1a624559a62376a87
branch: docs/oam-019-imbuements-revalidation
pr: 588
status: validating
next_action: Validate Agent Task Ownership, Imbuement Validation and full ci:final-gate CI on the exact final governance head created by this checkpoint commit. If every gate passes, comments/reviews/threads are clean and Canary main drift does not overlap the two governance paths, expected-head squash-merge PR #588; then perform separate authoritative lifecycle archive and one-file durable program reconciliation. Do not start OAM-020.
first_failure:
  marker: OAM-019 bounded materializer scope verifier
  evidence: The first bounded materializer applied the donor hunks but its verifier used git diff --name-only before staging, so generated untracked files were omitted from the comparison and the harness failed before producing an accepted target commit. The verifier was corrected to git add -A plus git diff --cached against origin/main. This was a proof/materialization harness defect, not an Imbuement production defect.
context_routes:
  - docs/agents/OTERYN_OAM_019_IMBUEMENTS_REVALIDATION.md
  - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
  - docs/agents/real-tibia/registry/modules/imbuements.yaml
  - docs/ai-agent/IMBUEMENT_VALIDATION_REPORT.md
owned_paths:
  - docs/agents/OTERYN_OAM_019_IMBUEMENTS_REVALIDATION.md
  - docs/agents/tasks/active/CAN-20260719-oteryn-imbuements-revalidation.md
proven:
  - OAM-018 is fully complete through target, governance, lifecycle and durable program reconciliation.
  - Fresh OAM-019 task-start baselines are pinned above.
  - Canonical imbuements depends on completed combat and player-persistence boundaries; protocol is an interaction.
  - No live task owned overlapping Imbuement runtime/data writes at task start.
  - Merged donor PRs 86, 206, 239, 251 and 282 form the accepted coherent bounded adaptation.
  - Target PR 43 final head 4e993c4ee160fe03d8575c1b830ef71dde450562 contains exactly ten intended runtime/data/test paths and no temporary materializer paths.
  - Target exact-head autofix 121, Repository Audit 12, CI 142 and Required 128 passed.
  - Linux debug full CTest passed 367/367 and the eight new focused OAM-019 tests passed 8/8.
  - Test artifact 8442743109 has digest sha256:a0ef33bd15be8d004dce89ce5014782990961cb239c50e9f48f19d906694c6e0.
  - The initial macOS smoke failure was transient harness/timing behavior; same-head rerun passed without code changes.
  - Target comments, reviews and review threads were empty and Otheryn main had no drift before merge.
  - Target PR 43 merged by expected-head squash as 63547f30fc21e495217b8a92fa44aaad2db188ef.
  - Canary pre-final task schema checks passed after binding frontmatter and checkpoint to PR 588.
derived:
  - Final OAM-019 disposition is imbuements ADAPT, not REUSE.
  - No client/protocol wire-shape change is required for the accepted bounded adaptation because existing presentation/transport surfaces consume the same server registry and no wire contract changed.
unknown:
  - Canary governance merge SHA until PR 588 completes exact-final-head gates and merge.
  - Authoritative lifecycle and durable program reconciliation SHAs until those separate stages complete.
conflicts: []
rejected_hypotheses:
  - Selecting market merely because it is adjacent in the items-economy inventory despite its additional protocol/client dependency burden.
  - Treating target/upstream file presence as sufficient evidence for Imbuement REUSE.
  - Treating the bounded materializer verifier failure as a production Imbuement defect.
  - Treating the first macOS smoke wrapper failure as a production Imbuement defect after its artifact proved a clean online startup/shutdown and the same-head rerun passed.
changed_paths:
  - docs/agents/OTERYN_OAM_019_IMBUEMENTS_REVALIDATION.md
  - docs/agents/tasks/active/CAN-20260719-oteryn-imbuements-revalidation.md
blockers: []
validation:
  - command: OAM-019 fresh dependency and ownership preflight
    result: PASS
    evidence: Immutable Canary/Otheryn/upstream/OTClient baselines pinned; no overlapping live Imbuement write ownership; dependencies completed.
  - command: Otheryn PR 43 exact final head validation
    result: PASS
    evidence: autofix 121, Repository Audit 12, CI 142 and Required 128 passed on 4e993c4ee160fe03d8575c1b830ef71dde450562; CTest 367/367; focused OAM-019 8/8.
  - command: Otheryn PR 43 final audit and expected-head merge
    result: PASS
    evidence: Exactly ten intended paths; zero comments/reviews/threads; no target-main drift; squash merge 63547f30fc21e495217b8a92fa44aaad2db188ef.
  - command: Canary pre-final governance schema and focused validation
    result: PASS
    evidence: Agent Task Ownership 2596, Imbuement Validation 324 and CI 3738 passed before final target evidence was recorded; fresh exact-final-head gates are required after this checkpoint commit.
```

# Next-agent sequence

1. Do not commit again to PR #588 after this final task/checkpoint commit unless the entire final-head gate is intentionally invalidated and rerun.
2. Require fresh exact-head Agent Task Ownership, Imbuement Validation and `ci:final-gate` CI on PR #588.
3. Audit exactly the two governance paths, comments/reviews/threads and Canary-main drift, then expected-head squash-merge #588.
4. Create a separate authoritative lifecycle PR containing only active-task deletion and archive addition; validate and merge it.
5. Only after authoritative lifecycle merge, close any self-owned automatic duplicate archive PR for #588 if one exists.
6. Create a separate one-file durable program reconciliation PR recording OAM-019 completion and OAM-020 NOT STARTED; validate and merge it.
7. Do not start OAM-020 in this task.
