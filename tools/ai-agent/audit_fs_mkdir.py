#!/usr/bin/env python3
"""Generate deterministic CS-006 FS.mkdir evidence from tracked files."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT_MD = ROOT / "artifacts/upstream/crystalserver/CS006_FS_MKDIR_AUDIT.md"
OUT_JSON = ROOT / "artifacts/upstream/crystalserver/cs006_fs_mkdir_audit.json"


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=ROOT, text=True, capture_output=True, check=False)


def grep(pattern: str) -> list[dict[str, object]]:
    result = run(
        "git", "grep", "-n", "-I", "-E", pattern, "--", ".",
        ":!tools/ai-agent/audit_fs_mkdir.py",
        ":!.github/workflows/audit-fs-mkdir.yml",
        ":!artifacts/upstream/crystalserver/CS006_FS_MKDIR_AUDIT.md",
        ":!artifacts/upstream/crystalserver/cs006_fs_mkdir_audit.json",
    )
    if result.returncode not in (0, 1):
        raise RuntimeError(result.stderr)
    rows: list[dict[str, object]] = []
    for raw in result.stdout.splitlines():
        path, line, text = raw.split(":", 2)
        rows.append({"path": path, "line": int(line), "text": text.strip()})
    return rows


def context(path: str, line: int, radius: int = 5) -> list[str]:
    lines = (ROOT / path).read_text(encoding="utf-8", errors="replace").splitlines()
    start = max(1, line - radius)
    end = min(len(lines), line + radius)
    return [f"{number}: {lines[number - 1]}" for number in range(start, end + 1)]


def signals(lines: list[str]) -> list[str]:
    text = "\n".join(lines).lower()
    groups = {
        "configuration": ("config", "configmanager"),
        "environment": ("getenv", "os.getenv", "environment"),
        "network-request": ("request", "protocol", "packet", "http", "socket"),
        "player-user": ("player", "account", "character", "username"),
        "database": ("database", "db.", "query", "result.get"),
        "command-argument": ("argv", "arg[", "command", "parameter", "param"),
        "filesystem-derived": ("path", "filename", "folder", "directory"),
    }
    return [name for name, words in groups.items() if any(word in text for word in words)]


def table(rows: list[dict[str, object]]) -> str:
    if not rows:
        return "_None found._"
    result = ["| Path | Line | Source |", "|---|---:|---|"]
    for row in rows:
        source = str(row["text"]).replace("|", "\\|").replace("`", "\\`")
        result.append(f"| `{row['path']}` | {row['line']} | `{source}` |")
    return "\n".join(result)


def main() -> None:
    sha = run("git", "rev-parse", "HEAD").stdout.strip()
    tracked_count = len(run("git", "ls-files").stdout.splitlines())

    fs_refs = grep(r"FS\.mkdir(_p)?[[:space:]]*\(")
    definitions = [row for row in fs_refs if re.search(r"function\s+FS\.mkdir(_p)?", str(row["text"]))]
    calls = [row for row in fs_refs if row not in definitions]
    for row in calls:
        ctx = context(str(row["path"]), int(row["line"]))
        row["context"] = ctx
        row["lexical_signals"] = signals(ctx)
        row["manual_provenance_required"] = True

    shell = grep(r"os\.execute[[:space:]]*\(")
    native = grep(r"std::filesystem|filesystem::|create_director(y|ies)|createDirectory|createDirectories|lfs\.mkdir")
    mkdir_mentions = grep(r"mkdir(_p)?")
    test_signals = grep(r"Run Lua Tests|lua tests|test_.*\.lua|busted|luaunit|dofile\(|loadfile\(")

    payload = {
        "schema": "canary-cs006-fs-mkdir-audit-v1",
        "repository": "blakinio/canary",
        "commit": sha,
        "tracked_files": tracked_count,
        "definitions": definitions,
        "calls": calls,
        "os_execute": shell,
        "native_or_binding_candidates": native,
        "mkdir_mentions": mkdir_mentions,
        "lua_test_harness_signals": test_signals,
        "limitations": [
            "Lexical signals are not reachability or exploitability proof.",
            "Dynamic aliases may require manual tracing.",
            "The temporary runner and generated reports are excluded from matching.",
        ],
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# CS-006 FS.mkdir security audit",
        "",
        f"- Repository: `blakinio/canary`",
        f"- Audited commit: `{sha}`",
        f"- Tracked files: {tracked_count}",
        f"- Definitions: {len(definitions)}",
        f"- Non-definition calls: {len(calls)}",
        f"- Lua `os.execute` references: {len(shell)}",
        f"- Native/binding candidates: {len(native)}",
        "",
        "## Method",
        "",
        "Deterministic `git grep` inventory over all tracked text files at the exact branch commit. Lexical input labels are hints only; each call requires manual provenance tracing.",
        "",
        "## Definitions",
        "",
        table(definitions),
        "",
        "## Call sites",
        "",
        table(calls),
        "",
    ]
    for row in calls:
        labels = ", ".join(row["lexical_signals"]) or "none"
        lines.extend([
            f"### `{row['path']}:{row['line']}`",
            "",
            f"Lexical signals: **{labels}**; manual provenance required.",
            "",
            "```text",
            *row["context"],
            "```",
            "",
        ])
    lines.extend([
        "## Lua shell execution",
        "",
        table(shell),
        "",
        "## Native filesystem or binding candidates",
        "",
        table(native),
        "",
        "## Broader mkdir mentions",
        "",
        table(mkdir_mentions),
        "",
        "## Lua test harness signals",
        "",
        table(test_signals),
        "",
        "## Manual conclusions required",
        "",
        "- Trace each call argument to a fixed literal, configuration, environment, database, player/network or command source.",
        "- Verify whether an existing shell-free native binding can preserve maintained-platform behavior.",
        "- Select a regression that proves no unintended marker command executes.",
        "- Do not copy CrystalServer's denylist-plus-shell construction as the final design.",
    ])
    OUT_MD.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
