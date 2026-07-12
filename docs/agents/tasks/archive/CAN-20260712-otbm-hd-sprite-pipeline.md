---
task_id: CAN-20260712-otbm-hd-sprite-pipeline
status: completed
agent: "GPT-5.6 Thinking"
branch: feat/otbm-hd-sprite-pipeline
base_branch: main
created: 2026-07-12T16:30:00+02:00
updated: 2026-07-12T18:12:00+02:00
last_verified_commit: "03c0569753ee8e3a87472cafd282af97bf430d8b"
risk: medium
related_pr: "#154 (replaces auto-closed #147)"
depends_on:
  - "merged OTBM asset, appearance, sprite and renderer tooling"
blocks: []
owned_paths:
  - tools/ai-agent/otbm_hd.py
  - tools/ai-agent/otbm_hd_tool.py
  - tools/ai-agent/test_otbm_hd.py
  - docs/ai-agent/OTBM_HD_PIPELINE.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/CHANGELOG.md
  - docs/agents/tasks/archive/CAN-20260712-otbm-hd-sprite-pipeline.md
modules_touched:
  - OTBM HD sprite pipeline
  - OTBM renderer integration
reuses:
  - otbm_assets
  - otbm_appearances
  - otbm_binary
  - otbm_scan
  - otbm_sprites
  - otbm_renderer
cross_repo_tasks:
  - "future OTClient CWM/modern-asset integration; not changed in this task"
---

# Goal

Add a deterministic, reviewable HD-sprite pipeline around the existing OTBM renderer. The delivered slice exports only sprites used by a bounded map region, prepares padded inputs for an external AI upscaler, normalizes and validates returned PNGs, and renders the same region at 2x using accepted overrides while falling back to the original sprites.

# Delivered surface

- `export`: extracts only sprite IDs referenced by the bounded OTBM region and records item IDs, use counts, sample positions, dimensions, alpha bounds and hashes.
- `upscale`: supports deterministic nearest-neighbor reference output and an external model command using `{input}`, `{output}`, `{scale}` and `{sprite_id}` placeholders with `shell=False`.
- normalization: adds transparent padding, crops scaled padding and restores the nearest-scaled source alpha mask independently of model RGB.
- `validate`: verifies source/export/override hashes, dimensions and exact alpha geometry.
- `render`: preserves logical 32-pixel tiles while rendering at the declared pixel scale, with accepted overrides and deterministic source fallback.
- `compare`: generates a like-for-like nearest-scaled original beside the HD render.

# Safety boundaries verified

- No `.otbm`, `items.otb`, `appearances.dat`, sprite sheet, CWM, client package, active datapack or generated preview was committed.
- Generated test/output artifacts remained outside Git.
- Item IDs, appearance IDs, sprite IDs, map coordinates, stack order, displacement and elevation remain unchanged.
- External commands execute without a shell.
- Model output is not accepted unless geometry, hashes and alpha validation pass.
- OTClient/CWM/modern asset-pack integration remains a separate cross-repository task.

# Focused validation

```text
PYTHONPATH=/mnt/data/hd_impl/stubs:/mnt/data/hd_impl \
  python -m unittest -v /mnt/data/hd_impl/test_otbm_hd.py

Ran 6 tests in 1.227s
OK

python -m py_compile \
  /mnt/data/hd_impl/otbm_hd.py \
  /mnt/data/hd_impl/otbm_hd_tool.py \
  /mnt/data/hd_impl/test_otbm_hd.py

result: PASS
```

Covered PNG round trips and alpha bounds, padding/scale/crop, alpha restoration, shell-free command tokenization, external backend normalization, nearest override validation and explicit rejected-sprite fallback.

# Cobra Bastion proof of concept

```text
map SHA-256: a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2
bounds: 33377,32631,7 -> 33417,32671,7
map tiles: 1,681
sprite/item uses: 2,627
unique exported sprites: 287
missing appearances: 0
missing sprites: 0
accepted and validated overrides: 287/287
HD output: 3,136 x 3,136
used override sprites: 287
fallback sprites: 0
```

The proof used nearest-neighbor strictly as a deterministic geometry/integration baseline. It proves the extraction and HD-render path, not AI visual quality. A compatible external model is still required for a visual-quality trial.

# GitHub validation

Current reviewed head before archival: `03c0569753ee8e3a87472cafd282af97bf430d8b`.

Successful workflows:

- `OTBM Map Tools` run `29199085932`;
- `AI Agent Tools` run `29199085953`;
- `CI` run `29199085998`, including:
  - Lua Tests;
  - Fast Checks;
  - required `Build - Linux / Compile (linux-release)`.

Windows, macOS, Docker and datapack runtime jobs were correctly skipped by changed-path scope detection.

# History note

PR #147 auto-closed when its head ref was temporarily moved to current `main` during synchronization. The original head was preserved, restored and reopened as replacement PR #154. The PR is mergeable and the changed-file review contains only AI-agent Python tooling, tests and documentation.
