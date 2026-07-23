---
task_id: CAN-20260723-native-auth-production-like-boundary
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: OTS-20260721-oteryn-identity-auth
status: implementing
agent: "GPT-5.6 Thinking"
branch: test/CAN-20260723-native-auth-production-like-boundary
base_branch: main
created: 2026-07-23T18:30:00+02:00
updated: 2026-07-23T18:30:00+02:00
last_verified_commit: 5bd9d91c570af127edab51a2c3509e0f37b6a30e
risk: high
related_issue: ""
related_pr: ""
depends_on:
  - "Hardened native-auth physical E2E run 30021347231"
  - "Canary PR #807 merged as 981c82f5ebb6bc22c867312c2b274a71f6aeeb3e"
  - "Oteryn Platform PR #124 merged as 53158217a6c6017230301cf4daa783b04fcc13d5"
blocks: []
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260723-native-auth-production-like-boundary.md
    - tests/e2e/test_native_auth_production_like_boundary.py
    - .github/workflows/native-auth-production-like-validation.yml
  shared: []
modules_touched:
  - Oteryn native-auth production-like validation
reuses:
  - hardened native-auth evidence harness from closed PR #755
  - Oteryn Platform Gateway exact merged revision
  - Oteryn native-auth Platform stub
public_interfaces: []
cross_repo_tasks:
  - OTERYN-20260723-native-auth-production-cutover
---

# Goal

Build a validation-only production-like simulation for the remaining Oteryn native-auth deployment boundary without claiming real production evidence or performing production activation.

# Acceptance criteria

- [ ] Prove the exact merged Gateway rejects non-loopback plain HTTP Game Session dependencies.
- [ ] Prove trusted HTTPS with hostname verification succeeds against a production-like private Session Issuer boundary.
- [ ] Prove an untrusted CA and a hostname mismatch fail closed.
- [ ] Prove simulated current/previous service-credential overlap accepts both credentials during rotation and rejects the retired credential after overlap removal.
- [ ] Prove a loopback-only issuer simulation is not reachable through the runner's non-loopback interface.
- [ ] Prove Gateway login responses remain non-cacheable and bounded when the Session dependency is unavailable.
- [ ] Retain exact Gateway/Canary/OTClient revision pins and non-secret machine-readable evidence.
- [ ] Keep classification bounded to PRODUCTION_LIKE_PROVEN; real production private-network/TLS/secret-manager/deployed-revision evidence remains UNKNOWN.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-23T18:30:00+02:00
head: 5bd9d91c570af127edab51a2c3509e0f37b6a30e
branch: test/CAN-20260723-native-auth-production-like-boundary
pr: null
status: implementing
context_routes:
  - universal-e2e
  - agent-governance
  - cross-repo
owned_paths:
  - docs/agents/tasks/active/CAN-20260723-native-auth-production-like-boundary.md
  - tests/e2e/test_native_auth_production_like_boundary.py
  - .github/workflows/native-auth-production-like-validation.yml
changed_paths:
  - docs/agents/tasks/active/CAN-20260723-native-auth-production-like-boundary.md
proven:
  - Hardened exact-revision OTClient -> Gateway -> Canary physical E2E already passed in run 30021347231.
  - The remaining real production gate cannot be proven from GitHub repository state alone.
derived:
  - A disposable TLS/rotation simulation can reduce deployment risk but cannot promote evidence to PRODUCTION_PROVEN.
unknown:
  - real production Gateway -> Canary network/firewall topology
  - real production TLS certificate/hostname/trust termination
  - real production secret-manager current/previous credential state
  - real deployed production Gateway and Canary revisions
conflicts: []
first_failure:
  marker: validation-not-yet-run
  evidence: production-like boundary harness is being implemented
validation: []
blockers: []
next_action: Implement and run the validation-only production-like Gateway -> Session boundary simulation on exact merged hardened revisions.
```
