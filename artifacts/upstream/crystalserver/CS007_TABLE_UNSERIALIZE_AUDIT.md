# CS-007 `table.unserialize` audit

- Target: `blakinio/canary` at task baseline `06f8ba4464d6a18ad48445737444bab5b3a2efcb`.
- Donor evidence: `zimbadev/crystalserver` commit `891685169745e46f665069edcc35847f0704aa21`.
- Tracked files scanned: **6894**; text files: **6858**.
- This inventory is deterministic source evidence, not runtime-reachability proof.

## Executed compatibility/security probe

```text
ROUNDTRIP 1 plain-string PASS "\"plain text\""
ROUNDTRIP 2 whitespace-string PASS "\"spaces and\\9tabs\\\
newlines\""
ROUNDTRIP 3 escaped-string PASS "\"quotes: 'single' and \\\"double\\\" and \\\\ slash\""
ROUNDTRIP 4 zero PASS "0"
ROUNDTRIP 5 negative-float PASS "-12.5"
ROUNDTRIP 6 exponent-number PASS "1250000"
ROUNDTRIP 7 boolean-true PASS "true"
ROUNDTRIP 8 boolean-false FAIL "true"
ROUNDTRIP 9 mixed-table FAIL "{[1] = \"array\",[3] = true,[true] = {[\"number\"] = -4.5,[\"nested\"] = \"ok\",},[\"name\"] = \"value with spaces\",[7.25] = \"numeric-key\",}"
EXPLOIT_EXECUTED true
```

The exploit result proves whether the current helper evaluates an arbitrary Lua expression; it does not by itself prove an attacker-controlled production path.

Round-trip failures are retained as evidence. They may be defects in `table.serialize` rather than `table.unserialize` and must not be silently bundled into CS-007.

## `table.unserialize` definitions and calls

Occurrences: **6**

### `.github/workflows/audit-cs007-table-unserialize-v2.yml:78`

```text
74:           end
75:
76:           for i, value in ipairs(cases) do
77:             local encoded = table.serialize(value)
78:             local decoded = table.unserialize(encoded)
79:             assert(equal(value, decoded), "round-trip failed for case " .. i .. ": " .. encoded)
80:             io.write(string.format("ROUNDTRIP %d %s %q\n", i, type(value), encoded))
81:           end
82:
```

### `.github/workflows/audit-cs007-table-unserialize-v2.yml:85`

```text
81:           end
82:
83:           _G.__cs007_executed = false
84:           local exploit = '(function() _G.__cs007_executed = true return { ["executed"] = true } end)()'
85:           local decoded = table.unserialize(exploit)
86:           assert(_G.__cs007_executed == true, "current helper did not execute exploit")
87:           assert(type(decoded) == "table" and decoded.executed == true)
88:           io.write("EXPLOIT_EXECUTED true\n")
89:           LUA
```

### `.github/workflows/audit-cs007-table-unserialize.yml:78`

```text
74:           end
75:
76:           for i, value in ipairs(cases) do
77:             local encoded = table.serialize(value)
78:             local decoded = table.unserialize(encoded)
79:             assert(equal(value, decoded), "round-trip failed for case " .. i .. ": " .. encoded)
80:             io.write(string.format("ROUNDTRIP %d %s %q\n", i, type(value), encoded))
81:           end
82:
```

### `.github/workflows/audit-cs007-table-unserialize.yml:85`

```text
81:           end
82:
83:           _G.__cs007_executed = false
84:           local exploit = '(function() _G.__cs007_executed = true return { ["executed"] = true } end)()'
85:           local decoded = table.unserialize(exploit)
86:           assert(_G.__cs007_executed == true, "current helper did not execute exploit")
87:           assert(type(decoded) == "table" and decoded.executed == true)
88:           io.write("EXPLOIT_EXECUTED true\n")
89:           LUA
```

### `data/libs/functions/tables.lua:101`

```text
97: 		error("Can not serialize value of type '" .. t .. "'.")
98: 	end
99: end
100:
101: function table.unserialize(str)
102: 	return loadstring("return " .. str)()
103: end
104:
105: function table.shallowCopy(oldTable)
```

### `docs/agents/tasks/active/CAN-20260714-table-unserialize-security.md:45`

```text
41:   - existing `table.serialize` canonical output
42:   - existing standalone Lua test workflow
43: public_interfaces:
44:   - "table.serialize(value) -> string"
45:   - "table.unserialize(serialized) -> value"
46: cross_repo_tasks: []
47: ---
48:
49: # Goal
```

## `table.serialize` definitions and calls

Occurrences: **6**

### `.github/workflows/audit-cs007-table-unserialize-v2.yml:77`

```text
73:             return true
74:           end
75:
76:           for i, value in ipairs(cases) do
77:             local encoded = table.serialize(value)
78:             local decoded = table.unserialize(encoded)
79:             assert(equal(value, decoded), "round-trip failed for case " .. i .. ": " .. encoded)
80:             io.write(string.format("ROUNDTRIP %d %s %q\n", i, type(value), encoded))
81:           end
```

### `.github/workflows/audit-cs007-table-unserialize.yml:77`

```text
73:             return true
74:           end
75:
76:           for i, value in ipairs(cases) do
77:             local encoded = table.serialize(value)
78:             local decoded = table.unserialize(encoded)
79:             assert(equal(value, decoded), "round-trip failed for case " .. i .. ": " .. encoded)
80:             io.write(string.format("ROUNDTRIP %d %s %q\n", i, type(value), encoded))
81:           end
```

### `data/libs/functions/tables.lua:69`

```text
65:
66: 	return newlist
67: end
68:
69: function table.serialize(x, recur)
70: 	local t = type(x)
71: 	recur = recur or {}
72:
73: 	if t == nil then
```

### `data/libs/functions/tables.lua:91`

```text
87: 		table.append(recur, x)
88:
89: 		local s = "{"
90: 		for k, v in pairs(x) do
91: 			s = s .. "[" .. table.serialize(k, recur) .. "]"
92: 			s = s .. " = " .. table.serialize(v, recur) .. ","
93: 		end
94: 		s = s .. "}"
95: 		return s
```

### `data/libs/functions/tables.lua:92`

```text
88:
89: 		local s = "{"
90: 		for k, v in pairs(x) do
91: 			s = s .. "[" .. table.serialize(k, recur) .. "]"
92: 			s = s .. " = " .. table.serialize(v, recur) .. ","
93: 		end
94: 		s = s .. "}"
95: 		return s
96: 	else
```

### `docs/agents/tasks/active/CAN-20260714-table-unserialize-security.md:44`

```text
40: reuses:
41:   - existing `table.serialize` canonical output
42:   - existing standalone Lua test workflow
43: public_interfaces:
44:   - "table.serialize(value) -> string"
45:   - "table.unserialize(serialized) -> value"
46: cross_repo_tasks: []
47: ---
48:
```

## Direct `loadstring` occurrences

Occurrences: **6**

### `artifacts/upstream/crystalserver/CRYSTALSERVER_COMPARISON_STAGE1.md:168`

```text
164: - Author/date: `jprzimba`, 2026-07-10
165: - Related PR: CrystalServer #816
166: - Files/symbols: `data/libs/functions/tables.lua`; `table.unserialize`
167: - CrystalServer change: replace `loadstring` with a bespoke parser.
168: - Current Canary evidence: Canary evaluates `loadstring("return " .. str)()`.
169: - Exact value: dynamic execution is confirmed; attacker control and compatibility requirements are not yet proven.
170: - Status: `PARTIAL_VALUE`
171: - Risk: high
172: - Dependencies: complete call-site inventory and serialized-value compatibility corpus.
```

### `artifacts/upstream/crystalserver/CS006_FS_MKDIR_AUDIT.md:392`

```text
388: | `artifacts/upstream/crystalserver/CRYSTALSERVER_COMPARISON_STAGE1.md` | 151 | `- Files/symbols: \`data/libs/functions/fs.lua\`; \`FS.mkdir\`` |
389: | `artifacts/upstream/crystalserver/CRYSTALSERVER_COMPARISON_STAGE1.md` | 153 | `- Current Canary evidence: Canary concatenates the path into \`os.execute('mkdir "' .. path .. '"')\` without validation.` |
390: | `artifacts/upstream/crystalserver/CRYSTALSERVER_COMPARISON_STAGE1.md` | 251 | `2. **CS-006 — FS.mkdir security boundary**` |
391: | `artifacts/upstream/crystalserver/CRYSTALSERVER_COMPARISON_STAGE1.md` | 271 | `- \`FS.mkdir\` and \`table.unserialize\` reachability from untrusted input remains unknown.` |
392: | `artifacts/upstream/crystalserver/crystalserver_comparison_stage1.json` | 1 | `{"schema":"canary-crystalserver-comparison-v1","generated_at":"2026-07-13T21:01:05Z","analysis_date":"2026-07-13","stage":1,"functional_changes":false,"program_id":"CAN-PROGRAM-CRYSTALSERVER-COMPARISON","task_id":"CAN-20260713-crystalserver-comparison-inventory","baselines":{"target":{"repository":"blakinio/canary","branch":"main","sha":"360d79ebad5802edd4d89e99d0f210ab19b36b60","server_version":"3.6.1","client_protocol":1525,"access":"write-via-task-branch-and-pr"},"comparison":{"repository":"zimbadev/crystalserver","branch":"main","sha":"fc0d53b9f9965463b6082c07e6d3d482294541a7","server_version":"4.1.9","client_protocol":1525,"access":"read-only"},"reference":{"repository":"opentibiabr/canary","branch":"main","sha":"9365c1c4aa63529b9ff757f53737274894c02b8e","server_version":null,"client_protocol":null,"access":"read-only"}},"last_analyzed_crystal_commit":"fc0d53b9f9965463b6082c07e6d3d482294541a7","screening":{"queries":[{"term":"fix","hits_returned":50},{"term":"crash","hits_returned":30}],"overlap_not_fully_deduplicated":true,"deep_reviewed_unique":10,"deferred_unverified":4,"method":"Open CrystalServer diff, inspect corresponding current Canary source, then classify behaviorally."},"status_counts":{"ALREADY_PRESENT":2,"CANARY_SUPERIOR":1,"VALID_FIX_MISSING":1,"PARTIAL_VALUE":3,"CLIENT_COUPLED":2,"CONTENT_ONLY":0,"UNVERIFIED":0,"DANGEROUS":1,"REJECTED":0},"candidates":[{"id":"CS-001","repository":"zimbadev/crystalserver","crystal_commit":"a7350014528002fb27ed64d260a96d28a580d41a","author":"jprzimba","date":"2026-07-12","related_pr":822,"files":["src/creatures/combat/condition.cpp"],"symbols":["ConditionLight::startCondition","ConditionLight::unserializeProp"],"problem":"A zero light level reaches ticks / lightInfo.level and can cause integer division by zero.","evidence":["CrystalServer clamps the divisor and deserialized level to at least one.","Current Canary startCondition divides directly by lightInfo.level.","Current Canary deserialization assigns a persisted zero without normalization.","Other Canary mutation paths already clamp, showing a partial invariant."],"canary_locations":["src/creatures/combat/condition.cpp:ConditionLight::startCondition","src/creatures/combat/condition.cpp:ConditionLight::addCondition","src/creatures/combat/condition.cpp:ConditionLight::setParam","src/creatures/combat/condition.cpp:ConditionLight::unserializeProp"],"status":"VALID_FIX_MISSING","risk":"high","dependencies":["fresh ownership check","focused C++ regression test","required C++ build and CI"],"proposed_tests":["Deserialize CONDITIONATTR_LIGHTLEVEL=0 and start the condition without a division fault.","Verify normalized level and a valid lightChangeInterval.","Cover any reachable constructor or script path that can supply zero."],"decision":"Create a separate test-first implementation task after Stage 1 merges.","rationale":"The fault is deterministic from current source and the bounded guard is absent.","provenance_used":"Behavioral idea only: normalize invalid light level at persistence and division boundaries."},{"id":"CS-002","repository":"zimbadev/crystalserver","crystal_commit":"0c0f1acafd77a86fb5ce56fe768ff6d98d100c35","author":"jprzimba","date":"2026-07-11","related_pr":821,"files":["src/creatures/npcs/npc.cpp"],"symbols":["Npc::closeAllShopWindows"],"problem":"Callbacks while closing NPC shops can erase entries and invalidate iteration.","evidence":["CrystalServer snapshots GUIDs before callbacks.","Current Canary increments the iterator before calling closeShopWindow, then clears leftovers."],"canary_locations":["src/creatures/npcs/npc.cpp:Npc::closeAllShopWindows"],"status":"ALREADY_PRESENT","risk":"medium","dependencies":[],"proposed_tests":["Callbacks erase current entries while every shop player is visited exactly once and the map ends empty."],"decision":"No implementation.","rationale":"Current Canary already avoids using an iterator after the mutating callback.","provenance_used":"No code adapted."},{"id":"CS-003","repository":"zimbadev/crystalserver","crystal_commit":"90ac0eb7d2ba0a88476881c972d9de83fbbcb3e8","author":"matzinhozz","date":"2026-06-26","related_pr":799,"files":["src/lua/functions/core/libs/kv_functions.cpp"],"symbols":["KVFunctions::init","Lua::registerSharedClass","Lua::pushSharedUserdata"],"problem":"Shared KV userdata leaks if the metatable lacks shared-pointer garbage collection.","evidence":["CrystalServer changed non-shared class registration to shared registration.","Current Canary already uses typed registerSharedClass<KV> and pushSharedUserdata<KV>."],"canary_locations":["src/lua/functions/core/libs/kv_functions.cpp:KVFunctions::init","src/lua/functions/core/libs/kv_functions.cpp:KVFunctions::luaKVScoped"],"status":"CANARY_SUPERIOR","risk":"high","dependencies":[],"proposed_tests":["Repeated scoped KV creation and Lua GC releases all Lua-held strong references."],"decision":"Preserve current Canary implementation.","rationale":"Canary already applies the safe typed shared-userdata pattern.","provenance_used":"No code adapted."},{"id":"CS-004","repository":"zimbadev/crystalserver","crystal_commit":"dcb4f00ffd55ede2399c979eee3b7fe6e7e0ee6e","author":"jprzimba","date":"2025-07-17","related_pr":292,"files":["src/items/containers/container.cpp"],"symbols":["Container::replaceThing"],"problem":"Null input or an out-of-range replacement index can cause invalid access.","evidence":["CrystalServer adds null and bounds guards.","Current Canary already performs both guards before item conversion and replacement."],"canary_locations":["src/items/containers/container.cpp:Container::replaceThing"],"status":"ALREADY_PRESENT","risk":"high","dependencies":[],"proposed_tests":["Null thing and index equal to size are no-ops with unchanged cache, weight, and parents."],"decision":"No implementation.","rationale":"Equivalent validation is already present.","provenance_used":"No code adapted."},{"id":"CS-005","repository":"zimbadev/crystalserver","crystal_commit":"fc0d53b9f9965463b6082c07e6d3d482294541a7","author":"jprzimba","date":"2026-07-12","related_pr":819,"files":["src/game/game.cpp","src/game/game.hpp"],"symbols":["Game::getPlayerByGUID","Game::addPlayer","Game::removePlayer"],"problem":"Online player GUID lookup is linear in the number of players.","evidence":["CrystalServer adds a GUID index maintained on add/remove.","Current Canary still scans the online player map.","No current Canary performance regression or benchmark was provided."],"canary_locations":["src/game/game.cpp:Game::getPlayerByGUID"],"status":"PARTIAL_VALUE","risk":"medium","dependencies":["benchmark","index lifecycle tests","concurrency review","resolve overlap with open PR #289"],"proposed_tests":["Add/remove/relogin consistency and duplicate GUID behavior.","Offline fallback remains unchanged.","Benchmark representative online-player counts."],"decision":"Defer until path ownership clears and measurements justify the index.","rationale":"The optimization is plausible but not a proven bug fix and adds synchronized state.","provenance_used":"Candidate design signal only."},{"id":"CS-006","repository":"zimbadev/crystalserver","crystal_commit":"891685169745e46f665069edcc35847f0704aa21","author":"jprzimba","date":"2026-07-10","related_pr":816,"files":["data/libs/functions/fs.lua"],"symbols":["FS.mkdir"],"problem":"A path is concatenated into a shell command without validation.","evidence":["Current Canary uses os.execute with a quoted but unsanitized path.","CrystalServer adds a denylist but still invokes a shell.","Call-site attacker control is not yet established."],"canary_locations":["data/libs/functions/fs.lua:FS.mkdir","data/libs/functions/fs.lua:FS.mkdir_p"],"status":"PARTIAL_VALUE","risk":"high","dependencies":["complete call-site inventory","supported path semantics","cross-platform safe filesystem API"],"proposed_tests":["Reject quotes, separators, substitutions, control characters, and other command syntax.","Preserve valid Windows, POSIX, relative, absolute, and Unicode paths as required.","Prove no shell interpretation occurs."],"decision":"Create a separate security task; do not copy the CrystalServer denylist.","rationale":"The dangerous construction exists, but the upstream patch is not a sufficient security design.","provenance_used":"Problem signal only; no parser or sanitizer code approved."},{"id":"CS-007","repository":"zimbadev/crystalserver","crystal_commit":"891685169745e46f665069edcc35847f0704aa21","author":"jprzimba","date":"2026-07-10","related_pr":816,"files":["data/libs/functions/tables.lua"],"symbols":["table.unserialize","table.serialize"],"problem":"Deserialization executes loadstring over the supplied serialized text.","evidence":["Current Canary evaluates loadstring('return ' .. str)().","CrystalServer replaces it with a bespoke parser.","Call-site trust and full serializer compatibility are not yet established."],"canary_locations":["data/libs/functions/tables.lua:table.serialize","data/libs/functions/tables.lua:table.unserialize"],"status":"PARTIAL_VALUE","risk":"high","dependencies":["complete call-site inventory","compatibility corpus","input size/depth policy","security review"],"proposed_tests":["Round-trip every value emitted by table.serialize.","Reject function calls, environment access, trailing code, malformed input, and resource-exhaustion payloads."],"decision":"Create a separate compatibility/security task; do not transplant the upstream parser.","rationale":"Dynamic execution is confirmed, but a replacement must preserve legitimate data and resist hostile input.","provenance_used":"Problem signal only; bespoke parser code not approved."},{"id":"CS-008","repository":"zimbadev/crystalserver","crystal_commit":"34cbec0c34325619ef23c5d12c940b7b1c276975","author":"jprzimba","date":"2026-07-01","related_pr":808,"files":["src/game/game.cpp","src/io/iomarket.cpp","src/io/iomarket.hpp"],"symbols":["Game::playerCreateMarketOffer","IOMarket::getActiveOffers","IOMarket::getPlayerOfferCountPerSide","IOMarket::getItemOfferCountPerSide"],"problem":"Large Market offer sets are claimed to crash the client.","evidence":["CrystalServer adds limits 1000, 700, and 1500 plus SQL LIMIT clauses.","Current Canary IOMarket lacks equivalent constants and count helpers.","No authoritative client capacity or exact protocol contract was established."],"canary_locations":["src/io/iomarket.hpp:IOMarket","src/io/iomarket.cpp","src/game/game.cpp:Game::playerCreateMarketOffer"],"status":"CLIENT_COUPLED","risk":"high","dependencies":["maintained OTClient source and tests","protocol 15.25 contract","DB concurrency test","physical-client E2E"],"proposed_tests":["Byte/payload boundary tests for oversized Market responses.","Concurrent offer creation does not bypass limits.","Exact ordering, pagination, per-player, and per-item behavior."],"decision":"No automatic implementation.","rationale":"The constants and behavior cannot be validated server-only.","provenance_used":"Candidate concept only."},{"id":"CS-009","repository":"zimbadev/crystalserver","crystal_commit":"cfc0c5c496eae53f1f33a07f563068f44914ddbb","author":"jprzimba","date":"2026-06-15","related_pr":766,"files":["src/enums/disconnect_client.hpp","src/server/network/protocol/protocolgame.cpp","src/server/network/protocol/protocolgame.hpp"],"symbols":["DisconnectClient_t","ProtocolGame::disconnectClient","ProtocolGame::onRecvFirstMessage"],"problem":"Disconnect packets without an expected reason byte are claimed to crash clients.","evidence":["CrystalServer appends a reason byte and classifies several rejection flows.","Current Canary disconnectClient accepts only a message.","Expected field presence/order and supported-profile behavior are unverified."],"canary_locations":["src/server/network/protocol/protocolgame.hpp:ProtocolGame::disconnectClient","src/server/network/protocol/protocolgame.cpp"],"status":"CLIENT_COUPLED","risk":"high","dependencies":["protocol-profile matrix","maintained OTClient parser","cross-repo contract","real-client integration"],"proposed_tests":["Byte-exact disconnect packets for each supported profile and reason.","Invalid credentials, outdated protocol, and duplicate-session real-client flows."],"decision":"No automatic implementation.","rationale":"Adding a byte is a protocol contract change even when both projects declare 15.25.","provenance_used":"Candidate packet shape only."},{"id":"CS-010","repository":"zimbadev/crystalserver","crystal_commit":"ffe4db548371c44ce01dfc280af0209318272292","author":"jprzimba","date":"2025-11-27","related_pr":513,"files":["src/game/game.cpp"],"symbols":["Game::removeCreature"],"problem":"Dereferencing a missing creature parent can crash removal.","evidence":["Current Canary dereferences creature->getParent() after optional tile removal.","CrystalServer returns false if parent is null.","The upstream return occurs after tile removal and notifications but before lifecycle cleanup."],"canary_locations":["src/game/game.cpp:Game::removeCreature"],"status":"DANGEROUS","risk":"critical","dependencies":["parent-null reproduction","lifecycle invariant","instance and multichannel review","focused integration tests"],"proposed_tests":["Parent null before removal and parent reset during tile removal.","Repeated removal for player, monster, NPC, and summon.","List, ID index, instance ownership, zone, summon, and logout cleanup remains complete."],"decision":"Investigate the defect signal but reject direct transplantation.","rationale":"The upstream early return can leave a creature partially removed and corrupt runtime state.","provenance_used":"Problem signal only; early-return implementation explicitly rejected."}],"deferred_backlog":[{"crystal_commit":"9e046413b965982745ca63559f68bd30264bfc9d","preliminary_status":"UNVERIFIED","reason":"Duplicate item-definition claim needs current Canary XML, identifier, and asset-contract validation."},{"crystal_commit":"809633b1f9fc9a690bef70ac0ecb916d5a5aa5d6","preliminary_status":"UNVERIFIED","reason":"God-command item limit is arbitrary without current parsing and resource-bound evidence."},{"crystal_commit":"55db69b7be12fa7b6a8865038033d953ae8cff18","preliminary_status":"UNVERIFIED","reason":"Corpse and reward-parent handling needs current symbol and state-transition tests."},{"crystal_commit":"6bda45e7d7b8f0e9a9c55b3b6b779b492504102f","preliminary_status":"UNVERIFIED","reason":"Broad spell-formula rewrite requires official behavior evidence and bounded decomposition."}],"proposed_tasks":[{"order":1,"candidate_ids":["CS-001"],"scope":"ConditionLight zero-level regression test and minimal fix."},{"order":2,"candidate_ids":["CS-006"],"scope":"FS.mkdir trust-boundary and safe filesystem-operation audit."},{"order":3,"candidate_ids":["CS-007"],"scope":"Serialized-table call-site inventory, compatibility corpus, and safe decoder design."},{"order":4,"candidate_ids":["CS-010"],"scope":"Creature-removal parent invariant reproduction and lifecycle-safe design."},{"order":5,"candidate_ids":["CS-008","CS-009"],"scope":"Separate maintained-OTClient protocol contract investigations."},{"order":6,"candidate_ids":["CS-005"],"scope":"GUID lookup benchmark and index-lifecycle proof after path ownership clears."}],"constraints":["All writes only to blakinio/canary.","No direct push to main.","No mass copying or broad cherry-picks.","No .otbm, items.otb, binary assets, sprites, secrets, private dumps, or production configuration.","One candidate implementation per task, branch, worktree, and draft PR.","Protocol, client, schema, migration, multichannel, instance, shared userdata, map, identifier, and asset candidates require extended analysis."],"limitations":["No local checkout or worktree was available.","Shell DNS could not resolve github.com, so local git status, branch, remote, worktree, ownership checker, diff-check, build, and tests were not run.","The 50 fix and 30 crash search hits overlap and are not a unique commit count.","Only ten unique candidate diffs were deeply reviewed.","No runtime reproduction or maintained-client integration was executed in Stage 1.","FS.mkdir and table.unserialize untrusted-input reachability is unknown.","Exact maintained OTClient Market and disconnect contracts are unknown."]}` |
393: | `data/events/scripts/player.lua` | 441 | `FS.mkdir_p(string.format("%s/reports/players/%s", CORE_DIRECTORY, name))` |
394: | `data/events/scripts/player.lua` | 489 | `FS.mkdir_p(string.format("%s/reports/bugs/%s", CORE_DIRECTORY, name))` |
395: | `data/libs/functions/fs.lua` | 12 | `function FS.mkdir(path)` |
396: | `data/libs/functions/fs.lua` | 16 | `local success, err = os.execute('mkdir "' .. path .. '"')` |
```

### `artifacts/upstream/crystalserver/crystalserver_comparison_stage1.json:1`

```text
1: {"schema":"canary-crystalserver-comparison-v1","generated_at":"2026-07-13T21:01:05Z","analysis_date":"2026-07-13","stage":1,"functional_changes":false,"program_id":"CAN-PROGRAM-CRYSTALSERVER-COMPARISON","task_id":"CAN-20260713-crystalserver-comparison-inventory","baselines":{"target":{"repository":"blakinio/canary","branch":"main","sha":"360d79ebad5802edd4d89e99d0f210ab19b36b60","server_version":"3.6.1","client_protocol":1525,"access":"write-via-task-branch-and-pr"},"comparison":{"repository":"zimbadev/crystalserver","branch":"main","sha":"fc0d53b9f9965463b6082c07e6d3d482294541a7","server_version":"4.1.9","client_protocol":1525,"access":"read-only"},"reference":{"repository":"opentibiabr/canary","branch":"main","sha":"9365c1c4aa63529b9ff757f53737274894c02b8e","server_version":null,"client_protocol":null,"access":"read-only"}},"last_analyzed_crystal_commit":"fc0d53b9f9965463b6082c07e6d3d482294541a7","screening":{"queries":[{"term":"fix","hits_returned":50},{"term":"crash","hits_returned":30}],"overlap_not_fully_deduplicated":true,"deep_reviewed_unique":10,"deferred_unverified":4,"method":"Open CrystalServer diff, inspect corresponding current Canary source, then classify behaviorally."},"status_counts":{"ALREADY_PRESENT":2,"CANARY_SUPERIOR":1,"VALID_FIX_MISSING":1,"PARTIAL_VALUE":3,"CLIENT_COUPLED":2,"CONTENT_ONLY":0,"UNVERIFIED":0,"DANGEROUS":1,"REJECTED":0},"candidates":[{"id":"CS-001","repository":"zimbadev/crystalserver","crystal_commit":"a7350014528002fb27ed64d260a96d28a580d41a","author":"jprzimba","date":"2026-07-12","related_pr":822,"files":["src/creatures/combat/condition.cpp"],"symbols":["ConditionLight::startCondition","ConditionLight::unserializeProp"],"problem":"A zero light level reaches ticks / lightInfo.level and can cause integer division by zero.","evidence":["CrystalServer clamps the divisor and deserialized level to at least one.","Current Canary startCondition divides directly by lightInfo.level.","Current Canary deserialization assigns a persisted zero without normalization.","Other Canary mutation paths already clamp, showing a partial invariant."],"canary_locations":["src/creatures/combat/condition.cpp:ConditionLight::startCondition","src/creatures/combat/condition.cpp:ConditionLight::addCondition","src/creatures/combat/condition.cpp:ConditionLight::setParam","src/creatures/combat/condition.cpp:ConditionLight::unserializeProp"],"status":"VALID_FIX_MISSING","risk":"high","dependencies":["fresh ownership check","focused C++ regression test","required C++ build and CI"],"proposed_tests":["Deserialize CONDITIONATTR_LIGHTLEVEL=0 and start the condition without a division fault.","Verify normalized level and a valid lightChangeInterval.","Cover any reachable constructor or script path that can supply zero."],"decision":"Create a separate test-first implementation task after Stage 1 merges.","rationale":"The fault is deterministic from current source and the bounded guard is absent.","provenance_used":"Behavioral idea only: normalize invalid light level at persistence and division boundaries."},{"id":"CS-002","repository":"zimbadev/crystalserver","crystal_commit":"0c0f1acafd77a86fb5ce56fe768ff6d98d100c35","author":"jprzimba","date":"2026-07-11","related_pr":821,"files":["src/creatures/npcs/npc.cpp"],"symbols":["Npc::closeAllShopWindows"],"problem":"Callbacks while closing NPC shops can erase entries and invalidate iteration.","evidence":["CrystalServer snapshots GUIDs before callbacks.","Current Canary increments the iterator before calling closeShopWindow, then clears leftovers."],"canary_locations":["src/creatures/npcs/npc.cpp:Npc::closeAllShopWindows"],"status":"ALREADY_PRESENT","risk":"medium","dependencies":[],"proposed_tests":["Callbacks erase current entries while every shop player is visited exactly once and the map ends empty."],"decision":"No implementation.","rationale":"Current Canary already avoids using an iterator after the mutating callback.","provenance_used":"No code adapted."},{"id":"CS-003","repository":"zimbadev/crystalserver","crystal_commit":"90ac0eb7d2ba0a88476881c972d9de83fbbcb3e8","author":"matzinhozz","date":"2026-06-26","related_pr":799,"files":["src/lua/functions/core/libs/kv_functions.cpp"],"symbols":["KVFunctions::init","Lua::registerSharedClass","Lua::pushSharedUserdata"],"problem":"Shared KV userdata leaks if the metatable lacks shared-pointer garbage collection.","evidence":["CrystalServer changed non-shared class registration to shared registration.","Current Canary already uses typed registerSharedClass<KV> and pushSharedUserdata<KV>."],"canary_locations":["src/lua/functions/core/libs/kv_functions.cpp:KVFunctions::init","src/lua/functions/core/libs/kv_functions.cpp:KVFunctions::luaKVScoped"],"status":"CANARY_SUPERIOR","risk":"high","dependencies":[],"proposed_tests":["Repeated scoped KV creation and Lua GC releases all Lua-held strong references."],"decision":"Preserve current Canary implementation.","rationale":"Canary already applies the safe typed shared-userdata pattern.","provenance_used":"No code adapted."},{"id":"CS-004","repository":"zimbadev/crystalserver","crystal_commit":"dcb4f00ffd55ede2399c979eee3b7fe6e7e0ee6e","author":"jprzimba","date":"2025-07-17","related_pr":292,"files":["src/items/containers/container.cpp"],"symbols":["Container::replaceThing"],"problem":"Null input or an out-of-range replacement index can cause invalid access.","evidence":["CrystalServer adds null and bounds guards.","Current Canary already performs both guards before item conversion and replacement."],"canary_locations":["src/items/containers/container.cpp:Container::replaceThing"],"status":"ALREADY_PRESENT","risk":"high","dependencies":[],"proposed_tests":["Null thing and index equal to size are no-ops with unchanged cache, weight, and parents."],"decision":"No implementation.","rationale":"Equivalent validation is already present.","provenance_used":"No code adapted."},{"id":"CS-005","repository":"zimbadev/crystalserver","crystal_commit":"fc0d53b9f9965463b6082c07e6d3d482294541a7","author":"jprzimba","date":"2026-07-12","related_pr":819,"files":["src/game/game.cpp","src/game/game.hpp"],"symbols":["Game::getPlayerByGUID","Game::addPlayer","Game::removePlayer"],"problem":"Online player GUID lookup is linear in the number of players.","evidence":["CrystalServer adds a GUID index maintained on add/remove.","Current Canary still scans the online player map.","No current Canary performance regression or benchmark was provided."],"canary_locations":["src/game/game.cpp:Game::getPlayerByGUID"],"status":"PARTIAL_VALUE","risk":"medium","dependencies":["benchmark","index lifecycle tests","concurrency review","resolve overlap with open PR #289"],"proposed_tests":["Add/remove/relogin consistency and duplicate GUID behavior.","Offline fallback remains unchanged.","Benchmark representative online-player counts."],"decision":"Defer until path ownership clears and measurements justify the index.","rationale":"The optimization is plausible but not a proven bug fix and adds synchronized state.","provenance_used":"Candidate design signal only."},{"id":"CS-006","repository":"zimbadev/crystalserver","crystal_commit":"891685169745e46f665069edcc35847f0704aa21","author":"jprzimba","date":"2026-07-10","related_pr":816,"files":["data/libs/functions/fs.lua"],"symbols":["FS.mkdir"],"problem":"A path is concatenated into a shell command without validation.","evidence":["Current Canary uses os.execute with a quoted but unsanitized path.","CrystalServer adds a denylist but still invokes a shell.","Call-site attacker control is not yet established."],"canary_locations":["data/libs/functions/fs.lua:FS.mkdir","data/libs/functions/fs.lua:FS.mkdir_p"],"status":"PARTIAL_VALUE","risk":"high","dependencies":["complete call-site inventory","supported path semantics","cross-platform safe filesystem API"],"proposed_tests":["Reject quotes, separators, substitutions, control characters, and other command syntax.","Preserve valid Windows, POSIX, relative, absolute, and Unicode paths as required.","Prove no shell interpretation occurs."],"decision":"Create a separate security task; do not copy the CrystalServer denylist.","rationale":"The dangerous construction exists, but the upstream patch is not a sufficient security design.","provenance_used":"Problem signal only; no parser or sanitizer code approved."},{"id":"CS-007","repository":"zimbadev/crystalserver","crystal_commit":"891685169745e46f665069edcc35847f0704aa21","author":"jprzimba","date":"2026-07-10","related_pr":816,"files":["data/libs/functions/tables.lua"],"symbols":["table.unserialize","table.serialize"],"problem":"Deserialization executes loadstring over the supplied serialized text.","evidence":["Current Canary evaluates loadstring('return ' .. str)().","CrystalServer replaces it with a bespoke parser.","Call-site trust and full serializer compatibility are not yet established."],"canary_locations":["data/libs/functions/tables.lua:table.serialize","data/libs/functions/tables.lua:table.unserialize"],"status":"PARTIAL_VALUE","risk":"high","dependencies":["complete call-site inventory","compatibility corpus","input size/depth policy","security review"],"proposed_tests":["Round-trip every value emitted by table.serialize.","Reject function calls, environment access, trailing code, malformed input, and resource-exhaustion payloads."],"decision":"Create a separate compatibility/security task; do not transplant the upstream parser.","rationale":"Dynamic execution is confirmed, but a replacement must preserve legitimate data and resist hostile input.","provenance_used":"Problem signal only; bespoke parser code not approved."},{"id":"CS-008","repository":"zimbadev/crystalserver","crystal_commit":"34cbec0c34325619ef23c5d12c940b7b1c276975","author":"jprzimba","date":"2026-07-01","related_pr":808,"files":["src/game/game.cpp","src/io/iomarket.cpp","src/io/iomarket.hpp"],"symbols":["Game::playerCreateMarketOffer","IOMarket::getActiveOffers","IOMarket::getPlayerOfferCountPerSide","IOMarket::getItemOfferCountPerSide"],"problem":"Large Market offer sets are claimed to crash the client.","evidence":["CrystalServer adds limits 1000, 700, and 1500 plus SQL LIMIT clauses.","Current Canary IOMarket lacks equivalent constants and count helpers.","No authoritative client capacity or exact protocol contract was established."],"canary_locations":["src/io/iomarket.hpp:IOMarket","src/io/iomarket.cpp","src/game/game.cpp:Game::playerCreateMarketOffer"],"status":"CLIENT_COUPLED","risk":"high","dependencies":["maintained OTClient source and tests","protocol 15.25 contract","DB concurrency test","physical-client E2E"],"proposed_tests":["Byte/payload boundary tests for oversized Market responses.","Concurrent offer creation does not bypass limits.","Exact ordering, pagination, per-player, and per-item behavior."],"decision":"No automatic implementation.","rationale":"The constants and behavior cannot be validated server-only.","provenance_used":"Candidate concept only."},{"id":"CS-009","repository":"zimbadev/crystalserver","crystal_commit":"cfc0c5c496eae53f1f33a07f563068f44914ddbb","author":"jprzimba","date":"2026-06-15","related_pr":766,"files":["src/enums/disconnect_client.hpp","src/server/network/protocol/protocolgame.cpp","src/server/network/protocol/protocolgame.hpp"],"symbols":["DisconnectClient_t","ProtocolGame::disconnectClient","ProtocolGame::onRecvFirstMessage"],"problem":"Disconnect packets without an expected reason byte are claimed to crash clients.","evidence":["CrystalServer appends a reason byte and classifies several rejection flows.","Current Canary disconnectClient accepts only a message.","Expected field presence/order and supported-profile behavior are unverified."],"canary_locations":["src/server/network/protocol/protocolgame.hpp:ProtocolGame::disconnectClient","src/server/network/protocol/protocolgame.cpp"],"status":"CLIENT_COUPLED","risk":"high","dependencies":["protocol-profile matrix","maintained OTClient parser","cross-repo contract","real-client integration"],"proposed_tests":["Byte-exact disconnect packets for each supported profile and reason.","Invalid credentials, outdated protocol, and duplicate-session real-client flows."],"decision":"No automatic implementation.","rationale":"Adding a byte is a protocol contract change even when both projects declare 15.25.","provenance_used":"Candidate packet shape only."},{"id":"CS-010","repository":"zimbadev/crystalserver","crystal_commit":"ffe4db548371c44ce01dfc280af0209318272292","author":"jprzimba","date":"2025-11-27","related_pr":513,"files":["src/game/game.cpp"],"symbols":["Game::removeCreature"],"problem":"Dereferencing a missing creature parent can crash removal.","evidence":["Current Canary dereferences creature->getParent() after optional tile removal.","CrystalServer returns false if parent is null.","The upstream return occurs after tile removal and notifications but before lifecycle cleanup."],"canary_locations":["src/game/game.cpp:Game::removeCreature"],"status":"DANGEROUS","risk":"critical","dependencies":["parent-null reproduction","lifecycle invariant","instance and multichannel review","focused integration tests"],"proposed_tests":["Parent null before removal and parent reset during tile removal.","Repeated removal for player, monster, NPC, and summon.","List, ID index, instance ownership, zone, summon, and logout cleanup remains complete."],"decision":"Investigate the defect signal but reject direct transplantation.","rationale":"The upstream early return can leave a creature partially removed and corrupt runtime state.","provenance_used":"Problem signal only; early-return implementation explicitly rejected."}],"deferred_backlog":[{"crystal_commit":"9e046413b965982745ca63559f68bd30264bfc9d","preliminary_status":"UNVERIFIED","reason":"Duplicate item-definition claim needs current Canary XML, identifier, and asset-contract validation."},{"crystal_commit":"809633b1f9fc9a690bef70ac0ecb916d5a5aa5d6","preliminary_status":"UNVERIFIED","reason":"God-command item limit is arbitrary without current parsing and resource-bound evidence."},{"crystal_commit":"55db69b7be12fa7b6a8865038033d953ae8cff18","preliminary_status":"UNVERIFIED","reason":"Corpse and reward-parent handling needs current symbol and state-transition tests."},{"crystal_commit":"6bda45e7d7b8f0e9a9c55b3b6b779b492504102f","preliminary_status":"UNVERIFIED","reason":"Broad spell-formula rewrite requires official behavior evidence and bounded decomposition."}],"proposed_tasks":[{"order":1,"candidate_ids":["CS-001"],"scope":"ConditionLight zero-level regression test and minimal fix."},{"order":2,"candidate_ids":["CS-006"],"scope":"FS.mkdir trust-boundary and safe filesystem-operation audit."},{"order":3,"candidate_ids":["CS-007"],"scope":"Serialized-table call-site inventory, compatibility corpus, and safe decoder design."},{"order":4,"candidate_ids":["CS-010"],"scope":"Creature-removal parent invariant reproduction and lifecycle-safe design."},{"order":5,"candidate_ids":["CS-008","CS-009"],"scope":"Separate maintained-OTClient protocol contract investigations."},{"order":6,"candidate_ids":["CS-005"],"scope":"GUID lookup benchmark and index-lifecycle proof after path ownership clears."}],"constraints":["All writes only to blakinio/canary.","No direct push to main.","No mass copying or broad cherry-picks.","No .otbm, items.otb, binary assets, sprites, secrets, private dumps, or production configuration.","One candidate implementation per task, branch, worktree, and draft PR.","Protocol, client, schema, migration, multichannel, instance, shared userdata, map, identifier, and asset candidates require extended analysis."],"limitations":["No local checkout or worktree was available.","Shell DNS could not resolve github.com, so local git status, branch, remote, worktree, ownership checker, diff-check, build, and tests were not run.","The 50 fix and 30 crash search hits overlap and are not a unique commit count.","Only ten unique candidate diffs were deeply reviewed.","No runtime reproduction or maintained-client integration was executed in Stage 1.","FS.mkdir and table.unserialize untrusted-input reachability is unknown.","Exact maintained OTClient Market and disconnect contracts are unknown."]}
```

### `artifacts/upstream/crystalserver/cs006_fs_mkdir_audit.json:1655`

```text
1651:     },
1652:     {
1653:       "line": 1,
1654:       "path": "artifacts/upstream/crystalserver/crystalserver_comparison_stage1.json",
1655:       "text": "{\"schema\":\"canary-crystalserver-comparison-v1\",\"generated_at\":\"2026-07-13T21:01:05Z\",\"analysis_date\":\"2026-07-13\",\"stage\":1,\"functional_changes\":false,\"program_id\":\"CAN-PROGRAM-CRYSTALSERVER-COMPARISON\",\"task_id\":\"CAN-20260713-crystalserver-comparison-inventory\",\"baselines\":{\"target\":{\"repository\":\"blakinio/canary\",\"branch\":\"main\",\"sha\":\"360d79ebad5802edd4d89e99d0f210ab19b36b60\",\"server_version\":\"3.6.1\",\"client_protocol\":1525,\"access\":\"write-via-task-branch-and-pr\"},\"comparison\":{\"repository\":\"zimbadev/crystalserver\",\"branch\":\"main\",\"sha\":\"fc0d53b9f9965463b6082c07e6d3d482294541a7\",\"server_version\":\"4.1.9\",\"client_protocol\":1525,\"access\":\"read-only\"},\"reference\":{\"repository\":\"opentibiabr/canary\",\"branch\":\"main\",\"sha\":\"9365c1c4aa63529b9ff757f53737274894c02b8e\",\"server_version\":null,\"client_protocol\":null,\"access\":\"read-only\"}},\"last_analyzed_crystal_commit\":\"fc0d53b9f9965463b6082c07e6d3d482294541a7\",\"screening\":{\"queries\":[{\"term\":\"fix\",\"hits_returned\":50},{\"term\":\"crash\",\"hits_returned\":30}],\"overlap_not_fully_deduplicated\":true,\"deep_reviewed_unique\":10,\"deferred_unverified\":4,\"method\":\"Open CrystalServer diff, inspect corresponding current Canary source, then classify behaviorally.\"},\"status_counts\":{\"ALREADY_PRESENT\":2,\"CANARY_SUPERIOR\":1,\"VALID_FIX_MISSING\":1,\"PARTIAL_VALUE\":3,\"CLIENT_COUPLED\":2,\"CONTENT_ONLY\":0,\"UNVERIFIED\":0,\"DANGEROUS\":1,\"REJECTED\":0},\"candidates\":[{\"id\":\"CS-001\",\"repository\":\"zimbadev/crystalserver\",\"crystal_commit\":\"a7350014528002fb27ed64d260a96d28a580d41a\",\"author\":\"jprzimba\",\"date\":\"2026-07-12\",\"related_pr\":822,\"files\":[\"src/creatures/combat/condition.cpp\"],\"symbols\":[\"ConditionLight::startCondition\",\"ConditionLight::unserializeProp\"],\"problem\":\"A zero light level reaches ticks / lightInfo.level and can cause integer division by zero.\",\"evidence\":[\"CrystalServer clamps the divisor and deserialized level to at least one.\",\"Current Canary startCondition divides directly by lightInfo.level.\",\"Current Canary deserialization assigns a persisted zero without normalization.\",\"Other Canary mutation paths already clamp, showing a partial invariant.\"],\"canary_locations\":[\"src/creatures/combat/condition.cpp:ConditionLight::startCondition\",\"src/creatures/combat/condition.cpp:ConditionLight::addCondition\",\"src/creatures/combat/condition.cpp:ConditionLight::setParam\",\"src/creatures/combat/condition.cpp:ConditionLight::unserializeProp\"],\"status\":\"VALID_FIX_MISSING\",\"risk\":\"high\",\"dependencies\":[\"fresh ownership check\",\"focused C++ regression test\",\"required C++ build and CI\"],\"proposed_tests\":[\"Deserialize CONDITIONATTR_LIGHTLEVEL=0 and start the condition without a division fault.\",\"Verify normalized level and a valid lightChangeInterval.\",\"Cover any reachable constructor or script path that can supply zero.\"],\"decision\":\"Create a separate test-first implementation task after Stage 1 merges.\",\"rationale\":\"The fault is deterministic from current source and the bounded guard is absent.\",\"provenance_used\":\"Behavioral idea only: normalize invalid light level at persistence and division boundaries.\"},{\"id\":\"CS-002\",\"repository\":\"zimbadev/crystalserver\",\"crystal_commit\":\"0c0f1acafd77a86fb5ce56fe768ff6d98d100c35\",\"author\":\"jprzimba\",\"date\":\"2026-07-11\",\"related_pr\":821,\"files\":[\"src/creatures/npcs/npc.cpp\"],\"symbols\":[\"Npc::closeAllShopWindows\"],\"problem\":\"Callbacks while closing NPC shops can erase entries and invalidate iteration.\",\"evidence\":[\"CrystalServer snapshots GUIDs before callbacks.\",\"Current Canary increments the iterator before calling closeShopWindow, then clears leftovers.\"],\"canary_locations\":[\"src/creatures/npcs/npc.cpp:Npc::closeAllShopWindows\"],\"status\":\"ALREADY_PRESENT\",\"risk\":\"medium\",\"dependencies\":[],\"proposed_tests\":[\"Callbacks erase current entries while every shop player is visited exactly once and the map ends empty.\"],\"decision\":\"No implementation.\",\"rationale\":\"Current Canary already avoids using an iterator after the mutating callback.\",\"provenance_used\":\"No code adapted.\"},{\"id\":\"CS-003\",\"repository\":\"zimbadev/crystalserver\",\"crystal_commit\":\"90ac0eb7d2ba0a88476881c972d9de83fbbcb3e8\",\"author\":\"matzinhozz\",\"date\":\"2026-06-26\",\"related_pr\":799,\"files\":[\"src/lua/functions/core/libs/kv_functions.cpp\"],\"symbols\":[\"KVFunctions::init\",\"Lua::registerSharedClass\",\"Lua::pushSharedUserdata\"],\"problem\":\"Shared KV userdata leaks if the metatable lacks shared-pointer garbage collection.\",\"evidence\":[\"CrystalServer changed non-shared class registration to shared registration.\",\"Current Canary already uses typed registerSharedClass<KV> and pushSharedUserdata<KV>.\"],\"canary_locations\":[\"src/lua/functions/core/libs/kv_functions.cpp:KVFunctions::init\",\"src/lua/functions/core/libs/kv_functions.cpp:KVFunctions::luaKVScoped\"],\"status\":\"CANARY_SUPERIOR\",\"risk\":\"high\",\"dependencies\":[],\"proposed_tests\":[\"Repeated scoped KV creation and Lua GC releases all Lua-held strong references.\"],\"decision\":\"Preserve current Canary implementation.\",\"rationale\":\"Canary already applies the safe typed shared-userdata pattern.\",\"provenance_used\":\"No code adapted.\"},{\"id\":\"CS-004\",\"repository\":\"zimbadev/crystalserver\",\"crystal_commit\":\"dcb4f00ffd55ede2399c979eee3b7fe6e7e0ee6e\",\"author\":\"jprzimba\",\"date\":\"2025-07-17\",\"related_pr\":292,\"files\":[\"src/items/containers/container.cpp\"],\"symbols\":[\"Container::replaceThing\"],\"problem\":\"Null input or an out-of-range replacement index can cause invalid access.\",\"evidence\":[\"CrystalServer adds null and bounds guards.\",\"Current Canary already performs both guards before item conversion and replacement.\"],\"canary_locations\":[\"src/items/containers/container.cpp:Container::replaceThing\"],\"status\":\"ALREADY_PRESENT\",\"risk\":\"high\",\"dependencies\":[],\"proposed_tests\":[\"Null thing and index equal to size are no-ops with unchanged cache, weight, and parents.\"],\"decision\":\"No implementation.\",\"rationale\":\"Equivalent validation is already present.\",\"provenance_used\":\"No code adapted.\"},{\"id\":\"CS-005\",\"repository\":\"zimbadev/crystalserver\",\"crystal_commit\":\"fc0d53b9f9965463b6082c07e6d3d482294541a7\",\"author\":\"jprzimba\",\"date\":\"2026-07-12\",\"related_pr\":819,\"files\":[\"src/game/game.cpp\",\"src/game/game.hpp\"],\"symbols\":[\"Game::getPlayerByGUID\",\"Game::addPlayer\",\"Game::removePlayer\"],\"problem\":\"Online player GUID lookup is linear in the number of players.\",\"evidence\":[\"CrystalServer adds a GUID index maintained on add/remove.\",\"Current Canary still scans the online player map.\",\"No current Canary performance regression or benchmark was provided.\"],\"canary_locations\":[\"src/game/game.cpp:Game::getPlayerByGUID\"],\"status\":\"PARTIAL_VALUE\",\"risk\":\"medium\",\"dependencies\":[\"benchmark\",\"index lifecycle tests\",\"concurrency review\",\"resolve overlap with open PR #289\"],\"proposed_tests\":[\"Add/remove/relogin consistency and duplicate GUID behavior.\",\"Offline fallback remains unchanged.\",\"Benchmark representative online-player counts.\"],\"decision\":\"Defer until path ownership clears and measurements justify the index.\",\"rationale\":\"The optimization is plausible but not a proven bug fix and adds synchronized state.\",\"provenance_used\":\"Candidate design signal only.\"},{\"id\":\"CS-006\",\"repository\":\"zimbadev/crystalserver\",\"crystal_commit\":\"891685169745e46f665069edcc35847f0704aa21\",\"author\":\"jprzimba\",\"date\":\"2026-07-10\",\"related_pr\":816,\"files\":[\"data/libs/functions/fs.lua\"],\"symbols\":[\"FS.mkdir\"],\"problem\":\"A path is concatenated into a shell command without validation.\",\"evidence\":[\"Current Canary uses os.execute with a quoted but unsanitized path.\",\"CrystalServer adds a denylist but still invokes a shell.\",\"Call-site attacker control is not yet established.\"],\"canary_locations\":[\"data/libs/functions/fs.lua:FS.mkdir\",\"data/libs/functions/fs.lua:FS.mkdir_p\"],\"status\":\"PARTIAL_VALUE\",\"risk\":\"high\",\"dependencies\":[\"complete call-site inventory\",\"supported path semantics\",\"cross-platform safe filesystem API\"],\"proposed_tests\":[\"Reject quotes, separators, substitutions, control characters, and other command syntax.\",\"Preserve valid Windows, POSIX, relative, absolute, and Unicode paths as required.\",\"Prove no shell interpretation occurs.\"],\"decision\":\"Create a separate security task; do not copy the CrystalServer denylist.\",\"rationale\":\"The dangerous construction exists, but the upstream patch is not a sufficient security design.\",\"provenance_used\":\"Problem signal only; no parser or sanitizer code approved.\"},{\"id\":\"CS-007\",\"repository\":\"zimbadev/crystalserver\",\"crystal_commit\":\"891685169745e46f665069edcc35847f0704aa21\",\"author\":\"jprzimba\",\"date\":\"2026-07-10\",\"related_pr\":816,\"files\":[\"data/libs/functions/tables.lua\"],\"symbols\":[\"table.unserialize\",\"table.serialize\"],\"problem\":\"Deserialization executes loadstring over the supplied serialized text.\",\"evidence\":[\"Current Canary evaluates loadstring('return ' .. str)().\",\"CrystalServer replaces it with a bespoke parser.\",\"Call-site trust and full serializer compatibility are not yet established.\"],\"canary_locations\":[\"data/libs/functions/tables.lua:table.serialize\",\"data/libs/functions/tables.lua:table.unserialize\"],\"status\":\"PARTIAL_VALUE\",\"risk\":\"high\",\"dependencies\":[\"complete call-site inventory\",\"compatibility corpus\",\"input size/depth policy\",\"security review\"],\"proposed_tests\":[\"Round-trip every value emitted by table.serialize.\",\"Reject function calls, environment access, trailing code, malformed input, and resource-exhaustion payloads.\"],\"decision\":\"Create a separate compatibility/security task; do not transplant the upstream parser.\",\"rationale\":\"Dynamic execution is confirmed, but a replacement must preserve legitimate data and resist hostile input.\",\"provenance_used\":\"Problem signal only; bespoke parser code not approved.\"},{\"id\":\"CS-008\",\"repository\":\"zimbadev/crystalserver\",\"crystal_commit\":\"34cbec0c34325619ef23c5d12c940b7b1c276975\",\"author\":\"jprzimba\",\"date\":\"2026-07-01\",\"related_pr\":808,\"files\":[\"src/game/game.cpp\",\"src/io/iomarket.cpp\",\"src/io/iomarket.hpp\"],\"symbols\":[\"Game::playerCreateMarketOffer\",\"IOMarket::getActiveOffers\",\"IOMarket::getPlayerOfferCountPerSide\",\"IOMarket::getItemOfferCountPerSide\"],\"problem\":\"Large Market offer sets are claimed to crash the client.\",\"evidence\":[\"CrystalServer adds limits 1000, 700, and 1500 plus SQL LIMIT clauses.\",\"Current Canary IOMarket lacks equivalent constants and count helpers.\",\"No authoritative client capacity or exact protocol contract was established.\"],\"canary_locations\":[\"src/io/iomarket.hpp:IOMarket\",\"src/io/iomarket.cpp\",\"src/game/game.cpp:Game::playerCreateMarketOffer\"],\"status\":\"CLIENT_COUPLED\",\"risk\":\"high\",\"dependencies\":[\"maintained OTClient source and tests\",\"protocol 15.25 contract\",\"DB concurrency test\",\"physical-client E2E\"],\"proposed_tests\":[\"Byte/payload boundary tests for oversized Market responses.\",\"Concurrent offer creation does not bypass limits.\",\"Exact ordering, pagination, per-player, and per-item behavior.\"],\"decision\":\"No automatic implementation.\",\"rationale\":\"The constants and behavior cannot be validated server-only.\",\"provenance_used\":\"Candidate concept only.\"},{\"id\":\"CS-009\",\"repository\":\"zimbadev/crystalserver\",\"crystal_commit\":\"cfc0c5c496eae53f1f33a07f563068f44914ddbb\",\"author\":\"jprzimba\",\"date\":\"2026-06-15\",\"related_pr\":766,\"files\":[\"src/enums/disconnect_client.hpp\",\"src/server/network/protocol/protocolgame.cpp\",\"src/server/network/protocol/protocolgame.hpp\"],\"symbols\":[\"DisconnectClient_t\",\"ProtocolGame::disconnectClient\",\"ProtocolGame::onRecvFirstMessage\"],\"problem\":\"Disconnect packets without an expected reason byte are claimed to crash clients.\",\"evidence\":[\"CrystalServer appends a reason byte and classifies several rejection flows.\",\"Current Canary disconnectClient accepts only a message.\",\"Expected field presence/order and supported-profile behavior are unverified.\"],\"canary_locations\":[\"src/server/network/protocol/protocolgame.hpp:ProtocolGame::disconnectClient\",\"src/server/network/protocol/protocolgame.cpp\"],\"status\":\"CLIENT_COUPLED\",\"risk\":\"high\",\"dependencies\":[\"protocol-profile matrix\",\"maintained OTClient parser\",\"cross-repo contract\",\"real-client integration\"],\"proposed_tests\":[\"Byte-exact disconnect packets for each supported profile and reason.\",\"Invalid credentials, outdated protocol, and duplicate-session real-client flows.\"],\"decision\":\"No automatic implementation.\",\"rationale\":\"Adding a byte is a protocol contract change even when both projects declare 15.25.\",\"provenance_used\":\"Candidate packet shape only.\"},{\"id\":\"CS-010\",\"repository\":\"zimbadev/crystalserver\",\"crystal_commit\":\"ffe4db548371c44ce01dfc280af0209318272292\",\"author\":\"jprzimba\",\"date\":\"2025-11-27\",\"related_pr\":513,\"files\":[\"src/game/game.cpp\"],\"symbols\":[\"Game::removeCreature\"],\"problem\":\"Dereferencing a missing creature parent can crash removal.\",\"evidence\":[\"Current Canary dereferences creature->getParent() after optional tile removal.\",\"CrystalServer returns false if parent is null.\",\"The upstream return occurs after tile removal and notifications but before lifecycle cleanup.\"],\"canary_locations\":[\"src/game/game.cpp:Game::removeCreature\"],\"status\":\"DANGEROUS\",\"risk\":\"critical\",\"dependencies\":[\"parent-null reproduction\",\"lifecycle invariant\",\"instance and multichannel review\",\"focused integration tests\"],\"proposed_tests\":[\"Parent null before removal and parent reset during tile removal.\",\"Repeated removal for player, monster, NPC, and summon.\",\"List, ID index, instance ownership, zone, summon, and logout cleanup remains complete.\"],\"decision\":\"Investigate the defect signal but reject direct transplantation.\",\"rationale\":\"The upstream early return can leave a creature partially removed and corrupt runtime state.\",\"provenance_used\":\"Problem signal only; early-return implementation explicitly rejected.\"}],\"deferred_backlog\":[{\"crystal_commit\":\"9e046413b965982745ca63559f68bd30264bfc9d\",\"preliminary_status\":\"UNVERIFIED\",\"reason\":\"Duplicate item-definition claim needs current Canary XML, identifier, and asset-contract validation.\"},{\"crystal_commit\":\"809633b1f9fc9a690bef70ac0ecb916d5a5aa5d6\",\"preliminary_status\":\"UNVERIFIED\",\"reason\":\"God-command item limit is arbitrary without current parsing and resource-bound evidence.\"},{\"crystal_commit\":\"55db69b7be12fa7b6a8865038033d953ae8cff18\",\"preliminary_status\":\"UNVERIFIED\",\"reason\":\"Corpse and reward-parent handling needs current symbol and state-transition tests.\"},{\"crystal_commit\":\"6bda45e7d7b8f0e9a9c55b3b6b779b492504102f\",\"preliminary_status\":\"UNVERIFIED\",\"reason\":\"Broad spell-formula rewrite requires official behavior evidence and bounded decomposition.\"}],\"proposed_tasks\":[{\"order\":1,\"candidate_ids\":[\"CS-001\"],\"scope\":\"ConditionLight zero-level regression test and minimal fix.\"},{\"order\":2,\"candidate_ids\":[\"CS-006\"],\"scope\":\"FS.mkdir trust-boundary and safe filesystem-operation audit.\"},{\"order\":3,\"candidate_ids\":[\"CS-007\"],\"scope\":\"Serialized-table call-site inventory, compatibility corpus, and safe decoder design.\"},{\"order\":4,\"candidate_ids\":[\"CS-010\"],\"scope\":\"Creature-removal parent invariant reproduction and lifecycle-safe design.\"},{\"order\":5,\"candidate_ids\":[\"CS-008\",\"CS-009\"],\"scope\":\"Separate maintained-OTClient protocol contract investigations.\"},{\"order\":6,\"candidate_ids\":[\"CS-005\"],\"scope\":\"GUID lookup benchmark and index-lifecycle proof after path ownership clears.\"}],\"constraints\":[\"All writes only to blakinio/canary.\",\"No direct push to main.\",\"No mass copying or broad cherry-picks.\",\"No .otbm, items.otb, binary assets, sprites, secrets, private dumps, or production configuration.\",\"One candidate implementation per task, branch, worktree, and draft PR.\",\"Protocol, client, schema, migration, multichannel, instance, shared userdata, map, identifier, and asset candidates require extended analysis.\"],\"limitations\":[\"No local checkout or worktree was available.\",\"Shell DNS could not resolve github.com, so local git status, branch, remote, worktree, ownership checker, diff-check, build, and tests were not run.\",\"The 50 fix and 30 crash search hits overlap and are not a unique commit count.\",\"Only ten unique candidate diffs were deeply reviewed.\",\"No runtime reproduction or maintained-client integration was executed in Stage 1.\",\"FS.mkdir and table.unserialize untrusted-input reachability is unknown.\",\"Exact maintained OTClient Market and disconnect contracts are unknown.\"]}"
1656:     },
1657:     {
1658:       "line": 441,
1659:       "path": "data/events/scripts/player.lua",
```

### `data/libs/functions/tables.lua:102`

```text
98: 	end
99: end
100:
101: function table.unserialize(str)
102: 	return loadstring("return " .. str)()
103: end
104:
105: function table.shallowCopy(oldTable)
106: 	local newTable = {}
```

### `docs/agents/tasks/active/CAN-20260714-table-unserialize-security.md:56`

```text
52:
53: # Candidate evidence
54:
55: - CrystalServer commit: `891685169745e46f665069edcc35847f0704aa21`, PR #816.
56: - Current Canary `data/libs/functions/tables.lua` still executes `loadstring("return " .. str)()`.
57: - The donor recursive parser is evidence only and must not be copied without independent correctness and compatibility proof.
58:
59: # Acceptance criteria
60:
```

## Direct `load` occurrences

Occurrences: **152**

### `.github/workflows/gameplay-analytics-dashboards.yml:49`

```text
45:         run: python -m unittest discover -s tools/analytics -p "test_validate_gameplay_analytics_dashboard.py" -v
46:       - name: Check dashboard view test shell syntax
47:         run: bash -n tools/analytics/test_gameplay_analytics_dashboard_views.sh
48:       - name: Parse dashboard JSON
49:         run: python -c "import json; json.load(open('grafana/gameplay-analytics-dashboard.json'))"
50:       - name: Parse provisioning YAML examples
51:         run: |
52:           pip install PyYAML
53:           python -c "import yaml; yaml.safe_load(open('grafana/provisioning/datasources/mariadb.yaml.example'))"
```

### `data-canary/lib/core/quests.lua:1`

```text
1: return require("data.lib.core.quests.loader").load(DATA_DIRECTORY)
```

### `data-otservbr-global/lib/core/quests.lua:1`

```text
1: return require("data.lib.core.quests.loader").load(DATA_DIRECTORY)
```

### `data/libs/functions/functions.lua:809`

```text
805: 	return out
806: end
807:
808: function unserializeTable(str, out)
809: 	local tmp = load("return " .. str)
810: 	if tmp then
811: 		tmp = tmp()
812: 	else
813: 		logger.warn("[unserializeTable] - Unserialization error: {}", str)
```

### `data/scripts/talkactions/god/manage_kv.lua:95`

```text
91: 			player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "Player '" .. playerName .. "' not found or is not a valid player.")
92: 			return false
93: 		end
94: 	end
95: 	local success, parsedValue = pcall(load("return " .. value))
96: 	if not success then
97: 		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "Invalid value format.")
98: 		return false
99: 	end
```

### `docs/ai-agent/OTS_AI_WORLD_VALIDATION_PROJECT.md:106`

```text
102: ### 2.7. Runtime Canary
103:
104: Najwyższy poziom walidacji powinien uruchamiać prawdziwy serwer i sprawdzać:
105:
106: - pełne `Map::load()` / `IOMap`;
107: - ładowanie companion XML;
108: - ładowanie NPC i spawnów;
109: - rejestrację eventów;
110: - błędy i ostrzeżenia startowe;
```

### `docs/ai-agent/OTS_AI_WORLD_VALIDATION_PROJECT.md:561`

```text
557: - [ ] audyt storage i nagród.
558:
559: ### Kamień milowy 3 — pełne ładowanie runtime
560:
561: - [ ] pełne `Map::load()` / `IOMap` w kontrolowanym środowisku;
562: - [ ] companion XML, NPC i spawny ładują się;
563: - [ ] brak niezaakceptowanych błędów startowych;
564: - [ ] raport powtarzalny w CI.
565:
```

### `docs/ai-agent/OTS_OTBM_AGENT_HANDOFF.md:27`

```text
23: 7. produkcyjny resolver wiążący identyfikatory mapy z handlerami Lua/XML;
24: 8. poprawioną lokalną kopię mapy bez pojedynczego nieobsługiwanego itemu `2141`;
25: 9. natywne potwierdzenie struktury poprawionej kopii przez Canary `OTB::Loader::parseTree()`.
26:
27: Najważniejszy wynik: **warstwa narzędziowa jest gotowa**. Pozostały ręczny audyt 151 nierozwiązanych identyfikatorów, opcjonalny pełny test `Map::load()` / `IOMap` i pierwsza mała rekonstrukcja regionu.
28:
29: Szerszy projekt AI review map, questów, NPC i spawnów jest osobnym zadaniem i nie należy mieszać go z tym handoffem.
30:
31: ---
```

### `docs/ai-agent/OTS_OTBM_AGENT_HANDOFF.md:217`

```text
213: ```
214:
215: Test użył rzeczywistego `src/io/fileloader.cpp` i niezmienionej logiki `OTB::Loader::parseTree()`.
216:
217: To zamyka walidację strukturalną binarnego drzewa OTBM. Pełny test semantyczny `Map::load()` / `IOMap` z kompletnymi zależnościami serwera nadal pozostaje zalecanym testem przed produkcyjnym wdrożeniem mapy.
218:
219: ---
220:
221: ## 7. Produkcyjny resolver handlerów
```

### `docs/ai-agent/OTS_OTBM_AGENT_HANDOFF.md:360`

```text
356: ---
357:
358: ## 10. Co nadal zostało do zrobienia
359:
360: ### P0 — opcjonalny pełny test `Map::load()` / `IOMap`
361:
362: - zbudować pełne testy integracyjne Canary z zależnościami vcpkg;
363: - uruchomić `Map::load()` na poprawionej kopii;
364: - wczytać companion XML, houses, zones, spawns i NPC;
```

### `docs/ai-agent/OTS_OTBM_AGENT_HANDOFF.md:363`

```text
359:
360: ### P0 — opcjonalny pełny test `Map::load()` / `IOMap`
361:
362: - zbudować pełne testy integracyjne Canary z zależnościami vcpkg;
363: - uruchomić `Map::load()` na poprawionej kopii;
364: - wczytać companion XML, houses, zones, spawns i NPC;
365: - zachować wynik jako artefakt CI lub lokalny log.
366:
367: ### P0 — ręczny audyt 151 identyfikatorów
```

### `docs/ai-agent/OTS_OTBM_AGENT_HANDOFF.md:417`

```text
413: - [x] natywny `OTB::Loader::parseTree()` potwierdza strukturę poprawionej kopii.
414:
415: ### Jeszcze nie zakończone
416:
417: - [ ] opcjonalny pełny test integracyjny `Map::load()` / `IOMap`;
418: - [ ] 151 ID ma docelową, evidence-based klasyfikację;
419: - [ ] wybrano i zwalidowano pierwszy pilotowy region;
420: - [ ] rozpoczęto produkcyjną rekonstrukcję świata.
421:
```

### `docs/ai-agent/OTS_OTBM_AGENT_HANDOFF.md:437`

```text
433: ```bash
434: python tools/ai-agent/otbm_script_resolution_tool.py --help
435: ```
436:
437: 7. Zapoznaj się z logiem natywnego `FileLoader` i w razie dostępnego pełnego środowiska uruchom dodatkowo `Map::load()`.
438: 8. Wybierz jedną grupę z 151 ID do ręcznej analizy albo jeden mały region pilotowy.
439: 9. Każdą zmianę wykonuj na osobnej gałęzi i w osobnym PR.
440:
441: ---
```

### `docs/ai-agent/WEAPON_PROFICIENCY_ACHIEVEMENT_REPORT.md:64`

```text
60: Disposition: `confirmed-runtime-defect`.
61:
62: ### Load normalization can recover the flag
63:
64: `WeaponProficiency::load()` calls `normalizeStoredState(weaponId)`, and normalization derives the mastered flag from stored XP versus maximum XP. A relog can repair the flag state, but that does not repair the missing immediate transition or award achievements automatically.
65:
66: Disposition: `confirmed-backfill-input`, not yet a backfill policy.
67:
68: ### No mastery achievement hook
```

### `docs/systems/login-session-manager.md:70`

```text
66: - **Modern clients with `authType == "session"`** are exactly the existing
67:   code path this integrates with: `IOLoginData::gameWorldAuthentication` already
68:   skips password re-validation in this mode and instead calls
69:   `Account::authenticate()`, which today falls through to the DB-backed
70:   `account_sessions` table (`Account::load()` → `loadBySession`). The planned
71:   follow-up adds `LoginSessionManager::issueToken`/`consumeToken` as a check
72:   *ahead of* that DB lookup, for connections whose resolved `ProtocolProfileId`
73:   actually sent a session-key field. The DB-backed table is left untouched —
74:   it also serves standalone login-panel/launcher integrations that mint their
```

### `src/account/account.cpp:38`

```text
34: 	m_account->premiumLastDay = 0;
35: 	m_account->accountType = ACCOUNT_TYPE_NORMAL;
36: }
37:
38: AccountErrors_t Account::load() {
39: 	using enum AccountErrors_t;
40: 	if (m_account->id != 0 && g_accountRepository().loadByID(m_account->id, m_account)) {
41: 		m_accLoaded = true;
42: 		return Ok;
```

### `src/account/account.cpp:64`

```text
60: 	if (!m_accLoaded) {
61: 		return AccountErrors_t::NotInitialized;
62: 	}
63:
64: 	return load();
65: }
66:
67: AccountErrors_t Account::save() const {
68: 	using enum AccountErrors_t;
```

### `src/account/account.hpp:80`

```text
76: 	 * @brief Load Account Information.
77: 	 *
78: 	 * @return AccountErrors_t AccountErrors_t::Ok(0) Success, otherwise Fail.
79: 	 */
80: 	AccountErrors_t load();
81:
82: 	/**
83: 	 * @brief Re-Load Account Information to get update information(mainly the
84: 	 * players list).
```

### `src/account/account_repository_db.cpp:30`

```text
26: }
27:
28: bool AccountRepositoryDB::loadByID(const uint32_t &id, std::unique_ptr<AccountInfo> &acc) {
29: 	auto query = fmt::format("SELECT `id`, `type`, `premdays`, `lastday`, `creation`, `premdays_purchased`, 0 AS `expires` FROM `accounts` WHERE `id` = {}", id);
30: 	return load(query, acc);
31: };
32:
33: bool AccountRepositoryDB::loadByEmailOrName(bool oldProtocol, const std::string &emailOrName, std::unique_ptr<AccountInfo> &acc) {
34: 	auto identifier = oldProtocol ? "name" : "email";
```

### `src/account/account_repository_db.cpp:36`

```text
32:
33: bool AccountRepositoryDB::loadByEmailOrName(bool oldProtocol, const std::string &emailOrName, std::unique_ptr<AccountInfo> &acc) {
34: 	auto identifier = oldProtocol ? "name" : "email";
35: 	auto query = fmt::format("SELECT `id`, `type`, `premdays`, `lastday`, `creation`, `premdays_purchased`, 0 AS `expires` FROM `accounts` WHERE `{}` = {}", identifier, g_database().escapeString(emailOrName));
36: 	return load(query, acc);
37: };
38:
39: bool AccountRepositoryDB::loadBySession(const std::string &sessionKey, std::unique_ptr<AccountInfo> &acc) {
40: 	const auto escapedSessionId = g_database().escapeString(transformToSHA256(sessionKey));
```

### `src/account/account_repository_db.cpp:52`

```text
48: 		escapedSessionId,
49: 		escapedLegacySessionId,
50: 		escapedSessionId
51: 	);
52: 	return load(query, acc);
53: };
54:
55: bool AccountRepositoryDB::save(const std::unique_ptr<AccountInfo> &accInfo) {
56: 	bool successful = g_database().executeQuery(
```

### `src/account/account_repository_db.cpp:285`

```text
281:
282: 	return true;
283: }
284:
285: bool AccountRepositoryDB::load(const std::string &query, std::unique_ptr<AccountInfo> &acc) {
286: 	auto result = g_database().storeQuery(query);
287:
288: 	if (result == nullptr) {
289: 		return false;
```

### `src/account/account_repository_db.hpp:52`

```text
48:
49: private:
50: 	std::unordered_map<CoinType, std::string> coinTypeToColumn {};
51:
52: 	bool load(const std::string &query, std::unique_ptr<AccountInfo> &acc);
53: 	bool loadAccountPlayers(std::unique_ptr<AccountInfo> &acc) const;
54: 	void setupLoyaltyInfo(std::unique_ptr<AccountInfo> &acc);
55: };
```

### `src/canary_server.cpp:457`

```text
453: 	}
454:
455: 	g_configManager().setConfigFileLua(configName);
456:
457: 	modulesLoadHelper(g_configManager().load(), g_configManager().getConfigFileLua());
458:
459: #ifdef _WIN32
460: 	const std::string &defaultPriority = g_configManager().getString(DEFAULT_PRIORITY);
461: 	if (strcasecmp(defaultPriority.c_str(), "high") == 0) {
```

### `src/canary_server.cpp:687`

```text
683: 	timedLoad(coreFolder + "/scripts", [&coreFolder] {
684: 		return g_scripts().loadScripts(coreFolder + "/scripts", false, false);
685: 	});
686: 	timedLoad("npclib", [] {
687: 		return g_npcs().load(true, false);
688: 	});
689:
690: 	timedLoad("events/events.xml", [] {
691: 		return g_events().loadFromXml();
```

### `src/canary_server.cpp:710`

```text
706: 	timedLoad(datapackFolder + "/monster", [&datapackFolder] {
707: 		return g_scripts().loadScripts(datapackFolder + "/monster", false, false);
708: 	});
709: 	timedLoad("npc", [] {
710: 		return g_npcs().load(false, true);
711: 	});
712:
713: 	// It needs to be loaded after the revscript is read in order to use the scripting interface.
714: 	timedLoad("json/eventscheduler/events.json", [] {
```

### `src/config/configmanager.cpp:27`

```text
23: ConfigManager &ConfigManager::getInstance() {
24: 	return inject<ConfigManager>();
25: }
26:
27: bool ConfigManager::load() {
28: 	lua_State* L = luaL_newstate();
29: 	if (!L) {
30: 		throw std::ios_base::failure("Failed to allocate memory");
31: 	}
```

### `src/config/configmanager.cpp:451`

```text
447: 	m_configString.clear();
448: 	m_configInteger.clear();
449: 	m_configBoolean.clear();
450: 	m_configFloat.clear();
451: 	const bool result = load();
452: 	if (transformToSHA1(getString(SERVER_MOTD)) != g_game().getMotdHash()) {
453: 		g_game().incrementMotdNum();
454: 	}
455: 	return result;
```

### `src/config/configmanager.hpp:27`

```text
23: 	void operator=(const ConfigManager &) = delete;
24:
25: 	static ConfigManager &getInstance();
26:
27: 	bool load();
28: 	bool reload();
29:
30: 	void missingConfigWarning(const char* identifier);
31:
```

### `src/creatures/interactions/chat.cpp:349`

```text
345: Chat &Chat::getInstance() {
346: 	return inject<Chat>();
347: }
348:
349: bool Chat::load() {
350: 	pugi::xml_document doc;
351: 	auto coreFolder = g_configManager().getString(CORE_DIRECTORY);
352: 	auto folder = coreFolder + "/chatchannels/chatchannels.xml";
353: 	pugi::xml_parse_result result = doc.load_file(folder.c_str());
```

### `src/creatures/interactions/chat.hpp:101`

```text
97: 	Chat &operator=(const Chat &) = delete;
98:
99: 	static Chat &getInstance();
100:
101: 	bool load();
102:
103: 	std::shared_ptr<ChatChannel> createChannel(const std::shared_ptr<Player> &player, uint16_t channelId);
104: 	bool deleteChannel(const std::shared_ptr<Player> &player, uint16_t channelId);
105:
```

### `src/creatures/npcs/npcs.cpp:106`

```text
102: 	}
103: 	npcType->info.shopItemVector.emplace_back(shopBlock);
104: }
105:
106: bool Npcs::load(bool loadLibs /* = true*/, bool loadNpcs /* = true*/, bool reloading /* = false*/) const {
107: 	if (loadLibs) {
108: 		const auto coreFolder = g_configManager().getString(CORE_DIRECTORY);
109: 		return g_luaEnvironment().loadFile(coreFolder + "/npclib/load.lua", "load.lua") == 0;
110: 	}
```

### `src/creatures/npcs/npcs.cpp:120`

```text
116: }
117:
118: bool Npcs::reload() {
119: 	// Load the "npclib" folder
120: 	if (load(true, false, true)) {
121: 		// Load the npcs scripts folder
122: 		if (!load(false, true, true)) {
123: 			return false;
124: 		}
```

### `src/creatures/npcs/npcs.cpp:122`

```text
118: bool Npcs::reload() {
119: 	// Load the "npclib" folder
120: 	if (load(true, false, true)) {
121: 		// Load the npcs scripts folder
122: 		if (!load(false, true, true)) {
123: 			return false;
124: 		}
125:
126: 		npcs.clear();
```

### `src/creatures/npcs/npcs.hpp:110`

```text
106:
107: 	std::shared_ptr<NpcType> getNpcType(const std::string &name, bool create = false);
108:
109: 	// Reset npcs informations on reload
110: 	bool load(bool loadLibs = true, bool loadNpcs = true, bool reloading = false) const;
111: 	bool reload();
112:
113: private:
114: 	std::unique_ptr<LuaScriptInterface> scriptInterface;
```

### `src/creatures/players/components/README.md:74`

```text
70: 	g_logger().error("Failed to persist storages for player {}", player.getName());
71: }
72:
73: // Reload everything on login
74: player.storage().load();
75: ```
76:
77: ---
78:
```

### `src/creatures/players/components/README.md:138`

```text
134: - Call `remove(key)` explicitly when you want to delete a storage key.
135: - Although `add(key, -1)` is technically supported, prefer `remove()` for clarity and maintainability.
136: - Use `has()` to check for existence before assuming a key is present.
137: - Do **not** call `save()` manually after every change. Storages are automatically:
138:   - **Loaded on login** (`load()`).
139:   - **Saved on logout** (`save()`), persisting only keys that were actually modified or removed.
140: - This incremental approach ensures that logout remains efficient even for players with thousands of storages, while avoiding unnecessary writes during gameplay.
141:
142: ---
```

### `src/creatures/players/components/player_forge_history.cpp:43`

```text
39: 		return h.id == id;
40: 	});
41: }
42:
43: bool PlayerForgeHistory::load() {
44: 	auto playerGUID = m_player.getGUID();
45: 	Benchmark benchmark;
46: 	auto query = fmt::format("SELECT * FROM forge_history WHERE player_id = {}", playerGUID);
47: 	const DBResult_ptr &result = g_database().storeQuery(query);
```

### `src/creatures/players/components/player_forge_history.hpp:53`

```text
49: 	const std::vector<ForgeHistory> &get() const;
50: 	void add(const ForgeHistory &history);
51: 	void remove(uint32_t id);
52:
53: 	bool load();
54: 	bool save();
55:
56: private:
57: 	std::vector<ForgeHistory> m_history;
```

### `src/creatures/players/components/weapon_proficiency.cpp:272`

```text
268:
269: 	return true;
270: }
271:
272: void WeaponProficiency::load() {
273: 	proficiency.clear();
274:
275: 	auto wp_kv = m_player.kv()->scoped("weapon-proficiency");
276: 	for (const auto &key : wp_kv->keys()) {
```

### `src/creatures/players/components/weapon_proficiency.hpp:35`

```text
31: 	[[nodiscard]] static bool loadFromJson(bool reload = false);
32:
33: 	[[nodiscard]] static std::unordered_map<uint16_t, Proficiency> &getProficiencies();
34:
35: 	void load();
36: 	void save(uint16_t weaponId) const;
37: 	bool saveAll() const;
38: 	[[nodiscard]] std::vector<uint16_t> getTrackedWeaponIds() const;
39: 	[[nodiscard]] size_t getMasteredWeaponCount() const;
```

### `src/creatures/players/components/wheel/player_wheel.cpp:1114`

```text
1110: 		}
1111: 	});
1112:
1113: 	for (const auto &uuid : sortedUnlockedGemGUIDs) {
1114: 		auto gem = PlayerWheelGem::load(gemsKV(), uuid);
1115: 		if (!gem) {
1116: 			continue;
1117: 		}
1118: 		unlockedGems.emplace_back(gem);
```

### `src/creatures/players/components/wheel/player_wheel.cpp:1947`

```text
1943: 		}
1944: 	});
1945:
1946: 	for (const auto &uuid : sortedUnlockedGemGUIDs) {
1947: 		auto gem = PlayerWheelGem::load(gemsKV(), uuid);
1948: 		if (!gem) {
1949: 			continue;
1950: 		}
1951: 		m_revealedGems.emplace_back(gem);
```

### `src/creatures/players/components/wheel/player_wheel.cpp:4363`

```text
4359: void PlayerWheelGem::remove(const std::shared_ptr<KV> &kv) const {
4360: 	kv->scoped("revealed")->remove(uuid);
4361: }
4362:
4363: PlayerWheelGem PlayerWheelGem::load(const std::shared_ptr<KV> &kv, const std::string &uuid) {
4364: 	auto val = kv->scoped("revealed")->get(uuid);
4365: 	if (!val || !val.has_value()) {
4366: 		return {};
4367: 	}
```

### `src/creatures/players/components/wheel/player_wheel.hpp:63`

```text
59: 	void save(const std::shared_ptr<KV> &kv) const;
60:
61: 	void remove(const std::shared_ptr<KV> &kv) const;
62:
63: 	static PlayerWheelGem load(const std::shared_ptr<KV> &kv, const std::string &uuid);
64:
65: private:
66: 	ValueWrapper serialize() const;
67:
```

### `src/creatures/players/grouping/groups.cpp:48`

```text
44:
45: bool Groups::reload() {
46: 	// Clear groups
47: 	g_game().groups.getGroups().clear();
48: 	return g_game().groups.load();
49: }
50:
51: void parseGroupFlags(Group &group, const pugi::xml_node &groupNode) {
52: 	if (const pugi::xml_node node = groupNode.child("flags")) {
```

### `src/creatures/players/grouping/groups.cpp:69`

```text
65: 		}
66: 	}
67: }
68:
69: bool Groups::load() {
70: 	pugi::xml_document doc;
71: 	const auto folder = g_configManager().getString(CORE_DIRECTORY) + "/XML/groups.xml";
72: 	const pugi::xml_parse_result result = doc.load_file(folder.c_str());
73: 	if (!result) {
```

### `src/creatures/players/grouping/groups.hpp:28`

```text
24: public:
25: 	static uint8_t getFlagNumber(PlayerFlags_t playerFlags);
26: 	static PlayerFlags_t getFlagFromNumber(uint8_t value);
27: 	static bool reload();
28: 	bool load();
29: 	[[nodiscard]] std::shared_ptr<Group> getGroup(uint16_t id) const;
30: 	std::vector<std::shared_ptr<Group>> &getGroups();
31:
32: private:
```

### `src/creatures/players/player.cpp:12517`

```text
12513: 		return true;
12514: 	}
12515:
12516: 	account = std::make_shared<Account>(accountId);
12517: 	return AccountErrors_t::Ok == account->load();
12518: }
12519:
12520: uint8_t Player::getAccountType() const {
12521: 	return account ? account->getAccountType() : AccountType::ACCOUNT_TYPE_NORMAL;
```

### `src/game/functions/game_reload.cpp:110`

```text
106: 	return std::ranges::any_of(reloadResults, [](bool result) { return result; });
107: }
108:
109: bool GameReload::reloadChat() {
110: 	const bool result = g_chat().load();
111: 	logReloadStatus("Chat", result);
112: 	return result;
113: }
114:
```

### `src/game/game.cpp:921`

```text
917: 	switch (newState) {
918: 		case GAME_STATE_INIT: {
919: 			loadItemsPrice();
920:
921: 			groups.load();
922: 			g_chat().load();
923:
924: 			// Load monsters and npcs stored by the "loadFromXML" function
925: 			map.spawnsMonster.startup();
```

### `src/game/game.cpp:922`

```text
918: 		case GAME_STATE_INIT: {
919: 			loadItemsPrice();
920:
921: 			groups.load();
922: 			g_chat().load();
923:
924: 			// Load monsters and npcs stored by the "loadFromXML" function
925: 			map.spawnsMonster.startup();
926: 			map.spawnsNpc.startup();
```

### `src/game/game.cpp:7674`

```text
7670: }
7671:
7672: void Game::removeCreatureCheck(const std::shared_ptr<Creature> &creature) {
7673: 	metrics::method_latency measure(__METRICS_METHOD_NAME__);
7674: 	if (creature->inCheckCreaturesVector.load()) {
7675: 		creature->creatureCheck.store(false);
7676: 	}
7677: }
7678:
```

### `src/game/scheduling/dispatcher.cpp:148`

```text
144: 	if (tasks.empty()) {
145: 		return;
146: 	}
147:
148: 	if (!queueLatencyLoggingEnabled.load(std::memory_order_acquire)) {
149: 		return;
150: 	}
151:
152: 	const auto gameState = g_game().getGameState();
```

### `src/game/scheduling/dispatcher.cpp:158`

```text
154: 		return;
155: 	}
156:
157: 	const auto now = OTSYS_TIME();
158: 	const auto loggingStartedAt = queueLatencyLoggingStartedAt.load(std::memory_order_relaxed);
159: 	int64_t oldestAge = 0;
160: 	size_t queuedAfterLoggingStart = 0;
161: 	std::string_view oldestContext;
162: 	for (const auto &task : tasks) {
```

### `src/game/scheduling/save_manager.cpp:110`

```text
106: 		return;
107: 	}
108:
109: 	threadPool.detach_task([this, scheduledAt]() {
110: 		if (m_scheduledAt.load() != scheduledAt) {
111: 			logger.warn("Skipping save for server because another save has been scheduled.");
112: 			return;
113: 		}
114: 		saveAll();
```

### `src/io/functions/iologindata_load_player.cpp:765`

```text
761: 		g_logger().warn("[{}] - Player nullptr", __FUNCTION__);
762: 		return;
763: 	}
764:
765: 	auto rows = g_playerStorageRepository().load(player->getGUID());
766: 	player->storage().ingest(rows);
767: }
768:
769: void IOLoginDataLoad::loadPlayerVip(const std::shared_ptr<Player> &player, DBResult_ptr result) {
```

### `src/io/functions/iologindata_load_player.cpp:910`

```text
906: 		g_logger().warn("[{}] - Player nullptr", __FUNCTION__);
907: 		return;
908: 	}
909:
910: 	if (!player->forgeHistory().load()) {
911: 		g_logger().warn("[{}] - Failed to load forge history for player: {}", __FUNCTION__, player->getName());
912: 	}
913: }
914:
```

### `src/io/functions/iologindata_load_player.cpp:1015`

```text
1011: 	player->badge().checkAndUpdateNewBadges();
1012: 	player->title().checkAndUpdateNewTitles();
1013: 	player->cyclopedia().loadSummaryData();
1014:
1015: 	player->weaponProficiency().load();
1016:
1017: 	player->initializePrey();
1018: 	player->initializeTaskHunting();
1019: 	// Load and apply the player's Virtue from the saved spell data, if available
```

### `src/io/iologindata.cpp:34`

```text
30: 			g_logger().warn("IP [{}] trying to connect into another account character", convertIPToString(ip));
31: 			return false;
32: 		}
33:
34: 		if (AccountErrors_t::Ok != account.load()) {
35: 			g_logger().error("Failed to load account [{}]", account.getID());
36: 			return false;
37: 		}
38:
```

### `src/io/iologindata.cpp:59`

```text
55: bool IOLoginData::gameWorldAuthentication(const std::string &accountDescriptor, const std::string &password, std::string &characterName, uint32_t &accountId, bool oldProtocol, const uint32_t ip, std::optional<uint32_t> preAuthenticatedAccountId) {
56: 	if (preAuthenticatedAccountId) {
57: 		Account account(*preAuthenticatedAccountId);
58: 		account.setProtocolCompat(oldProtocol);
59: 		if (AccountErrors_t::Ok != account.load()) {
60: 			g_logger().error("Couldn't load pre-authenticated account [{}].", *preAuthenticatedAccountId);
61: 			return false;
62: 		}
63:
```

### `src/io/iologindata.cpp:70`

```text
66:
67: 	Account account(accountDescriptor);
68: 	account.setProtocolCompat(oldProtocol);
69:
70: 	if (AccountErrors_t::Ok != account.load()) {
71: 		g_logger().error("Couldn't load account [{}].", account.getDescriptor());
72: 		return false;
73: 	}
74:
```

### `src/io/player_storage_repository.hpp:29`

```text
25: 	 * @brief Loads all storage rows for a given player.
26: 	 * @param playerId Database GUID of the player.
27: 	 * @return Vector of key/value rows. Empty if none exist.
28: 	 */
29: 	virtual std::vector<PlayerStorageRow> load(uint32_t playerId) = 0;
30:
31: 	/**
32: 	 * @brief Deletes a batch of storage keys for a player.
33: 	 * @param playerId Database GUID of the player.
```

### `src/io/player_storage_repository_db.cpp:25`

```text
21: 	#include <fmt/format.h>
22: 	#include <fmt/ranges.h>
23: #endif
24:
25: std::vector<PlayerStorageRow> DbPlayerStorageRepository::load(uint32_t id) {
26: 	std::vector<PlayerStorageRow> out;
27: 	auto query = fmt::format("SELECT `key`,`value` FROM `player_storage` WHERE `player_id`={}", id);
28: 	if (auto result = Database::getInstance().storeQuery(query)) {
29: 		do {
```

### `src/io/player_storage_repository_db.hpp:29`

```text
25: 	 * @brief Loads all storage rows for a player from the database.
26: 	 * @param playerId Player GUID.
27: 	 * @return Vector of PlayerStorageRow with all key/value pairs.
28: 	 */
29: 	std::vector<PlayerStorageRow> load(uint32_t playerId) override;
30:
31: 	/**
32: 	 * @brief Deletes a batch of storage keys for a player in the database.
33: 	 * @param playerId Player GUID.
```

### `src/kv/kv.cpp:89`

```text
85: 			}
86: 		}
87: 	}
88:
89: 	auto value = load(key);
90: 	if (value) {
91: 		{
92: 			std::scoped_lock lock(mutex_);
93: 			setLocked(key, *value);
```

### `src/kv/kv.hpp:122`

```text
118:
119: protected:
120: 	Logger &logger;
121:
122: 	virtual std::optional<ValueWrapper> load(const std::string &key) = 0;
123: 	virtual bool save(const std::string &key, const ValueWrapper &value) = 0;
124: 	virtual std::vector<std::string> loadPrefix(const std::string &prefix = "") = 0;
125:
126: private:
```

### `src/kv/kv_sql.cpp:21`

```text
17:
18: KVSQL::KVSQL(Database &db, Logger &logger) :
19: 	KVStore(logger), db(db) { }
20:
21: std::optional<ValueWrapper> KVSQL::load(const std::string &key) {
22: 	const auto query = fmt::format("SELECT `key_name`, `timestamp`, `value` FROM `kv_store` WHERE `key_name` = {}", db.escapeString(key));
23: 	const auto result = db.storeQuery(query);
24: 	if (result == nullptr) {
25: 		return std::nullopt;
```

### `src/kv/kv_sql.hpp:27`

```text
23: 	bool saveAll() override;
24:
25: private:
26: 	std::vector<std::string> loadPrefix(const std::string &prefix = "") override;
27: 	std::optional<ValueWrapper> load(const std::string &key) override;
28: 	bool save(const std::string &key, const ValueWrapper &value) override;
29: 	bool prepareSave(const std::string &key, const ValueWrapper &value, DBInsert &update) const;
30:
31: 	DBInsert dbUpdate();
```

### `src/lib/thread/thread_pool.hpp:56`

```text
52: 		thread_local static int16_t id = -1;
53:
54: 		if (id == -1) {
55: 			lastId.fetch_add(1);
56: 			id = lastId.load();
57: 		}
58:
59: 		return id;
60: 	}
```

### `src/lua/functions/lua_functions_loader.cpp:33`

```text
29: #include "enums/lua_variant_type.hpp"
30:
31: class LuaScriptInterface;
32:
33: void Lua::load(lua_State* L) {
34: 	if (!L) {
35: 		g_game().dieSafely("Invalid lua state, cannot load lua functions.");
36: 	}
37:
```

### `src/lua/functions/lua_functions_loader.hpp:186`

```text
182: #define reportErrorFunc(a) reportError(__FUNCTION__, a, true)
183:
184: class Lua {
185: public:
186: 	static void load(lua_State* L);
187:
188: 	static std::string getErrorDesc(ErrorCode_t code);
189:
190: 	static void reportError(const char* function, const std::string &error_desc, bool stack_trace = false);
```

### `src/lua/scripts/lua_environment.cpp:51`

```text
47: }
48:
49: bool LuaEnvironment::initState() {
50: 	luaState = luaL_newstate();
51: 	Lua::load(luaState);
52: 	runningEventId = EVENT_ID_USER;
53:
54: 	return true;
55: }
```

### `src/lua/scripts/luascript.cpp:507`

```text
503:
504: LuaBytecodeCacheStats LuaScriptInterface::getBytecodeCacheStats() {
505: 	const auto &stats = getMutableLuaBytecodeCacheStats();
506: 	return LuaBytecodeCacheStats {
507: 		.packHits = stats.packHits.load(std::memory_order_relaxed),
508: 		.fileHits = stats.fileHits.load(std::memory_order_relaxed),
509: 		.misses = stats.misses.load(std::memory_order_relaxed),
510: 		.writes = stats.writes.load(std::memory_order_relaxed),
511: 		.packInvalidations = stats.packInvalidations.load(std::memory_order_relaxed),
```

### `src/lua/scripts/luascript.cpp:508`

```text
504: LuaBytecodeCacheStats LuaScriptInterface::getBytecodeCacheStats() {
505: 	const auto &stats = getMutableLuaBytecodeCacheStats();
506: 	return LuaBytecodeCacheStats {
507: 		.packHits = stats.packHits.load(std::memory_order_relaxed),
508: 		.fileHits = stats.fileHits.load(std::memory_order_relaxed),
509: 		.misses = stats.misses.load(std::memory_order_relaxed),
510: 		.writes = stats.writes.load(std::memory_order_relaxed),
511: 		.packInvalidations = stats.packInvalidations.load(std::memory_order_relaxed),
512: 		.fileInvalidations = stats.fileInvalidations.load(std::memory_order_relaxed),
```

### `src/lua/scripts/luascript.cpp:509`

```text
505: 	const auto &stats = getMutableLuaBytecodeCacheStats();
506: 	return LuaBytecodeCacheStats {
507: 		.packHits = stats.packHits.load(std::memory_order_relaxed),
508: 		.fileHits = stats.fileHits.load(std::memory_order_relaxed),
509: 		.misses = stats.misses.load(std::memory_order_relaxed),
510: 		.writes = stats.writes.load(std::memory_order_relaxed),
511: 		.packInvalidations = stats.packInvalidations.load(std::memory_order_relaxed),
512: 		.fileInvalidations = stats.fileInvalidations.load(std::memory_order_relaxed),
513: 	};
```

### `src/lua/scripts/luascript.cpp:510`

```text
506: 	return LuaBytecodeCacheStats {
507: 		.packHits = stats.packHits.load(std::memory_order_relaxed),
508: 		.fileHits = stats.fileHits.load(std::memory_order_relaxed),
509: 		.misses = stats.misses.load(std::memory_order_relaxed),
510: 		.writes = stats.writes.load(std::memory_order_relaxed),
511: 		.packInvalidations = stats.packInvalidations.load(std::memory_order_relaxed),
512: 		.fileInvalidations = stats.fileInvalidations.load(std::memory_order_relaxed),
513: 	};
514: }
```

### `src/lua/scripts/luascript.cpp:511`

```text
507: 		.packHits = stats.packHits.load(std::memory_order_relaxed),
508: 		.fileHits = stats.fileHits.load(std::memory_order_relaxed),
509: 		.misses = stats.misses.load(std::memory_order_relaxed),
510: 		.writes = stats.writes.load(std::memory_order_relaxed),
511: 		.packInvalidations = stats.packInvalidations.load(std::memory_order_relaxed),
512: 		.fileInvalidations = stats.fileInvalidations.load(std::memory_order_relaxed),
513: 	};
514: }
515:
```

### `src/lua/scripts/luascript.cpp:512`

```text
508: 		.fileHits = stats.fileHits.load(std::memory_order_relaxed),
509: 		.misses = stats.misses.load(std::memory_order_relaxed),
510: 		.writes = stats.writes.load(std::memory_order_relaxed),
511: 		.packInvalidations = stats.packInvalidations.load(std::memory_order_relaxed),
512: 		.fileInvalidations = stats.fileInvalidations.load(std::memory_order_relaxed),
513: 	};
514: }
515:
516: /// Same as lua_pcall, but adds stack trace to error strings in called function.
```

### `src/map/map.cpp:45`

```text
41: 		return tile;
42: 	}
43: }
44:
45: void Map::load(const std::string &identifier, const Position &pos) {
46: 	try {
47: 		path = identifier;
48: 		IOMap::loadMap(this, pos);
49: 	} catch (const std::exception &e) {
```

### `src/map/map.cpp:80`

```text
76: 		}
77: 	}
78:
79: 	// Load the map
80: 	load(identifier, pos);
81:
82: 	// Only create items from lua functions if is loading main map
83: 	// It needs to be after the load map to ensure the map already exists before creating the items
84: 	if (mainMap) {
```

### `src/map/map.cpp:130`

```text
126: }
127:
128: void Map::loadMapCustom(const std::string &mapName, bool loadHouses, bool loadMonsters, bool loadNpcs, bool loadZones, int customMapIndex) {
129: 	// Load the map
130: 	load(g_configManager().getString(DATA_DIRECTORY) + "/world/custom/" + mapName + ".otbm");
131:
132: 	if (loadMonsters && !IOMap::loadMonstersCustom(this, mapName, customMapIndex)) {
133: 		g_logger().warn("Failed to load monster custom data");
134: 	}
```

### `src/map/map.hpp:44`

```text
40: 	/**
41: 	 * Load a map.
42: 	 * \returns true if the map was loaded successfully
43: 	 */
44: 	void load(const std::string &identifier, const Position &pos = Position());
45: 	/**
46: 	 * Load the main map
47: 	 * \param identifier Is the main map name (name of file .otbm)
48: 	 * \param loadHouses if true, the main map houses is loaded
```

### `src/server/network/protocol/protocollogin.cpp:50`

```text
46: 		disconnectClient(ProtocolProfileRegistry::getUnsupportedClientProtocolMessage(false));
47: 		return;
48: 	}
49:
50: 	if (account.load() != AccountErrors_t::Ok || !account.authenticate(password)) {
51: 		std::ostringstream ss;
52: 		ss << (oldProtocol ? "Username" : "Email") << " or password is not correct.";
53: 		disconnectClient(ss.str());
54: 		return;
```

### `src/server/signals.cpp:131`

```text
127:
128: 	g_events().loadFromXml();
129: 	g_logger().info("Reloaded events");
130:
131: 	g_chat().load();
132: 	g_logger().info("Reloaded chatchannels");
133:
134: 	g_luaEnvironment().loadFile(g_configManager().getString(CORE_DIRECTORY) + "/core.lua", "core.lua");
135: 	g_logger().info("Reloaded core.lua");
```

### `tests/fixture/kv/in_memory_kv.hpp:41`

```text
37: protected:
38: 	std::vector<std::string> loadPrefix(const std::string &prefix = "") override {
39: 		return {};
40: 	}
41: 	std::optional<ValueWrapper> load(const std::string &key) override {
42: 		return std::nullopt;
43: 	}
44: 	bool save(const std::string &key, const ValueWrapper &value) override {
45: 		return false;
```

### `tests/integration/game/otbm_loader_it.cpp:76`

```text
72: 	ASSERT_TRUE(std::filesystem::is_regular_file(editedMap));
73: 	ASSERT_TRUE(std::filesystem::is_regular_file(temporaryDirectory.path / "manifest.json"));
74:
75: 	Map map;
76: 	map.load(editedMap.string());
77:
78: 	const auto patchedTile = map.getTile(Position(300, 600, 7));
79: 	ASSERT_NE(patchedTile, nullptr) << "Canary did not materialize the patched tile";
80:
```

### `tests/integration/main.cpp:139`

```text
135: 	std::fprintf(stderr, "[integration main] config reload done\n");
136: 	std::fflush(stderr);
137:
138: 	if (!dbOnlyFilter) {
139: 		if (!g_game().groups.load()) {
140: 			std::fprintf(stderr, "[integration main] failed to load groups\n");
141: 			std::fflush(stderr);
142: 			return EXIT_FAILURE;
143: 		}
```

### `tests/integration/player_storage/player_storage_repository_db_it.cpp:63`

```text
59: 			DbPlayerStorageRepository repo {};
60: 			auto ids = getTestIds();
61: 			ASSERT_TRUE(createPlayer(db, ids.accountId, ids.playerId));
62: 			ASSERT_TRUE(db.executeQuery(fmt::format("INSERT INTO `player_storage` (`player_id`,`key`,`value`) VALUES ({}, 100, 42), ({}, 200, 55)", ids.playerId, ids.playerId)));
63: 			auto rows = repo.load(ids.playerId);
64: 			ASSERT_EQ(2u, rows.size());
65: 			EXPECT_TRUE(hasRow(rows, 100, 42));
66: 			EXPECT_TRUE(hasRow(rows, 200, 55));
67: 		})();
```

### `tests/integration/player_storage/player_storage_repository_db_it.cpp:78`

```text
74: 			auto ids = getTestIds();
75: 			ASSERT_TRUE(createPlayer(db, ids.accountId, ids.playerId));
76: 			ASSERT_TRUE(db.executeQuery(fmt::format("INSERT INTO `player_storage` (`player_id`,`key`,`value`) VALUES ({}, 1, 10), ({}, 2, 20), ({}, 3, 30)", ids.playerId, ids.playerId, ids.playerId)));
77: 			EXPECT_TRUE(repo.deleteKeys(ids.playerId, { 1, 3 }));
78: 			auto rows = repo.load(ids.playerId);
79: 			ASSERT_EQ(1u, rows.size());
80: 			EXPECT_EQ(2u, rows[0].key);
81: 			EXPECT_EQ(20, rows[0].value);
82: 		})();
```

### `tests/integration/player_storage/player_storage_repository_db_it.cpp:92`

```text
88: 			DbPlayerStorageRepository repo {};
89: 			auto ids = getTestIds();
90: 			ASSERT_TRUE(createPlayer(db, ids.accountId, ids.playerId));
91: 			EXPECT_TRUE(repo.upsert(ids.playerId, { { 1, 10 }, { 2, 20 } }));
92: 			auto rows = repo.load(ids.playerId);
93: 			EXPECT_EQ(2u, rows.size());
94: 			EXPECT_TRUE(hasRow(rows, 1, 10));
95: 			EXPECT_TRUE(hasRow(rows, 2, 20));
96: 			EXPECT_TRUE(repo.upsert(ids.playerId, { { 1, 100 } }));
```

### `tests/integration/player_storage/player_storage_repository_db_it.cpp:97`

```text
93: 			EXPECT_EQ(2u, rows.size());
94: 			EXPECT_TRUE(hasRow(rows, 1, 10));
95: 			EXPECT_TRUE(hasRow(rows, 2, 20));
96: 			EXPECT_TRUE(repo.upsert(ids.playerId, { { 1, 100 } }));
97: 			auto rows2 = repo.load(ids.playerId);
98: 			EXPECT_TRUE(hasRow(rows2, 1, 100));
99: 			EXPECT_TRUE(hasRow(rows2, 2, 20));
100: 		})();
101: 	}
```

### `tests/integration/test_env.hpp:18`

```text
14: 		db.executeQuery("BEGIN");
15:
16: 		std::exception_ptr ep {};
17: 		try {
18: 			load();
19: 		} catch (const DatabaseException &) {
20: 			ep = std::current_exception();
21: 		} catch (const std::exception &e) {
22: 			std::fprintf(stderr, "[databaseTest] std::exception: %s\n", e.what());
```

### `tests/unit/account/account_test.cpp:111`

```text
107:
108: TEST_F(AccountTest, LoadReturnsByIdIfExists) {
109: 	repository().addAccount("canary@test.com", AccountInfo { 1, 1, 1, AccountType::ACCOUNT_TYPE_GOD });
110: 	auto account = make_shared<Account>(1);
111: 	EXPECT_TRUE(eqEnum(account->load(), AccountErrors_t::Ok));
112: }
113:
114: TEST_F(AccountTest, LoadReturnsByDescriptorIfExists) {
115: 	repository().addAccount("canary@test.com", AccountInfo { 1, 1, 1, AccountType::ACCOUNT_TYPE_GOD });
```

### `tests/unit/account/account_test.cpp:117`

```text
113:
114: TEST_F(AccountTest, LoadReturnsByDescriptorIfExists) {
115: 	repository().addAccount("canary@test.com", AccountInfo { 1, 1, 1, AccountType::ACCOUNT_TYPE_GOD });
116: 	auto account = make_shared<Account>("canary@test.com");
117: 	EXPECT_TRUE(eqEnum(account->load(), AccountErrors_t::Ok));
118: }
119:
120: TEST_F(AccountTest, LoadReturnsErrorIfIdInvalid) {
121: 	repository().addAccount("canary@test.com", AccountInfo { 1, 1, 1, AccountType::ACCOUNT_TYPE_GOD });
```

### `tests/unit/account/account_test.cpp:123`

```text
119:
120: TEST_F(AccountTest, LoadReturnsErrorIfIdInvalid) {
121: 	repository().addAccount("canary@test.com", AccountInfo { 1, 1, 1, AccountType::ACCOUNT_TYPE_GOD });
122: 	auto account = make_shared<Account>(2);
123: 	EXPECT_TRUE(eqEnum(account->load(), AccountErrors_t::LoadingAccount));
124: }
125:
126: TEST_F(AccountTest, LoadReturnsErrorIfDescriptorInvalid) {
127: 	repository().addAccount("canary@test.com", AccountInfo { 1, 1, 1, AccountType::ACCOUNT_TYPE_GOD });
```

### `tests/unit/account/account_test.cpp:129`

```text
125:
126: TEST_F(AccountTest, LoadReturnsErrorIfDescriptorInvalid) {
127: 	repository().addAccount("canary@test.com", AccountInfo { 1, 1, 1, AccountType::ACCOUNT_TYPE_GOD });
128: 	auto account = make_shared<Account>("not@valid.com");
129: 	EXPECT_TRUE(eqEnum(account->load(), AccountErrors_t::LoadingAccount));
130: }
131:
132: TEST_F(AccountTest, ReloadReturnsErrorIfNotYetLoaded) {
133: 	EXPECT_TRUE(eqEnum(Account { 1 }.reload(), AccountErrors_t::NotInitialized));
```

### `tests/unit/account/account_test.cpp:140`

```text
136: TEST_F(AccountTest, ReloadReloadsAccountInfo) {
137: 	Account acc { 1 };
138: 	repository().addAccount("canary@test.com", AccountInfo { 1, 1, 1, AccountType::ACCOUNT_TYPE_GOD });
139:
140: 	EXPECT_TRUE(eqEnum(acc.load(), AccountErrors_t::Ok));
141: 	EXPECT_TRUE(eqEnum(acc.getAccountType(), AccountType::ACCOUNT_TYPE_GOD));
142:
143: 	repository().addAccount("canary@test.com", AccountInfo { 1, 1, 1, AccountType::ACCOUNT_TYPE_GAMEMASTER });
144:
```

### `tests/unit/account/account_test.cpp:158`

```text
154: 	Account acc { 1 };
155: 	repository().failSave = true;
156: 	repository().addAccount("canary@test.com", AccountInfo { 1, 1, 1, AccountType::ACCOUNT_TYPE_GOD });
157:
158: 	EXPECT_TRUE(eqEnum(acc.load(), AccountErrors_t::Ok));
159: 	EXPECT_TRUE(eqEnum(acc.save(), AccountErrors_t::Storage));
160: }
161:
162: TEST_F(AccountTest, SavePersistsAccountInfo) {
```

### `tests/unit/account/account_test.cpp:167`

```text
163: 	Account acc { 1 };
164: 	repository().failSave = false;
165: 	repository().addAccount("canary@test.com", AccountInfo { 1, 1, 1, AccountType::ACCOUNT_TYPE_GOD });
166:
167: 	EXPECT_TRUE(eqEnum(acc.load(), AccountErrors_t::Ok));
168: 	EXPECT_TRUE(eqEnum(acc.save(), AccountErrors_t::Ok));
169: }
170:
171: TEST_F(AccountTest, GetCoinsReturnsErrorIfNotYetLoaded) {
```

### `tests/unit/account/account_test.cpp:181`

```text
177: TEST_F(AccountTest, GetCoinsReturnsErrorIfRepositoryFails) {
178: 	Account acc { 1 };
179: 	repository().addAccount("canary@test.com", AccountInfo { 1, 1, 1, AccountType::ACCOUNT_TYPE_GOD });
180:
181: 	EXPECT_TRUE(eqEnum(acc.load(), AccountErrors_t::Ok));
182: 	auto [coins, error] = acc.getCoins(Normal);
183: 	EXPECT_EQ(0, coins);
184: 	EXPECT_TRUE(eqEnum(error, AccountErrors_t::Storage));
185: }
```

### `tests/unit/account/account_test.cpp:192`

```text
188: 	Account acc { 1 };
189: 	repository().addAccount("canary@test.com", AccountInfo { 1, 1, 1, AccountType::ACCOUNT_TYPE_GOD });
190: 	expectSetCoins(repository(), 1, Normal, 100);
191:
192: 	EXPECT_TRUE(eqEnum(acc.load(), AccountErrors_t::Ok));
193: 	auto [coins, error] = acc.getCoins(Normal);
194: 	EXPECT_EQ(100, coins);
195: 	EXPECT_TRUE(eqEnum(error, AccountErrors_t::Ok));
196: }
```

### `tests/unit/account/account_test.cpp:206`

```text
202:
203: 	repository().addAccount("canary2@test.com", AccountInfo { 2, 1, 1, AccountType::ACCOUNT_TYPE_GOD });
204: 	expectSetCoins(repository(), 2, Normal, 33);
205:
206: 	EXPECT_TRUE(eqEnum(acc.load(), AccountErrors_t::Ok));
207: 	auto [coins, error] = acc.getCoins(Normal);
208: 	EXPECT_EQ(33, coins);
209: 	EXPECT_TRUE(eqEnum(error, AccountErrors_t::Ok));
210: }
```

### `tests/unit/account/account_test.cpp:218`

```text
214: 	repository().addAccount("canary@test.com", AccountInfo { 1, 1, 1, AccountType::ACCOUNT_TYPE_GOD });
215: 	expectSetCoins(repository(), 1, Normal, 100);
216: 	expectSetCoins(repository(), 1, Tournament, 100);
217:
218: 	EXPECT_TRUE(eqEnum(acc.load(), AccountErrors_t::Ok));
219:
220: 	auto [normalCoins, normalError] = acc.getCoins(Normal);
221: 	EXPECT_EQ(100, normalCoins);
222: 	EXPECT_TRUE(eqEnum(normalError, AccountErrors_t::Ok));
```

### `tests/unit/account/account_test.cpp:239`

```text
235: 	repository().failAddCoins = true;
236: 	repository().addAccount("canary@test.com", AccountInfo { 1, 1, 1, AccountType::ACCOUNT_TYPE_GOD });
237: 	expectSetCoins(repository(), 1, Normal, 100);
238:
239: 	EXPECT_TRUE(eqEnum(acc.load(), AccountErrors_t::Ok));
240: 	EXPECT_TRUE(eqEnum(acc.addCoins(Normal, 100), AccountErrors_t::Storage));
241: }
242:
243: TEST_F(AccountTest, AddCoinsReturnsErrorIfGetCoinsFails) {
```

### `tests/unit/account/account_test.cpp:248`

```text
244: 	Account acc { 1 };
245: 	repository().addAccount("canary@test.com", AccountInfo { 1, 1, 1, AccountType::ACCOUNT_TYPE_GOD });
246: 	expectSetCoins(repository(), 1, Normal, 100);
247:
248: 	EXPECT_TRUE(eqEnum(acc.load(), AccountErrors_t::Ok));
249: 	EXPECT_TRUE(eqEnum(acc.addCoins(Tournament, 100), AccountErrors_t::Storage));
250: }
251:
252: TEST_F(AccountTest, AddCoinsAddsCoins) {
```

### `tests/unit/account/account_test.cpp:258`

```text
254: 	repository().failAddCoins = false;
255: 	repository().addAccount("canary@test.com", AccountInfo { 1, 1, 1, AccountType::ACCOUNT_TYPE_GOD });
256: 	expectSetCoins(repository(), 1, Normal, 100);
257:
258: 	EXPECT_TRUE(eqEnum(acc.load(), AccountErrors_t::Ok));
259: 	EXPECT_TRUE(eqEnum(acc.addCoins(Normal, 100), AccountErrors_t::Ok));
260:
261: 	auto [coins, error] = acc.getCoins(Normal);
262: 	EXPECT_EQ(200, coins);
```

### `tests/unit/account/account_test.cpp:275`

```text
271:
272: 	repository().addAccount("canary2@test.com", AccountInfo { 2, 1, 1, AccountType::ACCOUNT_TYPE_GOD });
273: 	expectSetCoins(repository(), 2, Normal, 33);
274:
275: 	EXPECT_TRUE(eqEnum(acc.load(), AccountErrors_t::Ok));
276: 	EXPECT_TRUE(eqEnum(acc.addCoins(Normal, 100), AccountErrors_t::Ok));
277:
278: 	auto [coins, error] = acc.getCoins(Normal);
279: 	EXPECT_EQ(133, coins);
```

### `tests/unit/account/account_test.cpp:290`

```text
286: 	expectSetCoins(repository(), 1, Normal, 100);
287: 	expectSetCoins(repository(), 1, Tournament, 57);
288: 	repository().addAccount("canary@test.com", AccountInfo { 1, 1, 1, AccountType::ACCOUNT_TYPE_GOD });
289:
290: 	EXPECT_TRUE(eqEnum(acc.load(), AccountErrors_t::Ok));
291: 	EXPECT_TRUE(eqEnum(acc.addCoins(Normal, 100), AccountErrors_t::Ok));
292:
293: 	auto [normalCoins, normalError] = acc.getCoins(Normal);
294: 	EXPECT_EQ(200, normalCoins);
```

### `tests/unit/account/account_test.cpp:321`

```text
317: 	repository().addAccount("canary@test.com", AccountInfo { 1, 1, 1, AccountType::ACCOUNT_TYPE_GOD });
318: 	expectSetCoins(repository(), 1, Normal, 100);
319:
320: 	repository().failAddCoins = true;
321: 	EXPECT_TRUE(eqEnum(acc.load(), AccountErrors_t::Ok));
322: 	EXPECT_TRUE(eqEnum(acc.removeCoins(Normal, 100), AccountErrors_t::Storage));
323: }
324:
325: TEST_F(AccountTest, RemoveCoinsReturnsErrorIfGetCoinsFails) {
```

### `tests/unit/account/account_test.cpp:330`

```text
326: 	Account acc { 1 };
327: 	repository().addAccount("canary@test.com", AccountInfo { 1, 1, 1, AccountType::ACCOUNT_TYPE_GOD });
328: 	expectSetCoins(repository(), 1, Normal, 100);
329:
330: 	EXPECT_TRUE(eqEnum(acc.load(), AccountErrors_t::Ok));
331: 	EXPECT_TRUE(eqEnum(acc.removeCoins(Tournament, 100), AccountErrors_t::Storage));
332: }
333:
334: TEST_F(AccountTest, RemoveCoinsRemovesCoins) {
```

### `tests/unit/account/account_test.cpp:340`

```text
336: 	repository().failAddCoins = false;
337: 	repository().addAccount("canary@test.com", AccountInfo { 1, 1, 1, AccountType::ACCOUNT_TYPE_GOD });
338: 	expectSetCoins(repository(), 1, Normal, 100);
339:
340: 	EXPECT_TRUE(eqEnum(acc.load(), AccountErrors_t::Ok));
341: 	EXPECT_TRUE(eqEnum(acc.removeCoins(Normal, 100), AccountErrors_t::Ok));
342:
343: 	auto [coins, error] = acc.getCoins(Normal);
344: 	EXPECT_EQ(0, coins);
```

### `tests/unit/account/account_test.cpp:357`

```text
353:
354: 	repository().addAccount("canary2@test.com", AccountInfo { 2, 1, 1, AccountType::ACCOUNT_TYPE_GOD });
355: 	expectSetCoins(repository(), 2, Normal, 33);
356:
357: 	EXPECT_TRUE(eqEnum(acc.load(), AccountErrors_t::Ok));
358: 	EXPECT_TRUE(eqEnum(acc.removeCoins(Normal, 100), AccountErrors_t::Ok));
359:
360: 	auto [coins, error] = acc.getCoins(Normal);
361: 	EXPECT_EQ(0, coins);
```

### `tests/unit/account/account_test.cpp:372`

```text
368: 	repository().addAccount("canary@test.com", AccountInfo { 1, 1, 1, AccountType::ACCOUNT_TYPE_GOD });
369: 	expectSetCoins(repository(), 1, Normal, 100);
370: 	expectSetCoins(repository(), 1, Tournament, 57);
371:
372: 	EXPECT_TRUE(eqEnum(acc.load(), AccountErrors_t::Ok));
373: 	EXPECT_TRUE(eqEnum(acc.removeCoins(Normal, 100), AccountErrors_t::Ok));
374:
375: 	auto [normalCoins, normalError] = acc.getCoins(Normal);
376: 	EXPECT_EQ(0, normalCoins);
```

### `tests/unit/account/account_test.cpp:400`

```text
396: 	repository().addAccount("canary@test.com", AccountInfo { 1, 1, 1, AccountType::ACCOUNT_TYPE_GOD });
397: 	expectSetCoins(repository(), 1, Transferable, 80);
398: 	expectSetCoins(repository(), 1, Normal, 100);
399:
400: 	EXPECT_TRUE(eqEnum(acc.load(), AccountErrors_t::Ok));
401: 	EXPECT_TRUE(eqEnum(acc.removeCoins(Transferable, Normal, 130), AccountErrors_t::Ok));
402:
403: 	auto [transferableCoins, transferableError] = acc.getCoins(Transferable);
404: 	EXPECT_EQ(0, transferableCoins);
```

### `tests/unit/account/account_test.cpp:434`

```text
430: 	repository().addAccount("canary@test.com", AccountInfo { 1, 1, 1, AccountType::ACCOUNT_TYPE_GOD });
431: 	expectSetCoins(repository(), 1, Transferable, 40);
432: 	expectSetCoins(repository(), 1, Normal, 50);
433:
434: 	EXPECT_TRUE(eqEnum(acc.load(), AccountErrors_t::Ok));
435: 	EXPECT_TRUE(eqEnum(acc.removeCoins(Transferable, Normal, 100), AccountErrors_t::RemoveCoins));
436:
437: 	auto [transferableCoins, transferableError] = acc.getCoins(Transferable);
438: 	EXPECT_EQ(40, transferableCoins);
```

### `tests/unit/account/account_test.cpp:455`

```text
451: 	expectSetCoins(repository(), 1, Transferable, 80);
452: 	expectSetCoins(repository(), 1, Normal, 100);
453: 	repository().failAddCoins = true;
454:
455: 	EXPECT_TRUE(eqEnum(acc.load(), AccountErrors_t::Ok));
456: 	EXPECT_TRUE(eqEnum(acc.removeCoins(Transferable, Normal, 130), AccountErrors_t::Storage));
457:
458: 	auto [transferableCoins, transferableError] = acc.getCoins(Transferable);
459: 	EXPECT_EQ(80, transferableCoins);
```

### `tests/unit/account/account_test.cpp:475`

```text
471: 	repository().failAddCoins = false;
472: 	expectSetCoins(repository(), 1, Normal, 1);
473: 	repository().addAccount("canary@test.com", AccountInfo { 1, 1, 1, AccountType::ACCOUNT_TYPE_GOD });
474:
475: 	EXPECT_TRUE(eqEnum(acc.load(), AccountErrors_t::Ok));
476: 	EXPECT_TRUE(eqEnum(acc.removeCoins(Normal, 100), AccountErrors_t::RemoveCoins));
477:
478: 	expectSetCoins(repository(), 1, Normal, 50);
479: 	EXPECT_TRUE(eqEnum(acc.load(), AccountErrors_t::Ok));
```

### `tests/unit/account/account_test.cpp:479`

```text
475: 	EXPECT_TRUE(eqEnum(acc.load(), AccountErrors_t::Ok));
476: 	EXPECT_TRUE(eqEnum(acc.removeCoins(Normal, 100), AccountErrors_t::RemoveCoins));
477:
478: 	expectSetCoins(repository(), 1, Normal, 50);
479: 	EXPECT_TRUE(eqEnum(acc.load(), AccountErrors_t::Ok));
480: 	EXPECT_TRUE(eqEnum(acc.removeCoins(Normal, 100), AccountErrors_t::RemoveCoins));
481:
482: 	expectSetCoins(repository(), 1, Normal, 100);
483: 	EXPECT_TRUE(eqEnum(acc.load(), AccountErrors_t::Ok));
```

### `tests/unit/account/account_test.cpp:483`

```text
479: 	EXPECT_TRUE(eqEnum(acc.load(), AccountErrors_t::Ok));
480: 	EXPECT_TRUE(eqEnum(acc.removeCoins(Normal, 100), AccountErrors_t::RemoveCoins));
481:
482: 	expectSetCoins(repository(), 1, Normal, 100);
483: 	EXPECT_TRUE(eqEnum(acc.load(), AccountErrors_t::Ok));
484: 	EXPECT_TRUE(eqEnum(acc.removeCoins(Normal, 100), AccountErrors_t::Ok));
485:
486: 	ASSERT_EQ(1u, repository().coinsTransactions_.size());
487: 	ASSERT_EQ(1u, repository().coinsTransactions_[1].size());
```

### `tests/unit/account/account_test.cpp:495`

```text
491: 	EXPECT_TRUE(eqEnum(coinType, Normal));
492: 	EXPECT_TRUE(eqEnum(type, CoinTransactionType::Remove));
493: 	EXPECT_EQ(string { "REMOVE Coins" }, description);
494:
495: 	EXPECT_TRUE(eqEnum(acc.load(), AccountErrors_t::Ok));
496: 	EXPECT_TRUE(eqEnum(acc.removeCoins(Normal, 100), AccountErrors_t::RemoveCoins));
497:
498: 	ASSERT_EQ(1u, repository().coinsTransactions_.size());
499: 	ASSERT_EQ(1u, repository().coinsTransactions_[1].size());
```

### `tests/unit/account/account_test.cpp:505`

```text
501:
502: TEST_F(AccountTest, RegisterCoinTransactionDoesNothingIfDetailIsEmpty) {
503: 	Account acc { 1 };
504: 	repository().addAccount("canary@test.com", AccountInfo { 1, 1, 1, AccountType::ACCOUNT_TYPE_GOD });
505: 	EXPECT_TRUE(eqEnum(acc.load(), AccountErrors_t::Ok));
506: 	expectSetCoins(repository(), 1, Normal, 1);
507:
508: 	EXPECT_TRUE(eqEnum(acc.addCoins(Normal, 100, string {}), AccountErrors_t::Ok));
509: 	EXPECT_TRUE(eqEnum(acc.removeCoins(Normal, 80, string {}), AccountErrors_t::Ok));
```

### `tests/unit/account/account_test.cpp:529`

```text
525: TEST_F(AccountTest, GetPasswordReturnsPassword) {
526: 	Account acc { 1 };
527: 	repository().addAccount("canary@test.com", AccountInfo { 1, 1, 1, AccountType::ACCOUNT_TYPE_GOD });
528:
529: 	EXPECT_TRUE(eqEnum(acc.load(), AccountErrors_t::Ok));
530: 	EXPECT_EQ(string { "123456" }, acc.getPassword());
531: }
532:
533: TEST_F(AccountTest, GetPasswordLogsErrorOnFailure) {
```

### `tests/unit/account/account_test.cpp:538`

```text
534: 	Account acc { 1 };
535: 	repository().failGetPassword = true;
536: 	repository().addAccount("canary@test.com", AccountInfo { 1, 1, 1, AccountType::ACCOUNT_TYPE_GOD });
537:
538: 	EXPECT_TRUE(eqEnum(acc.load(), AccountErrors_t::Ok));
539: 	EXPECT_EQ(string {}, acc.getPassword());
540: 	ASSERT_FALSE(testLogger().logs.empty());
541: 	EXPECT_EQ(string { "error" }, testLogger().logs[0].level);
542: 	EXPECT_EQ(string { "Failed to get password for account[1]!" }, testLogger().logs[0].message);
```

### `tests/unit/account/account_test.cpp:636`

```text
632: 		"canary@test.com",
633: 		AccountInfo { 1, 1, 1, AccountType::ACCOUNT_TYPE_GOD, { { "Canary", 1 }, { "Canary2", 2 } } }
634: 	);
635:
636: 	EXPECT_TRUE(eqEnum(acc.load(), AccountErrors_t::Ok));
637: 	auto [players, error] = acc.getAccountPlayers();
638:
639: 	EXPECT_TRUE(eqEnum(error, AccountErrors_t::Ok));
640: 	ASSERT_EQ(2u, players.size());
```

### `tests/unit/account/account_test.cpp:652`

```text
648: 		"canary@test.com",
649: 		AccountInfo { 1, 1, 1, AccountType::ACCOUNT_TYPE_GOD, { { "Canary", 1 }, { "Canary2", 2 } } }
650: 	);
651:
652: 	EXPECT_TRUE(eqEnum(acc.load(), AccountErrors_t::Ok));
653: 	repository().password_ = "7c4a8d09ca3762af61e59520943dc26494f8941b";
654: 	EXPECT_TRUE(acc.authenticate("123456"));
655: }
656:
```

### `tests/unit/account/account_test.cpp:671`

```text
667: 			false,
668: 			getTimeNow() + 24 * 60 * 60 * 1000 }
669: 	);
670:
671: 	EXPECT_TRUE(eqEnum(acc.load(), AccountErrors_t::Ok));
672: 	EXPECT_TRUE(acc.authenticate());
673: }
674:
675: TEST_F(AccountTest, GetCharacterByAccountIdAndNameFindsCharacter) {
```

### `tests/unit/game/instance/instance_creature_ownership_policy_test.cpp:167`

```text
163: 	for (auto &thread : threads) {
164: 		thread.join();
165: 	}
166:
167: 	EXPECT_EQ(summonCount, successCount.load());
168: 	EXPECT_EQ(static_cast<std::size_t>(summonCount + 1), manager.registeredCreatureCount(instance.id));
169: }
```

### `tests/unit/game/instance/instance_manager_test.cpp:334`

```text
330: 	for (auto &thread : threads) {
331: 		thread.join();
332: 	}
333:
334: 	EXPECT_EQ(1, cleanupCalls.load());
335: 	EXPECT_EQ(InstanceState::Destroyed, *manager.getState(result.id));
336: 	EXPECT_EQ(1u, manager.availableSlotCount());
337: }
338:
```

### `tests/unit/game/instance/instance_manager_test.cpp:358`

```text
354: 	for (auto &thread : threads) {
355: 		thread.join();
356: 	}
357:
358: 	EXPECT_EQ(static_cast<int>(regionCount), successCount.load());
359: 	EXPECT_EQ(0u, manager.availableSlotCount());
360: 	EXPECT_EQ(regionCount, manager.activeInstanceCount());
361: }
```

### `tests/unit/game/multichannel/cluster_leader_election_test.cpp:139`

```text
135:
136: 	for (int i = 0; i < racerCount; ++i) {
137: 		threads.emplace_back([&, i] {
138: 			readyCount.fetch_add(1);
139: 			while (!go.load()) {
140: 				std::this_thread::yield();
141: 			}
142: 			results[static_cast<std::size_t>(i)] = election.acquire("market.expire", i, "instance-" + std::to_string(i), 30000, 1000);
143: 		});
```

### `tests/unit/game/multichannel/cluster_leader_election_test.cpp:146`

```text
142: 			results[static_cast<std::size_t>(i)] = election.acquire("market.expire", i, "instance-" + std::to_string(i), 30000, 1000);
143: 		});
144: 	}
145:
146: 	while (readyCount.load() < racerCount) {
147: 		std::this_thread::yield();
148: 	}
149: 	go.store(true);
150:
```

### `tests/unit/game/multichannel/cluster_session_manager_test.cpp:140`

```text
136:
137: 	for (int i = 0; i < racerCount; ++i) {
138: 		threads.emplace_back([&, i] {
139: 			readyCount.fetch_add(1);
140: 			while (!go.load()) {
141: 				std::this_thread::yield();
142: 			}
143: 			results[static_cast<std::size_t>(i)] = manager.acquire(7, i, "instance-" + std::to_string(i), 30000, 1000);
144: 		});
```

### `tests/unit/game/multichannel/cluster_session_manager_test.cpp:147`

```text
143: 			results[static_cast<std::size_t>(i)] = manager.acquire(7, i, "instance-" + std::to_string(i), 30000, 1000);
144: 		});
145: 	}
146:
147: 	while (readyCount.load() < racerCount) {
148: 		std::this_thread::yield();
149: 	}
150: 	go.store(true);
151:
```

### `tests/unit/game/multichannel/idempotency_test.cpp:110`

```text
106:
107: 	for (int i = 0; i < attempts; ++i) {
108: 		threads.emplace_back([&, i] {
109: 			readyCount.fetch_add(1);
110: 			while (!go.load()) {
111: 				std::this_thread::yield();
112: 			}
113: 			results[static_cast<std::size_t>(i)] = ledger.record("txn-shared", "mail.deliver");
114: 		});
```

### `tests/unit/game/multichannel/idempotency_test.cpp:116`

```text
112: 			}
113: 			results[static_cast<std::size_t>(i)] = ledger.record("txn-shared", "mail.deliver");
114: 		});
115: 	}
116: 	while (readyCount.load() < attempts) {
117: 		std::this_thread::yield();
118: 	}
119: 	go.store(true);
120: 	for (auto &thread : threads) {
```

### `tests/unit/security/login_session_manager_test.cpp:145`

```text
141: 	for (auto &thread : threads) {
142: 		thread.join();
143: 	}
144:
145: 	EXPECT_EQ(1, successCount.load());
146: }
```

### `tools/ai-agent/examples/otbm_hd_tibiasr2x_backend.py:68`

```text
64:             base = functional.interpolate(value[:, :3], scale_factor=2, mode="nearest")
65:             features = self.body(self.act(self.head(value)))
66:             return (base + torch.tanh(self.tail(features)) * 0.25).clamp(0, 1)
67:
68:     checkpoint = torch.load(args.model, map_location="cpu", weights_only=True)
69:     if not isinstance(checkpoint, dict) or checkpoint.get("format") != "tibia-sr2x-v1":
70:         raise SystemExit("unsupported TibiaSR checkpoint format")
71:     model = TibiaSR2x(int(checkpoint["channels"]), int(checkpoint["blocks"]))
72:     model.load_state_dict(checkpoint["state_dict"])
```

### `tools/ai-agent/test_content_pipeline.py:19`

```text
15: from path_policy import is_safe_write
16: from task_validation import *  # noqa: F401,F403
17:
18:
19: def load(name):
20:     path = ROOT / "tools/ai-agent" / f"{name}.py"
21:     spec = importlib.util.spec_from_file_location(name, path)
22:     module = importlib.util.module_from_spec(spec)
23:     spec.loader.exec_module(module)
```

### `tools/ai-agent/test_content_pipeline.py:27`

```text
23:     spec.loader.exec_module(module)
24:     return module
25:
26:
27: validate_task = load("validate_task_spec").validate
28: make_plan = load("plan_content").plan
29: validate_plan = load("validate_content_plan").validate
30: render = load("render_content").render
31:
```

### `tools/ai-agent/test_content_pipeline.py:28`

```text
24:     return module
25:
26:
27: validate_task = load("validate_task_spec").validate
28: make_plan = load("plan_content").plan
29: validate_plan = load("validate_content_plan").validate
30: render = load("render_content").render
31:
32:
```

### `tools/ai-agent/test_content_pipeline.py:29`

```text
25:
26:
27: validate_task = load("validate_task_spec").validate
28: make_plan = load("plan_content").plan
29: validate_plan = load("validate_content_plan").validate
30: render = load("render_content").render
31:
32:
33: class PipelineTests(unittest.TestCase):
```

### `tools/ai-agent/test_content_pipeline.py:30`

```text
26:
27: validate_task = load("validate_task_spec").validate
28: make_plan = load("plan_content").plan
29: validate_plan = load("validate_content_plan").validate
30: render = load("render_content").render
31:
32:
33: class PipelineTests(unittest.TestCase):
34:     def registry(self):
```

### `tools/ai-agent/test_promotion_handoff.py:12`

```text
8:
9: ROOT = Path(__file__).resolve().parents[2]
10:
11:
12: def load(name):
13:     path = ROOT / "tools/ai-agent" / f"{name}.py"
14:     spec = importlib.util.spec_from_file_location(name, path)
15:     module = importlib.util.module_from_spec(spec)
16:     spec.loader.exec_module(module)
```

### `tools/ai-agent/test_promotion_handoff.py:20`

```text
16:     spec.loader.exec_module(module)
17:     return module
18:
19:
20: build = load("build_promotion_handoff").build
21:
22:
23: class PromotionHandoffTests(unittest.TestCase):
24:     def task(self):
```

### `tools/ai-agent/test_research_to_task.py:12`

```text
8: ROOT = Path(__file__).resolve().parents[2]
9: sys.path.insert(0, str(ROOT / "tools/ai-agent"))
10:
11:
12: def load(name: str):
13:     path = ROOT / "tools/ai-agent" / f"{name}.py"
14:     spec = importlib.util.spec_from_file_location(name, path)
15:     module = importlib.util.module_from_spec(spec)
16:     assert spec.loader is not None
```

### `tools/ai-agent/test_research_to_task.py:21`

```text
17:     spec.loader.exec_module(module)
18:     return module
19:
20:
21: build_draft = load("research_to_task").build_draft
22: validate_task = load("validate_task_spec").validate
23:
24:
25: class ResearchToTaskTests(unittest.TestCase):
```

### `tools/ai-agent/test_research_to_task.py:22`

```text
18:     return module
19:
20:
21: build_draft = load("research_to_task").build_draft
22: validate_task = load("validate_task_spec").validate
23:
24:
25: class ResearchToTaskTests(unittest.TestCase):
26:     def normalized(self):
```

### `tools/ai-agent/test_weapon_proficiency_achievement_audit.py:84`

```text
80:             cpp = root / "src/creatures/players/components/weapon_proficiency.cpp"
81:             cpp.parent.mkdir(parents=True)
82:             cpp.write_text(
83:                 '''
84: void WeaponProficiency::load() {
85:     normalizeStoredState(weaponId);
86: }
87: void WeaponProficiency::normalizeStoredState(uint16_t weaponId) {
88:     data.mastered = data.experience >= maxExperience;
```

### `tools/ai-agent/weapon_proficiency_achievement_audit.py:224`

```text
220:             )
221:         target_rows.append({"id": achievement_id, "reference": reference, "registry": definition})
222:
223:     add_experience = extract_function_body(cpp_text, "void WeaponProficiency::addExperience")
224:     load_body = extract_function_body(cpp_text, "void WeaponProficiency::load()")
225:     normalize_body = extract_function_body(cpp_text, "void WeaponProficiency::normalizeStoredState")
226:
227:     existing_transition_sets_mastered = "mastered = true" in add_experience
228:     initial_creation_caps_experience = any(
```

### `tools/check_lua_api_binding_docs.py:262`

```text
258:
259:
260: def load_docs():
261:     with DOC_PATH.open("r", encoding="utf-8") as file:
262:         return json.load(file)
263:
264:
265: def find_doc_entry(data, binding):
266:     if binding.kind == "method":
```

### `tools/check_lua_api_quality.py:75`

```text
71:
72:
73: def load_json(path):
74:     with path.open("r", encoding="utf-8") as file:
75:         return json.load(file)
76:
77:
78: def write_json(path, data):
79:     path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
```

## Donor assessment boundary

CrystalServer's replacement parser is not adopted by this audit. Its global whitespace removal and handwritten grammar require independent compatibility, malformed-input and resource-bound validation.

## Required manual follow-up

1. Separate helper definitions/tests from production call sites.
2. Trace every production input to persistence, network, file or trusted literal origin.
3. Define the exact grammar emitted by current `table.serialize`, including escaped strings and mixed key types.
4. Split any serializer defect from the decoder-security candidate unless one atomic compatibility change is proven necessary.
5. Choose a bounded decoder only after the compatibility corpus is complete.
