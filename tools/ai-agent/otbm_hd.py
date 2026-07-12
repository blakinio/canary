from __future__ import annotations

import hashlib
import json
import shlex
import struct
import subprocess
import tempfile
import zlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from otbm_assets import build_asset_index
from otbm_appearances import build_appearances_index
from otbm_binary import DEFAULT_MAX_TILES, _require, tile_view
from otbm_renderer import (
    DEFAULT_PADDING_TILES,
    MAX_CANVAS_PIXELS,
    TILE_SIZE,
    RenderDiagnostics,
    SpriteRepository,
    _ordered_items,
    _pattern,
    _render_items,
    _resolve_appearance_path,
    _sprite_ids,
)
from otbm_scan import bounds_tile_count, normalize_bounds, scan_map
from otbm_sprites import encode_png

HD_EXPORT_FORMAT = "canary-otbm-hd-sprite-export-v1"
HD_OVERRIDE_FORMAT = "canary-otbm-hd-sprite-overrides-v1"
HD_RENDER_REPORT_FORMAT = "canary-otbm-hd-render-report-v1"
MAX_SAMPLES_PER_SPRITE = 16
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


class HDPipelineError(ValueError):
    pass


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise HDPipelineError(f"JSON root must be an object: {path}")
    return payload


def _paeth(a: int, b: int, c: int) -> int:
    p = a + b - c
    pa = abs(p - a)
    pb = abs(p - b)
    pc = abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    if pb <= pc:
        return b
    return c


def decode_png(path: Path) -> tuple[int, int, bytes]:
    data = path.read_bytes()
    if not data.startswith(PNG_SIGNATURE):
        raise HDPipelineError(f"Not a PNG file: {path}")
    offset = len(PNG_SIGNATURE)
    width = height = bit_depth = color_type = interlace = None
    compressed = bytearray()
    while offset + 12 <= len(data):
        length = struct.unpack_from(">I", data, offset)[0]
        chunk_type = data[offset + 4 : offset + 8]
        start = offset + 8
        end = start + length
        if end + 4 > len(data):
            raise HDPipelineError(f"Truncated PNG chunk in {path}")
        chunk = data[start:end]
        expected_crc = struct.unpack_from(">I", data, end)[0]
        actual_crc = zlib.crc32(chunk_type)
        actual_crc = zlib.crc32(chunk, actual_crc) & 0xFFFFFFFF
        if actual_crc != expected_crc:
            raise HDPipelineError(f"PNG CRC mismatch in {path}")
        if chunk_type == b"IHDR":
            if length != 13:
                raise HDPipelineError(f"Invalid IHDR in {path}")
            width, height, bit_depth, color_type, compression, filtering, interlace = struct.unpack(">IIBBBBB", chunk)
            if compression != 0 or filtering != 0:
                raise HDPipelineError(f"Unsupported PNG compression/filter method in {path}")
        elif chunk_type == b"IDAT":
            compressed.extend(chunk)
        elif chunk_type == b"IEND":
            break
        offset = end + 4
    if not all(isinstance(value, int) for value in (width, height, bit_depth, color_type, interlace)):
        raise HDPipelineError(f"PNG has no valid IHDR: {path}")
    if width <= 0 or height <= 0:
        raise HDPipelineError(f"PNG dimensions must be positive: {path}")
    if bit_depth != 8 or interlace != 0:
        raise HDPipelineError(f"Only non-interlaced 8-bit PNG is supported: {path}")
    channels_by_type = {0: 1, 2: 3, 4: 2, 6: 4}
    channels = channels_by_type.get(color_type)
    if channels is None:
        raise HDPipelineError(f"Unsupported PNG color type {color_type}: {path}")
    try:
        raw = zlib.decompress(bytes(compressed))
    except zlib.error as exc:
        raise HDPipelineError(f"PNG decompression failed for {path}: {exc}") from exc
    stride = width * channels
    expected_size = height * (stride + 1)
    if len(raw) != expected_size:
        raise HDPipelineError(f"Unexpected PNG payload size for {path}: {len(raw)} != {expected_size}")
    previous = bytearray(stride)
    rgba = bytearray(width * height * 4)
    source_offset = 0
    target_offset = 0
    for _ in range(height):
        filter_type = raw[source_offset]
        source_offset += 1
        encoded = raw[source_offset : source_offset + stride]
        source_offset += stride
        row = bytearray(stride)
        for index, value in enumerate(encoded):
            left = row[index - channels] if index >= channels else 0
            up = previous[index]
            up_left = previous[index - channels] if index >= channels else 0
            if filter_type == 0:
                decoded = value
            elif filter_type == 1:
                decoded = (value + left) & 0xFF
            elif filter_type == 2:
                decoded = (value + up) & 0xFF
            elif filter_type == 3:
                decoded = (value + ((left + up) // 2)) & 0xFF
            elif filter_type == 4:
                decoded = (value + _paeth(left, up, up_left)) & 0xFF
            else:
                raise HDPipelineError(f"Unsupported PNG filter {filter_type}: {path}")
            row[index] = decoded
        for x in range(width):
            source = x * channels
            if color_type == 6:
                r, g, b, a = row[source : source + 4]
            elif color_type == 2:
                r, g, b = row[source : source + 3]
                a = 255
            elif color_type == 4:
                gray, a = row[source : source + 2]
                r = g = b = gray
            else:
                gray = row[source]
                r = g = b = gray
                a = 255
            rgba[target_offset : target_offset + 4] = bytes((r, g, b, a))
            target_offset += 4
        previous = row
    return width, height, bytes(rgba)


def write_png(path: Path, width: int, height: int, rgba: bytes) -> None:
    if width <= 0 or height <= 0 or len(rgba) != width * height * 4:
        raise HDPipelineError("Invalid RGBA image dimensions")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(encode_png(width, height, rgba))


def scale_nearest(width: int, height: int, rgba: bytes, scale: int) -> tuple[int, int, bytes]:
    if scale < 1:
        raise HDPipelineError("scale must be at least 1")
    if len(rgba) != width * height * 4:
        raise HDPipelineError("RGBA payload length does not match image dimensions")
    if scale == 1:
        return width, height, bytes(rgba)
    output_width = width * scale
    output_height = height * scale
    output = bytearray(output_width * output_height * 4)
    for source_y in range(height):
        source_row = rgba[source_y * width * 4 : (source_y + 1) * width * 4]
        expanded = bytearray(output_width * 4)
        cursor = 0
        for source_x in range(width):
            pixel = source_row[source_x * 4 : source_x * 4 + 4]
            for _ in range(scale):
                expanded[cursor : cursor + 4] = pixel
                cursor += 4
        for repeat in range(scale):
            target_y = source_y * scale + repeat
            start = target_y * output_width * 4
            output[start : start + output_width * 4] = expanded
    return output_width, output_height, bytes(output)


def pad_image(width: int, height: int, rgba: bytes, padding: int) -> tuple[int, int, bytes]:
    if padding < 0:
        raise HDPipelineError("padding must be non-negative")
    if padding == 0:
        return width, height, bytes(rgba)
    output_width = width + padding * 2
    output_height = height + padding * 2
    output = bytearray(output_width * output_height * 4)
    for y in range(height):
        source_start = y * width * 4
        target_start = ((y + padding) * output_width + padding) * 4
        output[target_start : target_start + width * 4] = rgba[source_start : source_start + width * 4]
    return output_width, output_height, bytes(output)


def crop_image(width: int, height: int, rgba: bytes, left: int, top: int, right: int, bottom: int) -> tuple[int, int, bytes]:
    if min(left, top, right, bottom) < 0 or left + right >= width or top + bottom >= height:
        raise HDPipelineError("Invalid crop margins")
    output_width = width - left - right
    output_height = height - top - bottom
    output = bytearray(output_width * output_height * 4)
    for y in range(output_height):
        source_start = ((y + top) * width + left) * 4
        target_start = y * output_width * 4
        output[target_start : target_start + output_width * 4] = rgba[source_start : source_start + output_width * 4]
    return output_width, output_height, bytes(output)


def alpha_bytes(rgba: bytes) -> bytes:
    return bytes(rgba[index] for index in range(3, len(rgba), 4))


def restore_alpha(model_rgba: bytes, source_scaled_rgba: bytes) -> bytes:
    if len(model_rgba) != len(source_scaled_rgba):
        raise HDPipelineError("Model and source alpha images have different sizes")
    output = bytearray(model_rgba)
    for index in range(0, len(output), 4):
        alpha = source_scaled_rgba[index + 3]
        output[index + 3] = alpha
        if alpha == 0:
            output[index : index + 3] = b"\x00\x00\x00"
    return bytes(output)


def alpha_bounds(width: int, height: int, rgba: bytes) -> list[int] | None:
    xs: list[int] = []
    ys: list[int] = []
    for y in range(height):
        for x in range(width):
            if rgba[(y * width + x) * 4 + 3] != 0:
                xs.append(x)
                ys.append(y)
    if not xs:
        return None
    return [min(xs), min(ys), max(xs), max(ys)]


def _appearance_map(asset_index: dict[str, Any]) -> tuple[dict[int, dict[str, Any]], dict[str, Any]]:
    appearances_index = build_appearances_index(_resolve_appearance_path(asset_index))
    _require(appearances_index["ok"], f"Appearances data is invalid: {appearances_index['issues'][:5]}")
    appearances = {
        int(entry["id"]): entry
        for entry in appearances_index["appearances"]
        if isinstance(entry.get("id"), int) and entry.get("category") == "object"
    }
    return appearances, appearances_index


def export_region_sprites(
    map_path: Path,
    assets_root: Path,
    bounds: tuple[tuple[int, int, int], tuple[int, int, int]],
    output_root: Path,
    *,
    max_tiles: int = DEFAULT_MAX_TILES,
) -> dict[str, Any]:
    lower, upper = normalize_bounds(bounds[0], bounds[1])
    requested_tiles = bounds_tile_count((lower, upper))
    _require(requested_tiles <= max_tiles, f"Requested region contains {requested_tiles} positions; limit is {max_tiles}")
    asset_index = build_asset_index(assets_root, hash_files=True)
    _require(asset_index["ok"], f"Client asset package is invalid: {asset_index['issues'][:5]}")
    appearances, appearances_index = _appearance_map(asset_index)
    scan = scan_map(map_path, bounds=(lower, upper), count_tiles=False)
    _require(not scan.duplicates, f"Region contains duplicate tile positions: {sorted(scan.duplicates)[:5]}")
    diagnostics = RenderDiagnostics()
    repository = SpriteRepository(asset_index, diagnostics)
    usage: dict[int, dict[str, Any]] = {}
    for position, record in sorted(scan.records.items(), key=lambda pair: (pair[0][2], pair[0][1], pair[0][0])):
        for item in _render_items(tile_view(record, include_raw=False)):
            appearance = appearances.get(item.item_id)
            if appearance is None:
                diagnostics.missing_appearances.add(item.item_id)
                continue
            pattern = _pattern(item, appearance, position, diagnostics)
            for sprite_id in _sprite_ids(appearance, pattern, diagnostics, item.item_id):
                if sprite_id == 0:
                    continue
                entry = usage.setdefault(sprite_id, {"itemIds": set(), "useCount": 0, "samplePositions": []})
                entry["itemIds"].add(item.item_id)
                entry["useCount"] += 1
                if len(entry["samplePositions"]) < MAX_SAMPLES_PER_SPRITE:
                    entry["samplePositions"].append(list(position))
    sprites: list[dict[str, Any]] = []
    for sprite_id in sorted(usage):
        sprite = repository.get(sprite_id)
        if sprite is None:
            diagnostics.missing_sprites.add(sprite_id)
            continue
        width, height, rgba = sprite
        relative_path = Path("original") / f"{sprite_id}.png"
        path = output_root / relative_path
        write_png(path, width, height, rgba)
        png_sha = _sha256_path(path)
        info = usage[sprite_id]
        sprites.append(
            {
                "spriteId": sprite_id,
                "itemIds": sorted(info["itemIds"]),
                "useCount": info["useCount"],
                "samplePositions": info["samplePositions"],
                "source": {
                    "path": relative_path.as_posix(),
                    "width": width,
                    "height": height,
                    "pngSha256": png_sha,
                    "alphaSha256": _sha256_bytes(alpha_bytes(rgba)),
                    "alphaBounds": alpha_bounds(width, height, rgba),
                },
            }
        )
    if diagnostics.missing_appearances:
        diagnostics.error(
            "missing_appearances",
            f"{len(diagnostics.missing_appearances)} placed item IDs have no object appearance",
            itemIds=sorted(diagnostics.missing_appearances),
        )
    if diagnostics.missing_sprites:
        diagnostics.error(
            "missing_sprites",
            f"{len(diagnostics.missing_sprites)} referenced sprite IDs could not be exported",
            spriteIds=sorted(diagnostics.missing_sprites),
        )
    manifest = {
        "format": HD_EXPORT_FORMAT,
        "ok": not diagnostics.errors,
        "source": {
            "map": str(map_path.resolve()),
            "mapSha256": scan.map_sha256,
            "assetsRoot": str(assets_root.resolve()),
            "assetCatalogSha256": asset_index["catalog"]["sha256"],
            "appearancesSha256": appearances_index["source"]["sha256"],
        },
        "bounds": {"from": list(lower), "to": list(upper)},
        "summary": {
            "requestedPositions": requested_tiles,
            "mapTiles": len(scan.records),
            "spriteCount": len(sprites),
            "spriteUses": sum(entry["useCount"] for entry in sprites),
            "missingAppearanceCount": len(diagnostics.missing_appearances),
            "missingSpriteCount": len(diagnostics.missing_sprites),
        },
        "sprites": sprites,
        "warnings": diagnostics.warnings,
        "errors": diagnostics.errors,
    }
    _write_json(output_root / "manifest.json", manifest)
    return manifest


def _command_argv(template: str, *, input_path: Path, output_path: Path, scale: int, sprite_id: int) -> list[str]:
    if not template.strip():
        raise HDPipelineError("External backend requires a non-empty command template")
    replacements = {
        "{input}": str(input_path),
        "{output}": str(output_path),
        "{scale}": str(scale),
        "{sprite_id}": str(sprite_id),
    }
    argv: list[str] = []
    for token in shlex.split(template):
        for marker, value in replacements.items():
            token = token.replace(marker, value)
        argv.append(token)
    if not argv:
        raise HDPipelineError("External backend command is empty")
    return argv


def _run_external(
    template: str,
    *,
    input_path: Path,
    output_path: Path,
    scale: int,
    sprite_id: int,
    timeout_seconds: int,
) -> dict[str, Any]:
    argv = _command_argv(template, input_path=input_path, output_path=output_path, scale=scale, sprite_id=sprite_id)
    completed = subprocess.run(argv, capture_output=True, text=True, timeout=timeout_seconds, check=False, shell=False)
    return {
        "argv": argv,
        "returnCode": completed.returncode,
        "stdout": completed.stdout[-1000:],
        "stderr": completed.stderr[-1000:],
    }


def upscale_export(
    export_root: Path,
    output_root: Path,
    *,
    scale: int = 2,
    padding: int = 4,
    backend: str = "nearest",
    command: str | None = None,
    timeout_seconds: int = 120,
    keep_work: bool = False,
) -> dict[str, Any]:
    if scale < 2 or scale > 8:
        raise HDPipelineError("scale must be between 2 and 8")
    if padding < 0 or padding > 64:
        raise HDPipelineError("padding must be between 0 and 64")
    if backend not in {"nearest", "external"}:
        raise HDPipelineError("backend must be nearest or external")
    if timeout_seconds <= 0:
        raise HDPipelineError("timeout_seconds must be positive")
    export_path = export_root / "manifest.json"
    export_manifest = _load_json(export_path)
    if export_manifest.get("format") != HD_EXPORT_FORMAT:
        raise HDPipelineError(f"Unsupported export manifest format: {export_manifest.get('format')}")
    sprites = export_manifest.get("sprites")
    if not isinstance(sprites, list):
        raise HDPipelineError("Export manifest has no sprite list")
    output_sprites = output_root / "sprites"
    output_sprites.mkdir(parents=True, exist_ok=True)
    work_parent: Path | None = None
    temp: tempfile.TemporaryDirectory[str] | None = None
    if keep_work:
        work_parent = output_root / "work"
        work_parent.mkdir(parents=True, exist_ok=True)
    else:
        temp = tempfile.TemporaryDirectory(prefix="otbm-hd-")
        work_parent = Path(temp.name)
    results: list[dict[str, Any]] = []
    try:
        for raw_entry in sprites:
            if not isinstance(raw_entry, dict) or not isinstance(raw_entry.get("spriteId"), int):
                continue
            sprite_id = int(raw_entry["spriteId"])
            source = raw_entry.get("source")
            result: dict[str, Any] = {"spriteId": sprite_id, "status": "rejected", "errors": []}
            try:
                if not isinstance(source, dict) or not isinstance(source.get("path"), str):
                    raise HDPipelineError("Source metadata is missing")
                source_path = export_root / source["path"]
                expected_sha = source.get("pngSha256")
                if not isinstance(expected_sha, str) or _sha256_path(source_path) != expected_sha:
                    raise HDPipelineError("Source PNG hash does not match export manifest")
                width, height, rgba = decode_png(source_path)
                if width != source.get("width") or height != source.get("height"):
                    raise HDPipelineError("Source PNG dimensions do not match export manifest")
                padded_width, padded_height, padded = pad_image(width, height, rgba, padding)
                input_path = work_parent / f"{sprite_id}-input.png"
                raw_output_path = work_parent / f"{sprite_id}-raw.png"
                write_png(input_path, padded_width, padded_height, padded)
                process: dict[str, Any] | None = None
                if backend == "nearest":
                    model_width, model_height, model_rgba = scale_nearest(padded_width, padded_height, padded, scale)
                    write_png(raw_output_path, model_width, model_height, model_rgba)
                else:
                    if command is None:
                        raise HDPipelineError("External backend requires --command")
                    process = _run_external(
                        command,
                        input_path=input_path,
                        output_path=raw_output_path,
                        scale=scale,
                        sprite_id=sprite_id,
                        timeout_seconds=timeout_seconds,
                    )
                    if process["returnCode"] != 0:
                        raise HDPipelineError(f"External command failed with exit code {process['returnCode']}")
                    if not raw_output_path.is_file():
                        raise HDPipelineError("External command did not create the requested output file")
                model_width, model_height, model_rgba = decode_png(raw_output_path)
                expected_padded_width = padded_width * scale
                expected_padded_height = padded_height * scale
                if (model_width, model_height) != (expected_padded_width, expected_padded_height):
                    raise HDPipelineError(
                        f"Upscaler returned {model_width}x{model_height}; expected {expected_padded_width}x{expected_padded_height}"
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
                source_scaled_width, source_scaled_height, source_scaled = scale_nearest(width, height, rgba, scale)
                if (output_width, output_height) != (source_scaled_width, source_scaled_height):
                    raise HDPipelineError("Cropped output dimensions do not match scaled source")
                normalized = restore_alpha(cropped, source_scaled)
                output_path = output_sprites / f"{sprite_id}.png"
                write_png(output_path, output_width, output_height, normalized)
                result.update(
                    {
                        "status": "accepted",
                        "sourcePngSha256": expected_sha,
                        "path": output_path.relative_to(output_root).as_posix(),
                        "width": output_width,
                        "height": output_height,
                        "pngSha256": _sha256_path(output_path),
                        "alphaSha256": _sha256_bytes(alpha_bytes(normalized)),
                        "alphaBounds": alpha_bounds(output_width, output_height, normalized),
                    }
                )
                if process is not None:
                    result["process"] = process
            except (OSError, HDPipelineError, subprocess.TimeoutExpired) as exc:
                result["errors"].append(str(exc))
            results.append(result)
    finally:
        if temp is not None:
            temp.cleanup()
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
        "backend": {"name": backend, "command": command if backend == "external" else None},
        "summary": {"spriteCount": len(results), "accepted": accepted, "rejected": len(results) - accepted},
        "sprites": results,
    }
    _write_json(output_root / "manifest.json", manifest)
    return manifest


def validate_override_pack(override_root: Path, *, export_root: Path | None = None) -> dict[str, Any]:
    manifest_path = override_root / "manifest.json"
    manifest = _load_json(manifest_path)
    if manifest.get("format") != HD_OVERRIDE_FORMAT:
        raise HDPipelineError(f"Unsupported override manifest format: {manifest.get('format')}")
    scale = manifest.get("scale")
    if not isinstance(scale, int) or scale < 2:
        raise HDPipelineError("Override manifest has an invalid scale")
    source_export = manifest.get("sourceExport")
    if not isinstance(source_export, dict):
        raise HDPipelineError("Override manifest has no source export metadata")
    if export_root is None:
        source_path = source_export.get("path")
        if not isinstance(source_path, str):
            raise HDPipelineError("Override manifest has no source export path")
        export_manifest_path = Path(source_path)
        export_root = export_manifest_path.parent
    else:
        export_manifest_path = export_root / "manifest.json"
    expected_export_sha = source_export.get("sha256")
    if not isinstance(expected_export_sha, str) or _sha256_path(export_manifest_path) != expected_export_sha:
        raise HDPipelineError("Source export manifest hash mismatch")
    export_manifest = _load_json(export_manifest_path)
    if export_manifest.get("format") != HD_EXPORT_FORMAT:
        raise HDPipelineError(f"Unsupported source export format: {export_manifest.get('format')}")
    export_by_id = {
        int(entry["spriteId"]): entry
        for entry in export_manifest.get("sprites", [])
        if isinstance(entry, dict) and isinstance(entry.get("spriteId"), int)
    }
    raw_sprites = manifest.get("sprites")
    if not isinstance(raw_sprites, list):
        raise HDPipelineError("Override manifest has no sprite list")
    results: list[dict[str, Any]] = []
    invalid_accepted = 0
    accepted = 0
    rejected = 0
    for raw_entry in raw_sprites:
        if not isinstance(raw_entry, dict) or not isinstance(raw_entry.get("spriteId"), int):
            continue
        sprite_id = int(raw_entry["spriteId"])
        status = raw_entry.get("status")
        result: dict[str, Any] = {
            "spriteId": sprite_id,
            "status": status,
            "overrideUsable": False,
            "errors": [],
        }
        if status != "accepted":
            rejected += 1
            results.append(result)
            continue
        accepted += 1
        try:
            export_entry = export_by_id.get(sprite_id)
            if export_entry is None:
                raise HDPipelineError("Sprite is absent from source export")
            source = export_entry.get("source")
            if not isinstance(source, dict) or not isinstance(source.get("path"), str):
                raise HDPipelineError("Source export metadata is incomplete")
            source_path = export_root / source["path"]
            if _sha256_path(source_path) != source.get("pngSha256"):
                raise HDPipelineError("Source PNG hash mismatch")
            if raw_entry.get("sourcePngSha256") != source.get("pngSha256"):
                raise HDPipelineError("Override is linked to a different source PNG")
            relative = raw_entry.get("path")
            if not isinstance(relative, str):
                raise HDPipelineError("Override PNG path is missing")
            output_path = override_root / relative
            if _sha256_path(output_path) != raw_entry.get("pngSha256"):
                raise HDPipelineError("Override PNG hash mismatch")
            source_width, source_height, source_rgba = decode_png(source_path)
            width, height, rgba = decode_png(output_path)
            if (width, height) != (source_width * scale, source_height * scale):
                raise HDPipelineError("Override dimensions do not match declared scale")
            _, _, source_scaled = scale_nearest(source_width, source_height, source_rgba, scale)
            if alpha_bytes(rgba) != alpha_bytes(source_scaled):
                raise HDPipelineError("Override alpha mask differs from scaled source")
            if _sha256_bytes(alpha_bytes(rgba)) != raw_entry.get("alphaSha256"):
                raise HDPipelineError("Override alpha hash mismatch")
            result["overrideUsable"] = True
        except (OSError, HDPipelineError) as exc:
            invalid_accepted += 1
            result["errors"].append(str(exc))
        results.append(result)
    return {
        "format": "canary-otbm-hd-validation-report-v1",
        "ok": invalid_accepted == 0 and len(results) > 0,
        "manifest": str(manifest_path.resolve()),
        "sourceExportManifest": str(export_manifest_path.resolve()),
        "scale": scale,
        "summary": {
            "spriteCount": len(results),
            "accepted": accepted,
            "rejected": rejected,
            "validAccepted": accepted - invalid_accepted,
            "invalidAccepted": invalid_accepted,
        },
        "sprites": results,
    }


@dataclass
class HDRenderDiagnostics(RenderDiagnostics):
    override_sprites: set[int] = field(default_factory=set)
    fallback_sprites: set[int] = field(default_factory=set)


class HDSpriteRepository:
    def __init__(
        self,
        asset_index: dict[str, Any],
        diagnostics: HDRenderDiagnostics,
        override_root: Path,
        override_manifest: dict[str, Any],
    ):
        scale = override_manifest.get("scale")
        if not isinstance(scale, int) or scale < 2:
            raise HDPipelineError("Override manifest has an invalid scale")
        self.scale = scale
        self.root = override_root
        self.diagnostics = diagnostics
        self.base = SpriteRepository(asset_index, diagnostics)
        self.entries = {
            int(entry["spriteId"]): entry
            for entry in override_manifest.get("sprites", [])
            if isinstance(entry, dict) and isinstance(entry.get("spriteId"), int) and entry.get("status") == "accepted"
        }
        self.cache: dict[int, tuple[int, int, bytes]] = {}

    def get(self, sprite_id: int) -> tuple[int, int, bytes] | None:
        if sprite_id in self.cache:
            return self.cache[sprite_id]
        source = self.base.get(sprite_id)
        if source is None:
            return None
        source_width, source_height, source_rgba = source
        entry = self.entries.get(sprite_id)
        if entry is not None and isinstance(entry.get("path"), str):
            try:
                path = self.root / entry["path"]
                width, height, rgba = decode_png(path)
                if (width, height) != (source_width * self.scale, source_height * self.scale):
                    raise HDPipelineError("override dimensions do not match source scale")
                if _sha256_path(path) != entry.get("pngSha256"):
                    raise HDPipelineError("override PNG hash mismatch")
                result = (width, height, rgba)
                self.cache[sprite_id] = result
                self.diagnostics.override_sprites.add(sprite_id)
                return result
            except (OSError, HDPipelineError) as exc:
                self.diagnostics.error("invalid_hd_override", str(exc), spriteId=sprite_id)
        result = scale_nearest(source_width, source_height, source_rgba, self.scale)
        self.cache[sprite_id] = result
        self.diagnostics.fallback_sprites.add(sprite_id)
        return result


def _blend(canvas: bytearray, canvas_width: int, canvas_height: int, image: bytes, width: int, height: int, x: int, y: int) -> None:
    for source_y in range(height):
        target_y = y + source_y
        if target_y < 0 or target_y >= canvas_height:
            continue
        for source_x in range(width):
            target_x = x + source_x
            if target_x < 0 or target_x >= canvas_width:
                continue
            source_offset = (source_y * width + source_x) * 4
            sa = image[source_offset + 3]
            if sa == 0:
                continue
            target_offset = (target_y * canvas_width + target_x) * 4
            if sa == 255:
                canvas[target_offset : target_offset + 4] = image[source_offset : source_offset + 4]
                continue
            da = canvas[target_offset + 3]
            inv = 255 - sa
            out_a = sa + (da * inv + 127) // 255
            if out_a == 0:
                continue
            for channel in range(3):
                source_premultiplied = image[source_offset + channel] * sa
                target_premultiplied = canvas[target_offset + channel] * da
                output_premultiplied = source_premultiplied + (target_premultiplied * inv + 127) // 255
                canvas[target_offset + channel] = min(255, (output_premultiplied + out_a // 2) // out_a)
            canvas[target_offset + 3] = out_a


def _draw_item_hd(
    canvas: bytearray,
    canvas_width: int,
    canvas_height: int,
    repository: HDSpriteRepository,
    diagnostics: HDRenderDiagnostics,
    item: Any,
    appearance: dict[str, Any],
    position: tuple[int, int, int],
    tile_dest_x: int,
    tile_dest_y: int,
    elevation: int,
) -> int:
    pattern = _pattern(item, appearance, position, diagnostics)
    sprite_ids = _sprite_ids(appearance, pattern, diagnostics, item.item_id)
    flags = appearance.get("flags") if isinstance(appearance.get("flags"), dict) else {}
    shift = flags.get("shift") if isinstance(flags.get("shift"), dict) else {}
    displacement_x = int(shift.get("x", 0)) * repository.scale
    displacement_y = int(shift.get("y", 0)) * repository.scale
    scaled_tile = TILE_SIZE * repository.scale
    scaled_elevation = elevation * repository.scale
    for sprite_id in sprite_ids:
        sprite = repository.get(sprite_id)
        if sprite is None:
            if sprite_id:
                diagnostics.missing_sprites.add(sprite_id)
            continue
        width, height, rgba = sprite
        draw_x = tile_dest_x - scaled_elevation + scaled_tile - width - displacement_x
        draw_y = tile_dest_y - scaled_elevation + scaled_tile - height - displacement_y
        _blend(canvas, canvas_width, canvas_height, rgba, width, height, draw_x, draw_y)
        diagnostics.rendered_sprites += 1
    diagnostics.rendered_items += 1
    elevation_value = flags.get("height") if isinstance(flags.get("height"), dict) else {}
    added = int(elevation_value.get("elevation", 0))
    return min(24, elevation + max(0, added))


def render_region_hd(
    map_path: Path,
    assets_root: Path,
    bounds: tuple[tuple[int, int, int], tuple[int, int, int]],
    override_root: Path,
    output: Path,
    *,
    export_root: Path | None = None,
    padding_tiles: int = DEFAULT_PADDING_TILES,
    max_tiles: int = DEFAULT_MAX_TILES,
) -> dict[str, Any]:
    validation = validate_override_pack(override_root, export_root=export_root)
    _require(validation["ok"], f"HD override pack is invalid: {validation['summary']}")
    override_manifest = _load_json(override_root / "manifest.json")
    scale = int(override_manifest["scale"])
    lower, upper = normalize_bounds(bounds[0], bounds[1])
    _require(lower[2] == upper[2], "Pixel rendering currently supports exactly one floor")
    requested_tiles = bounds_tile_count((lower, upper))
    _require(requested_tiles <= max_tiles, f"Requested region contains {requested_tiles} positions; limit is {max_tiles}")
    _require(0 <= padding_tiles <= 32, "padding_tiles must be between 0 and 32")
    asset_index = build_asset_index(assets_root, hash_files=True)
    _require(asset_index["ok"], f"Client asset package is invalid: {asset_index['issues'][:5]}")
    appearances, appearances_index = _appearance_map(asset_index)
    source_export = override_manifest.get("sourceExport", {})
    if source_export.get("assetCatalogSha256") != asset_index["catalog"]["sha256"]:
        raise HDPipelineError("Override pack was built from a different asset catalog")
    if source_export.get("appearancesSha256") != appearances_index["source"]["sha256"]:
        raise HDPipelineError("Override pack was built from different appearances data")
    scan = scan_map(map_path, bounds=(lower, upper), count_tiles=False)
    _require(not scan.duplicates, f"Region contains duplicate tile positions: {sorted(scan.duplicates)[:5]}")
    if source_export.get("mapSha256") != scan.map_sha256:
        raise HDPipelineError("Override pack was built from a different map")
    scaled_tile = TILE_SIZE * scale
    padding = padding_tiles * scaled_tile
    region_width = upper[0] - lower[0] + 1
    region_height = upper[1] - lower[1] + 1
    canvas_width = region_width * scaled_tile + padding * 2
    canvas_height = region_height * scaled_tile + padding * 2
    _require(canvas_width * canvas_height <= MAX_CANVAS_PIXELS, "Requested HD render canvas is too large")
    canvas = bytearray(canvas_width * canvas_height * 4)
    diagnostics = HDRenderDiagnostics()
    repository = HDSpriteRepository(asset_index, diagnostics, override_root, override_manifest)
    for position, record in sorted(scan.records.items(), key=lambda pair: (pair[0][1], pair[0][0], pair[0][2])):
        items = _render_items(tile_view(record, include_raw=False))
        ordered, top = _ordered_items(items, appearances)
        tile_x = padding + (position[0] - lower[0]) * scaled_tile
        tile_y = padding + (position[1] - lower[1]) * scaled_tile
        elevation = 0
        for item in ordered:
            appearance = appearances.get(item.item_id)
            if appearance is None:
                diagnostics.missing_appearances.add(item.item_id)
                continue
            elevation = _draw_item_hd(
                canvas,
                canvas_width,
                canvas_height,
                repository,
                diagnostics,
                item,
                appearance,
                position,
                tile_x,
                tile_y,
                elevation,
            )
        for item in top:
            appearance = appearances.get(item.item_id)
            if appearance is None:
                diagnostics.missing_appearances.add(item.item_id)
                continue
            _draw_item_hd(
                canvas,
                canvas_width,
                canvas_height,
                repository,
                diagnostics,
                item,
                appearance,
                position,
                tile_x,
                tile_y,
                0,
            )
    if diagnostics.missing_appearances:
        diagnostics.error(
            "missing_appearances",
            f"{len(diagnostics.missing_appearances)} placed item IDs have no object appearance",
            itemIds=sorted(diagnostics.missing_appearances),
        )
    if diagnostics.missing_sprites:
        diagnostics.error(
            "missing_sprites",
            f"{len(diagnostics.missing_sprites)} referenced sprite IDs could not be rendered",
            spriteIds=sorted(diagnostics.missing_sprites),
        )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(encode_png(canvas_width, canvas_height, bytes(canvas)))
    return {
        "format": HD_RENDER_REPORT_FORMAT,
        "ok": not diagnostics.errors,
        "source": {
            "map": str(map_path.resolve()),
            "mapSha256": scan.map_sha256,
            "assetsRoot": str(assets_root.resolve()),
            "assetCatalogSha256": asset_index["catalog"]["sha256"],
            "appearancesSha256": appearances_index["source"]["sha256"],
            "overrides": str(override_root.resolve()),
            "overridesManifestSha256": _sha256_path(override_root / "manifest.json"),
        },
        "bounds": {"from": list(lower), "to": list(upper)},
        "output": {
            "path": str(output.resolve()),
            "width": canvas_width,
            "height": canvas_height,
            "paddingPixels": padding,
            "renderScale": scale,
            "logicalTileSize": TILE_SIZE,
            "pixelTileSize": scaled_tile,
        },
        "summary": {
            "requestedPositions": requested_tiles,
            "mapTiles": len(scan.records),
            "renderedItems": diagnostics.rendered_items,
            "renderedSprites": diagnostics.rendered_sprites,
            "overrideSpriteCount": len(diagnostics.override_sprites),
            "fallbackSpriteCount": len(diagnostics.fallback_sprites),
            "missingAppearanceCount": len(diagnostics.missing_appearances),
            "missingSpriteCount": len(diagnostics.missing_sprites),
        },
        "overrideSpriteIds": sorted(diagnostics.override_sprites),
        "fallbackSpriteIds": sorted(diagnostics.fallback_sprites),
        "warnings": diagnostics.warnings,
        "errors": diagnostics.errors,
    }


def compare_renders(original: Path, hd: Path, output: Path, *, gap: int = 16) -> dict[str, Any]:
    original_width, original_height, original_rgba = decode_png(original)
    hd_width, hd_height, hd_rgba = decode_png(hd)
    if hd_width % original_width != 0 or hd_height % original_height != 0:
        raise HDPipelineError("HD render dimensions are not an integer scale of the original")
    scale_x = hd_width // original_width
    scale_y = hd_height // original_height
    if scale_x != scale_y:
        raise HDPipelineError("HD render uses different horizontal and vertical scales")
    scaled_width, scaled_height, scaled_original = scale_nearest(original_width, original_height, original_rgba, scale_x)
    if (scaled_width, scaled_height) != (hd_width, hd_height):
        raise HDPipelineError("Scaled original and HD render dimensions differ")
    canvas_width = hd_width * 2 + gap
    canvas_height = hd_height
    canvas = bytearray(canvas_width * canvas_height * 4)
    for y in range(canvas_height):
        left_source = y * hd_width * 4
        left_target = y * canvas_width * 4
        canvas[left_target : left_target + hd_width * 4] = scaled_original[left_source : left_source + hd_width * 4]
        right_target = left_target + (hd_width + gap) * 4
        canvas[right_target : right_target + hd_width * 4] = hd_rgba[left_source : left_source + hd_width * 4]
    write_png(output, canvas_width, canvas_height, bytes(canvas))
    return {
        "format": "canary-otbm-hd-comparison-report-v1",
        "ok": True,
        "original": str(original.resolve()),
        "hd": str(hd.resolve()),
        "output": str(output.resolve()),
        "scale": scale_x,
        "width": canvas_width,
        "height": canvas_height,
    }
