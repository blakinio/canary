from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from tibia_client_reference_evidence_gateway import (
    ClientReferenceEvidenceGatewayError,
    build_evidence_plan,
    execute_evidence_plan,
    load_bindings,
    normalize_bindings,
    sha256_path,
    source_paths_for_plan,
    write_report,
)


def _safe_relative_output(root: Path, value: Path) -> Path:
    if value.is_absolute() or not value.parts or any(
        part in {"", ".", ".."} for part in value.parts
    ):
        raise ClientReferenceEvidenceGatewayError(
            "output must be a safe non-empty path relative to the bindings directory"
        )
    candidate = root / value
    current = root
    for part in value.parts[:-1]:
        current = current / part
        if current.exists() and current.is_symlink():
            raise ClientReferenceEvidenceGatewayError(
                f"output parent must not be a symlink: {current}"
            )
    if candidate.is_symlink():
        raise ClientReferenceEvidenceGatewayError(
            f"output must not be a symlink: {candidate}"
        )
    resolved = candidate.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ClientReferenceEvidenceGatewayError(
            f"output escapes bindings directory: {value}"
        ) from exc
    return resolved


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Resolve one exact reviewed Tibia client-reference binding to compact "
            "evidence through the canonical OTBM QA-018 gateway."
        )
    )
    parser.add_argument(
        "--bindings", type=Path, required=True, help="Reviewed TCR evidence bindings JSON"
    )
    parser.add_argument(
        "--binding-id", required=True, help="Exact reviewed binding ID"
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Safe output path relative to the bindings directory",
    )
    parser.add_argument(
        "--plan-only",
        action="store_true",
        help="Emit the exact normalized QA-018 manifest without reading source reports",
    )
    parser.add_argument(
        "--overwrite", action="store_true", help="Atomically replace an existing output"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        raw_path = args.bindings.expanduser()
        if raw_path.is_symlink():
            raise ClientReferenceEvidenceGatewayError(
                f"bindings input must not be a symlink: {args.bindings}"
            )
        bindings_path = raw_path.resolve(strict=True)
        bindings = normalize_bindings(load_bindings(bindings_path))
        plan = build_evidence_plan(
            bindings,
            args.binding_id,
            bindings_file_sha256=sha256_path(bindings_path),
        )
        root = bindings_path.parent
        output_path = _safe_relative_output(root, args.output)
        if output_path == bindings_path:
            raise ClientReferenceEvidenceGatewayError(
                "output must not collide with bindings input"
            )
        if output_path in source_paths_for_plan(bindings_path, plan):
            raise ClientReferenceEvidenceGatewayError(
                "output must not collide with a selected QA-018 evidence source"
            )
        report = (
            plan
            if args.plan_only
            else execute_evidence_plan(bindings_path, plan)
        )
        write_report(output_path, report, overwrite=args.overwrite)
    except (
        OSError,
        UnicodeError,
        json.JSONDecodeError,
        ClientReferenceEvidenceGatewayError,
    ) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(
        json.dumps(
            {
                "format": report["format"],
                "mode": report["mode"],
                "bindingId": report["bindingId"],
                "kind": report["kind"],
                "reportSha256": report["reportSha256"],
                "evidenceBundleSha256": report["evidenceBundleSha256"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
