# Packaging, dependencies and recovery

Two questions this answers: how the SEST packs coexist with 142 workshop mods,
and what you actually need to be able to recover if the game install goes bad.

## A SEST pack is a patch, not a mod

The packs ship **121 files and every one is a `.ini`** — not a single model,
texture or asset bundle among them. Check it yourself:

```powershell
Get-ChildItem integration\*\SEST_* -Recurse -File | Group-Object Extension
```

That is deliberate: the repo stays small and every change is readable as a
diff. The consequence is that **no pack is standalone**. `SEST_F-15EX_Revamp`
ships `aircraft/usaf_f-15ex_SEII.ini` and nothing else — the geometry that file
describes lives in workshop mod 3636386513. Install the pack without the mod
and the game has a unit definition pointing at a mesh that is not there.

So there is no "package it up and hand it to someone" build. What there is
instead is a derived dependency list.

## What each pack needs

```powershell
python tools\check_dependencies.py
```

Two kinds, both computed from the files rather than hand-declared, so they
cannot drift:

| Kind | Meaning |
|---|---|
| `overrides` | The pack ships its own copy of a file that workshop mod provides. That mod supplies the model. |
| `references` | A loadout hangs a store, a roster names a unit, or a sensor or weapon entry names a system, defined in another mod entirely. |
| `SEST pack` | One pack depends on another — `SEST_RAAF_Bases` rosters aircraft that three other packs define. |

Anything vanilla already provides is not a dependency and is not listed. The
spread is wide: `SEST_TacMap_Colors` needs nothing but the base game;
`SEST_RAAF_Bases` references nine workshop mods on the 24 Sep 2026 export.
System names count because a sensor is a reference like any other: before they
did, `SEST_ADF_Persistent_ISR` was reported standalone although its Triton's
`AN/AAS-52_Visual` turret is defined only by the MQ-9 Reaper mod (`3503670861`).

The check exits non-zero if a pack needs something that is not exported and not
in the load order, or hangs a store, rosters a unit or names a system that
nothing defines, so it belongs in the same pre-flight run as the others. A
forked file that carries its upstream's own dead reference is listed instead of
failed, because it is equally broken with or without SEST: a store or system
name counts as inherited when an upstream unit file names it too, a roster only
when the upstream copy of the same file carries it. On the 24 Sep 2026 export
that list is eight system names on 28 forked unit files - `Hardpoint`,
`WingHardpoint`, `BombBay*` and `AircraftDefensiveECM` on aircraft, and the
Choules' `Aldebaran`, which came with the Galicia it is cloned from.

## Installing alongside other mods

Each pack installs as its **own folder** under `StreamingAssets`, exactly like a
workshop mod, and never writes into the game's own files. Sea Power's Mod
Manager lists them beside the workshop entries and they take part in the same
load order.

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\install-sest-packs.ps1 -WhatIfOnly   # dry run
powershell -ExecutionPolicy Bypass -File .\tools\install-sest-packs.ps1              # apply
# launch the game once, enable the SEST entries in the Mod Manager, quit
powershell -ExecutionPolicy Bypass -File .\tools\set-mod-order.ps1 -AddMissing
```

The installer **discovers** packs under `integration\` rather than working from
a list, so a new pack needs no edit anywhere to be picked up.

**The one rule that matters:** every SEST pack sits above every workshop mod.
A pack is a whole-file replacement, so anything that outranks it makes the patch
silently do nothing — no error, nothing in the log. `data/load-order.tokens.txt`
keeps them blocked at the top for exactly that reason, and
`tools/check_load_order.py` fails the build if one sinks. This is not
theoretical: `SEST_Growler_NGJ_MALICE` was inert for several sessions because
U.S. Navy 2027 moved up one tier and happened to jump over it.

## Retired packs

A pack is retired when the upstream mod adopts the fix. The patch then adds
nothing and costs something: an override is a whole-file replacement, so it
freezes everything *else* in that file at the version the pack was built
against, and it keeps a dependency alive for no gameplay reason. Git holds the
implementation if upstream ever regresses.

| Pack | Retired | Why |
|---|---|---|
| `SEST_Zumwalt_CPS` | 2026-09-20 | Modern US Navy fixed both defects it existed for. The duplicate `[WeaponSystem1]` is gone (the CPS hull now declares 1–23, each once, with a real `[WeaponSystem2]`), and the dangling `SensorSystem12` reference is gone with it. The LMVLS now carries no `AssociatedSensors` at all, which is correct here rather than a new bug: `usn_ircps` is `GuidanceType=0, MidCourseCorrection=0`, so it draws no guidance channel — the rule in `tools/check_weapon_employment.py` applies to MCC 1 and 3, not 0. |

## Removing them

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\install-sest-packs.ps1 -Uninstall
```

Deletes the pack folders and nothing else — workshop mods and game files are
untouched. Order entries for a removed pack are skipped with a warning by
`set-mod-order.ps1`, not an error, so a partial uninstall never wedges anything.

## Recovery — and why a game snapshot is the wrong tool

The packs are **generated**, not hand-made. Every one rebuilds from its
`build_patch.py` against the exported upstream files, so the recovery story for
them is a git pull and one command, not a restore.

What is genuinely at risk, and what covers it:

| At risk | Covered by | Cost to recover |
|---|---|---|
| SEST packs in `StreamingAssets` | this repo | `install-sest-packs.ps1`, seconds |
| Mod order in `usersettings.ini` | `set-mod-order.ps1` writes a timestamped `.bak_` every run, and the canonical order is in git | re-run the script |
| Missions edited in game | `import-mission.ps1` — **only once you have run it** | nothing, if you never imported |
| Workshop mod configs | `mods-source/` in git | re-export |
| Workshop mod binaries | Steam | re-subscribe |

A full game snapshot would duplicate the four rows that are already covered and
would not help with the one that is not. **The gap is missions you have edited
in the mission editor and not yet imported** — those live in the game's
`user_missions` folder, outside the repo, and nothing else has a copy.
`install-sest-packs.ps1` overwrites a mission there with the repo's copy of the
same name and keeps no backup (git is the history), so an edit that was not
imported first is gone after the next install. That is the thing worth being
disciplined about, and it is one command:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\refresh-mission.ps1
```

If you want belt-and-braces anyway, copy `user_missions` and
`usersettings.ini` — a few hundred KB — rather than imaging tens of GB of game
install you can re-download.

## The git loop

The repo is the source of truth for everything except Steam's own downloads.

**After Claude pushes work:**
```powershell
git pull
powershell -ExecutionPolicy Bypass -File .\tools\install-sest-packs.ps1
powershell -ExecutionPolicy Bypass -File .\tools\set-mod-order.ps1 -AddMissing
```

**After subscribing to or unsubscribing from anything:**
```powershell
powershell -ExecutionPolicy Bypass -File .\tools\export-mod-configs.ps1
git add -A mods-source
git commit -m "export: <what changed>"
git push
```
The export prunes mods you have unsubscribed and, inside each mod, files the
author has removed, so both show up as deletions — review them in `git status`
and commit them. Stale directories left behind were making conflict checks
report fights with mods that are not in the game any more; stale files inside a
mod did worse, because a unit the author had renamed kept resolving here while
the game could not find it.

Then check the export against its own manifest:

```powershell
python tools\check_inventory.py
```

It compares every `mods-source\<id>\` with the file count and byte total the
exporter recorded for that mod in `_export-manifest.csv`, and checks that the
manifest, the folders, the installed catalog entries and the load order all name
the same Workshop ids. A folder holding more than its manifest row is a file the
mod no longer ships; nothing else in the repo can see one.

### Known red: `check_inventory` until the first mirrored export is committed

`check_inventory.py` exits 1 on this branch, and is expected to until the gaming
PC runs the mirroring exporter and the deletions are committed. On the 24 Sep
2026 export it fails 17 mods, for two reasons.

**Ghost files (13 mods, 203 files over their manifests).** Every export before
the mirror was an overlay, so a file an author deleted or renamed stayed behind
and kept resolving. 171 files here are missing from the mirrored 20 Sep export
on the `sest-dev/kind-faraday` line and untouched by any export since, and they
account for most of the surplus: Modern US Navy (`3390330875`) 37 of 56, Italian
Navy (`3505420313`) 64 of 65, Euromod (`3629144864`) 42 of 45, U.S. Navy 2027
(`3606774881`) 8 of 12, Euromod JMSDF (`3695809489`) 5 of 6, US Naval Aviation
(`3737267013`) 4 of 5, Modern British Navy (`3599752717`) 1 of 2, and all of it
in the Dutch Navy (`3444379330`), French Navy (`3567256221`), F-35C Alt.
Loadouts (`3607989779`) and Spanish Navy Modern (`3731208477`) mods. The other
32, one each in Modern Italian Navy (`3488139470`) and Anchor Chain
(`3784474738`) among them, cannot be named from git: the 20 Sep mirror still
had them, or an export after it wrote them, and the 24 Sep manifest no longer
counts them. Only the mirror can name those.

Of the 171, one reached a campaign: Southern Watch 11 placed USS Jack H. Lucas
as `usn_ddg_burke_f2a_g4_2022`, a Modern US Navy Flight IIA group file that was
gone by 20 Sep. She now sails as `usn_ddg_burke_f3_125` Variant1, her own
Flight III hull. One more is a round: `usn_rim-162e` (ESSM Block II) exists
only as a U.S. Navy 2027 ghost, yet that mod's eighteen 2027 Burkes still load
it into a Mk 41 magazine every fit carries and its 2027 Nimitz into both SAM
launchers, so in game those are empty - on Southern Watch 11's second Burke,
and on the 2027 hulls in the NORTHERN FRONT II and III saves, the NF3 Boomer
Hunt and Carrier Duel scenarios, DARWIN US SUPPLY and four SULU SEA OFFENSIVE
cuts. That is upstream's to fix, not a reference either campaign can move, and
`check_alias_bases.py` will report it as MISSING AMMO once the ghost is
deleted. The other ghosts that missions or packs reach (`usn_rim-162a`,
`usn_rim-66m-2`, `usn_rim-66m-5`, `usn_rim-116c`, the two sonobuoys,
`usn_agm-65b`, `usn_agm-65d`, `fr_am-39_Block2`) still resolve once deleted,
through another mod's or the base game's copy of the same id, which is the one
the game already loads.

**Line endings (4 mods: same file count, fewer bytes).** PLAN Pack
(`3775128499`), Ka-31 (`3776340577`), Tu-214R (`3780118683`) and E-3G
(`3781062859`) hold files committed on 25 Aug with their CRs stripped, the day
before `mods-source/` was pinned `-text`; the manifest measures the CRLF
originals. The mirrored 20 Sep export did not change those blobs either, so a
mirrored export may leave these four red. If it does, run
`git add --renormalize mods-source/<id>` for each and check
`git diff --cached --stat` shows only those folders before committing.

If the working export itself is suspect, take a clean one beside it. The
destination is new and empty, so there is nothing for an overlay to leave
behind, and the checkout's `mods-source` is not touched:

```powershell
$fresh = Join-Path $env:TEMP ('Seapower-clean-' + [guid]::NewGuid().ToString('N'))
powershell -ExecutionPolicy Bypass -File .\tools\export-mod-configs.ps1 -DestDir $fresh
if ($LASTEXITCODE -ne 0) { throw 'Export failed; do not use it.' }
```

It carries its own `_export-manifest.csv`, so `check_inventory.py --root` can
audit it from a scratch copy of the repo whose `mods-source` has been replaced
by it (keep `_vanilla`). If it passes there, it is the export to commit.

**After editing a mission in game:** run `refresh-mission.ps1`, then commit.

PowerShell 5.1 has no `&&`. Chain with `;` or use separate lines.

## Pre-flight

Six checks, all offline, all exit non-zero on failure. Run them after any
subscribe, unsubscribe or reorder, and after the export's `check_inventory.py`
above:

```powershell
python tools\check_load_order.py       # no mod outranks a SEST pack
python tools\check_dependencies.py     # every pack's upstream is present
python tools\preflight.py              # every reference the mission makes resolves
python tools\check_scenarios.py        # carved NF3 scenarios: counts, formations, section numbers
python tools\check_station_clash.py 0.001   # nothing mounted on top of anything
python tools\check_weapon_employment.py     # every weapon can actually be fired
```

The last one asks a different question from `preflight`. Preflight checks that
a reference resolves; this checks that the mount can satisfy what the round
needs — the gap the RAN NSMs fell through, where every id resolved and the
launcher still never fired.

`preflight.py` resolves ids against `mods-source`, so it cannot see either kind
of export drift on its own. A mod missing from the export looks like a typo;
when that is the cause, it names the mods the catalog calls installed but the
export does not hold. A ghost file looks like a working unit, which is what
`check_inventory.py` is for.
