# Workshop listing — paste-ready copy

The reference copy for the Steam page of SEST Integration Pack - Modernised
Campaigns (3812461539) and its collection (3812390790). The live page was
last rewritten on Steam on 4 Oct 2026 and is not in this repository: check it
before pasting. Nothing here is generated; when the campaigns change, edit it
by hand.

The item's Required Items are the load order's Workshop mods, so Subscribe
offers them all in one click, as the collection does; SETUP writes the order.
`publishing.md` (*Dependencies*) has the detail.

Counts (20 Oct 2026, with GPT's fleet, terrain and debrief line, the two
new mods and the old Anzac mod gone): 199 Workshop mods in
`data/load-order.tokens.txt` (200 entries with the pack), 165 named by a mission (REQUIRED-MODS.txt), 526 borrowed
files from 62 mods (CREDITS.txt). Redo them from those files when they
change. The 19-tube pod
is credited to RADF's `adf_lau-3a`: the pod is the game's own `usn_lau-3a`,
which CREDITS.txt never compares against, and RADF's is that file with one
line changed. The MALD brought in the B-2 Spirit on 19 Oct; on 20 Oct the
J-20 balance file brought in the J-20 mod, and the reworked Redback no
longer derives from the Dingtools Weapon Pack's APKWS.

---

## Title

```
SEST Integration Pack - Modernised Campaigns
```

## Short description

```
Four Task Force Mode campaigns (Southern Watch, Southern Reach / Tasman
Shield, Red Line, Sulu Line) and every SEST fix in one Mod Manager entry.
Needs the 199 Workshop mods in the 'SEST - Modernised Campaign Collection'
(3812390790): subscribe to it, then run SETUP.
```

## Description

```
SEST INTEGRATION PACK - MODERNISED CAMPAIGNS

Four Task Force Mode campaigns and every SEST fix in one Mod Manager entry.
A draft world campaign for the Dynamic Campaign Mod is included.

THE CAMPAIGNS
  • Southern Watch (October–November 2028). Twelve connected missions keeping
    Australia's northern sea routes open as a coercion campaign becomes a
    limited regional war. It opens small - one frigate, a Seahawk, a lane
    full of traffic, weapons tight - and does not stay small. Plus ten
    optional operations (six flown by somebody else's force), two
    contingencies and eleven standalone dispatches.
  • Southern Reach / Tasman Shield (December 2028 – March 2029). Twenty-six
    missions, from the Antarctic resupply at 60°S to a ceasefire. A boat sunk
    in the Tasman is missing later; an approach not held reinforces the
    enemy off Sydney.
  • Red Line (November 2028 – February 2029). Six missions and an epilogue
    as the Chinese carrier group commander, won by restraint, escort or
    evasion. Plus two optional operations and a contingency: a submarine
    nobody has claimed, the Japanese escorts coming south, and a pilot in
    the water.
  • Sulu Line (October–November 2028). Seven missions with a Philippine-led
    task group. No free rearm: ammunition comes from supply ships you bought
    or the convoy you escort. Three optional side operations change later
    missions.

HOW IT PLAYS
  • You buy the force. Losses and expenditure carry forward. Partners arrive
    on their own terms; partway through Southern Watch and Southern Reach
    the allied fleet can also be requisitioned at its own navies' prices,
    and in Sulu Line the Thai detachment and one RAN frigate are bought into
    the task group.
  • Finding things matters more often than fleet battles. Civilian traffic
    is everywhere, and neutral losses end operations.
  • Each mission has a planned time and is lost at 1.5 times it; the
    briefing states both.

WHAT IT NEEDS - READ THIS
The campaigns name units from 166 Workshop mods. Subscribe to the collection
'SEST - Modernised Campaign Collection' (3812390790): all 199 of its mods in
one press. Then Mod Manager → Open Folder on this pack, quit the game and
double-click 'SETUP - double-click me.cmd'. It checks the subscriptions,
installs the Anchor Chain preloader and writes the 200-entry load order with
this pack at the top. It is safe to run again.
  • If the Mod Manager offers to move this pack's dependencies above it,
    answer no: that undoes every fix in it. SETUP puts the order back.
  • Some mods still name SeaLifter as a requirement. It is not needed; they
    run without it.
  • A missing mod means a missing unit at best and a mission that will not
    load at worst. Without the collection and SETUP, this is not the
    download for you.
  • Mods marked as made for an older game version load and play.
In the folder: SETUP, REQUIRED-MODS.txt (every mod the campaigns name),
LOAD-ORDER.txt and CREDITS.txt.

CREDIT
A Sea Power unit file is a whole-file override, so 526 files here are other
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

## Change log: 20 Oct 2026

For the update after the 19 Oct one. If the 19 Oct update was never
uploaded, paste its log below this one as well. Two mods joined and one
left: add Combat Cost Tracker (3807187341) and Group Manager (3818251045) to
the collection and to the item's Required Items, and remove the
[DEPRECATED] Anzac Class Frigate (3440622312) from both, before Submit.
The Open Allocation versions left the pack on 21 Oct (the owner's
decision): paste the Description (above) and the Collection description
(below) as well, since both stopped offering them.

```
[h2]20 October 2026[/h2]

[b]Southern Watch[/b]
[list]
[*]Broken Wake is deeper: HMAS Sheean joins the underwater screen, and sinking the armed relay trawler before minute 25 calls off a later missile-boat attack. Stuart's six-knot recovery and the civilians stay at its heart.
[*]O10 Ballistic Shield adds a small RQ-7 field team on Yapen and dispersed ammunition, fuel and command targets.
[*]Three new dispatches: Joint Fires School (2030 artillery training) and The Far Picture, a 2034 air-to-air range flown twice, with the targets' sensors off and then on.
[*]The Open Door, Second Ring and Southern Lifeline revised: B-52Hs with ARRW, RAAF F-35As with JSM, Collins surfacing at the rendezvous.
[*]Missions that start with a loaded deck start with aircraft being prepared.
[/list]

[b]Red Line[/b]
[list]
[*]Three side operations: in Datum the enclave's Y-9 puts a class on the submarine nobody has claimed, and the next mission starts with her position on the plot for fifteen minutes; in The Ships from the North it names the Japanese escorts coming south; in Pilot in the Water your screen races an Australian patrol vessel to a downed J-15 pilot. Four new pages. A Red Line campaign already under way must be started again.
[/list]

[b]Ships and weapons[/b]
[list]
[*]The Ford carries sixteen F-35Cs in a 70-aircraft US Navy wing, whichever hull you pick.
[*]Tomahawk MST Block Va climbs to keep 500 ft over land ahead during cruise; sea-skimming and the terminal attack are unchanged.
[*]J-20A: visual identification at 6 NM and a stronger infrared signature close in. Its radar stealth is unchanged.
[*]The AIM-9L flies on the stock game's figures, like the AIM-9M it now shares the air with.
[*]The new Oliver Hazard Perry long hull's Mk 13 launcher loads its Harpoons and SM-1s.
[/list]

[b]Also[/b]
[list]
[*]Two new mods: Combat Cost Tracker (SEST's units priced in its catalogues) and Group Manager.
[*]The old Anzac Class Frigate mod is no longer needed: the Anzacs come from Euromod - Modern Royal Australian Navy. You can unsubscribe it.
[*]The task-force debrief lists ships lost in a mission again.
[*]Briefings show recognition photos for 54 more classes, the P-8A among them.
[*]Follows the 20 Oct mod updates: Ford, Mogami, Wasp, F-35C, the OHP long hull and Red Storm Arsenal's Chinese missiles.
[/list]

[b]The allied fleet[/b]
[list]
[*]Southern Watch: from Weapons Free the standard campaign also sells the allied fleet, at its own navies' prices: 52 ship classes from eleven navies - carriers, amphibious ships, replenishment ships, destroyers and frigates - and the RAN's second Canberra-class LHD, with 19 allied aircraft types where a mission can launch and recover them. The windows before Weapons Free sell what they did.
[*]Southern Reach: the same ships from Tasman Crossing, with the 10 allied aircraft types its missions can fly.
[*]Red Line: the PLAN's own Type 901 and Type 903A supply ships, from the first force allocation, before Trailing Contact.
[*]Carriers and amphibious ships come without aircraft, as every ship you buy does. No submarine is sold, and no ship a mission names.
[*]A campaign already under way may not show them: start a new campaign to see them.
[/list]

[b]Every campaign[/b]
[list]
[*]The Open Allocation versions are retired: what they sold beyond each story's own list is in the standard campaigns now, from the windows above, so each campaign is listed once. A campaign under way in an Open Allocation version cannot be continued: start the standard campaign.
[/list]

[b]Fixes[/b]
[list]
[*]Southern Watch, The Quiet Passenger: Paper Trail's lead on the passenger appears again, beside Southern Cross's datum on the submarine.
[*]Red Line: briefings and the Situation window no longer show the trailing submarines' class or navy before you classify them. Civilian ships fly their own flags, and the command-net reports no longer name officers.
[*]Every campaign: a ship or aircraft your orders protect is labelled "Protected - do not engage" under its briefing photo, not "Expected opposition". In The Twelve-Mile Line the frigate and her helicopter read "Opposition - do not fire first".
[*]Sulu Line, Service at Sea: losing Sulu Provider no longer ends the mission. Complete the rendezvous without her and she is missing at The Aborlan Battery.
[/list]

[b]Install[/b]
[list]
[*]Subscribe to all again for the two new mods, then close the game and run SETUP. SETUP leaves the old Anzac mod out of the order.
[/list]
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
[*]The B-2's ADM-160 MALD decoy glides at its release height and dives at the end, instead of dropping to skim the sea at 6 ft.
[*]The JH-7A carries one self-protection jammer instead of two AN/ALQ-99s.
[*]Names for the Italian Skyguard SAM and the F-16C Block 40 in the South Korean navy mod; the RAN Sea King Mk.50A/B's squadrons load.
[*]Follows the latest mod updates: the PAC-3 MSE's ceiling, HMAS Hobart's damage model, the EA-18G's EO views.
[/list]

[b]Install[/b]
[list]
[*]SeaLifter is no longer listed as a requirement. The mods that name it run without it, so nothing needs a manual install.
[*]Nothing new to subscribe to: the same 198 Workshop mods.
[/list]
```

## Collection description (3812390790)

Keep the pinned "Read first" discussion's install steps in step with it.

```
Everything the SEST Integration Pack's four campaigns need: 199 Workshop mods
plus the pack itself (3812461539).

1. Subscribe to all.
2. In the Mod Manager, open the SEST Integration Pack's folder, quit the game
   and double-click 'SETUP - double-click me.cmd'. It checks the
   subscriptions, installs the Anchor Chain preloader and writes the load
   order, with the pack at the top.
3. If the Mod Manager offers to move the pack's dependencies above it, say
   no. Running SETUP again puts the order back.

Nothing needs a manual install: some mods still name SeaLifter, but they run
without it.

Campaigns: Southern Watch, Southern Reach / Tasman Shield, Red Line and Sulu
Line, plus a draft world campaign for the Dynamic Campaign Mod. All fiction,
set in 2028-29.
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
