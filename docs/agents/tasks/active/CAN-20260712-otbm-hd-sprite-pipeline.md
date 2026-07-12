---
task_id: CAN-20260712-otbm-hd-sprite-pipeline
status: active
agent: "GPT-5.6 Thinking"
branch: feat/otbm-hd-sprite-pipeline
base_branch: main
created: 2026-07-12T16:30:00+02:00
updated: 2026-07-12T16:30:00+02:00
last_verified_commit: "b1992c7380416139f4a0a2eb7ea0d593be47fdb2"
risk: medium
related_pr: "pending"
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

Add a deterministic, reviewable HD-sprite pipeline around the existing OTBM renderer. The first slice must export only sprites used by a bounded map region, prepare padded inputs for an external AI upscaler, normalize and validate returned PNGs, and render the same region at 2x using accepted overrides while falling back to the original sprites.

# Safety boundaries

- Do not modify or commit `.otbm`, `items.otb`, `appearances.dat`, sprite sheets, CWM files, client packages, or generated PNG previews.
- Keep all generated test/output data outside the active datapack and repository.
- Preserve logical item IDs, appearance IDs, sprite IDs, map coordinates, stack order, displacement and elevation.
- AI output is never trusted automatically: every override must pass geometry and alpha validation.
- The external AI backend is opt-in and invoked without a shell.

# Acceptance criteria

- [ ] Export bounded-region sprite PNGs and a deterministic manifest with item and usage provenance.
- [ ] Prepare transparent padding before upscale and crop the scaled padding afterward.
- [ ] Support deterministic nearest-neighbor reference output and a generic external-command AI backend.
- [ ] Restore/preserve the source alpha mask independently of RGB model output.
- [ ] Validate exact scale, dimensions, alpha bounds and manifest/source hashes.
- [ ] Render at 2x using accepted sprite overrides and deterministic nearest-neighbor fallback.
- [ ] Produce a machine-readable report listing override and fallback usage.
- [ ] Add focused unit tests and documentation.
- [ ] Run a local Cobra Bastion proof of concept using the user-supplied map/assets without committing binaries.

# Current progress

- Repository rules, open PRs, module catalogue, risks and build/test matrix reviewed.
- No open PR currently owns the planned HD tool paths.
- Branch created from `b1992c7380416139f4a0a2eb7ea0d593be47fdb2`.

# Validation log

Pending implementation.
