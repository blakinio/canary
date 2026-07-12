#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
VIEWS = ROOT / "schema/gameplay_analytics_views.sql"
DASHBOARD = ROOT / "grafana/gameplay-analytics-dashboard.json"
DATASOURCE_EXAMPLE = ROOT / "grafana/provisioning/datasources/mariadb.yaml.example"
DASHBOARD_PROVISIONING_EXAMPLE = ROOT / "grafana/provisioning/dashboards/gameplay-analytics.yaml.example"
DOCS = ROOT / "docs/systems/gameplay-analytics-dashboards.md"

REQUIRED_VIEWS = {
    "analytics_daily_vocation_metrics",
    "analytics_daily_party_mode_metrics",
    "analytics_dead_letter_health",
    "analytics_session_drilldown",
    "analytics_spell_efficiency_drilldown",
}

REQUIRED_PANEL_TITLES = {
    "EXP/h by vocation, level bracket, hunt area and server version",
    "DPS, damage taken/s and healing/s",
    "Deaths per 100 sessions",
    "Solo versus party: EXP/h",
    "Shared experience ratio",
    "Spell efficiency",
    "Profit and supply cost per hour (NPC value)",
    "Session counts and minimum sample-size warning",
    "Persisted dead-letter sessions",
    "Queue, retry and flush health",
}

SERIES_DIMENSION_PANELS = {
    "EXP/h by vocation, level bracket, hunt area and server version",
    "DPS, damage taken/s and healing/s",
    "Deaths per 100 sessions",
    "Solo versus party: EXP/h",
    "Shared experience ratio",
    "Profit and supply cost per hour (NPC value)",
}

FORBIDDEN_VARIABLE_NAMES = {"player", "player_id", "player_name", "character", "character_name"}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read(path: Path) -> str:
    require(path.is_file(), f"missing file: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def validate_views(text: str) -> None:
    for view in REQUIRED_VIEWS:
        require(
            f"CREATE OR REPLACE VIEW `{view}`" in text,
            f"missing repeatable reporting view: {view}",
        )
    for column in ("NULLIF(", "`combat_seconds`"):
        require(column in text, f"reporting views must guard divide-by-zero with {column}")
    require(
        "FROM `analytics_daily_party_balance`" in text,
        "solo-versus-party reporting must read the dedicated party aggregate",
    )
    require(
        "`party_mode` AS `mode`" in text,
        "solo-versus-party reporting must preserve the mode assigned before daily grouping",
    )
    require(
        "LEAST(100.00" in text,
        "shared-experience reporting must cap malformed or legacy values at 100 percent",
    )
    require("COUNT(*) AS `dead_letter_records`" in text, "dead-letter view must expose terminal record count")
    require("COUNT(*) AS `pending_dead_letters`" in text, "dead-letter view must retain the compatibility alias")
    require("not an active database replay queue" in text, "dead-letter view must document terminal semantics")


def collect_panels(panels: list[dict]) -> list[dict]:
    collected: list[dict] = []
    for panel in panels:
        collected.append(panel)
        collected.extend(collect_panels(panel.get("panels", [])))
    return collected


def validate_dashboard(raw: str) -> dict:
    try:
        dashboard = json.loads(raw)
    except json.JSONDecodeError as error:
        raise AssertionError(f"dashboard JSON is not valid: {error}") from error

    require("panels" in dashboard and isinstance(dashboard["panels"], list), "dashboard must define panels")
    panels = collect_panels(dashboard["panels"])
    panels_by_title = {panel.get("title"): panel for panel in panels if panel.get("title")}

    missing = REQUIRED_PANEL_TITLES - set(panels_by_title)
    require(not missing, f"dashboard is missing required panels: {', '.join(sorted(missing))}")

    variables = dashboard.get("templating", {}).get("list", [])
    variable_names = {variable.get("name", "").lower() for variable in variables}
    forbidden = variable_names & FORBIDDEN_VARIABLE_NAMES
    require(not forbidden, f"dashboard must not define per-player variables: {', '.join(sorted(forbidden))}")

    def collect_datasource_types(node) -> set[str]:
        types: set[str] = set()
        if isinstance(node, dict):
            if "datasource" in node and isinstance(node["datasource"], dict):
                datasource_type = node["datasource"].get("type")
                if datasource_type:
                    types.add(datasource_type)
            for value in node.values():
                types |= collect_datasource_types(value)
        elif isinstance(node, list):
            for item in node:
                types |= collect_datasource_types(item)
        return types

    datasource_types = collect_datasource_types(dashboard)
    require(datasource_types == {"mysql"}, f"every panel must use the mysql (MariaDB-compatible) datasource, found: {datasource_types}")

    for title in SERIES_DIMENSION_PANELS:
        panel = panels_by_title[title]
        targets = panel.get("targets", [])
        require(targets, f"series panel has no query targets: {title}")
        for target in targets:
            sql = target.get("rawSql", "")
            metric_expression = sql.split(" AS metric", 1)[0]
            for dimension in ("level_bracket", "hunt_area", "server_version"):
                require(dimension in metric_expression, f"{title} metric label lacks {dimension}")
            require("hunt_area IN ($hunt_area)" in sql, f"{title} lacks the hunt-area filter")
            require("server_version IN ($server_version)" in sql, f"{title} lacks the server-version filter")

    dead_letter_panel = panels_by_title["Persisted dead-letter sessions"]
    dead_letter_sql = " ".join(target.get("rawSql", "") for target in dead_letter_panel.get("targets", []))
    require("dead_letter_records" in dead_letter_sql, "dead-letter panel must query terminal record count")
    require("pending_dead_letters" not in dead_letter_sql, "dead-letter panel must not label terminal records as pending retries")
    require("not an active database replay queue" in dead_letter_panel.get("description", ""), "dead-letter panel description must be truthful")

    return dashboard


def validate_datasource_example(text: str) -> None:
    require("type: mysql" in text, "datasource example must use the mysql plugin type")
    require("CHANGE_ME" in text, "datasource example must ship placeholder connection values, not real ones")
    require("password:" not in text.split("secureJsonData:")[0], "password must live under secureJsonData, not in plain fields")
    require(
        "commit the filled-in" in text,
        "datasource example must warn against committing real credentials",
    )


def validate_dashboard_provisioning_example(text: str) -> None:
    require("type: file" in text, "dashboard provisioning example must use the file provider")
    require("folder:" in text, "dashboard provisioning example must place the dashboard in its own folder")


def validate_docs(text: str) -> None:
    for phrase in (
        "## Import",
        "## Upgrade",
        "## Empty datasets",
        "## No per-player variables",
        "## Minimum sample size",
        "## Indexes and query cost",
        "## Solo versus party semantics",
        "## Shared-experience percentage",
        "## Series identity",
        "terminal failure records",
        "CREATE OR REPLACE VIEW",
        "analytics_daily_party_balance",
        "drill-down",
    ):
        require(phrase in text, f"dashboard documentation lacks: {phrase}")


def main() -> int:
    try:
        validate_views(read(VIEWS))
        validate_dashboard(read(DASHBOARD))
        validate_datasource_example(read(DATASOURCE_EXAMPLE))
        validate_dashboard_provisioning_example(read(DASHBOARD_PROVISIONING_EXAMPLE))
        validate_docs(read(DOCS))
    except AssertionError as error:
        print(f"gameplay analytics dashboard validation failed: {error}", file=sys.stderr)
        return 1

    print("gameplay analytics dashboard validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
