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
| `BigStick174` | Intercept174 | **6× AIM-174B** + **4× AIM-260** on the inner wing pylon rails + 2× AIM-120D-3 + 2× AIM-9X + tank | **Murder Hornet** (`usn_aim-174b`) |
| `BigStick174ER` | Intercept174 LongRange | **4× AIM-174B** (fuselage) + 3× 610 gal tanks (centreline + both wing stations) + 2× AIM-120D-3 and 2× AIM-9X on the inner-pylon shoulder rails — outer wing pylons removed entirely | **Murder Hornet** (`usn_aim-174b`) |
| `Truck174` | Intercept174 Truck (8×) | **8× AIM-174B** (4 fuselage + 4 on the inner-pylon shoulder rails) + centreline tank only | **Murder Hornet** (`usn_aim-174b`) |
| `Malice6` | InterceptMALICE (6× AIM-424) | **6× AIM-424 MALICE** in the BigStick174 layout + 2× AIM-120D-3 + 2× AIM-9X + tank | **US Naval Aviation** (AGM-88G model) |
| `MaliceER` | InterceptMALICE LongRange | **4× AIM-424** (fuselage) + 3 tanks + inboard AAMs — mirrors BigStick174ER | **US Naval Aviation** (AGM-88G model) |
| `MaliceTruck` | InterceptMALICE Truck (8×) | **8× AIM-424** + centreline tank — mirrors Truck174 | **US Naval Aviation** (AGM-88G model) |

The AIM-424 MALICE itself ships inside this pack (`ammunition/sest_aim-424.ini`, byte-identical
copies in the two F-35 JATM packs and the Growler pack): AARGM-ER airframe, aligned key-for-key
against U.S. Navy 2027's AIM-174B so the two encyclopedia cards compare directly — same
explicit-drag flight model, same 150,000 ft loft, same fragmentation warhead class, same datalink
midcourse, same chart basis. It reaches 290 nm against the 174B's 316 (it has to fit an F-35 bay)
and buys that back with a far better seeker: 40 nm active and 80 nm passive against 15/15, plus a
full passive anti-emitter mode that homes on radars as well as jammers.

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
matching upstream's strike-fit conventions; `BigStick174` is a clean air-to-air fit with pods hidden.

## Rebuilding after an upstream update

The patch is generated, not hand-maintained: `build_patch.py` reads the original mod out of
`mods-source/3636386513/`, injects the new loadouts, and validates every ammunition id and
position key against the exported ecosystem (F-15EX mod, weapon pack, Murder Hornet, vanilla).
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

`BigStick174`, `BigStick174ER` and both MALICE mirrors also carry 4× AIM-260 on the
inner wing pylon rails, which those fits previously left empty.


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
