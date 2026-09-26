# Southern Watch — first play test

Nothing in this campaign has been run in the game. Everything below is a claim
the build makes about files it wrote; this card is the order to falsify them
in, riskiest first, and what "wrong" looks like for each.

Report back with the step number and what you saw. A step that fails stops
that column, not the whole card — skip to the next section.

## Install

`docs/campaigns/southern-watch/install-alignment.md` is the full procedure,
and it is worth following once: the last install reported IN LINE against a
commit that contained none of this campaign, because the repo was on the wrong
branch and the guard was pointed at the wrong one.

The short version, game **closed** (it rewrites `usersettings.ini` on exit):

```powershell
git checkout sest-dev/loving-bell-3cnvvw
git pull origin sest-dev/loving-bell-3cnvvw
powershell -ExecutionPolicy Bypass -File .\tools\sync-sest.ps1
```

Expect `1 of 1` installed plus a `purged` line per old per-pack folder.

One warning is **expected** and is not a fault: the
`component ApproximateVersion values differ` note from the consolidation. A
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
| 2.3 | Buy an Anzac, take Variant3 or Variant8 | Both offered, priced 240 |
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

3.5 is the invariant: 17 rows, each pairing exactly with its sections. One
empty row means the pairing model is wrong.

## 4 — Fuel and recovery (changed most recently)

Every player aircraft now flies on finite fuel with a `HomeBase`, using ranges
read from the airframe files. Nothing here has been observed.

| # | Do | Expect |
|---|---|---|
| 4.1 | SW01, follow the P-8 | Fuel falls. It is homed on **RAAF Darwin**, 111 NM, 34% of its radius |
| 4.2 | SW07, follow a Super Hornet to the end of the clock | 378 NM to Darwin, 74% of radius — the tightest fast-jet margin. It should make it |
| 4.3 | D2, the VH-3D | 191 NM to the carrier, **87%** — the tightest margin anywhere. Most likely thing on this card to fail |
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

## 7 — the review's engine tests

The independent review of `057405fe` listed the runs that no static check
can replace. Each is a counterexample to try, not a feature to admire.

| # | Do | Expect | If not |
|---|---|---|---|
| 7.1 | SW03: send lifter A to the platform and park lifter B in the withdrawal box | Nothing. B's arrival scores nothing until **B** has visited the platform; A entering the box wins | If B's arrival wins, `Action_EnableTriggers` is not reaching the per-unit triggers |
| 7.2 | SW03: A makes the pickup, then lose A | Defeat, with the "lost after the pickup" message | If the mission continues, the per-unit lost trigger was not enabled |
| 7.3 | SW08 from the campaign map | No deployment screen; the authored Growler, F-35As and KC-130Js are present with their authored stores; the F-35As recover to **Langgur** | A deployment screen means blank generation does not do what the guide says |
| 7.4 | SW09: leave the box at 30:00 and return at 34:00; then at 36:00 | Tells us whether `Time=2100` is absolute and whether re-entry counts. Record what completed and when | Either answer is a design answer: the brief says the rule is the box at the moment the window closes |
| 7.5 | SW09: the withdrawal trigger it enables has its own clock | Note whether the box completes immediately on entry or waits | Decides whether a disabled trigger's `Condition_Time` restarts on enable |
| 7.6 | Recovery: order RTB on the Lynx (O3), the Harrier (D3), the U-2 (D7), the VH-3D (D2) and an F-35A (SW08) | Each lands on its `HomeBase` | Name the airframe and the deck; the fit was declared by the two files |
| 7.7 | D3: watch the column and the roadblock from the start | The column **drives** the road toward the distribution point; the roadblock moves onto it | Land units ignoring `Waypoints` means the column objective needs a different shape |
| 7.8 | O3: the Korean ships | Sejong the Great and Daegu appear, fire, and the Lynx flies from Sejong | A missing hull names the mod (3789208859) or its Euromod parent |
| 7.9 | SW01: win at the deadline's last minute; and win while a fatal loss lands in the same update | One outcome only, objectives resolved once | Two endings means the shared exit needs a delay after all |
| 7.10 | SW05 with an Arafura alone | She is `Taskforce1Vessel1`; the mission's texts read correctly for her; the magazine objective fails when her NSM cells are empty | If the authored Anzac is still beside her, the `Replaced` model is wrong |

## What I most expect to be wrong

1. **None of the art appears** (1A) — three keys read out of the vanilla
   campaigns, none of them ever watched working from a mod.
2. **The bought force does not deploy the way the anchor assumes** (2.4).
3. **The VH-3D runs dry** (4.3) — 87% of a radius that rests on a 0.40
   planning fraction.
4. **Objective cancellation does not read as cancelled** (5.2).
5. **A campaign variable does not survive a save** (6.4).
6. **`IsTrue` does not spawn** (6.7, 6.8) — the one comparison the shipped
   data never uses.

Any of those is a design answer, not a bug report — send what you saw and I
will change the model rather than patch the symptom.
