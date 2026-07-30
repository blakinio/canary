from __future__ import annotations

import argparse
import json
import os
import tempfile
import unittest
from pathlib import Path

from test_tibia_reference_adoption_router import (
    TARGET_OTBM_REPAIR,
    make_gateway,
    make_request,
)
from tibia_reference_adoption_router import canonical_json, sha256_path
from tibia_reference_adoption_router_tool import run


class AdoptionRouterOutputSafetyTests(unittest.TestCase):
    def write_inputs(self, root: Path) -> tuple[Path, Path]:
        gateway = make_gateway("house", {"state": "mismatch", "dimensions": ["footprint"]})
        gateway_path = root / "gateway.json"
        gateway_path.write_text(canonical_json(gateway) + "\n", encoding="utf-8")
        request = make_request(gateway, targets=[TARGET_OTBM_REPAIR])
        request["gateway"]["fileSha256"] = sha256_path(gateway_path)
        request_path = root / "request.json"
        request_path.write_text(canonical_json(request) + "\n", encoding="utf-8")
        return gateway_path, request_path

    def args(
        self,
        gateway: Path,
        request: Path,
        output: Path,
        *,
        overwrite: bool = False,
    ) -> argparse.Namespace:
        return argparse.Namespace(
            gateway_report=gateway,
            request=request,
            output=output,
            overwrite=overwrite,
        )

    def test_create_new_then_overwrite_atomically(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            gateway, request = self.write_inputs(root)
            output = root / "routing.json"
            first = run(self.args(gateway, request, output))
            self.assertTrue(output.is_file())
            on_disk = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(on_disk, first)
            with self.assertRaisesRegex(ValueError, "already exists"):
                run(self.args(gateway, request, output))
            second = run(self.args(gateway, request, output, overwrite=True))
            self.assertEqual(second, first)
            self.assertEqual(json.loads(output.read_text(encoding="utf-8")), first)

    def test_rejects_output_input_alias(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            gateway, request = self.write_inputs(root)
            with self.assertRaisesRegex(ValueError, "alias an input"):
                run(self.args(gateway, request, gateway, overwrite=True))

    def test_rejects_symlink_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            gateway, request = self.write_inputs(root)
            target = root / "target.json"
            target.write_text("{}\n", encoding="utf-8")
            output = root / "routing.json"
            try:
                os.symlink(target, output)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks are unavailable in this environment")
            with self.assertRaisesRegex(ValueError, "must not be a symlink"):
                run(self.args(gateway, request, output, overwrite=True))

    def test_rejects_symlink_input(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            gateway, request = self.write_inputs(root)
            gateway_link = root / "gateway-link.json"
            try:
                os.symlink(gateway, gateway_link)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks are unavailable in this environment")
            with self.assertRaisesRegex(ValueError, "must not be a symlink"):
                run(self.args(gateway_link, request, root / "routing.json"))

    def test_rejects_same_input_for_gateway_and_request(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            gateway, _ = self.write_inputs(root)
            with self.assertRaisesRegex(ValueError, "must be distinct"):
                run(self.args(gateway, gateway, root / "routing.json"))


if __name__ == "__main__":
    unittest.main()
