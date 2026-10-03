# Packaging, dependencies and recovery

Two questions this answers: how the SEST packs coexist with 144 workshop mods,
and what you actually need to be able to recover if the game install goes bad.

## A SEST pack is a patch, not a mod

The patch packs ship **nothing but `.ini` files** — not a single model,
texture or asset bundle among them. Only the campaign pack adds anything else:
its campaign pages, briefing maps, art and mod lists. Check it yourself (the
filter leaves out the campaign pack and the built `dist` copy):

```powershell
Get-ChildItem integration\*\SEST_* -Recurse -File |
  Where-Object { $_.FullName -notmatch '\\(campaign|dist)\\' } |
  Group-Object Extension
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
own files. `tools/consolidate_packs.py` builds it from every source pack; Sea
Power's Mod Manager lists it as one entry, SEST Integration Pack, beside the
workshop entries, and it takes part in the same load order.

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\install-sest-packs.ps1 -WhatIfOnly   # dry run
powershell -ExecutionPolicy Bypass -File .\tools\install-sest-packs.ps1              # apply
# game closed: -AddMissing puts a newly installed pack at the top, enabled
powershell -ExecutionPolicy Bypass -File .\tools\set-mod-order.ps1 -AddMissing
```

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

**After a session pushes work:**
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

### Known red: `check_inventory` on four line-ending mods, the missing Rafale, and Auto Time-on-Target

`check_inventory.py` exits 1 on this branch. Since 3 Oct it also names
`3789793270`, Auto Time-on-Target, as missing from the catalogue's active set
and from the order while its folder is still on disk: the player unsubscribed
it that day and the repo retired it the same day, ahead of the export that
will prune the folder. That red clears on the next `export-mod-configs.ps1`
push and needs no other action. The mirrored export ran on the
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

**The Rafale (since 30 Sep).** The Dassault Rafale mod (`3504168760`) left
the PC's Steam subscriptions between the 27 and 28 Sep snapshots, and the 30
Sep export pruned `mods-source/3504168760` once Steam had deleted the folder.
The catalog and the canonical order still carry it, Southern Watch's D3 and
D6 place it, the Open Allocation allied fleet sells it and SEST Rafale F5
patches it, so `check_inventory` reports it as an extra in the catalog and
the order, and `check_campaign_coverage`, `check_dependencies` and
`preflight --all` fail wherever they meet its files. The pack is built with
the last export that had the mod: `git archive e0d961d7~1
mods-source/3504168760 | tar -x`, then `python3 tools/build_all.py
--from-scratch`, then delete the folder again. Resubscribing and
re-exporting clears all four; if the mod is gone from the Workshop, the
Rafale is retired from the campaigns and the pack instead.

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

## After a Sea Power update

A game update moves the one thing every pack and mission here is built on
and nobody exports on purpose: the game's own files. Three things in this
repo track them. `mods-source/_vanilla/original` is the vanilla export: on 2
Oct 2026, 4,051 text files from 0.8.3 Build 261001 of 1 Oct 2026, the version
and build being the first `dd-Mon-yyyy: X.Y.Z Build #N` line of
`data/install-snapshot/changelog.live.txt`, the game's own `changelog.txt`
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
the drift, bumping, rebuilding and gating, then the usual sync.

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
  git checkout sest-dev/loving-bell-3cnvvw
  if ($LASTEXITCODE) { throw 'checkout failed' }
  git pull --ff-only origin sest-dev/loving-bell-3cnvvw
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
  git push origin sest-dev/loving-bell-3cnvvw
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

### In the repo: read the drift, bump the version, rebuild, gate, document, push

1. **Note the baseline, then merge the deploy branch.** The drift tool's
   default baseline is the last commit that touched the export, which after
   the merge is the PC's own, so record the one before it first:

   ```bash
   git log -1 --format=%h -- mods-source/_vanilla/original   # the drift baseline: a4d3c1c1 on 2 Oct 2026
   git fetch origin
   git merge origin/sest-dev/loving-bell-3cnvvw
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

4. **Rebuild everything.**

   ```bash
   python3 tools/build_all.py --from-scratch           # about 90 s; 20 packs, then the consolidated dist
   ```

5. **Every gate.** Known red on this branch: `check_inventory.py` on the
   four line-ending mods (3775128499, 3776340577, 3780118683, 3781062859)
   and, until it is resolved, the Rafale (3504168760), which also reddens
   `check_campaign_coverage`, `check_dependencies` and `preflight --all`
   wherever they meet its files, and one test in `test_build_pack.py`
   (`AlliedFleet`, on `fr_rafale_m_l`). *Known red* above has both stories.
   Anything else red is the update's, and step 2's report says where.

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
   ```

7. **Regenerate the derived docs, then update the hand-written ones.**

   ```bash
   python3 tools/generate_load_order.py      # docs/load-order-full.md
   python3 tools/generate_catalog.py         # docs/mod-catalog.md
   find integration/dist/SEST_Integration -type f | wc -l   # the installed file count: 1265 on 3 Oct 2026
   ```

   By hand: the install guide's count, if it moved - the `IN LINE: all 1265
   installed files` line under *Already aligned once?*, `N is 1265` in
   step 4 of `docs/campaigns/southern-reach/install-alignment.md` and the
   derivation under that table, which ends `1265 with the combat systems`
   and gains a clause for what the update added or removed - and
   `Consolidated, they are 1265 files` in `README.md`;
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
   git push origin claude/campaign-missions-lore-td653z     # or the session's branch
   ```

9. **Then the PC runs the standard update block** (*Already aligned once?*
   in `docs/campaigns/southern-reach/install-alignment.md`): it
   fast-forwards the deploy branch to the session's and syncs, and its last
   line must read `IN LINE: all 1265 installed files match this commit`, or
   the new count from step 7.

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
value is a MIRROR in that report, not a clash. 1265 files.

### What the update does to a Task Force Mode save

Not known. The repo has no record of a Task Force Mode save carried across
a game update: the campaigns were built against 0.8.2, and the snapshot's
`campaign-saves.txt` lists two stock campaign saves beside that game, one
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

### The Workshop mods' own declarations

The Mod Manager reads `[Compatibility]` from every mod's `_info.ini`. The
rule, as the stock comment carried in 102 of the exported manifests states
it, is that `ApproximateVersion` "checks MAJOR and MINOR match but will
accept higher PATCH", and overrides the range keys when both are present.
Of the 144 exported mods, 118 declare an `ApproximateVersion`, so on a
0.9.x game every one of them fails that check, as the SEST packs did when
they declared 0.6.8 against a 0.8.x game
(`docs/interoperability-report.md` records the flag the Mod Manager
showed; what a flag costs beyond the mark is not recorded here). Eight
declare a range instead, two of them with an upper bound: Anchor Chain
(3380210757) admits `0.4.0 <= v < 1.0.0`, and Coordinated Strike Tool
(3806686336) admits `0.8.2 <= v < 0.9.0`, so a 0.9.x game marks it
incompatible until its author widens the range and the next export brings
the new manifest; nothing in this repo can change that, and
`check_game_version.py` exits 1 on it until then. The other 18 have no
`[Compatibility]` section at all, so there is nothing for the check to fail
them on; what the Mod Manager shows for them is not recorded here
(`grep -L '\[Compatibility\]' mods-source/*/_info.ini` lists them).
The export is what brings an author's new declaration here, so a Workshop
exclusion that persists after an update is a reason to re-export, not a
reason to edit `mods-source`.

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
