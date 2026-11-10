R12 WORKSHOP-INCLUDED FEATURES — 9 NOVEMBER 2026

WORLD-BATTLE FLOW REFINEMENT (UI 1.4.10)
At the beginning of a paused world battle, a preparation checklist now shows
the setup steps. Choose Start preparation, arrange the force while paused,
then explicitly unpause to begin. A restarted battle shows it again; a saved
mid-battle session and ordinary missions keep their existing behavior.

To leave an unfinished battle, press Esc and choose End battle... . This
opens the normal debrief. Leave the debrief to return to the world campaign;
victory is not required. Read and confirm the campaign's full warning about
current losses and unresolved fighting. The existing outcome logic is retained.
Cancel at the confirmation to stay in the debrief and use its normal controls.
Test both an early withdrawal and a normal completed battle, then save/load.

This Steam update now INCLUDES the World Operations and Coordinated Strike
feature code as well as the unified world and ribbon data. The five reviewed
beta DLLs travel inside beta-support/SEST-Beta-Features.zip. They stay inert
until normal SETUP installs them on the supported beta game build. Stable
plugins remain in plugins/ for the normal game. No Steam branch is changed.

SUBSCRIBERS: close the game and run SETUP - double-click me.cmd from the
Workshop item. On a fresh beta installation, launch to the main menu, wait
about ten seconds, quit and run SETUP again to enable the staged features.
On an existing enabled installation, SETUP upgrades in one run. Run SETUP
after Steam updates the item to reapply its bundled features. Original restore
backups and Identify data are retained; unknown code is not overwritten.

PUBLISHER: run Prepare-PC.cmd from the full R12 toolkit. Upload only the
verified SEST_Integration folder it prints. That folder includes the feature
archive, normal SETUP integration and all campaign/ribbon data. Complete the
PC checks below before Submit Mod. No Steam publication has occurred here.

R11 MODERNISED WORLD, SERVICE RIBBONS AND STRIKE PRESENTATION
9 November 2026 | SEST-DEV | beta 0.8.7-261107, native SHA 499675cd

For the existing R10 beta installation: close Sea Power, extract the full
release toolkit into a new folder, then run Prepare-PC.cmd at its root.
That imports the reviewed source, checks author config updates, repairs
the beta code and installs the backed-up campaign data. It prints separate
data backup and canonical upload paths. It never submits anything to Steam.

Run the root Prepare-PC.cmd once. R12\Repair-Beta-Startup.cmd alone changes
code only; the root command also installs the new world and ribbon data.
If a check stops, retain its report and send the error. Do not print a
success message or continue installing after a failed author-update check.

WORLD CAMPAIGN
- One menu entry: SEST Modernised Worldwide Campaign 2028. The original
  world plus all regional additions are combined: 156 bases, 293 forces,
  54 patrols and 1,586 catalogue entries. Check Europe, Indian Ocean,
  Australia, the Americas and both sides of the date line on the beta map.
- Start a NEW game to receive the updated definition. The previous regional
  save ID is retained; existing saves keep their own units and base state.
- On the strategic map, F11 opens World Campaign Operations. Test Overview,
  Forces, Costs and Service; drag, resize, scroll, close and pop out/return.
  Scrolling the window should not zoom the map. Test smaller resolutions.
- Credits are native campaign points. USD is an independent catalogue
  estimate, with price basis and unknown items displayed. It is not deducted
  from the campaign budget. Fleet subtotal excludes embarked aircraft,
  stores, cargo and ground units; no zero-cost assumption for unknown prices.
- Launch and complete a battle; return to the world map, then save/load.
  Confirm the itemised battle cost appears once. Reloading the same completed
  report should not earn duplicate ribbons or duplicate battle totals.

RIBBONS
- Native completion ribbons are defined for Southern Watch, Southern Reach,
  Red Line and Sulu Line. Complete the final playable mission and inspect
  the native Task Force Service Record and citation. Existing third-party
  ribbon definitions, including Baltic Approaches, are preserved.
- World service is a separate profile record: Meridian Accord after three
  completed manual battles, Iron Meridian after ten, theatre service after
  two battles with recorded engagement positions. Auto-resolves do not count.
  Older reports without positions count globally only. Awards are fictional.
- World service persists under LocalLow/Triassic Games/Sea Power/SEST/
  world-service-v1.txt. It belongs to this profile/campaign/coalition across
  saves. Native commander records and native campaign saves are unchanged.
  An unknown saved format becomes read-only and is preserved.
- Specialist logistics/ROE/performance awards are not granted from spending.
  They need additional gameplay evidence before implementation.

COORDINATED STRIKE TOOL
- Open the existing author's tool during a battle. Verify its original unit,
  target, timing, readiness, salvo, guidance, arm, cancel and launch controls.
- SEST adds shared colours and a strike summary: planned rounds, leg notices,
  planned weapon value and remaining-to-launch value. Prices are estimates,
  separate from the F11 record of actual expenditure. Missing prices show ?.
- This iteration refines the author's IMGUI presentation. It does not replace
  the planner with a Noesis window or change its scheduling/launch algorithms.

COMPATIBILITY AND REGRESSION CHECKS
- Current Topography 1.6.0 keeps the author's option fallbacks and gets the
  inspected 50 m shoreline correction. Old 1.5.0 support is retained. Both
  inspected flat-only images remain held on this globe build.
- Current Pop-Out Windows 1.2.0 is recognised by its inspected hash. Check Contacts,
  Group Manager and F11 windows on the main and secondary display.
- DCM's automatic anti-ship salvo-hold patch targets the current beta method;
  the author's anti-ship-only predicate and existing native blocks remain.
- Recheck Identify sends, native F11 mission costs, debrief, campaign
  continuation, terrain clearance, SAR, Osprey and second-mission startup.

LEGACY ORIGINAL SAVE
The original definition is archived outside the new-game menu. Only if you
need a save made under sest.world_sandbox_2028, use tools/select-legacy-world.ps1
from the imported source checkout with -PackPath pointing at Workshop item
3812461539. This temporarily exposes its original menu entry. -Disable returns
to one world entry. It never rewrites a save. Your current regional saves do
not require this activation.

After testing, quit and run R12\Capture-Repair-Results.cmd; send the new capture.
Managed and installer checks cannot verify native Noesis rendering, Steam
upload behavior or a complete world campaign. Treat this as a beta candidate
until those PC checks pass. The canonical upload keeps normal-release active plugins and carries the
beta feature archive. SETUP selects the reviewed beta installation on the
supported build. The Operations/strike code is included in this Steam update.

R12 WORLD OPERATIONS FOLLOW-UP
Start Global Maritime Operations 2028 as each coalition. Confirm 196 bases,
next stage at 300 renown, and eight reachable recruitment stages. F11 must
match Admiralty task rewards and deadlines; completion pays only once.
Check Muharraq, Chambers Field, Souda and Diego Garcia in a generated battle.
Check quarter-stock new fields request supply and retain correct ownership
after save/reload. No aircraft or ships should be added by this update.

R12 OPENING AND WORLD-MAP COSTS
Check campaign-selection paragraphs and the opening operations paper for
readable wrapped text. Understood and Open the Guide must keep working.
On the strategic map, click Combat Costs beside Economy, then try F11.
The title must say Cumulative Combat Costs. Check scroll, resize, close,
return from battle and reload; existing and new world saves need the map
button once only. Completed battle USD totals must be in the summary.
R12 RIBBON EXPANSION - 10 NOVEMBER 2026
- F11 Service: 25 world ribbons; scroll, progress, text and coloured strips.
- Complete an accepted Admiralty order; compare qualifying task count. Failed,
  cancelled or moot orders and auto-resolved battles must not add manual service.
- Existing v1 records retain the old eight awards and manual battle progress.
- New Southern Watch/Reach commander: Australia remains default; US is an option.
- Check a native operation milestone in Service Records, then a nation's real
  award and its scenario citation. Other nationalities must not receive it.
- Confirm the opening brief, sidebar Combat Costs, direct F11, paused battle
  preparation, end-battle return, Contacts/Formation and strike controls remain.


SEST BETA FUNCTIONALITY TEST — CAPTURED ASSEMBLY 499675cd, 9 NOVEMBER 2026

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
