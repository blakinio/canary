---
task_id: CAN-20260713-imbuement-direct-access-guard
program_id: ""
coordination_id: ""
status: in_progress
agent: "GPT-5.6 Thinking"
branch: fix/imbuement-direct-access-guard
base_branch: main
created: 2026-07-13T15:55:00+02:00
updated: 2026-07-13T15:55:00+02:00
last_verified_commit: "600418aa26fedb6c09eb1e035d82b332955e84c6"
risk: medium
related_issue: "dry-test finding after IMB-001..006 live-parity repair"
related_pr: "pending"
depends_on:
  - merged Imbuement live-parity PR #251
  - merged lifecycle cleanup PR #255
blocks: []
owned_paths:
  exclusive:
    - src/creatures/players/imbuements/imbuement_access_policy.hpp
    - src/creatures/players/player.cpp
    - tests/unit/players/imbuements/imbuements_test.cpp
    - tools/ai-agent/imbuement_validation.py
    - tools/ai-agent/test_imbuement_validation.py
    - docs/ai-agent/IMBUEMENT_VALIDATION_REPORT.md
    - docs/ai-agent/IMBUEMENT_RUNTIME_TEST_PLAN.json
    - docs/agents/tasks/active/CAN-20260713-imbuement-direct-access-guard.md
  shared: []
  read_only:
    - src/items/item.cpp
    - src/game/game.cpp
    - src/server/network/protocol/protocolgame.cpp
    - data/XML/imbuements.xml
modules_touched:
  - Imbuement direct-application authorization
  - Imbuement deterministic validation
reuses:
  - ImbuementStoragePolicy
  - existing Imbuement focused tests and workflow
public_interfaces: []
cross_repo_tasks: []
---

# Goal

Close the dry-test-discovered server-side authorization gap where a modified client can submit a hidden Imbuement numeric ID directly and bypass the presentation-only premium/storage filtering.

# Confirmed dry-test finding

- `Imbuements::getImbuements()` hides locked storage entries before presenting the window.
- `Game::playerApplyImbuement()` resolves the submitted numeric ID and delegates to `Player::onApplyImbuement()`.
- `Player::onApplyImbuement()` delegates target validation to `Item::canAddImbuement()`.
- `Item::canAddImbuement()` validates slot bounds, target category/tier compatibility and duplicate category, but does not validate premium entitlement or quest storage.
- Therefore a crafted packet can attempt an Intricate/Powerful ID that the normal client did not present.

# Intended repair

- Add one deterministic direct-access policy reusing `ImbuementStoragePolicy`.
- Enforce it before any money/material mutation in normal direct application and scroll creation.
- Preserve `Player::applyScrollImbuement()` behavior: possession/use of an already-created scroll remains a separate path and must not be accidentally gated by the shrine unlock.
- Add C++ and Python regressions for premium, storage enabled/disabled, unlocked storage and exact runtime guard coverage.
- Refresh the stale Markdown report baseline/status discovered by the same dry review.

# Acceptance criteria

- [ ] Non-premium players cannot directly apply or create premium Imbuements by sending an ID.
- [ ] With shrine-storage filtering enabled, missing quest storage blocks direct application and scroll creation before resources are mutated.
- [ ] A present unlock storage permits the operation.
- [ ] With storage filtering disabled, the storage gate remains disabled.
- [ ] Existing Imbuement Scroll application remains unchanged.
- [ ] Deterministic validators and focused tests cover the guard.
- [ ] Full current-head CI is inspected before merge.
- [ ] Task is archived in a separate cleanup PR.

# Local limitation

The execution environment previously could not resolve `github.com`; no local checkout/test is claimed unless this changes. GitHub API and GitHub Actions remain separate evidence.
