<#
.SYNOPSIS
    Put the mod order back after the game has rewritten it.

.DESCRIPTION
    WHY THIS EXISTS. Sea Power owns usersettings.ini while it runs and rewrites
    the whole [LoadOrder] section when it exits. So the sequence you actually
    use - launch, tick some mods in the Mod Manager, quit - always ends with
    the game's own ordering, not the canonical one. Anything you set before
    launching is gone.

    The fix has to run AFTER the game closes, every time you change the mod
    selection. This script does exactly that, and by default it WAITS for Sea
    Power to exit rather than making you remember: start it, go play, and the
    order is corrected the moment you quit.

    It reports what the game changed - reordered, newly discovered, or
    disabled - before rewriting, so you can see what the Mod Manager did.
    The real work is done by set-mod-order.ps1 -AddMissing.

.EXAMPLE
    # Start it, then launch the game. It applies as soon as you quit.
    powershell -ExecutionPolicy Bypass -File .\tools\fix-load-order.ps1

.EXAMPLE
    # Game already closed - just fix it now.
    powershell -ExecutionPolicy Bypass -File .\tools\fix-load-order.ps1 -NoWait

.EXAMPLE
    # See what it would do, change nothing.
    powershell -ExecutionPolicy Bypass -File .\tools\fix-load-order.ps1 -NoWait -DryRun
#>
[CmdletBinding()]
param(
    [string]$SettingsPath = (Join-Path $env:USERPROFILE "AppData\LocalLow\Triassic Games\Sea Power\usersettings.ini"),
    [string]$StreamingAssetsDir,
    [switch]$NoWait,
    [switch]$DryRun,
    [int]$TimeoutMinutes = 240
)

$ErrorActionPreference = "Stop"
$scriptDir = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
$repoRoot = Split-Path -Parent $scriptDir
. (Join-Path $scriptDir "lib\common.ps1")

$tokensPath = Join-Path $repoRoot "data\load-order.tokens.txt"
if (-not (Test-Path -LiteralPath $tokensPath)) { throw "canonical order not found (git pull?): $tokensPath" }

# --- Wait for the game to close ---------------------------------------------
if (Test-SeaPowerRunning) {
    if ($NoWait) {
        throw ("Sea Power is running. It rewrites usersettings.ini on exit, so anything " +
               "written now is discarded. Quit the game first, or drop -NoWait to wait for it.")
    }
    Write-Host "Sea Power is running. Waiting for it to exit..." -ForegroundColor Cyan
    Write-Host "  (go and play - the order is corrected the moment you quit; Ctrl+C to give up)"
    $deadline = (Get-Date).AddMinutes($TimeoutMinutes)
    while (Test-SeaPowerRunning) {
        if ((Get-Date) -gt $deadline) { throw "still running after $TimeoutMinutes minutes - giving up." }
        Start-Sleep -Seconds 5
    }
    # The game writes usersettings.ini as it shuts down; let that finish.
    Write-Host "  game closed - letting it finish writing usersettings.ini"
    Start-Sleep -Seconds 3
} else {
    Write-Host "Sea Power is not running." -ForegroundColor DarkGray
}

# --- Report what the game did ------------------------------------------------
if (-not (Test-Path -LiteralPath $SettingsPath)) { throw "settings file not found: $SettingsPath" }
$canonical = @(Get-Content -LiteralPath $tokensPath | Where-Object { $_ -and $_ -notmatch "^#" })
$text = Get-Content -LiteralPath $SettingsPath -Raw
$m = [regex]::Match($text, "(?s)\[LoadOrder\]\r?\n(.*?)(?=\r?\n\[|$)")
if (-not $m.Success) { throw "[LoadOrder] section not found in $SettingsPath" }
$activeCount = [int][regex]::Match($m.Groups[1].Value, "NumberOfModFiles=(\d+)").Groups[1].Value

$live = [ordered]@{}
foreach ($em in [regex]::Matches($m.Groups[1].Value, "Mod(\d+)Directory=([^,\r\n]+),(True|False)")) {
    if ([int]$em.Groups[1].Value -le $activeCount -and -not $live.Contains($em.Groups[2].Value)) {
        $live[$em.Groups[2].Value] = $em.Groups[3].Value
    }
}

$wantOrder = @($canonical | Where-Object { $live.Contains($_) })
$haveOrder = @($live.Keys | Where-Object { $canonical -contains $_ })
$outOfOrder = 0
for ($i = 0; $i -lt $wantOrder.Count; $i++) { if ($wantOrder[$i] -ne $haveOrder[$i]) { $outOfOrder++ } }

$unknown  = @($live.Keys | Where-Object { $canonical -notcontains $_ })
$sestOff  = @($live.Keys | Where-Object { $_ -like "SEST_*" -and $live[$_] -eq "False" })
$notListed = @($canonical | Where-Object { -not $live.Contains($_) })

Write-Host ""
Write-Host ("what the game has now : {0} entries, {1} in a different position to canonical" -f $live.Count, $outOfOrder)
if ($unknown)   { Write-Warning "not in data\load-order.tokens.txt (will be appended at the end): $($unknown -join ', ')" }
if ($sestOff)   { Write-Warning "SEST packs you have DISABLED (their patches will do nothing): $($sestOff -join ', ')" }
if ($notListed) { Write-Host    ("canonical entries the game has not listed : {0}" -f $notListed.Count) -ForegroundColor DarkGray }
if ($outOfOrder -eq 0 -and -not $unknown) { Write-Host "order already matches canonical." -ForegroundColor Green }

# --- Apply -------------------------------------------------------------------
Write-Host ""
$orderArgs = @{ AddMissing = $true }
if ($StreamingAssetsDir) { $orderArgs["StreamingAssetsDir"] = $StreamingAssetsDir }
if ($DryRun) { $orderArgs["DryRun"] = $true }
# NOTE: splat a HASHTABLE. Array splatting binds POSITIONALLY.
& (Join-Path $scriptDir "set-mod-order.ps1") @orderArgs

if (-not $DryRun) {
    Write-Host ""
    Write-Host "Order restored. Launch the game again and it will load in this order." -ForegroundColor Green
    Write-Host "Re-run this any time you change which mods are ticked." -ForegroundColor DarkGray
}
