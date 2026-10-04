# Aligning the gaming PC with this branch — and with the other sessions

This is the procedure for bringing a Sea Power install up to a build that
carries **the three campaigns** (Southern Watch, Southern Reach and Red Line)
together with every fix the other sessions have pushed, and the work ported
from their older branches (§6). It replaces
the counts in `../southern-watch/install-alignment.md`; the checks and the
failure story there still hold and are not repeated.

Two facts shape it:

- **The PC deploys from one branch**, the one `data\deploy-branch.txt` names:
  `sest-dev/loving-bell-3cnvvw`. `sync-sest.ps1` refuses to run from any
  other branch, on purpose — the last time it ran on the wrong one it reported
  `IN LINE` against a build with none of the campaign in it.
- **Sessions work on their own branches.** This session's work was on
  `claude/campaign-missions-lore-td653z` (`694db53e`, 3 Oct). It is no longer
  the source. The deploy branch has since taken `10b6b48b` and `7d670392`
  (3 Oct) and `d4fd1668` and `fa692245` (4 Oct), fast-forwarded in from
  `sest-dev/inspiring-wozniak-8vuckh`, and this session's branch contains
  none of them: the two have diverged, and a fast-forward to it is refused.
  Do not merge it on the PC: the PC checks out the deploy branch and syncs,
  and the sync pulls the deploy branch.

Close Sea Power before any of it. It rewrites `usersettings.ini` on exit and
throws away a load-order change made while it is running.

## Already aligned once? The short version for later rounds

`sest-dev/loving-bell-3cnvvw` is at `fa692245` (4 Oct) or later; `fa692245`
is the build published as Workshop item 3812461539.
`feature/northern-front-iii-export` is behind it at `3b040cc0` (3 Oct). A
later round lands on the deploy branch itself, so an update is: check out the
deploy branch, then sync (`sync-sest.ps1` pulls it). The block no longer
merges or pushes anything. Close Sea Power, then paste this into PowerShell
as one block. It has no blank lines on purpose: the console reads a paste
line by line, and an empty line would end the block early. If it stops at a
`>>` prompt, press Enter once more to run it.

```powershell
& { $ErrorActionPreference = 'Stop'
  if (Get-Process -Name 'Sea Power', 'SeaPower' -ErrorAction SilentlyContinue) { throw 'Sea Power is running - exit it first' }
  Set-Location -LiteralPath 'C:\Users\rolyl\Seapower-mods'
  if (git status --short) { throw 'The clone has uncommitted changes - stop and report them' }
  git checkout sest-dev/loving-bell-3cnvvw
  if ($LASTEXITCODE) { throw 'checkout failed' }
  powershell -ExecutionPolicy Bypass -File .\tools\sync-sest.ps1
  if ($LASTEXITCODE) { throw 'sync failed - read its last lines' }
}
```

It stops, before anything is installed, if the game is running or if the
clone has changes of its own (report them rather than committing them). The
sync's last lines should read
`IN LINE: all 1266 installed files match this commit (<hash>)`, the hash
being the deploy branch's head after the sync's pull (`git log --oneline -1`).
Merge a session branch on the PC only when a round names one that already
contains `fa692245` (step 2). The four mods you added on the evening of 3 Oct
are in the canonical order now, so the sync's `dropped stale workshop entry`
lines for them stop; if it still prints one, the id it names is a
subscription the repo has not seen - export it.
`-RefreshMissions` on the sync is only for a round where the sync says it
merged your own mission edits: it re-spreads the airliners in the missions
you imported from the game.

Then check what landed (game closed or open):

```powershell
& { $ErrorActionPreference = 'Stop'
  Set-Location -LiteralPath 'C:\Users\rolyl\Seapower-mods'
  . .\tools\lib\common.ps1
  $root = Find-StreamingAssets
  if (-not $root) { throw 'Sea Power StreamingAssets not found' }
  $c = Join-Path $root 'SEST_Integration\campaigns'
  foreach ($d in Get-ChildItem -LiteralPath $c -Directory | Sort-Object Name) {
    $own = Select-String -LiteralPath (Join-Path $d.FullName 'campaign.ini') -SimpleMatch -Pattern ('Base=campaigns/' + $d.Name + '/campaign.ini') -Quiet
    $rules = Test-Path -LiteralPath (Join-Path $d.FullName 'campaign_rules_en.xml')
    '{0,-26} own file: {1,-5}  rules page: {2}' -f $d.Name, $own, $rules
  }
  $rig = Join-Path $c 'sest-southern-watch\missions\Southern Watch 03 - Rig Seventeen.ini'
  'Rig Seventeen ship home bases: {0} (want 0)' -f @(Select-String -LiteralPath $rig -Pattern '^HomeBase=Taskforce1Vessel').Count
  $open = Join-Path $c 'sest-southern-watch-open\campaign.ini'
  if (-not (Test-Path -LiteralPath $open)) { throw 'No Open Allocation campaigns installed - the sync did not take this build' }
  $line = Select-String -LiteralPath $open -Pattern '^TaskForceModeAllowedRosterUnits=(.*)$' | Select-Object -First 1
  'Southern Watch Open Allocation, first window: {0} units on sale (want 93: its 10 and the 83-unit allied fleet)' -f ($line.Matches[0].Groups[1].Value -split '\|').Count
  $ts11a = Join-Path $c 'sest-southern-reach\missions\Tasman Shield 11A - The Twelve-Mile Line.ini'
  if (-not (Test-Path -LiteralPath $ts11a)) { throw 'The Twelve-Mile Line is not installed - the sync did not take this build' }
  'The Twelve-Mile Line: scripted salvo lines {0} (want 1)' -f @(Select-String -LiteralPath $ts11a -SimpleMatch -Pattern 'AttackAtWaypoint,plan_yj-83a,Taskforce1Vessel2').Count
  $ts12 = Join-Path $c 'sest-southern-reach\missions\Tasman Shield 12 - Southern Cross.ini'
  'Southern Cross reads its result: {0} (want True)' -f (Select-String -LiteralPath $ts12 -SimpleMatch -Pattern 'TS11ADefectorSafe' -Quiet)
}
```

It should print six campaign folders, each `own file: True  rules page:
True`, then `Rig Seventeen ship home bases: 0`, `93 units on sale`,
`scripted salvo lines 1` and `Southern Cross reads its result: True`. The 93
is Southern Watch's own 10 units plus the 83-unit allied fleet; 10 means an
install from before the allied fleet. A
folder missing, a `False`, a count of 2, "No Open Allocation campaigns
installed" or "The Twelve-Mile Line is not installed" means the sync did not
install this build: read its output before playing.

### This round (3 Oct, late evening): four new mods, the Chinese loading tips, the Rafale back

> Addendum, 4 Oct: this is no longer the latest round. The deploy branch has
> since taken `10b6b48b` and `7d670392` (3 Oct: bare mission numbers on the
> Southern Reach and Red Line backdrops; Red Line runs to February 2029),
> then `d4fd1668` (the planned window plus a 1.5x deadline, sea-state ship
> speeds, `SETUP - double-click me.cmd` and `sest-setup.ps1` at the pack
> root) and `fa692245` (timeout texts follow the deadline, SETUP relaunch
> hardened). Expect `IN LINE: all 1266 installed files`, not the 1264 below.
> That build is published as Workshop item 3812461539.

Your export (`bb2316d4`) brought Moloti's Armed Merchantmen, French Air Force,
the MV-75 Cheyenne II (the one the Mod Manager shows as `3810611344` with an
(A) badge - its `_info.ini` files its name under the wrong heading) and the
PLAAF Aircraft Pack, plus updates to Euromod, both Italian navy mods, Modern
British Navy, JMSDF and the B-1B. Each is in this build (Southern Watch build
notes, *Four new mods, the Chinese loading tips, and the Rafale back*):

1. **The Chinese loading tips.** The PLAAF Aircraft Pack files a
   `[LoadingTips]` section in Chinese under its `language_en/` folder, and
   because language files merge key by key under the game's own key names,
   it replaced every loading-screen tip. SEST Collection Fixes now ships the
   game's English `loading_tips.ini` word for word from the top of the
   order, so the tips are English again; the pack also names the H-6J's
   ESM pod in English, the one Chinese line in that mod's weapon names.
2. **The Rafale is back.** The French Air Force mod ships the whole Rafale
   family under the ids the old mod used, so everything retired this
   morning returned this evening: D3's CAP pair (on this mod), D6's Rafale
   41 (SEST Rafale F5's AIM-260 fit), the allied fleet's Rafale M and B
   Late, the Banda vignette *Rafale, Timor Gap*, and the SEST Rafale F5
   pack, rebuilt on the new files. One difference you will see: this mod's
   Rafale M Late carries ONE heavy store on the centreline with two wing
   tanks, so its SEST MALICE and LRASM fits carry one round and have no
   three-tank twin; the land-based B and C Late keep two under the wings
   and their three-tank fits. 20 packs.
3. **The four mods are catalogued, ordered and placed.** The two aircraft
   packs sit at the bottom of the order, above Red Storm Arsenal only, so
   the specialist mods keep every file they share; the merchantmen sit by
   Merchants Expanded and the MV-75 by the MV-22B. Southern Lifeline (SW09)
   gains an armed Okean intelligence trawler keeping station on the support
   group (it shows on the Situation roster under Russia); Fujian's Shadow
   (SW11) an H-6K with four YJ-12 a minute behind the J-15D; The Long
   Perimeter (D8) an Army MV-75 beside the Ospreys.
4. **The six updated mods** rebuilt clean; every guard held.
5. **The count is 1264**: 1260 plus the Rafale F5 pack's three airframes and
   the restored tips file.

What to do: the standard update block (*Already aligned once?*), expecting
`IN LINE: all 1264 installed files match this commit (<hash>)`. Then start
the game and look at the loading screen: the tips should read in English.

### The 3 Oct evening round: your play-test notes, the Situation button, the Rafale retired (and back, above)

Your first Task Force Mode run came back with three notes; each is in this
build, and your decision on the Rafale with them (Southern Watch build notes,
*The first play test*):

1. **The Port Moresby cable's date** stays as it was, on your word:
   `DTG: 210600Z OCT 28` is the military form, day 21, 0600 Zulu, October
   2028. (The build wrote the year in full for one commit; reverted.)
2. **Steel Highway's submarine.** It was on the plot from the first minute
   because you found the beacon in The Missing Beacon, and that reward handed
   the contact over classified for the whole mission - too much for a
   mission about classifying it. The reward is now a datum: a detected,
   unclassified contact where the bridge record put the boat, which ages off
   after fifteen minutes unless your sensors hold it. The Quiet Passenger's
   Kiwi 01 reward is treated the same way. "Two subs": the mission places
   one and the briefing says one; the Southern Watch card (H.8) asks you to
   count again, because the likeliest second symbol is the revealed datum
   beside a sonar contact on the same boat.
3. **The Situation button.** Every campaign and twin now ships an enemy
   theatre roster, so the button at the bottom right of the campaign screen
   lists the forces the missions place - by nation, flagships, persistent
   units with their variants, boats, aircraft with flight sizes. Whether it
   tracks a sunk unit is yours to see (Southern Reach card 7.8).
4. **The Rafale is retired.** No other mod in the collection ships one; the
   French Navy pack's Charles de Gaulle names the Rafale mod's fighters in
   its air group and sails without them. D3's Rafale CAP pair, D6's Rafale
   41, the allied fleet's Rafale M and B, the Banda vignette *Rafale, Timor
   Gap* and the SEST Rafale F5 pack are gone; 19 packs now, and the four
   checks that were red for it are green. The sync will delete the vignette
   and its briefing from your missions folder if it mirrors, or leave two
   stale files there if it only copies: either is harmless.
5. **The Ford has its Seahawks back.** Modern US Navy's update dropped the
   `usn_mh-60r_26` the Ford mod's air group embarks ten of; the copy of the
   Ford the pack ships embarks ten `usn_mh-60r` instead.
6. **The count is 1260**: 1257 plus the six roster files, less the Rafale
   pack's three.

What to do: the standard update block (*Already aligned once?*), expecting
`IN LINE: all 1260 installed files match this commit (<hash>)`. If you have
subscribed to the two new mods you mentioned (a French air force mod, a PLAAF
systems mod), run the export block instead - it syncs first, then exports
and pushes them, and the next build catalogues and places them.

### The 3 Oct afternoon round: seven mod updates, 0.8.4, the PLAN Pack takes its own

Your export brought seven updated mods, not two, and the game had quietly
moved to **0.8.4 Build 261002** on 2 Oct (two fixes: the mod menu's folder
picker, null references). Everything was rebuilt on them; Southern Watch
build notes, *Seven mod updates and 0.8.4*, has the record. For you:

1. **The PLAN Pack did the morning's work for its own hulls.** Its update
   gives every one of its ships a combat system of its own (the 054A reads
   ZKJ-5A, the 052D ZBJ-1A, the 055 and its Fujian ZBJ-1B, the 056A
   ZKJ-5B) and puts its Type 730 and 1130 on the 0.8.3 CIWS keys itself, at
   anchors 65 and 90 - the 1130 with 2800-round volleys, a strong CIWS by
   the game's ladder and the author's call. The pack's eight extend files
   and four retunes for that mod were retired by the guards built for
   exactly this; the Liaoning, Type 071, Red Storm's PLAN hulls and the
   Luda/Sovremenny keep their SEST profiles. Shift+Y on a 054A now reads
   ZKJ-5A, so the test of our extend moved to the Type 071 and the Liaoning
   (Southern Reach card 7.3a, Red Line 8A.3a, Southern Watch H.4a).
2. **The Fujian is the PLAN Pack's now.** It ships its own `plan_cv_type_003`
   above the Fujian mod's, with the same air wing of its new J-15T, J-35,
   KJ-600 and Z-18s. The campaigns credit it so. Keep the Fujian mod
   subscribed: it is still the only source of 25 PLAAF rounds the J-35 and
   others fire.
3. **Every pack declares 0.8.4.** No version warning in the Mod Manager.
4. **The exporter bug is fixed** (its `Build #` match; the block below the
   fold has the right one), and Auto Time-on-Target's folder is pruned, so
   `check_inventory` is back to its two known reds.
5. **Your save is on record.** `NEW TEST 1.sav` - Southern Watch (Open
   Allocation), mission 2 done - came in with the snapshot. Whether it
   reopens after this round's rebuild is worth one line when you next load
   it: it is the first Task Force Mode save the repo has.
6. **The count is 1257** (1265 less the eight PLAN Pack extend files).

What to do: the standard update block (*Already aligned once?*), expecting
`IN LINE: all 1257 installed files match this commit (<hash>)`, then the
play test: the 2 Oct watch list (Hold aircraft, Standing Orders) plus
Shift+Y on the Anzac and on a Type 071 or the Liaoning.

### The 3 Oct morning round: combat systems, the CIWS model, Auto Time-on-Target retired

The two 0.8.3 decisions the 2 Oct round left to you are taken, and the look
at the CIWS data found something larger. Southern Watch build notes,
*Combat systems and the CIWS model*, has the whole record; what changes for
you:

1. **Your ships name their combat systems.** The Anzac reads Saab 9LV with
   CEAFAR (`SEST 9LV MLU`), the Hobart Aegis Baseline 9, Canberra, Arafura
   and Supply 9LV, the Mogami her OYQ-1 - where the Anzac and Mogami
   declared none and Supply declared None. Every PLAN surface hull the
   campaigns field, and every coalition hull that lacked one, gets a profile
   too, by `#!extend` from the SEST pack (60 files). Submarines take none,
   like every vanilla boat. Shift+Y on an Anzac and on a 054A is the test
   (Southern Reach card 7.3 and 7.3a): the 054A reading `SEST PLAN
   Multirole` proves an extend from our pack reaches another mod's hull,
   which Euromod relies on but we have not seen.
2. **The CIWS are on the 0.8.3 model.** The PLAN's Type 730 and 1130 fall
   from anchors 85 and 102 to 55 and 60 (vanilla's Phalanx Block 1 is 50),
   the Kashtan from 95 to 45, the Phalanx Block 1A/1B copies in three packs
   from 85/90 to 50/55, and 22 sections in all; the Anzac's Phalanx is
   vanilla's Block 1 definition. And four aircraft mods you run (Tu-95MS,
   MORE SU24M VARIANTS, KC-135 Stratotanker, Su-30SM2) each carry a stale
   copy of the game's whole `weapons.ini`, so the game's own 0.8.3 AK-630,
   Phalanx and AK-230 - and 63 stock guns and launchers - were not being
   read on any hull; the pack restores the game's text for 66 sections.
   Those four mods are fine to keep: the pack now overrides the copies.
3. **Auto Time-on-Target is retired.** You unsubscribed it on 3 Oct;
   it is out of the canonical order, the catalogue's active set, the code
   tier and the campaign excuses, so the sync stops re-adding it and this
   round prints `dropped stale workshop entry` for it once. Coordinated
   Strike Tool (F8) stays. `check_inventory` is red on its folder until
   your next export prunes it.
4. **The count is 1265** (1203, plus 60 extend files and the two systems
   files).

What to do: the standard update block (*Already aligned once?*), expecting
`IN LINE: all 1265 installed files match this commit (<hash>)`, then the
play test - the 2 Oct round's watch list still stands (Hold aircraft,
Standing Orders), with Shift+Y on the Anzac and a 054A added to it.

### The 2 Oct round: Sea Power 0.8.3

Steam updated the game on 2 Oct: **0.8.3 Build 261001** of 1 Oct (the repo
had reasoned from 0.8.2 Build #358 of 20 Jul). Your export brought the new
game files - 4,051 text files, 200 of them new and 1,080 changed - and the
day's mod updates (Euromod, its Anchorchain expansion, Identify Expanded,
Modern US Navy, US Naval Aviation, the German Navy, Flight Deck Ops, the
F-22, the MiG-29s, the Apache, the Fury). Everything was rebuilt on them;
what it took and what it means for you:

1. **The pack declares 0.8.3** in every component, so the Mod Manager shows
   no version warning on `SEST Integration Pack`. Of your Workshop mods, 23
   declare 0.8.2 (a lower patch number, which the Mod Manager accepts), and
   the 54 that already showed as out of date still do. Coordinated Strike
   Tool's own range (below 0.9.0) admits 0.8.3.
2. **Five SEST builders stopped on the new files and were rebased**, each
   where its own check said: the campaign rules page (the game now fills the
   Survived Missions column itself, so the build no longer writes our
   numbers in), Collection Fixes (the Side Globe jammer is now cloned from
   the game's own new Side Globe, `Gurzuf`), the Intercept Model (the
   game's damage table gained `InterceptChanceFloor`, carried), SEST
   Replenishment (the Sacramento the Type 901 is cloned from fires APDS from
   its Phalanx since the 28 Sep build, so the refit's magazine slot follows
   it) and Allied Fixes (the Apache mod's update renamed the Sea Apache's
   rocket). Each campaign's build notes, "Sea Power 0.8.3".
3. **Two editor missions** - `01 Threads` and `02 Hot Gulf` - would have
   crashed the editor's map panel: the game's Tu-95RT no longer offers a
   Default fit, and four of them named none. They now name `Recon`
   (`fix_loadout_variants.py`, the repo's existing fix for exactly this).
4. **Two files join the pack**, so the count is **1203**: the early Wasp
   (Modern US Navy released it from a Pending folder, so SEST Replenishment
   now meters it like the other LHDs) and the SY-1 round (the Type 021
   Huangfeng the game added carries it, so it is a ship-carried missile the
   metering tags).
5. **Nothing new is placed.** The units 0.8.3 added - the RAAF Nomad and
   Searchmaster (1975-93), a 1971 KC-10 (your KC-10A mod is the 2028 one),
   the Type 021 (1965), the Hatsuyuki, Takatsuki and Tachikaze, the
   Spruance VLS (to 2005), Bunker Hill, the Improved Victor III, a Scud-B
   launcher - are not in service in the campaigns' years.
6. **Your saves.** The game's own 28 Sep build "fixed campaign persistence
   for units sometimes not working"; nothing in this round touches a save.
   A Southern Reach campaign already past Approaches should still be started
   again, for the reason the 28 Sep round gave.

7. **The announcement** (read after the first sync) adds what the game's
   changelog had not said, and three of its items touch the pack: the
   game dropped its KC-135A and Tu-16N stubs, so the three RAAF bases
   that listed a KC-135A detachment now list the KC-135 Stratotanker
   mod's airframe (the Tu-16N in Southern Watch D7 comes from its own mod
   and stands); *player aircraft now return to base on Weapons Hold*,
   which 21 campaign missions start a Wedgetail, Triton, tanker or Rivet
   Joint in; and the new OODA model reads a `[CombatSystems]` block the
   Hobart, Arafura, Canberra and Choules inherited from their donors but
   the Anzac, Collins and Mogami have not got (Southern Watch build notes,
   "Sea Power 0.8.3", *What the announcement adds*). Watch, in order:
   - **Wedgetail 05, Texaco 71 and Rivet 21 in Approaches**: on station
     through the clock, or turning for East Sale at the start. If they go
     home, every Hold aircraft moves to Tight (the same thing for an
     unarmed aircraft) in the next build.
   - **Standing Orders** (Left Shift+O): "Ships on Weapons Tight engage
     hostile aircraft" is now off by default, and "Ships use anti-ship
     missiles on Weapons Free" is a new toggle. Note both states before
     the first fleet action; a frigate that watches a Z-9 at Tight, or an
     Anzac that holds its NSMs at Free, is the game's default, not a
     mission fault.
   - **Unit Status** (Shift+Y) on the Anzac and the Hobart, Engagement
     tab: the Hobart's combat system reads AEGIS Mk 7; what the Anzac
     reads is the game's default for a hull that declares none.
   - any **daylight-only** warning on an aircraft or a fit at night.

What to do: the standard update block (*Already aligned once?*), expecting
`IN LINE: all 1203 installed files match this commit (<hash>)`, then the play
test the 30 Sep round asked for. Auto Time-on-Target was still subscribed
and loaded in this snapshot, and the Rafale still absent: the 30 Sep round's
items 2 and 5 stand.

### The 30 Sep round: the Rivet Joint, Coordinated Strike Tool, the snapshot

What the 30 Sep snapshot showed, and what this round does about it:

1. **No mission was played.** Both logged sessions are the Mod Manager and
   a quit; the play test of The Twelve-Mile Line and the wider forces is
   still to do (Southern Reach test card, sections 5 and 6; Red Line 4).
2. **Auto Time-on-Target is still there.** The snapshot has it subscribed,
   enabled at position 7 and loaded (`bepinex.log`: `[AutoTOT] DOTS scan
   hardening active`) beside Coordinated Strike Tool 1.3.1. Two salvo
   timers at once: unsubscribe it in Steam (Workshop page, Unsubscribe) and
   let the game drop it from its list; the canonical order keeps it until
   your next export shows it gone.
3. **Coordinated Strike Tool** (3806686336) is catalogued with the code
   mods below Anchor Chain and excused from coverage, as Auto Time-on-Target
   was; the sync moves it up from the bottom of your list. It is now the
   code-mod check below (F8).
4. **RC-135V/W Rivet Joint** (3808882954) is catalogued in Tier 5 above Red
   Storm Arsenal - whose own RC-135W is a different file, so nothing
   collides - and placed in two missions: Rivet 21, a USAF RC-135 off
   Sydney in Tasman Shield 11 (Hold, named in the chart's corner), and a
   coalition RC-135 south of the box in Red Line 03 (Hold, spared: shooting
   it down ends the mission). Each campaign's build notes, "Rivet Joint";
   test cards, Southern Reach item 5 and Red Line 4.6. The file count stays
   1201.
5. **The Rafale is gone from your subscriptions.** The Dassault Rafale mod
   (3504168760) dropped off the 28 Sep snapshot's Steam list and the 30 Sep
   export deleted its files. Southern Watch D3 and D6 place it, the Open
   Allocation allied fleet sells it and SEST Rafale F5 patches it. Open its
   Workshop page (`steamcommunity.com/sharedfiles/filedetails/?id=3504168760`):
   if it is still there, subscribe again and run the export block below; if
   it is not, say so and the Rafale is retired from the campaigns. Until
   then the pack carries it as built from the last export that had it, and
   four checks are red on the committed tree (step 3).
6. **Mod updates absorbed.** The export also brought Russian Navy 21
   (sensors, S-400 rounds, seven hulls), Euromod's MIM-23 Hawk family,
   Modern US Navy's ES-3A, both Spanish packs and Flight Deck Ops' Kiev;
   the SEST packs that patch those hulls were rebuilt on the new files.

### The 28 Sep round: the Rig Seventeen fix, rules pages, Open Allocation, the discount, wider forces, The Twelve-Mile Line

Seven changes since the Red Line round, in play order:

1. **Rig Seventeen** died twice on a force carried through White Water and
   Steel Highway. In a mission your force is inserted into, no player-side
   aircraft names a Taskforce1 ship as its home base any more, as in stock
   (44 lines across 38 missions; Southern Watch build notes, "Rig Seventeen
   died again"). Your Southern Watch save needs nothing: continue it and
   load Rig Seventeen. If it dies again, capture with `-IncludeSaves` and
   push. Your helicopters now name no home ship; order them to land on it.
2. **Campaign Rules** - the button at the bottom right of the campaign map
   now opens a page in each campaign (it opened nothing before).
3. **Open Allocation** - each campaign is listed a second time, e.g.
   "Southern Watch - Open Allocation (Royal Australian Navy)": the same
   missions with the whole roster on sale from the first force allocation.
   It is a new campaign with its own save; the standard ones are untouched.
   Southern Watch test card 6G is its check list.
4. **Same-nation discount** - every campaign, standard and Open Allocation,
   now gives its commander Pacific Strike's 20% off units of their own
   nation, and every unit on sale is the commander's own (the US-built
   airframes fly Australian squadrons). It came after the first 28 Sep
   sync: the same update block brings it, the count stays 1189, and the
   Campaign Rules page gains a National Purchase Discount section. A
   campaign already under way may keep its old value - a new start will
   show it; test card G.6 checks both.
5. **The allied fleet** - the Open Allocation versions of Southern Watch
   and Southern Reach also sell the allied fleet at full price: 83 and 76
   US, UK, NATO, Japanese, Korean and extra Australian ship, submarine and
   aircraft classes, from the first force allocation. Aircraft are sold only
   where a mission can launch and recover them. Test card G.7-G.9.
6. **Wider forces** - Southern Reach and Red Line place units from more
   of the collection (Il-78 tankers behind the Bears, USAF KC-46A tankers,
   a Pacific Fleet corvette, the 052D's Z-20F, a neutral French frigate,
   an Operation Deep Freeze LC-130; a RAAF Wedgetail and Growler and a US
   Virginia on the coalition side in Red Line), each checked for realism.
   Their `REQUIRED-MODS.txt` lists grow to 40 and 34. Each campaign's
   build notes, "Wider forces"; test cards, "The wider forces".
7. **The Twelve-Mile Line** (Tasman Shield 11A) - an optional mission
   after Approaches: a Chinese Type 056A's crew asks for Australian
   protection and runs for Eden with a frigate astern. Try it from the
   mission browser first (Tasman Shield folder). It adds a campaign entry
   after Approaches, so a Southern Reach campaign already past Approaches
   should be started again; one before it is fine. Southern Reach test
   card, section 6. The file count goes from 1189 to 1201 (the mission,
   its briefing folder and chart in both copies, its card, and the
   story page before it).

The file count goes from 1171 to 1189: the three rules pages (1174) and the
three Open Allocation folders of five files each.

### The round before: Red Line and the ported work

This round adds a third campaign to the same pack, **Red Line — The Other
Watch**: six missions played from the Chinese side, with its own folder of
docs (`docs/campaigns/red-line/`). It also redraws nine Southern Watch and
Southern Reach mission cards whose objective ring ran off the chart, and it
brings eleven pieces of the other sessions' work (§6), among them three new
packs: SEST Replenishment At Sea, SEST A-10C+ and SEST Intercept Model. The
pack count is **20**.

The installed file count goes from 691 to **1189**. It was 1189 before the 27 Sep
export too, by coincidence: that export took it to 1171 (21 Burke and Spruance
overrides left with the hulls Modern US Navy and U.S. Navy 2027 deleted, three
reload files arrived with rounds they added), each campaign's Campaign Rules
page made 1174, and the three Open Allocation twins - five files each under
`campaigns\sest-*-open\` - made 1189:
`campaigns\sest-red-line\` (44 files: six missions with their briefing
folders, 16 art files - the four story pages and 12 images - `campaign.ini`,
roster, commander settings and a `REQUIRED-MODS.txt`) and the browser copies under `missions\Red Line\` (31),
plus 423 from the ports: 333 vessel files (Replenishment's reloadable
launchers and supply systems), 87 ammunition files and 3 aircraft files.
Nothing needs subscribing: every mod it places is one the canonical load
order already enables. Step 5 has its checks, and §6 has **five one-time
steps on the PC** that the ports need.

---

## 0 — where things stand (read this first)

| Branch | What it is | State |
|---|---|---|
| `sest-dev/loving-bell-3cnvvw` | the deploy branch the PC tracks | at `fa692245` (4 Oct) or later; `fa692245` is the build published as Workshop item 3812461539 |
| `claude/campaign-missions-lore-td653z` | this session: the three campaigns and their Open Allocation twins, the multi-campaign builder, the coastline proof, the RNZAF bases, and the ported work | at `694db53e` (3 Oct), diverged from the deploy branch: it lacks `10b6b48b`, `7d670392`, `d4fd1668` and `fa692245`; do not merge it on the PC |
| `feature/northern-front-iii-export` | the repo's default branch on GitHub | at `3b040cc0`, behind the deploy branch; do not deploy from it |
| the other `sest-dev/*`, `fix/*`, `feature/*`, `chore/*` branches | earlier sessions | see §6: what was ported, and what was left and why |

So "aligned to this session and the other sessions" means: the deploy branch
at `fa692245` or later, then the normal sync (which pulls it), then §6's
one-time steps.

## 1 — on the PC: find the clone and get on the deploy branch

`<you>` is a placeholder for a real path, not something to type — PowerShell
reads `<` as a redirection operator.

```powershell
@("$env:USERPROFILE", "$env:USERPROFILE\Documents", "$env:USERPROFILE\source\repos",
  "$env:USERPROFILE\Desktop", "C:\", "D:\") |
  ForEach-Object { Get-ChildItem $_ -Directory -Filter Seapower-mods -ErrorAction SilentlyContinue } |
  Select-Object -ExpandProperty FullName
```

```powershell
cd C:\Users\<you>\Seapower-mods
git status --short                       # must be EMPTY - see below if not
git fetch origin
git checkout sest-dev/loving-bell-3cnvvw
git pull origin sest-dev/loving-bell-3cnvvw
```

If `git status --short` prints anything, the PC has local changes (usually a
mission you edited in game and imported). Do not lose them and do not carry
them into the merge blind: `git stash` before the checkout, and `git stash pop`
after step 2 only if you know what they are. A clean tree is the condition
for everything below.

## 2 — bring this session's branch into the deploy branch

Not needed today: read the paragraph under this block before running it.

```powershell
git fetch origin claude/campaign-missions-lore-td653z
git merge --ff-only origin/claude/campaign-missions-lore-td653z
```

`--ff-only` is the check. It succeeds silently if, and only if, this session's
branch already contains everything on the deploy branch. It no longer does:
`10b6b48b` and `7d670392` (3 Oct) and `d4fd1668` and `fa692245` (4 Oct) are
on the deploy branch and not on it, so the merge is refused. Skip this step's
merge and pushes unless a round hands you a branch that contains `fa692245`;
step 1's pull already brings the deploy branch. If the merge of such a branch
refuses (`Not possible to fast-forward`), somebody pushed to the deploy branch
after that branch was cut; stop and say so rather than doing a real merge on
the PC. The fix is one more merge in a session, not a hand merge on the gaming
machine. Run the checks below either way.

Then push the deploy branch so the PC and GitHub agree:

```powershell
git push origin sest-dev/loving-bell-3cnvvw
```

Then make GitHub show it. The repository's landing page (and every new
session, which starts from the default branch) reads
`feature/northern-front-iii-export`, which moves only when you push it.
Either:

- **GitHub → the repository → Settings → General → Default branch →**
  switch to `sest-dev/loving-bell-3cnvvw` (recommended: the page, the README
  and every new session then start from what the PC runs), or
- fast-forward the old default branch to match, from the PC:

```powershell
git push origin sest-dev/loving-bell-3cnvvw:feature/northern-front-iii-export
```

That push only succeeds as a fast-forward, which it is today; it cannot
overwrite anything.

Check, and do not skip:

```powershell
git branch --show-current            # sest-dev/loving-bell-3cnvvw
git log --oneline -1                 # note the short hash: the IN LINE line must name it
Get-Content data\deploy-branch.txt   # sest-dev/loving-bell-3cnvvw
git merge-base --is-ancestor fa692245 HEAD; $?   # True: the 4 Oct build (the one on Workshop item 3812461539) or later
```

The last line is the one that says the pull brought the published build: it
asks git whether `fa692245` is inside the branch you are on. (A file check
would need a file only this round brings, and a round of fixes may bring
none.) `False` means step 1's pull did not take.

## 3 — let the build check itself (optional on the PC, done here)

The committed packs are the builders' own output, rebuilt from scratch on
this tree in this session with a clean `git status` afterwards, and the gates
were run on it:

```
python tools\build_all.py --from-scratch      # 20 packs, clean git status after
python tools\check_campaign_coverage.py       # three campaigns, 1589 placed references, all 210 enabled mods and SEST packs (190 Workshop mods + 20 packs)
python tools\check_load_order.py
python tools\check_dependencies.py
python tools\check_weapon_employment.py
python tools\check_scenarios.py
python tools\preflight.py "Tasman Shield 09 - The Southern Convoy"
```

`check_inventory.py` is a known red. The mirrored export (§6, step 2)
ran on the PC on 27 Sep (`97eac5f7`) and cleared the ghost files; what stays
red is four mods whose files differ from the manifest only by line endings
(3775128499, 3776340577, 3780118683, 3781062859).
`docs/packaging-and-recovery.md`, *Known red*, gives the
`git add --renormalize` fix. The second red the 30 Sep export added, the missing
Rafale, cleared on 3 Oct, first by retiring the Rafale and then, that evening, by the
French Air Force mod bringing it back (*Known red* has the story). Running the rest again on the PC proves the
PC's Python sees the same tree; it does not change what gets installed. Skip
it if you are short of time; do not skip step 2's checks.

## 4 — install and order, one command

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\sync-sest.ps1
```

What to read in its output:

| Line | Means | If it is wrong |
|---|---|---|
| `IN LINE: all N installed files match this commit (hash)` | the deployed bytes equal the commit | the hash must be step 2's; a different one means the pull did not take. **N is 1266** for this build |
| `1 of 1` installed | the consolidated pack copied | `canonical pack not installed` means the copy failed; nothing below matters |
| `dropped stale workshop entry` | a subscription the repo has not catalogued | none expected. An id it names is a new subscription: export it (`export-mod-configs.ps1`) and push, as the Southern Watch procedure describes |
| `purged SEST_…` | an old per-pack folder removed | only on a machine that still had the per-pack layout |

Where the count comes from, from Southern Watch's 388: the pack ships
`campaigns\sest-southern-reach\` (25 missions with their briefing folders and
charts, 66 art files, `campaign.ini`, roster, commander settings and a
`REQUIRED-MODS.txt`), the browser copies under `missions\Southern Reach\` and
`missions\Tasman Shield\`, a `REQUIRED-MODS.txt` for Southern Watch's own
folder and the two RNZAF base files (691 in all); then this round's Red Line
and ported files (1189; 1171 after the 27 Sep export; 1174 with the three Campaign Rules
pages; 1189 with the three Open Allocation twins; 1201 with The Twelve-Mile Line - its
mission, briefing folder and chart in both copies, its card and the story page before
it - which takes Southern Reach to 26 missions and 69 art files; 1203 on the 0.8.3
game files, SEST Replenishment metering two more hulls' rounds: the early Wasp Modern
US Navy released from its Pending folder and the SY-1 the game repriced; 1265 with
the combat systems - 60 `#!extend` files, one per mod hull given a profile, and the
`combatsystems.ini` and `weapons.ini` Collection Fixes now ships; 1257 the same
afternoon, the PLAN Pack's update having given its own eight hulls their systems; 1260
that evening, the three campaigns' enemy theatre rosters and their twins' copies added and the
retired Rafale F5 pack's three files gone; 1264
late that evening, the Rafale F5 pack's three airframes back on the French Air Force mod and
the game's `loading_tips.ini` Collection Fixes restores over the PLAAF Aircraft Pack's Chinese copy; 1266 on 4 Oct, with `SETUP - double-click me.cmd` and `sest-setup.ps1` at the pack root).

## 5 — confirm the campaigns arrived

```powershell
$sa = "<…>\Sea Power_Data\StreamingAssets\SEST_Integration"
Get-ChildItem "$sa\campaigns" -Directory | Select-Object Name        # sest-red-line, sest-southern-reach, sest-southern-watch, each also with -open
(Get-ChildItem "$sa\campaigns\sest-southern-reach\art\*.png").Count   # 49
(Get-ChildItem "$sa\campaigns\sest-southern-reach\missions\*.ini").Count   # 26
(Get-ChildItem "$sa\campaigns\sest-red-line\art\*.png").Count         # 12
(Get-ChildItem "$sa\campaigns\sest-red-line\missions\*.ini").Count    # 6
Test-Path "$sa\land_units\airbase_rnzaf_ohakea.ini"                   # True
Test-Path "$sa\vessels\plan_aor_type901.ini"                          # True: Replenishment arrived
Get-ChildItem "$sa\missions" -Directory | Select-Object Name          # Red Line, Southern Reach, Southern Watch, Southern Watch - Dispatches, Tasman Shield
```

Then in game, in this order:

1. **Mod Manager** — `SEST Integration Pack` at the top, enabled; its
   description lists SEST A-10C+, SEST Intercept Model and SEST
   Replenishment At Sea among the packs and ends "Southern Watch - Southern
   Reach - Red Line".
2. **Campaign list** — six entries: `Southern Watch (Royal Australian
   Navy)`, `Southern Reach - Tasman Shield (Royal Australian Navy)` (46
   entries, a dark chart 29–66°S behind it) and `Red Line - The Other Watch
   (People's Liberation Army Navy)` (10 entries), and each again with
   `- Open Allocation` before the navy in brackets. The Campaign Rules button
   at the bottom right of each opens its rules page.
3. **Mission browser** — folders `Southern Reach` (12), `Tasman Shield`
   (14) and `Red Line` (6) beside the Southern Watch ones. If the campaign
   list is short but the browser has every folder, the Mod Manager is not
   reading one of the `campaigns\` folders; that difference is the diagnosis.

## 6 — the other sessions' branches: what was ported, what was not

Two older lines held work the deploy branch lacked: `sest-dev/kind-faraday-ctr5h0`
(with `beautiful-cerf-i7fqei`, `fix/banda-front-lean-finalize` and
`affectionate-volta-3xqkx6` inside it) and `feature/ras-integration` with
`chore/workshop-inventory-20260916` (the INV line). Neither was merged whole:
each forked in late August from a mod list older than the PC's. Instead,
eleven items were ported one by one, each rebuilt against today's export and
reviewed on its own before it landed here (merge `17df05a6`):

1. The JMSDF Seahawk rename (SW10, the Mogami pack, the Banda vignette, the
   Northern Front saves), the exporter's deletion mirror, and mission
   installs with no timestamped backups (`-PurgeBackups`).
2. The editor-crash sweep over every mission the installer deploys (32
   aircraft in nine files), `preflight --all` and `check_alias_bases`.
3. The land-defence site builder and the Indo-Pacific Land Assets showcase.
4. Banda Front Lean v2 and Living Seas as saved, `restore_roe`, and the
   generator chain behind them.
5. ARRW boost-glide, the Redback's seeker reach and the AIM-424 respec
   (680 kg).
6. The SM-3 overwrite's seeker and handover, folded into SEST Collection
   Fixes.
7. SEST Intercept Model: the global intercept table restored.
8. SEST A-10C+ and the standard A-10C's infrared head and squadron repairs; a
   second Warthog in D8.
9. `check_inventory`, `check_scenarios`, a stricter `check_dependencies`, and
   SW11's ghost Burke retargeted.
10. SEST Replenishment At Sea: working replenishment for the modern fleet,
    HMAS Supply and Stalwart real suppliers.
11. Eleven NF3 scenarios regenerated, with supply ships where the load order
    defines them.

Deliberately **not** ported:

| Item | Why not |
|---|---|
| SEST YF-23 MALICE pack | upstream now ships the fit: the restructured YF-23 mod carries its own AIM-424 intercept loadout, and the file the pack patched is gone |
| SEST Zumwalt CPS | retired on 20 Sep (`1233fd41`): Modern US Navy fixed both defects it existed for |
| the F-15EX AIM-260 seat lift | withdrawn (`afed87ce`) after an in-game report: the number was measured against a different missile mesh |
| the U.S. Navy 2027 retargets | not needed: the aliases resolve today, and `check_alias_bases.py` proves it after every export |
| the standalone SEST Aegis BMD pack | superseded: its SM-3 seeker and handover values are in SEST Collection Fixes (item 6), and its floor, range and loft were decided otherwise here |
| INV's `generate_load_order` and exporter rewrites | written on the 16 Sep base; the tools here have moved on since (the kind-faraday deletion mirror, unsubscribed mods dropped from the order), and the rewrites would undo that |
| peaceful-gauss's Workshop staging script | built for a two-item Workshop release that the one-pack design replaced |

The other branches (`feature/northern-front-iii-export`,
`sest-dev/quirky-noether-fq5i98`, `claude/repo-cleanup-interoperability-hleer5`)
hold nothing the deploy branch lacks.

### One-time steps on the PC for the ports

Game closed, after the sync in step 4:

1. **Clear the old backup missions.** Installs no longer write
   `* backup-<stamp>.ini` copies, but the old ones are still in the game's
   mission list. Preview, then purge:

   ```powershell
   powershell -ExecutionPolicy Bypass -File .\tools\install-sest-packs.ps1 -PurgeBackups -WhatIfOnly
   powershell -ExecutionPolicy Bypass -File .\tools\install-sest-packs.ps1 -PurgeBackups
   ```

   Only names ending ` backup-<digits>` are touched; a mission of your own
   called "Strait backup-plan" survives.
2. **Run the export once, now that it mirrors deletions.** Done on 27 Sep
   (`97eac5f7`): it deleted the ghost files earlier exports left behind, 192
   over 13 mods (`docs/packaging-and-recovery.md`, *Known red*), and the
   packs were rebuilt on it (`1a1befbc`). A later export mirrors the same
   way, so it should delete only what authors have removed since:

   ```powershell
   powershell -ExecutionPolicy Bypass -File .\tools\export-mod-configs.ps1 -IncludeVanilla
   git status --short mods-source
   ```

   Review any deletions, then commit and push. `python tools\check_inventory.py`
   stays red on four mods whose files differ only by line endings until they
   are renormalised; the same section gives the fix.
3. **Rebuild after that export, and after every export from now on.**
   SEST Replenishment At Sea freezes about 300 hulls at the export it was
   built from, so a pack older than the mods beside it puts last month's hull
   above this month's mod. `python tools\build_all.py --from-scratch`, commit
   the output with the export, push; or push the export alone and say so, and
   the next session rebuilds on it.
4. **Sync again** so the game carries the rebuilt pack.
5. **Clear the rest of the backup clutter**, game closed. Preview, then clean:

   ```powershell
   powershell -ExecutionPolicy Bypass -File .\tools\clean-backups.ps1 -WhatIfOnly
   powershell -ExecutionPolicy Bypass -File .\tools\clean-backups.ps1
   ```

   It removes, from the game's `user_missions` only, any `.ini` with "backup"
   in its name, `* - Copy.ini`, `*.bak`/`*.old`, and `_briefing` folders whose
   mission is gone; and every `usersettings.ini.bak_*` but the newest three
   (each sync writes one; `set-mod-order.ps1` now prunes to three itself).
   Read the preview: a mission of your own with "backup" in its title is on it.
   If the missions are back after the next launch (seen on the PC: every
   purged backup returned), Steam Cloud restored them. Start Sea Power, stay
   at the main menu, run the two lines again, then exit the game normally.

## 7 — then play

Each test card now opens with a short *first things to fly after this round*
list: the in-game checks the ports added, pointing at where each is written
up. Southern Watch's (`../southern-watch/test-card.md`) has the most of them.
Southern Reach's (`test-card.md`) still starts with the coastline, and Red
Line's (`../red-line/test-card.md`) with its rules of engagement.

---

## When something is wrong

| Symptom | The command that answers it |
|---|---|
| `git merge --ff-only` refuses | expected for `claude/campaign-missions-lore-td653z`, which lacks `10b6b48b`, `7d670392`, `d4fd1668` and `fa692245` (skip step 2's merge); for a branch a round hands you, `git log --oneline origin/sest-dev/loving-bell-3cnvvw -5` — whatever is there and not on that branch was pushed after it was cut; report it |
| sync refuses on the branch guard | you are not on `sest-dev/loving-bell-3cnvvw`; go back to step 1 rather than passing `-AnyBranch` |
| an Open Allocation entry is missing from the campaign list, or will not load its first mission | the twin loads its missions from the standard campaign's folder, which stock never does: Southern Watch test card 6G, G.1 and G.3 say what to bring back. The standard entries are unaffected either way |
| the game stops responding in the middle of a mission, above all one with sonobuoys in the water | a mod's debug logging: `powershell -ExecutionPolicy Bypass -File .\tools\quiet-mod-debug.ps1` (the sync runs it too), then capture with `-IncludeSaves` if it happens again - the capture now includes BepInEx's log, where code mods write |
| Rig Seventeen dies loading again | `powershell -ExecutionPolicy Bypass -File .\tools\capture-context.ps1 -Redact -IncludeSaves` with the game closed, then commit `data\install-snapshot` and push the deploy branch: the log names the step and the save shows the force |
| a campaign is missing in game but present on disk | `Get-ChildItem "$sa\campaigns\sest-southern-reach"` (or `sest-red-line`) shows the files; the browser copies are your route in, and the difference is the report |
| a Southern Reach unit is missing in a mission | the unit names its mod: `campaigns\sest-southern-reach\REQUIRED-MODS.txt` lists the hard-required Workshop mods for this campaign, with their count; `.\tools\show-load-order.ps1` shows which are enabled |
| a Red Line unit is missing in a mission | `campaigns\sest-red-line\REQUIRED-MODS.txt` lists the hard-required Workshop mods for that campaign, with their count |
| a ship is ashore or a route crosses land | the coastline extract disagrees with the game there; note the mission and the hull, that is the first row of the test card |
| `check_inventory.py` red after the export | read `docs/packaging-and-recovery.md`, *Known red*, before deleting or restoring anything |
| a code mod does nothing: Coordinated Strike Tool's planner (F8) does not open | Anchor Chain's preloader is not installed; subscribing is not enough. See below |
| Sea Power itself updated (Steam fetched a new build; the Mod Manager flags the SEST pack or a mod as version-incompatible, or a stock unit a mission fields is gone) | `docs/packaging-and-recovery.md`, *After a Sea Power update*: its PC block exports the new game files with `-IncludeVanilla`, captures the snapshot and pushes the deploy branch, game closed after one launch; a session then reads the drift (`check_vanilla_drift.py`), bumps the packs' version (`check_game_version.py --bump`), rebuilds, runs every gate and hands back the update block at the top of this page, whose `IN LINE` count may have moved |

### Code mods do not load (Coordinated Strike Tool)

Sourced from the Anchor Chain docs and the Coordinated Strike Tool's Workshop
page. Game closed.

1. Download `ACPreloader.zip` from the latest release at
   <https://github.com/SeaPower-Modders/AnchorChain/releases>.
2. Copy the contents of the folder in it that holds `winhttp.dll` into the
   Sea Power folder, beside `Sea Power.exe` (this needs admin rights). The
   Explorer route is equally good: Extract All, open the folder holding
   `winhttp.dll`, and copy its contents beside `Sea Power.exe`, leaving out
   any `changelog.txt` (the game has its own). Or save the
   zip into the Sea Power folder and paste this into PowerShell run as
   administrator (change `$g` if Steam lives elsewhere):

   ```powershell
   & {
   $ErrorActionPreference = 'Stop'
   $g   = 'C:\Program Files (x86)\Steam\steamapps\common\Sea Power'
   $zip = Join-Path $g 'ACPreloader.zip'
   if (-not (Test-Path -LiteralPath (Join-Path $g 'Sea Power.exe'))) { throw "Sea Power.exe not found in $g - stopping" }
   if (-not (Test-Path -LiteralPath $zip)) { throw "ACPreloader.zip not found in $g - stopping" }
   $tmp = Join-Path $env:TEMP ('ACPreloader-' + [guid]::NewGuid().ToString('N'))
   Expand-Archive -LiteralPath $zip -DestinationPath $tmp
   $hits = @(Get-ChildItem -LiteralPath $tmp -Recurse -Force -Filter winhttp.dll)
   if ($hits.Count -ne 1) { $hits.FullName; throw "Expected one winhttp.dll in the zip, found $($hits.Count) - stopping" }
   $src = $hits[0].DirectoryName
   foreach ($n in 'doorstop_config.ini', 'BepInEx') { if (-not (Test-Path -LiteralPath (Join-Path $src $n))) { throw "$n is not next to winhttp.dll in the zip - stopping" } }
   $items = @(Get-ChildItem -LiteralPath $src -Force | Where-Object Name -ne 'changelog.txt')
   $clash = @($items | Where-Object { Test-Path -LiteralPath (Join-Path $g $_.Name) })
   if ($clash.Count) { $clash.Name; throw 'These are already in the game folder - stopping so nothing is overwritten' }
   'Copying: ' + ($items.Name -join ', ')
   $items | Copy-Item -Destination $g -Recurse -Force
   foreach ($n in 'winhttp.dll', 'doorstop_config.ini', 'BepInEx') { '{0}: {1}' -f $n, (Test-Path -LiteralPath (Join-Path $g $n)) }
   }
   ```

   It checks every path before it copies anything and stops rather than
   overwrite. If the prompt still shows `>>` after pasting, press Enter once
   more.
3. Confirm `winhttp.dll`, `doorstop_config.ini` and `BepInEx\` are beside
   `Sea Power.exe`.
4. Enable Anchor Chain and Coordinated Strike Tool in the Mods menu, exit
   the game fully and start it again.
5. `BepInEx\LogOutput.log` should have the line `Coordinated Strike Tool
   1.3.1 loaded. Press the panel hotkey (default F8) in a mission to open
   the planner.` (the 30 Sep snapshot has it, `data\install-snapshot\bepinex.log`).
6. Press F8 inside a running mission.

One BepInEx only: the multiplayer launcher installs its own. If `BepInEx` is
already in the game folder, do not copy a second over it (the script above
stops there).
