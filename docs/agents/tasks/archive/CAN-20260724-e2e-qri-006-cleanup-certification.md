---
task_id: CAN-20260724-e2e-qri-006-cleanup-certification
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-QRI-006
status: completed
agent: "GPT-5.6 Thinking"
branch: feat/e2e-qri-006-cleanup-certification
base_branch: main
created: 2026-07-24
updated: 2026-07-24
last_verified_commit: "a5cafe1b7ce148af59c64d1382963ac6ac633334"
risk: medium
related_issue: ""
related_pr: "871, 875, 881"
depends_on:
  - merged and lifecycle-closed E2E-QRI-005 result envelope
  - canonical Universal Physical E2E lifecycle
blocks: []
owned_paths:
  exclusive: []
  shared: []
  read_only: []
modules_touched:
  - Universal E2E resource cleanup certification
reuses:
  - canary-universal-e2e-result-envelope-v1 schema version 3
  - canonical Universal Physical E2E wrapper, lifecycle and existing artifact upload
  - exact runner-owned PID files, dedicated process group, exit evidence and fixed disposable MariaDB authority
public_interfaces:
  - canary-universal-e2e-cleanup-certification-v1
cross_repo_tasks: []
---

# CAN-20260724 — E2E-QRI-006 resource cleanup certification

## Completion

- Final status: completed.
- Delivery PR: #871.
- Delivery squash merge: `6ad2172eb8e4d5a9fcda0d69f2b6c88906082bfb`.
- Post-merge evidence-hardening PR: #875.
- Hardening squash merge: `a5cafe1b7ce148af59c64d1382963ac6ac633334`.
- Lifecycle closure PR: #881.
- Final exact-head candidate: `c94af1cec25c28763ad95f13a7ae06673b6551f7`.
- Final Agent Task Ownership: PASS, run `30099655029`.
- Final full `ci:final-gate` CI: PASS, run `30099655274`.
- Final `autofix.ci`: PASS, run `30099654994`.
- Final Universal Agent E2E: PASS, run `30099655153`.
- Final physical artifact: `8599919569`, digest `sha256:bde3a45d3b9cf561011d119527df75a1eea43c0af7795f1874a545e59f6b3f95`.

## Delivered contract

- `canary-universal-e2e-cleanup-certification-v1`, schema version 1, is emitted as `cleanup-certification.json` through the existing Universal Physical E2E artifact upload.
- The existing schema-v3 `result.json` consumes the exact cleanup contract and promotes only the orthogonal `quality_dimensions.cleanup` value; gameplay status remains independent.
- Certification runs after the canonical lifecycle trap and evaluates only bounded runner-owned resources: the dedicated process group, exact recorded process IDs, declared clients, disposable MariaDB online rows and transactions, declared fixture ghost sessions, workspace restoration, temporary markers and workflow-owned service handoff.
- Residual members of the exact runner-owned process group are handled with bounded SIGTERM/SIGKILL escalation. No process lookup or termination by executable/name/substring, caller-selected PID/PGID, arbitrary command, SQL, host, table or production target was introduced.
- A cleanup failure causes the wrapper to fail even when gameplay succeeds, while preserving the gameplay evidence and first causal failure.
- No second runner, workflow, artifact system or result-envelope implementation was added.

## Physical proof

- Final physical `login/relog` completed successfully with gameplay `status: success`.
- Cleanup certification reported `cleanup_certified: true`, status `certified`, 18 of 18 required checks passed, zero warnings and zero unknowns.
- The schema-v3 envelope reported `quality_dimensions.cleanup: pass`.
- The dedicated process group had no remaining members after bounded cleanup; player-online, transaction and declared fixture ghost-session checks were zero; workspace files and temporary markers were restored/absent as required.
- Raw `client-events.tsv` records `packet_record_1=session-1.record` and `packet_record_2=session-2.record`, with no `/home/runner` or other absolute runner-system path.

## Failure history retained

- Physical run `30085762318` proved gameplay success and 17 of 18 cleanup checks, but found residual PID `4872` in the dedicated process group. This was the first causal cleanup failure.
- The certifier was corrected to reap only members of the exact dedicated process group with bounded escalation. Later physical evidence proved 18 of 18 checks with no remaining members.
- Post-merge artifact `8597198699` still exposed absolute packet-record paths in raw client events. PR #875 preserved the full runtime path only for `loginWorld` while emitting safe basenames into events, then physically re-proved the complete contract.
- Failed and superseded attempts remain documented and were not hidden by successful retries.

## Final scope and review audit

- Delivery PR #871 introduced the certifier, focused tests, wrapper integration, result-envelope integration and required discovery/task updates without modifying the shared lifecycle body or workflow.
- Follow-up PR #875 changed exactly three paths: the active task checkpoint, one focused regression test and `tools/e2e/client/agent_e2e.lua`.
- The follow-up PR had no issue comments, review submissions or unresolved inline review threads.
- Final exact-head Ownership, full Required CI, autofix and Universal Agent E2E all passed before squash merge.

## Evidence boundaries

- Cleanup certification applies only to exact runner-owned resources and the disposable E2E database authority represented by the contract checks.
- It does not certify production/staging cleanup, arbitrary host processes, workflow-owned container shutdown, unrelated services, determinism, resilience, exactly-once behavior, concurrency, performance or compatibility.
- Evidence maturity M0-M5 remains independent of orthogonal quality dimensions.

## Lifecycle closure

The delivery and evidence-hardening packages are merged. This archive record releases all QRI-006 task ownership; no active path remains reserved by E2E-QRI-006.
