# SEST F-15EX Revamp

Loadout expansion patch for dingtools' **F-15 EX Eagle II** (Workshop item 3636386513, internally
"F-15SE"), built and validated against the exported mod configs in `mods-source/`.

## What upstream already had

The stock mod ships 14 loadouts, including a 12+ AMRAAM missile truck (`AAMT120`), an AIM-260
intercept fit, JSOW/SDB/JASSM-ER strike fits, a 4× LRASM `AntiShip`, and ARRW hypersonics — so
this patch adds only what's genuinely missing, all cross-mod (the Harpoon fit was
dropped - LRASM and Quicksink cover anti-ship far better and the AGM-84 added nothing):

## The new loadouts

| Loadout | In-game name | Stores | Extra dependency |
|---|---|---|---|
| `AntiShipHeavy` | AntiShipLRASM6 | **6× AGM-158C-3 LRASM** (surge fit, mirrors the JSOW 6-station pattern) + 2× AIM-120D-3 + 2× AIM-9X + tank + pods | none beyond upstream |
| `Quicksink` | StrikeQuicksink | **4× GBU-31 anti-ship JDAM** + 2× AIM-120D-3 + 2× AIM-9X + tank + pods | Dingtools Weapon Pack (`dts_gbu-31`) |
| `Malice6` | InterceptMALICE (6× AIM-424) | **6× AIM-424 MALICE** (4 fuselage + 2 wing stations) + 2× AIM-120D-3 + 2× AIM-9X + tank | **US Naval Aviation** (AGM-88G model) |
| `MaliceER` | InterceptMALICE LongRange | **4× AIM-424** (fuselage) + 3× 610 gal tanks + inboard AAMs + 4× AIM-260 on the inner-pylon rails | **US Naval Aviation** (AGM-88G model) |
| `MaliceTruck` | InterceptMALICE Truck (8×) | **8× AIM-424** (4 fuselage + 4 on the inner-pylon shoulder rails) + centreline tank | **US Naval Aviation** (AGM-88G model) |

The AIM-424 MALICE itself ships inside this pack (`ammunition/sest_aim-424.ini`, byte-identical
copies in the two F-35 JATM packs, the F-16CM pack, the Rafale pack and the Growler pack). It is
the Raytheon AIM-424 LRAAM the US Navy revealed at Tailhook on **22 August 2026**, already in
flight test. The Navy fact file gives 4.11 m long, the **same 34.3 cm diameter as the SM-6**,
**680 kg (1,500 lb)**, a solid-propellant rocket motor, a blast-fragmentation warhead and a range
**"in excess of 250 nm"**.

It is aligned key-for-key against U.S. Navy 2027's AIM-174B so the two encyclopedia cards compare
directly — same explicit-drag flight model, same 150,000 ft loft, same fragmentation warhead class,
same datalink midcourse, same chart basis. That alignment is now more than convenience: the two
share a diameter, a mission and a service. It reaches **290 nm** against the 174B's 316 — over
the Navy's stated floor, just under its stablemate — and carries a far better seeker: 40 nm active
and 80 nm passive against 15/15, plus a full passive anti-emitter mode that homes on radars as well
as jammers, which is what makes it an AEW- and tanker-killer.

The seeker figures are estimates; the Navy disclosed none. The 3D model is a stand-in on US Naval
Aviation's AGM-88G assets. That mod also ships an AIM-424 mesh for its own `usn_aim-424`, but the
AGM-88G block is the one proven to load here, so switching waits for an in-game look.
`integration/common/aim424.py` shows the source or the reasoning behind every key.

## Install

1. Copy `SEST_F-15EX_Revamp/` into Sea Power's `Sea Power_Data\StreamingAssets\` folder
   (next to `original` and `user`).
2. In the in-game Mod Manager, place **SEST F-15EX Revamp ABOVE the F-15EX mod** (the patch
   carries a full modified copy of `aircraft/usaf_f-15ex_SEII.ini`, and the higher-listed mod
   wins the file). Keep Dingtools Weapon Pack above everything of dingtools' as usual.
3. If the Mod Manager doesn't list local StreamingAssets folders on your build, fall back to
   merging the patch's `aircraft/` and `language_*/` folders into `StreamingAssets\user\`
   (the always-loaded user-data layer).

The three anti-ship loadouts keep the AAQ-33/AAQ-13 targeting pods and a centreline 610 gal tank,
matching upstream's strike-fit conventions; `Malice6` is a clean air-to-air fit with pods hidden.

The three AIM-174B "Gunslinger" fits this pack used to add — `BigStick174`, `BigStick174ER` and
`Truck174` — were **removed at the user's request**. The MALICE fits carry the same three layouts
on the AIM-424, so nothing in the pack needs Murder Hornet any more.

## Rebuilding after an upstream update

The patch is generated, not hand-maintained: `build_patch.py` reads the original mod out of
`mods-source/3636386513/`, injects the new loadouts, and validates every ammunition id and
position key against the exported ecosystem (F-15EX mod, weapon pack, US Naval Aviation, vanilla).
When dingtools updates his mod, re-export `mods-source/` and re-run:

```bash
python3 integration/f-15ex-revamp/build_patch.py
```

It fails loudly (rather than building something broken) if upstream renamed a loadout key,
moved the injection point, or changed weapon ids.

Two more long-range missile-truck fits trade the wing twin-racks for fuel:

| Loadout | In-game name | Stores | Extra dependency |
|---|---|---|---|
| `AAMT120Tanks` | AAMT120 LongRange (3 tanks) | **16× AIM-120D-3** (8 rails + 8 on the fuselage twin racks) + three 610 gal tanks | Dingtools Weapon Pack |
| `AAMT260Tanks` | AAMT260 LongRange (3 tanks) | **16× AIM-260** in the same layout + three 610 gal tanks | Dingtools Weapon Pack |

`MaliceER` and `MaliceTruck` also carry 4× AIM-260 on the inner wing pylon rails.
`Malice6` does not: its wing stations carry underslung AIM-424, and the rail rule below
clears the rails under a store that wide.


## Squadrons

Upstream defines two — the 44th and 67th FS at Kadena, each with its own livery. A mission that
wanted more than two distinct F-15EX units had nothing to reference, so this pack ships a complete
replacement `aircraft/usaf_f-15ex_SEII_squadrons.ini` with eight:

| # | Squadron | Wing / base |
|---|---|---|
| 1 | 44th FS 'Vampires' | 18th Wing, Kadena AB, Japan |
| 2 | 67th FS 'Fighting Cocks' | 18th Wing, Kadena AB, Japan |
| 3 | 85th TES | 53rd Wing, Eglin AFB — first F-15EX operator |
| 4 | 40th FLTS | 96th Test Wing, Eglin AFB |
| 5 | 123rd FS 'Redhawks' | 142nd Wing OR ANG, Portland — first ANG F-15EX unit |
| 6 | 194th FS 'Griffins' | 144th FW CA ANG, Fresno |
| 7 | 131st FS | 104th FW MA ANG, Barnes |
| 8 | 114th FS 'Eagles' | 173rd FW OR ANG, Kingsley Field |

Squadrons 1 and 2 stay byte-identical to upstream's — the build fails if upstream's liveries change
underneath them — so nothing that already references Squadron1/2 shifts paint. The mod carries only
those two skins, so the six added units reuse them in rotation and differ by identity and callsign
rather than by appearance. Upstream's English and Chinese names and callsigns for the two Kadena
squadrons are kept verbatim; only the new units are appended.

Callsigns for the added units (Bench, Probe, Redhawk, Griffin, Minuteman, Talon) are flavour, not
documented radio callsigns. The squadron designations and basings are real.

SEST RAAF Bases uses all eight: a full two-squadron wing at Amberley plus single-squadron dets at
Tindal, Darwin, Scherger, Townsville, Curtin and Williamtown.


## Symmetry fixes

An aircraft hangs stores in mirrored pairs, and two upstream defects broke that.

**`AirToAirIntercept` carried one Sidewinder.** Station9 (right outer wing pylon) had
`dts_aim-260_w|120` while Station10 (left outer wing pylon) had `dts_aim-9x` — visibly different
missiles on the same pair of pylons. Every other fit in the mod pairs those stations correctly:

| Loadout | S9 (right) | S10 (left) |
|---|---|---|
| Default, AirToAir | AIM-9X | AIM-9X |
| AirToAirLongRange, AAMT120 | AIM-120D-3 | AIM-120D-3 |
| AAMT260 | AIM-260 | AIM-260 |
| **AirToAirIntercept** | **AIM-260** | **AIM-9X** ← the only mismatch |

It was also the only fit carrying an odd number of Sidewinders: exactly one, on the left wing.

Station10 is the stale half rather than Station9 — it reads plain `dts_aim-9x` with no position
key, which is the Default/AirToAir pattern, while every other wing-rail missile in that loadout
carries the `|120` rail offset. So Station10 is matched to Station9, which also makes the fit a
clean **12× AIM-260** (was 11× + 1× AIM-9X). If you would rather keep a short-range pair, flipping
it the other way is a one-line change in `SYMMETRY_FIXES`.

**Stations 2, 3 and 4 all sat at the identical point** `x=+0.0486` — "Right Wing pylon outer" plus
*two* "Right Wing pylon bottom", with no left-hand pylon-bottom station at all. Anything mounted on
3 and 4 would stack on the right wing with nothing opposite. Nothing in WeaponSystem1 uses them, so
this was a latent trap rather than a live bug; Station4 is now mirrored to the left so the pair is
usable. The remaining oddity — that "pylon bottom" still shares a point with "pylon outer" on each
side — is upstream's geometry, and correcting it would mean inventing a vertical offset that can't
be verified from the model, so it is deliberately left alone.

The build now **fails** if any loadout hangs mismatched stores on a mirror pair. Two pairs are
exempt, with reasons: stations 26/27 are two different pods (AAQ-33 targeting, AAQ-13 navigation) on
mounts at slightly different heights, and `StrikeNuke`'s single B61 on one wing station is
upstream's deliberate choice.

Note the check is done **per weapon system**. Each `[WeaponSystemN] #Hardpoint` block owns its own
station table, and a loadout named `[WeaponSystemN<Name>]` indexes into *that* table — conflating
them produces a page of false positives, because Station3 means "right wing pylon bottom" in
WeaponSystem1 and "right bottom aft" in WeaponSystem2.


## The AIM-260 hangs low from its own origin

Reported in game: the JATMs sit wrong on almost every fit here. They ride `|120`, the AMRAAM
rail seat — and the AMRAAMs on that same seat look right, so the round is the variable.

The collection had already solved this on another airframe. Both F-35 JATM packs give
`dts_aim-260` its **own** seat key instead of sharing the AMRAAM's, converged over four
tuning passes against screenshots (`docs/interoperability-report.md`): *"correcting the
low/aft hang the user screenshotted on the RAAF F-35A beast fit"* → *"First guess overshot -
missiles clipped into the pylons. Halved the vertical offset (~17cm up from the model
origin)"* → *"Vertical is flush at 0.0025"*. On the F-35 the AMRAAM on those same stations
carries no key at all, so **+0.0025 is the gap between where the two meshes hang from one
origin** — a property of `dts_aim-260.obj`, not of an F-35 pylon. Both pylon pairs needed the
identical `y` while their `z` differed, which is what a mesh correction looks like.

So every AIM-260 on this airframe now rides its own copy of whatever seat it used to share,
lifted 0.0025. Ten keys, generated from the base seats rather than typed, so retuning a base
seat carries into its JATM twin automatically:

| JATM seat | copied from | used by |
|---|---|---|
| `AAM260` | `120` wing rail | every rail fit — the seat the report is about |
| `AAM260B` | bare station | the fuselage rounds that carried no key |
| `AAM260MTH` / `AAM260MTW` | upstream's belly / wing racks | `AAMT260` |
| `AAM260-OR/OL/FR/FL/AR/AL` | this pack's `SESTR-*` slot seats | `AAMT260Tanks` |

Nothing else moves: AMRAAM, AIM-9X and AIM-424 keep the seats they already had.

**Scope, stated plainly.** The `|120` rail is the case the report is about and the one the
F-35 evidence transfers to directly. The rack seats get the same lift on the same reasoning —
the droop belongs to the mesh, so it applies wherever the round hangs — but that half is
inference, not a screenshot. If the belly rack rounds come back sitting proud of their slots,
name those seats in `JATM_SEATS_EXEMPT` in `build_patch.py` and they keep upstream's shared
geometry; the rails stay fixed either way.

## Side-rail height

Stations 1/2/5/6 are the side-attach rails on the inner wing pylon — the ones carrying AIM-260
above the fuel tank. **All four are identical in every loadout**: same y, same `|120` key, net
`-0.00050`. They cannot sit at different heights from each other.

The only measurable height difference among wing-mounted AAMs is between the two groups:

| Group | Stations | net y |
|---|---|---|
| side rails | 1/2/5/6 | −0.00050 |
| outer pylon | 7/8/9/10 | −0.00120 |

`SIDE_RAIL_DROP` lowers the side rails by **0.0007** so both groups sit level. That is the whole
change — it removes the one real discrepancy and nothing more.

**An earlier attempt dropped them 0.005** on the reasoning that they sat above the wing station
(−0.0063) where the tank pylon attaches. That was an inference about the model rather than a
measurement, and it was wrong in kind: the report was that *one missile sat higher than the others*
— a relative difference — not that the whole group was too high. Dropping further is guesswork
until someone who can see the model says otherwise.

The build asserts both wings move together, that all four finish at the same height, and that they
never reach the wing station.

The rotations were checked and left alone. `0,0,±90` on paired flanking rails is the dominant
convention across the collection (F/A-18E/F, A-10C, Mi-8, F-104, Tornado IDS), and `plan_j-15a`
uses byte-identical values — `S1+S5 = 0,0,90`, `S2+S6 = 0,0,-90`. Only the Tornado ADV rolls such
pairs oppositely.
