from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from otbm_runtime_incident_evidence_bridge import (
    RuntimeIncidentEvidenceBridgeError,
    build_incident_evidence_plan,
    execute_incident_evidence_plan,
    normalize_bindings,
    sha256_path,
    source_paths_for_plan,
    write_report,
)


def _load_bindings(path: Path) -> dict:
    candidate = path.expanduser()
    if candidate.is_symlink():
        raise RuntimeIncidentEvidenceBridgeError(f"bindings input must not be a symlink: {path}")
    source = candidate.resolve(strict=True)
    if not source.is_file():
        raise RuntimeIncidentEvidenceBridgeError(f"bindings input must be a regular file: {source}")
    try:
        document = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise RuntimeIncidentEvidenceBridgeError(f"cannot read bindings input {source}: {exc}") from exc
    if not isinstance(document, dict):
        raise RuntimeIncidentEvidenceBridgeError("bindings input must contain a JSON object")
    return document


def _parse_position(value: str) -> list[int]:
    parts = value.split(",")
    if len(parts) != 3:
        raise argparse.ArgumentTypeError("position must be X,Y,Z")
    try:
        return [int(part, 10) for part in parts]
    except ValueError as exc:
        raise argparse.ArgumentTypeError("position must contain decimal integers X,Y,Z") from exc


def _selector_from_args(args: argparse.Namespace) -> dict:
    if args.position is not None:
        return {"kind": "position", "value": args.position}
    for attribute, kind in (
        ("transition_id", "transition-id"),
        ("interaction_id", "interaction-id"),
        ("landmark_id", "landmark-id"),
        ("route_id", "route-id"),
        ("preflight_reference", "preflight-reference"),
    ):
        value = getattr(args, attribute)
        if value is not None:
            return {"kind": kind, "value": value}
    raise RuntimeIncidentEvidenceBridgeError("exactly one incident selector is required")


def _safe_relative_output(root: Path, value: Path) -> Path:
    if value.is_absolute() or not value.parts or any(part in {"", ".", ".."} for part in value.parts):
        raise RuntimeIncidentEvidenceBridgeError("output must be a safe non-empty path relative to the bindings directory")
    candidate = root / value
    current = root
    for part in value.parts[:-1]:
        current = current / part
        if current.exists() and current.is_symlink():
            raise RuntimeIncidentEvidenceBridgeError(f"output parent must not be a symlink: {current}")
    if candidate.is_symlink():
        raise RuntimeIncidentEvidenceBridgeError(f"output must not be a symlink: {candidate}")
    resolved = candidate.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise RuntimeIncidentEvidenceBridgeError(f"output escapes bindings directory: {value}") from exc
    return resolved


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Resolve one reviewed runtime-incident selector to compact exact OTBM evidence through the canonical QA-018 gateway."
    )
    parser.add_argument("--bindings", type=Path, required=True, help="Reviewed incident-evidence bindings JSON")
    selectors = parser.add_mutually_exclusive_group(required=True)
    selectors.add_argument("--position", type=_parse_position, help="Exact OTBM position X,Y,Z")
    selectors.add_argument("--transition-id", help="Exact reviewed transition ID")
    selectors.add_argument("--interaction-id", help="Exact reviewed route-interaction ID")
    selectors.add_argument("--landmark-id", help="Exact reviewed semantic landmark ID")
    selectors.add_argument("--route-id", help="Exact reviewed route ID")
    selectors.add_argument("--preflight-reference", help="Exact reviewed preflight reference")
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Safe output path relative to the bindings directory",
    )
    parser.add_argument(
        "--plan-only",
        action="store_true",
        help="Emit the exact normalized QA-018 manifest without reading evidence source files",
    )
    parser.add_argument("--overwrite", action="store_true", help="Atomically replace an existing output")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        raw_bindings = args.bindings.expanduser()
        if raw_bindings.is_symlink():
            raise RuntimeIncidentEvidenceBridgeError(f"bindings input must not be a symlink: {args.bindings}")
        bindings_path = raw_bindings.resolve(strict=True)
        bindings = _load_bindings(bindings_path)
        normalized = normalize_bindings(bindings)
        selector = _selector_from_args(args)
        plan = build_incident_evidence_plan(
            normalized,
            selector,
            bindings_file_sha256=sha256_path(bindings_path),
        )
        root = bindings_path.parent
        output_path = _safe_relative_output(root, args.output)
        if output_path == bindings_path:
            raise RuntimeIncidentEvidenceBridgeError("output must not collide with bindings input")
        source_paths = source_paths_for_plan(bindings_path, plan)
        if output_path in source_paths:
            raise RuntimeIncidentEvidenceBridgeError("output must not collide with a selected QA-018 evidence source")
        report = plan if args.plan_only else execute_incident_evidence_plan(bindings_path, plan)
        write_report(output_path, report, overwrite=args.overwrite)
    except (OSError, UnicodeError, json.JSONDecodeError, RuntimeIncidentEvidenceBridgeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(
        json.dumps(
            {
                "format": report["format"],
                "mode": report["mode"],
                "bindingId": report["bindingId"],
                "reportSha256": report["reportSha256"],
                "evidenceBundleSha256": report["evidenceBundleSha256"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
