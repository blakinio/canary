#!/usr/bin/env python3
"""Validate, query, and generate the Real Tibia module registry.

Registry .yaml files use the YAML 1.2 JSON-compatible subset, so normal
operation needs only Python's standard library. CI installs jsonschema to
also enforce the published Draft 2020-12 schemas.
"""
from __future__ import annotations

import datetime as dt
import fnmatch
import json
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[2]
FILES = (
    "MODULE_INDEX.md",
    "MODULE_DEPENDENCIES.md",
    "MODULE_PATH_INDEX.md",
    "SOURCE_INDEX.md",
    "STALE_MODULES.md",
)
BUCKETS = ("server", "client", "data", "tests", "docs")


class RegistryError(RuntimeError):
    """Raised when registry files cannot be loaded or queried safely."""


@dataclass(frozen=True)
class ValidationResult:
    errors: tuple[str, ...]
    warnings: tuple[str, ...]

    @property
    def ok(self) -> bool:
        return not self.errors


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise RegistryError(f"{path}: cannot read: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise RegistryError(
            f"{path}: registry YAML must use the YAML 1.2 JSON-compatible subset: "
            f"{exc.msg} at line {exc.lineno}, column {exc.colno}"
        ) from exc


def normalise(value: str) -> str:
    value = value.replace("\\", "/").strip()
    while value.startswith("./"):
        value = value[2:]
    return value


def safe_path(value: object) -> bool:
    if not isinstance(value, str):
        return False
    value = normalise(value)
    return (
        bool(value)
        and not value.startswith("/")
        and "\x00" not in value
        and ".." not in PurePosixPath(value).parts
    )


def schema_errors(path: Path, value: Any, schema: Path) -> list[str]:
    try:
        import jsonschema  # type: ignore
    except ModuleNotFoundError:
        return []
    validator = jsonschema.Draft202012Validator(
        load_json(schema), format_checker=jsonschema.FormatChecker()
    )
    errors: list[str] = []
    for error in sorted(
        validator.iter_errors(value), key=lambda item: list(item.absolute_path)
    ):
        location = "/".join(str(part) for part in error.absolute_path)
        errors.append(
            f"{path}: schema validation failed"
            f"{f' at {location}' if location else ''}: {error.message}"
        )
    return errors


def indexed(
    rows: object, field: str, label: str, errors: list[str]
) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    if not isinstance(rows, list):
        errors.append(f"{label}: expected an array")
        return result
    for index, row in enumerate(rows):
        if (
            not isinstance(row, dict)
            or not isinstance(row.get(field), str)
            or not row[field]
        ):
            errors.append(f"{label}[{index}]: missing non-empty {field}")
            continue
        key = row[field]
        if key in result:
            errors.append(f"{label}: duplicate {field} {key!r}")
        result[key] = row
    return result


class Registry:
    def __init__(
        self,
        root: Path,
        categories: dict[str, dict[str, Any]],
        sources: dict[str, dict[str, Any]],
        baselines: dict[str, dict[str, Any]],
        modules: dict[str, dict[str, Any]],
        paths: dict[str, Path],
    ) -> None:
        self.root = root
        self.categories = categories
        self.sources = sources
        self.baselines = baselines
        self.modules = modules
        self.module_paths = paths

    @property
    def registry_root(self) -> Path:
        return self.root / "docs/agents/real-tibia"

    @classmethod
    def load(cls, root: Path = ROOT) -> "Registry":
        registry = root / "docs/agents/real-tibia"
        documents = {
            "categories": load_json(registry / "registry/categories.yaml"),
            "sources": load_json(registry / "registry/sources.yaml"),
            "baselines": load_json(registry / "registry/versions.yaml"),
        }
        errors: list[str] = []
        categories = indexed(
            documents["categories"].get("categories"), "id", "categories", errors
        )
        sources = indexed(
            documents["sources"].get("sources"), "id", "sources", errors
        )
        baselines = indexed(
            documents["baselines"].get("baselines"), "id", "baselines", errors
        )
        if errors:
            raise RegistryError("; ".join(errors))
        module_dir = registry / "registry/modules"
        if not module_dir.is_dir():
            raise RegistryError(f"{module_dir}: module directory is missing")
        modules: dict[str, dict[str, Any]] = {}
        paths: dict[str, Path] = {}
        for path in sorted(module_dir.glob("*.yaml")):
            value = load_json(path)
            module_id = value.get("module_id") if isinstance(value, dict) else None
            if not isinstance(module_id, str) or not module_id:
                raise RegistryError(f"{path}: missing module_id")
            if module_id in modules:
                raise RegistryError(
                    f"{path}: duplicate module_id {module_id!r}; "
                    f"first defined in {paths[module_id]}"
                )
            modules[module_id], paths[module_id] = value, path
        return cls(root, categories, sources, baselines, modules, paths)

    def validate(self) -> ValidationResult:
        registry_root = self.registry_root
        errors: list[str] = []
        warnings: list[str] = []
        documents = {
            "categories": load_json(registry_root / "registry/categories.yaml"),
            "sources": load_json(registry_root / "registry/sources.yaml"),
            "versions": load_json(registry_root / "registry/versions.yaml"),
        }
        errors += schema_errors(
            registry_root / "registry/categories.yaml",
            documents["categories"],
            registry_root / "schemas/category.schema.json",
        )
        errors += schema_errors(
            registry_root / "registry/sources.yaml",
            documents["sources"],
            registry_root / "schemas/source.schema.json",
        )
        errors += schema_errors(
            registry_root / "registry/versions.yaml",
            documents["versions"],
            registry_root / "schemas/version.schema.json",
        )
        writable = sorted(
            key for key, row in self.sources.items() if row.get("writable") is True
        )
        if writable != ["canary-current"]:
            errors.append(
                "sources: exactly canary-current must be writable; found "
                + (", ".join(writable) or "none")
            )
        for key, baseline in sorted(self.baselines.items()):
            server = baseline.get("server", {})
            sha = server.get("sha") if isinstance(server, dict) else None
            if (
                not isinstance(sha, str)
                or len(sha) != 40
                or any(ch not in "0123456789abcdef" for ch in sha)
            ):
                errors.append(
                    f"baseline {key}: server.sha must be an exact lowercase 40-char SHA"
                )
            try:
                dt.datetime.fromisoformat(str(baseline.get("captured_at")))
            except ValueError:
                errors.append(f"baseline {key}: captured_at must be ISO-8601")
        ids = set(self.modules)
        for module_id, module in sorted(self.modules.items()):
            path = self.module_paths[module_id]
            errors += schema_errors(
                path, module, registry_root / "schemas/module.schema.json"
            )
            if path.stem != module_id:
                errors.append(
                    f"{path}: filename must match module_id {module_id!r}"
                )
            if module.get("category") not in self.categories:
                errors.append(f"{path}: unknown category {module.get('category')!r}")
            lifecycle = module.get("lifecycle", {})
            linked_documents = module.get("documents", {})
            lifecycle_program = (
                lifecycle.get("program") if isinstance(lifecycle, dict) else None
            )
            documents_program = (
                linked_documents.get("program")
                if isinstance(linked_documents, dict)
                else None
            )
            if lifecycle_program != documents_program:
                errors.append(
                    f"{path}: lifecycle.program and documents.program must match"
                )
            linked = ([lifecycle_program] if lifecycle_program else []) + (
                linked_documents.get("validation", [])
                if isinstance(linked_documents, dict)
                else []
            )
            for linked_path in linked:
                if not safe_path(linked_path):
                    errors.append(f"{path}: unsafe document path {linked_path!r}")
                elif (
                    not any(token in linked_path for token in "*?[")
                    and not (self.root / normalise(linked_path)).exists()
                ):
                    warnings.append(
                        f"{path}: referenced document is not present in this checkout: "
                        f"{linked_path}"
                    )
            scope = module.get("scope", {})
            if not isinstance(scope, dict) or not scope.get("includes"):
                errors.append(f"{path}: scope.includes must not be empty")
            path_groups = module.get("paths", {})
            for bucket in BUCKETS:
                values = (
                    path_groups.get(bucket, [])
                    if isinstance(path_groups, dict)
                    else None
                )
                if not isinstance(values, list):
                    errors.append(f"{path}: paths.{bucket} must be an array")
                else:
                    for value in values:
                        if not safe_path(value):
                            errors.append(
                                f"{path}: unsafe paths.{bucket} entry {value!r}"
                            )
            relationships = module.get("relationships", {})
            for relation in ("depends_on", "interacts_with"):
                targets = (
                    relationships.get(relation, [])
                    if isinstance(relationships, dict)
                    else None
                )
                if not isinstance(targets, list):
                    errors.append(
                        f"{path}: relationships.{relation} must be an array"
                    )
                    continue
                for target in targets:
                    if target == module_id:
                        errors.append(f"{path}: module cannot {relation} itself")
                    elif target not in ids:
                        errors.append(
                            f"{path}: relationships.{relation} references "
                            f"unknown module {target!r}"
                        )
            seen: set[str] = set()
            requirements = module.get("source_requirements", [])
            if not isinstance(requirements, list):
                errors.append(f"{path}: source_requirements must be an array")
                requirements = []
            for requirement in requirements:
                source = (
                    requirement.get("source")
                    if isinstance(requirement, dict)
                    else None
                )
                if source not in self.sources:
                    errors.append(f"{path}: unknown source {source!r}")
                if source in seen:
                    errors.append(
                        f"{path}: duplicate source requirement {source!r}"
                    )
                if isinstance(source, str):
                    seen.add(source)
            if "canary-current" not in seen:
                errors.append(
                    f"{path}: canary-current source requirement is mandatory"
                )
            freshness = module.get("freshness", {})
            try:
                dt.date.fromisoformat(str(freshness.get("last_inventory")))
            except (AttributeError, ValueError):
                errors.append(
                    f"{path}: freshness.last_inventory must be YYYY-MM-DD"
                )
            warning = freshness.get("warning_after_days")
            invalid = freshness.get("invalid_after_days")
            if (
                isinstance(warning, int)
                and isinstance(invalid, int)
                and warning >= invalid
            ):
                errors.append(
                    f"{path}: warning_after_days must be lower than "
                    "invalid_after_days"
                )
        errors += self._cycle_errors()
        generated = registry_root / "generated"
        if generated.exists():
            unexpected = sorted(
                path.name
                for path in generated.iterdir()
                if path.is_file() and path.name not in FILES
            )
            if unexpected:
                errors.append(
                    "generated directory contains unregistered files: "
                    + ", ".join(unexpected)
                )
        return ValidationResult(
            tuple(sorted(set(errors))), tuple(sorted(set(warnings)))
        )

    def _cycle_errors(self) -> list[str]:
        state: dict[str, int] = {}
        stack: list[str] = []
        found: list[str] = []

        def visit(module_id: str) -> None:
            if state.get(module_id) == 2:
                return
            if state.get(module_id) == 1:
                start = stack.index(module_id)
                found.append(
                    "dependency cycle: "
                    + " -> ".join(stack[start:] + [module_id])
                )
                return
            state[module_id] = 1
            stack.append(module_id)
            for target in self.modules[module_id]["relationships"]["depends_on"]:
                if target in self.modules:
                    visit(target)
            stack.pop()
            state[module_id] = 2

        for module_id in sorted(self.modules):
            visit(module_id)
        return found

    def matched_modules(self, repo_path: str) -> list[tuple[str, str, str]]:
        path = normalise(repo_path)
        matches: list[tuple[str, str, str]] = []
        for module_id, module in sorted(self.modules.items()):
            for bucket in BUCKETS:
                for pattern in module["paths"][bucket]:
                    if fnmatch.fnmatchcase(path, pattern):
                        matches.append((module_id, bucket, pattern))
        return matches

    def affected_modules(self, paths: Iterable[str]) -> list[str]:
        return sorted(
            {
                module_id
                for path in paths
                for module_id, _, _ in self.matched_modules(path)
            }
        )

    def stale_rows(self, as_of: dt.date | None = None) -> list[dict[str, Any]]:
        today = as_of or dt.date.today()
        rows: list[dict[str, Any]] = []
        for module_id, module in sorted(self.modules.items()):
            freshness = module["freshness"]
            last = dt.date.fromisoformat(freshness["last_inventory"])
            age = (today - last).days
            if age >= freshness["invalid_after_days"]:
                state = "invalid"
            elif age >= freshness["warning_after_days"]:
                state = "warning"
            else:
                state = "current"
            rows.append(
                {
                    "module_id": module_id,
                    "last_inventory": last.isoformat(),
                    "age_days": age,
                    "state": state,
                    "warning_after_days": freshness["warning_after_days"],
                    "invalid_after_days": freshness["invalid_after_days"],
                }
            )
        return rows

    def generated_as_of(self) -> dt.date:
        dates: list[dt.date] = []
        for baseline in self.baselines.values():
            try:
                dates.append(
                    dt.datetime.fromisoformat(baseline["captured_at"]).date()
                )
            except (KeyError, TypeError, ValueError):
                pass
        if not dates:
            raise RegistryError(
                "versions: at least one valid captured_at timestamp is required"
            )
        return max(dates)

    @staticmethod
    def header(title: str) -> list[str]:
        return [
            f"# {title}",
            "",
            "> Generated by `tools/agents/real_tibia_registry.py`; do not edit manually.",
            "> Registry records and live GitHub state remain authoritative.",
            "",
        ]

    def generated_documents(
        self, as_of: dt.date | None = None
    ) -> dict[str, str]:
        module_lines = self.header("Real Tibia Module Index") + [
            "| Module | Category | Lifecycle | Implementation | Evidence | Protocol | Persistence | Tests | Runtime | E2E | Program |",
            "|---|---|---|---|---|---|---|---|---|---|---|",
        ]
        dependency_lines = self.header("Real Tibia Module Dependencies") + [
            "| Module | Depends on | Interacts with |",
            "|---|---|---|",
        ]
        path_rows: list[tuple[str, str, str]] = []
        for module_id, module in sorted(self.modules.items()):
            maturity = module["maturity"]
            program = module["documents"].get("program")
            module_lines.append(
                f"| `{module_id}` — {module['name']} | `{module['category']}` | "
                f"`{module['lifecycle']['status']}` | `{maturity['implementation']}` | "
                f"`{maturity['evidence']}` | `{maturity['protocol']}` | "
                f"`{maturity['persistence']}` | `{maturity['automated_tests']}` | "
                f"`{maturity['runtime_validation']}` | `{maturity['gameplay_e2e']}` | "
                f"{f'`{program}`' if program else '—'} |"
            )
            relationships = module["relationships"]
            depends_on = ", ".join(
                f"`{value}`" for value in relationships["depends_on"]
            ) or "—"
            interacts_with = ", ".join(
                f"`{value}`" for value in relationships["interacts_with"]
            ) or "—"
            dependency_lines.append(
                f"| `{module_id}` | {depends_on} | {interacts_with} |"
            )
            for bucket in BUCKETS:
                path_rows.extend(
                    (pattern, module_id, bucket)
                    for pattern in module["paths"][bucket]
                )
        module_lines += ["", f"Total modules: **{len(self.modules)}**.", ""]
        dependency_lines += [
            "",
            "Only `depends_on` must remain acyclic. `interacts_with` is descriptive and may be reciprocal.",
            "",
        ]
        path_lines = self.header("Real Tibia Module Path Index") + [
            "| Path pattern | Module | Bucket |",
            "|---|---|---|",
        ]
        path_lines += [
            f"| `{pattern}` | `{module_id}` | `{bucket}` |"
            for pattern, module_id, bucket in sorted(path_rows)
        ]
        path_lines += [
            "",
            "Path matches are discovery hints, not automatic edit authorization. Active task ownership remains authoritative.",
            "",
        ]
        source_lines = self.header("Real Tibia Source Index") + [
            "| Source | Type | Writable | Exact SHA required | Authority dimensions |",
            "|---|---|---:|---:|---|",
        ]
        for source_id, source in sorted(self.sources.items()):
            authority = "; ".join(
                f"`{key}`: {value}"
                for key, value in sorted(source["authority"].items())
            )
            source_lines.append(
                f"| `{source_id}` — {source['name']} | `{source['type']}` | "
                f"{'yes' if source['writable'] else 'no'} | "
                f"{'yes' if source['exact_sha_required'] else 'no'} | "
                f"{authority} |"
            )
        source_lines += [
            "",
            "No source is a universal source of truth; use the parity playbook's question-specific precedence.",
            "",
        ]
        date = as_of or self.generated_as_of()
        stale_lines = self.header("Real Tibia Registry Freshness") + [
            f"Evaluated as of **{date.isoformat()}**.",
            "",
            "| Module | Last inventory | Age (days) | State | Warning / invalid thresholds |",
            "|---|---:|---:|---|---|",
        ]
        stale_lines += [
            f"| `{row['module_id']}` | {row['last_inventory']} | "
            f"{row['age_days']} | `{row['state']}` | "
            f"{row['warning_after_days']} / {row['invalid_after_days']} |"
            for row in self.stale_rows(date)
        ]
        stale_lines += [
            "",
            "A stale inventory remains historical evidence, but it must not be presented as current-main proof.",
            "",
        ]
        return {
            "MODULE_INDEX.md": "\n".join(module_lines),
            "MODULE_DEPENDENCIES.md": "\n".join(dependency_lines),
            "MODULE_PATH_INDEX.md": "\n".join(path_lines),
            "SOURCE_INDEX.md": "\n".join(source_lines),
            "STALE_MODULES.md": "\n".join(stale_lines),
        }


def write_generated(
    registry: Registry, check: bool, as_of: dt.date | None
) -> int:
    output = registry.root / "docs/agents/real-tibia/generated"
    if not check:
        output.mkdir(parents=True, exist_ok=True)
    stale: list[str] = []
    for name, content in registry.generated_documents(as_of).items():
        path = output / name
        expected = content.rstrip() + "\n"
        if check:
            if not path.exists() or path.read_text(encoding="utf-8") != expected:
                stale.append(name)
        else:
            path.write_text(expected, encoding="utf-8")
    if stale:
        print(
            "generated files are stale or missing: " + ", ".join(stale),
            file=sys.stderr,
        )
        return 1
    return 0
