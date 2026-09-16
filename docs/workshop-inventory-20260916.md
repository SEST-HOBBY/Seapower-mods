# Workshop inventory reconciliation — 16 September 2026

This branch contains a **provisional source snapshot**, not an install-ready release.
The supplied archive and its own export manifest disagree about file contents.
Do not merge or deploy this snapshot until a fresh export passes the inventory audit.

## What the counts mean

| Evidence | Workshop IDs | Local SEST entries | Total |
|---|---:|---:|---:|
| Supplied PC Mod Manager output | 137 | 1 | 138 |
| Supplied export manifest | 137 | Excluded by exporter | 137 |
| Numeric folders in the supplied ZIP | 137 | Excluded by exporter | 137 |
| Reconciled canonical order | 137 | 1 | 138 |
| Steam account UI, reported by user | 139, unverified | Not applicable | 139, unverified |

The 137 IDs in the export exactly match the 137 Workshop IDs in the supplied
enabled PC order. `SEST_Integration` is installed under StreamingAssets and accounts
for the 138th Mod Manager entry. Its 19 source packs consolidate into that single
entry; they are not 19 additional subscriptions. The earlier expected count of 132
does not describe this captured inventory.

If Steam's 139 is the same game's current subscription count, it is two above the
local Workshop inventory. The account's actual 139-ID list is needed to name the
difference; local folders cannot establish current subscription state. An item may
be subscribed without local content, and retained local content does not prove a
subscription. No Steam account access or direct PC execution was performed here.

The P-8 item `3602046770` has a blank manifest display name and no `_info.ini`.
It is counted by ID and does not explain the discrepancy. The observed order is
preserved separately in `data/observed-load-order-20260916.tokens.txt`.

## Changes from the repository's previous export

The base is `feature/ras-integration` at `56eff5bce1be7a954b309b94320e5c5e19c89d43`.
That export had 127 IDs: four restored folders plus seven new folders, minus one
absent folder, produce the observed 137. The previous catalog already listed B-1B
and B-52H as active, so catalog additions and folder additions had different counts.

| ID | Item | Reconciliation |
|---|---|---|
| 3652097318 | B-1B Lancer | Source restored |
| 3741944366 | B-52H | Source restored |
| 3663564190 | Fujian CV-18 | Source and active catalog status restored; RAS coverage restored |
| 3673250557 | Saab AEW&C / GlobalEye | Source and active catalog status restored |
| 3755769170 | F-2A Viper Zero | Added |
| 3769142422 | J-16 Qianlong | Added; distinct from the older J-16 item 3506979898 |
| 3789188689 | PLA & PLAN & PLAAF AEP | Added |
| 3796113927 | RQ-180 White Bat | Added |
| 3799742828 | MiG-31 Foxhound | Added |
| 3801363152 | CH-53E Standalone | Added |
| 3801549552 | J-36 | Added |
| 3654230227 | AI Doctrine Overhaul | Absent from both PC lists; the user confirmed it is unsubscribed on 2026-09-16, so catalog status `unsubscribed` |

The catalog now retains 141 records: 137 in the local inventory and four historical
entries. Deprecated/WIP labels describe mod quality and do not remove an observed
installed item from the inventory.

## Archive integrity finding

Input: `Seapower-mod-export-20260916-170443.zip`.
SHA-256: `691fa0e5d52891387b3d96f0f806c637847b349b3ad7fd21a8d62ad51594b9d0`.
Archive CRC checks passed. Windows separators were normalized during extraction;
all 8,624 supplied files, including the manifest, match the imported bytes.
The existing `_vanilla` reference was retained; this upload contains no new vanilla export.

The manifest records **8,453 mod files / 78,121,914 bytes**. The ZIP actually contains
**8,623 mod files / 80,811,573 bytes**: 170 extra files and 2,689,659 extra bytes.

| Workshop ID | Mod | Manifest files | Archive files | Excess |
|---|---|---:|---:|---:|
| 3390330875 | Modern US Navy | 253 | 285 | 32 |
| 3444379330 | Dutch Navy | 55 | 58 | 3 |
| 3505420313 | Italian Navy | 263 | 327 | 64 |
| 3567256221 | French Navy | 288 | 289 | 1 |
| 3599752717 | Modern British Navy | 111 | 112 | 1 |
| 3606774881 | U.S. Navy 2027 | 78 | 94 | 16 |
| 3607989779 | F-35C Alt. Loadouts | 25 | 26 | 1 |
| 3629144864 | Euromod | 522 | 565 | 43 |
| 3695809489 | JMSDF | 37 | 42 | 5 |
| 3737267013 | US Naval Aviation | 231 | 235 | 4 |

The previous exporter copied over existing folders without removing paths upstream
had deleted. That defect can produce exactly this kind of stale overlay. The counts
prove a mismatch; they do not identify the individual obsolete paths. Accordingly,
the supplied files are preserved and the manifest totals are not rewritten to make
the check pass. Build and conflict results below describe this provisional snapshot.

The repaired exporter stages fresh folders, keeps replaced data in `_export-backups`,
and restores the previous snapshot if publication fails. It also writes per-file
SHA-256 records to `_export-files.csv`. `-NoPrune` retains absent mod folders only;
present mods are still refreshed completely. A crash during publication may require
manual restoration from the printed backup directory. Neither Steam content nor
account subscriptions are changed.

## Load order and interoperability

The captured PC order is the starting point. Two deliberate adjustments are made:

- CH-53E is above Euromod and US Naval Aviation, as its included installation README
  explicitly requires. Both dependencies are present.
- Red Storm Arsenal is last, retaining the repository's existing specialist-over-bulk
  priority rule. SEST remains first.

PLA AEP retains its relative PC placement. It overlaps 17 ammunition files with the
PLA land pack, PLAN pack and Fujian; moving it up into a framework tier would change
those winners. Its code/binary behavior and preferred priority still need in-game
review. F-2A, J-16 Qianlong, MiG-31 and CH-53E have no whole-file config collisions
in this snapshot. Shared systems files may still contain competing keys; a
whole-file collision check is not proof of runtime compatibility.

The load-order generator now renders both documentation and the preview directly
from canonical tokens, so an independent tier list cannot silently reintroduce an
absent mod or disagree with what `set-mod-order.ps1` applies.

The active mission's obsolete Burke `MST` loadout is updated to the upstream
`≥125_MST` name. NORTHERN FRONT II also receives the corresponding Flight IIA loadout
names and the corrected Growler `usn_ea-18g_2020` ID. The 11 carved scenarios are
regenerated from the active parent, including older parent edits that had not yet
reached the generated copies. Historical mission backup files are retained.

## Validation and remaining gates

- All 19 SEST source packs rebuild and consolidate successfully. A second clean
  build reproduces the same hashes for all 1,049 generated files.
- The active mission resolves all 691 checked references after the loadout fix.
- NORTHERN FRONT II resolves all 537 checked references after its four corrections.
- All 11 generated scenarios and the SEST ANL Convoy mission also pass reference
  preflight; the scenario structure check covers 348 unit sections.
- SEST load-order, dependency, scenario-structure and patch-fidelity checks pass
  against the supplied snapshot. Dependency diagnostics still report inherited
  upstream issues separately; these are not a claim that every third-party mod works.
- The RAS documentation is updated to this build: 2,075 launchers on 277 hulls,
  88 metered rounds, and 137 exported mods. These counts may change after re-export.
- Seven Python inventory regression fixtures pass, including equal-count/different-ID
  lists, obsolete files, duplicate IDs, case collisions and per-file hash drift.
- `python3 tools/check_inventory.py` deliberately fails on the ten folder/manifest
  mismatches above. That is an unresolved input defect, not a waived check.
- The PowerShell exporter has a standalone fixture script at
  `tools/tests/test-export-mod-configs.ps1` covering backups, rollback, refresh,
  pruning, hashes and overlap rejection. A PowerShell runtime is unavailable in
  this workspace, so that script and real Windows behavior have not been executed.
- Game launch, models/textures, preloaders and live Steam account subscriptions
  cannot be verified from a text-only export.

## Obtain an uncontaminated replacement

From the existing PC checkout, this works even with the old exporter because the
destination is new and empty. It leaves the current checkout export untouched:

```powershell
$fresh = Join-Path $env:TEMP ('Seapower-clean-' + [guid]::NewGuid().ToString('N'))
powershell -ExecutionPolicy Bypass -File .\tools\export-mod-configs.ps1 -DestDir $fresh
if ($LASTEXITCODE -ne 0) { throw 'Export failed; do not package it.' }
Compress-Archive -Path (Join-Path $fresh '*') -DestinationPath ($fresh + '.zip')
Write-Host ($fresh + '.zip')
```

Reconcile that replacement with `check_inventory.py`, rebuild, then repeat the
checks before considering deployment. Separately obtain the 139 Steam account IDs
to resolve the reported subscription difference by ID rather than by count.
