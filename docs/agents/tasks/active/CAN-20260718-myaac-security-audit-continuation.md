---
task_id: CAN-20260718-myaac-security-audit-continuation
program_id: CAN-PROGRAM-SECURITY-VALIDATION
status: validating
agent: "GPT-5.5 Thinking"
branch: docs/myaac-security-audit-continuation-20260718
base_branch: main
created: 2026-07-18T20:56:00+02:00
updated: 2026-07-18T21:02:00+02:00
last_verified_commit: "2224e67db3f77643fe9fda076ea69df345f38408"
risk: high
related_issue: ""
related_pr: "556"
depends_on: []
blocks: []
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260718-myaac-security-audit-continuation.md
    - docs/security/MYAAC_SECURITY_AUDIT_HANDOVER_2026-07-18.md
  shared: []
  read_only:
    - docs/security/MYAAC_CANARY_SECURITY_AUDIT_2026-07-17.md
    - slawkens/myaac
    - opentibiabr/login-server
    - opentibiabr/canary
modules_touched:
  - security-audit
reuses:
  - existing MyAAC / Canary security audit report
  - existing security-validation program
  - existing agent task governance and context checkpoint contracts
public_interfaces: []
cross_repo_tasks: []
---

# CAN-20260718 — MyAAC security audit continuation

## Status

MyAAC-only continuation evidence has been preserved in a dedicated handover. The task is now validating documentation scope, checkpoint structure, PR state, and exact-head CI.

## Goal

Continue the MyAAC and MyAAC → login-server → Canary security audit, preserve only new or materially extended evidence, and leave a MyAAC-only continuation handover. External repositories remain read-only.

## Routes

- `agent-governance`

## Authorization and repository boundary

- Writable repository: `blakinio/canary` only.
- `slawkens/myaac` and `opentibiabr/*` are read-only evidence sources.
- No public or third-party deployment is tested.
- No production credentials, private logs, database dumps, or live secrets are committed.

## Acceptance criteria

- [x] Read current `AGENTS.md`, repository map, context routing, merged audit report, archived predecessor task, and PR #453 lifecycle history.
- [x] Check open PRs narrowly for overlapping MyAAC/login-stack audit ownership.
- [x] Revalidate material source chains against the pinned MyAAC baseline and current rolling `develop` where available.
- [x] Preserve one new rate-limit bypass finding and material extensions without duplicating existing findings.
- [x] Write a MyAAC-only handover with exact evidence states, limitations, branch/PR/task/head/CI/merge state, and one `next_action`.
- [x] Keep changed-file scope documentation-only and limited to owned paths.
- [ ] Validate task/checkpoint structure and inspect final changed-file list/diff.
- [ ] Apply final-head CI gate and merge only after all required checks pass.

## Validation

- Full MyAAC + MariaDB + login-server + Canary E2E is unavailable in the current sandbox.
- PHP CLI is available; Docker/MariaDB and PHP GD/ZipArchive are unavailable.
- An isolated exact-logic `RateLimit` harness confirmed the reset bypass but is not represented as full-stack E2E.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-18T21:02:00+02:00
head: 2224e67db3f77643fe9fda076ea69df345f38408
branch: docs/myaac-security-audit-continuation-20260718
pr: 556
status: validating
context_routes:
  - agent-governance
owned_paths:
  - docs/agents/tasks/active/CAN-20260718-myaac-security-audit-continuation.md
  - docs/security/MYAAC_SECURITY_AUDIT_HANDOVER_2026-07-18.md
proven:
  - merged PR 453 and its archived task were read; PR 453 final head f1961e9ce6a1f231a0ed8900519a9f4634fe4ea8 merged as 6b42890347338a13daca5fd6291b56b8dc6aa091
  - no open PR found with the same MyAAC/login-stack audit documentation scope before PR 556 was opened
  - MyAAC web and native game login rate limiting uses a shared per-IP bucket and resets that bucket after valid credentials
  - valid credentials for an attacker-controlled account can reset the IP bucket before the threshold, enabling repeated victim guesses without reaching lockout
  - the reset behavior remains present on current rolling MyAAC develop source
  - ordinary FLAG_ADMIN can directly edit arbitrary account password, TOTP secret, web_flags and game privilege fields; this materially extends the existing broken-access-control finding
  - FLAG_ADMIN can reach PHP execution through custom database PHP pages after self-granting page content permission and enabling PHP pages; this is an alternate RCE path under the existing broken-access-control finding
  - Gallery URL ingestion can fetch remote images through GD URL wrappers and persist a re-encoded copy, making the existing SSRF response-revealing for valid image resources when URL fopen wrappers are enabled
  - existing SEC-28 already records the global forum cooldown; this continuation only adds the non-atomic concurrent bypass aspect
  - paid-operation scan reconfirmed change-name/change-sex read-check-mutate-write races already covered by existing findings; no distinct new core paid-operation finding was promoted
  - no current ZIP Slip claim is proven
  - normal character-comment and guild-description update paths escape HTML before later raw rendering
  - MyAAC derives browser real IP from REMOTE_ADDR in the reviewed compatibility path; external login-server XFF spoofing does not transfer to this MyAAC path
  - isolated exact-logic RateLimit harness completed 80 victim guesses with max_attempts 5 by resetting after every 4 guesses; final bucket remained zero and unblocked
derived:
  - the new rate-limit reset finding provides a deterministic brute-force throttle bypass to an attacker holding any valid account credential, including an unverified account on paths that reset before email verification rejection
  - forum cooldown precheck and insert are not atomic, so concurrent requests can pass the same precheck
unknown:
  - full integrated behavior in a disposable MyAAC + MariaDB + login-server + Canary stack
  - current exact SHA of slawkens/myaac develop as built by an arbitrary future quickstart invocation
  - current PHP ZipArchive/libzip traversal behavior in the unavailable target runtime
conflicts: []
first_failure:
  marker: local source checkout
  evidence: sandbox git clone could not resolve github.com; source review continued through the GitHub connector
rejected_hypotheses:
  - forum global cooldown as a new finding; already preserved as SEC-28
  - current ZIP Slip arbitrary overwrite without target-runtime proof
  - normal character-comment stored XSS through the reviewed update flow
  - normal guild-description stored XSS through the reviewed update flow
  - MyAAC XFF-spoofed limiter bypass through get_browser_real_ip in the reviewed path
changed_paths:
  - docs/agents/tasks/active/CAN-20260718-myaac-security-audit-continuation.md
  - docs/security/MYAAC_SECURITY_AUDIT_HANDOVER_2026-07-18.md
validation:
  - command: narrow open-PR/task ownership review
    result: PASS
    evidence: no overlapping open MyAAC/login-stack audit documentation PR identified before PR 556
  - command: isolated exact-logic RateLimit harness
    result: PASS
    evidence: victim_guesses=80 remaining_attempts=0 blocked=no with max_attempts=5
  - command: predecessor durable report duplicate check
    result: PASS
    evidence: global forum cooldown was detected as existing SEC-28 and was not assigned a duplicate MYAAC number
blockers:
  - full integrated E2E unavailable in current sandbox
  - final changed-file/diff inspection and GitHub CI still pending
next_action: Inspect PR 556 changed-file list and full diff, verify task/checkpoint validation and required CI on the current head, apply ci:final-gate before the final checkpoint commit, then merge only if the exact final head is fully green and review-clean.
```
