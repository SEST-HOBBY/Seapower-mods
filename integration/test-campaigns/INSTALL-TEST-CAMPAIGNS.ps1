<#
SEST PC test campaigns for Dynamic Campaign Mod 1.0.1.

  powershell -ExecutionPolicy Bypass -File .\INSTALL-TEST-CAMPAIGNS.ps1            (install)
  powershell -ExecutionPolicy Bypass -File .\INSTALL-TEST-CAMPAIGNS.ps1 -Collect   (results ZIP)
  powershell -ExecutionPolicy Bypass -File .\INSTALL-TEST-CAMPAIGNS.ps1 -Uninstall (remove)

Copies the three campaigns in Test_Campaigns\dynamic_campaigns into the
game's user layer, Sea Power_Data\StreamingAssets\user\dynamic_campaigns, where
Dynamic Campaign Mod lists them in the Campaign menu. The Hormuz campaign's
folder also holds sest-weather.json, its placed storm (Cyclone DARYA); SEST's
runtime reads it from beside campaign.json, so it is copied with the folder
and checked byte for byte. Nothing in the Workshop
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
    # The placed-storm and campaign-ice lines from SEST's runtime, gathered in one file.
    $stormLines = @(foreach ($l in $logs) {
        if (Test-Path -LiteralPath $l) {
            Select-String -LiteralPath $l -SimpleMatch -Pattern 'world storms', 'campaign ice' | ForEach-Object { "$(Split-Path -Leaf $l): $($_.Line)" }
        }
    })
    Set-Content -LiteralPath (Join-Path $stage 'storms-log.txt') -Value $stormLines -Encoding UTF8
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
        'HORMUZ PLACED STORM (CYCLONE DARYA)',
        'D1 log has "world storms installed" and "world storms: sidecar ...sest-weather.json" (yes/no):',
        'D2 DARYA on the weather layer and in the storm list at the start, south-east of Group C; label, wind, category:',
        'D3 past track, forecast points and cone drawn (yes/no):',
        'D4 hover readout at Group C about 14 h in (15 Jan 18:00Z): wind / sea state / storm label:',
        'D5 contact at or near Group C while DARYA is close: contact-screen weather, then battle sea state / rain / thunder:',
        'D6 hover readout at Group B about 36 h in (16 Jan 16:00Z) and any contact/battle there:',
        'D7 Group A readout as DARYA dies (17 Jan 12:00-18:00Z) - should be DCM background weather:',
        'D8 save, quit to menu, load: DARYA at the same place (yes/no):',
        'D9 Polar North started after Hormuz in the same game session shows no DARYA (yes/no):',
        'D10 battle map Layers menu has "Weather (storms, gale rings, forecast track)"; log has "world storms map: layer" (yes/no):',
        'D11 Weather layer on in a battle near DARYA: centre marker, label and wind, gale ring, core ring, track with +1 h/+3 h/+6 h/+12 h (screenshot):',
        'D12 the layer moves with battle time (time-compress 30+ min): marker and labels move along the track (yes/no):',
        'D13 hover inside the gale ring shows the readout; toggling the layer off hides everything (yes/no):',
        '',
        'HORMUZ LOCAL BATTLE WEATHER (GROUPS D AND E, README-TESTS 1h)',
        'L1 Red D contact with Group D/E: campaign time, which group:',
        'L2 both DDG-105 Dewey (D) and DDG-106 Stockdale (E) in the one battle (yes/no; ships listed):',
        'L3 log has "world storms local weather: battle ... view weather on; baseline ..." (paste the line):',
        'L4 camera on DDG-105 (D): sea state / rain / lightning seen after ~10 s; log "applied sea state ..." (screenshot):',
        'L5 camera on DDG-106 (E): sea state / rain / lightning seen after 10-30 s; log "applied ..." (screenshot):',
        'L6 several jumps D/E (30 s each): each ship shows its own weather every time (yes/no):',
        'L7 free camera flown from E to D: weather builds on the way; clouds unchanged (yes/no):',
        'L8 save with the camera on D: log "save: the battle''s own weather written"; storm stays on screen; (optional) reload result:',
        'L9 battle end: log "baseline restored" or "nothing to restore"; any "local weather unavailable/stopped" line:',
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
        'S6 any visible ice or ice effect:',
        '',
        'CAMPAIGN MAP ICE (README-TESTS 5, POLAR NORTH AND SOUTH)',
        'C1 log has "campaign ice installed: map (...); movement (...)" (paste the line):',
        'C2 Polar North at the start, weather layer OFF: pale ice north of about 72N on 36E, cyan ice-edge line, navy heavy-pack line; log "campaign ice map: sea ice draped on the globe with the weather layer off" (screenshot):',
        'C3 weather layer ON, each of wind / sea state / rain / clouds / fog / storms: the same ice and lines drawn over it; log "weather frame ... composited with sea ice" (screenshots of two layers):',
        'C4 hover at about 74N 36E with the weather layer on: "Ice 62 % (heavy pack)" and "Surface groups 10 % speed (beset); submarines pass under" (paste):',
        'C5 time-compress to about 10 May (or the forecast slider): the edge on 36E moves from about 71.7N to about 73.7N; screenshots before and after (the day it moves):',
        'C6 Group N5 ordered to Red N3: speed text full, then "NN kn (ice)" past about 70.1N 41.7E (0.7), then 0.4 of its speed past about 70.8N 44E, before the contact at about 71.3N 45.4E (100 nm from Red N3); ETA shown, never 0 h; speeds noted:',
        'C7 Kobben (N4) ordered across the pack: its own speed, no "(ice)":',
        'C8 Polar South: ice edge at about 64.4S on 55W at the start; S5 to Red S3 as C6 (0.7 past about 64.0S, 0.4 past about 65.4S, contact at about 66.3S); ice retreats in a week of time compression:',
        'C9 Hormuz campaign: no ice anywhere; weather layer exactly as before:',
        'C10 any stutter when the campaign date changes; "campaign ice map: overlay for <date> ... built in N ms" and any "campaign ice ... unavailable/stopped" line (paste):'
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
    # A placed-storm sidecar must arrive unchanged beside campaign.json.
    $sidecar = Join-Path (Join-Path $Source $n) 'sest-weather.json'
    if (Test-Path -LiteralPath $sidecar) {
        $copy = Join-Path $dest 'sest-weather.json'
        if (-not (Test-Path -LiteralPath $copy) -or (Get-FileHash -LiteralPath $copy -Algorithm SHA256).Hash -ne (Get-FileHash -LiteralPath $sidecar -Algorithm SHA256).Hash) {
            throw "$copy was not copied intact. Run the install again."
        }
        Write-Host "  placed storm: $copy"
    }
}
Write-Host ''
Write-Host 'Start Sea Power, open Campaign: the three "SEST Test:" entries should be listed.'
Write-Host 'The Hormuz campaign carries Cyclone DARYA; it needs the R15 runtime with WorldStorms on (the default).'
Write-Host 'For the storm log lines add WorldStormsDiagnostics=1 under [Runtime] in the SEST runtime pack''s plugins\sest_runtime.ini.'
Write-Host 'If one is missing, search Sea Power\BepInEx\LogOutput.log for "Skipping campaign".'
