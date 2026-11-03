R4 BETA REPAIR: WATERMARK, #!EXTEND SCAN, COST ROWS. 3 NOVEMBER 2026

For the installed R3 candidate (R1 and R2 are accepted too):
1. Close Sea Power and extract this NEW ZIP into a fresh folder.
2. Run Repair-Beta-Startup.cmd. It replaces all five candidate files, keeps
   the original backups and re-enables only after every copy verifies.
3. Launch beta and check:
   - no "Sea Power v0.8.7-261026" text over the game view;
   - Player.log holds a "[SEST Runtime] modifier files repaired" line (or
     "nothing to repair");
   - play a mission that fires an AGR-30 Redback, then open the campaign
     menu's F11 window: the mission lists each round with its quantity,
     unit price, line total and catalog section (sest_agr-30 at $70,000
     from sest_weapon_costs.ini).
4. Quit, run Capture-Repair-Results.cmd and attach its ZIP.

Disable-Beta-Test.cmd stops this test activation. Restore-Previous-SEST.cmd
restores the original backed-up code; the repair updates that restore journal.

What R4 changes (Runtime 1.5.2 beta; the loader, bootstrap, UI 1.4.3 beta
and Identify shim are the R3 sources rebuilt with this candidate's compiler):
- The beta's version watermark (SeaPower.VersionWatermark) is hidden after
  it starts; nothing else on the HUD changes. HideVersionWatermark=0 in
  plugins/sest_runtime.ini keeps it.
- Beta 261026 scans #!extend files once. On this PC that scan runs before
  the Workshop folders are registered, because Anchor Chain's preloader and
  the SEST bootstrap read FileManager.Directories early, so every Workshop
  mod's #!extend, #!prepend and #!copy file was ignored all session: SEST's
  cost catalogs, Cross-Deck stubs and the Collection and Allied Fixes
  extends. The Runtime rescans once the Workshop folders are registered and
  clears the ini cache, as the Mod Manager's Apply does.
- Cumulative Combat Costs reads SEST's own catalog files where the merged
  catalog lacks a section, and lists every expended round per mission with
  quantity, unit price, line total and the section the price came from.

Not in R4: the clipped tab borders (no screenshot received), the Global
Hawk range (its data is unchanged; see BETA-FEATURE-PARITY.md) and the
author plugins that stop on beta APIs (MissileControlMod, MultiStageMissiles,
OptimalTargetDist, SubModelStabilization, TestRange, UiWorkerProbe,
WeaponLauncherEffects, BetterTacMap): those need their authors' ports.

--------------------------------------------------------------------------

SEST BETA FUNCTIONALITY TEST — 2 NOVEMBER 2026

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
