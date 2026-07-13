---
task_id: CAN-20260713-imbuement-live-parity
status: completed
agent: "GPT-5.6 Thinking"
branch: fix/imbuement-live-parity
cleanup_branch: docs/archive-imbuement-live-parity
base_branch: main
created: 2026-07-13T14:20:00+02:00
completed: 2026-07-13
last_verified_commit: "9673ea895adae1bb3e829be7f6ba99294ef714b3"
merge_commit: "7eb891044d5753b713aa398202d232679501b01e"
risk: medium
related_pr: "#251"
cleanup_pr: "pending"
depends_on:
  - merged Imbuement audit PR #166
  - merged Forgotten Knowledge storage repair PR #206
  - merged Vibrancy scroll repair PR #239
owned_paths: []
---

# Result

The active Canary Imbuement registry was aligned with the current live Tibia mechanics selected by the user and merged through PR #251. Existing Forgotten Knowledge storage wiring from PR #206 and Vibrancy scroll behavior from PR #239 were preserved.

# Final GitHub state

- Feature branch: `fix/imbuement-live-parity`.
- Feature PR: #251.
- Final feature head: `9673ea895adae1bb3e829be7f6ba99294ef714b3`.
- Squash merge: `7eb891044d5753b713aa398202d232679501b01e`.
- Final changed-file count: 11.
- No workflow, temporary helper, trigger, diagnostic, map, `items.otb`, binary asset, database schema, production configuration, client, protocol or `docs/agents/ACTIVE_WORK.md` path remained in the feature diff.
- Review conversation and review threads: none.

# Implemented live mechanics

## IMB-001 — fixed fees

| Tier | Price | Success | Protection surcharge |
|---|---:|---:|---:|
| Basic | 7,500 | 100% | 0 |
| Intricate | 60,000 | 100% | 0 |
| Powerful | 250,000 | 100% | 0 |

The existing Player application path charges the registry price and the existing protocol serializes price, percent and protection price from the same registry. No protocol-shape or second runtime subsystem was added.

## IMB-002 — Strike

| Tier | Critical chance | Critical damage |
|---|---:|---:|
| Basic | 5% | +5% |
| Intricate | 5% | +15% |
| Powerful | 5% | +40% |

## IMB-003 — Punch

- Basic: item `10281` x25.
- Intricate: item `10281` x25 + item `11489` x20.
- Powerful: previous sources + item `40529` x15.

## IMB-006 — quest unlocks

- Powerful Featherweight: storage `45929` (`DangerousDepths.Bosses.LastAchievement`), written after all three final Dangerous Depths boss-achievement markers are complete.
- Powerful Vibrancy: storage `46365` (`TheDreamCourts.DreamScarGlobal.NightmareTimer`), written by the Nightmare Beast death path and retained as an initialized persistent marker.
- Generic questline storages were rejected because they are written when each quest starts and would unlock the Powerful entries too early.

# Preserved repairs

- IMB-004: Intricate/Powerful Vibrancy scroll mappings `51746` and `51466`, existing resolution and atomicity coverage from PR #239.
- IMB-005: Forgotten Knowledge Powerful family storage groups `45489..45495` from PR #206.

# Deterministic baseline after repair

- 3 base tiers.
- 20 categories.
- 24 families and 72 tier entries.
- 48 XML scroll mappings matching 48 active Lua registrations.
- 24 Powerful families with nonzero unlock storage.
- No Powerful family with `storage=0`.
- Nonzero unlock storages: `45489..45495`, `45929`, `46365`.
- Final registry audit: zero findings.
- Final strict storage audit: zero findings.

# Final feature CI

Final head: `9673ea895adae1bb3e829be7f6ba99294ef714b3`.

## Focused workflows

- Imbuement Validation run `29252104756`, job `86822944305`: success.
  - focused Python compilation succeeded;
  - 13/13 focused tests succeeded;
  - registry and strict storage audits succeeded with no findings;
  - generated and committed runtime-plan JSON passed syntax validation.
- Agent Task Ownership run `29252104918`, job `86822944851`: success.
- AI Agent Tools run `29252104614`, job `86822944143`: success.
- autofix.ci run `29252209788`: success; no branch change was produced.

## Post-ready full CI

CI run `29252209979`: success.

- Detect Build Scope job `86823302671`: success.
- Fast Checks job `86823302708`: success; formatters, formatting diff, Lua API documentation checks, Reviewdog and yamllint succeeded; no formatting commit was created.
- Lua Tests job `86823302767`: success.
- Windows CMake job `86824472195`: success; CMake and Canary runtime smoke succeeded.
- Windows Solution job `86824472205`: success; MSBuild succeeded.
- macOS job `86824472210`: success; configure, build and Canary runtime smoke succeeded.
- Linux Release job `86824472227`: success.
- Linux Debug job `86824472218`: success; build, Canary runtime smoke, schema import and full C++ tests succeeded.
- The workflow-level `Required` gate and complete CI run concluded success.
- Docker and Docker Quickstart were skipped by the detected scope and are not claimed as executed.

## C++ test artifact

Linux Debug artifact `linux-debug-test-logs` ID `8280291862` recorded:

- 508/508 tests passed, 0 failed;
- `ImbuementsUnitTest.LoadsLiveFeesAndSkillBonus`: passed;
- `ImbuementsUnitTest.LoadsLiveStrikeAndBasicPunchData`: passed;
- `ImbuementsUnitTest.ResolvesIntricateAndPowerfulVibrancyScrolls`: passed;
- existing scroll application success/failure atomicity tests remained in the same suite.

# Local environment limitation

Local checkout was unavailable because the execution environment could not resolve `github.com`:

```text
getent hosts github.com
# no DNS result

git ls-remote https://github.com/blakinio/canary.git HEAD
# fatal: unable to access 'https://github.com/blakinio/canary.git/': Could not resolve host: github.com
```

No local command or local test is claimed as passed. GitHub API and GitHub Actions are separate evidence.

# Evidence boundary

This task proves current audited registry data, loader integration, deterministic validator contracts, compilation, Canary startup smoke and automated C++ regression coverage. It does not claim physical-client E2E, exhaustive equipment eligibility parity, end-to-end combat sampling for every item/client profile, or real deployment database persistence beyond the CI smoke/test environment. Those remain separate runtime scenarios in `docs/ai-agent/IMBUEMENT_RUNTIME_TEST_PLAN.json`.

# Decisions

- Current live Tibia was selected explicitly instead of the historical chance/protection economy.
- Existing registry, loader, Player application and protocol presentation were reused.
- Only active, proven quest-completion markers were assigned.
- IMB-004 and IMB-005 were preserved rather than reopened.
- Auto-merge was attempted after final checks; GitHub rejected enabling it because the PR was already clean and immediately mergeable.
- PR #251 was squash-merged with expected-head SHA protection.

# Failed approaches and dead ends

- Several guessed quest paths returned 404 before exact active paths were found through repository search.
- A validator-generated runtime plan temporarily reduced the rich scenario document; the full 319-line plan was restored from the exact feature base and updated.
- Temporary workflow finalizers initially skipped PR events, used an indentation-sensitive helper anchor and retained one stale IMB-006 assertion.
- GitHub Actions push attempts failed with HTTP 403 for `github-actions[bot]`; authorized GitHub API writes were used instead.
- Temporary workflows, helpers, triggers and diagnostic files were removed before final review.
- Fetching logs from running jobs sometimes returned transient `BlobNotFound`; final steps and downloaded artifacts were inspected after completion.

# Remaining work

None for this bounded task after the cleanup PR is merged.

# Handoff

Use `docs/ai-agent/IMBUEMENT_VALIDATION_REPORT.md` and `docs/ai-agent/IMBUEMENT_RUNTIME_TEST_PLAN.json` as the current Imbuement handoff. Do not restore the historical fee/chance model, do not replace storages `45929` or `46365` without stronger active evidence, and keep physical-client/gameplay verification separate from deterministic data parity.
