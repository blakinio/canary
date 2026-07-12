---
task_id: CAN-20260712-raid-startup-waves
status: active
agent: "OpenAI Codex"
branch: fix/raid-startup-waves
base_branch: main
created: 2026-07-12T21:20:00Z
updated: 2026-07-12T22:00:00Z
last_verified_commit: "366b3d4e6bba4cb8d3dee09a8c5a0181cc3d7423"
risk: medium
related_issue: "opentibiabr/canary#3599"
related_pr: ""
depends_on: []
blocks: []
owned_paths:
  - data-otservbr-global/scripts/raids/monsters/draptor.lua
  - data-otservbr-global/scripts/raids/monsters/yeti.lua
  - data-otservbr-global/scripts/raids/monsters/undead_cavebear.lua
  - tools/ai-agent/test_raid_spawn_wave_contracts.py
  - docs/agents/tasks/active/CAN-20260712-raid-startup-waves.md
  - docs/agents/ACTIVE_WORK.md
modules_touched:
  - scripted raid encounters
reuses:
  - data/libs/systems/encounters.lua
  - data/libs/systems/raids.lua
  - Python standard-library unittest conventions under tools/ai-agent
public_interfaces: []
cross_repo_tasks: []
---

# Goal

Reduce raid monster-creation peaks reported in upstream #3599 by splitting active Draptor and Yeti scripted encounters into progressive waves without changing monster totals, zones, broadcasts, the Draptor count or Grand Mother Foulscale.

# Acceptance criteria

- [x] The live scripted raid definitions are changed; unregistered legacy XML is not treated as runtime evidence.
- [x] Dragon total remains 150, split as `20,20,20,10,20,20,20,20` with a maximum wave of 20.
- [x] Yeti total remains 60, split as `20,20,20`.
- [x] Monster materialization is scheduled at 1 second and each progressive stage advances at 2 seconds.
- [x] Focused contract proves spawn delay is shorter than stage advance, because stage changes cancel pending encounter events.
- [x] Existing broadcasts, eight Draptor stages and Grand Mother Foulscale remain unchanged.
- [x] Undead Cavebear no longer reuses and resets the `farmine.draptor` encounter identity.
- [ ] Focused tests, Lua formatting/tests, datapack runtime smoke and required CI pass on the final head.
- [ ] Exact changed-file list and review state are verified before merge.

# Confirmed context

- `data-otservbr-global/raids/farmine/draptor.xml` and `raids/carlin/yeti.xml` remain in the tree but are absent from `raids/raids.xml`; changing them would not repair the active encounters.
- Active definitions are `scripts/raids/monsters/draptor.lua` and `yeti.lua`, loaded by the current datapack script loader.
- `Encounter:spawnMonsters` schedules creation after `timeToSpawnMonsters`, whose default is 3 seconds.
- `Encounter:enterStage` calls `cancelEvents()` before starting the next stage.
- Therefore a 2-second wave advance paired with the default 3-second spawn delay would cancel every planned monster creation.
- Upstream #3599 asks for progressive waves to avoid simultaneous creation peaks.
- Undead Cavebear incorrectly reused both the Draptor `Zone` and `Raid` identity, so whichever file loaded second reset the same encounter object.
- Its legacy XML identifies the area as `31909,32554,10` through `31983,32579,10`; the supplied OTBM scan confirms all 1,950 positions in that bounded floor-10 rectangle exist without duplicate tiles.

# Ownership and overlap

- Open fork PRs and active task records were reviewed before implementation.
- No open PR claims either active raid Lua file or the focused test path.
- Upstream is evidence-only and remains read-only.

# Implemented behavior

1. Draptor Dragon stages now read a named eight-wave table totalling 150, with no stage above 20.
2. Yeti stages now read a named three-wave table totalling 60.
3. Both encounters use a 1-second spawn lead-in and 2-second stage advances, so the scheduled creations complete before transition cleanup.
4. A real-source contract protects exact populations, maximum burst, timings, broadcasts, Draptors, boss and the underlying cancellation-order assumption.
5. Undead Cavebear uses its own raid/zone identity and its legacy floor-10 area, preventing it from replacing Draptor registration.

# Work log

## 2026-07-12T22:00:00Z

- Rebased the complete six-file change onto current `main` `366b3d4e...`; resolved only the expected shared Active Work index cleanup.
- Focused raid contract: 5/5 passed.
- Full AI Agent Tools discovery suite: 231/231 passed.
- Existing bounded OTBM scanner confirmed 1,950/1,950 tile positions on both queried floors with no duplicate tiles; legacy Undead Cavebear XML is the code evidence selecting floor 10.

## 2026-07-12T21:45:00Z

- Rejected an initial local XML-only patch before publication after registration analysis proved those files inactive.
- Traced `Encounter:autoAdvance`, `enterStage`, `cancelEvents` and `spawnMonsters` to establish the timing safety condition.
- Implemented the smallest active Lua change with a focused real-source contract.
- Audited the related encounter registry and found a duplicate `farmine.draptor` identity in Undead Cavebear; confirmed its floor-10 legacy area against the supplied OTBM before correcting it.

## 2026-07-12T21:20:00Z

- Confirmed legacy XML absolute-delay semantics and the original issue's intended totals.
- Claimed the task after checking open PR ownership.

# Decisions

| Decision | Reason/evidence |
|---|---|
| Change active Lua, not dormant XML | Only the scripted encounters are registered in the current raid system. |
| Set spawn lead-in to 1 second | It must complete before the 2-second stage transition cancels pending events. |
| Preserve populations and encounter content | The defect is creation burst size, not population, zone, announcements or boss composition. |
| Separate Undead Cavebear registration | Duplicate encounter names share and reset the same `Encounter.registry` object, making Draptor activation load-order dependent. |
| Do not change global encounter scheduling | A framework change would affect every encounter and is unnecessary for this bounded defect. |

# Risks and compatibility

- Runtime: medium; monster totals are preserved, but active encounter pacing is intentionally reduced from multi-minute spacing to progressive two-second waves. Undead Cavebear becomes independently registered on its legacy floor-10 area instead of competing with Draptor.
- Persistence/schema/protocol: none.
- Map/assets: unchanged.
- Legacy raids: unchanged; dormant XML is retained without misleading edits.
- Rollback: revert the Lua/test commit; no migration required.

# Remaining work

Run full focused validation, publish a draft PR, complete CI/review gates and merge.

# Handoff

Read this task, upstream #3599, the three owned raid Lua files and `data/libs/systems/encounters.lua`. Do not patch only dormant XML. Preserve `timeToSpawnMonsters < autoAdvance`; otherwise stage transition cancels the monster creation events. Do not merge the Draptor and Undead Cavebear identities again. Do not change monster totals, broadcasts, bosses, maps or assets.

# Completion

- Final status: active
- PR:
- Merge commit:
- Changelog updated: pending completion
- Archived at:
