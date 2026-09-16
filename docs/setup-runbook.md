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

Close Sea Power before changing its settings or installing. Check `git status` and
preserve any local mission or export changes before switching branches or pulling.
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

## Check in game

Open the active mission, **NORTHERN FRONT III FINAL NEWEST**, and a small generated
scenario. Check the Burke loadouts, B-1/B-52 availability, F-35/F-15/Growler upgrade
fits, carrier aircraft operations, and a replenishment transfer. Check the new
CH-53E, RQ-180, F-2A, J-16, MiG-31 and J-36 for their models and intended loadouts.
Report the unit ID, loadout, enabled order and observed failure if something differs.

`data/active-mission.txt` selects the default mission. `data/deploy-missions.txt`
selects what the installer copies, including a historical backup for recovery.
Backup missions retain their historical references and are not covered by the
current playable-mission validation results.

After editing in game, close it and use `tools/import-mission.ps1` to capture the
save. `tools/refresh-mission.ps1` additionally runs the mission transformation
scripts; review their diff before installation or committing. Keep mission changes
on the intended feature branch and avoid pushing directly to the default branch.
