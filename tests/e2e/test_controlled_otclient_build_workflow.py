from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "universal-agent-e2e.yml"


class ControlledOtclientBuildWorkflowTests(unittest.TestCase):
    def test_controlled_otclient_build_is_bounded_without_changing_pin_resolution(self) -> None:
        workflow = WORKFLOW.read_text(encoding="utf-8")

        self.assertIn("name: Build controlled OTClient", workflow)
        self.assertIn("repository: ${{ needs.resolve.outputs.client_repository }}", workflow)
        self.assertIn("ref: ${{ needs.resolve.outputs.client_ref }}", workflow)
        self.assertIn(
            "uses: lukka/run-cmake@5d55ea7949e25f69f0ecb516d8d572297e03a956",
            workflow,
        )
        self.assertIn('buildPresetAdditionalArgs: "[\'--parallel\', \'2\']"', workflow)

    def test_failed_controlled_otclient_build_retains_diagnostics(self) -> None:
        workflow = WORKFLOW.read_text(encoding="utf-8")

        diagnostics = """      - name: Upload controlled OTClient build diagnostics
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: otclient-linux-release-build-diagnostics
"""
        self.assertIn(diagnostics, workflow)
        self.assertIn("build/linux-release/CMakeCache.txt", workflow)
        self.assertIn("build/linux-release/.ninja_log", workflow)
        self.assertIn("build/linux-release/CMakeFiles/CMakeConfigureLog.yaml", workflow)
        self.assertIn("vcpkg_installed/vcpkg/issue_body.md", workflow)
        self.assertIn("if-no-files-found: warn", workflow)
        self.assertIn("retention-days: 14", workflow)

    def test_route_download_expression_is_unchanged_by_build_repair(self) -> None:
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "MAP_URL=\"$(grep -E '^mapDownloadUrl[[:space:]]*=' config.lua.dist | sed -E 's/.*\"([^\"]+)\".*/\\1/')\"",
            workflow,
        )


if __name__ == "__main__":
    unittest.main()
