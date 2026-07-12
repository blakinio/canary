---
task_id: CAN-20260712-otbm-hd-sprite-pipeline
status: ready-for-review
agent: "GPT-5.6 Thinking"
branch: feat/otbm-hd-sprite-pipeline
base_branch: main
created: 2026-07-12T16:30:00+02:00
updated: 2026-07-12T17:12:00+02:00
last_verified_commit: "983b0ebc761fd425bff5e80f72572870d61bbf00"
risk: medium
related_pr: "#147"
depends_on:
  - "merged OTBM asset, appearance, sprite and renderer tooling"
blocks: []
owned_paths:
  - tools/ai-agent/otbm_hd.py
  - tools/ai-agent/otbm_hd_tool.py
  - tools/ai-agent/test_otbm_hd.py
  - docs/ai-agent/OTBM_HD_PIPELINE.md
  - docs/agents/ACTIVE_WORK.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/CHANGELOG.md
  - docs/agents/tasks/active/CAN-20260712-otbm-hd-sprite-pipeline.md
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

Add a deterministic, reviewable HD-sprite pipeline around the existing OTBM renderer. The first slice exports only sprites used by a bounded map region, prepares padded inputs for an external AI upscaler, normalizes and validates returned PNGs, and renders the same region at 2x using accepted overrides while falling back to the original sprites.

# Safety boundaries

- Do not modify or commit `.otbm`, `items.otb`, `appearances.dat`, sprite sheets, CWM files, client packages, or generated PNG previews.
- Keep all generated test/output data outside the active datapack and repository.
- Preserve logical item IDs, appearance IDs, sprite IDs, map coordinates, stack order, displacement and elevation.
- AI output is never trusted automatically: every override must pass geometry and alpha validation.
- The external AI backend is opt-in and invoked without a shell.

# Acceptance criteria

- [x] Export bounded-region sprite PNGs and a deterministic manifest with item and usage provenance.
- [x] Prepare transparent padding before upscale and crop the scaled padding afterward.
- [x] Support deterministic nearest-neighbor reference output and a generic external-command AI backend.
- [x] Restore/preserve the source alpha mask independently of RGB model output.
- [x] Validate exact scale, dimensions, alpha mask and manifest/source hashes.
- [x] Render at 2x using accepted sprite overrides and deterministic nearest-neighbor fallback.
- [x] Produce machine-readable reports listing override and fallback usage.
- [x] Add focused unit tests and documentation.
- [x] Run a local Cobra Bastion proof of concept using the user-supplied map/assets without committing binaries.

# Implemented surface

- `export`: extracts only sprite IDs actually referenced by the bounded OTBM region and records item IDs, use counts, sample positions, dimensions, alpha bounds and hashes.
- `upscale`: supports a deterministic nearest baseline and an external model command using `{input}`, `{output}`, `{scale}` and `{sprite_id}` placeholders with `shell=False`.
- normalization: adds transparent padding before processing, crops scaled padding afterward and replaces model alpha with the nearest-scaled source alpha mask.
- `validate`: verifies source/export/override hashes, dimensions and exact alpha geometry.
- `render`: keeps the logical tile at 32 pixels while rendering at the declared pixel scale and applies accepted overrides with deterministic source fallback.
- `compare`: places a nearest-scaled original render beside the HD render for a like-for-like review.

# Validation log

Focused unit tests and bytecode compilation were run against the exact branch files copied from GitHub:

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

Covered:

- PNG encode/decode round trip and alpha bounds;
- padding, scaling, crop and alpha restoration;
- external command tokenization without a shell;
- external backend output normalization;
- nearest override pack creation and validation;
- explicit rejected-sprite fallback state.

# Cobra Bastion proof of concept

Local artifacts were generated outside the repository from:

```text
map: /mnt/data/otservbr(4).otbm
map SHA-256: a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2
assets: user-supplied modern client package
bounds: 33377,32631,7 -> 33417,32671,7
```

Results:

```text
map tiles: 1,681
sprite/item uses: 2,627
unique exported sprites: 287
missing appearances: 0
missing sprites: 0
accepted and validated overrides: 287/287
rejected overrides: 0
HD output: 3,136 x 3,136
used override sprites: 287
fallback sprites: 0
```

The proof of concept used the nearest-neighbor backend as a deterministic geometry/integration baseline. It validates extraction, padding, normalization, alpha preservation and 64-pixel tile rendering, but it is not evidence of AI visual quality. No compatible AI model weights were available in the execution environment; the external AI interface itself is covered by focused tests.

# Repository review

- Generated PNGs, manifests and user assets remain outside Git.
- No `.otbm`, `items.otb`, `appearances.dat`, sprite sheet, CWM, active datapack or production configuration path is changed.
- OTClient/CWM/modern asset-pack integration remains a separate cross-repository task.
- GitHub CI has not yet been observed on the current head; required checks remain authoritative before merge.
