# Banda Front Lean verification — 19 September 2026

The handover starts at `5ac8e449f681e49667c2e1bc11717f8e2b51bb83` on
`sest-dev/beautiful-cerf-i7fqei`. The follow-up branch is
`fix/banda-front-lean-finalize`.

The saved four-reviewer journal is not in the repository, and GitHub has no
check runs for that commit. The checks below were performed independently.

## Result

`SEST Banda Front Lean.ini` is byte-identical to the original committed Lean
output. `SEST Banda Front edited.ini` is untouched. The follow-up fixes the
reusable transformation and adds regression coverage; it does not retune the
mission or install other packs.

| Side | Land units in the edited save | Land units in Lean |
|---|---:|---:|
| Taskforce1 | 241 | 100 |
| Taskforce2 | 413 | 184 |
| Neutral | 140 | 112 |
| Total | 794 | 396 |

All 110 formations remain, including 106 land formations. All eight land units
outside formations remain. All 63 existing ships and aircraft are unchanged,
as are surviving land-unit positions, headings, types, and blue/red air groups.
Fifteen neutral airfields and helicopter rigs have explicitly empty air groups.
The 25 already-placed neutral aircraft remain.

## Follow-up fixes

- A guidance radar or launcher outside a formation no longer causes a
  `None` formation-index crash. A battery with an unformed radar is considered
  under its first formed launcher; retained launchers keep their associated
  radar, including when either member is outside a formation.
- BMD keep decisions are recorded against each unit's own formation. A wholly
  unformed battery remains intact.
- Removing land units from one side preserves newly added units belonging to
  the other side instead of failing with a mapping `KeyError`.

## Verification

| Check | Result |
|---|---|
| Regression suite | 9 tests pass: removal, references, air groups, unformed batteries, and full mission regeneration |
| Repeated regeneration in a temporary directory | Identical bytes on both runs and identical to the committed Lean file; edited input unchanged |
| Mission structure | Counts, dense unit numbering, formation references, and language references pass |
| `preflight.py "SEST Banda Front Lean"` | 754 references resolve |
| `build_all.py --from-scratch` | All 17 builders and consolidation complete; no generated content diff after Git's newline normalization |
| `check_load_order.py` | 46 overlaps checked across 133 order entries; all SEST overrides outrank their donors |
| `check_dependencies.py` | Required upstream mods are exported and ordered |
| `check_weapon_employment.py` | Eight distinct findings, identical across original, edited, and Lean missions; this gate remains red |
| `check_alias_bases.py` | Unit-base check exits successfully but reports existing ammunition/base warnings |

The rebuild produces CRLF instead of the committed LF in both copies of
`usn_ddg_arleigh_flt3_2027_variants.ini`. Their contents match after newline
normalization. Those unrelated generated files are not changed by this follow-up.

The eight weapon findings are two land-launcher guidance-channel findings
(NASAMS and SLAMRAAM), three MLRS magazine references, the Su-57 KH-58 position
group, the F-4E CAS station count, and the SEST Growler gun-magazine reference.
They are recorded rather than waived or folded into a mission-trimming change.

The source save also places 32 of the 41 retained externally guided launchers
outside their configured radar search radius. The trimmer retains radar
associations without moving the user's units. Retaining a radar does not prove
that a distant launcher can use it in game. Geometry and weapon-employment
repairs remain separate work; no in-game performance or firing test was possible
in this environment.

Reproduce the focused checks from the repository root:

```bash
python3 -m unittest discover -s tools/tests -p 'test_trim_land_sites.py' -v
python3 tools/preflight.py "SEST Banda Front Lean"
python3 integration/missions/trim_land_sites.py --dry-run
```

## Handoff when GitHub publication is unavailable

At handover the GitHub connector refused the write with HTTP 403, "Resource
not accessible by integration", and the Git CLI had no push credentials.
The follow-up is committed locally but has not been published or made into a PR.

`Seapower-Banda-Front-Lean-finalized.zip` contains the verified mission, this
report, the five-file patch, and `Banda-Front-Lean-finalize.bundle`. The bundle
contains the follow-up commit and requires the existing `5ac8e449` commit.

For the mission alone, close Sea Power and copy `SEST Banda Front Lean.ini`
from the ZIP into the `user_missions` folder shown below. Preserve an existing
Lean file before replacing it if you edited that copy. The edited source
mission has a different name and is not replaced.

To publish the completed tooling from the PC, download the ZIP to Downloads
and run this in PowerShell. It creates the fix branch without switching your
working branch or changing working files, then pushes that fix branch only.

```powershell
& {
    $ErrorActionPreference = 'Stop'
    $leanZip = Join-Path $env:USERPROFILE 'Downloads\Seapower-Banda-Front-Lean-finalized.zip'
    $leanHandoff = Join-Path $env:TEMP ('SEST-Lean-Handoff-' + [guid]::NewGuid().ToString('N'))
    Expand-Archive -LiteralPath $leanZip -DestinationPath $leanHandoff
    Set-Location 'C:\Users\rolyl\Seapower-mods'
    git fetch origin sest-dev/beautiful-cerf-i7fqei
    if ($LASTEXITCODE -ne 0) { throw 'Could not fetch the prerequisite branch.' }
    git fetch (Join-Path $leanHandoff 'Banda-Front-Lean-finalize.bundle') 'refs/heads/fix/banda-front-lean-finalize:refs/heads/fix/banda-front-lean-finalize'
    if ($LASTEXITCODE -ne 0) { throw 'Bundle import failed; nothing will be pushed.' }
    git push -u origin refs/heads/fix/banda-front-lean-finalize
    if ($LASTEXITCODE -ne 0) { throw 'Push failed; the fix remains available locally.' }
    Write-Host 'Published fix/banda-front-lean-finalize.'
}
```

## Install only the Lean mission on the PC

After publishing the bundle above, close Sea Power. This uses the Steam location shown in the user's successful
mission import. It fetches the follow-up branch without switching the working
branch, extracts the single mission, checks its hash, and copies it into the
game. Any previous Lean file is backed up in the staging folder shown at the
end. Other missions, the edited source save, mod files, and load order are not
written by these commands. Python is not required.

```powershell
& {
    $ErrorActionPreference = 'Stop'
    Set-Location 'C:\Users\rolyl\Seapower-mods'
    git fetch origin fix/banda-front-lean-finalize
    if ($LASTEXITCODE -ne 0) { throw 'Git fetch failed.' }

    $leanStage = Join-Path $env:TEMP ('SEST-Lean-' + [guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Path $leanStage | Out-Null
    git archive --format=zip "--output=$leanStage\mission.zip" FETCH_HEAD -- 'integration/missions/SEST Banda Front Lean.ini'
    if ($LASTEXITCODE -ne 0) { throw 'Mission extraction failed.' }
    Expand-Archive -LiteralPath "$leanStage\mission.zip" -DestinationPath $leanStage
    $leanSource = Join-Path $leanStage 'integration\missions\SEST Banda Front Lean.ini'
    $leanHash = 'e11405a8749bc713009033e923789d70a30383fcd3162dce1b8d47c0903008bf'
    if ((Get-FileHash -LiteralPath $leanSource -Algorithm SHA256).Hash -ne $leanHash) {
        throw 'The mission differs from the verified Lean file.'
    }

    $leanGameDir = 'C:\Program Files (x86)\Steam\steamapps\common\Sea Power\Sea Power_Data\StreamingAssets\user\missions\user_missions'
    if (-not (Test-Path -LiteralPath $leanGameDir -PathType Container)) { throw 'Game mission folder not found.' }
    $leanDestination = Join-Path $leanGameDir 'SEST Banda Front Lean.ini'
    if (Test-Path -LiteralPath $leanDestination) {
        Copy-Item -LiteralPath $leanDestination -Destination (Join-Path $leanStage 'previous-Lean.ini')
    }
    Copy-Item -LiteralPath $leanSource -Destination $leanDestination -Force
    if ((Get-FileHash -LiteralPath $leanDestination -Algorithm SHA256).Hash -ne $leanHash) {
        throw 'Installed mission hash does not match.'
    }
    Write-Host 'Installed: SEST Banda Front Lean. Select that mission in Sea Power.'
    Write-Host "Staging and any previous-file backup: $leanStage"
}
```

Verified source SHA-256:
`1b9d4cd7f3a2d59680634ae4cdec6b22d8942f3346ba535ff447ccf21dbecf94`.

Verified Lean SHA-256:
`e11405a8749bc713009033e923789d70a30383fcd3162dce1b8d47c0903008bf`.
