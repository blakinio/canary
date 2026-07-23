# OTBM QA Contract Hardening — OWA-005

Status: bounded hardening package for `CAN-PROGRAM-OTBM-WORLD-ASSURANCE-OPERATIONS`.

This note records the regression invariants added by `OWA-005 — QA Contract Hardening and Adversarial Fixtures`. It does not define a new canonical OTBM implementation. The tested code remains the delivered World Quality/Repair QA stack and existing OTBM-E2E candidate validation stack.

## Hard boundaries

OWA-005 does not add or replace an OTBM parser, World Index, Script Resolution engine, pathfinder, Semantic Diff engine, renderer, writer/materializer or Physical E2E runner. Fixtures are small deterministic Python objects only. No production map, generated `.otbm` or `.widx` is committed or used as a mutable fuzz target.

## Newly protected invariants

### Regression Guard canonical determinism

Semantically unordered Semantic Diff finding permutations must produce byte-equivalent Regression Guard object content and the same canonical report SHA-256.

`impactEvidence.sampledFindingIds`, sampled positions and sampled mechanic evidence are canonicalized independently of incoming finding order. OWA-005 found that `sampledMechanics` previously preserved input order; the bounded production fix sorts that emitted list by stable `findingId` and changes no selection semantics.

### Bounded evidence cannot authorize safe skip

A bounded-region Semantic Diff cannot authorize a represented Physical E2E scenario skip. The existing Regression Guard must continue to reject bounded or truncated evidence as skip authority even when a supplied impacted-selection artifact claims exact non-impact.

This protects the distinction between bounded absence and global absence.

### Dependency-scoped release freshness

Release provenance is tested across deterministic permutations of component order, dimension order and `dependsOn` order.

Changing only the appearance component SHA must stale exactly the dimensions that depend on appearances while an independent map-only source-correlation dimension remains current. Canonical output must not depend on manifest ordering.

### Certification current-map provenance

Region/quest certification target ordering is tested as semantically unordered input.

`stale`, `mixed` and `not-evaluated` current-map provenance cannot retain a formal certification level above `C0_NOT_EVALUATED`:

- `stale` -> `C0_NOT_EVALUATED`, certification state `stale`;
- `mixed` -> `C0_NOT_EVALUATED`, certification state `stale`;
- `not-evaluated` -> `C0_NOT_EVALUATED`, certification state `not-evaluated`.

All retain the explicit current-map provenance blocker.

### Continuous Assurance cross-contract composition

Permutation of semantically unordered selected validators, selected scenarios and their execution results must not change the Continuous Assurance report.

The gate must fail closed when after-Certification map/World Index provenance disagrees with the Regression Guard after-map identity. An after-certification state of `stale` must block the gate even when the numeric/formal certification level does not drop.

### Asset compatibility unknown evidence

A used OTBM item with no canonical object appearance remains an explicit error and produces `ok=false`. Reordering used item IDs must not change the report. Missing appearance evidence is never treated as compatible or as positive walkability evidence.

### Read-only composition

The hardening suite asserts that the tested Regression Guard and release-provenance composition inputs are not mutated. Asset compatibility input dictionaries are likewise preserved by report construction.

## Existing focused coverage reused, not duplicated

The following high-value boundaries were inspected and already have direct focused regression coverage in their owning suites:

- candidate Physical E2E: pipeline candidate SHA mismatch, Semantic Diff after-map SHA mismatch and impacted-selection Semantic Diff hash mismatch fail closed;
- candidate runtime materialization: disposable runtime copy must contain the exact verified candidate SHA and must remain under repository `artifacts/`;
- Dependency/Blast-Radius Graph: unresolved evidence is an explicit traversal boundary, expectation mismatches remain unresolved, unknown node references fail closed, and World Health/Coverage current map/World Index mismatches are rejected;
- Compact Evidence Gateway: source hash mismatch, source format mismatch and unsafe source path are rejected;
- existing per-contract output-safety suites remain the authority for no-clobber/create-new/input-output alias/unsafe-path/symlink behavior;
- existing identifier conflict tests remain the authority for duplicate finding/target/component/node IDs; OWA-005 does not auto-repair identifiers;
- existing World Index, Script Resolution, Reachability and Semantic Diff implementations remain canonical and are consumed only through their delivered evidence contracts.

## Remaining bounded hardening gaps

These are not claims of defects. They are future fixture opportunities after OWA-005:

1. Broader permutation families for optional evidence collections inside Coverage Dashboard and Dependency Graph manifests.
2. Additional explicit symlink/alias adversarial cases for contracts whose current output-safety suites cover path safety indirectly rather than through every platform-specific alias form.
3. Larger deterministic generated selector matrices for duplicate/reused AID/UID combinations across World Index -> Script Resolution -> Coverage, provided they continue to use the existing canonical implementations.
4. Candidate Physical E2E retained-runtime-hash failure injection at the Universal Physical E2E result boundary without adding a second runner.
5. Cross-contract freshness propagation that includes future asset/render certification dimensions when those dimensions become formal certification inputs.

None of these gaps authorizes current evidence to be treated as handled, safe, non-impacting or current when an owning contract says unresolved, conflicting, stale, truncated, ambiguous or unproven.
