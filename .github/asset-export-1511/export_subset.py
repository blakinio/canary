from __future__ import annotations

import hashlib
import json
import shutil
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

TAG = "15.11.c9d1cf"
REPOSITORY = "dudantas/tibia-client"
RAW_BASE = f"https://raw.githubusercontent.com/{REPOSITORY}/{TAG}/assets"
ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools" / "ai-agent"
OUTPUT = ROOT / "artifacts" / "client-1511"
ASSETS = OUTPUT / "assets"
ITEM_IDS_PATH = Path(__file__).with_name("item_ids.txt")

sys.path.insert(0, str(TOOLS))
from otbm_appearances import build_appearances_index  # noqa: E402


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(4 * 1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def download(relative: str, destination: Path) -> None:
    url = f"{RAW_BASE}/{relative}"
    destination.parent.mkdir(parents=True, exist_ok=True)
    last_error: Exception | None = None
    for attempt in range(1, 4):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "canary-otbm-asset-export/1"})
            with urllib.request.urlopen(request, timeout=120) as response, destination.open("wb") as output:
                shutil.copyfileobj(response, output, length=4 * 1024 * 1024)
            if destination.stat().st_size == 0:
                raise RuntimeError(f"Downloaded empty file: {relative}")
            print(f"downloaded {relative}: {destination.stat().st_size} bytes")
            return
        except (OSError, urllib.error.URLError, RuntimeError) as exc:
            last_error = exc
            if destination.exists():
                destination.unlink()
            if attempt < 3:
                time.sleep(attempt * 2)
    raise RuntimeError(f"Unable to download {url}: {last_error}")


def selected_item_ids() -> list[int]:
    return sorted({int(line.strip()) for line in ITEM_IDS_PATH.read_text(encoding="utf-8").splitlines() if line.strip()})


def main() -> int:
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    ASSETS.mkdir(parents=True)

    source_catalog_path = ROOT / "artifacts" / "catalog-content.full.json"
    download("catalog-content.json", source_catalog_path)
    catalog = json.loads(source_catalog_path.read_text(encoding="utf-8"))
    if not isinstance(catalog, list):
        raise RuntimeError("catalog-content.json must contain an array")

    appearance_entries = [entry for entry in catalog if isinstance(entry, dict) and entry.get("type") == "appearances"]
    if len(appearance_entries) != 1:
        raise RuntimeError(f"Expected exactly one appearances entry, found {len(appearance_entries)}")
    appearance_entry = appearance_entries[0]
    appearance_file = appearance_entry.get("file")
    if not isinstance(appearance_file, str) or not appearance_file:
        raise RuntimeError("Appearances catalog entry has no file")
    appearance_path = ASSETS / appearance_file
    download(appearance_file, appearance_path)

    appearance_index = build_appearances_index(appearance_path)
    if not appearance_index["ok"]:
        raise RuntimeError(f"Appearances parser failed: {appearance_index['issues'][:10]}")
    by_id = {
        int(entry["id"]): entry
        for entry in appearance_index["appearances"]
        if isinstance(entry, dict) and isinstance(entry.get("id"), int)
    }

    item_ids = selected_item_ids()
    missing_item_ids = [item_id for item_id in item_ids if item_id not in by_id]
    sprite_ids: set[int] = set()
    for item_id in item_ids:
        appearance = by_id.get(item_id)
        if not appearance:
            continue
        for group in appearance.get("frameGroups", []):
            if not isinstance(group, dict):
                continue
            info = group.get("spriteInfo")
            if not isinstance(info, dict):
                continue
            for sprite_id in info.get("spriteIds", []):
                if isinstance(sprite_id, int) and sprite_id > 0:
                    sprite_ids.add(sprite_id)

    sprite_entries = [entry for entry in catalog if isinstance(entry, dict) and entry.get("type") == "sprite"]
    selected_sprite_entries: list[dict[str, object]] = []
    covered_sprite_ids: set[int] = set()
    sorted_sprite_ids = sorted(sprite_ids)
    for entry in sprite_entries:
        first = entry.get("firstspriteid")
        last = entry.get("lastspriteid")
        filename = entry.get("file")
        if not isinstance(first, int) or not isinstance(last, int) or not isinstance(filename, str):
            continue
        matching = [sprite_id for sprite_id in sorted_sprite_ids if first <= sprite_id <= last]
        if not matching:
            continue
        selected_sprite_entries.append(entry)
        covered_sprite_ids.update(matching)
        download(filename, ASSETS / filename)

    missing_sprite_ids = sorted(sprite_ids - covered_sprite_ids)
    if missing_sprite_ids:
        raise RuntimeError(f"Catalog does not cover {len(missing_sprite_ids)} selected sprite IDs: {missing_sprite_ids[:50]}")

    filtered_catalog = [appearance_entry, *selected_sprite_entries]
    (ASSETS / "catalog-content.json").write_text(
        json.dumps(filtered_catalog, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (OUTPUT / "package.json").write_text(
        json.dumps(
            {
                "name": "tibia-client-render-assets",
                "version": "15.11",
                "sourceRepository": REPOSITORY,
                "sourceTag": TAG,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    report = {
        "format": "canary-render-asset-subset-v1",
        "source": {"repository": REPOSITORY, "tag": TAG},
        "selection": {
            "itemIdCount": len(item_ids),
            "missingItemIds": missing_item_ids,
            "spriteIdCount": len(sprite_ids),
            "spriteSheetCount": len(selected_sprite_entries),
        },
        "files": {
            "catalog": {
                "path": "assets/catalog-content.json",
                "sha256": sha256(ASSETS / "catalog-content.json"),
            },
            "appearances": {
                "path": f"assets/{appearance_file}",
                "sha256": sha256(appearance_path),
            },
            "spriteSheets": [
                {
                    "path": f"assets/{entry['file']}",
                    "firstSpriteId": entry["firstspriteid"],
                    "lastSpriteId": entry["lastspriteid"],
                    "spriteType": entry["spritetype"],
                    "sha256": sha256(ASSETS / str(entry["file"])),
                }
                for entry in selected_sprite_entries
            ],
        },
    }
    (OUTPUT / "selection-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report["selection"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
