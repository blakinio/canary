#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path


def replace_once(content: str, old: str, new: str, label: str) -> str:
    if old not in content:
        raise RuntimeError(f"expected patch anchor is missing: {label}")
    return content.replace(old, new, 1)


source_path = Path("tools/e2e/stability_certification.py")
source = source_path.read_text(encoding="utf-8")
source = replace_once(
    source,
    "from pathlib import Path\n",
    "from pathlib import Path, PurePosixPath\n",
    "path import",
)
source = replace_once(
    source,
    '''def _first_divergence(value: Any) -> str | None:
''',
    '''def _safe_relative_path(value: Any, label: str) -> str:
    text = _safe_text(value, label)
    assert text is not None
    if "\\\\" in text or text.startswith("/"):
        raise StabilityCertificationError(f"{label} must be a normalized POSIX relative path")
    raw_parts = text.split("/")
    if any(part in {"", ".", ".."} for part in raw_parts):
        raise StabilityCertificationError(f"{label} must be a normalized POSIX relative path")
    path = PurePosixPath(text)
    if path.is_absolute() or str(path) != text:
        raise StabilityCertificationError(f"{label} must be a normalized POSIX relative path")
    return text


def _missing_provenance_fields(provenance: Mapping[str, Any]) -> list[str]:
    return sorted(
        key
        for key, value in provenance.items()
        if not isinstance(value, str) or not value or value == "unknown"
    )


def _validate_provenance(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping) or set(value) != set(PROVENANCE_FIELDS):
        raise StabilityCertificationError(f"{label} is invalid")
    for field in ("server_revision", "client_revision", "datapack"):
        field_value = value.get(field)
        if field_value is not None:
            _safe_text(field_value, f"{label}.{field}")
    execution_tier = value.get("execution_tier")
    if execution_tier is not None and execution_tier not in EXECUTION_TIERS:
        raise StabilityCertificationError(f"{label}.execution_tier is invalid")
    return value


def _first_divergence(value: Any) -> str | None:
''',
    "validation helpers",
)
source = replace_once(
    source,
    '''    _safe_text(value.get("path"), f"{label}.path")
''',
    '''    _safe_relative_path(value.get("path"), f"{label}.path")
''',
    "source path validation",
)
source = replace_once(
    source,
    '''    if not isinstance(value.get("cleanup_certified"), bool) or not isinstance(
        value.get("contract_valid"), bool
    ):
        raise StabilityCertificationError(f"{label} booleans are invalid")
''',
    '''    _safe_text(value.get("status"), f"{label}.status")
    if not isinstance(value.get("cleanup_certified"), bool) or not isinstance(
        value.get("contract_valid"), bool
    ):
        raise StabilityCertificationError(f"{label} booleans are invalid")
    if value.get("cleanup_certified") is True and value.get("contract_valid") is not True:
        raise StabilityCertificationError(f"{label} certification requires a valid contract")
''',
    "cleanup validation",
)
source = replace_once(
    source,
    '''    if policy.get("comparability_fields") != list(PROVENANCE_FIELDS):
        raise StabilityCertificationError("policy comparability fields are invalid")
''',
    '''    if policy.get("comparability_fields") != list(PROVENANCE_FIELDS):
        raise StabilityCertificationError("policy comparability fields are invalid")
    if policy.get("pass_definition") != (
        "every counted attempt has status success and exact cleanup certification pass"
    ):
        raise StabilityCertificationError("policy pass definition is invalid")
''',
    "policy pass definition",
)
source = replace_once(
    source,
    '''    roots = boundary.get("roots")
    if not isinstance(roots, list):
        raise StabilityCertificationError("evidence_boundary.roots must be an array")
''',
    '''    roots = boundary.get("roots")
    if not isinstance(roots, list):
        raise StabilityCertificationError("evidence_boundary.roots must be an array")
    root_file_count = 0
    for index, root in enumerate(roots, start=1):
        root_label = f"evidence_boundary.roots[{index - 1}]"
        if not isinstance(root, Mapping) or set(root) != {"id", "result_files"}:
            raise StabilityCertificationError(f"{root_label} has an invalid field set")
        if root.get("id") != f"evidence-{index}":
            raise StabilityCertificationError(f"{root_label}.id is invalid")
        root_file_count += _require_non_negative_int(
            root.get("result_files"), f"{root_label}.result_files"
        )
    if root_file_count != (
        boundary.get("valid_envelope_count") + boundary.get("invalid_result_count")
    ):
        raise StabilityCertificationError("evidence root file counts are inconsistent")
''',
    "root validation",
)
source = replace_once(
    source,
    '''        provenance = cell.get("provenance")
        if not isinstance(provenance, Mapping) or set(provenance) != set(
            PROVENANCE_FIELDS
        ):
            raise StabilityCertificationError(f"{label}.provenance is invalid")
''',
    '''        provenance = _validate_provenance(
            cell.get("provenance"), f"{label}.provenance"
        )
        if cell_id != _cell_id(scenario, provenance):
            raise StabilityCertificationError(f"{label}.cell_id is inconsistent")
''',
    "cell provenance and id",
)
source = replace_once(
    source,
    '''            _safe_text(attempt.get("identity"), f"{attempt_label}.identity")
            _safe_text(attempt.get("run_id"), f"{attempt_label}.run_id")
            _require_positive_int(attempt.get("attempt"), f"{attempt_label}.attempt")
''',
    '''            identity = _safe_text(
                attempt.get("identity"), f"{attempt_label}.identity"
            )
            run_id = _safe_text(attempt.get("run_id"), f"{attempt_label}.run_id")
            attempt_number = _require_positive_int(
                attempt.get("attempt"), f"{attempt_label}.attempt"
            )
            if identity != f"{run_id}#{attempt_number}":
                raise StabilityCertificationError(
                    f"{attempt_label}.identity is inconsistent"
                )
''',
    "attempt identity",
)
source = replace_once(
    source,
    '''        if not isinstance(missing, list) or missing != sorted(set(missing)):
            raise StabilityCertificationError(f"{label} missing provenance is invalid")
''',
    '''        if not isinstance(missing, list) or missing != sorted(set(missing)):
            raise StabilityCertificationError(f"{label} missing provenance is invalid")
        if missing != _missing_provenance_fields(provenance):
            raise StabilityCertificationError(
                f"{label} missing provenance is inconsistent"
            )
''',
    "missing provenance consistency",
)
source = replace_once(
    source,
    '''        for field in (
            "failure_class_distribution",
            "first_divergence_distribution",
        ):
            distribution = cell.get(field)
            if not isinstance(distribution, Mapping):
                raise StabilityCertificationError(f"{label}.{field} is invalid")
            for key, count in distribution.items():
                _safe_text(key, f"{label}.{field} key")
                _require_positive_int(count, f"{label}.{field}.{key}")
''',
    '''        distribution_fields = {
            "failure_class_distribution": "failure_classification",
            "first_divergence_distribution": "first_divergence",
        }
        for field, attempt_field in distribution_fields.items():
            distribution = cell.get(field)
            if not isinstance(distribution, Mapping):
                raise StabilityCertificationError(f"{label}.{field} is invalid")
            for key, count in distribution.items():
                _safe_text(key, f"{label}.{field} key")
                _require_positive_int(count, f"{label}.{field}.{key}")
            if dict(distribution) != _distribution(attempts, attempt_field):
                raise StabilityCertificationError(
                    f"{label}.{field} is inconsistent"
                )
        expected_cleanup_failures = sum(
            attempt["cleanup"].get("contract_valid") is True
            and attempt["cleanup"].get("cleanup_certified") is False
            for attempt in attempts
        )
        expected_cleanup_unknowns = sum(
            attempt["cleanup"].get("contract_valid") is False
            for attempt in attempts
        )
        if cell.get("cleanup_failure_count") != expected_cleanup_failures:
            raise StabilityCertificationError(
                f"{label}.cleanup_failure_count is inconsistent"
            )
        if cell.get("cleanup_unknown_count") != expected_cleanup_unknowns:
            raise StabilityCertificationError(
                f"{label}.cleanup_unknown_count is inconsistent"
            )
''',
    "distribution and cleanup consistency",
)
source = replace_once(
    source,
    '''    invalid = report.get("invalid_evidence")
    if not isinstance(invalid, list):
        raise StabilityCertificationError("invalid_evidence must be an array")
''',
    '''    invalid = report.get("invalid_evidence")
    if not isinstance(invalid, list):
        raise StabilityCertificationError("invalid_evidence must be an array")
    invalid_keys: list[tuple[str, str, str]] = []
    for index, item in enumerate(invalid):
        label = f"invalid_evidence[{index}]"
        if not isinstance(item, Mapping) or set(item) != {"source", "error"}:
            raise StabilityCertificationError(f"{label} has an invalid field set")
        source_value = item.get("source")
        if not isinstance(source_value, Mapping) or set(source_value) != {
            "root_id",
            "path",
        }:
            raise StabilityCertificationError(f"{label}.source is invalid")
        root_id = _safe_text(source_value.get("root_id"), f"{label}.source.root_id")
        source_path = _safe_relative_path(
            source_value.get("path"), f"{label}.source.path"
        )
        error = _safe_text(item.get("error"), f"{label}.error")
        invalid_keys.append((root_id, source_path, error))
    if invalid_keys != sorted(invalid_keys):
        raise StabilityCertificationError("invalid_evidence must be sorted")
''',
    "invalid evidence validation",
)
source_path.write_text(source, encoding="utf-8")


test_path = Path("tests/e2e/test_stability_certification.py")
tests = test_path.read_text(encoding="utf-8")
anchor = '''    def test_normalize_envelope_reuses_coverage_normalization(self) -> None:
'''
new_tests = '''    def test_validation_rejects_tampered_cell_id(self) -> None:
        report = self.build(
            [self.envelope([self.attempt(1), self.attempt(2)])],
            minimum_runs=2,
        )
        report["certifications"][0]["cell_id"] = "0" * 20
        with self.assertRaisesRegex(
            stability.StabilityCertificationError, "cell_id is inconsistent"
        ):
            stability.validate_report(report)

    def test_validation_rejects_tampered_distribution(self) -> None:
        report = self.build(
            [self.envelope([self.attempt(1), self.attempt(2, status="failure")])],
            minimum_runs=2,
        )
        report["certifications"][0]["failure_class_distribution"] = {"assertion": 2}
        with self.assertRaisesRegex(
            stability.StabilityCertificationError,
            "failure_class_distribution is inconsistent",
        ):
            stability.validate_report(report)

    def test_validation_rejects_tampered_cleanup_count(self) -> None:
        report = self.build(
            [self.envelope([self.attempt(1), self.attempt(2, cleanup_certified=False)])],
            minimum_runs=2,
        )
        report["certifications"][0]["cleanup_failure_count"] = 0
        with self.assertRaisesRegex(
            stability.StabilityCertificationError,
            "cleanup_failure_count is inconsistent",
        ):
            stability.validate_report(report)

    def test_validation_rejects_unsafe_source_path(self) -> None:
        report = self.build(
            [self.envelope([self.attempt(1), self.attempt(2)])],
            minimum_runs=2,
        )
        report["certifications"][0]["attempts"][0]["source"]["path"] = "../result.json"
        with self.assertRaisesRegex(
            stability.StabilityCertificationError,
            "normalized POSIX relative path",
        ):
            stability.validate_report(report)

    def test_validation_rejects_unsupported_execution_tier(self) -> None:
        report = self.build(
            [self.envelope([self.attempt(1), self.attempt(2)])],
            minimum_runs=2,
        )
        report["certifications"][0]["provenance"]["execution_tier"] = "nightly"
        with self.assertRaisesRegex(
            stability.StabilityCertificationError,
            "execution_tier is invalid",
        ):
            stability.validate_report(report)

'''
if anchor not in tests:
    raise RuntimeError("test insertion anchor is missing")
test_path.write_text(tests.replace(anchor, new_tests + anchor, 1), encoding="utf-8")
