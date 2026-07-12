from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

from otbm_script_resolution_parser import DEFAULT_DATAPACKS, ENGINE_GENERIC_ACTION_IDS, REPORT_FORMAT
from otbm_script_resolution_scan import scan_repository


def load_item_scan(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("format") != "canary-otbm-item-scan-v1":
        raise ValueError(f"Unsupported item scan format: {payload.get('format')!r}")
    if not isinstance(payload.get("mechanicPlacements"), list):
        raise ValueError("Item scan has no mechanicPlacements array")
    return payload


def _registration_identity(registration: dict[str, Any]) -> tuple[Any, ...]:
    return (
        registration["handlerKind"],
        registration["eventType"],
        registration["path"],
        registration["object"],
    )


def _build_indexes(registrations: list[dict[str, Any]]) -> tuple[dict[tuple[str, Any], list[dict[str, Any]]], dict[int, list[dict[str, Any]]]]:
    direct: dict[tuple[str, Any], list[dict[str, Any]]] = defaultdict(list)
    item_handlers: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for registration in registrations:
        for value in registration.get("values", []):
            if registration["namespace"] == "itemId" and isinstance(value, int):
                item_handlers[value].append(registration)
            else:
                direct[(registration["namespace"], tuple(value) if isinstance(value, list) else value)].append(registration)
    return direct, item_handlers


def _classify_handlers(handlers: list[dict[str, Any]]) -> tuple[str, list[dict[str, Any]]]:
    unique: dict[tuple[Any, ...], dict[str, Any]] = {_registration_identity(handler): handler for handler in handlers}
    values = list(unique.values())
    if not values:
        return "unresolved", []
    if len(values) > 1:
        return "handled-multiple", values
    registration_type = values[0].get("registrationType")
    if registration_type == "range" or registration_type == "xml-range":
        return "handled-by-range", values
    if registration_type == "target-reference":
        return "handled-as-target", values
    return "handled-directly", values


def resolve_report(repository_scan: dict[str, Any], item_scan: dict[str, Any]) -> dict[str, Any]:
    registrations = repository_scan["registrations"]
    direct, item_handlers = _build_indexes(registrations)
    placements_out: list[dict[str, Any]] = []
    identifier_entries: dict[str, dict[int, dict[str, Any]]] = {
        "actionId": {},
        "uniqueId": {},
    }
    conflict_map: dict[tuple[str, int, str, str], list[dict[str, Any]]] = defaultdict(list)
    resolved_placements = 0
    unresolved_placements = 0
    partial_placements = 0
    status_counter: Counter[str] = Counter()

    for placement in item_scan["mechanicPlacements"]:
        results: list[dict[str, Any]] = []
        if "teleportDestination" in placement:
            results.append({"mechanic": "teleportDestination", "status": "handled-by-engine", "handlers": []})
        if "houseDoorId" in placement:
            results.append({"mechanic": "houseDoorId", "status": "handled-by-engine", "handlers": []})
        for namespace in ("uniqueId", "actionId"):
            value = placement.get(namespace)
            if not isinstance(value, int):
                continue
            handlers = list(direct.get((namespace, value), []))
            status, resolved_handlers = _classify_handlers(handlers)
            if status == "unresolved" and namespace == "actionId" and value in ENGINE_GENERIC_ACTION_IDS:
                status = "handled-generically"
            if status == "unresolved":
                fallback = item_handlers.get(int(placement["itemId"]), [])
                if fallback:
                    status = "handled-by-item-id"
                    resolved_handlers = fallback
            results.append({"mechanic": namespace, "value": value, "status": status, "handlers": resolved_handlers})
            entry = identifier_entries[namespace].setdefault(
                value,
                {
                    "value": value,
                    "placements": 0,
                    "itemIds": Counter(),
                    "positions": [],
                    "statuses": Counter(),
                    "handlers": {},
                },
            )
            entry["placements"] += 1
            entry["itemIds"][int(placement["itemId"])] += 1
            entry["positions"].append(placement["position"])
            entry["statuses"][status] += 1
            for handler in resolved_handlers:
                entry["handlers"][_registration_identity(handler)] = handler
                if status not in {"handled-by-item-id", "handled-as-target", "handled-generically"} and handler.get("registrationType") != "target-reference":
                    conflict_map[(namespace, value, handler["handlerKind"], handler["eventType"])].append(handler)
        statuses = [result["status"] for result in results]
        unresolved = sum(status == "unresolved" for status in statuses)
        if unresolved == 0:
            placement_status = "resolved"
            resolved_placements += 1
        elif unresolved == len(statuses):
            placement_status = "unresolved"
            unresolved_placements += 1
        else:
            placement_status = "partially-resolved"
            partial_placements += 1
        status_counter.update(statuses)
        placements_out.append({**placement, "status": placement_status, "resolutions": results})

    identifiers_out: dict[str, list[dict[str, Any]]] = {}
    unresolved_identifiers = 0
    partially_resolved_identifiers = 0
    for namespace, entries in identifier_entries.items():
        serialized: list[dict[str, Any]] = []
        for value in sorted(entries):
            entry = entries[value]
            statuses = entry["statuses"]
            if set(statuses) == {"unresolved"}:
                overall = "unresolved"
                unresolved_identifiers += 1
            elif "unresolved" in statuses:
                overall = "partially-resolved"
                partially_resolved_identifiers += 1
            elif len(statuses) == 1:
                overall = next(iter(statuses))
            else:
                overall = "handled-multiple"
            serialized.append(
                {
                    "value": value,
                    "placements": entry["placements"],
                    "status": overall,
                    "statusCounts": dict(sorted(statuses.items())),
                    "itemIds": [
                        {"id": item_id, "placements": count}
                        for item_id, count in sorted(entry["itemIds"].items())
                    ],
                    "positions": entry["positions"],
                    "handlers": list(entry["handlers"].values()),
                }
            )
        identifiers_out[namespace] = serialized

    conflicts: list[dict[str, Any]] = []
    for (namespace, value, handler_kind, event_type), handlers in sorted(conflict_map.items()):
        unique = {_registration_identity(handler): handler for handler in handlers}
        if len(unique) <= 1:
            continue
        conflicts.append(
            {
                "namespace": namespace,
                "value": value,
                "handlerKind": handler_kind,
                "eventType": event_type,
                "handlers": list(unique.values()),
                "reason": "Multiple active registrations compete in the same dispatch namespace and event type.",
            }
        )

    summary = {
        "filesScanned": int(repository_scan["filesScanned"]),
        "registrations": len(registrations),
        "dynamicRegistrations": len(repository_scan["dynamicRegistrations"]),
        "mechanicPlacements": len(item_scan["mechanicPlacements"]),
        "resolvedPlacements": resolved_placements,
        "partiallyResolvedPlacements": partial_placements,
        "unresolvedPlacements": unresolved_placements,
        "unresolvedIdentifiers": unresolved_identifiers,
        "partiallyResolvedIdentifiers": partially_resolved_identifiers,
        "conflicts": len(conflicts),
        "statusCounts": dict(sorted(status_counter.items())),
    }
    return {
        "format": REPORT_FORMAT,
        "ok": not conflicts,
        "sources": {"map": item_scan.get("source", {}), "datapacks": list(DEFAULT_DATAPACKS)},
        "summary": summary,
        "registrations": registrations,
        "dynamicRegistrations": repository_scan["dynamicRegistrations"],
        "identifiers": identifiers_out,
        "conflicts": conflicts,
        "mechanicPlacements": placements_out,
        "notes": [
            "The resolver is conservative: unresolved dynamic registrations remain visible instead of being guessed.",
            "Action ID 2000 is classified as the generic quest-chest mechanic.",
            "Teleport destinations and house-door IDs are classified as engine-handled mechanics.",
            "Item-ID fallback follows Canary dispatch after unique/action ID lookup.",
        ],
    }


def build_report(root: Path, item_scan_path: Path, datapacks: Iterable[str] = DEFAULT_DATAPACKS) -> dict[str, Any]:
    repository_scan = scan_repository(root, datapacks)
    item_scan = load_item_scan(item_scan_path)
    return resolve_report(repository_scan, item_scan)


def write_report(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
