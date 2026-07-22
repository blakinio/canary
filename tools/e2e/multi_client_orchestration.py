#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")
ENV_RE = re.compile(r"^[A-Z_][A-Z0-9_]*$")
MAX_TEXT = 128


class MultiClientError(ValueError):
    pass


def _mapping(value: Any, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise MultiClientError(f"{path} must be an object")
    return value


def _string(mapping: dict[str, Any], key: str, path: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value.strip():
        raise MultiClientError(f"{path}.{key} must be a non-empty string")
    value = value.strip()
    if len(value) > MAX_TEXT or any(ch in value for ch in "\r\n\x00"):
        raise MultiClientError(f"{path}.{key} contains unsupported control data or exceeds {MAX_TEXT} characters")
    return value


def _reject_unknown(mapping: dict[str, Any], allowed: set[str], path: str) -> None:
    unknown = sorted(set(mapping) - allowed)
    if unknown:
        raise MultiClientError(f"{path} contains unknown field(s): {', '.join(unknown)}")


def compile_secondary(manifest: dict[str, Any], *, artifact_dir: Path) -> dict[str, str]:
    root = _mapping(manifest, "manifest")
    scenario = _mapping(root.get("scenario"), "manifest.scenario")
    fixture = _mapping(scenario.get("fixture"), "manifest.scenario.fixture")
    primary_account = _string(fixture, "account", "manifest.scenario.fixture")
    primary_character = _string(fixture, "character", "manifest.scenario.fixture")

    multi = _mapping(scenario.get("multi_client"), "manifest.scenario.multi_client")
    _reject_unknown(multi, {"schema_version", "secondary"}, "manifest.scenario.multi_client")
    if multi.get("schema_version") != SCHEMA_VERSION:
        raise MultiClientError(
            f"manifest.scenario.multi_client.schema_version must be {SCHEMA_VERSION}"
        )

    secondary = _mapping(multi.get("secondary"), "manifest.scenario.multi_client.secondary")
    _reject_unknown(
        secondary,
        {"id", "account", "password_env", "character"},
        "manifest.scenario.multi_client.secondary",
    )
    actor_id = _string(secondary, "id", "manifest.scenario.multi_client.secondary")
    if not SLUG_RE.fullmatch(actor_id):
        raise MultiClientError(f"secondary.id must match {SLUG_RE.pattern}")
    account = _string(secondary, "account", "manifest.scenario.multi_client.secondary")
    password_env = _string(secondary, "password_env", "manifest.scenario.multi_client.secondary")
    character = _string(secondary, "character", "manifest.scenario.multi_client.secondary")
    if not ENV_RE.fullmatch(password_env):
        raise MultiClientError(f"secondary.password_env must match {ENV_RE.pattern}")
    if account == primary_account:
        raise MultiClientError("secondary account must differ from primary account")
    if character == primary_character:
        raise MultiClientError("secondary character must differ from primary character")

    actor_dir = artifact_dir / "actors" / actor_id
    release_file = artifact_dir / f"multi-client-{actor_id}.release"
    return {
        "AGENT_E2E_ACTOR_ID": actor_id,
        "AGENT_E2E_ACCOUNT": account,
        "AGENT_E2E_PASSWORD_ENV": password_env,
        "AGENT_E2E_CHARACTER": character,
        "AGENT_E2E_PRIMARY_CHARACTER": primary_character,
        "AGENT_E2E_ARTIFACT_DIR": str(actor_dir),
        "AGENT_E2E_SECONDARY_RELEASE_FILE": str(release_file),
        "AGENT_E2E_SCENARIO_KEY": f"{root.get('key', 'unknown')}#{actor_id}",
    }


def materialize(manifest_path: Path, artifact_dir: Path) -> dict[str, str]:
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise MultiClientError(f"cannot read scenario manifest: {exc}") from exc

    artifact_dir.mkdir(parents=True, exist_ok=True)
    values = compile_secondary(manifest, artifact_dir=artifact_dir.resolve())
    actor_dir = Path(values["AGENT_E2E_ARTIFACT_DIR"])
    actor_dir.mkdir(parents=True, exist_ok=True)

    env_path = artifact_dir / "multi-client-secondary.env"
    env_path.write_text(
        "".join(f"{key}={value}\n" for key, value in values.items()),
        encoding="utf-8",
    )
    evidence = {
        "schema_version": SCHEMA_VERSION,
        "primary_character": values["AGENT_E2E_PRIMARY_CHARACTER"],
        "secondary": {
            "id": values["AGENT_E2E_ACTOR_ID"],
            "account": values["AGENT_E2E_ACCOUNT"],
            "character": values["AGENT_E2E_CHARACTER"],
            "password_env": values["AGENT_E2E_PASSWORD_ENV"],
            "artifact_dir": values["AGENT_E2E_ARTIFACT_DIR"],
            "release_file": values["AGENT_E2E_SECONDARY_RELEASE_FILE"],
        },
    }
    (artifact_dir / "multi-client-plan.json").write_text(
        json.dumps(evidence, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return values


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate and materialize bounded Universal E2E two-client actor metadata.")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--artifact-dir", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        materialize(args.manifest, args.artifact_dir)
    except MultiClientError as exc:
        print(f"ERROR: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
