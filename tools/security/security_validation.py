#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

SCHEMA_VERSION = 1
REPORT_SCHEMA = "ots-security-validation-report-v1"
MAX_SOURCE_BYTES = 1024 * 1024
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")
REPOSITORY_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
COMPONENTS = {"server", "client", "web", "database", "cache"}
SEVERITIES = {"low", "medium", "high", "critical"}
MODES = {"source-regex"}


class SecurityScenarioError(ValueError):
    pass


@dataclass(frozen=True)
class SecurityScenario:
    path: Path
    data: dict[str, Any]
    source_files: tuple[Path, ...]
    evidence_files: tuple[Path, ...]

    @property
    def scenario_id(self) -> str:
        return str(self.data["id"])


@dataclass(frozen=True)
class SourceRecord:
    path: str
    sha256: str
    size_bytes: int
    text: str


def repository_root() -> Path:
    return Path(__file__).resolve().parents[2]


def scenario_root(root: Path) -> Path:
    return root / "tests" / "security" / "scenarios"


def _mapping(value: Any, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise SecurityScenarioError(f"{path} must be an object")
    return value


def _exact_keys(mapping: dict[str, Any], required: set[str], path: str) -> None:
    missing = sorted(required - set(mapping))
    unknown = sorted(set(mapping) - required)
    if missing:
        raise SecurityScenarioError(f"{path} missing required field(s): {', '.join(missing)}")
    if unknown:
        raise SecurityScenarioError(f"{path} contains unsupported field(s): {', '.join(unknown)}")


def _string(mapping: dict[str, Any], key: str, path: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value.strip():
        raise SecurityScenarioError(f"{path}.{key} must be a non-empty string")
    return value.strip()


def _string_list(mapping: dict[str, Any], key: str, path: str, *, allow_empty: bool = False) -> list[str]:
    value = mapping.get(key)
    if not isinstance(value, list) or (not value and not allow_empty):
        qualifier = "an array" if allow_empty else "a non-empty array"
        raise SecurityScenarioError(f"{path}.{key} must be {qualifier} of non-empty strings")
    if any(not isinstance(item, str) or not item for item in value):
        raise SecurityScenarioError(f"{path}.{key} must contain only non-empty strings")
    return value


def _regular_repository_file(root: Path, raw_path: str, label: str) -> Path:
    relative = Path(raw_path)
    if relative.is_absolute() or not relative.parts or any(part in {"", ".", ".."} for part in relative.parts):
        raise SecurityScenarioError(f"{label} must be a normalized repository-relative path: {raw_path!r}")
    if relative.as_posix() != raw_path:
        raise SecurityScenarioError(f"{label} must use normalized forward-slash separators: {raw_path!r}")

    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise SecurityScenarioError(f"{label} must not traverse a symlink: {raw_path!r}")

    resolved_root = root.resolve()
    resolved = current.resolve()
    try:
        resolved.relative_to(resolved_root)
    except ValueError as exc:
        raise SecurityScenarioError(f"{label} escapes the repository root: {raw_path!r}") from exc
    if not resolved.is_file():
        raise SecurityScenarioError(f"{label} does not exist as a regular file: {raw_path!r}")
    if resolved.stat().st_size > MAX_SOURCE_BYTES:
        raise SecurityScenarioError(f"{label} exceeds the {MAX_SOURCE_BYTES}-byte limit: {raw_path!r}")
    return resolved


def _compile_patterns(patterns: Iterable[str], label: str) -> None:
    for index, pattern in enumerate(patterns):
        try:
            re.compile(pattern, re.MULTILINE)
        except re.error as exc:
            raise SecurityScenarioError(f"{label}[{index}] is not a valid regular expression: {exc}") from exc


def validate_scenario(path: Path, root: Path) -> SecurityScenario:
    expected_root = scenario_root(root).resolve()
    if path.is_symlink():
        raise SecurityScenarioError(f"security scenario manifest must not be a symlink: {path}")
    try:
        resolved_path = path.resolve()
        resolved_path.relative_to(expected_root)
    except ValueError as exc:
        raise SecurityScenarioError(f"security scenario manifest must remain under {expected_root}: {path}") from exc

    try:
        data = json.loads(resolved_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SecurityScenarioError(f"{path}: invalid JSON: {exc}") from exc
    except OSError as exc:
        raise SecurityScenarioError(f"{path}: cannot read scenario: {exc}") from exc

    data = _mapping(data, "scenario")
    top_keys = {
        "schema_version",
        "id",
        "name",
        "description",
        "component",
        "target_adapter",
        "mode",
        "severity",
        "authorization",
        "source",
        "evidence",
    }
    _exact_keys(data, top_keys, "scenario")
    if data["schema_version"] != SCHEMA_VERSION:
        raise SecurityScenarioError(f"scenario.schema_version must be {SCHEMA_VERSION}")

    scenario_id = _string(data, "id", "scenario")
    target_adapter = _string(data, "target_adapter", "scenario")
    _string(data, "name", "scenario")
    _string(data, "description", "scenario")
    component = _string(data, "component", "scenario")
    mode = _string(data, "mode", "scenario")
    severity = _string(data, "severity", "scenario")
    if not SLUG_RE.fullmatch(scenario_id):
        raise SecurityScenarioError(f"scenario.id must match {SLUG_RE.pattern}")
    if not SLUG_RE.fullmatch(target_adapter):
        raise SecurityScenarioError(f"scenario.target_adapter must match {SLUG_RE.pattern}")
    if component not in COMPONENTS:
        raise SecurityScenarioError(f"scenario.component must be one of {sorted(COMPONENTS)}")
    if mode not in MODES:
        raise SecurityScenarioError(f"scenario.mode must be one of {sorted(MODES)}")
    if severity not in SEVERITIES:
        raise SecurityScenarioError(f"scenario.severity must be one of {sorted(SEVERITIES)}")

    authorization = _mapping(data["authorization"], "scenario.authorization")
    _exact_keys(authorization, {"scope", "repository"}, "scenario.authorization")
    if _string(authorization, "scope", "scenario.authorization") != "repository":
        raise SecurityScenarioError("scenario.authorization.scope must be 'repository'")
    repository = _string(authorization, "repository", "scenario.authorization")
    if not REPOSITORY_RE.fullmatch(repository):
        raise SecurityScenarioError("scenario.authorization.repository must be in owner/name form")

    source = _mapping(data["source"], "scenario.source")
    _exact_keys(source, {"files", "forbidden_regex", "required_regex"}, "scenario.source")
    files = _string_list(source, "files", "scenario.source")
    forbidden = _string_list(source, "forbidden_regex", "scenario.source", allow_empty=True)
    required = _string_list(source, "required_regex", "scenario.source", allow_empty=True)
    if not forbidden and not required:
        raise SecurityScenarioError("scenario.source must define at least one forbidden_regex or required_regex assertion")
    _compile_patterns(forbidden, "scenario.source.forbidden_regex")
    _compile_patterns(required, "scenario.source.required_regex")
    source_files = tuple(
        _regular_repository_file(root, item, f"scenario.source.files[{index}]")
        for index, item in enumerate(files)
    )

    evidence = _mapping(data["evidence"], "scenario.evidence")
    _exact_keys(evidence, {"regression_tests", "related_prs"}, "scenario.evidence")
    regression_tests = _string_list(evidence, "regression_tests", "scenario.evidence")
    related_prs = evidence["related_prs"]
    if not isinstance(related_prs, list) or not related_prs:
        raise SecurityScenarioError("scenario.evidence.related_prs must be a non-empty array of positive integers")
    if any(not isinstance(item, int) or isinstance(item, bool) or item <= 0 for item in related_prs):
        raise SecurityScenarioError("scenario.evidence.related_prs must contain only positive integers")
    evidence_files = tuple(
        _regular_repository_file(root, item, f"scenario.evidence.regression_tests[{index}]")
        for index, item in enumerate(regression_tests)
    )

    return SecurityScenario(path=resolved_path, data=data, source_files=source_files, evidence_files=evidence_files)


def discover(root: Path) -> list[SecurityScenario]:
    directory = scenario_root(root)
    if not directory.is_dir():
        raise SecurityScenarioError(f"security scenario directory does not exist: {directory}")

    scenarios: list[SecurityScenario] = []
    errors: list[str] = []
    for path in sorted(directory.rglob("*.json")):
        try:
            scenarios.append(validate_scenario(path, root))
        except SecurityScenarioError as exc:
            errors.append(f"{path}: {exc}")
    if errors:
        raise SecurityScenarioError("\n".join(errors))
    if not scenarios:
        raise SecurityScenarioError(f"no security scenarios found under {directory}")

    seen: dict[str, Path] = {}
    for scenario in scenarios:
        previous = seen.get(scenario.scenario_id)
        if previous:
            raise SecurityScenarioError(
                f"duplicate security scenario id {scenario.scenario_id}: {previous} and {scenario.path}"
            )
        seen[scenario.scenario_id] = scenario.path
    return scenarios


def select(scenarios: Iterable[SecurityScenario], scenario_id: str) -> SecurityScenario:
    matches = [scenario for scenario in scenarios if scenario.scenario_id == scenario_id]
    if len(matches) != 1:
        available = ", ".join(sorted(scenario.scenario_id for scenario in scenarios))
        raise SecurityScenarioError(f"security scenario {scenario_id!r} not found; available: {available}")
    return matches[0]


def _read_source(path: Path, root: Path) -> SourceRecord:
    raw = path.read_bytes()
    if len(raw) > MAX_SOURCE_BYTES:
        raise SecurityScenarioError(f"source file exceeded size limit after validation: {path}")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise SecurityScenarioError(f"source file is not UTF-8 text: {path}") from exc
    return SourceRecord(
        path=path.relative_to(root.resolve()).as_posix(),
        sha256=hashlib.sha256(raw).hexdigest(),
        size_bytes=len(raw),
        text=text,
    )


def _line_column(text: str, offset: int) -> tuple[int, int]:
    line = text.count("\n", 0, offset) + 1
    last_newline = text.rfind("\n", 0, offset)
    column = offset + 1 if last_newline < 0 else offset - last_newline
    return line, column


def run_scenario(scenario: SecurityScenario, root: Path, authorized_repository: str) -> dict[str, Any]:
    scenario_repository = str(scenario.data["authorization"]["repository"])
    if scenario_repository != authorized_repository:
        raise SecurityScenarioError(
            f"scenario {scenario.scenario_id} is authorized for {scenario_repository}, not {authorized_repository}"
        )

    source_config = scenario.data["source"]
    records = [_read_source(path, root) for path in scenario.source_files]
    findings: list[dict[str, Any]] = []

    for record in records:
        for pattern in source_config["forbidden_regex"]:
            regex = re.compile(pattern, re.MULTILINE)
            for match in regex.finditer(record.text):
                line, column = _line_column(record.text, match.start())
                findings.append(
                    {
                        "assertion": "forbidden_regex",
                        "path": record.path,
                        "pattern": pattern,
                        "line": line,
                        "column": column,
                    }
                )
        for pattern in source_config["required_regex"]:
            regex = re.compile(pattern, re.MULTILINE)
            if regex.search(record.text) is None:
                findings.append(
                    {
                        "assertion": "required_regex",
                        "path": record.path,
                        "pattern": pattern,
                        "line": None,
                        "column": None,
                    }
                )

    findings.sort(
        key=lambda item: (
            item["path"],
            item["assertion"],
            item["pattern"],
            item["line"] or 0,
            item["column"] or 0,
        )
    )
    records.sort(key=lambda item: item.path)
    evidence = scenario.data["evidence"]
    return {
        "schema": REPORT_SCHEMA,
        "schema_version": SCHEMA_VERSION,
        "scenario_id": scenario.scenario_id,
        "scenario_source": scenario.path.resolve().relative_to(root.resolve()).as_posix(),
        "name": scenario.data["name"],
        "component": scenario.data["component"],
        "target_adapter": scenario.data["target_adapter"],
        "mode": scenario.data["mode"],
        "severity": scenario.data["severity"],
        "authorization": scenario.data["authorization"],
        "result": "fail" if findings else "pass",
        "findings": findings,
        "sources": [
            {"path": record.path, "sha256": record.sha256, "size_bytes": record.size_bytes}
            for record in records
        ],
        "evidence": {
            "regression_tests": list(evidence["regression_tests"]),
            "related_prs": list(evidence["related_prs"]),
        },
    }


def render_report(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, sort_keys=True) + "\n"


def write_report(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(render_report(report), encoding="utf-8")
    temporary.replace(path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate and execute bounded OTS security scenarios.")
    parser.add_argument("--root", type=Path, default=repository_root())
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("list", help="List validated security scenarios.")
    subparsers.add_parser("validate", help="Validate every security scenario without executing it.")

    run = subparsers.add_parser("run", help="Execute one validated security scenario.")
    run.add_argument("--scenario", required=True)
    run.add_argument("--authorized-repository", required=True)
    run.add_argument("--report", type=Path)

    run_all = subparsers.add_parser("run-all", help="Execute every validated security scenario.")
    run_all.add_argument("--authorized-repository", required=True)
    run_all.add_argument("--report-dir", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    root = args.root.resolve()
    try:
        scenarios = discover(root)
        if args.command == "list":
            for scenario in scenarios:
                print(
                    f"{scenario.scenario_id}\t{scenario.data['component']}\t"
                    f"{scenario.data['severity']}\t{scenario.data['name']}"
                )
            return 0
        if args.command == "validate":
            print(f"Validated {len(scenarios)} security scenario(s).")
            return 0
        if args.command == "run":
            scenario = select(scenarios, args.scenario)
            report = run_scenario(scenario, root, args.authorized_repository)
            if args.report:
                write_report(args.report, report)
            else:
                sys.stdout.write(render_report(report))
            return 0 if report["result"] == "pass" else 1
        if args.command == "run-all":
            failed = 0
            for scenario in scenarios:
                report = run_scenario(scenario, root, args.authorized_repository)
                if args.report_dir:
                    write_report(args.report_dir / f"{scenario.scenario_id}.json", report)
                else:
                    sys.stdout.write(render_report(report))
                if report["result"] != "pass":
                    failed += 1
            print(f"Executed {len(scenarios)} security scenario(s); failures={failed}.", file=sys.stderr)
            return 1 if failed else 0
        parser.error(f"unsupported command {args.command}")  # pragma: no cover
    except (SecurityScenarioError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
