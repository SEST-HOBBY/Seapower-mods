# Packaging, dependencies and recovery

Two questions this answers: how the SEST packs coexist with 132 workshop mods,
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
| `references` | A loadout hangs a store, or a roster names a unit, defined in another mod entirely. |
| `SEST pack` | One pack depends on another — `SEST_RAAF_Bases` rosters aircraft that three other packs define. |

Anything vanilla already provides is not a dependency and is not listed. The
spread is wide: `SEST_TacMap_Colors` needs nothing but the base game;
`SEST_RAAF_Bases` needs thirteen workshop mods and three sibling packs.

The check exits non-zero if a pack needs something that is not exported and not
in the load order, so it belongs in the same pre-flight run as the others.

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
`user_missions` folder, outside the repo, and nothing else has a copy. That is
the thing worth being disciplined about, and it is one command:

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
The export prunes mods you have unsubscribed, so those show up as deletions —
commit them. Stale directories left behind were making conflict checks report
fights with mods that are not in the game any more.

**After editing a mission in game:** run `refresh-mission.ps1`, then commit.

PowerShell 5.1 has no `&&`. Chain with `;` or use separate lines.

## Pre-flight

Four checks, all offline, all exit non-zero on failure. Run them after any
subscribe, unsubscribe or reorder:

```powershell
python tools\check_load_order.py       # no mod outranks a SEST pack
python tools\check_dependencies.py     # every pack's upstream is present
python tools\preflight.py              # every reference the mission makes resolves
python tools\check_station_clash.py 0.001   # nothing mounted on top of anything
```
