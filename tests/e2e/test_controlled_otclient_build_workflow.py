from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "universal-agent-e2e.yml"


class ControlledOtclientBuildWorkflowTests(unittest.TestCase):
    def test_controlled_otclient_source_pin_resolution_is_unchanged(self) -> None:
        workflow = WORKFLOW.read_text(encoding="utf-8")

        self.assertIn("name: Build controlled OTClient", workflow)
        self.assertIn("repository: ${{ needs.resolve.outputs.client_repository }}", workflow)
        self.assertIn("ref: ${{ needs.resolve.outputs.client_ref }}", workflow)

    def test_verified_freetype_mirror_preseeds_standard_vcpkg_download_cache(self) -> None:
        workflow = WORKFLOW.read_text(encoding="utf-8")

        self.assertIn("- name: Seed verified FreeType source fallback", workflow)
        self.assertIn(
            "FREETYPE_SOURCE_URL: https://github.com/freetype/freetype/archive/refs/tags/VER-2-14-3.tar.gz",
            workflow,
        )
        self.assertIn(
            "FREETYPE_SOURCE_SHA512: c3b6b0cc4b428c9c647ab2148386901dfd315273b68051940e8fea6010d46fdd2913467c3ef58be0d499b8e2ef5a0f1a4cc5e739756155587f4f7dff08ef9695",
            workflow,
        )
        self.assertIn('downloads_dir="${VCPKG_DOWNLOADS:-${vcpkg_root}/downloads}"', workflow)
        self.assertIn('archive="${downloads_dir}/freetype-freetype-VER-2-14-3.tar.gz"', workflow)
        self.assertIn("sha512sum --check --status", workflow)
        self.assertIn("sha512sum --check -", workflow)
        self.assertIn('source_kind="github-mirror"', workflow)
        self.assertIn("tee freetype-source-fallback.txt", workflow)

    def test_original_pinned_run_cmake_contract_is_preserved(self) -> None:
        workflow = WORKFLOW.read_text(encoding="utf-8")

        self.assertIn(
            "uses: lukka/run-cmake@5d55ea7949e25f69f0ecb516d8d572297e03a956",
            workflow,
        )
        self.assertIn("configurePreset: linux-release", workflow)
        self.assertIn("buildPreset: linux-release", workflow)
        self.assertIn(
            "configurePresetAdditionalArgs: \"['-DTOGGLE_BIN_FOLDER=ON', '-DOPTIONS_ENABLE_IPO=OFF']\"",
            workflow,
        )
        self.assertNotIn("buildPresetAdditionalArgs", workflow)
        self.assertNotIn("for attempt in 1 2 3; do", workflow)

    def test_failed_controlled_otclient_build_retains_diagnostics(self) -> None:
        workflow = WORKFLOW.read_text(encoding="utf-8")

        diagnostics = """      - name: Upload controlled OTClient build diagnostics
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: otclient-linux-release-build-diagnostics
"""
        self.assertIn(diagnostics, workflow)
        self.assertIn("freetype-source-fallback.txt", workflow)
        self.assertIn("build/linux-release/CMakeCache.txt", workflow)
        self.assertIn("build/linux-release/.ninja_log", workflow)
        self.assertIn("build/linux-release/CMakeFiles/CMakeConfigureLog.yaml", workflow)
        self.assertIn("vcpkg_installed/vcpkg/issue_body.md", workflow)
        self.assertIn("if-no-files-found: warn", workflow)
        self.assertIn("retention-days: 14", workflow)

    def test_success_artifact_retains_fallback_provenance(self) -> None:
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("name: otclient-linux-release", workflow)
        self.assertIn("freetype-source-fallback.txt", workflow)

    def test_route_download_expression_is_unchanged_by_build_repair(self) -> None:
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "MAP_URL=\"$(grep -E '^mapDownloadUrl[[:space:]]*=' config.lua.dist | sed -E 's/.*\"([^\"]+)\".*/\\1/')\"",
            workflow,
        )


if __name__ == "__main__":
    unittest.main()
