SEST Runtime Fixes 1.5.0

Own code for the inspected Sea Power 0.8.7 Build 261021. The plugin stays inactive on an unknown game build. Enable the SEST pack and restart after an update. No game or third-party DLL is distributed in this pack.

Startup correction: native cost-window templates, input hooks and the pop-out bridge wait until the game's Noesis UI is initialized and a loaded game view is attached. No native UI setup runs from the early mod-assembly loading callback. The original tracker remains available until the replacement is ready.

F11: CUMULATIVE COMBAT COSTS
- Mission headings are bold with separators; side totals are larger with subtle colour accents. Pricing information, breakdowns and native completion dates have smaller secondary styles. Labels accompany every colour cue.
- In a mission: read-only USD category totals, quantities and cost details.
- Between missions in a Task Force campaign: cumulative totals and every completed mission, with authored mission labels and native completion dates.
- The campaign window fits between the native upper unit bar and lower timeline.
- Scroll inside the report. Its wheel input is consumed; the map does not zoom.
- Drag the native title bar to move the window; use its edges to resize. Placement is saved outside the game/mod files, separately for the mission and campaign.
- F11 or the window's close control closes it. The old currency/economy/year selector buttons are removed.
- With enabled Pop-Out Windows 1.0.1 and a second monitor, use the native title-bar pop-out control. Use the return control on that monitor to bring it back. The existing pop-out configuration and remembered windows are retained.

Group Manager 0.2.17
- Its compact toolbar gains a pop-out/return arrow beside the category controls and move handle. Hover over the panel to show the toolbar.
- The original group selection, filter, tree, drag/drop and resize controls remain.
- SEST scopes the panel's host lookup to the detached screen while it updates, then restores the normal root lookup. Main-screen placement remains separate from Pop-Out's placement. The third-party DLL is not edited or included.
- The bridge declines unknown versions rather than modifying an unreviewed UI.

SEST default UI keys
- Contacts: open it with its existing on-screen button. Where Contact Log is installed, SETUP unbinds its default F6 shortcut, which the game itself uses. A key you set yourself is kept.
- SETUP also unbinds Contact Log's default F8 diagnostic probe, so the strike planner keeps F8.
- Topographic Map keeps its own keys; SETUP does not change them.
- Where SEST UI Follow-up is active, the game's Quick Load moves from F9 alone to Ctrl+F9; see plugins/README.txt.

Contact Log 1.0.1
- The Contacts launcher and its window choose the main tactical view instead of the first view found across both monitors.
- Open Contacts with its existing on-screen button. A Pop out / Return to game button beside the Contacts and Classification Rules tabs moves their existing window between screens.
- Contact lists, filtering, classification editing, reference links and the original close controls remain the author's UI. The original DLL and configuration are not replaced.
- Main-screen placement remains in Contact Log's WindowRect setting. Detached placement and remembered screen choice are stored separately under the user's SEST folder. Existing Pop-Out layouts are retained.
- The bridge requires the inspected Contact Log 1.0.1 and Pop-Out Windows 1.0.1 DLLs and an available second monitor. Unknown DLLs are left alone.

Preparation and native sensor correction
- Own-unit plotting records initialize while paused at mission start or while the game's flight-preparation queue is active. No simulation step, sensor scan, pause toggle or enemy detection is run.
- Mission reset/unload clears the preparation cache. Replaced native plotting records can be initialized again.
- The native towed-system active-sonar retraction uses a checked sonar link. An incomplete sonar link waits locally and retries, rather than aborting the global fixed update. Mechanical retraction and valid sonar behavior remain native. A diagnostic names any affected unit.

Other retained corrections
- Compact debrief: mission and campaign cost totals; complete detail through F11.
- Destroyed launch-snapshot hull rows missing from the native debrief.
- Raw ammunition/inventory accounting, including ships, submarines, aircraft and land units; unknown quantities/prices remain marked. No crew, fuel burn, repair or survivor-damage estimates.
- RGM/UGM-109E5a land-clearance correction, with the native terminal profile.
- Native debrief times are unchanged.

Mods made for a newer game version
SETUP names them and leaves them alone, with one reviewed exception: THE REDFOR MOD, data only, which declares 0.8.8. While its folder holds no code, SETUP marks it compatible like a mod made for an older version and keeps the author's _info.ini. SETUP -RestoreModFiles puts the author's file back. This does not claim every REDFOR unit has been playtested.

Settings: plugins/sest_runtime.ini. Set an individual option to 0 and restart to disable that SEST correction. Game, mod and custom keybinding settings are not overwritten by the runtime updater. Native gameplay, layout, monitor focus and repeat-start acceptance are performed on the gaming PC.
