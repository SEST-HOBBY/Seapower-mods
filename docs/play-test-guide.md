# Play-test guide — all four campaigns

A plain checklist for testing the SEST campaigns in the game. It covers what
matters most, in the order to test it. Each campaign also has a detailed test
card (`docs/campaigns/<campaign>/test-card.md`) with every check numbered; this
guide uses the same numbers in brackets where they apply, so a report can point
at either.

Nothing in Sulu Line has been run in the game yet. The other three have been
loaded and partly played; their open questions are listed below.

---

## 0. Before you start (5 minutes)

1. Game closed. In the repo folder on the PC:
   `.\tools\sync-sest.ps1` — it must end with **IN LINE** and the current
   commit number.
2. Start Sea Power → **Mod Manager**: *SEST Integration Pack* is at the top
   and ticked. If it offers to move or fix dependencies, say **no**.
3. **SEST's runtime plugins.** After the main menu has shown, open
   `%USERPROFILE%\AppData\LocalLow\Triassic Games\Sea Power\Player.log`
   and find the `[SEST Runtime]` lines. Lines containing
   `correction installed` (the Tomahawk MST terrain clearance, the
   task-force debrief's lost-ship rows and the towed-sonar guard) mean SEST
   Runtime Fixes 1.5.0 is on: on Sea Power 0.8.7 that is expected. `inactive:
   uninspected native assembly` means the game has updated past the build
   SEST checked, and all of them are off: the game's own behaviour applies,
   so do not report the MST over mountains or the debrief as SEST faults
   then. `inactive: owning pack is not enabled` means the pack is not
   ticked (step 2). `F11 campaign totals inactive: uninspected Combat Cost
   Tracker` means SEST's F11 cost windows are off with the tracker you
   have: say so, with the tracker's version. With Contact Log subscribed,
   a `[SEST UI Follow-up] 1.4.2 input fix installed` line means the UI
   follow-up is on too; `[SEST UI Follow-up] inactive; original behavior
   retained` means it is off. With UI Follow-up on, Quick Load is Ctrl+F9.
   Say which lines you saw, and the game's build.
4. **Options:** note the two weapons settings under Left Shift+O —
   "Ships on Weapons Tight engage hostile aircraft" and "Ships use anti-ship
   missiles on Weapons Free". Leave them at their defaults and say what they
   were in your report.
5. Keep a note open. For every mission you play, write down:
   - the mission name and result (won / lost / ran out of time);
   - the objective list as it shows at the end, and the points awarded;
   - anything ashore, missing, unnamed or showing MISSING TEXT;
   - for a problem: what you did, what happened, and a screenshot.

**Save often.** Several checks need a save, a quit to desktop and a reload.

---

## 1. Quick check: everything loads (15 minutes)

Do this first. If something here fails, stop and report it; the deeper checks
depend on it.

| Do | Expect | If not |
|---|---|---|
| Open **Campaigns** | Four entries: Southern Watch, Southern Reach - Tasman Shield, Red Line - The Other Watch, Sulu Line - The Island Road. No *Open Allocation* version: they were retired on 21 Oct 2026 | Name the ones missing, or any Open Allocation entry still listed |
| Look at each campaign's background | A dark chart with numbered mission marks, the campaign name bottom-left | Blank or a stock picture: say which campaign |
| Mission browser (single missions) | Folders: Southern Watch, Southern Watch - Dispatches, Southern Reach, Tasman Shield, Red Line, Sulu Line | A missing folder |
| Load one mission from each folder from the browser: **Southern Watch 01 - White Water**, **Southern Reach 04 - Macquarie Passage**, **Red Line 01 - Trailing Contact**, **Sulu Line 01 - The Island Road** | Every ship and aircraft appears, flags shown, no ship on land | A missing or grounded unit: its name and the mission |
| Open a briefing in each | Photo banner at the top, a chart in the right-hand pane, photos of your forces and the opposition at the end | Blank pane or no photos |
| Read the line under the banner | A quotation in italics with its speaker; a different one in each mission of the campaign | Missing, or the same line twice in one campaign |
| Watch the loading screen a few times | A SEST photograph behind it, and a panel headed QUOTATION with one of the 26 quotations and its speaker | A stock picture, a gameplay tip, or text in Chinese |
| Load **SEST Banda - Tigers over Papua** or **NORTHERN FRONT III FINAL NEWEST**, find the Russian S-400 battery, Shahed launchers and any Russian ship | Russian Federation flag (white-blue-red) on the Russian units; the Meridian flag (navy, gold line, white band, star) on the Shahed and Sejjil launchers and the Peykaap boats, named "Meridian Maritime Group" | USSR or Iranian flags still showing, or a blank/missing flag icon: say which unit |
| **Airbase launch rate.** In the mission editor, put the Modern Chinese Airbase (Large) and the PLAAF airlift base on red with their default air groups, order a 12-aircraft launch from each, and time it; do the same on an unmodified install if you can | Aircraft spawn, taxi and roll at a steady rate; a dozen fighters airborne within a few minutes | Still one aircraft every minute or worse: note which base, which aircraft type (fighter or Y-20/KJ-500 class) and where they wait (in the hangar, on the taxiway, at the runway) |

---

## 2. Sulu Line — The Island Road (new, nothing tested yet)

Philippine Navy, seven missions, October–November 2028. **The whole campaign
rests on one rule: there is no free rearm.** Check that first.

### 2A. Starting the campaign

| Do | Expect | If not |
|---|---|---|
| Start Sulu Line on **Standard** | Commander screen: nation **Philippines**, the Philippine flag as navy emblem, rank **Commodore**, a Spanish-style default name (editable). Rank pictures are blank on purpose | The screen refuses the nation, shows a broken image, or won't continue **(4.1)** |
| Read Campaign Rules → Your Goal | "Rearm: never free…", and a paragraph naming the three supply-ship sales | Still says "for free" **(1.3)** |
| Open the Task Force builder before mission 1 | 1,000 points. On sale: Jose Rizal class, Miguel Malvar class, Del Pilar class, Conrado Yap, BRP Tarlac / Davao del Sur, HTMS Chula, the H-76 helicopter (offered first as the **AW109E LAH**, then as the AUH-76). **Not** on sale yet: Thai frigate and Seahawk, RAN Anzac and MH-60R, FA-50, the C8 charter **(1.1, 8.5)** | Anything else on sale, or a supply ship missing |
| Check prices | Philippine units 20% cheaper than their list price; Thai, Australian and MSC units at full price. Note especially whether the **Jose Rizal** and **Miguel Malvar** get the discount (their files spell the nation in lower case) **(4.2)** | Note the prices you see |
| Assign the H-76 to your Jose Rizal or Miguel Malvar in the Task Force Manager | Accepted **(8.2)** | Refused: SEST Cross-Deck's deck fit did not take effect. Bring back Player.log and the `pn_ffg-150` and `pn_ffg-06` lines of the pack's `CROSS-DECK.txt` |

**Buy:** at least one frigate, one Tarlac, and the H-76. Start from a new
campaign: a mid-mission save from an older build keeps the aircraft it
stored.

### 2B. The no-rearm rule (most important)

| Do | Expect | If not |
|---|---|---|
| In mission 1, fire some 76 mm rounds and at least one missile. Win | — | — |
| Open the Task Force screen before mission 2 | The frigate shows **fewer** rounds than she started with. **No** green "Rearmed" icon. The stores editor is locked with "Ammunition expended and no rearm before this mission" **(1.2)** | She is full again → the rule does not work in game. **Report this first**; the campaign needs rethinking |

### 2C. Supply ships at sea

| Do | Expect | If not |
|---|---|---|
| In mission 2, fire the gun. Then bring the frigate **within half a mile** of your Tarlac, **both ships at 8 knots or less**, and wait | The frigate's 76 mm count climbs; the Tarlac's stock falls **(2.1)** | Nothing crosses: note the round, the ships, both speeds and the distance |
| Same, after firing a **MICA** and a **Harpoon** | Both come back | Note which does not |
| If you bought the Thai frigate (from mission 2): fire a Harpoon, then go alongside | It comes back **(2.2)** | The launcher stays empty while the gun refills |
| After a mission where the Tarlac gave stores, check her before the next mission | Her stock is still lower **(2.3)** | It refilled to full: report it. The campaign still works but is easier than intended |
| Let a supply ship be sunk | She is gone from your task force. Mission 5's window does **not** sell another; missions 4 and 6 do **(2.4)** | — |

### 2D. Mission by mission

| Mission | What to check |
|---|---|
| **1 The Island Road** | Convoy of two reaches the box 30 NM south-west; two Meridian fast attack craft come from the south-east. Win = both convoy ships in the box. Puerto Princesa holds only what you bought and the mission's own flights: no F-4s, RA-5Cs, EA-6Bs, E-3A, P-3Cs, SH-3Hs or CH-46s **(8.1)**. Your H-76 flies from and lands on the frigate **(8.2)**. Fly the H-76 that starts in the air until it is low on fuel: it lands and refuels on the frigate or at Puerto Princesa, and search and rescue never says "no home base" **(8.4)** |
| **2 Fire Mission Jolo** | Ship starts 25 NM north of Jolo. Steam in; the 76 mm reaches the ridge from about 8 NM. **Three of five** positions destroyed = victory **(3.1)**. Check the launch rails can attack your ship |
| **3 Ayungin** | Nothing fires at the boat: the cutters carry machine guns only and shadow north of its track; the watcher is an unarmed intelligence ship **(5.1)**. Firing on any Chinese unit ends the mission. The boat entering the shoal's lagoon wins |
| **4 Service at Sea** | Before it, the RAN Anzac **and the RAN MH-60R** are on sale (here and before mission 6 only); assign the H-76, the Thai Seahawk and the MH-60R to Naresuan, the Thai Seahawk and the MH-60R to Tarlac, and the H-76 to the Anzac: each is accepted **(8.3, 8.6)**. Keep your lead ship within 3 miles of *Sulu Provider* for 30 minutes: a "Thirty minutes" message appears, then she steers north to the box. Use her to rearm: go alongside at 8 kn or less. In a second run let her be sunk after the message and take the lead ship into the box: the mission is **won** (Charter failed), and she is **missing** from mission 6 **(2.5)**. Losing her no longer ends the mission (20 Oct 2026) |
| **5 Celebes Gate** | Four coasters, one is the gun-runner (armed, with an escort boat and, from about minute 5, a drone nearby). Sinking a wrong one ends the mission. Sinking the right one before the Basilan Strait wins |
| **6 The Aborlan Battery** | Two Silkworm launchers ashore fire at ships inside about 25 NM, including the convoy at anchor, from about minute 5 (the battery is under cover and not on the map until then) **(3.2)**. Both launchers destroyed wins |
| **7 Balabac Strait** | Chinese surface group of five from the west, two JH-7A strike aircraft, maybe a submarine. **Three of five** ships sunk wins. Note how much ammunition you had left |

### 2E. Bring back

Mission results; the answer to **2B** (most important); whether rounds crossed
in **2C** and at what speeds; whether supply-ship stocks persisted; the
discount prices; how many shots it took to win missions 2 and 6; which
helicopters the frigates, Naresuan, Tarlac and the Anzac took (**8.2-8.3**),
and anything old on a Philippine field (**8.1**).

---

## 3. Southern Watch — The Northern Lifeline

Royal Australian Navy, October–November 2028. 12 core missions, 4 optional
operations, 2 contingencies, plus 8 single missions under *Southern Watch -
Dispatches*. Full card: `docs/campaigns/southern-watch/test-card.md`.

| Check | Do | Expect |
|---|---|---|
| Builder **(2.2–2.3)** | Before mission 1 | Only Anzac, Arafura and MH-60R on sale; Anzac at 192 (240 less 20%) |
| Your ship appears **(2.4)** | Deploy into mission 1 | The ship you bought is there, on station, not drifting, with no extra authored ship beside it |
| Roster grows **(2.5)** | Before mission 2 | Hobart and P-8 added |
| Air tasking **(3.1–3.5)** | Open Air Tasking before missions 1, 2 and 6 | Ship's Flight; then Maritime Patrol; then Combat Air Patrol. **Never** a row with 0 slots |
| Submarine hidden | Mission 2, Steel Highway: watch the first five minutes at normal speed | No submarine contact appears in the first two minutes. The boat starts 30 NM up the track with her radar off; the Poseidon and Wedgetail start over the convoy, 25-30 NM from her |
| Fuel **(4.2)** | Mission 7, follow a Super Hornet to the end | It gets home to Darwin. Running dry is the most likely failure here |
| Losing cleanly **(5.2)** | Mission 1, lose three merchants on purpose | Defeat, and the other objectives show **cancelled** |
| Memory **(6.1–6.4)** | Lose HMAS Supply in mission 2, then reach mission 9; also save, quit and reload in between | MV Coral Provider is **missing** from mission 9. Keep Supply alive and she is there |
| Rearm earned **(6.9)** | Hold mission 9's service window, then look before mission 10 | A rearm is offered. Miss the window and it is not |
| Rearm at sea **(6E)** | Mission 9, fire a missile, then go within half a mile of HMAS Stalwart at 12 kn or less | The missile comes back |
| Redback from the Seahawk **(first things, 6)** | Mission 3, Rig Seventeen: ready one of HMAS Canberra's MH-60Rs on **SEST Redback Strike** and look at it in the loadout preview, then launch it and order an attack on the Peykaap or the Boghammar from about 4 NM | Its tanks hang on their pylons and four 7-tube pods a side on the Hellfire launcher where the Hellfires do, with no Hellfire and the upper pods clear of the lower rails. Two AGR-30s leave the pods (it fired from 19-tube pods on 23 Oct 2026, not yet from these), the flame burns about ten seconds, the round climbs to about 2 km, slows steadily to about 150 knots over roughly a minute, picks up to about 220 knots 2 NM out and dives. If no salvo leaves, or it never climbs, note the range and any message (`docs/playtest-20261023-redback.md`) |
| P-8 Harpoons **(H.25)** | Before mission 5, Weapons Free: buy the P-8, task it on Maritime Strike with the AntiShip fit, and engage the Sovremenny with its Harpoons | The Harpoons launch and get midcourse updates. No launch (Player.log `can not be launched without associated sensor`) or the link lost at launch: bring back Player.log and the range |
| Optional ops **(6.7)** | Bring both Korean warships in at O3, then start mission 6 | ROKS Sejong the Great is in your screen |
| Open Allocation **(2.9)** | A **new** campaign, windows before missions 1-3 | The story's own short lists and nothing allied, ship or aircraft; Campaign Rules' availability line says the windows before Weapons Free offer what the story releases, and every one from the one before it the whole roster and the allied fleet |
| Open Allocation **(2.10)** | Window before mission 5, Weapons Free: buy a Mogami or a Type 23 | The whole roster, 82 units in all: the campaign's own ten (the Triton among them), the Canberra-class LHD and the allied fleet at its own navies' prices - carriers, amphibious and supply ships, destroyers and frigates (52 classes) and 19 aircraft types; the bought ship sails; still only one ship sails |
| Open Allocation **(2.11)** | Windows before missions 9, 11 and 12 | The same 82 at each - a Seahawk, Wedgetail and Triton before mission 11, a Hobart and a Growler before mission 12; a bought ship sails in mission 9 |
| Allied carrier **(G.12)** | Before mission 5, buy a Ford or a Wasp; sail it in mission 9 | It comes with an empty deck and sails with the force |
| Allied aircraft **(G.13)** | Before mission 5, buy a Typhoon FGR.4; fly missions 5 and 6 | Offered the strike row in mission 5 and Combat Air Patrol in mission 6; it gets back to its field |
| Old save **(2.12)** | Load a Southern Watch save from before this update, mid-campaign | It loads. Note what its windows offer: the whole roster and fleet, the story's list with the fleet or the escorts, or the story's list alone (a campaign under way may keep its old windows: start again to get this) |
| Both datums **(6.6a)** | Do O2 and O5, then start mission 4, The Quiet Passenger | Two intel lines; the submarine **and** the passenger on the plot as fifteen-minute datums |
| Orphaned save | Open `NEW TEST 1.sav`, a *Southern Watch - Open Allocation* save from before 21 Oct 2026 | It cannot be continued: the version it belongs to is retired. Note what the game does with it (hidden, an error, a broken menu). The campaign menu still opens and lists the four campaigns |

---

## 4. Southern Reach — Tasman Shield

Royal Australian Navy, December 2028–March 2029. 26 missions in two
chapters. Every position was checked against a real coastline, so grounding
is the thing to watch. Full card: `docs/campaigns/southern-reach/test-card.md`.

| Check | Do | Expect |
|---|---|---|
| Coastline **(1A.1–1A.2)** | Load **Tasman Shield 02 - Cook Strait**, pause at the start, then run 10 minutes at 8x | Every ship afloat; the ferries cross Wellington–Picton without grounding |
| Anchorage **(1A.3)** | Load **Southern Reach 04 - Macquarie Passage** | Supply and Coral Pioneer in Buckles Bay, afloat |
| Builder **(2.1)** | Before mission 1 | Anzac 192, Hobart 384, Seahawk 16 |
| Rearm earned **(2.3–2.4)** | Before SR06: once after **missing** SR04's 30-minute window, once after **holding** it | No rearm / rearm offered |
| Rearm at sea **(4.10)** | SR04, fire an NSM or ESSM, then go within half a mile of Supply at 12 kn or less | It comes back |
| Detachment **(2.5)** | Before TS02 | You choose which ships sail |
| Optional pair **(2.8)** | After TS09 | Both TS10A and TS10B offered; play one; after TS11 both are gone |
| Consequences **(3.6, 3.11)** | Sink VICTOR in SR07 → check SR10; sink ROMEO in TS05 → check TS09 | The sunk boat is missing later |
| Weapons Tight **(4.8)** | SR10, everything red starts Tight | Nothing fires until you do |
| Defector **(6)** | TS11A The Twelve-Mile Line | See section 6 of the card |
| Open Allocation **(2.11)** | A **new** campaign: every window, through Tasman Crossing | The story's own lists and nothing allied until the window before TS04; from it every force allocation (every window with a builder) offers the whole roster, 73 units in all: the campaign's own ten (a Hobart before TS12 too), the Canberra-class LHD and the allied fleet at its own navies' prices - 52 ship classes and 10 aircraft types. JS Mogami (Mogami Variant1), Daegu Variant1, HMAS Choules and the Supply-class AOR are **never** offered |

---

## 5. Red Line — The Other Watch

People's Liberation Army Navy, November 2028–February 2029: six core missions
and, since 20 Oct 2026, three side operations - O1 *Datum*, O2 *The Ships from
the North* and C1 *Pilot in the Water*, with four new pages. Won by restraint:
almost every mission is lost by firing on the wrong thing. A Red Line campaign
started before the side operations must be **started again** (17 entries, not
10). Full card: `docs/campaigns/red-line/test-card.md`.

| Check | Do | Expect |
|---|---|---|
| Commander **(1.2)** | Start the campaign | Nation China, rank Rear Admiral, PLAN emblem; rank pictures blank on purpose |
| Weapons Hold **(4.1)** — biggest risk | RL01, leave everything at Hold for 10 minutes with the submarine astern and the Poseidon overhead | Nothing fires |
| Weapons Tight **(4.3)** | RL02, frigate at Tight with the Poseidon passing overhead | It does not shoot the Poseidon |
| Direct order **(4.4)** | RL04, frigate at Hold, order it to fire on *Meridian Harmony* | The order is obeyed. Note what weapons state it switches to |
| No rearm **(3.4)** | Before RL04 | Repair only, no rearm offered |
| Open Allocation **(3.9, 3.10)** | A **new** campaign, before RL01, RL02, RL03 and RL06 | Every window offers the whole roster - 054A, Luda, Sovremenny, 056A, Z-9C, Y-9, KJ-500, J-15 and J-15D - and the Type 901 and Type 903A at 160 and 120, the PLAN's own: nothing calls them allied. RL06's text says a fixed-wing aircraft allocated there will not fly |
| Unseen **(5.1–5.2)** | RL05: wait deep and slow for a minute, then come to periscope depth under the Poseidon | Nothing at first; once the Poseidon classifies the boat, the mission is lost |
| Racetracks **(8.1)** | RL05 at 8x, watch the Poseidon for the whole mission | It keeps flying back and forth; it does not circle one end |
| Timing **(6.1)** | RL04, ignore the coaster | She clears the screen and the mission is lost around T+40 to T+60. Note the minute |
| Briefings and Situation **(8A.5-8A.6)** | RL01 and RL02 briefings, and the Situation button | No Collins or Virginia photo, and no submarine in the Situation list; the Poseidon's, Triton's and Wedgetail's photos read "Protected - do not engage" |
| Flags **(8A.7)** | RL01's ferry and tuna trawler; the cruise ships in RL05 and RL06 | Indonesian flags in RL01, Panama's on the cruise ships; no Russian flag |
| Side operations **(8B.1, 8B.3, 8B.5)** | A **new** campaign: fly O1, O2 and C1 | O1: the Y-9 classifies GOLF with buoys and nothing fires. O2: both Japanese escorts classified, and neither fighter pair fires first (8B.3a). C1: the lead ship stopped within three cables of the raft, "Pilot aboard." four minutes later and the win at once, at about minute 34 at full speed, before the patrol vessel reaches him at about 39. Note the minute the patrol vessel reaches the raft if you lose the race |
| What they leave **(7.3, 7.4)** | After O1, RL02; after O2, RL03 | RL02: GOLF on the plot for fifteen minutes as an unknown contact. RL03 (7.4, held since 21 Oct 2026): no AIR OPERATIONS line at the start naming Mogami and Maya, and both unclassified until you classify them, whether O2 was won or not. The AIR OPERATIONS report at minute 8 ("A second look from another bearing") is RL03's own and comes in every run |
| Reveal proof **(Southern Reach 3.10, Sulu Line 7.1)** | Southern Reach: win TS01, then fly TS03 *Chatham Watch*. Or Sulu Line: win *Night Market*, then fly *The Okean* | The tender (TS03) or the armed trawler (The Okean) starts on the plot classified. Say whether its classify objective - *Tender* in TS03, *Identify* in The Okean - completes at once, only after you classify her again, or never. This decides whether RL03's reveal after O2 comes back (7.4) |

---

## 6. Pack features to check while playing

| Feature | Where | Expect |
|---|---|---|
| Encyclopedia photos | Encyclopedia → any campaign ship (e.g. Anzac, Collins, Supply, Spruance, Tarlac) | A real photograph with its credit |
| New flags | Any unit of Peru, Ireland, Bahrain, Lebanon, Greenland, Hong Kong, Uzbekistan… | A flag, not a missing-flag icon |
| Readable names | Russian ships | Names in English letters, not Cyrillic |
| Spruance | Encyclopedia → Spruance class (VLS, LAMPS III) | Named, no "Missing Class"; places on the map without an error |
| Apache AH Mk 1 | Default loadout on the ground and in flight | Rocket pods no longer drawn over the Brimstones |
| RAAF F-35A | Strike Long Range Stealth (internal JSM) | No empty wing pylons |
| One AIM-424 | Southern Watch D6 Long Reach (YF-23s on AirToAirIntercept); Encyclopedia → the AIM-424 of the YF-23, the FQ-44 Fury and the Super Hornets | The AGM-88G stand-in under the jet, not a short fat Sea Sparrow; each card gives SEST's MALICE range, 290 nm. A Sea Sparrow: bring back Player.log |
| Merchant supply ships | Any mission with a C8, Seabee, Ro-Ro A/B or Mercur on your side | Ships take stores alongside at 8 kn or less |
| Map lines | Tactical map with several routes | Black lines by day, white at night, selected route red |
| Gallery | Mod Manager → SEST Integration Pack → Open Folder → Gallery → gallery.html | Opens in a browser with photos and credits |
| Richard Morris (editor) | Place Red Storm Arsenal's USS Richard Morris; deploy the variable-depth sonar; fire an NSM | The VDS cable pays out (it named a sonar that did not exist); the NSM hatches open before launch (14 Oct) |
| Buk-M3 (editor) | Place a Buk-M3 battery against a few aircraft | A launcher that has fired takes about two minutes to reload, not seconds (14 Oct) |
| Topol-M and DF-41 (editor) | Place a Road Mobile ICBMs truck with a land target 100 NM or more away | It fires; before 14 Oct its launcher name matched nothing |

---

## 7. What to send back

For each campaign you played, paste the notes from step 0, and put these
first:

1. **Sulu Line 2B:** were ships rearmed for free before mission 2? (yes / no)
2. **Sulu Line 2C:** did rounds cross from the supply ship? Which rounds, at
   what speeds?
3. **Red Line 4.1:** did anything at Hold fire?
4. **Southern Watch 2.4:** did your bought ship appear where it should?
5. **Southern Reach 1A.2:** did any ship run aground?
6. Any crash, freeze or red error text, with the mission name.
