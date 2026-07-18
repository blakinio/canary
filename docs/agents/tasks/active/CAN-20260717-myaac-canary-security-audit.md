# CAN-20260717 — MyAAC / Canary security audit record

## Status

Documentation and continuation handover captured; final-head CI gate pending before merge.

## Goal

Preserve the isolated offensive-security assessment of the Canary Docker quickstart, MyAAC integration, external login-server dependency, and the continuation findings that materially affect Canary-owned runtime/multichannel security boundaries. This task records evidence only; it does not modify read-only upstream repositories or implement remediations.

## Routes

- `agent-governance`
- `cross-repo` for documenting authentication and login-policy boundaries involving read-only dependencies
- `cpp-runtime` for the documented Canary-owned multichannel/economy continuation findings

## Authorization and repository boundary

- Writable repository: `blakinio/canary` only.
- `opentibiabr/canary`, `opentibiabr/login-server`, `slawkens/myaac`, `opentibiabr/otclient`, `opentibiabr/remeres-map-editor`, and `opentibiabr/client-editor` are evidence sources only and remain read-only.
- No public or third-party deployment was tested.
- This PR contains documentation only and does not include private keys, private logs, local database dumps, production secrets, or live credential material.

## Owned paths

- `docs/security/MYAAC_CANARY_SECURITY_AUDIT_2026-07-17.md`
- `docs/security/OTS_SECURITY_AUDIT_HANDOVER_2026-07-18.md`
- `docs/agents/tasks/active/CAN-20260717-myaac-canary-security-audit.md`

## Scope

The durable documentation consolidates:

- source review of MyAAC account, admin, CSRF, reset, session, template, plugin, FAQ, status, rate-limit, race-condition and raw-render paths;
- source review of Canary Docker quickstart integration;
- source review of the external `opentibiabr/login-server` authentication, HTTP, gRPC, rate-limit, session, and dependency behavior;
- isolated local PHP/Python harness tests reproducing selected current-source logic;
- continuation review of Canary-owned market/economy ordering and multichannel Redis/DB ownership, fencing, persistence, handoff, leader-election and global-state paths;
- continuation review of OTClient, RME and client-editor trust boundaries as read-only evidence sources;
- explicit limitations where Docker, MariaDB/MySQL, Composer, GD, ZipArchive, or full E2E integration were unavailable.

## Evidence model

- `PROVEN`: directly reproduced in an isolated local harness or directly revalidated against current source.
- `DYNAMICALLY CONFIRMED`: reproduced by an isolated focused harness.
- `DERIVED`: strongly supported by source composition but not executed end-to-end in the target stack.
- `CANDIDATE`: requires an additional call-chain or dynamic proof.
- `REJECTED` / `FALSE POSITIVE`: explicitly traced and not currently a valid finding.

Rejected hypotheses remain documented to prevent rediscovery.

## Acceptance criteria

- [x] Consolidated report committed under `docs/security/`.
- [x] Continuation handover committed under `docs/security/`.
- [x] Documentation distinguishes proven, derived, configuration-dependent, candidate, and rejected items.
- [x] Documentation contains no private secrets, private logs, database dumps, local absolute lab paths, or production-target instructions.
- [x] Current Canary quickstart observations were revalidated during the assessment.
- [x] Draft PR targets `blakinio/canary:main` from the dedicated task branch.
- [x] Changed-file scope is documentation only; no `.otbm`, `items.otb`, datapack, runtime, workflow, or production configuration change is part of this PR.
- [x] `ci:final-gate` was applied before this final checkpoint commit.
- [ ] Required GitHub checks pass on this exact final head.
- [ ] PR is marked ready and squash-merged after the autonomous merge gate is satisfied.

## Validation

- Documentation-only change: no local C++/Lua/runtime build is required for the changed paths.
- The final changed-file list and diff must contain only the three owned documentation paths above.
- No binary map/assets or production credentials may be introduced.
- Final-head CI must be checked on the commit created by this checkpoint update; no commit may be added after a green final-head gate without rerunning the gate.

## Context checkpoint

### Current state

- Branch: `docs/myaac-canary-security-audit-20260717`.
- Draft PR: `https://github.com/blakinio/canary/pull/453`.
- Durable report: `docs/security/MYAAC_CANARY_SECURITY_AUDIT_2026-07-17.md`.
- Continuation handover: `docs/security/OTS_SECURITY_AUDIT_HANDOVER_2026-07-18.md`.
- The handover preserves the expanded audit state, highest-priority auth/MyAAC/economy/multichannel findings, rejected hypotheses, validation gaps and concrete continuation priorities.
- The working external matrix reached 102 tracked findings at the end of the continuation pass; the binary spreadsheet itself is not committed in this documentation PR.
- No remediation code is included. Fixes must be split into bounded Canary-owned tasks/PRs with their own validation.

### Key continuation evidence

- `PROVEN`: lower MyAAC web-admin authority can reach sensitive privilege-editing and plugin-management surfaces; treat the traced escalation chain as critical broken access control.
- `PROVEN`: market create/accept/cancel/expiry ordering contains multiple atomicity and crash-consistency gaps.
- `PROVEN`: multichannel persistent player saves do not enforce fencing at the final persistence boundary.
- `PROVEN`: mail handoff apply/state transitions are not exactly-once atomic.
- `PROVEN`: house persistence and identity are not consistently channel-isolated.
- `PROVEN`: direct target-channel login bypasses the full channel-switch policy path.
- `PROVEN`: process-local offline-player resolution can full-save a character actually owned by another channel process.
- `PROVEN`: synchronous Redis heartbeat work can stall the main game dispatcher during Redis degradation.
- `PROVEN`: the intended Redis/DB fail-closed operational policy is not represented by one central mutation gate in the traced runtime/economy paths.
- `DYNAMICALLY CONFIRMED`: selected MyAAC rate-limit and HTML-filter behavior reproduced in isolated harnesses.
- `REJECTED`: livestream viewer opcode `0x96 -> parseSay()` cannot reach caster world speech/actions through the traced path; the viewer guard stops non-livestream speech before `Game::playerSay`.

### Limitations

- No full-stack MariaDB/MySQL + Redis + multi-process Canary E2E execution was available in the original lab.
- No full native login PCAP/decrypt/session-replay E2E was completed.
- No public deployment was attacked or scanned.
- External dependency findings are recorded as Canary integration risk; remediation in read-only repositories remains outside this task unless separately authorized.

### next_action

Inspect PR #453 final changed-file list/diff and current-head checks. If the exact final head is green, mergeable, review-thread clean and still documentation-only, mark the PR ready and squash-merge it. Open separate bounded remediation tasks for Canary-owned fixes; do not bundle runtime fixes into this documentation PR.
