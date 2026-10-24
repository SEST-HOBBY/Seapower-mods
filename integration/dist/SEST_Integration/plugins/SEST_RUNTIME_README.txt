SEST RUNTIME FIXES 1.2.0

Requires the existing Anchor Chain and HarmonyX installation. Only SEST's own
code ships here. Source and build/test instructions: integration/runtime-fixes/.
The plugin checks its owning pack is enabled and matches the captured native
Sea Power 0.8.7 (Build 261021) assembly SHA256 before installing its
features. It reads usersettings.ini once at startup; restart after
enabling/disabling the pack. An unknown game build, missing API or failed
correction is logged and leaves native behavior in place. Player.log lines
start [SEST Runtime]: the existing terrain/debrief fixes log "correction installed"; cost modules log their own installed lines. After
a game update, "inactive: uninspected native assembly ..." means all runtime features are
off and the game's own behaviour applies until SEST is matched to the new
build; nothing needs turning off.

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
Section 3 can omit sunken ships: for a generated or replaced mission (52 of
the 69 missions in SEST's four campaigns) the game lists the surviving
post-mission roster. The correction adds a missing hull's Lost row only when
this exact mission's launch snapshot includes its unique id AND its mission
state explicitly says IsDestroyed=True. It preserves hull/variant and
proficiency, avoids duplicate ids, and uses native row construction and
sorting. It does not change the owned roster, campaign points, save data or
section 2 totals. This can also repair the displayed older debrief when its
exact launch and destruction records remain saved. If those records are
missing, no loss is invented and no nearest-mission roster is substituted.
In a mission played as written (the other 17), SEST's mission files give
your ships no CampaignTag, so the game keeps no IsDestroyed record for them:
on 0.8.7 a ship sunk there is listed in section 3 without a Lost status (the
game's code says Undamaged; not yet seen in game), and the correction cannot
add one either.

Set an individual option to 0 and restart to use native behavior for that
feature. Linux tests cover mocked native APIs and policy, not Unity gameplay.

COMPLETE COMBAT COSTS (private playtest; native PC acceptance pending)
Requires enabled Combat Cost Tracker catalogs and a full game restart.
In a mission, F11 is the Combat Cost Tracker's own panel: this mission's costs.
In the Task Force menu between missions, F11 opens SEST's campaign panel at the
middle of the left edge, clear of the mission information, and F11 closes it. It shows the completed missions' Player and Enemy totals (weapons,
ships, aircraft, land, stores lost with destroyed units) and one line per
completed mission, the latest ten listed. Information only: no tabs or buttons.
Requires the inspected Combat Cost Tracker 0.7.1; with an unknown version the
tracker works as before and the campaign panel stays off. No game or tracker
DLL is redistributed.

Stores lost carry through the campaign. Each completed mission's lost stores and
full expenditure are written into the campaign save itself, so the next mission
no longer erases them. A mission completed before this fix gets its stores back
from SEST's local record of that game, but only when exactly one record matches
its losses; otherwise they show + ?. Raw quantities, never USD totals, are kept
under SEST/combat-history-v1.txt in the game's LocalLow settings directory.

The task-force campaign debrief gains Combat Cost rows for Player and Enemy,
this mission and completed campaign totals. Prices use the selected historical
or current mode. Existing checked prices are preserved; gaps use labelled SEST
estimates. All resolved weapon, ship, aircraft and land references are covered.

CampaignCombatCosts controls the debrief rows. CumulativeCombatCosts controls the
F11 campaign panel and the local record. CombatCostInventories captures remaining
itemized stores and raw expenditure. It writes only versioned SEST quantity keys
alongside native mission/campaign save records, never USD totals or purchase
points. Completed mission captures survive replays.

+ ? means missing quantities/prices, including unitemized flight-deck point pools.
Cargo, crew, operating fuel burn, repairs and damaged-only platforms are outside
this material-loss account. Land and parked-aircraft losses appear in SEST's
campaign panel and debrief rows; the in-mission panel keeps the tracker's scope.
Changing catalogs or price mode reprices the saved counts. Crew and game
acquisition points are never USD.

Player.log must show: campaign combat costs installed; combat inventory capture
installed; F11 campaign combat costs installed. Check the private playtest card
for the fire/loss/save tests. Linux mocks do not establish gameplay success on
0.8.7.
