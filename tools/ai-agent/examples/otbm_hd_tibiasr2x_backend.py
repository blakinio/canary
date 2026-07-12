#!/usr/bin/env python3
"""Optional one-load TibiaSR 2x batch backend.

This reference adapter intentionally keeps PyTorch, NumPy, Pillow, and model
weights outside Canary's mandatory dependencies. It accepts the batch manifest
created by otbm_hd_batch_tool.py and writes one PNG per staged sprite.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the experimental TibiaSR 2x model over one staged batch")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--scale", type=int, required=True)
    parser.add_argument("--threads", type=int, default=0)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.scale != 2:
        raise SystemExit("TibiaSR reference checkpoint supports only scale 2")

    try:
        import numpy as np
        from PIL import Image
        import torch
        from torch import nn
        import torch.nn.functional as functional
    except ImportError as exc:
        raise SystemExit(f"missing optional TibiaSR dependency: {exc}") from exc

    class ResidualBlock(nn.Module):
        def __init__(self, channels: int) -> None:
            super().__init__()
            self.c1 = nn.Conv2d(channels, channels, 3, 1, 1)
            self.c2 = nn.Conv2d(channels, channels, 3, 1, 1)
            self.a = nn.PReLU(channels)

        def forward(self, value):
            return value + self.c2(self.a(self.c1(value))) * 0.15

    class TibiaSR2x(nn.Module):
        def __init__(self, channels: int, blocks: int) -> None:
            super().__init__()
            self.head = nn.Conv2d(4, channels, 3, 1, 1)
            self.act = nn.PReLU(channels)
            self.body = nn.Sequential(*(ResidualBlock(channels) for _ in range(blocks)))
            self.tail = nn.Sequential(
                nn.Conv2d(channels, channels * 4, 3, 1, 1),
                nn.PixelShuffle(2),
                nn.PReLU(channels),
                nn.Conv2d(channels, 3, 3, 1, 1),
            )

        def forward(self, value):
            base = functional.interpolate(value[:, :3], scale_factor=2, mode="nearest")
            features = self.body(self.act(self.head(value)))
            return (base + torch.tanh(self.tail(features)) * 0.25).clamp(0, 1)

    checkpoint = torch.load(args.model, map_location="cpu", weights_only=True)
    if not isinstance(checkpoint, dict) or checkpoint.get("format") != "tibia-sr2x-v1":
        raise SystemExit("unsupported TibiaSR checkpoint format")
    model = TibiaSR2x(int(checkpoint["channels"]), int(checkpoint["blocks"]))
    model.load_state_dict(checkpoint["state_dict"])
    model.eval()
    if args.threads > 0:
        torch.set_num_threads(args.threads)

    batch = json.loads(args.manifest.read_text(encoding="utf-8"))
    if batch.get("format") != "canary-otbm-hd-batch-input-v1":
        raise SystemExit("unsupported batch manifest format")
    if batch.get("scale") != 2:
        raise SystemExit("batch manifest scale does not match the TibiaSR checkpoint")
    sprites = batch.get("sprites")
    if not isinstance(sprites, list):
        raise SystemExit("batch manifest has no sprite list")
    args.output_dir.mkdir(parents=True, exist_ok=True)

    with torch.inference_mode():
        for entry in sprites:
            sprite_id = int(entry["spriteId"])
            source_path = args.input_dir / f"{sprite_id}.png"
            source = Image.open(source_path).convert("RGBA")
            rgba = np.asarray(source, dtype=np.float32) / 255.0
            rgb = torch.from_numpy(rgba[:, :, :3]).permute(2, 0, 1).unsqueeze(0)
            alpha = torch.from_numpy(rgba[:, :, 3:4]).permute(2, 0, 1).unsqueeze(0)
            model_input = torch.cat((rgb * alpha, alpha), dim=1)
            predicted = model(model_input)[0].permute(1, 2, 0).numpy()
            rgb8 = np.clip(np.rint(predicted * 255), 0, 255).astype(np.uint8)
            scaled_alpha = source.getchannel("A").resize(
                (source.width * 2, source.height * 2), Image.Resampling.NEAREST
            )
            output = np.dstack((rgb8, np.asarray(scaled_alpha, dtype=np.uint8)))
            Image.fromarray(output, "RGBA").save(args.output_dir / f"{sprite_id}.png", compress_level=9)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
