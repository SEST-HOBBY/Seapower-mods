<#
.SYNOPSIS
    Harvest the text/config portion of your Sea Power Workshop mods into this repo.

.DESCRIPTION
    Finds your Sea Power install by scanning Steam library manifests (no hardcoded
    app ID), then copies only small text-based files (.ini, .txt, .json, .cfg, .xml,
    .md, .yaml) from each subscribed Workshop mod into mods-source/<workshop-id>/,
    preserving folder structure. Heavy binaries (models, textures, asset bundles)
    are skipped so the repo stays light — the configs are what loadout/integration
    work needs.

    Also writes mods-source/_export-manifest.csv mapping each workshop ID to a
    guessed mod name, file count, and copied bytes.

.EXAMPLE
    # From the repo root, in PowerShell:
    .\tools\export-mod-configs.ps1

    # If auto-detection fails, point it at the workshop content folder directly:
    .\tools\export-mod-configs.ps1 -WorkshopContentDir "D:\SteamLibrary\steamapps\workshop\content\<seapower-appid>"

    # Also export the vanilla game definitions (very useful as reference data):
    .\tools\export-mod-configs.ps1 -IncludeVanilla

    # Read-only: which mods have their authors updated since our last export,
    # and what have I subscribed to that is not exported yet?
    .\tools\export-mod-configs.ps1 -CheckUpdates

    Then commit and push (PowerShell has no && - use semicolons):
      git add -A mods-source; git commit -m "Export mod configs"; git push
#>
[CmdletBinding()]
param(
    [string]$WorkshopContentDir,
    [string]$DestDir,
    [switch]$IncludeVanilla,
    [switch]$NoPrune,
    [switch]$CheckUpdates,
    [string[]]$TextExtensions = @(".ini", ".txt", ".json", ".cfg", ".xml", ".md", ".yaml", ".yml", ".csv"),
    [long]$MaxFileBytes = 2MB
)

$ErrorActionPreference = "Stop"

# $PSScriptRoot can be empty inside param() defaults on Windows PowerShell,
# so paths are resolved here in the body instead.
$scriptDir = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
if (-not $DestDir) { $DestDir = Join-Path $scriptDir "..\mods-source" }

. (Join-Path $scriptDir "lib\common.ps1")

function Find-SeaPower {
    foreach ($lib in Get-SteamLibraries) {
        foreach ($acf in Get-ChildItem -LiteralPath $lib -Filter "appmanifest_*.acf" -ErrorAction SilentlyContinue) {
            $raw = Get-Content -LiteralPath $acf.FullName -Raw
            if ($raw -match '"name"\s+"([^"]*Sea Power[^"]*)"') {
                $appId = [regex]::Match($acf.Name, '\d+').Value
                $installDir = [regex]::Match($raw, '"installdir"\s+"([^"]+)"').Groups[1].Value
                [pscustomobject]@{
                    AppId      = $appId
                    Library    = $lib
                    GameDir    = Join-Path $lib "common\$installDir"
                    Workshop   = Join-Path $lib "workshop\content\$appId"
                }
                return
            }
        }
    }
}

# --- Locate the game ---------------------------------------------------------
$game = $null
if (-not $WorkshopContentDir) {
    $game = Find-SeaPower
    if (-not $game) {
        throw "Could not auto-detect Sea Power. Re-run with -WorkshopContentDir '<...>\steamapps\workshop\content\<seapower-appid>'"
    }
    $WorkshopContentDir = $game.Workshop
    Write-Host "Found Sea Power (app $($game.AppId))"
    Write-Host "  game dir : $($game.GameDir)"
    Write-Host "  workshop : $WorkshopContentDir"
}
if (-not (Test-Path $WorkshopContentDir)) {
    throw "Workshop content dir not found: $WorkshopContentDir"
}

New-Item -ItemType Directory -Force -Path $DestDir | Out-Null
$manifest = @()

# --- Which mods have the authors updated? ------------------------------------
# Steam gives no version we can see from the repo, so the check is content
# based: hash each live mod's text files exactly the way tools/fingerprint_mods.py
# hashed the exported copies, and compare. A mod whose hash moved has been
# updated on the Workshop since our export; a mod with no baseline is a fresh
# subscription. Nothing is copied or written in this mode.
if ($CheckUpdates) {
    $baselinePath = Join-Path $scriptDir "..\data\mod-fingerprints.json"
    if (-not (Test-Path -LiteralPath $baselinePath)) {
        throw "No fingerprint baseline. git pull, or run: python3 tools/fingerprint_mods.py"
    }
    $baseline = (Get-Content -LiteralPath $baselinePath -Raw | ConvertFrom-Json).mods
    $sha = [System.Security.Cryptography.SHA256]::Create()

    function Get-ModFingerprint([string]$dir) {
        $parts = New-Object System.Collections.Generic.List[string]
        foreach ($f in Get-ChildItem -LiteralPath $dir -Recurse -File -ErrorAction SilentlyContinue) {
            if ($TextExtensions -notcontains $f.Extension.ToLower()) { continue }
            if ($f.Length -gt $MaxFileBytes) { continue }
            $rel = $f.FullName.Substring($dir.Length).TrimStart('\', '/').Replace('\', '/').ToLower()
            $hash = [BitConverter]::ToString($sha.ComputeHash([IO.File]::ReadAllBytes($f.FullName))).Replace('-', '').ToLower()
            $parts.Add("${rel}:${hash}")
        }
        if ($parts.Count -eq 0) { return $null }
        # ORDINAL sort, to match Python's sorted(). Sort-Object is culture-aware
        # even with -CaseSensitive, and would order '-', '_' and '/' differently,
        # which silently changes the hash and reports every mod as updated.
        $arr = $parts.ToArray()
        [Array]::Sort($arr, [StringComparer]::Ordinal)
        $joined = ($arr -join "`n")
        return [BitConverter]::ToString($sha.ComputeHash([Text.Encoding]::UTF8.GetBytes($joined))).Replace('-', '').ToLower()
    }

    $updated = @(); $fresh = @(); $same = 0
    foreach ($mod in (Get-ChildItem -LiteralPath $WorkshopContentDir -Directory | Sort-Object Name)) {
        $fp = Get-ModFingerprint $mod.FullName
        if (-not $fp) { continue }
        $name = Get-ModDisplayName -ModDir $mod.FullName
        $known = $baseline.($mod.Name)
        if (-not $known) {
            $fresh += [pscustomobject]@{ Id = $mod.Name; Name = $name }
        } elseif ($known.fingerprint -ne $fp) {
            $updated += [pscustomobject]@{ Id = $mod.Name; Name = $name }
        } else { $same++ }
    }
    $live = (Get-ChildItem -LiteralPath $WorkshopContentDir -Directory).Name
    $gone = @($baseline.PSObject.Properties.Name | Where-Object { $live -notcontains $_ })

    Write-Host ""
    Write-Host ("unchanged since the last export : {0}" -f $same)
    if ($updated) {
        Write-Host "`nUPDATED by their authors (re-export to pick the changes up):" -ForegroundColor Yellow
        $updated | ForEach-Object { Write-Host ("  {0}  {1}" -f $_.Id, $_.Name) }
    }
    if ($fresh) {
        Write-Host "`nNEW subscriptions (not exported yet):" -ForegroundColor Green
        $fresh | ForEach-Object { Write-Host ("  {0}  {1}" -f $_.Id, $_.Name) }
    }
    if ($gone) {
        Write-Host "`nEXPORTED but no longer subscribed:" -ForegroundColor DarkGray
        $gone | ForEach-Object { Write-Host ("  {0}" -f $_) }
    }
    if (-not ($updated -or $fresh -or $gone)) { Write-Host "`nNothing has changed upstream." }
    else { Write-Host "`nTo capture: re-run this script without -CheckUpdates, then commit and push." }
    exit 0
}

# --- Export each subscribed mod ---------------------------------------------
$modDirs = Get-ChildItem -LiteralPath $WorkshopContentDir -Directory
Write-Host "Exporting text configs from $($modDirs.Count) workshop items..."
foreach ($mod in $modDirs) {
    $files = Get-ChildItem -LiteralPath $mod.FullName -Recurse -File |
        Where-Object { $TextExtensions -contains $_.Extension.ToLower() -and $_.Length -le $MaxFileBytes }
    $copied = 0; $bytes = 0
    foreach ($f in $files) {
        $rel = $f.FullName.Substring($mod.FullName.Length).TrimStart('\', '/')
        $target = Join-Path (Join-Path $DestDir $mod.Name) $rel
        New-Item -ItemType Directory -Force -Path (Split-Path $target) | Out-Null
        Copy-Item -LiteralPath $f.FullName -Destination $target -Force
        $copied++; $bytes += $f.Length
    }
    # Display name straight from the mod's own _info.ini, read as UTF-8.
    $name = Get-ModDisplayName -ModDir $mod.FullName
    $manifest += [pscustomobject]@{
        WorkshopId = $mod.Name
        DisplayName = $name
        FilesCopied = $copied
        Bytes = $bytes
    }
    Write-Host ("  {0}  {1,4} files  {2,10:N0} B  {3}" -f $mod.Name, $copied, $bytes, $name)
}

# --- Optionally export vanilla definitions -----------------------------------
if ($IncludeVanilla) {
    if (-not $game) { $game = Find-SeaPower }
    if (-not $game) { Write-Warning "Could not locate the Sea Power game dir; vanilla export skipped." }
    else {
        $sa = Get-ChildItem -LiteralPath $game.GameDir -Directory -Recurse -Depth 2 -ErrorAction SilentlyContinue |
            Where-Object { $_.Name -eq "StreamingAssets" } | Select-Object -First 1
        if ($sa) {
            $vanillaDest = Join-Path $DestDir "_vanilla"
            $files = Get-ChildItem -LiteralPath $sa.FullName -Recurse -File |
                Where-Object { $TextExtensions -contains $_.Extension.ToLower() -and $_.Length -le $MaxFileBytes }
            foreach ($f in $files) {
                $rel = $f.FullName.Substring($sa.FullName.Length).TrimStart('\', '/')
                # Skip the installed SEST packs - they are generated from this
                # repo, so exporting them back just duplicates them in git.
                if ($rel -match '^SEST_') { continue }
                $target = Join-Path $vanillaDest $rel
                New-Item -ItemType Directory -Force -Path (Split-Path $target) | Out-Null
                Copy-Item -LiteralPath $f.FullName -Destination $target -Force
            }
            Write-Host "Vanilla definitions exported to $vanillaDest ($($files.Count) files)"
        } else { Write-Warning "StreamingAssets not found under $($game.GameDir); vanilla export skipped." }
    }
}

# --- Prune mods that are no longer subscribed --------------------------------
# This export only ever ADDED directories. Unsubscribing a mod in Steam left its
# files sitting here forever, and every conflict check kept treating it as
# installed - reporting fights with mods that are not in the game any more. The
# manifest lists exactly what exists right now, so anything numeric that is not
# in it has been unsubscribed. Skip with -NoPrune.
if (-not $NoPrune) {
    $exported = @{}
    foreach ($row in $manifest) { $exported[[string]$row.WorkshopId] = $true }
    $stale = @(Get-ChildItem -LiteralPath $DestDir -Directory -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -match '^\d+$' -and -not $exported.ContainsKey($_.Name) })
    if ($stale.Count) {
        Write-Host ("`nPruning {0} mod(s) no longer subscribed:" -f $stale.Count)
        foreach ($d in $stale) {
            Write-Host ("  - {0}" -f $d.Name)
            Remove-Item -LiteralPath $d.FullName -Recurse -Force
        }
        Write-Host "  (git will show these as deletions - commit them)"
    }
}

$manifestPath = Join-Path $DestDir "_export-manifest.csv"
$manifest | Sort-Object WorkshopId | Export-Csv -Path $manifestPath -NoTypeInformation -Encoding UTF8
Write-Host "`nDone. Manifest: $manifestPath"
Write-Host "Next: git add -A mods-source; git commit -m `"Export mod configs`"; git push"
