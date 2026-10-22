SEST RUNTIME FIXES 1.0.0

Requires the existing Anchor Chain and HarmonyX installation. Only SEST's own
code ships here. Source and build/test instructions: integration/runtime-fixes/.
The plugin checks its owning pack is enabled and matches the captured native
Sea Power 0.8.6 assembly SHA256 before installing either correction. It reads
usersettings.ini once at startup; restart after enabling/disabling the pack.
An unknown game build, missing API or failed correction is logged and leaves
native behavior in place. Player.log lines start [SEST Runtime].

ON SEA POWER 0.8.7 BOTH CORRECTIONS ARE OFF
Sea Power 0.8.7 (Build 261021, 21 Oct 2026) ships a new game assembly that
has not been inspected yet, so the plugin installs neither correction and
Player.log says "[SEST Runtime] inactive: uninspected native assembly ...".
The game's own behaviour applies - Tomahawk MST cruise height and the
debrief's section 3 - until a SEST update is matched to the new build.
Nothing needs turning off, and the options below change nothing until then.

MST TERRAIN CLEARANCE (TerrainClearance=1 in sest_runtime.ini)
RGM-109E5a and UGM-109E5a only, with terrain-following enabled, in native cruise
stages before TerminalApproach. The normal safe-altitude calculation still
runs. The correction asks the game's own terrain sampler for its available
samples through 1.08 nautical miles ahead, along the missile's actual heading.
When those samples contain positive-height land, it requests at least 500 feet
above the highest sampled terrain, retaining any higher native altitude.
Over open water the native sea-skimming result is retained. Near a coastline
the missile may begin climbing over water in anticipation of terrain ahead.
Boost, terminal attack, seeker, range, damage and native pitch/turn limits are
unchanged. Terrain remains collidable; there is no teleport or guaranteed-hit
logic. This does not implement route planning around mountains or guarantee
clearance in the terminal phase. PC terrain-crossing tests remain required.

TASK-FORCE DEBRIEF (TaskForceDebrief=1)
Section 3 can omit sunken ships because it uses the surviving post-mission
roster. The correction adds a missing hull's Lost row only when this exact
mission's launch snapshot includes its unique id AND its mission state
explicitly says IsDestroyed=True. It preserves hull/variant and proficiency,
avoids duplicate ids, and uses native row construction and sorting. It does
not change the owned roster, campaign points, save data or section 2 totals.
This can also repair the displayed older debrief when its exact launch and
destruction records remain saved. If those records are missing, no loss is
invented and no nearest-mission roster is substituted.

Set an individual option to 0 and restart to use native behavior for that
feature. Linux tests cover mocked native APIs and policy, not Unity gameplay.
