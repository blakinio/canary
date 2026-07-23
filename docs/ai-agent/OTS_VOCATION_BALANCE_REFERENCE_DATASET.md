# OTS Vocation Balance Reference Dataset

## Purpose

This document is the data-oriented companion to:

- `docs/ai-agent/REAL_TIBIA_VOCATION_ADJUSTMENTS_FORUM_ANALYSIS.md`;
- `docs/ai-agent/OTS_VOCATION_BALANCE_FORUM_DERIVED_GUIDANCE.md`;
- the vocation/class role framework proposed by PR #799.

It records the concrete spell, mechanic, progression and implementation data needed before future vocation-balance work in `blakinio/canary` can move from product direction to bounded implementation.

This is not an authorization to copy a donor implementation or to apply numerical balance changes.

## Evidence model

Every value in this document belongs to one of these states:

- `CURRENT-OFFICIAL` — current official Tibia material observed after the 2026 vocation-adjustment release, including the July 7, 2026 numerical corrections and later fixes;
- `RELEASE-STATE` — official June 2, 2026 release-state value, superseded where a later official change exists;
- `CURRENT-OFFICIAL-LIBRARY` — current Tibia spell-library metadata observed on 2026-07-23;
- `CANARY-BASELINE` — current `blakinio/canary` source observation at baseline `24d106b5eea40371833ce20de96184b55cd9b661`;
- `CRYSTAL-CANDIDATE` — read-only `zimbadev/crystalserver` source observation pinned to `75e9c72e33ce2c3f193e4f2d2ff17ebae4bbfaac`;
- `UPSTREAM-CANDIDATE` — read-only `opentibiabr/canary` evidence when separately pinned;
- `CONFLICT` — authoritative/current sources disagree or chronology is incomplete;
- `UNKNOWN` — no sufficiently strong source has established the value or behavior.

A donor formula is not Real Tibia proof. A current official headline base power is not enough to prove a complete server formula. A missing expected file path is not by itself runtime-absence proof.

---

# 1. Pinned sources

## Official Tibia

Primary current/release references:

- Vocation Adjustments Release State, 2026-06-02: `https://www.tibia.com/news/?id=8833&subtopic=newsarchive`
- Vocation Adjustments Release, 2026-06-16: `https://www.tibia.com/news/?id=8849&subtopic=newsarchive`
- Fixes and Changes, 2026-06-23: `https://www.tibia.com/news/?id=8862&subtopic=newsarchive`
- Vocation Adjustments Changes, 2026-07-07: `https://www.tibia.com/news/?id=8872&subtopic=newsarchive`
- Fixes and Changes, 2026-07-07: `https://www.tibia.com/news/?id=8875&subtopic=newsarchive`
- Fixes and Changes, 2026-07-14: `https://www.tibia.com/news/?id=8887&subtopic=newsarchive`
- News ticker fix, 2026-07-15: `https://www.tibia.com/news/?id=8892&subtopic=newsarchive`
- current spell library: `https://www.tibia.com/library/?subtopic=spells`

Historical Monk balance references used where 2026 did not replace the underlying base value:

- Fifth Vocation Updates during Test Server, 2025-03-27;
- Balancing and Changes, 2025-04-24;
- Balancing and Changes, 2025-06-11;
- Balancing and Changes, 2025-07-22.

## Canary target

- repository: `blakinio/canary`
- pinned baseline used for this dataset: `24d106b5eea40371833ce20de96184b55cd9b661`
- role: implementation target and current-fork source of truth

## CrystalServer donor

- repository: `zimbadev/crystalserver`
- pinned source used for this dataset: `75e9c72e33ce2c3f193e4f2d2ff17ebae4bbfaac`
- role: read-only implementation candidate
- authority: none over Real Tibia or Canary

---

# 2. Current global balance layer introduced by the 2026 adjustment

These changes affect every vocation comparison and must be included in any simulation.

| System | Current / release data | Evidence state | Balance consequence |
|---|---|---|---|
| Avalanche / GFB / Thunderstorm / Stone Shower | base power 50 | RELEASE-STATE | changes AoE fallback comparison for mages and rune users |
| Explosion Rune | area increased from 5 to 9 squares | RELEASE-STATE | changes practical AoE coverage |
| Auto-attack charm triggering | charms trigger only on main target of an auto-attack | RELEASE-STATE | major RP/AoE-ammunition DPS interaction |
| Gift of Life | restores 20/25/30% maximum mana in addition to prior effect | RELEASE-STATE | changes death-prevention resource model |
| Group XP, two vocations | 35% | RELEASE-STATE | party-value model |
| Group XP, three vocations | 70% | RELEASE-STATE | party-value model |
| Character attack value | +20% after combat-mode removal | RELEASE-STATE | global outgoing damage baseline |
| Shield defense value | +30% after combat-mode removal | RELEASE-STATE | EK/shield formulas and mitigation |
| Spellbook defense value | +60% after combat-mode removal | RELEASE-STATE | mage mitigation |
| Dedication mitigation multiplier | 0.075% per promotion point | RELEASE-STATE | progression scaling |
| Gem mitigation multipliers | 20/22/24/30% | RELEASE-STATE | build scaling |
| Superior Mana Potion | level 100, 240-360 mana, 254 gold; Paladin/Monk/Sorcerer/Druid | RELEASE-STATE | sustain/economy/input model |
| Distilled mana potions | same effect as normal, all vocations, +50% gold cost | RELEASE-STATE | universal sustain at economy premium |
| Great Mana Potion | usable by all vocations after later fix | CURRENT-OFFICIAL | Knight sustain/input model |
| Energy Ring | 2 mana per absorbed damage | RELEASE-STATE | survival/resource coupling |
| UH/IH on other players | no longer allowed | RELEASE-STATE | team rescue composition |
| Stance persistence | persists across sessions | RELEASE-STATE | state-machine contract |
| No stance | allowed | RELEASE-STATE | neutral-state contract |
| Stance exclusivity | one active; Sorcerer may have one elemental plus one crippling stance | RELEASE-STATE | state-machine contract |

Any future balance benchmark that ignores these global changes is not comparable to the 2026 live environment.

---

# 3. Elite Knight — complete 2026 adjustment data

## 3.1 Stances

| Mechanic | Current data | State |
|---|---|---|
| Blood Rage | +25% total sword/axe/club skill | CURRENT-OFFICIAL, reduced from release-state 30% on 2026-07-07 |
| Blood Rage penalty | +15% damage taken | RELEASE-STATE, no later numerical change found |
| Protector | +30% shielding | RELEASE-STATE |
| Protector defense | -15% damage taken | RELEASE-STATE |
| Protector offense | -15% damage dealt | RELEASE-STATE |
| Neutral stance | supported | RELEASE-STATE |

The official July 14 fix states that Blood Rage now grants the correct 25% bonus in live gameplay. This is important because a configuration value existing without the runtime effect would not be sufficient parity proof.

## 3.2 Spell and healing table

| Spell | Incantation | Type | Base power | Mana | Level | Cooldown | Group CD | Current notes |
|---|---|---|---:|---:|---:|---:|---:|---|
| Shield Bash | `exori ico scu` | attack | 55 | 30 | 18 | 4s | 2s | shield required; shield defense based; target's next auto-attack within 10s reduced by 50% |
| Shield Slam | `exori scu` | attack AoE | 52 | 110 | 30 | 6s | 2s | shield required; adjacent enemies; next auto-attack within 10s reduced by 50% |
| Bruise Bane | `exura infir ico` | healing | 15 | 10 | 1 | 2s | 2s | revised scaling uses magic level and shielding |
| Wound Cleansing | `exura ico` | healing | 70 | 60 | 8 | 2s | 2s | mana raised 40 -> 60 on 2026-07-07 |
| Fair Wound Cleansing | `exura med ico` | healing | 225 | 135 | 300 | 2s | 2s | mana raised 90 -> 135 on 2026-07-07 |
| Intense Wound Cleansing | `exura gran ico` | healing | 500 | 300 | 80 | 120s | healing group | mana raised 200 -> 300 on 2026-07-07; individual cooldown reduced from 10m to 2m in release package |
| Berserk | `exori` | attack | UNKNOWN current official base power | 125 | 35 | current library | current library | mana raised 115 -> 125 |
| Fierce Berserk | `exori gran` | attack | UNKNOWN current official base power | 360 | 90 | current library | current library | mana raised 340 -> 360 |
| Groundshaker | `exori mas` | attack AoE | UNKNOWN current official base power | 200 | 33 | current library | current library | mana raised 160 -> 200 |
| Front Sweep | `exori min` | attack directional | 80 | 200 | 70 | 6s in Crystal candidate | 2s in Crystal candidate | official base increased 72 -> 80 |
| Chivalrous Challenge | `exeta amp res` | support/control | n/a | 80 | 150 | current library | current library | jump range 7; +1 target; range bug fixed 2026-07-07 |

`UNKNOWN current official base power` means the 2026 official package did not publish a headline base-power value for that spell. A donor value must not be relabelled as official.

## 3.3 Wheel / perk values

- Front Sweep Augment I: +40% base power.
- Front Sweep Augment II: five affected squares, adding two side squares.
- Shield Slam Augment I: +15% life leech.
- Shield Slam Augment II: +25 percentage points to the auto-attack reduction, for 75% total reduction.
- Battle Healing: +10% healing; current shield multiplier is 2 after July 7, so the intended headline shield state is 20% rather than the release-state 30%.
- Combat Mastery current thresholds after July 7: 1% effect per 14/12/10% missing HP rather than 12/10/8%; defense effect doubled with shield, offense effect doubled with two-handed weapon.

## 3.4 CrystalServer implementation findings

### Shield Bash

Crystal path: `data/scripts/spells/attack/shield_bash.lua`

Observed candidate:

- base power 55;
- mana 30;
- level 18;
- cooldown 4s;
- group cooldown 2s;
- range 1;
- physical damage;
- shield required;
- formula candidate:
  - min = `calculateBaseDamageHealing(level) + basePower + defense*1.5 + shielding*0.6`;
  - max = `calculateBaseDamageHealing(level) + basePower + defense*2.5 + shielding*1.0`.

Critical review finding:

The official mechanic says the target's **next** auto-attack within 10 seconds is reduced by 50%. The Crystal implementation applies a 10-second attribute condition that sets outgoing damage to 50%. Unless the engine condition is consumed after one auto-attack elsewhere, this may reduce more than one auto-attack. This must be behavior-tested before reuse.

Crystal marks Shield Bash as non-premium, while the current official spell list marks it premium. This is a donor/current-official mismatch.

### Shield Slam

Crystal path: `data/scripts/spells/attack/shield_slam.lua`

Observed candidate:

- base power 52;
- mana 110;
- level 30;
- cooldown 6s;
- group cooldown 2s;
- 3x3-centered area;
- formula candidate:
  - min = `calculateBaseDamageHealing(level) + basePower + defense*1.4 + shielding*0.55`;
  - max = `calculateBaseDamageHealing(level) + basePower + defense*2.3 + shielding*0.95`.

The same one-hit-versus-duration debuff question applies. Crystal also marks this spell non-premium while the current official library marks it premium.

### Front Sweep

Crystal stores base power 80 and applies a `80/72` multiplier to an older formula. The file itself contains a TODO stating that a new real formula should replace the percentage approximation. Treat the formula as implementation candidate only.

## 3.5 Canary baseline gap snapshot

At `24d106...`:

- expected `shield_bash.lua` path: not found;
- expected `shield_slam.lua` path: not found;
- current `front_sweep.lua` still uses the older formula without Crystal's explicit `80/72` scale and does not store a basePower field.

Classification: `definition-not-found / candidate drift`, not yet full runtime-absence proof.

---

# 4. Royal Paladin — complete 2026 adjustment data

## 4.1 Stances

| Mechanic | Current data | State |
|---|---|---|
| Sharpshooter | +32% total distance fighting | CURRENT-OFFICIAL; release-state 40% |
| Divine Defiance conversion | 6% of distance fighting into holy/healing magic level | CURRENT-OFFICIAL; release-state 7.5% |
| Divine Defiance dodge | 12% against non-adjacent enemies | CURRENT-OFFICIAL; release-state 15% |

## 4.2 Spell table

| Spell | Incantation | Damage / type | Base power | Mana | Level | CD | Group CD | Notes |
|---|---|---|---:|---:|---:|---:|---:|---|
| Divine Barrage | `exori dir san` | holy AoE around target | 130 | 175 | 70 | 4s | 2s | current post-July value; magic-level scaling |
| Ethereal Barrage | `exori dir moe` | physical AoE around target | 40 | 135 | 60 | 4s | 2s | distance-fighting scaling |
| Divine Caldera | `exevo mas san` | holy self-centered AoE | 150 | 160 | 50 | 4s | 2s | release-state 160, reduced to 150 July 7 |
| Salvation | `exura gran san` | healing | 500 base healing | 210 | 60 | current library | current library | base heal raised 400 -> 500 |
| Divine Dazzle | `exana amp res` | support/control | n/a | 80 | 250 | current library | current library | jump range 7 |
| Divine Grenade | `exevo tempo mas san` | holy delayed/area mechanic | existing spell | 160 | Wheel/Revelation | current | current | three targeting modes; range-limit bug fixed July 15 |
| Swift Foot | `utamo tempo san` | support | n/a | 400 | 55 | 4s individual | 2s secondary group | attack/cast allowed, -30% damage dealt |

## 4.3 AoE ammunition

| Ammunition | Element | Attack | Level | Gold |
|---|---|---:|---:|---:|
| Shatterstorm Arrow | physical | 27 | 50 | 45 |
| Firestorm Arrow | fire | 21 | 125 | 75 |
| Terrastorm Arrow | earth | 21 | 125 | 75 |
| Froststorm Arrow | ice | 21 | 125 | 75 |
| Thunderstorm Arrow | energy | 21 | 125 | 75 |

All hit 13 squares. The main-target-only charm rule must be included when comparing them with legacy Diamond Arrow rotations.

## 4.4 Wheel values

- Divine Barrage Augment I: current +8% base damage.
- Divine Barrage Augment II: current +12% base damage.
- Divine Caldera Augment II: current +10%.
- Ethereal Barrage Augment I: +10% life leech.
- Ethereal Barrage Augment II: +10% critical hit chance.
- Divine Dazzle Augment I: +2 targets.
- Divine Dazzle Augment II: -8s cooldown.

## 4.5 CrystalServer findings

### Divine Barrage

Crystal path: `data/scripts/spells/attack/divine_barrage.lua`

- basePower 130 — matches current official headline value;
- holy;
- mana 175;
- level 70;
- cooldown 4s;
- group cooldown 2s;
- range 7;
- area `AREA_CIRCLE2X2`;
- formula delegates to `calculateMagicSpellDamage(level, maglevel, basePower)`.

This is currently one of the strongest donor candidates among the new spells because its headline base power matches the July 7 official correction. Full targeting-mode and area parity still require runtime validation.

### Ethereal Barrage

Crystal path: `data/scripts/spells/attack/ethereal_barrage.lua`

- basePower 40;
- physical;
- mana 135;
- level 60;
- cooldown 4s;
- group cooldown 2s;
- range 7;
- area `AREA_CIRCLE2X2`;
- formula uses `spellSkillDamage(basePower, level, skill, attack)` with ±10% spread.

### Divine Caldera

Crystal stores basePower 160, but current official value is 150 after July 7. Crystal is stale on this field.

The Crystal formula scales `(levelBonus + ML coefficient) * basePower / 140`, so updating the basePower field would materially affect the output.

## 4.6 Canary baseline gap snapshot

At `24d106...`:

- expected `divine_barrage.lua`: not found;
- expected `ethereal_barrage.lua`: not found;
- existing `divine_caldera.lua` uses the older formula directly and does not store the current 150 basePower field.

This strongly nominates a bounded Paladin parity audit, but does not yet authorize donor transplantation.

---

# 5. Master Sorcerer — complete 2026 adjustment data

## 5.1 Elemental stances

| Stance | Base effect | Conversion effect |
|---|---|---|
| Master of Flames | +4% fire base power | casting fire converts next non-fire spell to fire |
| Master of Thunder | +4% energy critical chance | casting energy converts next non-energy spell to energy |
| Master of Decay | +30% death critical extra damage | casting death converts next non-death spell to death |

Lord of Destruction adds at stages 1/2/3:

- Flames: +2/3/4%, total 6/7/8% base power;
- Thunder: +2/3/4%, total 6/7/8% crit chance;
- Decay: +15/22.5/30%, total 45/52.5/60% crit extra damage.

## 5.2 Crippling stances

- Sap Strength: spells, runes and auto-attacks apply -10% damage dealt to targets.
- Expose Weakness: spells, runes and auto-attacks grant attackers 8% elemental pierce against targets.
- unlock level 175;
- one crippling stance may coexist with one elemental stance.

## 5.3 Spell table

| Spell | Incantation | Element | Current base power | Mana | Level | CD | Group CD | Notes |
|---|---|---|---:|---:|---:|---:|---:|---|
| Death Echo | `exevo mort ora` | death / stance-convertible | 75 | CONFLICT: release state 155; current official library 150 | 120 | 6s | 2s | 5x5 first hit, second hit 50%; official final release state says 1s delay and same area |
| Great Death Beam | `exevo max mort` | death / stance-convertible | 155 | 140 | 66 | Beam/Wheel dependent; historical 10/8/6 stage model | 2s + Great Beams group | regular learnable spell after 2026 change |
| Great Energy Beam | `exevo gran vis lux` | energy / stance-convertible | 155 | 110 | 29 | 6s | 2s + 6s Great Beams | current library metadata |
| Lightning | `exori amp vis` | energy | 110 | 60 | 55 | current library | current library | chains to 2 additional targets; range 7 |
| Strong Energy Strike | `exori gran vis` | energy | 125 | 60 | 80 | current library | current library | range 7 |
| Strong Flame Strike | `exori gran flam` | fire | 125 | 60 | 70 | current library | current library | range 7 |
| Ultimate Energy Strike | `exori max vis` | energy | 210 | 100 | 100 | current library | current library | range 7 |
| Ultimate Flame Strike | `exori max flam` | fire | 210 | 100 | 90 | current library | current library | range 7 |

## 5.4 Death Echo operational chronology

Release-state contract:

- 5x5 area;
- second hit after 1 second;
- same area;
- second hit 50% of initial damage;
- three targeting modes;
- base power 85 at release state, reduced to 75 July 7;
- Augment I -2s cooldown;
- Augment II current +12% base damage after July 7.

Post-release fixes:

- June 23: second explosion remains at the first explosion location if caster changes floor; cancelled casts no longer execute;
- July 7: targeting through doors made consistent;
- July 15: no-range-limit bug fixed.

Current official-library conflict:

- library reports mana 150;
- June release-state article reports mana 155;
- no later official balance article located in this pass explicitly documents 155 -> 150.

Classification: `CONFLICT`; current live/runtime observation should decide implementation value.

## 5.5 Mana Buffer

Current headline contract after July 7:

- if incoming damage exceeds current HP, determine lethal overkill;
- overkill is multiplied by 10 and consumed from mana;
- release-state additionally specifies 25% maximum mana consumption, triggerable at most once every 2 seconds;
- insufficient mana results in death.

Required deterministic boundaries:

- exact lethal hit;
- one point over lethal;
- sufficient/exactly sufficient/insufficient mana;
- multiple same-tick hits;
- 25% max-mana extra cost cooldown;
- Energy Ring/Magic Shield interactions;
- Gift of Life/death-prevention ordering;
- PvP behavior.

## 5.6 Beam Mastery

Current side-beam damage after July 7:

- stage 1: 25%;
- stage 2: 40%;
- stage 3: 70%.

The prior 40/60/80% values are superseded.

The central-beam target-count damage/cooldown behavior remains part of the package and must be validated separately.

## 5.7 CrystalServer findings

### Death Echo

Crystal path: `data/scripts/spells/attack/death_echo.lua`

Candidate metadata:

- basePower 85 — stale versus current 75;
- mana 155 — matches release-state but conflicts with current library 150;
- level 120;
- range 7;
- cooldown 6s;
- group cooldown 2s;
- 5x5 area;
- 1s delayed second hit;
- stance-based element conversion.

Critical formula finding:

The Crystal callbacks do **not** consume the `basePower` argument. Damage is calculated from fixed `calculateBaseDamageHealing(level)` plus magic-level coefficients. Therefore changing `spell:basePower(85)` to 75 alone would not change actual damage in this candidate. This is a major donor-review blocker.

The implementation also requires explicit proof that the second hit cannot trigger charms. No local no-charm guard is visible in the spell file.

### Great Death Beam / Great Energy Beam

Crystal stores basePower 170 for both, stale versus current official 155.

Their formula callbacks also do not use the basePower field. Crystal side-beam factors remain 40/60/80%, stale versus current 25/40/70%.

This means a superficial constant update would not fully repair the donor implementation.

## 5.8 Canary baseline gap snapshot

At `24d106...` expected `death_echo.lua` is not found. A full stance/Mana Buffer/beam audit remains required before any implementation claim.

---

# 6. Elder Druid — complete 2026 adjustment data

## 6.1 Stances

| Stance | Effect |
|---|---|
| Shared Conservation | Heal Friend and Nature's Embrace heal a secondary party target for 30%; secondary cannot equal primary; +10% self-healing |
| Elemental Synthesis | +10% of magic level as additional ice and earth magic level |

## 6.2 Spell table

| Spell | Incantation | Element/type | Current base power | Mana | Level | CD | Group CD | Notes |
|---|---|---|---:|---:|---:|---:|---:|---|
| Forked Glacier | `exevo fur frigo` | ice chain | 90 | 180 | 90 | 6s | 2s | target +6 additional; Wheel +1 target; current July value |
| Forked Thorns | `exevo fur tera` | earth chain | 97 | 180 | 80 | 6s | 2s | target +5 additional; Wheel +1 target; current July value |
| Nature's Embrace | `exura gran sio "name"` | healing | 2000 base heal | 400 | 275 | current library | current library | more consistent healing |
| Heal Friend | `exura sio "name"` | healing | UNKNOWN current official base | 120 | 18 | current library | current library | more consistent healing |
| Strong Terra Strike | `exori gran tera` | earth | 115 | 60 | 70 | current library | current library | range 7 |
| Strong Ice Strike | `exori gran frigo` | ice | 115 | 60 | 80 | current library | current library | range 7 |
| Ultimate Terra Strike | `exori max tera` | earth | 195 | 100 | 90 | current library | current library | range 7 |
| Ultimate Ice Strike | `exori max frigo` | ice | 195 | 100 | 100 | current library | current library | range 7 |
| Strong Ice Wave | `exevo gran frigo hur` | ice directional | 140 | 170 | 40 | 4s | 2s | area enlarged; current July base value |
| Wrath of Nature | `exevo gran mas tera` | earth AoE | 175 | 700 | 55 | current library | current library | more consistent damage |

## 6.3 Wheel / healing values

- Forked Spells I: -2s cooldown for both forked spells.
- Forked Spells II: +1 target.
- Heal Friend I: +4% base heal.
- Heal Friend II: +6% base heal.
- Terra Wave II: 10% life leech.
- Strong Ice Wave I: +6% base damage in final release state.
- Strong Ice Wave II: enlarged area.
- Healing Link: self-heal equals 25% of Nature's Embrace / Heal Friend healing.
- Blessing of the Grove: healing spells can crit; +5/7.5/10% extra healing below 60% HP, doubled below 30% HP.

## 6.4 Mana Buffer

Same current multiplier-10 lethal-overkill mechanic as Sorcerer. Test separately because ED healing and party responsibilities alter practical tail-risk behavior.

## 6.5 CrystalServer findings

### Forked Glacier

- Crystal basePower 97 — stale versus current 90;
- mana 180, level 90, cooldown 6s, group cooldown 2s, range 7;
- target count 7 total before Wheel (+1 candidate);
- chain jump distance candidate 5.

Critical formula finding: callback ignores `basePower`; it uses fixed level/ML coefficients and constants. Updating only the stored basePower will not implement the July nerf.

### Forked Thorns

- Crystal basePower 105 — stale versus current 97;
- mana 180, level 80, cooldown 6s, group cooldown 2s, range 7;
- 6 total targets before Wheel.

Its formula also ignores `basePower`.

### Strong Ice Wave

- Crystal basePower 150 — stale versus current 140;
- cooldown 4s and enlarged area are present;
- formula ignores `basePower`.

Again, changing only the metadata field would not change output.

## 6.6 Canary baseline gap snapshot

At `24d106...`:

- expected `forked_glacier.lua`: not found;
- expected `forked_thorns.lua`: not found.

Full current Canary stance, Mana Buffer, healing-formula and Wheel-path coverage remains to be audited.

---

# 7. Exalted Monk — complete balance data relevant to the 2026 adjustment

Monk requires both the 2026 package and the 2025 post-release nerf chronology because several 2026 changes modify mechanics whose current base values were established in 2025.

## 7.1 Virtue of Justice party effects

Final release-state package:

- nearby Knight: -3% damage received;
- nearby Paladin: +6% auto-attack damage;
- nearby Sorcerer: +6% spell and rune damage;
- nearby Druid: +12% healing done;
- Mentor Other removed;
- serene Monk receives corresponding vocation effects when those vocations are present.

Earlier test material contained different Sorcerer and Monk-specific values. Use the final release-state package for the release baseline.

The July 7 fix corrected Virtues not affecting the Monk.

## 7.2 Spell table

| Spell | Incantation | Type | Current / latest known base power | Mana | Level | CD | Group CD | Notes |
|---|---|---|---:|---:|---:|---:|---:|---|
| Thousand Fist Blows | `exori mas amp pug` | variable-element builder AoE | 62 | 145 | 120 | 12s | 2s | +1 Harmony; three targeting modes in final release state |
| Mystic Repulse | `exori amp pug` | variable-element builder | 85 | 150 | 30 | 12s | 2s | 2026 buff from 72 -> 85 |
| Chained Penance | `exori med pug` | chain builder | 70 | 180 | 70 | current official library | current official library | latest official base found July 22, 2025; 2026 initial range increased to radius 4 |
| Spiritual Outburst | `exori gran mas nia` | chain spender/revelation | 42 | 425 | Revelation | 24/20/16s by stage | 2s | repeats at 5 Harmony for 37.5/50/62.5% after historical update; July 14, 2026 target-hit bug fixed |
| Mass Spirit Mend | `exura mas nia` | healing | UNKNOWN current official base after 2026 rework | 400 current library | 150 | 12s | 1s current library | no longer spender; caster receives lesser effect |
| Flurry of Blows | `exori mas pug` | builder AoE | 55 latest official value found 2025-07-22 | 110 | 35 | current | current | Wheel area augment changed |
| Greater Flurry of Blows | `exori gran mas pug` | builder | 86 latest official value found 2025-07-22 | 300 | 90 | current | current | high-density scaling input |

## 7.3 Chained Penance chronology

- March 27, 2025: base 111, 3 chain targets, jump range 2, +3% chain bonus.
- April 24, 2025: base 111 -> 99.
- June 11, 2025: jump bonus +3% -> -9%.
- July 22, 2025: base 99 -> 70; jump bonus -9% -> -5%; targets 4 -> 5; Wheel Augment II changed to +18% base damage.
- June 2026 adjustment: jump range +1 and target selection changed to closest target.
- July 7, 2026: initial range increased to radius 4.

This chronology is necessary to avoid using the March 2025 base 111 or an intermediate chain rule as the current baseline.

## 7.4 Thousand Fist Blows

Final release-state:

- base power 62;
- mana 145;
- level 120;
- cooldown 12s;
- builder +1 Harmony;
- target and surrounding area;
- three targeting modes;
- Augment I +40% critical extra damage;
- Augment II -6s cooldown.

## 7.5 Other 2026 mechanic changes

- Way of the Monk shrines: +2% melee auto-attack damage reduction per shrine, up to 20%, in addition to existing auto-attack progression.
- Mass Spirit Mend: no longer spender; cooldown/healing changed; caster lesser effect.
- Mystic Repulse: base 72 -> 85, cooldown 20 -> 12.
- Chained Penance and Spiritual Outburst: jump range +1; choose closest target rather than highest HP percentage.
- familiar targeting/range adjusted for reliability.
- Guiding Presence shares 100% mantra effect.
- Sanctuary: +10% damage to adjacent enemies and +10% healing to adjacent allies, plus its existing field behavior.
- Flurry of Blows Augment I: area enlargement instead of 5% life leech.
- Mystic Repulse Augment I: -6s cooldown.
- Mass Spirit Mend Augment II: -4s cooldown.

## 7.6 CrystalServer findings

### Thousand Fist Blows

Crystal is close on headline metadata:

- basePower 62;
- mana 145;
- level 120;
- cooldown 12s;
- group cooldown 2s;
- range 7;
- +1 Harmony;
- candidate element conversion from weapon bond;
- candidate formula uses `calculateMonkSpellDamage(..., basePower, 0.8)` with ±10% spread.

Targeting semantics still require proof against final client modes.

### Mystic Repulse

Crystal stores basePower 72, stale versus current 85, while cooldown 12s is updated. Its formula uses the basePower argument, so this candidate is numerically stale but structurally easier to update than fixed-formula donor files.

### Chained Penance

Crystal stores basePower 70, matching the latest official base located in July 2025.

However:

- candidate chain search uses range 3, while current official initial range is radius 4;
- target count begins at 5 plus Wheel/item additions;
- candidate damage decays by `0.5^jump`, which does not match the latest located official -5% jump-bonus chronology;
- target ordering uses path length and highest-health tie-breaking rather than a plainly specified geometric closest-target contract.

Classification: high-value implementation reference, but not safe to copy.

### Spiritual Outburst

Crystal basePower 42 and stage cooldown 24/20/16 align with the historical official release values located in March 2025. It implements the delayed second chain at 5 Harmony with 37.5/50/62.5% factors.

The July 14, 2026 official fix that Spiritual Outburst was not hitting all targets means any donor must be runtime-tested against multi-target fixtures even when the headline formula appears aligned.

### Mass Spirit Mend

Crystal candidate is materially stale against current official library metadata:

- Crystal mana 250 vs current official library 400;
- Crystal group cooldown 2s vs current official library 1s;
- Crystal basePower 90, but no current official base-power value was established in this pass.

The Crystal comments say the caster receives a lesser effect, but the self-heal branch uses larger ML coefficients than the general branch. That apparent contradiction requires code-level and runtime review before reuse.

## 7.7 Canary baseline gap snapshot

At `24d106...` expected `thousand_fist_blows.lua` is not found. Full Monk parity must separately audit current existing Monk builders/spenders, Harmony, Virtues, Serene, Wheel and elemental-bond runtime paths.

---

# 8. Cross-repository candidate matrix

| Feature | Current official headline | Canary baseline | Crystal candidate | Current classification |
|---|---|---|---|---|
| Shield Bash | BP55, 4s, 30 mana, shield, next auto -50% | standard path not found | implemented; semantic concern on duration condition; premium mismatch | `CANDIDATE_REQUIRES_BEHAVIOR_PROOF` |
| Shield Slam | BP52, 6s, 110 mana, shield, adjacent, next auto -50% | standard path not found | implemented; same debuff concern; premium mismatch | `CANDIDATE_REQUIRES_BEHAVIOR_PROOF` |
| Divine Barrage | BP130 current | standard path not found | BP130 candidate | `HIGH_PRIORITY_CANDIDATE` |
| Ethereal Barrage | BP40 | standard path not found | BP40 candidate | `HIGH_PRIORITY_CANDIDATE` |
| Death Echo | BP75 current | standard path not found | BP85; formula ignores basePower | `STALE_AND_FORMULA_RISK` |
| Forked Glacier | BP90 current | standard path not found | BP97; formula ignores basePower | `STALE_AND_FORMULA_RISK` |
| Forked Thorns | BP97 current | standard path not found | BP105; formula ignores basePower | `STALE_AND_FORMULA_RISK` |
| Strong Ice Wave | BP140 current | existing path requires audit | BP150; formula ignores basePower | `STALE_AND_FORMULA_RISK` |
| Great Death Beam | BP155 current | existing path requires audit | BP170; formula ignores basePower | `STALE_AND_FORMULA_RISK` |
| Great Energy Beam | BP155 current | existing path requires audit | BP170; formula ignores basePower | `STALE_AND_FORMULA_RISK` |
| Thousand Fist Blows | BP62 | standard path not found | BP62 candidate | `HIGH_PRIORITY_CANDIDATE` |
| Mystic Repulse | BP85 current | existing path requires audit | BP72 | `STALE_NUMERIC_CANDIDATE` |
| Chained Penance | BP70 latest located; initial radius4 | existing path requires audit | BP70, search range3, different decay model | `PARTIAL_VALUE` |
| Spiritual Outburst | BP42 historical/current candidate | existing path requires audit | BP42, repeat-chain implemented | `PARTIAL_VALUE_REQUIRES_2026_FIX_TEST` |
| Mass Spirit Mend | current base UNKNOWN; mana400/group1s | existing path requires audit | base90, mana250/group2s | `STALE_AND_CONFLICTING` |

---

# 9. Critical donor-code findings that affect future balance work

## 9.1 `basePower` metadata is not always connected to actual damage

Several Crystal candidates expose `spell:basePower(...)` but their callbacks ignore the `basePower` parameter:

- Death Echo;
- Forked Glacier;
- Forked Thorns;
- Strong Ice Wave;
- Great Death Beam;
- Great Energy Beam.

Therefore a patch that only updates `spell:basePower(85)` to `75`, for example, may make metadata look correct while leaving runtime damage unchanged.

Future audits must trace the callback all the way to final min/max damage.

## 9.2 Headline value parity does not prove mechanic parity

Examples:

- Shield Bash/Shield Slam can have correct base power while applying a debuff with incorrect consumption semantics.
- Divine Barrage can have correct base power while targeting mode or exact area differs.
- Chained Penance can have correct base power while target ordering, jump distance and damage decay differ.
- Spiritual Outburst can have correct formula while missing targets in runtime, as demonstrated by the July 14 official live fix.

## 9.3 Current official material can conflict internally

Death Echo is the current example:

- June 2 release-state article: mana 155;
- current official spell library observed July 23: mana 150.

Do not silently pick one. Resolve with current live observation or a later explicit official change.

---

# 10. Required formula schema for future per-spell records

Every spell that enters an OTS balance implementation task should have this complete record:

```text
name
incantation
vocation
spell group
secondary group
attack/healing/support
combat element
premium
learn level
mana
individual cooldown
primary group cooldown
secondary group cooldown
target mode(s)
range
line-of-sight/wall behavior
area geometry
maximum targets
chain/fork ordering
jump distance
initial acquisition radius
base power
actual runtime min formula
actual runtime max formula
level coefficient
magic/skill coefficient
weapon/shield coefficient
critical rules
charm rules
life leech rules
mana leech rules
stance conversion
Wheel/Revelation augments
Weapon Proficiency modifiers
Gem/Fragment modifiers
state-machine requirements
PvP-specific behavior
known live fixes
current Canary definition
current Canary registration
current Canary runtime path
Crystal candidate definition
source conflicts
deterministic tests
telemetry scenarios
```

A spell is not balance-ready while material fields remain `UNKNOWN` unless the task explicitly excludes them.

---

# 11. Required scenario dataset

For every vocation/build combination record at least:

## Progression bands

- early;
- mid;
- high;
- endgame;
- optimized endgame.

## Combat contexts

- solo low density;
- solo high density;
- duo;
- standard party;
- boss single target;
- boss mechanics/movement;
- structured PvP;
- open-world PvP where supported.

## Outputs

- damage per second;
- damage per rotation;
- targets hit per cast;
- hit reliability;
- theoretical vs realistic-skilled vs ordinary-competent output;
- healing per second and minimum survival buffer;
- damage mitigated;
- deaths/wipes;
- life/mana leech;
- potion/rune/ammunition use;
- supply cost/hour;
- profit/hour;
- XP/hour;
- actions/minute;
- target/facing/crosshair actions;
- Wheel points required for functional breakpoint;
- Wheel points required for scaling breakpoint;
- party-slot contribution beyond direct damage.

---

# 12. Immediate research packages nominated by this dataset

These are analysis packages, not implementation permission.

## VBR-001 — New-spell definition and runtime parity

Audit:

- Shield Bash;
- Shield Slam;
- Divine Barrage;
- Ethereal Barrage;
- Death Echo;
- Forked Glacier;
- Forked Thorns;
- Thousand Fist Blows.

For each: current Canary definition/registration/runtime path, official current metadata, Crystal candidate, exact formula and deterministic behavior tests.

## VBR-002 — Stance state machines

Audit EK, RP, MS and ED stance activation, neutral state, persistence, switching, death/logout, buffs/debuffs, client state and Wheel interaction.

## VBR-003 — Formula integrity

Trace every spell where donor `basePower` is disconnected from its callback and define an architecture-native Canary base-power model before importing numbers.

## VBR-004 — Chain/fork targeting contract

Audit Chained Penance, Spiritual Outburst, Forked Glacier, Forked Thorns and any other player chain spells for:

- initial acquisition;
- no-selected-target behavior;
- geometric versus path distance;
- tie-breaking;
- walls/doors/LOS;
- repeated targets;
- max targets;
- jump distance;
- target movement.

## VBR-005 — Healing and survivability

Audit:

- Knight healing scaling with shielding/ML and 2s cadence;
- Battle Healing;
- ED Heal Friend/Nature's Embrace consistency;
- Mass Spirit Mend rework;
- Mana Buffer;
- Energy Ring;
- Gift of Life ordering.

## VBR-006 — Complete rotation/economy simulation

Use the forum-derived guidance compensation ledger to compare complete rotations including leech, kill time, incoming turns, supply use and practical execution.

---

# 13. Current conclusion

The 2026 official vocation-adjustment package is large enough that future OTS balance work requires a structured reference dataset rather than isolated spell edits.

The strongest implementation finding from the first donor comparison is that CrystalServer is valuable but heterogeneous:

- some new spells have headline values matching current official data;
- some are numerically stale after July 7;
- several store a basePower field that is not consumed by the actual damage callback;
- some candidate targeting/debuff semantics differ from the current official wording;
- some Monk values and cooldowns are materially stale;
- live Tibia itself received post-release fixes proving that mechanically plausible code can still fail at runtime.

The correct future workflow is therefore:

1. pin the current official behavior/value source;
2. pin current Canary and donor SHAs;
3. build the full per-spell record;
4. prove current Canary behavior;
5. compare Crystal and upstream candidates field-by-field;
6. write deterministic tests for targeting, geometry, state and formula boundaries;
7. adapt the smallest architecture-native implementation;
8. only then begin OTS-specific balance tuning using the role framework and forum-derived balance methodology.
