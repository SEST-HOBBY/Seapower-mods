# SEST SOUTHERN REACH
## Tasman Shield — campaign lore, design and build brief

**Design version:** 1.0 · **Written:** 24 September 2026 · **Fictional campaign:** 6 December 2028 – 2 March 2029 (87 days, two chapters)

**Game:** Sea Power: Naval Combat in the Missile Age, using the SEST mod collection. **Predecessor:** *SEST Southern Watch — The Northern Lifeline* (18 October – 28 November 2028), whose task group, characters and civilian hulls this campaign inherits.

**Premise:** the coercion network the north just fought moves south with the summer. Chapter A, *Southern Reach*, escorts the Antarctic resupply season through the Southern Ocean — sparse contacts, long transits, weather that sets the force you have, and a trawler that has to be told from a spy ship at forty miles. Chapter B, *Tasman Shield*, brings the same worn force home to defend the approaches Australia and New Zealand share — Fiordland, Cook Strait, the Tasman, Bass Strait and the Bight — among ferries, tankers, rigs and cable routes. One native Task Force save carries the force from the first mission to the last.

This is a design and build brief for a campaign that has been **statically built and never played**. Every character, company, incident and deployment is fiction. Equipment behaviour is whatever the winning mod file says, not the real system.

---

## 1. What the corrected build specification fixed, and how this design honours it

The Gemini draft this campaign grew from was reviewed against the repository before a line of it was built. The corrections that bind every mission card below:

| Rule | How it is applied |
|---|---|
| One continuous campaign, two chapters | One `campaign.ini`, 23 core missions plus a two-way optional branch; two mission-browser folders (*Southern Reach*, *Tasman Shield*) for mission-by-mission play |
| Native Task Force Mode, not a points calculator | `player_task_force_roster.ini`, per-mission allowlists, explicit `TaskForceModeRearm` / `TaskForceModeRepair` / `TaskForceModeEnableTaskForceBuilder` on every entry, emitted by the builder for every mission |
| `Includes*` and threat-profile fields are display only | Deployment is by `Generated` placement on an anchor, `Replaced` where a detachment is restricted, blank generation for the three detached submarine operations, and Air Tasking rows paired with cockpit slots |
| `Generated` vs `Replaced` | `Generated` for the 21 missions that sail the owned force; blank for the detached submarine and air operations (the stock pattern, Pacific Strike 03A/07A/08A: an authored boat, `IncludesSubmarine=True`, no builder). No mission uses `TaskForceModeMaxUnits` |
| Air Tasking is not automatic | Every row is one of the six roles `ui.ini` localises; every row has a slot-tagged cockpit; every purchasable aircraft that matches a row has a compatible field within its own sortie radius, checked by the builder |
| Airbase Preparation needs a real blue airfield | Enabled on TS07 only, where RAAF Base Williamtown is a placed player land unit |
| `JoinTaskForce` is not a persistence flag | No unit carries it. Allied and allocated aircraft fly the mission they are placed in |
| No `UnitsAreOutOfAmmo` objective | The one native-attested use (`03 Lifeline`) is left to Southern Watch's magazine objective; this campaign scores magazines through persistence and the rearm windows, never through a trigger |
| Replenishment is not scored | Every service is a *protected window*: the named hulls must be inside the service box when the window's clock runs, then withdraw (the `03 Lifeline` Trigger8 shape SW09 uses). No condition type counts what crossed. The crossing itself is real since 26 Sep 2026: HMAS Supply and Stalwart carry a working supply system (SEST Replenishment At Sea's table, shipped by SEST RAN Fleet), so a briefing may say that an escort alongside takes missiles and torpedoes back; no page says fuel crossed a hose |
| Submarine service | "Surfaced" is a house rule stated in the briefing; the engine has no depth predicate and none is claimed |
| No Antarctic environment mechanics | Ice, fog, the Convergence and radar ducting are briefing text, reduced aviation, shorter clocks and geometry. Nothing claims the engine models them |
| No shader or map work | The campaign is INI, XAML and PNG. The world's rendering of Storm Bay, Macquarie Island, Cook Strait and the ice edge is the play test's to confirm (§9) |
| No civilian traffic generator | Every neutral is an actual enabled hull with an authored route, origin and destination |
| Real platforms are not game mechanics | Ranges, reach and decks are read from the winning files by the builder; the tables in §5 were produced by it |
| Availability ≠ existence in 2028 | Hunter, C-17A, C-130J-30, S-100, a bespoke Nuyina and HMNZS Aotearoa are story references or disclosed stand-ins, never mission-critical |

---

## 2. Lore: the summer that followed the ceasefire

### The world on 6 December 2028

The northern ceasefire is nine days old. The Meridian Maritime Group's board has been replaced, its escort subsidiary is under three investigations, and the task group that held the corridor is alongside at Sydney with its dents. The talks in the north are about port access and inspections; nobody in them is talking about Antarctica.

Antarctica talks about itself. Every December the Australian Antarctic Division sails the summer season out of Hobart — people, fuel, food and a year's spares for Casey, Davis and Mawson, with the Macquarie Island station on the way — and every December the traffic is the same: a research and resupply ship, a chartered cargo hull, a fuel coaster, the expedition cruise ships, the toothfish longliners working the Convergence, and the airlink to Wilkins Aerodrome. It runs on a calendar the ice keeps.

This year a fleet arrived in October. **The Southern Ocean Fisheries and Research Protection Group** — a frigate, two corvettes, a research trawler with more antennas than nets and, in the new year, a carrier — deployed "to protect national fishing and scientific interests under the Convention" and has been asking merchant masters for their environmental-compliance paperwork sixty miles south of Tasmania. Alongside it, **Austral Meridian Services (AMS)**, a fisheries-compliance and marine-services contractor registered in the same building as the old Meridian escort subsidiary, is offering "escorted compliance corridors" to the Antarctic trade. Same network, new name, and the pretext changed from safety to conservation.

A small **Russian Pacific Fleet research-support detachment** — a research vessel that is a submarine tender, an intelligence trawler, a nuclear boat or two, and very long-range aircraft that arrive over the Southern Ocean with a tanker behind them — supports the effort under its own arrangement, as its predecessor supported the enclave in the north.

None of it is a war. All of it is the same pressure the north just fought, applied where Australia and New Zealand are thinnest: three thousand miles of ocean, one escort force, and traffic that cannot be told to stay home because the ice does not wait.

### Chapter A — Southern Reach (6 December 2028 – 14 January 2029)

The season opens with a convoy out of Storm Bay and a trawler that is not one (SR01). Collins puts a name on a nuclear boat working the Macquarie Ridge (SR02). The Wilkins airlink goes missing on the southern route and the search finds its crew aboard a foreign trawler that "recovered" them (SR03). The Macquarie Island resupply holds a service window with a Russian boat closing (SR04). A Triton and a Poseidon classify the protection group's command element in an empty ocean (SR05). A torpedo hits the fuel coaster south of the Auckland Islands — the first overt attack in the south (SR06) — and on Christmas Eve the task group is authorised to sink the boat that fired (SR07). The Christchurch gateway is held while a corvette tries to inspect a tanker (SR08). The January voyage south is fought through as a convoy action under the group's carrier air (SR09). At the ice edge the task group identifies the group's flagship and holds fire until fired on (SR10). The last ship south is escorted with a force that has spent most of what it sailed with (SR11). The group turns north into the Tasman, and the task group shadows it and names every hull in the network (SR12).

### Chapter B — Tasman Shield (22 January – 2 March 2029)

The group is now between two countries' home ports, and its aim is the same as the north's was: make the approaches unusable long enough to force a "joint compliance" settlement. Fiordland's tourist traffic hides a tender (TS01). A submarine sits on the Cook Strait cable route among the ferries (TS02). Two air forces find the tender and the boat rendezvousing east of New Zealand (TS03). Dispersed merchant groups cross the Tasman under carrier air (TS04). Farncomb fights the group's nuclear boat under the Sydney–Auckland cable corridor (TS05). Bass Strait's rigs, ferries and tankers have to be told from a decoy and a diesel boat (TS06). The relief detachment's aircraft are covered across the air bridge with Williamtown's fighters (TS07). The Bight is searched for the Russian detachment's last boat and its oiler (TS08). The southern convoy is fought through the carrier group's last full-strength strike (TS09). The player chooses which country's approaches to hold — Auckland's (TS10A) or Adelaide's (TS10B) — and the other's consequence follows them into the western Tasman (TS11). The last movement crosses the Tasman with what is left (TS12).

### The ending

The best ending is a supplied Antarctic winter, a working trans-Tasman route, two navies still able to sail, and a group that went home with fewer ships than it brought. A costly ending supplies the stations and reopens the route with a task group that cannot hold it again. A poor ending saves the force and loses the approaches. Civilian losses end the story politically whatever the ledger says.

### Recurring people and organisations (all fictional)

| Person or group | Role | Voice in the campaign |
|---|---|---|
| Captain Morgan Reid, RAN — the player | Task group commander, promoted after the north | Not a voice: the decisions are the character |
| Commodore Alex Mercer | Maritime Border Command; flies his flag ashore at Hobart, then Sydney | Every core briefing's FROM line; short, exact, allergic to a dead trawler |
| Wing Commander Daniel Ward | Air component, now at RAAF Base Edinburgh | Memos on what a sortie costs at 55 South |
| Master Leila Santos, MV Coral Pioneer | Chartered for the Macquarie run, then the Tasman relief | Deck-log extracts; she still will not heave to |
| Squadron Leader Tane Rewi, No. 5 Squadron RNZAF | New Zealand's Poseidons, out of Ohakea | Cables; the NZ contribution with a name and its own rules |
| Commander Tessa Brand, RNZN | NZ maritime liaison, HQ Joint Forces NZ | Says where the RNZN's ships are (Te Kaha in refit at Devonport, Te Mana on the Pacific station) so nobody has to invent them |
| Dr Helen Marsh, Australian Antarctic Division | Voyage leader aboard RSV Southern Endeavour | A civilian who has to be told what an escort can and cannot promise |
| AMS duty controller | The old Meridian net, moved south | Intercepts |
| The group commander | Professional, constrained, with a carrier he cannot lose | One intercepted signal, before TS11 |

### Organisations and hulls

- **RSV Southern Endeavour** — the research and resupply ship. Represented by a modern freighter (`civ_ms_freighter_d`); her name says "stand-in" in every mission she sails, because no icebreaker exists in the collection.
- **MV Coral Pioneer** (`civ_ms_mairangi_bay`) — Santos's ship, back from the north.
- **MT Derwent Spirit** (`civ_ms_sealift_pacific`) — the fuel coaster; torpedoed in SR06 and repaired at Bluff.
- **The protection group** — Type 054A frigates, Type 056A corvettes, the research trawler *Nan Hai 27* (an Okean-class collector among Okean-class trawlers), the carrier *Liaoning* from SR09, a Type 052D flagship in the fleet actions, Type 093B *ROMEO* under the Tasman.
- **The Russian detachment** — RV *Akademik Fersman* (a merchant hull, a tender), the Akula *VICTOR*, the Yasen *SIERRA-TWO*, and Bear-F / Bear-D flights with a Midas behind them.
- **AMS** — chartered coasters, a radar-decoy merchant, an armed merchant in Bass Strait.

---

## 3. Theatre and force rules

| Area | Narrative function | Build treatment |
|---|---|---|
| Storm Bay and the Derwent | The season's front door | Coastal geometry proved against the coastline extract; Hobart Airport as the airlink's field and, when the RAAF detaches there, the Poseidon's |
| Macquarie Ridge and the sub-Antarctic islands | The submarine highway south of New Zealand | Open-water submarine missions; the Auckland and Campbell Islands as coastline the routes go round |
| Macquarie Island | A station with an anchorage and no runway | Buckles Bay anchorage as a coastal station; the service window |
| The Southern Ocean and the ice edge | Isolation, long transits, sparse contacts | Open water by hundreds of miles; reduced aviation and shorter clocks the further south the mission sits; the southernmost centre is 60 South, 375 NM from the nearest Natural Earth coastline |
| Christchurch and Banks Peninsula | New Zealand's Antarctic gateway | RNZAF Poseidon, Christchurch as a field, US Antarctic Program traffic as neutral |
| Fiordland, Cook Strait, the Chathams | The homeland approaches, New Zealand side | Dense routed neutrals; Cook Strait inside 12 NM of coast on every side; the Chatham mission stays west of 180° |
| The Tasman | The crossing | Mid-ocean, carrier air, cable corridors as abstract boxes |
| Bass Strait, the Bight, Gulf St Vincent | The homeland approaches, Australian side | Rigs as unarmed neutral land units in water, ferries and tankers on routes, Edinburgh and East Sale as fields |

**Opening allocation (a design assumption, not a free fleet):** the player's task group requisitions from 1,000 points; RSV Southern Endeavour, Coral Pioneer, Derwent Spirit, HMAS Supply / Stalwart, HMAS Collins / Farncomb, the RNZAF Poseidon and every allied aircraft are allocated theatre assets that appear where the story puts them and never join the owned roster.

**Ownership states.** Every unit in every mission is one of: *owned persistent force* (bought, generated on the anchor), *allocated theatre support* (authored, named, never sold), or *civilian/partner objective* (blue merchants the mission protects, or neutrals the ROE protects).

**Opposition.** The bible's Southern Watch rule holds: a modern escort is dangerous because of the encounter, not because of a thousand-mile hypersonic. The Type 052D (reach 1,050 NM in the winning file) appears only in the two fleet actions (TS09 and TS11), screened by the carrier, where the player's Hobart is expected. Type 054A / 056A (85 NM) are the everyday escorts. Russian hulls with Kalibr are used as submarines (VICTOR, SIERRA-TWO) whose reach is a ceiling the builder treats as a ceiling; the surface escort in the Bight is the vanilla Udaloy (27 NM), on purpose.

---

## 4. The calendar and the economy

### Dates, points and service windows

| Code | Date | Mission | Points | Builder / repair / rearm | Air Tasking rows | Generation |
|---|---|---|---:|---|---|---|
| SR01 | 6 Dec 2028 | Southern Departure | 100 | buy (Anzac, Hobart, MH-60R) · repair · rearm | HeloRecon | Generated |
| SR02 | 9 Dec | Silent Track | 80 | none — detached submarine op | — | blank |
| SR03 | 12 Dec | Search Datum | 100 | buy (+P-8, Triton) · repair · rearm | HeloRecon, Recon | Generated |
| SR04 | 15 Dec | Macquarie Passage | 140 | buy (+Wedgetail) · repair · rearm | HeloRecon, Recon | Generated |
| SR05 | 18 Dec | Empty Horizon | 100 | none — allocated air op | — | blank |
| SR06 | 21 Dec | Broken Supply Line | 120 | rearm only if SR04's window held | HeloRecon, Recon | Generated |
| SR07 | 24 Dec | Beneath the South | 140 | buy · repair · rearm (Bluff) | HeloRecon, Recon | Generated |
| SR08 | 28 Dec | The Gateway | 120 | buy · repair · rearm (Lyttelton) | HeloRecon, Recon | Generated |
| SR09 | 2 Jan 2029 | Cold Route | 160 | buy · repair · rearm (Hobart) | HeloRecon, Recon | Generated |
| SR10 | 6 Jan | Southern Line | 140 | none | HeloRecon | Generated |
| SR11 | 10 Jan | Last Ship South | 160 | rearm only if Cold Route was held | HeloRecon | Generated |
| SR12 | 14 Jan | Turning North | 120 | buy (+F-35A) · repair · rearm (Hobart) | HeloRecon, Recon, CAP | Generated |
| TS01 | 22 Jan | Home Waters | 100 | buy (+Arafura) · repair · rearm (Sydney) | HeloRecon, Recon | Generated |
| TS02 | 25 Jan | Cook Strait | 120 | none; detachment | HeloRecon, Recon | Generated |
| TS03 | 28 Jan | Chatham Watch | 100 | none | HeloRecon, Recon | Generated |
| TS04 | 1 Feb | Tasman Crossing | 140 | buy (+F/A-18F, EA-18G) · repair · rearm | HeloRecon, Recon, CAP | Generated |
| TS05 | 4 Feb | Under the Tasman | 100 | none — detached submarine op | — | blank |
| TS06 | 8 Feb | Bass Strait | 140 | buy · repair · rearm (Melbourne) | HeloRecon, Recon, CAP | Generated |
| TS07 | 11 Feb | Southern Air Bridge | 140 | buy · repair · rearm (Sydney) · airbase prep | Recon, CAP | Generated |
| TS08 | 15 Feb | Great Australian Bight | 120 | repair only | HeloRecon, Recon | Generated |
| TS09 | 19 Feb | The Southern Convoy | 180 | buy · repair · rearm (Adelaide) | HeloRecon, Recon, CAP, Attack | Generated |
| TS10A | 22 Feb | Northern Priority (optional) | 60 | none; detachment | HeloRecon, Recon | Generated |
| TS10B | 22 Feb | Southern Priority (optional) | 60 | none; detachment | HeloRecon, Recon | Generated |
| TS11 | 26 Feb | Approaches | 180 | buy · repair · rearm (Sydney) | HeloRecon, Recon, CAP, Attack | Generated |
| TS12 | 2 Mar | Southern Cross | 0 | buy (aircraft, Anzac, Arafura) · repair | HeloRecon, Recon, CAP | Generated |

Mainline allocations total 2,800 points across 23 missions; the two optionals add 120. Opening budgets: Supported 1,250 / Standard 1,000 / Veteran 850, repair multipliers 0.75 / 1 / 1.25, point cap 1,500 (1,250 Veteran). Zero cap increments. `CSARPointModifier=10`, the stock value, so Automatic SAR's survivors are paid at every debrief.

### The roster (fictional prices; real variants and squadrons, checked by the builder)

| Item | Unit | Picks | Points | On sale from |
|---|---|---|---:|---|
| Anzac-class frigate | `ran_ffh_anzac` | Variant2, 3, 5, 6, 7, 8 (Arunta, Warramunga, Parramatta, Ballarat, Toowoomba, Perth) | 240 | SR01 |
| Hobart-class destroyer | `ran_ddg_hobart` | Variant1–3 | 480 | SR01 |
| Seahawk | `usn_mh-60r` | Squadron20 (816 Squadron RAN, composed by SEST Collection Fixes) | 20 | SR01 |
| P-8A Poseidon | `usn_p8` | Squadron3 (RAAF) | 45 | SR03 |
| MQ-4C Triton | `raaf_mq-4c_triton` | Squadron1 | 60 | SR03 |
| E-7A Wedgetail | `E7A_Wedgetail` | Squadron1 | 80 | SR04 |
| F-35A | `raaf_f-35a` | Squadron1, 2 (3 and 77 SQN, Williamtown) | 45 | SR12 |
| Arafura-class OPV | `ran_opv_arafura` | Variant1 | 100 | TS01 |
| F/A-18F | `usn_fa-18f_blk3` | Squadron8 | 35 | TS04 |
| EA-18G | `usn_ea-18g` | Squadron6 | 55 | TS04 |

Not for sale: Collins and Farncomb (detached operations, authored), Supply and Stalwart (theatre logistics), the RNZAF Poseidon (a national allocation), Choules and Canberra (no deck-support test south of the Convergence), any tanker (no tasking role exists for one).

### Campaign variables — consequences that are enforced

| Written by | Variable | How | Read by | Effect |
|---|---|---|---|---|
| SR01 | `SR01ShadowNamed` | classify *Nan Hai 27* | SR05 | the collector is a classified contact from the first minute |
| SR02 | `SR02BoatNamed` | classify VICTOR | SR07 | the Akula is classified at start — Collins's picture from the ninth |
| SR03 | `SR03CrewRecovered` | victory | TS12 | the collector that came for the airlink's crew is revealed as the spoiler's spotter |
| SR04 | `SR04ServiceHeld` | service window stage | SR06 | `TaskForceModeRearmByVariableAND` — rearm only if the window held |
| SR05 | `SR05GroupClassified` | classify the command element | SR10 | the group's escorts are identified at start |
| SR07 | `SR07AkulaSunk` | flag on VICTOR | SR10 | VICTOR is in the line only if she got away (`IsFalse`) |
| SR08 | `SR08CorvetteNamed` | classify the inspecting corvette | TS02 | the corvette in Cook Strait is identified at start |
| SR09 | `SR09TankerLost` | support loss of Derwent Spirit | SR11 | she sails in Last Ship South only if she survived (`IsFalse`) |
| SR09 | `SR09ColdRouteHeld` | victory | SR11 | rearm before Last Ship South only if Cold Route was won |
| SR12 | `SR12NetworkNamed` | classify the network | TS01, TS04 | the collector *Nan Hai 27* (TS01) and the 054A (TS04) classified at start |
| TS01 | `TS01TenderNamed` | classify the tender | TS03 | the tender at the rendezvous is identified |
| TS02 | `TS02SubNamed` | classify TANGO | TS03 | TANGO on the surface is classified at start |
| TS03 | `TS03TenderNamed` | classify the tender | TS05 | the survey ship is identified |
| TS05 | `TS05RomeoSunk` | flag on ROMEO | TS09, TS12 | ROMEO screens the group only if alive (`IsFalse`) |
| TS08 | `TS08YasenSunk` | flag on SIERRA-TWO | TS09 | SIERRA-TWO joins the convoy action only if alive (`IsFalse`) |
| TS10A | `TS10ANorthHeld` | victory | TS11 | the northern group reinforces the approaches only if not held (`IsFalse`) |
| TS10B | `TS10BSouthHeld` | victory | TS11 | the southern group reinforces only if not held (`IsFalse`) |
| TS11 | `TS11CarrierSunk` | flag on Liaoning | TS12 | the spoiler strike flies only if she is afloat (`IsFalse`) |

Only the `IsFalse` spawn form and the `VariableCheck` reveal form appear in the shipped data; both are used exactly as Southern Watch uses them, and `IsTrue` appears only in `TaskForceModeRearmByVariableAND`, where the authoring guide attests it.

---

## 5. Equipment truth

Produced by the builder from the winning files (24 September 2026). Range is the airframe's own; radius is 40% of it; reach is the longest round the fit hangs — a ceiling, never a capability.

| Role | Unit | Mod attribution for `U()` | What the file says |
|---|---|---|---|
| Frigate | `ran_ffh_anzac` | `SEST_RAN_Fleet` | reach 166; deck 1 (MH-60R, S-70B-2); 8 variants |
| Destroyer | `ran_ddg_hobart` | `SEST_RAN_Fleet` | reach 950; deck 1; 3 variants |
| OPV | `ran_opv_arafura` | `SEST_RAN_Fleet` | reach 166; fits Containers/AntiShip/AntiAir; 4 variants |
| Submarine | `ran_ssg_collins` | `SEST_RAN_Fleet` | 6 variants, all Australia; Variant1 Collins, Variant2 Farncomb |
| Replenishment | `ran_aor_supply` | `SEST_RAN_Fleet` | Variant1 Supply, Variant2 Stalwart; a working supply system since 26 Sep 2026 (0.5 nmi, 12 kn, nothing dearer than 8000 points: NSM, Tomahawk, SM-6 and torpedoes pass), not yet seen transferring in game |
| Seahawk | `usn_mh-60r` | `mh-60r-2154545636` | range 520 (radius 208); fits ASW/ASWLongRange/ASWPatrol/Anti-shipLate |
| Poseidon | `usn_p8` | `p-8-poseidon` | range 2,700 NM (radius 1,080); fits ASW/AntiShip; Squadron3 = RAAF, **Squadron6 = RNZAF (Nation=New Zealand)** |
| Wedgetail | `E7A_Wedgetail` | `e-7a-wedgetail` | range 2,700 (radius 1,080); no fits |
| Triton | `raaf_mq-4c_triton` | `SEST_ADF_Persistent_ISR` | range 9,430 (radius 3,772); unarmed |
| F-35A | `raaf_f-35a` | `SEST_RAAF_F-35A_JATM` | range 1,367 (radius 547); Squadron1/2 Williamtown, 3 Tindal |
| Super Hornet / Growler | `usn_fa-18f_blk3` / `usn_ea-18g` | `SEST_Growler_NGJ_MALICE` | radius 506; Squadron8 / Squadron6 Australian |
| Fields | `airbase_raaf_edinburgh`, `_east_sale`, `_williamtown`, `airbase_rnzaf_ohakea`, `airbase_rnzaf_auckland` | `SEST_RAAF_Bases` | capacity 200; the two RNZAF bases were added for this campaign (Nation=New Zealand, No. 5 Squadron P-8A) |
| Civil fields | `airfield_small_1` | `_vanilla` | capacity 48 — Hobart, Christchurch, Invercargill |
| Carrier | `plan_type_001` | `liaoning-type-001` | deck 36; her J-15s (`plan_j-15`, `plan_j-15d`: `type-003-004-maneuverwarfare`) reach 156 with AntiShip; Ka-31 AEW (`plan_ka-31`, `modern-plan-systems`); Z-18F ASW (`plan_z-18f`, `chinese-navy-plan`) |
| Escorts | `plan_type_054a_p5`, `plan_type_056a` | `modern-plan-systems` | reach 85 (YJ-83); 054A deck lists Z-9 only |
| Flagship | `plan_type_052d_p3` | `modern-plan-systems` | reach 1,050 — fleet actions only |
| Submarines | `plan_ssn_type_093b`, `plan_ss_type_039c` (`plan-submarines`); `plan_ss_kilo` (`chinese-navy-plan`); `wp_ssn_akula`, `wp_ssgn_yasen` (`russian-submarines`) | | 093B/039C reach 350 (YJ-18), Kilo 20, Akula/Yasen 573 (Kalibr) — ceilings |
| Russian surface | `wp_bpk_udaloy` (`_vanilla`), `wp_vt_boris_chilikin` (`SEST_Replenishment`) | | Udaloy reach 27, deck 2 (Ka-27); the oiler, a working supplier (nothing dearer than 13000 points) |
| Collector / tender | `wp_agi_okean` (`_vanilla`), `civ_ms_kommunist` (`_vanilla`), `plan_ap_qiongsha` (`_vanilla`) | | the Okean collector among `civ_fv_okean` trawlers; a merchant as a tender; a Qiongsha as the replenishment stand-in |
| Long-range air | `wp_tu-142m`, `wp_tu-95rt` (`_vanilla`), `wp_il-78` (`il-78`) | | red aircraft with no field in the mission fly on the engine's own no-base rule (unlimited fuel); the briefing says a Midas is behind them |
| Merchants | `civ_ms_freighter_d`, `civ_ms_amra`, `civ_ms_andizhan` (`re-power-resupply`); `civ_ms_sealift_pacific` (`SEST_Replenishment`, which the game reads her from since 26 Sep 2026); `civ_ms_mairangi_bay` (`merchants-expanded`); `anl_ms_bulk`, `ran_ms_roro_a` (`auxilliary-merchant-pack`, armed: WeaponStatus=Hold always); vanilla `civ_ms_ivan_franko` (liner), `civ_ms_ritina` (tanker), `civ_ms_roro_a/b/c` (ferries), `civ_ms_bulk`, `civ_ms_car_carrier_a`, `civ_ms_encounter` | | |
| Fishing | `civ_fv_okean`, `civ_fv_sterntrawler_a–d`, `civ_fv_crabboat`, `civ_fv_fishingboat_a/b` (`_vanilla`) | | |
| Rigs | `civ_spar_rig` (`_vanilla`, unarmed, Target) | | `snap="sea"` — a land unit that belongs in water; never `civ_spar_rig_helo` (the armed Iranian one) |
| Whale | `civ_humpback` (`humpback-whale`) | | a submarine to the engine; `shallow` |
| Airliners | `civ_a320`, `civ_a330` (`civil-aircraft-airbus`) | | |

### New Zealand dependency findings

1. **RNZAF P-8A resolves today** with no new dependency: `usn_p8` Squadron6 in the winning `usn_p8_squadrons.ini` (Workshop 3602046770) is `Nation=New Zealand`, RNZAF livery. It is the campaign's New Zealand aircraft. A second, Red Storm Arsenal implementation (`usn_p_8a` Squadron23) exists and is not used, to keep one airframe family.
2. **Publication risk:** 3602046770 is marked removed/incompatible on the public Workshop page. It is a Southern Watch dependency already (the RAAF Poseidon is the same file), so this campaign adds no new exposure; before publication the note in Southern Watch's publishing.md applies to both.
3. **No RNZN surface fleet** is in the enabled collection. *A Force for New Zealand* (3405821509) is not added. Te Kaha and Te Mana are where Commander Brand says they are, and no mission places them.
4. **No HMNZS Aotearoa.** Removed from the roster as the specification requires; the NZ logistics contribution is Lyttelton, Bluff and Ohakea.
5. **NZ helicopters:** none exist in the collection; none are placed.
6. **Two RNZAF bases** were added to `SEST_RAAF_Bases` (`airbase_rnzaf_ohakea`, `airbase_rnzaf_auckland`) so the Poseidon has a New Zealand field to recover on. They clone the same template every RAAF base does.

---

## 6. Mission cards — chapter A, Southern Reach

Every card names its centre (proved against the coastline extract), its role on the escalation curve (the builder's red-combat budget), the forces by ownership state, the objectives with their resolvers, and what it writes or reads. Distances are what the builder's own checks measure; a station that fails a check is moved, not argued with.

### SR01 — Southern Departure · Storm Bay · 6 Dec · role `opening` · 60 min
Built. See `sr01_southern_departure.py`. Convoy of three out of Storm Bay on 170; classify *Nan Hai 27* among two Okean trawlers; a 054A 55 NM SE closing on channel 16. Writes `SR01ShadowNamed`.

### SR02 — Silent Track · Macquarie Ridge · 9 Dec · role `patrol` · 70 min · blank
Centre −50.3, 162.8 (122 NM from the nearest coast). Detached submarine operation: **HMAS Collins** (`ran_ssg_collins` Variant1, blue, authored, `periscope`, weapons Tight) and **Kiwi 05** (`usn_p8` Squadron6, Rewi's crew, ASW fit, alt 12,000, Tight) out of **RNZAF Base Ohakea** (blue land unit, `nation="New Zealand"`, ~810 NM). Red: **VICTOR** (`wp_ssn_akula`, `belowlayer`, routed north-east along the ridge at telegraph 2) and *Nan Hai 27* (`wp_agi_okean`, Hold) 30 NM north as the tell. Neutral: a Bluff toothfish longliner (`civ_fv_sterntrawler_c`, routed), a NZ research vessel *RV Southern Surveyor* (`civ_ms_irkutsk`, routed), a humpback (`civ_humpback`, `shallow`). Objectives: **Track** (main): classify VICTOR then bring Collins to the exit point (arrive stage after classify, bearing 120, radius 10); **Restraint** (`spare`, red_sub): the ceasefire holds in the south — do not attack; **Collins** (protect). Fatal: Collins. Writes `SR02BoatNamed` (classify). ROE text: "put a name on her and get off her track."

### SR03 — Search Datum · the southern route · 12 Dec · role `patrol` · 70 min
Centre −52.0, 140.0 (open ocean). The Wilkins airlink **WILKINS 03** (story: an A319 stand-in) went out of contact on the Hobart–Casey track and an EPIRB was heard by a longliner. Player: Generated escort (anchor), **HeloRecon** and **Recon** slots, **Sentry 21** (Triton, fixed). Field: **Hobart Airport (RAAF detachment)** as a blue `airfield_small_1` (630 NM; the P-8 recovers there). Contacts to sort: three neutral fishing hulls with routes, the cruise ship *Polar Horizon* southbound, a merchant, a whale; red: **Nan Hai 24** (`civ_fv_okean`, red, Hold — the trawler that "recovered" the crew and is steaming for the collector) and *Nan Hai 27* (`wp_agi_okean`, Hold) 25 NM from the anchor. Objectives: **Datum** (main): classify *Nan Hai 24* (stage), then put a ship or the Seahawk within 3 NM of her (arrive on `at_unit`) — "a boarding party alongside"; **Neutrals**; **Flagship**. Fatal: *Nan Hai 24* destroyed (she has the crew aboard — a fatal on a red station). Victory sets `SR03CrewRecovered`. Window: buy (Anzac, Hobart, MH-60R, P-8, Triton), repair, rearm; rows HELO, RECON. Built as role `patrol`, not `recon`: the recon budget requires a red unit that can reach blue, and the only red hulls here are an unarmed trawler and the collector.

### SR04 — Macquarie Passage · Macquarie Island · 15 Dec · role `logistics` · 75 min
Centre −54.3, 158.3. **HMAS Supply** (Variant1, authored, named) and **MV Coral Pioneer** at the Buckles Bay anchorage (−54.50, 158.99: `coastal=True`; 1 NM off the isthmus), the **Macquarie Island station** as a neutral `civ_radiostation` ashore (−54.499, 158.937), the player's escorts Generated 3 NM east, HELO and RECON slots (Hobart Airport blue, 813 NM). Service window: Supply and Coral Pioneer inside 5 NM of Supply's start when 30 minutes have run (stage, `after_minutes=30`, sets `SR04ServiceHeld`), then both to the withdrawal line 14 NM north (authored `at`, radius 12). Supply's rig is live meanwhile: an escort inside half a mile at 12 kn or less takes missiles and torpedoes back, and the briefing says so; the window is what is scored. Red: **VICTOR** 45 NM south-west closing at telegraph 4; **RV Akademik Fersman** (`civ_ms_kommunist`, red, Hold) 35 NM west as her tender; a **Bear-F** (`wp_tu-142m`, ASW fit, Hold, routed over the anchorage at 8,000 ft, unlimited fuel by the engine's rule) making a pass. Objectives: **Service** (main), **Supply** (protect), **Cargo** (protect Coral Pioneer), **Restraint** (`spare` VICTOR, the Bear and the tender: a reconnaissance flight is not an attack). Fatal: Supply, Coral Pioneer. Window: buy (+Wedgetail), repair, rearm.

### SR05 — Empty Horizon · the open Southern Ocean · 18 Dec · role `recon` · 65 min · blank
Centre −56.0, 148.0. Allocated air operation: **Sentry 22** (Triton, fixed, 50,000 ft) and **Bluefin 32** (P-8 Squadron3, fixed, ASW fit) out of Hobart Airport (blue, 790 NM). Contacts, 80–110 NM south: the protection group's command element — **a 054A**, **a 056A**, *Nan Hai 27* (revealed if `SR01ShadowNamed`), a **Ka-31** up and a Z-9 — with three Okean trawlers, a Russian oiler (`wp_vt_boris_chilikin`, red, Hold) and a neutral merchant nearby for discrimination. Objectives: **Picture** (main): classify the 054A and the 056A (min 2, stage), then recover the Triton to a point north (arrive, bearing 0, radius 15); **Sentry** (protect); **Bluefin** (protect); no "undetected" objective. Fatal: the Triton. Writes `SR05GroupClassified`. Reads `SR01ShadowNamed`. The 054A's HQ-16 is the reason the Triton cannot simply overfly; the briefing says so.

### SR06 — Broken Supply Line · south of the Auckland Islands · 21 Dec · role `escort` · 75 min
Centre −51.5, 165.0 (51 NM from the islands). **MT Derwent Spirit** with "one engine and a hull patch" — telegraph 1 on a route north-east toward Bluff — and **Coral Pioneer** in company; the player's escorts Generated; HELO and RECON slots with **Invercargill Airport** (blue `airfield_small_1`, 260 NM) as the field. Red: **VICTOR** ahead of the track at `belowlayer` routed onto it; **a 054A** 50 NM east shadowing with its Z-9; a **Bear-D** (`wp_tu-95rt`, Hold) overhead. Neutral: an Auckland Islands expedition vessel, a Bluff longliner, a whale. Objectives: **Coaster** (main: arrive, `transit=6`, bearing 40, radius 10), **Cargo** (protect Coral Pioneer), **Neutrals**. Fatal: the coaster. Window: `rearm_if=("SR04ServiceHeld","IsTrue")`, no builder. Test card: fly it once with empty magazines.

### SR07 — Beneath the South · the deep Southern Ocean · 24 Dec · role `escort` · 80 min
Centre −57.5, 152.0. The first authorised kill: **sink VICTOR**. Player Generated with HELO and RECON slots (Hobart Airport blue, 900 NM); the Wedgetail is not here (it cannot hear a submarine and the Triton cannot drop a buoy; briefing). Red: **VICTOR** (`belowlayer`, routed across the escorts' bow at telegraph 2 — the search area is the point), **RV Akademik Fersman** (red, Hold; `spare` — sinking the tender is the incident Canberra will not own), a **Bear-F** pass. Reads `SR02BoatNamed` (VICTOR classified at start with Rewi's datum). Objectives: **Boat** (main: destroy red_sub), **Tender** (spare), **Flagship** (protect). Writes `SR07AkulaSunk` (flag). Window: buy, repair, rearm — "Christmas at Bluff".

### SR08 — The Gateway · Christchurch approaches · 28 Dec · role `escort` · 65 min
Centre −43.7, 173.5 (17 NM off Banks Peninsula). Protect the gateway traffic into Lyttelton: **MV Polar Giant** (US Antarctic Program cargo, `civ_ms_amra`, blue, named) and **MT Canterbury Spirit** (`civ_ms_ritina`, blue) from Pegasus Bay south-west to the Lyttelton approach (authored `at` −43.55, 172.90, radius 6 — on water, 4 NM off the Heads). Player Generated, HELO and RECON slots; **Kiwi 05** (fixed) out of **Christchurch International** (blue `airfield_small_1`, −43.489, 172.532) with **Ohakea** also placed. Red: **a 056A** closing on the tanker to "inspect", a **Z-9** from it, *Nan Hai 27* off Akaroa. Neutral: the Lyttelton–Chatham freighter, a Kaikoura whale-watch vessel (`civ_fv_fishingboat_a`), two trawlers, the Christchurch–Sydney airliner. Objectives: **Gateway** (main: both arrive), **Corvette** (classify, sets `SR08CorvetteNamed`), **Traffic**, **Flagship**. Weapons Tight; the corvette starts Tight too. Window: buy, repair, rearm (Lyttelton).

### SR09 — Cold Route · south of Australia · 2 Jan · role `fleet` · 90 min
Centre −48.5, 137.0. The January voyage: **Southern Endeavour**, **Derwent Spirit**, **Coral Pioneer**, **MV Aurora Trader** (`anl_ms_bulk`, Hold) and **MV Davis Provider** (`civ_ms_andizhan`) with the player's escorts Generated, HELO and RECON slots, **Wedgetail 05** (fixed) and **Kiwi 05** (fixed) out of **RAAF Base Edinburgh** (blue, 830 NM) — no fighter base is within reach and the briefing says so. Red: **Liaoning** 150 NM south-east with **two 054A** and a **056A**, a **J-15 AntiShip pair** and a **J-15D** routed onto the convoy, **Ka-31** up, **Z-18F** dipping, and **ROMEO** (`plan_ssn_type_093b`) ahead of the convoy — nine red combat units. Neutral: two Okean trawlers and a Hobart-bound bulker for discrimination. Objectives: **Convoy** (main: 4 of 5 arrive, Southern Endeavour among them; bearing 240, radius 15, `transit=12`); **Tanker** (protect Derwent Spirit; her loss is a `support_loss` that sets `SR09TankerLost`); **Wedgetail** (protect); **Neutrals**. Victory sets `SR09ColdRouteHeld`. Fatal: Southern Endeavour; two convoy hulls. Window: buy, repair, rearm (Hobart, before sailing).

### SR10 — Southern Line · the ice edge · 6 Jan · role `recon` · 55 min
Centre −60.0, 118.0 (375 NM from the nearest coastline; the southernmost mission). Reduced aviation: **HeloRecon only** — no field is within a Poseidon's radius and the briefing says the weather has grounded the Triton. The player's escorts Generated on the "Casey line". Red: the group's command element — **Liaoning**, **a 054A**, **a 056A**, *Nan Hai 27*, **Ka-31** — 40 NM south holding station over the fishing fleet, weapons Tight; **VICTOR** (`spawn_if=("SR07AkulaSunk","IsFalse")`) in the line. Neutral: three Okean trawlers, **RV Akademik Fersman** re-flagged neutral for this mission (a research vessel at the ice is a research vessel), a whale. Reads `SR05GroupClassified` (escorts identified at start). Objectives: **Identify** (main: classify Liaoning and *Nan Hai 27*, then withdraw north to the line — arrive after classify, bearing 0, radius 15); **Restraint** (`spare` *Nan Hai 27*: a shot at the collector is the incident they came for); **Flagship**; **Neutrals** (the neutral-loss objective covers the trawlers, the research vessel and the whale). The ROE is the mission: everything red starts Tight; fire first and the group answers.

### SR11 — Last Ship South · the deep transit · 10 Jan · role `escort` · 80 min
Centre −55.5, 128.0. **Southern Endeavour**'s last voyage with **Derwent Spirit** (`spawn_if=("SR09TankerLost","IsFalse")`) and the player's worn escorts Generated; **HeloRecon only** (Hobart Airport is 1,082 NM: outside a Poseidon's radius, on purpose). Red: **a 054A** and **a 056A** returning north, **ROMEO** across the track, a **J-15 pair** from Liaoning 220 NM east with the **Ka-31**. Objectives: **Endeavour** (main: arrive, bearing 250, radius 12, `transit=12`), **Tanker** (protect; only if she spawned), **Flagship**. Fatal: Southern Endeavour. Window: `rearm_if=("SR09ColdRouteHeld","IsTrue")`, no builder, no repair. Test card: the victory/defeat precedence case (loss and arrival in the same update).

### SR12 — Turning North · the Tasman approaches · 14 Jan · role `recon` · 70 min
Centre −40.5, 151.5 (138 NM off Gabo Island). The group transits north-east into the Tasman: **Liaoning**, **a 054A**, **a 056A**, the **Qiongsha** replenishment stand-in, *Nan Hai 27* and **RV Akademik Fersman**, all Tight, routed 040. Player Generated with HELO, RECON and **CAP** (F-35A from **RAAF Base East Sale**, blue, 248 NM) — the first fighter cover of the campaign; **Wedgetail 05** fixed. Objectives: **Network** (main: classify Liaoning, the Qiongsha and *Nan Hai 27*, min 3, then hold the shadowing line — arrive after classify); **Restraint** (`spare` everything red: shadow, do not start the Tasman war); **Flagship**. Writes `SR12NetworkNamed`. Window: buy (+F-35A), repair, rearm (Hobart). The chapter card that follows reads the ledger.

## 7. Mission cards — chapter B, Tasman Shield

### TS01 — Home Waters · Fiordland approaches · 22 Jan · role `patrol` · 65 min
Centre −46.1, 165.9 (25 NM off Puysegur). Dense neutral traffic: two Milford cruise ships (`civ_ms_ivan_franko`, `civ_ms_roro_c` as a small expedition ship), three Bluff cray boats and longliners, a Fiordland fisheries patrol stand-in (neutral `civ_fv_sterntrawler_d` "Fisheries NZ patrol"), an Invercargill–Queenstown airliner. Red: **MV Austral Compliance** (`civ_ms_kommunist`, red, Hold — AMS tender), *Nan Hai 27* (revealed if `SR12NetworkNamed`), and **TANGO** (`plan_ss_type_039c`, `belowlayer`, 20 NM south-west, not routed toward anyone). Player Generated (Arafura now on sale) with HELO and RECON slots; **Kiwi 05** fixed from **Invercargill** (blue). Objectives: **Tender** (main: classify the tender, then hold the patrol line — arrive after classify), **Boat** (classify TANGO, `15,0,None`), **Traffic**, **Flagship**. Writes `TS01TenderNamed`. Window: buy (+Arafura), repair, rearm (Sydney, then the transit).

### TS02 — Cook Strait · 25 Jan · role `patrol` · 60 min
Centre −41.55, 174.45 (12.6 NM from every coast; all stations inside the strait's water: Cloudy Bay −41.50, 174.25; off Oteranga −41.35, 174.55; Cape Campbell −41.70, 174.50). Protect the declared cable corridor — an abstract box, not a mechanic: **CS Tasman Reliance** (`civ_ms_encounter`, blue, "cable repair ship, stand-in") must hold the corridor box (stage: area, `after_minutes=25`) while the ferries cross. Red: **TANGO** at `periscope` on the corridor; **the 056A** from SR08 (revealed if `SR08CorvetteNamed`) entering from the south to "inspect" the cable ship, Tight. Neutral: two Interislander stand-ins (`civ_ms_roro_a`, `civ_ms_roro_b`, routed Wellington↔Picton), a Wellington–Christchurch airliner, a Marlborough fishing boat, a coastal tanker. Player Generated 5 NM south-south-east of the cable ship, on the corridor box's edge, HELO and RECON slots; **Kiwi 05** fixed from **Ohakea** (110 NM). Objectives: **Corridor** (main: the cable ship holds the box for the window, then reaches Wellington's approach — arrive after stage, authored `at` −41.42, 174.75, radius 5); **Contact** (classify TANGO, sets `TS02SubNamed`); **Ferries** (`spare` on the neutral ferries — the neutral rule already ends the mission; this scores it); **Traffic** (the neutral-loss objective); **Flagship**. Kiwi 05's station is −41.70, 174.20, 14 NM from TANGO (the patrol standoff). No MAD or dipping-sonar claim.

### TS03 — Chatham Watch · east of New Zealand · 28 Jan · role `patrol` · 70 min
Centre −44.0, 178.3 — every unit west of 180°; the Chathams are 200 NM further east and stay in the briefing. The rendezvous: **TANGO surfaced** (`ran`: 0 depth, telegraph 1) alongside **MV Austral Compliance** (red, Hold) 60 NM east of the player's Generated force; **Kiwi 05** (fixed) and the player's own Poseidon (RECON slot) out of **Ohakea** (262 NM); HELO slot. Reads `TS01TenderNamed`, `TS02SubNamed`. Objectives: **Boat** (main: destroy TANGO — the first kill of the Tasman chapter, authorised after Cook Strait); **Tender** (classify, sets `TS03TenderNamed`; `spare` her — a merchant hull under a state flag); **Flagship**. Neutral: a Chatham Islands freighter, two longliners, a whale.

### TS04 — Tasman Crossing · mid-Tasman · 1 Feb · role `escort` · 80 min
Centre −38.5, 158.5. Two merchant groups 30 NM apart, **abeam** of the 060 track (15 NM either side of it) — **group A** (Coral Pioneer, `anl_ms_bulk`) to the south-east and **group B** (`civ_ms_freighter_a`, `civ_ms_car_carrier_a`) to the north-west — bound for Auckland; the player's whole force Generated between them (no detachment: §4). Groups in line ahead cannot share an arrival box — the trailing one can never reach it in the clock — so the box is authored 20 NM ahead of the escort (−38.33, 158.87, radius 15) and each group is 25 NM from it. HELO, RECON and **CAP** rows: F-35A from **RAAF Base Williamtown** (blue, 473 NM), **Wedgetail 05** fixed. Red: **Liaoning** 200 NM south-east with **a 054A** (revealed if `SR12NetworkNamed`), a **J-15 AntiShip pair** and a **J-15D** routed low onto group B, **Ka-31**. Neutral: a Sydney–Auckland A330 crossing, a cruise ship, a bulker. Objectives: **Crossing** (main: 3 of 4 arrive, both groups' stations named in `units`, authored `at`, `transit=12`), **Wedgetail** (protect), **Neutrals**, **Flagship**. Window: buy (+F/A-18F, EA-18G), repair, rearm.

### TS05 — Under the Tasman · the cable corridor · 4 Feb · role `patrol` · 75 min · blank
Centre −36.5, 160.5. Detached submarine operation: **HMAS Farncomb** (Variant2, `periscope`, weapons Free — the ROE has changed) against **ROMEO** (`belowlayer`, routed along the corridor) escorting **RV Austral Survey** (`civ_ms_slavyansk`, red, Hold; revealed if `TS03TenderNamed`) and **a 054A** with its Z-9. Objectives: **Romeo** (main: destroy), **Survey** (`spare`), **Farncomb** (protect). Writes `TS05RomeoSunk` (flag). No window. Depth, speed and the layer are the mission; no deep-sound-channel claim.

### TS06 — Bass Strait · 8 Feb · role `escort` · 70 min
Centre −39.3, 147.0 (18 NM from the nearest coast; the Gippsland platforms at −38.55, 148.20 and −38.60, 147.85 are 30–40 NM off, `snap="sea"`). Dense traffic: two Devonport ferries (`civ_ms_roro_b`, routed Devonport↔Geelong), a Geelong-bound tanker (blue: **MT Bass Provider**, `civ_ms_ritina`), a bulker, two rig supply boats (`civ_fv_sterntrawler_a/b`), the Melbourne–Hobart airliner; **three platforms** (`civ_spar_rig`, neutral). Red: **MV Southern Compliance** (`wp_ms_mercur_decoy`, Hold — an AMS merchant radiating a frigate's radar), **a Kilo** (`plan_ss_kilo`, `belowlayer`) inside the strait, **a 056A** entering from the east, a **Z-9**. Player Generated with HELO, RECON and CAP rows from **RAAF Base East Sale** (blue, 75 NM). Objectives: **Tanker** (main: the tanker reaches the western exit — bearing 250, radius 10, `transit=12`), **Platforms** (`spare` the three rigs), **Traffic**, **Boat** (classify the Kilo, `15,0,None`). Window: buy, repair, rearm (Melbourne).

### TS07 — Southern Air Bridge · the Tasman air route · 11 Feb · role `escort` · 60 min
Centre −36.0, 152.5 (98 NM off the NSW coast). Protect **Relief 21** (`civ_a330`, blue, Hold — "the NZ relief detachment's charter, a civil stand-in") and **Wedgetail 06** (fixed) across the air bridge into Sydney: arrive box off Sydney Heads (authored `at` −33.85, 151.55, radius 10). Player Generated (the destroyer's SAMs are the surface half), **CAP** and **RECON** rows from **RAAF Base Williamtown** (blue, 195 NM; `airbase_prep=True`), **Sentry 23** (Triton, fixed). Red: **Liaoning** 250 NM south-east, a **J-15 pair** and a **J-15D** routed onto the charter's track, **Ka-31**. Neutral: two Sydney–Auckland airliners, a cruise ship, a coastal bulker. Objectives: **Bridge** (main: Relief 21 arrives), **Wedgetail** (protect), **Neutrals**, **Flagship**. Window: buy, repair, rearm (Sydney).

### TS08 — Great Australian Bight · 15 Feb · role `patrol` · 80 min
Centre −35.5, 132.5 (139 NM offshore). Long-range search with limited service: the player's escorts Generated with HELO and RECON rows from **RAAF Base Edinburgh** (blue, 300 NM); **HMAS Collins** (Variant1, blue, authored, `periscope`, Tight) 25 NM west of the escorts as the search's other half — a protected hull has to be within what its escort can steam in the clock (32 NM at 24 kn in 80 minutes), so she is not a separate sector 45 NM off. Red: **SIERRA-TWO** (`wp_ssgn_yasen`, `belowlayer`), the vanilla **Udaloy** *Marshal Shaposhnikov* (`wp_bpk_udaloy`, with a Ka-27 up) and the oiler **Boris Chilikin** (red, Hold) at a rendezvous 70 NM south-west. Neutral: two Port Lincoln tuna boats, a Bight bulker, a whale. Objectives: **Boat** (main: destroy SIERRA-TWO — 80 minutes is the point), **Oiler** (classify, `15,0,None`), **Collins** (protect), **Neutrals**. Writes `TS08YasenSunk` (flag). Window: repair only. The USN Virginia on the Western Australia rotation is in the briefing and not on the plot.

### TS09 — The Southern Convoy · south of Portland · 19 Feb · role `fleet` · 90 min
Centre −38.6, 140.5 (proved on water; Portland's approach at −38.6, 141.6 is 10 NM off). Five critical hulls (Adelaide and Melbourne bound: `civ_ms_ritina`, `anl_ms_bulk`, `civ_ms_freighter_b`, `civ_ms_car_carrier_a`, Coral Pioneer) and the player's escorts Generated; HELO, RECON, CAP and **Attack** rows — F-35A, Poseidon and Wedgetail from **Edinburgh** (251 NM, the nearer field, so the fighters recover there), the Super Hornet/Growler Attack row recovering at Edinburgh (radius 506). **Wedgetail 05** fixed. Red: **Liaoning**, **a 052D** (the flagship, only here and in TS11), **two 054A**, **a 056A**, three **J-15 AntiShip**, a **J-15D**, **Ka-31**, **Z-18F**, **ROMEO** (`spawn_if=("TS05RomeoSunk","IsFalse")`), **SIERRA-TWO** (`spawn_if=("TS08YasenSunk","IsFalse")`). Objectives: **Convoy** (main: 4 of 5, bearing 60 — the split point off Portland; bearing 20 runs into the Coorong coast at the solved distance — radius 15, `transit=12`), **Wedgetail**, **Neutrals** (a coastal ro-ro, a bulker, the Melbourne–Perth airliner), **Flagship**. Window: buy, repair, rearm (Adelaide).

### TS10A — Northern Priority · Hauraki Gulf approaches · 22 Feb · optional · role `patrol` · 60 min
Centre −36.45, 175.05 (the Gulf; Colville Channel −36.20, 175.25; Tiritiri −36.60, 174.95; all on water). The player's detachment (`detachment=True`) and **Kiwi 05** from **RNZAF Base Auckland** (blue, Whenuapai, 30 NM) hold Auckland's approaches against **a 056A**, *Nan Hai 27* and **MV Austral Compliance** trying to establish a "compliance station" off the Colville Channel. Neutral: the Auckland container traffic (two), a Great Barrier ferry, fishing boats, the Auckland–Sydney airliner. Objectives: **Approaches** (main: the container ship `MV Hauraki Trader` (blue) reaches the Rangitoto Channel approach — authored `at` −36.72, 174.90, radius 4); **Station** (classify the tender, `15,0,None`); **Traffic**; **Flagship**. Victory sets `TS10ANorthHeld`. `expires_after="Approaches"`.

### TS10B — Southern Priority · Gulf St Vincent approaches · 22 Feb · optional · role `patrol` · 60 min
Centre −35.15, 137.9 (the mouth of Gulf St Vincent; Backstairs Passage −35.70, 138.10). The player's detachment and a Poseidon (RECON) from **Edinburgh** (blue, 60 NM) hold Adelaide's approaches: **MT Osborne Spirit** (`civ_ms_ritina`, blue) starts 14 NM from the Outer Harbor approach (authored `at` −34.75, 138.35, radius 5 — sixty minutes at the solver's 18 kn buys 13.5 NM, which is why the centre moved north-east from the bible's first draft) past **a 054A** 40 NM south-west and **a Kilo** (`belowlayer`) between it and the track, with a **Z-9**. Neutral: a Kangaroo Island ferry (`civ_ms_roro_c`), tuna boats, a grain bulker, the Adelaide–Melbourne airliner. Objectives: **Approaches** (main), **Boat** (classify, `15,0,None`), **Traffic**, **Flagship**. Victory sets `TS10BSouthHeld`. `expires_after="Approaches"`.

### TS11 — Approaches · the western Tasman · 26 Feb · role `fleet` · 90 min
Centre −39.5, 151.0. Contain the remaining group: **Liaoning**, **the 052D**, **a 054A**, three **J-15**, a **J-15D**, **Ka-31**, **Z-18F**; plus **a 056A and *Nan Hai 27*** (`spawn_if=("TS10ANorthHeld","IsFalse")` — "the northern element joined") and **a second 054A** (`spawn_if=("TS10BSouthHeld","IsFalse")`). The last movement — three transports (blue) — must pass to the north-east while the group is held off. Player Generated; HELO, RECON, CAP, Attack rows from **Williamtown** (402 NM) and **East Sale** (200 NM); **Wedgetail 05** fixed. Objectives: **Movement** (main: 2 of 3 arrive, bearing 45, radius 15, `transit=14`), **Flagship** (destroy the 052D, `20,-10,Fail` — a destroy objective must not end Complete), **Carrier** (destroy Liaoning, `25,0,None`; flag `TS11CarrierSunk`), **Wedgetail** (protect), **Neutrals**. Window: buy, repair, rearm (Sydney). Time-on-target is an advantage, never a requirement; the briefing says so.

### TS12 — Southern Cross · mid-Tasman · 2 Mar · role `escort` · 75 min
Centre −40.5, 155.5. The relief convoy to New Zealand: **Coral Pioneer**, `civ_ms_freighter_d` "MV Aotearoa Relief", `anl_ms_bulk`, `civ_ms_sealift_pacific`; the player's worn escorts Generated; HELO, RECON, CAP (Williamtown, 495 NM; East Sale, 430 NM) — nothing bought here outlives the campaign; **Kiwi 05** and **Wedgetail 05** fixed. Two groups in the box: the **withdrawing group** (neutral: a 054A and the Qiongsha on a route north, complying) and the **spoiler** (red: a 054A Tight-then-Free on a route onto the convoy, **ROMEO** `spawn_if=("TS05RomeoSunk","IsFalse")`, a **J-15 pair** `spawn_if=("TS11CarrierSunk","IsFalse")`, and *Nan Hai 27* — revealed if `SR03CrewRecovered`, with the intel that the collector that came for the airlink's crew is the spoiler's spotter). Objectives: **Convoy** (main: 3 of 4, Coral Pioneer among them; bearing 80, radius 15, `transit=11`), **Ceasefire** (neutral: the withdrawing group), **Escorts** (protect), **Wedgetail** (protect). Points 0; the epilogue reads the ledger.

---

## 8. What this campaign does not claim

- That a hose ever passes fuel. Every service is a window and a position.
- That a submarine is surfaced, dived, quiet or loud. Depth tokens are placement; "surfaced" is a house rule in the text.
- That ice, fog, the Convergence, ducting, icing or polar communications exist in the engine.
- That anything is "undetected". No trigger measures it; nothing scores it.
- That a red aircraft with no field is fuel-limited. It is not; the engine's own rule for a base-less aircraft is unlimited fuel, and the briefings say a tanker is behind the Bears.
- That the Antarctic coast, Casey or Wilkins are on a map anything sails to. The southernmost centre is 375 NM from the nearest coastline.
- That an RNZN ship exists in this collection. None is placed.
- That Type 055 / 052D hypersonics are balanced. The 052D is in the two fleet actions (TS09, TS11) and nowhere else, and its reach is recorded.
- That Airbase Preparation, Air Tasking, Generated placement, `SpawnByVariableAND`, `VariableCheck` or `TaskForceModeRearmByVariableAND` behave as read. They are emitted exactly as the shipped campaign emits them, and §9 is where they get proved.

## 9. Acceptance gates before this is called playable

**Geography.** Load SR01 (Storm Bay), SR04 (Macquarie), SR10 (the ice edge, 60 South), SR08 (Banks Peninsula), TS02 (Cook Strait), TS06 (Bass Strait), TS10A (Hauraki Gulf). For each: coastline renders where the extract says it is; no ship spawns ashore; submarine depths are valid; routes and trigger areas behave; generated placement lands on the anchor; the tactical map labels the theatre; performance holds at the mission's neutral count. The repo's own evidence that the map reaches these latitudes is `chapter 5 - Polar Pickup` (a user mission at 76 South) and the stock `03 Lifeline at the Edge of the World` (46 South); nothing between has been loaded.

**Task Force.** Across SR01 → SR03 → SR04: buy an Anzac and a Seahawk; assign the Seahawk to Ship's Flight; buy a Poseidon before SR03 and see it in the Recon cockpit; expend; take repairable damage; complete; save; quit; reload; confirm force, ammunition, damage, crew and points; confirm SR04's repair window; confirm SR05→SR06 withholds rearm when `SR04ServiceHeld` is unset and grants it when set; confirm replaying SR03 does not pay twice.

**Air.** For every row: the squadron resolves, the fit exists, the role matches, the aircraft appears in the cockpit, it can do the job, it recovers on the field the builder homed it on (Hobart Airport, Invercargill and Christchurch are `airfield_small_1` stand-ins for real airports; if the game refuses a Poseidon on a 48-capacity field, the fix is a larger field unit, not unlimited fuel).

**Logistics.** SR04: leave the box before 30 minutes and the stage never fires; hold it and it does; SR06 reads it.

**Outcomes.** SR11: lose Southern Endeavour in the same update she arrives — which trigger wins. TS12: the withdrawing group is neutral; sink one and the mission ends on the neutral rule. SR03: sink *Nan Hai 24* and the mission ends on the fatal.

**Branch.** TS10A and TS10B both offered after TS09; fly one, skip the other, and TS11 shows the other's reinforcement; fly both and TS11 shows neither; confirm both pay 60 and neither pays twice.
