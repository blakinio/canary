---
task_id: CAN-20260713-imbuement-direct-access-guard
program_id: ""
coordination_id: ""
status: ready_for_review_pending_ci
agent: "GPT-5.6 Thinking"
branch: fix/imbuement-direct-access-guard
base_branch: main
created: 2026-07-13T15:55:00+02:00
updated: 2026-07-13T21:38:00+02:00
last_verified_commit: "b2253e0337507fc90d9867ecf6e8cf318958c79a"
risk: medium
related_issue: "dry-test finding after IMB-001..006 live-parity repair"
related_pr: "#282"
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

Close the dry-test-discovered server-side authorization gap where a modified client can submit a hidden Imbuement numeric ID directly and bypass presentation-only premium/storage filtering.

# Confirmed dry-test finding

- `Imbuements::getImbuements()` hides locked storage entries before presenting the window.
- `Game::playerApplyImbuement()` resolves the submitted numeric ID and delegates to `Player::onApplyImbuement()`.
- `Player::onApplyImbuement()` delegated target validation to `Item::canAddImbuement()`.
- `Item::canAddImbuement()` validates slot bounds, target category/tier compatibility and duplicate category, but does not validate premium entitlement or quest storage.
- Therefore a crafted packet could attempt an Intricate/Powerful ID that the normal client did not present.

# Implemented repair

- Added `ImbuementAccessPolicy::canApplyDirectly`, reusing `ImbuementStoragePolicy`.
- `Player::onApplyImbuement()` now checks premium and configured quest storage before target, money or material mutation.
- `Player::createScrollImbuement()` now applies the same server-side authorization before money/material/empty-scroll mutation.
- `Player::applyScrollImbuement()` is intentionally unchanged: possession of an already-created scroll remains the entitlement token.
- Added focused C++ policy coverage for Basic/free access, premium rejection, missing storage rejection, unlocked storage success and disabled-storage-filter behavior.
- Extended the deterministic runtime marker audit to require both server-side guard call sites.
- Refreshed the Markdown baseline from 7/22/2 to 9/24/0 and documented the direct-ID finding.
- Autofix commit `b2253e0337507fc90d9867ecf6e8cf318958c79a` changed only formatting in the new policy header.

# Dry-test matrix

| Scenario | Result after repair |
|---|---|
| Valid Basic direct application policy | PASS |
| Non-premium direct premium ID | REJECTED |
| Powerful ID with filtering enabled and missing storage | REJECTED |
| Powerful ID with proven storage present | ALLOWED |
| Powerful ID with storage filtering disabled | ALLOWED by configuration |
| Existing Intricate/Powerful Imbuement Scroll use | unchanged |
| Invalid slot/target/category | existing rejection preserved |
| Duplicate category/name | existing rejection preserved |
| Missing materials | rejected before gold mutation |
| Missing gold | rejected before material mutation |

# Acceptance criteria

- [x] Non-premium players cannot directly apply or create premium Imbuements by sending an ID.
- [x] With shrine-storage filtering enabled, missing quest storage blocks direct application and scroll creation before resources are mutated.
- [x] A present unlock storage permits the operation.
- [x] With storage filtering disabled, the storage gate remains disabled.
- [x] Existing Imbuement Scroll application remains unchanged.
- [x] Deterministic validators and focused tests cover the guard.
- [ ] Full current-head CI is inspected before merge.
- [ ] Task is archived in a separate cleanup PR.

# Evidence boundary

The dry test proves control flow and deterministic policy behavior. Full C++ compilation/tests, runtime smoke and platform builds remain GitHub CI evidence. Physical-client packet/E2E and production database persistence remain separate runtime evidence.

# Local limitation

The execution environment cannot resolve `github.com`; no local checkout/test is claimed. GitHub API and GitHub Actions are separate evidence.
