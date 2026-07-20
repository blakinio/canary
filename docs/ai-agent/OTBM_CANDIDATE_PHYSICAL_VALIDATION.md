# OTBM candidate-map Physical E2E validation

`tools/e2e/otbm_candidate_physical_validation.py` is the bounded OTBM-E2E-009 bridge between an already approved create-new map candidate and the existing Universal Physical E2E runtime.

It does not parse or write OTBM, calculate paths, implement a second World Index, start a second E2E runner, or create another workflow. The bridge validates exact evidence, prepares disposable runtime state, reuses existing exact-map route preparation, and delegates only selected scenarios to the unchanged existing `tools/e2e/run_physical_e2e.sh` runner.

## Contract

The output format is `canary-otbm-candidate-physical-validation-v1`, schema version `1`, validated by `OTBM_CANDIDATE_PHYSICAL_VALIDATION.schema.json`.

Required evidence inputs are:

- the unchanged source `.otbm`;
- the create-new candidate `.otbm`;
- successful `canary-otbm-repair-materialization-pipeline-v1` evidence with exact candidate Map Quality Gate proof;
- compatible `canary-otbm-semantic-diff-v1` evidence whose `before` map is the source and `after` map is the candidate;
- `canary-otbm-e2e-impacted-selection-v1` evidence pinned to the exact Semantic Diff bytes and the same before/after map and World Index hashes.

The bridge recomputes map and evidence SHA-256 values. A stale, mismatched, malformed, in-place, overwrite-capable, or non-quality-gated chain fails closed before physical execution.

## Selected-only execution

Only scenarios with `selected: true` in the OTBM-E2E-008 artifact are eligible to execute. Their current repository scenario manifests must still match the manifest SHA captured by that selection. Selected scenarios must target one logical Canary datapack/map so one candidate cannot silently stand in for unrelated worlds.

`--execute` performs this bounded sequence:

1. create a unique disposable repository workspace under the source repository `artifacts/` directory;
2. copy the repository into that workspace while excluding `.git`, existing `artifacts/`, local build trees, `otclient`, and client asset payloads;
3. replace only the selected logical map inside the **disposable copy** of the selected datapack with the exact verified candidate;
4. for `follow_route` scenarios, call the existing `prepare_otbm_route.py` against that candidate runtime map;
5. run only selected scenarios through the copied, otherwise unchanged existing `run_physical_e2e.sh`, while the exact Canary binary, controlled OTClient and assets remain caller-supplied;
6. require the runner-retained `map.sha256` to equal the verified candidate SHA-256;
7. remove the entire disposable runtime workspace;
8. re-hash the original source map and fail if it changed.

The active datapack and source/production map are never overwritten or deployed. No runtime override is added to `server_selection.py` and no candidate-specific execution mode is added to `run_physical_e2e.sh`; isolation comes from changing the runner's disposable working repository, not from creating a second runner or map-selection path.

## Candidate landmark provenance

The committed semantic landmark registry is pinned to the baseline map and World Index, so a changed candidate cannot reuse those provenance hashes unchanged.

For selected route scenarios the bridge may create a transient artifact-only candidate registry only when all of these facts are proven:

- Semantic Diff scope is `full-index`;
- findings are not truncated;
- the complete finding set is present and every finding has an exact position;
- the reviewed baseline landmark registry is pinned to the Semantic Diff `before` map and World Index;
- every reviewed origin/destination anchor used by selected route requests is absent from the changed-position set.

Only provenance hashes are re-pinned in the transient copy. The committed registry is never modified. Existing `prepare_otbm_route.py` then rebuilds the candidate World Index and independently requires its exact SHA to match the Semantic Diff `after` World Index pin.

If those conditions are not satisfied, route execution fails closed unless `--candidate-landmark-registry` supplies an explicitly reviewed registry pinned to the exact candidate map and candidate World Index.

## Usage

Validate evidence and scenario selection without starting Canary or OTClient:

```bash
python tools/e2e/otbm_candidate_physical_validation.py \
  --source-map /evidence/source.otbm \
  --candidate-map /evidence/candidate.otbm \
  --pipeline-result /evidence/pipeline-result.json \
  --semantic-diff /evidence/semantic-diff.json \
  --impacted-selection /evidence/impacted-selection.json \
  --output-dir artifacts/candidate-validation
```

Execute selected Physical E2E scenarios after the exact Canary binary, controlled OTClient, MariaDB and password environment required by the existing runner are available:

```bash
python tools/e2e/otbm_candidate_physical_validation.py \
  --source-map /evidence/source.otbm \
  --candidate-map /evidence/candidate.otbm \
  --pipeline-result /evidence/pipeline-result.json \
  --semantic-diff /evidence/semantic-diff.json \
  --impacted-selection /evidence/impacted-selection.json \
  --assets-dir /evidence/assets \
  --output-dir artifacts/candidate-validation \
  --execute
```

When OTBM-E2E-008 proves exact non-impact for every represented candidate scenario, `selectedCount` is zero and physical execution is not required. That decision applies only to the OTBM-aware scenario set represented by the selection artifact; it is not general gameplay correctness and does not suppress unrelated suites.
