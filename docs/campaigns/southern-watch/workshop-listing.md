# Workshop listing — paste-ready copy

The reference copy for the Steam page of SEST Integration Pack - Modernised
Campaigns (3812461539) and its collection (3812390790). The live page was
last rewritten on Steam on 4 Oct 2026 and is not in this repository: check it
before pasting. Nothing here is generated; when the campaigns change, edit it
by hand.

Every block below is ready to paste: Steam BBCode (`[h1]`-`[h3]`, `[b]`,
`[list]`/`[olist]` with `[*]`, `[url=...]`), one line per paragraph or list
item. Steam keeps every line break, so never re-wrap a block: until 23 Oct
2026 the description and the collection description were plain text wrapped
at 76 columns, and Steam broke their sentences across lines.
`tools/tests/test_workshop_listing.py` checks the blocks stay that way and
under Steam's 8,000 characters.

The item's Required Items are the load order's Workshop mods, so Subscribe
offers them all in one click, as the collection does; SETUP writes the order.
`publishing.md` (*Dependencies*) has the detail.

Counts (24 Oct 2026, the World Sandbox branch `8e72f353` with the 24 Oct
capture): 199 Workshop mods in `data/load-order.tokens.txt` (200 entries
with the pack), 165 named by a mission (REQUIRED-MODS.txt), 528 borrowed
files from 64 mods (CREDITS.txt; `sest-dev/jolly-ride-rptj4t` without the
World Sandbox branch has 527 from 63: the extra file is the Chilean
frigate's save alias variants). Redo them from
those files when they change. The 19-tube pod
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
Four Task Force Mode campaigns (Southern Watch, Southern Reach / Tasman Shield, Red Line, Sulu Line) and every SEST fix in one Mod Manager entry. Needs the 199 Workshop mods in the 'SEST - Modernised Campaign Collection' (3812390790): subscribe to it, then run SETUP.
```

## Description

```
[h1]SEST Integration Pack - Modernised Campaigns[/h1]
Four Task Force Mode campaigns, two world campaigns for the Dynamic Campaign Mod, combat costs for every unit and every SEST fix in one Mod Manager entry.

[h2]The campaigns[/h2]
[list]
[*][b]Southern Watch[/b] (October–November 2028). Twelve connected missions keeping Australia's northern sea routes open as a coercion campaign becomes a limited regional war. It opens small - one frigate, a Seahawk, a lane full of traffic, weapons tight - and does not stay small. Plus ten optional operations (six flown by somebody else's force), two contingencies and eleven standalone dispatches.
[*][b]Southern Reach / Tasman Shield[/b] (December 2028 – March 2029). Twenty-six missions, from the Antarctic resupply at 60°S to a ceasefire. A boat sunk in the Tasman is missing later; an approach not held reinforces the enemy off Sydney.
[*][b]Red Line[/b] (November 2028 – February 2029). Six missions and an epilogue as the Chinese carrier group commander, against missile craft, Q-ships and intercepting fighters on short clocks, where restraint still wins as often as firepower. Plus two optional operations and a contingency: a submarine nobody has claimed, the Japanese escorts coming south, and a pilot in the water.
[*][b]Sulu Line[/b] (October–November 2028). Seven missions with a Philippine-led task group. No free rearm: ammunition comes from supply ships you bought or the convoy you escort. Three optional side operations change later missions.
[*][b]World Sandbox 2028[/b] (draft, Dynamic Campaign Mod). One persistent 2028 world on the strategic map: real bases, finite fleets, patrols, purchases and replenishment, and every contact becomes a battle. The [b]Regional Expansion[/b] (preview) adds 15 bases and 26 RED forces from the Baltic to Iran, with their own supply ships. Start either as a new campaign; neither has been played through yet.
[/list]

[h2]How it plays[/h2]
[list]
[*]You buy the force. Losses and expenditure carry forward. Partners arrive on their own terms. Partway through Southern Watch and Southern Reach, and in Red Line from the start, every force allocation offers the whole roster with the allied fleet, or the PLAN's supply ships. In Sulu Line the Thai detachment and one RAN frigate are bought into the task group.
[*]Finding things matters more often than fleet battles. Civilian traffic is everywhere, and neutral losses end operations.
[*]Each mission has a planned time and is lost at 1.5 times it; the briefing states both.
[/list]

[h2]Combat costs[/h2]
With the Combat Cost Tracker from the collection, every weapon, ship, aircraft and land unit has a price, historical and current. Estimates are labelled, and chaff, flares, sonobuoys, drop tanks and pods count.
[list]
[*]F11 in a mission shows what the mission has cost so far.
[*]F11 in the Task Force menu shows the campaign's totals and every completed mission, in a window you can move and resize; the task-force debrief adds the mission's and the campaign's cost.
[*]Weapons fired, units lost and the stores lost with them carry through the campaign.
[/list]

[h2]What it needs - read this[/h2]
The campaigns name units from 165 Workshop mods. Subscribe to the collection [url=https://steamcommunity.com/sharedfiles/filedetails/?id=3812390790]SEST - Modernised Campaign Collection[/url]: all 199 of its mods in one press. Then Mod Manager → Open Folder on this pack, quit the game and double-click [b]SETUP - double-click me.cmd[/b]. It checks the subscriptions, installs the Anchor Chain preloader and writes the 200-entry load order with this pack at the top. It is safe to run again.
[list]
[*]If the Mod Manager offers to move this pack's dependencies above it, answer no: that undoes every fix in it. SETUP puts the order back.
[*]Some mods still name SeaLifter as a requirement. It is not needed; they run without it.
[*]A missing mod means a missing unit at best and a mission that will not load at worst. Without the collection and SETUP, this is not the download for you.
[*]Mods made for an older game version load and play; SETUP marks them compatible, so the Mod Manager stops warning about them.
[/list]
In the folder: SETUP, REQUIRED-MODS.txt (every mod the campaigns name), LOAD-ORDER.txt and CREDITS.txt.

[h2]Credit[/h2]
A Sea Power unit file is a whole-file override, so 528 files here are other authors' files with edits, each 90% or more unchanged, from 64 Workshop mods. CREDITS.txt lists every one, measured by diffing against the collection. Every photograph is real and credited. If you wrote one of those mods and would rather this pack did not carry your file, say so and it will change.

[h2]Fiction, language, status[/h2]
Every nation, unit, ship name, incident and date is invented; the campaigns take no position on any real dispute. English only. Built for Sea Power 0.8.7: every unit, squadron, loadout and weapon in every mission is checked to resolve on every build, but balance is not, and most missions have not been played to completion. SEST's code (the Tomahawk terrain fix, the debrief, the combat cost windows, the towed-sonar guard and, with Contact Log, the UI follow-up) runs only on Sea Power 0.8.7 Build 261021 and switches itself off on any other. Feedback on difficulty and pacing is wanted.
```

## Change log: integration of the owner's PC state, 28 Oct 2026

For the next upload, which also carries the SETUP update below and, if not
yet pasted, the 24 Oct block. Not to be uploaded before the Workshop refresh
capture (`chore/workshop-refresh-20261027`) is integrated and the release
gate passes: until then the pack would still carry the old Modern US Navy
and Italian FREMM files. Before Submit:

- Run SETUP from the Workshop copy on the PC. Expect THE REDFOR MOD to count
  as already marked, and Contact Log's RunProbe to become None if it is still
  F8 (a ToggleWindow of F9 is kept).
- Player.log must show three `[SEST Runtime] ... correction installed` lines
  (terrain, debrief, towed sonar) and, with Contact Log 1.0.1,
  `[SEST UI Follow-up] 1.4.2 input fix installed`. Take out any line below
  whose plugin did not install.
- The owner decides whether to keep the Quick Load line (UI Follow-up moves
  plain F9 to Ctrl+F9) and whether to mention the unexplained 27 Oct crash
  with both plugins on.

```
[h2]28 October 2026[/h2]

[b]Interface and costs[/b]
[list]
[*]SEST's runtime plugin is now 1.5.0. F11 opens game-styled cost windows in a mission and in the Task Force menu; move them by the title bar and resize them at the edges, and with Pop-Out Windows they go to a second screen. The debrief shows mission and campaign cost, with the details in F11.
[*]With Contact Log 1.0.1 and Group Manager 0.2.17, Contacts and Group Manager can pop out to a second screen. Own units are plotted while paused during preparation, and a towed sonar with an incomplete link no longer stops the game's update.
[*]New: SEST UI Follow-up, for players of Contact Log 1.0.1. Space and +/- no longer open or close Contacts, Group Manager gets a Stock UI / Enhanced UI switch, and the live F11 window stops rebuilding its price lists twice a second. Without Contact Log, or on another game build, it does nothing.
[*]With UI Follow-up active, Quick Load moves from F9 to Ctrl+F9; any other Quick Load key is kept. Once you press Accept in Options, Ctrl+F9 stays after you unsubscribe; set Quick Load back in Options.
[/list]

[b]Campaigns[/b]
[list]
[*]Sulu Line: Philippine airfields no longer come with a free 1970s U.S. air wing; a field holds what you buy for it and the mission's own flights. The Navy helicopter is offered as the AW109E LAH, then the AUH-76. The RAN MH-60R is on sale with the Anzac before Service at Sea and The Aborlan Battery. Deck fits for the H-76, the Thai Seahawk and the MH-60R on the Jose Rizal, Miguel Malvar, Naresuan, Anzac and BRP Tarlac (not yet confirmed in game). Start a new campaign or load a mission fresh to see these.
[*]World Sandbox and Regional Expansion: the US Navy's twelve P-8As are a real P-8A Poseidon (U.S. Navy 2027's) instead of a P-3 Orion body. Bases, numbers and price are unchanged. Start a new campaign to see it.
[*]Both P-8s' Harpoons now get a guidance channel: one P-8 could not fire its AntiShip Harpoons at all, the other fired them with no midcourse updates.
[/list]

[b]SETUP[/b]
[list]
[*]SETUP now checks mod versions the way the game does. After a game update, or a step back to an earlier version, it renews the marks it made, so the not-compatible warning does not come back. Mods made for a newer game version are named and left alone.
[*]If you use Contact Log, SETUP frees its default F6 and F8 keys, which the game also uses. Keys you changed yourself are kept.
[/list]
```

## Change log: SETUP update, after 25 Oct 2026

For the upload after `b1449201`. One change a player sees: SETUP marks the
collection's mods made for an older game version compatible (66 of them on
0.8.7), so the Mod Manager stops listing them at start-up. Before Submit, run
SETUP from the Workshop copy on the PC and check that the warning is gone.

```
[h2]SETUP update[/h2]
[list]
[*]SETUP now marks the mods made for an older game version compatible, so the Mod Manager stops listing them as not compatible at start-up. They loaded and played before; only the warning goes. Close the game and run SETUP again to get it, and again after Steam updates your mods.
[*]To put those mods' own files back, run sest-setup.ps1 -RestoreModFiles from a console in the pack folder.
[/list]
```

## Change log: 24 Oct 2026

The 25 Oct upload (`b1449201`, 4,299 files) carried the rest of this build
and the HH-60H fix; if its change log did not have this block, paste it with
the next update.

Everything after `c1bd1f4b` (the Seahawk), through `dc46eba2`, plus the World
Sandbox regional expansion (PR #44). **Uploaded 24 Oct 2026** from `8e72f353`
on `feature/world-sandbox-regional-expansion-20261024`, the install IN LINE at
4,297 files; PR #44 merged into `sest-dev/jolly-ride-rptj4t` the same day.
That upload's Steam change log has the Regional Expansion entry only.
Everything else in the block below
(combat costs, Red Line, Steel Highway, the SEST menu, the mod updates) is in
that build but not yet in a Steam change log: paste it with the next update,
above the 20 Oct block if that has not been uploaded either. The required mods
are unchanged by the 24 and 25 Oct captures. The costs lines rest on mocked tests and
the owner's report from the uploaded build: the Task Force panel at the left
and the stores carry-over work (`docs/playtests/campaign-costs-panel-20261024.md`,
steps 4, 6 and 7). Step 3, the in-mission panel, was not reported. The same
report has the Regional Expansion starting as a new campaign
(`docs/playtests/world-regions-20261024.md`, step 4); its line keeps
"(preview)" until its patrols, supply and saves have been seen.

```
[h2]24 October 2026[/h2]

[b]Combat costs[/b]
[list]
[*]Every weapon, ship, aircraft and land unit in the collection now has a price, current and historical (land units priced by SEST, which the tracker does not cover). Estimates are labelled as estimates, and chaff, flares, sonobuoys, drop tanks and pods now count.
[*]227 prices checked against published sources, from the Mk 82 to the GBU-57 and the AN/TPY-2 radar.
[*]F11 in a mission shows this mission's costs. F11 in the Task Force menu shows the campaign's totals, with one line per mission.
[*]The task-force debrief adds the mission's and the campaign's cost; the detail is in F11.
[*]Stores lost with a sunk ship or downed aircraft now stay in the campaign total; the next mission used to erase them.
[/list]

[b]Campaigns[/b]
[list]
[*]Red Line: shorter, harder missions. Missile craft attack Fujian in Trailing Contact; torpedo and missile attacks hit the tanker leg; fighters intercept in The Other Picture and The Ships from the North; a Q-ship presses in The Order to Withdraw and The Quiet Side. A Red Line campaign already under way keeps its old missions until started again.
[*]Southern Watch, Steel Highway: the submarine starts anywhere within 35 NM of its reported position, which shows on the plot for one minute.
[*]World Sandbox 2028 - Regional Expansion (preview): a second Dynamic Campaign Mod world, 15 more bases and 26 more RED forces from the Baltic to Iran, with their own supply ships. Start it as a new campaign.
[*]World Sandbox: starts again after the Chilean frigate and HH-60H renames.
[/list]

[b]Also[/b]
[list]
[*]The SEST menu no longer covers scenario pictures, briefing images and maps.
[*]Follows the 24 and 25 Oct mod updates: Modern US Navy, U.S. Navy 2027, US Naval Aviation, F-35C, Modern US Airbase, THE REDFOR MOD and the Anchorchain, RAN, Chilean, Scandinavian and JMSDF Euromod packs.
[/list]
```

## Change log: 20 Oct 2026

For the update after the 19 Oct one. If the 19 Oct update was never
uploaded, paste its log below this one as well. Two mods joined and one
left: add Combat Cost Tracker (3807187341) and Group Manager (3818251045) to
the collection and to the item's Required Items, and remove the
[DEPRECATED] Anzac Class Frigate (3440622312) from both, before Submit.
The Open Allocation versions left the pack on 21 Oct (the owner's
decision), and the standard campaigns now do what they did from Weapons
Free, Tasman Crossing and Red Line's first force allocation: paste the
Description (above) and the Collection description (below) as well, since
both stopped offering the versions and the Description says when everything
is on sale. Keep the log under 8,000 characters (23 Oct, with the Redback
line under Fixes as it now reads: 7,874 with the 19 Oct block below it,
7,966 if each line break counts as two).

On 22 Oct the game moved to Sea Power 0.8.7 and ten mods updated; the log
covers both. On 23 Oct seven mods updated their files and the YF-23 its code
alone (`docs/workshop-refresh-20261023-review.md`): the code 0.8.7 had
switched off in six of them (the Fury's, the EC-2's, the K5 KRAKEN's, the
MV-75's, the YF-23's and the Saronic Corsair's) loads again, so the log says
it is on again where it had said it was off. SEST needed no change. SEST's
runtime plugin switched itself off on 0.8.7 and was matched to it on 23 Oct
(`integration/runtime-fixes/README.md`), so the log claims its two
corrections again (the Tomahawk MST's 500 ft over land, the debrief's lost
ships, in missions the player picks a force for). Before Submit, check that
Player.log shows both `[SEST Runtime] ... correction installed` lines (it
did on 23 Oct, after syncing 990dd7f9, and in the 23 Oct capture, 87c0feb5,
taken at 28f62cd3). If one is missing (`terrain correction not installed` or
`debrief correction not installed`), take out that correction's line; if
both are (`inactive`, or two `not installed` lines), take out both lines and
the second sentence after "Built for Sea Power 0.8.7.". The OHP long hull's
Mk 13 is Modern US Navy's own fix since 22 Oct, so the log credits the
author, not SEST; and it says of the SM-6 Block I only that it keeps 300 s:
claim its 260 NM once a shot past 240 NM has been seen in game. The required
mods are unchanged by the 22 and 23 Oct captures.

The AGR-30 Redback changed twice on 23 Oct
(`docs/playtest-20261023-redback.md`). In the game the RAN MH-60R first
listed it against a boat and never fired it, its pod in the bottom of the
quad Hellfire launcher; on the next build (`57375598`) it fired. So the
Redback line is under Fixes, and the 19 Oct block's first AGR-30 item ("One
upgraded 70 mm guided rocket...", 275 characters) is gone: it described the
round of the morning of 19 Oct (infrared, 600 knots, aircraft first) and was
wrong anyway, and without it the two logs stay under 8,000 with each line
break counted as two. Only the firing has been seen. The rest of the line is
the build after `57375598`, made from the owner's second report that day:
the MH-60R's eight 7-tube pods on its Hellfire launcher with its tanks
kept, `TerminalApproachDist` back to 2 NM so that short shots climb, a
motor that works when an aircraft fires it, and a straight-line slow-down
to the 150-knot cruise. Nobody has seen those yet. Before Submit, check them
(the test card's first things, 6): a salvo leaving the 7-tube pods, the
pods on the launcher clear of its rails, the 2 km climb on a shot from about
4 NM, and the steady slow-down to about 150 knots over roughly a minute. If
the upper pods clip the lower rails and the lower pair comes out, the line
says four pods, not eight; for anything else that is wrong, take out its
words or fix it first. Look at the S-70B-2's SEST Redback Strike in the
loadout preview as well (the same test card item): if its pod sits inside
the Hellfire launcher, take the two S-70B-2 rows out of ROLLOUT in
`integration/allied-fixes/build_patch.py` and rebuild.

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
[/list]

[b]Also[/b]
[list]
[*]Two new mods: Combat Cost Tracker (SEST's units priced in its catalogues) and Group Manager.
[*]The old Anzac Class Frigate mod is no longer needed: the Anzacs come from Euromod - Modern Royal Australian Navy. You can unsubscribe it.
[*]The task-force debrief lists ships lost in missions you pick a force for.
[*]Briefings show recognition photos for 54 more classes, the P-8A among them.
[*]Follows the 20 Oct mod updates: Ford, Mogami, Wasp, F-35C, the OHP long hull and Red Storm Arsenal's Chinese missiles.
[/list]

[b]Sea Power 0.8.7 and the 22-23 October mod updates[/b]
[list]
[*]Built for Sea Power 0.8.7. The Tomahawk MST and debrief corrections are checked against it and switch themselves off on any other build.
[*]The SM-6 Block I keeps the 300 s flight time Euromod's Anchorchain Expansion gave it on 19-21 Oct; with the preloader it would otherwise be held to 240 s.
[*]Follows the 22 Oct mod updates: Chile's renamed ships in the world campaign, the Wasp's new recovery circuits, the Juan Carlos I's new deck loadouts in The Relief Ship, and the latest Modern US Navy (which now fixes the OHP long hull's Mk 13 itself; SEST's repair is retired), US Naval Aviation, Spanish, JMSDF and Euromod packs.
[*]With their authors' 23 Oct updates, the parts of other mods that Sea Power 0.8.7 had switched off are on again: the Fury's Drone Control, the EC-2's radio and data-link jamming, the K5 KRAKEN's one-way attack, the Saronic Corsair's order hooks, the MV-75's systems hook and the YF-23 pack's runtime fixes. SEST needed no change.
[/list]

[b]Open Allocation in the standard campaigns[/b]
[list]
[*]Southern Watch: from Weapons Free every force allocation offers the whole roster and the allied fleet, at its own navies' prices: 52 ship classes from eleven navies - carriers, amphibious ships, replenishment ships, destroyers and frigates - and the RAN's second Canberra-class LHD, with 19 allied aircraft types where a mission can launch and recover them. The windows before Weapons Free keep the story's own lists.
[*]Southern Reach: the same from Tasman Crossing, with the 10 allied aircraft types its missions can fly. The windows before it keep the story's own lists.
[*]Red Line: from the first force allocation, before Trailing Contact, every force allocation offers the whole roster and the PLAN's own Type 901 and Type 903A supply ships. The Quiet Side tasks only the ship's flight, so a fixed-wing aircraft bought for it will not fly.
[*]Carriers and amphibious ships come without aircraft, as every ship you buy does. No submarine is sold, and no ship a mission names. Some operations still limit what sails.
[*]The Open Allocation versions are retired, because the standard campaigns now do this: each campaign is listed once. Sulu Line's version is retired too: its story offers the whole roster from Service at Sea. A campaign under way in an Open Allocation version cannot be continued: start the standard one.
[*]A standard campaign already under way may keep its old windows: start it again to get this.
[/list]

[b]Fixes[/b]
[list]
[*]Southern Watch, The Quiet Passenger: Paper Trail's lead on the passenger appears again, beside Southern Cross's datum on the submarine.
[*]Red Line: briefings and the Situation window no longer show the trailing submarines' class or navy before you classify them. Civilian ships fly their own flags, and the command-net reports no longer name officers.
[*]Every campaign: a ship or aircraft your orders protect is labelled "Protected - do not engage" under its briefing photo, not "Expected opposition". In The Twelve-Mile Line the frigate and her helicopter read "Opposition - do not fire first".
[*]Sulu Line, Service at Sea: losing Sulu Provider no longer ends the mission. Complete the rendezvous without her and she is missing at The Aborlan Battery.
[*]AGR-30 Redback: the Seahawks fire it (seen 23 Oct). The MH-60R carries eight Redback pods on its Hellfire launcher in place of the Hellfires, keeping its fuel tanks. Short shots climb to 2 km, the motor now works when fired from aircraft, and the rocket slows steadily to its 150-knot cruise.
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
Everything the SEST Integration Pack's campaigns need: 199 Workshop mods plus the pack itself, [url=https://steamcommunity.com/sharedfiles/filedetails/?id=3812461539]SEST Integration Pack - Modernised Campaigns[/url].

[olist]
[*]Subscribe to all.
[*]In the Mod Manager, open the SEST Integration Pack's folder, quit the game and double-click [b]SETUP - double-click me.cmd[/b]. It checks the subscriptions, installs the Anchor Chain preloader and writes the load order, with the pack at the top.
[*]If the Mod Manager offers to move the pack's dependencies above it, say no. Running SETUP again puts the order back.
[/olist]

Nothing needs a manual install: some mods still name SeaLifter, but they run without it.

Campaigns: Southern Watch, Southern Reach / Tasman Shield, Red Line and Sulu Line, plus two draft world campaigns for the Dynamic Campaign Mod. All fiction, set in 2028-29.
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
