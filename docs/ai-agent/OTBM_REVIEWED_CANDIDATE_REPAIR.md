# OTBM Reviewed Candidate Repair Orchestration

`OTBM-QA-004` adds a deterministic evidence-chain boundary after the review-only QA-003 recommendation layer.

Public contracts:

- approval: `canary-otbm-reviewed-candidate-repair-approval-v1`;
- result: `canary-otbm-reviewed-candidate-repair-v1`;
- approval schema: `docs/ai-agent/OTBM_REVIEWED_CANDIDATE_REPAIR_APPROVAL.schema.json`;
- result schema: `docs/ai-agent/OTBM_REVIEWED_CANDIDATE_REPAIR.schema.json`;
- implementation: `tools/ai-agent/otbm_reviewed_candidate_repair.py`;
- CLI: `tools/ai-agent/otbm_reviewed_candidate_repair_tool.py`.

## Purpose

The orchestrator validates one already-produced, explicitly reviewed candidate evidence chain:

```text
QA-003 supported recommendation
  + exact human/review approval
  + existing repair/materialization pipeline result
  + exact Semantic Diff
  + exact OTBM-E2E-008 impacted selection
  + exact OTBM-E2E-009 candidate validation
  -> reviewed candidate repair result
```

It does not execute any of those stages. It verifies that the stages refer to the same exact source, candidate, mutation authorization and downstream evidence bytes.

## Approval contract

`canary-otbm-reviewed-candidate-repair-approval-v1` is caller-supplied reviewed evidence. The tool never generates it.

The approval pins:

- exact QA-003 recommendation SHA-256;
- exact source-map SHA-256;
- exact target selector;
- exact expected old state;
- exact intended target state;
- one canonical existing repair/materialization pipeline mode;
- exact writer/materializer-specific plan or approval SHA-256 and format;
- non-empty reviewer identity and review rationale.

The approval is rejected unless all copied target/state fields exactly equal the QA-003 recommendation.

## Deterministic mutation-mode binding

The orchestrator accepts only QA-003 states that already proved an existing technical path:

| QA-003 capability | Pipeline mode | Required pinned writer/materializer evidence |
|---|---|---|
| `phase8-attribute` + one supported Phase 8 operation | `fixed-width-attribute` | `canary-otbm-bounded-patch-plan-v1` |
| `tile-area` + `complete-zero-translation-replace-region` | `tile-area` | `canary-otbm-area-materialization-approval-v1` |
| `bounded-raw-tile-replacement` | `tile-replacement` | `canary-otbm-tile-materialization-approval-v1` |
| `bounded-raw-tile-insertion` | `tile-insertion` | `canary-otbm-tile-insertion-approval-v1` |
| `bounded-raw-tile-deletion` | `tile-deletion` | `canary-otbm-tile-deletion-approval-v1` |
| `bounded-raw-tile-type-conversion` | `tile-type-conversion` | `canary-otbm-tile-type-conversion-approval-v1` |

The successful pipeline result must use the same mode and contain exactly one direct input pin matching the approval's exact mutation-authorization SHA-256 and format.

No unsupported QA-003 state is promoted by approval. `review-required`, `unsupported-mutation-shape`, `blocked-by-runtime-evidence`, `ambiguous-target` and `no-repair-evidence` fail closed.

## Source and candidate chain

The tool requires:

1. recommendation source-map SHA-256 = approval source-map SHA-256;
2. pipeline source SHA-256 = approved source SHA-256 and `unchanged=true`;
3. pipeline output is create-new and byte-identical to its verified internal candidate;
4. pipeline Map Quality source SHA-256 = candidate SHA-256;
5. Semantic Diff `before` source map = approved source;
6. Semantic Diff `after` source map = candidate;
7. OTBM-E2E-008 pins the exact Semantic Diff bytes and the same before/after map and World Index identities;
8. OTBM-E2E-009 pins the exact pipeline result, Semantic Diff and impacted-selection bytes and the same source/candidate identities.

Any mismatch fails closed.

## Physical E2E completion states

The result exposes exactly three states.

### `physically-validated`

At least one represented OTBM-aware scenario is selected, OTBM-E2E-009 marks Physical E2E required and performed, every retained selected execution succeeded, and every runtime `map.sha256` equals the exact candidate SHA-256.

### `validated-no-physical-e2e-required`

OTBM-E2E-008 selected zero represented scenarios and OTBM-E2E-009 confirms Physical E2E is not required. This is an exact non-impact decision only for the represented OTBM-aware scenario set.

It does not suppress unrelated gameplay, integration or non-OTBM test suites.

### `physical-e2e-required`

At least one represented scenario is selected but OTBM-E2E-009 evidence shows execution was not performed. The composed report is emitted with `ok=false` and blocker `SELECTED_PHYSICAL_E2E_NOT_EXECUTED`.

The orchestrator never upgrades validate-only evidence to physical proof.

## Safety boundary

The orchestrator:

- reads JSON evidence only;
- never parses or scans OTBM;
- never builds a World Index;
- never executes Script Resolution or Reachability;
- never invokes Phase 8 patching or any materializer;
- never invokes the repair/materialization pipeline;
- never recomputes Semantic Diff;
- never recomputes impacted selection;
- never starts Universal Physical E2E or OTBM-E2E-009;
- never generates approval;
- never modifies, deploys or promotes a map.

A successful report proves only that the retained reviewed evidence chain is exact and mutually compatible. Physical success is limited to the represented selected scenarios and exact candidate provenance; it is not global gameplay correctness.

## Output safety

All six JSON inputs are read as stable regular non-symlink files and SHA-256 pinned into the result:

- recommendation;
- approval;
- pipeline result;
- Semantic Diff;
- impacted selection;
- candidate Physical E2E validation.

Inputs must be distinct. The output cannot alias an input by path or hard link. Output is create-new/no-clobber unless `--overwrite` is explicitly provided, in which case replacement is atomic.

Generated approval/result evidence remains outside Git.

## CLI

```bash
python tools/ai-agent/otbm_reviewed_candidate_repair_tool.py \
  --recommendation /external/recommendation.json \
  --approval /external/reviewed-approval.json \
  --pipeline-result /external/pipeline-result.json \
  --semantic-diff /external/semantic-diff.json \
  --impacted-selection /external/impacted-selection.json \
  --physical-validation /external/candidate-physical-validation.json \
  --output /external/reviewed-candidate-repair.json
```

The CLI exits successfully only for `physically-validated` or `validated-no-physical-e2e-required`. A valid but still-pending `physical-e2e-required` result is written and returns exit code `3`.
