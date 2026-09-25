# In-mission intel: notes toward a modern ISR voice

A first look, not a rewrite. Nothing in the missions has been changed for
this yet; these are notes to come back to.

## What the player hears now

Every in-mission message both campaigns send is one of five kinds, each a
single line of prose written once per mission:

| Kind | When it fires | Where it is written |
|---|---|---|
| Stage intel | a classify or area stage completes | `victory.after.intel` |
| Reveal intel | the mission opens and an earlier mission's result is read | `reveal_if[].intel` |
| Flag intel | a named enemy unit is destroyed | `flags[].intel` |
| Support-loss intel | a support asset is lost | `support_loss[].intel` |
| Discovery / reward intel | a classify objective pays off | `reveals`, `discoveries` |

They are well written, but they are narrative: "Lifter over the platform",
"WHISKEY classified: one low-profile semi-submersible". Nothing tells the
player where a threat is now, which way it is going, or which sensor saw it,
and nothing arrives unless the player has just done something.

## What modern ISR-cued traffic sounds like

Short, time-stamped, sourced, and positional. The shape:

```
1215K  SENTRY 21 (Triton): carrier group, 41 12S 152 03E, course 040, 14 kn.
       Two escorts in company. Deck spotted, no launch observed. Next pass 1245K.
```

- **Time first**, in the theatre's zone (K is UTC+10, Australian Eastern).
- **Source named**: Triton, P-8, Wedgetail link track, a satellite pass, a
  sonobuoy field, ESM, a partner nation's report. It tells the player what
  to trust and what to re-task.
- **A fix, course and speed**, not "somewhere to the south".
- **Confidence and age** when the fix is old or inferred ("datum 3 hours
  old, area of probability 10 NM").
- **What changed**, not the whole picture again.

## A builder feature that would do most of the work

The builder already knows every red unit's start, route and telegraph
speed. A mission could declare:

```python
isr_updates=[
    dict(at_minutes=15, units=["red_cv"], source="SENTRY 21 (Triton)"),
    dict(at_minutes=35, units=["red_sub"], source="Kiwi 05 sonobuoy field",
         accuracy_nm=8, note="below the layer"),
]
```

and the builder would compute each unit's expected position along its route
at that minute, write the message in the shape above, and emit a timed
trigger (`Condition_Type=Time`, `Action_Taskforce1_Intel`), the same
mechanism the stage messages already use. A submarine's fix would be offset
by `accuracy_nm` so the report is a datum, not a cheat. Satellite passes
could be scheduled the same way, at realistic intervals, for missions where
no aircraft is on station.

What it cannot know is whether the unit is still where its route says:
a unit the player has engaged or that has deviated is reported where it
should be. Keeping the updates to the first half of a mission, or to units
the player has not yet classified, keeps that honest.

## Line-by-line suggestions from the proofreading pass

The reviewers of each mission slice were asked to point at up to four
in-mission lines each and say how they could read as an ISR update. They are
collected below, unedited, as raw material. Each quoted line is as it read
before that pass's edits; a few have since been reworded (the SW06 shuttle
now runs north, and the loss messages no longer price anything in points).
Positions and times in the suggestions are the reviewers' illustrations,
taken from the stations the missions place, not checked values.

<!-- isr-notes:start -->

### Southern Watch - story pages

**event 00b_meridian_intsum body para 4 (story page; this slice has no intel= strings)**

> ...was tracked as a commercial hull for six hours before it did.

Say who held the track and give a fix, e.g. 'Triton SENTRY 04 held her from 172250K as a commercial hull, 11 kn, course 140, 18 NM north of Coral Pioneer's track, until she turned to inspect at 180430K.'

**event 02b_meridian_intercept note**

> It is assessed as the Chinese surface group reported 30 OCT: a Sovremenny-class destroyer and a Type 071 transport.

Give the cue as a track report, e.g. 'P-8 BLUEFIN pass 301140K: Sovremenny DDG and Type 071 LPD, 09 24S 131 06E, course 140, 14 kn, Z-20 airborne; satellite pass 010200Z shows them still on that course.' (SW05 sag station and heading)

**event 03b_ward_memo body para 5**

> WEDGETAIL IS ON A LONG ORBIT AND CAN SEE THE SECTION COME SOUTH. WHAT SHE CANNOT DO IS ANYTHING ABOUT IT.

Promise a live link track, e.g. 'WEDGETAIL 02 WILL PASS THE MIG-31 PAIR AS A LINK TRACK FROM THE MOMENT THEY LIFT OFF THE ENCLAVE FIELD - FL520, MACH 2, RANGE AND BEARING FROM TEXACO 41 EVERY MINUTE. WHAT SHE CANNOT DO IS ANYTHING ABOUT IT.'

**event 05b_opposing_intercept note**

> The passage on the twenty-third will be contested.

End on the latest fix, e.g. 'Satellite pass 221430K: FUJIAN and LIAONING at 02 30S 129 00E, course 140, 16 kn, deck spotted for a strike; Triton to re-acquire at first light.' (SW11 red_cv station and heading)

### Southern Watch - SW01 to SW04

**SW03 Rig Seventeen, victory after-stage intel (lifter over the platform)**

> Lifter over the platform. The crew is on the helideck and coming aboard - get that aircraft south of the line.

Make it a time-stamped air picture relayed through Canberra's ops room from a P-8/Triton track, e.g. '1652 - Lifter 11 in the hover over Rig Seventeen, crew boarding. Patrol boat now 12 NM north of the rig, course 180, 28 kn. Lifter to clear south to the amphibious group now.'

**SW04 The Quiet Passenger, victory after-stage intel (classification of Contact WHISKEY)**

> WHISKEY classified: one low-profile semi-submersible, running south on the surface with almost no freeboard. Walk her into the box. Do not sink the evidence.

Make it a fused classification report, e.g. '0314 - Poseidon FLIR and Seahawk dipping sonar confirm Contact WHISKEY: semi-submersible, awash, 5°27'S 130°11'E, course 185, 7 kn. Handover box 30 NM south. Do not engage.'

**SW02 Steel Highway, reveal_if intel on O1BeaconFound**

> Torres Light's bridge recorder put a submarine on this route two days before she went missing. Her last datum is on your plot as a classified contact: treat the first ping as hostile.

Make it a cued track update, e.g. 'Torres Light's recorder datum, refreshed by a Poseidon sonobuoy contact at 0750: Type 039C, 10°18'S 144°06'E, course 090, 5 kn, below the layer, 12 NM ahead on the convoy track. Confidence high.'

**SW04 The Quiet Passenger, reveal_if intel on O2KiwiPicture**

> Kiwi 01's picture from the twenty-fourth: the coaster Rewi's crew named was working with a submarine, and they logged its datum on this route. It is on your plot as a classified contact.

Make it a dated track with an update source, e.g. 'Kiwi 01 datum of 24 Oct, updated by a Triton pass at 0200: submarine SIERRA estimated 5°36'S 130°21'E, course 180, 4 kn, below the layer; area of probability 10 NM. On your plot as classified.'

### Southern Watch - SW05 to SW08

**SW06 Blind Horizon, reveals['Picture'].intel (, inside the slice)**

> Sentry 06 has the northern group classified: two escorts on a south-westerly course, with the fighters that came for her now on your plot. The picture holds for the rest of the operation.

Make it a time-stamped Triton track report, e.g. 'SENTRY 06, 0724: surface group classified - LUDA DDG, TYPE 054A FFG - 09 06S 132 42E, course 235, 24 kn, about 100 NM north-east of the convoy; J-16 pair ENCLAVE 11/12 north of the orbit, heading 180. Track shared to your plot.'

**SW06 Blind Horizon, discoveries (Airlift) intel, set in the post-MISSIONS consequence block**

> Those escorts are screening a track, not a patrol line. There is a transport running south-west into the enclave field and nobody has put a name on it. Sentry 06 is the only thing in range that can.

Make it a radar/ESM track update, e.g. 'SENTRY 06, 0731: single heavy transport, Y-20 type, FL280, 08 36S 134 12E, course 330, 440 kt, no IFF, on the surface group's screen axis. Recommend holding north one more leg to identify.' Also note that the placed Shuttle 40 flies course 330, not south-west as the current line says.

**SW06 Blind Horizon, SUPPORT_LOSS['06'] intel**

> Sentry 06 is lost. The surface picture north of the horizon goes with her, and a replacement Triton is 60 points and a week of crew work at Edinburgh. - Ward

Open with a datalink-loss report and the age of the track, e.g. '0748: SENTRY 06 datalink lost at 09 40S 132 30E. Northern group now last-known only, ageing from 0746; no further coverage until the next satellite pass or a Darwin P-8.' Then keep Ward's cost line, with 'points' turned into in-world wording.

### Southern Watch - SW09 to SW12

**SW09 Southern Lifeline, victory after-stage intel (the message when the 35-minute service window closes, about 0705), in the slice**

> The window has run. STALWART reports the hose is in and COLLINS is casting off - get them south together, to the withdrawal line, before somebody comes to look where the Tu-214R was looking.

Open with a time-stamped P-8 or Wedgetail air picture: '0705K. Service complete. Coot-A 90 (Tu-214R) last held 33 NM west of the box at FL340, outbound north; Flanker pair bearing 355, about 140 NM, heading 180 at 480 kt. STALWART and COLLINS to the withdrawal line, 18 NM south.'

**SW11 Fujian's Shadow, reveal_if intel on SW06NorthernGroupClassified**

> Two of the escorts ahead of you are hulls Sentry 06 put a name to on 6 November, and the third keeps the company they kept. The screen is on your plot from the start. What is behind it is not - that you still have to find.

Frame it as a satellite pass matched to Sentry 06's 6 November track file: '1010K. Satellite pass, 02-30S 129-00E: Luda and Sovremenny correlated with the Sentry 06 track file of 6 Nov, Type 054A in company, heading 140 at 14 kt. Three tracks identified. Carriers not in the pass footprint.'

**SW11 Fujian's Shadow, flags intel on SW11FujianSunk**

> FUJIAN is down. LIAONING is still out there and still flying, but the newest deck in their fleet is on the bottom of the Banda Sea, and the corridor knows it before the talks open.

Make it a battle-damage report from Hawkeye 601 or a P-8: 'Hawkeye 601: FUJIAN stopped, listing, no deck movement, last position 02-30S 129-00E. LIAONING 25 NM north-west of her, heading 320 at 20 kt, still launching.' Keep the closing line about the talks as Mercer's comment after it.

**SW12 The First Ship Through, SUPPORT_LOSS intel for Wedgetail 03**

> Wedgetail 03 is down on the last morning of the campaign. 2 Squadron has two airframes and this was one of them. - Ward

Make it an air-picture handover, and change 'of the campaign' (game-speak) to 'of the passage': '0655K. Wedgetail 03 lost at 11-30S 130-48E. Air picture now from Darwin radar and the P-8 only. Last Wedgetail track on Strike flight 71: 09-10S 132-00E, heading 250 at 450 kt.' Keep Ward's line about 2 Squadron's two airframes.

### Southern Watch - optional and contingency operations

**O2 Southern Cross, victory stage intel (on classifying the coaster)**

> Kiwi 01 has her: MV Harbour Light, chartered through the same Singapore office as the Meridian boats, with a towed array she has no business owning. Rewi's crew has the datum logged. Bring the aircraft home.

Make it Kiwi 01's own contact report: '1052L KIWI 01 (RNZAF P-8A), EO ident: MV HARBOUR LIGHT, 10°12'S 131°30'E, course 110, 6 kn, AIS off, towed array streamed. Subsurface contact in company, sonobuoy fix logged and passed to MOC Darwin. KIWI 01 RTB Darwin.'

**O1 The Missing Beacon, victory stage intel (on classifying Torres Light)**

> Torres Light, adrift and holed above the waterline, crew in the boats. Her bridge recorder is still aboard. Get your lead ship alongside before the Meridian ship does.

A time-stamped Poseidon track update covering both ships in the race: '1612L BLUEFIN (RAAF P-8A): MV TORRES LIGHT dead in the water at 10°24'S 131°54'E, drifting west about 1 kn, AIS silent, two liferafts alongside. MV MERIDIAN SALVOR 14 NM south-east at 10°33'S 132°05'E, course 310, 11 kn, alongside by about 1720L.'

**O1 The Missing Beacon, denied message (Meridian reaches the coaster first)**

> Meridian's ship is alongside Torres Light and her crane is working. Whatever that recorder held is going aboard a ship we cannot stop without sinking her.

Report it as a Triton EO pass: '1719L SENTRY 04 (MQ-4C) EO: SALVOR alongside TORRES LIGHT at 10°24'S 131°54'E, speed 0, crane working over the bridge wing; nearest RAN unit 4 NM north-west. Recorder assessed lost.' Then one line from Mercer for the consequence.

### Southern Watch - Allied Dispatches

**D7 Before the Lifeline, denied= message; the slice's only in-mission message besides start/win/lose, and it has no intel= strings**

> Bear G 90 is at its release line with the serial intact. The umpires score the simulated launch against the surface group.

Make it a 1988 track call from Kitty Hawk's Hawkeye: '0615 HAWKEYE 600: BEAR G 90, 80 NM bearing 334 from KITTY HAWK, heading 157, 420 kn, FL300, at release line. Umpires score simulated launch against the surface group.'

**D1 Western Passage, start message (brief paragraph 3, the shadowers)**

> The expeditionary detachment has put a MiG-35 pair and a Su-24 up along the northern edge. They are here to find the oiler, and one of the pair is carrying something for it.

Cue it from the GlobalEye: '0835 ARGUS 70: 2x FULCRUM-F, 1x FENCER-E, 82 NM bearing 019 from the group, heading 200, 480 kn, FL280. FULCRUM-F 22 assessed anti-ship fit.'

**D2 Flight Deck Day, start message (brief paragraph 2, the drifting merchant)**

> the Reaper north of the box is watching a merchant that has been drifting off its filed route for two days.

Make it a Reaper EO report backed by a satellite pass: '1500 REAPER 12: MV SOLOMON TRADER, 190 NM bearing 335 from the box, drifting 1 kn off her filed route; last AIS 36 hours ago; 0400 satellite pass had her in the same position.'

**D4 Return Passage, start message (forces and brief, the Australian patrol, from the Russian side)**

> Opposing: an Australian patrol - a Hobart and an Anzac with an F-35A and a P-8A over them.

Give the Russians their own picture: '0310 BEAR 02 surface search: HOBART-class and ANZAC-class, 120 NM bearing 252 from the auxiliary, course 060, 18 kn; P-8A overhead, F-35A assessed on CAP.'

### Southern Reach - story pages

_Not reviewed yet._

### Southern Reach - SR01 to SR12

_Not reviewed yet._

### Southern Reach - Tasman Shield TS01 to TS12

_Not reviewed yet._

<!-- isr-notes:end -->
