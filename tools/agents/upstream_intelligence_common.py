#!/usr/bin/env python3
"""Shared contracts and GitHub API access for upstream intelligence."""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from real_tibia_registry_lib import Registry, RegistryError, load_json, schema_errors

ROOT = Path(__file__).resolve().parents[2]
CONFIG_ROOT = Path("docs/agents/upstream")
SOURCE_CONFIG = CONFIG_ROOT / "registry/sources.yaml"
DECISION_DIR = CONFIG_ROOT / "registry/decisions"
SCHEMA_DIR = CONFIG_ROOT / "schemas"

REVIEWED_STATUSES = {
    "already-present", "blocked-by-dependency", "blocked-by-version", "canary-superior",
    "client-coupled", "conflicting", "dangerous", "donor-only", "equivalent-local",
    "implemented-local", "needs-triage", "no-longer-applicable", "partial-value",
    "rejected", "superseded", "valid-fix-missing",
}


class UpstreamError(RuntimeError):
    """Raised when configuration or scanning cannot be completed safely."""


@dataclass(frozen=True)
class ValidationResult:
    errors: tuple[str, ...]
    warnings: tuple[str, ...]

    @property
    def ok(self) -> bool:
        return not self.errors


def utc_now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0)


def iso_z(value: dt.datetime) -> str:
    return value.astimezone(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_time(value: object) -> dt.datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return (parsed if parsed.tzinfo else parsed.replace(tzinfo=dt.timezone.utc)).astimezone(dt.timezone.utc)


def stable_fingerprint(value: Mapping[str, Any]) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _json_request(url: str, token: str | None, *, opener: Any, timeout: int = 30) -> Any:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "blakinio-canary-upstream-intelligence/1",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    try:
        with opener(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", "replace")[:500]
        raise UpstreamError(f"GET {url}: HTTP {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise UpstreamError(f"GET {url}: {exc.reason}") from exc
    except (OSError, json.JSONDecodeError) as exc:
        raise UpstreamError(f"GET {url}: invalid response: {exc}") from exc


class GitHubClient:
    def __init__(self, token: str | None, opener: Any = urllib.request.urlopen) -> None:
        self.token = token
        self.opener = opener
        self.base = "https://api.github.com"

    def get(self, path: str, params: Mapping[str, object] | None = None) -> Any:
        query = ""
        if params:
            query = "?" + urllib.parse.urlencode(
                {key: str(value) for key, value in params.items() if value is not None}
            )
        return _json_request(self.base + path + query, self.token, opener=self.opener)

    def paged(
        self,
        path: str,
        params: Mapping[str, object],
        *,
        max_pages: int,
        max_items: int,
    ) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        page_size = min(100, max_items)
        for page in range(1, max_pages + 1):
            payload = self.get(path, {**params, "per_page": page_size, "page": page})
            if not isinstance(payload, list):
                raise UpstreamError(f"{path}: expected array response")
            for row in payload:
                if isinstance(row, dict):
                    items.append(row)
                    if len(items) >= max_items:
                        return items
            if len(payload) < page_size:
                break
        return items


def _domain_validate_sources(config: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(config, dict):
        return ["source registry: expected object"]
    report = config.get("report")
    if not isinstance(report, dict) or report.get("repository") != "blakinio/canary":
        errors.append("source registry: report.repository must be blakinio/canary")
    sources = config.get("sources")
    if not isinstance(sources, list) or not sources:
        return errors + ["source registry: sources must be a non-empty array"]
    seen_ids: set[str] = set()
    seen_repositories: set[str] = set()
    for index, source in enumerate(sources):
        label = f"sources[{index}]"
        if not isinstance(source, dict):
            errors.append(f"{label}: expected object")
            continue
        source_id = source.get("id")
        repository = source.get("repository")
        if not isinstance(source_id, str) or not source_id:
            errors.append(f"{label}: id is required")
        elif source_id in seen_ids:
            errors.append(f"{label}: duplicate id {source_id}")
        else:
            seen_ids.add(source_id)
        if not isinstance(repository, str) or repository.count("/") != 1:
            errors.append(f"{label}: repository must be owner/name")
        elif repository in seen_repositories:
            errors.append(f"{label}: duplicate repository {repository}")
        else:
            seen_repositories.add(repository)
        if source.get("writable") is not False:
            errors.append(f"{label}: writable must be false")
        daily = source.get("daily_file_details")
        deep = source.get("deep_file_details")
        if isinstance(daily, int) and isinstance(deep, int) and daily > deep:
            errors.append(f"{label}: daily_file_details must not exceed deep_file_details")
    return errors


def load_decisions(
    root: Path, module_ids: set[str]
) -> tuple[dict[str, dict[str, Any]], list[str], list[str]]:
    decisions: dict[str, dict[str, Any]] = {}
    errors: list[str] = []
    warnings: list[str] = []
    directory = root / DECISION_DIR
    if not directory.exists():
        return decisions, errors, warnings
    schema = root / SCHEMA_DIR / "decision.schema.json"
    for path in sorted(directory.glob("*.yaml")):
        value = load_json(path)
        errors.extend(schema_errors(path, value, schema))
        if not isinstance(value, dict):
            errors.append(f"{path}: expected object")
            continue
        candidate_id = value.get("candidate_id")
        if not isinstance(candidate_id, str) or not candidate_id:
            errors.append(f"{path}: candidate_id is required")
            continue
        if candidate_id in decisions:
            errors.append(f"{path}: duplicate candidate_id {candidate_id}")
        if value.get("status") not in REVIEWED_STATUSES:
            errors.append(f"{path}: unsupported status {value.get('status')!r}")
        revision = value.get("candidate_revision")
        if not isinstance(revision, str) or not re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", revision):
            errors.append(f"{path}: candidate_revision must be exact lowercase SHA/fingerprint")
        modules = value.get("modules", [])
        if not isinstance(modules, list):
            errors.append(f"{path}: modules must be an array")
        else:
            for module_id in modules:
                if module_id not in module_ids:
                    errors.append(f"{path}: unknown module {module_id!r}")
        local_sha = value.get("local_sha")
        if local_sha is not None and not (
            isinstance(local_sha, str) and re.fullmatch(r"[0-9a-f]{40}", local_sha)
        ):
            errors.append(f"{path}: local_sha must be null or exact lowercase SHA")
        decisions[candidate_id] = value
    return decisions, errors, warnings


def validate_repository(root: Path = ROOT) -> ValidationResult:
    errors: list[str] = []
    warnings: list[str] = []
    source_path = root / SOURCE_CONFIG
    config = load_json(source_path)
    errors.extend(schema_errors(source_path, config, root / SCHEMA_DIR / "source.schema.json"))
    errors.extend(_domain_validate_sources(config))
    try:
        registry = Registry.load(root)
    except (RegistryError, OSError) as exc:
        return ValidationResult((f"module registry: {exc}",), ())
    _, decision_errors, decision_warnings = load_decisions(root, set(registry.modules))
    errors.extend(decision_errors)
    warnings.extend(decision_warnings)
    return ValidationResult(tuple(sorted(set(errors))), tuple(sorted(set(warnings))))
