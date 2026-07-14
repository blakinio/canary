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
    '''def _new_confined_path(root: Path, path: Path, label: str) -> Path:
    candidate = path.expanduser()
    candidate = candidate if candidate.is_absolute() else root / candidate
    if candidate.is_symlink():
        raise BoundedPatchError(f"{label} must not be a symlink: {candidate}")
    resolved = candidate.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise BoundedPatchError(f"{label} escapes artifact root {root}: {resolved}") from exc
    _check_ancestors(root, resolved, label)
    if resolved.exists():
        raise BoundedPatchError(f"{label} already exists: {resolved}")
    resolved.parent.mkdir(parents=True, exist_ok=True)
    _check_ancestors(root, resolved, label)
    return resolved
''',
    '''def _new_confined_path(root: Path, path: Path, label: str) -> Path:
    candidate = path.expanduser()
    candidate = candidate if candidate.is_absolute() else root / candidate
    lexical = Path(os.path.abspath(candidate))
    try:
        lexical.relative_to(root)
    except ValueError as exc:
        raise BoundedPatchError(f"{label} escapes artifact root {root}: {lexical}") from exc
    if lexical.is_symlink():
        raise BoundedPatchError(f"{label} must not be a symlink: {lexical}")
    _check_ancestors(root, lexical, label)
    resolved = lexical.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise BoundedPatchError(f"{label} escapes artifact root {root}: {resolved}") from exc
    _check_ancestors(root, resolved, label)
    if resolved.exists():
        raise BoundedPatchError(f"{label} already exists: {resolved}")
    resolved.parent.mkdir(parents=True, exist_ok=True)
    _check_ancestors(root, lexical, label)
    _check_ancestors(root, resolved, label)
    return resolved
''',
    "confined path symlink ancestry",
)
replace_once(
    patcher,
    '''    allowed: set[int] = set()
    for operation in operations:
        for span in operation["spans"]:
            start = int(span["offset"])
            allowed.update(range(start, start + int(span["size"])))
''',
    '''    allowed: set[int] = set()
    for operation in operations:
        for byte in operation["bytes"]:
            offset = int(byte["offset"])
            encoded_size = int(byte["encodedSize"])
            allowed.add(offset + (1 if encoded_size == 2 else 0))
''',
    "payload-only changed-offset allowlist",
)

test = Path("tools/ai-agent/test_otbm_bounded_patch.py")
symlink_marker = '''    @unittest.skipUnless(hasattr(os, "symlink"), "symlinks are unavailable")
    def test_rejects_symlink_output(self) -> None:
'''
symlink_addition = '''    @unittest.skipUnless(hasattr(os, "symlink"), "symlinks are unavailable")
    def test_rejects_symlink_parent_inside_artifact_root(self) -> None:
        self.write_map()
        plan = self.make_plan([operation("action", "set-action-id", 0, 100, 1000, 1001)])
        self.artifacts.mkdir()
        real_parent = self.artifacts / "real-parent"
        real_parent.mkdir()
        os.symlink(real_parent, self.artifacts / "redirect", target_is_directory=True)
        with self.assertRaisesRegex(BoundedPatchError, "symlink"):
            apply_bounded_patch(
                plan=plan,
                source_path=self.source,
                scanner_path=self.scanner,
                artifact_root=self.artifacts,
                output_path=Path("redirect/patched.otbm"),
                evidence_directory=Path("evidence-symlink-parent"),
                result_path=Path("result-symlink-parent.json"),
                timeout_seconds=60,
            )

''' + symlink_marker
replace_once(test, symlink_marker, symlink_addition, "symlink-parent regression test")

class_marker = '''class BoundedPatchPlanTests(unittest.TestCase):
'''
primitive_class = '''class BoundedPatchPrimitiveTests(unittest.TestCase):
    def test_escape_prefix_is_not_an_allowed_changed_payload_byte(self) -> None:
        temporary = Path(tempfile.mkdtemp(prefix="otbm-payload-offset-test-"))
        try:
            source = temporary / "source.bin"
            output = temporary / "output.bin"
            source.write_bytes(bytes((NODE_ESCAPE, NODE_ESCAPE)))
            output.write_bytes(bytes((0xFC, NODE_ESCAPE)))
            operations = [
                {
                    "bytes": [{"offset": 0, "encodedSize": 2, "value": NODE_ESCAPE}],
                    "spans": [{"offset": 0, "size": 2}],
                }
            ]
            with self.assertRaisesRegex(BoundedPatchError, "unplanned physical byte change at offset 0"):
                otbm_bounded_patch._compare_outside_spans(source, output, operations)
        finally:
            shutil.rmtree(temporary, ignore_errors=True)


''' + class_marker
replace_once(test, class_marker, primitive_class, "payload-prefix regression test")

uppercase_marker = '''    def test_rejects_duplicate_target(self) -> None:
'''
uppercase_test = '''    def test_rejects_uppercase_source_hash(self) -> None:
        raw = {
            "format": "canary-otbm-bounded-patch-plan-v1",
            "source": {
                "fileName": "map.otbm",
                "sha256": "A" * 64,
                "size": 10,
                "otbmVersion": 4,
                "itemsMajor": 3,
                "itemsMinor": 57,
            },
            "region": {"from": [1000, 2000, 7], "to": [1100, 2200, 7]},
            "operations": [operation("action", "set-action-id", 0, 100, 1, 2)],
        }
        with self.assertRaisesRegex(BoundedPatchError, "lowercase SHA-256"):
            PatchPlan.from_raw(raw)

''' + uppercase_marker
replace_once(test, uppercase_marker, uppercase_test, "uppercase hash regression test")

for temporary in (
    Path(".github/workflows/phase8-final-harden-once.yml"),
    Path("tools/ai-agent/phase8_final_harden_once.py"),
):
    temporary.unlink(missing_ok=True)
