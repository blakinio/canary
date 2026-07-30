from pathlib import Path

FEATURE_HEAD = "38826ff475c4631ee42c7fd8dc2e246dedab2a25"
MERGE_SHA = "34a2a3750f20c318ecc07aa7407ca0b9a9311834"
READY_CI = "30522402785"
AT = "2026-07-30T09:45:00+02:00"


def one(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


active = Path("docs/agents/tasks/active/CAN-20260730-tcr-010-evidence-gateway.md")
archive = Path("docs/agents/tasks/archive/CAN-20260730-tcr-010-evidence-gateway.md")
raw = active.read_text(encoding="utf-8")
checkpoint = raw.index("## Context checkpoint")
text = raw[:checkpoint]
text = one(text, "status: ready", "status: merged", "task status")
text = one(
    text,
    "branch: feat/CAN-20260730-tcr-010-evidence-gateway",
    "branch: main",
    "task branch",
)
text = one(
    text,
    "updated: 2026-07-30T09:10:00+02:00",
    f"updated: {AT}",
    "task updated",
)
text = one(
    text,
    'last_verified_commit: "193428b3e6a42308ceb684cf271b568609de4aeb"',
    f'last_verified_commit: "{MERGE_SHA}"',
    "task verified commit",
)
text = one(
    text,
    "    - docs/agents/tasks/active/CAN-20260730-tcr-010-evidence-gateway.md",
    "    - docs/agents/tasks/archive/CAN-20260730-tcr-010-evidence-gateway.md",
    "task ownership path",
)
text = one(
    text,
    "- [ ] Pass exact-final-head CI, merge and archive.",
    "- [x] Pass exact-final-head CI, merge and archive.",
    "task final criterion",
)
text = text + f'''# Feature result

- Feature PR: `#1027`.
- Exact final head: `{FEATURE_HEAD}`.
- Squash merge: `{MERGE_SHA}`.
- Readiness/final-gate CI: run `{READY_CI}`, conclusion `success` including Linux release/debug, Docker image/quickstart and `Required`.
- Public formats: `canary-tibia-client-reference-evidence-bindings-v1` and `canary-tibia-client-reference-evidence-gateway-v1`.
- Focused suite: 19 tests; canonical QA-018 regression suite passed.
- No proprietary input/report, OTBM, datapack, runtime, E2E, acceptance or mutation authority was added.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: {AT}
head: {MERGE_SHA}
branch: main
pr: 1027
status: merged
context_routes:
  - agent-governance
  - otbm
  - real-tibia-parity
owned_paths:
  - docs/agents/tasks/archive/CAN-20260730-tcr-010-evidence-gateway.md
  - tools/ai-agent/tibia_client_reference_evidence_gateway.py
  - tools/ai-agent/tibia_client_reference_evidence_gateway_tool.py
  - docs/ai-agent/TIBIA_CLIENT_REFERENCE_EVIDENCE_GATEWAY.md
proven:
  - Exact reviewed house, content, proficiency and drift bindings delegate extraction to canonical QA-018.
  - Paths, SHA-256, formats, pointers, extract bounds and output confinement fail closed.
  - Feature head {FEATURE_HEAD} and readiness run {READY_CI} passed all required checks.
  - PR 1027 squash-merged as {MERGE_SHA} with no reviews, comments, threads or base drift.
derived:
  - TCR-011 is dependency-ready but remains a separate read-only routing package.
unknown: []
conflicts: []
first_failure:
  marker: TCR010_SCHEMA_AND_GLOBAL_SUITE_COMPATIBILITY
  evidence: Truncated schema and optional jsonschema import failures were repaired before final gate.
rejected_hypotheses:
  - Add a second parser or generic evidence gateway.
  - Grant acceptance, E2E, routing execution or mutation authority.
changed_paths:
  - docs/agents/tasks/archive/CAN-20260730-tcr-010-evidence-gateway.md
  - docs/agents/programs/OTBM_TIBIA_CLIENT_REFERENCE_PROGRAM.md
  - docs/agents/MODULE_CATALOG.md
validation:
  - command: readiness and ci:final-gate run {READY_CI}
    result: PASS
    evidence: Linux release/debug, Docker image/quickstart and Required completed success on {FEATURE_HEAD}.
blockers: []
next_action: Start one bounded TCR-011 Reviewed Adoption Router task; do not implement OWA-003 before TCR-011 is stable/merged.
```
'''
archive.parent.mkdir(parents=True, exist_ok=True)
archive.write_text(text, encoding="utf-8")
active.unlink()

programme = Path("docs/agents/programs/OTBM_TIBIA_CLIENT_REFERENCE_PROGRAM.md")
text = programme.read_text(encoding="utf-8")
text = one(
    text,
    "| TCR-010 | Compact Evidence Gateway Integration | active/in-review | `canary-tibia-client-reference-evidence-bindings-v1` + `canary-tibia-client-reference-evidence-gateway-v1`; draft PR #1027; delegates to QA-018 | TCR-005, TCR-006, TCR-007, TCR-009 stable/merged | low | Complete exact-head validation and merge. Reviewed-binding transport only; no parsing, reinterpretation, mutation, E2E, acceptance or routing. |",
    "| TCR-010 | Compact Evidence Gateway Integration | merged | `canary-tibia-client-reference-evidence-bindings-v1` + `canary-tibia-client-reference-evidence-gateway-v1`; PR #1027; merge `34a2a375...`; delegates to QA-018 | TCR-005, TCR-006, TCR-007, TCR-009 stable/merged | low | Complete. Exact reviewed binding transport is stable/merged; no parsing, reinterpretation, mutation, E2E, acceptance or routing authority. |",
    "TCR-010 queue row",
)
text = one(
    text,
    "| TCR-011 | Reviewed Adoption Router | blocked-by-TCR-010 | TCR-005/006/007/009 are stable; TCR-010 remains in review | TCR-005, TCR-006, TCR-007, TCR-009, TCR-010 stable/merged | medium | Start only after TCR-010 merges and archives. No executor, approval generation or mutation authority. |",
    "| TCR-011 | Reviewed Adoption Router | ready | TCR-005/006/007/009/010 are stable/merged | TCR-005, TCR-006, TCR-007, TCR-009, TCR-010 stable/merged | medium | Start one bounded read-only routing task. Classify exact reviewed findings to existing owners/capabilities; no executor, approval generation or mutation authority. |",
    "TCR-011 queue row",
)
text = one(
    text,
    "TCR-001 through TCR-007 and TCR-009 stabilize these reference, resolver, correlation and drift contracts. TCR-010 PR #1027 adds reviewed gateway bindings over QA-018 and remains in review until merge:",
    "TCR-001 through TCR-007 and TCR-009 through TCR-010 stabilize these reference, resolver, correlation, drift and compact gateway contracts:",
    "stable contract introduction",
)
text = one(
    text,
    "TCR-010 PR #1027 adds exact reviewed binding IDs for one bounded house, content, proficiency or drift extract and delegates path, SHA-256, format, JSON Pointer and serialized-size enforcement to QA-018. It adds no parser, semantic reinterpretation, E2E, acceptance or routing authority and remains non-stable until merge.",
    "The client-reference evidence binding and gateway contracts are `stable/merged` as of PR #1027 / merge `34a2a3750f20c318ecc07aa7407ca0b9a9311834`. They expose one exact reviewed house, content, proficiency or drift extract through QA-018 path, SHA-256, format, JSON Pointer and serialized-size enforcement. They add no parser, semantic reinterpretation, E2E, acceptance or routing authority.",
    "TCR-010 contract status",
)
text = one(
    text,
    "TCR-008 remains `optional/deferred-no-concrete-use-case`. TCR-009 is stable/merged and owner request `RTREQ-TCR-ITEM-DEFINITIONS-0002` is consumed. TCR-010 is active in PR #1027 and is not stable until merge; TCR-011 remains blocked only by stable/merged TCR-010.",
    "TCR-008 remains `optional/deferred-no-concrete-use-case`. TCR-009 and TCR-010 are stable/merged. TCR-011 is dependency-ready and remains the only required TCR package before OWA-003.",
    "programme disposition",
)
text = one(
    text,
    "OWA-003 may consume stable TCR-001 through TCR-007 and TCR-009 contracts only within their exact provenance boundaries. TCR-010 remains non-consumable until PR #1027 merges and TCR-011 remains unavailable. No consumer may infer map authority, `staticmapdata.object_id` equivalence, unreviewed proficiency-ID equivalence, gameplay/runtime parity or mutation authority.",
    "OWA-003 may consume stable TCR-001 through TCR-010 contracts only within their exact provenance boundaries, but implementation remains blocked until TCR-011 is stable/merged. No consumer may infer map authority, `staticmapdata.object_id` equivalence, unreviewed proficiency-ID equivalence, gameplay/runtime parity or mutation authority.",
    "OWA boundary",
)
text = one(
    text,
    "In-review public formats in PR #1027:",
    "Stable public formats:",
    "TCR-010 format status",
)
text = one(
    text,
    "- TCR-010 is active in draft PR `#1027` and remains non-stable until exact-final-head merge.",
    "- TCR-010 feature PR `#1027` merged as `34a2a3750f20c318ecc07aa7407ca0b9a9311834` after readiness/final-gate run `30522402785` passed.",
    "lifecycle disposition",
)
text = one(
    text,
    "# Exact next action after TCR-010 implementation\n\nComplete PR #1027 through exact-final-head validation and squash merge, then archive its task and mark TCR-011 ready. Do not start TCR-011 or OWA-003 before TCR-010 is stable/merged.\n\n# Handoff\n\nContinue from the active TCR-010 checkpoint and live PR #1027. Preserve QA-018 as the sole extractor, exact reviewed binding IDs, the four stable source formats, proprietary-input retention outside Git and all identifier/runtime/gameplay/mutation boundaries.\n",
    "# Exact next action after TCR-010 merge\n\nStart one bounded TCR-011 Reviewed Adoption Router task. Preserve exact finding references, deterministic existing-owner/capability classification and unsupported outcomes. Do not execute writers, generate approval, deploy, claim gameplay parity or start OWA-003 before TCR-011 is stable/merged.\n\n# Handoff\n\nContinue from `main` merge `34a2a3750f20c318ecc07aa7407ca0b9a9311834` and the archived TCR-010 checkpoint. Reuse TCR-005/006/007/009/010 stable contracts and existing repair/subsystem owners; do not add a second router, executor or mutation path.\n",
    "next action and handoff",
)
programme.write_text(text, encoding="utf-8")

catalogue = Path("docs/agents/MODULE_CATALOG.md")
lines = catalogue.read_text(encoding="utf-8").splitlines()
matches = [
    i
    for i, line in enumerate(lines)
    if line.startswith("| OTBM Tibia client reference architecture |")
]
if len(matches) != 1:
    raise SystemExit(f"catalogue row: expected one match, found {len(matches)}")
lines[matches[0]] = (
    "| OTBM Tibia client reference architecture | active programme; TCR-000..010 stable/merged, TCR-008 optional/deferred, TCR-011 ready | "
    "Exact manifest, StaticData, StaticMapData, proficiency, resolver/parity/correlation, drift and reviewed QA-018 gateway contracts plus the adoption-router queue | "
    "`docs/agents/programs/OTBM_TIBIA_CLIENT_REFERENCE_PROGRAM.md`, `docs/ai-agent/OTBM_TIBIA_CLIENT_REFERENCE_ARCHITECTURE.md`, "
    "`tools/ai-agent/tibia_*reference*.py`, `tools/ai-agent/tibia_client_reference_evidence_gateway*.py` | "
    "Reuse stable TCR producers and QA-018. Start TCR-011 as a separate deterministic read-only router; no parser, executor, approval generation, mutation, E2E or gameplay authority. OWA-003 remains blocked until TCR-011 is stable/merged. |"
)
catalogue.write_text("\n".join(lines) + "\n", encoding="utf-8")
