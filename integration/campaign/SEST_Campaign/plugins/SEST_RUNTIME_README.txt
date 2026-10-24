SEST RUNTIME FIXES 1.0.0

Requires the existing Anchor Chain and HarmonyX installation. Only SEST's own
code ships here. Source and build/test instructions: integration/runtime-fixes/.
The plugin checks its owning pack is enabled and matches the captured native
Sea Power 0.8.7 (Build 261021) assembly SHA256 before installing any of its
three parts. It reads usersettings.ini once at startup; restart after
enabling/disabling the pack. An unknown game build, missing API or failed
part is logged and leaves native behavior in place. Player.log lines start
[SEST Runtime]: on 0.8.7 two lines contain "correction installed" and one
"campaign combat costs installed". After a game update, "inactive:
uninspected native assembly ..." means all three are off and the game's own
behaviour applies until SEST is matched to the new build; nothing needs
turning off.

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

CAMPAIGN COMBAT COSTS (CampaignCombatCosts=1)
Adds rows to the task-force debrief's Mission Summary: what this mission and
the campaign so far cost each side, in USD, priced from the Combat Cost
Tracker's price lists (Workshop 3807187341, with SEST_Combat_Costs'
additions) by the tracker's own rules. The tracker must be enabled; without
its price lists no rows are shown. For example:

  Combat Cost: Weapons    Player $1.21M + ? | Enemy $0
  Combat Cost: Losses     Player $520M + ? | Enemy $770M
  Combat Cost: Mission    Player $521M + ? | Enemy $770M
  Combat Cost: Campaign   Player $522M + ? | Enemy $1.08B + ? (3 missions)
  Combat Cost: Basis      USD, IOC prices; stores aboard and land units excluded
  Combat Cost: Unpriced   Mission: 3 rounds, 1 ship | Campaign: 3 rounds,
                          1 ship, weapons not recorded for 1 mission

Counted: weapons expended (rounds launched plus rounds fired, as the tracker
counts them; a round the tracker leaves out, such as chaff, a sonobuoy or a
decoy with no cost category, is left out here too) and ships, submarines,
aircraft and helicopters destroyed, including aircraft lost aboard a sunk
ship or on deck. Not counted: stores aboard lost ships and aircraft, land
units, damage and repairs, and the Neutral side. Allied ships that sail in
your task force count as yours.
Prices are the tracker's historical (IOC) prices, or its current-year prices
when its config.ini says UseCurrentYearCosts=True; the Basis row says which.
Changing that setting or SEST's price lists re-prices past missions too.
"+ ?" means at least one item has no price: the Unpriced row counts them,
and an unknown price is never shown as $0. "not recorded" means the game
kept no readable weapon report for that side (expected for a mission
finished before 0.8.7; not yet seen); a side that fired nothing shows $0.
The campaign total adds each completed mission once, from the records the
game itself saves with the campaign: a failed attempt or a replay adds
nothing, a new campaign starts at zero, and a campaign already under way is
priced back to its first mission. Nothing is written to the save. Player.log
names each unpriced item once ("combat costs: no IOC price for ..."). Not
yet seen in game.

Set an individual option to 0 and restart to use native behavior for that
feature. Linux tests cover mocked native APIs and policy, not Unity gameplay.
