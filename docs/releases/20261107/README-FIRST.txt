MODERN NAVAL OPERATIONS — OWNER’S PC WALKTHROUGH
R15 • 22 November 2026 • based on the 11:29 Brisbane capture
Game target: Sea Power 0.9.3 Build 261116 public beta. Dynamic Campaign Mod 1.0.1.

1. PREPARE YOUR PC
Let Steam Downloads finish for Sea Power and close the game. Use the single MNO-GSCO-R15-PC-and-Workshop.zip for this pass. Extract the whole ZIP into a fresh folder in Downloads. If you already tried the 11:29 toolkit and saw “Wrong Workshop release manifest” or “This is not the reviewed SEST release manifest”, continue from this new folder. It can repair the earlier R15 in place. Your installed weather and polar test campaigns stay in the user folder.

If you have a working DCM 1.0.x world, note its side, campaign date and F11 Service progress and make a copy before loading it under the new name. A screenshot works for the comparison. The renamed world retains its existing ID and folder. Back up any older Task Force save you intend to try on 0.9.3.

2. INSTALL AND CHECK THE SUBSCRIBED ITEM
a. Double-click Prepare-PC.cmd in the new folder. An enabled R15 can finish in one run. If it asks for a menu probe, start Sea Power, wait ten seconds at the main menu, quit completely and run the same command again. Look for “VERIFIED: all 4622 canonical upload files match the release manifest.” If it stops on another author change or DLL mismatch, keep the report or error it names. Run the normal update capture before installing that changed build.
b. With the game closed, open the subscribed item and run SETUP - double-click me.cmd. For the default library, press Win+R and paste the path below. For another Steam library, choose the pack in Mod Manager and use Open Folder, then quit before SETUP.
   C:\Program Files (x86)\Steam\steamapps\workshop\content\1286220\3812461539
c. Look for “All done”. If SETUP lists [!!] warnings, save their wording. Reopen Mod Manager. The subscribed pack should be first. The expected list is this pack and 209 dependencies. If the old local SEST_090_PC_TEST appears, keep it disabled and the subscribed entry enabled.

3. RUN ONE PLAYTEST ON THE RENAMED BUILD
a. In a scenario, toggle Topography on and off. Pop Contacts or F11 into a separate window and bring it back. Check Identify Expanded appears once and retains your settings and audio. In the editor, inspect the Be-12 and Be-12N markings. Try an aircraft from the new Chinese UAV collection and an AEP aircraft’s HUD.
b. In Campaigns, open “SEST Test: Hormuz Weather Split”. Turn on the weather layer and find Cyclone DARYA. Check one contact near the storm, then save and reload to check its position. Open “SEST Test: Polar North (Barents)” or “SEST Test: Polar South (Antarctic Peninsula)” and check the ice edge and readout.

4. VERIFY THE RENAME AND SAVE
a. In Mod Manager the single subscribed entry at the top should read “Modern Naval Operations”. In Campaigns the world should read “Global Strategic Command Operations (GSCO)”. Start a fresh world and open the initial brief. Check the title is legible, choose a side and check the shipyard and F11 World Operations.
b. Use a copy of a world save made in Dynamic Campaign Mod 1.0.x. Open the copy and use the notes from step 1 if available. Compare the forces, date and F11 Service ribbons. A separate new world should start its own service record. DCM 0.25 and earlier worlds require a new game under DCM 1.0.1. Preserve a backup before opening a 0.9.2 Task Force save on 0.9.3.
c. In GSCO, open F11 Overview, Forces, Combat Costs and Service. Check a recorded engagement’s expenditure against its entry after returning to the map. Open one of the five authored Task Force campaigns as well. Check its own Service Record and debrief. Campaign-start preparation, a scenario’s deployment clearance and mission replay are separate checks in the screens where they appear.
d. For Red Line ribbon follow-up, checks R5 and R6 cover the debrief awards. R1 to R4 need R15 for the full playtest. The mission-by-mission card is docs/campaigns/red-line/test-card.md in the release checkout.
e. Quit. Run R15\Capture-Repair-Results.cmd from the renamed toolkit. Keep the SEST-Beta-References ZIP it names in Downloads and note each result as pass, fail or untested. If either the world title, save, costs or a feature check fails, keep the error, screenshot and log with the name of the campaign. Report each pass separately so an untested system stays visible.

5. PREPARE THE STEAM UPDATE
Open STEAM-POSTING-RUNBOOK.txt. It identifies the existing Steam item and collection, the release audience, the ten missing collection links and the files to paste. The 11:29 capture and this renamed candidate both target the public beta executable. The default Steam release still needs its own reference capture and acceptance before a general-release upload.

This toolkit's branch, feature/mno-gsco-r15, is in the included Git bundle. The source receipt identifies the exact revision. If Git specifically reports a missing prerequisite and your previous PC checkout is available, open PowerShell and run:
  git -C "$env:USERPROFILE\Seapower-mods" fetch origin f2da3f0faad13cb9fdfb3ffd2ef1c27a17b183b6
Then run Prepare-PC.cmd again.
