---
task_id: CAN-20260712-otbm-hd-batch-ai-backend
coordination_id: ""
status: active
agent: "GPT-5.6 Thinking"
branch: feat/otbm-hd-batch-ai-backend
base_branch: main
created: 2026-07-12T18:05:00+02:00
updated: 2026-07-12T18:05:00+02:00
last_verified_commit: "95244309453e980ac0377379f8ba5605ca3aba6b"
risk: medium
related_issue: ""
related_pr: ""
depends_on:
  - "merged OTBM HD sprite pipeline (#154)"
blocks: []
owned_paths:
  - tools/ai-agent/otbm_hd_batch.py
  - tools/ai-agent/otbm_hd_batch_tool.py
  - tools/ai-agent/examples/otbm_hd_tibiasr2x_backend.py
  - tools/ai-agent/test_otbm_hd_batch.py
  - docs/ai-agent/OTBM_HD_BATCH_BACKEND.md
  - docs/agents/ACTIVE_WORK.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/CHANGELOG.md
  - docs/agents/tasks/active/CAN-20260712-otbm-hd-batch-ai-backend.md
modules_touched:
  - OTBM HD sprite pipeline
reuses:
  - tools/ai-agent/otbm_hd.py
  - tools/ai-agent/otbm_hd_tool.py
public_interfaces:
  - "batch external AI backend command contract"
cross_repo_tasks: []
---

# Goal

Add a deterministic one-process batch AI backend for the merged OTBM HD sprite pipeline so a model is loaded once for an entire region instead of once per sprite, while retaining source hash, alpha, geometry, and fallback validation.

# Acceptance criteria

- [ ] Stage all valid exported sprites with transparent padding and a machine-readable batch input manifest.
- [ ] Invoke one external command with `shell=False` for the complete batch.
- [ ] Normalize each returned sprite independently, restore source alpha, and emit a manifest compatible with the existing validator and renderer.
- [ ] Reject missing, malformed, wrong-sized, symlinked, or stale outputs without accepting unrelated files.
- [ ] Provide an optional TibiaSR 2x reference backend without committing model weights or client assets.
- [ ] Run focused unit tests, bytecode compilation, and a local Cobra Bastion AI smoke outside Git.
- [ ] Module catalogue, documentation, changelog, and task record are current.
- [ ] Cross-repository impact is none; OTClient integration remains separate.
- [ ] Autonomous merge gate satisfied.

# Confirmed context

- Current `main` at task start: `95244309453e980ac0377379f8ba5605ca3aba6b`.
- PR #154 merged the per-sprite external backend and compatible override manifest format.
- The current external backend starts one process per sprite, which is impractical for models whose weights take meaningful time to load.
- Open PRs #159, #157, #156, #155, and #136 were inspected; none owns `tools/ai-agent/otbm_hd*` or the planned documentation paths.
- No OTBM, client package, sprite sheet, model weight, or generated preview may be committed.

# Existing work to reuse

| Module/task/PR | Reuse | Evidence/path | Why it fits |
|---|---|---|---|
| OTBM HD sprite pipeline / #154 | export format, PNG functions, padding/crop/alpha normalization, validator-compatible manifest | `tools/ai-agent/otbm_hd.py` | Keeps one canonical validation and renderer contract. |

# Ownership and overlap check

- Open PRs inspected: #159, #157, #156, #155, #136.
- Active tasks inspected: `docs/agents/ACTIVE_WORK.md`; GitHub open PR state treated as authoritative.
- Overlaps: none found in planned paths.
- Resolution: dedicated branch and narrow new files; shared indexes will be refreshed from current `main` before updates.

# Current state

Task claimed; implementation and local validation are in progress.

# Plan

1. Implement the batch command contract and normalization pipeline.
2. Add focused tests and optional TibiaSR reference backend.
3. Run the exact Cobra export through one model process and re-render the factual region.
4. Update docs/catalogue/changelog, inspect CI, repair failures, and squash-merge when green.

# Work log

## 2026-07-12T18:05:00+02:00

- Changed: created branch and task ownership record.
- Learned: the merged per-sprite backend preserves the required manifest and validation contracts and can be extended without changing OTBM or renderer behavior.
- Failed/blocked: none.
- Result: ready for early draft PR publication.

# Decisions

| Decision | Reason/evidence | ADR |
|---|---|---|
| Add a separate batch orchestrator that emits the existing override format | Avoids destabilizing the merged core and lets Real-ESRGAN, chaiNNer, or custom models load once. | none |
| Keep model weights and generated PNGs outside Git | Repository safety rules and licensing/size concerns. | none |

# Files and interfaces

| Path/interface/config/schema | Purpose | Status |
|---|---|---|
| `tools/ai-agent/otbm_hd_batch.py` | batch staging, execution, normalization, manifest | planned |
| `tools/ai-agent/otbm_hd_batch_tool.py` | CLI | planned |
| `tools/ai-agent/examples/otbm_hd_tibiasr2x_backend.py` | optional one-load PyTorch reference backend | planned |
| `tools/ai-agent/test_otbm_hd_batch.py` | focused regression tests | planned |
| `docs/ai-agent/OTBM_HD_BATCH_BACKEND.md` | command contract and workflow | planned |

# Validation and CI

| Commit | Command/check/workflow | Result | Evidence/notes |
|---|---|---|---|
| | focused Python tests and `py_compile` | not-run | |
| | Cobra Bastion batch AI smoke | not-run | local artifacts only |
| | GitHub required checks | not-run | |

Never write `passed` without verification.

# Failed approaches and dead ends

- Official NCNN/Vulkan inference was unsuitable in the current execution environment because the available wrapper terminated with a floating-point exception; it remains an external backend option on supported hosts.

# Risks and compatibility

- Runtime: external model process may fail or time out; each output remains rejected unless normalized and validated.
- Data/migration: none.
- Security: commands run without a shell; command templates and model paths must not contain secrets.
- Backward compatibility: existing per-sprite backend and override manifests remain unchanged.
- Cross-repo rollout: none for renderer artifacts; client/CWM integration is separate.
- Rollback: revert the PR; no map, client asset, or production state changes.

# Remaining work

1. Publish the early draft PR and implement the batch backend.

# Handoff

## Start here

Read this task and the merged `docs/ai-agent/OTBM_HD_PIPELINE.md`, then inspect current branch files and PR checks.

## Do not repeat

Do not add another override manifest format or commit model weights/generated sprites.

## Required reads

- `AGENTS.md`
- `docs/agents/ACTIVE_WORK.md`
- `docs/agents/MODULE_CATALOG.md`
- `docs/ai-agent/OTBM_HD_PIPELINE.md`
- `tools/ai-agent/otbm_hd.py`

## Open questions

- Whether a future client pack should use CWM or modern protobuf asset overrides remains outside this task.

# Completion

- Final status: active
- PR:
- Merge commit:
- Catalogue updated: pending
- Changelog updated: pending
- Archived at:
