from __future__ import annotations

import hashlib
import json
import os
import pathlib
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Iterable

EXPECTED_VERSION = os.environ.get("EXPECTED_PACKAGE_VERSION", "15.31.69f220")
SOURCE_REPOSITORY = "dudantas/tibia-client"
SOURCE_GIT_URL = f"https://github.com/{SOURCE_REPOSITORY}.git"
RAW_ROOT = f"https://raw.githubusercontent.com/{SOURCE_REPOSITORY}"
OUTPUT = pathlib.Path(os.environ.get("OWA003C_OUTPUT", ".owa-003c-evidence"))
MAX_JSON_BYTES = 16 * 1024 * 1024
MAX_FILE_BYTES = 256 * 1024 * 1024
USER_AGENT = "canary-owa-003c-executed-evidence/1"


class RematerializationError(RuntimeError):
    pass


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def reject_duplicate_keys(pairs: Iterable[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise RematerializationError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json(data: bytes, source: str) -> object:
    try:
        return json.loads(
            data.decode("utf-8"),
            object_pairs_hook=reject_duplicate_keys,
            parse_constant=lambda value: (_ for _ in ()).throw(
                RematerializationError(f"non-finite JSON value in {source}: {value}")
            ),
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RematerializationError(f"invalid JSON from {source}: {exc}") from exc


def download(url: str, *, limit: int, missing_ok: bool = False) -> bytes | None:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/octet-stream,application/json,text/plain,*/*",
        },
    )
    last_error: Exception | None = None
    for attempt in range(1, 4):
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                data = response.read(limit + 1)
            if len(data) > limit:
                raise RematerializationError(f"download exceeds {limit} bytes: {url}")
            return data
        except urllib.error.HTTPError as exc:
            if missing_ok and exc.code == 404:
                return None
            body = exc.read(512).decode("utf-8", errors="replace")
            last_error = RematerializationError(f"HTTP {exc.code} for {url}: {body!r}")
            if exc.code not in {403, 429, 500, 502, 503, 504}:
                break
        except urllib.error.URLError as exc:
            last_error = RematerializationError(f"URL error for {url}: {exc.reason!r}")
        if attempt < 3:
            time.sleep(attempt * 2)
    if last_error is None:
        last_error = RematerializationError(f"download failed without an error: {url}")
    raise last_error


def raw_url(tag: str, path: str) -> str:
    encoded_tag = urllib.parse.quote(tag, safe="")
    encoded_path = "/".join(urllib.parse.quote(part, safe="") for part in path.split("/"))
    return f"{RAW_ROOT}/{encoded_tag}/{encoded_path}"


def list_tags() -> list[str]:
    completed = subprocess.run(
        ["git", "ls-remote", "--tags", "--refs", SOURCE_GIT_URL],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=120,
    )
    if completed.returncode != 0:
        raise RematerializationError(
            "cannot list source tags: " + completed.stderr.strip()
        )
    tags: list[str] = []
    seen: set[str] = set()
    for line in completed.stdout.splitlines():
        _sha, separator, ref = line.partition("\t")
        if not separator or not ref.startswith("refs/tags/"):
            continue
        tag = ref.removeprefix("refs/tags/")
        if tag and tag not in seen:
            seen.add(tag)
            tags.append(tag)
    return sorted(tags)


def find_exact_tag(tags: Iterable[str]) -> tuple[str, bytes, dict[str, object]]:
    version_prefix = EXPECTED_VERSION.split(".", 2)[:2]
    needle = ".".join(version_prefix).lower()
    candidates = [tag for tag in tags if needle in tag.lower()]
    exact: list[tuple[str, bytes, dict[str, object]]] = []
    observations: list[str] = []
    for tag in candidates:
        url = raw_url(tag, "package.json")
        package_bytes = download(url, limit=MAX_JSON_BYTES, missing_ok=True)
        if package_bytes is None:
            observations.append(f"{tag}: no package.json")
            continue
        package = load_json(package_bytes, url)
        if not isinstance(package, dict):
            observations.append(f"{tag}: package.json is not an object")
            continue
        version = package.get("version")
        observations.append(f"{tag}: version={version!r}")
        if version == EXPECTED_VERSION:
            exact.append((tag, package_bytes, package))
    if len(exact) != 1:
        raise RematerializationError(
            "OWA003C_EXACT_SOURCE_TAG_NOT_UNIQUE: "
            f"expected one tag for package version {EXPECTED_VERSION}, found {len(exact)}; "
            f"candidate observations={observations}"
        )
    return exact[0]


def package_files(package: dict[str, object]) -> list[dict[str, object]]:
    files = package.get("files")
    if not isinstance(files, list) or not files:
        raise RematerializationError("package.json has no non-empty files array")
    normalized = [item for item in files if isinstance(item, dict)]
    if len(normalized) != len(files):
        raise RematerializationError("package.json files array contains non-object entries")
    return normalized


def find_package_entry(files: list[dict[str, object]], localfile: str) -> dict[str, object]:
    matches = [entry for entry in files if entry.get("localfile") == localfile]
    if len(matches) != 1:
        raise RematerializationError(
            f"expected exactly one package entry for {localfile}, found {len(matches)}"
        )
    return matches[0]


def verify_raw_file(
    *,
    tag: str,
    files: list[dict[str, object]],
    localfile: str,
    limit: int,
) -> tuple[bytes, dict[str, object]]:
    entry = find_package_entry(files, localfile)
    url = raw_url(tag, localfile)
    data = download(url, limit=limit)
    if data is None:
        raise RematerializationError(f"missing raw file: {localfile}")
    expected_size = entry.get("unpackedsize")
    expected_hash = entry.get("unpackedhash")
    if not isinstance(expected_size, int) or isinstance(expected_size, bool) or expected_size < 0:
        raise RematerializationError(f"package entry has invalid unpackedsize: {localfile}")
    if not isinstance(expected_hash, str) or len(expected_hash) != 64:
        raise RematerializationError(f"package entry has invalid unpackedhash: {localfile}")
    actual_hash = sha256_bytes(data)
    if len(data) != expected_size:
        raise RematerializationError(
            f"raw size mismatch for {localfile}: expected {expected_size}, got {len(data)}"
        )
    if actual_hash != expected_hash.lower():
        raise RematerializationError(
            f"raw SHA-256 mismatch for {localfile}: expected {expected_hash.lower()}, got {actual_hash}"
        )
    return data, {
        "localPath": localfile,
        "sourceUrl": url,
        "byteSize": len(data),
        "sha256": actual_hash,
        "packageEntry": {
            "packedPath": entry.get("url"),
            "packedByteSize": entry.get("packedsize"),
            "packedSha256": entry.get("packedhash"),
            "unpackedByteSize": expected_size,
            "unpackedSha256": expected_hash.lower(),
        },
    }


def catalog_selection(catalog: object) -> dict[str, str]:
    if not isinstance(catalog, list):
        raise RematerializationError("catalog-content.json must contain an array")
    result: dict[str, str] = {}
    for role in ("staticdata", "staticmapdata", "proficiencies"):
        matches = [
            entry
            for entry in catalog
            if isinstance(entry, dict) and entry.get("type") == role
        ]
        if len(matches) != 1 or not isinstance(matches[0].get("file"), str):
            raise RematerializationError(
                f"expected exactly one catalog entry with type {role}, found {len(matches)}"
            )
        result[role] = str(matches[0]["file"])
    return result


def write_regular_file(path: pathlib.Path, data: bytes) -> None:
    if path.is_symlink():
        raise RematerializationError(f"output path must not be a symlink: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def main() -> int:
    if OUTPUT.exists():
        if OUTPUT.is_symlink() or not OUTPUT.is_dir():
            raise RematerializationError(f"output must be a regular directory: {OUTPUT}")
        if any(OUTPUT.iterdir()):
            raise RematerializationError(f"output directory must be empty: {OUTPUT}")
    else:
        OUTPUT.mkdir(parents=True, mode=0o700)

    tags = list_tags()
    tag, package_bytes, package = find_exact_tag(tags)
    files = package_files(package)

    catalog_bytes, catalog_audit = verify_raw_file(
        tag=tag,
        files=files,
        localfile="assets/catalog-content.json",
        limit=MAX_JSON_BYTES,
    )
    catalog = load_json(catalog_bytes, "assets/catalog-content.json")
    selected = catalog_selection(catalog)

    write_regular_file(OUTPUT / "package.json", package_bytes)
    write_regular_file(OUTPUT / "assets" / "catalog-content.json", catalog_bytes)

    selected_audit: list[dict[str, object]] = []
    for role, filename in sorted(selected.items()):
        localfile = f"assets/{filename}"
        data, audit = verify_raw_file(
            tag=tag,
            files=files,
            localfile=localfile,
            limit=MAX_FILE_BYTES,
        )
        write_regular_file(OUTPUT / localfile, data)
        selected_audit.append({"role": role, **audit})

    audit = {
        "format": "canary-owa-003c-exact-tag-rematerialization-v1",
        "sourceRepository": SOURCE_REPOSITORY,
        "sourceTag": tag,
        "expectedPackageVersion": EXPECTED_VERSION,
        "observedPackageVersion": package.get("version"),
        "packageManifest": {
            "path": "package.json",
            "byteSize": len(package_bytes),
            "sha256": sha256_bytes(package_bytes),
        },
        "catalogContent": catalog_audit,
        "selectedInputs": selected_audit,
        "verification": {
            "tagSelection": "exact-package-version-single-match",
            "fileVerification": "package-unpacked-size-and-sha256",
            "proprietaryPayloadCommitted": False,
        },
    }
    audit_bytes = (json.dumps(audit, indent=2, sort_keys=True) + "\n").encode("utf-8")
    write_regular_file(OUTPUT / "input-audit.json", audit_bytes)
    print(json.dumps(audit, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RematerializationError, subprocess.SubprocessError) as exc:
        raise SystemExit(f"OWA003C_REMATERIALIZATION_FAILED: {exc}") from exc
