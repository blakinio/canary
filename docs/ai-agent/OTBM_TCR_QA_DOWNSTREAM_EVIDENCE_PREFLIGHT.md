# OWA-003B — TCR-to-QA Downstream Evidence Preflight

## Disposition

```text
BLOCKED_EXTERNAL_EVIDENCE
OWA003B_NO_RETAINED_EXECUTED_TCR_QA_FRESHNESS_IMPACT
```

This bounded read-only preflight starts from Canary main after OWA-003A feature PR #1031 and lifecycle PR #1032 merged.

It does not implement another OWA composition layer. It determines whether retained repository, task and pull-request evidence identifies the first exact executed input required by the downstream OWA-003 chain.

## Required downstream chain

```text
one executed canary-otbm-tcr-qa-freshness-impact-v1
  -> exact reviewed QA-008 dependency/blast-radius evidence where declared
  -> canonical Semantic Diff and QA-002 impacted validation
  -> owning validators and Universal Physical E2E execute
  -> exact QA-007 execution/result-set assurance
  -> refreshed QA-006 certification
```

The chain is ordered. Later compatibility is not evaluated when an earlier required exact input is absent.

## Preflight evidence

Current retained evidence proves:

- OWA-003A producer formats are stable/merged;
- its generated manifests and reports remain external artifacts by contract;
- the feature and lifecycle records preserve no invocation path, artifact ID, file SHA-256 and `reportSha256` for one executed real OWA-003A impact;
- repository searches found implementation, schema, documentation and synthetic fixture usage but no exact retained executed impact reference;
- no open OWA-003 task, branch or pull request owns downstream integration;
- OWA-003A explicitly leaves QA-008, QA-002 and QA-007 `not-evaluated` and QA-006 `not-refreshed`.

The first required downstream evidence is therefore absent.

## Why the preflight stops here

Without one exact executed OWA-003A impact, a consumer cannot prove:

- the exact TCR-011 routing report file/report identity;
- the exact QA-016 release-provenance file/report and current/previous BOM identities;
- the exact reviewed freshness manifest identity;
- the exact route/extract/target mappings actually evaluated;
- which components and dimensions passed exact changed-dependency equality;
- which unsupported or blocked routes remained targetless.

Consequently, there is no valid root evidence from which to bind QA-008 nodes/edges, establish a canonical map-change input for QA-002, identify executed validator/E2E results for QA-007 or refresh QA-006.

## Rejected substitutions

The following do not satisfy the blocker:

- the merged OWA-003A source code or schemas;
- unit-test/synthetic fixture outputs;
- TCR-011 routing alone;
- QA-016 release provenance alone;
- an inferred join based on IDs, names, paths or timestamps;
- a no-op/current-map-as-change scenario;
- a newly generated dependency graph without reviewed exact root evidence;
- plan-only QA-002 output;
- a QA-007 ledger with invented/not-run results;
- existing unrelated QA-006 certification.

## Re-entry requirement

An owning evidence workflow must retain or explicitly reference one executed `canary-otbm-tcr-qa-freshness-impact-v1` with all of these exact identities:

- artifact/path or durable external reference;
- file byte size and SHA-256;
- impact `reportSha256`;
- freshness-manifest file and canonical SHA-256;
- TCR-011 routing file and report SHA-256;
- QA-016 release-provenance file and report SHA-256;
- current BOM SHA-256 and previous BOM SHA-256 when compared;
- review ID and statement;
- invocation/workflow run and artifact identity where applicable.

Only after that input exists may a fresh bounded task evaluate, in order:

1. exact compatible QA-008 reviewed graph inputs and outputs;
2. canonical Semantic Diff and QA-002 selection;
3. exact selected validator and Universal Physical E2E execution evidence;
4. QA-007 exact result-set assurance;
5. refreshed QA-006 certification.

Missing evidence at any stage remains explicit and fail closed. No downstream package may create a second parser, dependency discoverer, Semantic Diff, validator, E2E runner, assurance engine or certification owner.

## Non-claims

This disposition does not mean that no executed impact exists anywhere. It means current retained repository/task/PR evidence does not identify one with sufficient exact provenance for consumption.

It does not classify gameplay behavior, map correctness, client/server parity, release safety or production readiness.
