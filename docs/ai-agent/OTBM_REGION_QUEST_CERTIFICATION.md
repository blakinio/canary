# OTBM Region and Quest Certification

`OTBM-QA-006` is a bounded read-only certification layer over the factual `canary-otbm-coverage-dashboard-v1` contract.

It does not parse OTBM, rebuild the World Index, resolve scripts, pathfind, run Physical E2E, validate candidates, or mutate maps. It assigns a formal `C0..C7` level only to explicitly selected non-world targets already present in an exact Coverage Dashboard.

## Inputs

- `canary-otbm-certification-targets-v1` — reviewed target IDs, requested maximum level, and rationale.
- `canary-otbm-coverage-dashboard-v1` — exact factual coverage dimensions and current-map provenance.

Both files are read stably and SHA-256 pinned in the output.

## Levels

Certification is contiguous. A target receives only the strongest level for which every requirement from `C1` through that level is satisfied.

| Level | Meaning | Required factual evidence |
|---|---|---|
| `C0_NOT_EVALUATED` | no current formal certification | missing/blocked first-level evidence or non-current provenance |
| `C1_STATIC_INDEXED` | exact reviewed mechanics are indexed | `indexedOnExactMap=proven` |
| `C2_STATIC_CORRELATED` | source and runtime-handler correlation are proven | C1 + `sourceCorrelated=proven` + `scriptResolved=proven` |
| `C3_STATIC_REACHABLE` | bounded static reachability is proven | C2 + `staticallyReachable=proven`; `interactionResolved` must be `proven` or `not-applicable` |
| `C4_STATIC_QUALITY_GREEN` | exact bounded static quality is compatible | C3 + `staticQualityCompatible=proven` |
| `C5_PHYSICAL_ROUTE_PROVEN` | selected reviewed route/mechanic population has current physical proof | C4 + `executableRouteCovered=proven` + `physicallyRuntimeProven=proven` |
| `C6_FEATURE_OR_MECHANIC_PHYSICALLY_PROVEN` | selected quest/mechanic-set population has current physical proof | C5 and target kind is `quest` or `mechanic-set` |
| `C7_CANDIDATE_CHANGE_REVALIDATED` | the reviewed candidate change is validated | C6 + `candidateMapValidated=proven` |

`region` and `landmark-route` targets are capped at C5. `quest` and `mechanic-set` targets may request up to C7.

The reviewed manifest may request a lower maximum level. The tool never promotes above that cap.

## Freshness

`staleAgainstCurrentMap.state` must be exactly `current`. `stale`, `mixed`, or `not-evaluated` provenance collapses formal certification to C0. The report still retains the evaluated evidence chain so reviewers can see what would otherwise be satisfied, but stale evidence is never represented as current certification.

## Non-claims

- C5/C6 are bounded to the exact reviewed target population represented by the Coverage Dashboard.
- Static or physical evidence for one target does not prove unrelated gameplay.
- C7 does not authorize deployment or promotion.
- No opaque score is emitted.
- Missing optional evidence is not global absence.
- The tool does not execute or rerun any validator or E2E scenario.

## CLI

```bash
python tools/ai-agent/otbm_region_quest_certification_tool.py \
  --manifest /path/to/certification-targets.json \
  --coverage-dashboard /path/to/coverage-dashboard.json \
  --output /path/to/certification.json
```

Outputs are create-new by default. Use `--overwrite` only for an explicit atomic replacement of a regular output file. Inputs cannot be overwritten or aliased by the output.
