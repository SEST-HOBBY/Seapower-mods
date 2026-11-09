SEST R12 - FINAL POSTING PACKAGE
9 November 2026 | SEST-DEV
Runtime 1.6.2 / UI 1.4.12

CONFIRMED ON THE PC
The opening briefing's headings and wrapped text, world-map Combat Costs
button, direct F11 cumulative USD costs and revised Steam description were
confirmed working by the owner. This follow-up retains that exact code.

FINAL GROWLER CORRECTION
The starting-flight selector previously allowed only SEST_SEAD120D for the
RAAF Growler. Southern Watch and Southern Reach now offer three conventional
choices: HARM (AGM-88C), AARGM (AGM-88E) and AARGM-ER (AGM-88G). Each carries
two anti-radiation missiles, two AIM-120Ds, NGJ pods and both wing tanks.
The first two are also available on the modern US Navy Growler. Existing
loadout IDs, aircraft defaults and campaign saves have not been rewritten.

PREPARE AND POST
1. Close Sea Power. Keep SEST and the collection subscribed. Extract this
   COMPLETE toolkit into a NEW folder and run Prepare-PC.cmd. Keep the
   printed release checkout, backup path and verified UPLOAD FOLDER.
   Use Prepare-PC, since Repair-PC alone only installs code, not loadout data.
2. Open Starting Airborne Flights in Southern Watch or Southern Reach.
   Select the RAAF E/A-18G and check the three loadouts above. The briefing
   and world costs do not need their acceptance tests repeated for this
   data-only follow-up. Quit the game after the check.
3. Run Upload-PC.cmd. It creates a verified publishing copy under
   StreamingAssets and puts STEAM-CHANGE-NOTE.txt on the clipboard. Keep
   this temporary local mod disabled.
4. Open Sea Power > Mod Manager > Create Mod > Update Existing. Select
   Workshop item 3812461539 and the EXACT folder printed by Upload-PC.cmd.
   Paste the change note and submit. Confirm success and a non-zero size.
5. Update the page description with STEAM-PAGE-DESCRIPTION.txt (Steam BBCode).
   STEAM-SHORT-DESCRIPTION.txt and STEAM-COLLECTION-DESCRIPTION.txt contain
   the separate short and collection copy if needed.
6. Quit and run Finish-Upload.cmd to move the temporary publishing copy out
   of the game. After Steam downloads the update, open the subscribed pack
   folder and run SETUP - double-click me.cmd with the game closed.

RETAINED FEATURES
- Global Maritime Operations 2028: 196 bases, 293 force groups, 54 patrols
  and 1,586 recruitment entries; 40 added airfields and 37 reviewed positions.
- Eight coalition command stages at 0 / 300 / 800 / 1,600 / 2,800 / 4,500 /
  7,000 / 10,500 renown, with progressive recruitment access.
- Native Admiralty assignments and battle outcomes reward command progress.
  Fuel and ammunition use depots, convoys, airlifts and replenishment ships.
- Paused world-battle preparation and Esc > End battle... return through the
  debrief without requiring victory; campaign consequences still apply.
- F11 Overview, Forces, Combat Costs and Service; campaign completion ribbons;
  independent world service records; Coordinated Strike styling and estimates;
  Topography, Pop-Out support and DCM salvo hold.

Existing worlds can use the tested UI fixes. A world created before the
196-base expansion needs a new campaign for that full layout and progression.
The expanded network is scenario data; building bases during play is not
included. Coalition access, deployments and stocks are hypothetical 2028
assumptions. Campaign credits and estimated USD costs are separate.

The reviewed Steelfin baseline is retained. Preparation checks author
configuration updates and makes backed-up code/data changes. It does not
submit to Steam, switch Steam branches, edit native game DLLs or write saves.
If an upstream check stops, keep its error/report for review.

SUBSCRIBER INSTALLATION
Subscribe to this pack and all collection items. In Mod Manager, open this
pack's folder, close Sea Power and run SETUP - double-click me.cmd. On the
supported beta, an enabled installation updates in one run. A fresh install
needs SETUP, a main-menu launch for about ten seconds, quitting and a second
SETUP run. Rerun SETUP after Steam refreshes this item. Keep SEST at the top.
Original backups, settings, Identify data and saves are retained.

To collect a later issue, quit and run R12\Capture-Repair-Results.cmd.
Validation details are in VALIDATION.json and R12-POSTING-REVIEW.txt.
