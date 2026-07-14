#!/usr/bin/env python3
"""Generate deterministic CS-006 FS.mkdir call-site and facility evidence."""

from __future__ import annotations

import json
import re
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[2]
REPORT_MD = ROOT / "artifacts/upstream/crystalserver/CS006_FS_MKDIR_AUDIT.md"
REPORT_JSON = ROOT / "artifacts/upstream/crystalserver/cs006_fs_mkdir_audit.json"

TEXT_SUFFIXES = {
    ".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".hxx",
    ".lua", ".py", ".sh", ".ps1", ".bat", ".cmd", ".yml", ".yaml",
    ".md", ".txt", ".json", ".xml", ".cmake", ".toml", ".ini",
}
SKIP_PREFIXES = (
    "artifacts/upstream/crystalserver/CS006_FS_MKDIR_AUDIT",
    "artifacts/upstream/crystalserver/cs006_fs_mkdir_audit",
    "tools/ai-agent/audit_fs_mkdir.py",
    ".github/workflows/audit-fs-mkdir.yml",
)


@dataclass(frozen=True)
class Match:
    path: str
    line: int
    text: str
    kind: str


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def tracked_files() -> list[Path]:
    raw = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT)
    result: list[Path] = []
    for item in raw.split(b"\0"):
        if not item:
            continue
        rel = item.decode("utf-8")
        if rel.startswith(SKIP_PREFIXES):
            continue
        path = ROOT / rel
        if path.suffix.lower() in TEXT_SUFFIXES or path.name in {"CMakeLists.txt", "Dockerfile"}:
            result.append(path)
    return sorted(result)


def read_lines(path: Path) -> list[str]:
    data = path.read_bytes()
    if b"\0" in data:
        return []
    return data.decode("utf-8", errors="replace").splitlines()


def collect(pattern: re.Pattern[str], kind: str, files: Iterable[Path]) -> list[Match]:
    matches: list[Match] = []
    for path in files:
        rel = path.relative_to(ROOT).as_posix()
        for number, line in enumerate(read_lines(path), start=1):
            if pattern.search(line):
                matches.append(Match(rel, number, line.strip(), kind))
    return matches


def classify_fs_matches(matches: list[Match]) -> tuple[list[Match], list[Match]]:
    definitions: list[Match] = []
    calls: list[Match] = []
    definition_re = re.compile(r"^\s*function\s+FS\.mkdir(?:_p)?\s*\(")
    for match in matches:
        if definition_re.search(match.text):
            definitions.append(match)
        else:
            calls.append(match)
    return definitions, calls


def nearby_context(path: str, line: int, radius: int = 4) -> list[str]:
    lines = read_lines(ROOT / path)
    start = max(1, line - radius)
    end = min(len(lines), line + radius)
    return [f"{idx}: {lines[idx - 1]}" for idx in range(start, end + 1)]


def likely_input_signals(context: list[str]) -> list[str]:
    joined = "\n".join(context).lower()
    signals = []
    terms = {
        "configuration": ("config", "getconfig", "configmanager"),
        "environment": ("getenv", "environment", "os.getenv"),
        "network/request": ("request", "packet", "protocol", "http", "socket"),
        "player/user": ("player", "account", "character", "username", "user"),
        "database": ("db.", "database", "query", "result.get"),
        "command/argument": ("argv", "arg[", "command", "param", "parameter"),
        "filesystem-derived": ("filename", "filepath", "directory", "folder", "path"),
    }
    for label, needles in terms.items():
        if any(needle in joined for needle in needles):
            signals.append(label)
    return signals


def markdown_table(matches: list[Match]) -> str:
    if not matches:
        return "_None found._\n"
    rows = ["| Path | Line | Kind | Source |", "|---|---:|---|---|"]
    for item in matches:
        source = item.text.replace("|", "\\|").replace("`", "\\`")
        rows.append(f"| `{item.path}` | {item.line} | {item.kind} | `{source}` |")
    return "\n".join(rows) + "\n"


def main() -> None:
    files = tracked_files()
    sha = git("rev-parse", "HEAD")

    fs_all = collect(re.compile(r"\bFS\.mkdir(?:_p)?\s*\("), "fs-mkdir-reference", files)
    definitions, calls = classify_fs_matches(fs_all)
    os_execute = collect(re.compile(r"\bos\.execute\s*\("), "lua-os-execute", files)
    native = collect(
        re.compile(
            r"std::filesystem|filesystem::|create_director(?:y|ies)|createDirectory|createDirectories|luaFileSystem|lfs\.mkdir",
            re.IGNORECASE,
        ),
        "native-or-binding-candidate",
        files,
    )
    mkdir_mentions = collect(
        re.compile(r"\bmkdir\b|mkdir_p", re.IGNORECASE),
        "mkdir-mention",
        [p for p in files if p.relative_to(ROOT).as_posix().startswith(("src/", "tests/", "data/", "data-otservbr-global/", ".github/"))],
    )
    lua_test_harness = collect(
        re.compile(r"lua tests|run lua tests|test_.*\.lua|busted|luaunit|dofile\(|loadfile\(", re.IGNORECASE),
        "lua-test-harness-signal",
        [p for p in files if p.relative_to(ROOT).as_posix().startswith(("tests/", "tools/", ".github/"))],
    )

    call_details = []
    for call in calls:
        context = nearby_context(call.path, call.line)
        call_details.append(
            {
                **asdict(call),
                "context": context,
                "input_signals": likely_input_signals(context),
                "manual_provenance_required": True,
            }
        )

    payload = {
        "schema": "canary-cs006-fs-mkdir-audit-v1",
        "repository": "blakinio/canary",
        "commit": sha,
        "tracked_text_files_scanned": len(files),
        "definitions": [asdict(x) for x in definitions],
        "calls": call_details,
        "os_execute": [asdict(x) for x in os_execute],
        "native_or_binding_candidates": [asdict(x) for x in native],
        "mkdir_mentions": [asdict(x) for x in mkdir_mentions],
        "lua_test_harness_signals": [asdict(x) for x in lua_test_harness],
        "limitations": [
            "Input-signal labels are lexical hints only and are not reachability proof.",
            "Manual tracing is required for every call site before severity is finalized.",
            "The report excludes its own generated files and temporary runner files.",
        ],
    }

    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    report = [
        "# CS-006 FS.mkdir security audit",
        "",
        f"- Repository: `blakinio/canary`",
        f"- Audited commit: `{sha}`",
        f"- Tracked text files scanned: {len(files)}",
        f"- Definitions: {len(definitions)}",
        f"- Non-definition `FS.mkdir`/`FS.mkdir_p` references: {len(calls)}",
        f"- Lua `os.execute` references: {len(os_execute)}",
        f"- Native/binding candidates: {len(native)}",
        "",
        "## Method",
        "",
        "The audit scans every tracked text source at the exact branch commit. It records exact file/line evidence for `FS.mkdir`, `FS.mkdir_p`, Lua shell execution, native filesystem candidates and Lua test harness signals. Lexical input labels are hints only; every call still requires manual provenance tracing.",
        "",
        "## FS definitions",
        "",
        markdown_table(definitions),
        "## FS call sites",
        "",
        markdown_table(calls),
    ]

    if call_details:
        report.extend(["## Call-site context and lexical signals", ""])
        for item in call_details:
            signals = ", ".join(item["input_signals"]) or "none"
            report.extend(
                [
                    f"### `{item['path']}:{item['line']}`",
                    "",
                    f"Lexical signals: **{signals}**. This is not proof; manual trace required.",
                    "",
                    "```text",
                    *item["context"],
                    "```",
                    "",
                ]
            )

    report.extend(
        [
            "## Lua shell execution inventory",
            "",
            markdown_table(os_execute),
            "## Native filesystem or Lua-binding candidates",
            "",
            markdown_table(native),
            "## Broader mkdir mentions",
            "",
            markdown_table(mkdir_mentions),
            "## Lua test harness signals",
            "",
            markdown_table(lua_test_harness),
            "## Required manual conclusions",
            "",
            "- Trace every call argument to its origin and classify trusted configuration, operator-controlled input, player/network input, database input or fixed literal.",
            "- Confirm whether a shell-free native binding already exists and whether it preserves Windows/Linux behavior.",
            "- Select a regression harness that can prove no unintended marker command executes.",
            "- Do not treat the CrystalServer metacharacter denylist as the final design because it still invokes a shell.",
            "",
            "## Limitations",
            "",
            "- Code search is lexical and conservative; dynamic table aliases may require separate tracing.",
            "- Input-signal labels are not reachability or exploitability proof.",
            "- Generated audit and temporary runner files are excluded to prevent self-matches.",
        ]
    )
    REPORT_MD.write_text("\n".join(report).rstrip() + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
