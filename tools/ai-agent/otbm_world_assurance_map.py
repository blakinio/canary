from __future__ import annotations

import copy
import hashlib
import html
import json
import os
import re
from collections import Counter
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

CAMPAIGN_FORMAT = "canary-otbm-world-assurance-campaign-v1"
MAP_FORMAT = "canary-otbm-world-assurance-map-v1"
SCHEMA_VERSION = 1
TILE_SIZE = 32
PANEL_WIDTH = 520
PANEL_MARGIN = 16
MAX_TARGETS = 100
TARGET_CLASSES = {"region", "landmark-route", "quest", "mechanic-set"}
COVERAGE_STATES = {"proven", "blocked", "stale", "not-evaluated", "not-applicable"}
CERTIFICATION_LEVELS = {
    "C0_NOT_EVALUATED",
    "C1_STATIC_INDEXED",
    "C2_STATIC_CORRELATED",
    "C3_STATIC_REACHABLE",
    "C4_STATIC_QUALITY_GREEN",
    "C5_PHYSICAL_ROUTE_PROVEN",
    "C6_FEATURE_OR_MECHANIC_PHYSICALLY_PROVEN",
    "C7_CANDIDATE_CHANGE_REVALIDATED",
}
CERTIFICATION_STATES = {"certified", "not-evaluated", "blocked", "stale"}
FRESHNESS_STATES = {"current", "stale", "not-evaluated"}
FRESHNESS_DIMENSION_STATES = {"current", "stale", "not-compared"}
PHYSICAL_STATES = {"proven", "missing", "blocked", "stale", "not-evaluated"}
TARGET_STATES = {"certified", "blocked", "stale"}


class WorldAssuranceMapError(ValueError):
    pass


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _sha(value: Any, label: str) -> str:
    if not isinstance(value, str) or len(value) != 64 or any(ch not in "0123456789abcdef" for ch in value):
        raise WorldAssuranceMapError(f"{label} must be a lowercase SHA-256 digest")
    return value


def _obj(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise WorldAssuranceMapError(f"{label} must be an object")
    return value


def _arr(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise WorldAssuranceMapError(f"{label} must be an array")
    return value


def _str(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise WorldAssuranceMapError(f"{label} must be a non-empty string")
    return value.strip()


def _pos(value: Any, label: str) -> tuple[int, int, int]:
    if not isinstance(value, list) or len(value) != 3 or any(isinstance(v, bool) or not isinstance(v, int) for v in value):
        raise WorldAssuranceMapError(f"{label} must be [x,y,z]")
    position = int(value[0]), int(value[1]), int(value[2])
    if not (0 <= position[0] <= 65535 and 0 <= position[1] <= 65535 and 0 <= position[2] <= 15):
        raise WorldAssuranceMapError(f"{label} is outside OTBM coordinate range")
    return position


def _slug(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", value).strip("-.")
    return slug or hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def validate_campaign_report(campaign: Mapping[str, Any]) -> str:
    if campaign.get("format") != CAMPAIGN_FORMAT or campaign.get("schemaVersion") != 1:
        raise WorldAssuranceMapError(f"campaign must use {CAMPAIGN_FORMAT} schemaVersion 1")
    provided = _sha(campaign.get("reportSha256"), "campaign.reportSha256")
    payload = dict(campaign)
    payload.pop("reportSha256", None)
    calculated = canonical_sha256(payload)
    if calculated != provided:
        raise WorldAssuranceMapError("campaign reportSha256 does not match canonical report content")
    targets = _arr(campaign.get("targets"), "campaign.targets")
    if not targets:
        raise WorldAssuranceMapError("campaign.targets must not be empty")
    if len(targets) > MAX_TARGETS:
        raise WorldAssuranceMapError(f"campaign target count exceeds {MAX_TARGETS}")
    return provided


def _selected_targets(campaign: Mapping[str, Any], target_ids: Sequence[str]) -> list[tuple[int, Mapping[str, Any]]]:
    targets = _arr(campaign.get("targets"), "campaign.targets")
    ids = [_str(t.get("id"), f"campaign.targets[{i}].id") for i, t in enumerate(targets) if isinstance(t, Mapping)]
    if len(ids) != len(targets):
        raise WorldAssuranceMapError("every campaign target must be an object with an id")
    if len(ids) != len(set(ids)):
        raise WorldAssuranceMapError("campaign target ids must be unique")
    wanted = list(target_ids)
    if len(wanted) != len(set(wanted)):
        raise WorldAssuranceMapError("target ids must not be duplicated")
    unknown = sorted(set(wanted) - set(ids))
    if unknown:
        raise WorldAssuranceMapError(f"unknown campaign target ids: {unknown}")
    selected = set(wanted) if wanted else set(ids)
    return [(i, targets[i]) for i, target_id in enumerate(ids) if target_id in selected]


def _evidence_ref(report_sha256: str, target_index: int, pointer: str) -> str:
    suffix = pointer if pointer.startswith("/") else f"/{pointer}"
    return f"campaign:{report_sha256}#/targets/{target_index}{suffix}"


def _target_geometry(
    target: Mapping[str, Any], target_id: str
) -> tuple[tuple[int, int, int], tuple[int, int, int], tuple[int, int, int], tuple[int, int, int]]:
    reviewed = _obj(target.get("reviewedDefinition"), f"target {target_id}.reviewedDefinition")
    bounds = _obj(reviewed.get("routingBounds"), f"target {target_id}.reviewedDefinition.routingBounds")
    lower = _pos(bounds.get("from"), f"target {target_id}.routingBounds.from")
    upper = _pos(bounds.get("to"), f"target {target_id}.routingBounds.to")
    if any(lower[i] > upper[i] for i in range(3)):
        raise WorldAssuranceMapError(f"target {target_id} routing bounds are invalid")
    if lower[2] != upper[2]:
        raise WorldAssuranceMapError(f"target {target_id} visualization requires exactly one floor")
    origin = _pos(reviewed.get("origin"), f"target {target_id}.origin")
    destination = _pos(reviewed.get("destination"), f"target {target_id}.destination")
    for label, position in (("origin", origin), ("destination", destination)):
        if position[2] != lower[2] or not (lower[0] <= position[0] <= upper[0] and lower[1] <= position[1] <= upper[1]):
            raise WorldAssuranceMapError(f"target {target_id} {label} is outside reviewed routing bounds")
    return lower, upper, origin, destination


def _coverage_panel(target: Mapping[str, Any], target_index: int, report_sha256: str) -> dict[str, Any]:
    coverage = _obj(target.get("qa005Coverage"), "qa005Coverage")
    dimensions = _obj(coverage.get("dimensions"), "qa005Coverage.dimensions")
    rows: list[str] = []
    counts: Counter[str] = Counter()
    for name in sorted(dimensions):
        dimension = _obj(dimensions[name], f"qa005Coverage.dimensions.{name}")
        state = _str(dimension.get("state"), f"qa005Coverage.dimensions.{name}.state")
        if state not in COVERAGE_STATES:
            raise WorldAssuranceMapError(f"qa005Coverage dimension {name} has invalid state")
        counts[state] += 1
        rows.append(f"{name}: {state}")
    summary = ", ".join(f"{name}={counts[name]}" for name in sorted(counts)) or "no dimensions"
    return {
        "id": "qa005-coverage",
        "title": "QA-005 coverage dimensions",
        "value": summary,
        "detailLines": rows,
        "evidenceRefs": [_evidence_ref(report_sha256, target_index, "/qa005Coverage")],
    }


def _proof_panels(target: Mapping[str, Any], target_index: int, report_sha256: str) -> list[dict[str, Any]]:
    certification = _obj(target.get("qa006Certification"), "qa006Certification")
    freshness = _obj(target.get("qa016Freshness"), "qa016Freshness")
    physical = _obj(target.get("physicalE2e"), "physicalE2e")
    blockers = sorted({_str(v, "blockers[]") for v in _arr(target.get("blockers"), "blockers")})
    certification_level = _str(certification.get("certificationLevel"), "qa006Certification.certificationLevel")
    certification_state = _str(certification.get("certificationState"), "qa006Certification.certificationState")
    freshness_state = _str(freshness.get("state"), "qa016Freshness.state")
    physical_state = _str(physical.get("state"), "physicalE2e.state")
    proof_boundary = _str(physical.get("proofBoundary"), "physicalE2e.proofBoundary")
    if certification_level not in CERTIFICATION_LEVELS:
        raise WorldAssuranceMapError("qa006Certification.certificationLevel is invalid")
    if certification_state not in CERTIFICATION_STATES:
        raise WorldAssuranceMapError("qa006Certification.certificationState is invalid")
    if freshness_state not in FRESHNESS_STATES:
        raise WorldAssuranceMapError("qa016Freshness.state is invalid")
    if physical_state not in PHYSICAL_STATES:
        raise WorldAssuranceMapError("physicalE2e.state is invalid")
    freshness_lines = []
    for item in _arr(freshness.get("dimensions"), "qa016Freshness.dimensions"):
        item = _obj(item, "qa016Freshness.dimensions[]")
        dimension_id = _str(item.get("dimensionId"), "qa016Freshness.dimensions[].dimensionId")
        dimension_status = _str(item.get("status"), "qa016Freshness.dimensions[].status")
        if dimension_status not in FRESHNESS_DIMENSION_STATES:
            raise WorldAssuranceMapError(f"QA-016 dimension {dimension_id} has invalid status")
        freshness_lines.append(f"{dimension_id}: {dimension_status}")
    return [
        {
            "id": "qa006-certification",
            "title": "QA-006 formal certification",
            "value": f"{certification_level} ({certification_state})",
            "detailLines": [],
            "evidenceRefs": [_evidence_ref(report_sha256, target_index, "/qa006Certification")],
        },
        _coverage_panel(target, target_index, report_sha256),
        {
            "id": "qa016-freshness",
            "title": "QA-016 freshness",
            "value": freshness_state,
            "detailLines": freshness_lines,
            "evidenceRefs": [_evidence_ref(report_sha256, target_index, "/qa016Freshness")],
        },
        {
            "id": "physical-e2e",
            "title": "Retained route-level Physical E2E",
            "value": physical_state,
            "detailLines": [proof_boundary],
            "evidenceRefs": [_evidence_ref(report_sha256, target_index, "/physicalE2e")],
        },
        {
            "id": "blockers",
            "title": "Explicit blockers",
            "value": f"{len(blockers)} blocker(s)",
            "detailLines": blockers or ["none"],
            "evidenceRefs": [_evidence_ref(report_sha256, target_index, "/blockers")],
        },
    ]


def _annotations(
    target_index: int,
    report_sha256: str,
    lower: tuple[int, int, int],
    upper: tuple[int, int, int],
    origin: tuple[int, int, int],
    destination: tuple[int, int, int],
) -> list[dict[str, Any]]:
    width_tiles = upper[0] - lower[0] + 1
    height_tiles = upper[1] - lower[1] + 1

    def point_geometry(position: tuple[int, int, int]) -> dict[str, int]:
        return {
            "x": (position[0] - lower[0]) * TILE_SIZE + TILE_SIZE // 2,
            "y": (position[1] - lower[1]) * TILE_SIZE + TILE_SIZE // 2,
            "radius": 7,
        }

    return [
        {
            "id": "reviewed-routing-bounds",
            "kind": "region-outline",
            "geometry": {"x": 1, "y": 1, "width": width_tiles * TILE_SIZE - 2, "height": height_tiles * TILE_SIZE - 2},
            "label": "reviewed routing bounds",
            "evidenceRefs": [_evidence_ref(report_sha256, target_index, "/reviewedDefinition/routingBounds")],
        },
        {
            "id": "origin",
            "kind": "point",
            "geometry": point_geometry(origin),
            "label": f"origin {origin[0]},{origin[1]},{origin[2]}",
            "evidenceRefs": [_evidence_ref(report_sha256, target_index, "/reviewedDefinition/origin")],
        },
        {
            "id": "destination",
            "kind": "point",
            "geometry": point_geometry(destination),
            "label": f"destination {destination[0]},{destination[1]},{destination[2]}",
            "evidenceRefs": [_evidence_ref(report_sha256, target_index, "/reviewedDefinition/destination")],
        },
    ]


def build_world_assurance_map_plan(
    campaign: Mapping[str, Any], *, campaign_file_sha256: str, target_ids: Sequence[str] = ()
) -> dict[str, Any]:
    report_sha256 = validate_campaign_report(campaign)
    campaign_file_sha256 = _sha(campaign_file_sha256, "campaign_file_sha256")
    selected = _selected_targets(campaign, target_ids)
    targets: list[dict[str, Any]] = []
    source_map_hashes: set[str] = set()
    status_counts: Counter[str] = Counter()
    for target_index, target in selected:
        target_id = _str(target.get("id"), f"campaign.targets[{target_index}].id")
        target_class = _str(target.get("class"), f"target {target_id}.class")
        if target_class not in TARGET_CLASSES:
            raise WorldAssuranceMapError(f"target {target_id} has unsupported class")
        exact = _obj(target.get("exactProvenance"), f"target {target_id}.exactProvenance")
        source_map_sha = _sha(exact.get("sourceMapSha256"), f"target {target_id}.sourceMapSha256")
        world_index_sha = _sha(exact.get("worldIndexSha256"), f"target {target_id}.worldIndexSha256")
        source_map_hashes.add(source_map_sha)
        lower, upper, origin, destination = _target_geometry(target, target_id)
        width = (upper[0] - lower[0] + 1) * TILE_SIZE
        height = (upper[1] - lower[1] + 1) * TILE_SIZE
        status = _str(target.get("status"), f"target {target_id}.status")
        if status not in TARGET_STATES:
            raise WorldAssuranceMapError(f"target {target_id} has invalid status")
        status_counts[status] += 1
        slug = _slug(target_id)
        targets.append(
            {
                "id": target_id,
                "class": target_class,
                "status": status,
                "exactProvenance": {"sourceMapSha256": source_map_sha, "worldIndexSha256": world_index_sha},
                "bounds": {"from": list(lower), "to": list(upper)},
                "baseRender": {
                    "renderer": "tools/ai-agent/otbm_renderer.py:render_region",
                    "output": f"{slug}-base.png",
                    "executed": False,
                    "outputSha256": None,
                    "width": width,
                    "height": height,
                    "source": None,
                    "summary": None,
                },
                "overlay": {
                    "output": f"{slug}-coverage.svg",
                    "executed": False,
                    "outputSha256": None,
                    "canvas": {"mapWidth": width, "mapHeight": height, "panelWidth": PANEL_WIDTH},
                    "annotations": _annotations(target_index, report_sha256, lower, upper, origin, destination),
                    "panels": _proof_panels(target, target_index, report_sha256),
                },
            }
        )
    if len(source_map_hashes) != 1:
        raise WorldAssuranceMapError("one visualization run requires selected targets from exactly one source-map SHA-256")
    report = {
        "format": MAP_FORMAT,
        "schemaVersion": SCHEMA_VERSION,
        "campaign": {
            "format": CAMPAIGN_FORMAT,
            "campaignId": _str(campaign.get("campaignId"), "campaign.campaignId"),
            "fileSha256": campaign_file_sha256,
            "reportSha256": report_sha256,
        },
        "sourceMapSha256": next(iter(source_map_hashes)),
        "targets": targets,
        "summary": {"targets": len(targets), "byStatus": dict(sorted(status_counts.items()))},
        "policy": {
            "existingRendererReused": True,
            "mapImageRenderer": "tools/ai-agent/otbm_renderer.py:render_region",
            "overlayContainsMapTerrain": False,
            "routeGeometryInferred": False,
            "pathfindingPerformed": False,
            "qaValidatorsRerun": False,
            "physicalE2eRun": False,
            "aiImageGenerationUsed": False,
            "mapModified": False,
            "compositeHealthScoreProduced": False,
            "colourIsProof": False,
            "generatedArtifactsCommitted": False,
        },
    }
    report["reportSha256"] = canonical_sha256(report)
    return report


def _confined(root: Path, path: Path, label: str, *, must_exist: bool) -> Path:
    root = root.expanduser().resolve()
    candidate = path.expanduser()
    candidate = candidate if candidate.is_absolute() else root / candidate
    if candidate.is_symlink():
        raise WorldAssuranceMapError(f"{label} must not be a symlink: {candidate}")
    resolved = candidate.resolve(strict=must_exist)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise WorldAssuranceMapError(f"{label} escapes artifact root {root}: {resolved}") from exc
    return resolved


def _relative(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def _is_within(parent: Path, child: Path) -> bool:
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


def _wrap(value: str, width: int = 64) -> list[str]:
    words = value.split()
    if not words:
        return [""]
    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        candidate = f"{current} {word}"
        if len(candidate) <= width:
            current = candidate
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def _svg_for_target(target: Mapping[str, Any], *, image_href: str) -> str:
    base = _obj(target.get("baseRender"), "baseRender")
    overlay = _obj(target.get("overlay"), "overlay")
    map_width = int(base.get("width", 0))
    map_height = int(base.get("height", 0))
    if map_width <= 0 or map_height <= 0:
        raise WorldAssuranceMapError("base render dimensions must be positive")
    panel_x = map_width + PANEL_MARGIN
    panel_lines: list[tuple[str, list[str], list[str]]] = []
    for panel in _arr(overlay.get("panels"), "overlay.panels"):
        p = _obj(panel, "overlay panel")
        title = _str(p.get("title"), "panel.title")
        lines = [_str(p.get("value"), "panel.value")]
        for detail in _arr(p.get("detailLines"), "panel.detailLines"):
            lines.extend(_wrap(_str(detail, "panel.detailLines[]")))
        refs = [_str(v, "panel.evidenceRefs[]") for v in _arr(p.get("evidenceRefs"), "panel.evidenceRefs")]
        if not refs:
            raise WorldAssuranceMapError(f"visible panel {p.get('id')} has no evidence reference")
        panel_lines.append((title, lines, refs))
    panel_height = PANEL_MARGIN
    for _title, lines, _refs in panel_lines:
        panel_height += 48 + max(1, len(lines)) * 18 + 12
    canvas_width = map_width + PANEL_WIDTH + PANEL_MARGIN * 2
    canvas_height = max(map_height, panel_height + PANEL_MARGIN)
    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_width}" height="{canvas_height}" viewBox="0 0 {canvas_width} {canvas_height}">',
        '<rect width="100%" height="100%" fill="#f5f5f5"/>',
        f'<image href="{html.escape(_str(image_href, "image_href"), quote=True)}" x="0" y="0" width="{map_width}" height="{map_height}">',
        f'<title>{html.escape("map-sha256:" + target["exactProvenance"]["sourceMapSha256"])}</title>',
        '</image>',
    ]
    for annotation in _arr(overlay.get("annotations"), "overlay.annotations"):
        a = _obj(annotation, "overlay annotation")
        refs = [_str(v, "annotation.evidenceRefs[]") for v in _arr(a.get("evidenceRefs"), "annotation.evidenceRefs")]
        if not refs:
            raise WorldAssuranceMapError(f"visible annotation {a.get('id')} has no evidence reference")
        title = html.escape(f"{a.get('label')} | {' | '.join(refs)}")
        geometry = _obj(a.get("geometry"), "annotation.geometry")
        if a.get("kind") == "region-outline":
            parts.extend(
                [
                    f'<rect x="{geometry["x"]}" y="{geometry["y"]}" width="{geometry["width"]}" height="{geometry["height"]}" fill="none" stroke="#202020" stroke-width="3" stroke-dasharray="8 5">',
                    f'<title>{title}</title></rect>',
                ]
            )
        elif a.get("kind") == "point":
            x, y, radius = geometry["x"], geometry["y"], geometry["radius"]
            parts.extend(
                [
                    f'<circle cx="{x}" cy="{y}" r="{radius}" fill="#ffffff" stroke="#111111" stroke-width="3"><title>{title}</title></circle>',
                    f'<text x="{x + 10}" y="{y - 10}" font-family="monospace" font-size="14" fill="#111111">{html.escape(_str(a.get("label"), "annotation.label"))}<title>{title}</title></text>',
                ]
            )
        else:
            raise WorldAssuranceMapError(f"unsupported annotation kind: {a.get('kind')}")
    y = PANEL_MARGIN
    for title, lines, refs in panel_lines:
        height = 48 + max(1, len(lines)) * 18 + 12
        evidence_title = html.escape(" | ".join(refs))
        parts.append(
            f'<g><title>{evidence_title}</title><rect x="{panel_x}" y="{y}" width="{PANEL_WIDTH - PANEL_MARGIN}" height="{height}" rx="8" fill="#ffffff" stroke="#444444" stroke-width="1"/>'
        )
        parts.append(
            f'<text x="{panel_x + 14}" y="{y + 24}" font-family="sans-serif" font-size="16" font-weight="bold" fill="#111111">{html.escape(title)}</text>'
        )
        line_y = y + 46
        for line in lines:
            parts.append(
                f'<text x="{panel_x + 14}" y="{line_y}" font-family="monospace" font-size="13" fill="#222222">{html.escape(line)}</text>'
            )
            line_y += 18
        parts.append("</g>")
        y += height + 10
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def _atomic_write_text(path: Path, content: str, *, overwrite: bool) -> None:
    if path.is_symlink():
        raise WorldAssuranceMapError(f"output must not be a symlink: {path}")
    if path.exists() and not overwrite:
        raise WorldAssuranceMapError(f"output already exists: {path}; pass overwrite=True")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    if temporary.is_symlink():
        raise WorldAssuranceMapError(f"temporary output must not be a symlink: {temporary}")
    temporary.unlink(missing_ok=True)
    try:
        temporary.write_text(content, encoding="utf-8")
        os.replace(temporary, path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def materialize_world_assurance_map(
    plan: Mapping[str, Any],
    *,
    artifact_root: Path,
    map_path: Path,
    assets_root: Path,
    output_directory: Path,
    overwrite: bool = False,
    renderer: Callable[..., Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    if plan.get("format") != MAP_FORMAT or plan.get("schemaVersion") != 1:
        raise WorldAssuranceMapError(f"plan must use {MAP_FORMAT} schemaVersion 1")
    supplied_hash = _sha(plan.get("reportSha256"), "plan.reportSha256")
    unsigned = dict(plan)
    unsigned.pop("reportSha256", None)
    if canonical_sha256(unsigned) != supplied_hash:
        raise WorldAssuranceMapError("plan reportSha256 does not match canonical plan content")
    root = artifact_root.expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    if root.is_symlink():
        raise WorldAssuranceMapError("artifact root must not be a symlink")
    source_map = _confined(root, map_path, "source map", must_exist=True)
    assets = _confined(root, assets_root, "assets root", must_exist=True)
    output = _confined(root, output_directory, "output directory", must_exist=False)
    if not source_map.is_file():
        raise WorldAssuranceMapError("source map must be a regular file")
    if not assets.is_dir():
        raise WorldAssuranceMapError("assets root must be a directory")
    if output.exists() and output.is_symlink():
        raise WorldAssuranceMapError("output directory must not be a symlink")
    if _is_within(assets, output):
        raise WorldAssuranceMapError("output directory must not be inside the client assets root")
    if output == source_map or output == assets:
        raise WorldAssuranceMapError("output directory collides with an input")
    expected_map_sha = _sha(plan.get("sourceMapSha256"), "plan.sourceMapSha256")
    actual_map_sha = sha256_path(source_map)
    if actual_map_sha != expected_map_sha:
        raise WorldAssuranceMapError("source map SHA-256 does not match campaign provenance")
    output.mkdir(parents=True, exist_ok=True)
    if output.is_symlink():
        raise WorldAssuranceMapError("output directory must not be a symlink")
    if renderer is None:
        from otbm_renderer import render_region as renderer

    result = copy.deepcopy(dict(plan))
    result.pop("reportSha256", None)
    for target in result["targets"]:
        base = target["baseRender"]
        overlay = target["overlay"]
        base_path = output / base["output"]
        overlay_path = output / overlay["output"]
        for candidate in (base_path, overlay_path):
            if candidate.is_symlink():
                raise WorldAssuranceMapError(f"output must not be a symlink: {candidate}")
            if candidate.exists() and not overwrite:
                raise WorldAssuranceMapError(f"output already exists: {candidate}; pass overwrite=True")
            if candidate.resolve(strict=False) in {source_map, assets}:
                raise WorldAssuranceMapError("output path collides with an input")
        bounds = (tuple(target["bounds"]["from"]), tuple(target["bounds"]["to"]))
        temporary = base_path.with_name(f".{base_path.name}.{os.getpid()}.tmp")
        if temporary.is_symlink():
            raise WorldAssuranceMapError(f"temporary render output must not be a symlink: {temporary}")
        temporary.unlink(missing_ok=True)
        try:
            render_report = renderer(source_map, assets, bounds, temporary, padding_tiles=0, max_tiles=1_000_000)
            if not isinstance(render_report, Mapping) or not render_report.get("ok"):
                raise WorldAssuranceMapError(f"existing factual renderer reported errors for {target['id']}")
            source = _obj(render_report.get("source"), "renderer.source")
            if source.get("mapSha256") != expected_map_sha:
                raise WorldAssuranceMapError("existing factual renderer reported unexpected source-map SHA-256")
            render_bounds = _obj(render_report.get("bounds"), "renderer.bounds")
            if render_bounds.get("from") != target["bounds"]["from"] or render_bounds.get("to") != target["bounds"]["to"]:
                raise WorldAssuranceMapError("existing factual renderer reported unexpected bounds")
            os.replace(temporary, base_path)
        except Exception:
            temporary.unlink(missing_ok=True)
            raise
        base["executed"] = True
        base["output"] = _relative(root, base_path)
        base["outputSha256"] = sha256_path(base_path)
        base["source"] = {
            "mapSha256": source.get("mapSha256"),
            "assetCatalogSha256": source.get("assetCatalogSha256"),
            "appearancesSha256": source.get("appearancesSha256"),
        }
        base["summary"] = dict(_obj(render_report.get("summary"), "renderer.summary"))
        overlay["output"] = _relative(root, overlay_path)
        svg = _svg_for_target(target, image_href=base_path.name)
        _atomic_write_text(overlay_path, svg, overwrite=overwrite)
        overlay["executed"] = True
        overlay["outputSha256"] = sha256_path(overlay_path)
    result["execution"] = {
        "artifactRoot": ".",
        "sourceMap": _relative(root, source_map),
        "assetsRoot": _relative(root, assets),
        "outputDirectory": _relative(root, output),
        "sourceMapSha256": actual_map_sha,
    }
    result["reportSha256"] = canonical_sha256(result)
    return result


def write_manifest(path: Path, report: Mapping[str, Any], *, overwrite: bool = False) -> None:
    _atomic_write_text(path, json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n", overwrite=overwrite)
