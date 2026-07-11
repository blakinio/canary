from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def replace_once(path: str, old: str, new: str) -> None:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"Expected exactly one occurrence in {path}, found {count}: {old!r}")
    target.write_text(text.replace(old, new, 1), encoding="utf-8")


replace_once(
    "tools/ai-agent/otbm_renderer.py",
    "appearances_index = build_appearances_index(_resolve_appearance_path(asset_index), asset_index=asset_index)",
    "appearances_index = build_appearances_index(_resolve_appearance_path(asset_index))",
)

replace_once(
    "tools/ai-agent/test_otbm_sprites.py",
    'struct.pack("<Q", len(bmp)) + compressed',
    'struct.pack("<Q", len(compressed)) + compressed',
)
replace_once(
    "tools/ai-agent/test_otbm_sprites.py",
    '        self.assertEqual(sheet.header.pb, 2)\n        report = sheet_report(sheet)',
    '        self.assertEqual(sheet.header.pb, 2)\n'
    '        self.assertEqual(sheet.header.declared_compressed_size, len(self.path.read_bytes()) - 45)\n'
    '        report = sheet_report(sheet)',
)
replace_once(
    "tools/ai-agent/test_otbm_sprites.py",
    '    def test_rejects_missing_signature(self) -> None:\n',
    '    def test_rejects_inner_compressed_size_mismatch(self) -> None:\n'
    '        data = bytearray(self.path.read_bytes())\n'
    '        declared = struct.unpack_from("<Q", data, 37)[0]\n'
    '        struct.pack_into("<Q", data, 37, declared + 1)\n'
    '        self.path.write_bytes(data)\n'
    '        with self.assertRaisesRegex(SpriteSheetError, "compressed size mismatch"):\n'
    '            decode_sprite_sheet(self.path)\n\n'
    '    def test_rejects_missing_signature(self) -> None:\n',
)

replace_once(
    "tools/ai-agent/test_otbm_renderer.py",
    'struct.pack("<Q", len(bmp)) + compressed',
    'struct.pack("<Q", len(compressed)) + compressed',
)
replace_once(
    "tools/ai-agent/test_otbm_renderer.py",
    '                object_appearance(101, 101, top=True),\n',
    '                object_appearance(101, 101, top=True),\n'
    '                # A reduced render package may omit sheets used only by unrelated appearances.\n'
    '                object_appearance(9999, 500),\n',
)

replace_once(
    "docs/ai-agent/OTBM_SPRITE_SHEET_REPORT.schema.json",
    '"required": ["properties", "lc", "lp", "pb", "dictionarySize", "declaredUncompressedSize"]',
    '"required": ["properties", "lc", "lp", "pb", "dictionarySize", "declaredCompressedSize"]',
)
replace_once(
    "docs/ai-agent/OTBM_SPRITE_SHEET_REPORT.schema.json",
    '"declaredUncompressedSize": {"oneOf": [{"type": "integer", "minimum": 1}, {"type": "null"}]}',
    '"declaredCompressedSize": {"type": "integer", "minimum": 0}',
)

replace_once(
    "docs/ai-agent/OTBM_SPRITES.md",
    "3. read the LZMA1 properties byte, dictionary size, and declared output size;",
    "3. read the LZMA1 properties byte, dictionary size, and declared compressed payload size;",
)
replace_once(
    "docs/ai-agent/OTBM_SPRITES.md",
    "- LZMA properties, dictionary size, stream termination, output size, and trailing data are checked;",
    "- LZMA properties, dictionary size, declared compressed payload size, stream termination, and trailing data are checked;",
)
replace_once(
    "docs/ai-agent/OTBM_SPRITES.md",
    "8. normalize bottom-up BMP rows to top-down RGBA.\n",
    "8. normalize bottom-up BMP rows to top-down RGBA.\n\n"
    "The eight-byte value after the LZMA properties and dictionary is the compressed raw-LZMA payload length used by the real OTClient/CIP files, not the decompressed BMP size.\n",
)

replace_once(
    "docs/ai-agent/OTBM_RENDERER.md",
    "The renderer validates the complete asset package before drawing. It then parses the referenced appearances protobuf and decodes only the CIP/LZMA sprite sheets needed by the requested map region.",
    "The renderer validates every file and sprite range declared by the supplied catalog before drawing. The catalog may represent a complete client or a reduced render package. Appearances are parsed independently, while sprite availability is required only for IDs actually referenced by items in the requested map region.",
)
replace_once(
    "docs/ai-agent/OTBM_RENDERER.md",
    "- appearances and sprite sheets must pass their independent parsers before rendering;",
    "- appearances and every sprite sheet used by the selected region must pass their independent parsers before rendering;",
)

for path in (
    "docs/ai-agent/OTBM_SPRITE_SHEET_REPORT.schema.json",
    "docs/ai-agent/OTBM_RENDER_REPORT.schema.json",
):
    json.loads((ROOT / path).read_text(encoding="utf-8"))

print("Applied real OTClient 15.11 asset fixes.")
