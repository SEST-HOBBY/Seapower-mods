SEST WORKSHOP UPDATE CANDIDATE — 8 NOVEMBER 2026, R8 TOOLKIT

This replaces the R7 toolkit. Your 8 November FULL capture contains a newer
game assembly (499675cd...), although the plugin DLL hashes are unchanged.
R8 targets that exact captured assembly. Your Steam branch stays on beta.
Canonical Workshop code remains stable Runtime 1.5.0 and UI 1.4.6; the
separate R8 playtest uses Runtime 1.5.5 and UI 1.4.8.

PREPARE YOUR PC

Close Sea Power. Extract the complete NEW toolkit into a fresh folder and
run Prepare-PC.cmd. Alternatively, open PowerShell in that folder and run:

  powershell -NoProfile -ExecutionPolicy Bypass -File .\Prepare-PC.ps1

The helper imports the reviewed bundle into a new detached worktree beside
C:\Users\rolyl\Seapower-mods. Existing worktrees and branches are retained.
It checks author configurations, upgrades the existing candidate to R8,
backs up and refreshes SEST data while preserving the verified beta code,
and prepares a separate canonical stable upload folder in Downloads.

If any step fails, preparation stops. There is no automatic Steam upload.
Keep the printed backup path and UPLOAD FOLDER. An author update after this
capture requires review; do not skip the check. -ImportOnly imports the
source checkout without applying the repair or refreshing installed data.

WHAT CHANGED

The seven author updates captured on 8 November are integrated: Modern US
Navy, Mogami, PLAN, South Korea, India, Hyundai Export Ships and Modern RAN.
The capture contains 94 changed/new files and 14 explicit deletions, with
all 203 dependencies present and no capture-stage problems.

- Helicopter rotor/submodel changes and the Wasp update propagate through
  the builders instead of retaining old full-file copies.
- Mogami's Type 07 ASROC / Type 12 torpedo entries, flight-deck accounting
  and model changes are retained. Removed shared SAM overrides are retired.
- PLAN measured geometry and sensor/seeker edits are retained.
- Korean, Indian and export-ship signature changes are retained.
- The RAN's promoted NASAMS/CEAOPS and Mogami files are captured alongside
  the retired testing/legacy paths. Canonical precedence is rebuilt.
- All preceding November fixes remain, including alias-aware roster nation
  detection, saved Chilean hull pricing and stable UI author bridges.

R8 compiles against the newly captured game assembly. Dynamic Campaign Mod
calls a night-sensor method that now takes an optional nation argument; the
bounded adapter supplies the native null default so the game infers it.
Unknown game images remain inactive. Current Noesis, Tracker and other
recorded plugin hashes match the preceding capture.

R8 LIMITATIONS AND GAMEPLAY CHECKS

EnhancedDecoyMod, both Topographic Map DLLs and MultiStageMissiles remain
held before CLR load for the previously identified compatibility failures.
Their data is kept; native countermeasures and missile staging remain.
ExtendedGuidance stays disabled by the SEST profile. Clipped tabs and the
Global Hawk comparison are not advertised as fixed.

Launch beta and check startup; F11 current/previous/campaign costs and
Redback prices; debrief and continuation into a second mission; preparation;
Contacts and formation pop-out/return; compass on unit video; SAR; and
Osprey launch/conversion/fuel. Check night-capability decisions and the
updated helicopter/Mogami models too. Quit, then run:

  R8\Capture-Repair-Results.cmd

Attach its ZIP for review. No Unity launch, native Noesis rendering or
actual gameplay is represented by the managed tests. Stable UI 1.4.6 also
needs a stable Build 261021 tester for its F11/pop-out/compass rendering;
you can keep your own PC on beta.

Backups: original beta code and Identify data retain their existing
journal. Data backups are under steamapps\SEST-release-backups; the exact
restore command is printed during installation. Restore data before
restoring earlier beta code if reverting both.

STEAM UPLOAD AFTER GAMEPLAY CHECKS PASS

Update existing item 3812461539. Select ONLY the inner SEST_Integration
folder printed under UPLOAD FOLDER. Do not select the installed beta item,
repository root or toolkit. Paste STEAM-CHANGE-NOTE.txt after checks pass.

Confirm Required Items and the collection match the 203 dependency IDs in
data/load-order.tokens.txt, including Contact Log 3819427362, Topographic
Map 3826122523, Pop-Out Windows 3826396311 and B-21 Raider 3821992229.

Item: https://steamcommunity.com/sharedfiles/filedetails/?id=3812461539
Collection: https://steamcommunity.com/sharedfiles/filedetails/?id=3812390790

Mod Manager > Create Mod > Update Existing > 3812461539 > Pick Folder >
verified SEST_Integration > Submit. Confirm Steam success in Player.log and
check the public item timestamp, size and dependencies afterwards.
