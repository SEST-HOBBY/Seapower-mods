SEST R12 FINAL - NATIONAL AWARDS, WORLD FIXES AND SETUP OPT-OUT
10 November 2026 | SEST-DEV
Beta 0.8.7-261107: Runtime 1.6.4 / UI 1.4.14
Standard 0.8.7-261021: Runtime 1.5.0 / UI 1.4.6 (unchanged)

This finalises the R12 posting and ribbon revisions after review.
R12-RIBBON-EXPANSION.txt lists the review findings fixed here and the minor
ones still open. It has not been played on the owner's PC yet.

WHAT IS NEW SINCE THE R12 RIBBON TEST BUILD
- Commander nations: Southern Watch and Southern Reach offer Australia (the
  default), US, UK and Japan. Red Line stays Chinese, Sulu Line Philippine.
  The same-nation discount is the game's own rule: an Australian commander
  keeps it on the Australian classes; a US, British or Japanese commander
  gets it on that nation's classes.
- Awards: 51 in all. 25 fictional world awards (beta), 12 fictional native
  campaign ribbons, and 14 real-award representations matched to the
  commander's rank: Australia 4, US 4, UK 2, Japan 1, Philippines 3. The task
  group receives the host nation's unit award. Every citation carries its
  mission date and two plain sentences. The US Achievement Medal and the two
  US unit commendations from the test build are no longer granted; a record
  already earned with it still shows. RIBBONS.txt has every mapping.
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
- Only the new world, Global Maritime Operations 2028, is in the campaign
  menu. The original World Sandbox stays under legacy_campaigns/ for
  tools\select-legacy-world.ps1 (see WORLD-CAMPAIGN-READ-ME.txt).

PREPARE AND CHECK
1. Close Sea Power. Keep SEST and the collection subscribed. Extract this
   COMPLETE toolkit into a NEW folder and run Prepare-PC.cmd. Keep the
   printed release checkout, backup path and verified UPLOAD FOLDER.
   Prepare-PC installs both code and campaign/loadout data; Repair-PC alone
   only repairs code. The author-update guard and original restore journal
   remain in place. Steam branch, subscriptions and saves are unchanged.
2. Load an existing world. Open the report and select Service. Check the
   existing awards/progress, the longer ribbon list, scrolling and
   citations. Complete an accepted Admiralty order and return to the map.
   The task count should rise once; the battle count and combat USD totals
   must not. If you can, complete a multi-phase operation as well: it should
   add one task. A world started on 1.6.2 or 1.6.3 keeps SEST's text as its
   saved SITREP 001; a new world shows DCM's report with the SEST brief first.
3. Start a new Southern Watch or Southern Reach campaign. The Service Record
   offers Australia, Japan, United Kingdom and USA; Australia is the default.
   Compare one Anzac and one Burke price as an Australian and as a US
   commander. Check the British commander's empty rank insignia and the
   White Ensign emblem. After a qualifying result, confirm the native
   Service Record shows the right awards and that a citation's date is the
   mission's, not 1985. A failed mission must not grant the mission award.
   Reopen the campaign to check persistence.
4. Recheck the opening brief, world Combat Costs sidebar and direct F11
   totals. In Starting Airborne Flights select the RAAF E/A-18G and confirm
   HARM (AGM-88C), AARGM (AGM-88E) and AARGM-ER (AGM-88G) choices. The three
   loadouts were data-tested; the selector still awaits an owner PC check.
   With Pop-Out 1.2.0 installed, check that its windows open.
5. Quit. Run "SEST beta features - turn off.cmd", start the game once and
   confirm SEST loads without the beta features; quit and run
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
- Global Maritime Operations 2028: 196 bases, 293 force groups, 54 patrols
  and 1,586 recruitment entries; 40 added airfields and 37 reviewed positions.
- Eight coalition command stages, varied native Admiralty rewards and
  recruitment progression; no new base-construction mechanic is claimed.
- Paused battle preparation, clear native end-battle/debrief flow, readable
  opening brief, world-map Combat Costs and direct cumulative F11 USD totals.
- Three conventional Growler starting-flight fits, coordinated strike
  presentation, current Topography/Pop-Out support and Identify preservation.
- Reviewed beta features inside the normal Workshop SETUP flow, upgrade
  recovery and rollback over the 1.6.2 and 1.6.3 test builds. Normal active
  release plugins stay in the upload; the installer selects the five
  reviewed files for the supported beta.

The owner accepted the four briefing/costs/page changes on 9 November.
This final revision has not been played on that PC yet. It is on GitHub
branch fix/r12-finalise-20261110 for review; nothing has been uploaded to
Steam.
