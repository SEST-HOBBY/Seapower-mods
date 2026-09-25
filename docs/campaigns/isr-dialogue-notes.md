# In-mission intelligence: reviewed ISR dialogue

Updated 26 September 2026 against the additional campaign content at
`d546858240ea948b6f76af27fcd6c5afa8c3ac41`. The 34 suggestions collected during
that proofreading pass have now been reconciled with the campaign sources.
The table below records their disposition. This supersedes the earlier raw
examples; those examples remain in Git history, not in the shipped dialogue.

## What is implemented

The existing opening assessments, story pages, classification messages,
saved-report reveals, discoveries, loss reports and exercise-control messages
now use a more modern intelligence voice. Reports identify their source or
reporting cell, distinguish observation from assessment, and state what needs
fresh local confirmation. Satellite radar imagery, AIS, patrol observations,
airborne radar and acoustic records contribute different parts of the picture.

A contact an earlier operation's report puts on the plot (`reveal_if`, and
SW06's `reveals`) is revealed with `UnitRevealTime=-1`: it stays on the plot
for the whole operation, and its message says so rather than sending the player
to find it again. Only contacts the reveal does not cover are left to local
sensors. Messages name their sender as `SENDER: text`; the builder stops on a
`|` in any message body or intel text, because the game splits a message on
`|` into title, body and button (see the 26 September review in
[narrative-review-20260926.md](narrative-review-20260926.md)).

Existing triggers, reveal persistence, force composition, schedules and scores
are unchanged. This is a text revision, not a satellite simulation or a new
stream of timed contact reports. No fabricated observation time, coordinate,
heading, speed, depth or next-pass schedule is inserted into a player-triggered
message. A narrative report dated before an operation remains an earlier report.

| Message | Existing condition | Wording rule |
|---|---|---|
| Stage intel | Classification or arrival/service check | State what the condition establishes; give the next order |
| Saved-report reveal | An earlier operation's variable is true | Correlate the saved identity; do not call an old datum a fresh acoustic fix |
| Destruction report | Named unit destroyed | Confirm that loss; assess other units separately |
| Support loss | Named support asset destroyed | State the coverage or support lost, without inventing a replacement or changing reveal persistence |
| Discovery | A classification condition completes | Describe the cue; do not pre-identify the next objective |
| Denied operation | Opposing unit reaches its assigned area | Report that event, without claiming an unobserved boarding or launch |
| Opening assessment / story page | Authored narrative | Distinguish prior collection from the operation's current sensor picture |

## Disposition of the 34 suggestions

Paths below refer to `integration/campaign/campaign_data.py` for Southern Watch
and `integration/campaign/southern_reach/` for Southern Reach / Tasman Shield.
Story paragraph references describe the content, not a new trigger.

| # | Location | Applied revision |
|---|---|---|
| 1 | SW `00b_meridian_intsum`, commercial-hull paragraph | AIS, merchant reports and patrol observations support identity, not peaceful intent |
| 2 | SW `02b_meridian_intercept`, analyst note | Patrol and satellite reports identify the group; current course needs confirmation |
| 3 | SW `03b_ward_memo`, Wedgetail paragraph | Radar acquisition and correlation replace guaranteed tracking from takeoff and minute-by-minute updates |
| 4 | SW `05b_opposing_intercept`, analyst note | Imagery and intercepted traffic give a last observed area; Ford's aircraft update it |
| 5 | SW03 `victory.after.intel` | Amphibious control reports the lifter over the rig and the crew boarding; the order is the return, because the pickup is the area arrival; no invented hover fix or measured loading |
| 6 | SW04 `victory.after.intel` | Escort classification report separates the semi-submersible's identity from its unconfirmed cargo |
| 7 | SW02 `reveal_if`, `O1BeaconFound` | Recovered recorder evidence matches the report; the contact is classified and held on the plot for the operation; engage under the current orders |
| 8 | SW04 `reveal_if`, `O2KiwiPicture` | Kiwi 01's prior report correlates the Type 039, held on the plot for the operation; no satellite fix of a submerged boat |
| 9 | SW06 `reveals.Picture.intel` | Sentry 06 / fusion-cell report names the Luda, the Type 054A and the J-16s, held on the plot for the rest of the operation |
| 10 | SW06 `discoveries`, `Airlift` | Preserve the corrected northbound transport cue without giving it an unearned identification |
| 11 | SW06 `support_loss` | Confirm Triton's loss and coverage gaps; retain earlier reports without claiming that persistent reveals decay |
| 12 | SW09 `victory.after.intel` | Service control reports the scheduled area check; prior reconnaissance remains a warning, not a fresh raid fix |
| 13 | SW11 `reveal_if`, `SW06NorthernGroupClassified` | Correlate the escort screen with earlier Sentry reporting; the escorts are held on the plot, the carriers must be found |
| 14 | SW11 `flags`, `SW11FujianSunk` | Confirm Fujian's loss without assuming Liaoning's survival, movement or flight activity |
| 15 | SW12 `support_loss`, Wedgetail | Report the allocated aircraft's loss and need for surviving sensors; no false claim that all of 2 Squadron has only two aircraft |
| 16 | SW O2 `victory.after.intel` | Kiwi 01 reports Harbour Light; separate surface collection from the acoustic record and order the recovery handover |
| 17 | SW O1 `victory.after.intel` | Escort watch reports Torres Light and the recovery race; no unassigned Poseidon source |
| 18 | SW O1 `denied` | Escort watch reports Salvor alongside with her crane working, and the recovery failed (the denial ends the operation); no unassigned Triton |
| 19 | SW D7 `denied` | Exercise control reports the Bear at its release area with the serial intact and closes the serial; the serial went live at 0412 (review-disposition: "nobody is shooting anything real") |
| 20 | SW D1 `brief` | Argus 70 provides the air picture and an assessed anti-ship threat without illustrative telemetry |
| 21 | SW D2 `brief` | Reaper 12 observes Solomon Trader while the shore cell compares AIS and imagery |
| 22 | SW D4 `brief` | Earlier surface reports place the patrol about 120 NM west-south-west, closing north-east; the escorts' and fighters' sensors update it |
| 23 | SR `02_sitrep`, protection-group paragraph | Satellite and maritime-patrol reporting supports the formation assessment |
| 24 | SR `04_sitrep`, northbound formation | Triton reporting and imagery give the formation and its reported speed |
| 25 | SR `03b_intsum`, ice-edge paragraph | Radar-satellite detections and naval emissions put the formation across the route to Casey; no invented recent fix from grounded aircraft |
| 26 | SR `06_sitrep`, carrier paragraph | Separate surface imagery from Wedgetail and partner air reports over the airway |
| 27 | SR02 `victory.after.intel` | Acoustic classification of VICTOR, shared with Wellington and Canberra; no invented live buoy position |
| 28 | SR05 `victory.after.intel` | Sentry 22 classifies the frigate and corvette for correlation with earlier imagery |
| 29 | SR10 `victory.after.intel` | Local identification confirms Liaoning and Nan Hai 27; no claim that a satellite alone reads hull identity |
| 30 | SR12 `victory.after.intel` | Surface identities go to the next patrol; local sensor coverage is still needed |
| 31 | TS01 `reveal_if`, `SR12NetworkNamed` | Correlate Nan Hai 27 with the 14 January record, held on the plot for the operation; current transmissions remain unconfirmed |
| 32 | TS03 `reveal_if`, `TS02SubNamed`, and opening | Correlate TANGO's Cook Strait record with the reported rendezvous; she is held on the plot from the first minute; no fabricated second satellite pass or guaranteed dive response |
| 33 | TS04 `reveal_if`, `SR12NetworkNamed` | Correlate the escort identity, held on the plot for the operation; locate Liaoning separately instead of inventing a live radar fix |
| 34 | TS12 `reveal_if`, `SR03CrewRecovered` | Use the 12 December search record to identify Nan Hai 27, held on the plot for the operation; distinguish an assessed spotting role from observed transmissions |

## Future timed reports

The earlier proposal would have extrapolated positions from authored routes and
telegraph settings, then presented them as observations at fixed times. That
would be misleading after manoeuvre, combat, damage, detection changes or a
source's destruction. Adding random position error does not make an invented
observation valid, and keeping reports early does not establish their accuracy.

Any later implementation needs a verified runtime source for contact state,
observation time, collection availability and identity/confidence. When that
information is unavailable, use an explicitly labelled prior report or search
cue without a fabricated current fix. Do not add `isr_updates` declarations
until the builder and running game can support and test those semantics.

A report with a genuine runtime observation can use: source, observation time
and time zone, contact, measured position/movement, confidence, and action.
Use UTC for cross-theatre reporting unless the authored document clearly defines
its local time. Scheduled future satellite coverage needs its own verified
mission implementation; it is not implied by a story reference to imagery.
