# OTBM HD sprite pipeline

## Purpose

`otbm_hd_tool.py` extends the read-only OTBM renderer with a reviewable HD-sprite workflow. It does not edit the map, item definitions, appearances data, sprite sheets, or active datapacks.

The pipeline operates on the exact sprite IDs used by a bounded map region:

```text
OTBM region
  -> export referenced sprite PNGs and provenance
  -> add transparent padding
  -> nearest reference or external AI command
  -> crop scaled padding
  -> restore the original alpha mask at the declared scale
  -> validate hashes and geometry
  -> render the same OTBM region with accepted overrides
  -> fall back to deterministic nearest scaling for rejected sprites
```

## Safety properties

- Source OTBM and client assets are read-only.
- Every export is tied to the complete map, asset-catalog, appearances, and PNG SHA-256 values.
- External commands are executed as an argument vector with `shell=False`.
- The model must produce the exact padded dimensions requested by the declared scale.
- The tool discards model-generated alpha and restores the nearest-scaled source alpha mask.
- An override is used only after source hash, output hash, dimensions, and alpha validation pass.
- Rejected model outputs are recorded and use the original sprite through deterministic nearest-neighbor fallback.
- Generated PNGs and manifests belong in `artifacts/**` or another temporary output directory and must not be committed.

## Commands

### 1. Export the sprites used by a region

```bash
python tools/ai-agent/otbm_hd_tool.py export \
  world.otbm client-assets/ \
  --from 33377,32631,7 \
  --to 33417,32671,7 \
  --output artifacts/cobra-hd/export
```

The export contains:

```text
export/
  manifest.json
  original/<spriteId>.png
```

Each manifest entry records the sprite ID, referencing item IDs, use count, sample map positions, image dimensions, alpha bounds, and hashes.

### 2. Produce a deterministic reference pack

Nearest-neighbor is not an AI enhancement. It is the geometry and integration baseline:

```bash
python tools/ai-agent/otbm_hd_tool.py upscale \
  artifacts/cobra-hd/export \
  --output artifacts/cobra-hd/nearest-2x \
  --scale 2 \
  --padding 4 \
  --backend nearest
```

### 3. Run an external AI backend

The backend is deliberately model-agnostic. The command template may use:

- `{input}`: padded source PNG;
- `{output}`: required output PNG;
- `{scale}`: integer scale;
- `{sprite_id}`: current sprite ID.

Example interface:

```bash
python tools/ai-agent/otbm_hd_tool.py upscale \
  artifacts/cobra-hd/export \
  --output artifacts/cobra-hd/ai-2x \
  --scale 2 \
  --padding 4 \
  --backend external \
  --command 'python ai_backend.py --input "{input}" --output "{output}" --scale {scale} --sprite-id {sprite_id}'
```

The repository does not bundle model weights. Do not place API tokens or credentials in the command template because the template is written to the generated manifest.

For best results, the external backend should preserve the sprite silhouette and palette instead of inventing new objects. Padding reduces edge damage for walls, floors, borders, and multi-sprite structures. The normalized output always receives the original scaled alpha mask.

### 4. Validate the override pack

```bash
python tools/ai-agent/otbm_hd_tool.py validate \
  artifacts/cobra-hd/ai-2x \
  --export artifacts/cobra-hd/export \
  --report artifacts/cobra-hd/validation.json
```

`--export` makes the pack portable. Without it, the validator uses the source-export path recorded when the pack was created.

### 5. Render with accepted overrides

```bash
python tools/ai-agent/otbm_hd_tool.py render \
  world.otbm client-assets/ artifacts/cobra-hd/ai-2x \
  --export artifacts/cobra-hd/export \
  --from 33377,32631,7 \
  --to 33417,32671,7 \
  --output artifacts/cobra-hd/cobra-ai-2x.png \
  --report artifacts/cobra-hd/render-report.json
```

The map remains logically 32x32 pixels per tile. A scale of two renders each logical tile as 64x64 pixels and scales sprite dimensions, displacement, elevation, and padding consistently.

### 6. Create a visual comparison

```bash
python tools/ai-agent/otbm_hd_tool.py compare \
  artifacts/cobra-original.png \
  artifacts/cobra-hd/cobra-ai-2x.png \
  --output artifacts/cobra-hd/comparison.png
```

The left side is the original render enlarged with nearest-neighbor. The right side is the HD override render. This avoids comparing different logical map sizes.

## Partial failures and review

A generated override manifest may contain both `accepted` and `rejected` entries. Validation treats rejected entries as explicit fallback states, but any accepted entry with a broken hash, size, or alpha mask invalidates the pack.

Recommended review states outside the tool are:

```text
accepted
rejected
manual-fix
use-original
```

Only accepted and validated PNGs are used as overrides.

## Cobra Bastion reference smoke

A local, non-committed smoke test used the supplied OTBM and matching modern client assets for floor 7, bounds `33377,32631,7` through `33417,32671,7`.

```text
map SHA-256: a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2
map tiles: 1,681
rendered item/sprite uses: 2,627
unique exported sprites: 287
missing appearances: 0
missing sprites: 0
nearest 2x overrides accepted and validated: 287/287
HD output: 3,136 x 3,136
fallback sprites: 0
```

This smoke validates extraction, padding, normalization, alpha preservation, override loading, and 64-pixel tile rendering. It is a nearest-neighbor reference, not evidence of AI visual quality. An actual AI-quality test requires an external model and weights supplied outside the repository.

## Current boundary and future work

This PR produces renderer override packs. It does not generate `.cwm`, rewrite modern protobuf assets, or modify OTClient.

Future client integration should be a separate cross-repository task because:

- CWM loading and modern `SpriteAppearances` follow different client paths;
- client sprite size, logical tile size, displacement, animations, effects, outfits, UI scaling, and backward compatibility must be tested together;
- binary client packs and model outputs must remain external build artifacts.
