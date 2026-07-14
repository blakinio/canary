from __future__ import annotations

from pathlib import Path


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: found {count} source matches, expected 1")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


patcher = Path("tools/ai-agent/otbm_bounded_patch.py")
replace_once(
    patcher,
    '''    if resolved.exists():
        raise BoundedPatchError(f"{label} already exists: {resolved}")
    resolved.parent.mkdir(parents=True, exist_ok=True)
    _check_ancestors(root, lexical, label)
    _check_ancestors(root, resolved, label)
    return resolved


def _relative(root: Path, path: Path) -> str:
''',
    '''    if resolved.exists():
        raise BoundedPatchError(f"{label} already exists: {resolved}")
    return resolved


def _prepare_new_destination(root: Path, path: Path, label: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    _check_ancestors(root, path, label)
    if path.is_symlink():
        raise BoundedPatchError(f"{label} must not be a symlink: {path}")
    if path.exists():
        raise BoundedPatchError(f"{label} already exists: {path}")


def _relative(root: Path, path: Path) -> str:
''',
    "deferred destination parent creation",
)
replace_once(
    patcher,
    '        temporary_output = workspace / output.name\n',
    '        temporary_output = workspace / "patched-output.otbm"\n',
    "internal output name",
)
replace_once(
    patcher,
    '''        os.link(temporary_output, output)
        published_output = True
''',
    '''        _prepare_new_destination(root, output, "patched output")
        _prepare_new_destination(root, evidence, "evidence directory")
        _prepare_new_destination(root, result_destination, "result report")
        os.link(temporary_output, output)
        published_output = True
''',
    "final destination preparation",
)

test = Path("tools/ai-agent/test_otbm_bounded_patch.py")
marker = '''    def test_post_validation_failure_removes_all_published_artifacts(self) -> None:
'''
addition = '''    def test_rejects_overlapping_destinations_without_creating_collision_path(self) -> None:
        self.write_map()
        plan = self.make_plan([operation("action", "set-action-id", 0, 100, 1000, 1001)])
        with self.assertRaisesRegex(BoundedPatchError, "must be separate"):
            apply_bounded_patch(
                plan=plan,
                source_path=self.source,
                scanner_path=self.scanner,
                artifact_root=self.artifacts,
                output_path=Path("collision"),
                evidence_directory=Path("collision/evidence"),
                result_path=Path("result-overlap.json"),
                timeout_seconds=60,
            )
        self.assertFalse((self.artifacts / "collision").exists())

    def test_output_name_may_match_internal_evidence_name(self) -> None:
        self.write_map()
        plan = self.make_plan([operation("action", "set-action-id", 0, 100, 1000, 1001)])
        result = apply_bounded_patch(
            plan=plan,
            source_path=self.source,
            scanner_path=self.scanner,
            artifact_root=self.artifacts,
            output_path=Path("before.widx"),
            evidence_directory=Path("evidence-reserved-name"),
            result_path=Path("result-reserved-name.json"),
            timeout_seconds=60,
        )
        self.assertTrue((self.artifacts / "before.widx").is_file())
        self.assertEqual(result["output"]["path"], "before.widx")  # type: ignore[index]

''' + marker
replace_once(test, marker, addition, "destination regression tests")

for temporary in (
    Path(".github/workflows/phase8-destination-harden-once.yml"),
    Path("tools/ai-agent/phase8_destination_harden_once.py"),
):
    temporary.unlink(missing_ok=True)
