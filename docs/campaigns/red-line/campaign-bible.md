# SEST RED LINE
## The Other Watch — campaign lore, canon and cast

**Written:** 26 September 2026; three side operations and four pages added 20 October 2026 · **Fictional campaign:** 3 November 2028 – 25 February 2029 (six core missions, two optional operations, one contingency, eight story pages) · **Game:** Sea Power, with the SEST collection

**Companions:** *SEST Southern Watch — The Northern Lifeline* (18 October – 28 November 2028) and *SEST Southern Reach — Tasman Shield* (6 December 2028 – 2 March 2029). Southern Watch's bible reserves the name for this: its "Recommended modes" table lists *Red Line* as the "optional opposing-force perspective". Its dispatch D4, *Return Passage*, whose map intro still begins "Red Line.", is the Russian side of the same weeks and stays where it is; this campaign is the Chinese side only.

This is a campaign that has been **statically built and never played**. Every character, company, incident and deployment is fiction. Equipment behaviour is whatever the winning mod file says.


## 24 October 2026 pacing revision — current playtest

Owner feedback: the missions were too timid and the opening two could be tedious. The earlier restraint-first design below is retained as a historical account; this section supersedes its mission goals, timings and blanket no-combat wording. Other campaigns' dates, named ships and outcomes remain intact. This revision has static validation; native gameplay acceptance is pending.

| Mission | Earlier window | Revised window | Current task |
|---|---:|---:|---|
| RL01 Trailing Contact | 70 min | 40 min | Carrier defence against two declared hostile missile craft, with attacks scheduled at minutes 8 and 12. ALPHA classification becomes an optional bonus; Fujian has a short station leg. |
| RL02 Routes They Can See | 95 min | 55 min | Final tanker approach with allocated airborne ASW support, GOLF's torpedo orders at minutes 10 and 18, and a separate missile flank at 14. No mandatory submarine kill/classification gate. |
| RL03 The Other Picture | 75 min | 45 min | Protect the KJ-500 with two allocated J-15s and any purchased CAP. A weapons-free F-35 pair enters at 8. Break the intercept and recover the radar aircraft; naval classification is a bonus. |
| RL04 The Order to Withdraw | 80 min | 50 min | Stop the escaping coaster while a Q-ship attacks Hulunhu. The supplier now has an explicit fatal protection objective. |
| RL05 Under the Convergence | 120 min | 60 min | One deliberately retained stealth mission: a shorter barrier crossing with HOTEL approaching during the playable window. |
| RL06 The Quiet Side | 95 min | 45 min | Protect the tender from a contractor Q-ship, cover the decoy station at minute 8, then rendezvous. Classification loses the stealth bonus; it no longer instantly ends the mission. |
| RLO1 Datum | 90 min | 45 min | Focused optional ASW search and return; its GOLF datum still benefits RL02. |
| RLO2 The Ships from the North | 80 min | 45 min | Reconnaissance under a real minute-8 F-2 interception. The protected ships and held cross-mission reveal remain unchanged. |
| RLC1 Pilot in the Water | 60 min | 35 min | The same four-minute pickup race, starting about 7 NM from the raft instead of 13. |

**Engagement rule:** declared hostile craft, the active intercepting fighters and the Q-ships may be engaged. Non-belligerent coalition observers in RL01/RL02/RL03/RL04 are on the neutral task force, so ordinary defensive settings do not automatically target them or feed their sensor picture to the unrelated attackers. Their protected-loss conditions remain. ALPHA is still the reserved Collins hull, GOLF remains Variant10 with the original loss flag, and no protected named coalition ship can be sunk by a successful mission. Kiwi 05 and HOTEL retain their original roles in the southern missions.

The revised combat exits also check the native `NoIncomingWeapons` condition alongside actual objectives or an elapsed-attack gate. This means **detected** incoming weapons, not proof that no undetected weapon exists. Timed attack orders are native `Attack=target,seconds,ammunition,shots`, documented in the exported official `MissionFileInformation.ini`; no performance or damage values are changed. Launches still require a surviving platform and usable weapons, and require PC observation. The supporting condition reference is the author's first-hand mission tests: https://steamcommunity.com/sharedfiles/filedetails/?id=3756786658 .


---

## 1. Premise

You play the officer both coalition campaigns only ever hear on a radio: the carrier group commander whose signal of 22 November Southern Watch intercepts before *Fujian's Shadow* ("a commander who would rather withdraw intact"), and whose signal of 25 February Southern Reach intercepts before *Approaches*. He is a professional with a carrier he cannot lose and an order that says the group will not fire first.

In the north he brings the group into the Banda approaches under a protection-and-evacuation mandate, puts a class on the Australian boat trailing his carrier, gets the enclave field's fuel into Biak the night before the coalition's relief window, and builds a picture of a convoy that other people will attack the next day. On the side, the enclave detachment's Y-9 puts a class on the boat nobody has claimed and names the Japanese escorts coming south to join that convoy, and the morning after the coalition's fleet action his screen races an Australian patrol vessel to a J-15 pilot in the water. In the first hours of the ceasefire he withdraws as ordered, and stops the one ship in his own company that wants the war back. In December he is sent south with Liaoning to take over the fisheries protection group; his submarine passes a Poseidon barrier unclassified, and his frigate plays the loud one while the tender meets her boat off Fiordland.

Every mission is won by restraint, identification, escort or evasion. There is nearly always a coalition aircraft overhead, recording.

## 2. Canon rules

The two coalition campaigns are canon. This one sits in their gaps and cannot move them, whatever the red player does.

| Rule | How it is kept |
|---|---|
| The canonical outcome of each mission is its victory | A Task Force defeat is replayed, so the victory is what happened. Every victory is written to be consistent with Southern Watch and Southern Reach |
| The coalition's named units cannot be lost here | Any coalition unit either campaign names or depends on is a `spare` objective with a fatal entry: the Collins-class boat, every Poseidon and the Triton, Kiwi 05, Mogami, Maya and the Common Sea convoy, and the units the wider forces added on 28 September - RL01's Wedgetail, RL03's Growler and RL05's Virginia-class boat HOTEL, and from 30 September RL03's Rivet Joint. From 20 October the same holds for Mogami and Maya in *The Ships from the North* and the Australian patrol vessel in *Pilot in the Water*, and for GOLF in *Datum*, who must be there for the next two northern missions. Sink one and the mission ends. Fighters that may fire - RL03's F-35As, RLO2's JASDF F-2As - are not spared: if one fires, the reply is against the aircraft that fired |
| No hull a coalition mission can own or lose before her last Red Line appearance is named | ALPHA is `ran_ssg_collins` Variant3 (Waller), the one Collins hull no other mission places and no roster sells; she was Variant6 until 20 October 2026, when that hull had become Southern Reach's Rankin attachment. GOLF is `usn_ssn_virginia_2027` Variant10, from the same day: Variant1 is the hull *Fujian's Shadow* places as "US submarine support" and can lose on the 23rd, four days before GOLF's last appearance. The patrol vessel in *Pilot in the Water* is `ran_opv_arafura` Variant4 (Gippsland), the one Arafura hull no mission places and no roster sells. Mogami and Maya are the hulls *Common Sea* places on the 20th, after both their Red Line appearances. The text calls each by her class or her role, and neither the briefing's photographs nor the Situation window shows ALPHA or GOLF (`recognise=False`, `orbat=False`): what they are is the task. The Poseidons carry no callsign except Kiwi 05, which Southern Reach already flies. The rule is held against every campaign the pack ships: their rosters, allied reserve included, and their player-side placements. No exception is left: the Open Allocation twins, which sold their commander's whole allied fleet from the first window and so JS Maya's hull (`jmsdf_ddg_maya` Variant1), left the pack on 21 October 2026, and the standard campaigns that sell that fleet from the same day sell it through the reserve's pack-wide named-hull filter, Maya Variant2 alone. The build checks the rule, and pins any Red Line hull a twin would still add (none today) so that one is a decision (`test_build_pack.RedLineSideOperations`) |
| Nothing after 23 November relies on Fujian, or on her screen's boat | *Fujian's Shadow* can sink her (`SW11FujianSunk`). The ceasefire mission places Liaoning, whom Southern Reach keeps until February. *Fujian's Shadow* also places a Type 093B in her screen as ROMEO, and can sink her too; Southern Reach's ROMEO is a Type 093B again. Hull 419 is the boat Southern Reach calls ROMEO, and nothing here says whether she is the northern one |
| A separate save | A third campaign cannot read the others' variables. The two it reads are its own: `RL02GolfSunk` keeps GOLF out of the ceasefire mission, and `RLO1GolfDatum` (*Datum*) puts her on *Routes They Can See*'s plot for fifteen minutes. *The Ships from the North* wrote a third, `RLO2EscortsNamed`, for *The Other Picture* until 21 October 2026; it is held until test card 7.4 is answered |
| No page states the other side's outcomes | The 22 November page stops before the twenty-third ("in the group's report, not on this page"); the last page stops before 26 February ("the other side's account"). The 6 November request says nothing of the answer, and the 24 November air log, the morning after *Fujian's Shadow*, says nothing of that day: the J-15 is Liaoning's and came down with a fire warning. A premise may be said, an outcome not: the 17 November page says Japanese aircraft from Langgur engaged northern-element ships south of Seram that morning (Southern Watch's *Viper Zero*), not how it ended, and *Pilot in the Water*'s brief says nothing that would mean the group had never fired, since the reply of the 22nd was to enforce the closure on the 23rd. No page says how a side operation ended, because the campaign shows each page whether or not the player flew it |
| The ceasefire | Takes effect at 0000 on 27 November (Southern Watch's C2, sitrep and last passage). The group acknowledges its order at 2304 on the 26th. *The Order to Withdraw* is at 0310 on the 27th; the first coalition convoy sails at first light on the 28th |
| Which group complied | Southern Watch says not every Chinese group acknowledged, and its closing page has one group, two hundred miles behind the convoy, that "complied with its withdrawal order" and another that "spent the afternoon deciding". *The First Ship Through* places those two in its Arafura box: a Luda and a Type 071 withdrawing (the northern element's kind of ship, which the tasking says is not this commander's) and an unacknowledged 054A. This group acknowledged at 2304 on the 26th and is neither of them: *The Order to Withdraw* takes it north-west out of the Banda Sea, 370 miles from that box, and nothing here goes near it |
| Voice | Chinese side throughout, restrained and professional: no gloating, no caricature, no claim about the coalition's motives. The Russian detachment appears only as other people's business ("under its own arrangement, not this headquarters'") |
| Names | The commander is "the group commander" in every page and briefing, and no person is named in any page or briefing: Kiwi 05 is Squadron Leader Rewi's aircraft in Southern Reach, and here it is its callsign. No real officer or command is named beyond "Fleet headquarters". Real ships appear only where the coalition campaigns already put them (Fujian, Liaoning and her replenishment ship Hulunhu, Mogami, Maya); the group's boats go by hull numbers, never by name |

## 3. Timeline against the two coalition campaigns

| Date | Southern Watch / Southern Reach | Red Line |
|---|---|---|
| 2 Nov | SW05 *Weapons Free*: a Sovremenny of the northern element fires on a protected convoy and is answered | |
| 3 Nov | | **Prologue** — the tasking signal (022200Z): enter the Molucca Sea, take station in the Banda approaches, the group will not fire first |
| 5 Nov | | **RL01 Trailing Contact**, Molucca Sea, 0710 |
| 6–7 Nov | SW06 *Blind Horizon*; sitrep 3: a Chinese task group has arrived and demanded the patrols suspend | **Page** — the request (060100Z): the group asks the coalition escort force to suspend its patrols, as tasked |
| 10 Nov | The Russian detachment's auxiliary is torpedoed (D4: "eleven days ago" on the 21st); SW O4 *Weather Alternate* | |
| 11 Nov | | **Page** — Fleet headquarters' intelligence summary: the boat is unclaimed and designated GOLF. **RLO1 Datum** (optional), north of Biak, 0640: the enclave's Y-9 puts a class on her |
| 12 Nov | The 12 November INTSUM: the Russian detachment's supply routes into the enclave are seen | **RL02 Routes They Can See**, Biak approaches, 2310: the Chinese detachment on the same field is supplied the same way |
| 13 Nov | SW08 *The Open Door*, 0450 | |
| 17 Nov | SW O9 *Viper Zero* (optional), 0650: four JASDF F-2As from Langgur, with ASM-3, go for a PLAN 054A and 056A escorting Changbai Shan south of Seram, which are closing on Hyuga and Asahi as they come south out of the Manipa Strait | **Page** — Fleet headquarters (171400Z): Japanese aircraft engaged northern-element ships south of Seram that morning, not this group's; two Japanese escorts passed the Talaud Islands southbound on the 16th; names required |
| 18 Nov | | **RLO2 The Ships from the North** (optional), Ceram Sea, 0920: the Y-9 and a J-15 pair name Mogami and Maya |
| 19 Nov | | **RL03 The Other Picture**, eastern Banda Sea, 1030 |
| 20 Nov | SW10 *Common Sea*: the same convoy and Japanese escort | |
| 21 Nov | D4 *Return Passage*; sitrep 5: the carrier group has moved south | |
| 22 Nov | 05b: the group commander's signal, intercepted (0110Z) | **Page** — the signal as sent, the reply (ENFORCE), and the order of the 26th |
| 23 Nov | SW11 *Fujian's Shadow* | |
| 24 Nov | | **Page** — the air operations log: a J-15 off Liaoning down with a fire warning at 0452. **RLC1 Pilot in the Water** (contingency), Banda Sea, 0610: the screen races an Australian patrol vessel to the pilot |
| 25 Nov | SW C2 *Broken Wake*: "the ceasefire is two days off" | |
| 26 Nov | | Ceasefire order 261100Z; acknowledged 2304 local |
| 27 Nov | 0000 ceasefire; sitrep: not every group has acknowledged; Santos's log, 1800 | **RL04 The Order to Withdraw**, Banda Sea, 0310 |
| 28 Nov | SW12 *The First Ship Through*, Arafura, 0620; closing page | |
| 6 Dec | SR01 *Southern Departure*: "the northern ceasefire is nine days old" | |
| 21 Dec | SR06: Derwent Spirit torpedoed south of the Auckland Islands | |
| 17 Dec | SR's Austral Meridian intercept: "the carrier" assessed as the group's reinforcement, transiting | Liaoning, two frigates and a corvette sail from the Java Sea. Southern Reach's 25 February signal counts the air wing's "seventy days" from here |
| 22 Dec | | **Page** — new orders, received five days out: take over the protection group, with its destroyer as flagship; the boat goes ahead and is not to be reported |
| 23 Dec | SR sitrep: action against the submarine that fired is authorised; a carrier movement from the Java Sea towards the south-east | |
| 24 Dec | SR07 *Beneath the South*: the hunt for VICTOR at 57 South | |
| 27 Dec | | **RL05 Under the Convergence**, south of the Bight, 0430 |
| 30 Dec | Liaoning arrives "with two frigates and a corvette" (1 January sitrep) | |
| 2–5 Jan | SR09 *Cold Route*: ROMEO, a Type 093B, ahead of the convoy, the first in the south; the 5 January INTSUM first lists one with the protection group | |
| 19 Jan | | **RL06 The Quiet Side**, Fiordland approaches, 0520 |
| 22 Jan | TS01 *Home Waters*: the tender found among the Milford cruise ships; TANGO reported | |
| 25–28 Jan | TS02 *Cook Strait*; Rewi's cable; TS03, the rendezvous east of New Zealand | |
| 25 Feb | 07b: the group commander's signal, intercepted (0140Z) | **Epilogue** — the signal as sent |
| 26 Feb | TS11 *Approaches* | |

No Red Line mission falls on a day either coalition campaign flies, their optionals and dispatches included (the build checks it since 20 October 2026). Sulu Line may share a day: it is the other end of the archipelago.

## 4. The missions

| | Date · place · clock | The task | What ends it |
|---|---|---|---|
| **RL01 Trailing Contact** | 5 Nov · Molucca Sea · 70 min · `patrol` | Classify ALPHA, the Collins-class boat twelve miles astern of Fujian, then take Fujian to her morning station, 22 miles down the track. Ships start at weapons Hold | The boat, the Poseidon, the Triton or the Wedgetail destroyed; Fujian lost |
| **RL02 Routes They Can See** | 12 Nov · Biak approaches · 95 min · `escort` | Bring MT Hai Yang 7 into Biak's northern roads before the relief window. GOLF, an unclaimed submarine, is weapons Free on the route | Hai Yang 7 lost; the Poseidon destroyed. Sinking GOLF is allowed and remembered |
| **RL03 The Other Picture** | 19 Nov · eastern Banda Sea · 75 min · `recon` | Classify Coral Pioneer, Mogami and Maya from outside their reach, then take the frigate back north-west. Two F-35s cover the convoy at weapons Tight | Any convoy or Japanese hull lost, or the Growler or the Rivet Joint, which never fire, downed |
| **RL04 The Order to Withdraw** | 27 Nov · Banda Sea · 80 min · `escort` | Liaoning and the replenishment ship across the line north-west, and MV Meridian Harmony, the armed coaster in company, stopped before she clears the screen. Repair only, no rearm | The Poseidon destroyed; Liaoning lost; the coaster reaching the edge of the screen. Sinking GOLF, if she is there, costs 40 points and does not end it: she exists only if RL02 left her afloat, and no trigger that ends a mission names a unit that may not have spawned |
| **RL05 Under the Convergence** | 27 Dec · south of the Bight · 120 min · `patrol` · detached | Take Hull 419, the Type 093B, through a Poseidon barrier to the carrier's forward box | The boat classified by the coalition - by the aircraft or by HOTEL, the Virginia crossing the line; the Poseidon, the Triton or HOTEL destroyed; the boat lost |
| **RL06 The Quiet Side** | 19 Jan · Fiordland approaches · 95 min · `patrol` | Hold the decoy station to the half hour, then bring MV Austral Compliance and Hull 334, the Type 039C, to the holding position | Hull 334 classified by the coalition; Kiwi 05 destroyed |

**The side operations** (20 October 2026; `docs/campaigns/campaign-upgrade-plan.md` section 4.2, step RL-1). The two optionals are flown by a fixed force the mission supplies - the enclave detachment's Y-9 *Sea Ear 31*, and on the 18th two J-15s the carrier air wing has released to the field - so nothing the player owns sails, and each closes when the next core mission is complete. The contingency is the screen's own detachment, as Southern Watch's *After the Wake* is.

| | Date · place · clock | The task | What ends it | Read by |
|---|---|---|---|---|
| **RLO1 Datum** | 11 Nov · north of Biak · 90 min · `patrol` · optional | Put a class on GOLF from the Y-9's buoys the morning after she hit the Russian auxiliary, then bring the aircraft back over the enclave field. Weapons Hold | GOLF or the Poseidon destroyed (she has two more missions to be in); the Y-9 lost | RL02: GOLF on the plot as a datum for fifteen minutes (`RLO1GolfDatum`), not a class: classifying her is still RL02's own objective |
| **RLO2 The Ships from the North** | 18 Nov · Ceram Sea · 80 min · `recon` · optional | Classify JS Mogami and JS Maya crossing for the Kai Islands, then take the Y-9 back east. A JASDF F-2A pair from Langgur comes up at weapons Tight; the J-15s are Tight too | Mogami or Maya hit; the Y-9 lost | nothing for now (held, owner, 21 Oct 2026, until test card 7.4 is answered). It wrote `RLO2EscortsNamed` until then, and RL03 started with both escorts classified; that rests on a reveal at Classify satisfying RL03's classification stage, which nothing has shown. Southern Reach's *Chatham Watch* and Sulu Line's *The Okean* have the same shape on optional objectives and are the proof (Southern Reach card 3.10, Sulu Line card 7.1) |
| **RLC1 Pilot in the Water** | 24 Nov · Banda Sea · 60 min · `patrol` · contingency | A J-15 off Liaoning is down with a fire warning; race an Australian patrol vessel (fourteen miles off him at about twenty knots, at the mile at about minute 39) to the pilot: the lead ship stopped within three cables of his raft for four minutes, and he is aboard. A detachment; no purchase, repair or rearm | The patrol vessel within a mile of him first; the patrol vessel or the Poseidon destroyed | nothing: it is a race, not a promise |

Points 100, 120, 140, 120, 80, 0; the side operations 60, 70 and 30. Budgets Supported 1,250 / Standard 1,000 / Veteran 850, cap 1,500 (1,250 on Veteran). The roster sells the 054A, the Luda and the Sovremenny (north), the 056A (south), the Z-9C, the Y-9 and KJ-500 (Recon rows in RL02 and RL03), and the J-15 and J-15D (a CAP row in RL03); carriers, submarines, the Z-18F and *The Order to Withdraw*'s replenishment ship are allocated per mission and never sold. *(21 Oct 2026: the group's other Type 901 and 903A hulls are on sale from the first force allocation, the PLAN's own ships at the same-nation discount - the owner's decision on retiring the Open Allocation version, which sold them. From the same window every force allocation offers the whole roster, north and south alike, as that version did: a 056A can be bought for the north, a Sovremenny for the south, and the aircraft before their rows - and at *The Quiet Side*, which tasks only the ship's flight, after the last of them: its window says a fixed-wing aircraft allocated there will not fly. Build notes, "21 October: the allied fleet in the standard campaigns".)*

## 5. Story pages

The first four are signals on teleprinter stock, labelled from this side of the table: an OUTGOING strap on the group's own signals, and a COMMANDER'S NOTE or FILE NOTE under each instead of an analyst's. The four added on 20 October 2026 keep to that, in three forms: two signals, an intelligence summary marked SECRET // CARRIER TASK GROUP ONLY (not the coalition's RELEASABLE TO COALITION PARTNERS), and an air operations log KEPT BY the air operations officer, with the commander's note under it. A role signs each, never a name. There is no press page: this side's newspapers would be real state outlets. Each new page hangs before a side operation, and the campaign shows it whether or not the player flies that operation, so none says how one ended.

| Page | Before | What it is |
|---|---|---|
| *Protection and Evacuation*, 3 November | prologue | Fleet headquarters' tasking. Paragraph 2 disowns the northern element's shot of the 2nd and says the other side will not draw the distinction; paragraph 3 is the order. Note: "Paragraph 3 is the order. Paragraph 2 is the reason it will be hard." |
| *The request*, 6 November | RLO1 | OUTGOING: the group asks the coalition escort force to suspend its patrols in the approaches while it is on station, "so that neither force mistakes the other's purpose", as the tasking's paragraph 2 ordered. Southern Watch's 12 November summary has the demand. The note leaves the answer to the tasking: "The tasking says what the answer will be. Paragraph 3 is the part of this one I meant." |
| *The unclaimed boat*, 11 November | RLO1 | Fleet headquarters' intelligence summary: the Russian auxiliary hit by one torpedo at 2340 on the 10th, the Russian detachment's business; no Chinese unit fired and no state has claimed it; the boat is GOLF; the fuel run goes through the same water on the 12th; a class is not a claim, and not authority to attack |
| *Ships from the north*, 17 November | RLO2 | Fleet headquarters: two Japanese escorts passed the Talaud Islands southbound on the 16th for the convoy forming at Kai; names required; the Y-9 and a J-15 pair allocated; Japanese aircraft from Langgur engaged northern-element ships south of Seram that morning, "not this group's" (*Viper Zero*'s premise, not its outcome); "the group is not at war with Japan"; what is done with the picture is not the group's decision |
| *Air operations log*, 24 November | RLC1 | The morning watch: Liaoning's dawn patrol launched at 0415, the fire warning at 0447, the ejection at 0452, the beacon at 0455, the Australian patrol vessel turning for it at 0540. Note: "He comes home in a Chinese ship, and nothing is fired to make it so." It says nothing of the 23rd |
| *Guidance requested*, 22 November | RL04 | Southern Watch's 05b as sent: every sentence the coalition decrypted, word for word, with the two ends the intercept missed. Then the reply (ENFORCE THE CLOSURE ON THE TWENTY-THIRD) and the order of the 26th (CEASEFIRE TAKES EFFECT 0000 ON 27 NOVEMBER. WITHDRAW NORTH-WEST). It says nothing of the twenty-third |
| *New orders*, 22 December | RL05 | Received five days out of the Java Sea. Take over the protection group, whose destroyer is the flagship "not to be lost" of the 25 February signal; Liaoning, two frigates and a corvette continue south-east; the submarine goes ahead and is not to be reported; the contractor is Austral Meridian Services ("you have met its parent"); the coaster of the 21st was not a Chinese shot. Paragraph 5 is November's paragraph 3 |
| *The last signal*, 25 February | epilogue | Southern Reach's 07b as sent, ending "I would rather be told not to." The note leaves the reply and the twenty-sixth to the other side |

## 6. Cast (all fictional)

| Who | Role | Where |
|---|---|---|
| The group commander — the player | Commands the carrier group in the north and the protection group in the south | Never named in prose. The commander screen's default name, *Cao Mingyuan*, is built from the game's own Chinese name pool and was checked against naval officers before use (build notes) |
| Fleet headquarters | Signs every briefing and four of the pages, one of them its intelligence summary | "It will not fire first" |
| The air operations officer | Keeps the air operations log of 24 November | Before RLC1 |
| Contact ALPHA | A Collins-class boat trailing Fujian | RL01 |
| MT Hai Yang 7 | The chartered tanker that fuels the enclave field | RL02, RL04 |
| The enclave field (PLAAF detachment) | Biak's airfield, where the J-15s and the KJ-500 recover | RLO1, RL02, RLO2, RL03 |
| Sea Ear 31 | The enclave detachment's Y-9, which puts a class on GOLF and names the ships from the north | RLO1, RLO2 |
| Flying Shark 81 and 82 | J-15s the carrier air wing released to the enclave field, the Y-9's escort | RLO2 |
| Flying Shark 85 | A J-15 off Liaoning, down with a fire warning on the 24th; her pilot is never named | RLC1 |
| Contact GOLF | An unclaimed submarine, the one assessed to have torpedoed the Russian auxiliary | RLO1 (spared), RL02, RL04 unless sunk |
| JS Mogami and JS Maya | The Japanese escorts coming south for the Common Sea convoy; spared | RLO2, RL03 |
| A JASDF F-2A pair | Out of Langgur, seeing the Y-9 off at weapons Tight; not spared, as RL03's F-35As are not | RLO2 |
| An Australian patrol vessel | An Arafura-class OPV in the southern approaches, turned for the pilot's beacon; spared | RLC1 |
| Contact HOTEL | The US Navy Virginia-class boat on the Western Australia rotation (Southern Reach TS08), crossing the passage line; spared | RL05 |
| Dragon Eye 05 | The KJ-500 that builds the picture | RL03 |
| A Rivet Joint | A USAF RC-135V/W out of Tindal, listening from a track south of the box; spared with the Growler | RL03 |
| MV Meridian Harmony | A Meridian armed coaster that joined the group on the 24th for protection | RL04 |
| Hull 419 | The Type 093B Southern Reach calls ROMEO | RL05 |
| Hull 334 and MV Austral Compliance | The Type 039C the coalition will call TANGO, and the AMS tender that serves her | RL06 |
| Kiwi 05 | Squadron Leader Rewi's RNZAF Poseidon | RL06 |
