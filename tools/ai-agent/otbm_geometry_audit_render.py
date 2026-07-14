from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Mapping

from otbm_geometry_audit_types import GeometryAuditError, RENDER_FORMAT, REPORT_FORMAT, SCHEMA_VERSION, sha256_path


def _bounded_region(position: tuple[int, int, int], radius: int) -> tuple[tuple[int, int, int], tuple[int, int, int]]:
    x, y, z = position
    return (
        (max(0, x - radius), max(0, y - radius), z),
        (min(0xFFFF, x + radius), min(0xFFFF, y + radius), z),
    )


def build_render_manifest(
    report: Mapping[str, Any],
    *,
    map_path: Path,
    assets_path: Path,
    output_dir: Path,
    radius: int = 8,
    max_requests: int = 100,
) -> dict[str, Any]:
    if report.get("format") != REPORT_FORMAT:
        raise GeometryAuditError("render manifest requires canary-otbm-geometry-audit-v1")
    if not isinstance(radius, int) or isinstance(radius, bool) or not 0 <= radius <= 64:
        raise GeometryAuditError("render radius must be in 0..64")
    if not isinstance(max_requests, int) or isinstance(max_requests, bool) or not 1 <= max_requests <= 1000:
        raise GeometryAuditError("max_requests must be in 1..1000")
    findings = report.get("findings")
    if not isinstance(findings, list):
        raise GeometryAuditError("geometry audit report does not contain findings")
    requests: list[dict[str, Any]] = []
    seen_regions: set[tuple[tuple[int, int, int], tuple[int, int, int]]] = set()
    for finding in findings:
        if len(requests) >= max_requests:
            break
        if not isinstance(finding, dict):
            continue
        raw_position = finding.get("position")
        if not (
            isinstance(raw_position, list)
            and len(raw_position) == 3
            and all(isinstance(part, int) and not isinstance(part, bool) for part in raw_position)
        ):
            continue
        position = int(raw_position[0]), int(raw_position[1]), int(raw_position[2])
        lower, upper = _bounded_region(position, radius)
        region = (lower, upper)
        if region in seen_regions:
            continue
        seen_regions.add(region)
        finding_id = str(finding.get("id", "finding"))
        request_id = hashlib.sha256(f"{finding_id}:{lower}:{upper}".encode("utf-8")).hexdigest()[:20]
        output = output_dir / f"geometry-{request_id}-z{position[2]}.png"
        report_output = output.with_suffix(".json")
        command = [
            "python",
            "tools/ai-agent/otbm_render_tool.py",
            str(map_path),
            str(assets_path),
            "--from",
            f"{lower[0]},{lower[1]},{lower[2]}",
            "--to",
            f"{upper[0]},{upper[1]},{upper[2]}",
            "--output",
            str(output),
            "--report",
            str(report_output),
        ]
        requests.append(
            {
                "id": request_id,
                "findingId": finding_id,
                "kind": finding.get("kind"),
                "position": list(position),
                "region": {"from": list(lower), "to": list(upper)},
                "output": str(output),
                "reportOutput": str(report_output),
                "command": command,
            }
        )
    map_record: dict[str, Any] = {"path": str(map_path)}
    if map_path.is_file() and not map_path.is_symlink():
        map_record.update({"size": map_path.stat().st_size, "sha256": sha256_path(map_path)})
    return {
        "format": RENDER_FORMAT,
        "schemaVersion": SCHEMA_VERSION,
        "policy": {
            "existingRendererRequired": True,
            "aiImageryUsed": False,
            "mapModified": False,
            "oneFloorPerRequest": True,
        },
        "sourceReport": {
            "format": REPORT_FORMAT,
            "scope": report.get("scope"),
            "findingTotal": report.get("summary", {}).get("findings", {}).get("total")
            if isinstance(report.get("summary"), dict)
            else None,
        },
        "inputs": {
            "map": map_record,
            "assets": {"path": str(assets_path)},
        },
        "requestCount": len(requests),
        "truncated": sum(1 for finding in findings if isinstance(finding, dict) and "position" in finding) > len(requests),
        "requests": requests,
    }
