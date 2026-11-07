SEST WORKSHOP UPDATE CANDIDATE — 7 NOVEMBER 2026, R7 TOOLKIT

This replaces the earlier 7 November toolkit and R6 repair for the new
0.8.7-261106 beta captured on your PC. Your Steam branch stays on beta.
The Workshop upload retains stable Runtime 1.5.0 with UI Follow-up 1.4.6;
the separate R7 playtest uses Runtime 1.5.4 and UI Follow-up 1.4.7.
Automated build/managed/installer checks are recorded. Gameplay is pending.

PREPARE YOUR PC

1. Close Sea Power. Extract the complete new toolkit into a fresh folder.
2. Run Prepare-PC.cmd, or open PowerShell in the extracted toolkit and run:

   powershell -NoProfile -ExecutionPolicy Bypass -File .\Prepare-PC.ps1

The helper uses your existing C:\Users\rolyl\Seapower-mods clone. It verifies
and imports the bundle into a NEW detached worktree beside that clone; it
does not switch your current branch or overwrite either existing worktree.
It checks current author configuration fingerprints, upgrades the existing
beta candidate to R7, and installs the refreshed SEST data while retaining
all five verified R7 code files. Previous data is kept under
steamapps\SEST-release-backups; its exact backup/restore command is printed.
Original beta code backups and Identify data remain in place.

Finally it prepares a fresh Downloads upload folder from the canonical
stable repository payload. That folder cannot inherit the installed beta
DLLs. No PC rebuild and no automatic Steam submission are performed.
If any step stops, keep its error/report; do not substitute older DLLs.
-ImportOnly imports the new worktree without running install steps.

WHAT IS IN THIS REFRESH

- All 14 changed author configuration exports from today's capture, plus
  the retained November campaign, SETUP, pricing and dependency corrections.
- Retires SEST's Harpoon/Mikuma repairs where the author fixed or removed
  the conflicting source data, preserves the reviewed price for the retired Chilean saved-campaign id,
  and updates the Sulu Line dependency accounting for the new PN Lynx choice.
- Follows thin squadron aliases when deciding a roster pick's nation,
  including the updated German NH-90 file.
- Stable UI 1.4.6 bridges the captured Pop-Out Windows 1.1.3 and Combat Cost
  Tracker 0.8.0 interfaces without changing Runtime 1.5.0.
- R7 targets the captured new game/Noesis DLLs, debrief nation argument,
  tracker visibility, campaign/terrain APIs, formation label lookup and
  Osprey fuel conversion. Current author beta releases replace six old
  adapters. The captured stable-only Loadout Manager duplicate is skipped.

R7 LIMITATIONS AND PLAYTEST

EnhancedDecoyMod, both Topographic Map DLLs and MultiStageMissiles are held
before CLR load because native interfaces changed. Their data is retained;
native countermeasures and missile staging remain. ExtendedGuidance stays
disabled by the SEST profile. See R7\BETA-FEATURE-PARITY.md for details.
Clipped tabs and the Global Hawk comparison are not claimed fixed.

Launch beta. Check startup; F11 current, previous and campaign totals and
Redback prices; mission debrief and continuation into a second mission;
preparation; Contacts and formation pop-out/return; compass on unit video;
SAR routing; and Osprey launch, conversion and fuel use. Quit and run
R7\Capture-Repair-Results.cmd. Keep the original backups until the test is
reviewed. Restore data before restoring earlier beta code if reverting both.

The beta test does not verify stable UI 1.4.6 rendering. Before releasing
that new stable bridge, a stable Build 261021 tester must check F11,
Contacts/formation pop-out and compass with these author versions. You do
not need to switch your own PC off beta. No gameplay result is fabricated.

STEAM UPLOAD AFTER CHECKS PASS

Update existing Workshop item 3812461539; do not create a new item.
Use ONLY the inner SEST_Integration folder printed by the preparation
script. Do not select the toolkit, repository root or installed beta item.
Paste STEAM-CHANGE-NOTE.txt after the gameplay checks pass.

Confirm Required Items and collection contain all 203 dependencies from
data/load-order.tokens.txt; check these four explicitly:
  Contact Log       3819427362
  Topographic Map   3826122523
  Pop-Out Windows   3826396311
  B-21 Raider       3821992229

Item: https://steamcommunity.com/sharedfiles/filedetails/?id=3812461539
Collection: https://steamcommunity.com/sharedfiles/filedetails/?id=3812390790

In Sea Power: Mod Manager > Create Mod > Update Existing > 3812461539 >
Pick Folder > the verified SEST_Integration folder > Submit. Confirm the
successful Steam result in Player.log, then verify the public timestamp,
size and dependencies. Steam publication has not been performed here.
