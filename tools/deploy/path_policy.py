"""Path safety for the atomic content deployment engine.

Every path this engine touches - release sources, release directories, the
active/previous symlinks - must resolve to somewhere inside a single
configured deployment root. This is deliberately a different, narrower
policy than ``tools/ai-agent/lib/path_policy.py`` (which reasons about writes
relative to the *repository*, e.g. forbidding writes into ``data/``): this
module has no concept of the repository at all, only of a deployment root
supplied by the caller.

The check is a single mechanism that rejects both ``..`` traversal and
symlink escape at once: ``Path.resolve()`` collapses ``..`` components *and*
follows symlinks (including symlinks in the middle of the path), so after
resolving, a path is safe if and only if it is still inside the resolved
root.
"""

from __future__ import annotations

from pathlib import Path


class PathEscapesRootError(ValueError):
    """Raised when a candidate path would resolve to somewhere outside the deployment root."""


def resolve_within_root(candidate: str | Path, root: str | Path) -> Path:
    """Resolve ``candidate`` (relative or absolute) and confirm it stays within ``root``.

    ``root`` must already exist - the deployment root is a provisioned,
    configured directory, not something this engine creates on the fly.
    Raises ``PathEscapesRootError`` if the resolved path is not inside root,
    whether that's via ``..`` segments, an absolute path pointing elsewhere,
    or a symlink (anywhere along the path, including the candidate itself)
    that leads outside.
    """
    root_resolved = Path(root).resolve(strict=True)
    candidate_path = Path(candidate)
    unresolved = candidate_path if candidate_path.is_absolute() else (root_resolved / candidate_path)
    resolved = unresolved.resolve(strict=False)

    try:
        resolved.relative_to(root_resolved)
    except ValueError as exc:
        raise PathEscapesRootError(f"path escapes deployment root: {candidate!s} -> {resolved.as_posix()} (root: {root_resolved.as_posix()})") from exc

    return resolved


def require_within_root(candidate: str | Path, root: str | Path) -> Path:
    """Same as :func:`resolve_within_root`, named for call sites that only care about the guard."""
    return resolve_within_root(candidate, root)
