# Workshop listing — paste-ready copy

The reference copy for the Steam page of SEST Integration Pack - Modernised
Campaigns (3812461539) and its collection (3812390790). The live page was
last rewritten on Steam on 4 Oct 2026 and is not in this repository: check it
before pasting. Nothing here is generated; when the campaigns change, edit it
by hand.

The item's Required Items are the load order's Workshop mods, so Subscribe
offers them all in one click, as the collection does; SETUP writes the order.
`publishing.md` (*Dependencies*) has the detail.

Counts (19 Oct 2026, with the 19-tube Redback pod): 198 Workshop mods in
`data/load-order.tokens.txt` (199 entries with the pack), 164 named by a
mission (REQUIRED-MODS.txt), 525 borrowed files from 62 mods (CREDITS.txt).
Redo them from those files when they change. The 525th, the 19-tube pod, is
credited to RADF's `adf_lau-3a`: the pod is the game's own `usn_lau-3a`,
which CREDITS.txt never compares against, and RADF's is that file with one
line changed.

---

## Title

```
SEST Integration Pack - Modernised Campaigns
```

## Short description

```
Four Task Force Mode campaigns (Southern Watch, Southern Reach / Tasman
Shield, Red Line, Sulu Line) and every SEST fix in one Mod Manager entry.
Needs the 198 Workshop mods in the 'SEST - Modernised Campaign Collection'
(3812390790): subscribe to it, then run SETUP.
```

## Description

```
SEST INTEGRATION PACK - MODERNISED CAMPAIGNS

Four Task Force Mode campaigns and every SEST fix in one Mod Manager entry.
Each campaign also comes as an Open Allocation version, and a draft world
campaign for the Dynamic Campaign Mod is included.

THE CAMPAIGNS
  • Southern Watch (October–November 2028). Twelve connected missions keeping
    Australia's northern sea routes open as a coercion campaign becomes a
    limited regional war. It opens small - one frigate, a Seahawk, a lane
    full of traffic, weapons tight - and does not stay small. Plus ten
    optional operations (six flown by somebody else's force), two
    contingencies and eight standalone dispatches.
  • Southern Reach / Tasman Shield (December 2028 – March 2029). Twenty-six
    missions, from the Antarctic resupply at 60°S to a ceasefire. A boat sunk
    in the Tasman is missing later; an approach not held reinforces the
    enemy off Sydney.
  • Red Line (November 2028 – February 2029). Six missions and an epilogue
    as the Chinese carrier group commander, won by restraint, escort or
    evasion.
  • Sulu Line (October–November 2028). Seven missions with a Philippine-led
    task group. No free rearm: ammunition comes from supply ships you bought
    or the convoy you escort. Three optional side operations change later
    missions.

HOW IT PLAYS
  • You buy the force. Losses and expenditure carry forward; partners arrive
    on their own terms and are not yours to keep.
  • Finding things matters more often than fleet battles. Civilian traffic
    is everywhere, and neutral losses end operations.
  • Each mission has a planned time and is lost at 1.5 times it; the
    briefing states both.

WHAT IT NEEDS - READ THIS
The campaigns name units from 164 Workshop mods. Subscribe to the collection
'SEST - Modernised Campaign Collection' (3812390790): all 198 of its mods in
one press. Then Mod Manager → Open Folder on this pack, quit the game and
double-click 'SETUP - double-click me.cmd'. It checks the subscriptions,
installs the Anchor Chain preloader and writes the 199-entry load order with
this pack at the top. It is safe to run again.
  • If the Mod Manager offers to move this pack's dependencies above it,
    answer no: that undoes every fix in it. SETUP puts the order back.
  • SeaLifter is not in the collection and needs a manual install (the B-2,
    A-10A, Su-25, Mi-8 and Type 003/004 carriers name it).
  • A missing mod means a missing unit at best and a mission that will not
    load at worst. Without the collection and SETUP, this is not the
    download for you.
  • Mods marked as made for an older game version load and play.
In the folder: SETUP, REQUIRED-MODS.txt (every mod the campaigns name),
LOAD-ORDER.txt and CREDITS.txt.

CREDIT
A Sea Power unit file is a whole-file override, so 525 files here are other
authors' files with edits, each 90% or more unchanged, from 62 Workshop mods.
CREDITS.txt lists every one, measured by diffing against the collection.
Every photograph is real and credited. If you wrote one of those mods and
would rather this pack did not carry your file, say so and it will change.

FICTION, LANGUAGE, STATUS
Every nation, unit, ship name, incident and date is invented; the campaigns
take no position on any real dispute. English only. Built for Sea Power
0.8.6: every unit, squadron, loadout and weapon in every mission is checked
to resolve on every build, but balance is not, and most missions have not
been played to completion. Feedback on difficulty and pacing is wanted.
```

## Change log: 19 Oct 2026

For the update after the 18 Oct one (`8732b75f`). Steam renders the BBCode.
The 198 required mods are unchanged, so the Required Items and the
collection stay as they are.

```
[h2]19 October 2026[/h2]

[b]AGR-30 Redback[/b]
[list]
[*]One upgraded 70 mm guided rocket replaces SEST's two (the 8 NM laser APKWS II-ER is retired): infrared fire and forget to 30 NM, a boost then a cruise at about 600 knots, a shallow climb and a dive onto the target. Aircraft and drones first, ships and land targets second.
[*]A new "SEST Redback Strike" loadout on the A-10s, Apaches, MQ-9s, Seahawks, the F-16CM, the RAAF F/A-18A and the Super Hornets. Every original loadout is still there; the Ocean Apache's "SEST APKWS-ER Strike" goes with its rocket.
[*]19-round LAU-3 pods on single pylons, 7-round LAU-68s on racks and the MQ-9s, each on its own mount. The Super Hornets fly the F/A-18A's layout: wing tanks, two pods side by side outboard of them, a 19-round pod on the outer pylon.
[/list]

[b]Southern Watch (the 18 October play test)[/b]
[list]
[*]Air Tasking rows offer every loadout an aircraft can fly for the job (the strike row: 8 to 31). Flight deck and airbase preparation is allowed from the start.
[*]Steel Highway's beacon datum is a one-minute record, not a contact. After the Wake is a life-raft search with a new, snorkelling boat. Southern Cross adds two F-35As and an optional drone kill.
[*]Rig Seventeen needs a three-minute hover over the rig, and HMAS Canberra carries her own Apaches and Seahawks. The Quiet Passenger: search, classify, stop her. Weapons Free recovers to Darwin.
[/list]

[b]Fixes[/b]
[list]
[*]The JH-7A carries one self-protection jammer instead of two AN/ALQ-99s.
[*]Names for the Italian Skyguard SAM and the South Korean F-16C Block 40; the RAN Sea King Mk.50A/B's squadrons load.
[*]Follows the latest mod updates: the PAC-3 MSE's ceiling, HMAS Hobart's damage model, the EA-18G's EO views.
[/list]

Nothing new to subscribe to.
```

## Collection description (3812390790)

Keep the pinned "Read first" discussion's install steps in step with it.

```
Everything the SEST Integration Pack's four campaigns need: 198 Workshop mods
plus the pack itself (3812461539).

1. Subscribe to all.
2. In the Mod Manager, open the SEST Integration Pack's folder, quit the game
   and double-click 'SETUP - double-click me.cmd'. It checks the
   subscriptions, installs the Anchor Chain preloader and writes the load
   order, with the pack at the top.
3. If the Mod Manager offers to move the pack's dependencies above it, say
   no. Running SETUP again puts the order back.

SeaLifter is not in the collection and needs a manual install.

Campaigns: Southern Watch, Southern Reach / Tasman Shield, Red Line and Sulu
Line, each with an Open Allocation version, plus a draft world campaign for
the Dynamic Campaign Mod. All fiction, set in 2028-29.
```

## Tags, images, and what to leave off

Tags: `Campaign`, `Missions`, `English`.

Preview: `StreamingAssets\SEST-preview.jpg` (124 KB; the image picker only
browses StreamingAssets). Screenshots, from `campaigns/sest-southern-watch/art/`
inside the pack: `00_campaign_background.png`, `southern_watch_01_sheet.png`,
`00_opening_image.png`, `southern_watch_08_sheet.png`, then an in-game shot of
the campaign map that you take yourself.

Leave off the page: the repository and how the pack is built, any claim that
it is balanced or play-tested, and any promise of translations or of support
for another mod list.
