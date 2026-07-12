---
task_id: CAN-20260712-otbm-hd-batch-ai-backend
coordination_id: ""
status: completed
agent: "GPT-5.6 Thinking"
branch: feat/otbm-hd-batch-ai-backend
base_branch: main
created: 2026-07-12T18:05:00+02:00
updated: 2026-07-12T19:18:00+02:00
last_verified_commit: "52618c2e4fc23ece56b6912ff754d1c6d321bc3d"
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
- [x] Current-head GitHub checks passed, review state was clear, and the autonomous merge gate was satisfied.

# Confirmed context

- PR #154 supplied the canonical export, normalization, validator, and renderer override contracts.
- PR #161 merged the one-process batch extension as squash commit `52618c2e4fc23ece56b6912ff754d1c6d321bc3d`.
- No OTBM, client package, sprite sheet, CWM, model weight, generated preview, active datapack, production configuration, or secret was committed.
- OTClient integration remains outside this task.

# Implemented behavior

- `otbm_hd_batch.py` stages hash-verified source PNGs and writes `canary-otbm-hd-batch-input-v1`.
- Required placeholders are `{input_dir}`, `{output_dir}`, and `{manifest}`; optional placeholders are `{scale}` and `{work_dir}`.
- One external process runs with `shell=False`; the plaintext command is not persisted, only its template SHA-256.
- Each output is validated independently for path confinement, regular-file status, PNG integrity, dimensions, crop geometry, source alpha, and hashes.
- Partial output remains reviewable: accepted sprites are used and rejected sprites fall back to originals.
- Output-root overwrite is opt-in and refuses to remove unrelated files.
- The optional TibiaSR adapter imports PyTorch/NumPy/Pillow lazily and loads `tibia-sr2x-v1` checkpoints with `weights_only=True`.

# Validation

## Local focused tests

```text
PYTHONPATH=/mnt/data/hd_batch_impl/stubs:/mnt/data/hd_batch_impl \
  python -m unittest -v \
  /mnt/data/hd_batch_impl/test_otbm_hd.py \
  /mnt/data/hd_batch_impl/test_otbm_hd_batch.py

Ran 20 tests in 6.202s
OK
```

```text
python -m py_compile \
  otbm_hd_batch.py \
  otbm_hd_batch_tool.py \
  examples/otbm_hd_tibiasr2x_backend.py \
  test_otbm_hd_batch.py

PASS
```

## Cobra Bastion factual AI smoke

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

The checkpoint was experimental and self-supervised. It demonstrated real AI processing and batch integration while preserving factual map layout and sprite silhouettes; it was not represented as recovered authentic 64x64 source detail.

## GitHub checks on merged head

Validated PR head: `3f98b642b7c8b7c3760f5c2a9c1260b1b7253132`.

- AI Agent Tools run `29201380863`: success.
- OTBM Map Tools run `29201380903`: success.
- CI run `29201380978`: success; build-scope detection passed and unaffected runtime jobs were skipped.
- Review threads: none.
- Mergeability before squash merge: true.

# Decisions

| Decision | Reason/evidence |
|---|---|
| Emit the existing override manifest rather than define another format | Reuses one canonical validator and renderer contract. |
| Require a fresh output root or constrained explicit overwrite | Prevents stale model outputs from being accepted. |
| Keep model weights and generated PNGs outside Git | Repository safety, licensing, provenance, and size constraints. |
| Describe TibiaSR as experimental self-supervised enhancement | No true 64x64 ground truth exists for the checkpoint. |

# Failed approaches and dead ends

- The available NCNN/Vulkan wrapper terminated with a floating-point exception in the execution environment; it remains usable as an external batch option on supported hosts.
- The first local TibiaSR adapter used module names that did not match the checkpoint keys. Matching `act`, `c1`, `c2`, and `a` fixed checkpoint loading; the complete 287-sprite rerun then passed.

# Risks and compatibility

- Runtime: failed or timed-out model processes produce rejected entries, never silently accepted output.
- Data/migration: none.
- Security: no shell, confined source/output paths, bounded captured process output, no command plaintext in manifests.
- Backward compatibility: existing per-sprite backend and override format remain unchanged.
- Cross-repository rollout: none; OTClient/CWM/protobuf asset integration is separate.
- Rollback: revert merge commit `52618c2e4fc23ece56b6912ff754d1c6d321bc3d`.

# Completion

- Final status: completed and merged
- PR: #161
- Merge commit: `52618c2e4fc23ece56b6912ff754d1c6d321bc3d`
- Catalogue updated: yes
- Changelog updated: yes
- Archived at: `docs/agents/tasks/archive/CAN-20260712-otbm-hd-batch-ai-backend.md`
