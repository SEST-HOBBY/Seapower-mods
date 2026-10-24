# Complete combat costs — PC acceptance card, 24 October 2026

Historical acceptance card for build 74878a80. The later combined revision replaces the F10 viewer with F11 tabs; use [the current card](red-line-f11-20261024.md) when installing that newer bundle.

Private playtest. The new features have passed Linux source/data checks and mocked runtime tests. They have not yet been accepted in the native game. Keep disposable test saves separate from a valued campaign; the capture adds its own raw-quantity keys during ordinary saves.

## Startup

1. Close Sea Power. Install the exact playtest and check its expected green `IN LINE` line. Anchor Chain, Combat Cost Tracker (`3807187341`) and SEST must be enabled; restart the game fully. Group Manager (`3818251045`) can stay enabled. Load only one SEST copy; local integration and Workshop `3812461539` must not both load.
2. In `Player.log`, find all three new lines: `[SEST Runtime] campaign combat costs installed`, `combat inventory capture installed`, and `live combat cost summary installed`. There must be no inactive/uninspected-build or installation error for them. Older terrain/debrief installation lines alone are insufficient.
3. In a fresh standalone mission, press F11 for the author's overlay and F10 for SEST's summary. Record both. Close the F10 popup at 1x and a higher compression, then open/close while already paused. The previous speed/pause must be restored, and F10 must not create stacked windows. Test other native mission popups still close correctly. Remap `CombatCostsKey` and restart if F10 conflicts with a personal binding.

## Prices and expenditure

4. Record selected price mode in `systems/combatcosts/config.ini`. Use `cost-list.csv` for that mode; do not compare historical numbers to current numbers. Fire one MALICE, Redback, ARRW, torpedo, bomb and gun round in separate measurable increments. Existing checked prices and new model prices are distinguished in the list. An explicitly non-procured helper should not add a bill.
5. Drop one sonobuoy and expend one chaff/noisemaker. F11 should expose those categories; F10 should reflect native recorded quantities. A reusable pod sitting on a hardpoint is not expenditure. Check fuel-tank/pod hardware when the native expenditure/loss counter records it; rockets inside a pod must be charged by their own quantity and hardware must not include them a second time.
6. Hide F11, fire another known round, then open F10 and restore F11. Recording must continue. If the author's overlay errors, check the separate SEST capture/viewer continues; do not deliberately corrupt live game files.

## Losses, persistence and campaign

7. In a disposable mission, lose one land radar/vehicle, one airborne aircraft and one parked aircraft. F10 should show their material losses once, using `cost-list.csv`. Record whether the native register supplies the parked aircraft at all; the plugin cannot synthesize a loss the game never reports.
8. Lose a ship carrying known itemized stores and an embarked helicopter. Compare the native recorded airframe/hull count with F10 and the debrief. Itemized stores must be added once and airframe/hull prices must not be added by the inventory supplement. A remaining virtual deck-ammunition point pool must show `+ ?`, never a conversion of points to USD. An embarked aircraft the native game does not register remains an engine limitation to report.
9. Save and reload mid-mission. Previously captured stores must be retained; a new loss must add once. Open F10 repeatedly and confirm that inspection adds no cost. Start another mission to confirm old current-mission quantities are cleared.
10. Complete two task-force campaign missions. Debrief rows must show weapons, ships, aircraft, land, lost stores, mission and campaign totals. The campaign must equal the two completed missions in the same price mode. Reopen a debrief, restart and reopen it again: totals must agree. Replay an already completed mission and verify its original completed capture remains rather than accumulating an extra attempt.
11. Open an older campaign. Existing native records should reprice; absent magazines remain `+ ?`. A different/new campaign starts at zero completed missions. In a separate comparison restart with the other cost mode, and confirm raw saved counts reprice from the matching CSV column. Opening a debrief must not change the save's SEST quantities.

## Return evidence

Send the observed F10/F11 and debrief totals, selected price mode, mission/save names, exact `IN LINE` commit/count and fresh Player.log. For a native-binding error, close the game and run `tools/export-map-diagnostics.ps1 -IncludeGameAssembly`; return its ZIP. The extended strict ABI verifier needs the exact 0.8.7 DLL to complete fresh verification; an older-DLL structural comparison is not acceptance.

Acceptance is pending until these behaviors are observed. Crew, repairs, damage-short-of-loss, operating fuel burn and unrepresented cargo are outside this material-loss account. This test does not assert those costs are zero.
