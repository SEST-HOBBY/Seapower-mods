# AGR-30 Redback on the Seahawks — 23 October 2026

The owner's report from the game (Sea Power 0.8.7), on the build with the
19 Oct follow-up's Seahawk mount (`27153767` onwards):

- "aus seahawk has issue with agr-30 as its sitting at the bottom of a quad
  hellfire rack";
- "also not shooting agr-30". Confirmed in a follow-up: the player ordered
  the RAN MH-60R, on SEST Redback Strike with the pods visibly on the
  aircraft, to attack a boat. The AGR-30 was in the weapon list and was not
  fired. (An earlier message saying it was not in the list, and one saying
  "AGR-20", were typos.)

So the store was loaded, offered for that target and chosen. What failed is
a condition the game checks at launch. Both faults were fixed at the source
in the build after `f13e38cc` (`57375598`). Later the same day the owner
saw the round fire from that build, asked for a different MH-60R fit, found
that it "doesnt boost as long anymore" and asked for a realistic slow-down
to the cruise: *Second report*, below, changes the fit and the flight
again. The checks in *In the game* are for the build after `57375598`.

## Why it did not fire

Ranked by the evidence in the files:

1. **Radio command with no guidance channel (the cause, on the
   evidence).** The 19 Oct follow-up made the round
   `MidCourseCorrection=1`, radio command, so that it could be retargeted. A radio-command round needs a guidance
   channel: a radar or command link with `WeaponChannels` above zero that
   the launching hardpoint names in `AssociatedSensors=`. The RAN MH-60R's
   hardpoint names none, and its only radar, APS-147, has no weapon
   channels anyway. So the game could offer the AGR-30 and still not launch
   it. The same airframe's AntiShip fit fires the Hellfire L, which is also
   Ka-band active radar with the same 11 kW, but `MidCourseCorrection=0`,
   so it needs no channel.
   - The stock game gives its radio-command rounds a channel: the AS-2
     the Tu-16K's Rubin-1A radar, the AGM-12B the F-5A's ARW-77 command
     transmitter, and the Su-24M's rounds a `GuidancePod` (radio command,
     one channel) hung beside them. The mods do the same: the MQ-9's author
     built a guidance pod into the airframe for its radio-command GBU-49
     although it already carries a laser designator.
   - `tools/check_weapon_employment.py` records the same symptom for HMAS
     Warramunga's NSM: a midcourse round with no channel, "the weapon simply
     never fired". That rule covers ship, submarine and land mounts only, so
     no gate saw this one.
   - Applying the rule to every SEST Redback carrier, nine of the 21 had no
     channel: both MH-60Rs, both S-70B-2s, the A-10A, the A-10C and the
     A-10C+ (an infrared head and a laser designator only), and the AH-64A
     and Sea Apache AH-64NA (a laser designator only).
2. **Active radar inside a pod (a possible second blocker).** The design
   notes said no container held an active-radar round. One does in the
   configs: US Naval Aviation's `usn_bru-61a_storm` quad on the F-35Bs holds
   the GBU-53, which SEST Collection Fixes ships as `GuidanceType=3` with no
   midcourse. No play test has seen one fire from that container, and no
   note records any carrier firing the active-radar Redback since
   `27153767`, so this stays open. If the Redback still does not leave the
   pod after this fix, the fallback is the infrared form of 18-19 Oct
   (`GuidanceType=1`), which flew from both pods. (It left the 19-tube
   LAU-3 on `57375598`; the 7-tube LAU-68 is still to be seen: *Second
   report*.)
3. **Ruled out.** The launch envelope (0 to 20,000 ft, 0.16 to 30 NM, no
   lower altitude limit; the Hellfire needs 100 ft), the target class (ASuW
   is the primary, and a boat is a surface target), the pods (the same shape
   as the LAU-68 and LAU-3 APKWS pods that fire elsewhere), the mount (a
   sub-model is only drawn; the colliders are the hull's) and the AI's role
   (the shot was ordered by the player).

## Why the pod sat in the rack

The MH-60R model has three pylon meshes. `H60_PylonA`, the inboard pylon, is
always drawn. Only the M299 Hellfire launcher's arm (`H60_Pylon114`) or the
Penguin's (`H60_Pylon119`) reaches the outboard station points. Each fit
shows one of those arms, or neither.

| Build | Where the pods hung | Result |
|---|---|---|
| `59efc31c` | 7-tube pods, two a side on the Hellfire rail points | found from the seats on 19 Oct |
| `d9755f4e` | the upper rail point (Stations 10/11), launcher hidden | "pods float without their supporting arm" |
| `27153767` | the lower rail point (Stations 12/13), launcher drawn | "at the bottom of a quad hellfire rack" |
| `57375598` | 19-tube on the inboard pylon's tank point (Stations 1/2), raised 0.13 m (`RedbackH60`); the eight Hellfires kept | it fired; "the agr where the fuel should be and the agm present and where the agr should be" |
| now | a 7-tube in each Hellfire's place on the drawn launcher, two per station line on 10-13: eight pods, 56 rounds, on `RedbackM299` (the Hellfire's seat lowered 0.04 m); tanks back on 1/2; the Penguin arm hidden | to be checked |

`57375598` reasoned from the files that every SH-60 in the collection (nine
files, six mods) hangs its tanks on Stations 1/2 and its torpedoes on 3/4,
on the inboard pylon, and put the pod in the tank's place, raised 0.13 m
toward the torpedo's point so that its top would meet the rack (a real
MH-60R hangs 70 mm pods from a BRU-14 rack, not an M299). The owner saw it
fire there, but wanted the tanks back and the rockets where the Hellfires
hang. *Second report* has the fit that replaces it.

## What changed

**The round, on every carrier.** `sest_agr-30` is fire and forget:

| Key | 19 Oct follow-up | `57375598` | Now |
|---|---|---|---|
| `MidCourseCorrection` | 1, radio command | 0, the donor's own | 0 |
| `TerminalApproachDist` | 2.0 NM | 8.0 NM | 2.0 NM again |

The second report also changed the speed keys: *Second report*, *The
slow-down*.

`Retargetable=True` stays. Six of the collection's `MidCourseCorrection=0`
rounds set it (the ROK Hyunmoo-4-2 and HGV are active radar, like this one),
but the stock game pairs it only with radio command (Walleye II), so whether
a Redback can still be retargeted in flight without a command link is for
the game to show.

Nothing updates the round in flight now, so its seeker has to find a target
that has moved since launch. `57375598` switched it on 8 NM from where the
target was at launch, as the SS-N-22B's does on the same guidance, so that
its 120-degree gimbal would cover a boat that moved a few miles during a
long flight. That also put every shot inside 8 NM into terminal approach
from launch, which holds the round's height: no climb (*Second report*). It
is 2 NM again. The dive still starts at 1.1 NM. As on 19 Oct: Ka-band,
11 kW, the 35 NM seeker, the 30 NM launch range, the ten-second flame and
the 2 km loft.

**The fits.** Built by `integration/allied-fixes/build_patch.py` (ROLLOUT)
through `integration/common/redback.py`:

| Carrier | Before | Now | Channel for radio command |
|---|---|---|---|
| RAN MH-60R (`ran_mh-60r`) | tanks on 1/2; a 19-tube on each lower Hellfire rail point (12/13), launcher drawn | the AntiShip fit with a 7-tube pod in each of its eight Hellfires' places on the drawn launcher (10-13, two per station line, `RedbackM299`), tanks on 1/2: 56 rounds (`57375598`: a 19-tube on each tank point, the Hellfires kept) | none |
| US Navy MH-60R (`usn_mh-60r`) | Mk 54s on 3/4; 19-tube on 12/13, launcher drawn | as the RAN one, from AntiShipLateLongRange | none (APS-153 not linked) |
| S-70B-2, US and RAN | one 19-tube on the Penguin arm (9) | one 7-tube there | none |
| MQ-9A, MQ-9 ER | two 7-tube on each outer launcher's Hellfire rail points; 7-tube inboard | one 7-tube under each outer pylon (`RedbackMQ9`, the centre of the author's Hellfire seat), the twin launchers hidden; 7-tube inboard | guidance pod, 1 channel |
| A-10A, A-10C, A-10C+ | unchanged | unchanged | none |
| AH-64A, Sea Apache AH-64NA | unchanged | unchanged | laser designator only |
| AH-64D, AH-64E, AH1, RAAF AH-64E | unchanged | unchanged | APG-78 |
| F-16CM, RAAF F/A-18A and F/A-18F, US F/A-18E/F/Block III | unchanged | unchanged | their radars |

With the round fire and forget, the last column no longer decides anything:
every carrier fires the same round on the same terms as the Hellfire L. The
carriers that had a channel lose the midcourse updates (and perhaps
retargeting); the nine that had none should now fire, and the RAN MH-60R
has (*Second report*).

The S-70B-2's Penguin hangs between the four Hellfire rails, 0.345 m apart.
The 19-tube pod's outer tubes alone are 0.48 m apart; the 7-tube pod's are
0.22 m, the Penguin's size. The S-70B-2 fit is provisional: the launcher
stays drawn, as in the author's Penguin fit, and the pod sits where the
Penguin does, centred at the height of the launcher's top rails. If the
loadout preview shows the launcher drawn around the pod, the two S-70B-2
rows come out of ROLLOUT before the next upload. Only the dispatch D7
fields an S-70B-2.

The MQ-9's two pods a side sat on the twin Hellfire launcher's rail points,
the arrangement the owner disliked on the Seahawk. The new mount is the
author's Hellfire height, centred under the pylon; the MQ-9 ER's own
AirToAir fit hangs its AIM-9X at that height on that pylon with the launcher
hidden. The MQ-9 now carries four pods, 28 rounds, not six and 42.

`tools/tests/test_redback.py` pins all of this: the round is
`MidCourseCorrection=0`; no carrier of the 21 needs a guidance channel it
lacks (a radio-command round would fail on the nine above); each MH-60R's
fit is its donor fit line for line (RAN AntiShip, US Navy
AntiShipLateLongRange) with only the four Hellfire lines (10-13) changed,
to `sest_agr-30_pod|RedbackM299`: eight pods and 56 rounds, the seat
exactly the Hellfire's lowered 0.04 m, the tanks on 1/2, the launcher drawn
and the Penguin arm hidden, and `RedbackH60` nowhere; the S-70B-2 carries
the 7-tube on the Penguin's station; and the MQ-9's pods hang on the
centred mount with the launchers hidden. The flight settings it pins are
under *Second report*.

## Not changed

- **The Super Hornets' twin 7-tube pods** (US F/A-18E, F and Block III, and
  the RAAF F/A-18F) hang ±0.41 m either side of a single mid pylon with no
  twin rack drawn: they float rather than sit in a rack. That is a separate
  fault, for the loadout preview to confirm before the mount is reworked.
- **The A-10A's Mavericks** on Stations 5/6 are the author's CAS fit's, drawn
  at the TER points; not a pod fault.
- **The employment gate.** `check_weapon_employment.py` still applies its
  guidance-channel rule to ship, submarine and land mounts only. Extending it
  to aircraft would also report other packs' fits (the A-10C+'s AIM-9X,
  datalink, on an aircraft without a radar; SEST Allied Fixes' P-8 Harpoon
  fit, radio command, with no linked sensor), which need their own look.

## Second report: it fires; the fit and the flight (23 October, later)

The owner, in the game (Sea Power 0.8.7) on `57375598`, the RAN MH-60R on
SEST Redback Strike:

- "the loadouts not good now. it has the agr where the fuel should be and
  the agm present and where the agr should be. swap agm for agr, no quad
  rack clipping issue. it fires";
- "agr doesnt boost as long anymore";
- "would like realistic slow down to cruise spped".

**It fires.** The MH-60R launched the AGR-30 from its 19-tube pods, so fire
and forget (`MidCourseCorrection=0`) was the fix, and it stays. The second
suspect above, an active-radar round inside a pod, is ruled out for the
LAU-3. The new fit hangs the 7-tube LAU-68 instead, which has not yet been
seen firing the active-radar round; it carried the infrared one on
18-19 Oct.

**The fit.** Both MH-60Rs fly their donor fit (RAN AntiShip, US Navy
AntiShipLateLongRange) with only the Hellfires changed:

- Stations 1/2: `usn_sh60_tank`, as the donor hangs them.
- Stations 10-13: `sest_agr-30_pod|RedbackM299` in place of each Hellfire
  line. The seat has two positions, so each line hangs two pods and the
  eight Hellfires become eight 7-tube pods, four a side, two on the upper
  rails and two on the lower: 56 rounds, a salvo of two per pod.
- `SubModelsToHide=H60_Pylon119`, the donor's: the Penguin arm hidden, the
  M299 launcher (`H60_Pylon114`) and the inboard pylon drawn.
- `RedbackM299Positions=0.002461,-0.0004,0|-0.002405,-0.0004,0`: the
  Hellfire's `TERAGM114` seat, at the same points side to side and fore and
  aft, lowered 0.04 m. The `RedbackH60` seat is gone.

Why the 7-tube: a side's four missile points on the launcher are 0.487 m
apart side to side and 0.389 m top to bottom (the same in all six files that
carry the M299). A LAU-68 (0.24 m across by its `FrontalArea`, perhaps up to
0.31 m in the game's mesh; 1.67 m long against the Hellfire's 1.63 m) fills
all four with 0.18-0.25 m between pods side to side and 0.08-0.15 m top to
bottom. A LAU-3 is 0.41 m across even at real size, more than the gap
between the upper and lower rails, so 19-tube pods cannot take all eight
places, and fewer of them sat in the bottom of the rack (`27153767`) or
floated (`d9755f4e`).

Why lowered: a Hellfire's top is about 0.09 m above its rail point, and a
LAU-68's would be 0.03-0.07 m higher on the same seat, into the rail.
Lowered 0.04 m, the pod's top is between 0.01 m below and 0.03 m above the
Hellfire's, inside the gap the rail's launch shoes leave. No mesh is in the
export, so these are estimates from the configs (the pods' frontal areas
and attachment points, the stock and Apache mod seats, the Penguin's and
the Hellfire's heights on the same airframe); the loadout preview decides,
and the seat's height is the one number to move. The inner pods also come
0.03-0.07 m closer to the launcher's centre than the Hellfires do. On the
same estimates each upper pod's bottom hangs 0.07-0.11 m lower than the
Hellfire's did, toward the lower rail: the seat leaves less room there than
the Hellfires had. If the upper pods clip the lower rails, the lower pair
comes out (Stations 12/13: the `usa_agm-114k_hh` swap to `None` in
ROLLOUT): four pods on the upper rails, 28 rounds.

Weight: the eight pods load 864 kg against the eight Hellfires' 379 kg. The
game sets no weight limit on a helicopter. Read in the 0.8.7 code (with
dnfile and dncil; nothing run), loadout mass changes the fuel burn (each
frame's range used is multiplied by 1 + loadout mass / empty mass: 1.125
with this fit, 1.055 with the Hellfires, so about 6% less range than the
AntiShip fit), the range and endurance the AI plans with, and the noise
sonar hears; not speed, climb, hover or handling. Firing does not lighten a
helicopter in the game. The game's gross weight with this fit, about
10.8 t, is about the real MH-60R's published maximum, or a little over.

Not changed: the S-70B-2s (one 7-tube in the Penguin's place; their fit
has no tanks or Hellfires, so the complaint cannot arise there) and the
MQ-9s. `57375598` moved the MQ-9's pods off its twin Hellfire launchers on
the reading that pods on Hellfire rails were what the owner disliked on the
Seahawk; this report shows it was the 19-tube pod in the bottom of the rack.
The MQ-9 fit stays as it is until the owner says otherwise.

**What the game does with these keys.** Read from Sea Power 0.8.7's code
on 23 Oct 2026, as the comment above the round's swaps in
`integration/allied-fixes/build_patch.py` records; with
`ApplyKinematics=False`, the game's simpler speed model:

- The flame is a timer. The sustainer effect shows from launch for
  `SustainerAccelerationTime`, ten seconds, whatever the round is doing.
  It has been ten seconds since 19 Oct.
- Each stage of the flight has a speed target: `MaxVelocity` while the round
  launches and turns onto its bearing, `MaxLoftVelocity` through the climb
  and the whole cruise, `TerminalVelocity` from `TerminalApproachDist` in.
  Above its target the round slows in a straight line, by `Deceleration`
  x 19.05 kt each second; below it the motor speeds it up by `Acceleration`
  x 22.9 kt each second, never past the target.
- Fired from an aircraft, the motor works only with `AccelerationTime=6`,
  the game's own default. The 19 Oct value, 0.01, gave no thrust at all, so
  the round kept roughly its launcher's speed.
- Terminal approach holds the height the round has (`TerminalAlt=Maintain`),
  and a round fired from inside `TerminalApproachDist` is in terminal
  approach from launch.

**Why the boost got shorter.** From the build the owner played before it
(`71bd3004`, the 19 Oct follow-up's round; the last recorded Workshop
upload, `e7b32f11` of 19 Oct, is older) to `57375598` two of the round's
keys changed: `MidCourseCorrection` 1 to 0 and `TerminalApproachDist` 2.0
to 8.0. The flame was the same ten-second timer on both. What went was the
climb: at 8 NM every shot from inside 8 NM began in terminal approach and
stayed at its launch height. `TerminalApproachDist` is 2.0 again,
`71bd3004`'s value. The climb to 2 km at 35 degrees covers about 1.5 NM
over the ground, so a shot from about 3.6 NM or more climbs all the way
before the approach starts; from nearer, the approach cuts the climb
short.

With no midcourse, the aim point is where the target was at launch, and the
seeker switches on 2 NM from it. The 120-degree gimbal then covers about
3.5 NM either side of that point (about 1.2 NM with the 60-degree field of
view alone). A boat that moves further than that during a long flight, such
as a 30-knot boat on a 25 NM shot, may not be found.

**The slow-down.** On those rules the old speed keys could not give what the
owner asked for. `MaxVelocity=150`, meant as the cruise, was the launch
target; `MaxLoftVelocity=450`, meant as a ceiling for the climb, was the
target for the climb and the whole cruise; and the motor gave an
aircraft-launched round no thrust. The keys now:

| Key | `71bd3004` and `57375598` | Now | What it sets |
|---|---|---|---|
| `MaxVelocity` | 150 | 450 | the run-up target as the round leaves the pod and turns |
| `MaxLoftVelocity` | 450 | 150 | the target through the climb and the cruise |
| `AccelerationTime` | 0.01 | 6 | the game's default: the motor works when an aircraft fires it |
| `Acceleration` | 2.0 | 12 | about 275 kt/s up toward a target |
| `Deceleration` | 0.8 | 0.25 | about 4.8 kt/s down toward a target |
| `TerminalApproachDist` | 2.0 / 8.0 NM | 2.0 NM | the 220 kt approach, at the height reached |
| `SustainerAccelerationTime` | 10 | 10 | the flame's ten seconds |
| `TerminalVelocity` | 220 | 220 | the approach's target |

So the round leaves the pod hard, running up toward 450 kt. Once it is on
its bearing it slows in a straight line, about 4.8 kt every second, toward
150 kt, while the flame burns its ten seconds and it climbs to 2 km: from
450 kt that takes about a minute (63 s). It cruises at 150 kt, picks up to
220 kt from 2 NM out at the height it has, and dives from 1.1 NM. How fast
it is when the run-up ends depends on how long the game's launch stages
last, which only the play test shows: at 275 kt/s the run-up from a
helicopter's 100 kt or so reaches 450 kt in about 1.3 s, so if those stages
are shorter the peak is lower and the slow-down shorter. A minute is about
as long as a 70 mm rocket coasting on drag alone would take to lose most of
that speed (an estimate, not a game figure), though drag slows a rocket
fastest at first and a straight line cannot follow it.

`tools/tests/test_redback.py` pins these settings, not the flight:
`MidCourseCorrection=0`, `ApplyKinematics=False`, `AccelerationTime` of
exactly 6, a `MaxVelocity` above `MaxLoftVelocity`, which is 150, a bleed
between the two of 30 to 120 s at 19.05 kt/s for each unit of
`Deceleration`, a `TerminalVelocity` above the cruise, the ten-second
flame, and `TerminalApproachDist` of 2.0, beyond the 1.1 NM dive and close
enough to leave the 2 km climb to a 4 NM shot. Nothing about the new fit or
the new flight has been seen in the game yet.

## In the game

Install the new build, then start **fresh** mission copies: a generated
campaign mission or a save keeps the old fit.

1. **Loadout preview, RAN MH-60R and US Navy MH-60R, SEST Redback Strike.**
   The tanks on the inner pylons (Stations 1/2), as in the AntiShip fit; on
   each M299 launcher four LAU-68 pods, two on the upper rails and two on
   the lower, where the AntiShip fit hangs its Hellfires; no Hellfire left;
   the Penguin arm hidden. Each pod's top should sit just under its rail,
   neither cutting into it nor hanging with a gap below. The upper pods'
   bottoms must clear the lower rails: the seat leaves less room there than
   the Hellfires did. Check on deck and after take-off. If the tops cut in
   or hang clear, say which and roughly by how much: the `RedbackM299`
   seat's height moves all eight. If the upper pods clip the lower rails,
   the lower pair comes out (Stations 12/13: the `usa_agm-114k_hh` swap to
   `None` in ROLLOUT): four pods, 28 rounds.
2. **It fires from the 7-tube pod.** SW03 Rig Seventeen: ready one of HMAS
   Canberra's MH-60Rs on SEST Redback Strike, launch it and, in forward
   flight, order an attack on the Peykaap or the Boghammar. A salvo of two
   should leave the pods. The round has left a Seahawk's 19-tube LAU-3
   (`57375598`) but has not yet been seen leaving its 7-tube LAU-68: if no
   salvo leaves, note it, the range and any message line.
3. **The flame.** About ten seconds from launch, on a short shot and a
   long one alike.
4. **The climb.** A shot from about 4 NM climbs to about 2 km before the
   approach: the climb that `57375598`'s 8 NM `TerminalApproachDist` took
   from every shot inside 8 NM.
5. **The speed.** Just after launch, note the highest speed the round
   reaches: it shows how long the game's launch stages last (450 kt, fired
   at about 100 kt, if they last about 1.3 s or more). Then it should slow
   steadily, with no sudden drop, to about 150 kt over roughly a minute
   (less from a lower peak), and cruise there. A shot from 8-15 NM shows it
   best; time the slow-down if you can.
6. **The approach and the dive.** About 2 NM from where the boat was at
   launch it picks up to about 220 kt at the height it has, then dives from
   1.1 NM, at roughly 45 degrees from 2 km.
7. **The other carriers that had no channel.** *SEST NF3 - Coastal Ambush*:
   the two A-10Cs on SEST Redback Strike fire it at the coastal battery and
   the launchers ashore. If one is to hand, an AH-64A or Sea Apache fires it
   at a boat.
8. **A long shot at a moving boat.** From 20-25 NM: the round climbs, slows
   to 150 kt and cruises, finds the boat after its seeker switches on 2 NM
   from where the boat was at launch, and dives. Record hit or miss: at 2 NM
   its gimbal covers about 3.5 NM either side of that point, which a fast
   boat can leave on a long shot. Then try to retarget a salvo in flight
   and note whether the game offers it.
9. **S-70B-2 and MQ-9 previews, before the next upload.** The S-70B-2's
   7-tube pod sits clear between the Hellfire rails where the Penguin does;
   if the launcher is drawn around it, the S-70B-2 rows come out. Each MQ-9
   shows one pod under each outer pylon, no Hellfire launcher, and a pod on
   each inner pylon (a change the owner did not ask for: two pods a side on
   the launcher's rails became one under the pylon, 28 rounds, not 42).

Copy `Player.log` straight after the session that tests 2 to 8.
