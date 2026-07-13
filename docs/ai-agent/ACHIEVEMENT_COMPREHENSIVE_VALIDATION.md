# Canary achievement validation report

## Decision

- audit: **pass**
- complete semantic/runtime validation: **no**
- definitions: **542**, IDs **1..570**, gaps **28**
- public / secret / points: **349 / 193 / 1431**
- API references / dynamic / undefined static: **182 / 22 / 0**

## External baseline

- listed: expected `564`, actual `542` — **mismatch**
- common: expected `363`, actual `349` — **mismatch**
- secretDiscovered: expected `201`, actual `193` — **mismatch**
- theoreticalPoints: expected `1475`, actual `1431` — **mismatch**

## Comprehensive status counts

- conflicting: 28
- partially-confirmed: 125
- unresolved: 411

## Per-achievement evidence table

| ID | Name | Status | Definition | Condition | Handler | Existing players | New players | Tests |
|---:|---|---|---|---|---|---|---|---|
| 1 | Castlemania | unresolved | confirmed | quest-or-task, collection, exploration, dialogue | unresolved | unresolved | unresolved | missing |
| 2 | Chorister | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 3 | The Milkman | unresolved | confirmed | quest-or-task | unresolved | unresolved | unresolved | missing |
| 4 | Vive la Resistance | unresolved | confirmed | quest-or-task | unresolved | unresolved | unresolved | missing |
| 5 | Culinary Master | unresolved | confirmed | quest-or-task, item-or-interaction | unresolved | unresolved | unresolved | missing |
| 6 | Shell Seeker | partially-confirmed | confirmed | collection | static-progress-candidate | unresolved | partially-confirmed | missing |
| 7 | Backpack Tourist | partially-confirmed | confirmed | quest-or-task | static-award-candidate | unresolved | partially-confirmed | missing |
| 8 | Dread Lord | partially-confirmed | confirmed | quest-or-task | static-award-candidate | unresolved | partially-confirmed | missing |
| 9 | Lord Protector | partially-confirmed | confirmed | quest-or-task | static-award-candidate | unresolved | partially-confirmed | missing |
| 10 | Nightmare Knight | partially-confirmed | confirmed | quest-or-task | static-award-candidate | unresolved | partially-confirmed | missing |
| 11 | Bone Brother | partially-confirmed | confirmed | quest-or-task | static-award-candidate | unresolved | partially-confirmed | missing |
| 12 | Blessed! | partially-confirmed | confirmed | quest-or-task, collection, dialogue | static-award-candidate | unresolved | partially-confirmed | missing |
| 13 | Recognised Trader | partially-confirmed | confirmed | quest-or-task, exploration | static-award-candidate | unresolved | partially-confirmed | missing |
| 14 | Fountain of Life | partially-confirmed | confirmed | item-or-interaction | static-award-candidate | unresolved | partially-confirmed | missing |
| 15 | Lord of the Elements | unresolved | confirmed | quest-or-task | unresolved | unresolved | unresolved | missing |
| 16 | Beach Tamer | unresolved | confirmed | quest-or-task | unresolved | unresolved | unresolved | missing |
| 17 | Follower of Azerus | unresolved | confirmed | quest-or-task | unresolved | unresolved | unresolved | missing |
| 18 | Follower of Palimuth | unresolved | confirmed | quest-or-task | unresolved | unresolved | unresolved | missing |
| 19 | Elite Hunter | unresolved | confirmed | quest-or-task, combat | unresolved | unresolved | unresolved | missing |
| 20 | Huntsman | unresolved | confirmed | quest-or-task, combat | unresolved | unresolved | unresolved | missing |
| 21 | Passionate Kisser | unresolved | confirmed | quest-or-task | unresolved | unresolved | unresolved | missing |
| 22 | Top AVIN Agent | partially-confirmed | confirmed | quest-or-task | static-award-candidate | unresolved | partially-confirmed | missing |
| 23 | Top CGB Agent | partially-confirmed | confirmed | quest-or-task | static-award-candidate | unresolved | partially-confirmed | missing |
| 24 | Top TBI Agent | unresolved | confirmed | quest-or-task | unresolved | unresolved | unresolved | missing |
| 25 | Secret Agent | partially-confirmed | confirmed | quest-or-task | static-award-candidate | unresolved | partially-confirmed | missing |
| 26 | Golem in the Gears | unresolved | confirmed | quest-or-task | unresolved | unresolved | unresolved | missing |
| 27 | Poet Laureate | unresolved | confirmed | quest-or-task, collection, exploration | unresolved | unresolved | unresolved | missing |
| 28 | Minstrel | unresolved | confirmed | item-or-interaction, progress-threshold | unresolved | unresolved | unresolved | missing |
| 29 | Friend of the Apes | partially-confirmed | confirmed | quest-or-task | static-award-candidate | unresolved | partially-confirmed | missing |
| 30 | Territorial | unresolved | confirmed | dialogue | unresolved | unresolved | unresolved | missing |
| 31 | Marid Ally | partially-confirmed | confirmed | quest-or-task | static-award-candidate | unresolved | partially-confirmed | missing |
| 32 | Efreet Ally | partially-confirmed | confirmed | quest-or-task | static-award-candidate | unresolved | partially-confirmed | missing |
| 33 | Lucid Dreamer | unresolved | confirmed | quest-or-task | unresolved | unresolved | unresolved | missing |
| 34 | Explorer | unresolved | confirmed | quest-or-task | unresolved | unresolved | unresolved | missing |
| 35 | Sea Scout | unresolved | confirmed | quest-or-task | unresolved | unresolved | unresolved | missing |
| 36 | Unlikely Pathfinder | unresolved | confirmed | exploration | unresolved | unresolved | unresolved | missing |
| 37 | Bearhugger | partially-confirmed | confirmed | quest-or-task | static-award-candidate | unresolved | partially-confirmed | missing |
| 38 | Ghostwhisperer | unresolved | confirmed | quest-or-task, dialogue | unresolved | unresolved | unresolved | missing |
| 39 | Animal Activist | partially-confirmed | confirmed | quest-or-task, combat | static-award-candidate | unresolved | partially-confirmed | missing |
| 40 | Honorary Barbarian | partially-confirmed | confirmed | quest-or-task | static-award-candidate | unresolved | partially-confirmed | missing |
| 41 | High Inquisitor | partially-confirmed | confirmed | quest-or-task | static-award-candidate | unresolved | partially-confirmed | missing |
| 42 | Worm Whacker | unresolved | confirmed | quest-or-task | unresolved | unresolved | unresolved | missing |
| 43 | King Tibianus Fan | unresolved | confirmed | quest-or-task | unresolved | unresolved | unresolved | missing |
| 44 | Just in Time | unresolved | confirmed | quest-or-task, exploration | unresolved | unresolved | unresolved | missing |
| 45 | Perfect Fool | partially-confirmed | confirmed | quest-or-task | static-award-candidate | unresolved | partially-confirmed | missing |
| 46 | Mathemagician | partially-confirmed | confirmed | quest-or-task, dialogue | static-award-candidate | unresolved | partially-confirmed | missing |
| 47 | Archpostman | partially-confirmed | confirmed | quest-or-task | static-award-candidate | unresolved | partially-confirmed | missing |
| 48 | Matchmaker | partially-confirmed | confirmed | quest-or-task | static-award-candidate | unresolved | partially-confirmed | missing |
| 49 | His True Face | unresolved | confirmed | quest-or-task, exploration, dialogue | unresolved | unresolved | unresolved | missing |
| 50 | Razing! | unresolved | confirmed | quest-or-task | unresolved | unresolved | unresolved | missing |
| 51 | Master Thief | unresolved | confirmed | quest-or-task | unresolved | unresolved | unresolved | missing |
| 52 | Amateur Actor | unresolved | confirmed | quest-or-task | unresolved | unresolved | unresolved | missing |
| 53 | Scrapper | unresolved | confirmed | quest-or-task | unresolved | unresolved | unresolved | missing |
| 54 | Greenhorn | unresolved | confirmed | quest-or-task | unresolved | unresolved | unresolved | missing |
| 55 | Warlord of Svargrond | unresolved | confirmed | quest-or-task | reference-without-static-award | unresolved | unresolved | missing |
| 56 | Herbicide | unresolved | confirmed | quest-or-task | unresolved | unresolved | unresolved | missing |
| 57 | Annihilator | unresolved | confirmed | quest-or-task | unresolved | unresolved | unresolved | missing |
| 58 | Master of the Nexus | partially-confirmed | confirmed | quest-or-task | static-award-candidate | unresolved | partially-confirmed | missing |
| 59 | Talented Dancer | partially-confirmed | confirmed | quest-or-task | static-award-candidate | unresolved | partially-confirmed | missing |
| 60 | Allow Cookies? | partially-confirmed | confirmed | quest-or-task | static-award-candidate | unresolved | partially-confirmed | missing |
| 61 | Ruthless | unresolved | confirmed | quest-or-task | unresolved | unresolved | unresolved | missing |
| 62 | Champion of Chazorai | partially-confirmed | confirmed | quest-or-task | static-award-candidate | unresolved | partially-confirmed | missing |
| 63 | Wayfarer | partially-confirmed | confirmed | quest-or-task | static-award-candidate | unresolved | partially-confirmed | missing |
| 64 | Waverider | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 65 | Rockstar | partially-confirmed | confirmed | item-or-interaction, progress-threshold | static-progress-candidate | unresolved | partially-confirmed | missing |
| 66 | Allowance Collector | partially-confirmed | confirmed | other | static-progress-candidate | unresolved | partially-confirmed | missing |
| 67 | High-Flyer | unresolved | confirmed | quest-or-task, exploration, progress-threshold | unresolved | unresolved | unresolved | missing |
| 68 | Clay Fighter | partially-confirmed | confirmed | other | static-award-candidate | unresolved | partially-confirmed | missing |
| 69 | Masquerader | partially-confirmed | confirmed | item-or-interaction | static-progress-candidate | unresolved | partially-confirmed | missing |
| 70 | Deep Sea Diver | unresolved | confirmed | item-or-interaction | unresolved | unresolved | unresolved | missing |
| 71 | Firewalker | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 72 | Here, Fishy Fishy! | partially-confirmed | confirmed | event-or-raid | static-progress-candidate | unresolved | partially-confirmed | missing |
| 73 | Green Thumb | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 74 | Potion Addict | partially-confirmed | confirmed | item-or-interaction, progress-threshold | static-progress-candidate | unresolved | partially-confirmed | missing |
| 75 | Ice Sculptor | partially-confirmed | confirmed | item-or-interaction | static-award-candidate | unresolved | partially-confirmed | missing |
| 76 | Interior Decorator | partially-confirmed | confirmed | collection, item-or-interaction | static-progress-candidate | unresolved | partially-confirmed | missing |
| 77 | Jinx | unresolved | confirmed | item-or-interaction | unresolved | unresolved | unresolved | missing |
| 78 | Lucky Devil | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 79 | Marblelous | partially-confirmed | confirmed | other | static-award-candidate | unresolved | partially-confirmed | missing |
| 80 | Party Animal | partially-confirmed | confirmed | item-or-interaction, progress-threshold | static-progress-candidate | unresolved | partially-confirmed | missing |
| 81 | Fireworks in the Sky | partially-confirmed | confirmed | item-or-interaction | static-progress-candidate | unresolved | partially-confirmed | missing |
| 82 | Quick as a Turtle | unresolved | confirmed | exploration, progress-threshold | unresolved | unresolved | unresolved | missing |
| 83 | Polisher | partially-confirmed | confirmed | item-or-interaction | static-progress-candidate | unresolved | partially-confirmed | missing |
| 84 | Ship's Kobold | partially-confirmed | confirmed | exploration, progress-threshold | static-progress-candidate | unresolved | partially-confirmed | missing |
| 85 | Steampunked | unresolved | confirmed | quest-or-task, exploration, progress-threshold | unresolved | unresolved | unresolved | missing |
| 86 | Vanity | unresolved | confirmed | item-or-interaction, progress-threshold | unresolved | unresolved | unresolved | missing |
| 87 | Superstitious | unresolved | confirmed | item-or-interaction, progress-threshold | unresolved | unresolved | unresolved | missing |
| 88 | Turncoat | unresolved | confirmed | quest-or-task | unresolved | unresolved | unresolved | missing |
| 89 | Marble Madness | partially-confirmed | confirmed | other | static-progress-candidate | unresolved | partially-confirmed | missing |
| 90 | Clay to Fame | partially-confirmed | confirmed | other | static-progress-candidate | unresolved | partially-confirmed | missing |
| 91 | Cold as Ice | partially-confirmed | confirmed | item-or-interaction | static-progress-candidate | unresolved | partially-confirmed | missing |
| 92 | Exquisite Taste | partially-confirmed | confirmed | collection | static-progress-candidate | unresolved | partially-confirmed | missing |
| 93 | Jamjam | unresolved | confirmed | quest-or-task | unresolved | unresolved | unresolved | missing |
| 94 | I Did My Part | unresolved | confirmed | quest-or-task, combat, item-or-interaction, exploration | unresolved | unresolved | unresolved | missing |
| 96 | Teamplayer | unresolved | confirmed | quest-or-task, combat, exploration | unresolved | unresolved | unresolved | missing |
| 97 | Daring Trespasser | unresolved | confirmed | quest-or-task, exploration | unresolved | unresolved | unresolved | missing |
| 98 | Slayer of Anmothra | unresolved | confirmed | quest-or-task, combat, event-or-raid | unresolved | unresolved | unresolved | missing |
| 99 | Slayer of Chikhaton | unresolved | confirmed | quest-or-task, combat, event-or-raid | unresolved | unresolved | unresolved | missing |
| 100 | Slayer of Irahsae | unresolved | confirmed | quest-or-task, combat, event-or-raid | unresolved | unresolved | unresolved | missing |
| 101 | Slayer of Phrodomo | unresolved | confirmed | quest-or-task, combat, event-or-raid | unresolved | unresolved | unresolved | missing |
| 102 | Slayer of Teneshpar | unresolved | confirmed | quest-or-task, combat, event-or-raid | unresolved | unresolved | unresolved | missing |
| 103 | Cocoon of Doom | unresolved | confirmed | quest-or-task, combat | unresolved | unresolved | unresolved | missing |
| 104 | Devovorga's Nemesis | unresolved | confirmed | quest-or-task, combat | unresolved | unresolved | unresolved | missing |
| 105 | Mister Sandman | unresolved | confirmed | item-or-interaction, progress-threshold | unresolved | unresolved | unresolved | missing |
| 106 | Rock Me to Sleep | unresolved | confirmed | item-or-interaction, progress-threshold | unresolved | unresolved | unresolved | missing |
| 107 | Modest Guest | unresolved | confirmed | progress-threshold | unresolved | unresolved | unresolved | missing |
| 108 | Joke's on You | partially-confirmed | confirmed | item-or-interaction | static-award-candidate | unresolved | partially-confirmed | missing |
| 109 | Oops | partially-confirmed | confirmed | item-or-interaction | static-award-candidate | unresolved | partially-confirmed | missing |
| 110 | Bluebarian | partially-confirmed | confirmed | item-or-interaction, progress-threshold | static-progress-candidate | unresolved | partially-confirmed | missing |
| 111 | Demonic Barkeeper | partially-confirmed | confirmed | other | static-progress-candidate | unresolved | partially-confirmed | missing |
| 112 | The Snowman | unresolved | confirmed | item-or-interaction | unresolved | unresolved | unresolved | missing |
| 113 | Number of the Beast | partially-confirmed | confirmed | progress-threshold | static-award-candidate | unresolved | partially-confirmed | missing |
| 114 | I Need a Hug | unresolved | confirmed | item-or-interaction | unresolved | unresolved | unresolved | missing |
| 115 | Slim Chance | unresolved | confirmed | item-or-interaction, exploration, progress-threshold | unresolved | unresolved | unresolved | missing |
| 116 | Rocket in Pocket | partially-confirmed | confirmed | item-or-interaction | static-progress-candidate | unresolved | partially-confirmed | missing |
| 117 | Make a Wish | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 118 | Santa's Li'l Helper | unresolved | confirmed | item-or-interaction | unresolved | unresolved | unresolved | missing |
| 119 | Cursed! | partially-confirmed | confirmed | other | static-award-candidate | unresolved | partially-confirmed | missing |
| 120 | Free Items! | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 121 | Rollercoaster | partially-confirmed | confirmed | progress-threshold | static-progress-candidate | unresolved | partially-confirmed | missing |
| 122 | Transmutator | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 123 | Berserker | unresolved | confirmed | item-or-interaction | unresolved | unresolved | unresolved | missing |
| 124 | Mastermind | unresolved | confirmed | item-or-interaction | unresolved | unresolved | unresolved | missing |
| 125 | Sharpshooter | unresolved | confirmed | item-or-interaction | unresolved | unresolved | unresolved | missing |
| 126 | Do Not Disturb | unresolved | confirmed | progress-threshold | unresolved | unresolved | unresolved | missing |
| 127 | Let the Sunshine In | unresolved | confirmed | item-or-interaction, progress-threshold | unresolved | unresolved | unresolved | missing |
| 128 | Bad Timing | partially-confirmed | confirmed | progress-threshold | static-progress-candidate | unresolved | partially-confirmed | missing |
| 129 | Nothing Can Stop Me | unresolved | confirmed | item-or-interaction, progress-threshold | unresolved | unresolved | unresolved | missing |
| 130 | Happy Farmer | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 131 | Natural Sweetener | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 132 | Homebrewed | unresolved | confirmed | item-or-interaction | unresolved | unresolved | unresolved | missing |
| 133 | Gold Digger | partially-confirmed | confirmed | exploration | static-progress-candidate | unresolved | partially-confirmed | missing |
| 134 | The Undertaker | partially-confirmed | confirmed | item-or-interaction | static-progress-candidate | unresolved | partially-confirmed | missing |
| 135 | Cookie Monster | unresolved | confirmed | progress-threshold | unresolved | unresolved | unresolved | missing |
| 136 | The Cake's the Truth | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 137 | Sweet Tooth | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 138 | With a Cherry on Top | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 139 | Mutated Presents | partially-confirmed | confirmed | other | static-award-candidate | unresolved | partially-confirmed | missing |
| 140 | Keeper of the Flame | unresolved | confirmed | event-or-raid | unresolved | unresolved | unresolved | missing |
| 141 | True Lightbearer | unresolved | confirmed | event-or-raid | unresolved | unresolved | unresolved | missing |
| 142 | Godslayer | unresolved | confirmed | quest-or-task, item-or-interaction | unresolved | unresolved | unresolved | missing |
| 143 | The Day After | unresolved | confirmed | dialogue | unresolved | unresolved | unresolved | missing |
| 144 | Commitment Phobic | unresolved | confirmed | collection, progress-threshold | unresolved | unresolved | unresolved | missing |
| 145 | Heartbreaker | unresolved | confirmed | dialogue, progress-threshold | unresolved | unresolved | unresolved | missing |
| 146 | Swift Death | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 147 | Brutal Politeness | partially-confirmed | confirmed | other | static-award-candidate | unresolved | partially-confirmed | missing |
| 148 | Life on the Streets | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 149 | Skull and Bones | partially-confirmed | confirmed | other | static-award-candidate | unresolved | partially-confirmed | missing |
| 150 | Nightmare Walker | partially-confirmed | confirmed | other | static-award-candidate | unresolved | partially-confirmed | missing |
| 151 | Exemplary Citizen | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 152 | Demonbane | partially-confirmed | confirmed | other | static-award-candidate | unresolved | partially-confirmed | missing |
| 153 | Of Wolves and Bears | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 154 | Hunting with Style | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 155 | Fool at Heart | partially-confirmed | confirmed | other | static-award-candidate | unresolved | partially-confirmed | missing |
| 156 | In Shining Armor | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 157 | Aristocrat | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 158 | Out in the Snowstorm | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 159 | One Thousand and One | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 160 | Swashbuckler | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 161 | Way of the Shaman | partially-confirmed | confirmed | other | static-award-candidate | unresolved | partially-confirmed | missing |
| 162 | Ritualist | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 163 | Master of War | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 164 | Wild Warrior | partially-confirmed | confirmed | other | static-progress-candidate | unresolved | partially-confirmed | missing |
| 165 | Peazzekeeper | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 166 | Yalahari of Wisdom | unresolved | confirmed | quest-or-task | unresolved | unresolved | unresolved | missing |
| 167 | Yalahari of Power | unresolved | confirmed | quest-or-task | unresolved | unresolved | unresolved | missing |
| 168 | Piece of Cake | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 169 | Alumni | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 170 | Warlock | partially-confirmed | confirmed | other | static-award-candidate | unresolved | partially-confirmed | missing |
| 171 | Bunny Slipped | unresolved | confirmed | quest-or-task | unresolved | unresolved | unresolved | missing |
| 172 | Guinea Pig | unresolved | confirmed | quest-or-task | unresolved | unresolved | unresolved | missing |
| 173 | Merry Adventures | unresolved | confirmed | quest-or-task | unresolved | unresolved | unresolved | missing |
| 174 | Afraid of no Ghost! | unresolved | confirmed | quest-or-task | unresolved | unresolved | unresolved | missing |
| 175 | Extreme Degustation | unresolved | confirmed | quest-or-task, collection | unresolved | unresolved | unresolved | missing |
| 176 | Cake Conqueror | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 177 | Baby Sitter | unresolved | confirmed | event-or-raid | unresolved | unresolved | unresolved | missing |
| 178 | Nanny from Hell | unresolved | confirmed | event-or-raid | unresolved | unresolved | unresolved | missing |
| 179 | Ghost Sailor | unresolved | confirmed | quest-or-task | unresolved | unresolved | unresolved | missing |
| 180 | Spectral Traveller | unresolved | confirmed | quest-or-task | unresolved | unresolved | unresolved | missing |
| 181 | Nether Pirate | unresolved | confirmed | quest-or-task | unresolved | unresolved | unresolved | missing |
| 182 | Scourge of Death | unresolved | confirmed | quest-or-task | unresolved | unresolved | unresolved | missing |
| 183 | Fire Lighter | unresolved | confirmed | item-or-interaction, event-or-raid | unresolved | unresolved | unresolved | missing |
| 184 | Witches Lil' Helper | unresolved | confirmed | event-or-raid | unresolved | unresolved | unresolved | missing |
| 185 | Banebringers' Bane | unresolved | confirmed | event-or-raid | unresolved | unresolved | unresolved | missing |
| 186 | Fire Devil | unresolved | confirmed | item-or-interaction, event-or-raid | unresolved | unresolved | unresolved | missing |
| 187 | Pyromaniac | unresolved | confirmed | item-or-interaction, event-or-raid | unresolved | unresolved | unresolved | missing |
| 188 | Honorary Witch | unresolved | confirmed | event-or-raid | unresolved | unresolved | unresolved | missing |
| 189 | Natural Born Cowboy | partially-confirmed | confirmed | mount-taming | static-award-candidate | unresolved | partially-confirmed | missing |
| 190 | Petrologist | partially-confirmed | confirmed | item-or-interaction | static-progress-candidate | unresolved | partially-confirmed | missing |
| 191 | Hidden Powers | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 192 | I Like it Fancy | unresolved | confirmed | item-or-interaction | unresolved | unresolved | unresolved | missing |
| 193 | Skin-Deep | partially-confirmed | confirmed | other | static-progress-candidate | unresolved | partially-confirmed | missing |
| 194 | Ashes to Dust | partially-confirmed | confirmed | item-or-interaction, progress-threshold | static-progress-candidate | unresolved | partially-confirmed | missing |
| 195 | Smart Thinking | conflicting | missing | unresolved | unresolved | unresolved | conflicting | missing |
| 196 | Safely Stored Away | unresolved | confirmed | progress-threshold | unresolved | unresolved | unresolved | missing |
| 197 | Something's in There | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 198 | Silent Pet | unresolved | confirmed | collection | unresolved | unresolved | unresolved | missing |
| 199 | Snowbunny | partially-confirmed | confirmed | other | static-progress-candidate | unresolved | partially-confirmed | missing |
| 200 | Dark Voodoo Priest | partially-confirmed | confirmed | item-or-interaction | static-award-candidate | unresolved | partially-confirmed | missing |
| 201 | Nomad Soul | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 202 | Truth Be Told | partially-confirmed | confirmed | quest-or-task | static-award-candidate | unresolved | partially-confirmed | missing |
| 203 | You Don't Know Jack | partially-confirmed | confirmed | quest-or-task | static-award-candidate | unresolved | partially-confirmed | missing |
| 204 | Berry Picker | unresolved | confirmed | event-or-raid | unresolved | unresolved | unresolved | missing |
| 205 | True Colours | unresolved | confirmed | event-or-raid, progress-threshold | unresolved | unresolved | unresolved | missing |
| 206 | Master Shapeshifter | unresolved | confirmed | event-or-raid | unresolved | unresolved | unresolved | missing |
| 207 | Slimer | unresolved | confirmed | item-or-interaction, progress-threshold | unresolved | unresolved | unresolved | missing |
| 208 | Mageslayer | partially-confirmed | confirmed | combat | static-award-candidate | unresolved | partially-confirmed | missing |
| 209 | Biodegradable | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 210 | Eye of the Deep | unresolved | confirmed | combat | unresolved | unresolved | unresolved | missing |
| 211 | Invader of the Deep | unresolved | confirmed | combat | unresolved | unresolved | unresolved | missing |
| 212 | Firefighter | unresolved | confirmed | event-or-raid | unresolved | unresolved | unresolved | missing |
| 213 | Deer Hunt | unresolved | confirmed | combat | unresolved | unresolved | unresolved | missing |
| 214 | Askarak Nemesis | unresolved | confirmed | combat | unresolved | unresolved | unresolved | missing |
| 215 | Shaburak Nemesis | unresolved | confirmed | combat | unresolved | unresolved | unresolved | missing |
| 216 | Fearless | unresolved | confirmed | event-or-raid | unresolved | unresolved | unresolved | missing |
| 217 | Doctor! Doctor! | partially-confirmed | confirmed | other | static-progress-candidate | unresolved | partially-confirmed | missing |
| 218 | Beak Doctor | partially-confirmed | confirmed | other | static-progress-candidate | unresolved | partially-confirmed | missing |
| 219 | Mystic Fabric Magic | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 221 | Arachnoise | unresolved | confirmed | combat | unresolved | unresolved | unresolved | missing |
| 222 | Rootless Behaviour | unresolved | confirmed | combat | unresolved | unresolved | unresolved | missing |
| 223 | Twisted Mutation | unresolved | confirmed | combat | unresolved | unresolved | unresolved | missing |
| 224 | Beautiful Agony | unresolved | confirmed | combat | unresolved | unresolved | unresolved | missing |
| 225 | Scorched Flames | unresolved | confirmed | combat | unresolved | unresolved | unresolved | missing |
| 226 | Crawling Death | partially-confirmed | confirmed | combat | static-award-candidate | unresolved | partially-confirmed | missing |
| 227 | The Serpent's Bride | unresolved | confirmed | combat | unresolved | unresolved | unresolved | missing |
| 228 | No More Hiding | unresolved | confirmed | combat | unresolved | unresolved | unresolved | missing |
| 229 | The Gates of Hell | unresolved | confirmed | combat | unresolved | unresolved | unresolved | missing |
| 230 | The Drowned Sea God | unresolved | confirmed | combat | unresolved | unresolved | unresolved | missing |
| 231 | Spareribs for Dinner | unresolved | confirmed | combat | unresolved | unresolved | unresolved | missing |
| 232 | Breaking the Ice | unresolved | confirmed | combat | unresolved | unresolved | unresolved | missing |
| 233 | Just Cracked Me Up! | unresolved | confirmed | combat | unresolved | unresolved | unresolved | missing |
| 234 | Something Smells | unresolved | confirmed | combat | unresolved | unresolved | unresolved | missing |
| 235 | Meat Skewer | unresolved | confirmed | combat | unresolved | unresolved | unresolved | missing |
| 236 | One Less | unresolved | confirmed | combat | unresolved | unresolved | unresolved | missing |
| 237 | Hissing Downfall | unresolved | confirmed | combat | unresolved | unresolved | unresolved | missing |
| 238 | Choking on Her Venom | unresolved | confirmed | combat | unresolved | unresolved | unresolved | missing |
| 239 | Blood-Red Snapper | unresolved | confirmed | combat | unresolved | unresolved | unresolved | missing |
| 240 | Back into the Abyss | unresolved | confirmed | combat | unresolved | unresolved | unresolved | missing |
| 241 | Pwned a Lot of Fur | unresolved | confirmed | quest-or-task, combat | unresolved | unresolved | unresolved | missing |
| 242 | Honest Finder | unresolved | confirmed | event-or-raid | unresolved | unresolved | unresolved | missing |
| 243 | Goldhunter | unresolved | confirmed | event-or-raid | unresolved | unresolved | unresolved | missing |
| 244 | Trail of the Ape God | unresolved | confirmed | combat, event-or-raid | unresolved | unresolved | unresolved | missing |
| 245 | Someone's Bored | partially-confirmed | confirmed | combat | static-award-candidate | unresolved | partially-confirmed | missing |
| 246 | Whistle-Blower | unresolved | confirmed | event-or-raid | unresolved | unresolved | unresolved | missing |
| 247 | Torn Treasures | unresolved | confirmed | event-or-raid, progress-threshold | unresolved | unresolved | unresolved | missing |
| 248 | Loyal Subject | unresolved | confirmed | dialogue, event-or-raid | unresolved | unresolved | unresolved | missing |
| 249 | Desert Fisher | unresolved | confirmed | event-or-raid | unresolved | unresolved | unresolved | missing |
| 251 | Dog Sitter | unresolved | confirmed | collection, event-or-raid | unresolved | unresolved | unresolved | missing |
| 252 | Ice Harvester | unresolved | confirmed | item-or-interaction, event-or-raid | unresolved | unresolved | unresolved | missing |
| 253 | Preservationist | unresolved | confirmed | item-or-interaction | unresolved | unresolved | unresolved | missing |
| 254 | Chest Robber | unresolved | confirmed | event-or-raid | unresolved | unresolved | unresolved | missing |
| 255 | Down the Drain | unresolved | confirmed | combat, event-or-raid | unresolved | unresolved | unresolved | missing |
| 256 | Fire from the Earth | unresolved | confirmed | combat, event-or-raid | unresolved | unresolved | unresolved | missing |
| 257 | Minor Disturbance | unresolved | confirmed | quest-or-task, progress-threshold | unresolved | unresolved | unresolved | missing |
| 258 | Dazzler | unresolved | confirmed | quest-or-task, progress-threshold | unresolved | unresolved | unresolved | missing |
| 259 | Hive Blinder | unresolved | confirmed | quest-or-task, progress-threshold | unresolved | unresolved | unresolved | missing |
| 260 | Hickup | unresolved | confirmed | quest-or-task, progress-threshold | unresolved | unresolved | unresolved | missing |
| 261 | Heartburn | unresolved | confirmed | quest-or-task, progress-threshold | unresolved | unresolved | unresolved | missing |
| 262 | Stomach Ulcer | unresolved | confirmed | quest-or-task, progress-threshold | unresolved | unresolved | unresolved | missing |
| 263 | Planter | unresolved | confirmed | quest-or-task, progress-threshold | unresolved | unresolved | unresolved | missing |
| 264 | Pimple | unresolved | confirmed | quest-or-task, progress-threshold | unresolved | unresolved | unresolved | missing |
| 265 | Suppressor | unresolved | confirmed | quest-or-task, progress-threshold | unresolved | unresolved | unresolved | missing |
| 266 | Gatherer | unresolved | confirmed | quest-or-task, progress-threshold | unresolved | unresolved | unresolved | missing |
| 267 | Supplier | unresolved | confirmed | quest-or-task, progress-threshold | unresolved | unresolved | unresolved | missing |
| 268 | Chitin Bane | unresolved | confirmed | quest-or-task, progress-threshold | unresolved | unresolved | unresolved | missing |
| 269 | Guard Killer | unresolved | confirmed | quest-or-task, combat, progress-threshold | unresolved | unresolved | unresolved | missing |
| 270 | Hive Infiltrator | unresolved | confirmed | quest-or-task, combat, progress-threshold | unresolved | unresolved | unresolved | missing |
| 271 | Exterminator | unresolved | confirmed | quest-or-task, combat, progress-threshold | unresolved | unresolved | unresolved | missing |
| 272 | Headache | unresolved | confirmed | quest-or-task, progress-threshold | unresolved | unresolved | unresolved | missing |
| 273 | Confusion | unresolved | confirmed | progress-threshold | unresolved | unresolved | unresolved | missing |
| 274 | Manic | unresolved | confirmed | progress-threshold | unresolved | unresolved | unresolved | missing |
| 276 | Navigational Error | unresolved | confirmed | quest-or-task, dialogue | unresolved | unresolved | unresolved | missing |
| 277 | Si, Ariki! | partially-confirmed | confirmed | other | static-award-candidate | unresolved | partially-confirmed | missing |
| 278 | Guardian Downfall | unresolved | confirmed | combat | unresolved | unresolved | unresolved | missing |
| 279 | Death Song | unresolved | confirmed | combat | unresolved | unresolved | unresolved | missing |
| 280 | Depth Dwellers | unresolved | confirmed | combat | unresolved | unresolved | unresolved | missing |
| 281 | Gem Cutter | unresolved | confirmed | quest-or-task | unresolved | unresolved | unresolved | missing |
| 282 | Spolium Profundis | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 283 | Bane of the Hive | unresolved | confirmed | collection | unresolved | unresolved | unresolved | missing |
| 285 | Hive War Veteran | unresolved | confirmed | quest-or-task | unresolved | unresolved | unresolved | missing |
| 286 | Hive Fighter | unresolved | confirmed | quest-or-task | unresolved | unresolved | unresolved | missing |
| 287 | Howly Silence | unresolved | confirmed | combat | unresolved | unresolved | unresolved | missing |
| 288 | Dream's Over | unresolved | confirmed | combat | unresolved | unresolved | unresolved | missing |
| 289 | Zzztill Zzztanding! | unresolved | confirmed | combat | unresolved | unresolved | unresolved | missing |
| 290 | Stepped on a Big Toe | unresolved | confirmed | combat | unresolved | unresolved | unresolved | missing |
| 291 | Kapow! | unresolved | confirmed | combat | unresolved | unresolved | unresolved | missing |
| 292 | Enter zze Draken! | unresolved | confirmed | combat | unresolved | unresolved | unresolved | missing |
| 293 | King of the Ring | unresolved | confirmed | combat | unresolved | unresolved | unresolved | missing |
| 294 | Back from the Dead | unresolved | confirmed | combat | unresolved | unresolved | unresolved | missing |
| 295 | Pwned All Fur | unresolved | confirmed | quest-or-task, combat | unresolved | unresolved | unresolved | missing |
| 297 | Bibby's Bloodbath | unresolved | confirmed | combat | unresolved | unresolved | unresolved | missing |
| 298 | Nestling | unresolved | confirmed | combat, progress-threshold | unresolved | unresolved | unresolved | missing |
| 299 | Becoming a Bigfoot | partially-confirmed | confirmed | quest-or-task | static-award-candidate | unresolved | partially-confirmed | missing |
| 300 | Gnome Little Helper | partially-confirmed | confirmed | quest-or-task | static-award-candidate | unresolved | partially-confirmed | missing |
| 301 | Gnome Friend | partially-confirmed | confirmed | quest-or-task | static-award-candidate | unresolved | partially-confirmed | missing |
| 302 | Gnomelike | partially-confirmed | confirmed | quest-or-task | static-award-candidate | unresolved | partially-confirmed | missing |
| 303 | Honorary Gnome | partially-confirmed | confirmed | quest-or-task | static-award-candidate | unresolved | partially-confirmed | missing |
| 304 | Crystals in Love | partially-confirmed | confirmed | quest-or-task | static-award-candidate | unresolved | partially-confirmed | missing |
| 305 | Substitute Tinker | partially-confirmed | confirmed | quest-or-task | static-award-candidate | unresolved | partially-confirmed | missing |
| 306 | Spore Hunter | partially-confirmed | confirmed | quest-or-task, collection | static-award-candidate | unresolved | partially-confirmed | missing |
| 307 | Grinding Again | partially-confirmed | confirmed | quest-or-task | static-award-candidate | unresolved | partially-confirmed | missing |
| 308 | Dungeon Cleaner | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 309 | Crystal Keeper | partially-confirmed | confirmed | quest-or-task | static-award-candidate | unresolved | partially-confirmed | missing |
| 310 | Call Me Sparky | partially-confirmed | confirmed | quest-or-task | static-award-candidate | unresolved | partially-confirmed | missing |
| 311 | One Foot Vs. Many | partially-confirmed | confirmed | quest-or-task | static-award-candidate | unresolved | partially-confirmed | missing |
| 312 | The Picky Pig | partially-confirmed | confirmed | quest-or-task | static-award-candidate | unresolved | partially-confirmed | missing |
| 313 | Diplomatic Immunity | unresolved | confirmed | item-or-interaction, progress-threshold | unresolved | unresolved | unresolved | missing |
| 314 | Fall of the Fallen | unresolved | confirmed | item-or-interaction, progress-threshold | unresolved | unresolved | unresolved | missing |
| 315 | Death on Strike | unresolved | confirmed | item-or-interaction, progress-threshold | unresolved | unresolved | unresolved | missing |
| 316 | Death from Below | unresolved | confirmed | combat, item-or-interaction | unresolved | unresolved | unresolved | missing |
| 317 | Gnomebane's Bane | unresolved | confirmed | combat, item-or-interaction | unresolved | unresolved | unresolved | missing |
| 318 | Final Strike | unresolved | confirmed | combat, item-or-interaction | unresolved | unresolved | unresolved | missing |
| 319 | Goo Goo Dancer | partially-confirmed | confirmed | item-or-interaction | static-progress-candidate | unresolved | partially-confirmed | missing |
| 320 | Funghitastic | unresolved | confirmed | quest-or-task | unresolved | unresolved | unresolved | missing |
| 321 | Crystal Clear | unresolved | confirmed | quest-or-task | unresolved | unresolved | unresolved | missing |
| 322 | Gnomish Art Of War | unresolved | confirmed | quest-or-task | unresolved | unresolved | unresolved | missing |
| 324 | True Dedication | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 325 | Task Manager | unresolved | confirmed | quest-or-task, progress-threshold | unresolved | unresolved | unresolved | missing |
| 326 | Gravedigger | unresolved | confirmed | quest-or-task | unresolved | unresolved | unresolved | missing |
| 327 | Repenter | unresolved | confirmed | quest-or-task, dialogue | unresolved | unresolved | unresolved | missing |
| 328 | Umbral Swordsman | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 331 | Cave Completionist | unresolved | confirmed | collection | unresolved | unresolved | unresolved | missing |
| 332 | Umbral Bladelord | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 333 | Umbral Headsman | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 334 | Umbral Executioner | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 335 | Umbral Brawler | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 336 | Umbral Berserker | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 337 | Umbral Archer | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 338 | Umbral Marksman | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 339 | Umbral Harbinger | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 340 | Umbral Master | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 341 | Nevermending Story | unresolved | confirmed | quest-or-task, collection | unresolved | unresolved | unresolved | missing |
| 342 | Luring Silence | unresolved | confirmed | quest-or-task | unresolved | unresolved | unresolved | missing |
| 343 | Never Surrender | unresolved | confirmed | combat | unresolved | unresolved | unresolved | missing |
| 344 | Dream Wright | unresolved | confirmed | quest-or-task, progress-threshold | unresolved | unresolved | unresolved | missing |
| 345 | Ending the Horror | unresolved | confirmed | quest-or-task | unresolved | unresolved | unresolved | missing |
| 346 | Sleepwalking | unresolved | confirmed | quest-or-task | unresolved | unresolved | unresolved | missing |
| 347 | Dream Warden | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 348 | Prison Break | unresolved | confirmed | combat | unresolved | unresolved | unresolved | missing |
| 349 | Noblesse Obliterated | unresolved | confirmed | combat | unresolved | unresolved | unresolved | missing |
| 350 | Elementary, My Dear | unresolved | confirmed | quest-or-task, item-or-interaction | unresolved | unresolved | unresolved | missing |
| 351 | Rathleton Commoner | unresolved | confirmed | quest-or-task | unresolved | unresolved | unresolved | missing |
| 352 | Rathleton Inhabitant | unresolved | confirmed | quest-or-task | unresolved | unresolved | unresolved | missing |
| 353 | Rathleton Citizen | unresolved | confirmed | quest-or-task | unresolved | unresolved | unresolved | missing |
| 354 | Combo Master | unresolved | confirmed | quest-or-task, progress-threshold | unresolved | unresolved | unresolved | missing |
| 355 | Glooth Engineer | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 356 | Lion's Den Explorer | partially-confirmed | confirmed | quest-or-task | static-award-candidate | unresolved | partially-confirmed | missing |
| 357 | Seasoned Adventurer | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 358 | Mind the Step! | unresolved | confirmed | quest-or-task, collection | unresolved | unresolved | unresolved | missing |
| 359 | Rathleton Squire | unresolved | confirmed | quest-or-task | unresolved | unresolved | unresolved | missing |
| 360 | The Professor's Nut | partially-confirmed | confirmed | quest-or-task, item-or-interaction | static-award-candidate | unresolved | partially-confirmed | missing |
| 361 | Plant vs. Minos | unresolved | confirmed | combat | unresolved | unresolved | unresolved | missing |
| 362 | Rumble in the Plant | unresolved | confirmed | combat | unresolved | unresolved | unresolved | missing |
| 363 | Robo Chop | unresolved | confirmed | combat | unresolved | unresolved | unresolved | missing |
| 364 | Go with da Lava Flow | partially-confirmed | confirmed | quest-or-task | static-award-candidate | unresolved | partially-confirmed | missing |
| 365 | Wail of the Banshee | partially-confirmed | confirmed | quest-or-task | static-award-candidate | unresolved | partially-confirmed | missing |
| 366 | Publicity | unresolved | confirmed | quest-or-task | unresolved | unresolved | unresolved | missing |
| 367 | Snake Charmer | unresolved | confirmed | quest-or-task | unresolved | unresolved | unresolved | missing |
| 368 | Hoard of the Dragon | partially-confirmed | confirmed | quest-or-task, progress-threshold | static-award-candidate | unresolved | partially-confirmed | missing |
| 370 | Little Ball of Wool | unresolved | confirmed | mount-taming | unresolved | unresolved | unresolved | missing |
| 371 | Luminous Kitty | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 372 | The Right Tone | unresolved | confirmed | mount-taming | unresolved | unresolved | unresolved | missing |
| 373 | Loyal Lad | unresolved | confirmed | mount-taming | unresolved | unresolved | unresolved | missing |
| 374 | Dragon Mimicry | unresolved | confirmed | mount-taming | unresolved | unresolved | unresolved | missing |
| 375 | Scales and Tail | unresolved | confirmed | mount-taming | unresolved | unresolved | unresolved | missing |
| 376 | Fata Morgana | unresolved | confirmed | mount-taming | unresolved | unresolved | unresolved | missing |
| 377 | Fabled Construction | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 378 | Mind the Dog! | unresolved | confirmed | mount-taming | unresolved | unresolved | unresolved | missing |
| 379 | Magnetised | unresolved | confirmed | mount-taming | unresolved | unresolved | unresolved | missing |
| 380 | Golden Sands | unresolved | confirmed | mount-taming | unresolved | unresolved | unresolved | missing |
| 381 | Friend of Elves | unresolved | confirmed | mount-taming | unresolved | unresolved | unresolved | missing |
| 382 | Lovely Dots | unresolved | confirmed | mount-taming | unresolved | unresolved | unresolved | missing |
| 383 | Way to Hell | unresolved | confirmed | mount-taming | unresolved | unresolved | unresolved | missing |
| 384 | Beneath the Sea | unresolved | confirmed | mount-taming | unresolved | unresolved | unresolved | missing |
| 385 | Starless Night | unresolved | confirmed | mount-taming | unresolved | unresolved | unresolved | missing |
| 386 | Lion King | unresolved | confirmed | mount-taming | unresolved | unresolved | unresolved | missing |
| 387 | Pecking Order | unresolved | confirmed | mount-taming | unresolved | unresolved | unresolved | missing |
| 388 | Pig-Headed | unresolved | confirmed | mount-taming | unresolved | unresolved | unresolved | missing |
| 389 | Personal Nightmare | unresolved | confirmed | mount-taming | unresolved | unresolved | unresolved | missing |
| 390 | Thick-Skinned | unresolved | confirmed | collection, mount-taming | unresolved | unresolved | unresolved | missing |
| 391 | Chequered Teddy | unresolved | confirmed | mount-taming | unresolved | unresolved | unresolved | missing |
| 392 | Blacknailed | unresolved | confirmed | mount-taming | unresolved | unresolved | unresolved | missing |
| 393 | Slugging Around | unresolved | confirmed | mount-taming | unresolved | unresolved | unresolved | missing |
| 394 | Knock on Wood | unresolved | confirmed | mount-taming | unresolved | unresolved | unresolved | missing |
| 395 | Fried Shrimp | unresolved | confirmed | mount-taming | unresolved | unresolved | unresolved | missing |
| 396 | Out of the Stone Age | unresolved | confirmed | mount-taming | unresolved | unresolved | unresolved | missing |
| 397 | Stuntman | unresolved | confirmed | mount-taming | unresolved | unresolved | unresolved | missing |
| 398 | Gear Up | unresolved | confirmed | mount-taming | unresolved | unresolved | unresolved | missing |
| 399 | Bearbaiting | unresolved | confirmed | mount-taming | unresolved | unresolved | unresolved | missing |
| 400 | Lucky Horseshoe | unresolved | confirmed | mount-taming | unresolved | unresolved | unresolved | missing |
| 401 | Swamp Beast | unresolved | confirmed | mount-taming | unresolved | unresolved | unresolved | missing |
| 402 | Spin-Off | unresolved | confirmed | mount-taming | unresolved | unresolved | unresolved | missing |
| 403 | Icy Glare | unresolved | confirmed | mount-taming | unresolved | unresolved | unresolved | missing |
| 404 | Cartography 101 | unresolved | confirmed | quest-or-task | unresolved | unresolved | unresolved | missing |
| 405 | Lost Palace Raider | unresolved | confirmed | quest-or-task | unresolved | unresolved | unresolved | missing |
| 406 | The More the Merrier | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 408 | Rift Warrior | partially-confirmed | confirmed | quest-or-task | static-award-candidate | unresolved | partially-confirmed | missing |
| 410 | Hat Hunter | partially-confirmed | confirmed | quest-or-task | static-award-candidate | unresolved | partially-confirmed | missing |
| 411 | Ogre Chef | unresolved | confirmed | quest-or-task, progress-threshold | unresolved | unresolved | unresolved | missing |
| 412 | The Call of the Wild | unresolved | confirmed | quest-or-task | unresolved | unresolved | unresolved | missing |
| 413 | Ender of the End | partially-confirmed | confirmed | quest-or-task | static-award-candidate | unresolved | partially-confirmed | missing |
| 414 | Vortex Tamer | partially-confirmed | confirmed | item-or-interaction, mount-taming | static-progress-candidate | unresolved | partially-confirmed | missing |
| 415 | Rhino Rider | unresolved | confirmed | mount-taming | unresolved | unresolved | unresolved | missing |
| 416 | Forbidden Fruit | unresolved | confirmed | item-or-interaction | unresolved | unresolved | unresolved | missing |
| 417 | Forbidden Knowledge | unresolved | confirmed | item-or-interaction | unresolved | unresolved | unresolved | missing |
| 418 | Treasure Hunter | partially-confirmed | confirmed | quest-or-task, item-or-interaction | static-award-candidate | unresolved | partially-confirmed | missing |
| 419 | Reason to Celebrate | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 420 | Toothfairy Assistant | unresolved | confirmed | quest-or-task | unresolved | unresolved | unresolved | missing |
| 421 | Fairy Teasing | partially-confirmed | confirmed | item-or-interaction | static-progress-candidate | unresolved | partially-confirmed | missing |
| 422 | Corruption Contained | partially-confirmed | confirmed | quest-or-task | static-award-candidate | unresolved | partially-confirmed | missing |
| 430 | Little Adventure | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 431 | Little Big Adventure | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 432 | Contender | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 433 | Serious Contender | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 434 | Skilled Hunter | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 435 | Master Hunter | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 436 | Hunting Permit | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 437 | Over the Moon | unresolved | confirmed | quest-or-task | unresolved | unresolved | unresolved | missing |
| 438 | His Days are Counted | partially-confirmed | confirmed | quest-or-task, combat, item-or-interaction | static-award-candidate | unresolved | partially-confirmed | missing |
| 439 | Duked It Out | partially-confirmed | confirmed | quest-or-task, combat, item-or-interaction | static-award-candidate | unresolved | partially-confirmed | missing |
| 440 | Buried the Baron | partially-confirmed | confirmed | quest-or-task, combat, item-or-interaction | static-award-candidate | unresolved | partially-confirmed | missing |
| 441 | Death in the Depths | partially-confirmed | confirmed | combat | static-award-candidate | unresolved | partially-confirmed | missing |
| 442 | Scourge of Scarabs | unresolved | confirmed | quest-or-task, combat, item-or-interaction | unresolved | unresolved | unresolved | missing |
| 443 | Cobbled and Patched | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 444 | Up the Molehill | unresolved | confirmed | mount-taming | unresolved | unresolved | unresolved | missing |
| 445 | Master Debater | unresolved | confirmed | quest-or-task, combat | unresolved | unresolved | unresolved | missing |
| 446 | High and Dry | unresolved | confirmed | dialogue, progress-threshold | unresolved | unresolved | unresolved | missing |
| 447 | Elven Woods | unresolved | confirmed | quest-or-task, exploration | unresolved | unresolved | unresolved | missing |
| 448 | Long Live the Queen | unresolved | confirmed | quest-or-task, exploration | unresolved | unresolved | unresolved | missing |
| 449 | Stronghold of Edron | unresolved | confirmed | quest-or-task, exploration | unresolved | unresolved | unresolved | missing |
| 450 | Dwarven Mines | unresolved | confirmed | quest-or-task, exploration | unresolved | unresolved | unresolved | missing |
| 451 | All Hail the King | unresolved | confirmed | quest-or-task, exploration | unresolved | unresolved | unresolved | missing |
| 452 | Jewel in the Swamp | unresolved | confirmed | quest-or-task, exploration | unresolved | unresolved | unresolved | missing |
| 453 | The Ogre Steppe | unresolved | confirmed | quest-or-task, exploration | unresolved | unresolved | unresolved | missing |
| 454 | Realms of Dreams | unresolved | confirmed | quest-or-task, exploration | unresolved | unresolved | unresolved | missing |
| 455 | Mummy's Dearest | unresolved | confirmed | quest-or-task, exploration | unresolved | unresolved | unresolved | missing |
| 456 | Daraman's Footsteps | unresolved | confirmed | quest-or-task, exploration | unresolved | unresolved | unresolved | missing |
| 457 | King of the Jungle | unresolved | confirmed | quest-or-task, exploration | unresolved | unresolved | unresolved | missing |
| 458 | Ancient Splendor | unresolved | confirmed | quest-or-task, exploration | unresolved | unresolved | unresolved | missing |
| 459 | Liberty Bay Watch | unresolved | confirmed | quest-or-task, exploration | unresolved | unresolved | unresolved | missing |
| 460 | Race to the Pole | unresolved | confirmed | quest-or-task, exploration | unresolved | unresolved | unresolved | missing |
| 461 | Lizard Kingdom | unresolved | confirmed | quest-or-task, exploration | unresolved | unresolved | unresolved | missing |
| 462 | Trip to the Beach | unresolved | confirmed | quest-or-task, exploration | unresolved | unresolved | unresolved | missing |
| 463 | Glooth Punk | unresolved | confirmed | quest-or-task, exploration | unresolved | unresolved | unresolved | missing |
| 464 | Twisted Dreams | unresolved | confirmed | quest-or-task, exploration | unresolved | unresolved | unresolved | missing |
| 465 | Library Liberator | unresolved | confirmed | combat | unresolved | unresolved | unresolved | missing |
| 466 | Spectulation | unresolved | confirmed | exploration | unresolved | unresolved | unresolved | missing |
| 467 | Millennial Falcon | unresolved | confirmed | quest-or-task, combat | unresolved | unresolved | unresolved | missing |
| 468 | Bibliomaniac | unresolved | confirmed | mount-taming | unresolved | unresolved | unresolved | missing |
| 469 | Battle Mage | partially-confirmed | confirmed | combat | static-award-candidate | unresolved | partially-confirmed | missing |
| 470 | Widely Travelled | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 471 | Running the Rift | unresolved | confirmed | item-or-interaction, mount-taming | unresolved | unresolved | unresolved | missing |
| 473 | Exalted Battle Mage | unresolved | confirmed | combat | unresolved | unresolved | unresolved | missing |
| 474 | Areas of Effect | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 475 | Tied the Knot | partially-confirmed | confirmed | quest-or-task, collection | static-award-candidate | unresolved | partially-confirmed | missing |
| 476 | Keeper of the 7 Keys | partially-confirmed | confirmed | quest-or-task | static-award-candidate | unresolved | partially-confirmed | missing |
| 477 | Dream Warrior | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 478 | Moth Whisperer | unresolved | confirmed | mount-taming | unresolved | unresolved | unresolved | missing |
| 479 | Lacewing Catcher | unresolved | confirmed | mount-taming | unresolved | unresolved | unresolved | missing |
| 480 | No Horse Open Sleigh | unresolved | confirmed | collection | unresolved | unresolved | unresolved | missing |
| 481 | Raider in the Dark | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 482 | Dream Catcher | unresolved | confirmed | combat | unresolved | unresolved | unresolved | missing |
| 483 | Champion of Summer | unresolved | confirmed | quest-or-task, combat | unresolved | unresolved | unresolved | missing |
| 484 | Champion of Winter | unresolved | confirmed | quest-or-task, combat | unresolved | unresolved | unresolved | missing |
| 486 | Bewitcher | unresolved | confirmed | event-or-raid, progress-threshold | unresolved | unresolved | unresolved | missing |
| 487 | Gryphon Rider | unresolved | confirmed | mount-taming | unresolved | unresolved | unresolved | missing |
| 488 | Sculptor Apprentice | partially-confirmed | confirmed | other | static-award-candidate | unresolved | partially-confirmed | missing |
| 489 | Sun and Sea | unresolved | confirmed | quest-or-task | unresolved | unresolved | unresolved | missing |
| 490 | A Study in Scarlett | partially-confirmed | confirmed | combat | static-award-candidate | unresolved | partially-confirmed | missing |
| 491 | Avid Spectral Reader | unresolved | confirmed | item-or-interaction | unresolved | unresolved | unresolved | missing |
| 492 | Hippofoddermus | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 493 | Inquisition's Hand | partially-confirmed | confirmed | quest-or-task | static-award-candidate | unresolved | partially-confirmed | missing |
| 494 | The Empire's Glory | unresolved | confirmed | quest-or-task, exploration | unresolved | unresolved | unresolved | missing |
| 495 | Inquisition's Arm | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 496 | Traditionalist | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 497 | Do a Barrel Roll! | unresolved | confirmed | collection | unresolved | unresolved | unresolved | missing |
| 499 | Orcsoberfest Welcome | unresolved | confirmed | combat | unresolved | unresolved | unresolved | missing |
| 500 | Prospectre | unresolved | confirmed | quest-or-task, combat | unresolved | unresolved | unresolved | missing |
| 501 | Nothing but Hot Air | unresolved | confirmed | mount-taming | unresolved | unresolved | unresolved | missing |
| 502 | Verminbane | unresolved | confirmed | quest-or-task, combat | unresolved | unresolved | unresolved | missing |
| 503 | Monsterhunter | unresolved | confirmed | quest-or-task, combat | unresolved | unresolved | unresolved | missing |
| 504 | Taskmaster | unresolved | confirmed | quest-or-task, combat | unresolved | unresolved | unresolved | missing |
| 505 | Mainstreet Nightmare | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 506 | Falconer | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 507 | Steppe Elegance | unresolved | confirmed | mount-taming | unresolved | unresolved | unresolved | missing |
| 508 | Beyonder | partially-confirmed | confirmed | quest-or-task | static-award-candidate | unresolved | partially-confirmed | missing |
| 510 | Drama in Darama | unresolved | confirmed | quest-or-task | unresolved | unresolved | unresolved | missing |
| 511 | Malefitz | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 512 | Lionheart | unresolved | confirmed | quest-or-task | unresolved | unresolved | unresolved | missing |
| 513 | Soul Mender | unresolved | confirmed | combat | unresolved | unresolved | unresolved | missing |
| 514 | You Got Horse Power | partially-confirmed | confirmed | mount-taming | static-award-candidate | unresolved | partially-confirmed | missing |
| 515 | Unleash the Beast | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 516 | Well Roared, Lion! | unresolved | confirmed | mount-taming | unresolved | unresolved | unresolved | missing |
| 518 | Honorary Rascoohan | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 519 | Release the Kraken | partially-confirmed | confirmed | mount-taming | static-award-candidate | unresolved | partially-confirmed | missing |
| 521 | Pied Piper | unresolved | confirmed | quest-or-task, progress-threshold | unresolved | unresolved | unresolved | missing |
| 522 | Woodcarver | unresolved | confirmed | quest-or-task, combat | unresolved | unresolved | unresolved | missing |
| 523 | Bounacean Chivalry | unresolved | confirmed | combat, item-or-interaction | unresolved | unresolved | unresolved | missing |
| 524 | Knowledge Raider | unresolved | confirmed | quest-or-task, progress-threshold | unresolved | unresolved | unresolved | missing |
| 525 | Citizen of Issavi | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 526 | King's Council | conflicting | conflicting | other | unresolved | unresolved | conflicting | missing |
| 527 | Hot on the Trail | partially-confirmed | confirmed | mount-taming | static-award-candidate | unresolved | partially-confirmed | missing |
| 528 | Shell We Take a Ride | unresolved | confirmed | mount-taming | unresolved | unresolved | unresolved | missing |
| 529 | Phantastic! | unresolved | confirmed | mount-taming | unresolved | unresolved | unresolved | missing |
| 530 | Some Like It Hot | unresolved | confirmed | quest-or-task | unresolved | unresolved | unresolved | missing |
| 531 | First Achievement | unresolved | confirmed | quest-or-task | unresolved | unresolved | unresolved | missing |
| 532 | Sharp Dressed | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 533 | Engine Driver | unresolved | confirmed | mount-taming | unresolved | unresolved | unresolved | missing |
| 534 | Friendly Fire | unresolved | confirmed | quest-or-task | unresolved | unresolved | unresolved | missing |
| 535 | Wedding Planner | unresolved | confirmed | quest-or-task | unresolved | unresolved | unresolved | missing |
| 536 | Beaver Away | unresolved | confirmed | mount-taming | unresolved | unresolved | unresolved | missing |
| 537 | Snake Pit | unresolved | confirmed | quest-or-task, exploration | unresolved | unresolved | unresolved | missing |
| 538 | Royalty of Hazard | unresolved | confirmed | combat | unresolved | unresolved | unresolved | missing |
| 539 | Measuring the World | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 540 | Ripp-Ripp Hooray! | partially-confirmed | confirmed | mount-taming | static-award-candidate | unresolved | partially-confirmed | missing |
| 541 | Warrior of the Iks | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 542 | Mutagenius | unresolved | confirmed | quest-or-task | unresolved | unresolved | unresolved | missing |
| 543 | Strangest Thing | unresolved | confirmed | mount-taming | unresolved | unresolved | unresolved | missing |
| 544 | Fully Decayed | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 545 | Like Fox and Mouse | unresolved | confirmed | mount-taming | unresolved | unresolved | unresolved | missing |
| 546 | The Spirit of Purity | partially-confirmed | confirmed | mount-taming | static-award-candidate | unresolved | partially-confirmed | missing |
| 547 | Museum Goer | unresolved | confirmed | combat | unresolved | unresolved | unresolved | missing |
| 548 | Mystic Predator | unresolved | confirmed | mount-taming | unresolved | unresolved | unresolved | missing |
| 549 | The Rule of Raccool | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 550 | A Friend in Need | conflicting | missing | quest-or-task | unresolved | unresolved | conflicting | missing |
| 551 | Holzkopf | conflicting | missing | item-or-interaction | unresolved | unresolved | conflicting | missing |
| 552 | I Wanna Fly Away | unresolved | confirmed | quest-or-task, item-or-interaction | unresolved | unresolved | unresolved | missing |
| 553 | The Rootwalker | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 554 | Soul Crusher | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 555 | Inner Peace | conflicting | conflicting | item-or-interaction | unresolved | unresolved | conflicting | missing |
| 556 | Fiend Rider | conflicting | conflicting | item-or-interaction, mount-taming | unresolved | unresolved | conflicting | missing |
| 557 | Fiend Slayer | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 558 | Tear the Toxic Veil | unresolved | confirmed | quest-or-task | unresolved | unresolved | unresolved | missing |
| 559 | Hope of the Merudri | conflicting | conflicting | quest-or-task | unresolved | unresolved | conflicting | missing |
| 560 | Umbral Redeemer | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 561 | Hell Rider | unresolved | confirmed | unresolved | unresolved | unresolved | unresolved | missing |
| 562 | Alpha Rider | conflicting | conflicting | item-or-interaction, mount-taming | unresolved | unresolved | conflicting | missing |
| 564 | The First of Many | partially-confirmed | confirmed | other | unresolved | partially-confirmed | partially-confirmed | unit-covered |
| 565 | A Well-Honed Arsenal | partially-confirmed | confirmed | other | unresolved | partially-confirmed | partially-confirmed | unit-covered |
| 566 | Arsenal of War | partially-confirmed | confirmed | other | unresolved | partially-confirmed | partially-confirmed | unit-covered |
| 567 | The Forbidden Build | partially-confirmed | confirmed | other | unresolved | partially-confirmed | partially-confirmed | unit-covered |
| 568 | Bat Person | unresolved | confirmed | quest-or-task | unresolved | unresolved | unresolved | missing |
| 569 | Illuminator | unresolved | confirmed | other | unresolved | unresolved | unresolved | missing |
| 570 | Power of Words | unresolved | confirmed | quest-or-task | unresolved | unresolved | unresolved | missing |
| 572 | Errand Runner | conflicting | missing | quest-or-task, combat | unresolved | unresolved | conflicting | missing |
| 573 | Workhorse | conflicting | missing | quest-or-task, combat | unresolved | unresolved | conflicting | missing |
| 574 | Taskaholic | conflicting | missing | unresolved | unresolved | unresolved | conflicting | missing |
| 575 | Pest Control | conflicting | missing | quest-or-task | unresolved | unresolved | conflicting | missing |
| 576 | Mimic | conflicting | missing | progress-threshold | unresolved | unresolved | conflicting | missing |
| 577 | Bastard | conflicting | missing | quest-or-task | unresolved | unresolved | conflicting | missing |
| 578 | Razor's Edge | conflicting | missing | combat | unresolved | unresolved | conflicting | missing |
| 579 | Lost Letters | conflicting | missing | other | unresolved | unresolved | conflicting | missing |
| 580 | Stagmeister | conflicting | missing | item-or-interaction | unresolved | unresolved | conflicting | missing |
| 581 | Feral Trapper | conflicting | missing | quest-or-task | unresolved | unresolved | conflicting | missing |
| 582 | Castle Crasher | conflicting | missing | other | unresolved | unresolved | conflicting | missing |
| 585 | A reliable Friend | conflicting | missing | mount-taming | unresolved | unresolved | conflicting | missing |
| 586 | Echo Initiate | conflicting | missing | item-or-interaction, event-or-raid | unresolved | unresolved | conflicting | missing |
| 587 | Echo Hunter | conflicting | missing | unresolved | unresolved | unresolved | conflicting | missing |
| 588 | Echo Walker | conflicting | missing | unresolved | unresolved | unresolved | conflicting | missing |
| 591 | Purrfectly Addicted | conflicting | missing | item-or-interaction, progress-threshold | unresolved | unresolved | conflicting | missing |
| 592 | Six Steps Ahead | conflicting | missing | mount-taming | unresolved | unresolved | conflicting | missing |
| 593 | Radiant Nimbus | conflicting | missing | mount-taming | unresolved | unresolved | conflicting | missing |
| 594 | Amati's Echo | conflicting | missing | quest-or-task | unresolved | unresolved | conflicting | missing |
| 595 | Enlightened, Indeed | conflicting | missing | unresolved | unresolved | unresolved | conflicting | missing |

## Findings

- **info / registry-zero-point-exception** — ID 406 (The More the Merrier) has grade 0 and zero points.
- **info / registry-zero-point-exception** — ID 526 (King's Council) has grade 1 and zero points.
- **info / registry-sparse-id-space** — Registry has 28 ID gaps.
- **warning / reference-baseline-mismatch** — Registry does not fully match the recorded external baseline.
- **warning / reference-definition-missing** — Reference ID 195 (Smart Thinking) is absent from the Canary registry.
- **warning / reference-definition-conflict** — Reference ID 526 (King's Council) conflicts with Canary metadata.
- **warning / reference-definition-missing** — Reference ID 550 (A Friend in Need) is absent from the Canary registry.
- **warning / reference-definition-missing** — Reference ID 551 (Holzkopf) is absent from the Canary registry.
- **warning / reference-definition-conflict** — Reference ID 555 (Inner Peace) conflicts with Canary metadata.
- **warning / reference-definition-conflict** — Reference ID 556 (Fiend Rider) conflicts with Canary metadata.
- **warning / reference-definition-conflict** — Reference ID 559 (Hope of the Merudri) conflicts with Canary metadata.
- **warning / reference-definition-conflict** — Reference ID 562 (Alpha Rider) conflicts with Canary metadata.
- **warning / reference-definition-missing** — Reference ID 572 (Errand Runner) is absent from the Canary registry.
- **warning / reference-definition-missing** — Reference ID 573 (Workhorse) is absent from the Canary registry.
- **warning / reference-definition-missing** — Reference ID 574 (Taskaholic) is absent from the Canary registry.
- **warning / reference-definition-missing** — Reference ID 575 (Pest Control) is absent from the Canary registry.
- **warning / reference-definition-missing** — Reference ID 576 (Mimic) is absent from the Canary registry.
- **warning / reference-definition-missing** — Reference ID 577 (Bastard) is absent from the Canary registry.
- **warning / reference-definition-missing** — Reference ID 578 (Razor's Edge) is absent from the Canary registry.
- **warning / reference-definition-missing** — Reference ID 579 (Lost Letters) is absent from the Canary registry.
- **warning / reference-definition-missing** — Reference ID 580 (Stagmeister) is absent from the Canary registry.
- **warning / reference-definition-missing** — Reference ID 581 (Feral Trapper) is absent from the Canary registry.
- **warning / reference-definition-missing** — Reference ID 582 (Castle Crasher) is absent from the Canary registry.
- **warning / reference-definition-missing** — Reference ID 585 (A reliable Friend) is absent from the Canary registry.
- **warning / reference-definition-missing** — Reference ID 586 (Echo Initiate) is absent from the Canary registry.
- **warning / reference-definition-missing** — Reference ID 587 (Echo Hunter) is absent from the Canary registry.
- **warning / reference-definition-missing** — Reference ID 588 (Echo Walker) is absent from the Canary registry.
- **warning / reference-definition-missing** — Reference ID 591 (Purrfectly Addicted) is absent from the Canary registry.
- **warning / reference-definition-missing** — Reference ID 592 (Six Steps Ahead) is absent from the Canary registry.
- **warning / reference-definition-missing** — Reference ID 593 (Radiant Nimbus) is absent from the Canary registry.
- **warning / reference-definition-missing** — Reference ID 594 (Amati's Echo) is absent from the Canary registry.
- **warning / reference-definition-missing** — Reference ID 595 (Enlightened, Indeed) is absent from the Canary registry.

## Trigger coverage

- direct-static-award: 89
- no-direct-static-reference: 420
- referenced-without-static-award: 1
- static-progress-path: 32

## Evidence boundary

A reference condition, registry definition and static API call are separate evidence layers. A missing direct static call is not proof that an achievement is unobtainable. Dynamic tables, wrappers, quest state machines, engine-side paths, persistence/backfill and real runtime reachability remain unresolved until separately proven.
