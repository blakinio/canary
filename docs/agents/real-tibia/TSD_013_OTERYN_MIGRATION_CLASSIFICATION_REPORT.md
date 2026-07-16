# TSD-013 — Oteryn Migration Classification

> Task-start main: `10d4bf63cf356a3cf912cbc8717854e6a6fd2895`.
> Canonical registry snapshot: 62 records.
> Classification only. No code is copied to Oteryn and no Oteryn readiness is claimed.

<!-- TSD013_CLASSIFICATION
registry_snapshot_sha: 10d4bf63cf356a3cf912cbc8717854e6a6fd2895
registry_total: 62
scope: ALL_CANONICAL_MODULES
disposition: REVALIDATE
-->

## Result

Every module present in the canonical Real Tibia registry at the task-start snapshot is classified **REVALIDATE** for any future Oteryn migration decision.

This report deliberately does **not** reproduce the 62 module IDs. The canonical inventory remains `docs/agents/real-tibia/registry/**`; the generated indexes remain derived views. The classification applies dynamically to the complete canonical registry snapshot rather than creating a second migration registry.

Registry impact:

- before: 62 records;
- after: 62 records;
- records added: 0;
- existing records modified: 0;
- generated indexes modified: 0.

## Meaning of REVALIDATE

`REVALIDATE` means only that the Canary-side module boundary and its current evidence remain useful inputs for a future migration decision.

It does **not** mean:

- copy the implementation;
- port the implementation as-is;
- preserve the same source-tree layout;
- preserve the same database schema;
- preserve the same protocol surface;
- preserve the same runtime or deployment topology;
- rewrite or drop the module;
- declare the module compatible with Oteryn;
- declare the module Oteryn-ready.

A stronger disposition requires an explicit target architecture and a bounded task that compares the then-current canonical registry record with that target contract.

## Why all modules remain REVALIDATE

### 1. No target architecture contract is registered

The current Tibia System Decomposition program has an empty `cross_repo_contracts` list. No Oteryn repository or architecture contract is part of the current program source-of-truth.

Without a target contract, the program cannot safely decide whether a Canary boundary should be copied, adapted, reimplemented, split, merged or omitted.

### 2. Canary evidence is not target compatibility proof

The registry records describe Canary and related evidence. Their maturity dimensions capture source-side implementation/evidence/persistence/protocol/tests/runtime/E2E state.

Even a record with stronger source-side maturity does not prove:

- Oteryn API compatibility;
- Oteryn persistence compatibility;
- Oteryn protocol compatibility;
- Oteryn threading/runtime compatibility;
- Oteryn ownership or DI compatibility;
- Oteryn deployment compatibility;
- safe code reuse.

### 3. TSD inventory records intentionally start conservatively

The decomposition program explicitly treats file/schema/helper/test presence as inventory evidence and forbids inferring runtime, persistence, protocol, parity, E2E or migration readiness from those paths alone.

TSD-013 therefore does not upgrade any module maturity and does not convert inventory into migration approval.

### 4. Tooling is not automatically target runtime code

`otbm-tooling`, `upstream-intelligence`, `physical-client-e2e`, `deployment-operations` and other platform-tooling records may remain useful as evidence or engineering tools around a future target. That still requires revalidation against the target repository, security model, CI environment and operational constraints.

No tooling record is marked for direct transfer by this package.

## Future decision gate

Before any module receives a disposition stronger than `REVALIDATE`, a future bounded task must have all of the following:

1. an explicit Oteryn repository/architecture contract;
2. exact target revision or immutable baseline;
3. target ownership and module-boundary rules;
4. target persistence and migration policy where applicable;
5. target protocol/client contract where applicable;
6. runtime/E2E proof requirements appropriate to the module;
7. a fresh read of the then-current canonical Canary registry record;
8. explicit decision evidence showing why copy/adapt/reimplement/merge/split/drop is safe.

If any required target fact is unknown, the module remains `REVALIDATE`.

## No second registry

This document is a checkpoint report, not a registry. It contains one global rule for the canonical snapshot and intentionally omits a duplicated 62-row module table.

Future work must query `docs/agents/real-tibia/registry/**` directly. It must not copy this report into a new Oteryn registry or treat generated Markdown as authority.

## No code transfer

TSD-013 performs no write to an Oteryn repository and no source move in Canary. It changes no runtime, gameplay, protocol, client, database, map, OTBM, datapack, assets, workflows, deployment implementation or E2E implementation.

The external repositories used by this project remain evidence sources only unless a future explicitly authorized cross-repository task says otherwise.

## Program close condition

After this feature PR and its separate lifecycle archive both pass exact-head checks, Ready/Required and squash merge:

- the bounded TSD-001 through TSD-013 queue is complete;
- the canonical registry remains at 62 records;
- the Oteryn migration disposition remains `REVALIDATE` for all canonical modules;
- any stronger migration action requires a new bounded program/task with an explicit Oteryn architecture contract.
