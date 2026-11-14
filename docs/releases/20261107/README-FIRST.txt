SEST R14 FOR SEA POWER 0.9.2: FULL PC ACCEPTANCE RUN
(R12 Final + nations + Red Line 3-4 + Russia + Makran + R14)
14 November 2026 | SEST-DEV
Game on your PC: Sea Power 0.9.2 Build 261113, a public release (your
capture of 14 November, 14:51)
Pack data: rebuilt on the game's 0.9.2 files (your export of that capture)
and on the mods as installed then; every pack declares 0.9.2
SEST code: R14 (Runtime 1.7.0 / UI 1.5.0, loader bootstrap 0.6.0), matched to
Sea Power 0.9.2 Build 261113 (Seapower-Scripts.dll 3f56861f) only, from your
reference ZIP of 14 November. It is compiled here and passes the 16 managed
and installer checks; it has never run in the game. This run is its first.
Nothing has been uploaded to Steam. Post only after this run passes.

WHAT CHANGED SINCE THE LAST VERSION OF THIS FILE
- SEST's code is matched to 0.9.2 (R14). Prepare-PC and Repair-PC work again
  on 0.9.2; the old "do not run Prepare-PC" warning is gone.
- On 0.9.2 Anchor Chain's own preloader always logs "Could not find
  AnchorChain chainloader": it looks before Steam has registered the
  Workshop folders. SEST's loader waits for them and then starts Anchor
  Chain itself. With SEST's features on, that line is expected; SETUP now
  says so instead of warning.
- SEST holds, before they load, the author plugins that call game code
  0.9.2 removed (Enhanced Decoy Mod, Multi-Stage Missiles, Osprey Mechanics
  and its deck operations, the flat Topographic Map) and those whose own
  build check rejects 0.9.2 (the Alpine runtime fixes in two items, Saronic
  Corsair strike, MV-75 fixture tilt, EC-2 comms jamming, K5 Kraken contact
  strike). ExtendedGuidance stays off by the SEST profile. Their data stays.
- Decision 6 is answered by the game's code: 0.9.2's own [RibbonAward_]
  rules test campaign variables that mission triggers set, and no trigger
  sees survivors rescued or a mission with no launch. Red Line's two
  ribbons therefore stay in SEST's runtime (R14).
- Dynamic Campaign Mod and Coordinated Strike Tool still declare game
  versions that end below 0.9.0. Global Maritime Operations 2028 needs
  Dynamic Campaign Mod.
- 59 of your installed mods carry the 0.8.7 mark SETUP wrote into their
  _info.ini before the update ("SEST marked this mod compatible"). The
  capture keeps each author's own file, and nothing is taken from a mark.

0. BEFORE STEP 1 (game closed; this installs nothing)
   a. Start Sea Power once only to open Mod Manager, then: switch your local
      test folder SEST_090_PC_TEST OFF, switch the subscribed "SEST
      Integration Pack - Modernised Campaigns" ON and move it to the top.
      R14 installs into that Workshop item (3812461539) and refuses to stage
      while it is out of the load order. Keep the collection on. If Mod
      Manager lists Dynamic Campaign Mod or Coordinated Strike Tool as not
      compatible, switch them on anyway if it lets you, and say whether it
      did: World Operations (step 2) needs Dynamic Campaign Mod. Quit.
   b. Keep SEST and the collection subscribed. Do not unsubscribe anything
      unless step 1 says so.

PREPARE AND CHECK
1. Close Sea Power. Extract this COMPLETE toolkit into a NEW folder and run
   Prepare-PC.cmd. It prints "Release checkout: ..." and "Beta journal:
   <phase>". Keep both lines. What happens next depends on the phase:
   - enabled (most likely: your PC still has the R12 World Map Costs test
     build of 9 November): it repairs that installation to R14, installs the
     release data and ends with the line "VERIFIED: all 4596 canonical
     upload files match the release manifest." Go to 1b.
   - none or restored: it stages R14 and stops with "Next: start Sea Power,
     wait at the main menu about 10 seconds, quit, then run Prepare-PC.cmd
     again." Do that; the second run switches R14 on, installs the data and
     prints the VERIFIED line.
   - staged: it switches R14 on (or asks for the main-menu launch first, as
     above), installs the data and prints the VERIFIED line.
   If it stops instead:
   - "Installed candidate files are not a reviewed beta candidate ..." on an
     enabled journal: your capture of 14 November showed SEST.RuntimeFixes.dll
     missing from the Workshop item's plugins folder, while the four other
     files are exactly the R12 World Map Costs build. Put that build's own
     file back from the release checkout, then run Prepare-PC.cmd again.
     Open PowerShell, paste this block as it stands, then type the Release
     checkout path when asked (it checks the file's SHA-256 first and never
     overwrites anything):
       & { $ErrorActionPreference = 'Stop'
       $checkout = Read-Host 'Release checkout path from Prepare-PC'
       $src = Join-Path $checkout 'integration\beta-feature-parity\candidates\R12-WorldMapCosts-20261109\SEST.RuntimeFixes.dll'
       $dst = 'C:\Program Files (x86)\Steam\steamapps\workshop\content\1286220\3812461539\plugins\SEST.RuntimeFixes.dll'
       if ((Get-FileHash -LiteralPath $src -Algorithm SHA256).Hash -ne 'EED2E5083E8C843BDB64DCF8C98E7C14CDEE24D7192EFD30386A2B4C2039CFE8') { throw 'Not the R12 World Map Costs file; nothing copied.' }
       if (Test-Path -LiteralPath $dst) { throw 'A SEST.RuntimeFixes.dll is already there; nothing copied. Send the Prepare-PC error instead.' }
       Copy-Item -LiteralPath $src -Destination $dst
       'Copied. Run Prepare-PC.cmd again.' }
   - "Existing SEST code differs from the captured baseline" or "An earlier
     candidate file already exists" (no journal, or a restored one): the
     test files are still in place without a journal that owns them. In
     Steam, unsubscribe from the SEST Integration Pack, wait until Steam has
     removed it, subscribe again and let it download (that puts back the
     published plugins). Then move these two, if present, to a new folder
     in Downloads (do not delete them): Sea Power\BepInEx\plugins\
     SEST.BetaSafeBootstrap.dll and the folder Sea Power\BepInEx\config\
     SEST-BetaAnchorChain. Redo step 0a, then run Prepare-PC.cmd again.
   - Anything else: keep the window's text and send it; do not work round it.
   Prepare-PC installs both code and campaign/loadout data; Repair-PC alone
   only repairs code. The author-update guard and original restore journal
   remain in place. Steam branch, subscriptions and saves are unchanged.
1b. R14's own check (first launch with R14 on). Start Sea Power to the main
   menu, quit, and open two logs. The release checkout's
   integration\beta-feature-parity\R11-PC-TESTS.txt, section "R14 SEA POWER
   0.9.2", lists what they must show; in short:
   Sea Power\BepInEx\LogOutput.log:
   - "SEST Beta Safe Anchor Chain 0.6.0", "Sea Power 0.9.2-261113 verified
     (3f56861f)", "BETA SAFE BOOTSTRAP READY; enable=True", "Starting
     bounded Anchor Chain 1.1.0 fork once.", "Loaded AnchorChain V1.1.0!"
     and "Bounded Anchor Chain loader returned to bootstrap.";
   - [Beta compatibility] ADAPTED for exactly DynamicCampaignMod,
     IdentifyExpanded, CoordinatedStrikeTool, SeaPowerSquadPanel, TestRange,
     OptimalTargetDist, MissileControlMod and SeaPowerTopo;
   - [Beta compatibility] SKIPPED before CLR load for exactly the twelve
     named at the top of this file (AlpineSeaPower twice), each with its
     reason, plus one expected line that is not one of them: "SKIPPED native
     library before CLR metadata scan: version.dll" (Saronic Corsair's own
     native helper);
   - "Loaded assembly" for every other author plugin, with no "Error loading
     assembly". Sub Ammunition's item also ships its pre-0.9 files in a
     backups folder, so a second "Loaded assembly SecondThrustMod" and
     "SubAmmunitionMod" line and two "Attempted to load a duplicate plugin"
     warnings for them are expected; the current files load first and run.
   %USERPROFILE%\AppData\LocalLow\Triassic Games\Sea Power\Player.log (SEST's
   own lines are written there):
   - "[SEST Runtime] ... installed" lines and "[SEST UI Follow-up] 1.5.0 beta
     input fix installed; full Runtime 1.7.0 paired", and no "[SEST Runtime]
     ... disabled for this session" line.
   Any difference stops the run here: quit, run R14\Capture-Repair-Results.cmd
   and send the capture with both logs. If the lists match, run SETUP -
   double-click me.cmd from the Workshop item once (game closed): among the
   checks near its start it should print "[ok] last launch: SEST's bundled
   loader started Anchor Chain", and it should finish with "All done".

2. Load an existing world. Press F11 and select Service. Check the
   existing awards/progress, the longer ribbon list, scrolling and
   citations. Complete an accepted Admiralty order and return to the map.
   The task count should rise once; the battle count and combat USD totals
   must not. If you can, complete a multi-phase operation as well: it should
   add one task. Since R13 a task counts even if you close its paper at once.
   World Operations needs Dynamic Campaign Mod on (step 0a); if Mod Manager
   would not switch it on, say so and skip this step.
   A world started on 1.6.2 or 1.6.3 keeps SEST's text as its saved SITREP
   001; a new world shows DCM's report with the SEST brief first.
3. Start a new Southern Watch or Southern Reach campaign. The Service Record
   offers the fourteen nations; Australia is the default. Compare one Anzac
   and one Burke price as an Australian and as a US commander. Check that
   the British commander's ranks from Lieutenant up show the game's Royal
   Navy insignia (new in 0.9.0) and the White Ensign emblem. Pick
   New Zealand and South Korea, and Thailand in Sulu Line: each shows its
   default name (Rawiri Tipene, Seongjin Han, Suphachai Kaeokham) and its
   emblem. Press the random-name button several times: the name should change
   each time to another from the SEST pool, given name first; if it stays on
   the default, the pool did not load. Pick Germany or Norway: the accented
   rank title draws on the commander screen and in a citation. After a
   qualifying result, confirm the native Service Record shows the right awards
   and that a citation's date is the mission's, not 1985; as a South Korean
   commander the National Security Medal shows its taegeuk (SW08), as a German
   one the Cross of Honour its gold cross. A failed mission must not grant the
   mission award. Reopen the campaign to check persistence. Hold clocks
   (required before posting): in Red Line's RLC1 note the minute the lead ship
   comes within three cables and the minute "Pilot aboard." appears (about
   four minutes later); in Southern Watch 03 Rig Seventeen note the minute the
   second lifter is over the rig and the minute "Rig crew loaded." appears
   (about three minutes later). If either appears at once, say so before
   posting. Red Line step 3: the checks P1 to P9 in the release checkout's
   docs/campaigns/red-line/test-card.md cover RL03's two exits, RL04's
   heave-to (with a run where she is sunk first) and the damage condition's
   spelling; report what each shows. Red Line step 4: checks R5 and R6 on
   the same card (the developer ribbon menu offers neither runtime ribbon;
   with MissionAwards=0 neither is granted) and, with R14, R1 to R4: win
   RL05 without launching anything and RLC1 with its pilot recovered, and
   judge each ribbon by the first of its two Player.log lines
   (RIBBONS.txt explains both). On 0.9.2 a won campaign mission cannot be
   played again, so copy the campaign save before RL05 and before RLC1, and
   restore the copy (or start a new campaign) before each further run of
   that mission: R2's runs and R6 with MissionAwards=0 each need RL05 not
   yet won. For R4, save, quit and reload: each ribbon shows once in the
   Service Record, and the won mission's Play stays disabled. Russian Federation (step 5): in the new
   Southern Watch campaign's Situation window the Project 20380 corvette
   shows the Russian Federation flag and the Akula the USSR's; in the
   Mission Editor Russian Navy 21's Admiral Gorshkov and a Su-35S show
   Russian Federation and the game's own Sovremenny and a Cold War Su-27
   the USSR, and the Kuznetsov's 2016 fit shows Russian Federation and her
   1991 fit the USSR; a mission saved with the Kuznetsov's 2016 fit and the
   Akula Gepard holds VariantReference=Variant2 and Variant13 (RU.8);
   Pacific Strike's 02 Action in the Taiwan Strait still generates its
   Soviet force (the release checkout's
   docs/campaigns/southern-watch/test-card.md, 6K, rows RU.1 to RU.8). The
   stubs, like every #!extend file in the pack, apply where SEST's Runtime
   repairs the game's modifier scan (ModifierRegistry, not turned off):
   first read Player.log's "[SEST Runtime] modifier files" line, which
   should count 243 files from this pack (RU.1). If that line is missing or
   counts fewer, or the Gorshkov shows the USSR (RU.2), stop and report it
   before judging anything else that depends on the pack's #!extend files
   (the cost catalogs, Cross-Deck, the combat-system profiles). Step 5 then
   shows whether 0.9.2 applies them with SEST's code off. Makran Line:
   start a new campaign; the Service Record offers Pakistan only, as a Commodore,
   with the flag of Pakistan as emblem. Buy a Tughril, PNS Alamgir and the
   Z-9CE, and assign the Z-9CE to both decks; play The Fuel Road and note
   whether the ships are rearmed before Gwadar Roads, whether the armed
   freighter's SS-N-2s launch there at minutes 14 and 32, and in Port Qasim
   whether Meridian Sentinel heaves to when the lead ship (at Hold) closes
   to about three miles (the release checkout's
   docs/campaigns/makran-line/test-card.md). If time allows, as a
   New Zealand commander buy the P-8A in the force allocation before Weapons
   Free (SW05) at the discounted price and fly it in the Maritime Patrol slot
   of 06 Blind Horizon (Weapons Free has no patrol slot).
3b. New in 0.9, in the same pass. Start each of the five campaigns and look
   at the first screens: 0.9.2 gave its own Pacific Strike three new lines
   for the "Points Based" way of getting units, and the five campaigns now
   carry the same; wherever the game shows that name and its sentence, they
   should read as in Pacific Strike (a blank, a key name such as
   CampaignMode_points_Name, or a campaign that will not start, is what to
   report). Check that Prepare Airbase opens in a mission with one player
   airfield, and in Southern Watch 10 Common Sea, which has two (Darwin
   should be the host); that a mission of each campaign starts from the
   campaign map with the bought task force; and the F10 panel's commander
   and awards tab with a Chinese or Pakistani commander, whose ranks name no
   image. Two looks the files ask for (Southern Watch build notes,
   "Ammunition and unit files"): after a Harpoon salvo, read the weapon
   report for launch failures, which 0.9.0 lists; and ready the Rafale M of
   dispatch D3 The Relief Ship with its anti-ship fit, to see that the
   carrier arms the Exocet, which 0.9.0 gave a supply category no deck in
   the pack stocks.
4. Recheck the opening brief, world Combat Costs sidebar and direct F11
   totals. In Starting Airborne Flights select the RAAF E/A-18G and confirm
   HARM (AGM-88C), AARGM (AGM-88E) and AARGM-ER (AGM-88G) choices. The three
   loadouts were data-tested; the selector still awaits an owner PC check.
   With Pop-Out Windows 1.2.3 installed, check Contacts, Formation and F11
   pop-out and return, on the main and a second display if you have one.
   Check Identify Expanded appears once in Mod Manager, as Workshop. Check
   the mods that now load as their authors built them for 0.9 (Sub
   Ammunition, Second Thrust, Automatic SAR) and the two that keep a small
   SEST fix on 0.9.2 (Missile Control's steering check, the 3D Topographic
   Map's 50 m shallow-water line); note any that misbehaves.
5. Quit. Run "SEST beta features - turn off.cmd", start the game once and
   confirm it starts with the beta features off. On 0.9.2, Workshop code
   mods load only through SEST's loader, so SEST's plugins, Dynamic
   Campaign Mod and the other code mods should not load then; data mods and
   the Task Force campaigns should. Note in the Mission Editor whether the
   Gorshkov still shows Russian Federation (RU.2) with SEST's code off.
   Quit and run "SEST beta features - turn on.cmd". Then run
   R14\Capture-Repair-Results.cmd and keep the capture; send it with your
   notes from steps 1b to 5. The automated checks passed; they do not establish
   native Noesis rendering or gameplay.

POST AFTER THE PC CHECKS
Post only if steps 1b to 5 passed. If any check failed, send the capture and
your notes instead: the Steam texts describe R14 working on 0.9.2, and the
held plugins they name are those of 1b.
6. Run Upload-PC.cmd. It creates a verified publishing copy under
   StreamingAssets and puts STEAM-CHANGE-NOTE.txt on the clipboard. Keep
   this temporary Local mod disabled.
7. Open Sea Power > Mod Manager > Create Mod > Update Existing. Select
   Workshop item 3812461539 and the EXACT folder printed by Upload-PC.cmd.
   Paste the change note and submit. Confirm success and a non-zero size.
8. Update the page description with STEAM-PAGE-DESCRIPTION.txt (Steam BBCode).
   Separate short and collection copy is included if needed.
9. Quit and run Finish-Upload.cmd to move the temporary publishing copy out
   of the game. After Steam downloads the update, open the subscribed pack
   and run SETUP - double-click me.cmd with the game closed. This restores
   the reviewed features if Steam refreshed the normal plugin files.

DECISIONS WAITING FOR YOU (docs/campaigns/southern-watch/build-notes.md,
"Sea Power 0.9.0", "The mods of 14 November" and "Sea Power 0.9.2", has
each with its figures)
1. CIWS. 0.9.0 rebalanced the game's own guns (Phalanx Block 0 anchor 40 to
   65, Block 1 50 to 70, AK-630 20 to 40; volleys cut, cooldowns raised).
   The eleven mod CIWS SEST retuned on 3 October are still on the old
   ladder, as is every other mod's. Move ours now, or wait for the authors?
2. Sensors. The deprecated E-7A Wedgetail mod carries an old copy of the
   game's whole sensors file and is the winning definition of 220 of the
   game's sensors (the lookout, SPS-49, SPG-62, SQS-53 among them). This is
   older than 0.9.0. Restore the game's sections, as SEST already does for
   weapons? It would change detection in every mission. (0.9.2's changelog
   has "modded sensors were not loaded properly" as fixed; what that
   changes for this is not known.)
3. The Royal Navy mod. 0.9.0's own Hermes, Leanders, Rothesay, Lynx HAS.2,
   Nimrods, Sea Dart and Sea Wolf have the ids of units and rounds mods
   already ship, and the mods' files load. The game's South Atlantic
   campaigns then fly the mods' versions. Keep, or restore the game's?
4. Answered by this release if it passes: data and code for 0.9.2 go up
   together. The live item (26 October upload) declares 0.8.7 and its
   LOAD-ORDER names three mods their author has since removed.
5. The game's own file layers. 0.9.0 lets a mod overwrite part of a game
   file ("file layers", its changelog says), and since 13 November the
   Kuznetsov mod does it with short files in an overrides\ folder. If that
   is what it looks like, the pack's 243 #!extend files could be written
   the game's own way and stop depending on Anchor Chain's loader. It needs
   one test on the PC before any work: say if you want it prepared.
6. Settled on 14 November: R14 is built for 0.9.2 (this run), and Red Line's
   two ribbons stay in SEST's runtime, because no 0.9.2 trigger sees
   survivors rescued or a mission with no launch
   (docs/code-on-0.9.2-20261114.md, "Outcome: R14").

This is R12 Final (merged as PR #58) together with the commander nations and
national awards (merged as PR #59), the combined release notes (merged as PR
#60) and Red Line's victory paths, the heave-to and progress reports (step 3
of the builder grammar, merged as PR #61), with step 4's two Red Line runtime
ribbons (merged as PR #62), the beta runtime R13 that granted them on
0.8.7-261107 (on release/r13-20261111) and R14, which grants them on 0.9.2,
step 5's Russian Federation registration of the modern
Russian ships and aircraft (on feature/russia-registration-20261111, in
review) and step 5's Makran Line campaign (on feature/makran-line-20261111,
built on the Russian registration), checked once on the PC and posted as one
update. RIBBONS.txt has every award mapping.
R12-RIBBON-EXPANSION.txt describes R12 Final before the commander nations: use
it only for the R12 review findings fixed and the minor ones still open, and
this file and RIBBONS.txt for the award counts, nations and PC steps. The
R12-*.txt notes are records of the R12 builds; where they say R12\ or R13\,
this toolkit's beta folder is R14\. None of the seven parts has been played
on the owner's PC yet; with R14, step 4's PC checks R1 to R4 on the Red Line
test card apply as well as R5 and R6.

WHAT IS NEW SINCE THE R12 RIBBON TEST BUILD
- R14 for Sea Power 0.9.2 Build 261113 (14 Nov 2026; Runtime 1.7.0 / UI
  1.5.0, loader bootstrap 0.6.0, candidates/R14-20261114): SEST's code is
  matched to 0.9.2 from your reference ZIP of 14 November. Seven of the
  fifteen pinned references moved (the game, Noesis, Anchor Chain 1.2.0,
  Pop-Out Windows 1.2.3 and three Unity modules). SEST's loader now checks
  every author plugin against the game's real members before it loads, and
  holds one that names code 0.9.2 removed, with the member named; the
  rewrites SEST made for author files that no longer exist are retired.
  Two current author files still need a SEST fix and keep one: Missile
  Control 0.1.18.1 (its own startup check would switch it off on 0.9.2)
  and the Topographic Map 1.6.2 (the game's 50 m shallow-water line). Six
  Alpine-family plugins whose own build check rejects 0.9.2 are held.
  The runtime mission ribbons follow 0.9.2's rule that a ribbon already
  held, or held as its replacement, is not granted again (0.9.2 does not
  let a won campaign mission be played again either). The repair
  recognises R13 and the fifteen earlier test builds; that path was not
  run here (the 0.8.7 reference ZIP it needs is not in the repository), so
  step 1 is its first test.
- Beta runtime R13 (Runtime 1.6.5 / UI 1.4.15, the merged
  feature/runtime-mission-awards-20261110): a campaign can name extra
  mission ribbons in SestRuntimeRibbonAwards, which R13 grants at the
  debrief as native award rows, after the game's own completion gate and
  awards. World Operations now records an Admiralty result when Dynamic
  Campaign Mod files it, whether or not its paper is read. MissionAwards=0
  under [Runtime] in plugins/sest_runtime.ini turns the ribbons off. The
  repair accepts every earlier test build; repair and rollback over the
  1.6.2, 1.6.3 and 1.6.4 (R12 Final) packages passed the fixture checks.
- Commander nations: Southern Watch and Southern Reach offer Australia (the
  default), US, UK, Japan, New Zealand, France, Canada, South Korea, Spain,
  Italy, Germany, the Netherlands, Norway and Denmark. Sulu Line offers the
  Philippines (default), Thailand and Australia. Red Line stays Chinese,
  and Makran Line Pakistani.
  Each nation has its navy's officer ranks, a navy name and an emblem; New
  Zealand, South Korea, the Netherlands, Denmark and Thailand use SEST name
  pools. The same-nation discount is the game's own rule and follows the
  commander's nation; each campaign's rules page gives the count. New
  Zealand's one class is the RNZAF P-8A, sold with the allied fleet; no
  class is Canadian.
- Awards: 75 definitions. 25 fictional world awards (beta), 15 fictional
  native campaign ribbons (Makran Line's three are new), and 32 real-award
  representations for 12 nations: 30 personal and service awards matched to
  the commander's starting rank and 2 host-nation unit awards to the task
  group (plus 3 retired US definitions kept so an earlier record still shows).
  In Southern Watch and Southern Reach, commanders of every offered nation
  except Italy, the Netherlands and Norway earn their own nation's awards;
  Sulu Line's Philippine awards go to a Philippine commander. The task group
  receives the host nation's unit award. Every native campaign citation
  carries its granting mission's date and two plain sentences; the world
  awards' citations state their criteria and are undated. The nation filter on
  the native awards was read from the code of game build 0.8.7-261107, and
  0.9.0's own campaigns now write it the same way (ribbon_id,NATION); step 3
  is its first look on 0.9, which adds a commander and awards tab to the F10
  panel. The Korean strips carry the taegeuk and the German
  Cross of Honour its gold cross.
- Red Line: the six combat briefings (RL01, RL02, RL03, RL04, RL06 and
  RLO2) and RLC1's give the terms their victory checks test (distance,
  minute, no incoming weapon); RL01, RL04 and RL06 mark the extra objective
  victory needs "Also required"; RL04's texts describe the withdrawal as its
  5 NM circle.
- Red Line victory paths (builder-grammar step 3): RL03's intercept breaks
  by an F-35 down (exit from minute 9) or, with neither down, from minute
  18 once no F-35 is within 70 NM of the return box's centre (the AIM-120C7
  reach the builder reads). RL04's Meridian Harmony is sunk or, closed to
  about 3 NM by the lead ship (not the helicopter), heaves to, turns
  neutral and follows the group; sinking her after that loses the mission,
  and sinking her first switches the heave-to off. RL02, RL03, RL04 and
  RL06 send progress reports. The engines-stopped outcome stays off until
  a Mission Editor save gives the damage condition's keys (check P1).
- Held stages: RLC1's and SW03's held stages now reactivate their held
  trigger at the arrival, so the four- and three-minute holds should count
  from then; not yet checked in game (step 3).
- Red Line runtime ribbons (step 4, campaign side, merged as PR #62): RL05
  Silent Passage and RLC1 Personnel Recovery are defined in the Red Line
  campaign and keyed for SEST's runtime: R13 (Runtime 1.6.5) on the
  0.8.7-261107 beta, and now R14 (Runtime 1.7.0), which this update ships
  and SETUP installs on Sea Power 0.9.2 Build 261113 only: there it grants
  each at the debrief when its terms are met, and not again once held. The
  game itself ignores the key, as R12 (Runtime 1.6.4) does; neither ribbon
  is counted in the 75 above.
  Each debrief logs two Player.log lines per runtime ribbon: the first is the
  verdict; the second says "already awarded" or repeats it, as Red Line's
  campaign.ini is its own [File] Base and is read twice. The developer ribbon
  menu offers neither (the Red Line test card's R5 and R6; R1 to R4 need R14,
  which SETUP installs on Sea Power 0.9.2 Build 261113 only, and RIBBONS.txt
  says what each needs).
- Russian Federation (step 5, on feature/russia-registration-20261111, in
  review): SEST Collection Fixes registers to the game's Russia nation,
  which it names Russian Federation, instead of the USSR: 16 post-1991,
  Russian-built ship and submarine classes (the Gorshkov and Grigorovich
  frigates, the Steregushchiy, Gremyashchiy and Buyan-M corvettes, the
  Yasen, Belgorod, Borei and Improved Kilo boats); the modern refits of
  Soviet-built ships in their modern fit only (the Kuznetsov's 2016 fit,
  not her 1991 one, Admiral Nakhimov's refit, Marshal Ustinov 2016, the
  Nanuchka III Smerch in her 2019 refit, the Tarantul R-60 of 2005, the
  REDFOR mod's Smetlivy in her 1995 Project 01090 refit) and the Akulas,
  Oscar IIs and Grishas launched after 1991, the Sierra II Pskov and
  Admiral Chabanenko (launched in 1992 and 1994); and 32 aircraft of
  post-1991 Russian types and upgrades (the Su-57, Su-35S, Su-30SM, Su-33,
  MiG-31BM, MiG-35, MiG-29K 9.41, A-50U, Tu-214R and their like). One
  #!extend stub per unit sets only the Nation of its mod's variants or
  squadrons file, listing the file's earlier sections empty so the game
  keeps the author's variant order; no author's file is copied. SEST's
  Akademik Pashin registers Russia in its own file. The Soviet-era fits,
  Cold War aircraft (the Su-27, MiG-31, MiG-29 9.12, Tu-160 as built,
  Tu-95MS, Il-76MD, Il-78, Ka-27PL, Mi-8, Mi-24), fictional variants and
  hulls never built stay Soviet, as stock Cold War missions use them.
  Every unit a SEST mission places still flies the Russian flag, as
  before; an aircraft a Russian deck or airbase launches flies its own
  squadron's registration, so a launched Su-33 or Su-57 now shows the
  Russian Federation and a launched Ka-27, Su-27 or Tu-160 the USSR. No mod
  has used an #!extend on a variants or squadrons file before, so it is
  checked once in step 3; no campaign offers a Russian commander, so the
  discount is not.
- Makran Line (step 5, on feature/makran-line-20261111): a
  fifth authored campaign, four Pakistan Navy missions in the North
  Arabian Sea, 24 October to 14 November 2028, inside Southern Watch's six
  weeks. The opponent is the fictional Meridian network alone, in armed
  merchants and trawlers; no Indian or Iranian state unit is placed. The
  roster is the Pakistani Pack's (the Tughril class, PNS Alamgir - kept
  for 2028 as a stated assumption - the Z-9CE, the pack's Sea King, the
  JF-17 Block II and III and the ZDK-03), every class with the same-nation
  discount; no submarine, no J-10CE. With no Pakistani supply ship in the
  collection, every force allocation rearms. Port Qasim's mothership is
  sunk or made to heave to, as Red Line's RL04 coaster is. The commander
  is a Pakistan Navy Commodore with the Navy's ten ranks (abbreviations
  not verified) and fictional ribbons only. Nothing in it has been run in
  the game. This update ships it: the upload includes
  campaigns/sest-makran-line, and the change note, page, short and
  collection texts pasted in steps 7 and 8 announce it as the fifth
  campaign. To hold it back, do not post this update; ask for a build
  without it.
- World Operations (beta): DCM's own SITREP 001 is kept, with the short SEST
  brief shown first. Completed multi-phase Admiralty operations now count
  once each, and a completion replayed after a reload counts once. Tabs
  rebuild only when their content changes. The battle checklist uses the
  mission clock, which every mission load resets.
- Beta loader: DCM's anti-ship salvo hold no longer switches itself off
  (the third reference to the game member is adapted too). Pop-Out 1.2.0 is
  accepted alongside 1.1.3 after a method-by-method IL comparison, so the
  Contacts fix, Formation UI mode and camera compass stay on with it. The
  formation pop-out bridge now recognises the inspected Group Manager.
  (R14 accepts Pop-Out 1.2.3 in place of 1.2.0, after the same checks.)
- SETUP: the feature step runs only on the game build its bundle targets,
  now Sea Power 0.9.2 Build 261113 (R14). On any other build it restores
  the normal Workshop plugins and continues, and problems
  are warnings, not errors. Three launchers sit beside SETUP:
  "SEST beta features - turn off.cmd", "- turn on.cmd" and "- remove.cmd".
  Turning off writes %LOCALAPPDATA%\SEST\BetaCompatibility\features-off.json,
  which SETUP respects. The publishing copy now uses a short folder,
  StreamingAssets\SEST_UP_<8 hex>.
- Workshop capture of 12 Nov 2026 (b362b5cf): 42 author updates taken in.
  The standalone J-8, J-11 and Y-8/Y-9 family left the Workshop and the
  load order (200 Workshop mods: the collection's 199 and the B-21
  Raider); the PLAAF Aircraft Pack flies Southern Watch's J-11BG and
  J-8Fs. Collection Fixes defines the KQT-8 MAD of the PLAN Pack's Y-8FQ
  and Y-9FQ and the ZDK-03's RWR, and restores the game's R-27T/ER/ET.
  The capture's game is 0.9.0 Build 261111 (buildid 26599367), and the
  Anchorchain Expansion now declares 0.9.0 to 0.10.0 only (validation.json).
- Sea Power 0.9.0 (13 Nov 2026): the game's 0.9.0 files are taken in and
  all 25 packs are rebuilt on them and declare 0.9.0 (4,592 files in the
  upload that day; 243 #!extend and #!prepend files; 1,633 recruitment
  entries in the world campaign). Found by reading the update against the
  pack, and
  changed: the game's ten changed combat-system profiles, its Western MAD
  and its mini-map settings are restored over mods' stale copies; the
  campaign files write the keys 0.9.0 added to its own campaigns (the map
  UI, the single task force, the staging airfield of the 42 missions that
  offer Prepare Airbase, the Campaign Mission flag); the British
  commander's ranks from Lieutenant up name the game's new Royal Navy
  insignia; 56 reviewed cost entries price 0.9.0's ships, aircraft and
  rounds by class, and the cost list now covers units defined by #!copy,
  which the game's own files use for the first time; SETUP's step 1 no
  longer tells a 0.9.0 player the game is "not recognised". SEST Cross-Deck
  extends six of the game's new Royal Navy hulls (Sheffield in three fits,
  the Amazon, Broadsword and Leander classes). Not changed, and waiting for
  you: the decisions listed at the top.
- The mods of 14 Nov 2026 (your report and two ZIPs of mod text, taken
  against commit 01cfa43b): eighteen author updates taken in, 175 files
  changed, 8 added, 5 removed. Most of it is the 0.9 form: the French Air
  Force's 80 aircraft and the Flanker family on the new flight model, with
  aerial refuelling and measured areas. What changed in substance: the
  Korean destroyers and frigates and the Hyundai export ships carry the
  SSM-700K where they had the mod's "Harm-II" anti-ship round, and the
  Sejong the Great the SM-6 where she had the SM-3 Block IIA; the F-15J
  lost its AirToAirIntercept fit; the Kuznetsov mod
  no longer replaces the game's E-2C, F-14A and Ka-27 squadron files and
  adds to them from an overrides folder instead. No builder stopped and no
  mission lost a unit, fit or squadron. The rebuild moved 17 forked ships
  and the three Rafale F5 aircraft onto their authors' new files, and
  dropped the fork of one round no ship carries any more (4,591 files in
  the upload that morning). Southern Watch and Southern Reach now need the
  Kuznetsov mod for a round, no longer for a squadron.
- Sea Power 0.9.2 (14 Nov 2026, your capture of 14:51 and its game export):
  the game's 0.9.2 files are taken in (4,500; ten files 0.9.2 no longer
  ships are removed), with seven more author updates (228 files changed,
  15 added, 6 removed), and all 25 packs are rebuilt and declare 0.9.2:
  4,596 files in the upload, 243 #!extend and #!prepend files, 1,636
  recruitment entries in the world campaign. From the game: almost all of
  0.9.2's 1,127 changed files are re-measured areas and volumes, which the
  forks take with their base files; the five campaigns write the three
  unit-acquisition lines 0.9.2 added to Pacific Strike and ship its
  campaign_localizations.ini; the new submarine Hai Shih is priced and in
  the world campaign's buy list. From the mods: Euromod's Main Pack gives
  186 rounds a volume and adds the Spearfish and the Royal Navy's
  submarine sonars; the Modern British Navy adds the Astute and Vanguard
  classes (priced, and in the buy list); the Modern US Navy re-parks the
  Ford's deck and gives the MH-60S a fourth squadron; the Italian Navy mod
  no longer ships its Skyguard launcher, so SEST no longer names it. No
  builder stopped and no mission lost a unit, fit or squadron.

RETAINED FEATURES
- Global Maritime Operations 2028, the one world in the campaign menu since
  R11: 196 bases, 293 force groups, 54 patrols and 1,636 recruitment entries;
  40 added airfields and 37 reviewed positions. The original World Sandbox
  stays under legacy_campaigns/ for tools\select-legacy-world.ps1 (see
  WORLD-CAMPAIGN-READ-ME.txt).
- Eight coalition command stages, varied native Admiralty rewards and
  recruitment progression; no new base-construction mechanic is claimed.
- Paused battle preparation, clear native end-battle/debrief flow, readable
  opening brief, world-map Combat Costs and direct cumulative F11 USD totals.
- Three conventional Growler starting-flight fits, coordinated strike
  presentation, current Topography/Pop-Out support and Identify preservation.
- Southern Watch and Southern Reach open their whole rosters and the allied
  fleet (52 ship classes, and 20 and 11 aircraft types) from Weapons Free and
  Tasman Crossing; Red Line from the start, Sulu Line from Service at Sea
  and Makran Line from Gwadar Roads.
- Reviewed beta features inside the normal Workshop SETUP flow, upgrade
  recovery and rollback over the 1.6.2, 1.6.3 and 1.6.4 test builds.
  Normal active release plugins stay in the upload; the installer selects
  the five reviewed files on Sea Power 0.9.2 Build 261113.

The owner accepted the four briefing/costs/page changes on 9 November.
None of the seven parts has been played on that PC yet. R12 Final, the
commander nations and Red Line steps 3 and 4 are merged on dev (PRs #58 to
#65, with the Steam images for R12 and the world campaign). This release
combines three branches on release/r13-combined-20261112: step 5's Russian
Federation registration (feature/russia-registration-20261111, in review),
step 5's Makran Line (feature/makran-line-20261111), which builds on it, and
R13 (release/r13-20261111: dev at a0721c18 with the R13 runtime merged as
00bca642 and packaged). None of the three is on dev or beta yet. The 0.9.0
rebuild of 13 November and the 0.9.2 rebuild of 14 November are on
claude/continue-previous-session-39wqwq, on top of the combined branch; R14,
the SETUP and PC-toolkit changes for 0.9.2 and this file are on
sest-dev/exciting-fermi-kb5bs9, which starts from that branch's head
(ac829bfb). None of it is on dev or beta.
This toolkit's branch, sest-dev/exciting-fermi-kb5bs9, is the branch the PC
installs, tests and posts from for this run, and the one its
SOURCE-RECEIPT.json names; Prepare-PC.ps1 accepts sest-dev/ branches. Once
the release is merged into dev and dev into beta, the toolkit is built from
beta again (docs/BRANCHES.md). Nothing has been uploaded to Steam.
