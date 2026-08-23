<#
.SYNOPSIS
    Discover where Sea Power stores the Mod Manager order/enabled list.

.DESCRIPTION
    Read-only: scans the Unity persistent-data folder (AppData\LocalLow), the
    StreamingAssets root and user\ folder, and Unity PlayerPrefs in the registry,
    then previews any file whose name looks mod-order related. Paste the whole
    output back so the write-side automation (set-mod-order.ps1) can be built
    against the real format. Close the game before running.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File .\tools\find-mod-order-store.ps1
#>
[CmdletBinding()]
param(
    [string]$StreamingAssetsDir = "C:\program files (x86)\steam\steamapps\common\Sea Power\Sea Power_Data\StreamingAssets"
)

$ErrorActionPreference = "Continue"

Write-Host "=== 1. AppData\LocalLow candidates ==="
$lowRoot = Join-Path $env:USERPROFILE "AppData\LocalLow"
$dirs = Get-ChildItem -LiteralPath $lowRoot -Directory -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -match "Triassic|MicroProse|Sea" }
if (-not $dirs) { Write-Host "  (no matching company folders under LocalLow)" }
$previewTargets = @()
foreach ($d in $dirs) {
    Get-ChildItem -LiteralPath $d.FullName -Recurse -File -ErrorAction SilentlyContinue |
        Select-Object -First 60 | ForEach-Object {
            Write-Host ("  {0,10:N0} B  {1}" -f $_.Length, $_.FullName)
            if ($_.Name -match "mod|order|load|manager|settings|config|prefs" -and $_.Length -lt 512KB) {
                $previewTargets += $_
            }
        }
}

Write-Host "`n=== 2. StreamingAssets root files ==="
Get-ChildItem -LiteralPath $StreamingAssetsDir -File -ErrorAction SilentlyContinue |
    ForEach-Object { Write-Host ("  {0,10:N0} B  {1}" -f $_.Length, $_.Name)
        if ($_.Name -match "mod|order|load" -and $_.Length -lt 512KB) { $previewTargets += $_ } }

Write-Host "`n=== 3. StreamingAssets\user files ==="
Get-ChildItem -LiteralPath (Join-Path $StreamingAssetsDir "user") -File -ErrorAction SilentlyContinue |
    ForEach-Object { Write-Host ("  {0,10:N0} B  {1}" -f $_.Length, $_.Name)
        if ($_.Name -match "mod|order|load|manager" -and $_.Length -lt 512KB) { $previewTargets += $_ } }

Write-Host "`n=== 4. Unity PlayerPrefs registry keys ==="
$keys = Get-ChildItem "HKCU:\Software" -ErrorAction SilentlyContinue |
    Where-Object { $_.PSChildName -match "Triassic|MicroProse|Sea" }
if (-not $keys) { Write-Host "  (no matching registry keys)" }
foreach ($k in $keys) {
    foreach ($sub in @($k) + @(Get-ChildItem $k.PSPath -ErrorAction SilentlyContinue)) {
        Write-Host "  key: $($sub.Name)"
        ($sub | Get-ItemProperty -ErrorAction SilentlyContinue).PSObject.Properties |
            Where-Object { $_.Name -notmatch "^PS" } |
            ForEach-Object {
                $vs = "$($_.Value)"
                if ($_.Value -is [byte[]]) {
                    $vs = [System.Text.Encoding]::UTF8.GetString($_.Value)
                }
                if ($vs.Length -gt 160) { $vs = $vs.Substring(0, 160) + " ..." }
                Write-Host ("    {0} = {1}" -f $_.Name, $vs)
            }
    }
}

Write-Host "`n=== 5. Previews of likely mod-order files ==="
if (-not $previewTargets) { Write-Host "  (none matched the name patterns)" }
foreach ($f in ($previewTargets | Sort-Object FullName -Unique | Select-Object -First 6)) {
    Write-Host "`n----- $($f.FullName) (first 40 lines) -----"
    try { Get-Content -LiteralPath $f.FullName -TotalCount 40 -ErrorAction Stop }
    catch { Write-Host "  (unreadable as text: $($_.Exception.Message))" }
}

Write-Host "`nDone. Paste ALL of the above back into the chat."
