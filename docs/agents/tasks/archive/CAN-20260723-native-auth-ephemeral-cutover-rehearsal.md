---
task_id: CAN-20260723-native-auth-ephemeral-cutover-rehearsal
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: OTS-20260721-oteryn-identity-auth
status: completed
related_pr: "841"
merge_commit: b9658d14feb75918a693162d1cfe75d0e62aa549
completed: 2026-07-24T18:45:23+02:00
evidence_classification: PRODUCTION_LIKE_PROVEN
---

# CAN-20260723-native-auth-ephemeral-cutover-rehearsal

## Outcome

The Canary-owned native-auth rehearsal harness was delivered and its exact source was exercised by the successful Platform-hosted cross-repository production-like cutover rehearsal.

## Delivered

- Ephemeral Platform, Gateway, Canary, OTClient, MariaDB and Redis orchestration support.
- Verified TLS, hostname trust and private-network segmentation checks.
- OAuth Authorization Code + PKCE, Game Login Ticket and Canary Game Session boundaries.
- Exact Knight 1 world entry, safe logout and replay rejection.
- Credential overlap, retirement, rollback, re-close and final smoke.
- Malformed response, unauthorized-character and dependency-outage fail-closed scenarios.
- Sensitive response cache headers, request correlation and sanitized evidence handling.
- Durable retained-proof workflow verifying the merged Platform run and evidence artifact provenance.

## Validation

- Exact successful harness source: `f46ae126557d4d26043c77fe17968b72fd5bc688`.
- Platform rehearsal run `30095854266`: PASS.
- Retained artifact `8597730728`.
- Artifact digest `sha256:e7e908e9129658654054a96adf641757edc2c904fc2b01a5b9fc97e393d18009`.
- Final Canary CI `30108252520`: PASS after one infrastructure-only vcpkg retry.
- Native Auth retained-proof workflow `30108252354`: PASS.
- Agent Task Ownership `30108252413`: PASS.

## Evidence boundary

The maximum claim is `PRODUCTION_LIKE_PROVEN`. This work did not deploy production, use production secrets/data, remove legacy authentication, claim `PRODUCTION_PROVEN`, or close the manual Production Go-Live Gate.

## Completion

- PR: `blakinio/canary#841`
- Merge commit: `b9658d14feb75918a693162d1cfe75d0e62aa549`
- Archived at: 2026-07-24T18:52:00+02:00
