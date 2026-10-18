<#
.SYNOPSIS
    tools\set-mod-order.ps1 and SEST's own Workshop item (3812461539), on a
    synthetic settings file, StreamingAssets folder, workshop content folder
    and canonical order: the item takes position 1 when the local
    SEST_Integration folder is absent, the local folder keeps position 1 and
    the item is dropped with a warning when it is present, never both, and
    -DryRun writes nothing.

.DESCRIPTION
    The script reads the game's usersettings.ini, StreamingAssets and Steam's
    workshop content folder, none of which this machine has, so the test
    writes stand-ins and points the script at them (-SettingsPath,
    -StreamingAssetsDir, -WorkshopContentDir, -TokensPath). The canonical
    order used is three entries: SEST_Integration, 3380210757, 3784474738.
    Exit code 1 on any failed check.

        pwsh -File tools/tests/test_set_mod_order.ps1
    (Windows PowerShell 5.1 runs it too.)
#>
[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$script = Join-Path (Split-Path -Parent $PSScriptRoot) "set-mod-order.ps1"
$root = Join-Path ([System.IO.Path]::GetTempPath()) ("sest-order-test-" + [Guid]::NewGuid().ToString("N").Substring(0, 8))
$failed = 0

function Check([bool]$ok, [string]$what) {
    if ($ok) { Write-Host "  ok     $what" } else { Write-Host "  FAILED $what"; $script:failed++ }
}

# A usersettings.ini with the given [LoadOrder] entries, all enabled.
function New-Settings([string[]]$entries) {
    $lines = @("[Graphics]", "Fullscreen=True", "", "[LoadOrder]", "NumberOfModFiles=$($entries.Count)")
    for ($i = 0; $i -lt $entries.Count; $i++) { $lines += ("Mod{0}Directory={1},True" -f ($i + 1), $entries[$i]) }
    $lines += @("", "[Audio]", "Volume=1")
    $path = Join-Path $root ("usersettings-" + [Guid]::NewGuid().ToString("N").Substring(0, 6) + ".ini")
    [IO.File]::WriteAllText($path, (($lines -join "`r`n") + "`r`n"))
    return $path
}

# The [LoadOrder] tokens of a settings file, in order.
function Get-Order([string]$path) {
    $sec = [regex]::Match([IO.File]::ReadAllText($path), "(?s)\[LoadOrder\]\r?\n(.*?)(?=\r?\n\[|$)")
    return @([regex]::Matches($sec.Groups[1].Value, "Mod\d+Directory=([^,\r\n]+),(True|False)") | ForEach-Object { $_.Groups[1].Value })
}

# Run the script; every stream, line by line as it streams, and a thrown
# error come back as one string.
function Invoke-Script([hashtable]$params) {
    $lines = New-Object System.Collections.Generic.List[string]
    try { & $script @params *>&1 | ForEach-Object { $lines.Add("$_") } } catch { $lines.Add("ERROR: $($_.Exception.Message)") }
    return ($lines -join "`n")
}
function Run([string]$settings, [string]$sa, [bool]$addMissing, [bool]$dryRun = $false) {
    $params = @{ SettingsPath = $settings; TokensPath = $tokens; WorkshopContentDir = $ws; StreamingAssetsDir = $sa }
    if ($addMissing) { $params["AddMissing"] = $true }
    if ($dryRun) { $params["DryRun"] = $true }
    return (Invoke-Script $params)
}

function Count-Sest([string[]]$order) {
    return @($order | Where-Object { $_ -eq "SEST_Integration" -or $_ -eq "3812461539" }).Count
}

try {
    New-Item -ItemType Directory -Force -Path $root | Out-Null
    $tokens = Join-Path $root "load-order.tokens.txt"
    [IO.File]::WriteAllText($tokens, "# test order`nSEST_Integration`n3380210757`n3784474738`n")
    $ws = Join-Path $root "content"
    foreach ($id in "3812461539", "3380210757", "3784474738") {
        New-Item -ItemType Directory -Force -Path (Join-Path $ws $id) | Out-Null
        [IO.File]::WriteAllText((Join-Path (Join-Path $ws $id) "_info.ini"), "[Language_en]`r`nName=Mod $id`r`n")
    }
    $saEmpty = Join-Path $root "sa-empty"
    New-Item -ItemType Directory -Force -Path $saEmpty | Out-Null
    $saLocal = Join-Path $root "sa-local"
    New-Item -ItemType Directory -Force -Path (Join-Path $saLocal "SEST_Integration") | Out-Null

    # A. the game lists the Workshop copy, no local folder: it keeps position 1
    $s = New-Settings @("3812461539", "3380210757", "3784474738")
    $text = Run $s $saEmpty $true
    $order = Get-Order $s
    Check ($order.Count -eq 3 -and $order[0] -eq "3812461539" -and $order[1] -eq "3380210757") "A: Workshop copy stays at position 1 with the local folder absent ($($order -join ', '))"
    Check ($text -match "3812461539 takes SEST_Integration's position 1") "A: says the item stands in for SEST_Integration"
    Check (-not ($text -match "dropped stale workshop entry")) "A: the item is not called a stale entry"
    Check ((Count-Sest $order) -eq 1) "A: exactly one SEST entry"
    Check (@(Get-ChildItem -LiteralPath $root -File -Filter ((Split-Path -Leaf $s) + ".bak_*")).Count -eq 1) "A: a backup was written beside the settings file"

    # B. the game lists the Workshop copy, the local folder is present: the folder takes position 1, the item is dropped
    $s = New-Settings @("3812461539", "3380210757", "3784474738")
    $text = Run $s $saLocal $true
    $order = Get-Order $s
    Check ($order.Count -eq 3 -and $order[0] -eq "SEST_Integration" -and -not ($order -contains "3812461539")) "B: local folder at position 1, the item dropped ($($order -join ', '))"
    Check ($text -match "dropped SEST's own Workshop item 3812461539" -and $text -match "Unsubscribe from 3812461539") "B: the warning names the item and says to unsubscribe"
    Check ($text -match "ADDED and enabled: SEST_Integration") "B: SEST_Integration reported as added"
    Check ((Count-Sest $order) -eq 1) "B: exactly one SEST entry"

    # C. the game lists both: never both in the result
    $s = New-Settings @("SEST_Integration", "3812461539", "3380210757", "3784474738")
    $text = Run $s $saLocal $true
    $order = Get-Order $s
    Check ($order[0] -eq "SEST_Integration" -and (Count-Sest $order) -eq 1 -and $order.Count -eq 3) "C: both listed, local folder present: SEST_Integration alone ($($order -join ', '))"
    Check ($text -match "dropped SEST's own Workshop item 3812461539") "C: the item dropped with the warning"

    # D. Steam has the Workshop copy but the game has never listed it, no local folder: placed at 1, enabled
    $s = New-Settings @("3380210757", "3784474738")
    $text = Run $s $saEmpty $true
    $order = Get-Order $s
    Check ($order.Count -eq 3 -and $order[0] -eq "3812461539") "D: the downloaded item is placed at position 1 ($($order -join ', '))"
    Check ($text -match "ADDED and enabled: 3812461539") "D: reported as added and enabled"
    Check (-not ($text -match "canonical pack not installed")) "D: no 'not installed' warning for SEST_Integration"

    # E. without -AddMissing the disk is not read: the listed item is kept at 1
    $s = New-Settings @("3812461539", "3380210757", "3784474738")
    $text = Run $s $saLocal $false
    $order = Get-Order $s
    Check ($order[0] -eq "3812461539" -and (Count-Sest $order) -eq 1) "E: without -AddMissing the listed item keeps position 1 ($($order -join ', '))"

    # F. -DryRun writes nothing
    $s = New-Settings @("3812461539", "3380210757", "3784474738")
    $before = [IO.File]::ReadAllBytes($s)
    $text = Run $s $saEmpty $true $true
    $after = [IO.File]::ReadAllBytes($s)
    Check (($text -match "DRY RUN - nothing written") -and ([Convert]::ToBase64String($before) -eq [Convert]::ToBase64String($after))) "F: -DryRun leaves the settings file unchanged"
    Check (@(Get-ChildItem -LiteralPath $root -File -Filter ((Split-Path -Leaf $s) + ".bak_*")).Count -eq 0) "F: -DryRun writes no backup"

    # G. a listed SEST_Integration whose folder is gone, with the Workshop copy on disk: the copy stands in
    $s = New-Settings @("SEST_Integration", "3380210757", "3784474738")
    $text = Run $s $saEmpty $true
    $order = Get-Order $s
    Check ($order[0] -eq "3812461539" -and -not ($order -contains "SEST_Integration")) "G: dead SEST_Integration replaced by the Workshop copy ($($order -join ', '))"
    Check ($text -match "its folder is not in StreamingAssets") "G: the warning says why SEST_Integration went"

    # H. neither copy anywhere: the existing warning, and no SEST entry invented
    $wsNone = Join-Path $root "content-none"
    New-Item -ItemType Directory -Force -Path $wsNone | Out-Null
    $s = New-Settings @("3380210757", "3784474738")
    $text = Invoke-Script @{ SettingsPath = $s; TokensPath = $tokens; WorkshopContentDir = $wsNone; StreamingAssetsDir = $saEmpty; AddMissing = $true }
    $order = Get-Order $s
    Check ((Count-Sest $order) -eq 0 -and $text -match "canonical pack not installed in StreamingAssets, and no Workshop copy") "H: nothing invented when neither copy exists"
} finally {
    if (Test-Path -LiteralPath $root) { Remove-Item -LiteralPath $root -Recurse -Force }
}

if ($failed) { Write-Host "$failed check(s) failed"; exit 1 }
Write-Host "all checks passed"
