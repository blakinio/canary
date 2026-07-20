# OAM-024 — Sanctions revalidation

## Final disposition

```text
sanctions → ADAPT
```

## Immutable task-start baselines

- Canary: `3fe0130a408d201d0ca846f86a37b0ab20479932`
- Otheryn: `bcc3e9f7e3e704f3c012bda8693648d52741630f`
- fresh upstream Canary: `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`
- maintained OTClient: `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`

Canonical registry record: `docs/agents/real-tibia/registry/modules/sanctions.yaml`.

Canonical production boundary:

```text
src/creatures/players/management/ban.*
```

Canonical dependency: completed OAM-004 `database-connection`.

## Fresh preflight and ownership

The durable OAM program recorded OAM-001..OAM-023 complete, OAM-023 archived and OAM-024 not started before this task. Task-start open-PR and active-task audits found no writer overlapping canonical `ban.*` or the OAM-024 governance paths. Open Canary work was independently owned OTBM/E2E, MyAAC closeout, shared-state/economy evidence audit and authenticated-session transport validation. Otheryn, maintained OTClient and fresh upstream had no open PRs at task start.

`sanctions` was selected as the smallest dependency-valid canonical package after comparing current registry dependencies and ownership. Broader `chat-communication`, `cyclopedia`, `guilds` and `creature-definitions` packages were not selected; packages depending on unfinished `cyclopedia` were not dependency-valid; `wheel-of-destiny` remained separately owned.

## Evidence-driven classification

At immutable task-start baselines, legacy, target and fresh upstream shared canonical blobs:

- `ban.cpp`: `ca4c11ea98d6a8f4b6281f0bb5e84d742ff21ecc`
- `ban.hpp`: `48086b3efef370b2c0e1fab8f85513a95e47dcad`

Blob identity was supporting evidence only and was not accepted as sufficient `REUSE` proof.

Semantic review confirmed the narrow sanctions core and its consumers:

- connection-attempt throttling is consumed at socket accept;
- IP-ban lookup is consumed by login protocol;
- account-ban and namelock lookup are consumed by game login;
- active/permanent account bans remain enforcement reads;
- expired account bans are transferred from `account_bans` to `account_ban_history`.

Relevant target and legacy history did not identify a stronger independent donor for canonical `ban.*`. The reviewed target/upstream/legacy account-ban expiry path instead exposed a bounded durability defect: history `INSERT` and active-ban `DELETE` were queued as two independent asynchronous database tasks. A failure between them had no atomic rollback boundary.

Because completed OAM-004 already provides the target `DBTransaction` primitive, the smallest valid disposition is `ADAPT`, not broad rewrite and not unconditional `REUSE`.

## Accepted target adaptation

Otheryn PR #48 changes only the bounded account-ban expiry handoff plus focused integration proof:

- `IOBan::isAccountBanned` performs the account-ban lookup under `SELECT ... FOR UPDATE` inside one `DBTransaction`;
- active/permanent bans preserve existing read/enforcement behavior;
- expired-ban history insertion and active-row deletion commit together;
- either write failure rolls back the pair, leaving the expired active row available for retry;
- IP-ban behavior remains unchanged.

No maintained OTClient, protocol, authentication, schema, map/OTBM, asset or deployment change is included.

Final target head:

```text
58ba19e0affe75f47c4185c41327880f8403503b
```

Final target diff has exactly four paths:

```text
docs/oam-024-sanctions-adapt.md
src/creatures/players/management/ban.cpp
tests/integration/database/CMakeLists.txt
tests/integration/database/sanctions_it.cpp
```

Exact-head gates:

```text
autofix.ci #153
run 29734614481
SUCCESS

CI #179
run 29734614607
SUCCESS

Required #160
run 29734614503
SUCCESS
```

Linux debug proof:

```text
CTest: 406/406 PASS
SanctionsRepositoryDBTest: 3/3 PASS
```

Focused cases prove active-ban preservation, exactly-once expiry archival and rollback of the history insert when the active-ban delete is forced to fail.

Test-log artifact:

```text
8458101363
```

Digest:

```text
sha256:97b9aeb5e93bac69461720671ee58bfe5742fd20df2710b139d0aa2298cd30fc
```

Before target merge:

- comments: 0
- reviews: 0
- review threads: 0
- Otheryn `main` drift from immutable target baseline: 0

PR #48 merged by expected-head squash as:

```text
65d364b216843db27e84a19a673eee4e6d766c68
```

## Explicit non-claims

OAM-024 does not claim exhaustive sanction enforcement at every entry point, generic account-authentication security, protocol compatibility, distributed/multi-database sanctions replication, moderation policy, generic security analytics, AI investigation, PvP skull/frag parity, physical-client sanctions E2E closure, generic persistence redesign, or changes to maintained OTClient, maps, OTBM, `items.otb`, assets, schema or deployment.

OAM-024 preserves the known OAM-004 limitation that player SQL persistence and later KV durability are not atomic; this sanctions adaptation does not touch that cross-store boundary.
