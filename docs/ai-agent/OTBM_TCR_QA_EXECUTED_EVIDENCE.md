# OWA-003C — Executed TCR-to-QA Evidence Recovery


## Superseding operational status — OWA-003D

The exact snapshot-B package was supplied on 2026-07-31 and matches version `15.31.69f220` with archive SHA-256 `95093b15462573cc413fc7752d99ab258f97b58734bc59a8f6ef34cc1921a0f8`. OWA-003D therefore supersedes the OWA-003C missing-payload blocker for this execution runtime.

Existing TCR-009/010/011, QA-016 and OWA-003A owners produced and retained one real operational impact in workflow run `30614565219`, artifact `8786807858`. Exact identities, review statement, validation and the new downstream fail-closed boundary are recorded in [OTBM_TCR_QA_OPERATIONAL_EXECUTION.md](OTBM_TCR_QA_OPERATIONAL_EXECUTION.md).

The remaining blocker is no longer missing snapshot B. It is `OWA003D_NO_REVIEWED_QA008_ROOT_AND_CANONICAL_MAP_CHANGE_CHAIN`. The OWA-003C record below is preserved as historical recovery evidence.

## Historical OWA-003C disposition

```text
BLOCKED_EXTERNAL_EVIDENCE
OWA003C_NO_RECOVERABLE_EXACT_TCR009_SNAPSHOT_B_PAYLOAD_OR_RETAINED_REPORT_CHAIN
```

This bounded recovery package starts from Canary `main` at `9704087e3d6fc7b434938b343a546c14a23a447e`, after OWA-003B feature and lifecycle closure.

Its purpose is not to create another TCR, QA or OWA implementation. It tests whether the exact real evidence already proven during TCR-009 can be recovered or deterministically rematerialized so that the stable TCR-010, TCR-011, QA-016 and OWA-003A owners can execute and retain one operational `canary-otbm-tcr-qa-freshness-impact-v1`.

## Proven retained identities

The accepted TCR-009 lifecycle evidence proves that two complete client-reference snapshots previously existed and were hash-closed with the same parser revision:

- parser revision: `b68fbf7bf26b57f0cf716abffb52cfa951fa66ce`;
- snapshot A final manifest SHA-256: `6096b021ca21d911165f89bfc714f558fc7efde0a455855caed071852ccfcee1`;
- snapshot B final manifest SHA-256: `54646c3f71cc98c53049c63a49a331ec08acb71a37c551f5c592f55645be7e53`;
- retained evidence summary SHA-256: `6224a175fab73931627c1ea36545e4b5f1bc4c29068fa337049130ee777a3431`;
- retained drift SHA-256: `be0593cb260cc717b2d8e9e1a19a565f958e85935fde4ac09ce8fb5bbb853b31`;
- drift findings: `27`.

These hashes prove prior exact execution. They are not substitutes for the report bytes required by TCR-010 and downstream consumers.

## Recovery search and execution evidence

### Current supplied inputs

The current bounded runtime contains:

- one snapshot-A package, version `15.25.bd5a04`;
- the current OWA-001 source map with SHA-256 `a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2`.

The map is the current map, not an OWA-006 candidate. Snapshot A cannot replace the distinct snapshot-B payload.

### GitHub Actions retained artifacts

The following TCR-009 execution and exact-head workflow runs were checked for retained report payloads:

- owner-result run `30494786511`;
- programme reconciliation run `30495080685`;
- Agent Task Ownership `30496191170`;
- Real Tibia Evidence Contracts `30496191189`;
- Real Tibia Module Registry `30496191154`;
- Upstream Intelligence `30496191244`;
- Tibia Client Reference Drift `30496191213`;
- AI Agent Tools `30496191172`;
- Universal E2E Stability `30496191194`;
- CI `30496191295`;
- readiness CI `30496550577`.

The owning drift/evidence runs retain no snapshot, index or drift-report artifact. The ownership artifact contains only coordination diagnostics. The AI Agent Tools artifacts contain project-audit/content-pack outputs, not the proprietary snapshot-B payload or the exact TCR-009 report chain.

TCR-010, TCR-011 and OWA-003A exact-head workflows were also checked. They retain no executed operational gateway, routing or freshness-impact report.

### Official launcher rematerialization

OWA-003C workflow run `30580163217`, job `90998119134`, attempted bounded retrieval from the official launcher endpoint. It failed with HTTP 403 before parsing or accepting any package bytes.

Run `30580431144`, job `90999022124`, repeated the attempt with browser-compatible and launcher-compatible request profiles, bounded retries and response diagnostics. All six attempts were rejected by Cloudflare with HTTP 403. No package bytes were accepted and no artifact was produced.

### Public exact-tag rematerialization

Run `30580936803`, job `91000700142`, queried the public `dudantas/tibia-client` Git tag inventory and required exactly one tag whose `package.json` declared version `15.31.69f220`. It found no `15.31` candidate tag and accepted no payload.

The recovery code additionally required every selected raw file to equal its package-manifest `unpackedsize` and `unpackedhash`. That validation was never reached because no exact version source existed.

## Why execution stops before TCR-010

TCR-010 requires an exact supported source report and exact reviewed extract bindings. A known SHA-256 without the corresponding bytes cannot be selected through a JSON Pointer, value-hashed, extracted or passed to TCR-011.

Therefore OWA-003C cannot truthfully produce:

- an executed `canary-tibia-client-reference-evidence-gateway-v1`;
- an executed `canary-tibia-reference-adoption-routing-v1`;
- an exact reviewer-authored OWA-003A route/component/dimension mapping over that routing report;
- a compatible QA-016 provenance/BOM comparison bound to the actual routed evidence;
- an executed `canary-otbm-tcr-qa-freshness-impact-v1`;
- any downstream QA-008, Semantic Diff, QA-002, validator, Physical E2E, QA-007 or QA-006 refresh evidence.

Later stages remain unevaluated because their first exact source report is absent.

## Rejected substitutions

The following are not accepted:

- treating retained SHA-256 strings as report payloads;
- reconstructing 27 drift findings from summaries or task prose;
- selecting snapshot A as both baseline and current;
- using the current OTBM as a candidate map;
- deriving TCR-010 extracts from the Real Tibia evidence record instead of the owning TCR report;
- guessing JSON Pointers, route targets, component IDs or dimension dependencies;
- using unit-test fixtures or generated synthetic reports;
- creating a no-op Semantic Diff, QA-002 plan, execution ledger or QA-007 result;
- using generic QA-004 or OTBM-E2E-009 capability as a concrete candidate chain.

## Exact re-entry requirement

Re-entry requires at least one of these exact recoverable roots:

1. the original snapshot-B package bytes for version `15.31.69f220`, matching the previously reviewed package identity and reproducing final manifest SHA-256 `54646c3f71cc98c53049c63a49a331ec08acb71a37c551f5c592f55645be7e53`; or
2. the complete retained TCR-009 report chain: both final/bootstrap manifests, all six generated indexes and the drift report, each with byte size and SHA-256 matching the accepted TCR-009 identities.

After recovery, the owning workflow must execute and retain, in order:

1. TCR-010 exact gateway report and reviewed bindings;
2. TCR-011 exact routing request/report;
3. current and previous QA-016 BOM plus release-provenance report;
4. reviewer-authored OWA-003A manifest;
5. OWA-003A impact with file SHA-256, `reportSha256`, byte size, workflow run ID, artifact ID and review statement.

Only then may a new bounded task evaluate canonical QA-008, Semantic Diff, QA-002, owning validators, Universal Physical E2E, QA-007 and QA-006 in order.

## Independent OWA-006 state

OWA-006 remains independently blocked by:

```text
OWA006_NO_RETAINED_REVIEWED_REAL_CANDIDATE_CHAIN
```

No candidate was created or inferred by OWA-003C. The supplied OTBM remains the current map and cannot be reused as a candidate.

## Non-claims

This recovery failure does not invalidate the stable TCR-009/010/011 or OWA-003A contracts. It means the exact external bytes required to perform a new operational execution are not recoverable from the current supplied files, repository state, retained Actions artifacts, official launcher access or public exact-tag mirror.

It does not classify gameplay correctness, map correctness, client/server parity, deployment safety or production readiness.
