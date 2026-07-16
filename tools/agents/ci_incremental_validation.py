#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fnmatch
import json
import os
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping, Sequence

FINAL_GATE_LABEL = "ci:final-gate"

# These profiles are intentionally conservative. A path may be broader than the
# workflow's normal trigger surface: once a workflow has run for a PR, a later
# synchronize event may contain a different kind of change. Reuse is allowed
# only when the *newest single-commit delta* is proven irrelevant to that
# workflow and the immediate parent has a successful same-workflow PR run.
PROFILE_PATTERNS: Mapping[str, tuple[str, ...]] = {
    "ci": (
        "src/**",
        "tests/**",
        "data/**",
        "data-canary/**",
        "data-otservbr-global/**",
        "cmake/**",
        "docker/**",
        "docs/lua-api/**",
        "docs/systems/**",
        "tools/**",
        "vcproj/**",
        "vcpkg.json",
        "CMakeLists.txt",
        "CMakePresets.json",
        ".github/scripts/**",
        ".github/workflows/**",
    ),
    "universal-e2e": (
        "src/**",
        "data/**",
        "data-canary/**",
        "data-otservbr-global/**",
        "cmake/**",
        "docker/data/01-test_account.sql",
        "docker/data/02-test_account_players.sql",
        "schema.sql",
        "vcpkg.json",
        "CMakeLists.txt",
        "CMakePresets.json",
        ".github/scripts/**",
        ".github/workflows/universal-agent-e2e.yml",
        ".github/workflows/reusable-build-linux.yml",
        "tools/agents/ci_incremental_validation.py",
        "tools/e2e/run_agent_e2e.py",
        "tools/e2e/run_physical_e2e.sh",
        "tools/e2e/client/**",
        "tests/e2e/**",
    ),
    "universal-load": (
        "src/**",
        "data/**",
        "data-canary/**",
        "cmake/**",
        "docker/data/01-test_account.sql",
        "docker/data/02-test_account_players.sql",
        "schema.sql",
        "vcpkg.json",
        "CMakeLists.txt",
        "CMakePresets.json",
        ".github/scripts/**",
        ".github/workflows/universal-agent-load.yml",
        ".github/workflows/reusable-build-linux.yml",
        "tools/agents/ci_incremental_validation.py",
        "tools/e2e/run_agent_load.py",
        "tools/e2e/run_agent_load_runtime.py",
        "tests/e2e/load/**",
        "tests/e2e/test_load_runner.py",
    ),
}

# Load-only tests must not make the physical-client workflow relevant. They are
# excluded after the conservative tests/e2e/** match above.
PROFILE_EXCLUDES: Mapping[str, tuple[str, ...]] = {
    "universal-e2e": (
        "tests/e2e/load/**",
        "tests/e2e/test_load_runner.py",
    ),
}


@dataclass(frozen=True)
class Decision:
    reuse_parent: bool
    run_heavy: bool
    reason: str
    parent_sha: str = ""
    changed_paths: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, object]:
        return {
            "reuse_parent": self.reuse_parent,
            "run_heavy": self.run_heavy,
            "reason": self.reason,
            "parent_sha": self.parent_sha,
            "changed_paths": list(self.changed_paths),
        }


def normalize_path(path: str) -> str:
    normalized = path.replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized.lstrip("/")


def _matches(path: str, pattern: str) -> bool:
    return fnmatch.fnmatchcase(normalize_path(path), pattern)


def path_impacts_profile(path: str, profile: str) -> bool:
    if profile not in PROFILE_PATTERNS:
        raise ValueError(f"unknown profile: {profile}")

    normalized = normalize_path(path)
    excludes = PROFILE_EXCLUDES.get(profile, ())
    if any(_matches(normalized, pattern) for pattern in excludes):
        return False
    return any(_matches(normalized, pattern) for pattern in PROFILE_PATTERNS[profile])


def impacting_paths(paths: Iterable[str], profile: str) -> tuple[str, ...]:
    return tuple(
        path
        for path in (normalize_path(value) for value in paths if value.strip())
        if path_impacts_profile(path, profile)
    )


def latest_same_workflow_run(
    runs: Sequence[Mapping[str, object]], workflow_name: str
) -> Mapping[str, object] | None:
    matching = [run for run in runs if str(run.get("name", "")) == workflow_name]
    if not matching:
        return None

    def sort_key(run: Mapping[str, object]) -> tuple[int, str, int]:
        run_attempt = int(run.get("run_attempt") or 0)
        created_at = str(run.get("created_at") or "")
        run_number = int(run.get("run_number") or 0)
        return (run_number, created_at, run_attempt)

    return max(matching, key=sort_key)


def parent_has_successful_workflow_run(
    runs: Sequence[Mapping[str, object]], workflow_name: str
) -> tuple[bool, str]:
    latest = latest_same_workflow_run(runs, workflow_name)
    if latest is None:
        return False, "no same-workflow pull-request run found for immediate parent"

    status = str(latest.get("status") or "")
    conclusion = str(latest.get("conclusion") or "")
    if status == "completed" and conclusion == "success":
        return True, "immediate parent latest same-workflow run completed successfully"
    return (
        False,
        f"immediate parent latest same-workflow run is {status or 'unknown'}/{conclusion or 'none'}",
    )


def decide_reuse(
    *,
    profile: str,
    workflow_name: str,
    event_name: str,
    event_action: str,
    force_full: bool,
    changed_paths: Sequence[str],
    parent_sha: str,
    parent_runs: Sequence[Mapping[str, object]],
) -> Decision:
    normalized_paths = tuple(normalize_path(path) for path in changed_paths if path.strip())

    if force_full:
        return Decision(False, True, "final gate forces full validation", parent_sha, normalized_paths)
    if event_name != "pull_request" or event_action != "synchronize":
        return Decision(
            False,
            True,
            "incremental reuse is limited to pull_request synchronize events",
            parent_sha,
            normalized_paths,
        )
    if not parent_sha:
        return Decision(False, True, "immediate parent SHA is unavailable", "", normalized_paths)
    if not normalized_paths:
        return Decision(
            False,
            True,
            "single-commit changed-path evidence is empty",
            parent_sha,
            normalized_paths,
        )

    impacting = impacting_paths(normalized_paths, profile)
    if impacting:
        return Decision(
            False,
            True,
            "single-commit delta affects validation profile: " + ", ".join(impacting),
            parent_sha,
            normalized_paths,
        )

    parent_ok, parent_reason = parent_has_successful_workflow_run(parent_runs, workflow_name)
    if not parent_ok:
        return Decision(False, True, parent_reason, parent_sha, normalized_paths)

    return Decision(
        True,
        False,
        "non-impacting single-commit delta with successful immediate-parent workflow evidence",
        parent_sha,
        normalized_paths,
    )


def _git_lines(*args: str) -> list[str]:
    completed = subprocess.run(
        ["git", *args],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return [line.strip() for line in completed.stdout.splitlines() if line.strip()]


def immediate_parent_and_paths() -> tuple[str, tuple[str, ...]]:
    parent_lines = _git_lines("rev-parse", "HEAD^")
    if len(parent_lines) != 1:
        raise RuntimeError("unable to resolve exactly one immediate parent")
    parent_sha = parent_lines[0]
    changed = tuple(_git_lines("diff", "--name-only", parent_sha, "HEAD"))
    return parent_sha, changed


def fetch_parent_workflow_runs(
    *, repository: str, parent_sha: str, token: str, api_url: str = "https://api.github.com"
) -> list[Mapping[str, object]]:
    query = urllib.parse.urlencode(
        {"head_sha": parent_sha, "event": "pull_request", "per_page": "100"}
    )
    url = f"{api_url.rstrip('/')}/repos/{repository}/actions/runs?{query}"
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "canary-ci-incremental-validation",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=20) as response:
        payload = json.load(response)

    runs = payload.get("workflow_runs", [])
    if not isinstance(runs, list):
        raise ValueError("GitHub Actions response workflow_runs must be a list")
    return [run for run in runs if isinstance(run, Mapping)]


def _write_github_output(path: str, decision: Decision) -> None:
    if not path:
        return
    with Path(path).open("a", encoding="utf-8") as handle:
        handle.write(f"reuse_parent={'true' if decision.reuse_parent else 'false'}\n")
        handle.write(f"run_heavy={'true' if decision.run_heavy else 'false'}\n")
        handle.write(f"parent_sha={decision.parent_sha}\n")
        handle.write("reason<<CI_INCREMENTAL_REASON\n")
        handle.write(decision.reason + "\n")
        handle.write("CI_INCREMENTAL_REASON\n")


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fail-closed incremental heavy-validation reuse decision"
    )
    parser.add_argument("--profile", choices=sorted(PROFILE_PATTERNS), required=True)
    parser.add_argument("--workflow-name", required=True)
    parser.add_argument("--repository", default=os.environ.get("GITHUB_REPOSITORY", ""))
    parser.add_argument("--token", default=os.environ.get("GITHUB_TOKEN", ""))
    parser.add_argument("--event-name", default=os.environ.get("GITHUB_EVENT_NAME", ""))
    parser.add_argument("--event-action", default="")
    parser.add_argument("--force-full", action="store_true")
    parser.add_argument("--github-output", default=os.environ.get("GITHUB_OUTPUT", ""))
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)

    try:
        parent_sha, changed_paths = immediate_parent_and_paths()
    except (OSError, RuntimeError, subprocess.CalledProcessError) as exc:
        decision = Decision(False, True, f"fail closed: cannot resolve single-commit delta: {exc}")
    else:
        if args.force_full or args.event_name != "pull_request" or args.event_action != "synchronize":
            parent_runs: list[Mapping[str, object]] = []
        else:
            try:
                parent_runs = fetch_parent_workflow_runs(
                    repository=args.repository,
                    parent_sha=parent_sha,
                    token=args.token,
                )
            except (OSError, ValueError, urllib.error.URLError) as exc:
                decision = Decision(
                    False,
                    True,
                    f"fail closed: cannot read immediate-parent workflow evidence: {exc}",
                    parent_sha,
                    changed_paths,
                )
                print(json.dumps(decision.as_dict(), sort_keys=True))
                _write_github_output(args.github_output, decision)
                return 0

        decision = decide_reuse(
            profile=args.profile,
            workflow_name=args.workflow_name,
            event_name=args.event_name,
            event_action=args.event_action,
            force_full=args.force_full,
            changed_paths=changed_paths,
            parent_sha=parent_sha,
            parent_runs=parent_runs,
        )

    print(json.dumps(decision.as_dict(), sort_keys=True))
    _write_github_output(args.github_output, decision)
    return 0


if __name__ == "__main__":
    sys.exit(main())
