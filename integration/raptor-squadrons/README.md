# SEST Raptor Squadrons

Squadron definitions for misaka's **F-22** mod (Workshop item 3418252667).

## The problem

All three of the mod's squadron files say this:

```ini
NumberOfSquadrons=7

[Default]
Nation=US

[Squadron1]
Nation=US
```

Seven declared, one defined — and the language file names that one `F-22A`. Two consequences:

- **Every Raptor in the game is anonymous.** The unit reads "F-22A" whatever squadron it belongs to.
- **`SquadronReference=Squadron2..7` does not resolve.** Missions that asked for them (NORTHERN FRONT II
  wanted Squadron4–7 at one airbase) had aircraft spawning without a resolved squadron, which is why
  `integration/missions/fix_squadron_refs.py` had to fold them all back onto Squadron1.

## What this ships

Complete replacement squadron files for all three Raptor ids the mod carries
(`usaf_f-22`, `usaf_f-22_s5`, `usaf_f-22_s6`) with the type's seven real operating squadrons,
plus the matching `aircraft_names.ini` entries so the names and callsigns actually appear:

| # | Squadron | Wing / base |
|---|---|---|
| 1 | 27th FS 'Fighting Eagles' | 1st Fighter Wing, JB Langley-Eustis, Virginia |
| 2 | 94th FS 'Hat in the Ring' | 1st Fighter Wing, JB Langley-Eustis, Virginia |
| 3 | 90th FS 'Pair O Dice' | 3rd Wing, JB Elmendorf-Richardson, Alaska |
| 4 | 525th FS 'Bulldogs' | 3rd Wing, JB Elmendorf-Richardson, Alaska |
| 5 | 199th FS 'Mytai Fighters' | 154th Wing HI ANG, JB Pearl Harbor-Hickam |
| 6 | 19th FS 'Gamecocks' | 15th Wing, JB Pearl Harbor-Hickam, Hawaii |
| 7 | 43rd FS 'Hornets' | 325th Fighter Wing (training unit), Eglin AFB |

Language entries are written for `language_en` and `language_cn`; the Chinese file keeps its own
"猛禽" type callsign and Chinese descriptions, with only the squadron identities added.

## No new paint — read this before expecting new skins

The squadrons differ by **identity, nation flag and callsign, not by livery**, for a concrete reason:
the mod ships one texture set (`assets/models/aircraft/f22/textures/f-22_mat.ini`) and its model has
no decal submodels at all — the `#---------- Modex ----------` block in `usaf_f-22_s6.ini` is empty,
so `SerialnumberReferences=AF_Serial` points at nothing. Setting `ResourcesLiveryFolder` here would
aim the Raptor at some other aircraft's textures and break the skin, so it is deliberately left alone.

The callsigns (Talon, Ringer, Dice, Bulldog, Mytai, Gamecock, Stinger) are flavour derived from each
unit's nickname, not documented radio callsigns. The squadron names and basings are the real ones.

## Install

1. Copy `SEST_Raptor_Squadrons/` into `Sea Power_Data\StreamingAssets\`, or run
   `tools\install-sest-packs.ps1`, which now handles it.
2. In the Mod Manager it must sit **ABOVE the F-22 mod** — it carries full replacement copies of the
   three `*_squadrons.ini` files and the higher-listed mod wins the file.
   `data/load-order.tokens.txt` already places it there.

## Rebuilding after an upstream update

```bash
python3 integration/raptor-squadrons/build_patch.py
```

It refuses to build if the mod has started defining its own squadrons (so a real upstream fix is never
silently overwritten), or if a language section it needs to rewrite has gone missing.
