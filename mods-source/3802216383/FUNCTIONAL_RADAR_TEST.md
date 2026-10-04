R10.22 functional radar test

Three locally defined and named radar systems are connected on both Hyuga and Ise:
- FCS-3 multifunction: fixed island arrays; Asahi eu_OPY-1 baseline, DirectedSearch, RPM 0, air and surface role. Configured range cap 347 km.
- OPS-20C main surface search: Asahi eu_OPS-20 baseline, surface role, 19 RPM. Configured range cap 46.3 km.
- OPS-20C auxiliary navigation: stock Nav_Radar baseline, surface role, 20 RPM. Configured range cap 32 km.
These are inherited gameplay settings, not verified real-world Hyuga ranges or guaranteed detection distances. The previous build already referenced these external profiles; this build packages unique local copies and appropriate display names. It does not claim a demonstrated runtime detection defect was found.
All existing scanner placements, meshes, sensor numbering and weapon associations are retained. Other systems still need their existing Euromod dependencies. No sonar or weapon-guidance changes in this build.

Install: replace the previous test folder with this folder; do not merge. Keep the existing required mods enabled. No direct game installation performed.

In-game detection test (not performed by Codex):
1. Start a fresh scenario with this R10.22 vessel. Confirm all three radar names appear in its sensor controls.
2. Use the ship alone, without friendly datalink sources. Place an airborne target at medium altitude around 30 km away and a surface target around 10 km away, on unobstructed sea. These are convenient test positions, not promised detection ranges.
3. Enable FCS-3 and check radar-sourced air acquisition. Disable it and enable each OPS-20C separately to check surface acquisition. Distinguish radar contacts from ESM/visual reports and retained tracks; restart each run if necessary.
4. Repeat with targets on different bearings to check coverage. Confirm each rotating scanner starts/stops with its own sensor control and stays on its mount; the island panels stay fixed.
5. Report missing sensor entries, failure to acquire, or errors from the game log. Detection depends on horizon, target signature, altitude, conditions and the game's sensor implementation.

Offline checks pass. Runtime detection and control behavior still require this test. Asahi/Euromod and original Sea Power sensor definitions are credited as the gameplay sources; existing asset credits remain included.
