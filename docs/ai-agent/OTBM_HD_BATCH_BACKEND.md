# OTBM HD batch AI backend

## Purpose

`otbm_hd_batch_tool.py` extends the merged OTBM HD sprite pipeline with a one-process external backend. The existing `external` backend starts one process per sprite. That is useful for simple filters, but repeatedly loading a neural model for hundreds of sprites is unnecessarily slow and memory-intensive.

The batch backend stages every valid exported sprite first, starts one model process, then normalizes and validates every returned PNG independently:

```text
OTBM HD export
  -> verify source hashes and dimensions
  -> add transparent padding
  -> write one batch input manifest
  -> start one external process with shell=False
  -> read <spriteId>.png outputs
  -> reject missing, symlinked, malformed or wrong-sized outputs
  -> crop scaled padding
  -> restore the exact nearest-scaled source alpha mask
  -> write the existing HD override manifest format
  -> reuse the existing validate/render commands
```

It does not edit the OTBM, client assets, appearances, item definitions or sprite sheets.

## Run a batch backend

```bash
python tools/ai-agent/otbm_hd_batch_tool.py \
  artifacts/cobra-hd/export \
  --output artifacts/cobra-hd/ai-2x \
  --scale 2 \
  --padding 4 \
  --timeout 1800 \
  --command 'python model_backend.py \
    --manifest "{manifest}" \
    --input-dir "{input_dir}" \
    --output-dir "{output_dir}" \
    --scale {scale}'
```

Required command placeholders:

- `{manifest}`: JSON batch manifest;
- `{input_dir}`: directory containing padded `<spriteId>.png` inputs;
- `{output_dir}`: empty directory where the backend must write `<spriteId>.png` outputs.

Optional placeholders:

- `{scale}`: declared integer scale;
- `{work_dir}`: common temporary work directory.

The command is tokenized with `shlex` and executed with `shell=False`. The plaintext command is not written to the override manifest. A SHA-256 of the template is recorded for provenance. Do not place credentials on the command line because process inspection and backend logs may expose them.

## Batch input manifest

The backend receives `canary-otbm-hd-batch-input-v1`:

```json
{
  "format": "canary-otbm-hd-batch-input-v1",
  "scale": 2,
  "padding": 4,
  "sprites": [
    {
      "spriteId": 123,
      "input": "input/123.png",
      "output": "output/123.png",
      "source": {
        "width": 32,
        "height": 32,
        "pngSha256": "..."
      },
      "padded": {
        "width": 40,
        "height": 40
      },
      "expectedOutput": {
        "width": 80,
        "height": 80
      }
    }
  ]
}
```

The backend should load its model once, iterate over `sprites`, and write one PNG for each successful sprite. Partial output is allowed: a missing or invalid sprite is marked rejected while other valid outputs remain accepted.

## Safety and failure behavior

- Source paths must stay inside the export directory and cannot be symlinks.
- The output root must be empty unless `--overwrite` is supplied.
- `--overwrite` removes only known generated paths and refuses to remove unrelated files.
- Backend outputs must be regular files inside the dedicated batch output directory; symlinks are rejected.
- Output dimensions must equal the padded input dimensions multiplied by the declared scale.
- Model-generated alpha is discarded. The pipeline restores the exact nearest-scaled source alpha mask.
- A command failure or timeout rejects every staged sprite and still produces a reviewable override manifest.
- Every accepted PNG receives source/output/alpha hashes and remains compatible with `otbm_hd_tool.py validate` and `render`.

## Optional TibiaSR 2x reference adapter

`examples/otbm_hd_tibiasr2x_backend.py` is an optional reference backend for the experimental `tibia-sr2x-v1` checkpoint format. It demonstrates the one-load batch contract and requires packages that are deliberately not Canary dependencies:

```text
PyTorch
NumPy
Pillow
```

Example:

```bash
python tools/ai-agent/otbm_hd_batch_tool.py \
  artifacts/cobra-hd/export \
  --output artifacts/cobra-hd/tibiasr-2x \
  --scale 2 \
  --padding 4 \
  --command 'python tools/ai-agent/examples/otbm_hd_tibiasr2x_backend.py \
    --manifest "{manifest}" \
    --input-dir "{input_dir}" \
    --output-dir "{output_dir}" \
    --model /outside/repository/tibia_sr2x.pt \
    --scale {scale}'
```

The adapter loads checkpoints with `weights_only=True`. Model weights must remain outside Git. A model file is trusted build input and must have separately recorded provenance and licensing.

The reference checkpoint is self-supervised: it learns to reconstruct original 32x32 client sprites from synthetic 16x16 degradations and is then applied at 32x32 to 64x64. It can sharpen or smooth existing texture structure, but it has no true 64x64 ground truth. Results must therefore be described as experimental AI enhancement, not authentic missing source detail.

## Cobra Bastion local smoke

A non-committed local test used the same factual region and exact client assets as PR #154:

```text
map SHA-256: a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2
bounds: 33377,32631,7 -> 33417,32671,7
map tiles: 1,681
sprite uses: 2,627
unique sprites staged: 287
external model process invocations: 1
accepted and validator-usable overrides: 287/287
rejected overrides: 0
missing appearances: 0
missing sprites: 0
render output: 3,136 x 3,136
```

The full map layout, item order, displacement, elevation and alpha silhouettes stayed unchanged. Mean absolute RGB difference from a nearest-neighbor 2x reference was `3.97`, with a 95th percentile absolute channel difference of `17`. Generated sprites, model weights, reports and previews remained outside Git.

## Current boundary

This tool produces renderer override artifacts. It does not create CWM files, rewrite modern protobuf assets, or modify OTClient. Client integration remains a separate cross-repository task with its own compatibility and rollout tests.
