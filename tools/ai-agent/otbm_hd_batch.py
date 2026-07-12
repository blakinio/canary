from __future__ import annotations

import hashlib
import json
import shlex
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from otbm_hd import (
    HD_EXPORT_FORMAT,
    HD_OVERRIDE_FORMAT,
    HDPipelineError,
    alpha_bounds,
    alpha_bytes,
    crop_image,
    decode_png,
    pad_image,
    restore_alpha,
    scale_nearest,
    write_png,
)

BATCH_INPUT_FORMAT = "canary-otbm-hd-batch-input-v1"
MAX_CAPTURE_CHARS = 4000


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise HDPipelineError(f"JSON root must be an object: {path}")
    return payload


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _reset_output_root(output_root: Path, *, overwrite: bool) -> None:
    if output_root.is_symlink():
        raise HDPipelineError("Output root must not be a symlink")
    if output_root.exists() and not output_root.is_dir():
        raise HDPipelineError("Output root must be a directory")
    if output_root.exists() and any(output_root.iterdir()):
        if not overwrite:
            raise HDPipelineError("Output root is not empty; choose a new directory or pass overwrite=True")
        for name in ("manifest.json", "sprites", "work"):
            target = output_root / name
            if target.is_symlink():
                target.unlink()
            elif target.is_dir():
                shutil.rmtree(target)
            elif target.exists():
                target.unlink()
        leftovers = [path.name for path in output_root.iterdir()]
        if leftovers:
            raise HDPipelineError(f"Output root contains unrelated files that overwrite will not remove: {leftovers[:5]}")
    output_root.mkdir(parents=True, exist_ok=True)


def batch_command_argv(
    template: str,
    *,
    input_dir: Path,
    output_dir: Path,
    manifest_path: Path,
    work_dir: Path,
    scale: int,
) -> list[str]:
    if not template.strip():
        raise HDPipelineError("Batch external backend requires a non-empty command template")
    required = ("{input_dir}", "{output_dir}", "{manifest}")
    missing = [marker for marker in required if marker not in template]
    if missing:
        raise HDPipelineError(f"Batch command template is missing required placeholders: {', '.join(missing)}")
    replacements = {
        "{input_dir}": str(input_dir),
        "{output_dir}": str(output_dir),
        "{manifest}": str(manifest_path),
        "{work_dir}": str(work_dir),
        "{scale}": str(scale),
    }
    argv: list[str] = []
    for token in shlex.split(template):
        for marker, value in replacements.items():
            token = token.replace(marker, value)
        argv.append(token)
    if not argv:
        raise HDPipelineError("Batch external backend command is empty")
    return argv


def _regular_output(path: Path, output_dir: Path) -> None:
    if path.is_symlink():
        raise HDPipelineError("Backend output must not be a symlink")
    if not path.is_file():
        raise HDPipelineError("Backend did not create the requested output PNG")
    try:
        path.resolve().relative_to(output_dir.resolve())
    except ValueError as exc:
        raise HDPipelineError("Backend output escaped the batch output directory") from exc


def run_batch_external(
    export_root: Path,
    output_root: Path,
    *,
    command: str,
    scale: int = 2,
    padding: int = 4,
    timeout_seconds: int = 1800,
    keep_work: bool = False,
    overwrite: bool = False,
) -> dict[str, Any]:
    if scale < 2 or scale > 8:
        raise HDPipelineError("scale must be between 2 and 8")
    if padding < 0 or padding > 64:
        raise HDPipelineError("padding must be between 0 and 64")
    if timeout_seconds <= 0:
        raise HDPipelineError("timeout_seconds must be positive")

    export_path = export_root / "manifest.json"
    export_manifest = _load_json(export_path)
    if export_manifest.get("format") != HD_EXPORT_FORMAT:
        raise HDPipelineError(f"Unsupported export manifest format: {export_manifest.get('format')}")
    raw_sprites = export_manifest.get("sprites")
    if not isinstance(raw_sprites, list):
        raise HDPipelineError("Export manifest has no sprite list")

    _reset_output_root(output_root, overwrite=overwrite)
    output_sprites = output_root / "sprites"
    output_sprites.mkdir(parents=True, exist_ok=True)

    temp: tempfile.TemporaryDirectory[str] | None = None
    if keep_work:
        work_root = output_root / "work"
        work_root.mkdir(parents=True, exist_ok=True)
    else:
        temp = tempfile.TemporaryDirectory(prefix="otbm-hd-batch-")
        work_root = Path(temp.name)
    input_dir = work_root / "input"
    raw_output_dir = work_root / "output"
    input_dir.mkdir(parents=True, exist_ok=True)
    raw_output_dir.mkdir(parents=True, exist_ok=True)

    result_by_id: dict[int, dict[str, Any]] = {}
    staged_by_id: dict[int, dict[str, Any]] = {}
    seen_sprite_ids: set[int] = set()
    batch_inputs: list[dict[str, Any]] = []
    process: dict[str, Any] | None = None

    try:
        for raw_entry in raw_sprites:
            if not isinstance(raw_entry, dict) or not isinstance(raw_entry.get("spriteId"), int):
                continue
            sprite_id = int(raw_entry["spriteId"])
            if sprite_id in seen_sprite_ids:
                raise HDPipelineError(f"Export manifest contains duplicate sprite ID {sprite_id}")
            seen_sprite_ids.add(sprite_id)
            result: dict[str, Any] = {"spriteId": sprite_id, "status": "rejected", "errors": []}
            result_by_id[sprite_id] = result
            try:
                source = raw_entry.get("source")
                if not isinstance(source, dict) or not isinstance(source.get("path"), str):
                    raise HDPipelineError("Source metadata is missing")
                source_path = export_root / source["path"]
                try:
                    source_path.resolve().relative_to(export_root.resolve())
                except ValueError as exc:
                    raise HDPipelineError("Source PNG path escapes the export directory") from exc
                if source_path.is_symlink():
                    raise HDPipelineError("Source PNG must not be a symlink")
                expected_sha = source.get("pngSha256")
                if not isinstance(expected_sha, str) or _sha256_path(source_path) != expected_sha:
                    raise HDPipelineError("Source PNG hash does not match export manifest")
                width, height, rgba = decode_png(source_path)
                if width != source.get("width") or height != source.get("height"):
                    raise HDPipelineError("Source PNG dimensions do not match export manifest")
                padded_width, padded_height, padded = pad_image(width, height, rgba, padding)
                staged_path = input_dir / f"{sprite_id}.png"
                write_png(staged_path, padded_width, padded_height, padded)
                staged = {
                    "spriteId": sprite_id,
                    "sourcePngSha256": expected_sha,
                    "sourceWidth": width,
                    "sourceHeight": height,
                    "sourceRgba": rgba,
                    "paddedWidth": padded_width,
                    "paddedHeight": padded_height,
                    "inputPath": staged_path,
                    "rawOutputPath": raw_output_dir / f"{sprite_id}.png",
                }
                staged_by_id[sprite_id] = staged
                batch_inputs.append(
                    {
                        "spriteId": sprite_id,
                        "input": staged_path.relative_to(work_root).as_posix(),
                        "output": staged["rawOutputPath"].relative_to(work_root).as_posix(),
                        "source": {
                            "width": width,
                            "height": height,
                            "pngSha256": expected_sha,
                        },
                        "padded": {"width": padded_width, "height": padded_height},
                        "expectedOutput": {"width": padded_width * scale, "height": padded_height * scale},
                    }
                )
            except (OSError, HDPipelineError) as exc:
                result["errors"].append(str(exc))

        batch_manifest_path = work_root / "batch-manifest.json"
        batch_manifest = {
            "format": BATCH_INPUT_FORMAT,
            "scale": scale,
            "padding": padding,
            "inputDirectory": str(input_dir.resolve()),
            "outputDirectory": str(raw_output_dir.resolve()),
            "summary": {"exportedSprites": len(result_by_id), "stagedSprites": len(batch_inputs)},
            "sprites": batch_inputs,
        }
        _write_json(batch_manifest_path, batch_manifest)

        if batch_inputs:
            argv = batch_command_argv(
                command,
                input_dir=input_dir,
                output_dir=raw_output_dir,
                manifest_path=batch_manifest_path,
                work_dir=work_root,
                scale=scale,
            )
            try:
                completed = subprocess.run(
                    argv,
                    capture_output=True,
                    text=True,
                    timeout=timeout_seconds,
                    check=False,
                    shell=False,
                )
                process = {
                    "returnCode": completed.returncode,
                    "stdout": completed.stdout[-MAX_CAPTURE_CHARS:],
                    "stderr": completed.stderr[-MAX_CAPTURE_CHARS:],
                }
            except subprocess.TimeoutExpired as exc:
                process = {
                    "returnCode": None,
                    "timedOut": True,
                    "stdout": (exc.stdout or "")[-MAX_CAPTURE_CHARS:] if isinstance(exc.stdout, str) else "",
                    "stderr": (exc.stderr or "")[-MAX_CAPTURE_CHARS:] if isinstance(exc.stderr, str) else "",
                }
            except OSError as exc:
                process = {
                    "returnCode": None,
                    "startError": str(exc),
                    "stdout": "",
                    "stderr": "",
                }

            if process.get("returnCode") != 0:
                if process.get("timedOut"):
                    reason = "Batch external command timed out"
                elif process.get("startError"):
                    reason = f"Batch external command could not start: {process['startError']}"
                else:
                    reason = f"Batch external command failed with exit code {process.get('returnCode')}"
                for sprite_id in staged_by_id:
                    result_by_id[sprite_id]["errors"].append(reason)
            else:
                for sprite_id, staged in staged_by_id.items():
                    result = result_by_id[sprite_id]
                    try:
                        raw_output_path = staged["rawOutputPath"]
                        _regular_output(raw_output_path, raw_output_dir)
                        model_width, model_height, model_rgba = decode_png(raw_output_path)
                        expected_width = staged["paddedWidth"] * scale
                        expected_height = staged["paddedHeight"] * scale
                        if (model_width, model_height) != (expected_width, expected_height):
                            raise HDPipelineError(
                                f"Upscaler returned {model_width}x{model_height}; expected {expected_width}x{expected_height}"
                            )
                        crop = padding * scale
                        output_width, output_height, cropped = crop_image(
                            model_width,
                            model_height,
                            model_rgba,
                            crop,
                            crop,
                            crop,
                            crop,
                        )
                        source_scaled_width, source_scaled_height, source_scaled = scale_nearest(
                            staged["sourceWidth"],
                            staged["sourceHeight"],
                            staged["sourceRgba"],
                            scale,
                        )
                        if (output_width, output_height) != (source_scaled_width, source_scaled_height):
                            raise HDPipelineError("Cropped output dimensions do not match scaled source")
                        normalized = restore_alpha(cropped, source_scaled)
                        final_path = output_sprites / f"{sprite_id}.png"
                        write_png(final_path, output_width, output_height, normalized)
                        result.update(
                            {
                                "status": "accepted",
                                "sourcePngSha256": staged["sourcePngSha256"],
                                "path": final_path.relative_to(output_root).as_posix(),
                                "width": output_width,
                                "height": output_height,
                                "pngSha256": _sha256_path(final_path),
                                "alphaSha256": _sha256_bytes(alpha_bytes(normalized)),
                                "alphaBounds": alpha_bounds(output_width, output_height, normalized),
                            }
                        )
                    except (OSError, HDPipelineError) as exc:
                        result["errors"].append(str(exc))

        results = [result_by_id[sprite_id] for sprite_id in sorted(result_by_id)]
        accepted = sum(entry.get("status") == "accepted" for entry in results)
        manifest = {
            "format": HD_OVERRIDE_FORMAT,
            "ok": accepted == len(results),
            "sourceExport": {
                "path": str(export_path.resolve()),
                "sha256": _sha256_path(export_path),
                "mapSha256": export_manifest.get("source", {}).get("mapSha256"),
                "assetCatalogSha256": export_manifest.get("source", {}).get("assetCatalogSha256"),
                "appearancesSha256": export_manifest.get("source", {}).get("appearancesSha256"),
            },
            "scale": scale,
            "padding": padding,
            "backend": {
                "name": "external-batch",
                "commandConfigured": True,
                "commandTemplateSha256": _sha256_bytes(command.encode("utf-8")),
                "invocations": 1 if batch_inputs else 0,
                "process": process,
            },
            "summary": {
                "spriteCount": len(results),
                "staged": len(batch_inputs),
                "accepted": accepted,
                "rejected": len(results) - accepted,
            },
            "sprites": results,
        }
        _write_json(output_root / "manifest.json", manifest)
        return manifest
    finally:
        if temp is not None:
            temp.cleanup()
