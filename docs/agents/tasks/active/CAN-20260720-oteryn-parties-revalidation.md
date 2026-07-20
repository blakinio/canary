---
task_id: CAN-20260720-oteryn-parties-revalidation
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-023
status: ready
agent: "GPT-5.5 Thinking"
branch: docs/oam-023-parties-revalidation
base_branch: main
created: 2026-07-20
updated: 2026-07-20
last_verified_commit: "e81ae95d60096db84d00b0f4ff5516b58c1ecc2d"
risk: medium
related_pr: "616"
depends_on:
  - OAM-005 character-lifecycle
blocks:
  - OAM-024
modules_touched:
  - parties
owned_paths:
  exclusive:
    - docs/agents/OTERYN_OAM_023_PARTIES_REVALIDATION.md
    - docs/agents/tasks/active/CAN-20260720-oteryn-parties-revalidation.md
---

# Goal

Revalidate canonical OAM-023 `parties`, classify the smallest dependency-valid clean-target disposition from current evidence, deliver only the bounded target implementation or proof required by that disposition, and complete target → governance → lifecycle archive → durable program reconciliation before OAM-024 starts.

# Immutable task-start baselines

- Canary: `0a39a0f76d5f811098dfaa7be9deea40347279d5`
- Otheryn: `50dfa248251f245f5519495a4fbd430b6814ffe4`
- fresh upstream Canary: `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`
- maintained OTClient: `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`

# Final disposition

```text
parties → REUSE
```

The classification is based on bounded semantic/history review plus exact-head focused target proof. Exact blob identity across target/upstream/legacy was supporting evidence only and was not treated as sufficient by itself.

# Target closure

Otheryn PR #47 was squash-merged with expected head `c3ff8bb09b736ec835ce1f49ee0d96b8e208ea88` as:

```text
bcc3e9f7e3e704f3c012bda8693648d52741630f
```

The target diff contained exactly:

- `docs/oam-023-parties-reuse.md`
- `tests/unit/game/CMakeLists.txt`
- `tests/unit/game/oam_023_parties_reuse_test.cpp`

There was no production runtime or maintained OTClient mutation. Ready-state exact-head gates passed: autofix.ci #147 / run `29728346604`, CI #172 / run `29728346757`, and Required #154 / run `29728346586`. Linux debug CTest passed 403/403 tests, including OAM-023 focused proof 3/3. Test-log artifact `8455540885` has digest `sha256:8c3868b1047057d8419194ce7a555566b8db7dd32024f1ecb1c2cdec1424938b`.

# Drift and boundaries

Canary `main` advanced after task start by one independent OTBM/E2E merge to `e81ae95d60096db84d00b0f4ff5516b58c1ecc2d`. The compare audit found changes only in `.github/workflows/universal-agent-e2e.yml`, the OTBM task record, `tests/e2e/**` and `tools/e2e/**`; there is no overlap with OAM-023 governance paths or canonical `src/creatures/players/grouping/party.*`.

No protocol, persistence, combat, vocation, Wheel, chat, guild, map/OTBM, `items.otb`, asset, schema or deployment scope is claimed. OAM-004 player SQL / later KV non-atomicity remains unchanged.

OAM-024 remains blocked until this governance PR is merged, the active task is archived in a separate lifecycle PR, and a separate durable program reconciliation is merged.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-20T10:53:00+02:00
head: d095f8bd6a22e516d23c005388e36054a8e615d8
branch: docs/oam-023-parties-revalidation
pr: "616"
status: ready
next_action: Merge governance PR #616 only after exact-head final-gate CI and final changed-file review and drift audits pass, then archive OAM-023 in a separate lifecycle PR.
context_routes:
  - agent-governance
  - cpp-runtime
owned_paths:
  - docs/agents/OTERYN_OAM_023_PARTIES_REVALIDATION.md
  - docs/agents/tasks/active/CAN-20260720-oteryn-parties-revalidation.md
proven:
  - OAM-022 was fully and durably complete and OAM-023 had not started before this task.
  - Canonical parties depends only on completed OAM-005 character-lifecycle and was the smallest dependency-valid non-conflicting package selected in the fresh preflight.
  - Target upstream and legacy party.cpp and party.hpp are exact-identical at the pinned baselines, but identity alone was not used to classify REUSE.
  - Semantic and relevant legacy-history review found no stronger independent legacy donor for canonical party.*.
  - Otheryn PR #47 exact-head ready-state autofix CI and Required gates passed and the proof-only PR was expected-head squash-merged as bcc3e9f7e3e704f3c012bda8693648d52741630f.
  - Linux debug CTest passed 403 of 403 tests including all 3 Oam023PartiesReuseTest cases.
  - Canary main drift since task start is one independent non-overlapping OTBM E2E merge ending at e81ae95d60096db84d00b0f4ff5516b58c1ecc2d.
derived:
  - parties can be classified REUSE without production or maintained OTClient mutation within the canonical OAM-023 boundary.
unknown: []
conflicts: []
rejected_hypotheses:
  - Blob identity alone is sufficient to classify parties as REUSE.
  - wheel-of-destiny should be selected despite separate active parity ownership.
  - The intervening OTBM E2E Canary main drift overlaps OAM-023 governance or canonical party.* paths.
changed_paths:
  - docs/agents/OTERYN_OAM_023_PARTIES_REVALIDATION.md
  - docs/agents/tasks/active/CAN-20260720-oteryn-parties-revalidation.md
blockers: []
first_failure:
  marker: resolved-task-checkpoint-contract
  evidence: Early ownership failures were isolated to the task checkpoint format and resolved; Agent Task Ownership #2775 and CI #3926 passed after contract alignment.
validation:
  - command: Otheryn PR #47 autofix.ci #147 run 29728346604
    result: PASS
    evidence: Exact target head c3ff8bb09b736ec835ce1f49ee0d96b8e208ea88 completed successfully.
  - command: Otheryn PR #47 CI #172 run 29728346757
    result: PASS
    evidence: Exact target head completed successfully with Linux debug CTest 403/403 PASS and OAM-023 focused tests 3/3 PASS.
  - command: Otheryn PR #47 Required #154 run 29728346586
    result: PASS
    evidence: Exact target head completed successfully.
  - command: Canary Agent Task Ownership #2775 run 29728636917
    result: PASS
    evidence: Active task ownership and checkpoint contract passed before final governance reconciliation.
  - command: Canary CI #3926 run 29728637169
    result: PASS
    evidence: Governance branch validation passed before the final evidence and checkpoint commit.
```
