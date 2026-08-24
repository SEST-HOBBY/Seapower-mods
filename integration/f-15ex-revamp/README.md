# SEST F-15EX Revamp

Loadout expansion patch for dingtools' **F-15 EX Eagle II** (Workshop item 3636386513, internally
"F-15SE"), built and validated against the exported mod configs in `mods-source/`.

## What upstream already had

The stock mod ships 14 loadouts, including a 12+ AMRAAM missile truck (`AAMT120`), an AIM-260
intercept fit, JSOW/SDB/JASSM-ER strike fits, a 4× LRASM `AntiShip`, and ARRW hypersonics — so
this patch adds only what's genuinely missing, all cross-mod:

## The four new loadouts

| Loadout | In-game name | Stores | Extra dependency |
|---|---|---|---|
| `AntiShipHeavy` | AntiShipLRASM6 | **6× AGM-158C-3 LRASM** (surge fit, mirrors the JSOW 6-station pattern) + 2× AIM-120D-3 + 2× AIM-9X + tank + pods | none beyond upstream |
| `AntiShipHarpoon` | AntiShipHarpoon | **4× AGM-84D Harpoon** (vanilla weapon) + 2× AIM-120D-3 + 2× AIM-9X + tank + pods | none — vanilla Harpoon |
| `Quicksink` | StrikeQuicksink | **4× GBU-31 anti-ship JDAM** + 2× AIM-120D-3 + 2× AIM-9X + tank + pods | Dingtools Weapon Pack (`dts_gbu-31`) |
| `BigStick174` | Intercept174 | **6× AIM-174B** (CFT corners, aft fuselage, wing) + 2× AIM-120D-3 + 2× AIM-9X + tank — flagged what-if | **Murder Hornet** (`usn_aim-174b`) |
| `BigStick174ER` | Intercept174 LongRange | **4× AIM-174B** (fuselage) + 3× 610 gal tanks (centreline + both wing stations) + 2× AIM-120D-3 and 2× AIM-9X on the inner-pylon shoulder rails — outer wing pylons removed entirely | **Murder Hornet** (`usn_aim-174b`) |
| `Truck174` | Intercept174 Truck (8×) | **8× AIM-174B** (4 fuselage + 4 on the inner-pylon shoulder rails) + centreline tank only | **Murder Hornet** (`usn_aim-174b`) |
| `Malice6` | InterceptMALICE (6× AIM-424) | **6× AIM-424 MALICE** in the BigStick174 layout + 2× AIM-120D-3 + 2× AIM-9X + tank | **US Naval Aviation** (AGM-88G model) |
| `MaliceER` | InterceptMALICE LongRange | **4× AIM-424** (fuselage) + 3 tanks + inboard AAMs — mirrors BigStick174ER | **US Naval Aviation** (AGM-88G model) |
| `MaliceTruck` | InterceptMALICE Truck (8×) | **8× AIM-424** + centreline tank — mirrors Truck174 | **US Naval Aviation** (AGM-88G model) |

The AIM-424 MALICE itself ships inside this pack (`ammunition/sest_aim-424.ini`, identical
copies in the two F-35 JATM packs): AARGM-ER airframe, AIM-174B-class reach, passive
anti-emitter mode.

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
