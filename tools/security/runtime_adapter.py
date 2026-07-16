#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import ipaddress
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.e2e import run_agent_e2e as e2e  # noqa: E402
from tools.security import security_validation as sv  # noqa: E402

SCHEMA_VERSION = 1
ADAPTER_SCHEMA = "ots-security-runtime-adapter-v1"
REPORT_SCHEMA = "ots-security-runtime-delegation-v1"
NETWORK_POLICY = "literal-loopback-only"


class RuntimeAdapterError(ValueError):
    pass


@dataclass(frozen=True)
class Provider:
    provider_id: str
    workflow: str
    resolver: str
    runner: str
    allowed_client_repositories: tuple[str, ...]


PROVIDERS = {
    "universal-e2e": Provider(
        provider_id="universal-e2e",
        workflow=".github/workflows/universal-agent-e2e.yml",
        resolver="tools/e2e/run_agent_e2e.py",
        runner="tools/e2e/run_physical_e2e.sh",
        allowed_client_repositories=("blakinio/otclient",),
    )
}


@dataclass(frozen=True)
class RuntimeAdapter:
    path: Path
    data: dict[str, Any]
    provider: Provider
    provider_files: tuple[Path, ...]

    @property
    def adapter_id(self) -> str:
        return str(self.data["id"])


def repository_root() -> Path:
    return ROOT


def adapter_root(root: Path) -> Path:
    return root / "tests" / "security" / "runtime_adapters"


def _mapping(value: Any, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise RuntimeAdapterError(f"{path} must be an object")
    return value


def _exact_keys(mapping: dict[str, Any], required: set[str], path: str) -> None:
    missing = sorted(required - set(mapping))
    unknown = sorted(set(mapping) - required)
    if missing:
        raise RuntimeAdapterError(f"{path} missing required field(s): {', '.join(missing)}")
    if unknown:
        raise RuntimeAdapterError(f"{path} contains unsupported field(s): {', '.join(unknown)}")


def _string(mapping: dict[str, Any], key: str, path: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value.strip():
        raise RuntimeAdapterError(f"{path}.{key} must be a non-empty string")
    return value.strip()


def _provider_paths(provider: Provider) -> tuple[str, ...]:
    return (provider.workflow, provider.resolver, provider.runner)


def validate_adapter(path: Path, root: Path) -> RuntimeAdapter:
    expected_root = adapter_root(root).resolve()
    if path.is_symlink():
        raise RuntimeAdapterError(f"runtime adapter manifest must not be a symlink: {path}")
    try:
        resolved_path = path.resolve()
        resolved_path.relative_to(expected_root)
    except ValueError as exc:
        raise RuntimeAdapterError(f"runtime adapter manifest must remain under {expected_root}: {path}") from exc

    try:
        data = json.loads(resolved_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeAdapterError(f"{path}: invalid JSON: {exc}") from exc
    except OSError as exc:
        raise RuntimeAdapterError(f"{path}: cannot read runtime adapter: {exc}") from exc

    data = _mapping(data, "adapter")
    _exact_keys(
        data,
        {
            "schema_version",
            "id",
            "target_adapter",
            "component",
            "authorization",
            "delegate",
            "confinement",
        },
        "adapter",
    )
    if data["schema_version"] != SCHEMA_VERSION:
        raise RuntimeAdapterError(f"adapter.schema_version must be {SCHEMA_VERSION}")

    adapter_id = _string(data, "id", "adapter")
    target_adapter = _string(data, "target_adapter", "adapter")
    component = _string(data, "component", "adapter")
    if not sv.SLUG_RE.fullmatch(adapter_id):
        raise RuntimeAdapterError(f"adapter.id must match {sv.SLUG_RE.pattern}")
    if not sv.SLUG_RE.fullmatch(target_adapter):
        raise RuntimeAdapterError(f"adapter.target_adapter must match {sv.SLUG_RE.pattern}")
    if component not in sv.COMPONENTS:
        raise RuntimeAdapterError(f"adapter.component must be one of {sorted(sv.COMPONENTS)}")

    authorization = _mapping(data["authorization"], "adapter.authorization")
    _exact_keys(authorization, {"scope", "repository"}, "adapter.authorization")
    if _string(authorization, "scope", "adapter.authorization") != "repository":
        raise RuntimeAdapterError("adapter.authorization.scope must be 'repository'")
    repository = _string(authorization, "repository", "adapter.authorization")
    if not sv.REPOSITORY_RE.fullmatch(repository):
        raise RuntimeAdapterError("adapter.authorization.repository must be in owner/name form")

    delegate = _mapping(data["delegate"], "adapter.delegate")
    _exact_keys(delegate, {"provider", "suite", "scenario"}, "adapter.delegate")
    provider_id = _string(delegate, "provider", "adapter.delegate")
    suite = _string(delegate, "suite", "adapter.delegate")
    scenario = _string(delegate, "scenario", "adapter.delegate")
    if not sv.SLUG_RE.fullmatch(suite):
        raise RuntimeAdapterError(f"adapter.delegate.suite must match {sv.SLUG_RE.pattern}")
    if not sv.SLUG_RE.fullmatch(scenario):
        raise RuntimeAdapterError(f"adapter.delegate.scenario must match {sv.SLUG_RE.pattern}")
    provider = PROVIDERS.get(provider_id)
    if provider is None:
        raise RuntimeAdapterError(
            f"adapter.delegate.provider must be one of {sorted(PROVIDERS)}, got {provider_id!r}"
        )

    confinement = _mapping(data["confinement"], "adapter.confinement")
    _exact_keys(confinement, {"network"}, "adapter.confinement")
    if _string(confinement, "network", "adapter.confinement") != NETWORK_POLICY:
        raise RuntimeAdapterError(f"adapter.confinement.network must be {NETWORK_POLICY!r}")

    try:
        provider_files = tuple(
            sv._regular_repository_file(root, raw_path, f"provider.{provider.provider_id}")
            for raw_path in _provider_paths(provider)
        )
    except sv.SecurityScenarioError as exc:
        raise RuntimeAdapterError(str(exc)) from exc

    return RuntimeAdapter(path=resolved_path, data=data, provider=provider, provider_files=provider_files)


def discover(root: Path) -> list[RuntimeAdapter]:
    directory = adapter_root(root)
    if not directory.is_dir():
        raise RuntimeAdapterError(f"runtime adapter directory does not exist: {directory}")

    adapters: list[RuntimeAdapter] = []
    errors: list[str] = []
    for path in sorted(directory.rglob("*.json")):
        try:
            adapters.append(validate_adapter(path, root))
        except RuntimeAdapterError as exc:
            errors.append(f"{path}: {exc}")
    if errors:
        raise RuntimeAdapterError("\n".join(errors))
    if not adapters:
        raise RuntimeAdapterError(f"no runtime adapters found under {directory}")

    seen: dict[str, Path] = {}
    for adapter in adapters:
        previous = seen.get(adapter.adapter_id)
        if previous:
            raise RuntimeAdapterError(
                f"duplicate runtime adapter id {adapter.adapter_id}: {previous} and {adapter.path}"
            )
        seen[adapter.adapter_id] = adapter.path
    return adapters


def select(adapters: Iterable[RuntimeAdapter], adapter_id: str) -> RuntimeAdapter:
    matches = [adapter for adapter in adapters if adapter.adapter_id == adapter_id]
    if len(matches) != 1:
        available = ", ".join(sorted(adapter.adapter_id for adapter in adapters))
        raise RuntimeAdapterError(f"runtime adapter {adapter_id!r} not found; available: {available}")
    return matches[0]


def _file_evidence(path: Path, root: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    return {
        "path": path.resolve().relative_to(root.resolve()).as_posix(),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "size_bytes": len(raw),
    }


def _literal_loopback(host: str) -> ipaddress.IPv4Address | ipaddress.IPv6Address:
    try:
        address = ipaddress.ip_address(host)
    except ValueError as exc:
        raise RuntimeAdapterError(
            f"delegated E2E host must be a literal loopback IP address, got {host!r}"
        ) from exc
    if not address.is_loopback:
        raise RuntimeAdapterError(f"delegated E2E host must be loopback, got {host!r}")
    return address


def resolve_adapter(adapter: RuntimeAdapter, root: Path, authorized_repository: str) -> dict[str, Any]:
    expected_repository = str(adapter.data["authorization"]["repository"])
    if expected_repository != authorized_repository:
        raise RuntimeAdapterError(
            f"runtime adapter {adapter.adapter_id} is authorized for {expected_repository}, not {authorized_repository}"
        )

    delegate = adapter.data["delegate"]
    try:
        scenarios = e2e.discover(root)
        scenario = e2e.select(scenarios, str(delegate["suite"]), str(delegate["scenario"]))
    except e2e.ScenarioError as exc:
        raise RuntimeAdapterError(f"delegated Universal E2E scenario is invalid: {exc}") from exc

    fixture = scenario.data["fixture"]
    host = str(fixture["host"])
    address = _literal_loopback(host)
    game_port = int(fixture["game_port"])

    client_repository = str(scenario.data["client"]["repository"])
    if client_repository not in adapter.provider.allowed_client_repositories:
        raise RuntimeAdapterError(
            "delegated E2E client repository is not approved for this provider: "
            f"{client_repository!r}"
        )

    provider_evidence = {
        key: _file_evidence(root / raw_path, root)
        for key, raw_path in (
            ("workflow", adapter.provider.workflow),
            ("resolver", adapter.provider.resolver),
            ("runner", adapter.provider.runner),
        )
    }
    scenario_evidence = _file_evidence(scenario.path, root)

    return {
        "schema": REPORT_SCHEMA,
        "schema_version": SCHEMA_VERSION,
        "adapter_schema": ADAPTER_SCHEMA,
        "adapter_id": adapter.adapter_id,
        "adapter_source": adapter.path.resolve().relative_to(root.resolve()).as_posix(),
        "target_adapter": adapter.data["target_adapter"],
        "component": adapter.data["component"],
        "authorization": adapter.data["authorization"],
        "delegate": {
            "provider": adapter.provider.provider_id,
            "scenario_key": scenario.key,
            "suite": scenario.suite,
            "scenario": scenario.scenario_id,
            "scenario_source": scenario_evidence,
            "client_repository": client_repository,
            "client_ref": str(scenario.data["client"]["ref"]),
            "provider_files": provider_evidence,
        },
        "confinement": {
            "network_policy": NETWORK_POLICY,
            "host": host,
            "host_ip_version": address.version,
            "host_is_loopback": True,
            "game_port": game_port,
        },
        "result": "pass",
    }


def render_report(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, sort_keys=True) + "\n"


def write_report(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(render_report(report), encoding="utf-8")
    temporary.replace(path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate and resolve code-owned OTS security runtime adapters."
    )
    parser.add_argument("--root", type=Path, default=repository_root())
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("list", help="List validated runtime adapters.")
    subparsers.add_parser("validate", help="Validate every runtime adapter without resolving a target.")

    resolve = subparsers.add_parser(
        "resolve", help="Resolve one authorized runtime adapter into deterministic delegation evidence."
    )
    resolve.add_argument("--adapter", required=True)
    resolve.add_argument("--authorized-repository", required=True)
    resolve.add_argument("--report", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    root = args.root.resolve()
    try:
        adapters = discover(root)
        if args.command == "list":
            for adapter in adapters:
                delegate = adapter.data["delegate"]
                print(
                    f"{adapter.adapter_id}\t{adapter.data['component']}\t"
                    f"{delegate['provider']}\t{delegate['suite']}/{delegate['scenario']}"
                )
            return 0
        if args.command == "validate":
            print(f"Validated {len(adapters)} security runtime adapter(s).")
            return 0
        if args.command == "resolve":
            adapter = select(adapters, args.adapter)
            report = resolve_adapter(adapter, root, args.authorized_repository)
            if args.report:
                write_report(args.report, report)
            else:
                sys.stdout.write(render_report(report))
            return 0
        parser.error(f"unsupported command {args.command}")  # pragma: no cover
    except (RuntimeAdapterError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
