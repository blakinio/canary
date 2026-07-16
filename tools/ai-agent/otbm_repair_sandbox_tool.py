#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, Mapping

from otbm_bounded_patch import apply_bounded_patch
from otbm_bounded_patch_types import BoundedPatchError, load_plan, sha256_file
from otbm_item_audit import ItemAuditError, audit_from_files as run_item_audit
from otbm_item_audit_tool import locate_scanner
from otbm_repair_preflight import PreflightError
from otbm_repair_preflight_tool import _build_input_pins, _file_pin
from otbm_repair_sandbox import (
    RepairSandboxError,
    build_verification_report,
    validate_phase8_result,
    verify_operation,
)
from otbm_script_resolution import ScriptAuditError, audit_from_files as run_script_resolution

EVIDENCE_FORMAT = "canary-otbm-bounded-patch-evidence-v1"
REQUIRED_EVIDENCE_FILES = {
    "before-anchors.json",
    "after-anchors.json",
    "semantic-diff.json",
}


def _path(value: str) -> Path:
    return Path(value)


def _resolve_file(path: Path, label: str, *, executable: bool = False) -> Path:
    candidate = path.expanduser()
    if candidate.is_symlink():
        raise RepairSandboxError(f"{label} must not be a symlink")
    resolved = candidate.resolve(strict=True)
    if not resolved.is_file():
        raise RepairSandboxError(f"{label} must be an existing regular file")
    if executable and not os.access(resolved, os.X_OK):
        raise RepairSandboxError(f"{label} must be executable")
    return resolved


def _resolve_directory(path: Path, label: str) -> Path:
    candidate = path.expanduser()
    if candidate.is_symlink():
        raise RepairSandboxError(f"{label} must not be a symlink")
    resolved = candidate.resolve(strict=True)
    if not resolved.is_dir():
        raise RepairSandboxError(f"{label} must be an existing directory")
    return resolved


def _prepare_artifact_root(path: Path) -> Path:
    candidate = path.expanduser()
    if candidate.is_symlink():
        raise RepairSandboxError("artifact root must not be a symlink")
    candidate.mkdir(parents=True, exist_ok=True)
    resolved = candidate.resolve(strict=True)
    if not resolved.is_dir():
        raise RepairSandboxError("artifact root must be a directory")
    return resolved


def _confined_relative(root: Path, relative: Path, label: str, *, must_be_new: bool = False) -> Path:
    if relative.is_absolute() or ".." in relative.parts or not relative.parts:
        raise RepairSandboxError(f"{label} must be a relative path below the artifact root")
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise RepairSandboxError(f"{label} must not traverse symlinks")
    resolved = (root / relative).resolve(strict=False)
    if resolved != root and root not in resolved.parents:
        raise RepairSandboxError(f"{label} escapes the artifact root")
    if must_be_new and resolved.exists():
        raise RepairSandboxError(f"{label} already exists: {relative}")
    return resolved


def _resolve_result_path(root: Path, value: Any, label: str, *, directory: bool = False) -> Path:
    if not isinstance(value, str) or not value:
        raise RepairSandboxError(f"{label} must be a non-empty artifact-root-relative path")
    path = _confined_relative(root, Path(value), label)
    if path.is_symlink():
        raise RepairSandboxError(f"{label} must not be a symlink")
    if directory:
        if not path.is_dir():
            raise RepairSandboxError(f"{label} must resolve to an existing directory")
    elif not path.is_file():
        raise RepairSandboxError(f"{label} must resolve to an existing regular file")
    return path


def _load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RepairSandboxError(f"cannot read {label}: {exc}") from exc
    if not isinstance(value, dict):
        raise RepairSandboxError(f"{label} must contain one JSON object")
    return value


def _verify_phase8_artifacts(root: Path, result: Mapping[str, Any]) -> tuple[Path, dict[str, Path], dict[str, Any]]:
    output = result.get("output")
    evidence = result.get("evidence")
    if not isinstance(output, Mapping) or not isinstance(evidence, Mapping):
        raise RepairSandboxError("Phase 8 result is missing output/evidence objects")
    output_path = _resolve_result_path(root, output.get("path"), "Phase 8 patched output")
    if output_path.stat().st_size != output.get("size") or sha256_file(output_path) != output.get("sha256"):
        raise RepairSandboxError("Phase 8 patched output bytes do not match the result pin")

    evidence_dir = _resolve_result_path(root, evidence.get("directory"), "Phase 8 evidence directory", directory=True)
    manifest_path = _resolve_result_path(root, evidence.get("manifest"), "Phase 8 evidence manifest")
    if evidence_dir not in manifest_path.parents:
        raise RepairSandboxError("Phase 8 evidence manifest is outside its evidence directory")
    manifest = _load_json(manifest_path, "Phase 8 evidence manifest")
    if manifest.get("format") != EVIDENCE_FORMAT:
        raise RepairSandboxError(f"Phase 8 evidence manifest must use format {EVIDENCE_FORMAT}")
    raw_files = manifest.get("files")
    if not isinstance(raw_files, list):
        raise RepairSandboxError("Phase 8 evidence manifest has no files array")
    files: dict[str, Path] = {}
    file_pins: dict[str, Any] = {}
    for index, raw in enumerate(raw_files):
        if not isinstance(raw, Mapping):
            raise RepairSandboxError(f"Phase 8 evidence manifest files[{index}] must be an object")
        name = raw.get("path")
        if not isinstance(name, str) or Path(name).name != name or name in files:
            raise RepairSandboxError("Phase 8 evidence manifest file paths must be unique base names")
        path = evidence_dir / name
        if path.is_symlink() or not path.is_file():
            raise RepairSandboxError(f"Phase 8 evidence file is missing or unsafe: {name}")
        actual_size = path.stat().st_size
        actual_hash = sha256_file(path)
        if actual_size != raw.get("size") or actual_hash != raw.get("sha256"):
            raise RepairSandboxError(f"Phase 8 evidence file does not match manifest pin: {name}")
        files[name] = path
        file_pins[name] = {"size": actual_size, "sha256": actual_hash}
    missing = sorted(REQUIRED_EVIDENCE_FILES - files.keys())
    if missing:
        raise RepairSandboxError(f"Phase 8 evidence is missing required files: {', '.join(missing)}")
    semantic_path = _resolve_result_path(root, evidence.get("semanticDiff"), "Phase 8 semantic diff")
    if semantic_path != files["semantic-diff.json"]:
        raise RepairSandboxError("Phase 8 semantic-diff result path does not match the verified evidence manifest")
    return output_path, files, {
        "manifest": _file_pin(manifest_path),
        "files": file_pins,
    }


def _write_json_create_new(path: Path, value: Any) -> None:
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
    except FileExistsError as exc:
        raise RepairSandboxError(f"verification report already exists: {path.name}") from exc
    except Exception:
        if descriptor is not None:
            os.close(descriptor)
        if created:
            path.unlink(missing_ok=True)
        raise


def _content_pins(value: Mapping[str, Any]) -> dict[str, Any]:
    return {key: value.get(key) for key in ("appearancesIndex", "itemsXml", "rules", "reviewRules", "scriptCorpus")}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Apply an existing Phase 8 plan to a sandbox copy and verify real before/after mechanic and script-resolution evidence."
    )
    parser.add_argument("source", type=_path)
    parser.add_argument("plan", type=_path)
    parser.add_argument("--scanner", type=_path)
    parser.add_argument("--artifact-root", type=_path, required=True)
    parser.add_argument("--appearances-index", type=_path, required=True)
    parser.add_argument("--items-xml", type=_path, required=True)
    parser.add_argument("--repository-root", type=_path, default=Path("."))
    parser.add_argument("--script-root", action="append", dest="script_roots")
    parser.add_argument("--rules", type=_path)
    parser.add_argument("--review-rules", type=_path)
    parser.add_argument("--patched-output", type=_path, default=Path("patched.otbm"))
    parser.add_argument("--phase8-evidence", type=_path, default=Path("phase8-evidence"))
    parser.add_argument("--phase8-result", type=_path, default=Path("phase8-result.json"))
    parser.add_argument("--output", type=_path, default=Path("sandbox-verification.json"))
    parser.add_argument("--timeout", type=int, default=3600)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.timeout <= 0:
            raise RepairSandboxError("timeout must be positive")
        source = _resolve_file(args.source, "source map")
        plan_path = _resolve_file(args.plan, "patch plan")
        scanner = locate_scanner(args.scanner).resolve(strict=True)
        if scanner.is_symlink() or not scanner.is_file() or not os.access(scanner, os.X_OK):
            raise RepairSandboxError("native scanner must be a non-symlink executable regular file")
        appearances = _resolve_file(args.appearances_index, "appearances index")
        items_xml = _resolve_file(args.items_xml, "items.xml")
        repository_root = _resolve_directory(args.repository_root, "repository root")
        rules = _resolve_file(args.rules, "runtime rules") if args.rules is not None else None
        review_rules = _resolve_file(args.review_rules, "review rules") if args.review_rules is not None else None
        artifact_root = _prepare_artifact_root(args.artifact_root)

        verification_output = _confined_relative(artifact_root, args.output, "verification report", must_be_new=True)
        phase8_output_destination = _confined_relative(artifact_root, args.patched_output, "patched output", must_be_new=True)
        phase8_evidence_destination = _confined_relative(artifact_root, args.phase8_evidence, "Phase 8 evidence", must_be_new=True)
        phase8_result_destination = _confined_relative(artifact_root, args.phase8_result, "Phase 8 result", must_be_new=True)
        if verification_output in {phase8_output_destination, phase8_result_destination, phase8_evidence_destination}:
            raise RepairSandboxError("verification report must be separate from Phase 8 destinations")
        if phase8_evidence_destination in verification_output.parents or verification_output in phase8_evidence_destination.parents:
            raise RepairSandboxError("verification report must be outside the Phase 8 evidence directory")

        plan = load_plan(plan_path)
        source_stat_before = source.stat()
        source_hash_before = sha256_file(source)
        if source_hash_before != plan.source.sha256 or source_stat_before.st_size != plan.source.size:
            raise RepairSandboxError("source map does not match the patch-plan source pin")
        plan_pin_before = _file_pin(plan_path)
        scanner_pin_before = _file_pin(scanner)
        input_pins_before = _build_input_pins(
            appearances_index=appearances,
            items_xml=items_xml,
            repository_root=repository_root,
            script_roots=args.script_roots,
            rules=rules,
            review_rules=review_rules,
        )

        phase8_result = apply_bounded_patch(
            plan=plan,
            source_path=source,
            scanner_path=scanner,
            artifact_root=artifact_root,
            output_path=args.patched_output,
            evidence_directory=args.phase8_evidence,
            result_path=args.phase8_result,
            timeout_seconds=args.timeout,
        )
        validate_phase8_result(phase8_result, plan)
        persisted_phase8_result = _load_json(phase8_result_destination, "persisted Phase 8 result")
        if persisted_phase8_result != phase8_result:
            raise RepairSandboxError("persisted Phase 8 result differs from the in-process result")
        patched_output, evidence_files, evidence_pins = _verify_phase8_artifacts(artifact_root, phase8_result)

        with tempfile.TemporaryDirectory(prefix=".otbm-repair-sandbox-audit-", dir=artifact_root) as temporary:
            workspace = Path(temporary)
            before_audit_path = workspace / "before-item-audit.json"
            after_audit_path = workspace / "after-item-audit.json"
            before_audit = run_item_audit(
                map_path=source,
                scanner=scanner,
                appearances_index_path=appearances,
                items_xml=items_xml,
                output=before_audit_path,
                scan_output=workspace / "before-item-scan.json",
                include_map_hash=True,
            )
            after_audit = run_item_audit(
                map_path=patched_output,
                scanner=scanner,
                appearances_index_path=appearances,
                items_xml=items_xml,
                output=after_audit_path,
                scan_output=workspace / "after-item-scan.json",
                include_map_hash=True,
            )
            before_resolution = run_script_resolution(
                item_audit_path=before_audit_path,
                repository_root=repository_root,
                script_roots=args.script_roots,
                output=workspace / "before-script-resolution.json",
                rules_path=rules,
                review_rules_path=review_rules,
            )
            after_resolution = run_script_resolution(
                item_audit_path=after_audit_path,
                repository_root=repository_root,
                script_roots=args.script_roots,
                output=workspace / "after-script-resolution.json",
                rules_path=rules,
                review_rules_path=review_rules,
            )

        before_map = before_audit.get("sources", {}).get("map", {})
        after_map = after_audit.get("sources", {}).get("map", {})
        if before_map.get("sha256") != plan.source.sha256 or before_map.get("size") != plan.source.size:
            raise RepairSandboxError("before item audit does not prove the planned source identity")
        phase8_output = phase8_result["output"]
        if after_map.get("sha256") != phase8_output.get("sha256") or after_map.get("size") != phase8_output.get("size"):
            raise RepairSandboxError("after item audit does not prove the Phase 8 output identity")

        before_anchors = _load_json(evidence_files["before-anchors.json"], "before anchor evidence")
        after_anchors = _load_json(evidence_files["after-anchors.json"], "after anchor evidence")
        operation_results = [
            verify_operation(
                operation=operation,
                before_item_audit=before_audit,
                after_item_audit=after_audit,
                before_anchors=before_anchors,
                after_anchors=after_anchors,
                before_script_resolution=before_resolution,
                after_script_resolution=after_resolution,
            )
            for operation in plan.operations
        ]

        source_stat_after = source.stat()
        if (
            source_stat_after.st_size != source_stat_before.st_size
            or source_stat_after.st_mtime_ns != source_stat_before.st_mtime_ns
            or sha256_file(source) != source_hash_before
        ):
            raise RepairSandboxError("original source map changed during sandbox verification")
        if _file_pin(plan_path) != plan_pin_before or _file_pin(scanner) != scanner_pin_before:
            raise RepairSandboxError("patch plan or native scanner changed during sandbox verification")
        input_pins_after = _build_input_pins(
            appearances_index=appearances,
            items_xml=items_xml,
            repository_root=repository_root,
            script_roots=args.script_roots,
            rules=rules,
            review_rules=review_rules,
        )
        if _content_pins(input_pins_after) != _content_pins(input_pins_before):
            raise RepairSandboxError("content-affecting audit/script inputs changed during sandbox verification")

        pins = {
            "plan": plan_pin_before,
            "source": {"fileName": source.name, "size": source_stat_before.st_size, "sha256": source_hash_before},
            "scanner": scanner_pin_before,
            "auditAndScriptInputsBefore": input_pins_before,
            "auditAndScriptInputsAfter": input_pins_after,
            "phase8Result": _file_pin(phase8_result_destination),
            "phase8Evidence": evidence_pins,
            "beforeItemAuditSummary": before_audit.get("summary"),
            "afterItemAuditSummary": after_audit.get("summary"),
            "beforeScriptResolutionSummary": before_resolution.get("summary"),
            "afterScriptResolutionSummary": after_resolution.get("summary"),
        }
        report = build_verification_report(
            plan=plan,
            phase8_result=phase8_result,
            operation_results=operation_results,
            pins=pins,
        )
        _write_json_create_new(verification_output, report)
        json.dump(
            {
                "ok": report["ok"],
                "operations": report["summary"]["operations"],
                "runtimeRegressionOperations": report["summary"]["runtimeRegressionOperations"],
                "runtimeUnresolvedAfter": report["summary"]["runtimeUnresolvedAfter"],
                "patchedOutput": str(patched_output),
                "output": str(verification_output),
            },
            sys.stdout,
            indent=2,
            sort_keys=True,
        )
        sys.stdout.write("\n")
        return 0
    except (
        FileNotFoundError,
        OSError,
        ValueError,
        BoundedPatchError,
        ItemAuditError,
        ScriptAuditError,
        PreflightError,
        RepairSandboxError,
    ) as exc:
        parser.error(str(exc))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
