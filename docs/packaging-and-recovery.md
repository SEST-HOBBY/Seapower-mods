# Packaging, dependencies and recovery

> **Branches since 11 November 2026** (docs/BRANCHES.md): the PC installs and tests `beta`, which `data/deploy-branch.txt` names; work merges into `dev` by pull request; `steam` is what is live on the Workshop. Where this guide names `sest-dev/jolly-ride-rptj4t` for a pull or install, use `beta`; push changes to a feature branch and open a pull request into `dev` instead of pushing to it.

Two questions this answers: how the SEST packs coexist with 195 workshop mods
(196 Mod Manager entries with `SEST_Integration`), and what you actually need
to be able to recover if the game install goes bad.

## A SEST pack is a patch, not a mod

The patch packs ship **nothing but `.ini` files** — not a single model,
texture or asset bundle among them — with one exception: SEST RAAF F-35A JATM
carries the RAAF F-35A's own model, textures and livery, because its Workshop
mod was removed and the campaigns fly it (see `mods-source/_retired/README.md`). Only the campaign pack adds anything else:
its campaign pages, briefing maps, art, mod lists and the player's SETUP
(`SETUP - double-click me.cmd`, `sest-setup.ps1` and its key helper
`sest-ui-keys.ps1`). Check it yourself (the
filter leaves out the campaign pack and the built `dist` copy):

```powershell
Get-ChildItem integration\*\SEST_* -Recurse -File |
  Where-Object { $_.FullName -notmatch '\\(campaign|dist)\\' } |
  Group-Object Extension
```

That is deliberate: the repo stays small and every change is readable as a
diff. The consequence is that **no pack is standalone**. `SEST_F-15EX_Revamp`
ships `aircraft/usaf_f-15ex_SEII.ini` and a few more `.ini` files but no
mesh — the geometry that file describes lives in workshop mod 3636386513.
Install the pack without the mod and the game has a unit definition pointing
at a mesh that is not there.

So no pack can be handed on by itself. What players get is the published
pair: the Workshop item 'SEST Integration Pack - Modernised Campaigns'
(3812461539, Public; the consolidated pack, every campaign included) and
the collection 'SEST - Modernised Campaign Collection' (3812390790): the Workshop mods in
`data/load-order.tokens.txt` plus the pack (published with 149 items; 191 once the October
2026 additions are added to it). The
item's Required Items list the same Workshop mods, so subscribing to the item
offers them all in one click; the collection does the same job (*Publishing
the pack*, below, says what that costs and how an update goes up). Inside the repo, what each pack needs is a
derived dependency list.

## What each pack needs

```powershell
python tools\check_dependencies.py
```

Three kinds, all computed from the files rather than hand-declared, so they
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
A name several mods define is credited to the one highest in the load order,
whose section is the one the game uses.

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

The packs install as **one folder**, `SEST_Integration`, under
`StreamingAssets`, exactly like a workshop mod, and never write into the game's
own files; only the player's SETUP the pack carries adds anything beside them,
the Anchor Chain preloader next to `Sea Power.exe` when it is missing. SETUP
also switches off one mod's debug logging, marks the listed mods made for an
older game version compatible (one `_info.ini` value each, the author's
file kept), unbinds Contact Log's default F6/F8 keys (they clash with
Topographic Map's F6 and Coordinated Strike Tool's F8 planner) when that
mod's settings file exists, and, like `set-mod-order.ps1`,
rewrites `[LoadOrder]` after a backup. `tools/consolidate_packs.py` builds it from
every source pack; Sea Power's Mod Manager lists it as one entry, SEST
Integration Pack, beside the workshop entries, and it takes part in the same
load order.

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\install-sest-packs.ps1 -WhatIfOnly   # dry run
powershell -ExecutionPolicy Bypass -File .\tools\install-sest-packs.ps1              # apply
# game closed: -AddMissing puts a newly installed pack at the top, enabled
powershell -ExecutionPolicy Bypass -File .\tools\set-mod-order.ps1 -AddMissing
```

`set-mod-order.ps1` knows SEST's own Workshop item, 3812461539, as SEST's
(`$SestOwnWorkshopIds` in `tools/lib/common.ps1`): with the local
`SEST_Integration` folder absent it keeps that id at position 1 instead of
dropping it as a stale Workshop entry, which it did until 14 Oct 2026; with
the folder present it keeps `SEST_Integration` at 1 and drops the id with a
warning to unsubscribe (the game lists it again at its next scan while the
subscription stands). It never lists both. `tools/tests/test_set_mod_order.ps1`
runs the cases on a stand-in settings file.

The consolidation **discovers** packs under `integration\` rather than working
from a list, so every `SEST_*` source folder there goes into `SEST_Integration`.
Only `tools/build_all.py`, which runs each pack's builder, needs a new pack
listed, in `local_packs` in `data/mod-catalog.json`.

**The one rule that matters:** the SEST pack sits above every workshop mod.
A pack is a whole-file replacement, so anything that outranks it makes the patch
silently do nothing — no error, nothing in the log. `data/load-order.tokens.txt`
keeps `SEST_Integration` at the very top, above Anchor Chain, for exactly that
reason, and `tools/check_load_order.py` fails the build if it sinks. This is not
theoretical: `SEST_Growler_NGJ_MALICE`, when it was still its own entry, was
inert for several sessions because U.S. Navy 2027 moved up one tier and happened
to jump over it.

## Retired packs

A pack is retired when the upstream mod adopts the fix. The patch then adds
nothing and costs something: an override is a whole-file replacement, so it
freezes everything *else* in that file at the version the pack was built
against, and it keeps a dependency alive for no gameplay reason. Git holds the
implementation if upstream ever regresses.

| Pack | Retired | Why |
|---|---|---|
| `SEST_Rafale_F5` | 2026-10-03, for one build | The Dassault Rafale mod it patched (JATM, MALICE and LRASM fits on the three late airframes) left the player's subscriptions on 28 Sep and the Workshop export on 30 Sep, and on the morning of 3 Oct the player retired the Rafale from the campaigns rather than resubscribe. That evening's export brought the French Air Force mod (`3758943352`), which ships the whole Rafale family under the same ids, and the pack was rebuilt on it the same evening - `integration/rafale-f5/build_patch.py` reads `3758943352` now, with the Rafale M Late's fits following that mod's one-store centreline geometry. Listed here because it was retired and came back; it is active. |
| `SEST_Zumwalt_CPS` | 2026-09-20 | Modern US Navy fixed both defects it existed for. The duplicate `[WeaponSystem1]` is gone (the CPS hull now declares 1–23, each once, with a real `[WeaponSystem2]`), and the dangling `SensorSystem12` reference is gone with it. The LMVLS now carries no `AssociatedSensors` at all, which is correct here rather than a new bug: `usn_ircps` is `GuidanceType=0, MidCourseCorrection=0`, so it draws no guidance channel — the rule in `tools/check_weapon_employment.py` applies to MCC 1 and 3, not 0. |

## The frozen hulls, and rebuilding after an export

The same cost applies to every live override, and one pack pays it on a
scale no other does. **SEST Replenishment At Sea ships about three hundred
whole-file overrides of other authors' hulls** (317 on the 24 Sep 2026
export): 307 modern hulls from 23 mods, each with one
`ReloadableWithoutMagazine=True` line per launcher that holds a round and has
no magazine, because without it that launcher can never be reloaded by
anything; and ten auxiliaries given a tuned supply block, nine of them hulls
RE-power also ships, forked from vanilla. It overrides 81 ammunition files
too. Each of those files is the upstream copy as it stood at the last export,
so until the pack is rebuilt:

- an upstream fix or rebalance to one of those hulls - Red Storm Arsenal,
  Modern US Navy, U.S. Navy 2027, the PLAN packs, Russian Navy 21, the
  Euromod navies - does not reach the game, because tier 0 still serves the
  old copy;
- a hull an author deletes keeps loading from the pack;
- a system or round an author renames leaves the fork naming the old one
  (`check_dependencies.py` reports it).

**The rule: rebuild after every export.** Run `export-mod-configs.ps1`,
then `python3 tools/build_all.py --from-scratch`, commit the regenerated
packs with the export, and redeploy. `tools/check_pack_fidelity.py` then
proves every SEST_Replenishment file is its current upstream plus only the
lines the pack inserts, and `tools/check_weapon_employment.py` reports the
defects a fork inherited from its upstream (a CIWS wired to a magazine the
upstream file never wrote, say) without failing on them, while still failing
anything the pack itself introduced. Deploying a pack built from an older
export than the mods installed beside it is the one way to make this pack
do harm.

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

**After a session pushes work** (on the PC, game closed, on the deploy branch
`data/deploy-branch.txt` names, `sest-dev/jolly-ride-rptj4t` since 25 Oct 2026):
```powershell
powershell -ExecutionPolicy Bypass -File .\tools\sync-sest.ps1
```
It refuses to run from any other branch, pulls, installs, sets the order with
`-AddMissing`, and ends with `IN LINE: all N installed files match this commit`.
Since 14 Oct 2026 it first looks for the Workshop copy of SEST, item
3812461539 under `steamapps\workshop\content\1286220` (the PC runs that copy
as a subscriber since the morning of 14 Oct): with that folder on disk it
stops before the pull, because the install would put a second copy beside it
and the game must never load both, and it names the two ways out -
unsubscribe from 3812461539, wait until the folder is gone and run again; or
keep the Workshop copy and run with `-SkipInstall`, which pulls and sets the
order only, `set-mod-order.ps1` keeping 3812461539 at position 1 in place of
`SEST_Integration`. Both copies on disk at once it refuses whatever the
switches (`tools/tests/test_sync_sest_guard.ps1` runs the three cases on
stand-in folders; the stop has not been seen on the PC yet).
The standard update block (*Already aligned once?* in
`docs/campaigns/southern-reach/install-alignment.md`) is this script behind two
checks: it checks out the deploy branch and runs it. A session's work reaches
the deploy branch by a fast-forward first; the four commits up to `fa692245`
(4 Oct) came in that way from `sest-dev/inspiring-wozniak-8vuckh`.

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

### Known red: `check_inventory` on four line-ending mods (the Rafale and Auto Time-on-Target cleared 3 Oct)

`check_inventory.py` exits 1 on this branch. For most of 3 Oct it also named
`3789793270`, Auto Time-on-Target, as missing from the catalogue's active set
and from the order while its folder was still on disk: the player unsubscribed
it that day and the repo retired it the same day, ahead of the export that
prunes the folder; the evening export (`bb2316d4`) pruned it and that red is
gone. The mirrored export ran on the
gaming PC on 27 Sep (`97eac5f7`) and cleared the ghost files; what stays red is
four mods whose files differ from their manifests only by line endings. On the
24 Sep 2026 export it failed 17 mods, for two reasons: ghost files and line
endings.

**Ghost files (13 mods on 24 Sep; cleared 27 Sep).** Every export before the
mirror was an overlay, so a file an author deleted or renamed stayed behind and
kept resolving. On the 24 Sep export 13 mods held 203 files over their
manifests. The 27 Sep mirror deleted what the mods no longer ship (git counts
192 deletions over 13 mods in `97eac5f7`), and every mod but the four below now
matches its manifest.

Of the ghosts, one reached a campaign: Southern Watch 11 placed USS Jack H. Lucas
as `usn_ddg_burke_f2a_g4_2022`, a Modern US Navy Flight IIA group file that was
gone by 20 Sep. She now sails as `usn_ddg_burke_f3_125` Variant1, her own Flight
III hull. Two rounds this section had counted as ghosts are back: the 20 Sep
mirror had dropped `usn_rim-162e` (ESSM Block II) and `usn_rim-116c`, but U.S.
Navy 2027 ships both again, in new versions, so the 27 Sep mirror updated them
rather than deleting them. The ESSM loads on that mod's 2027 Burkes and Nimitz
resolve again, and `check_weapon_employment.py` passes. The other ghosts that
missions or packs reached (`usn_rim-162a`, `usn_rim-66m-2`, `usn_rim-66m-5`, the two sonobuoys,
`usn_agm-65b`, `usn_agm-65d`, `fr_am-39_Block2`) still resolve now that they are
deleted, through another mod's or the base game's copy of the same id.

**The Rafale (30 Sep to 3 Oct, cleared; back the same evening).** The Dassault Rafale
mod (`3504168760`) left the PC's Steam subscriptions between the 27 and 28 Sep snapshots
and the 30 Sep export pruned its folder. For four days the pack was built with the last
export that had the mod (`git archive e0d961d7~1 mods-source/3504168760 | tar -x` before
a rebuild, the folder deleted again before the commit) and four checks were red on the
committed tree. On the morning of 3 Oct the player retired the Rafale from the campaigns
instead: D3's CAP pair and D6's escort went, the allied fleet stopped selling it, the
Banda vignette that flew it and the SEST Rafale F5 pack were retired, and the catalog
and order dropped the mod. That evening's export brought the French Air Force mod
(`3758943352`), which ships the whole Rafale family under the SAME unit ids, and
everything came back on it: the pair, the escort, the two allied-fleet entries, the
vignette and the pack, now built from `3758943352`. The old mod's catalogue entry stays
as the record, `unsubscribed`. Nothing is red for it, and no rebuild needs the archive.

**Line endings (4 mods: same file count, fewer bytes).** Modern PLAN Systems
(`3775128499`), Ka-31 (`3776340577`), Tu-214R (`3780118683`) and E-3G
(`3781062859`) hold files committed on 25 Aug with their CRs stripped, the day
before `mods-source/` was pinned `-text`; the manifest measures the CRLF
originals. Neither mirrored export (20 Sep, 27 Sep) changed those blobs, so
these four stay red until they are renormalised: run
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

## Publishing the pack

Players get the SEST pack from one Workshop item, and its dependencies from
that item's Required Items or from one collection, both mirroring
`data/load-order.tokens.txt`:

- **The item**: 'SEST Integration Pack - Modernised Campaigns', Workshop id
  3812461539, Public. It is the `SEST_Integration` folder, all three
  campaigns included. Every upload is an update to it, never a new item.
- **The collection**: 'SEST - Modernised Campaign Collection', 3812390790,
  the Workshop mods in `data/load-order.tokens.txt` plus the pack (196 items
  once the 13 October 2026 additions are in it; it was published with 149). A mod added to or dropped from the load order means the same change
  to the collection and to the item's Required Items, before the upload.

**Required Items are the load order's Workshop mods.** Set in October 2026
for the one-click subscribe; like the collection, they must be the Workshop
mods of `data/load-order.tokens.txt`. The cost: the
Mod Manager's dependency check ('Must load above this mod') may offer to move
the required items above the pack, which would undo every fix in it (the one
rule under *Installing alongside other mods*). The answer is no, and SETUP
run again puts the order back. Whether the prompt appears is not yet seen;
`docs/campaigns/southern-watch/publishing.md` (*Dependencies*) has the test
that settles it. Do not rely on Sync for the order: SETUP sets it.

**The update**, from the PC once the sync reads IN LINE with the commit to
publish, since the folder it picks is the installed copy of
`integration/dist/SEST_Integration`: Mod Manager > Create Mod > Update
Existing > Pick Folder `StreamingAssets\SEST_Integration` > Submit, then
confirm `m_eResult: k_EResultOK` in `Player.log`. The Create Mod image picker
only browses `StreamingAssets`, so the preview image is
`StreamingAssets\SEST-preview.jpg` (124 KB), outside the pack folder; it is
not in the repo.

**If the upload fails with `k_EResultLimitExceeded`.** Sea Power's Steam Cloud
has a 1,000-file cap, and files under `StreamingAssets\user\missions` count
toward it. Over the cap the upload fails with `k_EResultLimitExceeded` and
leaves 0 B on the item. That is how the first uploads failed: 804 of the
files were one folder, `StreamingAssets\user\missions\NEW MISSIONS CLEAN`,
which was moved to `%USERPROFILE%\Documents\SeaPower-moved-out-of-cloud`, and
the cloud is now about 180 files. The recovery is to move files out until the
cloud is under the cap and upload again; do not move that folder back.

The whole procedure, with the change log and what to check before Submit, is
in `docs/campaigns/southern-watch/publishing.md`; the listing text is in
`workshop-listing.md` beside it.

## After a Sea Power update

A game update moves the one thing every pack and mission here is built on
and nobody exports on purpose: the game's own files. Three things in this
repo track them. `mods-source/_vanilla/original` is the vanilla export: since
12 Nov 2026 (3a2c26944) 4,505 text files under 0.9.0 Build 261111 of 11 Nov
2026 (*The 0.9.0 run* below; the pack is 4,592 files on it); before it, from
22 Oct 2026 (1bda58a6), 4,049 text files under 0.8.7 Build 261021 of 21 Oct
2026, and before that 0.8.6 Build 261014 (729c5e97, 15 Oct) and 0.8.5 Build
261008 (7739076c, 11 Oct), none of whose drift needed a SEST change beyond
the version bump (`docs/workshop-refresh-20261022-review.md`; on 0.8.7 SEST's
runtime plugin, matched to one game build, switched itself off until the
steps in `integration/runtime-fixes/README.md` matched it to 0.8.7 on 23 Oct
2026); on 3
Oct 2026, 4,047 text files under 0.8.4 Build 261002 of 2 Oct 2026 (the 2 Oct
export's 4,051, taken under 0.8.3, less the KC-135A and Tu-16N stubs the game
no longer ships, deleted by hand on 3 Oct; the 3 Oct export changed none of
them), the version and build being the first `dd-Mon-yyyy: X.Y.Z Build #N`
line of `data/install-snapshot/changelog.live.txt`, the game's own `changelog.txt`
as the capture copied it (`data/install-snapshot/game-build.txt` holds
Steam's build id and the executable's date, not that number). The builders
fork vanilla files, the `language_*` and `systems` files merge with
vanilla's key by key, and the missions field stock units by id
(`campaign_data.py` names a unit's mod `_vanilla` when it is stock), so a
changed vanilla file matters through whatever here depends on it. Each SEST
pack declares the game's version in its `_info.ini` (`[Compatibility]`
`ApproximateVersion`) from a literal in its builder;
`tools/consolidate_packs.py` holds no literal and gives the consolidated
pack the highest version among its components, so a stale component shows
only in its own `_info.ini`. And the Workshop mods declare their own. Two
tools read all of that: `tools/check_vanilla_drift.py` says
what the update changed and what depends on each change, and
`tools/check_game_version.py` says which declarations the new version fails.
The order of work is the PC exporting the new game, then a session reading
the drift, bumping, rebuilding and gating, then the usual sync, then the
Workshop update of item 3812461539.

### On the PC: export the new game, snapshot it, push

Game closed, after launching it once: Steam finishes the update at launch,
and the game writes the new build's `player.log` and, on exit, its
`usersettings.ini`, which the capture reads. Paste this into PowerShell as
one block. It has no blank lines on purpose; if it stops at a `>>` prompt,
press Enter once more.

```powershell
& { $ErrorActionPreference = 'Stop'
  if (Get-Process -Name 'Sea Power', 'SeaPower' -ErrorAction SilentlyContinue) { throw 'Sea Power is running - exit it first' }
  Set-Location -LiteralPath 'C:\Users\rolyl\Seapower-mods'
  if (git status --short) { throw 'The clone has uncommitted changes - stop and report them' }
  git checkout beta
  if ($LASTEXITCODE) { throw 'checkout failed' }
  git pull --ff-only origin beta
  if ($LASTEXITCODE) { throw 'pull refused - stop and report it' }
  powershell -ExecutionPolicy Bypass -File .\tools\export-mod-configs.ps1 -IncludeVanilla
  if ($LASTEXITCODE) { throw 'export failed - read its last lines; nothing has been committed' }
  git add -A mods-source
  git commit -m 'Mod export after the Sea Power update'
  if ($LASTEXITCODE) { throw 'nothing to commit - not even the changelog moved, so the game has not updated or the export did not read it; read its output' }
  powershell -ExecutionPolicy Bypass -File .\tools\capture-context.ps1 -Redact
  if ($LASTEXITCODE) { throw 'capture failed - read its last lines' }
  git add -A data\install-snapshot
  git commit -m 'Install snapshot after the Sea Power update'
  if ($LASTEXITCODE) { throw 'nothing to commit - the capture wrote nothing new' }
  git push origin sest-dev/jolly-ride-rptj4t
  if ($LASTEXITCODE) { throw 'push failed' }
  Get-Content -LiteralPath data\install-snapshot\changelog.live.txt -TotalCount 8
  Get-Content -LiteralPath data\install-snapshot\game-build.txt
}
```

It stops before anything is committed if the game is running, if the clone
has changes of its own, or if the export fails, and at the first commit if
nothing changed. An update always rewrites the game's `changelog.txt`, which
the game ships outside `StreamingAssets` (in `Sea Power_Data` or beside `Sea
Power.exe`); since 2 Oct the exporter's `-IncludeVanilla` copies it in as
`mods-source/_vanilla/changelog.txt` (before that the file had been placed
by hand with the first export), the drift tool reads the old and new game
version from it, and `check_game_version.py` compares it with the
snapshot's copy. An unchanged tree therefore means the game has not
updated, or the export did not read it (its output says `vanilla export
skipped` when it could not find the install, and warns when it could not
find the changelog). The last
lines it prints are the new changelog head, whose `dd-Mon-yyyy: X.Y.Z Build
#N` line is the version everything below works from, and Steam's build
record. Report both. If a campaign is under way, add `-IncludeSaves` to the
capture line before running it; the save paragraph below says why.

**When the PC is on a Steam beta.** `mods-source/_vanilla` holds the
released game the pack is built for, and must keep holding it while a beta
is installed: the builders fork it and the gates compare against it. (From
28 Oct to 11 Nov 2026 that was 0.8.7 Build 261021 beside the betas 261026
to 261107; the beta became the release, 0.9.0 Build 261111, on 11 Nov, and
the export of 12 Nov is that release.) An export with `-IncludeVanilla`
on a beta PC writes the beta's files over it, which is what the 28 Oct 2026
capture did (1,031 changed files, one added file and `changelog.txt`, put
back by 9b382fd8). The
changelog head in `data/install-snapshot/changelog.live.txt` says which
build is installed: `Build 261026` is the beta. On the beta, run this block
without `-IncludeVanilla` on the export line, or, if it has already run,
put the vanilla export back to the committed build before the first commit:

```powershell
& { $ErrorActionPreference = 'Stop'
  Set-Location -LiteralPath 'C:\Users\rolyl\Seapower-mods'
  git checkout -- mods-source/_vanilla/original mods-source/_vanilla/changelog.txt
  if ($LASTEXITCODE) { throw 'restore failed - stop and report it' }
  git clean -fdq -- mods-source/_vanilla/original
  git status --short -- mods-source/_vanilla/original mods-source/_vanilla/changelog.txt
}
```

`git clean` there removes only files the beta added under
`_vanilla/original`, such as `missions/Demo/AircraftEditorMission.ini` on
the 28 Oct capture; the last line should print nothing. The export also
writes the rest of the StreamingAssets text tree into `_vanilla`, so
`git status --short -- mods-source/_vanilla` may still list files outside
`original/`. `user/controls.ini` is your own key bindings and stays as you
have it, as 9b382fd8 kept it; put any other one back with
`git checkout -- <path>`. A beta export
belongs to the beta work (the 28 Oct one is on the owner's
`chore/workshop-refresh-20261028` at `f590fb8c`), never in `_vanilla`.
The build names in that paragraph are of that time: since 0.9.0 the head of
`changelog.live.txt` reads `0.9.0 Build 261111 Public Release`.

**What the export cannot tell you: files the game removed.** The per-mod
export mirrors deletions; the vanilla export does not.
`export-mod-configs.ps1` copies each StreamingAssets text file over
`mods-source/_vanilla` with `-Force` and removes nothing (its
`-IncludeVanilla` block, beside the per-mod mirror above it), so a file the
update dropped stays
in `_vanilla/original`, keeps resolving for every checker, and looks the
same as a file the game still ships. The proof is already in the tree: six
`SEST_*` folders under `mods-source/_vanilla/`, exported before the script
learned to skip installed packs (`fe24f0c0`, 26 Aug), still there, still
declaring `ApproximateVersion=0.6.8`. The drift tool compares the working
tree against git, so its *removed* list names what is gone from the tree,
not what the game dropped while the export left the file in place. Finding
those needs the game on disk, so it is a PC step, game closed or open:

```powershell
& { $ErrorActionPreference = 'Stop'
  Set-Location -LiteralPath 'C:\Users\rolyl\Seapower-mods'
  . .\tools\lib\common.ps1
  $sa = Find-StreamingAssets
  if (-not $sa) { throw 'Sea Power StreamingAssets not found' }
  $live = Join-Path $sa 'original'
  $repo = (Resolve-Path -LiteralPath 'mods-source\_vanilla\original').Path
  $gone = @(Get-ChildItem -LiteralPath $repo -Recurse -File | Where-Object { -not (Test-Path -LiteralPath (Join-Path $live $_.FullName.Substring($repo.Length + 1))) })
  'Files in mods-source\_vanilla\original the game no longer ships: {0}' -f $gone.Count
  $gone | ForEach-Object { $_.FullName.Substring($repo.Length + 1) }
}
```

It lists every file in the repo's vanilla export that the installed game no
longer has. Delete what it lists, commit the deletions with the export
(`git add -A mods-source\_vanilla`), and the drift tool reports each as
removed with what here forks or fields it, which is what its exit code is
for. The exporter's `-DestDir` applies to vanilla too, so a clean export
beside the repo (*Known red* above) is the other route.

Since 13 Nov 2026 every capture writes that list itself:
`data/install-snapshot/game-files-dropped.txt` (`capture-context.ps1`), with
the export's build and the installed build in its first lines, and the
refresh summary counts it under its `Sea Power` line. So the block above is
for a clone whose scripts are older. The list is against whatever build is
installed: with a beta on the PC it names what the beta dropped, and those
files stay in `_vanilla` until the beta is the release. The session that
takes the capture in removes the listed files with
`python3 tools/apply_dropped_files.py`, which does it only when the export
holds the build the list was taken against, and refuses otherwise.

### A Workshop refresh for review

When the next development pass needs the collection as it is now - after
Steam has updated mods, or before a large piece of work - the capture goes on
its own branch, `chore/workshop-refresh-YYYYMMDD`, so it can be reviewed
against the SEST integration before anything is changed to follow it. The
branch is cut from the one that holds the newest export of the mods: the
deploy branch when it is current, and the working branch while a release
waits unmerged on it, as the 0.9.0 work did from 13 Nov 2026 (*The capture
for 0.9.0* below). It matters because the update check and the summary
compare the Workshop with what the branch holds. The 12 Nov 2026 capture ran
on a branch whose export was of 1 Nov and listed 52 mods as updated; 42
were. Let Steam finish every Sea Power download, start the game to the main
menu once (so Player.log and the BepInEx log record what loaded), quit it,
then:

```powershell
& { $ErrorActionPreference = 'Stop'
  if (Get-Process -Name 'Sea Power', 'SeaPower' -ErrorAction SilentlyContinue) { throw 'Sea Power is running - exit it first' }
  Set-Location -LiteralPath 'C:\Users\rolyl\Seapower-mods'
  if (git status --short) { throw 'The clone has uncommitted changes - stop and report them' }
  $b = 'chore/workshop-refresh-YYYYMMDD'                  # the branch Claude made
  git fetch origin $b
  if ($LASTEXITCODE) { throw 'fetch failed - is the branch name right?' }
  git checkout -B $b "origin/$b"
  powershell -ExecutionPolicy Bypass -File .\tools\export-mod-configs.ps1 -CheckUpdates -ReportPath data\install-snapshot\workshop-updates.txt
  powershell -ExecutionPolicy Bypass -File .\tools\export-mod-configs.ps1 -IncludeVanilla
  if ($LASTEXITCODE) { throw 'export failed - read its last lines; nothing has been committed' }
  powershell -ExecutionPolicy Bypass -File .\tools\capture-context.ps1 -Redact
  if ($LASTEXITCODE) { throw 'capture failed - read its last lines' }
  git add -A mods-source data\install-snapshot
  git commit -m "chore: capture workshop refresh $(Get-Date -Format yyyy-MM-dd)"
  git push -u origin $b
  if ($LASTEXITCODE) { throw 'push failed' }
  git checkout beta                 # back to the deploy branch for play
}
```

`workshop-updates.txt` is the exporter's read-only update check, taken before
the export overwrites the evidence. The script writes it itself with
`-ReportPath`, UTF-8 without a byte-order mark; until 14 Oct 2026 the console
output was piped through `Out-File -Encoding utf8`, which added a byte-order
mark and sent every name through the console code page - the 13 Oct report
shows 3731931836 as `??????` - and the check listed SEST's own item
3812461539 as a new subscription, which it now skips. `plugin-dlls.txt`
(written by the capture)
records every code DLL's hash and version, since a plugin update changes
behaviour with no .ini changing. In `workshop-subscriptions.txt` each item's
`updated` is Steam's own `timeupdated` from `appworkshop_1286220.acf` since
14 Oct 2026, with the folder's last-write time beside it as `folder`; the
folder time alone, the only date until then, does not move for an update
that only rewrites files inside existing subfolders, so it missed updates.
`bepinex.log` is the whole `BepInEx\LogOutput.log` (a file over 50 MB is kept
as its first and last 20,000 lines with a marker line), not the last 600
lines as before. `python3 tools/workshop_refresh_summary.py`
then writes `data/install-snapshot/workshop-refresh-summary.txt`: the four
inventories (Steam's record, folders on disk, the canonical order, the
catalog) side by side, and what changed since the previous capture - facts
only, for the review to judge. Nothing on the refresh branch is merged; it is
read by the next pass.

**On the public beta**, take the `-IncludeVanilla` line out of the block
above (the Workshop mods export the same either way), or run the restore
block in *On the PC* above before `git add`: the pack targets Build 261021
until the 11 Nov 2026 release, and a beta export in `mods-source/_vanilla`
would move every builder and gate onto the beta.

**The same capture in one command.** `tools\capture-all-mod-updates.ps1`
runs the steps of the block above in order: the capture with `-Redact`,
the read-only update check into `workshop-updates.txt`, the Workshop
export, then `fingerprint_mods.py`, `workshop_refresh_summary.py` and
`check_inventory.py`. It never runs the export with `-IncludeVanilla`, so
it is safe on the beta as it stands. It also writes a review ZIP outside the
clone (by default `Downloads\SEST-Workshop-Capture-<date-time>.zip`) with
the changed and new mod files, the snapshot's key files, the inventory
report and a README naming any stage that failed; a failed stage does not
stop the later ones. It refuses to start with the game running, on the
deploy branch, or with uncommitted changes. It never commits, pushes,
uploads or publishes, never builds, copies or installs a DLL, and only
reads Steam, the game folder, BepInEx and the Workshop folders; what it
writes is `data\install-snapshot\`, the Workshop mods' folders in
`mods-source\` and `data\mod-fingerprints.json`. The block below commits
and pushes what was captured, partial or not: a failed stage prints
`SEST CAPTURE PARTIAL` but does not stop the block, and the ZIP's README
lists the stage that failed, so send the ZIP either way:

```powershell
& { $ErrorActionPreference = 'Stop'
  Set-Location -LiteralPath 'C:\Users\rolyl\Seapower-mods'
  $b = 'chore/workshop-refresh-YYYYMMDD'                  # the branch Claude made
  git fetch origin $b
  if ($LASTEXITCODE) { throw 'fetch failed - is the branch name right?' }
  git checkout -B $b "origin/$b"
  powershell -ExecutionPolicy Bypass -File .\tools\capture-all-mod-updates.ps1
  if ($LASTEXITCODE) { throw 'capture refused or failed - read its last lines; nothing has been committed' }
  git add -A mods-source data\install-snapshot data\mod-fingerprints.json
  git commit -m "chore: capture workshop refresh $(Get-Date -Format yyyy-MM-dd)"
  git push -u origin $b
  if ($LASTEXITCODE) { throw 'push failed' }
  git checkout beta                 # back to the deploy branch for play
}
```

The push is the block's own last step, as above, not the script's. Send the
ZIP too when the review needs the files without the branch.

**What a capture says about the game.** It never exports the game's own
files, so by itself it cannot show a game update. Since 13 Nov 2026 it says
two things about the game all the same. `game-build.txt` carries the
SHA-256 of `Sea Power_Data\Managed\Seapower-Scripts.dll` (`code sha256`),
the value SETUP and SEST's plugins know a game build by; Sea Power 0.9.0 had
reached the repository on 12 Nov with its changelog and Steam build id and
without it. And the one-command capture compares the changelog it copied
(`changelog.live.txt`) with the export's (`mods-source/_vanilla/changelog.txt`):
when version or build differ it prints `THE INSTALLED GAME IS NOT THE
EXPORTED ONE` at the end of its run and in the ZIP's README, and
`workshop-refresh-summary.txt` says the same under its `Sea Power` line. A
line that says `Public Release` is a new release, and the game export is due
(*On the PC* above); one that does not is a beta, and `_vanilla` stays.
`tools\export-game.ps1` applies that rule: it runs the exporter with
`-IncludeVanilla` only when the installed build is a public release newer
than the export, and otherwise says which case it found and exports nothing
(exit 3 the same build, 4 a beta, 5 no game or no changelog, 6 an older
build). The block below runs it after the capture.

**The capture for 0.9.** From 13 Nov 2026 the 0.9 work waits unmerged on
`claude/continue-previous-session-39wqwq`. That branch holds the 12 Nov
export of the mods and the tools as they are now; the branch the PC was on
that week (`release/sest-workshop-20261101`) has an export of 1 Nov, an older
capture script and no `tools\capture-beta-references.ps1` at all. So the
block cuts the capture branch from the working branch itself, on the PC, and
nobody has to make it first. Change `$base` when the work has moved to
another branch. `tools/tests/test_capture_block.ps1` runs this block, as it
stands here, against a fixture:

<!-- capture-block -->
```powershell
& { $ErrorActionPreference = 'Stop'
  if (Get-Process -Name 'Sea Power', 'SeaPower' -ErrorAction SilentlyContinue) { throw 'Sea Power is running - exit it first' }
  Set-Location -LiteralPath 'C:\Users\rolyl\Seapower-mods'
  if (git status --short) { throw 'The clone has uncommitted changes - stop and report them' }
  $base = 'claude/continue-previous-session-39wqwq'
  $was = "$(git branch --show-current)".Trim()
  $b = 'chore/workshop-refresh-' + (Get-Date -Format 'yyyyMMdd-HHmm')
  git fetch origin $base
  if ($LASTEXITCODE) { throw 'fetch failed - is the base branch name right?' }
  git checkout -B $b "origin/$base"
  if ($LASTEXITCODE) { throw 'checkout failed - stop and report it' }
  powershell -ExecutionPolicy Bypass -File .\tools\capture-all-mod-updates.ps1
  if ($LASTEXITCODE) { throw "capture refused or failed - read its last lines; nothing is committed and the clone is on $b" }
  git add -A mods-source data\install-snapshot data\mod-fingerprints.json
  git commit -m "chore: capture workshop refresh $(Get-Date -Format yyyy-MM-dd)"
  if ($LASTEXITCODE) { throw "nothing was committed - stop and report it; the clone is on $b" }
  git push -u origin $b
  if ($LASTEXITCODE) { throw "push failed - the capture is committed on $b; push that branch again later" }
  powershell -ExecutionPolicy Bypass -File .\tools\export-game.ps1
  if ($LASTEXITCODE -eq 0) {
    git add -A mods-source
    git commit -m "Game export after the Sea Power update"
    git push origin $b
    if ($LASTEXITCODE) { throw "push failed - the game export is committed on $b; push that branch again later" }
  }
  powershell -ExecutionPolicy Bypass -File .\tools\capture-beta-references.ps1
  if ($LASTEXITCODE) { Write-Warning 'The reference capture did not finish - report its last lines. The mod capture above is pushed.' }
  if ($was) { git checkout $was }
  "Captured and pushed: $b"
}
```

It stops before anything is written if the game is running or the clone has
changes of its own, and names the branch the clone is left on if it stops
later. It commits and pushes what the capture wrote, partial or not (a
failed stage prints `SEST CAPTURE PARTIAL`). If the installed game is a
public release newer than the export, it then exports the game's own files
and pushes them as a second commit; with the same build or a beta installed
that step says so and does nothing. Last it runs the reference capture,
which writes only its ZIP, and returns the clone to the branch it was on. Two ZIPs land in Downloads. `SEST-Workshop-Capture-<date-time>.zip`
is the review bundle of what the pushed branch already holds.
`SEST-Beta-References-<date-time>-<6 hex>.zip` holds the game's and the
mods' code as installed; it is what matching SEST's code to a new game build
starts from, and it is not in the repository, so it has to be handed over.
The reference capture refuses the 0.8.7 Build 261021 game file and a running
game, and nothing else.

**A capture by ZIP: 14 Nov 2026.** The owner's PC did not use the block. It
ran a read-only comparison of its own against `data/mod-fingerprints.json`
at `01cfa43b` and sent a report and the whole text of each mod it found
changed, as three ZIPs (`data/install-snapshot/pc-report-20261114/` has the
report and says what it is). Taking it in, for the next time one comes that
way:

1. Unpack each ZIP into its own empty folder outside the clone and compare
   every file with `mods-source`, mod by mod, before copying anything.
2. Set aside the mods whose only difference is `_info.ini` with the line
   `; SEST marked this mod compatible`. SETUP writes that line and a new
   `ApproximateVersion` into the installed file; `export-mod-configs.ps1`
   reads the author's kept original instead, and a comparison of installed
   files does not. On 14 Nov that was 59 of the 77 mods the report called
   updated. Where a mod with real changes carries the mark too, keep the
   `_info.ini` the export has.
3. For the rest copy every uploaded file as it is (`mods-source` is stored
   byte for byte) and remove the files the upload no longer has.
4. Recount the taken mods' rows of `_export-manifest.csv` (files and bytes
   of the folder; the other rows must still agree with their folders), run
   `python3 tools/fingerprint_mods.py`, and compare the result with the
   fingerprints the PC reported: a taken mod must equal the PC's, and so
   must every mod the PC found unchanged. On 14 Nov 17 of 18 did, the
   eighteenth by the kept `_info.ini`, and all 123 unchanged.
5. Then the usual: rebuild, `python3 tools/refresh_upload_manifest.py`, the
   checks, the tests, the notes.

Such a capture brings no game files, no `changelog.live.txt` and no
snapshot of the kind `capture-context.ps1` writes, so the files of
`data/install-snapshot/` stay at the last full capture. That report showed
the game at 0.9.2-261113b by its Player.log while the export here was 0.9.0;
the pack stays on the export it has until the game's files come too.

### In the repo: read the drift, bump the version, rebuild, gate, document, push

1. **Note the baseline, then merge the deploy branch.** The drift tool's
   default baseline is the last commit that touched the export, which after
   the merge is the PC's own, so record the one before it first:

   ```bash
   git log -1 --format=%h -- mods-source/_vanilla/original   # the drift baseline: a4d3c1c1 on 2 Oct 2026
   git fetch origin
   git merge origin/sest-dev/jolly-ride-rptj4t
   ```

   The PC's two commits touch `mods-source/` and `data/install-snapshot/`,
   which no session edits by hand, so the merge should have nothing to
   resolve.

2. **Read what moved.**

   ```bash
   python3 tools/check_vanilla_drift.py --since <baseline>
   ```

   It lists what the update added, removed and changed in
   `_vanilla/original` and, for each, what depends on it. Read it in this
   order. An **overridden** file that a pack carries as a static copy, and a
   **merged-key clash** (a key vanilla now defines that a pack's
   `language_*` or `systems` file also defines - the builders refuse to
   shadow a vanilla key, so the build stops on it), are hand fixes: re-fork
   the copy from the new file, or rename or drop the pack's key. An
   overridden file whose builder names it is rebased by the rebuild in
   step 4; `check_pack_fidelity.py` proves the result for
   SEST_Replenishment's forks, which are most of them, and the other packs'
   forks have no such gate, so read the rebuild's diff. A **removed**
   unit that a mission fields is a mission edit: re-type it, as Southern
   Watch 11's Burke was re-typed when its Flight IIA file went. **New
   content** is an opportunity, not a fault: vanilla is a source the
   coverage reads, not a row it must reach, so a new stock unit fails
   nothing by being left alone. The test to apply is the one the coverage
   rule applies to a mod (`EXCUSES` in `integration/campaign/campaign_data.py`,
   whose builder rejects an excuse that has become untrue): either a mission
   can field it with realism, or there is a reason it cannot. The tool exits
   1 on the static copy, the clash and the removed fielded unit, and 0 on
   the rest.

3. **Check the version, then bump it.**

   ```bash
   python3 tools/check_game_version.py                 # reads data/install-snapshot/changelog.live.txt
   python3 tools/check_game_version.py --bump X.Y.Z    # X.Y.Z: the version the PC block printed
   ```

   The first run names every pack and builder whose `ApproximateVersion`
   differs from the game's, and every Workshop mod whose declared range
   excludes it, and exits 1 on either. On 2 Oct 2026, against 0.8.2, it
   already fails four packs: `SEST_ADF_Persistent_ISR` declares 0.6.8,
   `SEST_Rafale_F5` 0.8.1, and `SEST_Allied_Fixes` and `SEST_B52_ARRW`
   declare nothing. `--bump` rewrites the literal in every builder and
   every static `_info.ini` and prints each file it changes; it cannot
   rewrite a literal that is not there, so the two builders that write
   `_info.ini` without one (`integration/allied-fixes/build_patch.py`,
   `integration/b52-arrw/build_patch.py`) get their `[Compatibility]`
   section by hand. The builder-written `_info.ini` files stay stale until
   the rebuild.

   Then read `data/install-snapshot/player.log` for `[SEST Runtime]`. SEST's
   own runtime plugin is matched to one game assembly and fails closed on
   any other: `inactive: uninspected native assembly <hash>` means the
   update changed `Seapower-Scripts.dll` and its corrections are off, and
   SEST UI Follow-up (`plugins/SEST.ContactsFix.dll`) logs `inactive;
   original behavior retained` with it. No gate notices this. Do not add
   the new hash unverified: the steps, from the PC export
   (`tools/export-map-diagnostics.ps1 -IncludeGameAssembly`) to
   `build_plugin.py`, are in `integration/runtime-fixes/README.md`, and
   until they are done nothing player-facing may claim the corrections
   (0.8.7: off from its release on 21 Oct 2026, matched on 23 Oct). Since
   28 Oct 2026 the shipped runtime is 1.5.0, a binary captured from the
   owner's PC whose source is not in the repository: it cannot be re-gated
   until that source is recovered, and `build_plugin.py` refuses to replace
   it with the 1.2.0 fork base (`--replace-captured-binary` would). Any new
   runtime file also needs UI Follow-up rebuilt against its hash
   (`integration/ui-followup/README.md`).

4. **Rebuild everything.**

   ```bash
   python3 tools/build_all.py --from-scratch           # about 25 min; 24 packs, then the consolidated dist
   ```

5. **Every gate.** Known red on this branch: `check_inventory.py` on the
   four line-ending mods (3775128499, 3776340577, 3780118683, 3781062859);
   *Known red* above has the story. Anything else red is the update's, and
   step 2's report says where.

   ```bash
   python3 tools/check_pack_fidelity.py
   python3 tools/check_campaign_coverage.py
   python3 tools/check_dependencies.py
   python3 tools/check_load_order.py
   python3 tools/preflight.py --all
   python3 tools/check_weapon_employment.py
   python3 tools/check_alias_bases.py
   python3 tools/check_scenarios.py
   python3 tools/check_stale_phrases.py
   python3 tools/check_inventory.py
   python3 tools/check_game_version.py                 # green now, but for Workshop ranges no bump can fix
   python3 tools/check_vanilla_drift.py --since <baseline>   # green once the hand fixes are in
   ```

6. **Both test suites.**

   ```bash
   python3 -m unittest discover -s tools/tests -p 'test_*.py'
   python3 -m unittest integration/campaign/test_build_pack.py
   pwsh -File tools/tests/test_scan_ui_assets.ps1   # the UI-asset scan, on synthetic files
   ```

7. **Regenerate the derived docs, then update the hand-written ones.**

   ```bash
   python3 tools/generate_load_order.py      # docs/load-order-full.md
   python3 tools/generate_catalog.py         # docs/mod-catalog.md
   python3 tools/fingerprint_mods.py         # data/mod-fingerprints.json, the -CheckUpdates baseline
   find integration/dist/SEST_Integration -type f | wc -l   # the installed file count: 1266 on 4 Oct 2026, 4,592 on 13 Nov
   python3 tools/refresh_upload_manifest.py  # docs/releases/20261107/upload-manifest.json: the PC refuses an upload that differs from it
   ```

   By hand: the install guide's count, if it moved - the `IN LINE: all N
   installed files` line under *Already aligned once?*, `N is` in
   step 4 of `docs/campaigns/southern-reach/install-alignment.md` and the
   derivation under that table, which ends at the current count and
   gains a clause for what the update added or removed - and
   `Consolidated, they are N files` in `README.md`;
   a dated section in each campaign's `build-notes.md`
   (`docs/campaigns/<campaign>/`, in the style of *Rivet Joint (30
   September)* in Southern Reach's and Red Line's) saying what the update
   changed under that campaign, what
   was re-typed or placed, and what is not demonstrated; and the version
   and file count at the top of this section.

8. **Commit and push the session's branch.**

   ```bash
   git add -A
   git commit -m "Rebuild on the X.Y.Z export: <what the drift report named>"
   git push origin <the session's branch>
   ```

9. **Then the PC runs the standard update block** (*Already aligned once?*
   in `docs/campaigns/southern-reach/install-alignment.md`): once the
   session's commits are on the deploy branch (a fast-forward), it checks out
   that branch and syncs, and its last
   line must read `IN LINE: all 1266 installed files match this commit`, or
   the new count from step 7.

10. **Then update the published item, never a new one.** If the export
    added or dropped a Workshop mod, first change the collection
    (3812390790) and the item's Required Items to match
    `data/load-order.tokens.txt`. Then, with the PC IN LINE
    and Sea Power's Steam Cloud under its 1,000-file cap: Mod Manager >
    Create Mod > Update Existing (item 3812461539) > Pick Folder
    `StreamingAssets\SEST_Integration` > Submit, then confirm
    `m_eResult: k_EResultOK` in `Player.log`. Leave the form's Required Workshop IDs
    as it shows them, and check the item page still lists its Required Items
    after Submit. *Publishing the pack* above has the
    reasons and the failure to expect.

### The first run: 0.8.3, 2 October 2026

The procedure above was written the day before its first use, and the use
changed it in two places: the game's changelog dropped the `#` and the
`(N)` from its build lines on 28 Sep (`0.8.3 Build 261001`, `0.8.2 Build
260928b`), so both tools now read either shape; and the exporter had never
copied `changelog.txt`, so it does now. The exporter's own one-line report of
that copy still matched `Build #`, and on 3 Oct it died on the null that
returned - after every file was copied, before the prune and the manifest -
so the PC's first export after a mod update stopped with the tree dirty and
nothing committed. It matches either shape now and reports the copy whether
or not it finds a build line. An export that dies that way is re-run, not
repaired: every step is idempotent, and the manifest is written last for
that reason. What 0.8.3 needed, for the record
and as the pattern for next time (Southern Watch build notes, "Sea Power
0.8.3", has each in full): five builders stopped where their own checks
said - the campaign rules page (the stock page now binds the Survived
Missions column, so the swap went), Collection Fixes (a donor sensor
section gone, and section headers that now carry comments), the Intercept
Model (a key vanilla gained, pinned as `VANILLA_SINCE`), Replenishment (a
donor hull's magazine round changed) and Allied Fixes (a mod update renamed
a round) - and `preflight --all` caught the one silent change, a stock
aircraft that lost its Default fit under four editor-mission entries. The
drift tool found no static override, no key clash and no removed unit; the
nine supplier hulls re-based silently and `check_pack_fidelity` proved them.
Two files joined the pack (1203). Nothing new was placed: every unit the
game added is out of service in 2028. The day after, the Steam
announcement named two units the game had dropped (its KC-135A and Tu-16N
stubs) that the overlaying export had left in `_vanilla/original`; deleted
by hand, the drift tool found the three RAAF bases that generated the
KC-135A, and the Tu-16N standing because a Workshop mod ships it - which
is why a removed vanilla unit another mod still ships is reported, not a
finding.

The day after that, the announcement's two system changes were taken up
(Southern Watch build notes, *Combat systems and the CIWS model*): SEST
profiles for every hull the campaigns field that declared none, the fielded
mod CIWS retuned onto the new keys, and - found on the way - four aircraft
mods' stale copies of the game's whole `weapons.ini`, which had been hiding
the 0.8.3 model on every vanilla AK-630 and Phalanx; Collection Fixes now
restores the game's 66 affected sections. The pattern for the next update:
when the drift tool reports a MERGED change in `systems/weapons.ini`, look
at who else defines the section, because a stale whole-file copy in an
unrelated mod outranks the game. A pack section that carries vanilla's new
value is a MIRROR in that report, not a clash. 1265 files; 1257 by the
afternoon, when the PLAN Pack's own update declared systems on its eight
hulls and the extend guard retired ours - the second pattern for next time:
a mod that takes up a game feature itself retires the SEST stand-in, and the
guards are what make that a build stop rather than a doubled block. The game
was 0.8.4 Build 261002 by then (2 Oct, two fixes), caught by
`check_game_version` on the export and bumped.

### The 0.9.0 run, 13 November 2026

The game went to 0.9.0 Build 261111 on 11 Nov. The PC's export came on a
branch of its own (`chore/vanilla-export-090-pc`, `8f3e4bc6`), cut from the
deploy branch, so its paths were taken in on top of the combined release
(`3a2c26944`) rather than merged: 4,505 text files under
`_vanilla/original` (4,049 before), 456 added, 1,113 changed. Steps 2 to 8
followed on `claude/continue-previous-session-39wqwq`.

The difference from 0.8.3 is the lesson. Then, five builders stopped where
their own checks said. This time **no builder stopped**, the drift tool
passed, and 13 of the 14 checks were green on the first rebuild; the one
red check was the Workshop ranges no bump can fix (Coordinated Strike Tool
and Dynamic Campaign Mod both end below 0.9.0). The builders' guards catch
a donor that changes shape. They do not catch a game value that moves under
somebody's old copy, or a key the game adds to its own files and nobody
else's. Everything below was found by reading the game's diff against what
depends on it, by eight read-only investigations run side by side:

- **A stale whole-file copy, in another file.** The 0.8.3 run ended with
  "when the drift tool reports a MERGED change in `systems/weapons.ini`,
  look at who else defines the section". 0.9.0 did the same thing in
  `systems/combatsystems.ini`: two mods ship the game's whole file, their
  copies were the game's text until this update, and the ten profiles
  0.9.0 changed would have stayed at the old values. Collection Fixes
  restores them (`STALE_COMBAT_COPIES`), and one sensor section the same
  way. The check to repeat is not per file: for every `systems/` file the
  update changed, compare each mod's copy of a changed section with the
  game's text at the *previous* export. A copy equal to the old text was
  harmless yesterday and is a mask today.
- **Typed-in figures set against the game's own.** The eleven retuned mod
  CIWS are numbers written on 3 Oct beside the game's guns of that day;
  0.9.0 rebalanced the game's guns and nothing compared the two. They are
  deliberately not moved (Southern Watch build notes, *Sea Power 0.9.0*),
  but the build now prints the difference every time
  (`ciws_ladder_notice`). A table that says "vanilla's figures" should read
  them at build time or check them.
- **New game files under a mod's path.** Thirteen of the 103 new unit and
  round files have a path a subscribed mod already ships, so the mod's
  file loads. The drift report now marks them OUTRANKED.
- **Keys the game added to its own campaigns.** The campaign builder passed
  because nothing it writes was removed. Reading the stock campaigns' diff
  found four keys worth writing as the game writes them (the map UI, the
  single task force, the staging airfield, the Campaign Mission flag) and
  the game's new Royal Navy insignia.
- **A directive the game had not used before.** Three new stock units are
  `#!copy` files with no `[General]` of their own; the cost inventory
  passed over such files, as it had over nine mod units since October. It
  reads the directive now. The world campaign's roster reader still does
  not, so the three are not on its buy list.
- **Prices by the wrong model.** New ships named like nothing the cost
  rules knew were priced as merchant hulls or generic destroyers; 60
  reviewed comparators and five rule fixes followed.
- **Texts.** SETUP told every 0.9.0 player the game was "not recognised";
  the shipped notes, the Steam texts and four Steam cards called 0.8.7 the
  current game. The world campaign's read-me had said 1,586 buy entries
  through two rebuilds that moved the number, and now takes it from the
  build.

What could not be done here, and waits for the PC:

- **SEST's code.** Every SEST plugin is matched to a game file by SHA-256
  and none is matched to 0.9.0, whose `Seapower-Scripts.dll` hash is in no
  file in this repository. On the PC's one captured 0.9.0 launch nothing of
  SEST's loaded. The way back starts with `tools\capture-beta-references.ps1`
  on the 0.9.0 PC (it refuses only the old 0.8.7 release's file and a
  running game, and changes nothing).
- **The PC toolkit.** `Prepare-PC.cmd` of `docs/releases/20261107` imports
  the release and then stops, at the latest inside the beta repair, whose
  reference check starts with the game file it was built for, so it never
  reaches the data install or the VERIFIED line; `Repair-PC.cmd` stops the
  same way after renaming `enable.flag`. A data release for 0.9.0 needs a
  toolkit path that does not go through the beta repair.
- **Whether the game applies a Workshop mod's `#!extend` files on 0.9.0.**
  On the 0.8.7 betas it did not while Anchor Chain's preloader was
  installed, unless SEST's Runtime repaired the scan; that Runtime does not
  load on 0.9.0. One Mission Editor look settles it (Southern Watch card,
  RU.2).
- **Files the game dropped.** The export overlays and deletes nothing, so
  the block under *What the export cannot tell you* still has to be run on
  the PC for 0.9.0. The changelog says scenarios were removed; the export
  shows none gone.

Two tools came out of it. `tools/refresh_upload_manifest.py` writes the
release's upload manifest from the built pack, which until now no script in
the repository did, and a test holds the committed manifest to the built
pack. `tools/preflight.py` no longer reads a zone's `Type=Deployment` as a
unit, so the single-mission check works on campaign missions.

The pack after the run: 4,592 files (4,583 on the 12 Nov capture), 243 of
them `#!extend` or `#!prepend` files; 1,633 entries on the world campaign's
buy list (1,593); 4,547 cost rows (4,448). Thirteen of the 14 checks pass,
and `check_game_version` is red on the two Workshop ranges and on nothing
else. A second `build_all.py --from-scratch` left the tree clean. None of
it has been run in the game.

### What the update does to a Task Force Mode save

Not known yet, but since 3 Oct there is a save to find out with. The 3 Oct
snapshot (`-IncludeSaves`) carries `saves/NEW TEST 1.sav`, 51 KB, written at
01:55 that morning: a Task Force Mode save of **Southern Watch (Open
Allocation)** (`#!alias campaigns/sest-southern-watch-open/campaign.ini`)
holding the post-state of mission 2 - per-ship sections with every
magazine's remaining count and the in-game clock at 18 Oct 2028. It was
written under 0.8.3 or 0.8.4 (the game moved to 0.8.4 Build 261002 on 2
Oct) and is the first evidence that an authored campaign carries state
between missions as the stock one does. Whether it reopens after the 3 Oct
rebuild - the PLAN Pack's hulls gained combat systems and the SEST pack
changed under it - is the player's to report. Before that the repo had no
record of one: the campaigns were built against 0.8.2, and the snapshot's
`campaign-saves.txt` listed two stock campaign saves beside that game, one
from 24 Apr 2026, before 0.8.0, and one from 15 Aug, without recording
whether the April one still opens. The changelog's other `Save/Load` lines
are fixes and additions to what a save carries (reloaded aircraft losing
livery, callsign and loadouts; sonobuoy timers; sensors re-enabled after a
load and breaking EMCON; survivor rescue), not a statement about saves
across versions. The
one line that speaks to it, in 0.7.9 Build #321 of 25 Mar 2026, is
`Save/Load of formation control mode (will not work for old saves)`: the old
save loaded, without the new behaviour, for that one feature. What the repo
does say is about its own changes, not the game's: a mission-file change
needs nothing (continue the campaign, as after the Rig Seventeen fix); a
new campaign entry (The Twelve-Mile Line) means a campaign already past
that point should be started again; a `campaign.ini` value changed under a
running campaign may not reach it (the same-nation discount, test card G.6).
A game update that changes a stock unit a saved force holds is the case
none of those cover.

So before anything plays on the new build, capture with `-IncludeSaves`
(`capture-context.ps1 -Redact -IncludeSaves`, game closed): it copies the
campaign saves first, then the newest mission saves, up to six files, into
`data\install-snapshot\saves\`, the only copy outside the game's folder and
Steam Cloud. Then continue the campaign and report what happens; Southern
Watch test card 6.4 (save mid-campaign, quit, reload) is the check, and
*When something is wrong* in the install guide has the capture command for
a mission that dies loading.

**21 Oct 2026: `NEW TEST 1.sav` is orphaned.** The Open Allocation versions
left the pack that day (`docs/campaigns/southern-watch/build-notes.md`,
"Open Allocation retired from the pack"), so
`campaigns/sest-southern-watch-open/` is no longer installed and the save's
alias names a campaign that is not there. It cannot be continued, and
neither can any player's save in an Open Allocation version: the standard
campaign keeps its own progress (test card G.4) and is where to start
again. What the game does with an orphaned save - hide it, refuse it, or
break the campaign menu - is not known; the play-test guide's *Orphaned
save* row asks. The snapshot keeps the file as the record.

### The Workshop mods' own declarations

The Mod Manager reads `[Compatibility]` from every mod's `_info.ini`. The
rule, as the stock comment carried in 105 of the exported manifests states
it, is that `ApproximateVersion` "checks MAJOR and MINOR match but will
accept higher PATCH", and overrides the range keys when both are present.
Of the 148 exported mods, 121 declare an `ApproximateVersion`, so on a
0.9.x game every one of them fails that check, as the SEST packs did when
they declared 0.6.8 against a 0.8.x game
(`docs/interoperability-report.md` records the flag the Mod Manager
showed; what a flag costs beyond the mark is not recorded here). Eight
declare a range instead, two of them with an upper bound: Anchor Chain
(3380210757) admits `0.4.0 <= v < 1.0.0`, and Coordinated Strike Tool
(3806686336) admits `0.8.2 <= v < 0.9.0`, so a 0.9.x game marks it
incompatible until its author widens the range and the next export brings
the new manifest; nothing in this repo can change that, and
`check_game_version.py` exits 1 on it until then. Another 18 have no
`[Compatibility]` section at all, and one, Boeing P-8 Poseidon
(3602046770), ships no `_info.ini`, so there is nothing for the check to fail
them on; what the Mod Manager shows for them is not recorded here
(`grep -L '\[Compatibility\]' mods-source/*/_info.ini` lists the 18).
The export is what brings an author's new declaration here, so a Workshop
exclusion that persists after an update is a reason to re-export, not a
reason to edit `mods-source`.

## Pre-flight

Six checks, all offline, all exit non-zero on failure. Run them after any
subscribe, unsubscribe or reorder, and after the export's `check_inventory.py`
above:

```powershell
python tools\check_load_order.py       # no mod outranks a SEST pack, in the canonical order and in the captured live one
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
