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

Two warnings are **expected** and are not faults: `dropped stale workshop
entry` naming the two mods the repo has not catalogued yet (Automatic SAR and
the Euromod South Korean Navy — see the install document's step 5), and the
`component ApproximateVersion values differ` note from the consolidation.
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
| 1.1 | Campaign list | **SOUTHERN WATCH** present, 31 entries | Campaign not surfaced by the Mod Manager. Go to 1.3 and work from the browser |
| 1.2 | Start it | The 18 October card, then WHITE WATER | Note which of the two it stops on |
| 1.3 | Mission browser → `Southern Watch 01 - White Water` | Loads, ships and aircraft visible | A missing unit names the mod that failed to load |

Load one mission from each theatre before going further — **01 White Water**,
**08 The Open Door**, **11 Fujian's Shadow**. They use the most different
content. A texture or model that fails shows up here, not in the rules.

## 1A — the art (new, and entirely unverified)

The pack now ships 32 generated PNGs and points `campaign.ini` at them with
three keys read out of the vanilla campaigns. Whether a **mod-supplied**
campaign's art loads the way the base game's does has never been watched
happen, and the vanilla export carries no PNGs to compare against — so every
row here is a guess until you look.

| # | Do | Expect | If not |
|---|---|---|---|
| 1A.1 | Open the campaign list | A dark chart behind the list: graticule, numbered marks 01–12, a compass rose, SOUTHERN WATCH bottom-left | No backdrop = `BackgroundImage` is either ignored for mods, or ignored on `DisplayFormat=Legacy`. Say which, and try `MapView` |
| 1A.2 | Look at a mission tile | A card: big number, big title, a blue plot of own force with the objective ring | A blank tile = `TileImagePath_en` unread. A tile but no card on the detail pane = `MissionImage_en` unread |
| 1A.3 | Is the card **readable** at tile size? | The number and name carry it; the plot is a shape, not detail | Say what is too small — the card is generated, so this is a one-line change |
| 1A.4 | Open a story card (entry 1, "White Water 18 October") | A cream newspaper sheet, headline and two columns of type | A blank page = the Viewbox/Image binding in the XAML is wrong |
| 1A.6 | Step through the pages before mission 2 | Three different documents: a typed INTSUM with a FICTION banner, a ship's log on ruled paper, a teleprinter cable | Tells us whether all four forms render, not just the press sheet |
| 1A.5 | Is the backdrop cropped, stretched or letterboxed? | It should fill | Tell me the shape of what you see. 1920×1080 is a guess; nothing in the export states the wanted aspect |

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
| 2.5 | Finish SW01, open the builder before SW02 | The list has **grown** to 6 — Hobart, Supply and the P-8 added |
| 2.6 | Before SW12 | Aircraft only. **No hulls for sale** |

2.4 is the one to watch. If the bought ship is missing, misplaced, or the
authored ship is still there beside it, the anchor model is wrong and the
whole economy sits on it.

## 3 — Air tasking (rebuilt twice; rows must pair with cockpits)

| # | Do | Expect |
|---|---|---|
| 3.1 | Before SW01, open Air Tasking | Two flights: **Ship's Flight** (1 slot) and **Maritime Patrol** (1) |
| 3.2 | Assign a bought MH-60R to Ship's Flight | It takes the slot and is airborne at mission start |
| 3.3 | Before SW06 | **Combat Air Patrol** (2 slots) and **Maritime Patrol** (1) |
| 3.4 | SW07 | **No air tasking offered at all** — every aircraft in it is a named asset |
| 3.5 | Anywhere | No flight offered with **0 slots**, and no slot with no flight |

3.5 is the invariant: 22 rows, each pairing exactly with its sections. One
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

6.4 is the real test. Declaration, write and read are all present in the files
and statically consistent; whether the campaign carries a flag across a save
is the one thing no amount of reading can settle.

## What I most expect to be wrong

1. **None of the art appears** (1A) — three keys read out of the vanilla
   campaigns, none of them ever watched working from a mod.
2. **The bought force does not deploy the way the anchor assumes** (2.4).
3. **The VH-3D runs dry** (4.3) — 87% of a radius that rests on a 0.40
   planning fraction.
4. **Objective cancellation does not read as cancelled** (5.2).
5. **A campaign variable does not survive a save** (6.4).

Any of those is a design answer, not a bug report — send what you saw and I
will change the model rather than patch the symptom.
