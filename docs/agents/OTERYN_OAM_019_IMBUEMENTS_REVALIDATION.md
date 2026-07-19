# OAM-019 — Imbuements Revalidation

Status: **fresh preflight complete; exact donor and target adaptation analysis in progress**

Program: `CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION`

Coordination: `OAM-019`

## Immutable task-start baselines

```text
legacy/governance Canary: blakinio/canary@e551f3fd33c9642399bb1e70d1f2f6383464b936
target Otheryn: blakinio/Otheryn@7ba76d2754a060a9a9eec0a23c686aefac725af2
upstream evidence: opentibiabr/canary@691614c1a302aee776002ca3851eca399be1a82c
maintained OTClient: 2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f
```

## Canonical module

```text
imbuements
```

Canonical registry record: `docs/agents/real-tibia/registry/modules/imbuements.yaml`.

Registry dependency gate:
- `combat` — completed by OAM-013;
- `player-persistence` — completed by the foundational OAM persistence/lifecycle packages;
- `protocol` is an interaction, not a fundamental dependency.

The package owns Imbuement definitions, materials and fees, unlock storages, effects and scrolls, plus bounded runtime/storage validation. Generic items and Exaltation Forge tiers remain outside this package.

## Fresh live-state and ownership preflight

At task start:
- Canary `main` was `e551f3fd33c9642399bb1e70d1f2f6383464b936` after durable OAM-018 reconciliation;
- Otheryn `main` was `7ba76d2754a060a9a9eec0a23c686aefac725af2`;
- pinned upstream remained `691614c1a302aee776002ca3851eca399be1a82c`;
- Otheryn had no open pull requests;
- live Canary PRs did not claim Imbuement runtime/data paths;
- the broad security/economy audit PR #526 is evidence-only and does not own Imbuement runtime changes.

No overlapping live write ownership was found for the bounded Imbuement target boundary.

## Candidate selection rationale

`imbuements` is selected before `market` or `exaltation-forge` because its fundamental dependencies are already completed, it has existing deterministic validators and focused C++ coverage, and it does not require a maintained-client migration to establish the bounded server/data correctness package. Market and Forge retain broader protocol/client and cross-module dependencies.

## Delivered legacy evidence under review

Known merged Canary repair chain:
- PR #86 — configured Imbuement storage filtering correctness;
- PR #206 — Forgotten Knowledge Powerful unlock storage mapping;
- PR #239 — Vibrancy scroll mappings;
- PR #251 — current fees, Strike values, Basic Punch source and final quest unlock markers;
- PR #282 — direct numeric-ID premium/storage authorization before resource mutation.

The current target does not contain `imbuement_storage_policy.hpp`, while current Canary does. Therefore whole-module `REUSE` is not established. The exact coherent donor subset and target adaptation are being verified path-by-path before any target write.

## Current evidence boundary

The existing Canary validation report provides strong deterministic/static evidence, but explicitly does not prove full production deployment startup, all live unlock visibility, full equipment eligibility, every protocol/UI profile, full quest completion conditions, end-to-end combat math or real database persistence. OAM-019 will not broaden those claims without new exact evidence.

## Current state

OAM-019 is active. No target production file has been changed yet. The next action is to verify exact final donor PR state/blobs and materialize only the smallest coherent dependency-valid adaptation with focused target tests.

OAM-020 is NOT STARTED.
