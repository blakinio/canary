from __future__ import annotations

import unittest

import checkpoint


def valid_checkpoint() -> dict[str, object]:
    return {
        "checkpoint_version": "1",
        "updated_at": "2026-07-20T12:00:00Z",
        "head": "0123456789012345678901234567890123456789",
        "branch": "docs/test",
        "pr": "123",
        "status": "implementing",
        "context_routes": ["agent-governance"],
        "owned_paths": ["tools/agents/checkpoint.py"],
        "proven": ["bounded fact"],
        "derived": [],
        "unknown": [],
        "conflicts": [],
        "first_failure": {"marker": "none", "evidence": "none"},
        "rejected_hypotheses": [],
        "changed_paths": ["tools/agents/checkpoint.py"],
        "validation": [
            {"command": "unit tests", "result": "PASS", "evidence": "local"}
        ],
        "blockers": ["none"],
        "next_action": "Run focused validation.",
    }


class CheckpointCompactnessTests(unittest.TestCase):
    def test_list_at_compactness_limit_passes(self) -> None:
        data = valid_checkpoint()
        limit = checkpoint.MAX_LIST_ITEMS["proven"]
        data["proven"] = [f"fact {index}" for index in range(limit)]

        self.assertEqual([], checkpoint.validate_checkpoint(data))

    def test_list_over_compactness_limit_is_rejected(self) -> None:
        data = valid_checkpoint()
        limit = checkpoint.MAX_LIST_ITEMS["proven"]
        data["proven"] = [f"fact {index}" for index in range(limit + 1)]

        errors = checkpoint.validate_checkpoint(data)

        self.assertTrue(
            any(
                f"proven has {limit + 1} items; compactness limit is {limit}" in error
                for error in errors
            )
        )

    def test_validation_entries_are_bounded_too(self) -> None:
        data = valid_checkpoint()
        limit = checkpoint.MAX_LIST_ITEMS["validation"]
        data["validation"] = [
            {"command": f"check-{index}", "result": "PASS", "evidence": "local"}
            for index in range(limit + 1)
        ]

        errors = checkpoint.validate_checkpoint(data)

        self.assertTrue(
            any(
                f"validation has {limit + 1} items; compactness limit is {limit}" in error
                for error in errors
            )
        )


if __name__ == "__main__":
    unittest.main()
