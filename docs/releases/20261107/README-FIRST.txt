SEST R12 FINAL + NATIONS + RED LINE 3-4 + RUSSIA + MAKRAN + R13: PC ACCEPTANCE
13 November 2026 | SEST-DEV
Game: Sea Power 0.9.0 Build 261111 (released 11 November 2026)
Pack data: rebuilt on the game's 0.9.0 files; every pack declares 0.9.0
SEST code: matched to 0.8.7-261107 (Runtime 1.6.5 / UI 1.4.15, R13) and to
0.8.7-261021 (Runtime 1.5.0 / UI 1.4.6) only; on 0.9.0 it does not load

SEA POWER 0.9.0: READ THIS BEFORE ANYTHING BELOW
This release was put together for the 0.8.7-261107 beta. The game then
became 0.9.0, and your PC is on it (12 November capture). On 13 November
the pack's data was rebuilt for 0.9.0, on branch
claude/continue-previous-session-39wqwq, which sits on top of
release/r13-combined-20261112. Nothing built for 0.9.0 has been run in the
game: it cannot be run where the pack is built. What that means for you:

- DO NOT RUN Prepare-PC.cmd or Repair-PC.cmd from this toolkit while the
  game is 0.9.0. Prepare-PC imports the release and then stops, at the
  latest inside the beta repair, whose first check is the game file it was
  built for; the data is not installed and the VERIFIED line of step 1 is
  never printed. Repair-PC stops the same way after renaming the beta
  loader's enable.flag (harmless: that loader is inactive on 0.9.0 anyway).
  Upload-PC and Finish-Upload then refuse for want of their receipts.
  Steps 1 and 6 to 9 below therefore wait for a toolkit made for 0.9.0.
- SEST's code is off on 0.9.0. Each SEST plugin checks the game's
  Seapower-Scripts.dll by SHA-256 and none is matched to 0.9.0. In your 12
  November capture BepInEx\LogOutput.log has "Could not find AnchorChain
  chainloader" and "Beta safe loader INACTIVE: uninspected game/preloader
  build", and Player.log has no SEST line. So World Operations and its
  awards, the F11 cost totals and campaign costs, the Red Line runtime
  ribbons and the runtime corrections are off until the code is matched to
  0.9.0. The campaigns and data files do not depend on that code.
- Dynamic Campaign Mod and Coordinated Strike Tool declare game versions
  that end below 0.9.0, so the Mod Manager lists them as not compatible
  and SETUP leaves them alone; Global Maritime Operations 2028 needs
  Dynamic Campaign Mod. Only their authors can change that. Whether either
  runs on 0.9.0 is not on file.

WHAT TO DO ON THE PC NOW (game closed; these install and change nothing)
A. Start Sea Power 0.9.0 once to the main menu and quit, so the logs are
   from a launch after Steam finished the 12 November Workshop downloads
   (Anchor Chain itself updated that day, after your capture's launch).
B. In the repository clone run
     powershell -NoProfile -ExecutionPolicy Bypass -File tools\capture-beta-references.ps1
   It reads the game, BepInEx and the Workshop folders and writes
   SEST-Beta-References-<date>-<6 hex>.zip to Downloads. It refuses only the
   old 0.8.7 release's game file and a running game. That ZIP is what
   matching SEST's code to 0.9.0 starts from: the hash of 0.9.0's
   Seapower-Scripts.dll is in no file SEST has.
C. One look in the Mission Editor (Southern Watch test card, RU.2): Russian
   Navy 21's Admiral Gorshkov should show Russian Federation and the game's
   own Sovremenny the USSR. On the 0.8.7 betas the game ignored every
   Workshop mod's #!extend file while Anchor Chain's preloader was
   installed, unless SEST's Runtime repaired it, and that Runtime does not
   load on 0.9.0. If the Gorshkov shows the USSR, the pack's 243 #!extend
   and #!prepend files (the cost catalogs, Cross-Deck, the combat-system
   and Russian stubs) are not applied on 0.9.0: stop and report that before
   judging anything else. If you can, look once more with
   AnchorChain.Preloader.dll moved out of BepInEx\plugins, which separates
   the two causes.
D. The block under "What the export cannot tell you" in
   docs/packaging-and-recovery.md lists game files 0.9.0 dropped; the export
   cannot show them.

WHAT CAN BE CHECKED ON 0.9.0 WITHOUT SEST'S CODE (step 3 below, in part)
The commander nations, ranks, emblems and name pools; prices and the
same-nation discount; the native awards and their citation dates; the two
hold clocks; Red Line's P1 to P9 and R6's "neither ribbon is granted";
Makran Line's four missions. They use campaign data and the game's own
triggers only. The pack must first be on the PC, which this toolkit cannot
do on 0.9.0 (above), so these wait for the 0.9.0 toolkit too.
New for 0.9.0, to look at in the same pass: the British commander's rank
insignia from Lieutenant up (the game's own images, new in 0.9.0); that
Prepare Airbase opens in one mission with one player airfield and in
Southern Watch 10 Common Sea, which has two (Darwin should be the host);
that a mission of each campaign starts from the campaign map with the
bought task force; and the F10 panel's new commander and awards tab with a
Chinese or Pakistani commander, whose ranks name no image. Two looks the
files ask for (Southern Watch build notes, "Ammunition and unit files"):
after a Harpoon salvo, read the weapon report for launch failures, which
0.9.0 lists; and ready the Rafale M of dispatch D3 The Relief Ship with its
anti-ship fit, to see that the carrier arms the Exocet, which 0.9.0 gave a
supply category no deck in the pack stocks.
What needs SEST's code and so waits for it to be matched to 0.9.0: steps 2,
4 (the brief, the Combat Costs sidebar, the F11 totals, Pop-Out) and 5, the
Red Line checks R1 to R4, and RU.1.

DECISIONS WAITING FOR YOU (docs/campaigns/southern-watch/build-notes.md,
"Sea Power 0.9.0", has each with its figures)
1. CIWS. 0.9.0 rebalanced the game's own guns (Phalanx Block 0 anchor 40 to
   65, Block 1 50 to 70, AK-630 20 to 40; volleys cut, cooldowns raised).
   The eleven mod CIWS SEST retuned on 3 October are still on the old
   ladder, as is every other mod's. Move ours now, or wait for the authors?
2. Sensors. The deprecated E-7A Wedgetail mod carries an old copy of the
   game's whole sensors file and is the winning definition of 220 of the
   game's sensors (the lookout, SPS-49, SPG-62, SQS-53 among them). This is
   older than 0.9.0. Restore the game's sections, as SEST already does for
   weapons? It would change detection in every mission.
3. The Royal Navy mod. 0.9.0's own Hermes, Leanders, Rothesay, Lynx HAS.2,
   Nimrods, Sea Dart and Sea Wolf have the ids of units and rounds mods
   already ship, and the mods' files load. The game's South Atlantic
   campaigns then fly the mods' versions. Keep, or restore the game's?
4. Whether to post a data-only 0.9.0 update before the code is matched. The
   live item (26 October upload) declares 0.8.7 and its LOAD-ORDER names
   three mods their author has since removed from the Workshop.

The rest of this file is the acceptance plan as written for 0.8.7-261107,
corrected where 0.9.0 or the rebuild made a statement untrue.

This is R12 Final (merged as PR #58) together with the commander nations and
national awards (merged as PR #59), the combined release notes (merged as PR
#60) and Red Line's victory paths, the heave-to and progress reports (step 3
of the builder grammar, merged as PR #61), with step 4's two Red Line runtime
ribbons (merged as PR #62), the beta runtime R13 that grants them (on
release/r13-20261111), step 5's Russian Federation registration of the modern
Russian ships and aircraft (on feature/russia-registration-20261111, in
review) and step 5's Makran Line campaign (on feature/makran-line-20261111,
built on the Russian registration), checked once on the PC and posted as one
update. RIBBONS.txt has every award mapping.
R12-RIBBON-EXPANSION.txt describes R12 Final before the commander nations: use
it only for the R12 review findings fixed and the minor ones still open, and
this file and RIBBONS.txt for the award counts, nations and PC steps. The
R12-*.txt notes are records of the R12 builds; where they say R12\, this
toolkit's beta folder is R13\. None of the seven parts has been played on the
owner's PC yet; with R13, step 4's PC checks R1 to R4 on the Red Line test
card now apply as well as R5 and R6.

WHAT IS NEW SINCE THE R12 RIBBON TEST BUILD
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
  0.9.0's own campaigns now write it the same way (ribbon_id,NATION); it has
  not been seen on 0.9.0, which adds a commander and awards tab to the F10
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
  campaign and keyed for the beta runtime R13 (Runtime 1.6.5), which this
  update ships and SETUP installs on game build 0.8.7-261107 only: there it
  grants each at the debrief when its terms are met. The game itself, on
  0.8.7 or 0.9.0, ignores the key, as R12 (Runtime 1.6.4) does; neither
  ribbon is counted in the 75 above.
  Each debrief logs two Player.log lines per runtime ribbon: the first is the
  verdict; the second says "already awarded" or repeats it, as Red Line's
  campaign.ini is its own [File] Base and is read twice. The developer ribbon
  menu offers neither (the Red Line test card's R5 and R6; R1 to R4 need R13,
  which SETUP installs on 0.8.7-261107 only, and RIBBONS.txt says what each
  needs).
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
  the game. The STEAM-*.txt files and the Steam images do not mention it
  yet, because which update ships it is still your decision: the change
  note and page description pasted in steps 7 and 8 describe four
  campaigns.
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
- SETUP: the beta feature step runs only on game build 0.8.7-261107. On any
  other build, 0.9.0 included, it restores the normal Workshop plugins and
  continues, and problems
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
  upload; 243 #!extend and #!prepend files; 1,633 recruitment entries in
  the world campaign). Found by reading the update against the pack, and
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
  you: the four decisions listed at the top.

PREPARE AND CHECK
1. Close Sea Power. Keep SEST and the collection subscribed. Extract this
   COMPLETE toolkit into a NEW folder and run Prepare-PC.cmd. Keep the
   printed release checkout, the backup path and the line "VERIFIED: all
   4592 canonical upload files match the release manifest." Upload-PC.cmd
   prints the folder to upload (step 6). (On 0.9.0 this step does not
   complete: see the top of this file.)
   Prepare-PC installs both code and campaign/loadout data; Repair-PC alone
   only repairs code. The author-update guard and original restore journal
   remain in place. Steam branch, subscriptions and saves are unchanged.
2. Load an existing world. Press F11 and select Service. Check the
   existing awards/progress, the longer ribbon list, scrolling and
   citations. Complete an accepted Admiralty order and return to the map.
   The task count should rise once; the battle count and combat USD totals
   must not. If you can, complete a multi-phase operation as well: it should
   add one task. With R13 a task counts even if you close its paper at once.
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
   with MissionAwards=0 neither is granted) and, with R13, R1 to R4: win
   RL05 without launching anything and RLC1 with its pilot recovered, and
   judge each ribbon by the first of its two Player.log lines
   (RIBBONS.txt explains both). Russian Federation (step 5): in the new
   Southern Watch campaign's Situation window the Project 20380 corvette
   shows the Russian Federation flag and the Akula the USSR's; in the
   Mission Editor Russian Navy 21's Admiral Gorshkov and a Su-35S show
   Russian Federation and the game's own Sovremenny and a Cold War Su-27
   the USSR, and the Kuznetsov's 2016 fit shows Russian Federation and her
   1991 fit the USSR; a mission saved with the Kuznetsov's 2016 fit and the
   Akula Gepard holds VariantReference=Variant2 and Variant13 (RU.8);
   Pacific Strike's 02 Action in the Taiwan Strait still generates its
   Soviet force (the release checkout's
   docs/campaigns/southern-watch/test-card.md, 6K, rows RU.1 to RU.8). On
   0.8.7-261107 the stubs, like every #!extend file in the pack, apply only
   where SEST's beta Runtime repairs the game's modifier scan
   (ModifierRegistry, not turned off), so not with the beta features off
   (step 5): first read Player.log's "[SEST Runtime] modifier files" line,
   which should count 243 files from this pack (RU.1). On 0.9.0 that
   Runtime does not load and no such line is written; whether 0.9.0 applies
   the stubs unaided is what RU.2 shows (check C at the top). Makran Line:
   start
   a new campaign; the Service Record offers Pakistan only, as a Commodore,
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
4. Recheck the opening brief, world Combat Costs sidebar and direct F11
   totals. In Starting Airborne Flights select the RAAF E/A-18G and confirm
   HARM (AGM-88C), AARGM (AGM-88E) and AARGM-ER (AGM-88G) choices. The three
   loadouts were data-tested; the selector still awaits an owner PC check.
   With Pop-Out 1.2.0 installed, check that its windows open.
5. Quit. Run "SEST beta features - turn off.cmd", start the game once and
   confirm it starts with the beta features off. On 0.8.7-261107, Workshop code
   mods load only through SEST's beta loader, so SEST's plugins, Dynamic
   Campaign Mod and the other code mods should not load then; data mods and
   the Task Force campaigns should. Quit and run
   "SEST beta features - turn on.cmd". Then run R13\Capture-Repair-Results.cmd
   and keep the capture. The automated checks passed; they do not establish
   native Noesis rendering or gameplay.

POST AFTER THE PC CHECKS
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

RETAINED FEATURES
- Global Maritime Operations 2028, the one world in the campaign menu since
  R11: 196 bases, 293 force groups, 54 patrols and 1,633 recruitment entries;
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
  the five reviewed files for the supported beta.

The owner accepted the four briefing/costs/page changes on 9 November.
None of the seven parts has been played on that PC yet. R12 Final, the
commander nations and Red Line steps 3 and 4 are merged on dev (PRs #58 to
#65, with the Steam images for R12 and the world campaign). This release
combines three branches on release/r13-combined-20261112: step 5's Russian
Federation registration (feature/russia-registration-20261111, in review),
step 5's Makran Line (feature/makran-line-20261111), which builds on it, and
R13 (release/r13-20261111: dev at a0721c18 with the R13 runtime merged as
00bca642 and packaged). None of the three is on dev or beta yet. The 0.9.0
rebuild of 13 November is on claude/continue-previous-session-39wqwq, on top
of the combined branch, and is on neither.
This toolkit's branch, beta, is the branch the PC installs, tests and posts
from (docs/BRANCHES.md) and the one its SOURCE-RECEIPT.json names: once this
release is merged into dev and dev into beta, beta carries dev, and the
toolkit is built from it. Nothing has been uploaded to Steam.
