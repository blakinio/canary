---
task_id: CAN-20260712-otbm-hd-batch-ai-backend
coordination_id: ""
status: validating
agent: "GPT-5.6 Thinking"
branch: feat/otbm-hd-batch-ai-backend
base_branch: main
created: 2026-07-12T18:05:00+02:00
updated: 2026-07-12T19:06:00+02:00
last_verified_commit: "3eeda906f6943e830e968c78973a8d3f609da822"
risk: medium
related_issue: ""
related_pr: "#161"
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
  - "canary-otbm-hd-batch-input-v1"
  - "batch external AI command placeholders"
cross_repo_tasks: []
---

# Goal

Add a deterministic one-process batch AI backend for the merged OTBM HD sprite pipeline so a model is loaded once for an entire region instead of once per sprite, while retaining source hash, alpha, geometry, and fallback validation.

# Acceptance criteria

- [x] Stage all valid exported sprites with transparent padding and a machine-readable batch input manifest.
- [x] Invoke one external command with `shell=False` for the complete batch.
- [x] Normalize each returned sprite independently, restore source alpha, and emit a manifest compatible with the existing validator and renderer.
- [x] Reject missing, malformed, wrong-sized, symlinked, escaped, or stale outputs without accepting unrelated files.
- [x] Provide an optional TibiaSR 2x reference backend without committing model weights or client assets.
- [x] Run focused unit tests, bytecode compilation, and a local Cobra Bastion AI smoke outside Git.
- [x] Module catalogue, documentation, changelog, and task record are current.
- [x] Cross-repository impact is none; OTClient integration remains separate.
- [ ] Current-head GitHub checks pass, review state is clear, and autonomous merge gate is satisfied.

# Confirmed context

- `main` at task start was `95244309453e980ac0377379f8ba5605ca3aba6b`; current main continued advancing in unrelated instance work.
- PR #154 merged the per-sprite external backend and compatible override manifest format.
- The per-sprite backend starts one process per sprite, which is impractical for models whose weights take meaningful time to load.
- Open PRs #159, #157, #156, #155, and #136 were inspected at task start; none owned `tools/ai-agent/otbm_hd*` or the planned documentation paths.
- No OTBM, client package, sprite sheet, model weight, or generated preview is committed.

# Existing work to reuse

| Module/task/PR | Reuse | Evidence/path | Why it fits |
|---|---|---|---|
| OTBM HD sprite pipeline / #154 | export format, PNG functions, padding/crop/alpha normalization, validator-compatible manifest | `tools/ai-agent/otbm_hd.py` | Keeps one canonical validation and renderer contract. |

# Ownership and overlap check

- Open PRs inspected: #159, #157, #156, #155, #136; GitHub state remains authoritative.
- Active tasks inspected: `docs/agents/ACTIVE_WORK.md`.
- Overlaps: none found in owned implementation paths.
- Resolution: dedicated branch and narrow new files; shared indexes were refreshed without editing runtime/datapack paths.

# Current state

Implementation, focused tests, documentation, and the factual Cobra AI batch smoke are complete. PR #161 remains draft while GitHub checks and the final changed-file review are pending.

# Implemented behavior

- `otbm_hd_batch.py` stages hash-verified source PNGs and writes `canary-otbm-hd-batch-input-v1`.
- Required placeholders are `{input_dir}`, `{output_dir}`, and `{manifest}`; optional placeholders are `{scale}` and `{work_dir}`.
- One external process runs with `shell=False`; the plaintext command is not persisted, only its template SHA-256.
- Every returned sprite is checked independently for regular-file confinement, PNG validity, dimensions, crop geometry, source alpha, and hashes.
- Partial output remains reviewable: valid sprites are accepted and invalid/missing sprites are rejected for original-sprite fallback.
- Output-root overwrite is opt-in and refuses to remove unrelated files.
- The optional TibiaSR adapter imports PyTorch/NumPy/Pillow lazily, loads one `tibia-sr2x-v1` checkpoint with `weights_only=True`, and writes the staged batch without committing weights.

# Work log

## 2026-07-12T18:05:00+02:00

- Changed: created branch and task ownership record.
- Learned: the merged per-sprite backend preserves the required manifest and validation contracts and can be extended without changing OTBM or renderer behavior.
- Failed/blocked: none.
- Result: early draft PR prepared.

## 2026-07-12T19:06:00+02:00

- Changed: implemented the batch orchestrator, CLI, optional TibiaSR adapter, nine focused tests, documentation, catalogue, and changelog entries.
- Learned: the exact Cobra export can be processed with one model invocation while retaining compatibility with the merged validator and factual renderer.
- Failed/blocked: the first TibiaSR smoke exposed checkpoint module-name mismatch in the reference adapter; architecture names were corrected to the checkpoint contract and the full rerun succeeded. Official NCNN/Vulkan remained unavailable in this environment.
- Result: 287/287 Cobra sprites accepted and validator-usable; factual map render completed with no missing appearances, sprites, or duplicate tiles.

# Decisions

| Decision | Reason/evidence | ADR |
|---|---|---|
| Add a separate batch orchestrator that emits the existing override format | Avoids destabilizing the merged core and lets Real-ESRGAN, chaiNNer, or custom models load once. | none |
| Require a fresh output root or explicit constrained overwrite | Prevents stale model outputs from being accepted. | none |
| Keep model weights and generated PNGs outside Git | Repository safety rules and licensing/size concerns. | none |
| Describe TibiaSR as experimental self-supervised enhancement | The checkpoint has no true 64x64 ground truth and must not be represented as authentic recovered detail. | none |

# Files and interfaces

| Path/interface/config/schema | Purpose | Status |
|---|---|---|
| `tools/ai-agent/otbm_hd_batch.py` | batch staging, one-process execution, normalization, compatible manifest | implemented |
| `tools/ai-agent/otbm_hd_batch_tool.py` | CLI | implemented |
| `tools/ai-agent/examples/otbm_hd_tibiasr2x_backend.py` | optional one-load PyTorch reference backend | implemented |
| `tools/ai-agent/test_otbm_hd_batch.py` | focused regression tests | implemented |
| `docs/ai-agent/OTBM_HD_BATCH_BACKEND.md` | command contract, safety, smoke evidence | implemented |
| `canary-otbm-hd-batch-input-v1` | staged model input manifest | implemented |

# Validation and CI

| Commit | Command/check/workflow | Result | Evidence/notes |
|---|---|---|---|
| local branch files | `PYTHONPATH=/mnt/data/hd_batch_impl/stubs:/mnt/data/hd_batch_impl python -m unittest -v test_otbm_hd.py test_otbm_hd_batch.py` | passed | 20 tests in 6.202s; 11 merged-core and 9 new batch tests. |
| local branch files | `python -m py_compile otbm_hd_batch.py otbm_hd_batch_tool.py examples/otbm_hd_tibiasr2x_backend.py test_otbm_hd_batch.py` | passed | no syntax errors. |
| local artifacts | Cobra Bastion TibiaSR batch, existing validator, factual render | passed | one process; 287 staged/accepted; validator validAccepted 287; 1,681 tiles; 2,627 sprite uses; 0 missing; output 3,136x3,136. |
| current PR head | GitHub required checks | pending | inspect workflows/logs before readiness. |

# Cobra Bastion evidence

```text
map SHA-256: a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2
bounds: 33377,32631,7 -> 33417,32671,7
batch process invocations: 1
unique sprites staged: 287
accepted: 287
rejected: 0
validator validAccepted: 287
map tiles: 1,681
rendered sprite uses: 2,627
missing appearances: 0
missing sprites: 0
duplicate tiles: 0
output: 3,136 x 3,136
mean absolute RGB delta from nearest 2x: 3.967662060838366
p95 absolute RGB delta from nearest 2x: 17.0
```

# Failed approaches and dead ends

- Official NCNN/Vulkan inference was unsuitable in the current execution environment because the available wrapper terminated with a floating-point exception; it remains an external batch option on supported hosts.
- The first local TibiaSR adapter used descriptive module member names that did not match the existing checkpoint keys. The adapter now preserves the checkpoint's `act`, `c1`, `c2`, and `a` names and loads successfully with `weights_only=True`.

# Risks and compatibility

- Runtime: external model process may fail or time out; each output remains rejected unless normalized and validated.
- Data/migration: none.
- Security: commands run without a shell; source/output paths are confined; command templates and model paths must not contain secrets.
- Backward compatibility: existing per-sprite backend and override manifests remain unchanged.
- Cross-repo rollout: none for renderer artifacts; client/CWM integration is separate.
- Rollback: revert the PR; no map, client asset, model weight, or production state changes.

# Remaining work

1. Review the current PR diff/changed-file list and current-base mergeability.
2. Observe GitHub workflows, fix any actual failures, then archive this task, mark ready, and squash-merge.

# Handoff

## Start here

Read this task, PR #161, and `docs/ai-agent/OTBM_HD_BATCH_BACKEND.md`; then inspect current-head checks and changed files.

## Do not repeat

Do not add another override manifest format, commit model weights/generated sprites, or describe the self-supervised result as authentic HD source detail.

## Required reads

- `AGENTS.md`
- `docs/agents/ACTIVE_WORK.md`
- `docs/agents/MODULE_CATALOG.md`
- `docs/ai-agent/OTBM_HD_PIPELINE.md`
- `docs/ai-agent/OTBM_HD_BATCH_BACKEND.md`
- `tools/ai-agent/otbm_hd.py`

## Open questions

- Whether a future client pack should use CWM or modern protobuf asset overrides remains outside this task.

# Completion

- Final status: validating
- PR: #161
- Merge commit:
- Catalogue updated: yes
- Changelog updated: yes
- Archived at:
