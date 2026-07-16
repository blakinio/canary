# OTBM repair sandbox verifier

## Purpose

`tools/ai-agent/otbm_repair_sandbox_tool.py` verifies an already-reviewed Phase 8 bounded patch by applying it only through the existing Phase 8 patcher to a distinct artifact copy and then measuring real before/after item-audit and script-resolution evidence.

It does not add a new OTBM mutation path. Phase 8 remains the only writer used by this workflow.

The verifier answers:

> Did the existing bounded patcher change exactly the planned existing attribute on its sandbox copy, keep the source untouched, and produce the observed real before/after mechanic and static runtime-resolution evidence at the exact planned placement?

A successful sandbox report is still not proof of gameplay correctness, player intent, reachability or physical-client behavior.

## Reused proof boundary

The verifier calls existing `apply_bounded_patch()` once and requires its successful `canary-otbm-bounded-patch-result-v1` evidence.

It does **not** rebuild these Phase 8 responsibilities:

- source/plan pin validation;
- native patch-anchor resolution;
- physical escape-width safety;
- copy-only mutation;
- byte equality outside planned payload spans;
- full scanner reparse;
- before/after World Index generation;
- exact bounded Semantic OTBM Diff;
- rollback/source-unchanged evidence.

The sandbox rejects the result unless all required Phase 8 proof flags are true and the resolved operation list exactly matches the supplied plan.

## New verification responsibility

After Phase 8 has published the sandbox copy and evidence, the verifier:

1. verifies the published output hash and every Phase 8 evidence-manifest file hash;
2. runs the existing item audit against the unchanged source and actual patched output;
3. runs the existing script-resolution audit against both real item-audit reports using the same script roots and rules;
4. loads the Phase 8 public before/after patch-anchor reports;
5. correlates each plan operation through the existing repair-preflight correlation logic;
6. requires exactly one exact before and after candidate at the planned `tilePlacementIndex`;
7. proves position, item ID and item depth stay stable;
8. proves the target attribute is `expected` before and `replacement` after;
9. proves all untargeted mechanic attributes on that placement are unchanged;
10. computes the existing structural script-resolution before/after diff from the two real resolver placements;
11. rechecks the original source bytes/stat identity and content-affecting audit/script inputs before final report publication.

## Inputs

Required:

- source `.otbm`;
- existing `canary-otbm-bounded-patch-plan-v1` JSON;
- compiled existing `otbm_item_audit_scan` scanner;
- artifact root for all generated copy/evidence/report outputs;
- matching appearances index;
- matching `items.xml`;
- repository root containing active script roots.

Optional:

- explicit active `--script-root` values;
- runtime registration rules;
- script review rules;
- custom artifact-relative Phase 8 output/evidence/result names;
- custom artifact-relative sandbox verification report name.

All generated destinations must stay below the artifact root. The verification report is create-new/no-clobber and must remain outside the Phase 8 evidence directory.

## Run

```bash
python tools/ai-agent/otbm_repair_sandbox_tool.py \
  /external/world.otbm \
  /external/reviewed-plan.json \
  --scanner tools/ai-agent/otbm_item_audit_scan \
  --artifact-root /external/artifacts/repair-sandbox \
  --appearances-index /external/appearances-index.json \
  --items-xml data/items/items.xml \
  --repository-root . \
  --script-root data \
  --script-root data-otservbr-global
```

Default generated paths below the artifact root are:

```text
patched.otbm
phase8-evidence/
phase8-result.json
sandbox-verification.json
```

The source map itself is never a destination.

## Exact operation verification

For each Phase 8 operation the verifier uses the plan identity:

- operation ID;
- kind/attribute;
- position;
- tile-local placement index;
- item ID;
- item depth;
- expected value;
- replacement value.

Before correlation uses the expected attribute value. After correlation uses the replacement value. Both sides must resolve to exactly one `anchorStatus: exact` candidate whose tile placement index, item ID and depth equal the plan.

Ambiguous or missing candidates fail verification. The tool never guesses between identical-looking placements.

Only the targeted mechanic attribute may differ in the selected placement. Other existing mechanic attributes among action ID, unique ID, house-door ID and teleport destination must remain identical.

## Actual runtime-resolution evidence

The verifier does not use the hypothetical in-memory replacement audit as proof of the patched result. It runs the real item audit on the actual Phase 8 output copy and reruns the existing script resolver from that generated audit.

For each operation the report contains:

- real before placement snapshot;
- real after placement snapshot;
- before runtime status;
- after runtime status;
- before/after selected script-resolution evidence;
- deterministic structural runtime diff and fingerprints;
- `runtimeResolutionChanged`;
- `runtimeRegression` when a previously `handled-*` placement is no longer `handled-*`;
- `replacementRuntimeResolved`.

`runtimeRegression` is review evidence. It does not make structural sandbox `ok` false by itself. A planned repair may intentionally change runtime wiring, but that change must remain explicit and reviewed.

Statuses such as `unresolved`, `referenced-only`, `partially-resolved` and `conflicting` are preserved exactly. Review rules never promote them to handled runtime evidence.

## Input stability

Before Phase 8 execution the verifier pins:

- plan file;
- source map;
- scanner;
- appearances index;
- `items.xml`;
- runtime/review rules when supplied;
- exact selected Lua/XML script corpus fingerprint;
- repository Git evidence when available.

After all before/after audits and resolver runs it recomputes the content-affecting pins. A content change aborts verification.

Repository Git `dirty` state is recorded before/after but is not itself used as a content-equality gate because the sandbox may legitimately create untracked artifacts under a repository-local artifact directory. The exact script-corpus hash remains the authoritative scanned-script content gate.

The original source additionally keeps a size, mtime and SHA-256 recheck before final publication.

## Phase 8 evidence verification

The verifier independently reloads the persisted Phase 8 result and requires it to equal the in-process result. It then verifies:

- patched output size/hash;
- evidence-manifest format;
- every manifest-listed evidence file size/hash;
- required `before-anchors.json`;
- required `after-anchors.json`;
- required `semantic-diff.json`;
- semantic-diff result path equals the manifest-verified file.

This does not rerun World Index or Semantic Diff. It verifies and reuses the proof already produced by Phase 8.

## Report contract

Format:

```text
canary-otbm-repair-sandbox-verification-v1
```

Normative schema:

```text
docs/ai-agent/OTBM_REPAIR_SANDBOX_REPORT.schema.json
```

Top-level `ok: true` means the sandbox mutation and exact before/after evidence verification completed successfully.

It does **not** mean:

- no runtime regression exists;
- no unresolved mechanic exists;
- gameplay is correct;
- the change matches designer/player intent;
- the destination is reachable;
- a real Canary server executed the mechanic;
- a physical OTClient completed a scenario.

Those remain explicit separate proof layers.

## Map Quality Gate integration

The sandbox deliberately does not auto-generate `canary-otbm-map-quality-v1`.

The Map Quality Gate requires compatible Geometry, Reachability and Script Resolution reports proving the same map source. Reachability requires explicit origins/routes and optionally reviewed floor transitions. The sandbox has no authority to invent those inputs.

A later adapter may accept explicit compatible before/after quality-gate inputs or an explicit reviewed reachability scenario. Until then, sandbox verification and static Map Quality Gate remain composable but separate contracts.

## Tests

```bash
python -m unittest tools/ai-agent/test_otbm_repair_sandbox.py -v
```

The integration test compiles the existing native scanner, creates a tiny synthetic OTBM, runs the real Phase 8 bounded patcher, verifies its real evidence manifest, runs real before/after item audits and script resolution, observes an actual `handled-directly -> unresolved` change from the patched copy, and proves the source bytes are unchanged.

No user map or production map is modified by the tests.
