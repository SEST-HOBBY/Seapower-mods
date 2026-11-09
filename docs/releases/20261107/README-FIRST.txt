SEST R12 — FULL WORKSHOP FEATURE UPDATE
9 November 2026 | SEST-DEV

R12 WORLD-BATTLE FLOW REFINEMENT - UI 1.4.10
The 19:10 capture confirms the previous R12 payload is installed. This update
adds a paused battle-preparation checklist and a clearer End battle... entry
in the world-battle pause menu. Its confirmation explains that victory is not
required while retaining the campaign's complete consequence warning.

EXISTING R12 INSTALLATION: close Sea Power, extract this complete toolkit to
a new folder and run Repair-PC.cmd. This applies the inspected UI update.
Test a new paused battle, preparation, a replay and ending an unfinished
battle through Esc > End battle... > debrief > return to campaign. Quit and
run R12\Capture-Repair-Results.cmd. See R12-BATTLE-FLOW.txt for details.

Only the UI DLL changes from the previous R12 payload. Runtime, loader,
bootstrap and Identify shim retain their existing hashes. The reviewed
BetterTacMap/Pop-Out configuration baseline is retained. For a complete
publisher preparation and verified upload folder, use Prepare-PC.cmd below.

THIS STEAM UPDATE INCLUDES THE NEW UI FEATURES
The verified SEST_Integration upload now includes the Modernised Worldwide
Campaign, native ribbons and the installer for F11 World Operations, world
service progress, campaign costing and Coordinated Strike UI refinements.
Use this R12 package rather than the earlier R11 data-only upload folder.

PUBLISHER PC
1. Close Sea Power. Extract this complete toolkit to a new folder.
2. Run Prepare-PC.cmd. Keep its printed checkout, backup and UPLOAD FOLDER.
3. Check the new world, F11 tabs, service progress, strike controls, Topography,
   pop-outs, battle return and save/load. Quit and capture diagnostics.
4. Upload only the verified SEST_Integration folder to existing item 3812461539.
   If the picker requires StreamingAssets, use Upload-PC.cmd to create a
   fresh top-level publishing copy and copy the change note to the clipboard.
   Keep that temporary local copy disabled. After upload, quit the game and
   run Finish-Upload.cmd to move it out before using subscriber SETUP.
5. Confirm upload success, non-zero item size, change note and Required Items.

Preparation checks author configuration updates, repairs the existing beta
installation and installs backed-up data. It does not submit anything to
Steam, switch Steam branches or overwrite native game DLLs or save files.
If preparation stops, retain the error and report. Do not skip its checks.

SUBSCRIBER INSTALLATION
After Steam finishes downloading this item, close Sea Power and run
SETUP - double-click me.cmd from Mod Manager > Open Folder on the pack.
On the supported beta build:
- Existing enabled SEST beta installation: one SETUP run updates features.
- Fresh installation: SETUP stages features. Launch to the main menu, wait
  about ten seconds, quit, then run SETUP again to enable them.
- After a Steam item update, rerun SETUP to reapply the bundled features.
Original restore backups, Identify data, settings and saves are retained.
Unknown game/author DLL versions or unreviewed installed code are refused.
On other builds, SETUP leaves the normal-release active plugins selected.
The new feature code is present in the Workshop download, not a separate
external download. Installation still depends on the supported game build.

FEATURES
- One Modernised Worldwide Campaign combines the original and regional
  expansion: 156 bases, 293 forces, 54 patrols and 1,586 catalogue entries.
- Four native campaign completion ribbons with artwork and citations.
- F11 World Operations: Overview, Forces, Costs and Service.
- Independent profile service progress; native campaign saves are unchanged.
- Coordinated Strike shared styling and planned/remaining weapon estimates.
  Original scheduling and launch controls are retained.
- Reviewed beta Topography, Pop-Out and DCM salvo-hold support.

PC ACCEPTANCE
Check a new world and an existing regional save, complete a battle and return,
then save/load and confirm no duplicate service awards or battle cost totals.
Check native Service Record artwork/citations, F11 movement/scroll/pop-out,
strike planning and launch controls, Identify, Contacts and Group Manager.
Credits remain separate from estimated USD values. A full strike-window layout
redesign is follow-on work; this update delivers styling and cost summaries.
Quit and run R12\Capture-Repair-Results.cmd, then send the new capture.
Managed checks do not replace native rendering and gameplay acceptance.
No Steam submission or GitHub push has been performed by this toolkit.
