# Oteryn Target Architecture and Migration Contract

Status: **design contract; target repository and target baseline unavailable**

Program: `CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION`

Task: `CAN-20260715-oteryn-target-architecture-contract`

Task-start legacy baseline:

```text
blakinio/canary@d60d63dc37689ccc9ff7e9c37cfa2ebe71cbdc51
```

This document defines the entry conditions and proof contract for future Oteryn work. It does not authorize Oteryn implementation, create a repository, choose a target SHA, migrate a module or change Canary runtime behavior.

# 1. Target identity contract

Every migration implementation package must pin all target identity fields before code changes begin.

| Field | Current value | Requirement |
|---|---|---|
| target repository | unavailable | exact `owner/repository` required |
| target default branch | unavailable | exact branch required |
| target task-start SHA | unavailable | exact immutable SHA required |
| upstream parent repository | `opentibiabr/canary` | read-only |
| upstream baseline SHA | unavailable | exact then-current SHA required when target is established |
| legacy evidence repository | `blakinio/canary` | writable laboratory only; exact package SHA required |
| maintained client repository | resolve per package | exact controlled client SHA required when protocol/UI applies |
| target write authorization | unavailable | explicit ownership/authorization required |

Rules:

1. Never invent a repository, branch or SHA.
2. Never store a moving `main` as migration proof.
3. Oteryn should start from an explicitly pinned then-current upstream Canary baseline, not by cloning the legacy fork's history.
4. If the target repository does not exist, architecture/evidence work may continue in `blakinio/canary`, but target implementation must stop.
5. A future task may change the target identity only through a reviewed contract update pinned to exact SHAs.

# 2. Repository roles

## Legacy `blakinio/canary`

Role:

```text
legacy laboratory
evidence source
validation environment
migration-source candidate
```

It is not the Oteryn image to copy.

## Future Oteryn target

Required role:

```text
clean target
based on exact then-current upstream Canary baseline
selectively populated
architecturally intentional
module-by-module migration
```

The target must not inherit legacy baggage merely because a path, PR or subsystem exists in `blakinio/canary`.

## Upstream/reference repositories

The following are read-only evidence/reference inputs:

```text
opentibiabr/canary
opentibiabr/otclient
opentibiabr/remeres-map-editor
opentibiabr/client-editor
```

Any donor repository used by a bounded task is also read-only and is not official Real Tibia behavior authority.

# 3. Canonical module as migration unit

The only migration decision unit is a canonical module record from:

```text
docs/agents/real-tibia/registry/modules/*.yaml
```

The canonical registry remains the only logical module registry.

Do not create:

- an Oteryn migration registry duplicating module identity;
- a parallel taxonomy;
- a directory-based migration catalogue;
- a PR-history migration catalogue.

Do not migrate an entire directory, subsystem, datapack, map, client or repository merely because one canonical module touches it.

A path may map to multiple modules. Path mapping is discovery only.

# 4. Target architecture principles

Oteryn packages must preserve these architecture principles unless a later reviewed contract explicitly supersedes one.

## 4.1 Clean baseline first

Target bootstrap begins from an exact upstream Canary baseline and a clean target branch/repository state. Legacy code is evaluated as a candidate input, not inherited by default.

## 4.2 Explicit ownership and lifecycle

Every migrated responsibility must have an explicit target owner, lifecycle and shutdown/reload behavior where applicable.

Global/shared behavior must not be introduced as an accidental singleton or hidden cross-module dependency.

## 4.3 Dependency direction before feature breadth

Foundational contracts are established before dependent domain migration. A higher-level module cannot be approved for `REUSE` when its required target dependency contracts remain unresolved.

## 4.4 Persistence is a first-class boundary

Code presence does not prove persistence correctness. Packages affecting durable state must define schema ownership, load/save lifecycle, migration behavior, rollback and restart/crash expectations.

## 4.5 Protocol and client compatibility are explicit

Parser/serializer symmetry or compilation does not prove wire compatibility. Packages affecting login/game protocol, features, protobuf, identifiers, assets or UI payloads require exact client/server compatibility evidence and rollout rules.

## 4.6 Runtime proof is separate from static proof

Static inventory and tests do not prove runtime lifecycle. Runtime-sensitive packages require controlled runtime evidence.

## 4.7 Physical-client E2E is additive proof

The merged Universal Physical-Client E2E platform is the shared end-to-end layer. It complements unit/integration/runtime evidence and must not replace them.

## 4.8 World content stays evidence-bounded

OTBM/map/content migration uses the existing deterministic analysis stack. Donor evidence cannot authorize whole-map replacement, blind region import, automatic item substitution or assumed script handling.

## 4.9 Deterministic enforcement remains authoritative

AI may assist analysis and triage, but deterministic systems control gameplay, sanctions, economy mutation, migration execution, deployment and production safety.

# 5. Boundary classification

Every canonical module package must classify the target-relevant boundaries below as `applicable`, `not-applicable` or `unresolved`, with evidence.

| Boundary | Required questions |
|---|---|
| ownership/lifecycle | Who owns the module in target? How is it started, stopped, reloaded and cleaned up? |
| build/toolchain | What target build entries, dependencies and platform constraints apply? |
| configuration | Which configuration keys/defaults are owned, validated and versioned? |
| service/API | What public target interfaces exist and which legacy APIs are forbidden coupling? |
| scheduling/concurrency | What dispatcher/scheduler/thread/transaction assumptions exist? |
| persistence | What state is durable, where, with which migration and rollback contract? |
| protocol/session | What wire/session/client contracts are affected? |
| identifiers/assets | Which IDs, assets or external data are required and how are conflicts handled? |
| world/map | Which OTBM/world/runtime semantics are required and how are they proven? |
| runtime | What controlled runtime evidence demonstrates the target lifecycle? |
| tests | Which deterministic unit/integration/contract tests are required? |
| physical-client E2E | Which real-client scenario is required, if any? |
| operations | What deployment, observability, rollback and failure behavior applies? |
| security/privacy | What trust boundaries, permissions or sensitive data are involved? |

An unresolved applicable boundary blocks `REUSE`.

# 6. Migration package manifest

Every bounded migration package must record at least:

```text
package_id
module_id
legacy_repository
legacy_sha
legacy_source_paths
target_repository
target_base_sha
target_head_sha
upstream_repository
upstream_baseline_sha
target_paths
depends_on
interacts_with
boundary_classification
source_evidence
runtime_evidence
physical_client_e2e_evidence
migration_disposition
disposition_rationale
known_gaps
rollback_plan
provenance_notes
```

When a field is required but unavailable, use an explicit blocked/unresolved state. Do not synthesize a value.

# 7. Migration dispositions

## REUSE

Meaning: the legacy implementation can be transferred with minimal structural change.

Required evidence:

- target API compatibility;
- target ownership and lifecycle compatibility;
- persistence compatibility when applicable;
- protocol/client compatibility when applicable;
- current focused/integration tests for the audited scope;
- controlled runtime proof when runtime-sensitive;
- physical-client E2E when user-visible/session/protocol behavior requires it;
- no blocking legacy coupling;
- exact legacy/target/upstream provenance.

`REUSE` is not permitted from inventory evidence alone.

## ADAPT

Meaning: legacy behavior or implementation logic is useful, but target architecture requires deliberate changes.

Required evidence:

- functional contract worth preserving;
- identified target incompatibilities;
- explicit adaptation plan;
- target-side tests for changed boundaries;
- migration and rollback plan.

## REVALIDATE

Meaning: evidence is insufficient for a stronger decision.

This is the current default for all 62 canonical modules.

`REVALIDATE` grants no permission to copy, port, rewrite or drop a module.

## REWRITE

Meaning: the functional responsibility belongs in Oteryn, but the legacy implementation should not be transferred.

Required evidence:

- target need is established;
- concrete legacy architecture/coupling incompatibility is documented;
- target contract is explicit enough to implement independently;
- rewrite tests are defined from behavior/evidence rather than copied implementation details.

## DO_NOT_MIGRATE

Meaning: the responsibility does not belong in the target Oteryn architecture/product.

Required evidence:

- explicit target exclusion or superseding responsibility;
- dependency impact analysis;
- no unresolved consumer still requires the module.

## EXPERIMENTAL_ONLY

Meaning: the responsibility may remain in the legacy laboratory or an experimental target branch, but is not approved for Oteryn core.

Required evidence:

- reason it is useful experimentally;
- reason core target criteria are not met;
- isolation boundary preventing accidental production/core dependency.

# 8. Baseline pinning contract

For each migration package:

1. Re-fetch live `blakinio/canary:main` and record exact SHA.
2. Re-fetch the target default branch and record exact SHA.
3. Re-fetch `opentibiabr/canary` and pin the exact upstream SHA relevant to the target baseline.
4. Pin maintained-client SHA when protocol/UI applies.
5. Pin any donor/reference SHA used for comparison.
6. Pin map/datapack/client build/capture identity separately when applicable.
7. Record whether each baseline is task-start evidence, target ancestry, comparison-only evidence or runtime/E2E input.

A later moving branch head does not retroactively change package proof. A package must revalidate if its target or critical dependency baseline changes before merge.

# 9. Cross-repository evidence contract

Cross-repository evidence must state the role of each repository.

A path match or similar implementation may establish only a discovery candidate until semantic evidence is reviewed.

Rules:

- upstream/donor match != bug proof;
- upstream/donor match != ownership;
- upstream/donor match != semantic equivalence;
- upstream/donor match != migration authorization;
- exact ancestry != behavioral parity;
- maintained OTClient proves its own interpretation, not official Tibia behavior;
- official Tibia evidence and packet captures are used according to their question-specific authority.

When partial server/client rollout is unsafe, use an explicit atomic cross-repository contract before merge.

# 10. Dependency-aware migration ordering

The current canonical dependency graph places infrastructure dependencies before many domain modules. Therefore initial revalidation order is:

```text
target repository/baseline
→ engine/build/runtime foundation
→ database/persistence foundation
→ account/character lifecycle
→ network/login/protocol contract
→ item/world runtime foundation
→ first evidence-selected low-risk module
→ target physical-client E2E proof
→ dependency-ordered domain migrations
```

Later broad waves may include:

```text
combat
items/economy
creatures/spawns
content systems
client-facing systems
analytics/liveops
```

This is not a fixed bulk-migration sequence. Each package must inspect the live canonical `depends_on` graph and affected target dependencies.

No package may claim independence merely because files live in different directories.

# 11. Evidence ladder

A migration package advances through explicit proof layers:

```text
inventory/path discovery
→ source comparison
→ target architecture compatibility
→ deterministic focused tests
→ integration proof
→ runtime proof
→ persistence/protocol proof where applicable
→ physical-client E2E where applicable
→ migration disposition
```

Skipping a non-applicable layer requires an explicit `not-applicable` rationale.

`unresolved` must remain unresolved until evidence closes it.

# 12. Universal Physical-Client E2E contract

Future target proof must reuse the merged platform from PR #245.

Expected model:

```text
module migrated
→ target builds
→ deterministic tests pass
→ controlled runtime proof passes
→ applicable persistence/protocol checks pass
→ bounded physical-client scenario passes
```

Feature packages own only their scenario/assertions. Generic orchestration changes require a separate E2E-platform task.

# 13. Upstream Intelligence contract

Use the existing Upstream Intelligence program for read-only discovery.

Its source-role-aware mapper may identify candidate modules and local reference paths. It must not automatically change migration dispositions or create implementation branches.

Any candidate adopted into Oteryn requires a separate bounded migration task pinned to the exact candidate revision and target baseline.

# 14. OTBM and world-content contract

Reuse the existing OTBM pipeline, including the canonical World Index, item/mechanic audit, script resolution, reachability, spawn/NPC evidence, storage graph, Semantic OTBM Diff and geometry/consistency analysis.

World migration decisions must preserve separate evidence for:

- geometry;
- item/mechanic placements;
- AID/UID;
- teleport destinations;
- houses/doors;
- script registrations/handlers;
- NPC/monster definitions;
- spawn placements;
- storage progression;
- runtime behavior.

No whole-map replacement or blind donor import is authorized.

# 15. Legacy baggage rejection rules

A migration package must explicitly reject or isolate legacy baggage when any of these apply:

- target has a cleaner upstream-native implementation;
- legacy code depends on fork-specific globals or hidden lifecycle assumptions;
- duplicated managers/registries/services exist;
- persistence behavior is incomplete or unverifiable;
- protocol coupling is not version-gated;
- path layout hides multiple canonical module responsibilities;
- donor-derived behavior lacks authoritative evidence;
- temporary experiments or audit-only tools would become production dependencies;
- compatibility shims are only needed by the legacy repository.

A `REWRITE`, `ADAPT`, `DO_NOT_MIGRATE` or `EXPERIMENTAL_ONLY` outcome is preferable to carrying baggage without proof.

# 16. Validation and merge contract

Before any migration PR merges:

1. verify current base/head SHAs;
2. verify exact changed files;
3. verify ownership and no forbidden paths;
4. verify package manifest completeness;
5. verify required focused tests on current head;
6. verify integration/runtime/E2E proof on current head where applicable;
7. inspect PR comments;
8. inspect submitted reviews;
9. inspect unresolved review threads;
10. verify required CI on the current head;
11. verify no blocker or migration hold remains;
12. squash-merge with exact-head guard when available;
13. archive the task through a separate lifecycle-only PR.

Historical green CI on an older SHA is not sufficient.

# 17. Missing entry conditions

The following conditions are intentionally unresolved at OAM-001 completion:

```text
Oteryn target repository
Oteryn default branch
Oteryn target task-start SHA
Oteryn write authorization
exact then-current opentibiabr/canary target baseline SHA
```

These are blockers, not placeholders to fill with assumptions.

# 18. Exact next bounded task

After OAM-001 merges and its lifecycle task is archived, the exact next package is:

```text
OAM-002 — Oteryn target repository and baseline pinning
```

OAM-002 may start only after an authorized Oteryn repository is explicitly designated or created. It must record:

```text
target repository
target default branch
target task-start SHA
write ownership
ten-current upstream Canary baseline SHA
target ancestry/bootstrap relationship
```

Until then, no Oteryn implementation or module migration task may begin.
