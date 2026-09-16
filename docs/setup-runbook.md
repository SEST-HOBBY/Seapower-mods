# Setup runbook — local inventory and SEST Integration

The 16 September 2026 PC evidence contains **137 Workshop mods plus one local SEST
Integration Pack**, giving 138 Mod Manager entries. The registry contains 19 SEST
source packs, all consolidated into that one installed pack. Workshop mods supply
the original assets and remain separate installations.

**This review snapshot is provisional.** Its archive contains 170 more files than
its manifest records. Complete the [inventory audit's replacement-export steps](workshop-inventory-20260916.md)
and the checks below before installing it. The PowerShell exporter also needs its
Windows fixture run. Do not unsubscribe mods to force an older expected count.

## Preserve the PC state

Close Sea Power before changing its settings or installing: it rewrites
`usersettings.ini` on exit, so anything the tooling writes while the game is open is
silently thrown away, and every script that touches that file checks and refuses.
Check `git status` and preserve any local mission or export changes before switching
branches or pulling.
Keep the current Mod Manager order as a rollback reference. Review changes in a
separate checkout when the playing checkout has uncommitted work.

`data/observed-load-order-20260916.tokens.txt` preserves the supplied PC order.
`data/load-order.tokens.txt` is the reconciled order the installer uses. These serve
different purposes; the observed list is evidence, not an alternate installation list.

## Refresh the export and validate

The corrected exporter inventories numeric local Workshop folders. It stages fresh
copies and retains the previous snapshot under `_export-backups` beside the export
directory. `_export-files.csv` adds exact paths, sizes and SHA-256 hashes. It cannot
query the live Steam account subscription list. `-NoPrune` retains absent folders
for investigation; such extras will fail the inventory check.

After the replacement export has been reconciled into the review checkout, run:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\tests\test-export-mod-configs.ps1
if ($LASTEXITCODE -ne 0) { throw 'Exporter fixture failed.' }
python tools\check_inventory.py
if ($LASTEXITCODE -ne 0) { throw 'Resolve the export mismatch before building.' }
python tools\build_all.py --from-scratch
if ($LASTEXITCODE -ne 0) { throw 'SEST build failed.' }
foreach ($check in @('check_load_order', 'check_dependencies', 'preflight', 'check_scenarios', 'check_pack_fidelity', 'check_docs')) {
    python (Join-Path 'tools' ($check + '.py'))
    if ($LASTEXITCODE -ne 0) { throw ($check + ' failed.') }
}
```

The checks resolve configuration references and deliberate SEST overrides. They
cannot verify model/texture bundles, preloader installation or runtime behavior.
Follow the current Anchor Chain and SeaLifter installation instructions for the
mods that require them; seeing one aircraft in the editor is not a complete loader test.

## Install an approved, validated build

With the game closed, preview the installation and order:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\install-sest-packs.ps1 -WhatIfOnly
powershell -ExecutionPolicy Bypass -File .\tools\set-mod-order.ps1 -AddMissing -DryRun
```

After reviewing the preview:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\install-sest-packs.ps1
powershell -ExecutionPolicy Bypass -File .\tools\set-mod-order.ps1 -AddMissing
powershell -ExecutionPolicy Bypass -File .\tools\show-load-order.ps1
```

Expect **one SEST entry at the very top**. The installer mirrors
`integration/dist/SEST_Integration` and removes superseded individual `SEST_*`
installation folders. The per-pack repository folders are build inputs, not
additional mods to install. The order script backs up the settings, preserves
existing enabled flags and retains unknown items for review; it does not subscribe
to missing Workshop items. Consult [the generated complete order](load-order-full.md)
rather than an independent tier list.

CH-53E must be above Euromod and US Naval Aviation, following its supplied README.
SEST outranks all Workshop content; Red Storm Arsenal stays last. Changing PLA AEP's
position affects 17 shared ammunition files and needs a deliberate compatibility test.

The other author-mandated placements the canonical order encodes, if you ever
reorder by hand (top of the list wins when two mods ship the same file):

- **Anchor Chain** at the very top of the Workshop mods (SeaLifter loads via its preloader).
- **Dingtools Weapon Pack** above every dingtools mod: F-15EX, B-52H, B-1B, SAAB AEW&C.
- **PLA Land Unit Pack** above every PLA-related mod; **SAM Pack** near the top.
- **Airbases last** - SEST RAAF Bases, Modern US / Russian / Chinese Airbase.

## Keeping the install in step

Once installed and ordered the first time, the whole update loop is one command,
game closed:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\sync-sest.ps1
```

It pulls, installs the consolidated pack, and rewrites the mod order, inserting any
newly installed pack as enabled at its canonical position. It resolves the one merge
conflict this workflow keeps producing (a mission you imported while the tooling
changed the same file): your imported copy wins, and `-RefreshMissions` re-runs the
tooling on top. A conflict in any other file stops the script for you to handle.

Re-run the order fix **every time you change which mods are ticked.** Sea Power owns
`usersettings.ini` while it runs and rewrites the whole `[LoadOrder]` section on exit,
so ticking a mod in the Mod Manager always leaves you with the game's ordering, not
yours. `fix-load-order.ps1` waits for the game to quit and applies the canonical
order the moment it does:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\fix-load-order.ps1            # waits for the game to exit
powershell -ExecutionPolicy Bypass -File .\tools\fix-load-order.ps1 -NoWait    # game already closed
powershell -ExecutionPolicy Bypass -File .\tools\fix-load-order.ps1 -NoWait -DryRun
```

It first reports what the Mod Manager did - entries moved, anything not in the
canonical list, any SEST pack left disabled - then applies the order.
`set-mod-order.ps1 -AddMissing` is the same fix without the waiting.

## Check in game

Open the active mission, **NORTHERN FRONT III FINAL NEWEST**, and a small generated
scenario. Ten minutes covers the packs that are easiest to break silently:

1. **Modern Growlers** - AN/ALQ-249 is listed; NGJ MALICE and NGJ MALICE Heavy are selectable.
2. **F/A-18F Block III** - Block III MALICE is selectable with four AIM-424s.
3. **F-15EX** - the picker includes AntiShipLRASM6, AntiShipHarpoon, StrikeQuicksink and Intercept174.
4. **Ford (JSF variant)** - F-35C flights offer *Intercept (AIM-260, stealth)* and *Intercept Beast*.
5. **RAAF F-35A** - three Intercept fits present.
6. **Place RAAF Base Williamtown** - F-35As and E-7As spawn (default E-7A livery is expected).
7. **Place RAAF Base Tindal** - B-52H present; **Amberley** - B-1B present. The B-2 also re-proves the loaders.
8. **Spawn HMAS Hobart** - Australian ensign shows, MH-60R on deck. **HMAS Canberra** - helicopter-only air group operates.
9. **A Burke** - the `≥125_` loadout names resolve; **a replenishment transfer** completes.
10. **The new mods** - CH-53E, RQ-180, F-2A, J-16 Qianlong, MiG-31, J-36 show their models and intended loadouts.

Anything that fails: note which step and paste what you see - every SEST pack
regenerates from a script, so fixes are fast and versioned. Report the unit ID,
loadout, enabled order and observed failure.

`data/active-mission.txt` selects the default mission - every mission script and
`refresh-mission.ps1` / `import-mission.ps1` read that one file, so switching
development to another scenario is a one-line edit there rather than five drifting
defaults. `data/deploy-missions.txt` selects what the installer copies, including a
historical backup for recovery.
Backup missions retain their historical references and are not covered by the
current playable-mission validation results.

After editing in game, close it and use `tools/import-mission.ps1` to capture the
save. `tools/refresh-mission.ps1` additionally runs the mission transformation
scripts; review their diff before installation or committing. Keep mission changes
on the intended feature branch and avoid pushing directly to the default branch.
