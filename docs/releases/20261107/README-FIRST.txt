SEST WORKSHOP UPDATE CANDIDATE — 8 NOVEMBER 2026, R10 TOPOGRAPHY

R10 restores the captured Topographic Map globe DLL on beta 0.8.7-261107
(game hash 499675cd...). Your 23:53 Brisbane capture confirms R9 loaded
Missile Control, Test Range and Optimal Target Distance successfully.
Only AnchorChain.dll changes from R9; Runtime 1.5.5, UI 1.4.8, Bootstrap and
Identify data-path code keep their existing bytes. All prior fixes remain.

EXISTING R9 INSTALLATION — QUICK REPAIR

Close Sea Power. Extract this complete R10 ZIP into a fresh folder. Run:

  Repair-PC.cmd

This upgrades the reviewed candidate, retains its original restore journal,
and preserves original author DLLs, configuration, campaigns and saves.
Keep the Steam branch on beta. In a mission, open Map Layers > Topography,
or use the mountain button in the map title bar (default hotkey F6).

CHECK THE MAP

Check terrain shading, sea depths, height under the cursor, aircraft terrain
clearance and submarine depth/thermal overlays. Pan/zoom and switch day/night
looks. Try the mission editor, then start a second mission. Check startup
messages and responsiveness too. Quit and run:

  R10\Capture-Repair-Results.cmd

Attach the resulting ZIP. The managed tests do not render a Unity/Noesis map.

WHAT CHANGED

The game removed two terrain-scaling option fields. Four reads in the captured
SeaPowerTopo 1.5.0 globe DLL now use native land/depth scaling. Its shallow-water
boundary is aligned with the native 50 m DEM boundary, in metres. It is adapted
only in a private cache; the original Workshop DLL remains byte identical.

All native operands resolve, CLR type discovery passes, the map-layer and
hook lookups resolve, and all 65,536 signed DEM sample values match native
height/depth scaling within float round-trip tolerance. Other 388 method
bodies retain their behavior. Source attribution and the author's MIT notice
are included in R10. The source bundle records the exact adapter and tests.

FEATURES STILL HELD

SeaPowerTopoFlat remains held on the globe beta: it is the legacy flat-map
variant. EnhancedDecoyMod and MultiStageMissiles remain held, as do the R9
Exterior Cameras, K5 contact strike, XQ-58 shadow, Alpine runtime fixes,
MV-75/Cheyenne II systems, EC-2 jamming and MV-75 escape features.
ExtendedGuidance stays off by the SEST profile. Their author data/models
remain installed. Optional Optimal Target Distance AAW interception remains
uninstalled; native target rules stay active. Experimental worker fallbacks
remain. R10 is the Topography port and does not claim these other ports.

FULL PREPARATION / UPLOAD FOLDER

Prepare-PC.cmd imports the reviewed source bundle into a fresh detached
checkout, checks author configuration changes, repairs code, refreshes
backed-up data and builds a separate canonical stable upload folder. Use it
when you need the full preparation repeated. It stops on an author change;
keep the report for review. It never submits to Steam.

The data refresh is still the reviewed 8 November configuration capture:
94 changed/new files, 14 explicit deletions, all 203 dependencies present.
All seven author updates and the preceding November fixes remain integrated.
This later DLL/log capture does not supply newer author configuration files.

GAMEPLAY BEFORE PUBLICATION

Test F11 current/previous/campaign costs and Redback prices; debrief and a
second mission; preparation; Contacts/formation pop-out and return; compass
on unit video; SAR; Osprey launch/conversion/fuel; Test Range; missile control;
and Identify stop/surrender broadcasts. Managed tests do not launch Unity or
verify Noesis rendering, inputs, second-monitor behavior or flight.

Stable UI 1.4.6 also needs a stable Build 261021 tester for F11/pop-out/compass
rendering. You can keep your PC on beta. This toolkit does not claim that
those stable UI checks or R10 gameplay have passed.

After checks pass, update existing Workshop item 3812461539 using ONLY the
inner SEST_Integration folder printed under UPLOAD FOLDER. Use the prepared
canonical stable folder. STEAM-CHANGE-NOTE.txt retains the data-update note;
private beta-only feature holds and adapters are documented here and in R10.

Keep the printed backup paths. Restore data before restoring earlier code
if reverting both. The existing candidate's original restore journal and
Identify data remain retained.

Required Items and collection 3812390790 must match the 203 dependency IDs
in data/load-order.tokens.txt. Item and collection links:
https://steamcommunity.com/sharedfiles/filedetails/?id=3812461539
https://steamcommunity.com/sharedfiles/filedetails/?id=3812390790
