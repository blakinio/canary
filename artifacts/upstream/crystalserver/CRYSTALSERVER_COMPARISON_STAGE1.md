# CrystalServer Comparison — Stage 1 Inventory

Analysis date: 2026-07-13  
Program: `CAN-PROGRAM-CRYSTALSERVER-COMPARISON`  
Task: `CAN-20260713-crystalserver-comparison-inventory`  
Functional changes: **none**

## 1. Baselines

| Repository | Role | `main` SHA | Declared version | Client protocol | Access |
|---|---|---|---|---:|---|
| `blakinio/canary` | target | `360d79ebad5802edd4d89e99d0f210ab19b36b60` | server `3.6.1` | `1525` / 15.25 | write only through task branch and PR |
| `zimbadev/crystalserver` | comparison | `fc0d53b9f9965463b6082c07e6d3d482294541a7` | software `4.1.9` | `1525` / 15.25 | read-only |
| `opentibiabr/canary` | reference | `9365c1c4aa63529b9ff757f53737274894c02b8e` | not used as a version claim in Stage 1 | verify per task | read-only |

Last analyzed CrystalServer commit: `fc0d53b9f9965463b6082c07e6d3d482294541a7`.

## 2. Repository state and limitations

The GitHub connection confirmed write permission only for `blakinio/canary`; both comparison repositories expose read-only permission.

The mandatory governance documents were reviewed at the Canary baseline: `AGENTS.md`, `docs/agents/README.md`, `ACTIVE_WORK.md`, `MODULE_CATALOG.md`, `REPOSITORY_MAP.md`, `KNOWN_RISKS.md`, `BUILD_TEST_MATRIX.md`, and `CROSS_REPO_CONTRACTS.md`.

Live open PRs and their changed-file lists were inspected. Current material areas include instances (#289), achievement remediation (#264 and #288), Forge (#283/#284), Wheel staging (#279), the universal E2E platform (#245), and the paused Cyclopedia E2E experiment (#224). `src/game/game.cpp` and `src/game/game.hpp` currently overlap PR #289.

A local checkout/worktree was unavailable. The shell command:

```text
git ls-remote https://github.com/blakinio/canary.git refs/heads/main
```

failed with:

```text
fatal: unable to access 'https://github.com/blakinio/canary.git/': Could not resolve host: github.com
```

Consequently, Stage 1 does not claim local execution of `git status --short --branch`, `git branch -vv`, `git remote -v`, `git worktree list`, `python tools/agents/task_ownership.py`, or `git diff --check`. GitHub API state is used for baselines, open PRs, changed paths, source, and commit diffs.

## 3. Shared lineage and architectural divergence

The repositories retain strongly corresponding Canary engine paths and protocol concepts, and both current baselines declare client protocol 15.25. This structural correspondence supports symbol-level comparison, but it does not prove behavioral equivalence.

Current `blakinio/canary` also contains repository-specific governance and architecture not assumed by CrystalServer patches, including agent ownership records, cross-repository contract gates, multichannel/session work, instance infrastructure, and deterministic validation tooling. CrystalServer contains its own branding, content layout, and bundled feature decisions. Therefore, broad file replacement or cherry-picking would risk removing later Canary behavior and project-specific contracts.

No claim is made here about which project is globally newer or better.

## 4. Screening coverage

- `fix` commit search: 50 returned hits screened by metadata/message.
- `crash` commit search: 30 returned hits screened by metadata/message.
- The two result sets overlap and were not treated as 80 unique commits.
- Ten unique candidates had their CrystalServer diff opened and corresponding current Canary source inspected.
- Four additional commits remain in the deferred, unverified backlog.

Commit messages were used only to discover candidates. Classifications below are based on opened diffs and current Canary code.

## 5. Classification counts

| Status | Count |
|---|---:|
| `ALREADY_PRESENT` | 2 |
| `CANARY_SUPERIOR` | 1 |
| `VALID_FIX_MISSING` | 1 |
| `PARTIAL_VALUE` | 3 |
| `CLIENT_COUPLED` | 2 |
| `CONTENT_ONLY` | 0 |
| `UNVERIFIED` | 0 |
| `DANGEROUS` | 1 |
| `REJECTED` | 0 |
| **Total deep-reviewed candidates** | **10** |

Deferred backlog entries are not included in these counts.

## 6. Top ten candidates

### CS-001 — zero light level causes division by zero

- CrystalServer commit: `a7350014528002fb27ed64d260a96d28a580d41a`
- Author/date: `jprzimba`, 2026-07-12
- Related PR: CrystalServer #822
- Files/symbols: `src/creatures/combat/condition.cpp`; `ConditionLight::startCondition`, `ConditionLight::unserializeProp`
- CrystalServer change: clamp a zero light level before interval division and while deserializing.
- Current Canary evidence: `ConditionLight::startCondition` still calculates `ticks / lightInfo.level`; setter and `addCondition` paths clamp, but deserialization accepts zero unchanged.
- Exact problem: a persisted or otherwise constructed zero light level can reach integer division by zero.
- Status: `VALID_FIX_MISSING`
- Risk: high
- Dependencies: none identified; implementation still requires current ownership and C++ test/build validation.
- Proposed test: deserialize a light condition with level zero, start it, verify no division fault and a normalized level/interval; add a constructor-path boundary test if reachable.
- Decision: highest-priority implementation candidate, but not changed in Stage 1.

### CS-002 — NPC shop-window iterator invalidation

- CrystalServer commit: `0c0f1acafd77a86fb5ce56fe768ff6d98d100c35`
- Author/date: `jprzimba`, 2026-07-11
- Related PR: CrystalServer #821
- Files/symbols: `src/creatures/npcs/npc.cpp`; `Npc::closeAllShopWindows`
- CrystalServer change: copy GUIDs to a vector before callbacks that may mutate `shopPlayers`.
- Current Canary evidence: Canary increments the iterator before resolving the player and calling `closeShopWindow`, then clears remaining entries.
- Status: `ALREADY_PRESENT`
- Risk: medium
- Proposed test: closing all shop windows where callbacks erase current entries leaves the map empty and visits every player once.
- Decision: no code adaptation.

### CS-003 — KV shared Lua userdata leak

- CrystalServer commit: `90ac0eb7d2ba0a88476881c972d9de83fbbcb3e8`
- Author/date: `matzinhozz`, 2026-06-26
- Related PR: CrystalServer #799
- Files/symbols: `src/lua/functions/core/libs/kv_functions.cpp`; KV metatable registration and scoped userdata.
- CrystalServer change: replace non-owning class registration with shared-class registration so `__gc` releases `std::shared_ptr<KV>`.
- Current Canary evidence: Canary already uses typed `Lua::registerSharedClass<KV>` and `Lua::pushSharedUserdata<KV>`.
- Status: `CANARY_SUPERIOR`
- Risk: high
- Proposed test: repeated scoped KV creation plus Lua GC does not retain strong references.
- Decision: preserve Canary implementation; no adaptation.

### CS-004 — `Container::replaceThing` null and bounds validation

- CrystalServer commit: `dcb4f00ffd55ede2399c979eee3b7fe6e7e0ee6e`
- Author/date: `jprzimba`, 2025-07-17
- Related PR: CrystalServer #292
- Files/symbols: `src/items/containers/container.cpp`; `Container::replaceThing`
- CrystalServer change: reject null input and out-of-range index before dereference/access.
- Current Canary evidence: both checks already precede item conversion and replacement.
- Status: `ALREADY_PRESENT`
- Risk: high
- Proposed test: null thing and `index == size()` are no-ops without cache/weight/parent changes.
- Decision: no code adaptation.

### CS-005 — direct player GUID index

- CrystalServer commit: `fc0d53b9f9965463b6082c07e6d3d482294541a7`
- Author/date: `jprzimba`, 2026-07-12
- Related PR: CrystalServer #819
- Files/symbols: `src/game/game.cpp`, `src/game/game.hpp`; `Game::getPlayerByGUID`, `addPlayer`, `removePlayer`
- CrystalServer change: maintain a concurrent GUID-to-player map instead of linearly scanning online players.
- Current Canary evidence: current `getPlayerByGUID` still scans the player map.
- Exact value: plausible O(1) lookup improvement; no correctness defect or measured Canary bottleneck has been demonstrated.
- Status: `PARTIAL_VALUE`
- Risk: medium
- Dependencies: lifecycle consistency, concurrency semantics, benchmark; current path ownership overlaps open PR #289.
- Proposed tests: add/remove/relogin index consistency, duplicate GUID behavior, offline fallback, and a representative benchmark against realistic online-player counts.
- Decision: defer until overlap clears and measurements justify added state.

### CS-006 — shell construction in `FS.mkdir`

- CrystalServer commit: `891685169745e46f665069edcc35847f0704aa21`
- Author/date: `jprzimba`, 2026-07-10
- Related PR: CrystalServer #816
- Files/symbols: `data/libs/functions/fs.lua`; `FS.mkdir`
- CrystalServer change: add path validation before constructing a platform-specific shell command.
- Current Canary evidence: Canary concatenates the path into `os.execute('mkdir "' .. path .. '"')` without validation.
- Exact value: the unsafe construction pattern exists; exploitability depends on call-site trust boundaries not yet inventoried.
- Status: `PARTIAL_VALUE`
- Risk: high
- Dependencies: all call sites, supported path semantics, cross-platform behavior, safer native filesystem alternatives.
- Proposed tests: reject command separators, quotes, control characters, expansions, traversal where forbidden, and preserve valid Windows/POSIX/Unicode paths.
- Decision: separate security task; do not copy CrystalServer's denylist or continue using a shell merely because it is validated.

### CS-007 — executable `table.unserialize`

- CrystalServer commit: `891685169745e46f665069edcc35847f0704aa21`
- Author/date: `jprzimba`, 2026-07-10
- Related PR: CrystalServer #816
- Files/symbols: `data/libs/functions/tables.lua`; `table.unserialize`
- CrystalServer change: replace `loadstring` with a bespoke parser.
- Current Canary evidence: Canary evaluates `loadstring("return " .. str)()`.
- Exact value: dynamic execution is confirmed; attacker control and compatibility requirements are not yet proven.
- Status: `PARTIAL_VALUE`
- Risk: high
- Dependencies: complete call-site inventory and serialized-value compatibility corpus.
- Proposed tests: round-trip all values produced by `table.serialize`; reject function calls, environment access, trailing code, malformed nesting, oversized/deep input, and ambiguous keys.
- Decision: separate task; do not transplant the unverified upstream parser.

### CS-008 — Market offer limits intended to prevent client crash

- CrystalServer commit: `34cbec0c34325619ef23c5d12c940b7b1c276975`
- Author/date: `jprzimba`, 2026-07-01
- Related PR: CrystalServer #808
- Files/symbols: `src/game/game.cpp`, `src/io/iomarket.cpp`, `src/io/iomarket.hpp`; offer creation and queries.
- CrystalServer change: impose per-player/per-item limits and SQL result limits using constants 1000, 700, and 1500.
- Current Canary evidence: current `IOMarket` does not expose those limits or count helpers.
- Missing evidence: exact protocol/client capacity, pagination semantics, official limits, race behavior between count and insert, and why the selected constants are correct.
- Status: `CLIENT_COUPLED`
- Risk: high
- Dependencies: maintained OTClient source/tests, DB concurrency tests, protocol 15.25 contract, physical-client E2E.
- Proposed tests: oversized server response boundaries, deterministic client decode, concurrent offer creation, exact limit behavior, and query ordering/pagination.
- Decision: no automatic implementation.

### CS-009 — disconnect-message reason byte

- CrystalServer commit: `cfc0c5c496eae53f1f33a07f563068f44914ddbb`
- Author/date: `jprzimba`, 2026-06-15
- Related PR: CrystalServer #766
- Files/symbols: `src/server/network/protocol/protocolgame.cpp/.hpp`, new disconnect-reason enum; `ProtocolGame::disconnectClient`
- CrystalServer change: append a reason byte after the disconnect message and use different reason values.
- Current Canary evidence: current declaration accepts only a message and has no equivalent enum.
- Missing evidence: whether each supported client/profile expects the byte, field width/order, capability/version gate, old-client behavior, and current maintained OTClient parsing.
- Status: `CLIENT_COUPLED`
- Risk: high
- Dependencies: Canary protocol profiles, maintained OTClient, cross-repo contract record, integration test.
- Proposed tests: byte-exact packets for each supported profile and reason; real-client invalid credentials/outdated protocol/duplicate-session flows.
- Decision: no automatic implementation.

### CS-010 — parent-null handling during creature removal

- CrystalServer commit: `ffe4db548371c44ce01dfc280af0209318272292`
- Author/date: `jprzimba`, 2025-11-27
- Related PR: CrystalServer #513
- Files/symbols: `src/game/game.cpp`; `Game::removeCreature`
- CrystalServer change: return `false` if `creature->getParent()` is null before `postRemoveNotification`.
- Current Canary evidence: Canary dereferences the parent after optional tile removal.
- Safety problem in upstream patch: the null check occurs after tile-side removal and spectator notifications but before `afterCreatureZoneChange`, `removeList`, `setRemoved`, instance unregister, summon cleanup, and logout cleanup. Returning there can leave partially removed state.
- Status: `DANGEROUS`
- Risk: critical
- Dependencies: proof of how parent becomes null, lifecycle invariant, cleanup ordering, instance/multichannel interactions, focused integration tests.
- Proposed tests: parent-null before removal, parent reset during tile removal, repeated removal, summon/player/NPC/monster cases, list/index/instance-owner cleanup, and spectator notifications.
- Decision: investigate the defect signal, but reject direct transplantation of the upstream patch.

## 7. Candidates already present in Canary

- `CS-002`: safe NPC shop iteration is already achieved through iterator pre-increment.
- `CS-004`: null and bounds checks already protect `Container::replaceThing`.

These are closed evidence, not implementation tasks.

## 8. Cases where Canary is superior

- `CS-003`: current Canary uses typed shared-class registration and matching shared-userdata APIs for KV. The CrystalServer commit repairs an older registration pattern that is not present at the Canary baseline.

## 9. Client-dependent candidates

- `CS-008`: Market limits and response sizing.
- `CS-009`: disconnect reason byte.

Both require exact maintained-client behavior, profile/version gating, server tests, client tests, and physical integration. Matching protocol version numbers alone do not prove matching payload contracts.

## 10. Dangerous or unverified candidates

- `CS-010` is dangerous to copy because the proposed early return can preserve partial removal side effects.
- Deferred `9e046413...` item-definition cleanup remains unverified against current Canary item XML/ID contracts.
- Deferred `809633b1...` admin item-count limit lacks a justified bound and current parsing/resource evidence.
- Deferred `55db69b7...` corpse/reward-parent checks require current symbol/state analysis.
- Deferred `6bda45e7...` broad spell-formula rewrite requires official formula evidence and is too wide for automatic adaptation.

## 11. Proposed task and PR queue

1. **CS-001 — ConditionLight zero-level crash**  
   Test-first C++ task; smallest normalization fix; focused condition tests and required builds.
2. **CS-006 — FS.mkdir security boundary**  
   Independent Lua/security task; inventory call sites and prefer non-shell filesystem behavior.
3. **CS-007 — table.unserialize security and compatibility**  
   Independent task; build corpus first and replace execution only with proven compatibility.
4. **CS-010 — removeCreature lifecycle invariant**  
   Reproduction/design task; do not start with the CrystalServer patch.
5. **CS-008 and CS-009 — client contracts**  
   Separate cross-repo tasks after the universal E2E platform is usable.
6. **CS-005 — GUID lookup benchmark**  
   Start only after PR #289 or its successor clears overlapping paths.

Every item requires a new task record, branch, worktree, early draft PR, fresh baselines, exact ownership claims, and current-head CI.

## 12. Uncertainty and missing evidence

- The commit-search results are discovery sets, not a complete audit of all CrystalServer history.
- Search-hit overlap was not fully deduplicated; only ten opened, unique diffs are counted as deep review.
- Related CrystalServer issue/PR discussions were inferred from commit-linked PR numbers; full discussion evidence was not available for every candidate.
- No local Canary build or test was run in Stage 1 because no checkout/worktree was available.
- No runtime reproduction has yet been executed. `CS-001` is classified from a deterministic code path: current source divides by a field that current deserialization can set to zero.
- `FS.mkdir` and `table.unserialize` reachability from untrusted input remains unknown.
- Exact maintained OTClient Market and disconnect contracts remain unknown.
- Current Canary item XML state for the deferred duplicate-definition commit remains unverified.

The program must downgrade or upgrade classifications when new current-main, test, runtime, client, or discussion evidence appears.
