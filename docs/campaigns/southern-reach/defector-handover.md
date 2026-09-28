# TS08A — The Defector

An optional 95-minute escort in the eastern Great Australian Bight on
17 February 2029, between Great Australian Bight and The Southern Convoy.
The mission browser includes `Tasman Shield 08A - The Defector`.

This is a fresh implementation from the visible brief in the paused Claude
session. The screenshots showed three designs and three reviews completed,
but the synthesis failed. Their contents were not recovered. This document
does not claim that the original designs or the wider realism reviews were
completed here. The mission's people, mutiny and deployment are fictional.

## Play

RV Severny Veter is stopped southwest of the flagship, initially on the
opposing side at weapons Hold. Bring the flagship within 2 NM of her to
accept navigational control. A helicopter does not satisfy that rendezvous.
Then give the ship a course and speed and escort her northeast. Both she and
the flagship must enter the marked 4 NM handover area within 95 minutes.

A separate Udaloy recovery escort and a Ka-27 approach from the southwest.
The Udaloy is not TS08's named escort, which may already have been sunk.
Sinking the pursuer does not win this mission. Losing the defector, flagship
or any of the three civilian ships fails it. The requesting crew's account
is explicitly unverified; protection is the operational task, and the
decision on their request belongs ashore.

The mission offers 60 campaign points, a detachment and optional Seahawk /
patrol aircraft assignments. It provides no purchases, repairs, rearm or
prize-ship allocation. It can be skipped; TS09 retains its support window.
The offer expires once TS09 is complete. No cross-mission variable was added.

## Native mechanism and limits

The shared compiler accepts `victory.after.transfer_to_player` only for a
single stopped opposing surface ship at Hold, with a fixed rendezvous at
that ship, player surface ships as the meeting units, and an explicit fatal
loss rule. It rejects a moving ship, an aircraft rendezvous, a classify or
per-unit stage, and a persistent grant. Existing missions emit no new action.

The handover emits:

```ini
Action_UnitTransferToTaskforce=Taskforce1
Action_Units=Taskforce2Vessel1
```

The action is attested by the exported stock mission
`mods-source/_vanilla/original/missions/PLAN/PLAN 04 Escape from the Sulu Sea.ini`
(Trigger6). That example transfers a neutral submarine and later checks its
survival using its original section name. TS08A uses the same action on an
opposing surface ship. That exact transition still needs an engine test.
The escape and fatal triggers deliberately retain `Taskforce2Vessel1`.

The handover stage enables the escape check. The escape requires the ship
AND flagship in the box; initial proximity, destroying the pursuer, or
flying an aircraft over the rendezvous cannot win. The loss checks remain
active before and after transfer. There is no `JoinTaskForce`, `CampaignTag`
or roster addition for the ship. Whether the engine nevertheless persists
transferred units is a play-test question, not an established result.

The Udaloy's stock SS-N-14B has a 27 NM range in the exported ammunition
file. The dry-run report's 100 NM ceiling comes from the Ka-27's sonobuoy;
it is not an anti-ship threat at that range. The Ka-27 is at weapons Hold.
Coordinates pass the repository's coastline checks, but the game's coast,
AI pursuit and timing have not been exercised.

## Save compatibility and first play test

Use the standalone mission first, or start a **new Southern Reach campaign**
(either allocation version). Adding a dated optional entry shifts later
campaign indices; existing campaign saves have not been migrated or tested.
Keep backups of the old installed pack and saves if continuing an older run.

| Check | Expected result |
|---|---|
| Load and pause | Defector stopped, at Hold; all ships afloat; the rendezvous ring visible |
| Fly the Seahawk over the ship | No side transfer or victory |
| Bring only the flagship within 2 NM | One handover message; ship becomes selectable and accepts course/speed orders; northeast escape ring visible |
| Move only one of the two ships into the escape box | No victory |
| Bring both into the box after handover | Passage completes and one victory/debrief occurs |
| Destroy the pursuer before handover | Mission continues; no automatic completion |
| Lose the defector before, then after handover in separate runs | Passage fails in both cases using the original section reference |
| Lose the flagship, then a civilian in separate runs | Relevant objective fails and the mission ends in defeat |
| Wait out the clock | Defeat at 95 minutes; no late success or duplicate result |
| Lose a protected ship on the same tick as arrival | A loss must not produce a successful debrief; report any engine ordering issue |
| Skip the optional mission in a new campaign | TS09 remains reachable with its normal support window |
| Complete TS09 | Unplayed TS08A is no longer available |
| Win TS08A, then inspect the campaign roster | No defector added to the owned fleet; no repeat point award |
| Open Allocation version | Same branch, handover and escape behavior with the selected flagship |

Compiler tests and static pack validation cannot establish these runtime
results. Record the failing row and the observed unit/trigger if one differs.
