#!/usr/bin/env python3
"""Select one changed Universal Agent E2E scenario for same-repository PRs.

This module chooses a suite/scenario pair only. Existing run_agent_e2e.py remains
responsible for scenario validation, resolution, and execution.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Iterable, Sequence
from urllib.parse import quote, urlsplit

CANONICAL_SUITE = "login"
CANONICAL_SCENARIO = "relog"
SCENARIO_ROOT = PurePosixPath("tests/e2e/scenarios")
_SAFE_COMPONENT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
_REPOSITORY = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
_SHA40 = re.compile(r"^[0-9a-f]{40}$")


class SelectionError(ValueError):
    """Raised when exact PR evidence or a uniquely selected manifest is invalid."""


@dataclass(frozen=True)
class ScenarioSelection:
    suite: str
    scenario: str
    reason: str
    manifest: str = ""

    def as_dict(self) -> dict[str, str]:
        return {
            "suite": self.suite,
            "scenario": self.scenario,
            "reason": self.reason,
            "manifest": self.manifest,
        }


def _canonical(reason: str) -> ScenarioSelection:
    return ScenarioSelection(CANONICAL_SUITE, CANONICAL_SCENARIO, reason)


def _validate_exact_shas(base_sha: str, head_sha: str) -> None:
    if not _SHA40.fullmatch(base_sha) or not _SHA40.fullmatch(head_sha):
        raise SelectionError("pull-request base/head SHAs must be exact lowercase 40-character SHAs")


def _scenario_candidate(raw_path: str, repo_root: Path) -> PurePosixPath | None:
    path = PurePosixPath(raw_path)
    if path.is_absolute() or ".." in path.parts:
        return None

    root_parts = SCENARIO_ROOT.parts
    if len(path.parts) != len(root_parts) + 2 or path.parts[: len(root_parts)] != root_parts:
        return None

    suite, filename = path.parts[-2], path.parts[-1]
    if not _SAFE_COMPONENT.fullmatch(suite) or not filename.endswith(".json"):
        return None
    if not (repo_root / Path(*path.parts)).is_file():
        return None
    return path


def _load_manifest_id(repo_root: Path, manifest: PurePosixPath) -> str:
    manifest_path = repo_root / Path(*manifest.parts)
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SelectionError(f"cannot parse selected scenario manifest {manifest}: {exc}") from exc

    scenario_id = payload.get("id") if isinstance(payload, dict) else None
    if not isinstance(scenario_id, str) or not _SAFE_COMPONENT.fullmatch(scenario_id):
        raise SelectionError(
            f"selected scenario manifest {manifest} must contain a safe non-empty string id"
        )
    return scenario_id


def select_from_changed_paths(
    *,
    event_name: str,
    current_repository: str,
    pr_head_repository: str,
    requested_suite: str,
    requested_scenario: str,
    changed_paths: Iterable[str],
    repo_root: Path,
) -> ScenarioSelection:
    """Resolve an E2E selection without executing the scenario."""

    if event_name != "pull_request":
        return ScenarioSelection(
            requested_suite or CANONICAL_SUITE,
            requested_scenario or CANONICAL_SCENARIO,
            "explicit-or-canonical-non-pr",
        )

    if not current_repository or pr_head_repository != current_repository:
        return _canonical("canonical-fallback-non-same-repository-pr")

    candidates = sorted(
        {
            candidate
            for raw_path in changed_paths
            if (candidate := _scenario_candidate(raw_path, repo_root)) is not None
        },
        key=str,
    )
    if len(candidates) != 1:
        return _canonical(f"canonical-fallback-existing-scenario-count-{len(candidates)}")

    manifest = candidates[0]
    scenario_id = _load_manifest_id(repo_root, manifest)
    return ScenarioSelection(
        suite=manifest.parts[-2],
        scenario=scenario_id,
        reason="single-changed-scenario-manifest",
        manifest=str(manifest),
    )


def git_changed_paths(repo_root: Path, base_sha: str, head_sha: str) -> list[str]:
    """Return destination paths changed between exact pull-request SHAs."""

    _validate_exact_shas(base_sha, head_sha)
    try:
        completed = subprocess.run(
            [
                "git",
                "-C",
                str(repo_root),
                "diff",
                "--name-status",
                "--find-renames",
                f"{base_sha}...{head_sha}",
            ],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        detail = getattr(exc, "stderr", "") or str(exc)
        raise SelectionError(f"cannot inspect exact PR delta with git: {detail.strip()}") from exc

    paths: list[str] = []
    for line in completed.stdout.splitlines():
        if not line.strip():
            continue
        fields = line.split("\t")
        status = fields[0]
        if status.startswith(("R", "C")):
            if len(fields) != 3:
                raise SelectionError(f"unexpected git rename/copy record: {line}")
            paths.append(fields[2])
        elif len(fields) == 2:
            paths.append(fields[1])
        else:
            raise SelectionError(f"unexpected git diff record: {line}")
    return paths


def github_compare_changed_paths(
    repository: str,
    base_sha: str,
    head_sha: str,
    *,
    api_url: str = "https://api.github.com",
    token: str = "",
) -> list[str]:
    """Read exact changed filenames from GitHub's immutable compare endpoint.

    GitHub compare responses expose at most 300 file entries. Exactly 300 is
    therefore treated as incomplete evidence and fails closed.
    """

    _validate_exact_shas(base_sha, head_sha)
    if not _REPOSITORY.fullmatch(repository):
        raise SelectionError("repository must be an exact owner/name pair")

    parsed = urlsplit(api_url)
    if parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password:
        raise SelectionError("GitHub API URL must be an absolute HTTPS URL without credentials")
    if parsed.query or parsed.fragment:
        raise SelectionError("GitHub API URL must not contain query or fragment components")

    owner, name = repository.split("/", 1)
    endpoint = (
        f"{api_url.rstrip('/')}/repos/{quote(owner, safe='')}/{quote(name, safe='')}"
        f"/compare/{base_sha}...{head_sha}"
    )
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "canary-universal-agent-e2e-pr-scenario-selector",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = urllib.request.Request(endpoint, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (OSError, urllib.error.URLError, json.JSONDecodeError) as exc:
        raise SelectionError(f"cannot inspect exact PR delta with GitHub compare API: {exc}") from exc

    files = payload.get("files") if isinstance(payload, dict) else None
    if not isinstance(files, list):
        raise SelectionError("GitHub compare response does not contain a files array")
    if len(files) >= 300:
        raise SelectionError("GitHub compare file evidence may be truncated at 300 entries")

    paths: list[str] = []
    for entry in files:
        filename = entry.get("filename") if isinstance(entry, dict) else None
        if not isinstance(filename, str) or not filename:
            raise SelectionError("GitHub compare response contains an invalid filename entry")
        paths.append(filename)
    return paths


def select_for_event(
    *,
    event_name: str,
    current_repository: str,
    pr_head_repository: str,
    requested_suite: str,
    requested_scenario: str,
    base_sha: str,
    head_sha: str,
    repo_root: Path,
    api_repository: str = "",
    api_url: str = "https://api.github.com",
    api_token: str = "",
) -> ScenarioSelection:
    changed_paths: list[str] = []
    if event_name == "pull_request" and current_repository and pr_head_repository == current_repository:
        _validate_exact_shas(base_sha, head_sha)
        try:
            changed_paths = git_changed_paths(repo_root, base_sha, head_sha)
        except SelectionError as git_error:
            if not api_repository:
                raise git_error
            changed_paths = github_compare_changed_paths(
                api_repository,
                base_sha,
                head_sha,
                api_url=api_url,
                token=api_token,
            )

    return select_from_changed_paths(
        event_name=event_name,
        current_repository=current_repository,
        pr_head_repository=pr_head_repository,
        requested_suite=requested_suite,
        requested_scenario=requested_scenario,
        changed_paths=changed_paths,
        repo_root=repo_root,
    )


def _write_github_output(path: Path, selection: ScenarioSelection) -> None:
    with path.open("a", encoding="utf-8") as handle:
        for key, value in selection.as_dict().items():
            handle.write(f"{key}={value}\n")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--event-name", required=True)
    parser.add_argument("--current-repository", default="")
    parser.add_argument("--pr-head-repository", default="")
    parser.add_argument("--requested-suite", default=CANONICAL_SUITE)
    parser.add_argument("--requested-scenario", default=CANONICAL_SCENARIO)
    parser.add_argument("--base-sha", default="")
    parser.add_argument("--head-sha", default="")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--api-repository", default="")
    parser.add_argument("--api-url", default="https://api.github.com")
    parser.add_argument("--api-token", default="")
    parser.add_argument("--github-output", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        selection = select_for_event(
            event_name=args.event_name,
            current_repository=args.current_repository,
            pr_head_repository=args.pr_head_repository,
            requested_suite=args.requested_suite,
            requested_scenario=args.requested_scenario,
            base_sha=args.base_sha,
            head_sha=args.head_sha,
            repo_root=args.repo_root.resolve(),
            api_repository=args.api_repository,
            api_url=args.api_url,
            api_token=args.api_token,
        )
    except SelectionError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.github_output:
        _write_github_output(args.github_output, selection)
    print(json.dumps(selection.as_dict(), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
