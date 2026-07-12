from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
import sys
from pathlib import Path

from otbm_hd import (
    HD_EXPORT_FORMAT,
    _command_argv,
    alpha_bounds,
    alpha_bytes,
    crop_image,
    decode_png,
    pad_image,
    restore_alpha,
    scale_nearest,
    upscale_export,
    validate_override_pack,
    write_png,
)


class OTBMHDPipelineTests(unittest.TestCase):
    def test_png_round_trip_and_alpha_bounds(self) -> None:
        rgba = bytes(
            [
                0, 0, 0, 0,
                255, 0, 0, 255,
                0, 255, 0, 128,
                0, 0, 0, 0,
            ]
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sprite.png"
            write_png(path, 2, 2, rgba)
            width, height, decoded = decode_png(path)
        self.assertEqual((width, height), (2, 2))
        self.assertEqual(decoded, rgba)
        self.assertEqual(alpha_bounds(width, height, decoded), [0, 0, 1, 1])

    def test_padding_scale_crop_and_alpha_restore(self) -> None:
        source = bytes(
            [
                10, 20, 30, 0,
                40, 50, 60, 255,
                70, 80, 90, 128,
                100, 110, 120, 0,
            ]
        )
        padded_width, padded_height, padded = pad_image(2, 2, source, 1)
        scaled_width, scaled_height, scaled = scale_nearest(padded_width, padded_height, padded, 2)
        width, height, cropped = crop_image(scaled_width, scaled_height, scaled, 2, 2, 2, 2)
        _, _, source_scaled = scale_nearest(2, 2, source, 2)
        model = bytes((255 if index % 4 != 3 else value) for index, value in enumerate(cropped))
        restored = restore_alpha(model, source_scaled)
        self.assertEqual((width, height), (4, 4))
        self.assertEqual(alpha_bytes(restored), alpha_bytes(source_scaled))
        for index in range(0, len(restored), 4):
            if restored[index + 3] == 0:
                self.assertEqual(restored[index : index + 3], b"\x00\x00\x00")

    def test_nearest_override_pack_validates(self) -> None:
        rgba = bytes([255, 255, 255, 255] * 4)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            export_root = root / "export"
            source_path = export_root / "original" / "7.png"
            write_png(source_path, 2, 2, rgba)
            source_sha = hashlib.sha256(source_path.read_bytes()).hexdigest()
            export_manifest = {
                "format": HD_EXPORT_FORMAT,
                "ok": True,
                "source": {
                    "mapSha256": "map",
                    "assetCatalogSha256": "catalog",
                    "appearancesSha256": "appearances",
                },
                "sprites": [
                    {
                        "spriteId": 7,
                        "itemIds": [100],
                        "useCount": 1,
                        "samplePositions": [[1, 2, 7]],
                        "source": {
                            "path": "original/7.png",
                            "width": 2,
                            "height": 2,
                            "pngSha256": source_sha,
                            "alphaSha256": hashlib.sha256(alpha_bytes(rgba)).hexdigest(),
                            "alphaBounds": [0, 0, 1, 1],
                        },
                    }
                ],
            }
            export_root.mkdir(parents=True, exist_ok=True)
            (export_root / "manifest.json").write_text(json.dumps(export_manifest), encoding="utf-8")
            override_root = root / "overrides"
            result = upscale_export(export_root, override_root, scale=2, padding=1, backend="nearest")
            validation = validate_override_pack(override_root, export_root=export_root)
        self.assertTrue(result["ok"])
        self.assertEqual(result["summary"], {"spriteCount": 1, "accepted": 1, "rejected": 0})
        self.assertTrue(validation["ok"])
        self.assertEqual(validation["summary"]["validAccepted"], 1)

    def test_external_backend_runs_without_shell_and_restores_alpha(self) -> None:
        rgba = bytes(
            [
                10, 20, 30, 0,
                40, 50, 60, 255,
                70, 80, 90, 128,
                100, 110, 120, 0,
            ]
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            export_root = root / "export"
            source_path = export_root / "original" / "7.png"
            write_png(source_path, 2, 2, rgba)
            source_sha = hashlib.sha256(source_path.read_bytes()).hexdigest()
            export_manifest = {
                "format": HD_EXPORT_FORMAT,
                "ok": True,
                "source": {"mapSha256": "map", "assetCatalogSha256": "catalog", "appearancesSha256": "appearances"},
                "sprites": [{
                    "spriteId": 7,
                    "source": {"path": "original/7.png", "width": 2, "height": 2, "pngSha256": source_sha},
                }],
            }
            export_root.mkdir(parents=True, exist_ok=True)
            (export_root / "manifest.json").write_text(json.dumps(export_manifest), encoding="utf-8")
            module_root = Path(__file__).resolve().parent
            backend = root / "backend.py"
            backend.write_text(
                "import argparse, sys\n"
                f"sys.path.insert(0, {str(module_root)!r})\n"
                f"sys.path.insert(0, {str(module_root / 'stubs')!r})\n"
                "from pathlib import Path\n"
                "from otbm_hd import decode_png, scale_nearest, write_png\n"
                "p=argparse.ArgumentParser();p.add_argument('--input');p.add_argument('--output');p.add_argument('--scale',type=int);a=p.parse_args()\n"
                "w,h,rgba=decode_png(Path(a.input));w,h,rgba=scale_nearest(w,h,rgba,a.scale)\n"
                "rgba=bytes(255 if i%4==3 else value for i,value in enumerate(rgba))\n"
                "write_png(Path(a.output),w,h,rgba)\n",
                encoding="utf-8",
            )
            command = f'"{sys.executable}" "{backend}" --input "{{input}}" --output "{{output}}" --scale {{scale}}'
            override_root = root / "overrides"
            result = upscale_export(
                export_root,
                override_root,
                scale=2,
                padding=1,
                backend="external",
                command=command,
            )
            validation = validate_override_pack(override_root, export_root=export_root)
            width, height, output = decode_png(override_root / "sprites" / "7.png")
            _, _, expected = scale_nearest(2, 2, rgba, 2)
        self.assertTrue(result["ok"])
        self.assertTrue(validation["ok"])
        self.assertEqual((width, height), (4, 4))
        self.assertEqual(alpha_bytes(output), alpha_bytes(expected))

    def test_rejected_sprite_is_valid_fallback_state(self) -> None:
        rgba = bytes([255, 255, 255, 255] * 4)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            export_root = root / "export"
            source_path = export_root / "original" / "7.png"
            write_png(source_path, 2, 2, rgba)
            source_sha = hashlib.sha256(source_path.read_bytes()).hexdigest()
            export_manifest = {
                "format": HD_EXPORT_FORMAT,
                "ok": True,
                "source": {"mapSha256": "map", "assetCatalogSha256": "catalog", "appearancesSha256": "appearances"},
                "sprites": [{"spriteId": 7, "source": {"path": "original/7.png", "width": 2, "height": 2, "pngSha256": source_sha}}],
            }
            export_root.mkdir(parents=True, exist_ok=True)
            export_manifest_path = export_root / "manifest.json"
            export_manifest_path.write_text(json.dumps(export_manifest), encoding="utf-8")
            override_root = root / "overrides"
            override_root.mkdir()
            override_manifest = {
                "format": "canary-otbm-hd-sprite-overrides-v1",
                "sourceExport": {
                    "path": str(export_manifest_path),
                    "sha256": hashlib.sha256(export_manifest_path.read_bytes()).hexdigest(),
                },
                "scale": 2,
                "sprites": [{"spriteId": 7, "status": "rejected", "errors": ["model failed"]}],
            }
            (override_root / "manifest.json").write_text(json.dumps(override_manifest), encoding="utf-8")
            validation = validate_override_pack(override_root, export_root=export_root)
        self.assertTrue(validation["ok"])
        self.assertEqual(validation["summary"]["accepted"], 0)
        self.assertEqual(validation["summary"]["rejected"], 1)

    def test_external_command_template_is_tokenized_without_shell(self) -> None:
        argv = _command_argv(
            'python backend.py --input "{input}" --output "{output}" --scale {scale} --id {sprite_id}',
            input_path=Path("input file.png"),
            output_path=Path("output file.png"),
            scale=2,
            sprite_id=42,
        )
        self.assertEqual(
            argv,
            [
                "python",
                "backend.py",
                "--input",
                "input file.png",
                "--output",
                "output file.png",
                "--scale",
                "2",
                "--id",
                "42",
            ],
        )


if __name__ == "__main__":
    unittest.main()
