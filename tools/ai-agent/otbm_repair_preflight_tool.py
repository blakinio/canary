#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from otbm_bounded_patch_types import sha256_file
from otbm_item_audit import ItemAuditError, audit_from_files as run_item_audit
from otbm_item_audit_tool import locate_scanner
from otbm_repair_preflight import (
    PreflightError,
    build_hypothetical_item_audit,
    build_preflight_report,
    parse_position,
)
from otbm_script_resolution import ScriptAuditError, audit_from_files as run_script_resolution


def _path(value: str) -> Path:
    return Path(value)


def _position_text(value: str) -> list[int]:
    try:
        parts = [int(part.strip()) for part in value.split(",")]
    except ValueError as exc:
        raise argparse.ArgumentTypeError("position must be x,y,z integers") from exc
    try:
        return list(parse_position(parts, "position"))
    except PreflightError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc


def _non_negative_int(value: str) -> int:
    try:
        result = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("value must be an integer") from exc
    if result < 0:
        raise argparse.ArgumentTypeError("value must be non-negative")
    return result


def _run_patch_anchor_scan(scanner: Path, source: Path, output: Path, timeout_seconds: int) -> dict[str, Any]:
    if timeout_seconds <= 0:
        raise PreflightError("timeout must be positive")
    try:
        completed = subprocess.run(
            [str(scanner), "--patch-anchors", str(source), str(output)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_seconds,
            check=False,
            shell=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise PreflightError(f"native patch-anchor scan timed out after {timeout_seconds} seconds") from exc
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip() or f"exit code {completed.returncode}"
        raise PreflightError(f"native patch-anchor scan failed: {detail}")
    try:
        payload = json.loads(output.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PreflightError(f"cannot read native patch-anchor report: {exc}") from exc
    if payload.get("format") != "canary-otbm-patch-anchors-native-v1":
        raise PreflightError(f"unexpected native patch-anchor format: {payload.get('format')!r}")
    if completed.stdout.strip() != f"anchors={len(payload.get('anchors', []))}":
        raise PreflightError("native patch-anchor summary does not match report anchor count")
    return payload


def _replacement_value(kind: str | None, raw: str | None) -> Any:
    if kind is None:
        if raw is not None:
            raise PreflightError("--replacement requires --operation-kind")
        return None
    if raw is None:
        raise PreflightError("--operation-kind requires --replacement")
    if kind == "set-teleport-destination":
        return _position_text(raw)
    return _non_negative_int(raw)


def _prepare_new_output(path: Path, source: Path, label: str) -> Path:
    candidate = path.expanduser()
    if candidate.is_symlink():
        raise PreflightError(f"{label} must not be a symlink")
    resolved = candidate.resolve(strict=False)
    if resolved == source:
        raise PreflightError(f"{label} must not be the source map")
    if candidate.exists():
        try:
            if os.path.samefile(candidate, source):
                raise PreflightError(f"{label} must not be a hard link to the source map")
        except OSError as exc:
            raise PreflightError(f"cannot inspect existing {label}: {exc}") from exc
        raise PreflightError(f"{label} already exists: {candidate}")
    return resolved


def _write_json(path: Path, value: Any) -> None:
    encoded = (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor: int | None = None
    created = False
    try:
        descriptor = os.open(path, flags, 0o600)
        created = True
        with os.fdopen(descriptor, "wb") as stream:
            descriptor = None
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
    except Exception:
        if descriptor is not None:
            os.close(descriptor)
        if created:
            path.unlink(missing_ok=True)
        raise


def _source_unchanged(path: Path, expected_stat: os.stat_result, expected_hash: str) -> bool:
    current = path.stat()
    return (
        current.st_size == expected_stat.st_size
        and current.st_mtime_ns == expected_stat.st_mtime_ns
        and sha256_file(path) == expected_hash
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run read-only OTBM repair preflight using the existing item audit, native patch anchors and script resolution; "
            "optionally emit a review-only Phase 8 bounded patch-plan draft."
        )
    )
    parser.add_argument("map", type=_path)
    parser.add_argument("--scanner", type=_path)
    parser.add_argument("--appearances-index", type=_path, required=True)
    parser.add_argument("--items-xml", type=_path, required=True)
    parser.add_argument("--repository-root", type=_path, default=Path("."))
    parser.add_argument("--script-root", action="append", dest="script_roots")
    parser.add_argument("--rules", type=_path)
    parser.add_argument("--review-rules", type=_path)
    parser.add_argument("--position", type=_position_text)
    parser.add_argument("--item-id", type=_non_negative_int)
    parser.add_argument("--action-id", type=_non_negative_int)
    parser.add_argument("--unique-id", type=_non_negative_int)
    parser.add_argument("--house-door-id", type=_non_negative_int)
    parser.add_argument("--teleport-destination", type=_position_text)
    parser.add_argument(
        "--operation-kind",
        choices=("set-action-id", "set-unique-id", "set-house-door-id", "set-teleport-destination"),
    )
    parser.add_argument("--replacement")
    parser.add_argument("--operation-id", default="repair-1")
    parser.add_argument("--draft-plan", type=_path)
    parser.add_argument("--output", type=_path, required=True)
    parser.add_argument("--timeout", type=int, default=3600)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        selector = {
            "position": args.position,
            "itemId": args.item_id,
            "actionId": args.action_id,
            "uniqueId": args.unique_id,
            "houseDoorId": args.house_door_id,
            "teleportDestination": args.teleport_destination,
        }
        selector = {key: value for key, value in selector.items() if value is not None}
        replacement = _replacement_value(args.operation_kind, args.replacement)
        if args.draft_plan is not None and args.operation_kind is None:
            raise PreflightError("--draft-plan requires --operation-kind and --replacement")

        map_candidate = args.map.expanduser()
        if map_candidate.is_symlink():
            raise PreflightError("map must not be a symlink")
        map_path = map_candidate.resolve(strict=True)
        if not map_path.is_file():
            raise PreflightError("map must be an existing regular file")
        scanner = locate_scanner(args.scanner).resolve(strict=True)
        repository_root = args.repository_root.expanduser().resolve(strict=True)
        output_path = _prepare_new_output(args.output, map_path, "preflight output")
        draft_plan_path = (
            _prepare_new_output(args.draft_plan, map_path, "draft plan") if args.draft_plan is not None else None
        )
        if draft_plan_path is not None and draft_plan_path == output_path:
            raise PreflightError("preflight output and draft plan must be different paths")
        source_stat_before = map_path.stat()
        source_hash_before = sha256_file(map_path)
        scanner_stat_before = scanner.stat()
        scanner_hash = sha256_file(scanner)

        with tempfile.TemporaryDirectory(prefix="otbm-repair-preflight-") as temporary:
            workspace = Path(temporary)
            item_audit_path = workspace / "item-audit.json"
            item_scan_path = workspace / "item-scan.json"
            anchor_path = workspace / "patch-anchors-native.json"
            script_resolution_path = workspace / "script-resolution.json"

            item_audit = run_item_audit(
                map_path=map_path,
                scanner=scanner,
                appearances_index_path=args.appearances_index,
                items_xml=args.items_xml,
                output=item_audit_path,
                scan_output=item_scan_path,
                include_map_hash=True,
            )
            anchor_report = _run_patch_anchor_scan(scanner, map_path, anchor_path, args.timeout)
            script_resolution = run_script_resolution(
                item_audit_path=item_audit_path,
                repository_root=repository_root,
                script_roots=args.script_roots,
                output=script_resolution_path,
                rules_path=args.rules,
                review_rules_path=args.review_rules,
            )

        if not _source_unchanged(map_path, source_stat_before, source_hash_before):
            raise PreflightError("source map changed while repair preflight was running")
        scanner_stat_after = scanner.stat()
        if (
            scanner_stat_before.st_size != scanner_stat_after.st_size
            or scanner_stat_before.st_mtime_ns != scanner_stat_after.st_mtime_ns
            or sha256_file(scanner) != scanner_hash
        ):
            raise PreflightError("native scanner changed while repair preflight was running")
        audit_map = item_audit.get("sources", {}).get("map", {})
        if audit_map.get("sha256") != source_hash_before or audit_map.get("size") != source_stat_before.st_size:
            raise PreflightError("item-audit source identity does not match the preflight source pin")
        anchor_source = anchor_report.get("source")
        if not isinstance(anchor_source, dict):
            raise PreflightError("native patch-anchor report has no source object")
        if anchor_source.get("path") != map_path.name or anchor_source.get("size") != source_stat_before.st_size:
            raise PreflightError("patch-anchor source identity does not match the preflight source pin")

        source = {
            "fileName": map_path.name,
            "sha256": source_hash_before,
            "size": source_stat_before.st_size,
            "otbmVersion": anchor_source.get("otbmVersion"),
            "itemsMajor": anchor_source.get("itemsMajor"),
            "itemsMinor": anchor_source.get("itemsMinor"),
        }
        report = build_preflight_report(
            item_audit=item_audit,
            anchor_report=anchor_report,
            script_resolution=script_resolution,
            selector=selector,
            source=source,
            operation_kind=args.operation_kind,
            replacement=replacement,
            operation_id=args.operation_id,
        )
        if report["draftPlan"] is not None and args.operation_kind is not None:
            audit_index = int(report["candidates"][0]["auditIndex"])
            hypothetical_item_audit = build_hypothetical_item_audit(
                item_audit=item_audit,
                audit_index=audit_index,
                operation_kind=args.operation_kind,
                replacement=replacement,
            )
            with tempfile.TemporaryDirectory(prefix="otbm-repair-preflight-after-") as after_temporary:
                after_workspace = Path(after_temporary)
                hypothetical_item_audit_path = after_workspace / "item-audit-hypothetical.json"
                hypothetical_resolution_path = after_workspace / "script-resolution-hypothetical.json"
                _write_json(hypothetical_item_audit_path, hypothetical_item_audit)
                hypothetical_resolution = run_script_resolution(
                    item_audit_path=hypothetical_item_audit_path,
                    repository_root=repository_root,
                    script_roots=args.script_roots,
                    output=hypothetical_resolution_path,
                    rules_path=args.rules,
                    review_rules_path=args.review_rules,
                )
            after_placements = [
                row
                for row in hypothetical_resolution.get("placements", [])
                if isinstance(row, dict) and row.get("index") == audit_index
            ]
            if len(after_placements) != 1:
                raise PreflightError("hypothetical replacement script resolution did not preserve the selected placement index")
            before_status = str(report["candidates"][0]["scriptResolution"].get("status", "unknown"))
            after_status = str(after_placements[0].get("status", "unknown"))
            report["replacementScriptResolution"] = {
                "hypothetical": True,
                "beforeStatus": before_status,
                "afterStatus": after_status,
                "runtimeResolutionChanged": before_status != after_status,
                "placement": after_placements[0],
                "summary": hypothetical_resolution.get("summary"),
                "note": "This is static hypothetical resolver evidence only; no OTBM was modified and gameplay correctness is not proven.",
            }
        else:
            report["replacementScriptResolution"] = None
        report["evidence"] = {
            "itemAudit": {"format": item_audit.get("format"), "summary": item_audit.get("summary")},
            "patchAnchors": {
                "format": anchor_report.get("format"),
                "anchors": len(anchor_report.get("anchors", [])),
                "scannerSha256": scanner_hash,
            },
            "scriptResolution": {
                "format": script_resolution.get("format"),
                "summary": script_resolution.get("summary"),
                "scriptRoots": script_resolution.get("sources", {}).get("scriptRoots"),
            },
        }

        if not _source_unchanged(map_path, source_stat_before, source_hash_before):
            raise PreflightError("source map changed before repair preflight evidence publication")

        published: list[Path] = []
        try:
            if draft_plan_path is not None and report["draftPlan"] is not None:
                _write_json(draft_plan_path, report["draftPlan"])
                published.append(draft_plan_path)
            _write_json(output_path, report)
            published.append(output_path)
        except Exception:
            for path in reversed(published):
                path.unlink(missing_ok=True)
            raise

        summary = report["summary"]
        json.dump(
            {
                "ok": report["ok"],
                "matchedCandidates": summary["matchedCandidates"],
                "draftPlanReady": summary["draftPlanReady"],
                "runtimeUnresolvedCandidates": summary["runtimeUnresolvedCandidates"],
                "conflictingCandidates": summary["conflictingCandidates"],
                "output": str(output_path),
                "draftPlan": str(draft_plan_path) if draft_plan_path and report["draftPlan"] else None,
            },
            sys.stdout,
            indent=2,
            sort_keys=True,
        )
        sys.stdout.write("\n")
        if not report["ok"]:
            return 2
        if args.operation_kind is not None and not summary["draftPlanReady"]:
            return 2
        return 0
    except (FileNotFoundError, OSError, ValueError, ItemAuditError, ScriptAuditError, PreflightError) as exc:
        parser.error(str(exc))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
