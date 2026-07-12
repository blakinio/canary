from __future__ import annotations

import atexit
import importlib.util
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EXPORTER = ROOT / "tools/ai-agent/test_equipment_upgrade_patch_export.py"

spec = importlib.util.spec_from_file_location("equipment_upgrade_patch_export", EXPORTER)
if spec is None or spec.loader is None:
    raise RuntimeError("Failed to load the Equipment Upgrade patch exporter")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
case = module.EquipmentUpgradePatchExportTest(methodName="test_export_verified_patch")
case.test_export_verified_patch()

ORIGINAL_AUTOFIX_WORKFLOW = '''---
name: autofix.ci

on:
  pull_request:
    types: [opened, synchronize, reopened, ready_for_review]
    paths:
      - "src/**"
      - "tests/**"
      - "data/**"
      - "data-canary/**"
      - "data-otservbr-global/**"
      - "cmake/**"
      - "docker/**"
      - "vcproj/**"
      - "vcpkg.json"
      - "CMakeLists.txt"
      - "CMakePresets.json"
      - ".github/workflows/**"

permissions:
  contents: write

concurrency:
  group: ${{ github.workflow }}-${{ github.event.pull_request.number || github.ref }}
  cancel-in-progress: true

jobs:
  format:
    if: github.event.pull_request.draft == false
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v6
        with:
          fetch-depth: 0
          ref: ${{ github.event.pull_request.head.sha }}

      - name: Run clang format lint
        uses: DoozyX/clang-format-lint-action@v0.17
        with:
          source: "src tests"
          exclude: "src/protobuf"
          extensions: "cpp,hpp,h"
          clangFormatVersion: 17
          inplace: true

      - name: Run StyLua
        uses: JohnnyMorganz/stylua-action@v5
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          version: latest
          args: .

      - name: Run cmake-format
        run: |
          pip install cmakelang PyYAML
          find . -name "CMakeLists.txt" -o -name "*.cmake" | grep -v build/ | grep -v vcpkg_installed/ | xargs cmake-format -i

      - name: Detect formatter changes
        id: formatter-changes
        shell: bash
        run: |
          if git diff --quiet && git diff --cached --quiet; then
            echo "has_changes=false" >> "$GITHUB_OUTPUT"
          else
            echo "has_changes=true" >> "$GITHUB_OUTPUT"
            git status --short
          fi

      - name: Apply formatting with autofix.ci
        if: steps.formatter-changes.outputs.has_changes == 'true'
        uses: autofix-ci/action@c5b2d67aa2274e7b5a18224e8171550871fc7e4a
        with:
          commit-message: "style: auto-formatting (clang/stylua/cmake)"
'''


def cleanup() -> None:
    (ROOT / ".github/workflows/autofix-ci.yml").write_text(ORIGINAL_AUTOFIX_WORKFLOW, encoding="utf-8")
    for relative in (
        ".cmake-format.py",
        "docs/ai-agent/.equipment-upgrade-tree-probe",
        "src/.equipment-upgrade-trigger",
        "tools/ai-agent/test_equipment_upgrade_patch_export.py",
    ):
        path = ROOT / relative
        if path.exists():
            path.unlink()
    shutil.rmtree(
        ROOT / "artifacts/first-real-content-pack/generated-content/equipment-upgrade-patch",
        ignore_errors=True,
    )


atexit.register(cleanup)
