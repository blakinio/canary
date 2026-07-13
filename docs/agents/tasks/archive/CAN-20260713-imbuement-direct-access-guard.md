---
task_id: CAN-20260713-imbuement-direct-access-guard
status: completed
agent: "GPT-5.6 Thinking"
branch: fix/imbuement-direct-access-guard
cleanup_branch: docs/archive-imbuement-direct-access-guard
base_branch: main
created: 2026-07-13T15:55:00+02:00
completed: 2026-07-13
last_verified_commit: "cf93781d2f9c0bdfcf89bb96490d15f79a51feee"
merge_commit: "6e92ca68dbabd76acef6331ba8b77b1843dc2bc3"
risk: medium
related_pr: "#282"
cleanup_pr: "#285"
depends_on:
  - merged Imbuement live-parity PR #251
  - merged lifecycle cleanup PR #255
owned_paths: []
---

# Result

Dry testing found and repaired a server-side Imbuement authorization gap. The normal client window hid premium or quest-locked entries, but a modified client could submit the hidden numeric Imbuement ID directly because the final application path validated item/slot/category compatibility without repeating premium and storage authorization.

PR #282 added a deterministic server-side guard before any direct-application or scroll-creation resource mutation and was squash-merged into `main`.

# Final GitHub state

- Feature PR: #282.
- Feature branch: `fix/imbuement-direct-access-guard`.
- Final feature head: `cf93781d2f9c0bdfcf89bb96490d15f79a51feee`.
- Squash merge: `6e92ca68dbabd76acef6331ba8b77b1843dc2bc3`.
- Cleanup PR: #285.
- Final changed-file count: 7.
- No XML value, map, asset, item binary, protocol shape, database schema, client, production configuration, workflow or `docs/agents/ACTIVE_WORK.md` change remained in the feature diff.
- PR conversation/review threads: none.

# Confirmed pre-repair control flow

1. `Imbuements::getImbuements()` filtered locked entries while constructing the normal client list.
2. `Game::playerApplyImbuement()` accepted the submitted numeric ID and delegated to `Player::onApplyImbuement()`.
3. `Player::onApplyImbuement()` relied on `Item::canAddImbuement()` for target validation.
4. `Item::canAddImbuement()` checked slot bounds, item/tier/category compatibility and duplicate category, but did not check premium entitlement or quest storage.
5. Therefore presentation filtering was not an authoritative server-side permission boundary.

# Implemented repair

- Added `ImbuementAccessPolicy::canApplyDirectly`, reusing `ImbuementStoragePolicy`.
- `Player::onApplyImbuement()` checks premium entitlement and configured quest storage before target/resource mutation.
- `Player::createScrollImbuement()` applies the same authorization before gold, materials or empty-scroll mutation.
- `Player::applyScrollImbuement()` remains unchanged: possession of an already-created scroll remains the entitlement token.
- Added deterministic runtime marker validation for both guard call sites.
- Added C++ policy regression coverage.
- Corrected the stale report baseline to 9 distinct unlock IDs, 24/24 Powerful families with nonzero storage and 0 Powerful `storage=0` bypasses.

# Dry-test matrix after repair

| Scenario | Result |
|---|---|
| Basic direct application | allowed |
| Non-premium premium-ID submission | rejected |
| Powerful ID, filtering enabled, storage absent | rejected |
| Powerful ID, proven unlock storage present | allowed |
| Storage filtering disabled by configuration | allowed |
| Existing Imbuement Scroll use | unchanged |
| Invalid slot/target/category | existing rejection preserved |
| Duplicate category/name | existing rejection preserved |
| Missing materials | rejected before gold mutation |
| Missing gold | rejected before material mutation |

# Final validation

Final head: `cf93781d2f9c0bdfcf89bb96490d15f79a51feee`.

## Focused workflows

- Imbuement Validation run `29279232315`, job `86916027899`: success.
  - focused Python compilation succeeded;
  - focused unit tests succeeded;
  - registry and strict storage audits succeeded;
  - runtime-plan JSON validation succeeded.
- Agent Task Ownership run `29279232306`, job `86916028002`: success.
- AI Agent Tools run `29279232258`, job `86916028186`: success.
- autofix.ci run `29279232338`, job `86916028233`: success; no further branch change.

## Post-ready full CI

CI run `29279232552`: success.

- Detect Build Scope `86916076752`: success.
- Fast Checks `86916076774`: success.
- Lua Tests `86916076776`: success.
- Docker image build and validation `86916368711`: success.
- macOS configure, build and Canary runtime smoke `86916368716`: success.
- Windows Solution/MSBuild `86916368717`: success.
- Linux Release build, generated-docs validation and Canary/Global runtime smoke `86916368732`: success.
- Linux Debug build, Canary runtime smoke, schema import and full C++ tests `86916368740`: success.
- Complete CI workflow and required gate: success.

## C++ test artifact

Artifact `linux-debug-test-logs` ID `8290937317` recorded:

- 521/521 tests passed, 0 failed;
- `ImbuementsUnitTest.DirectAccessPolicyEnforcesPremiumAndStorageWithoutChangingScrollEntitlement`: passed;
- the existing fees, Strike, Punch, Vibrancy scroll resolution and scroll atomicity tests remained green.

# Evidence boundary

This task proves deterministic policy behavior, authoritative server-side guard placement, compilation, Canary startup smoke, schema import and automated C++ regression coverage. Physical-client crafted-packet E2E and production database persistence remain separate runtime evidence; no known defect remains in the audited direct-access path.

# Local limitation

The execution environment could not resolve `github.com`, so no local checkout/build/test is claimed. GitHub API and GitHub Actions are separate evidence.

# Failed approaches and operational notes

- Initial implementation/report commits created by `github-actions[bot]` produced `action_required` PR workflow states; a subsequent authorized GitHub API commit established the final verifiable head.
- Autofix produced one formatting-only commit for the new policy header; final authenticated task metadata commit moved the final head to `cf93781d...`.
- Auto-merge could not be enabled because GitHub reported the PR as already `clean`; the PR was squash-merged with expected-head SHA protection.

# Remaining work

None for this bounded dry-test finding after cleanup PR #285 is merged.

# Handoff

Use `docs/ai-agent/IMBUEMENT_VALIDATION_REPORT.md` and `docs/ai-agent/IMBUEMENT_RUNTIME_TEST_PLAN.json` as the current handoff. Do not remove the server-side premium/storage guard, and keep already-created scroll use as the separate entitlement path unless real Tibia evidence requires a different model.
