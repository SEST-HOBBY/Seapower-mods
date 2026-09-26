# Southern Reach — first play test

Nothing in this campaign has been run in the game. Everything below is a claim
the build makes about files it wrote; this card is the order to falsify them
in, riskiest first, and what "wrong" looks like for each. It assumes the
Southern Watch card (`../southern-watch/test-card.md`) has been run once, so
the questions that campaign already answers — does a mod-supplied campaign
appear, does its art load, does Task Force Mode buy and rearm — are not
repeated here except where this campaign does something new.

Report back with the step number and what you saw. A step that fails stops
that column, not the whole card.

## Install

Same procedure as Southern Watch (`../southern-watch/install-alignment.md`).
The pack is the same `SEST_Campaign` folder; both campaigns are in it. After
the sync the Mod Manager should show the two RNZAF bases' names in the land
unit list (Ohakea, Auckland/Whenuapai) — they are new files in
`SEST_RAAF_Bases`, and if they are missing nothing New Zealand will place.

The campaign ships twice: as `campaigns/sest-southern-reach/` and again as
`missions/Southern Reach/` and `missions/Tasman Shield/` for the mission
browser.

## 1 — does it load

| # | Do | Expect | If not |
|---|---|---|---|
| 1.1 | Campaign list | **SOUTHERN REACH** beside SOUTHERN WATCH, 44 entries (25 missions, 19 story pages) | Only one campaign listed = the second `campaigns/` folder is not scanned; go to 1.3 |
| 1.2 | Start it | The 6 December press page, then SOUTHERN DEPARTURE | Note which it stops on |
| 1.3 | Mission browser | Two new folders, **Southern Reach** (12) and **Tasman Shield** (13) | A missing folder names a broken `_info.ini` |
| 1.4 | Load one mission from each water | **SR01 Southern Departure** (Storm Bay), **SR10 Southern Line** (60°S), **TS02 Cook Strait**, **TS10A Northern Priority** (the Hauraki Gulf) | These are the four most different charts; a unit that fails to appear names its mod |

## 1A — the coastline (new, and the biggest single risk)

Every position in this campaign was proved against a Natural Earth
coastline, not the game's. Cook Strait is 12 NM wide; the margins are 2 NM
for a ship, half a mile for a waypoint.

| # | Do | Expect | If not |
|---|---|---|---|
| 1A.1 | Load **TS02 Cook Strait**, pause at T+0, look at every hull | All afloat: the cable ship 9 NM off Oteranga, the detachment east of it, two ferries in the strait, a fishing boat in Cloudy Bay, a tanker off Cape Campbell | A hull ashore: say which. The extract's margin is wrong there and the rule needs widening |
| 1A.2 | Run TS02 at 8x for ten minutes, watch the ferries | They cross Wellington–Picton without grounding | A ferry that beaches names a waypoint the extract passed and the game does not |
| 1A.3 | Load **SR04 Macquarie Passage** | Supply and Coral Pioneer in Buckles Bay 1 NM off the isthmus; the station ashore on it; the Akula's route round the north tip stays wet | The `coastal=True` rule (any distance, per hull) is the one being tested |
| 1A.4 | Load **TS06 Bass Strait** | Three platforms *in the water* 30–40 NM north-east of the force, not on the Gippsland coast | `snap="sea"` on a land unit not honoured |
| 1A.5 | Load **TS10A** and **TS10B** | The Hauraki Gulf and Gulf St Vincent traffic all afloat; the arrival boxes (Rangitoto Channel approach, Outer Harbor approach) at sea | An approach box drawn on land = the 1 NM trigger margin is too thin there |
| 1A.6 | Load **SR08 The Gateway** | The Lyttelton approach box 2 NM off the Heads, on water | Same |

## 1B — the art

Same three keys as Southern Watch, new content. The forms new to this campaign
are the signal, the log and the INTSUM tile (`bkg_tile_message.png`).

| # | Do | Expect | If not |
|---|---|---|---|
| 1B.1 | Campaign list backdrop | A dark chart 29–66°S, 116–180°E, 23 marks coded SR01…TS12 joined in campaign order, two small open circles for the optionals (TS10A off the Hauraki Gulf top-right, TS10B off Adelaide), the compass rose bottom-right, SOUTHERN REACH bottom-left | |
| 1B.2 | Step through the two story pages before SR02 | A ship's log on ruled paper (Coral Pioneer, 6 December), then a cable on teleprinter stock (Wellington's allocation, 8 December) | Either blank = that form's tile or image path is not read |
| 1B.3 | The page before SR10 | A typed INTSUM under a SECRET // RELEASABLE TO COALITION PARTNERS marking (The command element); organisation, reference/date and subject occupy separate lines, with no clipping | |
| 1B.4 | Any Tasman Shield mission card | The TASMAN SHIELD series label and date line, the code (TS01…) in the corner, own force in blue, the objective ring | A card still saying SOUTHERN REACH on a Tasman mission = the series label is not per mission |
| 1B.5 | The briefing chart for **SR10 Southern Line** | The ice-edge box at 60°S with a locator inset of the whole southern theatre, and *no* Hobart Airport on the chart (it is 1,000 NM away) | Hobart on the chart = `focus_nm` not applied |
| 1B.6 | The briefing chart for **TS02 Cook Strait** | Both islands, Ohakea marked, the cable-route and Wellington labels legible | Overlapping labels are a known cosmetic issue; say if they are unreadable |

## 1C — flags and traffic (fixed after the first install)

| # | Do | Expect | If not |
|---|---|---|---|
| 1C.1 | Any Tasman Shield mission with Kiwi 05, or an RNZAF base (TS02, TS03, TS10A) | The New Zealand flag on the Poseidon's unit panel and on Ohakea / Whenuapai | Still no flag = the game reads the nation from somewhere this build did not fix; note which unit |
| 1C.2 | SR08 or TS01, the civil airfield (Christchurch, Invercargill) | New Zealand flag | Same |
| 1C.3 | Any Southern Reach mission with an airliner, run at 8x for ten minutes | The airliner flies off along its route (Sydney, Auckland, Hobart...) and does not circle | An airliner orbiting its start point = its route did not load; name the mission |
| 1C.4 | A loose mission you play often (Northern Front III, the chapter missions) | Civil aircraft carry on past where they used to turn and orbit | One still circling: name the mission and the aircraft |

## 2 — Task Force Mode (the new keys)

| # | Do | Expect | If not |
|---|---|---|---|
| 2.1 | Before SR01 | Builder open: Anzac (240), Hobart (480), Seahawk (20) on sale, nothing else | |
| 2.2 | SR02 Silent Track | No builder, no deployment: Collins and Kiwi 05 only; the mission launches as authored | Anything of the owned force on the plot = blank generation not honoured |
| 2.3 | Before SR06, having **missed** the SR04 window | No rearm offered | Rearm offered = `TaskForceModeRearmByVariableAND=SR04ServiceHeld,IsTrue` not read |
| 2.4 | Before SR06, having **held** it | Rearm offered | |
| 2.5 | Before TS02 Cook Strait | A deployment screen: choose which hulls sail | No choice = `TaskForceModeDeploymentOptions` unread; the whole force sails into the strait |
| 2.6 | Before TS07 Southern Air Bridge | Airbase preparation at Williamtown: two ready slots, one in progress | Absent = `TaskForceModeAirbasePrep*` unread |
| 2.7 | Before TS08 | Repair only; no purchase, no rearm | |
| 2.8 | After TS09 | Both TS10A and TS10B offered; play one; after TS11 both are gone | Both still offered after TS11 = `ExpiresAfterMissionComplete=41` points at the wrong entry |
| 2.9 | Before TS12 | Buy and repair, no rearm; after TS12 the campaign ends (`FinalMission`) | |
| 2.10 | Any Recon row with a Poseidon bought | Kiwi 05's fields (Ohakea, Whenuapai, Invercargill, Christchurch) accept a RAAF Poseidon for recovery | A Poseidon that cannot recover in New Zealand = the range check accepted a field the game refuses |

## 3 — the consequences

Each row is a variable one mission writes and a later one reads. Play the
writer both ways where the card says so.

| # | Write | Then read | Expect |
|---|---|---|---|
| 3.1 | SR01: classify *Nan Hai 27* | SR05 | The collector is a classified contact from the first minute, with Mercer's intel line |
| 3.2 | SR02: classify VICTOR | SR07 | The Akula is classified at start |
| 3.3 | SR03: win (Nan Hai 24 boarded) | TS12 | *Nan Hai 27* is **identified** at start as the spoiler's spotter |
| 3.4 | SR04: hold the window / miss it | SR06 | Rearm offered / not (2.3–2.4) |
| 3.5 | SR05: classify both escorts | SR10 | The frigate and corvette are identified at start |
| 3.6 | SR07: sink VICTOR / let her go | SR10 | No Akula in the line / an Akula in the line |
| 3.7 | SR08: classify the corvette | TS02 | The 056A from Cape Campbell is classified at start |
| 3.8 | SR09: lose Derwent Spirit / keep her; win / lose | SR11 | No tanker in the convoy / a tanker; rearm offered only after a win |
| 3.9 | SR12: name the network | TS01, TS04 | The collector (TS01) and the 054A (TS04) classified at start |
| 3.10 | TS01, TS02, TS03: classify the tender, TANGO, the tender again | TS03, TS05 | Both revealed at the rendezvous; the survey ship revealed under the Tasman |
| 3.11 | TS05: sink ROMEO / miss her | TS09, TS12 | No 093B under either convoy / a 093B under both |
| 3.12 | TS08: sink SIERRA-TWO / miss her | TS09 | No Yasen in the convoy action / a Yasen |
| 3.13 | TS10A won / TS10B won / neither played | TS11 | No corvette-and-collector from the north / no second frigate from the south / both present |
| 3.14 | TS11: sink Liaoning / leave her | TS12 | No J-15 pair on the convoy / a pair |

## 4 — the shapes that have not been played

| # | Mission | Do | Expect | If not |
|---|---|---|---|---|
| 4.1 | SR03 Search Datum | Classify *Nan Hai 24*, put your flagship within 3 NM of her | Victory; sinking her fails the mission | The `at_unit` box does not follow her / the fatal on a red hull does not fire |
| 4.2 | SR04 Macquarie Passage | Keep both ships inside 5 NM until T+30, then north | The intel at T+30, then the line | The stage fires early (units merely inside at any time) or never |
| 4.3 | TS02 Cook Strait | Same shape at T+25 with the cable ship | | |
| 4.4 | TS03 Chatham Watch | Approach the surfaced TANGO | She dives when she detects the force | She sits on the surface: report it, the mission is then too easy |
| 4.5 | TS04 Tasman Crossing | Two groups abeam, one box ahead | 3 of 4 into the box wins; the strike goes for the north-western group | Only one group can reach = the abeam geometry did not survive the game's speeds |
| 4.6 | TS07 Southern Air Bridge | Route Relief 21 (an A330 on the player's side) to the box off the Heads | Victory when the airliner arrives; losing it fails | A blue civil airliner cannot be given the route, or the arrival trigger ignores aircraft |
| 4.7 | TS12 Southern Cross | Leave the withdrawing frigate alone, fight the spoiler | The ceasefire objective holds; the neutral-loss rule ends the mission if the player fires on the withdrawing group | The player's weapons-free escorts engage the neutral frigate on their own |
| 4.8 | SR10 Southern Line | Everything red starts Tight | Nothing fires until the player does | The group opens fire unprovoked = the Tight state is not honoured on spawn |
| 4.9 | SR06 Broken Supply Line | Fly it once with empty magazines (2.3) | Winnable by keeping the coaster moving and the Seahawk over the boat | If it is not, the rearm consequence is too hard and the bible's §4 needs a softer rule |
| 4.10 | SR04 Macquarie Passage | Fire an escort's NSM or ESSM, then bring her inside half a mile of Supply at 12 kn or less during the window | The round comes back from Supply | Nothing crosses: report it with Southern Watch 6E, same system |

## 5 — the numbers to bring back

Whatever else, bring back for each mission played: the mission number, the
result (win / lose / timeout), the objective ledger as shown, the points
awarded, and any unit that was ashore, missing or misnamed. Those are what the
next build pass is made of.
