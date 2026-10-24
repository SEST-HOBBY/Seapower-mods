# Fleet, terrain and debrief PC update

Private playtest built on the PC-confirmed 44cde6d0 / 4093-file update. Neither the GitHub deployment branch nor the Steam item is updated. The final bundle includes the corrected capture collector, the optional map-worker diagnostic, the O10 field-team/preparation checkpoint, and the changes below. A green IN LINE check verifies installed bytes, not gameplay.

## Ford's embarked fighters

Southern Watch 11 Fujian's Shadow now explicitly embarks sixteen US Navy F-35Cs, twenty-four F/A-18Es, twelve F/A-18Fs, six Growlers, four E-2Ds and eight MH-60Rs: seventy aircraft against ninety places. Every squadron reference resolves to a US squadron in the installed definitions.

Both modern Ford ids (`usn_cvn_ford` and `usn_cvn_gerald_r_ford`) receive the same default wing, and their companion Default/Variant air-group overrides are corrected too. Otherwise a native CustomAirGroup variant could silently restore the Hornet-only wing. This covers other authored missions using either modern hull. The historical `_legacy` hull is untouched; the separate `_jsf` Enterprise in Long Reach keeps its existing F-35 configuration. The seventy-aircraft mix is an authored SEST 2028 configuration, not a claim about a real deployed air wing.

## RGM-109E5a / UGM-109E5a mountain impacts

The screenshot identifies RGM-109E5a (MST Blk Va). TerrainFollowFlight is already true. Its native safe-altitude routine samples terrain only over a short forward interval and, for weapons, replaces the normal land clearance with the weapon's current low-altitude minimum. This is a plausible contributor to the reported mountain impacts; a PC reproduction is still needed to confirm the complete cause. The final 16-foot profile is not assumed to apply to every land attack: UseFinalFlightInLandMode defaults false.

The new own-code SEST Runtime Fixes plugin keeps the original calculation and adds a cruise-only floor for these exact RGM/UGM ids. It uses the game's actual geographic position, heading and terrain sampler, including available samples through 1.08 nm ahead, and requests 500 feet over positive-height land. A higher native result stays higher. Open-water sea-skimming is retained; anticipatory climbing can begin over water near a coast.

Launch and TerminalApproach stages are excluded. Native steering and collision remain active. This does not plan a route around mountains, increase missile range or damage, disable terrain collisions, or guarantee terminal clearance. Compare a fresh crossing of the reported ridge with an open-water engagement and a terminal hit on a coastal target. Preserve Player.log if it still collides.

## Missing lost ships in task-force status

The screenshot records Arafura and Warramunga in section 2 but omits them from section 3. The native debrief can build its status roster from the surviving post-mission force, which excludes destroyed hulls. The plugin therefore appends a missing Lost row only if this exact mission's launch snapshot includes the hull's unique id and its corresponding Mission state explicitly records IsDestroyed=True. Native row construction and sorting preserve the hull variant and proficiency. Existing ids are never duplicated; aircraft counts retain their native treatment.

This is a display correction. It does not restore a ship to the fleet, change campaign points, change section 2 totals, or write a save. Reopening an older debrief can display the lost hulls if its exact launch/destruction records remain. With no exact launch snapshot, it leaves the native display and logs why; it never borrows another mission's roster or invents a loss. A saved-campaign PC check remains necessary.

## J-20 close-range profile

The supplied J-20A definition has nonzero RCS 0.0014. The encyclopedia rounds it to 0 m². Radar stealth and all radar-guided seeker parameters are retained.

Two explicit SEST playability changes are made to that aircraft only: visual identification cap 5 -> 6 nm, and IRSignature SemiSmall (10) -> Meager (50). These are game configuration categories, not measured real-world J-20 signatures. The signature parameter changes by five times; that is not a claim that detection distance changes by five times. The builder checks the donor values before applying them and fails if the upstream radar signature changes. It does not alter the shared signature table, other aircraft, weapons or flight performance.

Visual identification, IR acquisition and a radar missile's own seeker are different requirements. Clouds, aspect, field of view and sensor operation still matter. Compare fresh J-20 and conventional fighter contacts at the same altitude, range, weather and aspect; use visual/IR-capable sensors and an IR weapon for the IR test. A visual contact does not guarantee a long-range radar missile can acquire it.

## Broken Wake

The original six-knot Stuart recovery, 31 wounded, two neutral merchants, Kilo and minute-five J-15D pair remain. Sheean joins as a player-controlled, independently placed submarine attachment with weapons held. Its position is checked using the coastline model rather than snapping to the older harvested position pool; that pool's nearest supposed land point disagrees with the coastline model here. The actual start is approximately 30 nm offshore.

An armed relay trawler east of the lane releases a fast missile craft at minute 25. Destroying the relay before that time disables that specific timed join. Destroying it later cannot recall the launched attack. The first J-15D pair and Kilo remain independent. Both branch conditions use native Time/UnitDestroyed, AND NOT, and Action_DisableTriggers; no unknown dynamic-spawn variable behavior is assumed.

Optional objectives cover relay classification, silencing the relay, neutralizing the Kilo and preserving Sheean. Reports at minutes 18 and 35 develop the relay deadline and engineering situation. They grant no target reveal. Stuart arriving still ends the operation; neutral harm still fails it. The player chooses between detaching a hunter to prevent the surface attack and maintaining a close ASW/air-defence screen. There is no randomized outcome presented as a simulation feature.

## Runtime boundaries and validation

SEST.RuntimeFixes.dll contains only SEST source code, compiled against the existing small Anchor Chain API stand-in; the stand-in is not shipped. It discovers already loaded HarmonyX and game types. It checks the owning mod's enabled state and the inspected native assembly SHA256 `c913e31f2d73e526f2d28043f522f2be26f12534fd0421eedee3cd70eab9cdd8`. Unknown game builds or incompatible APIs leave native behavior active and log the reason. Features can be disabled individually in plugins/sest_runtime.ini, followed by a restart.

The isolated C# suite exercises both callbacks against mocked native APIs, including terrain/sea/terminal exclusions, retained higher altitudes, invalid values, failure fallback, duplicate loss rows, hull/proficiency identity and exact-mission evidence. A separate read-only check verifies the real captured native method signatures, fields, stage names and lookahead constant without executing or distributing game code. No native game, Unity, HarmonyX or other mod DLL is redistributed. Full pack build, Python regression and audit receipts accompany the installer.

All 25 source packs were rebuilt from scratch and consolidated. After correcting Broken Wake's geography, the campaign pack was rebuilt and consolidated again: 4104 deployment files, 77 missions and four campaigns. The final 241 campaign tests pass; 133 tooling cases run with 126 passed and seven Windows PowerShell cases skipped. All twelve audit gates pass. The native-API check and 37 isolated C# assertions pass. The new J-20 fork increases SEST-owned priced-aircraft coverage from 34/36 to 35/37; the 63 cost compatibility sections and their prices remain unchanged.

PC acceptance remains outstanding for the new runtime hooks, mountain crossing, debrief records and native initial preparation controls. The previous F-15 map/MapKnownUnits investigation is still open. No map-worker, IFF, AIM-424/AIM-260 range or cost-catalog change is included in this revision. The worker Off/On/Status diagnostic remains optional and session-scoped.
