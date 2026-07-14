from __future__ import annotations

from pathlib import Path


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: found {count} source matches, expected 1")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def replace_section(path: Path, start: str, end: str, replacement: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if text.count(start) != 1 or text.count(end) != 1:
        raise SystemExit(
            f"{label}: start count {text.count(start)}, end count {text.count(end)}, expected 1/1"
        )
    first = text.index(start)
    last = text.index(end, first)
    path.write_text(text[:first] + replacement + text[last:], encoding="utf-8")


types = Path("tools/ai-agent/otbm_bounded_patch_types.py")
replace_once(
    types,
    '        sha256 = _text(value["sha256"], "source.sha256").lower()\n',
    '        sha256 = _text(value["sha256"], "source.sha256")\n',
    "lowercase SHA normalization",
)

patcher = Path("tools/ai-agent/otbm_bounded_patch.py")
replace_once(
    patcher,
    "from typing import Any, Iterable, Mapping, Sequence\n",
    "from typing import Any, Mapping, Sequence\n",
    "unused Iterable import",
)
replace_once(
    patcher,
    "MARKER_BYTES = {0xFD, 0xFE, 0xFF}\n",
    "",
    "unused marker constant",
)
replace_section(
    patcher,
    "def _write_json(path: Path, value: Mapping[str, Any]) -> None:\n",
    "def _run_scanner(scanner: Path, arguments: Sequence[str], *, timeout_seconds: int) -> subprocess.CompletedProcess[str]:\n",
    '''def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    encoded = (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\\n").encode("utf-8")
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    linked = False
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, path)
        linked = True
        temporary.unlink()
        _fsync_directory(path.parent)
    except Exception:
        if linked:
            path.unlink(missing_ok=True)
        temporary.unlink(missing_ok=True)
        raise


def _publish_directory_no_overwrite(source: Path, destination: Path) -> None:
    destination.mkdir(mode=0o700)
    try:
        for child in sorted(source.iterdir(), key=lambda candidate: candidate.name):
            if child.is_symlink() or not child.is_file():
                raise BoundedPatchError(f"evidence workspace contains a non-regular entry: {child}")
            published = destination / child.name
            os.link(child, published)
            child.unlink()
        source.rmdir()
        _fsync_directory(destination)
        _fsync_directory(destination.parent)
    except Exception:
        shutil.rmtree(destination, ignore_errors=True)
        raise


''',
    "atomic JSON and evidence publication section",
)
replace_once(
    patcher,
    "    published_output = False\n    published_evidence = False\n    try:\n",
    "    published_output = False\n    published_evidence = False\n    published_result = False\n    try:\n",
    "publication flags",
)
replace_once(
    patcher,
    "        os.rename(workspace, evidence)\n        published_evidence = True\n        _fsync_directory(evidence.parent)\n        _write_json(result_destination, result)\n        return result\n",
    "        _publish_directory_no_overwrite(workspace, evidence)\n        published_evidence = True\n        _write_json(result_destination, result)\n        published_result = True\n        return result\n",
    "evidence/result publication",
)
replace_once(
    patcher,
    "        if not result_destination.exists():\n            if published_output:\n                output.unlink(missing_ok=True)\n            if published_evidence:\n                shutil.rmtree(evidence, ignore_errors=True)\n",
    "        if not published_result:\n            if published_output:\n                output.unlink(missing_ok=True)\n            if published_evidence:\n                shutil.rmtree(evidence, ignore_errors=True)\n",
    "failure cleanup guard",
)

test = Path("tools/ai-agent/test_otbm_bounded_patch.py")
replace_once(
    test,
    "from unittest import mock\n\nfrom otbm_bounded_patch import apply_bounded_patch\n",
    "from unittest import mock\n\nimport otbm_bounded_patch\nfrom otbm_bounded_patch import apply_bounded_patch\n",
    "test module import",
)
marker = '    @unittest.skipUnless(hasattr(os, "symlink"), "symlinks are unavailable")\n'
addition = '''    def test_result_publication_failure_removes_output_and_evidence(self) -> None:
        self.write_map()
        original = self.source.read_bytes()
        plan = self.make_plan([operation("action", "set-action-id", 0, 100, 1000, 1001)])
        original_write_json = otbm_bounded_patch._write_json

        def fail_result(path: Path, value: object) -> None:
            if path.name == "result.json":
                raise OSError("simulated result publication failure")
            original_write_json(path, value)  # type: ignore[arg-type]

        with mock.patch("otbm_bounded_patch._write_json", side_effect=fail_result):
            with self.assertRaisesRegex(OSError, "simulated result publication failure"):
                self.apply(plan)
        self.assertEqual(self.source.read_bytes(), original)
        self.assertFalse((self.artifacts / "patched.otbm").exists())
        self.assertFalse((self.artifacts / "evidence").exists())
        self.assertFalse((self.artifacts / "result.json").exists())

'''
replace_once(test, marker, addition + marker, "result publication failure test")

for temporary in (
    Path(".github/workflows/phase8-hardening-once.yml"),
    Path("tools/ai-agent/phase8_harden_once.py"),
):
    temporary.unlink(missing_ok=True)
