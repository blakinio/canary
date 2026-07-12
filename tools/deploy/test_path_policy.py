from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from path_policy import PathEscapesRootError, resolve_within_root


class PathPolicyTests(unittest.TestCase):
    def test_accepts_path_within_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "sub").mkdir()
            resolved = resolve_within_root("sub/file.txt", root)
            self.assertEqual(resolved, (root / "sub/file.txt").resolve())

    def test_rejects_dot_dot_traversal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "root"
            root.mkdir()
            with self.assertRaises(PathEscapesRootError):
                resolve_within_root("../outside.txt", root)

    def test_rejects_absolute_path_outside_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "root"
            root.mkdir()
            with self.assertRaises(PathEscapesRootError):
                resolve_within_root(Path(tmp) / "elsewhere.txt", root)

    def test_rejects_symlink_escape(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "root"
            root.mkdir()
            outside = Path(tmp) / "outside"
            outside.mkdir()
            (outside / "secret.txt").write_text("nope", encoding="utf-8")
            escape_link = root / "escape"
            escape_link.symlink_to(outside, target_is_directory=True)

            with self.assertRaises(PathEscapesRootError):
                resolve_within_root("escape/secret.txt", root)

    def test_rejects_symlink_escape_at_leaf(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "root"
            root.mkdir()
            outside_file = Path(tmp) / "outside.txt"
            outside_file.write_text("nope", encoding="utf-8")
            leaf_link = root / "link.txt"
            leaf_link.symlink_to(outside_file)

            with self.assertRaises(PathEscapesRootError):
                resolve_within_root("link.txt", root)

    def test_root_must_already_exist(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            missing_root = Path(tmp) / "does-not-exist"
            with self.assertRaises(OSError):
                resolve_within_root("file.txt", missing_root)


if __name__ == "__main__":
    unittest.main()
