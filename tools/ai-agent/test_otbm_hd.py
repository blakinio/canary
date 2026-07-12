from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from otbm_hd import (
    HD_EXPORT_FORMAT,
    HD_OVERRIDE_FORMAT,
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
        model = bytearray(cropped)
        for index in range(0, len(model), 4):
            model[index : index + 3] = b"\xff\xff\xff"
            model[index + 3] = 255
        restored = restore_alpha(bytes(model), source_scaled)
        self.assertEqual((width, height), (4, 4))
        self.assertEqual(alpha_bytes(restored), alpha_bytes(source_scaled))
        for index in range(0, len(restored), 4):
            if restored[index + 3] == 0:
                self.assertEqual(restored[index : index + 3], b"\x00\x00\x00")

    def test_external_command_template_is_tokenized_without_shell(self) -> None:
        argv = _command_argv(
            'python tool.py --input "{input}" --output "{output}" --scale {scale} --id {sprite_id}',
            input_path=Path("input file.png"),
            output_path=Path("output file.png"),
            scale=2,
            sprite_id=123,
        )
        self.assertEqual(
            argv,
            [
                "python",
                "tool.py",
                "--input",
                "input file.png",
                "--output",
                "output file.png",
                "--scale",
                "2",
                "--id",
                "123",
            ],
        )

    def test_nearest_pack_round_trip_validation(self) -> None:
        rgba = bytes(
            [
                0, 0, 0, 0,
                10, 20, 30, 255,
                40, 50, 60, 128,
                0, 0, 0, 0,
            ]
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            export_root = root / "export"
            original = export_root / "original" / "77.png"
            write_png(original, 2, 2, rgba)
            source_sha = hashlib.sha256(original.read_bytes()).hexdigest()
            export_manifest = {
                "format": HD_EXPORT_FORMAT,
                "ok": True,
                "source": {
                    "mapSha256": "map-sha",
                    "assetCatalogSha256": "catalog-sha",
                    "appearancesSha256": "appearances-sha",
                },
                "sprites": [
                    {
                        "spriteId": 77,
                        "source": {
                            "path": "original/77.png",
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
            manifest = upscale_export(export_root, override_root, scale=2, padding=1, backend="nearest")
            self.assertEqual(manifest["format"], HD_OVERRIDE_FORMAT)
            self.assertTrue(manifest["ok"])
            validation = validate_override_pack(override_root, export_root=export_root)
            self.assertTrue(validation["ok"])
            self.assertEqual(validation["summary"]["validAccepted"], 1)
            width, height, output = decode_png(override_root / "sprites" / "77.png")
            self.assertEqual((width, height), (4, 4))
            _, _, scaled_source = scale_nearest(2, 2, rgba, 2)
            self.assertEqual(output, scaled_source)


if __name__ == "__main__":
    unittest.main()
