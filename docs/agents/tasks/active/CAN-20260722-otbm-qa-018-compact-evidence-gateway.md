---
task_id: CAN-20260722-otbm-qa-018-compact-evidence-gateway
program_id: CAN-PROGRAM-OTBM
status: ready
agent: "GPT-5.6 Thinking"
branch: feat/otbm-qa-018-compact-evidence-gateway-20260722
base_branch: main
created: 2026-07-22
updated: 2026-07-22
last_verified_commit: "e3025b29a6d1f56fe675768e98b3b773d3931355"
risk: medium
related_issue: ""
related_pr: "741"
depends_on:
  - shared-doc governance PR 743 merged
owned_paths:
  exclusive:
    - tools/ai-agent/otbm_evidence_gateway.py
    - tools/ai-agent/otbm_evidence_gateway_tool.py
    - tools/ai-agent/test_otbm_evidence_gateway.py
    - tools/ai-agent/test_otbm_evidence_gateway_output_safety.py
    - tools/ai-agent/test_otbm_evidence_gateway_schema.py
    - docs/ai-agent/OTBM_EVIDENCE_GATEWAY.md
    - docs/ai-agent/OTBM_EVIDENCE_GATEWAY_MANIFEST.schema.json
    - docs/ai-agent/OTBM_EVIDENCE_GATEWAY.schema.json
    - docs/agents/tasks/active/CAN-20260722-otbm-qa-018-compact-evidence-gateway.md
modules_touched:
  - otbm-evidence-gateway
public_interfaces:
  - canary-otbm-evidence-gateway-manifest-v1
  - canary-otbm-evidence-bundle-v1
cross_repo_tasks: []
---

# CAN-20260722 — OTBM-QA-018 Compact OTBM Evidence Gateway

## Status

READY — bounded QA-018 implementation is complete on PR #741. Shared governance merged through PR #743. `ci:final-gate` was applied before the final checkpoint cycle; this commit only normalizes checkpoint YAML to the validator-required block-list shape. No feature code changed and no further feature-branch commits are permitted.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-22T23:27:00+02:00
head: 384dcdfc199cf9e07468aeb33c547b5f25f42e31
branch: feat/otbm-qa-018-compact-evidence-gateway-20260722
pr: 741
status: ready
context_routes:
  - otbm
  - agent-governance
owned_paths:
  - tools/ai-agent/otbm_evidence_gateway.py
  - tools/ai-agent/otbm_evidence_gateway_tool.py
  - tools/ai-agent/test_otbm_evidence_gateway.py
  - tools/ai-agent/test_otbm_evidence_gateway_output_safety.py
  - tools/ai-agent/test_otbm_evidence_gateway_schema.py
  - docs/ai-agent/OTBM_EVIDENCE_GATEWAY.md
  - docs/ai-agent/OTBM_EVIDENCE_GATEWAY_MANIFEST.schema.json
  - docs/ai-agent/OTBM_EVIDENCE_GATEWAY.schema.json
  - docs/agents/tasks/active/CAN-20260722-otbm-qa-018-compact-evidence-gateway.md
proven:
  - PR 741 implements exact SHA/format-pinned bounded JSON Pointer extracts with source/extract hashes and safe relative source paths.
  - The gateway does not parse OTBM, validate or reinterpret source semantics, pathfind, run E2E or own downstream acceptance.
  - Pre-final CI 29959852882, Ownership 29959852726, OTBM Map Tools 29959852619 and AI Agent Tools 29959852579 passed on head e3025b29a6d1f56fe675768e98b3b773d3931355.
  - Shared governance PR 743 merged as 47759e49fca04526ef24097e9f3cf859b0f66b3a after full final-gate CI 29960786583 succeeded.
  - Initial exact-final Ownership 29962332088 failed checkpoint validation on the same inline context_routes shape already diagnosed in QA-017; checkpoint syntax is normalized here without changing feature code.
  - ci:final-gate was already applied before this checkpoint normalization commit.
derived:
  - QA-018 requires a fresh exact-final validation cycle on this corrected checkpoint head and no further commits.
unknown:
  - Downstream subsystem-specific scenario design, runtime execution and acceptance remain outside the gateway.
conflicts: []
first_failure:
  marker: checkpoint-context-routes-yaml
  evidence: Initial exact-final Ownership 29962332088 failed checkpoint validation on the inline context_routes form; corrected to validator-required block-list form on this commit.
rejected_hypotheses:
  - Feature implementation regression caused the checkpoint Ownership failure; focused OTBM validation remained green and the checkpoint shape matched the independently diagnosed QA-017 failure.
changed_paths:
  - docs/agents/tasks/active/CAN-20260722-otbm-qa-018-compact-evidence-gateway.md
  - tools/ai-agent/otbm_evidence_gateway.py
  - tools/ai-agent/otbm_evidence_gateway_tool.py
  - tools/ai-agent/test_otbm_evidence_gateway.py
  - tools/ai-agent/test_otbm_evidence_gateway_output_safety.py
  - tools/ai-agent/test_otbm_evidence_gateway_schema.py
  - docs/ai-agent/OTBM_EVIDENCE_GATEWAY.md
  - docs/ai-agent/OTBM_EVIDENCE_GATEWAY_MANIFEST.schema.json
  - docs/ai-agent/OTBM_EVIDENCE_GATEWAY.schema.json
validation:
  - command: GitHub Actions pre-final CI/Ownership/OTBM/AI
    result: PASS
    evidence: 29959852882, 29959852726, 29959852619 and 29959852579 all succeeded.
blockers: []
next_action: Verify exact-final-head CI, Ownership, OTBM Map Tools and AI Agent Tools on this corrected checkpoint head plus review/mergeability on PR 741, then mark ready, enable auto-merge and complete lifecycle closure after merge.
```
