from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

from otbm_hd import HD_EXPORT_FORMAT, alpha_bytes, decode_png, scale_nearest, validate_override_pack, write_png
from otbm_hd_batch import HDPipelineError, batch_command_argv, run_batch_external


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_export(root: Path, sprite_count: int = 2) -> dict:
    sprites = []
    for sprite_id in range(1, sprite_count + 1):
        rgba = bytes(
            [
                10 * sprite_id,
                20,
                30,
                0,
                40,
                50 * sprite_id,
                60,
                255,
                70,
                80,
                90 * sprite_id,
                128,
                100,
                110,
                120,
                0,
            ]
        )
        path = root / "original" / f"{sprite_id}.png"
        write_png(path, 2, 2, rgba)
        sprites.append(
            {
                "spriteId": sprite_id,
                "itemIds": [100 + sprite_id],
                "useCount": sprite_id,
                "samplePositions": [[1, 2, 7]],
                "source": {
                    "path": f"original/{sprite_id}.png",
                    "width": 2,
                    "height": 2,
                    "pngSha256": _sha(path),
                    "alphaSha256": hashlib.sha256(alpha_bytes(rgba)).hexdigest(),
                    "alphaBounds": [0, 0, 1, 1],
                },
            }
        )
    manifest = {
        "format": HD_EXPORT_FORMAT,
        "ok": True,
        "source": {
            "mapSha256": "map",
            "assetCatalogSha256": "catalog",
            "appearancesSha256": "appearances",
        },
        "sprites": sprites,
    }
    root.mkdir(parents=True, exist_ok=True)
    (root / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    return manifest


def _backend_script(root: Path) -> Path:
    script = root / "fake_batch_backend.py"
    module_root = Path(__file__).resolve().parent
    script.write_text(
        "import argparse,json,sys\n"
        f"sys.path.insert(0,{str(module_root)!r})\n"
        "from pathlib import Path\n"
        "from otbm_hd import decode_png,scale_nearest,write_png\n"
        "p=argparse.ArgumentParser();p.add_argument('--manifest');p.add_argument('--input-dir');p.add_argument('--output-dir');p.add_argument('--scale',type=int);p.add_argument('--counter');p.add_argument('--omit',type=int,default=0);p.add_argument('--fail',action='store_true');a=p.parse_args()\n"
        "counter=Path(a.counter);counter.write_text(str(int(counter.read_text())+1 if counter.exists() else 1))\n"
        "\nif a.fail: raise SystemExit(7)\n"
        "m=json.loads(Path(a.manifest).read_text());assert m['format']=='canary-otbm-hd-batch-input-v1'\n"
        "out=Path(a.output_dir);out.mkdir(parents=True,exist_ok=True)\n"
        "\nfor e in m['sprites']:\n"
        " sid=int(e['spriteId'])\n"
        " if sid==a.omit: continue\n"
        " w,h,rgba=decode_png(Path(a.input_dir)/f'{sid}.png')\n"
        " w,h,rgba=scale_nearest(w,h,rgba,a.scale)\n"
        " rgba=bytes(255 if i%4!=3 else value for i,value in enumerate(rgba))\n"
        " write_png(out/f'{sid}.png',w,h,rgba)\n",
        encoding="utf-8",
    )
    return script


class OTBMHDBatchTests(unittest.TestCase):
    def test_command_template_tokenization(self) -> None:
        argv = batch_command_argv(
            'python backend.py --input-dir "{input_dir}" --output-dir "{output_dir}" --manifest "{manifest}" --scale {scale}',
            input_dir=Path("input dir"),
            output_dir=Path("output dir"),
            manifest_path=Path("batch manifest.json"),
            work_dir=Path("work dir"),
            scale=2,
        )
        self.assertEqual(
            argv,
            [
                "python",
                "backend.py",
                "--input-dir",
                "input dir",
                "--output-dir",
                "output dir",
                "--manifest",
                "batch manifest.json",
                "--scale",
                "2",
            ],
        )

    def test_missing_required_placeholder_is_rejected(self) -> None:
        with self.assertRaises(HDPipelineError):
            batch_command_argv(
                'python backend.py --input-dir "{input_dir}" --output-dir "{output_dir}"',
                input_dir=Path("input"),
                output_dir=Path("output"),
                manifest_path=Path("manifest"),
                work_dir=Path("work"),
                scale=2,
            )

    def test_batch_process_runs_once_and_pack_validates(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            export_root = root / "export"
            source_manifest = _write_export(export_root)
            backend = _backend_script(root)
            counter = root / "counter.txt"
            output_root = root / "overrides"
            command = (
                f'"{sys.executable}" "{backend}" --manifest "{{manifest}}" '
                f'--input-dir "{{input_dir}}" --output-dir "{{output_dir}}" '
                f'--scale {{scale}} --counter "{counter}"'
            )
            result = run_batch_external(export_root, output_root, command=command, scale=2, padding=1)
            validation = validate_override_pack(output_root, export_root=export_root)
            batch_backend = result["backend"]
            width, height, output = decode_png(output_root / "sprites" / "1.png")
            source_width, source_height, source = decode_png(
                export_root / source_manifest["sprites"][0]["source"]["path"]
            )
            _, _, source_scaled = scale_nearest(source_width, source_height, source, 2)
            counter_value = counter.read_text(encoding="utf-8")
        self.assertTrue(result["ok"])
        self.assertTrue(validation["ok"])
        self.assertEqual(counter_value, "1")
        self.assertEqual(result["summary"], {"spriteCount": 2, "staged": 2, "accepted": 2, "rejected": 0})
        self.assertEqual(batch_backend["invocations"], 1)
        self.assertNotIn("command", batch_backend)
        self.assertEqual((width, height), (4, 4))
        self.assertEqual(alpha_bytes(output), alpha_bytes(source_scaled))

    def test_missing_backend_output_rejects_only_that_sprite(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            export_root = root / "export"
            _write_export(export_root)
            backend = _backend_script(root)
            counter = root / "counter.txt"
            output_root = root / "overrides"
            command = (
                f'"{sys.executable}" "{backend}" --manifest "{{manifest}}" '
                f'--input-dir "{{input_dir}}" --output-dir "{{output_dir}}" '
                f'--scale {{scale}} --counter "{counter}" --omit 2'
            )
            result = run_batch_external(export_root, output_root, command=command, scale=2, padding=1)
            validation = validate_override_pack(output_root, export_root=export_root)
        self.assertFalse(result["ok"])
        self.assertTrue(validation["ok"])
        self.assertEqual(result["summary"]["accepted"], 1)
        self.assertEqual(result["summary"]["rejected"], 1)
        rejected = next(entry for entry in result["sprites"] if entry["spriteId"] == 2)
        self.assertIn("did not create", rejected["errors"][0])

    def test_failed_batch_rejects_all_staged_sprites(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            export_root = root / "export"
            _write_export(export_root)
            backend = _backend_script(root)
            counter = root / "counter.txt"
            output_root = root / "overrides"
            command = (
                f'"{sys.executable}" "{backend}" --manifest "{{manifest}}" '
                f'--input-dir "{{input_dir}}" --output-dir "{{output_dir}}" '
                f'--scale {{scale}} --counter "{counter}" --fail'
            )
            result = run_batch_external(export_root, output_root, command=command, scale=2, padding=1)
            validation = validate_override_pack(output_root, export_root=export_root)
        self.assertFalse(result["ok"])
        self.assertTrue(validation["ok"])
        self.assertEqual(result["summary"]["accepted"], 0)
        self.assertEqual(result["summary"]["rejected"], 2)
        self.assertEqual(result["backend"]["process"]["returnCode"], 7)

    def test_nonempty_output_requires_explicit_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            export_root = root / "export"
            _write_export(export_root, sprite_count=0)
            output_root = root / "overrides"
            output_root.mkdir()
            (output_root / "unrelated.txt").write_text("keep", encoding="utf-8")
            with self.assertRaises(HDPipelineError):
                run_batch_external(
                    export_root,
                    output_root,
                    command='python backend.py --input-dir "{input_dir}" --output-dir "{output_dir}" --manifest "{manifest}"',
                )
            with self.assertRaises(HDPipelineError):
                run_batch_external(
                    export_root,
                    output_root,
                    command='python backend.py --input-dir "{input_dir}" --output-dir "{output_dir}" --manifest "{manifest}"',
                    overwrite=True,
                )

    def test_source_path_escape_is_rejected_per_sprite(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            export_root = root / "export"
            manifest = _write_export(export_root, sprite_count=1)
            outside = root / "outside.png"
            outside.write_bytes((export_root / "original" / "1.png").read_bytes())
            manifest["sprites"][0]["source"]["path"] = "../outside.png"
            manifest["sprites"][0]["source"]["pngSha256"] = _sha(outside)
            (export_root / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            output_root = root / "overrides"
            result = run_batch_external(
                export_root,
                output_root,
                command='python backend.py --input-dir "{input_dir}" --output-dir "{output_dir}" --manifest "{manifest}"',
            )
        self.assertFalse(result["ok"])
        self.assertEqual(result["summary"]["staged"], 0)
        self.assertIn("escapes", result["sprites"][0]["errors"][0])

    def test_missing_executable_rejects_all_without_raising(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            export_root = root / "export"
            _write_export(export_root, sprite_count=1)
            result = run_batch_external(
                export_root,
                root / "overrides",
                command='definitely-not-an-executable --input-dir "{input_dir}" --output-dir "{output_dir}" --manifest "{manifest}"',
            )
        self.assertFalse(result["ok"])
        self.assertEqual(result["summary"]["rejected"], 1)
        self.assertIn("could not start", result["sprites"][0]["errors"][0])

    @unittest.skipIf(os.name == "nt", "symlink creation requires elevated privileges on many Windows runners")
    def test_symlinked_backend_output_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            export_root = root / "export"
            _write_export(export_root, sprite_count=1)
            output_root = root / "overrides"
            backend = root / "symlink_backend.py"
            backend.write_text(
                "import argparse\nfrom pathlib import Path\np=argparse.ArgumentParser();p.add_argument('--input-dir');p.add_argument('--output-dir');p.add_argument('--manifest');a=p.parse_args()\nout=Path(a.output_dir);out.mkdir(parents=True,exist_ok=True);(out/'1.png').symlink_to(Path(a.input_dir)/'1.png')\n",
                encoding="utf-8",
            )
            command = (
                f'"{sys.executable}" "{backend}" --manifest "{{manifest}}" '
                f'--input-dir "{{input_dir}}" --output-dir "{{output_dir}}"'
            )
            result = run_batch_external(export_root, output_root, command=command, scale=2, padding=1)
        self.assertFalse(result["ok"])
        self.assertIn("symlink", result["sprites"][0]["errors"][0])


if __name__ == "__main__":
    unittest.main()
