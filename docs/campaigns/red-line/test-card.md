# Red Line — current playtest card

Use [the combined Red Line/F11 acceptance card](../../playtests/red-line-f11-20261024.md) for this build. Its Red Line table covers all nine playable missions, active attack timing, protected contacts, shortened routes and preserved campaign variables.

Start a new 17-entry Red Line campaign for the revised launch definitions, and check the mission-browser copies as well. Planned windows are authored timing limits; actual play balance has not yet been observed. Keep the game closed while installing and confirm the exact green IN LINE message before restarting.

Highest-risk checks:

1. RL01's two missile-craft attacks at minutes 8/12; both must be stopped without harming protected neutral observers.
2. RL02's guaranteed airborne Dipper 23, GOLF's 10/18-minute torpedo orders and the minute-14 missile flank. No optional air purchase should be needed to begin the ASW search.
3. RL03/RLO2's minute-eight interceptor entries and actual missile launches. Allocated J-15s must be playable and fitted. RL03 now ends either way the intercept breaks (10 Nov 2026): an F-35 down, from minute nine (the Intercept path); or with no kill, from minute eighteen once neither F-35 is within 70 NM of the return box's centre (the Disengage path). Either way Dragon Eye must be in the box with no incoming weapon tracked. Checks P2 and P6 below.
4. RL04/RL06's Q-ship attacks and torpedo reach. The tender/supplier is a real protection task; report failed launches rather than assuming a scripted order is a shot. RL04's coaster may now be sunk or made to heave to (10 Nov 2026): set the lead ship's weapons to Hold and close Meridian Harmony on her track to about three miles. She turns neutral, heads north-west at slow speed, and a BRIDGE intel line says so. Sinking her after that ends the mission. Checks P3, P4 and P7 below.
5. RL05's shorter quiet passage and retained unseen fatal. RL06 instead scores concealment separately and continues after classification.
6. RLO1's 900-second bare-position benefit in RL02, `RL02GolfSunk` suppressing GOLF in RL04, and the still-held `RLO2EscortsNamed` reveal. No unrelated campaign outcome is changed.
7. RLC1's four-minute pickup hold now runs from arrival (10 Nov 2026; check P5): the stage enables and reactivates the held trigger, as stock Chagos Gambit arms its rain loop, so "Pilot aboard." should come about four minutes after the lead ship is within three cables of the raft, not the moment she gets there. Note the minute she arrives and the minute of "Pilot aboard."; "Pilot aboard." at once means the game does not restart a Time condition on `Action_ReactivateTriggers`. Test the fast-response and slow/delayed cases in game; static feasibility does not verify the native hold clock. The win stays at the pickup: "Pilot aboard." and the win come together, and the mission ends there. There is no return leg to sail.
8. All protected-contact loss conditions, air recovery, Task Force buying/rearming and mission exit/replay behaviour.

## PC checks for the builder grammar (10 November 2026)

The build steps of 10 Nov 2026 (build notes, "10 November 2026: alternative victories, the heave-to and progress reports") use only stock trigger pieces (two combinations, AND NOT on a Time and two area tests in one trigger, appear only in SEST's own missions), but these behaviours need a game:

- **P1 UnitDamageState spelling.** In the Mission Editor, save one trigger with *Unit damage state*, mode *All propulsion systems inoperable*, and a second with *Integrity below threshold* at 50%. Send the `Condition_ConditionN_*` keys and values the editor writes. They fill `campaign_data.DAMAGE_STATE`. Until then the flag stays off and RL04 offers no "stop her engines" outcome.
- **P2 RL03 Disengage.** With an F-35 inside 70 NM of the return box's centre, the mission must not end. With neither shot down, once both F-35s are beyond 70 NM of it, or have gone home after spending their missiles, it must end within about 5 seconds, and never before minute 18. The debrief shows "the F-35s have broken off" and Fighters is not completed. This confirms that North Borneo's refresh shape (`Taskforce=Taskforce2`, `AND NOT`, a 5-second reactivate) behaves as in stock.
- **P3 TriggerCompleted on a late trigger.** RL04's *Turns back: HeaveTo* ships disabled and is enabled by a challenge. Its having fired must satisfy the HoveTo path: once she has hove to and both ships are in the withdrawal circle with nothing inbound, the mission is won with the "has hove to" text.
- **P4 RL04 heave-to.** With the lead ship at Hold, close Meridian Harmony. Within about three miles she must change to a neutral symbol, take the new waypoint north-west and slow to telegraph 2. The ship's flight alone must not do it. Note the range when it happens. A frigate at Tight must stop engaging her once she is neutral. Sinking her afterwards must end the mission with "had hove to and was following the group when she was sunk". The *Progress: Running* report ("halfway to clearing the screen") must not appear after she has turned. In a second run, sink her from beyond three miles, then sail the lead ship through the water she passed: no heave-to line may come, and the mission must still be won once the group is in the withdrawal circle.
- **P5 Hold clock.** Item 7 above. "Pilot aboard." must come four minutes after the lead ship is within three cables, not on arrival. This also covers Southern Watch SW03's three-minute hold.
- **P6 RL03 attack orders out of range.** The F-35s' `Attack=` orders fire at 600 s and 960 s at Dragon Eye. If the KJ-500 is outside AIM-120 range, does the F-35 close and fire, fire anyway, or drop the order? This decides how often Disengage opens without a fight.
- **P7 Meridian Harmony's speed.** At telegraph 4 in sea state 2, measure her knots and the minute she reaches the marked circle south-east. The challenge chain runs along her route to that circle, so her speed decides whether the lead ship can catch her on it.
- **P8 Main flags.** In RL01 (Raiders), RL04 (Spoiler) and RL06 (Qship), the second Main objective must only change the objectives list and the debrief. It must not change the win or the loss, and a win must not end with that objective failed.
- **P9 RL03 in one tick.** Shoot down one F-35 before minute 18, then bring Dragon Eye into the box after minute 18 with the other F-35 beyond 70 NM. Expect one mission end and one victory message, the Intercept path's ("the intercept is broken"), and no "Progress" line with it.

The design's P10 (an RLC1 return leg) is left out: RLC1 has no return leg, by the owner's choice.

Progress reports (RL02, RL03, RL04 and RL06) are intel lines only, named *Progress: ...*. Note any that arrives at a moment it misstates.

Old restraint-only timings, GOLF's automatic weapons-free search and thirty-minute decoy guidance have been superseded. The campaign bible's dated revision describes current goals. Return mission, step, time, outcome and Player.log for any failure.
