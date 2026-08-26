# NF3 Scenarios

Small standalone missions carved out of **NORTHERN FRONT III FINAL NEWEST** by
`../make_scenarios.py`. Every unit keeps the type, loadout, position and waypoints it
has in the parent mission — these are the same forces, fought in isolation.

**Generated. Do not edit by hand.** Change the scenario list in `make_scenarios.py` and
re-run; the parent mission is never modified, so re-importing a newer save and
regenerating gives you scenarios that match it.

| Scenario | Units | The fight |
|---|---|---|
| **Sanctioned Convoy Intercept** | 83 | Three sanctioned tanker lifts under escort. A RAN inshore screen and one strike pair must sort neutral traffic from sanctioned traffic. Includes the full civilian layer — the identification problem *is* the mission |
| **Bomber Stream** | 27 | Nine H-6K Zhanshen in three packages plus a Tu-95 flight, against two F-22 flights and their tankers. Pure air intercept, no surface or land units |
| **Carrier Duel** | 14 | A Ford-class group and a PLAN carrier group, each with escort and air wing, nothing to hide behind. The smallest of the set |
| **SEAD over the Shelf** | 28 | An S-400 site plus a supporting AD battery against a strike package with dedicated escort. What the SEST MALICE and AGM-88 fits are for |
| **Boomer Hunt** | 77 | A PLAN SSBN group transiting with escort; a NATO surface group and one ASW pair have to find it. Civilian layer included as sonar clutter |

## Regenerating

```bash
python3 integration/missions/make_scenarios.py           # rebuild all five
python3 integration/missions/make_scenarios.py --list    # formations available to carve
```

The generator renumbers each unit class from 1, rewrites the `Taskforce<N>_Formation`
lines and the `<Unit>NameOverride` keys to match, and recomputes every `NumberOf*` count —
the only cross-references a mission file has.

## In game

They deploy with everything else (`tools\install-sest-packs.ps1`) and appear in the
mission list alongside the full missions, prefixed `SEST NF3 -`. The `scenarios/`
subfolder is repo-side grouping only; the game lists `user_missions` flat.
