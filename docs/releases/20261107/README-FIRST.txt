SEST R12 FINAL + COMMANDER NATIONS + RED LINE 3-4 + RUSSIA - PC ACCEPTANCE
11 November 2026 | SEST-DEV
Beta 0.8.7-261107: Runtime 1.6.4 / UI 1.4.14
Standard 0.8.7-261021: Runtime 1.5.0 / UI 1.4.6 (unchanged)

This is R12 Final (merged as PR #58) together with the commander nations and
national awards (merged as PR #59), the combined release notes (merged as PR
#60) and Red Line's victory paths, the heave-to and progress reports (step 3
of the builder grammar, merged as PR #61), with step 4's two Red Line runtime
ribbons prepared and inert until R13 (merged as PR #62) and step 5's Russian
Federation registration of the modern Russian ships and aircraft (on
feature/russia-registration-20261111, in review), checked once on the PC and
posted as one update. RIBBONS.txt has every award mapping.
R12-RIBBON-EXPANSION.txt describes R12 Final before the commander nations: use
it only for the R12 review findings fixed and the minor ones still open, and
this file and RIBBONS.txt for the award counts, nations and PC steps. None of
the five parts has been played on the owner's PC yet; step 4 has nothing to
play before R13 except the Red Line test card's checks R5 and R6.

WHAT IS NEW SINCE THE R12 RIBBON TEST BUILD
- Commander nations: Southern Watch and Southern Reach offer Australia (the
  default), US, UK, Japan, New Zealand, France, Canada, South Korea, Spain,
  Italy, Germany, the Netherlands, Norway and Denmark. Sulu Line offers the
  Philippines (default), Thailand and Australia. Red Line stays Chinese.
  Each nation has its navy's officer ranks, a navy name and an emblem; New
  Zealand, South Korea, the Netherlands, Denmark and Thailand use SEST name
  pools. The same-nation discount is the game's own rule and follows the
  commander's nation; each campaign's rules page gives the count. New
  Zealand's one class is the RNZAF P-8A, sold with the allied fleet; no
  class is Canadian.
- Awards: 72 definitions. 25 fictional world awards (beta), 12 fictional
  native campaign ribbons, and 32 real-award representations for 12 nations:
  30 personal and service awards matched to the commander's starting rank and
  2 host-nation unit awards to the task group (plus 3 retired US definitions
  kept so an earlier record still shows). In Southern Watch and Southern
  Reach, commanders of every offered nation except Italy, the Netherlands and
  Norway earn their own nation's awards; Sulu Line's Philippine awards go to a
  Philippine commander. The task group receives the host nation's unit award.
  Every native campaign citation carries its granting mission's date and two
  plain sentences; the world awards' citations state their criteria and are
  undated. The nation filter on the native awards is read from the beta's
  code; on standard 0.8.7-261021 it has not been checked. The Korean strips
  carry the taegeuk and the German Cross of Honour its gold cross.
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
- Red Line runtime ribbons, prepared for R13 (step 4, campaign side,
  merged as PR #62): RL05 Silent
  Passage and RLC1 Personnel Recovery are defined in the Red Line campaign
  and keyed for the beta runtime R13 (Runtime 1.6.5). This update ships
  Runtime 1.6.4, which ignores the key as the game and the standard build
  do, so neither ribbon is granted and neither is counted in the 72 above.
  Until R13 is installed the checks are that neither appears and that the
  developer ribbon menu offers neither (the Red Line test card's R5 and R6;
  R1 to R4 need R13, and RIBBONS.txt says what each ribbon needs).
- Russian Federation (step 5, on feature/russia-registration-20261111, in
  review): SEST Collection Fixes registers to the game's Russia nation,
  which it names Russian Federation, instead of the USSR: 16 post-1991,
  Russian-built ship and submarine classes (the Gorshkov and Grigorovich
  frigates, the Steregushchiy, Gremyashchiy and Buyan-M corvettes, the
  Yasen, Belgorod, Borei and Improved Kilo boats); the modern refits of
  Soviet-built ships in their modern fit only (the Kuznetsov's 2016 fit,
  not her 1991 one, Admiral Nakhimov's refit, Marshal Ustinov 2016, the
  Nanuchka IIIs of 2019, the Tarantul R-60 of 2005) and the Akulas, Oscar
  IIs, Grishas and Admiral Chabanenko completed after 1991;
  and 32 aircraft of post-1991 Russian types and upgrades (the Su-57,
  Su-35S, Su-30SM, Su-33, MiG-31BM, MiG-35, MiG-29K 9.41, A-50U, Tu-214R
  and their like). One #!extend stub per unit sets only the Nation of its
  mod's variants or squadrons file; no author's file is copied. SEST's
  Akademik Pashin registers Russia in its own file. The Soviet-era fits,
  Cold War aircraft (the Su-27, MiG-31, MiG-29 9.12, Tu-160 as built,
  Tu-95MS, Il-76MD, Il-78, Ka-27PL, Mi-8, Mi-24), fictional variants and
  hulls never built stay Soviet, as stock Cold War missions use them. The
  SEST missions fly the Russian flag on the same units as before. No mod
  has used an #!extend on a variants or squadrons file before, so it is
  checked once in step 3; no campaign offers a Russian commander, so the
  discount is not.
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
- SETUP: the beta feature step runs only on the supported beta. On any other
  build it restores the normal Workshop plugins and continues, and problems
  are warnings, not errors. Three launchers sit beside SETUP:
  "SEST beta features - turn off.cmd", "- turn on.cmd" and "- remove.cmd".
  Turning off writes %LOCALAPPDATA%\SEST\BetaCompatibility\features-off.json,
  which SETUP respects. The publishing copy now uses a short folder,
  StreamingAssets\SEST_UP_<8 hex>.

PREPARE AND CHECK
1. Close Sea Power. Keep SEST and the collection subscribed. Extract this
   COMPLETE toolkit into a NEW folder and run Prepare-PC.cmd. Keep the
   printed release checkout, the backup path and the line "VERIFIED: all
   4473 canonical upload files match the release manifest." Upload-PC.cmd
   prints the folder to upload (step 6).
   Prepare-PC installs both code and campaign/loadout data; Repair-PC alone
   only repairs code. The author-update guard and original restore journal
   remain in place. Steam branch, subscriptions and saves are unchanged.
2. Load an existing world. Press F11 and select Service. Check the
   existing awards/progress, the longer ribbon list, scrolling and
   citations. Complete an accepted Admiralty order and return to the map.
   The task count should rise once; the battle count and combat USD totals
   must not. If you can, complete a multi-phase operation as well: it should
   add one task. A world started on 1.6.2 or 1.6.3 keeps SEST's text as its
   saved SITREP 001; a new world shows DCM's report with the SEST brief first.
3. Start a new Southern Watch or Southern Reach campaign. The Service Record
   offers the fourteen nations; Australia is the default. Compare one Anzac
   and one Burke price as an Australian and as a US commander. Check the
   British commander's empty rank insignia and the White Ensign emblem. Pick
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
   the same card (the developer ribbon menu offers neither runtime ribbon,
   and neither is granted on this build). Russian Federation (step 5): in
   the new Southern Watch campaign's Situation window the Project 20380
   corvette shows the Russian Federation flag and the Akula the USSR's; in
   the Mission Editor Russian Navy 21's Admiral Gorshkov and a Su-35S show
   Russian Federation and the game's own Sovremenny and a Cold War Su-27
   the USSR, and the Kuznetsov's 2016 fit shows Russian Federation and her
   1991 fit the USSR; Pacific Strike's 02 Action in the Taiwan Strait still
   generates its Soviet force (the release checkout's
   docs/campaigns/southern-watch/test-card.md, 6K, rows RU.1 to RU.8). On
   the beta the stubs, like every #!extend file in the pack, apply only
   where SEST's beta Runtime repairs the game's modifier scan
   (ModifierRegistry, not turned off), so not with the beta features off
   (step 5): first read Player.log's "[SEST Runtime] modifier files" line,
   which should count 232 files from this pack (RU.1). If time allows, as a
   New Zealand commander buy the P-8A in the force allocation before Weapons
   Free (SW05) at the discounted price and fly it in the Maritime Patrol slot
   of 06 Blind Horizon (Weapons Free has no patrol slot).
4. Recheck the opening brief, world Combat Costs sidebar and direct F11
   totals. In Starting Airborne Flights select the RAAF E/A-18G and confirm
   HARM (AGM-88C), AARGM (AGM-88E) and AARGM-ER (AGM-88G) choices. The three
   loadouts were data-tested; the selector still awaits an owner PC check.
   With Pop-Out 1.2.0 installed, check that its windows open.
5. Quit. Run "SEST beta features - turn off.cmd", start the game once and
   confirm it starts with the beta features off. On the beta, Workshop code
   mods load only through SEST's beta loader, so SEST's plugins, Dynamic
   Campaign Mod and the other code mods should not load then; data mods and
   the Task Force campaigns should. Quit and run
   "SEST beta features - turn on.cmd". Then run R12\Capture-Repair-Results.cmd
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
  R11: 196 bases, 293 force groups, 54 patrols and 1,586 recruitment entries;
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
  Tasman Crossing; Red Line from the start and Sulu Line from Service at Sea.
- Reviewed beta features inside the normal Workshop SETUP flow, upgrade
  recovery and rollback over the 1.6.2 and 1.6.3 test builds. Normal active
  release plugins stay in the upload; the installer selects the five
  reviewed files for the supported beta.

The owner accepted the four briefing/costs/page changes on 9 November.
None of the five parts has been played on that PC yet. PRs #58 to #65 are
merged on dev, with the Steam images for R12 and the world campaign; step 5's
Russian Federation registration is on feature/russia-registration-20261111, in
review. This toolkit's branch, beta, is the branch the PC installs, tests and
posts from (docs/BRANCHES.md); it carries what dev holds when the toolkit is
built.
Nothing has been uploaded to Steam.
