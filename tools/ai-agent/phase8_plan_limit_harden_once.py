from __future__ import annotations

from pathlib import Path


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: found {count} source matches, expected 1")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


types = Path("tools/ai-agent/otbm_bounded_patch_types.py")
replace_once(
    types,
    'MAX_REGION_COORDINATES = 1_000_000\n',
    'MAX_REGION_COORDINATES = 1_000_000\nMAX_OPERATIONS = 10_000\nMAX_OPERATION_ID_LENGTH = 200\n',
    "plan limits",
)
replace_once(
    types,
    '''        if expected == replacement:
            raise BoundedPatchError(f"operations[{index}] does not change the value")
        return cls(
            operation_id=_text(value["id"], f"operations[{index}].id"),
''',
    '''        if expected == replacement:
            raise BoundedPatchError(f"operations[{index}] does not change the value")
        operation_id = _text(value["id"], f"operations[{index}].id")
        if len(operation_id) > MAX_OPERATION_ID_LENGTH:
            raise BoundedPatchError(
                f"operations[{index}].id exceeds {MAX_OPERATION_ID_LENGTH} characters"
            )
        return cls(
            operation_id=operation_id,
''',
    "operation id bound",
)
replace_once(
    types,
    '''        if not isinstance(raw_operations, list) or not raw_operations:
            raise BoundedPatchError("operations must be a non-empty array")
        operations = tuple(PatchOperation.from_raw(entry, index) for index, entry in enumerate(raw_operations))
''',
    '''        if not isinstance(raw_operations, list) or not raw_operations:
            raise BoundedPatchError("operations must be a non-empty array")
        if len(raw_operations) > MAX_OPERATIONS:
            raise BoundedPatchError(f"operations contains {len(raw_operations)} entries; limit is {MAX_OPERATIONS}")
        operations = tuple(PatchOperation.from_raw(entry, index) for index, entry in enumerate(raw_operations))
''',
    "pre-parse operation limit",
)

patcher = Path("tools/ai-agent/otbm_bounded_patch.py")
replace_once(
    patcher,
    '''    RESULT_FORMAT,
    BoundedPatchError,
''',
    '''    RESULT_FORMAT,
    MAX_OPERATIONS,
    BoundedPatchError,
''',
    "shared operation limit import",
)
replace_once(patcher, "MAX_OPERATIONS = 10_000\n", "", "duplicate operation limit")
replace_once(
    patcher,
    '        if current.exists() and current.is_symlink():\n',
    '        if current.is_symlink():\n',
    "broken parent symlink rejection",
)

test = Path("tools/ai-agent/test_otbm_bounded_patch.py")
replace_once(
    test,
    'from otbm_bounded_patch_types import BoundedPatchError, PatchPlan, sha256_file\n',
    'from otbm_bounded_patch_types import MAX_OPERATIONS, BoundedPatchError, PatchPlan, sha256_file\n',
    "test operation limit import",
)
plan_marker = '''    def test_rejects_duplicate_target(self) -> None:
'''
plan_tests = '''    def test_rejects_operation_count_before_parsing_entries(self) -> None:
        raw = {
            "format": "canary-otbm-bounded-patch-plan-v1",
            "source": {
                "fileName": "map.otbm",
                "sha256": "0" * 64,
                "size": 10,
                "otbmVersion": 4,
                "itemsMajor": 3,
                "itemsMinor": 57,
            },
            "region": {"from": [1, 1, 7], "to": [1, 1, 7]},
            "operations": [None] * (MAX_OPERATIONS + 1),
        }
        with self.assertRaisesRegex(BoundedPatchError, "limit is 10000"):
            PatchPlan.from_raw(raw)

    def test_rejects_overlong_operation_id(self) -> None:
        raw = {
            "format": "canary-otbm-bounded-patch-plan-v1",
            "source": {
                "fileName": "map.otbm",
                "sha256": "0" * 64,
                "size": 10,
                "otbmVersion": 4,
                "itemsMajor": 3,
                "itemsMinor": 57,
            },
            "region": {"from": [1000, 2000, 7], "to": [1100, 2200, 7]},
            "operations": [operation("x" * 201, "set-action-id", 0, 100, 1, 2)],
        }
        with self.assertRaisesRegex(BoundedPatchError, "exceeds 200 characters"):
            PatchPlan.from_raw(raw)

''' + plan_marker
replace_once(test, plan_marker, plan_tests, "plan limit regression tests")

symlink_marker = '''    @unittest.skipUnless(hasattr(os, "symlink"), "symlinks are unavailable")
    def test_rejects_symlink_output(self) -> None:
'''
symlink_test = '''    @unittest.skipUnless(hasattr(os, "symlink"), "symlinks are unavailable")
    def test_rejects_broken_symlink_parent(self) -> None:
        self.write_map()
        plan = self.make_plan([operation("action", "set-action-id", 0, 100, 1000, 1001)])
        self.artifacts.mkdir()
        os.symlink(self.artifacts / "missing-target", self.artifacts / "broken-parent", target_is_directory=True)
        with self.assertRaisesRegex(BoundedPatchError, "symlink"):
            apply_bounded_patch(
                plan=plan,
                source_path=self.source,
                scanner_path=self.scanner,
                artifact_root=self.artifacts,
                output_path=Path("broken-parent/patched.otbm"),
                evidence_directory=Path("evidence-broken-parent"),
                result_path=Path("result-broken-parent.json"),
                timeout_seconds=60,
            )

''' + symlink_marker
replace_once(test, symlink_marker, symlink_test, "broken symlink regression test")

for temporary in (
    Path(".github/workflows/phase8-plan-limit-harden-once.yml"),
    Path("tools/ai-agent/phase8_plan_limit_harden_once.py"),
):
    temporary.unlink(missing_ok=True)
