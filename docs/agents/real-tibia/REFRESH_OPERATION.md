# Real Tibia Evidence Refresh and Drift Operation

`tools/agents/real_tibia_refresh_plan.py` is the read-only RTEC-006 planning boundary. It selects published evidence records that require bounded re-verification and emits one deterministic JSON plan to standard output.

The planner does not modify evidence, dossier files, owner requests, generated indexes or programme state. A selected record is a review trigger, not proof that Canary is defective, Real Tibia changed, or parity drift exists.

## Inputs

Every run requires an explicit date:

```sh
python tools/agents/real_tibia_refresh_plan.py --as-of 2026-07-31
```

The date is the only freshness clock. The tool never reads the wall clock.

Optional selectors are repeatable:

```sh
python tools/agents/real_tibia_refresh_plan.py \
  --as-of 2026-07-31 \
  --target-version canary_commit=dcc09b1d012cbf4462aecc9970ae8540353ea8e3 \
  --target-version official_tibia_release="Summer Update 2026" \
  --changed-path src/creatures/interactions/chat.cpp \
  --changed-source current-canary-chat-communication-path \
  --module vocations
```

| Selector | Meaning |
|---|---|
| `--target-version AXIS=VALUE` | Compare an exact current target against exact record observation/comparison anchors for one canonical version axis. One value per axis is allowed. |
| `--changed-path REPO_PATH` | Select records whose exact Canary provenance path is equal to, below, or above the supplied repository-relative path. Wildcards and unsafe paths are rejected. |
| `--changed-source SOURCE_ID` | Select records that contain the exact evidence `source_id`. |
| `--module MODULE_ID` | Select every actionable published record in an exact canonical module. |
| `--root PATH` | Use another repository root, primarily for focused tests. |

The canonical version axes are:

- `official_tibia_release`;
- `official_client_build`;
- `protocol_profile`;
- `canary_commit`;
- `maintained_otclient_commit`;
- `map_sha256`;
- `datapack_revision`;
- `appearances_items_revision`;
- `spawn_npc_sidecar_revision`;
- `database_schema_revision`.

Commit and map targets require exact lowercase hashes. Other version values use the existing evidence-contract version syntax. Duplicate selectors and duplicate target axes fail closed.

## Publication and actionability boundary

The planner loads the existing `Corpus` and reuses `validate_for_publication` from the evidence tooling.

- `discovered`, `normalized` and `review-needed` records remain outside the plan because they are not published evidence.
- `REJECTED` and `SUPERSEDED` evidence, and records with matching terminal statuses, remain visible to corpus validation but are not actionable plan items.
- Generated-index missing/drift diagnostics are ignored by this read-only operation because a planning `--as-of` date may intentionally differ from the last published index date.
- Every other corpus validation error remains blocking, including future evidence relative to `--as-of`.

The planner never regenerates an index to make planning succeed.

## Selection rules

A published actionable record is selected when at least one rule matches.

### Freshness

The planner uses the existing `Corpus.stale_rows()` result. Boundaries are inclusive:

- `age_days >= warning_after_days` produces `freshness-warning-window-reached`;
- `age_days >= invalid_after_days` produces `invalidation-window-expired`;
- explicit `evidence_state: STALE` produces `explicit-state`.

### Version delta

For each supplied target axis, the planner collects exact values from:

- `current_canary_comparison.baseline`;
- `applicability.observed_in[]` markers whose mode is `EXACT`.

A `version-delta` reason is emitted only when the record contains at least one exact value for the axis and the target is not among those values. An `UNKNOWN` axis is not promoted into a drift finding.

Records whose `authority_dimension` is `historical-version` are not selected solely because a newer target version exists. Their historical claim remains bounded to its recorded version unless another selector or freshness rule applies.

### Path, source and module

Changed paths are matched against the union of:

- `current_canary_comparison.exact_paths`;
- each source's `selected.files`;
- a source locator's `repository_path` when the locator refers to `blakinio/canary` or does not name a repository.

A path matches when either side is the exact path or an ancestor of the other. Source and module selectors use exact identifiers.

## Priority

Each selected item receives one deterministic priority:

| Priority | Trigger |
|---|---|
| `critical` | Explicit stale state or expired invalidation window. |
| `high` | Exact version delta, changed path or changed source. |
| `normal` | Freshness warning or explicit module selection without a higher trigger. |

Items are sorted by priority, module ID and evidence ID. Reasons and all selector arrays are also sorted deterministically.

## Output contract

The JSON document uses:

```text
format: canary-real-tibia-refresh-plan-v1
schema_version: 1
```

Top-level fields include:

- `as_of` and normalized `selection`;
- `input_sha256`, binding the date, selectors, canonical module set and exact published evidence document path/SHA-256 inventory;
- `summary`, with corpus/publication/actionability counts and reason/priority counts;
- `items`, each retaining exact record identity, record SHA-256, provenance paths/source IDs, exact version anchors, reasons and the non-mutating next action;
- `nonclaims`;
- `plan_sha256`, calculated over the complete plan excluding the `plan_sha256` field itself.

`verify_plan_sha256()` can verify an in-memory plan. Re-running against identical evidence bytes and logically identical selector sets produces the same JSON values and digests regardless of argument order.

## Operator sequence

1. Verify current `main`, open PRs and active ownership before planning.
2. Run the planner with an explicit `--as-of` and only evidence-backed change selectors.
3. Retain the JSON outside Git when it is operational output; do not commit generated review queues into the evidence corpus.
4. Review each item and create bounded Collector work only for records that genuinely require new evidence.
5. Re-verify through the normal RTEC collection and independent review lifecycle.
6. Let the authorized coordinator publish any later dossier or shared-index changes in separately owned work.

The planner does not reserve paths, create tasks, transition requests, accept evidence or certify parity.

## Validation

Focused validation for planner changes is:

```sh
python -m py_compile \
  tools/agents/real_tibia_refresh_plan.py \
  tools/agents/test_real_tibia_refresh_plan.py
python -m unittest -v tools.agents.test_real_tibia_refresh_plan
```

The broader Real Tibia focused discovery command remains:

```sh
python -m unittest discover -v -s tools/agents -p 'test_real_tibia*.py'
```

A successful command proves only deterministic planner behavior over the validated corpus contract. It does not prove that any selected record is stale in the real world or that an external source changed.
