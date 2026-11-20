<#
SEST PC test campaigns for Dynamic Campaign Mod 1.0.0.

  powershell -ExecutionPolicy Bypass -File .\INSTALL-TEST-CAMPAIGNS.ps1            (install)
  powershell -ExecutionPolicy Bypass -File .\INSTALL-TEST-CAMPAIGNS.ps1 -Collect   (results ZIP)
  powershell -ExecutionPolicy Bypass -File .\INSTALL-TEST-CAMPAIGNS.ps1 -Uninstall (remove)

Copies the three campaigns in Test_Campaigns\dynamic_campaigns into the
game's user layer, Sea Power_Data\StreamingAssets\user\dynamic_campaigns, where
Dynamic Campaign Mod lists them in the Campaign menu. Nothing in the Workshop
item, the game's own files or your saves is changed. Each installed folder gets
a marker file; -Uninstall removes only folders that carry it.
Run with the game closed.
#>
param(
    [switch]$Uninstall,
    [switch]$Collect,
    [string]$GameDir = ''
)
$ErrorActionPreference = 'Stop'
$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
$Source = Join-Path $Here 'Test_Campaigns\dynamic_campaigns'
$Marker = '.sest-test-campaign'

function Find-Game {
    if ($GameDir) { return $GameDir }
    $candidates = @(
        'C:\Program Files (x86)\Steam\steamapps\common\Sea Power',
        'C:\Program Files\Steam\steamapps\common\Sea Power'
    )
    foreach ($c in $candidates) { if (Test-Path -LiteralPath (Join-Path $c 'Sea Power_Data')) { return $c } }
    throw 'Sea Power was not found. Add -GameDir "D:\...\Sea Power" (the folder that holds Sea Power_Data).'
}

$Game = Find-Game
$UserCampaigns = Join-Path $Game 'Sea Power_Data\StreamingAssets\user\dynamic_campaigns'
$LocalLow = Join-Path $env:USERPROFILE 'AppData\LocalLow\Triassic Games\Sea Power'
$Names = @(Get-ChildItem -LiteralPath $Source -Directory | ForEach-Object { $_.Name })

if (Get-Process -Name 'Sea Power' -ErrorAction SilentlyContinue) {
    if (-not $Collect) { throw 'Close Sea Power first.' }
}

if ($Uninstall) {
    foreach ($n in $Names) {
        $dest = Join-Path $UserCampaigns $n
        if (-not (Test-Path -LiteralPath $dest)) { Write-Host "Not installed: $n"; continue }
        if (-not (Test-Path -LiteralPath (Join-Path $dest $Marker))) {
            Write-Host "Left alone (no SEST test marker): $dest"; continue
        }
        Remove-Item -LiteralPath $dest -Recurse -Force
        Write-Host "Removed $dest"
    }
    if ((Test-Path -LiteralPath $UserCampaigns) -and -not (Get-ChildItem -LiteralPath $UserCampaigns -Force)) {
        Remove-Item -LiteralPath $UserCampaigns -Force
        Write-Host "Removed the empty folder $UserCampaigns"
    }
    exit 0
}

if ($Collect) {
    $stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
    $stage = Join-Path $env:TEMP "SEST-TestCampaigns-$stamp"
    New-Item -ItemType Directory -Path $stage | Out-Null
    $since = (Get-Date).AddDays(-2)
    $installed = Join-Path (Join-Path $UserCampaigns $Names[0]) $Marker
    if (Test-Path -LiteralPath $installed) { $since = (Get-Item -LiteralPath $installed -Force).LastWriteTime }
    $logs = @(
        (Join-Path $Game 'BepInEx\LogOutput.log'),
        (Join-Path $LocalLow 'Player.log'),
        (Join-Path $LocalLow 'Player-prev.log')
    )
    foreach ($l in $logs) { if (Test-Path -LiteralPath $l) { Copy-Item -LiteralPath $l -Destination $stage } }
    $battles = Join-Path $stage 'battles'
    New-Item -ItemType Directory -Path $battles | Out-Null
    $found = @(Get-ChildItem -LiteralPath $LocalLow -Recurse -Filter 'battle_*.ini' -ErrorAction SilentlyContinue |
        Where-Object { $_.LastWriteTime -ge $since })
    $i = 0
    foreach ($b in $found) {
        $i++
        $rel = $b.FullName.Substring($LocalLow.Length).TrimStart('\') -replace '[\\/:]', '_'
        Copy-Item -LiteralPath $b.FullName -Destination (Join-Path $battles ("{0:D2}_{1}" -f $i, $rel))
    }
    $notes = @(
        "SEST test campaigns results $stamp",
        "Battle files written since install: $($found.Count)",
        '',
        'Fill in after each line (or reply with the lines in chat).',
        '',
        'HORMUZ WEATHER SPLIT',
        'H1 campaign listed and starts:',
        'H2 weather layer on; readout at Group A (northern Gulf): wind / sea state / cloud / rain:',
        'H3 readout at Group B (Strait of Hormuz):',
        'H4 readout at Group C (Arabian Sea):',
        'H5 any storm or low drawn in the region (yes/no, where):',
        'H6 contact 1: group, campaign time, map readout at that spot just before Play battle:',
        'H7 battle 1 weather seen in game (cloud, rain/fog/thunder, sea state):',
        'H8 contact 2: group, time, map readout:',
        'H9 battle 2 weather seen:',
        'H10 contact 3 (optional): group, time, readout / battle weather:',
        'H11 campaign time before and after one battle, and battle length played:',
        '',
        'POLAR NORTH (BARENTS, MARCH)',
        'N1 campaign listed and starts; map draws up to 81N:',
        'N2 ships move and route around Svalbard/Bear Island:',
        'N3 weather readout at N1 (77N), N2 (Bear Island), N3 (Norwegian Sea):',
        'N4 contact and battle at the ice edge load; terrain/coast look right:',
        'N5 Ocean Noise in the battle weather panel (ice edge) and in the N3 control if you fight there:',
        'N6 any visible ice, speed limit or other ice effect:',
        '',
        'POLAR SOUTH (ANTARCTIC PENINSULA, JANUARY)',
        'S1 campaign listed and starts; map draws down to 72S:',
        'S2 ships move and route through the Bransfield Strait / around the Peninsula:',
        'S3 weather readout at S1, S2 (Weddell 68S), S3 (Drake):',
        'S4 contact and battle load at 63S / 68S; terrain and Antarctic coast look right:',
        'S5 Ocean Noise in battle (Bransfield, Weddell) and in the Drake control:',
        'S6 any visible ice or ice effect:'
    )
    Set-Content -LiteralPath (Join-Path $stage 'RESULTS.txt') -Value $notes -Encoding UTF8
    $zip = Join-Path $env:USERPROFILE "Downloads\SEST-TestCampaigns-results-$stamp.zip"
    Compress-Archive -Path (Join-Path $stage '*') -DestinationPath $zip
    Copy-Item -LiteralPath (Join-Path $stage 'RESULTS.txt') -Destination ($zip -replace '\.zip$', '-RESULTS.txt')
    Write-Host "Results ZIP: $zip"
    Write-Host "Battle files included: $($found.Count)"
    Write-Host "Fill in $($zip -replace '\.zip$', '-RESULTS.txt') in Notepad, or reply with the lines."
    exit 0
}

if (-not (Test-Path -LiteralPath $Source)) { throw "Missing $Source - unzip the whole package first." }
New-Item -ItemType Directory -Path $UserCampaigns -Force | Out-Null
foreach ($n in $Names) {
    $dest = Join-Path $UserCampaigns $n
    if ((Test-Path -LiteralPath $dest) -and -not (Test-Path -LiteralPath (Join-Path $dest $Marker))) {
        throw "$dest exists and is not a SEST test campaign. Nothing was installed."
    }
}
foreach ($n in $Names) {
    $dest = Join-Path $UserCampaigns $n
    if (Test-Path -LiteralPath $dest) { Remove-Item -LiteralPath $dest -Recurse -Force }
    Copy-Item -LiteralPath (Join-Path $Source $n) -Destination $dest -Recurse
    Set-Content -LiteralPath (Join-Path $dest $Marker) -Value "installed $(Get-Date -Format s)" -Encoding ASCII
    Write-Host "Installed $dest"
}
Write-Host ''
Write-Host 'Start Sea Power, open Campaign: the three "SEST Test:" entries should be listed.'
Write-Host 'If one is missing, search Sea Power\BepInEx\LogOutput.log for "Skipping campaign".'
