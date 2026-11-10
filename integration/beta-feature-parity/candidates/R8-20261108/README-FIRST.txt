R8 BETA REPAIR — CAPTURED ASSEMBLY 499675cd. 8 NOVEMBER 2026

Use this for the game assembly captured on 8 November (499675cd). Earlier
R3/R6/R7 repairs do not target this new assembly. Existing candidate backups and Identify data
are kept. Close Sea Power, extract into a NEW folder, and run
Repair-Beta-Startup.cmd. Then test in game and Capture-Repair-Results.cmd.

Runtime 1.5.5 and UI 1.4.8 target Combat Cost Tracker 0.8 and Pop-Out Windows
1.1.3. Updated author plugins use their own current beta fixes. The repair
also updates debrief rows, campaign/terrain bindings, formation's retired
label lookup, Osprey fuel conversion and the new night-sensor nation argument. Check all of these on the PC.

Held pending author ports: EnhancedDecoyMod, Topographic Map and
MultiStageMissiles. Their data is retained. ExtendedGuidance stays disabled
by the SEST profile. Native countermeasures and missile staging remain.

This ZIP is for a private beta playtest. The Steam upload uses the separate
canonical stable payload prepared by prepare-workshop-upload.ps1. Do not
upload these beta DLLs. BETA-FEATURE-PARITY.md lists the current limitations
and historical implementation notes.

SEST BETA FUNCTIONALITY TEST — CAPTURED ASSEMBLY 499675cd, 8 NOVEMBER 2026

Stay on the beta game build. This is a beta compatibility test candidate,
with the complete pre-beta Runtime feature implementation; it is not yet
a gameplay-verified Steam release. Do not use the earlier stable restore ZIP.

PC STEPS (close Sea Power before each command)

1. Extract this ZIP into Downloads, then double-click 1-Stage-Beta.cmd.
2. Launch beta to the MAIN MENU. Wait about 10 seconds, then quit the game.
   This first launch only checks startup readiness; plugins remain inactive.
3. Double-click 2-Enable-Beta.cmd. It requires the successful menu probe,
   migrates local Identify data, removes its Local row and enables the loader.
4. Launch beta again and test the features listed below. Quit when finished.
5. Double-click 3-Capture-Test-Results.cmd and attach the resulting
   SEST-Beta-References-*.zip from Downloads to the chat.

If the first probe or Enable stops, run 3-Capture-Test-Results.cmd and send
the ZIP/error. Do not skip the probe by creating flags manually.

WHAT TO CHECK

- Mod Manager: Identify Expanded appears once, as Workshop; no Local entry.
- F11: Cumulative Combat Costs opens; current, last-game and campaign totals,
  quantities, loss values and history are present.
- Finish a mission: debrief cost rows and mission completion time display.
- Continue to a second mission: preparation map/units, preparation and start.
- Contacts: shortcut/opening; Space and +/- control time; pop out and return.
- Formation: original/enhanced controls, pop out/return and responsiveness.
- Compass: hidden on the tactical map, retained on unit video.

RESTORE

With the game closed, run Restore-Previous-SEST.cmd. Original SEST code is
backed up before staging, and local Identify data is backed up before moving.
New/migrated Identify data remains under %LOCALAPPDATA%\SEST\IdentifyExpanded.
Backups remain under %LOCALAPPDATA%\SEST\BetaCompatibility\backups.
Settings restore byte for byte if unchanged since Enable; later edits are kept.

This candidate updates code inside your existing SEST Workshop item 3812461539.
It preserves campaign/data packs and saves, keeps the Workshop Identify DLL,
and does not change the Steam branch, game DLLs or original AnchorChain files.

The standard Steam game location is used directly. For another installation,
open PowerShell here and run, replacing the example path:

powershell -NoProfile -ExecutionPolicy Bypass -File .\Install-SEST-Beta.ps1 -Action Stage -GameRoot "D:\SteamLibrary\steamapps\common\Sea Power"

Use the same -GameRoot for Enable, Collect or Restore. For Workshop content in
a separate Steam library, also supply -WorkshopContentRoot pointing directly
to that library's steamapps\workshop\content\1286220 folder.

See BETA-FEATURE-PARITY.md for implementation, source provenance and build notes.
VALIDATION.json records the managed and fixture checks. In-game rendering,
second-monitor behavior and campaign progression remain to be verified on PC.
