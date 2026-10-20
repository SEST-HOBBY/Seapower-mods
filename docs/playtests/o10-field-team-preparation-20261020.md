# O10 field team and mission preparation

The PC feedback found a friendly full airfield on hostile Biak and requested a small UAV ground team, more dispersed strategic targets, and player control of opening deck, weapon and sensor settings.

## UAV detachment

The existing `sest_uav_forward` id now uses FallschimJager705's Field Drone Squad model and its launch/recovery positions from Small and Medium-Sized UAV Series, Workshop 3601891050. The subscribed mod supplies the mesh and materials. No new model or imagery is generated or redistributed. All twelve missions using this id inherit the small model. The native Airbase subtype is retained for aircraft handling; there is no stock runway/hangar model in this unit.

The team carries two reserve RQ-7s and supports three aircraft total, allowing the mission's airborne Moth to recover. It has one fixed-wing launch/recovery lane. The donor's attack-drone weapon, quadcopter lane, unused GPS sensor and invalid third hit-zone target are removed. Optics and aimpoints sit on the small ground model. The unit's own localized variant is retained.

O10's team is moved to friendly Yapen at approximately 1.72 S, 135.96 E, across water south of the enemy Biak enclave. Moth retains finite fuel, its minute-ten join and the team as HomeBase. The opening reconnaissance track and recovery distance are checked against the existing RQ-7 range; it is still vulnerable to a surviving SAM belt and is not a scripted target reveal. Other missions retain their authored local team locations.

## O10 optional targets

Three independent support sites are added to Biak: a western military ammunition depot, an eastern military fuel reserve, and a northern command truck. Each uses an existing collection unit, is on checked firm ground and is more than five nautical miles from the original pads. Each has an independent optional objective worth five points. They do not count as missile launchers, and destroying them does not disarm the missiles already loaded on the pads.

The main condition remains three of the original five launcher kills, with Langgur preserved. The third launcher kill still ends the operation. The briefing tells the player to service optional aimpoints before that kill if desired. The O7RingDown gate on the S-350 is unchanged.

## Native preparation phase

SEST's campaign mission definitions explicitly opt into the existing `OnMissionStart` / `Action_PrepareFlightDeck=True` phase. The renderer emits it only when the placed starting player force has a flight deck. This applies to native campaign copies and the corresponding standalone mission files. It does not convert authored operations into persistent-force missions or change the force purchased by the player.

A custom three-field preparation message explains the interaction: choose Start preparation to dismiss the message; keep the simulation paused; select each playable platform on the map or in Formation Manager; open its ordinary Flight Deck window to assign aircraft and loadouts; set weapon status and individual sensors with ordinary unit controls; unpause when ready. With flight-deck timings enabled, the native phase registers the available decks and completes queued preparation on the first unpause. Instant-timing settings retain their normal behavior. No new sensor/weapon defaults or force-wide Hold order is imposed.

The captured native `Trigger.ActionTrigger` handles this phase and filters player-controlled, surviving decks; its standard language text instructs the player to prepare while paused. The before-launch campaign airbase planner additionally requires a nonblank mission generation type. O10 deliberately has blank generation, so adding an AirbasePrepAvailable key alone would not expose that planner. This update uses the native loaded-mission phase instead.

A previous PC report could not select a platform in the forced standard preparation pause. The native phase therefore remains the main PC acceptance risk: dismiss the preparation message before selection and verify that the map and platform controls respond. The new explanatory message is not evidence that this earlier UI failure has been fixed. No game DLL, Harmony hook or UI plugin is changed. If selection still fails, preserve the current log and report which window remains open; a separate UI correction will be needed.

## Validation and PC test

Four focused regressions check the small unarmed model and finite deck, Yapen recovery geometry, independent support objectives with the main tally preserved, and preparation triggers without altered force generation or starting weapon/sensor values. Full build, audit and test results are included in the delivery notes after validation.

After installing, start a fresh O10. Check the Yapen team in 3D, launch/recover a reserve RQ-7, and inspect the UAV label. In preparation, select Langgur and the UAV team, prepare different loadouts, change an Eagle's weapon state and a battery's radar switch, then unpause and confirm the chosen states remain. Locate the three optional targets using reconnaissance and verify that only actual launcher kills advance the main condition. Test the preparation phase in a carrier mission as well.

The previously reported F-15EX map identification and MapKnownUnits exception remain separate investigations. This update makes no IFF, AAM range or map-worker change.
