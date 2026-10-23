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
a condition the game checks at launch. Both faults are fixed at the source
in the build after `f13e38cc`. Neither fix has been seen in the game yet;
the checks at the end decide it.

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
   (`GuidanceType=1`), which flew from both pods.
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
| now | the inboard pylon's tank point (Stations 1/2), raised 0.13 m (`RedbackH60`) | to be checked |

Every SH-60 file in the collection (nine of them, from six mods) hangs its
tanks on Stations 1/2 and its torpedoes on 3/4, on the inboard pylon,
whichever outboard arm is drawn. The pod takes the tank's point, raised
to the rack. The tank is far fatter than a LAU-3, and its point is 0.22 m
below the torpedo's on the same rack, so a pod hung there bare would hang
about 0.1 m clear of the rack: the "pods float" of 19 Oct again. SEST's
`RedbackH60` mount raises it 0.13 m, to 0.09 m below the torpedo's point,
which is about the LAU-3's radius less the Mk 54's (the stock AH-1T and
F-5A and the Apache mod seat a LAU-3 0.10-0.13 m lower than a LAU-68 or a
Mk 82 on the same pylon). The pod's top should then meet the rack where
the torpedo's does. No mesh is in the export, so this is an estimate for
the loadout preview to confirm. On the real MH-60R, 70 mm pods hang from a
BRU-14 rack, not under an M299.

## What changed

**The round, on every carrier.** `sest_agr-30` is fire and forget:

| Key | 19 Oct follow-up | Now |
|---|---|---|
| `MidCourseCorrection` | 1, radio command | 0, the donor's own |
| `TerminalApproachDist` | 2.0 NM | 8.0 NM |

`Retargetable=True` stays. Six of the collection's `MidCourseCorrection=0`
rounds set it (the ROK Hyunmoo-4-2 and HGV are active radar, like this one),
but the stock game pairs it only with radio command (Walleye II), so whether
a Redback can still be retargeted in flight without a command link is for
the game to show.

Nothing updates the round in flight now, so its seeker has to find a target
that has moved since launch. It switches on 8 NM from where the target was
at launch, as the SS-N-22B's does on the same guidance, and its 120-degree
gimbal covers a boat that moved a few miles during a long flight. The dive
still starts at 1.1 NM. The 220-knot terminal speed target may now apply
from 8 NM rather than 2; the game shows which. Everything else is as on
19 Oct: Ka-band, 11 kW, 35 NM seeker, 30 NM launch, the ten-second motor,
the 2 km loft and the 150-knot cruise.

**The fits.** Built by `integration/allied-fixes/build_patch.py` (ROLLOUT)
through `integration/common/redback.py`:

| Carrier | Before | Now | Channel for radio command |
|---|---|---|---|
| RAN MH-60R (`ran_mh-60r`) | tanks on 1/2; a 19-tube on each lower Hellfire rail point (12/13), launcher drawn | a 19-tube on each inboard pylon (1/2, the tanks' point, raised 0.13 m on `RedbackH60`); the launcher's eight Hellfires (10-13), as the AntiShip fit hangs them | none |
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
retargeting); the nine that had none should now fire.

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
`MidCourseCorrection=0`, its seeker switches on
inside its reach and before the dive, no carrier of the 21 needs a guidance
channel it lacks (a radio-command round would fail on the nine above), the
MH-60R's pods are on Stations 1/2 on a station and hide pair an author's
fit already uses, raised toward the torpedo's point and not past it, its
Hellfires stay on the drawn launcher, the S-70B-2 carries the 7-tube on
the Penguin's station, and the MQ-9's pods hang on the centred mount with
the launchers hidden.

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

## In the game

Install the new build, then start **fresh** mission copies: a generated
campaign mission or a save keeps the old fit.

1. **Loadout preview, RAN MH-60R and US Navy MH-60R, SEST Redback Strike.**
   One LAU-3 on each inboard pylon where the tank hangs in the Ferry fit;
   the M299 launcher outboard with its eight Hellfires and no pod in it; the
   Penguin arm hidden. The right pod sits about a metre further aft than the
   left, as the right tank does. The pod's top should meet the rack where
   the Mk 54's does in the ASW fit. Check on deck and after take-off. If
   the pod's top cuts into the pylon or hangs clear of it, say which and
   roughly by how much: the `RedbackH60` mount moves it.
2. **The shot that failed.** SW03 Rig Seventeen: ready one of HMAS
   Canberra's MH-60Rs on SEST Redback Strike, launch it and order an attack
   on the Peykaap or the Boghammar, first inside 4 NM, then at 8-15 NM,
   hovering and in forward flight. Expect a salvo of two from the pods. Note
   any message line if it still does not fire.
3. **The other carriers that had no channel.** *SEST NF3 - Coastal Ambush*:
   the two A-10Cs on SEST Redback Strike fire it at the coastal battery and
   the launchers ashore. If one is to hand, an AH-64A or Sea Apache fires it
   at a boat.
4. **A long shot at a moving boat.** From 20-25 NM: the round lofts, cruises,
   finds the boat after its seeker switches on 8 NM out, and dives. Record
   hit or miss and whether the terminal speed rises from 8 NM or only in the
   dive. Then try to retarget a salvo in flight and note whether the game
   offers it.
5. **S-70B-2 and MQ-9 previews, before the next upload.** The S-70B-2's
   7-tube pod sits clear between the Hellfire rails where the Penguin does;
   if the launcher is drawn around it, the S-70B-2 rows come out. Each MQ-9
   shows one pod under each outer pylon, no Hellfire launcher, and a pod on
   each inner pylon (a change the owner did not ask for: two pods a side on
   the launcher's rails became one under the pylon, 28 rounds, not 42).
6. **If the Seahawk still does not fire,** the pod's active-radar round is
   the remaining suspect: say so, and the round goes back to the infrared
   seeker that flew from both pods on 18-19 Oct.

Copy `Player.log` straight after the session that tests 2 and 3.
