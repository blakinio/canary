# OAM-019 — Imbuements Revalidation

Status: **target adaptation proved and merged; Canary governance closeout in final validation**

Program: `CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION`

Coordination: `OAM-019`

## Final disposition

```text
imbuements → ADAPT
```

The task-start target/upstream Imbuement core was not sufficient for whole-module `REUSE`. Delivered legacy Canary history contains multiple coherent, dependency-valid correctness/data repairs that were absent from the target. OAM-019 migrated only that reviewed bounded chain and retained the target architecture around it.

## Immutable task-start baselines

```text
legacy/governance Canary: blakinio/canary@e551f3fd33c9642399bb1e70d1f2f6383464b936
target Otheryn: blakinio/Otheryn@7ba76d2754a060a9a9eec0a23c686aefac725af2
upstream evidence: opentibiabr/canary@691614c1a302aee776002ca3851eca399be1a82c
maintained OTClient: 2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f
```

## Canonical module and dependency gate

Canonical registry record: `docs/agents/real-tibia/registry/modules/imbuements.yaml`.

The package owns Imbuement definitions, materials and fees, unlock storages, effects and scrolls, plus bounded runtime/storage validation.

Dependencies:
- `combat` — completed by OAM-013;
- `player-persistence` — completed by the foundational persistence/lifecycle packages;
- `protocol` remains an interaction, not a fundamental dependency.

Generic item ownership, Exaltation Forge tiers, client UI implementation and broad protocol migration remain outside OAM-019.

## Fresh live-state and ownership preflight

At task start:
- Canary `main` was `e551f3fd33c9642399bb1e70d1f2f6383464b936` after durable OAM-018 reconciliation;
- Otheryn `main` was `7ba76d2754a060a9a9eec0a23c686aefac725af2`;
- pinned upstream was `691614c1a302aee776002ca3851eca399be1a82c`;
- Otheryn had no open pull requests;
- live Canary pull requests did not claim Imbuement runtime/data write ownership;
- the broad shared-state/economy security audit was evidence-only and did not own this migration boundary.

No overlapping live write ownership was found.

## Accepted coherent donor chain

The bounded adaptation is the coherent result of these merged Canary repairs:

1. PR #86 — configured-storage filtering correctness. The old path passed the boolean result of `imbuement->getStorage() == -1` into `Player::getStorageValue()`, effectively checking storage `0` or `1`. The accepted helper `ImbuementStoragePolicy::shouldHide()` reads the configured storage ID and fails closed when the required storage is absent.
2. PR #206 — reconciles the 22 Powerful Forgotten Knowledge entries from stale `50488/50490/50492/50494/50496/50498/50501` IDs to the active boss-written groups `45489..45495`.
3. PR #239 — adds the missing Intricate Vibrancy scroll `51746` and Powerful Vibrancy scroll `51466` mappings used by the existing scroll-resolution runtime.
4. PR #251 — aligns the selected confirmed live data contract: application fees `7,500 / 60,000 / 250,000`, 100% success, zero protection surcharge; Strike 5% chance with +5%/+15%/+40% damage; Basic Punch item `10281 x25`; Powerful Featherweight storage `45929`; Powerful Vibrancy storage `46365`.
5. PR #282 — adds server-side direct numeric-ID authorization for premium/storage requirements before resource mutation in normal application and Imbuement Scroll creation. Applying an already-created Imbuement Scroll remains intentionally unchanged: possession of the scroll is the entitlement token.

No whole-file legacy `player.cpp` transfer was accepted. The target adaptation materialized only the reviewed Imbuement-specific hunks plus the two isolated policy helpers and focused tests.

## Accepted target adaptation

Otheryn PR #43 final head:

```text
4e993c4ee160fe03d8575c1b830ef71dde450562
```

It changed exactly ten intended runtime/data/test paths:

```text
data/XML/imbuements.xml
src/creatures/players/imbuements/imbuement_access_policy.hpp
src/creatures/players/imbuements/imbuement_storage_policy.hpp
src/creatures/players/imbuements/imbuements.cpp
src/creatures/players/player.cpp
tests/fixture/core/XML/imbuements.xml
tests/unit/players/imbuements/CMakeLists.txt
tests/unit/players/imbuements/imbuement_storage_policy_test.cpp
tests/unit/players/imbuements/oam_019_imbuements_adapt_test.cpp
tests/unit/players/imbuements/oam_019_scroll_runtime_test.cpp
```

Temporary fail-closed materializer files used to apply bounded hunks through the connector were removed before the accepted target head and are absent from the final PR diff.

The target tests prove:
- configured storage IDs are read exactly and missing required storage fails closed;
- direct application/scroll creation policy enforces premium and configured storage requirements;
- the accepted production XML contains the exact fee/success/protection, storage-group, Vibrancy scroll, Strike and Basic Punch contract;
- both Vibrancy scroll IDs resolve to their intended tiers;
- real `Player::applyScrollImbuement` consumes exactly one scroll on success;
- invalid targets and occupied Vibrancy categories do not consume the scroll or introduce a second Imbuement.

## Exact target validation

Accepted exact head `4e993c4ee160fe03d8575c1b830ef71dde450562` passed:

- autofix.ci #121 / run `29687711140`: SUCCESS;
- Repository Audit #12 / run `29687711133`: SUCCESS;
- CI #142 / run `29687711219`: SUCCESS after one same-head macOS failed-job rerun;
- Required #128 / run `29687711131`: SUCCESS after the CI result became green;
- Linux debug build/runtime smoke/schema import: PASS;
- full Linux debug CTest: `367/367` PASS;
- new focused OAM-019 tests: `8/8` PASS.

Primary test artifact:

```text
id: 8442743109
name: linux-debug-test-logs
digest: sha256:a0ef33bd15be8d004dce89ce5014782990961cb239c50e9f48f19d906694c6e0
```

The first macOS smoke wrapper attempt failed after successful compilation. Artifact `8442686987` (`sha256:57d85a77b0d1819c5d2d9c9368a8eef9cefae5071750d6c990b4cba56ebac4fb`) showed the server reached `Canary CI Smoke server online!`, accepted SIGTERM, saved cleanly, completed thread-pool shutdown and produced empty stderr. One permitted same-head rerun passed without code changes. This was classified as transient smoke-harness/timing behavior, not an Imbuement runtime defect.

Target comments, review submissions and review threads were empty. Otheryn `main` remained at task-start `7ba76d2754a060a9a9eec0a23c686aefac725af2` through the final merge audit, so there was no target-main drift. PR #43 merged by expected-head squash as:

```text
63547f30fc21e495217b8a92fa44aaad2db188ef
```

## Boundary classification

- ownership/lifecycle: applicable and accepted within existing Imbuement singleton/Player lifecycle;
- build/toolchain: applicable and passed on Linux debug/release, macOS, Windows CMake/Solution and Docker;
- configuration: applicable for `TOGGLE_IMBUEMENT_SHRINE_STORAGE`; existing configuration semantics preserved;
- service/API: applicable only to existing Imbuement/Player APIs plus isolated policy helpers;
- scheduling/concurrency: not materially changed by OAM-019;
- persistence: applicable but bounded; storage IDs and existing remaining-duration persistence contracts are preserved, not redesigned;
- protocol/session: interaction only; no wire-shape/client change introduced;
- identifiers/assets: exact reviewed item/scroll/storage IDs only; no new IDs invented;
- world/map: not applicable to the accepted target change;
- runtime: applicable and covered by platform smoke plus real Player scroll-application tests;
- tests: applicable and passed as above;
- physical-client E2E: not required for this bounded server/data adaptation and not claimed;
- operations/security: direct numeric-ID authorization is enforced before relevant resource mutation; deployment/production rollout is outside this package.

## Explicit exclusions and known gaps

OAM-019 does not claim:
- exhaustive current Real Tibia Imbuement parity;
- exhaustive equipment eligibility correctness;
- full live before/after unlock visibility for every quest path;
- independent proof of the Dangerous Depths and Dream Courts completion conditions beyond the accepted donor evidence;
- exact protocol/UI presentation across every supported client profile;
- physical-client E2E closure;
- end-to-end combat-math parity for every Imbuement effect;
- real production database save/load or crash/restart persistence completeness;
- generic resource-transaction atomicity beyond the reviewed Imbuement application ordering;
- changes to generic items, Exaltation Forge, maps, assets, `items.otb`, schema or client code.

OAM-004 SQL/KV non-atomicity and all previously completed module ownership remain preserved.

## Current state

OAM-019 target work is complete and merged. Canary governance PR #588 is the active closeout boundary. After governance merge, OAM-019 still requires a separate authoritative lifecycle archive and a separate one-file durable program reconciliation.

OAM-020 is NOT STARTED.
