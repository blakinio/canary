#!/usr/bin/env python3
from __future__ import annotations

import os
import re
from pathlib import Path

HEAD_SHA = os.environ["PR_HEAD_SHA"]


def patch_source() -> None:
    path = Path("tools/e2e/stability_certification.py")
    content = path.read_text(encoding="utf-8")
    old = '''    for item in normalized:
        source = item["source"]
        path = root_map[source["root_id"]] / source["path"]
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(payload, Mapping):
                raise StabilityCertificationError(
                    "result envelope root must be an object"
                )
            envelopes.append(
                normalize_envelope(
                    payload,
                    root_id=source["root_id"],
                    relative_path=source["path"],
                )
            )
        except (OSError, json.JSONDecodeError, StabilityCertificationError) as exc:
            invalid.append(
                {
                    "source": dict(source),
                    "error": str(exc),
                }
            )
'''
    new = '''    for item in normalized:
        source = item["source"]
        root = root_map[source["root_id"]]
        path = root / source["path"]
        try:
            resolved = path.resolve()
            try:
                resolved.relative_to(root)
            except ValueError as exc:
                raise StabilityCertificationError(
                    "result.json resolves outside the evidence root"
                ) from exc
            payload = json.loads(resolved.read_text(encoding="utf-8"))
            if not isinstance(payload, Mapping):
                raise StabilityCertificationError(
                    "result envelope root must be an object"
                )
            envelopes.append(
                normalize_envelope(
                    payload,
                    root_id=source["root_id"],
                    relative_path=source["path"],
                )
            )
        except OSError as exc:
            reason = exc.strerror or exc.__class__.__name__
            invalid.append(
                {
                    "source": dict(source),
                    "error": f"cannot read result evidence: {reason}",
                }
            )
        except json.JSONDecodeError as exc:
            invalid.append(
                {
                    "source": dict(source),
                    "error": (
                        f"invalid JSON at line {exc.lineno}, "
                        f"column {exc.colno}: {exc.msg}"
                    ),
                }
            )
        except StabilityCertificationError as exc:
            invalid.append(
                {
                    "source": dict(source),
                    "error": str(exc),
                }
            )
'''
    if old not in content:
        raise RuntimeError("expected stability discovery block is missing")
    path.write_text(content.replace(old, new, 1), encoding="utf-8")


def patch_catalog() -> None:
    path = Path("docs/agents/MODULE_CATALOG.md")
    content = path.read_text(encoding="utf-8")
    if "Universal OTS E2E factual stability certification" in content:
        return
    row = "| Universal OTS E2E factual stability certification | active (#912) | `canary-universal-e2e-stability-certification-v1`, schema version 1: deterministic read-only classification of explicitly supplied retained schema-v3 result attempts into exact comparable scenario/server/client/datapack/tier cells with an explicit minimum run count, clean-pass ratio, failure classes, first-divergence frequency, cleanup failures and nearest-rank duration distribution; mixed results such as 9/10 remain `unstable` | `tools/e2e/stability_certification.py`, `tests/e2e/test_stability_certification.py`, `docs/e2e/E2E_STABILITY_CERTIFICATION.md`, schema and `.github/workflows/e2e-stability-certification.yml`, task `CAN-20260725-e2e-qri-022-stability-certification` | Reuse the QRI-004 evidence discovery/normalization boundary, schema-v3 result envelopes and complete cleanup certification. Every attempt remains visible; duplicate identities, missing provenance and historical success without cleanup proof block certification. This layer does not run or retry scenarios, download artifacts, set retention/schedules or prove a physical baseline by itself. |"
    lines = content.splitlines()
    index = next(
        i
        for i, line in enumerate(lines)
        if line.startswith("| Universal OTS E2E factual coverage dashboard |")
    )
    lines.insert(index + 1, row)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def patch_program() -> None:
    path = Path("docs/agents/programs/E2E_AUTOMATION_PROGRAM.md")
    content = path.read_text(encoding="utf-8")
    content = re.sub(
        r"^updated: .*$",
        "updated: 2026-07-25T10:40:00+02:00",
        content,
        count=1,
        flags=re.MULTILINE,
    )
    content = re.sub(
        r"^last_verified_commit: .*$",
        f'last_verified_commit: "{HEAD_SHA}"',
        content,
        count=1,
        flags=re.MULTILINE,
    )
    if "| Factual stability certification |" not in content:
        rows = [
            "| Factual coverage dashboard | merged | PR #885; lifecycle archive #900 | reuse `canary-universal-e2e-coverage-dashboard-v1` schema v1 over explicit retained evidence; registration never proves execution |",
            "| Factual stability certification | active contract/tooling | PR #912 | reuse `canary-universal-e2e-stability-certification-v1` schema v1; first real repeated-run physical baseline remains separate evidence |",
        ]
        lines = content.splitlines()
        index = next(
            i
            for i, line in enumerate(lines)
            if line.startswith("| Resource cleanup certification |")
        )
        lines[index + 1 : index + 1] = rows
        content = "\n".join(lines) + "\n"
    old = '''Select one package at a time after live dependency and ownership preflight. QRI-001, QRI-002, QRI-003, QRI-005 and QRI-006 are delivered. Current recommendation:

1. `E2E-QRI-004` — factual M0-M5 plus quality-dimension coverage dashboard consuming the merged result and cleanup contracts;
2. `E2E-QRI-022` — flake/stability certification after the selected scenarios are stable enough to measure.

Later waves cover transactional/resilience correctness (`QRI-008` through `014`), test intelligence (`QRI-015` through `021`) and operational/release confidence (`QRI-023` through `028`).
'''
    new = '''Select one package at a time after live dependency and ownership preflight. QRI-001 through QRI-006, including the factual QRI-004 dashboard, are delivered. Current recommendation:

1. complete active `E2E-QRI-022` PR #912 as a deterministic retained-evidence certification contract without adding execution, retry or scheduling;
2. after the contract merges, select exactly one stable physical scenario and explicit retained artifact population for the first repeated-run baseline;
3. keep artifact collection/retention and any nightly execution seam separate until that factual baseline proves the need.

Later waves cover transactional/resilience correctness (`QRI-008` through `014`), test intelligence (`QRI-015` through `021`) and operational/release confidence (`QRI-023` through `028`).
'''
    if old not in content:
        raise RuntimeError("expected programme recommendation block is missing")
    path.write_text(content.replace(old, new, 1), encoding="utf-8")


def patch_changelog() -> None:
    path = Path("docs/agents/CHANGELOG.md")
    content = path.read_text(encoding="utf-8")
    if "canary-universal-e2e-stability-certification-v1" in content:
        return
    bullet = "- Adds the active `canary-universal-e2e-stability-certification-v1` schema-version-1 contract in PR #912 as a deterministic read-only consumer of explicit retained schema-v3 Universal E2E result roots. Exact scenario/server/client/datapack/tier cells preserve every attempt and classify only complete minimum-sized clean-pass sets as `pass`; mixed evidence such as 9/10 is `unstable`, all failures are `fail`, insufficient evidence is `not-evaluated`, and missing provenance, duplicate identities or historical success without cleanup proof are `blocked`. The tool reports exact failure/divergence and nearest-rank duration distributions, adds no scenario runner/retry/downloader/retention/schedule and does not claim a physical stability baseline from contract tests.\n"
    path.write_text(
        content.replace("## Unreleased\n\n", "## Unreleased\n\n" + bullet, 1),
        encoding="utf-8",
    )


def patch_task() -> None:
    path = Path(
        "docs/agents/tasks/active/CAN-20260725-e2e-qri-022-stability-certification.md"
    )
    content = path.read_text(encoding="utf-8")
    content = content.replace(
        "    - .github/workflows/e2e-qri-022-integration.yml\n",
        "    - .github/workflows/e2e-stability-certification.yml\n",
    )
    content = content.replace(
        "  - .github/workflows/e2e-qri-022-integration.yml\n",
        "  - .github/workflows/e2e-stability-certification.yml\n",
    )
    content = content.replace(
        "- [ ] Focused tests, bytecode compilation and JSON schema parsing pass against canonical repository modules.",
        "- [x] Focused tests, bytecode compilation and JSON schema parsing pass against canonical repository modules.",
    )
    content = content.replace(
        "- [ ] Catalogue/program/changelog entries are updated narrowly.",
        "- [x] Catalogue/program/changelog entries are updated narrowly.",
    )
    content = content.replace(
        "- [ ] The temporary checkout validation/integration workflow removes itself and is absent from final diff.",
        "- [x] Failed temporary integration experiments are removed; the permanent PR-only focused validation workflow remains.",
    )
    content = re.sub(
        r'^updated_at: .*$',
        "updated_at: 2026-07-25T10:40:00+02:00",
        content,
        count=1,
        flags=re.MULTILINE,
    )
    content = re.sub(
        r'^head: [0-9a-f]{40}$', HEAD_SHA, content, count=1, flags=re.MULTILINE
    )
    content = re.sub(
        r'^last_verified_commit: ".*"$',
        f'last_verified_commit: "{HEAD_SHA}"',
        content,
        count=1,
        flags=re.MULTILINE,
    )
    content = content.replace(
        "  - Focused test outcome against the repository's actual canonical coverage/result/cleanup modules until the checkout workflow completes.\n",
        "",
    )
    anchor = "  - The current implementation, focused tests, strict schema and operator documentation are committed on the task branch.\n"
    proof = "  - Universal E2E Stability Certification run 30150829220 passed bytecode compilation, all focused canonical-module tests and strict schema JSON parsing.\n"
    if proof not in content:
        content = content.replace(anchor, anchor + proof)
    content = content.replace(
        "  - docs/e2e/E2E_STABILITY_CERTIFICATION.schema.json\nvalidation:",
        "  - docs/e2e/E2E_STABILITY_CERTIFICATION.schema.json\n  - .github/workflows/e2e-stability-certification.yml\n  - docs/agents/MODULE_CATALOG.md\n  - docs/agents/CHANGELOG.md\n  - docs/agents/programs/E2E_AUTOMATION_PROGRAM.md\nvalidation:",
    )
    validation_anchor = "  - command: same-repository draft PR safety check\n    result: PASS\n    evidence: PR #912 targets blakinio/canary:main from feat/e2e-qri-022-stability-certification\n"
    validation = "  - command: Universal E2E Stability Certification workflow run 30150829220\n    result: PASS\n    evidence: bytecode compilation, focused canonical-module tests and strict schema JSON parsing all passed\n"
    if validation not in content:
        content = content.replace(validation_anchor, validation_anchor + validation)
    content = re.sub(
        r'^next_action: .*$',
        "next_action: Review the exact PR #912 diff and all current-head workflow evidence, repair only evidenced defects, then apply and pass the exact final-head gate without claiming a physical repeated-run baseline.",
        content,
        count=1,
        flags=re.MULTILINE,
    )
    path.write_text(content, encoding="utf-8")


patch_source()
patch_catalog()
patch_program()
patch_changelog()
patch_task()
