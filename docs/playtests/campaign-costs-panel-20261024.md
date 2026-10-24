# F11 campaign costs panel and stores carry-over: PC check, 24 October 2026

This replaces the F11 steps (3 to 9) of `red-line-f11-20261024.md`; its Red Line steps still apply. Linux mocks cannot show Unity, Harmony or gameplay behaviour, so every step below needs the PC.

What changed, at the owner's request:

- **In a mission, F11 shows this mission's costs.** It is the Combat Cost Tracker's own panel; SEST no longer adds tabs or buttons to it.
- **In the Task Force menu, F11 shows the campaign's costs.** It is one information panel with no buttons: Player and Enemy totals and one line per completed mission. F11 closes it.
- **Stores lost carry through the campaign.** Before this fix the game rebuilt its campaign state from the `.sav` when the next mission launched, which erased the first mission's SEST stores record.

## Install and startup

1. Close Sea Power. Bring the clone up to the pushed `sest-dev/jolly-ride-rptj4t` commit, or run the playtest installer if you were sent a bundle. Note the green `IN LINE` commit and file count. Enable Anchor Chain, Combat Cost Tracker (`3807187341`) and SEST (one copy only), then restart the game fully.
2. Player.log must contain:
   - `campaign combat costs installed`
   - `combat inventory capture installed`
   - `F11 campaign combat costs installed`

   Report any `inactive`, `not installed`, `not copied to the campaign save` or missing-member line.

## F11 in a mission

3. Start or continue a Task Force campaign mission and press F11. You should see the tracker's own panel only, with no `Cumulative Combat Costs` or `Last games` tabs and no SEST buttons. Fire something and confirm the panel still counts it.

## F11 in the Task Force menu

4. Return to the Task Force menu and press F11. One panel titled `COMBAT COSTS / CAMPAIGN` should open at the middle of the left edge, not covering the mission information on the right:
   - a header line with the price basis and the number of completed missions;
   - `Player total` and `Enemy total`, each with Weapons, Ships, Aircraft, Land and `Stores lost with units`;
   - `Missions, latest first`, one line per completed mission.

   There must be no buttons or tabs. Press F11 again: it closes. Open it, then launch a mission: it must not stay on screen in the mission.
5. Hold Ctrl, Alt or Shift and press F11: nothing should change. Try a small window, and the tracker's own scale setting: the panel and its last line should fit on screen.

## Stores carry over (the reported bug)

6. In a mission, lose a ship or aircraft that still has stores aboard (a destroyer with missiles left is easiest) and complete the mission. In the Task Force menu, F11: note that mission's line and `Stores lost with units`.
7. Launch the next mission, then complete it or quit back to the Task Force menu. F11 again: the first mission's line and its stores lost must be unchanged, not `+ ?`. Then fully restart the game, continue the campaign and check once more.
8. Open the first mission's task-force debrief. Its `Combat Cost: Lost Stores` and `Combat Cost: Campaign` rows should agree with the panel.

## A campaign already in progress

9. In the campaign where the first mission "didn't save", open the panel. If SEST's local record of that game matches its losses exactly, the stores come back. That mission is then counted once, never twice. If no record matches, or several do, the stores stay `+ ?`. Report which happened, and the mission name.

## Result, 24 October 2026

The owner's report on the live Workshop build (`8e72f353`, 4,297 files, which carries everything above). It was a yes to each question, with no log or screenshot:

- **Step 4: pass.** The Task Force menu panel opens at the middle of the left edge.
- **Steps 6 and 7: pass.** Stores lost stay in the campaign total after the next mission.

Not reported: steps 3, 5 and 8, step 7's check after a full restart, and step 9's outcome (stores recovered from the record, or `+ ?`).

## What to send

Exact `IN LINE` commit and count, the step number, the panel's lines (a screenshot is easiest), the price mode, and a fresh Player.log.
