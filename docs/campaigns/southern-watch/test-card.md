# Southern Watch — first play test

Only parts of this campaign have been watched in the game (the first installs
and play tests recorded below). Everything else below is a claim the build
makes about files it wrote; this card is the order to falsify them in,
riskiest first, and what "wrong" looks like for each.

Report back with the step number and what you saw. A step that fails stops
that column, not the whole card — skip to the next section.

## First things to fly after this round

This round brought the other sessions' ported work
(`../southern-reach/install-alignment.md`, §6). Its in-game checks, quickest
first; the detail lives where each line points:

1. **RAS with Stalwart** — SW09, 6E below. The pack's own list is
   `integration/replenishment/README.md`, *In-game test checklist*.
2. **Intercept Model A/B** — the paired builds from
   `tools/make_intercept_ab_builds.py` (`integration/intercept-model/README.md`),
   then 6F below: is the 5% out-of-band ceiling live?
3. **A-10C+ sensors** — D8's Hog 22, 6D below.
4. **Mogami's Seahawk** — SW10: the SH-60K and SH-60J launch from and recover
   to JS Mogami, not the Langgur strip (`docs/design-notes.md`, the JMSDF
   rename).
5. **The ARRW profile** — *SEST NF3 - SEAD over the Shelf*: the B-52Os'
   AGM-183As loft to about 99,000 ft, where they used to cruise level at
   90,000.
6. **The Redback** — *SEST NF3 - Coastal Ambush*: the A-10Cs' AGR-30s guide
   out to 25 NM; before, a shot past 8 NM fell unguided.
7. **MALICE mass** — an F-15EX on its Malice6 fit (six AIM-424s, 680 kg each
   now) gets airborne and reaches its station.
8. **SM-3 terminal** — a Flight III Burke's SM-3 IIA at a DF-21D or DF-26B
   raid locks well outside 10 NM, with no lock/unlock cycling (`build-notes.md`,
   *The SM-3 seeker*).
9. **The editor-crash sweep** — open the missions you edit in the mission
   editor: no "An item with the same key has already been added"
   (`integration/missions/README.md`).
10. **The new scenarios** — eleven `SEST NF3 -` missions in the list, five with
    a supply ship (`integration/missions/scenarios/README.md`).
11. **Red Line's Hold/Tight and unseen triggers** — `../red-line/test-card.md`,
    4 and 5.

## Install

`docs/campaigns/southern-reach/install-alignment.md` is the current full
procedure (it covers all three campaigns). `install-alignment.md` in this
folder keeps the failure story and its checks, and is worth reading once: an
earlier install reported IN LINE against a commit that contained none of this
campaign, because the repo was on the wrong branch and the guard was pointed
at the wrong one.

The short version, game **closed** (it rewrites `usersettings.ini` on exit):

```powershell
git checkout sest-dev/loving-bell-3cnvvw
git pull origin sest-dev/loving-bell-3cnvvw
powershell -ExecutionPolicy Bypass -File .\tools\sync-sest.ps1
```

Expect `1 of 1` installed plus a `purged` line per old per-pack folder.

The `component ApproximateVersion values differ` note is no longer expected:
it came from a build, which this short version does not run, and every
component pack now declares the same version. A
`dropped stale workshop entry` line should no longer appear - Automatic SAR,
the MV-22B and the Korean navy are all catalogued - and if one does, it names
a new subscription. Afterwards the Mod Manager should show **Automatic SAR**
and **MV-22B Osprey** enabled.
`canonical pack not installed in StreamingAssets` is the one that means the
install did not take — stop there.

The campaign ships twice on purpose: as a campaign under
`campaigns/sest-southern-watch/`, and every mission again under
`missions/Southern Watch/` and `missions/Southern Watch - Dispatches/`
so the mission browser can reach them without the campaign layer. **If the
campaign does not appear, the browser copies still should** — that difference
is itself the answer to step 1.

## 1 — does it load

| # | Do | Expect | If not |
|---|---|---|---|
| 1.1 | Campaign list | **SOUTHERN WATCH** present, 35 entries | Campaign not surfaced by the Mod Manager. Go to 1.3 and work from the browser |
| 1.2 | Start it | The 18 October card, then WHITE WATER | Note which of the two it stops on |
| 1.3 | Mission browser → `Southern Watch 01 - White Water` | Loads, ships and aircraft visible | A missing unit names the mod that failed to load |

Load one mission from each theatre before going further — **01 White Water**,
**08 The Open Door**, **11 Fujian's Shadow**. They use the most different
content. A texture or model that fails shows up here, not in the rules.

## 1A — the art (new, and entirely unverified)

The pack now ships 38 generated PNGs and points `campaign.ini` at them with
three keys read out of the vanilla campaigns. Whether a **mod-supplied**
campaign's art loads the way the base game's does has never been watched
happen, and the vanilla export carries no PNGs to compare against — so every
row here is a guess until you look.

| # | Do | Expect | If not |
|---|---|---|---|
| 1A.1 | Open the campaign list | A dark chart behind the list: graticule, numbered marks 01–12, a compass rose, SOUTHERN WATCH bottom-left | No backdrop = `BackgroundImage` is ignored for mods. The format is now the stock `MapView`; the stock campaign's own backdrop is not on disk, so its size (1920x1080 here) is still a guess |
| 1A.2 | Look at a mission entry and its briefing panel | A card at the stock sheet size (1184x640, the same as Pacific Strike's): big number, big title, a blue plot of own force with the objective ring | The first install drew nothing here on `Legacy` with 1920x1080 sheets. Blank again on `MapView` at the stock size = a mod-supplied `MissionImage_` is not read at all |
| 1A.3 | Is the card **readable** in the panel? | The number and name carry it; the plot is a shape, not detail | Say what is too small — the card is generated, so this is a one-line change |
| 1A.4 | A story entry's tile on the campaign map | A small plain tile behind the title: cream for a press sheet, dark for a signal, log or INTSUM (128x128, the stock names `bkg_tile_newspaper` / `bkg_tile_message`) | A blank tile = `TileImagePath_` unread for mods |
| 1A.5 | Open a story card (entry 1, "White Water 18 October") | A cream newspaper sheet, headline and two columns of type | A blank page = the `Assets[]` binding in the XAML is not resolving against `AssetsPath_` |
| 1A.6 | Step through the pages before mission 2 | Three different documents: a typed INTSUM under a SECRET // RELEASABLE TO COALITION PARTNERS marking, a ship's deck log with a time column and the master's note boxed at the foot, a teleprinter cable | Check long headers and notes wrap, all log entries remain visible, and body text clears the footer |
| 1A.7 | Is the backdrop cropped, stretched or letterboxed? | It should fill | Tell me the shape of what you see |
| 1A.8 | The briefing screen's right-hand pane, before any mission | A chart: coastline, graticule, own forces in blue, reported enemy areas in red, a locator inset top-right | This was the blank area on the first install. Still blank = `BriefingMap_en.xml` is not read from a mod's `_briefing` folder, which would contradict the Workshop missions that ship one |

**This is the section most likely to fail**, and failing it costs nothing else
— the campaign plays without art.

## 2 — Task Force Mode (never exercised, highest risk)

The whole purchasing and persistence layer is inferred from the shipped
Pacific Strike campaign and has never been run.

| # | Do | Expect |
|---|---|---|
| 2.1 | Start the campaign on **Standard** | 1,000 points, cap 1,500 |
| 2.2 | Open the builder before SW01 | Exactly **3** buyable: Anzac, Arafura, MH-60R |
| 2.3 | Buy an Anzac, take Variant3 or Variant8 | Both offered, at 192: the roster's 240 less the 20% same-nation discount (G.6) |
| 2.4 | Deploy into SW01 | The purchased ship is **Taskforce1Vessel1**, on station, not adrift |
| 2.5 | Finish SW01, open the builder before SW02 | The list has **grown** to 5 — Hobart and the P-8 added. No Supply, no Collins, no KC-46: the roster sells nothing a mission cannot deploy |
| 2.6 | Before SW05 | The builder says one ship sails it; the deployment screen accepts **exactly one vessel** (`Replaced`, `MaxUnits=1`). Send an Arafura and the magazine objective must still read her NSM cells |
| 2.7 | Before SW07, SW08, O2 | **No deployment screen at all.** The note says nothing of your force sails; the mission launches as authored |
| 2.7a | Before O1 and C1 | A **deployment screen** (a detachment of your choosing) and a Ship's Flight row; no builder, no repair |
| 2.7b | Before SW03, then before SW05, then before SW11 | SW03's list is SW02's: **no F-35A** until the window before SW05, where the strike row can take it. Before SW11 there is **no Seahawk, Wedgetail or Triton** (no row in the carrier action); the P-8 is offered and fits the Attack row |
| 2.8 | Before SW12 | Aircraft plus **Arafura and Anzac** as replacement hulls; no Hobart. Buy an F-35A and assign it to Combat Air Patrol: it must appear, fly and recover at Darwin |

2.4 is the one to watch. If the bought ship is missing, misplaced, or the
authored ship is still there beside it, the anchor model is wrong and the
whole economy sits on it.

## 3 — Air tasking (rebuilt twice; rows must pair with cockpits)

| # | Do | Expect |
|---|---|---|
| 3.1 | Before SW01, open Air Tasking | One flight: **Ship's Flight** (1 slot). Before SW02: Ship's Flight and **Maritime Patrol** (1) |
| 3.2 | Assign a bought MH-60R to Ship's Flight | It takes the slot and is airborne at mission start |
| 3.3 | Before SW06 | **Combat Air Patrol** (2 slots) and **Maritime Patrol** (1) |
| 3.4 | SW07 | **No air tasking offered at all** — every aircraft in it is a named asset |
| 3.5 | Anywhere | No flight offered with **0 slots**, and no slot with no flight |
| 3.6 | Before SW11, assign a bought Growler to Combat Air Patrol, then to Maritime Strike | The only fit offered in either is **SEST SEAD120D** (2x AGM-88G, 2x AIM-120D, two tanks); no fit with the AIM-260 appears. Ford's Growler in the strike slot flies its own **SEAD** fit. Grizzly 31 in SW07 carries AIM-120D, not AIM-260 |

3.5 is the invariant: 19 rows, each pairing exactly with its sections. One
empty row means the pairing model is wrong.

## 4 — Fuel and recovery (changed most recently)

Every player aircraft now flies on finite fuel, using ranges read from the
airframe files, and has a field or deck in reach. In a mission your force is
generated into, one whose nearest deck is a Taskforce1 ship names no
`HomeBase` (the stock rule; build notes, "Rig Seventeen died again"): order
it to land on the ship. Nothing here has been observed.

| # | Do | Expect |
|---|---|---|
| 4.1 | SW01, follow the P-8 | Fuel falls. It is homed on **RAAF Darwin**, 117 NM, 11% of its radius |
| 4.2 | SW07, follow a Super Hornet to the end of the clock | 378 NM to Darwin, 74% of radius — the tightest margin anywhere. Most likely thing in this section to fail |
| 4.3 | D2, the VH-3D | 80 NM to the carrier box and its deck, **USS Theodore Roosevelt**, 37% of radius. It should make it easily |
| 4.4 | Any mission, let one fly past bingo | It should divert or recover, not fall out of the sky |

If 4.2 or 4.3 runs dry, the 0.40 sortie fraction is too generous and wants
lowering — tell me the airframe and roughly when it went.

## 5 — Triggers and outcomes

| # | Do | Expect |
|---|---|---|
| 5.1 | SW01, win it | Victory, convoy objective complete, mission ends cleanly |
| 5.2 | SW01, deliberately lose 3 merchants | Defeat, and every other objective shows **cancelled**, not complete |
| 5.3 | SW06, classify the northern surface group | Intel message, then ~2 min later a **new objective appears** naming the shuttle |
| 5.4 | SW06, ignore the recon entirely and just run the convoy | Win. The Airlift task never appears and scores nothing |
| 5.5 | Any mission, win near the deadline | One outcome only — no double ending, no defeat after a victory |

5.2 is the one I would bet against: it tests that cancelling works the way the
shipped missions imply.

## 6 — Campaign memory (needs two missions and a reload)

| # | Do | Expect |
|---|---|---|
| 6.1 | Lose HMAS Supply in SW02, play through to SW09 | **MV Coral Provider is absent** from SW09 |
| 6.2 | Keep Supply alive, same route | Coral Provider **is there** |
| 6.3 | Classify the group in SW06, reach SW11 | The three escorts are identified from the start, with an intel line |
| 6.4 | Save mid-campaign, quit to desktop, reload | The flags above still hold |

| 6.5 | Get alongside Torres Light first in O1, then start SW02 | An intel line and the submarine on the route shown as a **classified** contact from the start; skip O1, or let Meridian's ship get there first, and it is not |
| 6.6 | Identify the coaster in O2, then start SW04 | The same shape: Kiwi 01's picture as intel, the submarine classified |
| 6.7 | Bring both Korean warships in at O3, then start SW06 | **ROKS Sejong the Great** is in the screen. Lose either, or skip O3, and she is not (`SpawnByVariableAND=O3ShieldJoined,IsTrue` — the first `IsTrue` spawn in the pack) |
| 6.8 | Put both coasters in at O4, then start SW08 | A **KC-46** on the track south of the box; skip or fail O4 and there is none |
| 6.9 | Hold the SW09 service window, then open the SW10 pre-mission screen | A **rearm** is offered. Miss the window (leave the box before 35:00 and lose it) and it is not (`TaskForceModeRearmByVariableAND`) |

6.4 is the real test. Declaration, write and read are all present in the files
and statically consistent; whether the campaign carries a flag across a save
is the one thing no amount of reading can settle. 6.7 and 6.9 use syntax the
shipped data does not attest (`IsTrue`; the rearm-by-variable key is from the
developer guide), so each is a design answer either way.

## 6A — rescue and the Osprey (new)

| # | Do | Expect | If not |
|---|---|---|---|
| 6A.1 | Mod Manager after the sync | **Automatic SAR** and **MV-22B Osprey** enabled, not flagged as not loaded | Still not loaded = the order was rewritten after the sync (the game was running), or Anchor Chain's loader is not installed |
| 6A.2 | Any mission where a ship sinks or an aircraft goes down: right-click a helicopter, **Start automatic SAR** | It flies to the nearest distress beacon and picks up survivors ("Picked up survivors") | Whether it treats the VTOL Osprey as a helicopter is untested - try it |
| 6A.3 | Finish that mission and read the debrief | A **Survivors rescued** line and "*N* survivors -> *M* additional point(s) awarded". Tell me N and M | The campaign ships the stock `CSARPointModifier=10`; N and M settle which way it scales |
| 6A.4 | Rig Seventeen: send **Lifter 12 (the Osprey)** to the rig, then south of the line | Victory - either lifter can make the lift, and the per-lifter chain works for the Osprey as for the Super Stallion | It must launch from and recover to HMAS Canberra; a refusal names the deck list |
| 6A.5 | The Long Perimeter: fly Dragon 71/72 into the airstrip before the ridge is cleared | The Tor engages them in the last five miles; once the ridge is down, the landing completes **Lift** | The lift completing with the ridge untouched means the SAM never engaged - tell me |

| 6A.6 | Any mission with an Anzac under missile attack | ESSMs climb out of the Mk41 and meet incoming sea-skimmers low; they no longer cruise at a metre above the sea to get there | If one still flies low, note what it was fired at - a ship means the ASuW secondary mode, not the flight profile |

## 6B — side operations carry your losses (new)

Reported: the operation after White Water brought back a ship that had been
lost there, without its damage. O1 and C1 now deploy your own force; SW07's
picket is a hull you cannot buy.

| # | Do | Expect |
|---|---|---|
| 6B.1 | Take damage and lose a ship in SW01, then open O1 | The lost ship is **not offered**; the damaged one deploys **with its damage** |
| 6B.2 | O1, go straight for Torres Light at speed | Classify her (intel line), get the **lead ship** within 1.5 NM: **victory**, and SW02 reveals the submarine (6.5) |
| 6B.3 | O1, stay on the lane and let Meridian Salvor run (about 70 minutes) | She reaches Torres Light first: **defeat** with the Meridian message, and no SW02 reveal. With a frigate lead, 30 minutes on the lane is still recoverable; with an Arafura it is not |
| 6B.4 | O1, sink Meridian Salvor, then get the lead ship alongside | **Victory**, and **Restraint fails** (-20) at the debrief. Sink her and never get alongside: the clock runs out with the timeout text, not the Meridian one |
| 6B.5 | O1 or C1, lose the lead ship while another survives | The mission **ends at once** in a defeat, not at the deadline |
| 6B.6 | Lose Hobart in SW02, then open C1 | Hobart is **not** in C1; your own detachment sails it, and the lead ship reaching the box's northern edge wins |
| 6B.7 | Lose HMAS Perth in SW05 or SW06, then play SW07 | SW07's picket is **HMAS Arunta**, not Perth |
| 6B.8 | Select any RAN MH-60R or S-70B-2 (bought, or on a fleet ship or RAAF base) | The unit panel shows **Australia** - 816 Squadron RAN for the MH-60R, 'Tiger' for the S-70B-2 - not the US or France |
| 6B.9 | Any mission with a helicopter | The helicopter flies and works as one: it hovers, dips and lands on its ship. It is never in a formation with a jet or a ship |
| 6B.10 | D2, look at USS Carl Vinson's deck | Her parked Seahawks look like Seahawks. A scrambled texture means the composed MH-60R livery is being applied to ADO's SH-60B deck prop (build notes) |
| 6B.11 | O1's tactical map | **No contact near 0°, 0°**, and no blue unit pushed against the map's edge. If either is still there, note what the contact says it is |

## 6C — red aircraft that were briefed to come (new)

Each of these used to orbit its spawn point (6C.4's J-15D was routed but
flew as the #2 of an unrouted leader). Watch the first 20 minutes, and 40 in
SW09 and SW12.

| # | Do | Expect |
|---|---|---|
| 6C.1 | SW05, sit still | The JH-7A pair goes **west first**, then comes down the corridor; no YJ-91 before about 14 minutes |
| 6C.2 | SW07, send the tanker home at once | The Foxhounds come south towards TEXACO's station and **turn back north** at about 13 minutes; the tanker is never in R-33 reach. The returning package is, for about the first 13 minutes, and so is a Wedgetail that holds its orbit from about 11 to 15 |
| 6C.3 | SW09 | The Tu-214R comes to about 33 NM west of the service box at about 20 minutes and leaves; the Flanker pair swings round the outside and is in Kh-31A range of the ships at about 30-34 minutes, near the end of the window |
| 6C.4 | SW11 | Flying Shark 21 heads for the transports on its own; shooting it down completes **Strike** (not the KJ-600) |
| 6C.5 | SW12, Fujian alive in SW11 | The spoiler JH-7A opens east, is inside YJ-91 range of the convoy at about 21 minutes (expect a launch then), passes over it at about 35-38, and goes home |
| 6C.6 | D7, leave the Bear alone | It reaches the marked release line at about 19 minutes and the serial **fails** with the umpires' message; the Badger stays north, out of play |
| 6C.7 | Banda Foxhound Sweep | The MiG-31s run at the Wedgetail fast. Lose the Wedgetail or the tanker: **defeat**, HVA failed - shooting the MiGs down afterwards does not win it back |
| 6C.8 | Banda Triton's Picture | The J-16s come down to the Triton's station |

## 6D — the A-10C+ (new)

D8 now flies a Warthog pair: Hog 21 is the standard A-10C, Hog 22 the SEST
A-10C+. Neither change to the aircraft files has been seen in the game.

| # | Do | Expect | If not |
|---|---|---|---|
| 6D.1 | D8, select Hog 22 and open its encyclopedia entry | **A-10C+**, with an infrared sensor, the Litening pod and a laser designator listed; AIM-9X on its rails | No designator or pod means the new sensor blocks are not read - name what the entry does list |
| 6D.2 | D8, Hog 22 as briefed (its Default fit hangs GBU-12s on the two inboard pylons): drop one on the ridge with no other aircraft lasing | The bomb guides on Hog 22's own designator | An unguided fall means the designator does not feed the bomb |
| 6D.3 | Mission editor: place a standard A-10C and look at its squadrons | **Two** liveries to choose from (81st and 91st TFW), and Hog 21's panel shows an infrared sensor | One livery means the squadron count was not the cause |

## 6E — Stalwart's supply system (new)

HMAS Supply and Stalwart now carry a working supply system (SEST
Replenishment At Sea's table, shipped by SEST RAN Fleet): half a mile, 12 kn
for her and 16 for the receiver, nothing dearer than 8000 points. SW09's
briefing says what crosses; nothing scores it. No transfer from either hull
has been seen in the game.

| # | Do | Expect | If not |
|---|---|---|---|
| 6E.1 | SW09, fire one of Perth's NSMs early, then bring her inside half a mile of Stalwart at 12 kn or less | Stalwart's supply panel ("Ammunition supply") appears and the empty NSM canister refills | No panel: the supply block is not read. A panel but no refill: the canister's reload flag is not honoured (the pack README's checklist item 2) |
| 6E.2 | SW09, Collins alongside with a torpedo or two gone | The torpedoes come back while she is surfaced | Nothing crosses: say whether the panel showed Collins as a receiver at all |
| 6E.3 | SW09, during a transfer, run Perth up to 20 kn and watch the range to Stalwart | The transfer stops as her speed passes 16 kn, while she is still inside half a mile | It carries on past 16 kn: the speed gate is not honoured. If it only stops once the range opens past half a mile, that was the range gate; slow down, close up and try again |

## 6F — the restored intercept table (new)

SEST Intercept Model puts back the global intercept keys a Workshop copy of
`damage.ini` had dropped, among them `InterceptChanceOutOfAltitudeOverride=0.05`:
any surface-to-air shot at a target outside the round's attack-altitude band
is capped at 5%. Whether the engine was already falling back to that is not
in any file, and it has not been seen in the game. The two missions where it
decides most are Blind Horizon and Fujian's Shadow, because the YJ-83 family
skims at **8 ft** (`SeaSkimmingAlt`, feet): under the 10-ft floor of every SAM
Hobart carries (ESSM `usn_rim-162a`, SM-2 `usn_rim-66m-5`, SM-6
`usn_rim-174a`) and of Sejong's RAM (`usn_rim-116e`), under the Burkes' SM-2
and SM-6 (10 ft) and Ford's ESSM (26 ft). The ESSM Block 2 (`usn_rim-162h`,
5-ft floor) that Lucas and the Anzacs carry and Ford's own RAM (no band) are
the only blue rounds inside it. Every fighter in both missions flies well
inside every band.

| # | Do | Expect | If not |
|---|---|---|---|
| 6F.1 | SW06, let the surface group reach its launch basket and fire at the convoy (YJ-83A from the 054A, HY-1JA from the Luda) | If the ceiling is live: a Hobart - and Sejong, if Borrowed Shield put her there - engages the YJ-83A at about **5%** a shot and the guns do the work, while an Anzac in the escort engages it at normal odds with ESSM Block 2; the HY-1JA (82 ft, inside every band) is engaged at normal odds by all | Normal odds against the YJ-83A mean the engine already fell back and the pack changes nothing here. Either way, bring back the odds shown or the SAMs fired per missile killed |
| 6F.2 | SW06, fight the J-16s at 34,000 ft with the F-35As, and let Hobart take one if it comes in range | Normal odds throughout: 34,000 ft is inside every band on both sides | A 5% cap here means the band test is not what the files say - name the round |
| 6F.3 | SW11, let Flying Shark 21 launch its two YJ-83 at the transports | Lucas's ESSM Block 2, any Anzac's and Ford's RAM engage at normal odds; a Hobart, Wilson and Ford's ESSM at about 5% | Say which ship killed each missile. Everything at 5%, Lucas included, means the floor is not read in feet |
| 6F.4 | SW11, the J-35, J-20 and J-15D against Ford's F-35Cs and the Burkes' SM-6 | Normal odds: all at 30,000 ft | As 6F.2 |

Compare with Range Week (D5): its Shahed line flies at 300 ft, under the
David's Sling Stunner's 500-ft floor and THAAD's, so a live ceiling holds both
batteries to 5% there too.

## 6G — Open Allocation (new)

Three new entries in the campaign list, one per campaign, that sell the whole
roster from the first window. Build notes, "Open Allocation".

| # | Do | Expect | If not |
|---|---|---|---|
| G.1 | Open the campaign list | Three more entries: Southern Watch, Southern Reach - Tasman Shield and Red Line - The Other Watch, each with "- Open Allocation" before the navy in brackets, with the same background art | An entry missing = the game does not list a campaign folder with no missions of its own. Bring back the Player.log lines from opening the list |
| G.2 | Start Southern Watch - Open Allocation and open Task Force Builder at the first window | Anzac, Hobart, Arafura, F-35A, Super Hornet, Growler, P-8, Wedgetail, Triton and MH-60R on sale at their usual prices; the situation opens with the Open Allocation line; the Campaign Rules button shows "Southern Watch - Open Allocation - Task Force Mode" | Only the three first-window units = the twin's allowlist was not read |
| G.3 | Buy an F-35A there, then fly White Water | White Water loads and plays as in the standard campaign; the F-35A does not appear (no row for it) and is still in the force afterwards | A load failure = missions are not loaded from another campaign's folder: capture with `-IncludeSaves` and push |
| G.4 | Continue the standard Southern Watch save | Unchanged: its own windows, its own progress | The twin sharing the standard save = the campaigns are keyed by something other than their folder |
| G.5 | Red Line - Open Allocation, first window | Every Red Line roster entry on sale, the J-15, J-15D, KJ-500 and Y-9 among them | As G.2 |
| G.6 | Any campaign, standard or Open Allocation: open the Service Record, then Campaign Rules > Unit Catalog, then Task Force Builder; later, damage a Hobart to Moderate before a repair window | The Service Record reads "Same-nation discount: 20%". In the Unit Catalog the campaign's own units show the commander's nation: Australia in Southern Watch and Southern Reach, the Super Hornet, Growler, P-8 and MH-60R included; China in Red Line. In the standard campaigns and both Red Line versions that is every row; in the Southern Watch and Southern Reach Open Allocation versions Canberra, Choules, Supply and Collins show Australia too, and every allied class shows its own nation at list price (see G.7). Builder prices a fifth under the roster's: Anzac 240 to 192, Hobart 480 to 384, MH-60R 20 to 16; 054A 280 to 224, Z-9C 20 to 16. Record the Moderate repair: 120 = charged on the listed price, 96 = on the discounted one. Note whether your Rig Seventeen save shows the discount or only a new campaign does | One of the campaign's own US-built airframes (the Super Hornet, Growler, P-8 or MH-60R) at full price = the game takes the discount nation from the unit file, not the squadron: say which, and it goes back to a per-unit decision. The allied US aircraft at full price in those two Open Allocation versions (F-22, F-35C, F-15E, F/A-18E, the US Navy's P-8, and in Southern Watch the F-15EX) are correct |
| G.7 | Southern Watch - Open Allocation: Campaign Rules > Unit Catalog | The allied classes are listed with their nations and prices - e.g. Arleigh Burke Flt III 520 (USA), Type 45 460 (United Kingdom), Maya 500 (Japan), E-2D 70 (France) - beside the campaign's own at their discounted prices; the Commander tab says the discount covers 14 Australian classes and 79 of other nations pay full price | A short catalogue = the game did not read the long roster; bring back which entries appear |
| G.8 | Same campaign, first force allocation: buy a Burke Flight III and fly White Water | The builder offers the allied fleet at the first window and the Burke sails with the escort; nothing else in White Water changes | The Burke missing from the builder = the long allowlist line was not read |
| G.9 | Buy a Typhoon (United Kingdom) and a Collins; fly Steel Highway, Blind Horizon, then Southern Lifeline | Steel Highway and Southern Lifeline offer the Typhoon no row: their Ship's Flight (SAR) and Maritime Patrol (MPA/ASW/ESM/AEW) rows do not take its Fighter and Bomber roles. Blind Horizon offers it in Combat Air Patrol. The Collins waits in reserve until Southern Lifeline, where it sails | A Typhoon offered in a Ship's Flight or Maritime Patrol row, a Typhoon missing from Blind Horizon's Combat Air Patrol, or a Collins that never sails: note the mission and the row |

## 7 — the review's engine tests

The independent review of `057405fe` listed the runs that no static check
can replace. Each is a counterexample to try, not a feature to admire.

| # | Do | Expect | If not |
|---|---|---|---|
| 7.1 | SW03: send lifter A to the platform and park lifter B in the withdrawal box | Nothing. B's arrival scores nothing until **B** has visited the platform; A entering the box wins | If B's arrival wins, `Action_EnableTriggers` is not reaching the per-unit triggers |
| 7.2 | SW03: A makes the pickup, then lose A | Defeat, with the "lost after the pickup" message | If the mission continues, the per-unit lost trigger was not enabled |
| 7.3 | SW08 from the campaign map | No deployment screen; the authored Growler, F-35As and KC-130Js are present with their authored stores; the F-35As recover to **Langgur** | A deployment screen means blank generation does not do what the guide says |
| 7.3a | SW03 Rig Seventeen from the campaign map **on a force carried through 01 and 02**, and O3 Borrowed Shield when it opens. The direct load on a fresh force passed 27 Sep; the carried-over load died the same day and is what this row tests | The mission loads; the Osprey and the CH-53 are over HMAS Canberra with no home base named; none of your own aircraft appear (neither mission has an air-tasking slot) | A load that dies again: run `tools\\capture-context.ps1 -Redact -IncludeSaves` with the game closed and push it - the log names the step and the save shows the force |
| 7.3b | After a sync (which switches the PLA AEP's debug logging off), fly SW02 Steel Highway through its submarine hunt with the P-8 and the Seahawks laying sonobuoys, to the end | The game stays responsive; BepInEx\\LogOutput.log stays small, with no `SubAmmunition] SONO pos` flood | Another freeze: close it with the capture block (it now takes the BepInEx log) and push; say what was happening on screen when it stopped |
| 7.4 | SW09: leave the box at 30:00 and return at 34:00; then at 36:00 | Tells us whether `Time=2100` is absolute and whether re-entry counts. Record what completed and when | Either answer is a design answer: the brief says the rule is the box at the moment the window closes |
| 7.5 | SW09: the withdrawal trigger it enables has its own clock | Note whether the box completes immediately on entry or waits | Decides whether a disabled trigger's `Condition_Time` restarts on enable |
| 7.6 | Recovery: order RTB on the Harrier (D3), the U-2 (D7), the VH-3D (D2) and an F-35A (SW08); order the Lynx (O3) to land on Sejong the Great | Each lands on its `HomeBase`; the Lynx, which names none since 27 Sep, lands where it is sent | Name the airframe and the deck; the fit was declared by the two files |
| 7.7 | D3: watch the column and the roadblock from the start | The column **drives** the road toward the distribution point; the roadblock moves onto it | Land units ignoring `Waypoints` means the column objective needs a different shape |
| 7.8 | O3: the Korean ships | Sejong the Great and Daegu appear, fire, and the Lynx flies from Sejong | A missing hull names the mod (3789208859) or its Euromod parent |
| 7.9 | SW01: win at the deadline's last minute; and win while a fatal loss lands in the same update | One outcome only, objectives resolved once | Two endings means the shared exit needs a delay after all |
| 7.10 | SW05 with an Arafura alone | She is `Taskforce1Vessel1`; the mission's texts read correctly for her; the magazine objective fails when her NSM cells are empty | If the authored Anzac is still beside her, the `Replaced` model is wrong |

## What I most expect to be wrong

1. **None of the art appears** (1A) — three keys read out of the vanilla
   campaigns, none of them ever watched working from a mod.
2. **The bought force does not deploy the way the anchor assumes** (2.4).
3. **A Super Hornet runs dry** (4.2) — 74% of a radius that rests on a 0.40
   planning fraction.
4. **Objective cancellation does not read as cancelled** (5.2).
5. **A campaign variable does not survive a save** (6.4).
6. **`IsTrue` does not spawn** (6.7, 6.8) — the one comparison the shipped
   data never uses.

Any of those is a design answer, not a bug report — send what you saw and I
will change the model rather than patch the symptom.

## 6H — Sea Power 0.8.3

| # | Do | Expect | If not |
|---|---|---|---|
| H.1 | SW02 Steel Highway, pause at T+0, then ten minutes at 8x watching the Wedgetail and the KC-46A (both weapons Hold) | On station through the ten minutes | Turning for base at the start = the game returns pre-placed Hold aircraft to base: say so, and every Hold aircraft in the pack moves to Tight (Southern Reach card 7.1) |
| H.2 | SW08 The Open Door (04:50): hover the F-15EX's StrikePrecision fit and the B-52's | No daylight-only warning; the GBU-10s and JDAMs release | A warning on the F-15EX = its Sniper pod's night keys are not read; a warning on the B-52 = the AVQ-22's 0.3 is below the game's bar: say which |
| H.3 | Any mission, Left Shift+O before the first engagement | Note "Ships on Weapons Tight engage hostile aircraft" (off since 0.8.3) and "Ships use anti-ship missiles on Weapons Free" (new) | A Hobart holding its Harpoons at Free is the default, not a mission fault: set and say |
| H.4 | SW05 or SW07, Shift+Y on the Hobart and the Anzac, Engagement tab | The Hobart reads SEST AEGIS BL9; the Anzac SEST 9LV MLU | AEGIS Mk 7 or a default = the RAN Fleet hulls did not install: check the sync's IN LINE |
| H.4a | SW05 Weapons Free, Shift+Y on the Type 071 | SEST PLAN Amphibious (Fast, 80 contacts): the SEST pack's `#!extend` reached another mod's hull | The game's default = it does not (Southern Reach card 7.3a) |
| H.4c | SW06 Blind Horizon (or SW10, SW11, SW12), Shift+Y on the PLAN 054A; SW11, the Fujian | ZKJ-5A and ZBJ-1B: the PLAN Pack's own systems since its 3 Oct update | Anything else = the PLAN Pack's block is not read |
| H.4b | SW06 or SW11, let the 054A's YJ-83 salvo reach the Anzac, and an NSM salvo reach the 054A | The Anzac's Phalanx (Block 1 now) fires volleys with pauses; the 054A's Type 1130 fires long volleys (2800 rounds, 7 s) and stops most of a small salvo, the PLAN Pack's own anchor 90 | Fire without pause on either = the 0.8.3 keys are not read: say which hull; count what a four-NSM salvo loses |
| H.5 | Tindal, Learmonth or Butterworth in any mission that places them: the air group panel | A KC-135 Stratotanker detachment (two aircraft) where the KC-135A was | No tanker = the Stratotanker mod is not enabled |
| H.6 | Campaign screen, the Situation button (bottom right) | The PLAN theatre forces by class, the Fujian, Liaoning and Type 071 as flagships, the boats, the aircraft; an Iranian and a Russian block; nothing of ours | No button or an empty panel = the game did not read `enemy_theater_roster.ini` |
| H.7 | After The Missing Beacon (beacon found), SW02 Steel Highway at T+0 and at T+16 min | A detected contact, unclassified, on the plot at the start where the bridge record put the boat; gone by sixteen minutes unless your sensors hold it | A classified track, or one that never ages off = the bare timed reveal is not read as intended: say which |
| H.8 | Same mission: count the submarine symbols on the plot in the first five minutes | One | Two = the revealed datum and a sonar contact on the same boat are plotted twice: say how long they stay apart and whether they merge |
| H.9 | Any loading screen, with the PLAAF Aircraft Pack enabled | Nineteen tips, in English, headed TIP | Chinese text = SEST Collection Fixes' `language_en/loading_tips.ini` is not winning the merge: check the pack sits at the top of the order |
| H.10 | D3 The Relief Ship, unit list; D6 Long Reach, unit list | Rafale 11 and 12 (Rafale M) over the French group; Rafale 41 (Rafale M Late) in the escort with the fit "SEST Intercept (AIM-260)" | A missing Rafale = the French Air Force mod is not loaded; a stock fit on Rafale 41 = SEST Rafale F5 is outranked |
| H.11 | Editor: a Rafale M Late's loadout list | Four SEST fits (Intercept, InterceptMALICE, AntiShip LRASM, Intercept Heavy), the MALICE and LRASM ones with one round on the centreline and two wing tanks; the Rafale B and C Late show six, with the two three-tank LongRange fits | A floating or pylon-less round on the centreline = the seat name changed upstream: say which fit |
| H.12 | SW09 Southern Lifeline: the Situation button before the mission, then the plot | A Russian surface entry for the trawler on the roster; in the mission an Okean-class trawler twelve miles north-east of the support group, holding its fire | The trawler shooting at the escort = its weapons-hold did not take: say what it fired |
| H.13 | SW11 Fujian's Shadow: the second anti-ship raid | An H-6K (Badger 31) a minute behind the J-15D on the same run, four YJ-12 if it launches | A Badger with no missiles = the YJ-12 did not resolve from the PLAAF Aircraft Pack at the bottom of the order |
| H.14 | D8 The Long Perimeter: the lift stream | Three lifters - Dragon 71, Dragon 72 and an MV-75 (Valor 73), the tiltrotor with its cabin occupied | A missing Valor 73 = the MV-75 mod did not load (it needs Anchor Chain, like the Osprey) |
| H.15 | Mod Manager > Open Folder on the SEST pack (a Workshop copy), quit the game, double-click "SETUP - double-click me.cmd" | A console window: the game and workshop paths, "built against 148 mods", "all 148 mods are downloaded", [ok]/[done] lines for the preloader, the debug switch and the order, "All done", "Press Enter to close this window". A UAC prompt only if neither winhttp.dll nor BepInEx was in the game folder | The window flashes and closes = PowerShell refused the script: run the .cmd from an open console and bring back the error. "STOPPED" = read the line; each names its own fix |
| H.16 | After H.15, the Mod Manager, and the mod list | The SEST pack first and ticked, the 148 in LOAD-ORDER.txt order, your other mods at the bottom as they were; nothing in the list or the log mentions the .cmd or the .ps1 | A "dependency issues" prompt on the pack = Required Workshop IDs got set on the Steam item: clear them. A mod the game lists that SETUP dropped = it was not under workshop/content: say which |
| H.17 | Any mission: let the clock reach the planned minute (SW04 The Quiet Passenger: 45:00), then keep playing | At 45:00 a yellow "Behind schedule" message naming the 45-minute window and about 23 minutes more; nothing else changes; at 68:00 (1.5x) the red "Operational window closed" failure as before | No message at the planned minute = BehindScheduleMessage is not read from [Language_en]: bring back the file's Trigger list. Failure at 45:00 = an old build |
| H.18 | SR04 Macquarie Passage, sea state 5: Supply and Coral Pioneer at flank north from the 30-minute check | Both inside the withdrawal line (16 NM north of Buckles Bay, radius 12) before 75:00, the planned window; note Supply's speed over ground | Not inside by 75:00 = the SEA_SPEED row for state 5 (0.45) is still optimistic: bring back her speed and the minute she crossed, and the table moves |
| H.19 | SW01 White Water, first five minutes: note where Warramunga, the merchants and the two Meridian contacts start, and when the first missile alert comes | Warramunga about 3 NM ahead of the merchants on the threat side, the Meridian pair about 29 NM out to the east-north-east, beyond its own radar; no launch before you have had time to classify it | A launch inside the first few minutes, or Warramunga still astern of the merchants: bring back the minute of the first launch and the range to the shooter |
| H.20 | SW02 Steel Highway, opening: buy a P-8 and note where it spawns; then prosecute Contact BRAVO | The escorts 2 NM ahead of the merchants; the P-8 at 6,000 ft about 10 NM from the datum, 30 NM up the track; no torpedo or YJ-18 in the water in the first ten minutes | The P-8 far from the datum or high, or the boat firing before the screen is formed: bring back its spawn, the minute of the first launch and the range |
| H.21 | O2 Southern Cross: fly Kiwi 01 to the coaster, classify it, and bring her to Darwin; keep Pilbara on the lane | Win. The Meridian boat shadows the coaster and does not fire on Pilbara unprovoked; no missile in the first ten minutes | Pilbara under missile attack without having fired: bring back the minute and the range to the boat - Tight may not hold her for this AI |
| H.22 | Any mission from the opening-gate table (build notes): the first five minutes | No enemy weapon in the air before you have a contact on your plot and time to classify it | A launch in the first minutes: bring back the mission, the shooter and the range |
