# Side operations

Decided 17 Oct 2026, built 18 Oct 2026: side operations go into the existing
campaigns as **in-theatre optional missions**, on four themes: smugglers and
arms runners, privately escorted armed merchants, air defence, and major
assault and defence operations. Some are chained to each other and to the
core missions; others stand alone. Each puts collection mods to work that no
SEST mission used before.

Every operation below is built: a campaign mission spec, through the same
builder and gates as the core missions (`build_pack.py`). None has been
flown in the game.

## How they work

- **Optional, in theatre, on the calendar.** Each hangs off its campaign's
  chain (`group="optional"`, `expires_after`): skip it and the campaign plays
  unchanged; fly it and something specific is better later, or it pays its
  points and stands alone.
- **Who flies them.** Where the player's own ships could be there, they are
  (a detachment, as Southern Watch's O1, O3 and O4 already do). Where the
  story is somebody else's (a Philippine Navy patrol group, a Japanese strike,
  a US bomber package), the mission brings its own fixed force and nothing
  the player owns sails. In Sulu Line that matters most: there is no free
  rearm, so a side operation flown by the player's ships would spend
  magazines the campaign never gives back.
- **Links are campaign variables.** An optional writes a variable when it is
  won; a later mission reads it (`reveal_if`, or `spawn_if` to keep a threat
  away). That is the only thing the game carries between missions, and only
  inside one campaign's save.
- **Geography.** The proven-position pool (spots some loading mission once
  put a ship on) is thin south of Jolo and round Tanimbar, so the side
  operations are proved against the coastline instead, as Southern Reach
  is: two new Natural Earth extracts, `geo/sulu_theatre_coast.json` (116-127E,
  3-12N) and `geo/banda_theatre_coast.json` (118-142E, 15S-2N), cut with
  `tools/make_coast_extract.py`. A mission opts in with `geography="coast"`
  and is proved on the extract whose box holds its centre.

## Sulu Line: the Night Market thread (smugglers and arms runners)

The drug money is what buys Meridian's guns. Three optionals, two of them
chained, and two core missions that read them. All three are flown by the
Navy's Tawi-Tawi patrol group or the Air Force, not the player's task group.

| ID · date | Operation | Task | Forces and mods put to work | Link |
|---|---|---|---|---|
| SL01A · 15 Oct | **Night Market** | Night, flat calm, north of Tawi-Tawi: find a semi-submersible running for the coast among six fishing boats, with a chartered civilian helicopter as the runners' eye, and stop her before she reaches the pickup boats. | BRP Emilio Jacinto and two Jose Andrada patrol boats (Luzon Line, first use), a Navy H-76 out of Sanga-Sanga. Red Storm Arsenal's semi-submersible and speedboats; **civilian AS350** (first use) under the Pirates flag. | writes `SLNarcoTaken` |
| SL03A · 29 Oct | **The Okean** | The Sibutu Passage at night: an armed Meridian trawler among two real Okean-class trawlers, coming north to hand arms to fast boats. Her hidden torpedo tube goes live when she reaches them. | BRP Apolinario Mabini, BRP Florencio Inigo, a Navy H-76. **Project 2498's `civ_fv_okean_surprise`** (first use) beside two vanilla `civ_fv_okean`; **Iranian Navy Bell 212** (first use) as Meridian's shuttle. | reads `SLNarcoTaken` (her name is in the semi-submersible's navigation set: she starts classified); writes `SLOkeanTaken` |
| SL05 · 9 Nov (core) | Celebes Gate | As built. | As built. | reads `SLOkeanTaken`: the spotter drone does not come |
| SL05A · 12 Nov | **The Drone Yard** | Two FA-50s against a Meridian drone yard on Mapun, before its spotter drone finds a Navy charter fifty miles away. | Tabak 11 and 12, BRP Artemio Ricarte and the charter. **Shahed 238 launchers** (first use), a Shahed-136 rail, two guns, a Forpost spotter. | writes `SLYardStruck` |
| SL06 · 16 Nov (core) | The Aborlan Battery | As built. | As built. | reads `SLYardStruck`: if the yard was never struck, a Shahed-136 rail from Mapun joins the battery |

## Southern Watch

Six more optionals beside O1-O4 and the two contingencies. Paper Trail is
the bible's O02 and Viper Zero its O09, built at last; the others are new.
Only The Second Convoy sails the player's own ships (a detachment, the day
after Weapons Free); the rest are somebody else's operation and bring their
own fixed force, as Southern Cross does.

### Escorted hulls (arms runners and privately escorted armed merchants; chained)

| ID · date | Operation | Task | Forces and mods put to work | Link |
|---|---|---|---|---|
| O5 · 21 Oct | **Paper Trail** | North of Tanimbar, a week before anyone may shoot: shadow a Meridian-escorted merchant to her handover and identify the receiver among three waiting ships, with two uncrewed boats doing the close work and the patrol ship kept out of the escort's sight (an `unseen` objective). | HMAS Eyre; **Anduril K5 KRAKEN** under the RAN flag and a **Saronic Corsair Scout** lent by the US Navy (both first use). A Peykaap escort, a Meridian-chartered coaster. | writes `O5ReceiverNamed` |
| SW04 · 30 Oct (core) | The Quiet Passenger | As built. | As built. | reads `O5ReceiverNamed`: the passenger starts as a fifteen-minute datum (the bible's "likely patrol lane"), beside O2's datum on the submarine. From 18 to 20 Oct 2026 the builder dropped this read (O2's replaced it); the test card's 6.6a checks both |
| O6 · 3 Nov | **The Second Convoy** | The day after Weapons Free, between Tanimbar and Kai: stop two cargo ships running dark for Biak before they reach the Banda Sea, past an armed merchant, two boats, a radar decoy that radiates like a frigate and a trawler with a hidden torpedo tube. | The player's detachment and Seahawk. The armed `wp_ms_andizhan_armed` (first use), the radar decoy `wp_ms_mercur_decoy`, Peykaaps, Project 2498's armed Okean. | reads `O5ReceiverNamed`: both cargo ships start classified |

### Major assault (chained)

| ID · date | Operation | Task | Forces and mods put to work | Link |
|---|---|---|---|---|
| O7 · 14 Nov | **Second Ring** | The night after The Open Door, Russia has rebuilt the belt round the Biak field. Destroy its two engagement radars from two hundred miles out. | Two B-52H with ARRW, RAAF Growlers with AGM-88G, two F-15EX, a Wedgetail. **S-350 Vityaz**, **S-300PMU2**, **Buk-M3**, **Nebo-U**, **Iskander-M** (all first use), two J-16. | writes `O7RingDown` |
| O9 · 17 Nov | **Viper Zero** | Four F-2A with ASM-3 and an EC-2 jammer stop a PLAN group (054A, 056A, Type 071) closing on JS Hyuga as she comes south for Common Sea. | **JS Hyuga** (first use), JS Asahi, an SH-60K; **EC-2 stand-off jammer** (first use). | writes `O9GroupStruck` |
| SW10 · 20 Nov (core) | Common Sea | As built. | As built. | reads `O9GroupStruck`: the frigate from the east starts classified (Common Sea already flies the F-2A option the bible promised) |

### Air defence

| ID · date | Operation | Task | Forces and mods put to work | Link |
|---|---|---|---|---|
| O8 · 15 Nov | **Bomber Stream** | Four H-6K with YJ-12 and two J-16 for the ships forming at Darwin: shoot down three bombers before any is inside two hundred miles, with a Darwin-Denpasar airliner crossing the intercept. | Four RAAF F-35A with AIM-260, two F-22, a Wedgetail, an RAAF KC-30A (the French Air Force mod's, first use in a campaign). | stand-alone |
| O10 · 21 Nov | **Ballistic Shield** | Hold the Langgur strip in the Kai Islands against the enclave's ballistic missiles while two F-15EX with ARRW and a Triton hunt the five launchers on Biak. | **THAAD**, Patriot PAC-3, the **Steelfin** battery (first use); **Fattah-1**, **Fattah-2**, **Emad** (all first use), a Shahed 238 battery, a Tu-214R spotter. | reads `O7RingDown`: if Second Ring was won, the S-350 over the pads is not there |

## Red Line

Built 20 Oct 2026, the plan's step RL-1 (`campaign-upgrade-plan.md`
section 4.2), on days neither coalition campaign flies. Two optionals are
the enclave field's own aircraft, a fixed force as Southern Watch's are;
the contingency sails a detachment of the player's screen, with no
purchase, repair or rearm. Each fires on nothing: the restraint is the
task. The spine went from 10 entries to 17, so a Red Line campaign under
way must be started again. Bible: `docs/campaigns/red-line/campaign-bible.md`;
test card section 8B.

| ID · date | Operation | Task | Forces and mods put to work | Link |
|---|---|---|---|---|
| RLO1 · 11 Nov | **Datum** | North of Biak, the morning after the Russian auxiliary was torpedoed: put a class on the boat nobody has claimed (GOLF) with sonobuoys, at weapons Hold, under a RAAF Poseidon that is recording. | *Sea Ear 31*, the enclave detachment's Y-9, and the enclave field. GOLF is `usn_ssn_virginia_2027` Variant10, spared (she is needed in RL02 and RL04). | writes `RLO1GolfDatum` |
| RL02 · 12 Nov (core) | Routes They Can See | As built. | As built. | reads `RLO1GolfDatum`: GOLF on the plot for fifteen minutes with no class, Southern Watch's O2 -> SW04 shape; classifying her is still the mission's own task |
| RLO2 · 18 Nov | **The Ships from the North** | The Ceram Sea: name the two Japanese escorts coming south for the Kai convoy, JS Mogami and JS Maya, and bring the Y-9 home, with a JASDF F-2A pair up from Langgur at weapons Tight. | The Y-9 and two J-15s released to the enclave field. The F-2A (`jp_f-2a_late`, the Viper Zero mod) on the red side for the first time; Mogami and Maya on the hulls RL03 and Common Sea place, spared. | writes nothing for now: `RLO2EscortsNamed` is held (owner, 21 Oct 2026) until test card 7.4 is answered; the names go to headquarters and the operation pays its own points |
| RL03 · 19 Nov (core) | The Other Picture | As built. | As built. | reads nothing. Until 21 Oct 2026 it read `RLO2EscortsNamed` and revealed both escorts at Classify for the whole mission; that this counts for its classify stage is unproven, so the reveal is held until test card 7.4 is answered (restorable from `9035f291`) |
| RLC1 · 24 Nov | **Pilot in the Water** | The Banda Sea, the morning after *Fujian's Shadow*: a J-15 off Liaoning is down with a fire warning, and an Australian patrol vessel is racing the screen to the pilot. Stop the lead ship within three cables of his raft for four minutes, before she is within a mile of him. | A detachment of the screen and its flight. The stock one-man raft `all_life_raft_single` (first SEST use) on the player's side; `ran_opv_arafura` Variant4 (Gippsland), the Arafura hull no mission places and no roster sells; a RAAF P-8A. Both spared. | stand-alone |


Seventeen mods no SEST mission used before: civilian AS350, Project 2498
Zyetseth, Iran Bell-212, Shahed 238, Anduril Maritime Drones, Saronic
Corsair ASV, S-350 Vityaz, S-300PMU2, Buk-M3, Nebo-U, Iskander-M, EC-2,
JMSDF Hyuga class, Fattah-1, Fattah-2, Emad and Steelfin. All seventeen were
on the coverage excuse list and are off it. Units placed for the first time
from mods already in use: the Luzon Line's Jacinto and Andrada patrol craft,
the armed Andizhan and the RAAF KC-30A.

Royal Australian Defence Forces is now reached too, through the Jacinto's
Perth_parts material folder, and its excuse is retired. Each campaign's
reference list (`required-mods-urls.txt`) gains the mods its side operations
place; the pack's Required Items already hold them all.

## Left out

- **Project 2498 Zyetseth** itself (the assault freighter) has spaces in its
  unit id, which a campaign file cannot name. Its sister file, the Okean
  trawler with the hidden tube, is what the slate uses.

## Not yet confirmed in the game

The builder proves positions, reach, the fair opening, prices and
variables. It cannot prove behaviour:

- that a Shahed 238 launcher fires on a ship another red unit is tracking
  (The Drone Yard);
- that the Okean's mid-route weapons order turns her torpedo tube on
  (`SetWeaponStatus` at a waypoint, the stock order);
- that a semi-submersible at periscope depth is as hard to find at night as
  the brief says;
- that the Pirates flag shows on an aircraft;
- that the Fattah, Emad and Shahed 238 launchers fire on land targets from a
  track the Tu-214R gives them, and that THAAD, Patriot and Steelfin engage
  what they fire (Ballistic Shield);
- that the EC-2's jammer degrades the 054A's radars (Viper Zero);
- that the Meridian escort classifying HMAS Eyre is what fails Paper Trail's
  `unseen` objective, as stock's Polar Fury trigger does for a submarine;
- that a reveal at Classify counts for a `UnitClassified` objective on the
  same unit. Red Line's RLO2 -> RL03 had it on RL03's main stage and is held
  (21 Oct 2026) until it is shown; Southern Reach's TS01 -> TS03 and Sulu
  Line's SL01A -> SL03A keep it on optional objectives and are the proof
  (Southern Reach card 3.10, Sulu Line card 7.1);
- what a held stage does when the ship leaves before its minutes and comes
  back after them (Pilot in the Water), and whether a J-15 pair at Tight
  opens on identified F-2As (The Ships from the North).
