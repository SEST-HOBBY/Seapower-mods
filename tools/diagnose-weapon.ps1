<#
.SYNOPSIS
    Ask the LIVE install why a weapon is not firing, instead of guessing from the repo.

.DESCRIPTION
    The repo can prove what SHOULD be installed. It cannot see what IS installed, and
    that gap has now cost two rounds of diagnosis on the RAN Anzacs' NSMs: the fix was
    correct in git and the missiles still did not fly, which leaves "the fix never
    reached the game" and "the round is not in the game at all" as live possibilities
    that no amount of repo analysis can settle.

    This reads the installed files and the Mod Manager's own settings and reports:

      1. Is the SEST pack installed, enabled, and at the top of the order?
      2. Does the INSTALLED unit file carry the wiring the repo says it should?
      3. Does the ammunition the launcher asks for exist anywhere the game can see it,
         and is the mod that supplies it enabled?
      4. Is a stale per-pack folder (the pre-consolidation layout) still present and
         fighting the consolidated pack?
      5. Every mod that supplies a copy of the unit file, in load order, so a silent
         override is visible.

    Read-only: it opens files and prints. It changes nothing, and it is safe to run
    with the game open.

.EXAMPLE
    # defaults are the RAN Anzac's NSM case
    powershell -ExecutionPolicy Bypass -File .\tools\diagnose-weapon.ps1

    # any other unit/round pair
    powershell -ExecutionPolicy Bypass -File .\tools\diagnose-weapon.ps1 -Unit ran_ddg_hobart -Ammo usn_rgm_184a
#>
[CmdletBinding()]
param(
    [string]$Unit = "ran_ffh_anzac",
    [string]$Kind = "vessels",
    [string]$Ammo = "usn_rgm_184a",
    [string]$StreamingAssetsDir,
    [string]$WorkshopContentDir,
    [string]$SettingsPath = (Join-Path $env:USERPROFILE "AppData\LocalLow\Triassic Games\Sea Power\usersettings.ini")
)

$ErrorActionPreference = "Stop"
$scriptDir = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
. (Join-Path $scriptDir "lib\common.ps1")

function Head($t) { Write-Host "`n=== $t" -ForegroundColor Cyan }
function Good($t) { Write-Host "  OK   $t" -ForegroundColor Green }
function Bad($t)  { Write-Host "  BAD  $t" -ForegroundColor Red }
function Info($t) { Write-Host "       $t" }

if (-not $StreamingAssetsDir) { $StreamingAssetsDir = Find-StreamingAssets }
if (-not $StreamingAssetsDir -or -not (Test-Path -LiteralPath $StreamingAssetsDir)) {
    throw "StreamingAssets not found. Re-run with -StreamingAssetsDir '<...>\Sea Power_Data\StreamingAssets'"
}
Head "Install"
Info "StreamingAssets: $StreamingAssetsDir"

if (-not $WorkshopContentDir) {
    # Get-SteamLibraries already returns <root>\steamapps, so the workshop path is
    # relative to that - joining another "steamapps" was why this used to miss.
    # The app id is not hardcoded: pick the content folder that actually holds the
    # workshop ids this repo tracks.
    $wanted = @(Get-Content -LiteralPath (Join-Path $scriptDir "..\data\load-order.tokens.txt") |
                Where-Object { $_ -match '^\s*\d+\s*$' } | ForEach-Object { $_.Trim() })
    $best = 0
    foreach ($lib in Get-SteamLibraries) {
        $content = Join-Path $lib "workshop\content"
        if (-not (Test-Path -LiteralPath $content)) { continue }
        foreach ($app in Get-ChildItem -LiteralPath $content -Directory -ErrorAction SilentlyContinue) {
            $have = @(Get-ChildItem -LiteralPath $app.FullName -Directory -ErrorAction SilentlyContinue |
                      Where-Object { $wanted -contains $_.Name }).Count
            if ($have -gt $best) { $best = $have; $WorkshopContentDir = $app.FullName }
        }
    }
    if ($WorkshopContentDir) { Write-Verbose "matched $best known mods under $WorkshopContentDir" }
}
if ($WorkshopContentDir) { Info "Workshop content: $WorkshopContentDir" }
else { Bad "Workshop content folder not found - subscribed mods cannot be inspected" }

# --- 1. the SEST pack ---------------------------------------------------------
Head "1. SEST pack"
$sest = Join-Path $StreamingAssetsDir "SEST_Integration"
if (Test-Path -LiteralPath $sest) {
    $n = (Get-ChildItem -LiteralPath $sest -Recurse -File).Count
    Good "SEST_Integration installed ($n files)"
} else {
    Bad "SEST_Integration is NOT installed - run tools\install-sest-packs.ps1"
}
$stale = Get-ChildItem -LiteralPath $StreamingAssetsDir -Directory -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -like "SEST_*" -and $_.Name -ne "SEST_Integration" }
if ($stale) {
    Bad ("stale per-pack folders still installed: {0}" -f (($stale.Name) -join ', '))
    Info "These predate the consolidated pack. Re-run install-sest-packs.ps1, which removes them."
} else { Good "no stale per-pack folders" }

# --- 2. the installed unit file ----------------------------------------------
Head "2. Installed $Unit.ini"
$installed = Join-Path $sest "$Kind\$Unit.ini"
if (-not (Test-Path -LiteralPath $installed)) {
    Bad "not present in the installed pack: $installed"
} else {
    $t = Get-Content -LiteralPath $installed -Raw
    $repo = Join-Path $scriptDir "..\integration\dist\SEST_Integration\$Kind\$Unit.ini"
    if (Test-Path -LiteralPath $repo) {
        $a = (Get-FileHash -LiteralPath $installed -Algorithm SHA256).Hash
        $b = (Get-FileHash -LiteralPath $repo -Algorithm SHA256).Hash
        if ($a -eq $b) { Good "installed copy is byte-identical to the repo's" }
        else {
            Bad "installed copy DIFFERS from the repo - the install is stale"
            Info "fix: git pull, then tools\install-sest-packs.ps1 (game closed)"
        }
    }
    $mounts = [regex]::Matches($t, "(?m)^\[WeaponSystem([^\]]+)\][^\n]*\n((?:(?!^\[).*\n)*)")
    $firing = @()
    foreach ($m in $mounts) {
        if ($m.Groups[2].Value -match "(?m)^Ammunition=$([regex]::Escape($Ammo))\b") {
            $firing += $m
        }
    }
    if (-not $firing) { Bad "no weapon system in the installed file fires $Ammo" }
    else {
        Good ("$($firing.Count) launcher(s) fire ${Ammo}:")
        foreach ($m in $firing) {
            Write-Host "  --- [WeaponSystem$($m.Groups[1].Value)]" -ForegroundColor DarkGray
            foreach ($line in ($m.Groups[2].Value -split "`r?`n")) {
                if ($line.Trim() -and $line -notmatch '^\s*#') { Write-Host "      $line" }
            }
        }
    }
}

# --- 3. the round -------------------------------------------------------------
Head "3. Ammunition $Ammo"
$providers = @()
if ($WorkshopContentDir) {
    foreach ($d in Get-ChildItem -LiteralPath $WorkshopContentDir -Directory -ErrorAction SilentlyContinue) {
        $f = Get-ChildItem -LiteralPath $d.FullName -Recurse -File -Filter "$Ammo.ini" -ErrorAction SilentlyContinue |
             Select-Object -First 1
        if ($f) { $providers += [pscustomobject]@{ Source = $d.Name; Name = (Get-ModDisplayName -ModDir $d.FullName); Path = $f.FullName } }
    }
}
foreach ($d in Get-ChildItem -LiteralPath $StreamingAssetsDir -Directory -ErrorAction SilentlyContinue) {
    $f = Get-ChildItem -LiteralPath $d.FullName -Recurse -File -Filter "$Ammo.ini" -ErrorAction SilentlyContinue |
         Select-Object -First 1
    if ($f) { $providers += [pscustomobject]@{ Source = $d.Name; Name = "(StreamingAssets)"; Path = $f.FullName } }
}
if (-not $providers) {
    Bad "NOTHING in the live install defines $Ammo - the launcher has no missile to fire."
    Info "That alone would stop it firing, whatever the launcher says."
} else {
    Good "$($providers.Count) provider(s):"
    $providers | ForEach-Object { Info ("{0}  {1}" -f $_.Source, $_.Name) }
    # SEST sits at position 1, so its copy is the one the game reads when present.
    $winner = ($providers | Where-Object { $_.Source -eq 'SEST_Integration' } | Select-Object -First 1)
    if (-not $winner) { $winner = $providers[0] }
    Info ("winning copy: {0}" -f $winner.Path)
    $at = Get-Content -LiteralPath $winner.Path -Raw
    foreach ($k in 'GuidanceType', 'MidCourseCorrection', 'MinLaunchRange', 'MaxLaunchRange',
                   'MinAttackAltitude', 'LaunchReliability', 'SupplyCategory') {
        $m = [regex]::Match($at, "(?m)^$k=([^/\r\n]+)")
        if ($m.Success) { Info ("  {0,-20} {1}" -f $k, $m.Groups[1].Value.Trim()) }
    }
}

# --- 4. the mod order actually in force --------------------------------------
Head "4. Mod Manager order (usersettings.ini)"
if (-not (Test-Path -LiteralPath $SettingsPath)) { Bad "settings not found: $SettingsPath" }
else {
    $text = Get-Content -LiteralPath $SettingsPath -Raw
    $m = [regex]::Match($text, "(?s)\[LoadOrder\]\r?\n(.*?)(?=\r?\n\[|$)")
    if (-not $m.Success) { Bad "[LoadOrder] section not found" }
    else {
        $section = $m.Groups[1].Value
        $active = [int]([regex]::Match($section, "NumberOfModFiles=(\d+)").Groups[1].Value)
        $entries = @()
        foreach ($em in [regex]::Matches($section, "Mod(\d+)Directory=([^,\r\n]+),(True|False)")) {
            if ([int]$em.Groups[1].Value -le $active) {
                $entries += [pscustomobject]@{ Pos = [int]$em.Groups[1].Value; Dir = $em.Groups[2].Value; On = $em.Groups[3].Value }
            }
        }
        Info "active entries: $($entries.Count)"
        $s = $entries | Where-Object { $_.Dir -eq "SEST_Integration" }
        if (-not $s) { Bad "SEST_Integration is not in the load order - the Mod Manager has never seen it" }
        elseif ($s.On -ne "True") { Bad "SEST_Integration is present but DISABLED (position $($s.Pos))" }
        elseif ($s.Pos -ne 1) { Bad "SEST_Integration is enabled but at position $($s.Pos), not 1 - something outranks it" }
        else { Good "SEST_Integration enabled at position 1" }

        foreach ($p in $providers) {
            if ($p.Source -match '^\d+$') {
                $e = $entries | Where-Object { $_.Dir -eq $p.Source }
                if (-not $e) { Bad "$($p.Source) ($($p.Name)) supplies $Ammo but is NOT in the load order" }
                elseif ($e.On -ne "True") { Bad "$($p.Source) ($($p.Name)) supplies $Ammo but is DISABLED - the round will not load" }
                else { Good "$($p.Source) ($($p.Name)) enabled at position $($e.Pos)" }
            }
        }
    }
}

# --- 5. who else ships this unit file ----------------------------------------
Head "5. Other providers of $Kind\$Unit.ini"
$others = @()
if ($WorkshopContentDir) {
    foreach ($d in Get-ChildItem -LiteralPath $WorkshopContentDir -Directory -ErrorAction SilentlyContinue) {
        $f = Get-ChildItem -LiteralPath $d.FullName -Recurse -File -Filter "$Unit.ini" -ErrorAction SilentlyContinue |
             Select-Object -First 1
        if ($f) { $others += "$($d.Name)  $(Get-ModDisplayName -ModDir $d.FullName)" }
    }
}
if ($others) {
    Bad "another mod also ships $Unit.ini - whichever is higher wins:"
    $others | ForEach-Object { Info $_ }
} else { Good "only the SEST pack ships it - no override fight" }

Write-Host "`nSend this whole output back. It settles what the repo cannot see." -ForegroundColor Yellow
