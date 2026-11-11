# Workshop listing — paste-ready copy

The reference copy for the Steam page of SEST Integration Pack - Modernised
Campaigns (3812461539) and its collection (3812390790). The 9 November R12 release copy below is prepared for posting; it has not
been posted to Steam by this workflow. The opening brief and world-map costs
were accepted on the PC; check the final Growler choices after installing. Nothing here is generated; when the campaigns change, edit it
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

Counts (3 Nov 2026, `release/consolidated-20261103` from `9b382fd8`): 203
Workshop mods in `data/load-order.tokens.txt` (204 entries with the pack;
the 28 Oct capture added Contact Log, Topographic Map, Pop-Out Windows and
the B-21 Raider), 166 named by a mission (REQUIRED-MODS.txt, unchanged by
the four). The borrowed-file count, 538 files from 65 mods (CREDITS.txt;
U.S. Navy 2027's `usn_p8_2027` joined for the P-8 guidance link), is
`c32c485e`'s: check it against the rebuilt CREDITS.txt before pasting.
Redo them from those files when they change. The 19-tube pod
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
Four connected naval campaigns, three with national commander awards, and Global Maritime Operations 2028: 196 bases, eight command stages, persistent logistics. Requires the SEST collection. Subscribe to all, then run SETUP from the pack folder.
```

## Description

```
[h1]SEST Integration Pack - Modernised Campaigns[/h1]
Four connected Task Force Mode campaigns and a persistent global campaign for Sea Power, built around reconnaissance, force protection, sustainment and command decisions in fictional 2028-2029 operations.

[h2]The campaigns[/h2]
[list]
[*][b]Southern Watch[/b] - Twelve connected missions defending Australia's northern sea routes as maritime coercion develops into a regional conflict. Begin with a frigate, a helicopter and uncertain contacts; progress to coordinated air and naval operations. Optional operations, contingencies and standalone dispatches expand the campaign.
[*][b]Southern Reach / Tasman Shield[/b] - Twenty-six missions across the Tasman, South Pacific and Antarctic approaches. Protect resupply routes, manage a growing force and carry the consequences of earlier operations towards a ceasefire.
[*][b]Red Line[/b] - Six missions and an epilogue commanding a Chinese carrier group. Counter missile craft, submarines, disguised threats and intercepting aircraft while balancing identification, restraint and force protection. Two optional operations add reconnaissance and a contingency adds a pilot recovery.
[*][b]Sulu Line[/b] - Seven missions with a Philippine-led task group. Build the force you can afford, protect your supply ships and manage ammunition across successive operations. Three optional operations affect later missions.
[/list]
Each campaign opens its whole roster as the story allows: from the start in Red Line, Weapons Free in Southern Watch, Tasman Crossing in Southern Reach and Service at Sea in Sulu Line. From those points Southern Watch and Southern Reach also sell an allied fleet of 52 ship classes and the allied aircraft their missions can fly.

Starting airborne Growler flights in Southern Watch and Southern Reach offer [b]HARM, AARGM and AARGM-ER[/b] loadouts, with AIM-120D self-defence missiles, NGJ pods and two external tanks.

[h2]Commanders and service records[/h2]
[list]
[*][b]Commander nations.[/b] Southern Watch and Southern Reach offer Australia (default), the United States, the United Kingdom, Japan, New Zealand, France, Canada, South Korea, Spain, Italy, Germany, the Netherlands, Norway and Denmark. Sulu Line offers the Philippines (default), Thailand and Australia; Red Line keeps its Chinese command. Each nation has its navy's officer ranks, a commander name pool and an emblem. Choose it in the Service Record when you start a campaign; one already under way keeps its commander.
[*][b]Purchase discount.[/b] The game's same-nation discount covers classes from the commander's own nation; each campaign's rules page gives the count. New Zealand's is the RNZAF P-8A Poseidon, sold with the allied fleet. No class on the rosters is Canadian.
[*][b]Service Records.[/b] Every commander can earn each campaign's completion and operation ribbons. In Southern Watch and Southern Reach, commanders of every offered nation except Italy, the Netherlands and Norway also earn their own nation's awards at their rank, and the task group the Australian Meritorious Unit Citation; Sulu Line has Philippine awards for a Philippine commander. Citations are dated and name the mission. These are game awards for fictional operations, not real honours; national award rules are verified on beta 0.8.7-261107.
[/list]

[h2]Global Maritime Operations 2028[/h2]
A single worldwide campaign for [b]Dynamic Campaign Mod[/b], combining the original world and its regional expansion. Command either coalition across the Atlantic, Mediterranean, Indian Ocean and Pacific, moving forces on the strategic map and fighting engagements in Sea Power.
[list]
[*][b]196 bases, 293 force groups, 54 patrol routes and 1,586 recruitment entries.[/b] The network includes 40 additional real-world airfields; existing positions have been reviewed, including Muharraq, Souda and Diego Garcia.
[*][b]Eight command stages[/b] give earlier milestones and progressive access to recruitment. Accepted Admiralty assignments reward escort, surveillance, area control and multi-phase operations as well as combat, when those tasks are offered.
[*][b]Operational logistics[/b] use finite fuel and ammunition. Depots produce supplies, convoys deliver them, airlifts move ammunition and replenishment ships sustain forces at sea.
[*][b]Battle preparation and return[/b] (beta). World engagements open with a paused preparation checklist. Use Esc > End battle... and return through the debrief when you need to disengage; the campaign still assesses the outcome.
[/list]
[b]Start a new world campaign for the complete revised layout and progression.[/b] Existing saves keep their own world; WORLD-CAMPAIGN-READ-ME.txt explains how to reopen an original World Sandbox save. The added facilities are operating locations; building new bases during play is not included.

[h2]Operations and combat costs[/h2]
Items marked [b](beta)[/b] need public beta 0.8.7-261107, where SETUP installs them; the rest also work on standard 0.8.7-261021.
[list]
[*][b]World Operations[/b] (beta): F11 brings together Overview, Forces, Combat Costs and Service, with your next command milestone, recruitment unlocks and Admiralty task rewards and deadlines.
[*][b]Cumulative Combat Costs[/b] reports recorded weapons expenditure and losses for each mission and campaign through F11 and in the Task Force debrief; on the beta world map it sits beside Economy. [b]Estimated USD costs are separate from campaign credits and physical supplies.[/b]
[*][b]World service ribbons[/b] (beta): 25 fictional awards for manual battles, campaign days, theatres and completed Admiralty tasks; a whole multi-phase operation counts once, and a replay after reloading never counts twice.
[*]Coordinated Strike refinements (beta) add shared styling and planned/remaining weapon-cost estimates. Contact Log, Group Manager and camera-compass refinements work with Pop-Out Windows 1.2.0 on the beta.
[/list]

[h2]Installation and updates[/h2]
[b]This pack requires the collection's original Workshop mods.[/b]
[olist]
[*]Subscribe to this pack and use [b]Subscribe to all[/b] on the [url=https://steamcommunity.com/sharedfiles/filedetails/?id=3812390790]SEST - Modernised Campaign Collection[/url].
[*]In Mod Manager, open this pack's folder. Close Sea Power, then run [b]SETUP - double-click me.cmd[/b]. It checks the required subscriptions, installs the preloader and sets the load order with SEST at the top.
[*]On the supported beta, a fresh installation needs SETUP, a launch to the main menu for about ten seconds, quitting, then a second SETUP run. An enabled SEST beta installation updates in one run. To keep the beta features off, run [b]SEST beta features - turn off.cmd[/b]; SETUP leaves them off until you run [b]SEST beta features - turn on.cmd[/b]. On the beta, code mods such as Dynamic Campaign Mod then stay off too.
[*]After Steam updates this item, close the game and rerun SETUP. If Mod Manager offers to move the dependencies above SEST, keep SEST at the top.
[/olist]

[h2]Compatibility and scope[/h2]
Built for Sea Power 0.8.7. SETUP checks the installed game and plugins, installs the reviewed beta features only on public beta 0.8.7-261107 and keeps the normal plugins on any other build. Newer versions may need another compatibility update.

The campaigns are fictional 2028-2029 operations using real and modded equipment. Coalition alignments, deployments and stocks are scenario assumptions, not statements of current national policy or readiness. World placement and balance remain subject to playtesting. English language.

[h2]Credits[/h2]
The original Workshop creators supply the units, models and supporting systems this pack integrates. Keep those mods subscribed. CREDITS.txt identifies contributions, compatibility work and credited media. Feedback with the mission name, game build and a clear reproduction is welcome.
```

## Change log: R12 final with commander nations and national awards, 11 Nov 2026

```
SEST R12 - Commander nations, national awards, World Operations (beta) and SETUP opt-out

Commanders and awards: Southern Watch and Southern Reach now offer fourteen commander nations - Australia (default), the US, UK, Japan, New Zealand, France, Canada, South Korea, Spain, Italy, Germany, the Netherlands, Norway and Denmark - each with its navy's ranks, a name pool and an emblem; Sulu Line offers a Philippine, Thai or Australian commander. The game's same-nation discount follows the commander (each campaign's rules page gives the classes); New Zealand's one class is the RNZAF P-8A, now sold with the allied fleet, and no class is Canadian. In Southern Watch and Southern Reach, commanders of every offered nation except Italy, the Netherlands and Norway earn their own nation's awards at the commander's rank, and the task group earns the Australian Meritorious Unit Citation; in Sulu Line a Philippine commander earns Philippine awards and the group the Philippine Republic Presidential Unit Citation. Each of the four campaigns also gains fictional ribbons any commander can earn: a completion ribbon and two operation ribbons. Every citation carries its mission's 2028-2029 date. The national awards are game awards for fictional operations, not real honours, and their rules are verified for public beta 0.8.7-261107. Existing commanders and saves are unchanged.

Red Line: the extra objectives victory needs are marked "Also required", and the six combat briefings (Trailing Contact, Routes They Can See, The Other Picture, The Order to Withdraw, The Quiet Side and The Ships from the North) state the exact terms that complete them. The Other Picture's intercept breaks either way: shoot down an F-35, or, with neither shot down, wait from minute eighteen until no F-35 is within seventy miles of the return box's centre. In The Order to Withdraw, Meridian Harmony can be sunk, or closed to about three miles by the screen's lead ship (its helicopter does not count), when she heaves to, turns neutral and follows the group; sinking her after that ends the mission. The withdrawal is its marked five-mile circle. Progress reports in four Red Line missions mark the way to the exit.

World campaign: Global Maritime Operations 2028 has 196 bases, including 40 additional real airfields, and eight command stages. It replaces both earlier world entries, SEST World Sandbox 2028 and its Regional Expansion, and keeps the Regional Expansion's campaign ID, so those saves keep their own state. The original World Sandbox is no longer in the campaign menu; WORLD-CAMPAIGN-READ-ME.txt in the pack folder explains how to show it again for an old save. Start a new world campaign for the full layout.

On public beta 0.8.7-261107 only (installed by SETUP; Runtime 1.6.4 / UI 1.4.14): F11 World Operations with Overview, Forces, Combat Costs and Service; the Combat Costs button beside Economy; 25 fictional world service awards for manual battles, campaign days, theatres, completed Admiralty orders and multi-phase operations (including Route Security); a paused battle preparation checklist and Esc > End battle...; Coordinated Strike refinements. The world opening briefing shows a short SEST brief before Dynamic Campaign Mod's own situation report, and Contacts, Formation and compass refinements work with Pop-Out Windows 1.2.0.

SETUP: it installs the beta features only on the build they were reviewed for and puts the normal plugins back on any other build; if a reviewed game or author file has changed, SETUP leaves the beta features off, shows a warning and finishes. Use "SEST beta features - turn off.cmd" to opt out (SETUP then leaves them off) and "SEST beta features - turn on.cmd" to re-enable. On the beta, Workshop code mods load only through SEST's beta loader, so turning the features off also turns off Workshop code mods (SEST's plugins and the collection's code mods, Dynamic Campaign Mod included); data mods and the Task Force campaigns still work.

Growler starting flights in Southern Watch and Southern Reach offer HARM, AARGM and AARGM-ER loadouts.
```

## Change log: R12 world operations and Steelfin refresh, 9 Nov 2026

Prepared for the current release candidate; publish after PC acceptance.

```
[b]Global Maritime Operations 2028[/b]
[list]
[*]Expanded the world to 196 bases, including 40 additional airfields, and reviewed existing airfield positions.
[*]Added eight command stages, progressive recruitment bands, operational briefings and live task rewards/milestones in F11 Overview.
[*]Added paused world-battle preparation and a clear End battle... action; victory is not required to return through the debrief.
[*]Included the supported beta feature installer in the Workshop pack: rerun SETUP after Steam updates the item.
[*]Refreshed against the 9 November Steelfin export: its removed demo mission does not change the SEST campaigns, weapons or launcher.
[/list]
```

## Change log: November release candidate, 7 Nov 2026

Paste this block after the release candidate's PC checks pass. Earlier blocks below are historical; do not paste their superseded pop-out/version claims. The final PC checks and upload preparation are in `docs/releases/20261107/README-FIRST.txt`.

```
[h2]7 November 2026 — November integration update[/h2]

[list]
[*]Refreshed the integration against the captured Workshop configurations of 3 November, including campaign dependencies, aircraft/squadron definitions, SETUP and cost-catalogue corrections.
[*]Added the public beta's missing tactical-map settings and explicit helicopter night-vision levels for the Redback loadout warning.
[*]Updated SEST UI Follow-up for the inspected Pop-Out Windows 1.1.3 on the normal game release. Other plugin versions retain the original behavior until checked. Quick Load remains Ctrl+F9 while SEST UI Follow-up is active.
[*]The canonical load order is now 204 entries: SEST and 203 Workshop dependencies. Subscribe to all Required Items, including B-21 Raider, before running SETUP.
[/list]

[b]Compatibility:[/b] This upload retains the normal-release CIWS values and Runtime 1.5.0. On public beta Build 261026, the normal Workshop loader does not provide full SEST code functionality; the separate R6 repair remains a beta test candidate. The beta modifier-file limitation is not fixed by this Workshop upload alone. No claim is made here that the clipped tabs or Global Hawk behavior have been fixed.
```

## Change log: integration of the owner's PC state, 28 Oct 2026

For the next upload, which also carries the SETUP update below and, if not
yet pasted, the 24 Oct block. The 26 Oct 2026 upload went up from PR #50's
head without a reviewed change log (`publishing.md`, *What is on the
Workshop*), so this block is still to paste. The next upload is
`release/consolidated-20261103`'s build, which integrates the 28 Oct
capture; the release gates are in `docs/release-20261103-consolidated.md`.
Paste the Description as well (its counts, its F11 line, the credit, the
code list and the beta sentence changed, and the older-mods line with the
SETUP update). Before Submit:

- Run SETUP from the Workshop copy on the PC. Expect THE REDFOR MOD to count
  as already marked, and Contact Log's RunProbe to become None if it is still
  F8 (a ToggleWindow of F9 is kept).
- Player.log must show three `[SEST Runtime] ... correction installed` lines
  (terrain, debrief, towed sensor), no `[SEST Runtime] inactive: uninspected
  native assembly` line and, with Contact Log 1.0.1, `[SEST UI Follow-up]
  1.4.2 input fix installed`. `inactive: owning pack is not enabled in
  usersettings.ini` means the pack is not ticked in the Mod Manager, and the
  whole plugin is off: tick it, restart and look again. `F11 campaign totals
  inactive: uninspected Combat Cost Tracker` means the installed tracker is
  not the 0.7.1 build SEST inspected, so SEST's F11 windows (in a mission and
  in the Task Force menu) are off and the tracker's own F11 panel is left as
  it is: hold the upload, or take out the F11 sentences of the change log's
  first bullet and the Description's Task Force F11 item. A pop-out bridge's
  `... inactive` line is not SEST's to prevent: it means the installed
  Contact Log, Group Manager or Pop-Out Windows is not the version SEST
  inspected. With Pop-Out Windows 1.0.2 from the collection, expect it from
  Runtime's pop-out bridge and from UI Follow-up's Contacts pop-out surface
  fix, Formation UI mode switch and camera compass (pinned to 1.0.1); the
  block below already says those are off. Take out any other line below
  whose plugin did not install.
- The Quick Load line stays while `SEST.ContactsFix.dll` makes the move (UI
  Follow-up moves plain F9 to Ctrl+F9); it can go only if the plugin is held
  back or rebuilt without it. The owner decides whether to mention the
  unexplained 27 Oct crash with both plugins on.

```
[h2]28 October 2026[/h2]

[b]Interface and costs[/b]
[list]
[*]SEST's runtime plugin is now 1.5.0. F11 opens game-styled cost windows in a mission and in the Task Force menu; move them by the title bar and resize them at the edges. The debrief shows mission and campaign cost, with the details in F11.
[*]Own units are plotted while paused during preparation, and a towed sonar with an incomplete link no longer stops the game's update.
[*]SEST's pop-outs to a second monitor (Contacts, Group Manager and the F11 windows) are off for now: they were built for Pop-Out Windows 1.0.1, and the collection carries 1.0.2. Pop-Out Windows' own pop-outs work as usual.
[*]New: SEST UI Follow-up, for players of Contact Log 1.0.1. Space and +/- no longer open or close Contacts, and the live F11 window stops rebuilding its price lists twice a second. Its Group Manager Stock UI / Enhanced UI switch is off for the same reason until SEST is updated for Pop-Out Windows 1.0.2. Without Contact Log, or on another game build, it does nothing.
[*]With UI Follow-up active, Quick Load moves from F9 to Ctrl+F9; any other Quick Load key is kept. Once you press Accept in Options, Ctrl+F9 stays after you unsubscribe; set Quick Load back in Options.
[/list]

[b]Campaigns[/b]
[list]
[*]Sulu Line: Philippine airfields no longer come with a free 1970s U.S. air wing; a field holds what you buy for it and the mission's own flights (not yet confirmed in game). The Navy helicopter is offered as the AW109E LAH, then the AUH-76. The RAN MH-60R is on sale with the Anzac before Service at Sea and The Aborlan Battery. Deck fits for the H-76, the Thai Seahawk and the MH-60R on the Jose Rizal, Miguel Malvar, Naresuan, Anzac and BRP Tarlac (not yet confirmed in game). Start a new campaign or load a mission fresh to see these.
[*]World Sandbox and Regional Expansion: the US Navy's twelve P-8As are a real P-8A Poseidon (U.S. Navy 2027's) instead of a P-3 Orion body. Bases, numbers and price are unchanged. Start a new campaign to see it.
[*]Both P-8s' Harpoons now get a guidance channel: one P-8 could not fire its AntiShip Harpoons at all, the other fired them with no midcourse updates (not yet confirmed in game).
[*]Each campaign's REQUIRED-MODS.txt now also counts what the units you can buy need: their hull variants, the rounds of every fit they offer and their models. Sulu Line now lists Modern US Navy and United States Naval Aviation, Southern Reach twelve more mods and packs, and Southern Watch three more as hard required. All of them are already in the collection.
[/list]

[b]Collection[/b]
[list]
[*]Four mods join the collection: Contact Log (a sortable list of every contact your task force holds), Sea Power Topographic Map (land heights and sea depths on the tactical map), Sea Power Pop-Out Windows (game windows on a second monitor) and the B-21 Raider (the US stealth bomber, on sale in the World Sandbox). Press Subscribe to all on the collection to get them.
[*]If SETUP stopped after 26 Oct asking for Contact Log, Topographic Map and Pop-Out Windows: subscribe to the collection again, then run SETUP again.
[/list]

[b]SETUP[/b]
[list]
[*]SETUP now checks mod versions the way the game does. Run SETUP again after a game update, or after going back to an earlier version, and it renews the marks it made, so the not-compatible warning does not come back. Mods made for a newer game version are named and left alone, except THE REDFOR MOD, reviewed and data only, which SETUP marks while its folder holds no code.
[*]If you use Contact Log, SETUP frees its default F6 and F8 keys, which clash with Topographic Map's F6 and Coordinated Strike Tool's F8 planner. It does so once Contact Log has written its settings file: start the game with Contact Log once, then run SETUP again. Keys you changed yourself are kept.
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
[h1]SEST - Modernised Campaign Collection[/h1]
The 203 supporting Workshop mods for [url=https://steamcommunity.com/sharedfiles/filedetails/?id=3812461539]SEST Integration Pack - Modernised Campaigns[/url], and the pack itself. The original creators supply the ships, submarines, aircraft, weapons, facilities and supporting tools; the integration pack adds the campaigns, compatibility work, shared setup, service records and combat cost reporting.

[h2]What the collection and pack offer[/h2]
[list]
[*][b]Four Task Force Mode campaigns[/b] - Southern Watch, Southern Reach / Tasman Shield, Red Line and Sulu Line. Each opens its whole roster as the story allows, and Southern Watch and Southern Reach add an allied fleet of 52 ship classes.
[*][b]Global Maritime Operations 2028[/b] - A worldwide Dynamic Campaign Mod scenario with 196 bases, eight command stages, recruitment progression and finite logistics.
[*][b]National command[/b] - Fourteen commander nations in Southern Watch and Southern Reach and three in Sulu Line, each with its navy's ranks, a name pool and an emblem, the game's same-nation discount on that nation's classes (none is Canadian) and dated service records with national awards for twelve nations.
[*][b]Supporting tools[/b] - Combat Cost Tracker, Contact Log, Topographic Map, Group Manager, Pop-Out Windows and Coordinated Strike Tool, several with SEST refinements.
[/list]
World Operations, world service ribbons and several interface features need the supported public beta (0.8.7-261107); the integration pack's page lists them.

[h2]Installation[/h2]
[olist]
[*]Use [b]Subscribe to all[/b] and let Steam finish downloading. Make sure the SEST Integration Pack is subscribed too.
[*]In Mod Manager, open the SEST Integration Pack's folder. Close Sea Power and run [b]SETUP - double-click me.cmd[/b] to check subscriptions and set the load order.
[*]For a fresh installation on the supported beta, launch to the main menu for about ten seconds, quit, then run SETUP again. Existing enabled beta installations update in one run.
[*]Rerun SETUP after Steam updates the integration pack. Keep SEST above its dependencies in Mod Manager.
[/olist]
Start a new world campaign for the complete revised layout and progression; existing saves keep their own world.

Campaign operations, coalition alignments and deployments are fictional. Each creator keeps credit for their original mod; keep them subscribed.
```

## Tags, images, and what to leave off

Tags: `Campaign`, `Missions`, `English`.

Preview: `StreamingAssets\SEST-preview.jpg` (124 KB; the image picker only
browses StreamingAssets). Screenshots, from `campaigns/sest-southern-watch/art/`
inside the pack: `00_campaign_background.png`, `southern_watch_01_sheet.png`,
`00_opening_image.png`, `southern_watch_08_sheet.png`, then an in-game shot of
the campaign map that you take yourself.

Steam artwork (redone 10 Nov 2026 for R12): `Gallery/visuals/steam/` in the
pack, made by `integration/gallery/steam_art/render.js` from `cards.json`.
The item's cover (`pack-preview.jpg`) and eight cards, `pack-1` to `pack-8`
(`pack-8-world.jpg`, Global Maritime Operations 2028, is new), plus the
collection's `collection-cover.jpg` and `collection-background.jpg`. Every
photo's credit is printed on its image and listed in `VISUAL_CREDITS.txt`.

Leave off the page: the repository and how the pack is built, any claim that
it is balanced or play-tested, and any promise of translations or of support
for another mod list.
